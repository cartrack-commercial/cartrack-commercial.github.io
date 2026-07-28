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

## Conventions
- Commit trailers used in this project:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` + `Claude-Session: …`
- Never put the model id in commits / code / PRs (chat only).
- People's pronouns: use they/them unless stated. **Jean = he.**
