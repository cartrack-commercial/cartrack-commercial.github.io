# Cartrack Insurance — Commercial Division · working memory

Handoff notes so a fresh session starts informed. Anne (annekruger3010@gmail.com)
runs the Cartrack Insurance Commercial division: three internal web apps + hand-built
insurance **quote comparisons** for the RMs.

---

## The three apps (all single-file HTML, auto-deploy on push to `main` via GitHub Pages)

| App | Repo | Lives at |
|---|---|---|
| **Launcher** (this repo) | `cartrack-commercial/cartrack-commercial.github.io` | `cartrack-commercial.github.io` |
| **RM System** (pipeline, clients, payroll, Command View) | `cartrack-commercial/cartrack-rm-system` | `…github.io/cartrack-rm-system/` |
| **Premium Comparison portal** | `cartrack-commercial/cartrack-premium-comparison` | `…github.io/cartrack-premium-comparison/tool.html` |

- **Deploy = commit + push to `main`.** No build step, no code to paste — Pages rebuilds in ~1–2 min. The apps in `/workspace/<repo>` are the working clones (add via `add_repo` if not in session scope).
- **Version stamp:** bump `const APP_VERSION='v2026.MM.DDx'` in the RM app on every push (shows on the sign-in card so support knows what a phone is running).
- **Design system for the APPS:** "Compliance DS" — Saira (headings) + IBM Plex Sans (body) + IBM Plex Mono (mono), near-black `#0B0C0F` ink + brand orange `#F47735`. Home-screen icons = white Cartrack arrow on `#0B0C0F` (in each repo's `assets/`).

### RM System notes
- Supabase-backed (anon key in client; **RLS is the only protection — payroll holds salaries, confirm RLS is locked down**; no server-side auth, PIN gate is client-side only). Tables: `deals`, `portfolio`, `payroll`, `config`, `orgs`.
- Saves are merge-safe per-row upserts; durable localStorage outbox for mobile resilience.
- **Active Clients carry `policy` (policy no.), `insurer` (who the commission statement comes from) and `brokerFee`** — editable in the client modal (RM) and as Command View columns (management). Added 28 Jul 2026 on Lourie's request.
- **Payroll formula: `payout = premium × commRate% + brokerFee ÷ 2`.** Confirmed by Anne 28 Jul: the split is **always half**, and the broker fee is **always monthly recurring** (not once-off) — it repeats every payroll month like the premium. Constant `BROKER_FEE_SHARE=0.5`. The payroll table shows the fee and the half as separate columns so an RM query can be answered by pointing at the row.
- ⚠️ **`broker_fee` needs a DB column:** `alter table portfolio add column if not exists broker_fee numeric default 0;` — the app tolerates its absence (learns from server rows, strips the field on a rejected write) so saves never break, but the fee won't persist until it's run.
- **Command View is management-editable:** Brendan/Lourie can correct any RM's deal (tap → modal → `saveRM(owner)`) and any book premium (inline field → `savePortfolio(owner)`) — writes to the owning RM's shared row, pulls through to everyone. Payroll already saves on blur.

### Premium Comparison portal notes
- Upload current schedule + competitor quotes → in-browser extraction (pdf.js/xlsx self-hosted in `assets/vendor/`; tesseract OCR lazy from CDN) → seeded editable **Review** → **Report**.
- Report design matches the PDF packs (Space Grotesk/Space Mono/Libre Franklin, dark hero). Has a **schedule audit** (RM view) that flags telematics-waiver, fund forfeiture, credit shortfall, GIT, cross-border. **Client view vs RM view** toggle.
- **Fleet catalogue parser + reconcile-or-total guard:** itemises only when lines sum to the stated total, else keeps the exact total for the RM to itemise. Auto-splits multiple insurers into separate columns.
- Honest limit: can't match hand-work on messy/photo schedules or cover-gap judgment.

---

## How to do a quote comparison (the method the RMs rely on)

1. **Extract every schedule.** `pdftotext -layout` for digital PDFs; **Read the pages as images** when it's an iPhone/CamScanner photo (no text layer — e.g. Twin Trans current). Never guess a figure off a faded scan.
2. **Reconcile to the cent.** Compare on the **all-in monthly (VAT + fees + SASRIA included)** figure. ⚠️ SA schedules often show a "Total Premium" that is *before* fees/SASRIA/VAT — find the true all-in (e.g. WesKaap Santam headline R34,091 vs real all-in **R43,946.83**).
3. **Line-for-line**, current vs each proposal, with a per-line verdict + plain-English "why".
4. **Recommendation logic:** *dearer-but-better = still move; only a genuine cover GAP justifies holding.* Credit a proposal for extra cover the current lacks (don't treat added cover as just "more expensive").
5. **The decisive cover varies by client type** — find it and lead with it:
   - tanker / dangerous-goods hauler → **pollution / environmental liability** (Twin Trans: King Price dropped it)
   - bus / passenger transport → **passenger liability (fare-paying)** (WesKaap: both proposals weakened it)
   - general transport fleet → **third-party liability limit, excess structure, telematics excess waiver**
6. **Split deliverables:** RM-internal pack (findings, questions to the underwriter) vs a clean client-facing version. Tone = peer briefing, not schooling.
7. **Compliance:** replacing a policy → any reduction in cover (and fund forfeiture) **must be disclosed to the client in writing** before they decide (Record of Advice).

### Insurance structure (keep these straight)
- **Broker** = the intermediary who advises/places (Cartrack Insurance Agency, **FSP 17266** — us; PSG / One Financial / Santam Direk = incumbents we replace).
- **UMA (Underwriting Manager)** = sets terms, runs claims (Merx FSP 42991; VAPS Insurance Underwriters FSP 46264; Alpha).
- **Insurer** = carries the risk (Old Mutual Insure behind Merx; **King Price behind VAPS**; Guardrisk behind Alpha; Renasa behind Ownsurance; Santam direct).
- So "King Price / VAPS" or "Merx / Old Mutual" is **one** proposal, not two.

### PDF pack builder (comparison deliverables)
- **THE build system is the `/cartrack-proposal` skill — now committed IN THIS REPO at
  `.claude/skills/cartrack-proposal/`** (merged from Anne's Mac, 28 Jul 2026). It contains
  `SKILL.md` (component cheat-sheet), `build.py`, `assets/template.html` (client proposal),
  `assets/playbook-template.html` (RM playbook), `cartrack.css`, Saira + IBM Plex fonts and
  all logos. `build.py` auto-detects Chrome (Mac) / Playwright Chromium (web sessions) —
  works in BOTH places, so full comparisons + branded PDFs can be done end-to-end in any chat.
  Usage: copy a template to `<name>_content.html`, edit, then
  `python3 .claude/skills/cartrack-proposal/build.py <name>_content.html <out>.pdf --title "…" [--client-logo x.png]`.
  Same skill also lives at `~/.claude/skills/cartrack-proposal/` on the Mac — if either copy is
  improved, sync the other.
- Older generation kit (Libre Franklin era, ALW pilot): `cartrack-premium-comparison/pack-builder/`
  (HANDOFF.md there). Legacy fonts `spacegrotesk/spacemono/librefranklin` remain in
  `cartrack-premium-comparison/assets/`.
- Afrikaans RM messages: informal, mix in English words (Anne's standing preference). Figures must NOT be monospace — Space Grotesk (display) / Libre Franklin tabular (figures) / Space Mono (labels only).

---

## Client status (as at Jul 2026)
- **Waste Carriers & Nutri Humus** (228-vehicle fleet). RM: **Jean (he)**. **Compare CURRENT Merx UM / Old Mutual Insure `MRXP03339` (via PSG) vs PROPOSED OWNsurance/Renasa "OwnRship"** quote **amended 9 Jul 2026** (⚠️ ignore the stale 8-Jul quote at R476,436.56). Files: OneDrive → `…/Waste Carriers quotes- Jean/`. Extract with `pdftotext` (Mac pip is PEP-668 blocked; pdftotext works).
  - **Headline (monthly):** Current **R504,844.03** (includes a **R73,088.68/mo reserve fund**, 20% reserve, cash-back if loss ratio ≤60%) vs OWNsurance **R450,734.71**. **Hard, UNCONDITIONAL saving = R54,109.32/mo = R649,311.84/yr.** Alpha/Guardrisk **R458,686.13** was rejected (no cash-back).
  - **The fund (everyone trips on this):** the quote's "Annual savings **R1,768,416.95**" is NOT a saving vs Merx — it's the annual contribution into the **client's OWN savings fund** (60/40 OFC split). Reconciles with **SEQUENTIAL** commission deduction: vehicle premium R308,462.75 × (1−0.09 binder) × (1−0.125 broker) × 0.60 fund × 12 = **R1,768,416.95**. Additive 21.5% (→R1,743,431) is WRONG. Cartrack remuneration = broker 12.5% **then** binder 9%, one after the other (~20.375% of motor premium). First claims paid from fund with **no excess**; unused fund returns to client 30 days after each 12-month period.
  - **Effective annual cost by claims scenario (the honest way to show the win, not a single headline):** 0 claims → **R3,640,400** · R1m claims → **R4,640,400** · fund fully used → **R5,408,817**. Current gross ≈ **R6,058,128**.
  - **Cover gaps to CLOSE (regressions at OWNsurance — flag every one):** Public Liability **R10m is CLAIMS-MADE** (retro 23/06/2021), absent from the OWN quote → needs matching **run-off/retro**. Cars third-party **R5m→R3.5m**. **Chemicals-load TP carve-out R2.5m**. **Credit shortfall gone** (103 financed vehicles). **Environmental/pollution EXCLUDED both sides** → place **EIL** separately. Tracking: **116 of 228 untracked (R87.57m SI)** — the Cartrack lead AND a theft/hijack precondition.
  - **THE GATE (before presenting):** get the client's **Merx loss ratio + current reserve balance** (incumbent fund may rebate if loss ratio ≤60%; 2025/26 bonus calculated ±15 Aug 2026, so exit timing matters; current period runs to 01/07/2027).
  - **Open items (deal gated on these):** written query to OWNsurance — pool schedule, 40%-split confirmation, **GIT option (GIT is NOT in this quote, R0.00; R1.77m baseline)**. Merx underwriter questions still outstanding too (telematics waiver / is Cartrack approved, excess table, loss ratio + fund forfeiture, tracking on 116 untracked, pollution, credit shortfall, territorial).
  - Telematics side-note: excess-waiver finding ~**R238,990/truck** is Brendan→Bret's units track — kept separate.
  - **Deliverables built (regen via `/cartrack-proposal`; sources in `05 Builds & Code/Claude Code/`):** line-by-line **docx** (section H = 10 written confirmations); **client proposal PDF** (…CLIENT); **RM playbook PDF** (…INTERNAL - RM ONLY). **Skill + OneDrive live on Anne's Mac — render branded PDFs in the LOCAL session, never rebuild the design.**
- **Twin Trans** (Santam vs King Price/VAPS): done. King Price cheaper but drops pollution + halves third-party (R5m→R2.5m, fire/explosion R1m) — dangerous for a fuel tanker.
- **Wes-Kaap Busdiens CC** (Vredenburg; t/a WES-KAAP TOERE — daily commuter, WCED scholar transport, charter; ±R13.1m fleet, 34 buses). RM: **Bronwyn Fouche** (surname confirmed by Anne 28 Jul; still need her direct email for the proposal contact card — packs currently carry the Rosebank switchboard + insurance@cartrack.com). Santam current vs Old Mutual (ONE) vs King Price (VAPS). **Went through 3 rounds — full detail in `deal-notes/weskaap-busdiens-build-history.md`.**
  - **Real current benchmark = Santam R37,535.20/mo** (⚠️ NOT the old R43,946.83 — bus SASRIA was stripped off the current policy in June, R6,956.59→R544.96). Pax liability R2.5m/vehicle ✓.
  - **Final standings (24 Jul):** King Price r21389 **R33,928.03** (−R3,607.17/mo ≈ −R43,286/yr) BUT pax cover is **R2.0m/event on an e-hailing RTU form** ⚠ — likely won't respond for a scheduled bus operator (the **gate**); Old Mutual .4 **R37,304.63** (−R230.57, clean **R2.5m/vehicle** ✓, genuine like-for-like); Santam current R37,535.20.
  - **Outstanding before signature:** (1) VAPS **written** confirmation pax liability responds for scheduled commuter/scholar/charter + lift to R2.5m/event; (2) OM to add unauthorised pax R2.5m; (3) client's written SASRIA sign-off (no riot cover on buses = their choice); (4) client keep/cut on KP windscreen (off → R28,408.03).
  - **Method catch-outs:** KP third-party has a **R1m fire/explosion sub-limit**; Santam prices pax liability *in the motor rate*; verify decisive cover **per item, not per summary** (that's how the KP e-hailing exclusion was caught, schedule p10). Client website weskaaptoere.co.za proves scheduled/no-e-hailing ops — cite it against KP wording.
  - Deliverables built via `/cartrack-proposal` (sources `weskaap_playbook_content.html`, `weskaap_proposal_content.html`): RM Playbook + Client Proposal (24 Jul). **Skill + files on Anne's Mac — render branded PDFs locally.**
- **Tech Tech Consulting (Pty) Ltd** (Old Mutual Insure → Bryte). RM: **Cules**. Reconciled like-for-like (identical **12 vehicles / 18 BAR / 18 electronic items**).
  - CURRENT: Old Mutual Insure, policy **PE218826COM** (Ballast Brokers / Frontline) — **R22,423.35/mo**. Source: "Marcus TECH TECH CURRENT POLICY.pdf".
  - PROPOSED: Bryte **QT1018651** — **R16,967.14/mo**. Source: "Bryte commercial quote - Tech Tech MARCUS.pdf".
  - **Saving −R5,456.21/mo (≈R65,475/yr), cheaper day one.** Two genuine **upgrades**: data reinstatement R10k→R100k (10×); liability restructured from R1m primary + separate R20m AIG CULP umbrella into a clean **R20m primary PL**, legal defence R10k→R50k, wrongful arrest R50k. **Simplifier:** two insurers (OM + AIG) → one (Bryte).
  - **Watch-outs (red-team in the playbook):** Bryte motor excess vs OM 5%/min R5,000 (confirm); liability line +R187/mo on that section; two **"TBA" registrations** (2026 BAIC B30, Suzuki EECO); confirm retail sums insured; high-value vehicles need approved tracking (**Cartrack units satisfy this**).
  - **DONE:** client 5-page branded proposal (via `/cartrack-proposal`) → "Tech Tech - Cartrack Proposal.pdf" (source `techtech_content.html`).
  - **PENDING:** RM Playbook (internal, RM-eyes-only) via the cartrack-proposal skill's `playbook-template.html` → "Tech Tech - RM Playbook.pdf" in the same folder. Skill is now in this repo (`.claude/skills/cartrack-proposal/`) so this can be built in ANY session; OneDrive originals still on Anne's Mac.
- **Powerflow Electrical** (electrical contractors, 36 Bambi Rd, Rispark; 10 vehicles, 15 employees). RM: **Cules**. 3-way done 28 Jul 2026 — all-in monthly, reconciled to the cent:
  - **Current Guardrisk / Protocol Risk Managers `PTC0000-06970`** (via Pogir Baston) **R7,408.35** · **Western `48784179`** (FSP Commercial Online) **R6,848.77** · **Natsure/Compass `COM191179`** **R6,997.56**.
  - **Recommendation: Natsure (−R410.79/mo ≈ −R4,929/yr)** — NOT the cheapest. Decisive cover for an electrical contractor = **liability**: Natsure gives **Broadform R20m ground-up** (replaces R2m primary + R20m excess layer whose retro dates are mismatched: PL 1/08/2024 vs Ext PL 1/09/2024), **spread of fire R500k→R1m**, **gratuitous advice R100k** added, passenger/unauthorised passenger held at **R5m**.
  - **Why Western is benched despite being R148.79/mo cheaper:** PL **retro date 01/10/2025 vs current 01/08/2024 = 14 months of past work uninsured** (claims-made!); passenger + unauthorised passenger **R5m→R2.5m**; and its R25m umbrella carries a **minimum-underlying-limit condition (EL R2.5m, products R2.5m)** against actual underlying of R1m EL / nil products → cannot attach.
  - **Gates before binding Natsure:** (1) **Broadform retro date is NOT stated on the quote** — pin to 01/08/2024 or earlier; (2) contents quoted "**excluding stock and computers**", no electronic-equipment section → schedule the computers; (3) **motor security wording self-contradicts** (clause 1: <R350k needs only immobiliser; closing para: all theft cover subject to VESA tracker) — all 10 vehicles are <R350k → **10-unit Cartrack lead**; (4) welding claims excluded; (5) company reg number blank on BOTH quotes.
  - **Defective workmanship / products liability EXCLUDED on all three** — the client's core exposure; ask both insurers to price it.
  - Motor: same SI R1,232,150 all three; own damage R5,195.25 (cur) / R5,080.64 (W) / R4,649.90 (N). Natsure theft excess worsens to 10% min R5,000.
  - **Deliverables built 28 Jul (this repo's skill):** `powerflow_proposal_content.html` + `powerflow_playbook_content.html` → client proposal PDF + RM playbook PDF. Afrikaans WhatsApp sent to Anne.
- **Hamisa Group** (one client group, `stephen@hamisagroup.co.za`, all currently at **Inscon Hawkins & Associates**). RM: **Bronwyn Fouche** (= the Bronwyn on Wes-Kaap). ⚠️ Both Bryte quotes spell it **"Bronwan"** — **"Bronwyn" is correct** (confirmed by Anne 28 Jul); use the correct spelling on all deliverables and have the quotes corrected. Three entities, group total **R92,831.87/mo**:
  - **Hamisa Safety Equipment Supplies** (PPE to mining; Danskraal/Ladysmith, Lanseria, Witbank). Current **Infiniti `BEYOND-3744-0000169` R18,432.07** vs proposed (Bryte-titled, see below) **R16,092.75** → **−R2,339.32/mo ≈ −R28,072/yr**. ✅ DONE 28 Jul — client proposal + RM playbook built (`hamisa_safety_*_content.html`).
    - Saving comes from re-rating (fire −R1,190.70, theft −R690, electronic equipment −R550.47), NOT cover cuts: GIT held **R2,750,000**, fleet **R1,406,123 exact match** (Toyota FBRE20, VW Caddy Cargo, Isuzu D-Max), BAR + accidental damage identical; office contents R876,053→R993,541 and theft R200,000→R232,500 both UP.
    - ⚠️ **PL is R5m PER ADDRESS on the current policy** (Danskraal retro 05/08/2025, Witbank retro 11/04/2024) — the index summary showing "R10,000,000" is the 2-address total, NOT a single limit. Proposed = R5m across ALL premises but **adds Lanseria, which has no PL today**. Per-event limit unchanged; what's lost is per-address stacking.
    - **Fix before binding:** (1) retro dates carried across (quote resets to inception); (2) electronic equipment **R288,555 → reinstate R308,555**; (3) motor third-party **R5m → back to R10m** (contingent liability does improve R1m→R5m).
  - **Hamisa Engineering Group & Nala Trust** (engineering/general works/petrol station/car wash/PPE; 9 addresses incl. Harmony Gold Kusasalethu + Tshepong shafts). Current **Infiniti `BEYOND-M-3520-0000140` R56,652.48** vs **Bryte `QT1019726` R46,808.14**. ⛔ **GATED: the current schedule is printed 24/03/2025 (Version 18) and the anniversary is 01/10 — 16 months stale, so the −R9,844 headline is unreliable. Get the post-Oct-2025 schedule.** (That PDF is a scan with no text layer — read pages as images.) PL R20m held ✓.
  - **Kgahlisa General Supplies (Pty) Ltd** (fuel retail service station + gas exchange, Botshabelo). Current **Hollard via Inscon binder `INSCON-3518-0000012` R17,747.32** vs **Petrosure UM / Old Mutual Insure R16,394.21**. ⛔ **GATED — quote is NOT like-for-like:** covers **4 of 7 vehicles** (missing Mitsubishi RBF14CA-3FP70 R854,601, VW Caddy4 HL56TBGP R227,900, VW Polo TSI KX77CJGP R314,900 = **R1,384,003 unquoted**), and **Motor Traders Internal R3,750,000 → R250,000 (−93%)** on a forecourt with customers' cars in custody. Credit: adds **Forecourt Negligence/Contamination Liability R1m**. Quote names broker as "FSP Solutions" — confirm it's ours.
  - **Common to BOTH Bryte quotes:** liability + EL **retroactive date = "inception date of policy"** (claims-made → wipes prior work); **products liability/defective workmanship = R0**; every page footer reads *"Quotation — Hollard Insurance Company"* on BrokerBüddy letterhead despite the Bryte title → **confirm the actual insurer**; both subject to survey + claims experience.
  - **Deliverables:** `Hamisa Group - outstanding queries.md` (section A = client/Inscon for the Engineering schedule; B = Petrosure re Kgahlisa fleet + motor traders; C = insurer re retro dates, products liability, insurer identity).
- **Mike Lawlor** (private client of RM **Hein van Rooyen**, hein.vanrooyen@cartrack.com — Nat. Sales Manager). Two policies, sent 28 Jul: (a) **properties polis** quoted via TRQ/Tranquille — reconciled: R11,763.02 → R11,564.35, catch = Public Liability R50m occurrence → R20m claims-made; (b) **private polis** 3-way, comparison DONE 28 Jul:
  - Insured: Mike & Candice Lawlor, Meyersdal. (Mike's ID = the current-CIB PDF password — in `Mike_Password.docx` in the deal folder / chat uploads; do NOT store it here.) 3 houses (main R30.36m, Danabaai R6.14m, Vaal Marina R2.38m), contents R6.67m, 5 vehicles: Porsche 911 GT3 RS '19 (R4m + **R1m Weisig Package** = R5m, Agreed Value, 3,500km/yr), RR Sport SDV6 '16, BMW M5 F90 '18 (Wesbank, Cartrack CT1 fitted), RR Sport D350 '23 (Tracker), '68 Dodge Charger (R2m Agreed Value).
  - **All-in monthly: Current CIB\V567478 R20,879.02 · Hollard Prestige QT1017001 (via BrokerBuddy) R18,613.71 · Santam Executive STM-CAR0313-STMEXE-0288041 R19,886.93.** Quote passwords are in Hein's 28-Jul email (not stored here).
  - **Recommendation: Hollard** (−R2,265.31/mo = −R27,183.72/yr, like-for-like buildings R38.88m, Agreed Value both collectors, R30m liability). Fix first: add R1m Weisig to Porsche (quote shows R4m), pin Dodge basic excess ("Unspecified"), early-warning trackers required ALL vehicles in 14 days (= Cartrack lead).
  - **Santam is a trap as quoted:** buildings cut to R26.38m (main R20m, Danabaai R4m → average applies), collectors on Retail basis, Dodge mis-coded "1996 Base Coupe" (real: 1968 Charger). Its genuine win = excesses (R5,500 vs CIB R200k on Porsche/Dodge, R50k others; Hollard R150k Porsche) + theft-excess waiver with approved tracker. Only re-quote rebuilt to R38.88m + Agreed Value if client prioritises excess.
  - All-risks gap all three: no itemised valuables (CIB has R300k out-of-home + locked-safe warranties; Hollard 20% WWC on contents; Santam ALL RISKS = not taken). Ask client re jewellery/watches.
  - Claims history (for ROA): 2021 geyser R10,400; 2021 lightning R107,693. Replacing CIB ⇒ written disclosure of any reductions (ROA).
  - **PENDING:** client proposal PDF + RM playbook (via repo skill) + written questions to Hollard & Santam.

## Compliance work (FSP 17266) — separate from the quote comparisons

**Hard facts to remember:**
- **Brendan AND Jennie ("Jenny") Allen are BOTH Key Individuals.** Either can sign as KI.
  Brendan is also Head of Company and **Anne's husband**. Juan Marais = Director (signed the
  Telesure Partner Application Questionnaire).
- **Anne has NO Cartrack email address and NO access to any Cartrack internal system.**
  All mail to Jenny, Brendan or anyone at Cartrack goes from **annekruger3010@gmail.com**. Never
  assume a Cartrack address, a VPN, an intranet, HR or group IT is reachable — it is not.
- **ReadyState / Thought Lab (Huntley Smith): Brendan signed NOTHING and is NOT proceeding.**
  Verified in their own PDFs: no IP clause, no copyright notice, no non-compete, no
  non-circumvention, no confidentiality marking. The only NDA reference is "mutual NDA signed
  before the onboarding session" — never reached. So building an in-house equivalent carries no
  contract risk from them. Real risks are POPIA on rep data, Anne's FAIS positioning (she is not
  an approved CO or KI — she supports the KI, she does not perform the compliance function), and
  who owns the copyright in what she builds if she is not an employee.

### Telesure (TIH) Outsource Partner Due Diligence — report received 22 Sep 2026
Compiled by **Gugu Mkhize**, monitoring period **August 2026**. Overall **Limited Concern**;
arrangement **NOT material** under Joint Standard 1 of 2024. No sanctions, suspensions or
enforcement. Scoreboard: No Concern 26 · Limited Concern 4 · Major Concern 6.

⚠️ **The report uses TWO different numbering schemes** — a front checklist table (p4–p5) and a
back narrative (p21–p24). Same number means different things in each. Always say which one.
- **Front checklist §9 Complaints = 9.1–9.6, ALL SIX Major Concern.** (register 12m · 10 complaint
  samples · escalated · Ombud · list of reps who handle complaints · TCF evidence.)
- **Front checklist §6 Fit & proper: 6.3 + 6.4 Limited Concern** (rep file samples not provided).
- **Back narrative §9** = Fit and proper, rates those same rep files **Major Concern** →
  **internal contradiction, worth challenging.**
- Back narrative POPI section: No Concern **but** PAIA/Privacy approval section is *incomplete and
  unsigned*, Information Regulator refs need updating, plus data-subject rights, breach
  notification and version control. **All closeable by Anne.**
- Telesure calls the FSP **"Apex Financial Services"** twice (p1 footer, p3 summary) — their error.
- The report carries blank **"Cartrack Insurance Agency Feedback:"** boxes — respond in those.

**Root cause of the 6 Major Concerns:** Section 6 of the pack held only ONE file (the nil
complaints register). Telesure asked for six things. **Verified in sent mail: only two OSA emails
were ever sent — Section 1 on 14 Jul, and the full zip on 15 Jul. The numbered section emails
2–13 were never sent.** A nil position must be *declared*, not merely shown.

**Named roles (confirmed by Brendan via Anne, 3 Oct 2026):** Complaints Officer = **Brendan
Kruger** · Key Individuals = **Brendan Kruger + Jennie Allen** · Compliance Officer = **Daniel
Opperman** · **Ombud liaison = none appointed** → assigned to the Complaints Officer with oversight
by the other KI.
⚠️ **Brendan holds two roles (Complaints Officer AND KI)**, so "escalate to the KI" is not an
independent route for a complaint about the Complaints Officer. Those go to **Jennie Allen** (second
KI) + **Daniel Opperman** (CO). This is written into the Responsibility Schedule and flagged to
Brendan for confirmation — a due-diligence reviewer will look for it.

**Built 22 Sep to close it** (sources in scratchpad `telesure-response/`, house style + fillable):
`Nil Complaints Return and Declaration.pdf` (closes 9.1–9.4; **rebuilt 2 Oct on GCOC ss16–19**) ·
`Complaints Handling Responsibility Schedule.pdf` (closes 9.5; **names filled 3 Oct**) ·
`TCF in Complaints Handling - Evidence Map.pdf` (closes 9.6) · `POPIA and PAIA Compliance
Addendum.pdf` (closes the 3 POPI recommendations; needs **Information Officer AND KI**).
The other three need a KI signature.
**SENT 9 Oct 2026 (01:49 + 01:50), both to Brendan only.** Email 1 = forwardable pack (5 PDFs loose:
Nil Return, Responsibility Schedule, TCF Map, POPIA Addendum, Organogram). Email 2 = INTERNAL (no
attachments). ⚠️ **The 15 Jul 15:44 "by section" zip did NOT attach to Email 1** although the body
says "enclosed in the archive" — a one-line reply draft (`r3203196410834962143`) sits on that thread
for Anne to attach the zip and send. Until it goes, the archive reference is dangling.
**Outlook for Mac does not show Gmail-API drafts** — always open mail.google.com in a browser.
**"OSA Pack corrected finals.zip" (15 Jul 10:14) is NOT the pack** — it is the 31 built docs, flat,
missing the 7 evidence docs (CIPC Ann A, 2 audit reports, compliance monitoring Jun 26, AFS Ann C+D,
ISO cert) and it contains the internal OSA checklist. Only the 15:44 "by section" zip is complete.

**Supabase (RM System DB) — hard date.** Anne's 2 Oct request (thread `1a0fb9e09a2c7a57`): Cartrack
must create a Pro-plan Supabase org on a company card so the `cartrack-rm-system` project can be
transferred off her personal account. Jaden replied 5 Oct: agrees but "not sure I have the
jurisdiction" — stuck pending **Carmen / Roger**. **Her personal card is debited 13 Oct.** Self-set
9 Oct deadline missed. Chase draft created 9 Oct.

**Cannot be closed by Anne** — cyber security questionnaire (she flagged it in writing on 15 Jul),
sample rep files 6.3/6.4, 12-month backup evidence, register data corrections. All need
Brendan / Jenny / HR / group IT.

**Shareholder organogram — ⚠️ it is the WRONG DOCUMENT.** "CIA Organogram Annexure B" is a **staff
org chart** (directors → Head of Company → GSM → 7 teams, headcount 70), not a shareholding chart.
Telesure item 3.1 asks for a *shareholder* organogram (FSR Act / FAIS s8 = ownership + controlling
interest chain). That is the probable reason it was marked "not submitted" after being sent twice.
Rendered to PDF 9 Oct (`03.1 Organogram - Annexure B.pdf`, landscape, house style, source
`telesure-response/forms/organogram.html`) and sent as Annexure B — fine as a supporting doc, but
**3.1 is NOT closed. Need from Brendan: who holds the shares in Cartrack Insurance Agency (Pty) Ltd,
in what %, up to the ultimate holding company.** Then build a one-page ownership diagram. Never
assert the shareholding from memory.
Source chart has name typos reproduced faithfully (Schlebush→Schlebusch, Van Resnburg, Jacons,
baloyi, VanWyk) — flagged to Anne, not corrected without authority.

### RE5 / FAIS source material — lives in Google Drive, NOT in this repo
Anne's Drive → **My Drive / RE5** (`1tvxEft5aIhhjiBfhy3f9X8oKvu0IPrGB` — note the capital **I**,
the browser font renders it like a lowercase l and the wrong one 404s). Reachable with the Drive
MCP from any session; the scratchpad has been wiped 3× so **always re-read from Drive, never
assume local copies survive**.

| File | Drive ID | What it is | May it go in the repo? |
|---|---|---|---|
| `Re5 Task QC - 14 January 2025.pdf` | `193-G-eL-Wuhf4JV80reHBl0ZR7apqWDl` | **FSCA official qualifying-criteria matrix** — every RE5 task mapped to exact Act + section. The authoritative citation index. | ✅ Yes — regulator's published criteria |
| `RE1 RE5 Prep Guide - 14 January 2025.pdf` | `1q5XDd7FNmU8jQ-JhmdUtifd8ixtn5s59` | Official FSCA prep guide, exam mechanics | ✅ Yes |
| `F5 Academy - RE1 Study Guide - RE5 Online - Jan 2025 update.pdf` | `1U4vaD5HH0gYEvf9gyfFoa0kYsJKpRBUJ` | Third-party study guide, covers **both RE1 and RE5** | ⛔ **NO** |

⚠️ **Copyright boundary — hold this line.** The F5 guide reads *"© 2024 RE5 Online, a division of
F5 Academy. You may print this guide to use as your study material. You may not reproduce,
distribute, rebrand or edit it."* Committing it (or chunks of its prose) to this repo is
distribution. The split:
- **FSCA Task/QC matrix** → regulator's published criteria. Build the compliance citation map from this.
- **Statutory text** (Act / GCOC wording the guide quotes) → it is law. Quote it freely in Cartrack documents.
- **F5's own explanatory prose** → study use only. Never in a Cartrack-facing deliverable or this repo.

**RE5 exam mechanics:** 50 questions · 2% each · 2 hours · **pass 66% (33/50)** · closed book,
nothing allowed in the room · **unlimited attempts** · no negative marking, so never leave a blank.
Every task is examined at least once (no safe skips). Question styles include **negative**
("which is NOT…") and **roman-numeral multi-select** — where careful readers lose marks.
Only the published criteria can be examined, so the Task/QC doc is a complete syllabus.

### GCOC complaints framework — verified 2 Oct 2026
⚠️ Telesure cited only **"GCOC s17"** and the first draft of our complaints documents followed them.
That is too narrow. The framework is **General Code of Conduct Part XI, ss16–19** (BN 80 of 2003 as
amended June 2020), plus **FAIS Act ss20 and 27**, and the **Ombud Council Rules for the Ombud for
Financial Services Providers, 2024**.

**s16 defines the terms — use these, not general usage:**
- **"reportable complaint"** = any complaint OTHER than one (a) upheld immediately by the person who
  received it; (b) upheld within ordinary client-query processes in **≤5 business days**; or
  (c) submitted so the provider had no reasonable opportunity to record prescribed details.
- **"upheld"**, **"rejected"**, **"compensation payment"** (provider accepts liability; excludes
  goodwill payments, contractual amounts and refunds), **"goodwill payment"** (no liability accepted).
- A provider must **categorise, record and report on reportable complaints**.

`Nil Complaints Return and Declaration.pdf` was rebuilt 2 Oct on these defined terms: 13 rows that
*derive* the reportable figure (received, less upheld-immediately, less upheld-in-5-days), plus
compensation and goodwill payments, and a confirmation that no categorisation was required because
no reportable complaint arose **while the framework exists anyway**.

### Accuracy protocol for compliance work (non-negotiable)
1. **Cite primary sources only** — Act + section number, never a summary and never Claude's memory.
2. **Two-pass rule** — build from source, then verify every citation in a separate pass.
3. **Say which numbering scheme / which document / which page** a finding comes from.
4. Use the register's **"To confirm"** status honestly; an unverified cell stays unverified.
5. **Date-stamp everything.** FAIS moves (Fit & Proper Determination 2017, Joint Standards, NFO).
6. Claude gets section numbers wrong. Every citation needs a primary-source check before it goes
   into anything signed.

### `/cartrack-compliance` skill — built 3 Oct 2026, IN THIS REPO
`.claude/skills/cartrack-compliance/` — use it for any FSP 17266 compliance document.
`SKILL.md` (entity details, accuracy protocol, build chain, the traps) ·
`references/fais-citation-map.md` (the FSCA RE5 qualifying-criteria matrix re-keyed by topic — the
authoritative index of which section governs what) · `references/gcoc-complaints.md` (ss16–19 +
the s16 defined terms, verified) · `assets/style.css` + `assets/fill.py` (the build toolkit, with
the meta-strip and redaction bugs fixed) · `templates/document.html`.

### Compliance design system
Separate from Compliance DS (the apps). Print docs = black full-bleed masthead, orange `#F47735`
rule, orange circle section badges, lilac fillable fields `#e9edf8`, meta strip, authline footer.
Cambria/Caladea + Calibri/Carlito + Consolas. Build: HTML → Chromium headless
(`/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --print-to-pdf`) → PyMuPDF widget
injection. ⚠️ The auto field-detector overreaches — exclude meta-strip and table-header captions.

## Conventions
- Commit trailers used in this project:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` + `Claude-Session: …`
- Never put the model id in commits / code / PRs (chat only).
- People's pronouns: use they/them unless stated. **Jean = he.**
