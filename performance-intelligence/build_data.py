#!/usr/bin/env python3
"""
Cartrack Insurance · Commercial Division — Performance Intelligence (DUMMY EDITION)
====================================================================================
Data builder. Mirrors the floor pack's pipeline: row-level records → one aggregated
`BB` blob → injected into index.html between the @@BB@@ markers.

  python3 build_data.py            # regenerate dummy data and rewrite index.html
  python3 build_data.py --json     # print the blob instead of writing it

EVERYTHING HERE IS SIMULATED. Seeded, so it is reproducible. The RM names are fictional.
The vocabulary is the live RM System's own (7 stages, 4 lead sources, 8 lost reasons,
7-day stale rule, 12.5% brokerage), so the day this is pointed at the real Supabase
tables (`deals`, `portfolio`) only `simulate()` changes — every aggregate below, and the
whole of index.html, stays as it is.
"""
import json, math, random, re, sys, datetime as dt, statistics as st
from collections import defaultdict, Counter

SEED = 20260907
R = random.Random(SEED)

# ─────────────────────────── vocabulary (from cartrack-rm-system/index.html) ───────────────────────────
STAGES = ['1. Data Discovery','2. Intro Meeting Set','3. Audit & Docs Requested','4. Risk Schedules Received',
          '5. Market Sourcing','6. Proposal / Closing Set','7. Won / Takeover Active']
LEAD_SOURCES = ['Cartrack Data','House Account','RM Self-Sourced','Referral']
LOST_REASONS = ['Price too high','Went with a competitor','Stayed with current broker','Cover / terms not suitable',
                'No response — went cold','Not proceeding / on hold','Vehicle / business sold or closed','Other']
STALE_DAYS = 7
BROKERAGE_RATE = 0.125

# ─────────────────────────── desks (the commercial analogue of the floor's islands) ───────────────────────────
DESKS = {
  'Desk 1':'Desk 1 · Fleet & Transport',
  'Desk 2':'Desk 2 · SME Commercial',
  'Desk 3':'Desk 3 · Private Client',
  'Desk 4':'Desk 4 · Dealerships',       # bound deals, no pipeline activity — blind
  'Desk 5':'Desk 5 · Renewal Book',      # premium, no pipeline activity — blind
  'Desk 6':'Desk 6 · Coastal',
  'Desk 7':'Desk 7 · Key Accounts',
  'untagged':'Untagged',
}

SEGMENTS = {  # name: (median monthly premium, sigma, weight, fleet median)
  'Transport & logistics':      (26000, 0.85, 0.20, 34),
  'Passenger transport':        (31000, 0.70, 0.06, 26),
  'Contractors & trades':       (7200,  0.75, 0.22, 9),
  'Retail, fuel & forecourt':   (14500, 0.80, 0.11, 7),
  'Professional services':      (6200,  0.70, 0.13, 6),
  'Mining & industrial supply': (18500, 0.90, 0.10, 12),
  'Agriculture':                (11800, 0.85, 0.08, 14),
  'Private client':             (15500, 0.75, 0.10, 4),
}
# insurer / UMA: (median quote turnaround days, sigma, segments it quotes)
INSURERS = {
  'Bryte':                  (3.0, 0.45, ['Contractors & trades','Professional services','Retail, fuel & forecourt','Mining & industrial supply','Agriculture']),
  'Hollard':                (4.0, 0.45, ['Contractors & trades','Professional services','Private client','Retail, fuel & forecourt','Agriculture']),
  'Santam':                 (5.0, 0.50, ['Transport & logistics','Passenger transport','Private client','Agriculture','Retail, fuel & forecourt']),
  'Merx / Old Mutual':      (7.0, 0.50, ['Transport & logistics','Passenger transport','Mining & industrial supply']),
  'VAPS / King Price':      (3.0, 0.50, ['Transport & logistics','Passenger transport','Contractors & trades']),
  'OWNsurance / Renasa':    (9.0, 0.55, ['Transport & logistics','Mining & industrial supply']),
  'Natsure / Compass':      (6.0, 0.50, ['Contractors & trades','Retail, fuel & forecourt','Mining & industrial supply']),
  'Western':                (7.0, 0.55, ['Contractors & trades','Professional services','Agriculture']),
  'Alpha / Guardrisk':      (12.0,0.55, ['Transport & logistics','Passenger transport','Mining & industrial supply','Retail, fuel & forecourt']),
  'CIB':                    (4.0, 0.45, ['Private client']),
}
HOUR_W = {8:9,9:14,10:14,11:12,12:8,13:6,14:12,15:11,16:9,17:5}
HAZ = {1:.38,2:.31,3:.29,4:.30,5:.26,6:.24,7:.21,8:.19,9:.18,10:.17}   # contact probability by touch number
LOST_W = {'No response — went cold':34,'Stayed with current broker':22,'Price too high':14,'Not proceeding / on hold':12,
          'Went with a competitor':8,'Cover / terms not suitable':5,'Vehicle / business sold or closed':2,'Other':3}

# ─────────────────────────── the roster (FICTIONAL) ───────────────────────────
# desk_jul / desk_aug: where the RM's deals are tagged each month (mirrors the floor's tagging story)
# lam: new leads a month · pers: chance of another touch after an unanswered one · delay: days to first touch
# c/m/s/p/w: contact / meeting / schedule / proposal / win skill multipliers · pspeed: proposal build days (median)
# blank: share of lost deals closed with no reason · stale: tendency to leave open deals untouched
ROSTER = [
 dict(rm='Thabo Mokoena',   desk_jul='untagged', desk_aug='Desk 1', lam=34, pers=.55, delay=1.5, c=1.00, m=.62, s=.60, p=.72, w=.42, pspeed=6,  blank=.10, stale=.18, book=52, active=('jul','aug')),
 dict(rm='Anneke Botha',    desk_jul='Desk 1',   desk_aug='Desk 1', lam=30, pers=.78, delay=1.0, c=1.08, m=.68, s=.64, p=.86, w=.55, pspeed=4, pspeed_aug=2, blank=.04, stale=.10, book=61, active=('jul','aug')),  # started using the comparison portal in August
 dict(rm='Sipho Dlamini',   desk_jul='Desk 2',   desk_aug='Desk 2', lam=42, pers=.36, delay=2.5, c=0.94, m=.58, s=.55, p=.58, w=.42, pspeed=15, blank=.38, stale=.34, book=44, active=('jul','aug')),
 dict(rm='Riaan Steyn',     desk_jul='Desk 2',   desk_aug='Desk 2', lam=36, pers=.70, delay=1.5, c=1.02, m=.64, s=.61, p=.80, w=.52, pspeed=4,  blank=.08, stale=.14, book=58, active=('jul','aug')),
 dict(rm='Naledi Khumalo',  desk_jul='Desk 3',   desk_aug='Desk 3', lam=28, pers=.82, delay=0.8, c=1.12, m=.72, s=.70, p=.90, w=.58, pspeed=3,  blank=.02, stale=.06, book=73, active=('jul','aug')),
 dict(rm='Chantal Adams',   desk_jul='Desk 6',   desk_aug='Desk 6', lam=26, pers=.62, delay=2.0, c=0.98, m=.60, s=.66, p=.34, w=.46, pspeed=22, blank=.16, stale=.28, book=39, active=('jul','aug')),  # schedules in, few proposals out
 dict(rm='Werner Nel',      desk_jul='Desk 7',   desk_aug='Desk 7', lam=13, pers=.90, delay=1.0, c=1.05, m=.70, s=.68, p=.84, w=.55, pspeed=7,  blank=.05, stale=.08, book=27, active=('jul','aug'), big=True),
 dict(rm='Lerato Sithole',  desk_jul='Desk 2',   desk_aug='Desk 2', lam=24, pers=.50, delay=2.0, c=0.96, m=.60, s=.58, p=.70, w=.46, pspeed=9, blank=.20, stale=.22, book=31, active=('jul',)),        # left end July
 dict(rm='Johan Pretorius', desk_jul='Desk 1',   desk_aug='Desk 1', lam=22, pers=.66, delay=1.2, c=0.92, m=.60, s=.56, p=.74, w=.44, pspeed=6,  blank=.12, stale=.16, book=0,  active=('aug',), start=dt.date(2026,8,10)),  # joined 10 Aug
 dict(rm='Pieter Fourie',   desk_jul='Desk 6',   desk_aug='Desk 6', lam=14, pers=.95, delay=1.0, c=1.00, m=.62, s=.62, p=.78, w=.50, pspeed=6,  blank=.10, stale=.12, book=18, active=('jul','aug'), overwork=True),  # small book, over-works dead leads
]
DESK_SRC = {  # lead-source mix by desk (Cartrack Data is over-stated because the field defaults to it)
  'Desk 1':{'Cartrack Data':.62,'House Account':.10,'RM Self-Sourced':.20,'Referral':.08},
  'Desk 2':{'Cartrack Data':.55,'House Account':.08,'RM Self-Sourced':.27,'Referral':.10},
  'Desk 3':{'Cartrack Data':.30,'House Account':.22,'RM Self-Sourced':.28,'Referral':.20},
  'Desk 6':{'Cartrack Data':.58,'House Account':.10,'RM Self-Sourced':.24,'Referral':.08},
  'Desk 7':{'Cartrack Data':.40,'House Account':.35,'RM Self-Sourced':.15,'Referral':.10},
  'untagged':{'Cartrack Data':.62,'House Account':.10,'RM Self-Sourced':.20,'Referral':.08},
}
DESK_SEG = {
  'Desk 1':{'Transport & logistics':.55,'Passenger transport':.15,'Agriculture':.10,'Mining & industrial supply':.10,'Contractors & trades':.10},
  'Desk 2':{'Contractors & trades':.42,'Professional services':.25,'Retail, fuel & forecourt':.20,'Mining & industrial supply':.08,'Agriculture':.05},
  'Desk 3':{'Private client':.85,'Professional services':.15},
  'Desk 6':{'Transport & logistics':.25,'Passenger transport':.15,'Agriculture':.25,'Retail, fuel & forecourt':.20,'Contractors & trades':.15},
  'Desk 7':{'Transport & logistics':.45,'Mining & industrial supply':.30,'Passenger transport':.15,'Retail, fuel & forecourt':.10},
  'untagged':{'Transport & logistics':.55,'Passenger transport':.15,'Agriculture':.10,'Mining & industrial supply':.10,'Contractors & trades':.10},
}
SRC_WIN = {'Cartrack Data':1.0,'House Account':1.15,'RM Self-Sourced':1.05,'Referral':1.35}

# ─────────────────────────── calendar ───────────────────────────
SIM_START, SIM_END = dt.date(2026,5,4), dt.date(2026,9,7)   # SIM_END = the data cut (today). Nothing after it exists.
CUT = SIM_END
WIN_S, WIN_P, WIN_W = 21, 14, 21   # cohort maturity windows in days: contact→schedules, schedules→proposal, proposal→decision
def within(d0, d1, days): return d1 is not None and d1 <= min(d0 + dt.timedelta(days=days), CUT)
HOLIDAYS = {dt.date(2026,6,16)}           # matches the floor pack's working-day calendar: Jul 23 · Aug 21
def is_wd(d): return d.weekday() < 5 and d not in HOLIDAYS
def add_wd(d, n):
    n = max(0, int(round(n)))
    while n > 0:
        d += dt.timedelta(days=1)
        if is_wd(d): n -= 1
    return d
def add_cal(d, n): return next_wd(d + dt.timedelta(days=max(0,int(round(n)))))
def next_wd(d):
    while not is_wd(d): d += dt.timedelta(days=1)
    return d
MONTHS = {'jul':(dt.date(2026,7,1),dt.date(2026,7,31)), 'aug':(dt.date(2026,8,1),dt.date(2026,8,31))}
WD = {m:sum(1 for i in range((b-a).days+1) if is_wd(a+dt.timedelta(days=i))) for m,(a,b) in MONTHS.items()}
WDCAL = {'2026-09':21,'2026-10':22,'2026-11':21,'2026-12':21,'2027-01':21,'2027-02':20}
def inm(d, m): a,b = MONTHS[m]; return d is not None and a <= d <= b
def month_of(d): return 'jul' if d.month==7 else 'aug' if d.month==8 else None

def wchoice(w):
    ks = list(w.keys()); tot = sum(w.values()); x = R.random()*tot
    for k in ks:
        x -= w[k]
        if x <= 0: return k
    return ks[-1]
def lognorm(med, sig): return med*math.exp(R.gauss(0, sig))
def rnd(x, d=1): return round(x, d) if x is not None else None
def pct(a, b, d=1): return rnd(100.0*a/b, d) if b else 0

# ─────────────────────────── simulation ───────────────────────────
def simulate():
    deals, touches = [], []
    dealers_won, renewals = [], []
    did = 0
    for rp in ROSTER:
        start = rp.get('start', SIM_START)
        end = dt.date(2026,8,31) if 'aug' in rp['active'] else dt.date(2026,7,31)
        d = start
        while d <= end:
            if is_wd(d):
                per_day = rp['lam']/21.5
                x = R.random(); p = math.exp(-per_day); sacc = p; k = 0
                while x > sacc and k < 8:
                    k += 1; p *= per_day/k; sacc += p
                n = k
                aug = d >= dt.date(2026,8,1)
                pers = min(.97, rp['pers'] + (.22 if aug else 0))          # August: a follow-up push across the team
                cmul = rp['c']*(1.10 if aug else 1.0)
                pspeed = rp.get('pspeed_aug', rp['pspeed']) if aug else rp['pspeed']
                for _ in range(n):
                    did += 1
                    desk = rp['desk_jul'] if d <= dt.date(2026,7,31) else rp['desk_aug']
                    src = wchoice(DESK_SRC[desk]); seg = wchoice(DESK_SEG[desk])
                    med, sig, _, fleetmed = SEGMENTS[seg]
                    prem = lognorm(med*(1.8 if rp.get('big') else 1.0), sig)
                    if rp.get('big') and R.random() < .10: prem *= 2.5
                    if not rp.get('big') and R.random() < .02: prem *= 3.0           # the thin top tail every book has
                    fleet = max(1, int(round(lognorm(fleetmed*(2.4 if rp.get('big') else 1), .6))))
                    deal = dict(id='d%04d'%did, rm=rp['rm'], desk=desk, src=src, seg=seg, prem=round(prem,2), fleet=fleet,
                                untracked=int(round(fleet*R.uniform(.25,.65))), created=d, contacted=None, meet=None, docs=None,
                                sched=None, mkt=None, prop=None, dec=None, won=False, lost=None, reason=None, insurer=None,
                                quotes=[], last=d, ntouch=0)
                    def chase(day, n_, kind):
                        """stage-chasing activity on an open deal: not a first-contact attempt, so it carries no k"""
                        for j in range(n_):
                            day = add_wd(day, R.choice([1,1,2,2,3,4]))
                            if day > SIM_END: return
                            touches.append(dict(deal=deal['id'], rm=rp['rm'], desk=desk, date=day, hour=wchoice(HOUR_W), k=0, hit=True, kind=kind))
                            deal['last'] = max(deal['last'], day)
                    # ---- first-contact attempts ----
                    t = add_wd(d, R.expovariate(1/max(.3,rp['delay'])))
                    k = 0; contacted = None
                    cap = 12 if rp.get('overwork') else 8
                    while k < cap and t <= SIM_END:
                        k += 1
                        hit = R.random() < HAZ.get(k, .17)*cmul
                        touches.append(dict(deal=deal['id'], rm=rp['rm'], desk=desk, date=t, hour=wchoice(HOUR_W), k=k, hit=hit, kind='attempt'))
                        deal['ntouch'] = k; deal['last'] = t
                        if hit: contacted = t; break
                        if R.random() > pers*(1.0 if k < 4 else .75): break
                        t = add_wd(t, R.choice([1,1,2,2,3,4,5]))
                    if contacted is None:
                        if R.random() < min(.97, .88*(1.15-rp['stale'])):     # closed as cold a few weeks later; tidy RMs sweep, untidy ones do not
                            ld = add_wd(deal['last'], R.randint(8,22))
                            if ld <= SIM_END:
                                deal['dec'] = ld; deal['lost'] = True
                                deal['reason'] = None if R.random() < rp['blank'] else 'No response — went cold'
                        deals.append(deal); continue
                    deal['contacted'] = contacted
                    # ---- meeting ----
                    if R.random() < rp['m']*SRC_WIN[src]**.3:
                        deal['meet'] = add_wd(contacted, R.randint(2,9)); chase(contacted, 1, 'meeting')
                    else:
                        _close(deal, rp, contacted, min(.95,.8*(1.15-rp['stale']))); deals.append(deal); continue
                    deal['docs'] = add_wd(deal['meet'], R.randint(0,2)); deal['last'] = deal['docs']
                    # ---- schedules ----
                    if R.random() < rp['s']:
                        deal['sched'] = add_wd(deal['docs'], int(lognorm(6, .6))); chase(deal['docs'], R.choice([1,1,2,3]), 'docs')
                    else:
                        chase(deal['docs'], R.choice([1,2,2,3]), 'docs'); _close(deal, rp, deal['docs'], min(.95,.78*(1.15-rp['stale']))); deals.append(deal); continue
                    deal['last'] = max(deal['last'], deal['sched'])
                    # ---- market sourcing ----
                    deal['mkt'] = add_wd(deal['sched'], R.choice([0,0,1,1,2]))
                    cands = [i for i,(_,_,segs) in INSURERS.items() if seg in segs] or list(INSURERS)
                    nq = min(len(cands), R.choice([2,2,3,3,3]))
                    for ins in R.sample(cands, nq):
                        medd, sg, _ = INSURERS[ins]
                        back = add_cal(deal['mkt'], lognorm(medd, sg))
                        deal['quotes'].append(dict(ins=ins, req=deal['mkt'], back=back))
                        if (back-deal['mkt']).days > 7: chase(add_wd(deal['mkt'],7), 1, 'insurer')
                    backs = sorted(q['back'] for q in deal['quotes'])
                    enough = backs[1] if len(backs) > 1 else backs[0]        # the RM builds once two quotes are in
                    deal['last'] = max(deal['last'], min(enough, SIM_END))
                    # ---- proposal ----
                    if R.random() < rp['p']:
                        deal['prop'] = add_cal(enough, lognorm(pspeed, .5))
                        chase(enough, 1, 'proposal')
                        bq = [q for q in deal['quotes'] if q['back'] <= deal['prop']] or deal['quotes']
                        deal['insurer'] = R.choice(bq)['ins']
                        deal['last'] = max(deal['last'], min(deal['prop'], SIM_END))
                    else:
                        # never presented: sits in Market Sourcing. Half are eventually closed as cold.
                        if R.random() < min(.95,.7*(1.15-rp['stale'])):
                            ld = add_wd(enough, R.randint(15,40))
                            if ld <= SIM_END:
                                deal['dec'] = ld; deal['lost'] = True
                                deal['reason'] = None if R.random() < rp['blank'] else wchoice({'No response — went cold':6,'Not proceeding / on hold':3,'Stayed with current broker':2})
                        deals.append(deal); continue
                    # ---- decision ----
                    gap = (deal['prop'] - deal['sched']).days
                    speed = 1.5 if gap <= WIN_P else (.9 if gap <= 21 else .55)
                    pw = min(.9, rp['w']*speed*SRC_WIN[src])
                    decd = add_cal(deal['prop'], lognorm(9, .6))
                    chase(deal['prop'], R.choice([1,1,2]), 'closing')
                    if decd <= SIM_END:
                        deal['dec'] = decd
                        if R.random() < pw:
                            deal['won'] = True
                        else:
                            deal['lost'] = True
                            deal['reason'] = None if R.random() < rp['blank'] else wchoice(LOST_W)
                        deal['last'] = max(deal['last'], decd)
                    deals.append(deal)
            d += dt.timedelta(days=1)
    # ---- the two blind desks: bound business with no pipeline activity ----
    for m,(a,b) in MONTHS.items():
        nd = 9 if m=='jul' else 6
        for i in range(nd):
            day = next_wd(a + dt.timedelta(days=R.randint(0,(b-a).days-1)))
            dealers_won.append(dict(rm='Dealer desk (Auto Pedigree)' if i%3 else 'Dealer desk (Imperial Select)', desk='Desk 4', seg='Contractors & trades' if i%2 else 'Private client',
                                    prem=round(lognorm(4200,.6),2), day=day, src='House Account', insurer=R.choice(['Hollard','Santam','Bryte'])))
        nr = 41 if m=='jul' else 36
        for i in range(nr):
            day = next_wd(a + dt.timedelta(days=R.randint(0,(b-a).days-1)))
            seg = wchoice({k:v[2] for k,v in SEGMENTS.items()})
            renewals.append(dict(rm='Renewals admin', desk='Desk 5', seg=seg, prem=round(lognorm(SEGMENTS[seg][0]*.9, SEGMENTS[seg][1]*.9),2), day=day,
                                 src='House Account', insurer=R.choice(list(INSURERS))))
    # an RM whose name is spelled differently on the book than on the pipeline (the floor's orphan problem)
    for m,(a,b) in MONTHS.items():
        renewals.append(dict(rm='C. Adams-Botha', desk='Desk 6', seg='Agriculture', prem=round(lognorm(9800,.4),2), day=next_wd(a+dt.timedelta(days=R.randint(3,20))), src='Referral', insurer='Santam', orphan=True))
    return deals, touches, dealers_won, renewals

def _close(deal, rp, after, p_lost):
    """deal dies after `after`: sometimes closed as lost with a reason, sometimes left open."""
    if R.random() < p_lost:
        ld = add_wd(after, R.randint(6,30))
        if ld <= SIM_END:
            deal['dec'] = ld; deal['lost'] = True
            deal['reason'] = None if R.random() < rp['blank'] else wchoice({'No response — went cold':5,'Stayed with current broker':4,'Not proceeding / on hold':2,'Price too high':1,'Other':1})
            deal['last'] = ld

# ─────────────────────────── aggregation ───────────────────────────
def quart(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs: return dict(p25=0, med=0, p75=0)
    def q(p):
        i = (len(xs)-1)*p; lo = int(math.floor(i)); hi = min(lo+1, len(xs)-1)
        return xs[lo] + (xs[hi]-xs[lo])*(i-lo)
    return dict(p25=rnd(q(.25)), med=rnd(q(.5)), p75=rnd(q(.75)))
def pctl(xs, p):
    xs = sorted(x for x in xs if x is not None)
    if not xs: return 0
    i = (len(xs)-1)*p; lo = int(math.floor(i)); hi = min(lo+1, len(xs)-1)
    return xs[lo] + (xs[hi]-xs[lo])*(i-lo)
def median(xs): return rnd(st.median(xs)) if xs else None
def gini(xs):
    xs = sorted(xs); n = len(xs)
    if n == 0 or sum(xs) == 0: return 0
    cum = 0; s = sum(xs); g = 0
    for i,x in enumerate(xs, 1): g += i*x
    return rnd(2*g/(n*s) - (n+1)/n, 3)
def lorenz(xs):
    xs = sorted(xs); s = sum(xs) or 1; out = []; c = 0
    for i in range(1, 21):
        k = int(round(len(xs)*i/20)); out.append(dict(x=i*5, y=rnd(100*sum(xs[:k])/s)))
    return out

def rm_month(rp, m, deals, touches):
    a, b = MONTHS[m]
    mine = [d for d in deals if d['rm'] == rp['rm']]
    tch = [t for t in touches if t['rm'] == rp['rm'] and inm(t['date'], m)]
    att = [t for t in tch if t['kind']=='attempt']
    days = len({t['date'] for t in tch})
    leads = [d for d in mine if inm(d['created'], m)]
    cont = [d for d in mine if inm(d['contacted'], m)]
    meet = [d for d in mine if inm(d['meet'], m)]
    sched = [d for d in mine if inm(d['sched'], m)]
    mkt = [d for d in mine if inm(d['mkt'], m)]
    prop = [d for d in mine if inm(d['prop'], m)]
    won = [d for d in mine if d['won'] and inm(d['dec'], m)]
    lost = [d for d in mine if d['lost'] and inm(d['dec'], m)]
    openp = [d for d in mine if d['created'] <= b and not ((d['won'] or d['lost']) and d['dec'] <= b)]
    stale = [d for d in openp if (b - min(d['last'], b)).days > STALE_DAYS]
    # leads touched in the month, grouped by attempts within the month
    per_lead = defaultdict(list)
    for t in att: per_lead[t['deal']].append(t)
    once = [k for k,v in per_lead.items() if len(v) == 1]
    once_unc = [k for k in once if not per_lead[k][0]['hit']]
    # cohort rates, each on its own cohort with a fixed maturity window (never above 100%)
    c_d = len(per_lead); c_n = sum(1 for v in per_lead.values() if any(t['hit'] for t in v))
    mat = lambda xs, f, w: [d for d in xs if d[f] <= CUT - dt.timedelta(days=w)]
    cs, ss, ps = mat(cont,'contacted',WIN_S), mat(sched,'sched',WIN_P), mat(prop,'prop',WIN_W)
    s_d = len(cs); s_n = sum(1 for d in cs if within(d['contacted'], d['sched'], WIN_S))
    p_d = len(ss); p_n = sum(1 for d in ss if within(d['sched'], d['prop'], WIN_P))
    w_d = len(ps); w_n = sum(1 for d in ps if d['won'] and within(d['prop'], d['dec'], WIN_W))
    prem = sum(d['prem'] for d in won)
    bfee = sum(R.choice([0,350,450,650,850]) for _ in won)  # dummy broker fees on bound deals
    comm = prem*BROKERAGE_RATE + bfee
    ttc = [(d['contacted']-d['created']).days for d in cont]
    tts = [(d['sched']-d['contacted']).days for d in sched if d['contacted']]
    ttp = [(d['prop']-d['sched']).days for d in prop if d['sched']]
    ttw = [(d['dec']-d['prop']).days for d in won if d['prop']]
    desk = rp['desk_jul'] if m=='jul' else rp['desk_aug']
    srcs = Counter(d['src'] for d in leads); inss = Counter(d['insurer'] for d in won if d['insurer'])
    lapses = 0 if rp['book']==0 else sum(1 for _ in range(rp['book']) if R.random() < .012)
    book = rp['book'] - (lapses if m=='aug' else 0)
    bookprem = rp['book']*lognorm(10800,.15) if rp['book'] else 0
    svc = int(round(rp['book']*R.uniform(.28,.42))) if rp['book'] else 0     # book-servicing activities (visits, claims, endorsements)
    x = dict(rm=rp['rm'], desk=desk, days=days, touches=len(tch), tpd=rnd(len(tch)/days) if days else 0, attempts=len(att), svc=svc,
             leads=len(leads), tpl=rnd(len(att)/len(per_lead),2) if per_lead else 0,
             contacted=len(cont), contactrate=pct(c_n, c_d), c_n=c_n, c_d=c_d,
             meet=len(meet), sched=len(sched), schedrate=pct(s_n, s_d), s_n=s_n, s_d=s_d,
             mkt=len(mkt), prop=len(prop), proprate=pct(p_n, p_d), p_n=p_n, p_d=p_d,
             won=len(won), winrate=pct(w_n, w_d), w_n=w_n, w_d=w_d, prem=round(prem,2), ann=round(prem*12,2), comm=round(comm,2),
             avg=rnd(st.median([d['prem'] for d in won]),0) if won else 0, mx=rnd(max([d['prem'] for d in won]),0) if won else 0,
             lost=len(lost), noreason=pct(sum(1 for d in lost if not d['reason']), len(lost)),
             open=len(openp), openprem=round(sum(d['prem'] for d in openp),2), stale=len(stale), stalepct=pct(len(stale), len(openp)),
             tt_contact=median(ttc), tt_sched=median(tts), tt_prop=median(ttp), tt_win=median(ttw),
             units=sum(d['untracked'] for d in sched), book=book, bookprem=round(bookprem,2), lapses=lapses,
             once=len(once), once_unc=len(once_unc),
             topsrc=srcs.most_common(1)[0][0] if srcs else '–', topsrcpct=pct(srcs.most_common(1)[0][1], len(leads)) if srcs else 0,
             topins=inss.most_common(1)[0][0] if inss else '–', mq='exact')
    return x

def cohort_funnel(deals, m, rms):
    """the funnel the floor cannot draw: every lead created in the month, followed to the data cut"""
    a, b = MONTHS[m]
    c = [d for d in deals if inm(d['created'], m) and d['rm'] in rms]
    f = dict(n=len(c), contacted=sum(1 for d in c if d['contacted']), meet=sum(1 for d in c if d['meet']), sched=sum(1 for d in c if d['sched']),
             prop=sum(1 for d in c if d['prop']), won=sum(1 for d in c if d['won']), lost=sum(1 for d in c if d['lost']),
             prem=round(sum(d['prem'] for d in c if d['won']),2), age=(CUT-b).days)
    f['open'] = f['n']-f['won']-f['lost']
    return f

def tests_2p(x1, n1, x2, n2):
    p1, p2 = (min(1,x1/n1) if n1 else 0), (min(1,x2/n2) if n2 else 0); pp = (x1+x2)/((n1+n2) or 1)
    se0 = math.sqrt(pp*(1-pp)*((1/n1 if n1 else 0)+(1/n2 if n2 else 0))) or 1e-9
    se = math.sqrt((p1*(1-p1)/n1 if n1 else 0)+(p2*(1-p2)/n2 if n2 else 0)) or 1e-9
    z = (p2-p1)/se0; p = math.erfc(abs(z)/math.sqrt(2))
    d = 100*(p2-p1)
    return dict(d=d, lo=d-196*se, hi=d+196*se, z=z, p=p)

def build():
    deals, touches, dealers, renewals = simulate()
    BB = dict(d={}, e={}, x={}, a=dict(attempts={}, audit={}, tests={}, timing={}, haz={}, dist={}, hist={}, dec={}, ins={}, cyc={}, stall={}), q=dict(wdcal=WDCAL))
    rmrows = {}
    for m,(a,b) in MONTHS.items():
        rows = [rm_month(rp, m, deals, touches) for rp in ROSTER if m in rp['active']]
        rmrows[m] = rows
        act = [r for r in rows if r['leads'] >= 10]
        bm = {k: quart([r[k] for r in act]) for k in ['tpd','contactrate','tpl','schedrate','proprate','winrate','stalepct','tt_prop','noreason']}
        # desks
        desks = {}
        for k in DESKS:
            rr = [r for r in rows if r['desk']==k]
            dd = dict(rms=len(rr), touches=sum(r['touches'] for r in rr), leads=sum(r['leads'] for r in rr), contacted=sum(r['contacted'] for r in rr),
                      c_n=sum(r['c_n'] for r in rr), c_d=sum(r['c_d'] for r in rr), s_n=sum(r['s_n'] for r in rr), s_d=sum(r['s_d'] for r in rr),
                      p_n=sum(r['p_n'] for r in rr), p_d=sum(r['p_d'] for r in rr), w_n=sum(r['w_n'] for r in rr), w_d=sum(r['w_d'] for r in rr),
                      sched=sum(r['sched'] for r in rr), prop=sum(r['prop'] for r in rr), won=sum(r['won'] for r in rr), prem=round(sum(r['prem'] for r in rr),2),
                      comm=round(sum(r['comm'] for r in rr),2), open=sum(r['open'] for r in rr), stale=sum(r['stale'] for r in rr), units=sum(r['units'] for r in rr))
            if k=='Desk 4':
                dw = [d for d in dealers if inm(d['day'], m)]
                dd.update(won=len(dw), prem=round(sum(d['prem'] for d in dw),2), comm=round(sum(d['prem'] for d in dw)*BROKERAGE_RATE,2))
            if k=='Desk 5':
                rw = [d for d in renewals if inm(d['day'], m) and not d.get('orphan')]
                dd.update(won=len(rw), prem=round(sum(d['prem'] for d in rw),2), comm=round(sum(d['prem'] for d in rw)*BROKERAGE_RATE,2))
            dd.update(contactrate=pct(dd['c_n'], dd['c_d']), schedrate=pct(dd['s_n'], dd['s_d']), proprate=pct(dd['p_n'], dd['p_d']),
                      winrate=pct(dd['w_n'], dd['w_d']), stalepct=pct(dd['stale'], dd['open']))
            desks[k] = dd
        # orphans: sellers on the book with no pipeline activity
        orph = defaultdict(lambda: dict(won=0, prem=0.0, desk='', topsrc='', ins=Counter()))
        for d in dealers + renewals:
            if inm(d['day'], m):
                o = orph[d['rm']]; o['won'] += 1; o['prem'] += d['prem']; o['desk'] = d['desk']; o['topsrc'] = d['src']; o['ins'][d['insurer']] += 1
        orphans = [dict(rm=k, won=v['won'], prem=round(v['prem'],2), desk=v['desk'], topsrc=v['topsrc'], topins=v['ins'].most_common(1)[0][0]) for k,v in orph.items()]
        orphans.sort(key=lambda o: -o['prem'])
        BB['d'][m] = dict(rms=sorted(rows, key=lambda r: -r['touches']), orphans=orphans, desks=desks, wd=WD[m], bm=bm, n_active=len(act))
        # ---- E: series + mixes ----
        ser = []
        won_m = [d for d in deals if d['won'] and inm(d['dec'], m)]
        for i in range((b-a).days+1):
            day = a + dt.timedelta(days=i)
            tt = [t for t in touches if t['date']==day]
            wd_ = [d for d in won_m if d['dec']==day]
            ser.append(dict(d=day.isoformat(), dn=i+1, dow=day.weekday(), touches=len(tt), contacted=sum(1 for t in tt if t['hit']),
                            leads=sum(1 for d in deals if d['created']==day), sched=sum(1 for d in deals if d['sched']==day),
                            prop=sum(1 for d in deals if d['prop']==day), contactrate=pct(sum(1 for t in tt if t['hit']), len(tt)),
                            won=len(wd_), prem=round(sum(d['prem'] for d in wd_),2)))
        allwon = won_m + [d for d in dealers if inm(d['day'], m)] + [d for d in renewals if inm(d['day'], m)]
        srcmix = Counter(); srcv = Counter(); insmix = Counter(); insv = Counter(); segmix = Counter(); segv = Counter(); srcw = Counter()
        for d in deals:
            if inm(d['created'], m): srcmix[d['src']] += 1
        for d in won_m:
            srcv[d['src']] += d['prem']; srcw[d['src']] += 1
        for d in allwon:
            if d.get('insurer'): insmix[d['insurer']] += 1; insv[d['insurer']] += d['prem']
            segmix[d['seg']] += 1; segv[d['seg']] += d['prem']
        lost_m = [d for d in deals if d['lost'] and inm(d['dec'], m)]
        lostmix = Counter(d['reason'] or 'Not recorded' for d in lost_m)
        openend = [d for d in deals if d['created'] <= b and not ((d['won'] or d['lost']) and d['dec'] <= b) and d['rm'] in {r['rm'] for r in rows}]
        def stage_at(d):
            if d['prop'] and d['prop'] <= b: return 6
            if d['mkt'] and d['mkt'] <= b: return 5
            if d['sched'] and d['sched'] <= b: return 4
            if d['docs'] and d['docs'] <= b: return 3
            if d['meet'] and d['meet'] <= b: return 2
            return 1
        stagemix = Counter(stage_at(d) for d in openend)
        BB['e'][m] = dict(wd=WD[m], series=ser,
                          srcmix=[dict(k=k, n=n, w=srcw[k], r=round(srcv[k],2)) for k,n in srcmix.most_common()],
                          insmix=[dict(k=k, n=n, r=round(insv[k],2)) for k,n in insmix.most_common()],
                          segmix=[dict(k=k, n=n, r=round(segv[k],2)) for k,n in segmix.most_common()],
                          lostmix=[dict(k=k, v=v) for k,v in lostmix.most_common()],
                          stagemix=[dict(k=STAGES[s-1], v=stagemix.get(s,0), prem=round(sum(d['prem'] for d in openend if stage_at(d)==s),2)) for s in range(1,7)],
                          nreasons=len([k for k in lostmix if k!='Not recorded']))
        # ---- AN.attempts (touch hazard within the month) ----
        per_lead = defaultdict(list)
        for t in touches:
            if inm(t['date'], m) and t['kind']=='attempt': per_lead[t['deal']].append(t)
        leads_touched = len(per_lead)
        reached = sum(1 for v in per_lead.values() if any(t['hit'] for t in v))
        once = sum(1 for v in per_lead.values() if len(v)==1)
        once_unc = sum(1 for v in per_lead.values() if len(v)==1 and not v[0]['hit'])
        def att_rate(k):
            ts = [t for v in per_lead.values() for t in v if t['k']==k]
            return (len(ts), pct(sum(1 for t in ts if t['hit']), len(ts)))
        n2, a2 = att_rate(2); n3, a3 = att_rate(3)
        BB['a']['attempts'][m] = dict(leads=leads_touched, reached=reached, once=once, once_unreached=once_unc, a2=a2, a3=a3, rec2=int(round(once_unc*a2/100)))
        haz = []
        for k in range(1, 11):
            ts = [t for v in per_lead.values() for t in v if (t['k']==k if k<10 else t['k']>=10)]
            dl = {t['deal'] for t in ts}
            # "meeting set per touch": share of touches at attempt k whose deal reached a meeting
            mt = sum(1 for t in ts if t['hit'] and next(d for d in deals if d['id']==t['deal'])['meet'])
            haz.append(dict(k=k, n=len(ts), ar=pct(sum(1 for t in ts if t['hit']), len(ts)), mr=pct(mt, len(ts), 2)))
        BB['a']['haz'][m] = haz
        # ---- timing ----
        tm = [t for t in touches if inm(t['date'], m) and t['kind']=='attempt']
        hour = []; dow = []; cell = []
        for h in sorted(HOUR_W):
            ts = [t for t in tm if t['hour']==h]
            if len(ts) >= 15: hour.append(dict(h=h, n=len(ts), r=pct(sum(1 for t in ts if t['hit']), len(ts))))
        for dd in range(5):
            ts = [t for t in tm if t['date'].weekday()==dd]
            if ts: dow.append(dict(d=dd, n=len(ts), r=pct(sum(1 for t in ts if t['hit']), len(ts))))
        for dd in range(5):
            for h in sorted(HOUR_W):
                ts = [t for t in tm if t['date'].weekday()==dd and t['hour']==h]
                if len(ts) >= 8: cell.append(dict(d=dd, h=h, n=len(ts), a=sum(1 for t in ts if t['hit']), r=pct(sum(1 for t in ts if t['hit']), len(ts))))
        BB['a']['timing'][m] = dict(hour=hour, dow=dow, cell=cell)
        # ---- dist (premium per bound deal, pipeline wins) ----
        ps = sorted(d['prem'] for d in won_m)
        byrm = Counter(); 
        for d in won_m: byrm[d['rm']] += d['prem']
        shares = sorted([v/sum(ps) for v in byrm.values()], reverse=True) if ps else []
        BB['a']['dist'][m] = dict(p10=rnd(pctl(ps,.1),0), p25=rnd(pctl(ps,.25),0), med=rnd(pctl(ps,.5),0), p75=rnd(pctl(ps,.75),0), p90=rnd(pctl(ps,.9),0),
                                  p99=rnd(pctl(ps,.99),0), max=rnd(max(ps),0) if ps else 0, mean=rnd(sum(ps)/len(ps),0) if ps else 0, lor=lorenz(ps), gini=gini(ps),
                                  top5share=pct(sum(ps[-5:]), sum(ps)), sellers=len(byrm), top2=pct(sum(shares[:2]),1), top10=pct(sum(shares[:10]),1),
                                  hhi=int(round(sum((100*s)**2 for s in shares))))
        wins_per = [r['won'] for r in rows]
        bins = [sum(1 for w in wins_per if w==0), sum(1 for w in wins_per if w==1), sum(1 for w in wins_per if w==2), sum(1 for w in wins_per if w==3),
                sum(1 for w in wins_per if 4<=w<=5), sum(1 for w in wins_per if 6<=w<=8), sum(1 for w in wins_per if w>=9)]
        BB['a']['hist'][m] = dict(bins=bins, n=len(rows), med=median(wins_per), mean=rnd(sum(wins_per)/len(rows)), sd=rnd(st.pstdev(wins_per)), min=min(wins_per), max=max(wins_per))
        # ---- cycle times, stall, insurers ----
        cyc = {}
        for key, lab, f, t_ in [('contact','Lead to first contact','created','contacted'),('meet','Contact to intro meeting','contacted','meet'),
                                ('sched','Meeting to schedules received','meet','sched'),('prop','Schedules to proposal presented','sched','prop'),('win','Proposal to bound','prop','dec')]:
            xs = [(d[t_]-d[f]).days for d in deals if d[f] and d[t_] and inm(d[t_], m) and (key!='win' or d['won'])]
            cyc[key] = dict(label=lab, n=len(xs), **quart(xs))
        BB['a']['cyc'][m] = cyc
        sm = [d for d in deals if d['sched'] and inm(d['sched'], m) and d['sched'] <= CUT - dt.timedelta(days=WIN_P)]
        stalled = [d for d in sm if not within(d['sched'], d['prop'], WIN_P)]
        never = [d for d in sm if not d['prop']]
        decided = [d for d in deals if d['prop'] and d['dec'] and (d['won'] or d['lost']) and inm(d['dec'], m) and d['sched']]
        fast = [d for d in decided if (d['prop']-d['sched']).days <= WIN_P]; slow = [d for d in decided if (d['prop']-d['sched']).days > WIN_P]
        fw = pct(sum(1 for d in fast if d['won']), len(fast)); sw = pct(sum(1 for d in slow if d['won']), len(slow))
        allsm = [d for d in deals if d['sched'] and inm(d['sched'], m)]
        BB['a']['stall'][m] = dict(sched=len(sm), sched_all=len(allsm), stalled=len(stalled), never=len(never), stalledpct=pct(len(stalled), len(sm)), fast_n=len(fast), fast_win=fw, slow_n=len(slow), slow_win=sw,
                                   prize_wins=rnd(len(stalled)*max(0,fw-sw)/100), stalled_prem=round(sum(d['prem'] for d in stalled),2), window=WIN_P,
                                   matured_to=(CUT - dt.timedelta(days=WIN_P)).isoformat())
        ins = {}
        for d in deals:
            for q in d['quotes']:
                if inm(q['req'], m):
                    ins.setdefault(q['ins'], []).append((q['back']-q['req']).days)
        BB['a']['ins'][m] = sorted([dict(k=k, n=len(v), med=median(v), p75=rnd(pctl(v,.75)), over10=pct(sum(1 for x in v if x>10), len(v))) for k,v in ins.items()], key=lambda x: x['med'])
        # ---- audit ----
        A = dict(touches=sum(r['touches'] for r in rows), attempts=len(tm), svc=sum(r['svc'] for r in rows), leads=sum(r['leads'] for r in rows), contacted=sum(r['contacted'] for r in rows), meet=sum(r['meet'] for r in rows),
                 sched=sum(r['sched'] for r in rows), mkt=sum(r['mkt'] for r in rows), prop=sum(r['prop'] for r in rows), won=sum(r['won'] for r in rows),
                 prem=round(sum(r['prem'] for r in rows),2), comm=round(sum(r['comm'] for r in rows),2), wd=WD[m],
                 bwon=sum(v['won'] for v in desks.values()), bprem=round(sum(v['prem'] for v in desks.values()),2), bcomm=round(sum(v['comm'] for v in desks.values()),2),
                 med=BB['a']['dist'][m]['med'], mean=BB['a']['dist'][m]['mean'], top5=round(sum(ps[-5:]),2), mx=BB['a']['dist'][m]['max'],
                 units=sum(r['units'] for r in rows), book=sum(r['book'] for r in rows), bookprem=round(sum(r['bookprem'] for r in rows),2), lapses=sum(r['lapses'] for r in rows),
                 open=sum(r['open'] for r in rows), openprem=round(sum(r['openprem'] for r in rows),2), stale=sum(r['stale'] for r in rows),
                 lost=len(lost_m), noreason=sum(1 for d in lost_m if not d['reason']), nreasons=BB['e'][m]['nreasons'],
                 c_n=sum(r['c_n'] for r in rows), c_d=sum(r['c_d'] for r in rows), s_n=sum(r['s_n'] for r in rows), s_d=sum(r['s_d'] for r in rows),
                 p_n=sum(r['p_n'] for r in rows), p_d=sum(r['p_d'] for r in rows), w_n=sum(r['w_n'] for r in rows), w_d=sum(r['w_d'] for r in rows),
                 cohort=cohort_funnel(deals, m, {r['rm'] for r in rows}),
                 src={k:v for k,v in Counter(d['src'] for d in deals if inm(d['created'], m)).items()},
                 srcv={k:round(v,2) for k,v in srcv.items()})
        BB['a']['audit'][m] = A
        # ---- Q ledger ----
        QR = {}
        for r in rows:
            od = r['once_unc']; odc = od*a2/100
            s_gap = max(0, r['contacted']*(bm['schedrate']['med']-r['schedrate'])/100) if r['leads']>=10 else 0
            p_gap = max(0, r['sched']*(bm['proprate']['med']-r['proprate'])/100) if r['leads']>=10 else 0
            c_gap = max(0, r['days']*(bm['tpd']['med']-r['tpd'])) if r['leads']>=10 else 0
            pe = odc*bm['schedrate']['med']/100*bm['proprate']['med']/100 + s_gap*bm['proprate']['med']/100 + p_gap
            QR[r['rm']] = dict(od=od, od_contact=rnd(odc), s_gap=rnd(s_gap), p_gap=rnd(p_gap), stale=r['stale'], c_gap=rnd(c_gap,0), pe=rnd(pe), desk=r['desk'])
        QD = {}
        for k in DESKS:
            rr = [r for r in rows if r['desk']==k]
            v = desks[k]
            QD[k] = dict(od=sum(QR[r['rm']]['od'] for r in rr), od_contact=rnd(sum(QR[r['rm']]['od_contact'] for r in rr)), s_gap=rnd(sum(QR[r['rm']]['s_gap'] for r in rr)),
                         p_gap=rnd(sum(QR[r['rm']]['p_gap'] for r in rr)), stale=sum(QR[r['rm']]['stale'] for r in rr), c_gap=rnd(sum(QR[r['rm']]['c_gap'] for r in rr),0),
                         pe=rnd(sum(QR[r['rm']]['pe'] for r in rr)), rms=len(rr), touches=v['touches'], leads=v['leads'], won=v['won'], prem=v['prem'],
                         contactrate=v['contactrate'], schedrate=v['schedrate'], proprate=v['proprate'], stalepct=v['stalepct'])
        BB['q'][m] = dict(rms=QR, desks=QD, a2=a2, wd=WD[m])
    # ---- pooled speed-of-proposal effect (both months, matured deals) ----
    dec_all = [d for d in deals if d['prop'] and d['dec'] and (d['won'] or d['lost']) and d['sched'] and (inm(d['dec'],'jul') or inm(d['dec'],'aug'))]
    fa = [d for d in dec_all if (d['prop']-d['sched']).days <= WIN_P]; sl = [d for d in dec_all if (d['prop']-d['sched']).days > WIN_P]
    BB['a']['stall']['both'] = dict(fast_n=len(fa), fast_win=pct(sum(1 for d in fa if d['won']), len(fa)), slow_n=len(sl), slow_win=pct(sum(1 for d in sl if d['won']), len(sl)),
                                    test=tests_2p(sum(1 for d in sl if d['won']), len(sl), sum(1 for d in fa if d['won']), len(fa)))
    for m in MONTHS:
        st_ = BB['a']['stall'][m]; Am = BB['a']['audit'][m]; bmw = pct(Am['w_n'], Am['w_d']) or BB['d'][m]['bm']['winrate']['med']; pm = BB['a']['dist'][m]['med']
        Am['wrate'] = bmw
        st_['prize_wins_pooled'] = rnd(st_['stalled']*max(0, BB['a']['stall']['both']['fast_win']-BB['a']['stall']['both']['slow_win'])/100)
        st_['prize_prem'] = round(st_['prize_wins_pooled']*pm, 2)
        for k,v in BB['q'][m]['rms'].items(): v['re'] = round(v['pe']*bmw/100*pm, 2)
        for k,v in BB['q'][m]['desks'].items(): v['re'] = round(v['pe']*bmw/100*pm, 2)
    # ---- X: month-on-month ----
    J = {r['rm']:r for r in rmrows['jul']}; Au = {r['rm']:r for r in rmrows['aug']}
    keys = ['tpd','contactrate','tpl','schedrate','proprate','winrate','stalepct','tt_prop','noreason','touches','leads','contacted','sched','prop','days','won','prem','comm']
    delta = []
    for rm in sorted(set(J)|set(Au)):
        j, a_ = J.get(rm), Au.get(rm)
        row = dict(rm=rm, desk_j=j['desk'] if j else None, desk_a=a_['desk'] if a_ else None, moved=bool(j and a_ and j['desk']!=a_['desk']), active_both=bool(j and a_))
        for k in keys:
            jv = j[k] if j else None; av = a_[k] if a_ else None
            row['j_'+k] = jv; row['a_'+k] = av
            row['d_'+k] = rnd((av or 0)-(jv or 0), 2) if (j and a_ and jv is not None and av is not None) else None
        delta.append(row)
    dx = {}
    for k in DESKS:
        vj, va = BB['d']['jul']['desks'][k], BB['d']['aug']['desks'][k]
        dx[k] = {f: dict(j=vj[f], a=va[f], d=rnd(va[f]-vj[f], 2)) for f in ['touches','rms','leads','contacted','contactrate','sched','prop','proprate','won','prem','stalepct','winrate']}
    BB['x'] = dict(delta=delta, joiners=sorted(set(Au)-set(J)), leavers=sorted(set(J)-set(Au)), desks=dx, bmJ=BB['d']['jul']['bm'], bmA=BB['d']['aug']['bm'])
    # ---- tests ----
    AJ, AA = BB['a']['audit']['jul'], BB['a']['audit']['aug']
    BB['a']['tests'] = dict(contact=tests_2p(AJ['c_n'], AJ['c_d'], AA['c_n'], AA['c_d']),
                            sched=tests_2p(AJ['s_n'], AJ['s_d'], AA['s_n'], AA['s_d']),
                            prop=tests_2p(AJ['p_n'], AJ['p_d'], AA['p_n'], AA['p_d']),
                            win=tests_2p(AJ['w_n'], AJ['w_d'], AA['w_n'], AA['w_d']))
    # ---- decomposition of the change in average bound premium, by segment ----
    def segstats(m):
        w = [d for d in deals if d['won'] and inm(d['dec'], m)]
        n = len(w) or 1
        out = {}
        for s in SEGMENTS:
            ws = [d['prem'] for d in w if d['seg']==s]
            out[s] = (len(ws)/n, (sum(ws)/len(ws)) if ws else 0)
        return out
    sj, sa = segstats('jul'), segstats('aug')
    rate = sum(sj[s][0]*(sa[s][1]-sj[s][1]) for s in SEGMENTS)
    mix = sum((sa[s][0]-sj[s][0])*sj[s][1] for s in SEGMENTS)
    inter = sum((sa[s][0]-sj[s][0])*(sa[s][1]-sj[s][1]) for s in SEGMENTS)   # rate + mix + inter == avg_a - avg_j exactly
    BB['a']['dec'] = dict(rate=rnd(rate,2), mix=rnd(mix,2), inter=rnd(inter,2), avg_j=BB['a']['dist']['jul']['mean'], avg_a=BB['a']['dist']['aug']['mean'])
    BB['meta'] = dict(seed=SEED, built=dt.date.today().isoformat(), cut=CUT.isoformat(), deals=len(deals), touches=len(touches), windows=dict(sched=WIN_S, prop=WIN_P, win=WIN_W), stale_days=STALE_DAYS, note='SIMULATED DUMMY DATA — fictional RMs, illustrative only')
    return BB

def inject(BB, path):
    src = open(path, encoding='utf-8').read()
    blob = 'const BB=' + json.dumps(BB, separators=(',',':'), ensure_ascii=False) + ', D=BB.d, E=BB.e, X=BB.x, AN=BB.a, Q=BB.q;'
    new, n = re.subn(r'/\*@@BB@@\*/.*?/\*@@/BB@@\*/', lambda _: '/*@@BB@@*/' + blob + '/*@@/BB@@*/', src, flags=re.S)
    if n != 1: sys.exit('build_data.py: @@BB@@ markers not found exactly once in ' + path)
    open(path, 'w', encoding='utf-8').write(new)
    print(f'wrote {path}: {len(blob):,} chars of data · {BB["meta"]["deals"]} deals · {BB["meta"]["touches"]} touches')

if __name__ == '__main__':
    BB = build()
    if '--json' in sys.argv:
        print(json.dumps(BB, indent=1, ensure_ascii=False)); sys.exit()
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    inject(BB, os.path.join(here, 'index.html'))
