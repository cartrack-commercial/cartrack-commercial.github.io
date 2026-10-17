# Handover: "RM Quote comparison- Main coding"

Owner of this record: **Root Innovations (Pty) Ltd** (Anné Kruger). Snapshot written **17 October 2026**.
Chat session `session_01WYo9baZkrtwYdeTMUmKWgn`, created **13 July 2026**, still running.
Kept current from now on: every delivery, decision or result is added under the right heading, dated.

Sources: codes [S00] to [S12] resolve to files via `deal-notes/handover-source-map.md` on branch
`claude/rm-portal-chat-location-bef5o5` (kept with the client deal notes, not in this file).

Naming rule for this file: no client, member or colleague names. Colleagues appear by role. The host
company is "the host agency": the commercial insurance division of a vehicle-tracking group, an
authorised FSP. Client detail lives in the deal notes named by path in section 3, not here.

---

## 1. What this chat is for

The working session behind the host agency's commercial division: Anné's build-and-analysis desk.
It maintains three internal web apps (a launcher, an RM pipeline and payroll system, and a premium
comparison portal) and produces hand-built insurance quote comparisons for the relationship managers
(RMs): reconcile the client's current schedule and every competing quotation to the cent, find the
cover that decides the deal, and ship a branded client proposal PDF, an internal RM playbook PDF and
an Afrikaans WhatsApp brief. **Started 13 July 2026.** **Status 17 October 2026: active.** Every
comparison request in the RM queue as at 17 Oct 2026 has been delivered. The open items are insurer
reissues and client information (section 6). As of 17 Oct 2026 the chat runs under Root Innovations.

---

## 2. What Anné has done (facts, dated)

**Systems and governance**
- Commissioned and runs three internal web apps on GitHub Pages for the division (launcher live from
  6 Jul 2026; RM System and comparison portal live in the same period). Deploys by pushing to `main`.
- Moved the RM System's database to a paid Supabase plan (Pro: daily backups, 7-day retention).
- 12 Aug 2026: led recovery after a data-loss incident in the RM System (RMs' leads overwritten).
  Commissioned the structural fix: a write guard and snapshots (section 3).
- 2 Sept 2026: restored two lost client rows for an RM from the Recovery tab. Briefed the whole RM
  group by WhatsApp on the write guard, snapshots, "Missing work" tab and payroll changes.
- 3 Sept 2026: commissioned a security position and an RLS check script for the RM System, and
  received the advice that Supabase Auth (≈20h) should come before new features. Parked.
- 16 Sept 2026: set the house rule that client-facing proposals use black heading blocks only, and
  that only internal playbooks are coloured. All packs brought into line.
- 21 Sept 2026: set the rule that the host agency's accounts executive is never named in any
  material, and had the name scrubbed from code, packs and notes.
- 21 Sept 2026: delivered a four-document handover pack (RM System architecture, security position,
  comparison method, portal build spec) to two developers from the host group. Kept the security
  document out of version control.
- 22 Sept 2026: decided to remove a management performance page from the public launcher after
  finding it assigned real people to a simulated plan in a public repository.
- 28 Sept 2026: gave the two developers write access to two app repositories. 29 Sept 2026: exposed a
  copy database schema to their API at their request.
- 9 Oct 2026: requested and received a bundle of all code produced in this chat (212 files).
- 17 Oct 2026: asked who the two developers are and what they were given. Received an audit of their
  copy app and access (section 6). Decided that compliance stays with her and is not handed over.

**Comparisons delivered (built in this chat at Anné's direction, for the RMs)**
- 25 client accounts analysed, 13 Jul to 17 Oct 2026. 34 branded client and playbook PDFs and 44
  content sources are held in `deal-notes/`. Breakdown and numbers are in section 4.
- 17 Oct 2026 alone: four accounts delivered. A new-business policy review (5pp + 6pp), a fuel
  hauler round 3 (7pp + 7pp), an abattoir reissue (7pp + 7pp) and a civil contractor three-way
  (6pp + 6pp), each with its Afrikaans WhatsApp.

**Sales and results**
- A cheese manufacturer group's fleet and property deal was reported signed at **R210,000/month**
  premium. The RM posted it in the division WhatsApp group between 8 and 12 Oct 2026. Anné built its
  four-way comparison and the lean 3-page closing proposal (7 to 8 Oct 2026).
- Other closes are not recorded in this chat. Add them here as they are confirmed.

**Commercial model**
- Between 9 and 17 Oct 2026: asked how to charge RMs for comparisons. A draft was prepared: a monthly retainer of
  R3,000 covering 8 comparisons, with extras billed per comparison. **Not yet decided.**

---

## 3. What has been built

| Name | What it does | Users | State | Where it lives | Built with | Reuse for Root Innovations |
|---|---|---|---|---|---|---|
| Launcher | Branded landing page with tiles to the apps, home-screen icon, service worker | Division staff | Live | Repo `cartrack-commercial/cartrack-commercial.github.io`, branch `main`; `index.html` (17,740 bytes), `sw.js`, `manifest.webmanifest`; URL `cartrack-commercial.github.io` | Single-file HTML/CSS/JS, GitHub Pages | Pattern only (strip brand) |
| RM System | Pipeline, Active Clients book, payroll and commission, Command View for management, Recovery tab, write guard, snapshots, Missing work tab, Copy for Accountant | RMs, management, payroll administrator | Live, **v2026.09.22a** (last code commit 22 Sept 2026) | Repo `cartrack-commercial/cartrack-rm-system`, `main`, `index.html`; URL `cartrack-commercial.github.io/cartrack-rm-system/`; Supabase project ref `govvmqgpxzbqghzgcitb` (tables `deals`, `portfolio`, `payroll`, `config`, `orgs`, `users`, `activity`) | Single-file HTML, supabase-js, Supabase Postgres + PostgREST, localStorage outbox | Code after stripping (keys, passcodes, seed data, names); data never |
| Premium Comparison portal | Upload schedule + quotes, in-browser extraction (pdf.js, xlsx, lazy OCR), editable review, report with client/RM views, 18-rule schedule audit | RMs | Live (last commit 28 Sept 2026) | Repo `cartrack-commercial/cartrack-premium-comparison`, `main`, `tool.html`; URL `cartrack-commercial.github.io/cartrack-premium-comparison/tool.html` | Single-file HTML, pdf.js, SheetJS, Tesseract | After stripping brand |
| `cartrack-proposal` pack builder | Renders client proposals and RM playbooks to branded A4 PDF from a content HTML file | This chat; any Claude Code session | Live | `.claude/skills/cartrack-proposal/` in the launcher repo (branch `claude/rm-portal-chat-location-bef5o5`) and a cleaned copy in the portal repo (`main`, 28 Sept 2026) | Python `build.py`, headless Chromium/Chrome, house CSS, Saira + IBM Plex fonts | After stripping brand (logos, colours, footer FSP lines). **Prime Root Innovations template** |
| Deal notes and pack sources | One Markdown note per account plus `*_proposal_content.html` / `*_playbook_content.html` and built PDFs | This chat, RMs (PDFs) | Live record | Launcher repo, branch `claude/rm-portal-chat-location-bef5o5`, folder `deal-notes/` (25 notes, 44 sources, 34 named PDFs) | Markdown, HTML | Not as is (client data). Structure and section order reusable |
| Working memory | Hand-off notes so a fresh session starts informed: apps, method, house rules, every account | This chat | Live | Launcher repo, `CLAUDE.md` | Markdown | After stripping (client and personal data) |
| Comparison kickoff prompt | Reusable prompt to start a comparison | Anné | Live | Launcher repo, `COMPARISON_PROMPT.md` (20 Jul 2026) | Markdown | As is, after a brand check |
| Handover pack to developers | RM System architecture, comparison method, portal build spec, and (off-repo) security position | Two developers | Delivered 21 Sept 2026 | Launcher repo `handoff/` (`01-rm-system.md`, `03-comparison-method.md`, `04-portal.md`, PDFs, `build/build_handoff.py`); doc 2 kept off-repo | Markdown, Python, Chromium pagination by measured layout | Method doc and PDF paginator: after stripping |
| RLS check script | Reports RLS state, policies and anon grants per table | Anné (run in her browser) | Ready | `deal-notes/rm-system-rls-check.sql` | SQL | As is |
| RM System roadmap | Prioritised feature list with hours | Anné | Draft (2 Sept 2026) | `deal-notes/rm-system-roadmap.md` | Markdown | Pattern only |
| Separate-business starter brief | Brief for building another firm's app on the same pattern, sharing no data | Anné | Draft (12 Aug 2026) | Launcher repo `eminent-wealth-starter-brief.md` | Markdown | As is |
| Claude artifacts | App wiring map (3 Sept 2026), RM System security position (22 Sept 2026), early comparison frames (13 to 14 Jul 2026) | Anné | Published, private | `claude.ai/code/artifact/b0838e98-0833-45b9-b917-dd4948279f67`, `claude.ai/artifact/PaUibU2kGcDZ28PuJjKCXU`, and four comparison frames listed on the session | HTML | Wiring map pattern only |
| Code bundle | Zip of all code from this chat, 212 files, 8 folders, README | Anné | Delivered 9 Oct 2026 | Session scratchpad only (ephemeral); copy is with Anné | Zip | Archive |
| Developers' copy app | A Vercel app on a `cia` schema copy, built by the two developers, not by this chat | Developers | Theirs, last synced 6 Oct 2026 | `cia-phi-five.vercel.app`, Supabase schema `cia` | Their stack | Not ours |
| Performance Intelligence page | Management pack on simulated data | None | **Abandoned**, deleted 22 Sept 2026 | Git history only | HTML | Not at all as built. Approach reusable with roles, never names |

IP note: these were built for the host agency's division. Before reusing any code or template in Root
Innovations, confirm what the arrangement with the host agency allows.

---

## 4. Proof points (anonymised; source in brackets)

**Volume**
- 25 commercial insurance accounts compared in about 14 weeks (13 Jul to 17 Oct 2026). 34 branded
  PDFs delivered (`deal-notes/`).

**Savings found, monthly premium, as quoted**
- A 228-vehicle waste fleet: **−R54,109/mo unconditional** (−R649,312/yr), with the savings-fund
  maths reconciled exactly [S00].
- A long-haul transporter, 47 units, five markets: **−R14,657/mo** (≈ −R175,878/yr) on the only quote
  that held third party at R10m ([S02]).
- A civil contractor group, three policies: **−R13,666/mo as quoted, −R11,940/mo once corrected**
  (≈R143,000/yr) ([S03]).
- A funeral group, 61 vehicles: lowest quote **−R34,902/mo (−23%)**. Its building cover was found
  understated by R13.5m, so the presentable figure was ≈R120,000/mo, still over R31,000/mo below
  current ([S04]).
- An x-ray equipment installer: **−R8,840/mo (−17.3%)**, while adding the work-away liability the
  current policy excluded ([S05]).
- A retail butchery: fleet **−R5,879/mo (−21.9%)**; whole account −R9,218/mo ([S00], [S06]).
- An IT consultancy: **−R5,456/mo**, with data reinstatement up tenfold and liability consolidated to
  R20m [S00].
- A security guarding company: −R2,634/mo, plus passenger liability added for guards ([S07]).

**Losses prevented (advice that said "do not move" or "fix first")**
- A fuel hauler: found a second policy (215 vehicles, not 30). That reversed a move which would have
  cost **+R18,606/mo** and forfeited **R562,632** of insurer bonus. A later quote −R4,407/mo was shown
  to leave out R15,612/mo of cross-border cover ([S08]).
- A butchery's commercial policy: moving would save R741/yr against a R42,638 bonus (57 years of
  saving). Advised to stay ([S06]).
- A diesel hauler with two hijackings: showed one hijack would cost +R280,000 in excess at the
  cheaper insurer, 33 months of its saving. Advised to hold ([S09]).

**Errors caught in insurers' quotations**
- Sasria divided by 10 instead of 12, on quotations from three insurers' spreadsheets, across four
  accounts ([S05], [S04], [S10], [S03]).
- A dropped zero on a R15m building ([S04]) and on R21.7m of rent cover at a
  special-needs school ([S11]).
- A quote covering 20 of 27 vehicles and under-insuring one by R885,000 ([S09]).

**Lead generation for the host group's core product**
- ≈580 vehicle-tracking units identified as policy conditions or theft-cover gaps across 15 accounts.
  The largest were 179, 93 to 112, 70, 54 and 43 units (deal notes, all S-codes).

**Sales**
- A cheese manufacturer group signed at **R210,000/month** premium (division WhatsApp, 8 to 12 Oct 2026).

**Systems**
- RM System first paint cut from **13.7s to 0.47s** worst case (30 Jul 2026, [S00]).
- Comparison portal's all-in premium reader: correct on **10 of 10** real schedules, up from 3 of 10
  (portal commit 28 Jul 2026).
- Data-loss safety net found silently failing: no snapshot written from 12 Aug to 22 Sept 2026, and a
  halving gap in the write guard. Both fixed 22 Sept 2026 (RM System commit `31fad50`).

---

## 5. Skills and methods shown

- **Reconcile to the cent** on the all-in monthly figure (VAT, fees, Sasria). Print the as-quoted
  total beside any corrected one.
- **Match fleets by registration, not by count or value.** Two items share a value by coincidence;
  two registrations never do.
- **Find the decisive cover by client type:** pollution for tankers, fare-paying passenger liability
  for buses, work-away liability for installers and funeral operators, hoists for workshops,
  liability for schools.
- **Separate standing gaps from regressions**, and price what a move forfeits (bonuses, funds,
  retro dates) against what it saves.
- **Read every page:** endorsements contradict schedules (excess bases, fire sub-limits, tracking
  warranties). The decisive line is usually on page 40, not page 2.
- **Two-document deliverable:** a sober client proposal and a coloured internal playbook, plus an
  Afrikaans WhatsApp with the number, the finding and the next step.
- **Data-safety engineering** on a client-side app: write guards, snapshots, recovery from payroll
  history, two-phase boot.
- **Recovering files when uploads fail:** Gmail "Add to Drive" or Drive upload, then the Drive
  connector. HEIC conversion, scanned PDFs read as images.
- **Judgement under pressure:** "less is more" closing proposals (3 pages) when the RM needs to
  close, and full teardown playbooks when the RM needs to argue.
- **Governance:** keeping security weaknesses and personal names out of public repositories, and
  removing work that exposed them.

---

## 6. What is open (17 Oct 2026)

**Waiting on insurers (RMs to send the reissue e-mails in their playbooks)**
- Civil contractor: plant quote list and name, Sasria ÷12 on two quotes, liability extensions
  restored. Two quotes lapse 5 and 11 Nov 2026.
- Abattoir: pollution cover on the diesel tanker, and written confirmation that R5m third party
  covers fire. Quote lapses about 30 Oct 2026.
- Fuel hauler: cross-border liability and EIL priced by the new market. Truck excess. Tracking brand
  named. Goods-in-transit commission and driver fidelity.
- Cheese manufacturer group: fleet list from the RM's 5 Oct e-mail; incumbent's reply; insurer replies.

**Waiting on clients or RMs**
- New-business policy review: real premium (debit order) and a market quotation (RM).
- Abattoir: the full 72-page current schedule, and where the tanker is insured today.
- Medical waste fleet: current schedule arrived 21 Sept 2026 and the deal was ungated. Still open: the
  three-year claims record, liability priced by both insurers, a re-rate of one quote to the asset
  register, shift patterns ([S12], "What is still open").
- RM System: one RM's change list (outstanding since 2 Sept 2026). Two won clients to restore and
  correct (R31,000 and R12,000/mo). One pipeline deal awaiting the RM's yes or no.

**Waiting on Anné**
- Decide the RM charging model (retainer draft above).
- Decide whether to remove the accounts executive's name from the portal repo's design-system readme
  (offered; not yet done).
- Decide whether to e-mail the developers on the database move and payroll access (offered; not drafted).
- Run the RLS check SQL in her browser. Supabase Auth (≈20h) is still parked.

**Do not merge:** RM System PR #2 and launcher PR #2 (standing instruction). Stale branches still carry
the accounts executive's name.

**Next three steps**
1. RMs send the four reissue e-mails this week. Packs are rebuilt as replies land (the abattoir
   lapses first, about 30 Oct).
2. Anné decides the RM charging model, so Root Innovations can invoice from November.
3. Strip the `cartrack-proposal` skill and the comparison method into a Root Innovations template
   kit, and confirm the IP position first (section 3 note).

---

## 7. Never reuse from this chat (kind and location only; no values)

- **Client schedules and quotations (source PDFs)**: chat uploads, Google Drive "My Drive/Comparisons",
  OneDrive folders on Anné's Mac. Some source PDFs and extracts **are committed** in the public launcher
  repo under `deal-notes/`: four quotation PDFs, a current schedule PDF, a .docx quotation and nine
  text extracts (fuel hauler, medical waste fleet, funeral group, x-ray installer, diesel hauler, school). Treat them as client data. Consider removing them and purging the history.
- **Client personal and business data**: contact names, e-mails, phone numbers, company registration
  and VAT numbers, addresses, policy numbers, bank account fragments. These sit in `deal-notes/*.md`,
  `CLAUDE.md`, and the pack sources.
- **A private client's ID number**, used as a PDF password: in a Word file in the deal folder and in
  chat uploads. Quote passwords sit in an RM's e-mail.
- **Supabase anon key**: in the RM System's `index.html` (public repo).
- **Master passcodes and PINs**: in the RM System's `index.html` (public repo) and the `config` table.
- **RM salaries and commission**: Supabase `payroll` table and the `cia` copy schema.
- **A temporary password** shared with a developer: in a WhatsApp screenshot (chat upload).
- **Seed prospects with real names and premiums**: `SEED_DEALS` in the RM System's `index.html`.
- **The host agency's accounts executive's name**: never, in any form.
- **The actuary's call-centre file** (real agent names and performance): session upload only.

---

## 8. Lessons

1. A failed read and an empty table look identical. Anything that writes on emptiness needs positive
   proof (12 Aug 2026 data loss).
2. An empty `catch` hides a broken safety net. The snapshots never wrote for six weeks.
3. Count policies before comparing. A second policy reversed one recommendation and enlarged another.
4. Insurers' spreadsheets repeat the same error: check Sasria ÷12 on every quote.
5. A number on our pack that is on neither the quote nor the schedule reads as our mistake. Show the
   as-quoted figure beside every correction.
6. Public repositories are public. Names, passcodes and simulated plans with real owners do not
   belong in them.
7. The decisive line is in the endorsements, not the summary page.
8. The RM needs the closing number on page 1 and the argument in the playbook. "Less is more" for the
   client and full detail for the RM.
9. Write the business description correctly. Two accounts were insured under a description of a
   business they do not run.
10. Moving is not free: bonuses, funds and claims-made retro dates are part of the price.

---

### Change log
- 17 Oct 2026: handover created (snapshot).
