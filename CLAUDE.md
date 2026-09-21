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

- 🚫 **NETLIFY IS NOT INVOLVED.** No `netlify.toml`, no Netlify build, no functions, in any of the
  three repos. Hosting is GitHub Pages off `main`; the data path is browser → supabase-js → Supabase
  PostgREST → Postgres, with no back end of ours in between. Anne's personal Netlify team does hold
  three CLI-uploaded sites (`krugerhouse`, `eminentwealthmedical`, `radiant-mermaid-ac8ce7`), but none
  is a Cartrack app. Wiring reference (3 Sept 2026):
  https://claude.ai/code/artifact/b0838e98-0833-45b9-b917-dd4948279f67
- **Deploy = commit + push to `main`.** No build step, no code to paste — Pages rebuilds in ~1–2 min. The apps in `/workspace/<repo>` are the working clones (add via `add_repo` if not in session scope).
- **Version stamp:** bump `const APP_VERSION='v2026.MM.DDx'` in the RM app on every push (shows on the sign-in card so support knows what a phone is running).
- **Design system for the APPS:** "Compliance DS" — Saira (headings) + IBM Plex Sans (body) + IBM Plex Mono (mono), near-black `#0B0C0F` ink + brand orange `#F47735`. Home-screen icons = white Cartrack arrow on `#0B0C0F` (in each repo's `assets/`).

### RM System notes
- 🔐 **RLS check, and why RLS alone cannot fix this (3 Sept 2026).** Run
  `deal-notes/rm-system-rls-check.sql` in the SQL editor: it reports RLS on/off per table, every
  policy with its role and rule, and anon's table grants. **Read all three, not just the first.**
  The app holds no Supabase Auth session, so every request arrives as `anon`; any policy loose
  enough for the app to work is loose enough for anyone who copies the key out of the page source.
  So RLS being ON is necessary but not sufficient, and payroll cannot be truly closed until
  Supabase Auth is in (roadmap, ~20h). Sandboxed web sessions cannot reach Supabase to test this;
  the SQL has to be run from Anne's browser.
- Supabase-backed (anon key in client; **RLS is the only protection — payroll holds salaries, confirm RLS is locked down**; no server-side auth, PIN gate is client-side only). Tables: `deals`, `portfolio`, `payroll`, `config`, `orgs`, plus `users`/`activity`.
- **Which Supabase project:** ref `govvmqgpxzbqghzgcitb`, project **`cartrack-rm-system`**, under org **annekruger3010-svg's Org** (✅ **on the Pro plan** — daily backups, 7-day retention; PITR is a separate ~$100/mo add-on and is NOT taken) — *not* the "Kruger House" org, whose project has none of these tables. SQL Editor: `https://supabase.com/dashboard/project/govvmqgpxzbqghzgcitb/sql/new`.
- Saves are merge-safe per-row upserts; durable localStorage outbox for mobile resilience.
- 🚨 **`seedIfEmpty` WRITES OVER THE SERVER ROW — it destroyed RMs' leads on 12 Aug 2026. Never let it decide off in-memory state.** The 30 Jul boot rewrite replaced its per-RM re-read with a check against already-loaded state, treating the read as pure cost. It was carrying safety: `sGet` falls back to `_mem` on a failed read, **`const _mem={}` is in-memory and empty on every page load**, so `loadRM` stores `[]` — indistinguishable from an empty table — and the seed overwrote live books. Now gated on three conditions that must ALL hold: (1) `sb` exists; (2) `_readOk[key]` — that key's read was actually *answered* by the server, not fallen back; (3) a fresh re-read immediately before writing still shows the row empty. **Any future "skip the read to make boot faster" change must check this first.** The general lesson: a failed read and an empty table look identical downstream, so anything that *writes* on emptiness needs positive proof of emptiness.
- 🛡️ **Write guard + snapshots (12 Aug 2026) — the structural fix, not another cleanup tool.** `_guardWrite` in `sSet` **refuses** any write to `deals:`/`portfolio:`/`lost:` that would empty a collection or drop >half of it in one go, and toasts the user. Only bites at **3+ existing rows** (so an RM with two leads can delete both) and the halving rule needs 4+. Bulk archive is unaffected — archiving doesn't shorten the array. **This would have stopped the 12 Aug loss outright.** Alongside it, `_snapshot` copies the previous value to `config:snapshot:<key>` before every overwrite (max 1 per key per 10 min) — recovery *reconstructs* and loses notes/next-steps, a snapshot is the **exact rows** back.
- 👀 **RMs have a read-only "Missing work" tab (12 Aug 2026).** Recovery itself is **Command View only** — RMs only ever see My Pipeline / My Clients / My Commission / Leaderboard, so telling an RM to "open Recovery" is wrong. `rmMissing`/`recoveryForRM(slug)` show them their own missing leads + Active Clients with a copy-to-WhatsApp button. **Deliberately no restore button:** the judgement of what should come back is the RM's, the write is management's. Command View recovery covers the whole team in one pass, so Anne runs it once for everyone.
- 🛟 **Recovery tab reads TWO records (extended 12 Aug 2026).** The **change journal** (`changes:<date>:<slug>`, its own config rows) rebuilds *pipeline deals*. **Payroll months** (`payroll:<YYYY-MM>`, own table) are dated **snapshots of Active Clients** — every month is seeded from the RMs' books, so the rows carry client/premium/commRate/brokerFee/policy/insurer. That's the ONLY surviving record of the book when `portfolio` is overwritten, and it's why the 12 Aug loss was recoverable. Recovery takes the **most recent** month mentioning each client, skips ones already back on the book, and proposes the rest as tick-boxes (`act:'mkclient'` → `savePortfolio`). Route `payrolls:` returns every month. ⚠️ **A payroll month only holds clients that existed when it was first opened**, so anyone won since then is in NO snapshot — that's why Elizabeth's recent wins showed nothing. Won deals (stage 7) are therefore a **second source** for `mkclient`. ⚠️ Before this, recovery only *reported* missing Active Clients ("re-import or add manually") — that's why Elizabeth's Won Clients stayed missing after Anne's first restore.
- ⚡ **Boot is deliberately two-phase (30 Jul 2026) — don't re-serialise it.** The sign-in card paints first (`S.screen='gate';render()` is the LAST statement in the script — `renderGate` reads `APP_VERSION`, declared late, so painting earlier throws); data loads behind it. `seedIfEmpty` decides off already-loaded state (it used to re-read every RM = ~15 sequential round trips *per page load*); config's 3 keys fetch together; deals/portfolio/house run concurrently; lost leads load lazily on the Not Successful / Recovery tabs; the won-deal backfill runs after render. Supabase CDN script is `defer` + Google Fonts non-blocking. **Two waits are load-bearing, keep them:** `cfgReady()` before any PIN screen (late PINs make a real PIN look unset → RM overwrites it) and `bootReady()` before the app opens (a half-loaded pipeline that gets saved writes an empty book over the real one). Same reason `markLost` awaits `loadLost` first. Measured worst case (CDN dead): 13.7s → 0.47s to first paint.
- **Active Clients carry `policy` (policy no.), `insurer` (who the commission statement comes from) and `brokerFee`** — editable in the client modal (RM) and as Command View columns (management). Added 28 Jul 2026 on Lourie's request.
- 🆕 **PAYROLL FORMULA CHANGED 27 Aug 2026 (Lourie): `payout = commission ÷ 2`.** The comm stat now
  gives a rand commission per client, so there is no rate % and no broker fee in the payout.
  `RM_COMMISSION_SHARE=0.5` — the same 50/50 split Anne confirmed on 28 Jul, just taken off the
  commission instead. **Active Clients: Broker Fee column → Commission; Insurer → relabelled UMA**
  (it always held "who the commission statement comes from"). **Payroll: Rate % and ½ Fee removed**,
  columns are Client · Premium · Commission · RM commission. **Payout Summary:** Clients · Premium ·
  Commission · RM commission · Less salary · Nett payout.
  - ⚠️ **Legacy rows keep the OLD formula.** Anything captured before 27 Aug has no `commission`,
    only premium + `commRate` (+ `brokerFee`), and `payoutOf` falls back to
    `premium × commRate% + brokerFee ÷ 2` whenever `commission` is absent — **a month already paid
    may never move.** The payroll screen tags those rows "legacy". `BROKER_FEE_SHARE=0.5` and
    `feeShareOf` stay in the code for exactly this reason; do not delete them.
  - 🔒 **Payroll months are FROZEN except the current one and the one before it.**
    `_isOpenMonth(mo)` — payroll is closed *after* month-end (Lourie runs August during September),
    so a strict "current month only" rule would freeze the very month being worked on. Premium and
    commission only sync from the book inside that window; **policy no. and UMA are descriptive, not
    financial, and may be corrected on any month.** This protects the payroll snapshots that the
    Recovery tab rebuilds a lost book from.
  - **Copy for Accountant rewritten:** every RM's **full book**, tab-separated for Excel — Client
    Name · Policy Number · Premium · Commission · RM Commission · UMA — plus a **Less Salary** row
    carrying its amount under RM Commission, and a **Total** row for premium, commission and RM
    commission. Then an ALL RMs line and TOTAL NETT PAYOUT.
- **Superseded (pre-27 Aug):** `payout = premium × commRate% + brokerFee ÷ 2`, confirmed by Anne
  28 Jul — split always half, broker fee always monthly recurring. Still the formula for legacy rows.
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
2b. ⚠️ **If a like-for-like adjustment moves an insurer's headline, PRINT THE AS-QUOTED TOTAL
   NEXT TO IT, on the cover and in the table.** The RM and the client both read our pack with the
   insurer's own quote open beside it. A number that does not appear on either document reads as
   an error and the pack loses. Caught 3 Sept 2026: the Cordiguard pack led with ONE at
   ≈R40,208 (the honest like-for-like on 25 vehicles) while ONE's quote says R42,932.86 for 27,
   and Elizabeth flagged the mismatch. Name the gap and what causes it, every time.
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
- ⚠️ **USE THE HOUSE TABLE COMPONENTS. Do NOT invent a cut-down table style** (Anne caught
  this 16 Sept 2026: the Bakers client pack "suddenly looked different" from the Vuyos one). The
  template and CSS are identical across packs; what changes a pack's look is using a reduced subset.
  **Every client proposal must have:**
  - 🎨 **MASTHEADS: client proposal = ALWAYS plain `class="masthead"` (black ink).
    NEVER `.orange` / `.teal` / `.blue` / `.purple` / `.pink`.** The coloured mastheads are the
    **RM playbook's** signature and nothing else. (Anne, 16 Sept 2026: "All the heading blocks in the
    client facing proposal must be black, not colour, only the playbook must be colourful." Every
    other client pack in the repo was already clean; only Bakers and Gateway had been coloured.)
    Coloured **callouts** (`.rec` / `.warn` / `.info` / `.verdict` / `.dark`) stay as they are in
    both document types; the rule is about the heading blocks.
  - **Cover leads with MONEY, not a warning.** Three `.stat` cards: what they pay today, the best
    quotation, the difference. A finding goes on page 2 or 3, never in place of the numbers.
  - **A "Markets approached" chip row on the cover**: `.chips > .chip` (`.dot` orange dot for the
    ones quoted, `.on` filled for incumbents).
  - **Page 2 = "reconciled to the cent"**: a `.stat-band` of 3 to 4 cards, then a REAL house table.
  - **House tables**: plain `<table>` + `<colgroup>` with `<col class="propcol">` on the recommended
    insurer's column and `class="propcol"` on its cells; **first column left-aligned** with
    `.item` (bold label) + `.desc` (grey sub-note); `class="r"` on figure columns ONLY;
    `tr.total` for the totals row; **`.neg` = GREEN saving, `.pos` = RED cost** (note the naming is
    inverted from intuition).
  - 🚫 **Never add a `<style>` block with `.fx{table-layout:fixed}` / `.tight` overrides.**
    That is what flattened the Bakers and Gateway packs into grey lists and left half-empty pages.
  - A page that ends halfway down is a sign the content is too thin, not that the design changed.
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
  - 🆕 **ROUND 6 (2 Sept 2026): ONE quotes the whole account.** Detail in `deal-notes/weskaap-round6-one.md`.
    **ONE fleet `HCV/1295809`** (ONE Insurance Underwriting Managers FSP 8783, "fleet basis" R390,000/yr flat)
    **R32,714.04** + **ONE commercial `ONET/1297249.2`** (One Insurance Limited) R3,531.54 = **R36,245.58
    vs Santam R37,535.20 (−R1,289.62, −3.4%)**. Fleet value **R13,011,084 = Santam's register to the rand,
    51 units, same comp/TPFT split.** Fleet is flat (−R514); the saving is STP's **R2,897.76/mo broker fee**.
    - 🚨 **ONE priced the buses as a building.** Its fire section insures "Miscellaneous R8,942,700" =
      Santam's column-5 subtotal (which contains a **R7,923,960 "Sasria cover for the busses, depot risk
      only" line at R0.00**) + the diesel again, at R1,341.41 + Sasria R350.82, and rates the P&M and
      office contents twice. Real property at Uitspan Street = R868,740. **Corrected ONE ≈ R34,581.73
      (≈ −R2,953/mo, −7.9%, ≈ R35,440/yr).** Get it reissued before the client sees a number.
    - ⚠️ **A 52nd vehicle:** 2010 Toyota Prado VX CFG41137 on the ONE commercial quote, not on Santam
      (R1,276.99). Excluding it ONE ≈ R33,305 (≈ −R4,230). Confirm whose it is.
    - **Liability doubles:** passenger, unauthorised passenger (closes the July ask), third party (incl.
      fire/explosion), contingent all **R5,000,000** vs Santam R2,500,000. Keys R20k nil excess, wreckage
      R30k, fire brigade R25k, roadside on cars/LDVs, 10% profit share option.
    - ⛔ **THE GATE, sixth time: "Passenger Liability R5 000 000" does NOT say fare-paying.** ONE UM's
      July TOURS quote needed a dedicated FPPL section. Get it printed on the schedule with seat basis.
    - **Regressions to disclose:** bus own-damage excess **10% of claim min R4,000** (Santam prints no bus
      excess, voluntary R5,000; cars 5% min R4,000); **no automatic cover for acquisitions**; single-vehicle
      limit R650,000 (Iveco R1,280,643 declared); hired-in excluded; "final fleet list required", Sasria
      "to be agreed", re-rate on claims history; valid to **2 Oct 2026**.
    - Also: fleet quote insurer NOT named (UM paper; office quote is One Insurance Limited; July was OMART);
      ONE business description omits the bus operation; office contents "Alarm: No" vs theft section
      "burglar alarm warranty: Yes"; two MAN 65-seaters have no regs on Santam; laptop R5,500 → R15,500.
    - 🛰️ **Tracking on 10 units or no theft cover** (≥R500k + Hilux/Fortuner/Quantum): Hilux CFG31635,
      Fortuner HT38DMGP, Quantum CFG16629, Scanias CFG39808 + CFG24228, both MANs, Irizar CFG 43813,
      Iveco CFG28098, Prado.
    - **Deliverables 2 Sept** (`weskaap_r6_proposal_content.html` / `weskaap_r6_playbook_content.html`):
      client proposal 5pp + RM playbook 7pp. Recommendation: ONE, once fire is reissued, FPPL is on
      the schedule and the insurer is named. Target inception 1 Nov, notice to STP by 30 Sept.
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
  - 🆕 **ROUND 2 — THE WHOLE ACCOUNT (21 Aug 2026).** Full detail in
    `deal-notes/cs-continental-round2.md`. Phillip sent the **commercial policy** + two FSP/Western
    proposals. **The 12 Aug work was fleet-only.**
    - **Commercial policy `OT129830654` (Cs Continental Cc, reg 2007/127891/23, premises 98 Oak
      Street Primrose — a SHOPPING CENTRE building) = R19,600.21/mo**, rev 10 of 06/07/2026,
      renewal **29 July**. Turnover R89m, 40 staff, ex **Old Mutual Insure** 10+ yrs.
    - **Whole account: current R46,460.96/mo → Western R37,243.31/mo = −R9,217.65/mo ≈
      −R110,612/yr (−19.8%) — but 99.3% of it is the FLEET.**
    - **Fleet three-way: OUT R26,860.75 · VAPS52226 R20,981.44 · Western/FSP `48707523`
      R17,704.87.** Western beats VAPS by **R3,276.57/mo (R39,319/yr)** and is now the lead quote.
      Administrator FSP Commercial Online FSP 35978, Cartrack broker code 5855.
    - ⛔ **DO NOT MOVE THE COMMERCIAL.** Saving is **R61.77/mo = R741/yr**, against a **projected
      Business OUTbonus of R42,637.61 payable 28 July 2028** on that policy. **The bonus is worth
      57 years of the saving.**
    - ⚠️ **CORRECTS THE 12 AUG NOTE.** "Client does not qualify for a Business OUTbonus… nothing is
      forfeited by leaving" is **true of the FLEET only** (ratio too high). The **commercial** policy
      has a clean ratio and a live bonus. Cash-back objection: dead on the fleet, alive on the
      commercial.
    - ⚠️ **ALSO CORRECTS 12 AUG:** "both policies are motor-only — no GIT, no machinery breakdown on
      the cold rooms." **The commercial policy DOES carry GIT (R700,000/conveyance) and machinery
      breakdown (R2,000.71 on R2.68m of food processing equipment).** The instinct on
      **deterioration** was right though — see below.
    - 🚨 **THE BEST FINDING: the surge protection breaches the policy's own condition.** Schedule
      declares **"Db protection (Imax LESS THAN 40kA)"**; the fire special conditions require
      **SANS-approved Imax of at least 40kA**, failing which **the insured carries the first 20% of
      any lightning/power-surge claim**. Plant & machinery SI **R10,000,000**, refrigeration-based
      business, and **a lightning claim was paid 29 Dec 2023**. Fix costs a sparky's morning.
    - ⚠️ **BI gross profit R3,000,000 on R89,000,000 turnover** (12-month indemnity) — **identical on
      the Western quote**, so a standing gap. Even at a 15% margin GP would exceed R13m.
    - ⚠️ **Deterioration of stock NOT taken anywhere**: optional on machinery breakdown (OUT),
      optional on GIT (OUT), and **R0,00 on the Western quote**. For a meat business that IS the
      characteristic loss.
    - ⚠️ **GIT R700,000/conveyance vs annual carry R282,000,000** and 91–120 transits/mo; **type of
      goods declared "Agricultural produce"** on a butchery (Western describes it properly);
      **driver fidelity NOT taken** (schedule spells out: no cover for driver/employee criminal
      involvement); **carry R282m vs turnover R89m = 3.2×, one figure is wrong.**
    - ⚠️ **Public liability R5,300,000 claims-made, retro 06 JANUARY 2026** — 7 months of tail on a
      food business, and only valid if prior cover was uninterrupted claims-made (they came from
      OMI). Products liability included R5.3m BUT excludes *"defective design, formula, plan or
      specification where you are responsible for any part of the manufacturing, packaging or
      preparation prior to sale"* — a butchery prepares and packages meat. RSA only.
    - Also: **buildings R30,100,000** with **no escalation / subsidence / leakage / rent clause**;
      plant & machinery R10m at **excess R33,700**; **occupancy certificate NO**; **no fidelity**
      (40 staff, cash retail, and money cover for employee theft dies after 15 working days); money
      limits R10k/R10k/R10k; solar R120,000 needs a **CoC**; alarm must be **armed when unoccupied**
      yet all security devices read "Unspecified"; **motor specified = 3 private cars** (Lexus LS460,
      Hummer H3, Chery Tiggo) with **passenger liability NOT taken**.
    - ⚠️ **Motor losses are worse than the fleet schedule showed:** the commercial policy carries a
      further **R341,015 of accidental-damage vehicle claims in 8 months** (Apr–Dec 2024) on the
      three private cars, on top of the fleet's R968,238/24 months.
    - 🛰️ **12-unit lead** (9 fleet + 3 specified). OUT's GIT section **names Cartrack on its approved
      list** and requires an SVR device on any load over R300,000 or **no theft/hijack cover**;
      Western excludes theft/hijack over **R350,000** without a **VESA-approved** system.
    - **Western proposal is "subject to a written 3 years minimum claims experience before going on
      risk"** — the price is NOT firm. Same gate as 12 Aug.

- **Lomaen Medical (Pty) Ltd** (import, marketing, installation and repair of **x-ray machines**;
  8 Friesland Drive, Longmeadow Business Park South, Modderfontein 1609). RM: **Bronwan Fouche**.
  Full detail in `deal-notes/lomaen-medical.md`. Analysed 21 Aug 2026.
  - **CURRENT: CIB (Pty) Ltd (FSP 8425) underwritten by Guardrisk, policy `CIB655753C`, broker of
    record Flexipleks Insurance Brokers CC** — **R51,145.80/mo = R613,749.60/yr** (rev 37, endorsed
    29/07/2026). Insured VAT 4760147696, reg 1995/001319/07 — both blank on the Bryte quote.
  - **Bryte full cover R42,305.81/mo = R507,669.76/yr → −R8,839.99/mo ≈ −R106,080/yr (−17.3%)** ·
    Bryte vehicles-only R15,002.46/mo. All three reconcile to the cent.
  - ⛔ **THE FINDING — the current liability section carries "WORK AWAY EXCLUSION – 001":** *"no
    indemnity … for work done away from the Insured premises."* **Their whole business is installing
    and repairing x-ray machines AT CUSTOMER SITES.** Plus **no products liability / defective
    workmanship at all**. Bryte includes **work away in the R10m** and adds **products & defective
    workmanship R5m** — for **+R221.68/mo inside a programme R8,840/mo cheaper.** Lead with this.
  - **Retro date resolved: the CIB schedule says 01/06/2017**, exactly the date Bryte says is
    retained — so the "inception" in the Bryte header is a printing error, not a term. Still fix it.
  - **Motor R18,168.58 → R12,163.43 (−33%) AND Bryte insures R404,885 MORE** on the same 11 items:
    Hino 300 814 R599,316→R783,833 (+R184,517), Hyundai H100 +R86,000, Hino 300 614 +R85,393.
    **Those are retail-value updates — the client is under-insured today.** Suzuki +R1,995 = the
    anti-smash shield folded into the SI.
  - ⚠️ **Motor regressions:** passenger + unauthorised passenger **R5,000,000 → R2,500,000** on 8
    items; current carries a **fire/explosion sub-limit R1,000,000** Bryte doesn't state (may be a
    gain). ⚠️ **The Bryte quote states NO motor excess at all** — current is basic R4,000/R5,000,
    theft 10% min R5,000. **Get the excess table before presenting.**
  - 🚨 **THE GATE — the sprinkler waiver.** The CIB fire section records *"SURVEY DONE — Stacking
    Heights exceeds 3m. sprinkler system waived."* Bryte is "subject to satisfactory survey". **If
    Bryte's surveyor won't waive it on R73.3m of stock stacked >3m, the client is asked to sprinkler
    a warehouse.** Put the existing survey + waiver to Bryte's underwriter NOW. Also match the
    condition that fire hose reels be pressure-tested annually by an SAQCC-registered technician.
  - **Roadside R1,330/mo + Office Buddy R225/mo are new** (current motor assistance is R39.82 on 3
    vehicles). Strip both → saving becomes **R10,275.53/mo ≈ R123,306/yr**. Client's call.
  - **Claims disclosed R30,000** — effectively clean on a R613,750/yr programme, which is why 17% is
    available. Confirm it is the full 3-year figure.
  - 🛰️ **Cartrack already on 4 of 11 vehicles** (Fleet Professional CT9, "CIB approved"). 7 to go.
  - 🎯 **Vehicles-only costs MORE for the identical 11 vehicles:** motor R158,436.82 standalone vs
    R145,961.16 inside the programme = **+R12,475.66/yr (+8.5%)**, entirely two rates (Hino 300 814
    3.560%→3.300%, VW Crafter 4.000%→3.000%). Every other line identical.
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
  - ⚠️ **No business interruption on the Bryte quote AND none on the current** (CIB shows BI R0.00,
    "Cover in force: No"). **A standing gap, not a regression** — R73.3m of stock, one address,
    import lead times. Neither broker has ever put it on the table. Quote it.
  - ⚠️ **Sasria motor looks under-declared**: 3 private + 3 commercial <3,500kg = 6 of 11 items, and
    **R0 against "commercial 3,500kg and over"** despite two Hinos (the 814 at R783,833).
  - ⚠️ **Footer reads "Quotation – Hollard Insurance Company" on a Bryte-titled quote — the SAME
    discrepancy as the Hamisa Group quotes.** Confirm who carries the risk in writing.
  - Gates: satisfactory survey before inception · full 3-year claims history ("underwriting needs
    claims experience to raise new business") · **alarm warranty on BOTH theft and electronic
    equipment** · quotes valid 30 days (full cover → 19 Sept 2026).
  - **Deliverables built 21 Aug** (`lomaen_proposal_content.html` / `lomaen_playbook_content.html`):
    client proposal PDF (6pp) + RM playbook PDF (6pp, INTERNAL),
    rebuilt against the current schedule once it landed. Extract kept at
    `deal-notes/lomaen_current_extract.txt`.

- **Gear Lab Roodepoort (Pty) Ltd** (gearbox & clutch workshop, 6 Buhrmann Street, Horison,
  Roodepoort 1724). RM: **Elizabeth Schlebusch**. **NEW BUSINESS — the client has NO current
  insurance**, so there is no benchmark; the job is limits-vs-business, not a comparison. Full
  detail in `deal-notes/gear-lab.md`. Analysed 25 Aug 2026.
  - **Hollard `QT1026483` via BrokerBuddy (Commercial) FSP 43153 = R3,731.48/mo** ·
    **ONE `ONEC/1293516.1` (One Insurance Limited t/a ONE) = R2,718.29/mo** → ONE is
    **−R1,013.19/mo (−27.2%)**. Both reconcile to the cent.
  - 🚨 **THE FINDING — neither quote covers the core exposure.** Hollard: **"Vehicle Hoists and
    Ramps: No"** on all 4 items, and exception 14 excludes loss *"occurring by or through the use of
    any vehicle hoist or ramp unless otherwise stated in the Schedule"* (plus exception 11 defective
    workmanship, exception 5 mechanical/electrical breakdown). ONE: **car hoists YES ✓ but "Damage
    to vehicles being worked upon: No"**. **A gearbox workshop puts every vehicle it touches on a
    hoist.** Both need those extensions quoted before anything is presented.
  - ⚠️ **Material damage on customers' vehicles is R50,000 on BOTH** — a modern SUV in for a gearbox
    rebuild is R500k–R1.5m and a workshop holds several at once. Get the max value on the premises.
  - ⛔ **TWO DIFFERENT INSUREDS.** Hollard: "Gear Lab", reg **2000/260824/07**, VAT **9874563**
    (**invalid — 7 digits; SA VAT is 10 starting with 4**). ONE: "Gear Lab Roodepoort (Pty) Ltd",
    reg **2025/509941/07**, VAT blank, business type "Not Specified". **A 2000 company and a 2025
    company at the same address — bind the wrong one and there is no cover.** If the trading entity
    is the 2025 registration it is a start-up, which explains the absence of insurance.
  - ⚠️ **The inception conditions cannot be met**: ONE requires a satisfactory claims history AND a
    previous policy schedule — **the client has never been insured, so neither exists.** Tell both
    insurers in writing and get the price confirmed on a no-prior-cover basis BEFORE acceptance.
    ONE's inception/endorsement dates read **01/01/3000** (placeholder) — no start date is set.
  - ⚠️ **Buildings disagree: Hollard R1,750,000 vs ONE R2,555,000** — R805,000 apart on the same
    premises. Contents agree exactly (Hollard P&M R350k + stock R5.2m = ONE's fire SI R5,550,000).
  - ⚠️ **ONE charges NO M4 Sasria** on motor traders; Hollard charges R44.27. Query it.
    ⚠️ ONE's internal-risk extension list shows **"WorkAway: No" AND "WorkAway: Yes"** on
    consecutive lines. ⚠️ ONE theft is 43% cheaper than Hollard on an identical R100,000 — read both
    sections' warranties before leaning on it.
  - **Nothing on either quote for:** business interruption (R5.2m of stock, one address — the most
    serious omission), machinery breakdown on hoists/presses, electronic equipment (diagnostic
    gear), money, glass, fidelity, GIT, accidental damage, or **any vehicle Gear Lab owns**.
  - Hollard liability is **claims-made** (retro = inception, fine for a first policy but disclose
    it); ONE broadform basis/retro not stated. Hollard commission 20% non-motor / 12.5% motor +
    **R75 broker fee**; ONE intermediary commission R476.27.
  - **Deliverables built 25 Aug** (`gearlab_proposal_content.html` / `gearlab_playbook_content.html`):
    client proposal PDF (5pp) + RM playbook PDF (5pp, INTERNAL).

- **Cordiguard Security Services (Pty) Ltd** (Elizabeth's e-mail says "Coriguard"; every schedule
  reads **Cordiguard**, reg 2018/057432/07, VAT 4260286408). Guarding and patrolling, *"No Armed
  Response, Supervisors and Management Vehicles"*, 107 Trezona Ave, Mindalore, Krugersdorp; second
  site Elandsfontein Moklo Mine (North West). Co-insured **Multi Source Distribution Agency** (owner
  of the two Vitz). RM: **Elizabeth Schlebusch**. Client meeting **Thu 4 Sept 2026 pm**. Full detail
  in `deal-notes/coriguard-security.md`. Analysed 2 Sept 2026.
  - ⛔ The first "ONE" attachment was the GEAR LAB quote. **The real ONE `ONEC/1296323.1` arrived 2 Sept
    10:46: R42,932.86 for 27 vehicles** (adds Rangers KZ32XSGP + MY91ZHGP; fresher regs for JACs, Vitz,
    FJ MJ25CJGP, i10 MR38ZYGP). **Like-for-like on 25 ≈ R40,207.95 = −R8,309 vs Bryte (−17.1%), −R5,675
    vs Santam.** Best liability section (broadform, occurrence, wrongful arrest + legal defence R250k
    each, R95/mo) BUT **no passenger liability on 26/27** (R1m on one Vitz), unauthorised pax on 8 only,
    TP limit printed on 2 of 27, **+5% excess 23:00 to 04:00 and +5% single-vehicle** (a patrol fleet),
    Sasria M2 on every car (≈R580/mo over), tracking required on 22. Sent back for reissue.
    **Revised recommendation: ONE if it adds pax liability on all + drops the night loading; else
    Santam corrected.** Proposal form = blank Tranquille template.
  - **CURRENT: Bryte `BCOM23-8364-0032049`** via **Alpina Brokers** (Stephan van Eeden, FSP 42616),
    review date 01/09/2026 (already rolled) = **R48,516.75/mo** (R46,716.75 + VAPs R1,800:
    One Loyalty R770, Phishield R100, X'S Sure on the BMW R930). Commission R5,995.23/mo.
  - **Santam `STM-CAR0313-STMCN2-0301343` R45,882.64 (−R2,634.11/mo, −5.4%, ≈ −R31,609/yr)** ·
    Hollard via BrokerBuddy `QT1026819` + `QT1026897` R45,628.42 (−R2,888.33). All reconcile.
    **Motor is flat (Santam −R336.73 on 25 vehicles); the saving is VAPs (−R1,200) plus two things
    Santam quoted SMALLER: accidental damage R360k→R150k (one site) and the Samsung S24 at R0.
    Like-for-like ≈ −R2,180/mo ≈ R26,000/yr. Say that.**
  - 🚨 **FINDING 1: passenger liability.** Bryte "Additional Passenger Liability: No" on all 25;
    the armoured FJ Cruiser (R850,000, mine patrols) says *"Passenger Liability is excluded."*
    Guards ride in these bakkies every shift. **Santam: R2.5m passenger + R2.5m unauthorised
    passenger on every vehicle inside the premium.** Hollard: none. Lead with this.
  - 🚨 **FINDING 2: public liability R1,000,000 on all three, and Santam's memoranda says
    "EXCLUDES WORKAWAY"** while its own excess table prices work away (same page). A guarding
    company's only liability is at other people's premises. Gate: work away written in, R5m and
    R10m priced. Retro 20 Oct 2023 retained at Santam ✓; **Hollard prints no retro date and drops
    wrongful arrest + legal defence.** Same shape as Lomaen / Vuyos.
  - **FINDING 3: excess.** Bryte 10% min R10,000 (+ single-vehicle flat R10,000); **Santam 5% min
    R4,000**; windscreen 25% min R2,500 → R350.
  - ⚠️ **Bryte's TP contradicts itself:** item pages say Sub-Section B R5,000,000; wording p35
    says R2,500,000 aggregate, R1,000,000 fire/explosion. Santam R2.5m (ask R5m). **Hollard
    R1,000,000.**
  - ⛔ **Hollard benched:** nominated drivers only; TP R1m; no passenger liability; no theft cover
    on 24/25 without a tracker certificate ("Received: No" on all 25); "Collared Burner" loss-ratio
    endorsement (extra premium at 70%); 48-hour inspection on every second-hand vehicle; **its item
    premiums = Bryte's item totals to the cent on 15 of 22 matched** (rest differ by exactly the
    credit shortfall it dropped). Not a re-rating.
  - ⚠️ **Fix on Santam before presenting:** (1) **MOT0003 Ranger JN04CFGP (ABSA) quoted "ADFT",
    not comprehensive**; (2) work away + limit; (3) AD back to R360k over both sites; (4) Samsung
    R21,000; (5) interests: ABSA, Wesbank ×6, Ford Credit, Phezulu Oil (5 Polos + i10), FJ seller
    holds title, MSDA as co-insured/owner of the Vitz (Santam says Cordiguard); (6) BMW year 2023
    vs 2022; (7) regs blank for 3 JACs, BMW, 2 Vitz everywhere; (8) TP R5m; (9) incept 1 Oct 2026
    (quote expires 23 Sept, "subject to confirmation of claims history").
  - **Disclose to Santam:** Bryte MOT0012 KV57DMGP cash-settled damage 03/10/2025, proof of repair
    outstanding. Get the 3-year claims record from Alpina.
  - 🛰️ **25-unit lead.** Bryte wording requires trackers on every Ranger 2007+, every Polo, >R750k,
    TWO on the Fortuner (16 of 25; "Required" printed on 11, none fitted). Santam condition on 4,
    clause 1937 = 20% min R5,000 excess if security not as declared. Hollard: no theft cover at all.
  - **Not taken anywhere:** GPA for the guards, fidelity, employers' liability, BI. Quote GPA +
    fidelity next.
  - **Deliverables built 2 Sept** (`coriguard_proposal_content.html` / `coriguard_playbook_content.html`):
    client proposal PDF (6pp) + RM playbook PDF (7pp, INTERNAL). No em dashes.

- **Arboretum Primary School and Pre-Primary School FTRRI** (Richards Bay; two campuses, 3 school
  buses, buildings R45.9m). RM: **Hein van Rooyen**. ✅ **UNBLOCKED 14 Sept 2026** (was "blocked on a
  clean Marsh schedule"). Full detail in `deal-notes/arboretum-primary.md`.
  - **A better scan of the current Santam schedule arrived**: the 1 Sept file was pure black/white
    (2 grey values, figures gone); the new one has 200+ grey levels and **every sum insured is
    legible**. ⚠️ **Premiums are still zeroed out** (every section 0.00, Total Due blank), so the
    current price remains unknown. Anne's standing rule on the R30,000 still applies.
  - Current: **Santam via Marsh `77115603*002` v11**, Ronel Irvine, anniversary **01/04/2027**.
  - **Three-way: Hollard `HOL-CAR0313-NBUS2-0303527` R23,516.03 · ONE `EDU/1294794.1` (OMART)
    R24,093.16 · Bryte `QT1029359` via BrokerBuddy R29,672.78.** All reconcile to the cent.
  - 🚨 **BENCH HOLLARD. Endorsement LIA_011 "Schools exception" excludes child molestation or sexual
    abuse, wrongful or excessive discipline, and bullying or harassment**, and a memo excludes
    **pupil-to-pupil liability**. Limit **R1,000,000** claims-made **retro = inception**; no legal
    defence, no wrongful arrest, no products. EL cut R5m → R1m. Its **R17.5m umbrella needs a R2.5m
    underlying but the underlying is R1m** (same defect as Western/Powerflow). ⚠️ Two Hollard PDFs
    share one quote number: 10:28 superseded by 11:07 "corrected Combined Liability to R1m", and
    **the premium did not move when the limit did**.
  - 🚨 **BENCH BRYTE: "Passenger liability: No" on all 11 items**, incl. both Quantums and the Iveco
    midibus (unauthorised pax R2.5m only). Also 4 data errors: CH07GJZN coded **10 seat** vs Santam
    **14**; Venter Traveller trailer coded as a **2007 Force Traveller minibus**; a trailer dated
    **1925**; both tractors reg "Required".
  - ⚠️ **CORRECTS the 1 Sept briefing on three points.** (1) **ONE's R5m passenger liability is a
    MATCH of Santam, not an upgrade** (the old pack told Hein to lead with it as better). (2) Glass
    **R10,000** and (3) accidental damage **R20,000** are on the CURRENT Santam schedule at exactly
    those figures, so they are standing gaps, not ONE placeholders. Printers R1,699,778 likewise
    copied from Santam to the rand.
  - **Current-policy cover nobody has costed:** liability is **R1m + R20m top-up on an OCCURRENCE
    basis** (top-up applies to PL only, motor TPL and EL deleted), **teacher liability + pupil
    liability included**, **PI teacher & scholars R1,000,000**, legal defence R500k, wrongful arrest
    R250k; **employers liability R5m claims-made with retro 01/04/2008** (18 years of tail);
    **escalation + inflation R9,952,238** across both buildings (no quote carries it); **Government
    is a co-insurer for the balance of the Waterberry Wood buildings**; **Leaf Technologies' interest**
    noted on EE (36 leased Intel NUCs R499,905); Dangerous Activity Exception (fireworks, fairground
    rides, animals, archery) already excludes a school fete today.
  - ✅ ONE is **better on the surge excess** (10% min R2,000 vs Santam 20% min R2,500), ⛔ but its PL
    is conditional on **COM 0003 disclaimer notice boards at the entrances**.
  - **No theft, no fidelity, no BI** on the current policy or any quote. Standing gaps. Fidelity first.
  - **Recommend ONE**, subject to 5 fixes: all three entities named (ONE names only the primary
    school), retro dates on broadform + EL, teacher/pupil/PI priced, escalation + inflation,
    inception date (still reads 01/01/3000, renewal 01/08/2027 vs anniversary 01/04/2027).
  - **Deliverables 14 Sept** (`arboretum_proposal_content.html` / `arboretum_playbook_content.html`):
    client proposal 6pp + RM playbook 6pp (INTERNAL).
- **The Gateway School and Gateway Society FTRR&I** (school for special-needs children, Van Dalen
  Street North, Ruimsig, Roodepoort 1724; reg 2000/260903/07, NPO; **21 Toyota Quantum Sesfikile
  midi-buses** + 3 trailers + 1 LDV = 25 items). RM: **Phillip Van Wyk**. Four-way done 15 Sept 2026,
  full detail in `deal-notes/gateway-school.md`.
  - **CURRENT: Old Mutual Insure, `OMI - MULTISURE 2024.4`, policy `MUF-PWV0680-M-0208559`** (insurer
    ref 690934272) via **PWV Insurance Brokers** FSP 22500, agency `PWV0680`, broker **Gerda Baker**;
    administrator Broker Solutions Group FSP 31598. **On risk since 01/09/2010**, review date
    **01/09/2026 (already rolled)**, version 22 printed 11/08/2026. **All-in R46,640.87/mo**
    (R45,936.34 + Sasria R657.77 + Sasria shortfall R46.76; VAT R6,083.59; fees R0.00).
    ⚠️ **95-page scan with no text layer**, read as page images (256 grey levels).
  - **Four-way, all reconcile to the cent: Bryte via BrokerBuddy `QT1029228` R41,359.96
    (−R5,280.91/mo, −R63,371/yr) · King Price `COM58558` R42,901.67 (−R3,739.20)
    · Alpha `ALPHACOM204975` R45,539.16 (−R1,101.71) · Auto & General R46,795.48
    (+R154.61, DEARER than staying).**
  - 🚨 **BRYTE HAS DROPPED A ZERO ON RENT.** Buildings Combined Sub-Section C: current
    **R21,677,345**, King Price R21,677,345, A&G R21,677,344, **Bryte R2,167,734** (short
    **R19,509,611**). The cheapest quote is cheapest partly because it is not quoting the same policy.
    **Same shape as the Vuyos Santam Robertville find.**
  - 🚨 **KING PRICE prints "Passenger liability: Private and LDV only" R3,000,000 on all 25
    items**, and **the current policy already gives R2,500,000 passenger + R2,500,000 unauthorised
    passenger + R2,500,000 contingent on every bus, inside the premium.** So it is a **regression
    dressed as an upgrade**. Proof to put to them: the OMI schedule classifies the vehicles as
    **"MIDI-BUS"** and rates them Sasria **Category M3 Minibus (16 passengers incl driver)**, and
    **Alpha quoted R2.5m pax at a NIL excess on the same fleet** (R5m on 3). **Second time on this
    insurer after Wes-Kaap Busdiens** (e-hailing RTU form). Keep the precedent internal.
  - ✅ **King Price's schools cover is GENUINELY NEW, not a match.** The current broadform
    extensions print **"Schools extension: No"** and "Cancellation of special event extension: No".
    So teacher liability, pupil liability incl. pupil-to-pupil, **PI R1,000,000** (wrongful expulsion
    of a scholar), post-traumatic counselling and event cancellation are all cover the school has
    never had. **On LIMIT it is a match**: current = R5m broadform + **R20,000,000 umbrella** = R25m.
    Bryte R20m is a reduction, A&G R5m drops the umbrella, **Alpha quotes NO liability at all**.
  - 🚨 **THE MOST URGENT ITEM: they are in breach of a tracking WARRANTY today.** Every bus
    on the CURRENT schedule reads *Immobiliser: Factory Fitted · **Tracking 1: Early Warning
    System Required** · Alarm system: **None***, and carries **"Vehicle Recovery System (the
    Device) Warranty and Memorandum"** under Warranties and Endorsements. Required, recorded absent,
    written as a warranty. **24 of 25 vehicles carrying special-needs children.** King Price adds
    **+25% of the claim** as excess for non-compliance; **A&G waives its theft excess entirely if a
    device is fitted** (≈R33,750 on a R450k Quantum). **24-unit lead, and it is urgent whoever wins.**
  - ❌ **CORRECTIONS to my own earlier passes, all superseded in the deal note:**
    (1) "Buildings under-insured by R13.6m / R18.3m": **WRONG.** All four carry base buildings at
    **R86,709,378 to the rand**; the R104,968,348 headline is base + **R18,208,970 of 1st and 2nd year
    inflation escalation** + R50,000 geysers. What IS true: escalation margins are thinner on every
    quote (KP carries R8,670,938, one year only).
    (2) "Buildings disagree by R4,667,734 between Bryte and A&G": **WRONG**, an artifact of
    summing base + rent R2,167,734 + liability R2,500,000 on one side and base alone on the other.
    (3) "About ten buses carry no registration on Bryte": **WRONG.** Bryte has all 25;
    **two are TRANSPOSED**: `XYG685GP` should be **YXG685GP**, `HG38XBGP` should be **HG38BXGP**.
    (4) "Alpha is the current policy": **WRONG**, it is a fourth quote.
  - **Property owners' liability cut by all:** current R5,000,000 → KP R2,500,000, Bryte
    R2,500,000, **A&G R1,000,000**.
  - **Standing gaps confirmed on the CURRENT policy** (so not quote laziness): **employers' liability,
    fidelity, glass, BI at R297,000**, deterioration of stock, accounts receivable, D&O, employment
    practices, GIT, products/defective workmanship, negligent advice, statutory defence costs,
    wrongful arrest, defamation. **The current broadform DOES carry pollution liability R5,000,000**
    (R17.28/mo), third party vehicles R1m and a provider of food and drink extension (tuck shop).
  - Current detail worth keeping: fire R9,635,900 = school contents R7,883,489 + **solar system
    R1,752,411**; EE **R1,615,810** (= Bryte and KP to the rand) + data reinstatement R21,600;
    **GPA covers 25 BUS DRIVERS** R50k death / R50k disability (**Bryte has no GPA section**);
    machinery breakdown is a **borehole pump** R16,800; buildings basic excess R25,000; Sasria type on
    buildings recorded as **"Residential"** on a school. **Alpha has not quoted the 3 trailers**; A&G
    quotes 22 of 25 items.
  - ⚠️ **VAT number is blank on the CURRENT schedule too**, and Bryte prints `9517532`
    (7 digits; SA VAT is 10 starting with 4).
  - 📎 **How the documents arrived:** they would not upload from the Mac. Anne used Gmail's
    **"Add to Drive"** on the attachment chips (Google to Google, no download, no file dialog) and they
    were pulled with the Drive MCP. **This Gmail connector cannot download attachments** (no
    `GetMessageAttachment`; `RAW` is unusable at 4-5MB). **Use the Add to Drive route every time.**
  - **Deliverables rebuilt 15 Sept** (`gateway_proposal_content.html` / `gateway_playbook_content.html`):
    client proposal 6pp + RM playbook 6pp (INTERNAL). Alpha extract at `gateway_alpha_extract.txt`.

- **Bakers Tankers / Bakers Bulk / MG Carriers FTRR&I** (bulk fuel and general haulage, 15 Vereeniging
  Road, Alrode, Alberton 1451; reg 2008/014516/07, VAT 4720248410; contact **Mr Z Essop**,
  zaahid@bakerstankers.co.za). RM: **Bronwan Fouche**. ⏰ **Client meeting Thu 17 Sept 2026 for a
  final answer.** Full detail in `deal-notes/bakers-tankers.md`. Analysed 15 Sept, **rewritten
  16 Sept when the second OUTsurance schedule landed.**
  - 🚨 **`OT78078997` (108pp, via Google Drive, 16 Sept) IS A SECOND OUTSURANCE POLICY, NOT A
    REISSUE, AND IT REVERSES THE RECOMMENDATION.** Inception 10 Jun 2022, renewal **10 Jun 2027**,
    **185 items (65 vehicles + 120 trailers)**, **R97,875.36/mo**. Together with `OT89649119`
    (30 items, R75,457.10, renewal 1 Sept 2027) that is **215 distinct vehicles, ZERO shared
    registrations, R173,332.46/mo**. Both reconcile to the cent; the seven insured fleets on
    `OT78078997` sum exactly to its two section totals.
  - ✅ **THE 184-VEHICLE QUESTION IS ANSWERED. Nothing is uninsured, and Alpha V4 is quoting the
    same fleet.** Trucks 54 v 55 · **trailers 124 v 124 exact** · cars and LCV 37 v 35 · trailer SI
    R27,454,899 on 120 v R28,444,295 on 124 · **Sasria R31,732.51 v R31,511.54, R221 apart on a
    statutory rate.** Four checks, none could line up by accident.
  - 💥 **SO ALPHA IS DEARER: R191,938.68 v R173,332.46 = +R18,606.22/mo ≈ +R223,275/yr (+10.7%).**
    🎯 **But its RATES are better:** trucks R1,682.14 v R1,805.45, trailers R191.08 v R207.02, cars
    R316.89 v R448.15, **vehicle sections R127,352.98 v R139,746.36 = −R12,393.38.** What makes it
    dearer is **R33,074.16/mo of additions**: **towing R17,529.16** (two lines at 16.0%, both capped
    at **R30,000** = R210,350/yr to buy R30,000 of towing) + **clean-up R11,000.00 for R1,000,000**
    + windscreen R2,750 + VAPS R1,605 + general R190. OUT carries roadside, extended territories,
    EIL, keys and passenger liability **inside** its rates and adds **PL R11,664,000 for R1,853.59
    that Alpha does not quote**. 🎯 **Strip Alpha's towing and it lands at R174,409.52, within
    R1,077.06/mo of staying. That is the lever.**
  - ❌ **CORRECTIONS to the 15/16 Sept packs, all superseded:** (1) "OUTsurance covers 30 vehicles,
    R75,457.10" was one policy of two; (2) "per-truck rate −30%" was the wrong basis, across all 54
    OUT trucks it is **−6.8%**; (3) "184 vehicles may be uninsured" is answered; (4) **the OUTbonus
    is TWICE what I recorded: R255,621.49 on 27 Feb 2028 + R307,010.54 on 7 Aug 2028 =
    R562,632.03**; (5) "OUT's EIL reaches back six weeks" is the newer policy, **`OT78078997` carries
    retro 01 Jan 2025**; (6) programme figures R117,123.77 / R130,559.25 were built on 30 of 215.
  - ⛔ **THE HAZMAT FINDING STANDS AND IS NOW ON BOTH POLICIES**, business described "Service &
    Repair, Transport, Goods", turnover **R150,000,000**, 200 employees. 🚨 **And the contradiction
    is in OUTsurance's own words twice:** the EIL special conditions require drivers to be familiar
    with *"the transport of dangerous substances and goods"* and to hold *"a professional driving
    permit for vehicles transporting dangerous goods"*, on the same schedule that excludes hazardous
    materials. Put both paragraphs to Virgil Niekerk.
  - 🚨 **POLLUTION IS THE OPPOSITE OF WHAT THE LAST PACK SAID. OUT already gives R5,000,000 per
    vehicle on 52 trucks for R3,483.84/mo** (R895.33 retro 01 Jan 2025 + R2,588.51 retro 30 Jun
    2026); Alpha wants **R11,000/mo for R1,000,000, HCV only**. 3.2× the price for a fifth of the
    limit. ⚠️ **BUT NO TRAILER ON EITHER OUT POLICY CARRIES EIL.** I wrote this up as an Alpha
    regression; it is a **standing gap** on 124 trailers, and on a tanker fleet the product is in the
    trailer. ⚠️ "Containers used" reads **NO** on `OT78078997` and **YES** on `OT89649119`.
  - 🚨 **NEW: the tanker trailer sums insured cannot be right.** 34 described tankers: **nine at
    R56,047**, five at R95,659, eight at R150,664, two at R729,000, six at R1,293,750. A 2017 road
    tanker at R729,000 beside 1999/2006 tankers at R56,047; replacement is R800k to R1.6m.
    **And Alpha has copied the same values across.** Get a valuation. Largest exposure in the file.
  - 🚨 **NEW: 61 of the 215 items are 2006 or older**, and Alpha requires *"a full vehicle evaluation
    before comprehensive cover"* on anything over 20 years. 61 inspections before cover attaches.
  - ✅ **NEW: they DO cross borders.** Extended territories is bought on **every one of the seven
    fleets, R15,611.75/mo = R187,341/yr**. ⚠️ **Corrects the open GIT question** ("ask if they
    actually cross those borders"): CLP's 12 territories v Santam's 4 is a **real** gain.
  - ⚠️ **3 vehicles have tracking REQUIRED and NOT INSTALLED: KZ73CSGP, CB42HNZN, FJ04NTGP** →
    **no theft or hijack cover today**. All 26 on `OT89649119` require a device with no fitment
    recorded. ✅ **Cartrack is NAMED on OUTsurance's approved list.** 🛰️ **179-unit lead** (55 trucks
    + 124 trailers); no trailer carries a tracking field on either policy while **CLP's GIT makes
    theft cover on any load over R500,000 conditional on live tracking**.
  - ⚠️ **Claims are BETTER than assumed: both policies project an OUTbonus, which needs a claims
    ratio ≤30%.** `OT78078997`'s own page 6 lists **38 Guardian incidents 2018 to Feb 2022,
    R778,376 across the 17 valued**, incl. a hijack 30 Jun 2021, yet every fleet section prints
    *"incidents in the last ten years: None"*. Alpha still only **asks for** 3 years' claims
    experience, so **R191,938.68 is not firm**.
  - ⚠️ **PL R11,664,000 at R1,853.59** (legal defence + wrongful arrest R10.8m each, excess R8,020).
    🚨 **OUTsurance itself prints "Based on your industry type, we recommend the Defective Products
    optional cover, which is not currently selected."** Defective products AND workmanship both
    untaken on a R150m repair-and-transport business. **Credit shortfall untaken** with ABSA's
    interest noted. **Passenger liability R5m/15 seats IS taken at OUT; Alpha's HCV liability table
    prints none.** **Extended TP not taken either side, so TP is R5m both.**
  - **Excess: OUT wins and it is not close.** Trucks **R11,400 to R26,640**, trailers **R5,720**,
    light R6,840 to R9,320 v **Alpha 10% of claim min R30,000** on HCV and all 124 trailers. On a
    R1.5m truck that is R150,000 v R11,400.
  - **GIT unchanged and still the one clean win:** Santam `AMDBLE265448M` R41,666.67 → CLP / New
    National via Nautical R39,212.15 = **−R2,454.52/mo ≈ −R29,454/yr**, matched limits (conveyance
    and driver fidelity R1,620,000 both), debris R25k→R30k. ⚠️ CLP names **Bakers Tankers alone**
    (Santam and BOTH OUT schedules name all three); ⚠️ **High Risk Cargo over R1m = a further 25%
    min R25,000** and the definition includes copper and batteries against declared **Scrap Metal
    and Scrap Batteries** (fuel is not on the list); ⚠️ period "commencing on TBA".
  - ✅ **Envirosure Spill Protect Plan, Transport** (FSP 38594, Centriq FSP 3417, ref
    `20260814/FP/01`, Adelle Hartley) **R15,890.00/mo**, dangerous goods R5m + TP solution R5m,
    claims-made **retro = inception**, Africa south of the Equator, 27 vehicles, excess nil except
    **flat R10,000 on TP claims**. 🚨 **Dated 14 Aug, valid to 14 Sept, LAPSED.** ⚠️ **Broker printed
    as "Vaps", not Cartrack.** 🎯 **Do NOT quote a spill price until OUTsurance answers on hazmat:**
    if the exclusion does not bite, Envirosure largely duplicates the trucks and what is needed is a
    **trailers-only** price; if it does bite, the EIL on 52 trucks is worthless and R15,890 is cheap.
    **Ask Adelle for both versions.**
  - 💰 **Programme: current R214,999.13/mo** (motor R173,332.46 + GIT R41,666.67) **v R247,040.83 as
    quoted = +R32,041.70/mo ≈ +R384,500/yr.** Alpha without towing → R229,511.67 = +R14,512.54.
  - ✅ **RECOMMENDATION CHANGED: keep the motor at OUTsurance** (cheaper, far better excesses, 5× the
    pollution limit, an R11.664m PL section Alpha does not quote, R562,632 of bonus); **move the GIT
    to CLP**; **buy spill cover sized to the hazmat answer**; **fix what is broken on their own book**
    (tanker values, 3 untracked vehicles, no trailer EIL, no credit shortfall, no defective products).
  - **Admin:** address **15 Nereeniging Rd, Alberton 1449** (Santam) v **15 Vereeniging Rd,
    Alberton 1451** (both OUT + CLP), and `OT78078997` prints "Vereeninging" on its own page 2;
    **VAT and reg blank on BOTH OUT schedules** so neither is a tax invoice; loss of keys R3,000 v
    R10,000 between the two policies; **2 MAN TGA trucks (JXH251MP, JXH256MP) are third-party only**,
    R65.15/mo, no own damage/theft/hijack; **Alpha's renewal reads 01/10/2026** against OUT renewals
    of 10 Jun 2027 and 1 Sept 2027, so a move cancels both mid-term; Alpha names Bakers Tankers alone;
    `OT89649119`'s depot caps at 27 vehicles (**that is a depot record, NOT the hazmat fleet count**,
    which kills the earlier "27 is the real tanker fleet" theory); `OT78078997` has no depot record.
  - ⚠️ `Bakers_GIT.pdf` is a **40-page scan with no text layer** (229 grey levels), read as page
    images. `OT78078997` has a text layer, 108 pages.
  - 📎 **`OT78078997` arrived via Google Drive from iOS** ("Saving to Drive"), pulled with
    `search_files` → `download_file_content` → base64 → pymupdf. **Same route as Gateway and Vuyos.
    Use it every time a file will not upload.**
  - **Deliverables rebuilt 16 Sept** (`bakers_proposal_content.html` / `bakers_playbook_content.html`):
    client proposal 6pp + RM playbook 7pp (INTERNAL). Sources kept at
    `bakers_outsurance_OT78078997.pdf` (+ `bakers_out_OT78078997_extract.txt`),
    `bakers_envirosure_quote.pdf`, `bakers_alpha_v4_quote.pdf`.

- **Tshenolo Waste (Pty) Ltd** (medical and hazardous waste: speci-bins and containers to health
  care practitioners and institutions, collection and transport, hazardous waste training; head
  office Lanseria Corporate Estate, 25 Amelia Lane, Krugersdorp 1739). RM: **Cules Van Dyk**.
  ⛔ **STILL GATED 21 Sept 2026: THREE quotes are in (two Natsure + Alpha), NO current schedule.**
  Full detail in `deal-notes/tshenolo-waste.md`.
  - Cules (15 Sept): *"Dit is twee polisse wat opgesplit is … Natsure spaar hulle R77 000/mo."*
    ⚠️ **That phrase describes the two files he sent, the NATSURE proposal split into a fleet policy
    and a commercial policy. It is NOT a reference to two current policies.**
  - 🆕 **THIRD QUOTE, 21 Sept: Alpha / Guardrisk `ALPHACOM205554` = R423,308.39/mo**, reconciles to
    the cent, 190pp, printed 18 Sept, one Commercial policy. **Alpha (Pty) Ltd FSP 21820** underwriter,
    **Guardrisk FSP 75** insurer, accounts executive **[redacted]**, commission R58,383.08/mo,
    broker fee R0.00, inception 01/10/2026. Cules: *"R122 000 spaar per maand"*.
    **vs Natsure R461,855.31 = −R38,546.92/mo ≈ −R462,563/yr (−8.3%)**: motor −R13,380.83,
    non-motor −R22,310.54, Sasria −R2,855.55.
    ⚠️ **Cules's two figures agree**: R423,308 + R122,000 ≈ R545,300 and R461,855 + R77,000 ≈
    R538,900, so the current is **near R540,000/mo**. **That is an inference, NOT the schedule.**
  - 🚨 **ALPHA FINDING 1: "Liability arising out of the carriage of dangerous goods: No" on ALL 45
    trucks**, together with "Clean up costs (leakage from vehicle): No", "Spillage and clean-up
    costs: Substance transported: No" and "Tool of trade liability: No". **Alpha prices all of these
    on its own schedule and none is taken, on a hazardous and medical waste fleet.** The clean-up
    lines do not appear at all on the buses or trailers. **So pollution ranks Natsure R250,000/truck,
    Alpha nothing.** ⚠️ And Alpha identifies the trailers: a skeletal 7.2m drawbar R697,831 and a
    **G.R.P 15,500mm tridem axle trailer R2,689,098** (a liquid body, no registration), the unit most
    likely to spill, with no clean-up line.
  - 🚨 **ALPHA FINDING 2: third party HALVED on trucks and buses, R5,000,000 → R2,500,000**, behind a
    R5,000 excess. Alpha is R2.5m across all 70. (Natsure's R5m was itself an aggregate containing
    passenger and fire/explosion, so the real gap is under 2:1, but it is a gap.)
  - 🚨 **ALPHA FINDING 3: STILL NO PUBLIC LIABILITY. "Broadform liability: Not included."**
    **Three quotes, R423k to R462k/mo, not one carries PL, products or employers' liability.** Also
    not included at Alpha: buildings combined, BI, accounts receivable, accidental damage, GIT,
    money, glass, fidelity, machinery breakdown, deterioration, GPA, D&O, umbrella.
  - 🚨 **ALPHA FINDING 4: the quotes disagree on vehicle values by R4,580,901 on the SAME 70.**
    HCV R53,132,476 (N) v R49,232,600 (A) · private R17,847,679 v R17,447,259 · LCV R2,917,060 v
    R2,636,455 · **buses and trailers match to the rand**. Per car: G63 R2,761,100 → **R3,366,480**
    (+605,380) · X5 R2,526,800 (**2026**) → R1,878,600 (**2023**) · M135i R1,225,671 (2025) →
    R860,271 (**2024**) · X7 M50d R1,585,400 → R1,900,600. **Two cars carry different MODEL YEARS on
    the two quotes.** Resolve against a real asset register, do not just take the higher number.
  - ✅ **ALPHA FINDING 5: the excess loadings are GONE. No night loading, no single-vehicle
    loading**, against Natsure's +5% and +5% cumulative. **So the "what shifts do they run" question
    does not arise at Alpha.** ⚠️ But the basis flips: Natsure **4.5% of VEHICLE VALUE** min R5,000
    (≈R45,000 on the average truck whatever the claim) v Alpha **10% of CLAIM** min R5,000.
    🎯 **Crossover ≈ R450,000: below it Alpha is far better, above it Natsure is.** Theft 15% of
    claim min R3,000 (A) v 20%/10%/nil-with-Ctrack of value (N). **The Ctrack clause is Natsure's
    alone; Alpha names no brand.**
  - ✅ **ALPHA FINDING 6: BAR R60,240.03 v R87,773.88, −R27,533.85/mo ≈ −R330,400/yr.** Bicycles
    6.00% v 7.00%, **air conditioning R2,298,999 at 5.20% v 8.50%** (≈R6,300/mo of the gap).
    ⚠️ But Alpha has **10 fewer items and R1,578,149 less SI**, so reconcile the lists first.
    ⚠️ **The 30 Trek bicycles are on BOTH quotes**, R5.98m to R6.41m.
  - ✅ **ALPHA GIVES THE FLEET LIST Natsure never did.** 45 trucks, almost all **Isuzu** FTR 850 AMT
    and FRR 600, one Fuso, one **2025 Volvo FH 520 6x4 truck-tractor R2,617,300 (reg "Required")**.
    By year 2019×2, 2020×9, 2021×1, 2022×7, 2023×6, 2024×12, 2025×8. ✅ **Nothing older than 2019, so
    Natsure's "inspection certificates for every vehicle 10 years and older" affects ZERO vehicles.**
    Plates span GP, ZN and NU, so the fleet sits across the six premises.
  - ⚠️ **Carried over to Alpha unchanged:** 🛰️ **63 of 70 "tracking required" with "Approved tracking
    device: Unknown"** (70-unit lead stands on both) · **fare-paying passenger liability "No" on both
    buses** at both insurers (2020/2021 Iveco 50C15 Sisonke midibuses, confirm they carry staff) ·
    **credit shortfall No on all 70** (BMW Finance noted on MK81FKGP) · **reg and VAT read
    "Required"** on all three documents · **"Included entities: refer to page 2" and page 2 is the
    cover summary**, no entity list in 190 pages · **declared turnover, wages and employees all
    BLANK** (same shape as Lomaen) · **Electricity Grid Failure exclusion** incl. surge on
    reconnection · towing thinner (R15,000 in/out and R15,000 wreckage v Natsure R25,000/R50,000
    plus optional non-accident towing R900,000 and Truck Assist).
  - **Source: `deal-notes/tshenolo_alpha_ALPHACOM205554.docx`** (+ `tshenolo_alpha_extract.txt`).
    📎 Arrived as a **.docx** after the Drive upload failed; extracted from `word/document.xml`.
  - Both quotes: **Compass Insurance FSP 12148, UMA Natsure HCV and Commercial FSP 50704**, broker
    Cartrack FSP 17266. HCV quoted by Olga Van Der Merwe, COM by Thuli Sibiya to
    brendan.kruger@cartrack.com. **Commission R38,659.50 + R26,200.77 = R64,860.27/mo =
    R778,323/yr.** Both reconcile to the cent. Both monthly policies, 12 territories, subject to
    confirmed claims experience, payment method "Cash deposit" against a debit-order condition,
    **VAT and company reg blank on both**.
  - **`HCVU192176`** (11 Sept, eff 01/10/2026, valid to 11 Oct) **R311,086.71**: vehicle R268,232.90
    + optional extensions R20,220.00 + Sasria R22,633.81. **55 vehicles, SI R61,174,651:** HCV 45
    R53,132,476 (5.50%, R5,411.64 ea) · trailers 2 R3,386,929 (3.00%) · LDV 6 R2,917,060 (4.00%) ·
    bus 2 R1,738,186 (4.50%). **No per-vehicle schedule in the PDF.**
  - **`COM192164`** (14 Sept, eff **01/11/2026**) **R150,768.60**: office contents R1,643.51 + AD
    R145.83 + fire R3,596.88 + theft R2,158.33 + **BAR R87,773.88** + EE R4,456.82 + **motor
    R45,179.94** + assists R480 + car hire R2,290 + road assist R390 + Sasria R2,653.41.
    **Six premises:** Lanseria (twice), Kimberley, Maitland CT, Mafikeng, **Denver JHB (plant and
    machinery R12,839,148)**. Lanseria stock R2,856,318, BAR R13,249,973, EE R503,761, theft
    R280,000 first loss. **No buildings SI anywhere** (leased, confirm).
  - 🚨 **FINDING 1: THERE IS NO PUBLIC LIABILITY ON EITHER QUOTE.** No PL, no products, no employers'
    liability. The only liability is motor third party. **They put sharps containers into hospitals,
    handle biohazardous waste on other people's premises and run training.** ⛔ **Ask Cules FIRST
    whether a THIRD policy carries it**; if not, the client would move to a programme without its
    characteristic cover. **Also absent everywhere: BI, fidelity, money, glass, GIT, machinery
    breakdown (on R12.8m of plant), deterioration of stock, environmental impairment liability.**
  - 🚨 **FINDING 2: R6,405,927 of TREK RACING BICYCLES on Business All Risks, 30 items at
    R300,000 to R785,952 each, R37,367.90/mo = R448,415/yr at 7.00%.** That is 43% of the BAR sum
    insured and 43% of its premium, on a medical waste company. Plus **"Air Conditioner
    R2,298,999 at R16,284.58/mo = 8.5% pa all-risks = R195,415/yr"** (stock at the same address is
    rated 0.275%). 🎯 **Together R53,652.48/mo = R643,830/yr = 36% of the commercial quote and 12%
    of the whole programme, against a claimed saving of R77,000/mo.** Are they the client's? Are
    they on the current policy? Get the air conditioning re-rated off all risks.
  - 🚨 **FINDING 3: 15 luxury cars, R17,847,679, EVERY ONE "Tracking System Name: Required /
    Tracking device installed: No"** (two also "Immobiliser: No"). Merc-AMG G63 R2,761,100 · BMW X7
    M60i R2,745,829 · BMW X5 R2,526,800 · Defender 110 R2,112,505 · RR Velar SVAD R1,820,979 · BMW
    X7 M50d R1,585,400 · BMW M135i R1,225,671 … **11 are over R350,000 and the quote says a tracker
    must be fitted BEFORE theft/hijack cover incepts = R16,822,004 with no theft cover on day one.**
    ⚠️ **Two cars carry NO registration** (the M135i R1,225,671 and a Suzuki Ertiga R255,500).
    🛰️ **70-unit lead across R79,022,330** (55 fleet + 15 cars), and on the cars it is a condition
    precedent. EE schedule already lists "Team Track Bin Tracking and Management" R35,000.
  - 🚨 **FINDING 4: the two quotes incept a MONTH APART**, 01/10/2026 and 01/11/2026, both monthly.
    Align them or there is a month of half-moved cover or double payment.
  - 🚨 **FINDING 5, and it is ours: the nil-excess theft benefit names a COMPETITOR.**
    *"**Ctrack** Tracking and Recovery Device operational on Heavy Commercial Vehicle or Trailer when
    the entire combination is stolen or hijacked in the same event: **NILL Excess**"* against
    *"Tracking or Recovery Device operational: 10% of the value of the vehicle"*. **Cartrack is the
    broker on this quote.** Dearest truck (R2,012,670) = **R201,267 a claim**; dearest trailer
    (R2,689,098) = **R268,910**. **Get Cartrack written in, in BOTH places (HCV/Busses and
    Trailers).**
  - 🚨 **FINDING 6: Sasria is wrong on BOTH quotes.** HCV declares R59,436,465 against a fleet of
    R61,174,651, **the R1,738,186 difference is exactly the two buses**. COM declares the 15 private
    cars as **"Goods Vehicles M2" at R18,219,979** against a motor SI of **R17,847,679**
    (**R372,300 out**, and private cars are not goods vehicles).
  - 🚨 **FINDING 7: clean-up is R250,000 a truck** (R11,250,000 over 45 HCV at R600/yr per unit) on a
    hazardous waste fleet, **and only on the trucks**, nothing on trailers, LDVs or buses. Ask for
    R1m/R2.5m/R5m and whether R11.25m is an aggregate. **Clean-up costs are NOT environmental
    impairment liability** (NEMA), same gap and same route as Bakers (Envirosure Spill Protect).
  - 🚨 **FINDING 8: third party is an AGGREGATE R5,000,000**: passenger liability R2,500,000 and
    fire/explosion R5,000,000 both sit **inside** *"any other event and the aggregate of (a), (b)
    and (c) R5,000,000"*. Reads like R7.5m, is R5m.
  - ⚠️ **FINDING 9: excess stacks and the basic is a % of VEHICLE VALUE, not of claim.** HCV/bus
    **4.5% of value, min R5,000** (= **R53,132 on the average truck**, every claim) **+5%
    single-vehicle +5% driving 23h00 to 04h00**, cumulative. ⛔ **Ask Cules what shifts they run**,
    healthcare waste often moves before dawn. Same shape as Cordiguard.
  - ⚠️ **Office contents look copied and one is rated 10× the others:** the same **R440,748** appears
    at Lanseria AND Kimberley to the rand (R104.68 = 0.285% and R101.00 = 0.275%), while a second
    Lanseria entry of R605,399 is **R1,437.82/mo = 2.85% pa**, all three described identically.
    ≈R15,500/yr. ⚠️ **Maitland and Mafikeng carry theft R20,000 and NOTHING else.** ⚠️ Lanseria
    theft is **R280,000 first loss** against R13.25m of BAR and R2.86m of stock at that address.
  - ⚠️ **National Power Failure (Blackout) Exclusion incl. load shedding** across the whole
    commercial policy. ⚠️ **Warranties that void cover** (not paperwork on a hazardous waste site):
    SAIDSA alarm with armed response + arming log, electrical CoC, fire equipment serviced annually,
    **SABS Class I lightning arrestor and Class II surge arrestor**, stock raised 150mm on pallets,
    **hazardous and flammable storage per OHS Act Reg 4 and SANS 02363**, **waste bagged daily and
    removed weekly**, ventilation, no smoking, keys in a locked fixed safe.
  - ⚠️ **Fleet quote not firm:** 3 years' loss history confirmed by the current insurer · signed
    proposal and debit order · **inspection/valuation certificates for every vehicle 10 years and
    older** (count unknown without the schedule) · *"Should the risk already be insured with Natsure
    HCV and Commercial this quotation will be null and void"* → **check which UMA the current policy
    sits behind** (Natsure also wrote Powerflow and Idol).
  - ⚠️ Also: windscreen on LDVs "Yes" with **0 vehicles** and R0.00; **car hire not taken** on buses
    and LDVs with a **7-day loss of use excess period**; **credit shortfall No** on all 70 vehicles;
    "Additional Third Party Liability: No" on LDV/PVT; 2 trailers averaging **R1,693,464** (dearest
    R2,689,098) is high, confirm.
  - **Sources: `deal-notes/tshenolo_natsure_HCVU192176.pdf` (33pp) and
    `deal-notes/tshenolo_natsure_COM192164.pdf` (119pp)**, both with text layers.
    📎 `COM192164` arrived via **Google Drive from iOS**, same route as Gateway, Vuyos and Bakers.
## RM System: 2 Sept 2026 recovery + open requests (read before touching data)

- **Second small loss, 2 Sept 2026.** Elizabeth's "Missing work" tab showed **geo fire (R4,100/m) and
  Kotto (R48/m)** gone from her Active Clients. Anne restored both from Command View → Recovery at
  ~14:40. Two rows out of a book is **below the write guard's threshold** (it only refuses a save that
  empties a book or halves it at 4+ rows), so it passed. Root cause NOT yet traced: get date/time/phone
  from her if it recurs and read `changes:<date>:elizabeth`.
- **Recovery also listed, still to restore once confirmed:**
  - **Cules: Twin Trans Pty CC and Quinton van der Merwe.** Cules confirmed 14:48: both won and active,
    **Twin Trans R31,000/mo, Quinton R12,000/mo.** ⚠️ Recovery proposes the *deal* figures (R2,800 and
    R4,129) because it rebuilds from the won deal; the deal record is frozen at signing. **Restore, then
    correct the book premiums to R31,000 and R12,000 in Command View.**
  - **Phillip: CS Continental Meat & Butchery**, deal at stage 6 (Proposal / Closing Set), R0, missing
    from his pipeline. Awaiting his yes/no.
  - "Needs a human eye (20)" list also had *Bronwyn · Agile Unlimited, details edited 2026-08-11 but the
    deal looks older*: ask Bronwan.
- **Group WhatsApp sent 2 Sept 14:47** (System support and comparisons group): explained write guard,
  snapshots, Missing work tab, v2026.08.27a, Lourie's payroll changes; asked **Bernard to send his change
  list** and everyone for suggestions. Bernard's list still outstanding.
- **Feature roadmap (Anne asked "what other cool features", 2 Sept):** full list in
  `deal-notes/rm-system-roadmap.md`. Suggested next 25k block (~30h): nightly data-health alert, one-tap
  undo per RM from snapshots, comm stat import, renewal calendar, version nag. Supabase Auth (20h) still
  parked but should precede the rest.

## Conventions
- Commit trailers used in this project:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` + `Claude-Session: …`
- Never put the model id in commits / code / PRs (chat only).
- People's pronouns: use they/them unless stated. **Jean = he.**
- 📲 **ALWAYS end a comparison with the Afrikaans WhatsApp for the RM.** Every pack ships with one:
  informal Afrikaans, English words mixed in, no em dashes, the headline number, the one finding
  that decides it, and what the RM must do next. Anne should never have to ask for it. (Standing
  instruction, restated 14 Sept 2026.)
- 🚫 **NEVER use an em dash (the long dash). Anne hates it and says it reads as AI-written.**
  This is permanent and applies to EVERYTHING: WhatsApp messages, client proposals, RM playbooks,
  e-mails, deal notes, chat replies. Use a comma, a colon, brackets, or start a new sentence
  instead. Also avoid the HTML entity for it in the pack templates.
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
  - 🆕 **ROUND 3 — MiWay + the FULL current Santam schedule (26 Aug 2026).** Detail appended to
    `deal-notes/integral-trading-silent-valley.md`.
    - **Current Santam `10000064816`** (98pp, eff. 3 Jul 2026, intermediary **PROFILE RISK MANAGERS
      CC** AGT4207099) = **R131,719.79** — motor R105,452.84 (**27 items summing to R31,311,815
      exactly** ✓) + GIT R14,918.01 + PL R1,452.32 + Sasria R9,883.62 + VAS R13.
    - 💰 **Intermediary commission R16,455.67/mo (R197,468/yr), broker fee R0.00** — the client is
      used to seeing a zero in the fee line. **That is the answer to Petrosure's fee question.**
    - **SEVEN named insureds**, not two: Integral Trading, **CGR Holdings**, **Serin South Africa**,
      **Fuel Me**, Silent Valley, **Investec Bank** (rights & interest), **Petrocure**. Any
      replacement must name all seven.
    - Current **GIT limit per load R1,000,000**, 12 territories, both FAP reducers confirmed
      (R100,000→**R20,000** own damage; R250,000→**R20,000** theft/hijack). Current **PL
      R10,000,000 per event, UNLIMITED aggregate**, work-away excess capped R25,000.
    - **MiWay `123806085` = R129,095.75** (reconciles ✓). ⛔ **REJECTED.**
    - 🚨 **THE FINDING: MiWay's "saving" IS the public liability section.** Motor R117,763.07 for
      **20 units** vs Santam R115,150.38 for **27** = **+R2,612.69 DEARER for seven fewer
      vehicles**; it pays for that by **deleting the whole R10m PL section** (−R1,452.32) and a
      cheaper GIT (−R3,800.67) carrying a **R67,500 hijack excess vs R20,000**. Net −R2,624.04 is a
      smaller policy, not a re-rating.
    - **R4,838,555 of fleet unquoted, 7 items** — the R2,415,000 T&TT trailer awaiting registration,
      **all four light vehicles** (KM75WBGP R700,000, LD70ZPGP R600,200, LP98BKGP R511,905,
      KS34GCGP R226,200) and both Paramount trailers (FVR386EC + FVR390EC R192,625 each).
    - 🚨 **And one that IS quoted but UNDER-INSURED: LW22DGGP R2,400,000 → R1,515,000, short
      R885,000** — average would settle it at ~63c in the rand. Worse than an omission because it
      looks covered. ⚠️ MiWay lists **MY40PXGP** where Santam has **MY40PZGP**.
    - ⚠️ **CORRECTS a working figure of ≈R9,359,555 "unquoted"** — that first pass matched trailers
      on sum insured instead of registration, so LW22DGGP and both 2026 FAW trucks (quoted as "TBA")
      dropped out of the match wrongly. **20 of 27 units is unchanged; the rand figures are above.**
    - 🎯 **ITS REAL VALUE: MiWay is the ONLY quote rated on the claims.** It prints *"December 2025 ·
      Vans & Trucks · Vehicle Accident (2 Losses) · R6 500 000"* on the face of the quote, and lands
      **R5,795.73/mo ABOVE Petrosure's R123,300.02**, which still reads *"Loss History: Tba"*.
      **That is proof Petrosure's number will move — use it in the reply.** ⚠️ But MiWay recorded
      them as *accidents*, both in Dec 2025, not **two hijackings one year apart** — correct it in
      writing before treating R129,095.75 as firm.
    - MiWay regressions: **TP R5m** (vs current R10m on the 10 truck-tractors; trailers only R1m) —
      *the same ceiling that benched Petrosure*; motor excess **10% min R30,000**; **+15% excess on
      any single-vehicle articulated accident without driver/road-facing camera footage** (→ video
      telematics lead); +R10,000 for <4yr or foreign licences; **passenger liability, environmental
      transport liability and credit shortfall all EXCLUDED** (Investec/Redtree noted); neighbouring
      + extended territories excluded (tolerable — diesel/RSA only — but record it as an instruction).
    - MiWay gains: **GIT load limit R1,350,000** (up from R1,000,000), **driver dishonesty INCLUDED
      on GIT**, side tank spill R250,000, towing R100,000, mech-breakdown tow R75,000 — all
      materially better than Petrosure's R15,000 towing / R10,000 wreckage and nothing above 3.5t.
    - ⚠️ MiWay proposal data is wrong: **"number of vehicles in the last 3 years: 10"** (it is 27),
      previous insurer **"UNDISCLOSED"**, risk address **No 1 Melrose Blvd** (Santam has Cnr Dekema
      & Steenbras, Wadeville), day AND night parking both **"VARIABLE"** — after two hijackings.
      Tracking names **Tracker/Netstar/SAIAS/VESA — Cartrack NOT named**, though Cartrack is already
      on 16 of 18 tracked units; quote warns *"some vehicles do not meet the security requirement."*
    - ⛔ **The hold stands.** MiWay is dearer than Petrosure and worse than staying.
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

- **Vuyos Funerals (Pty) Ltd** (funeral group, 11 premises across Soweto / Vanderbijlpark /
  Vosloorus; head office Shop 8 Mapatleng Shopping Centre, Devland 1811; 61 vehicles incl.
  **16 Mercedes Vito buses**). RM: **Elizabeth Schlebusch**. Full detail in
  `deal-notes/vuyos-funerals.md`. Analysed 25 Aug 2026. ⏰ **Anniversary 03/09/2026.**
  - **CURRENT: Old Mutual Insure `LD/M/02/MSURE/699973904`**, broker of record **Mellins Insure
    Brokerage (Pty) Ltd** (agency 9916857), mid-term adjustment eff. 23/03/2026, 91pp —
    **R151,685.30/mo = R1,820,224/yr.** 11 sections reconcile exactly.
  - **Santam `40318049` v1 R116,783.28 (−R34,902.02/mo ≈ −R418,824/yr, −23.0%)** · Auto & General
    `T6H407743` R135,249.12 (−R16,436.18) · Bryte R135,638.93 (−R16,046.37). **All three beat the
    incumbent.** 82% of Santam's saving is motor alone (R129,748.50 → R101,104.10) — and Santam
    quotes **63 vehicles against the current 61**.
  - 🚨 **THE FINDING — Santam dropped a zero.** Ten of eleven premises match the current schedule
    **to the rand**; **285 Granville Avenue, Robertville is R15,000,000 on the policy and
    R1,500,000 at Santam.** That single item is the *entire* R13,500,000 gap between Santam's
    R13.7m and the R27,200,000 both Bryte and A&G carry (which ties exactly to the current schedule
    less R260,000 of escalators). **Bryte and A&G are right; Santam is wrong.** Uncorrected, a fire
    at Robertville settles under average at ~10c in the rand. **Correcting it adds ≈R2,900–R3,400/mo
    → present ≈R120,000, NOT R116,783.28** — still R31,000+/mo below current.
  - 🚨 **SECOND FINDING — the current public liability carries a WORK AWAY EXCLUSION:** *"no
    indemnity … for liability arising from any work carried out elsewhere than at the premises
    occupied by the insured"* (+ a spread-of-fire exclusion). **Every funeral happens at a church, a
    cemetery or a family home.** **Bryte writes "General and Tenants/Workaway R5,000,000" into the
    limit for R295.83/mo**; Santam and A&G are silent → get both in writing. **Same shape as the
    Lomaen Medical find.** Retro date **01/09/2025**, so moving forfeits only ~12 months of tail —
    disclose it, but don't let it stall the deal.
  - 🚨 **THE BRYTE QUOTE IS WRONG TWICE and it changes the ranking.** Prints R136,128.65; true
    R135,638.93. (1) **Sasria block divides by TEN not twelve** — R29,382.73/yr shown as R2,938.27/mo,
    truly R2,448.56: **identical to the Lomaen quotes, so it is systemic in Bryte's spreadsheet.**
    (2) **The ANNUAL column carries one premises of glass instead of five** — R12,121.90 vs a true
    R56,201.50, **under-counting R44,079.60.** ⚠️ **CORRECTS an earlier working figure of
    R131,965.63** (derived by ÷12 of an annual that was itself wrong) — **Bryte is the dearest, not
    the middle**, and its broker fee is still "to be advised".
  - ⚠️ **Passenger liability R2,500,000 on ALL FOUR documents** — 16 Vito buses carrying mourners.
    **Not a regression; a standing gap nobody ever put to them.** Same shape as Wes-Kaap Busdiens.
    Third party R2.5m current/Santam/A&G, **R5m only at Bryte** (+ contingent & parking facilities
    R5m) — cheap fix is to ask Santam to price TP at R5m.
  - ⚠️ **Deterioration of stock is nowhere** — and the current schedule's **Electricity Grid
    Interruption exclusion names *"deterioration of stock, food or other items"*.** They refrigerate
    bodies: load-shedding + no deterioration cover is a live hole today. **No BI anywhere** (R0 on
    current, not selected A&G, R0 Bryte) — standing gap. No machinery breakdown on the refrigeration.
  - ⚠️ **Santam's theft covers ONE premises** (Devland); **Bryte has no theft section at all.**
  - ⚠️ **A wrong address originates with the incumbent and has been copied onto the quotes:**
    *"9368 Mophiring Street Orlando, **Cato Ridge, 3680**"* — Orlando is Soweto, Cato Ridge is KZN.
    Carries buildings R2,000,000, fire, glass R220,398 and accidental damage.
  - ⚠️ **R4,771,300 of non-funeral vehicles** on the fleet as "business/pool drivers": 2021 BMW X6 M
    R2,514,000, 2012 Merc SL 500 R1,635,000, 2023 Harley Tri Glide R622,300 (~17% of fleet value).
    Fleet SI disagree: **R28,331,021 (A&G) vs R30,211,680 (Bryte)**.
  - 💰 **FAIS disclosure: Mellins earns R17,599.12/mo = R211,189/yr** on this account (broker service
    fee shows R0.00). **Expect a same-day counter-quote** — the work-away exclusion is the answer a
    price cut can't give.
  - 🛰️ **54-unit Cartrack lead, and we're already the incumbent:** only **7 of 61 vehicles** carry a
    tracking warranty on the current policy and **all seven are Cartrack**, named on the schedule.
  - ⚠️ **A&G charges the R75 broker fee TWICE** (once on motor, once on non-motor).
  - **Deliverables built 25 Aug** (`vuyos_proposal_content.html` / `vuyos_playbook_content.html`):
    client proposal PDF (7pp) + RM playbook PDF (6pp, INTERNAL), rebuilt against the current
    schedule once it arrived via Google Drive. Extract kept at `vuyos_current_om_extract.txt`.
  - 📎 **How the current policy arrived:** it would not attach in the Claude web app — Anne uploaded
    it to **Google Drive → My Drive/Comparisons** and it was pulled with the Drive MCP tools
    (`search_files` → `download_file_content`, base64 → PDF → pypdf). **Use this route for any
    file that fails to attach.**
