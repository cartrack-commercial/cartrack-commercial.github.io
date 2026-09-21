#!/usr/bin/env python3
"""Render the handoff markdown documents as branded Cartrack PDFs.

Pagination is measured in a real browser, not estimated: blocks are appended to
a live .page element and scrollHeight is checked after each one, so nothing is
silently clipped by the stylesheet's overflow:hidden.
"""
import base64, pathlib, sys, json, re
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from md2blocks import parse, table_html, inline

REPO = pathlib.Path('/home/user/cartrack-commercial.github.io')
SKILL = REPO / '.claude/skills/cartrack-proposal'
ASSETS = SKILL / 'assets'
sys.path.insert(0, str(SKILL))
import build as ctbuild

COLOURS = ['orange', 'teal', 'blue', 'purple', 'pink']
A4PX = 297 * 96 / 25.4            # 1122.5
LIMIT = A4PX - 10                 # safety band so nothing kisses the clip edge

DOCS = [
    dict(src=REPO / 'handoff/01-rm-system.md', out='Cartrack Handoff 1 - RM System.pdf',
         num='01', kicker='Handoff document 1 of 4', h1='The RM System',
         blurb='How the app is built, how the data is shaped, and why six pieces of it that look strange must not be removed. Every one of them exists because something was lost once.',
         stats=[('Single file', 'index.html', '3,300 lines, no build step'),
                ('Tables', '7 exist, 5 live', 'users and activity are unused'),
                ('Load bearing', '6 decisions', 'each one from a real incident')]),
    dict(src=None, out='Cartrack Handoff 2 - Security Position.pdf',
         num='02', kicker='Handoff document 2 of 4', h1='The security position',
         blurb='Stated here rather than left to be found. What is exposed today, why row level security on its own cannot close it, and the twenty hours that can.',
         stats=[('Server side auth', 'None', 'every request arrives as anon'),
                ('Protecting payroll', 'RLS only', 'and RLS alone cannot do it'),
                ('The fix', 'Supabase Auth', 'about 20 hours, do it first')]),
    dict(src=REPO / 'handoff/03-comparison-method.md', out='Cartrack Handoff 3 - Comparison Method.pdf',
         num='03', kicker='Handoff document 3 of 4', h1='The comparison method',
         blurb='The method behind every comparison this division has produced, extracted from twenty five of them. Section 3 is the part that wins deals.',
         stats=[('Built from', '25 comparisons', 'transport, schools, security, waste, retail'),
                ('Findings taxonomy', '9 classes', 'every one found on a live document'),
                ('Governing rule', 'Dearer but better', 'only a cover gap justifies holding')]),
    dict(src=REPO / 'handoff/04-portal.md', out='Cartrack Handoff 4 - Portal Build Spec.pdf',
         num='04', kicker='Handoff document 4 of 4', h1='The portal',
         blurb='What the tool does today, what it cannot do, and what to build next. The build spec is ordered by what has actually caught something on a live document.',
         stats=[('Audit rules today', '25', 'about 20 document parsers'),
                ('Last commit', '28 July 2026', '13 comparisons since, all by hand'),
                ('Build spec', '12 items', 'each one cites a live finding')]),
]
DOC2 = pathlib.Path('/tmp/claude-0/-home-user-cartrack-commercial-github-io/'
                    '18cc1d9e-a15a-5af3-a000-be6c792ba0e1/scratchpad/handoff/02-security-position-handover.md')
DOCS[1]['src'] = DOC2

OUTDIR = pathlib.Path('/tmp/claude-0/-home-user-cartrack-commercial-github-io/'
                      '18cc1d9e-a15a-5af3-a000-be6c792ba0e1/scratchpad/handoff_pdf')
OUTDIR.mkdir(parents=True, exist_ok=True)


def css_head():
    fonts = ''.join(ctbuild.font_face(f, w, ASSETS / p) for f, w, p in ctbuild.FONTS)
    return fonts + (ASSETS / 'cartrack.css').read_text()


def masthead(colour, kicker, title, badge=None):
    b = f'<span class="play-badge">{badge}</span>' if badge else ''
    return (f'<div class="masthead {colour}"><div class="eyebrow on-dark">{kicker}</div>'
            f'<h2>{title}</h2>{b}</div>')


def foot(n, doc):
    return ('<div class="foot"><div class="mark"><img src="{{CARTRACK_MARK}}">'
            f'<span>Cartrack Insurance &middot; Commercial Division &middot; {doc["kicker"]} '
            f'&middot; internal</span></div><div>{n}</div></div>')


def cover(doc, title, lede, toc):
    stats = ''.join(
        f'<div class="stat"><div class="k">{k}</div><div class="v" style="font-size:19px">{v}</div>'
        f'<div class="sub">{s}</div></div>' for k, v, s in doc['stats'])
    return f'''<div class="page cover"><div class="top">
  <div class="glow"></div><img class="wm" src="{{{{CARTRACK_MARK_WHITE}}}}">
  <div class="head-row">
    <div><div class="eyebrow ink" style="color:var(--ink-400);margin-bottom:6px">Prepared by</div>
      <img src="{{{{CARTRACK_WHITE}}}}" style="width:50mm;display:block"></div>
    <div style="text-align:right"><div class="eyebrow ink" style="color:var(--ink-400);margin-bottom:6px">Classification</div>
      <div style="color:#fff;font-family:var(--font-mono);font-size:10px;letter-spacing:.14em;
        border:1px solid rgba(255,255,255,.4);border-radius:8px;padding:7px 12px">INTERNAL</div></div>
  </div>
  <div class="lower">
    <div class="eyebrow rule" style="margin-bottom:14px">{doc['kicker']} &middot; 21 September 2026</div>
    <h1>{title}</h1>
    <p class="lead" style="color:var(--ink-300);max-width:150mm;margin-top:12px">{lede}</p>
    <div class="stat-band" style="max-width:165mm">{stats}</div>
    <div style="margin-top:10mm">
      <div class="eyebrow ink" style="color:var(--ink-400);margin-bottom:7px">In this document</div>
      <div style="columns:2;column-gap:12mm;color:var(--ink-300);font-size:9.4px;line-height:1.75;max-width:160mm">{toc}</div>
    </div>
    <div style="margin-top:9mm">
      <div class="eyebrow ink" style="color:var(--ink-400);margin-bottom:7px">The handoff pack</div>
      <div class="chips">
        <span class="chip{' dot on' if doc['num']=='01' else ''}">1 &middot; RM System</span>
        <span class="chip{' dot on' if doc['num']=='02' else ''}">2 &middot; Security position</span>
        <span class="chip{' dot on' if doc['num']=='03' else ''}">3 &middot; Comparison method</span>
        <span class="chip{' dot on' if doc['num']=='04' else ''}">4 &middot; Portal build spec</span>
      </div>
    </div>
  </div></div>
  <div class="foot legal" style="position:absolute;bottom:12mm;left:16mm;right:16mm;border:none;color:var(--ink-400)">
    Cartrack Insurance Agency (Pty) Ltd &middot; Reg 2001/008050/07 &middot; FSP 17266 &middot;
    Grosvenor Corner, 13 Keyes Avenue, Rosebank, Johannesburg &middot; internal handoff document,
    not for circulation outside Cartrack</div>
</div>'''


def flatten(sections, pre):
    """-> list of (section_title_or_None, [html strings], table markers)"""
    items = []
    if pre:
        items.append((None, pre))
    for s in sections:
        items.append((s['title'], s['blocks']))
    return items


def pack(page, css, units, doc):
    """units = [{'title':..,'blocks':[{'t':..}]}]  ->  list of page HTML strings"""
    payload = []
    for idx, (title, blocks) in enumerate(units):
        bl = []
        for b in blocks:
            if b['t'] == 'table':
                bl.append({'kind': 'table', 'head': b['head'], 'rows': b['rows'],
                           'html': table_html(b['head'], b['rows'])})
            else:
                bl.append({'kind': 'html', 'html': b['h']})
        payload.append({'title': title, 'blocks': bl})

    js = r"""
(args) => {
  const {units, limit, mast, colours} = args;
  const host = document.getElementById('host');
  const pages = [];
  const mk = (c, kick, t) => mast.replace('%C%', c).replace('%K%', kick).replace('%T%', t).replace('%B%', '');
  const sectHead = (t) => '<div class="sect" style="margin:13px 0 5px;padding-top:9px;'
      + 'border-top:1.5px solid var(--ink-150)"><div class="eyebrow rule">Section</div>'
      + '<h2 style="font-size:18px;margin-top:3px">' + t + '</h2></div>';

  // flatten into a stream: {kind:'sect'|'html'|'table', ...}
  const stream = [];
  let si = 0;
  for (const u of units) {
    if (u.title) { stream.push({kind:'sect', title:u.title, colour:colours[si % colours.length]}); si++; }
    for (const b of u.blocks) stream.push(b);
  }

  let p = null, acc = '', curColour = colours[0], curTitle = 'Continued';
  const fresh = (html) => { host.innerHTML=''; p=document.createElement('div');
    p.className='page'; p.style.height='auto'; p.style.overflow='visible';
    p.innerHTML=html; host.appendChild(p); acc=html; };
  const fits = () => p.scrollHeight <= limit;
  const tryAdd = (h) => { const b=p.innerHTML; p.insertAdjacentHTML('beforeend',h);
    if (fits()) { acc+=h; return true; } p.innerHTML=b; return false; };
  const breakPage = () => { if (acc.trim()) pages.push(acc);
    fresh(mk(curColour, 'Section &middot; continued', curTitle)); };

  for (let i = 0; i < stream.length; i++) {
    const b = stream[i];

    if (b.kind === 'sect') {
      curColour = b.colour; curTitle = b.title;
      if (p === null) { fresh(mk(b.colour, 'Section', b.title)); continue; }
      // try an inline section header plus its first real block, to avoid an orphan
      const save = p.innerHTML, saveAcc = acc;
      const nxt = stream[i+1];
      let ok = tryAdd(sectHead(b.title));
      if (ok && nxt && nxt.kind !== 'sect') {
        const h = nxt.kind === 'table'
          ? '<table><thead><tr>' + nxt.headHtml.map(x=>'<th>'+x+'</th>').join('')
            + '</tr></thead><tbody>' + nxt.rowHtml.slice(0,2).join('') + '</tbody></table>'
          : nxt.html;
        const probe = p.innerHTML;
        p.insertAdjacentHTML('beforeend', h);
        if (!fits()) ok = false;
        p.innerHTML = probe;
      }
      if (!ok) { p.innerHTML = save; acc = saveAcc;
        if (acc.trim()) pages.push(acc);
        fresh(mk(b.colour, 'Section', b.title)); }
      continue;
    }

    if (p === null) fresh(mk(curColour, 'Section', curTitle));

    if (b.kind === 'table') {
      const build = (rows) => '<table><thead><tr>' + b.headHtml.map(x=>'<th>'+x+'</th>').join('')
        + '</tr></thead><tbody>' + rows.join('') + '</tbody></table>';
      let rows = b.rowHtml.slice();
      while (rows.length) {
        const before = p.innerHTML;
        p.insertAdjacentHTML('beforeend', build(rows));
        if (fits()) { p.innerHTML = before; tryAdd(build(rows)); rows = []; break; }
        p.innerHTML = before;
        let lo=0, hi=rows.length, best=0;
        while (lo <= hi) { const mid=(lo+hi)>>1;
          p.innerHTML = before + build(rows.slice(0,mid));
          if (p.scrollHeight <= limit && mid > 0) { best=mid; lo=mid+1; } else { hi=mid-1; } }
        p.innerHTML = before;
        if (best >= 2) { tryAdd(build(rows.slice(0,best))); rows = rows.slice(best); }
        breakPage();
      }
      continue;
    }

    if (!tryAdd(b.html)) { breakPage(); tryAdd(b.html); }
  }
  if (acc.trim()) pages.push(acc);
  return pages;
}
"""
    # pre-split table html into head/rows so JS can rebuild partial tables
    for u in payload:
        for b in u['blocks']:
            if b['kind'] == 'table':
                h = b['html']
                b['headHtml'] = [inline(x) for x in b['head']]
                nc = len(b['head'])
                rr = []
                for r in b['rows']:
                    r = (r + [''] * nc)[:nc]
                    tds = []
                    for j, c in enumerate(r):
                        cell = inline(c)
                        tds.append(f'<td><div class="item">{cell}</div></td>' if j == 0 else f'<td>{cell}</td>')
                    rr.append('<tr>' + ''.join(tds) + '</tr>')
                b['rowHtml'] = rr

    mast_tpl = ('<div class="masthead %C%"><div class="eyebrow on-dark">%K%</div>'
                '<h2>%T%</h2>%B%</div>')
    return page.evaluate(js, {'units': payload, 'limit': LIMIT,
                             'mast': mast_tpl, 'colours': COLOURS})


def main():
    from playwright.sync_api import sync_playwright
    css = css_head()
    results = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--no-sandbox','--disable-dev-shm-usage'])
        pg = br.new_page(viewport={'width': 900, 'height': 1200})
        pg.set_content(f'<!DOCTYPE html><html><head><meta charset="utf-8">'
                       f'<style>{css}</style></head><body><div id="host"></div></body></html>')
        pg.wait_for_timeout(700)          # let the embedded fonts settle
        for doc in DOCS:
            md = doc['src'].read_text()
            title, pre, sections = parse(md)
            units = flatten(sections, pre)
            pages = pack(pg, css, units, doc)
            toc = ''.join('<div>' + re.sub(r'^(\d+)\.\s*', r'<b style="color:#fff">\1</b>&nbsp;&nbsp;', s['title']) + '</div>'
                          for s in sections)
            body = [cover(doc, doc['h1'], doc['blurb'], toc)]
            for i, ph in enumerate(pages, start=2):
                body.append(f'<div class="page">{ph}{foot(i, doc)}</div>')
            content = '\n'.join(body)
            work = OUTDIR / (doc['out'].replace('.pdf', '') + '_content.html')
            work.write_text(content)
            out = OUTDIR / doc['out']
            ctbuild.build(str(work), str(out), None, doc['h1'] + ' - Cartrack Insurance')
            results.append((doc['out'], len(body)))
        br.close()
    for o, n in results:
        print(f'{n:>3} pages  {o}')


if __name__ == '__main__':
    main()
