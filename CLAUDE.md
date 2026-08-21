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
- Supabase-backed (anon key in client; **RLS is the only protection — payroll holds salaries, confirm RLS is locked down**; no server-side auth, PIN gate is client-side only). Tables: `deals`, `portfolio`, `payroll`, `config`, `orgs`, plus `users`/`activity`.
- **Which Supabase project:** ref `govvmqgpxzbqghzgcitb`, project **`cartrack-rm-system`**, under org **annekruger3010-svg's Org** — *not* the "Kruger House" org, whose project has none of these tables. SQL Editor: `https://supabase.com/dashboard/project/govvmqgpxzbqghzgcitb/sql/new`.
- Saves are merge-safe per-row upserts; durable localStorage outbox for mobile resilience.
- 🚨 **`seedIfEmpty` WRITES OVER THE SERVER ROW — it destroyed RMs' leads on 12 Aug 2026. Never let it decide off in-memory state.** The 30 Jul boot rewrite replaced its per-RM re-read with a check against already-loaded state, treating the read as pure cost. It was carrying safety: `sGet` falls back to `_mem` on a failed read, **`const _mem={}` is in-memory and empty on every page load**, so `loadRM` stores `[]` — indistinguishable from an empty table — and the seed overwrote live books. Now gated on three conditions that must ALL hold: (1) `sb` exists; (2) `_readOk[key]` — that key's read was actually *answered* by the server, not fallen back; (3) a fresh re-read immediately before writing still shows the row empty. **Any future "skip the read to make boot faster" change must check this first.** The general lesson: a failed read and an empty table look identical downstream, so anything that *writes* on emptiness needs positive proof of emptiness.
- 🛡️ **Write guard + snapshots (12 Aug 2026) — the structural fix, not another cleanup tool.** `_guardWrite` in `sSet` **refuses** any write to `deals:`/`portfolio:`/`lost:` that would empty a collection or drop >half of it in one go, and toasts the user. Only bites at **3+ existing rows** (so an RM with two leads can delete both) and the halving rule needs 4+. Bulk archive is unaffected — archiving doesn't shorten the array. **This would have stopped the 12 Aug loss outright.** Alongside it, `_snapshot` copies the previous value to `config:snapshot:<key>` before every overwrite (max 1 per key per 10 min) — recovery *reconstructs* and loses notes/next-steps, a snapshot is the **exact rows** back.
- 👀 **RMs have a read-only "Missing work" tab (12 Aug 2026).** Recovery itself is **Command View only** — RMs only ever see My Pipeline / My Clients / My Commission / Leaderboard, so telling an RM to "open Recovery" is wrong. `rmMissing`/`recoveryForRM(slug)` show them their own missing leads + Active Clients with a copy-to-WhatsApp button. **Deliberately no restore button:** the judgement of what should come back is the RM's, the write is management's. Command View recovery covers the whole team in one pass, so Anne runs it once for everyone.
- 🛟 **Recovery tab reads TWO records (extended 12 Aug 2026).** The **change journal** (`changes:<date>:<slug>`, its own config rows) rebuilds *pipeline deals*. **Payroll months** (`payroll:<YYYY-MM>`, own table) are dated **snapshots of Active Clients** — every month is seeded from the RMs' books, so the rows carry client/premium/commRate/brokerFee/policy/insurer. That's the ONLY surviving record of the book when `portfolio` is overwritten, and it's why the 12 Aug loss was recoverable. Recovery takes the **most recent** month mentioning each client, skips ones already back on the book, and proposes the rest as tick-boxes (`act:'mkclient'` → `savePortfolio`). Route `payrolls:` returns every month. ⚠️ **A payroll month only holds clients that existed when it was first opened**, so anyone won since then is in NO snapshot — that's why Elizabeth's recent wins showed nothing. Won deals (stage 7) are therefore a **second source** for `mkclient`. ⚠️ Before this, recovery only *reported* missing Active Clients ("re-import or add manually") — that's why Elizabeth's Won Clients stayed missing after Anne's first restore.
- ⚡ **Boot is deliberately two-phase (30 Jul 2026) — don't re-serialise it.** The sign-in card paints first (`S.screen='gate';render()` is the LAST statement in the script — `renderGate` reads `APP_VERSION`, declared late, so painting earlier throws); data loads behind it. `seedIfEmpty` decides off already-loaded state (it used to re-read every RM = ~15 sequential round trips *per page load*); config's 3 keys fetch together; deals/portfolio/house run concurrently; lost leads load lazily on the Not Successful / Recovery tabs; the won-deal backfill runs after render. Supabase CDN script is `defer` + Google Fonts non-blocking. **Two waits are load-bearing, keep them:** `cfgReady()` before any PIN screen (late PINs make a real PIN look unset → RM overwrites it) and `bootReady()` before the app opens (a half-loaded pipeline that gets saved writes an empty book over the real one). Same reason `markLost` awaits `loadLost` first. Measured worst case (CDN dead): 13.7s → 0.47s to first paint.
- **Active Clients carry `policy` (policy no.), `insurer` (who the commission statement comes from) and `brokerFee`** — editable in the client modal (RM) and as Command View columns (management). Added 28 Jul 2026 on Lourie's request.
- **Payroll formula: `payout = premium × commRate% + brokerFee ÷ 2`.** Confirmed by Anne 28 Jul: the split is **always half**, and the broker fee is **always monthly recurring** (not once-off) — it repeats every payroll month like the premium. Constant `BROKER_FEE_SHARE=0.5`. The payroll table shows the fee and the half as separate columns so an RM query can be answered by pointing at the row.
- ✅ **`broker_fee` column added 30 Jul 2026** (`alter table portfolio add column if not exists broker_fee numeric default 0;`) — the fee now persists. The app still tolerates its absence (learns from server rows, strips the field on a rejected write) so saves never break.
- ⚠️ **Payroll seeds from the book ONCE — that was the "broker fee doesn't pull through" bug (Lourie, 12 Aug 2026).** `loadPayroll` only reads Active Clients when a month is *first* opened; a month opened before a fee was captured kept its seeded `0` forever. Fixed with `syncPayrollFromBook(pay,force)`: on every load it **fills blanks only** (zero fee adopts the book's fee; blank policy/insurer fill in), and a **"↻ Refresh from Active Clients"** button on Enter Commission force-syncs fee/policy/insurer **and adds clients won since the month was opened**. **Premium and rate % are never synced** (they're edited per month — re-reading them would wipe Brendan's work), and a fee typed on the payroll screen sets `feeEdited` so it is never silently overwritten (a deliberate R0 stays R0). Matching is RM + client name, case/whitespace-insensitive (payroll rows carry no portfolio id); archived clients excluded.
- ⚠️ **A won deal exists TWICE — deal record + Active Clients row — and they drift.** `_promoteWonToBook` copies a stage-7 deal into the portfolio then archives the deal, so the pipeline record is frozen at the signing figure while the book is what anyone actually maintains. That was Hein's "Biggest deal of the month still shows R460,634" (12 Aug 2026) after he corrected Klada to R4,606.34 **in the book**. Fixed with `_livePremium(slug,deal)` — resolves a won deal's premium through the portfolio by client name (same case/whitespace-insensitive matcher as payroll), falling back to `d.premium` when the client isn't there yet. **Applied to all three My Day sites** (honours `_titles`, `_bestMonth`, both month-total reducers) so a corrected figure can't show in one place and not another. Archived book rows still resolve — the same sweep archives the deal, so skipping them would reinstate the stale number.
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
- **Wes-Kaap Busdiens CC** (Vredenburg; t/a WES-KAAP TOERE — daily commuter, WCED scholar transport, charter; ±R13.1m fleet, 34 buses). RM: **Bronwan Fouche** (spelling SETTLED by Anne 12 Aug 2026 — "Bronwan", not Bronwyn, despite her own WhatsApp contact card; still need her direct email for the proposal contact card — packs currently carry the Rosebank switchboard + insurance@cartrack.com). Santam current vs Old Mutual (ONE) vs King Price (VAPS). **Went through 3 rounds — full detail in `deal-notes/weskaap-busdiens-build-history.md`.**
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
  - 🆕 **PI / DEFECTIVE WORKMANSHIP ADD-ON + a second policy (19 Aug 2026).** Full detail in
    `deal-notes/powerflow-pi-defective-workmanship.md`. Client meeting 20 Aug 09:00.
    - 🚨 **A SECOND EXISTING POLICY surfaced: Guardrisk Construction & Engineering
      `CAR167430` (Contractors All Risk) via the SAME broker Pogir Bastion — R2,336.62/mo**
      (contract works R15m R1,750.00 + **public liability R10m** R416.67 + Sasria R169.95; excess
      R5,000 major/all other, PL R15,000; 01/03/2026–28/02/2027). **The 28 Jul pack understated the
      programme: true current spend is R7,408.35 + R2,336.62 = R9,744.97/mo.**
    - **AC&E PI & Liability UM (FSP 45553) for New National Assurance (FSP 2603), quote
      `PI/PL26/JH58942` 7 Aug 2026, via FSP Solutions / Cartrack broker code 5855:**
      PI **R10m e&e** excess R25,000 = R29,681/yr · GPL **R10m e&e** excess R10,000 (10% min
      R25,000 underground services) = R7,420/yr · **Defective Workmanship R10m ANNUAL AGGREGATE**
      10% min R25,000 = R16,696/yr. **Total R53,797/yr = R4,483.08/mo** (×12 = exactly the annual —
      **no financing cost for monthly**). 20% broker commission + 15% ancillary fee disclosed.
      **Expires 6 Sept 2026.** This closes the gap flagged 28 Jul.
    - **Full programme: current R9,744.97 → recommended R13,817.26** (Natsure R6,997.56 + CAR
      R2,336.62 + AC&E R4,483.08) = **+R4,072.29/mo ≈ +R48,867/yr**. The re-market saves R410.79;
      the add-on costs R4,483.08 — **the switch pays for ~a tenth of the new cover**.
    - ⛔ **THE DISCLOSURE: retroactive date = INCEPTION**, claims-made — and the CAR policy adds
      *"RUN-ON COVER – Not included – Only new projects as and when policy becomes effective"*.
      **Everything already built and handed over is uninsured for design AND workmanship.** On
      solar/battery, defects surface years later. Ask AC&E to price a retro date; if refused it
      **must be disclosed in writing (Record of Advice)**.
    - ⚠️ **DW cannot be bought alone** — AC&E note (4): only available if their GPL is taken. Client
      already has R10m PL on CAR + R2m/R20m on commercial (or R20m broadform at Natsure), so the
      **R618.33/mo GPL is the entry ticket, not new cover**. Ask if DW can sit over external PL.
    - ⚠️ **The interlock:** DW excludes *"arising from defective design"*; PI covers design/advisory.
      Take one and not the other → a failed installation becomes an arguable gap. **That's the
      honest case for the package.** Options: all three R4,483.08/mo · PI only R2,473.42 ·
      GPL+DW R2,009.66.
    - 🚨 **Turnover mismatch.** CAR declares **annual turnover R15,000,000** and **max contract limit
      R6,000,000** (above = excluded unless noted) — yet notes **Linden Lane decommissioning
      R22,000,000** (273.24 kWp solar PV + **1001 kWh battery energy storage**, excess 10% min
      R35,000, wef 10 Oct 2025). **3.7× the contract limit, 1.5× declared turnover. PI is rated on
      turnover — get the real figure before placing.**
    - Also: quote has address/e-mail/VAT blank (**VAT 4370276398**, reg 2015/083526/07 are on the
      CAR schedule); activities read *"Design and Advisory electrical Installation Works and Solar
      (PLEASE CONFIRM)"* — **get battery energy storage named**; DW also excludes rectifying/recalling
      the work, inefficacy, pre-handover and aircraft; gradual pollution, asbestos, computer losses
      and **PFAS** excluded; warranty of no known claims since the proposal date **5 Aug 2026**;
      cover incepts only on payment in full.
    - **Deliverables built 19 Aug** (`powerflow_addendum_content.html` /
      `powerflow_addendum_playbook_content.html`): client addendum 6pp + RM playbook 5pp.
- **Hamisa Group** (one client group, `stephen@hamisagroup.co.za`, all currently at **Inscon Hawkins & Associates**). RM: **Bronwan Fouche** (= the Bronwan on Wes-Kaap). ✅ Spelling SETTLED by Anne 12 Aug 2026: **"Bronwan"** is correct — the Bryte quotes had it right and the 28 Jul note saying "Bronwyn" was wrong. The 24 Jul Wes-Kaap pack and the Hamisa Safety pack still say Bronwyn and need rebuilding if it matters. Three entities, group total **R92,831.87/mo**:
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
- **CS Continental Meat** (retail butchery, 98 Oak Avenue, Germiston Central; turnover R89m, 40 staff;
  contact Ms C Da Graca, claudia@cscontinental.co.za). RM: **Phillip Van Wyk**. Fleet-only comparison
  done 12 Aug 2026 — **current OUTsurance `OT130005936` (rev 7, 6 Jul 2026; broker of record = Lara Gray,
  an OUTsurance in-house broker) R26,860.75/mo** vs **King Price / VAPS HCV `VAPS52226` R20,981.44/mo**
  → **−R5,879.31/mo ≈ −R70,552/yr (−21.9%)**.
  - **Cleanest like-for-like in this book:** all 9 vehicles matched on registration / M&M code / chassis,
    retail-value basis both sides, **accessory values identical to the rand** (Nissan R40k, Dyna8 R200k,
    Hino R200k, Hilux ×2 R2,243). Total SI **R2,720,186** both sides. Motor section R24,175.42 → R15,053.16.
    Two thirds of the saving is 3 vehicles: 2× 2026 Hilux (R4,902.82 → R1,783.33 each) + Peugeot 208.
    **KP is DEARER on the Hino (+R333.49)** — say so.
  - **The real win is the EXCESS, not the premium.** OUT basic R7,610 (R8,500 Isuzu, R13,500 Hino);
    KP base is worse on paper (10% of claim min R30,000 on trucks) but the three reducers bought
    (own damage R1,587.40 + theft/hijack R681.32 + third party R390.00) cap it at a **flat R5,000 inner
    excess (R2,500 Nissan/Yaris), third-party damage NIL on items 2–9**. Hino −R8,500 per claim.
  - **Regressions to fix:** third-party liability **R5m → R2.5m, and only R1m if fire/explosion**
    (VAPS Sub-Section B, p11) ← the decisive cover point; **credit shortfall dropped** on both financed
    Hiluxes (Capitec noted; OUT charges R507.84/mo); claims prep R10k → R5k; **medical expenses R5,000/vehicle
    on OUT does not appear on the KP quote** (KP's own note: cover not stated = no cover); windscreen capped
    R15,000/vehicle with the excess waiver not taken. **Gains:** unauthorised passenger liability R2.5m
    (OUT lists it as available, NOT taken), contingent liability R2.5m, fuel-tank spillage R250k,
    wreckage removal R50k, towing R100k, loss of keys R50k, movement of 3rd-party vehicles R1m,
    cross-border territories, better roadside (R20k/yr per truck vs 2 call-outs) for R18.88 less.
  - ⛔ **THE GATE — the loss ratio.** OUT's own schedule discloses **19 motor-fleet incidents, ≈R1.46m paid
    over 10 yrs, R968,238 in the last 24 months** (incl. **R628,915 on 09/01/2026**) against ≈R645k of
    premium → **≈150%**. Nothing on VAPS52226 says "subject to claims experience", which is exactly why
    **Phillip must get VAPS to confirm IN WRITING that they rated on that record before the price goes to
    the client.** Corollary: OUT's schedule states the client **does not qualify for a Business OUTbonus
    on 31 Jul 2028** — so nothing is forfeited by leaving (kills the cash-back objection).
  - **Other gates:** (1) VAPS tracking rule (eff. 1 Mar 2023) — tracking **with recovery** on every vehicle
    over R200,000 = **6 of 9**; VESA 3/4 or factory alarm/immobiliser on the rest; **all nine tracking fields
    are BLANK** and no proof of fitment/operation/paid subscription/24h manned monitoring = **no theft or
    hijack cover at all** → **9-unit Cartrack lead** (OUT already names Cartrack on its approved list);
    (2) **the KP quote carries OUTsurance's OWN reg no. `1994/010719/06` and VAT `4340147224` in the
    POLICYHOLDER fields** — copied off the OUT schedule, where they are the *insurer's* numbers (the client's
    are blank there); (3) inception reads 01/08/2026 but the quote was signed 04/08 and **OUT already renewed
    on 01/08** — reset the date, time the cancellation, no gap/no double debit; (4) both 2026 Hiluxes are
    **"TBA"** — no registration numbers on either schedule; (5) OUT depot record says "Max number of
    vehicles 7" against 9 scheduled.
  - **Upsell in plain sight:** both policies are **motor-only** — no **goods in transit** (R89m of meat
    moving in 9 trucks, VAPS shows GIT "Not taken") and no deterioration-of-stock / machinery breakdown on
    the cold rooms. Also: OUT's claims list shows a separate **Building** category (geyser 2024 + 2026) →
    other business sits at OUTsurance, ask what and quote the whole account. 5 accidental-damage claims in
    24 months on 9 vehicles = a driver problem → camera telematics + driver scoring after the 9 units.
  - **Deliverables built 12 Aug** (`csmeat_proposal_content.html` / `csmeat_playbook_content.html`):
    client proposal PDF (6pp) + RM playbook PDF (7pp, INTERNAL). Afrikaans WhatsApp sent to Anne for Phillip.

- **Lomaen Medical (Pty) Ltd** (import, marketing, installation and repair of **x-ray machines**;
  8 Friesland Drive, Longmeadow Business Park South, Modderfontein 1609). RM: **Bronwan Fouche**.
  Full detail in `deal-notes/lomaen-medical.md`. Analysed 21 Aug 2026.
  - **Brief was NOT current-vs-proposed** — Bronwan asked for *"Full cover en dan vehicles aleen"*:
    the SAME insurer (Bryte) quoting two scopes, so the client can choose how much to place.
  - **Option A · Full cover** (quote 20/08/2026) **R507,669.76/yr = R42,305.81/mo** ·
    **Option B · Vehicles only** (13/08/2026) **R180,029.57/yr = R15,002.46/mo**. Both reconcile to
    the cent.
  - 🎯 **THE FINDING: vehicles-only costs MORE for the identical 11 vehicles.** Motor is
    **R158,436.82 standalone vs R145,961.16 inside the full programme = +R12,475.66/yr (+8.5%)**.
    Entirely two rates: **Hino 300 814 (R783,833) 3.560%→3.300%** and **VW Crafter 50 (R1,043,770)
    4.000%→3.000%**. Every other line identical. So the full programme = R340,115.87 of extra cover
    **less R12,475.66 back on the vehicles they were buying anyway**.
  - **Stock in trade R73,266,429** is the whole story (of a R74,471,499 fire SI). GIT **R3m/load,
    R75m annual carry**, road/rail/air, TP carriers ≤25% of carry. Liability R10m general/tenants/
    work away + **products & defective workmanship R5m**. BAR R1,860,536, EE ≈R1.1m (~55 laptops,
    IBA MAGIMIX R276,520, Synapse 3D), theft first loss R504,386.
  - ⚠️ **Both quotes divide the SASRIA monthly column by 10, not 12.** Quote says R42,868.39 and
    R15,051.34; true monthlies are **R42,305.81** and **R15,002.46**. Every other section /12
    correctly. Get it reissued — if the client checks the maths and it fails, the pack loses.
  - ⚠️ **Liability retro date contradicts itself on the face of the quote**: header
    "RETROACTIVE DATE: INCEPTION DATE OF POLICY" vs "Retroactive date 01 June 2017 will be
    retained" three lines down. Bronwan has confirmation it IS retained — **fix the schedule before
    inception**, 8 years of past work turns on it.
  - ⚠️ **Liability rated on nothing: "TURNOVER R0" and "WAGES R0"** printed on the section → the
    R5,576.00 is a placeholder and WILL be re-rated. (Same shape as the Powerflow PI turnover find.)
  - ⚠️ **Stock at the customer's site**: BAR carries "stock subsequent to off-loading post conveyance
    at the consignee" R300,000 — but **max 4 weeks post delivery, fire/allied perils only, theft
    needs forcible entry, ALL accidental damage excluded**. For an installer of x-ray machines that
    is precisely the exposure window. Ask for the period extended + accidental damage in.
  - ⚠️ **No business interruption section at all** (Sasria BI = R0) on R73.3m of stock, one address,
    import lead times. Nobody asked for it. Ask.
  - ⚠️ **Sasria motor looks under-declared**: 3 private + 3 commercial <3,500kg = 6 of 11 items, and
    **R0 against "commercial 3,500kg and over"** despite two Hinos (the 814 at R783,833).
  - ⚠️ **Footer reads "Quotation – Hollard Insurance Company" on a Bryte-titled quote — the SAME
    discrepancy as the Hamisa Group quotes.** Confirm who carries the risk in writing.
  - Gates: satisfactory survey before inception · full 3-year claims history ("underwriting needs
    claims experience to raise new business") · **alarm warranty on BOTH theft and electronic
    equipment** · quotes valid 30 days (full cover → 19 Sept 2026).
  - ⏳ **STILL OUTSTANDING: the current schedule** (`4311 os skedule 20260731 met Laptop Tamryn
    bygevoeg`) — password-protected, never reached the session. **Until it lands there is no
    benchmark**; we can only compare the two Bryte scopes, not beat what the client pays today.
  - **Deliverable built 21 Aug**: `lomaen_proposal_content.html` → client comparison PDF (5pp).

## Conventions
- Commit trailers used in this project:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` + `Claude-Session: …`
- Never put the model id in commits / code / PRs (chat only).
- People's pronouns: use they/them unless stated. **Jean = he.**
- **Integral Trading Services / Silent Valley** — ROUND 2 (17 Aug 2026). Petrosure (via **FSP
  Solutions**, Lezanne Vosloo) answered **all 15 queries** and reissued W5101 at **R123,300.02**
  (was R122,203.83) vs Santam **R131,719.79** → **−R8,419.77/mo ≈ −R101,037/yr**. Only two things
  changed in the quote: **MG45VLGP corrected R1,516,105 → R1,816,105** (fleet SI now matches at
  **R31,311,815**) and **roadside R200 on the 4 light vehicles only**. Score: **5 closed** (retro
  date held 20/08/2021 ✓, agreed value on GRW/Afrit/T&TT ✓, SI corrected ✓, PL R10m per event no
  aggregate ✓, roadside added), **4 open** (TP lift to their R5m not applied or priced; annual
  carry figure needed from client; Sasria gap unexplained; **they asked US for the broker fee**),
  **6 refused** (no GIT excess reducer, single-vehicle loading stays, **quote NOT rated on claims
  — still "Loss History: Tba"**, forecourt-template deflection, **no EIL → referred to
  Envirosure**, no credit shortfall).
  - ⛔ **STILL HOLD, and now for a sharper reason: the two that decide it are the two they cannot
    fix.** TP on the 10 truck-tractors is **capped at R5m** vs Santam's R10m (hard ceiling, in
    writing), and **the hijack excess cannot be reduced**.
  - 🚨 **NEW: the claims record. Cules disclosed R6,500,000 — two trailers hijacked with their
    loads, one last year one this year.** ≈206% loss ratio over 24 months. **The client's actual
    loss is hijacking, which is precisely the excess Petrosure won't reduce**: R1m load hijacked =
    **Santam R20,000 (two excess reducers, R100k/R250k insured amounts) vs Petrosure R300,000**
    (10% + 20%). +R280,000 per hijack against R101,037/yr of saving = **one hijack eats 33 months
    of the saving**. Trailer itself: R2.4m T&TT unit R360k (Santam 15%) vs R480k (Petrosure 20%).
  - ✅ **Territory is a NON-issue** — Cules confirmed **diesel, RSA only**. Santam's 12-country
    cargo territory isn't used. Trucks park at **N17 Diesel Depot & Truck Stop**, workshop at
    **Overall Road Express** — neither is the scheduled premises; get both declared.
  - ⚠️ Roadside is worse than it looks: Petrosure gives none **above 3.5t GVM**, so 23 heavy units
    get nothing; Santam includes breakdown towing, towing in AND outside RSA, wreckage removal +
    extended. Petrosure caps towing R15,000 trucks / R5,000 private, wreckage removal R10,000.
  - ✅ Genuine Petrosure gains: **passenger + unauthorised passenger + contingent liability
    R2,500,000** (Santam records "Not included" on 10 items), small-claim excess min R5,000 vs
    R30,000, legal defence R250k vs R50k, wrongful arrest R100k vs R50k.
  - 🛰️ **Cartrack is already the incumbent tracker on 16 of 18 tracked units** (13 Tag Range
    Recovery, 2 Telematics Range, 1 Fleet Management; Tracker Network ×1, Capital Air ×1).
    Petrosure needs tracking on **all 24 units over R250,000** + **pre-inspection of every
    vehicle** → ~6 units to add, 2 competitor units to convert, and two hijackings make the case
    for video telematics on the 10 horses.
  - New on the 17 Aug quote: **Electricity Grid Interruption exclusion** with a Type 2
    SANS-compliant surge-arrestor condition.
  - Deliverables **rebuilt 19 Aug** for round 2 (`integral_proposal_content.html` /
    `integral_playbook_content.html`): client proposal 6pp + RM playbook 7pp.
- **Idol Transport (Pty) Ltd** (long-haul HCV + GIT, 35 Steyer Street, Aureus, Randfontein; reg
  2016/003501/07; contact Zinhle Zulu `zinhle@idoltransport.co.za`). RM: **Cules**. 5-market
  comparison done 19 Aug 2026 — full detail in `deal-notes/idol-transport.md`.
  - **Fleet identical on every quote: 47 units, SI R27,964,847** — 18 HCV (17 MAN + 1 Actros)
    R17,462,400 · 25 trailers R8,989,747 · 4 LDV R1,512,700. Mixers, truck-tractors, tippers AND
    tanker trailers (fuel/DC/tri-tank) — commodity is declared General Goods / Food Products.
  - **Current = Transport-ONE `HCV/1240900` sched 6, One Underwriting Managers t/a ONE,
    underwritten by Old Mutual Alternative Risk Transfer Insure (OMART, FSP 49551), broker of
    record Cci Global. R148,370.94/mo**, reconciles to the cent (motor R103,791.73 + GIT R28,800
    + PL R3,729.60 + PA R507.61 + fee R100 + Sasria R11,442).
  - **All-in:** OWNsurance/Renasa **R133,714.43 (−R14,656.51/mo ≈ −R175,878/yr)** · MiWay
    R137,406.27 (excl. driver dishonesty) / R146,183.83 (incl.) · **current R148,370.94** ·
    VAPS/King Price R148,976.78 (**+R605.84 — dearer**) · Natsure/Compass R150,502.87.
  - **Recommend OWNsurance** — the ONLY quote that is cheaper AND holds **third-party liability
    R10,000,000** and **agreed value**. Excess transformed: motor flat R10,000 → **nil** on own
    damage/theft/hijack/third party under OwnRship Option A (holds even when the fund is
    depleted); GIT R50,000 → **R5,000**.
  - ⚠️ **Same OWNsurance fund trap as Waste Carriers.** "Annual savings R341,670.46" + "GIT
    R163,800.00" is the client's OWN fund, not a saving. Reconciles EXACTLY with **sequential**
    deduction: motor R59,597.15 × 0.91 (9% binder) × 0.875 (12.5% broker) × **60%** × 12; GIT
    R37,500 × 0.91 × **0.80 (20% broker)** × **50%** × 12. Fund = R505,470.46/yr = R42,122.54/mo.
    **Effective annual cost: 0 claims R1,099,103 · R250k claims R1,349,103 · fund used
    R1,604,573 · staying R1,780,451.** On a R1.2m/yr loss record the fund lasts ~5 months —
    **sell the zero excess, not the rebate.**
  - ⛔ **THE GATE — the loss record.** Idol's own MiWay disclosure: **58 losses, R2,651,053 over
    3 yrs; R2,402,455 in the last 24 months against R2,491,002 of motor premium ≈ 96%.**
    OWNsurance's line one is "subject to a satisfactory claims history" — **written confirmation
    it rated on that record before any figure goes to the client.**
  - 🚨 **43-unit Cartrack lead, and a live hole today.** ONE endorsement HCV0019 makes theft cover
    conditional on a monitored tracking/recovery device on every vehicle **over R500,000 = 20
    units**, yet **all 23 items read "Tracking device Required: No"** (a R581,842 theft was paid
    Feb 2025). VAPS needs **43 units >R200k + 14 dual-camera video telematics >R800k + trailer
    units on BOTH links to GIT spec** (GIT ≥R1.2m rule). MiWay names Tracker/Netstar — get
    Cartrack named in writing. 43 accident losses on 22 vehicles = driver scoring lead too.
  - **Territory is the sharpest divide:** current 16 countries; OWNsurance GIT **11** (loses
    Angola, Uganda, Rwanda, Kenya); VAPS 8; **Natsure and MiWay = RSA ONLY**.
  - **Why the rest are benched:** MiWay moves all trucks to **retail value**, caps GIT at a
    **single R2m** (not R2m × 18), doubles GIT excess to R100,000, **excludes driver dishonesty
    on GIT in both versions**, excludes neighbouring/extended territories on motor AND goods,
    trailers cost R34,772.65 vs R13,330.07, plus a **R13,289.44/mo broker fee** — and its VAT
    number is wrong (4150284554 vs 4250264712). VAPS is dearer and cuts TP **R10m→R2.5m (R1m
    fire/explosion)**, PL R20m→R10m, capsizing-whilst-tipping excess becomes **5% of vehicle
    value** (4 tippers). Natsure is dearest, GIT +87%, RSA-only goods, and its HCV SI is
    **R16,584,900 vs R17,462,400** (KD45LTGP carries no value) — but it is the **only** quote
    with **passenger liability R2,500,000** and broadform R10m **per address**.
  - ⚠️ **Two Natsure versions exist** — use only **22 Jul (Olga van der Merwe) R150,502.87**; the
    21 Jul (Chantel Farelo) R199,504.29 carried R41,400/mo of GIT excess helpers since removed.
  - **Also not replaced on the OWNsurance quote: public liability R20,000,000 and driver personal
    accident** — place separately.
  - **Deliverables built 19 Aug** (`idol_proposal_content.html` / `idol_playbook_content.html`):
    client proposal PDF (6pp) + RM playbook PDF (9pp, INTERNAL).
