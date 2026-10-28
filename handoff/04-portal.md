# The comparison portal: state of play and build spec

**Cartrack Insurance, Commercial Division. Handoff document 4 of 4.**
21 September 2026. Source read at `cartrack-premium-comparison`, `tool.html`, 3,897 lines.

Read document 3 first. This document is about which parts of that method a machine can do.

---

## 1. What it is

`cartrack-premium-comparison/tool.html`, a **single HTML file**, served by GitHub Pages at
`…github.io/cartrack-premium-comparison/tool.html`. No back end, no build, no accounts.

**Nothing leaves the device.** Extraction runs entirely in the browser: `pdf.js` and `xlsx` are
self-hosted in `assets/vendor/`, and Tesseract OCR is lazy-loaded from a CDN only when a document
has no text layer. Drafts are held in `localStorage`. No client schedule is ever uploaded anywhere.
That is a genuine strength and it should be preserved: these documents are third-party confidential.

Three steps: **Upload → Review → Report.**

---

## 2. What it does today

### Extraction

- PDFs via `pdf.js`; spreadsheets via `xlsx`; **OCR fallback via Tesseract** when there is no text
  layer.
- About **twenty format-specific parsers**, written against the documents that actually came in:
  Bryte proposals, OUTsurance schedules, Frontline schedules, generic current-policy schedules,
  vehicle registers, and terms tables.
- **Insurer identification** from filename and body text against a list of sixteen insurers.
- **All-in premium detection** (`allInPremium`, `fleetTotalPremium`, `premiumIsAnnual`,
  `fleetSasria`), which is the single most useful thing it does: it tries to find the true all-in
  monthly rather than the headline, and it detects when a figure is annual.
- **A fleet catalogue parser with a reconcile-or-total guard.** It itemises a fleet only when the
  line items sum to the stated total; otherwise it keeps the exact total and asks the RM to
  itemise. That guard is the right instinct and should be the pattern for everything added later:
  **produce a checked number or an honest blank, never a plausible guess.**
- **Automatic split of multiple insurers into separate columns.**

### Review

A seeded, fully editable table. Every extracted figure is a suggestion the RM can correct. Line
status and flags are computed as they type.

### Report

A branded report matching the PDF packs, with a **client view / RM view toggle**, verdict cards,
a savings chart, per-building sections, head-to-head tables, an executive summary and a
recommendation. It also has a **"send to book"** handoff that encodes a deal for the RM System.

### The schedule audit

The most valuable part, and the part closest to document 3. It runs about **twenty-five rules**
over the raw text of the current schedule and the proposal, classified as `gap`, `check`, `play`
(a Cartrack opportunity) or `time` (timing or forfeiture):

**Retroactive dates and claims-made:** proposal restarts the retro date at inception · proposal's
retro date is materially later than the current one, with the gap in months · no retro date stated
· mismatched retro dates within the current policy.

**Cover gaps:** defective workmanship and products liability absent for a contractor · umbrella
carrying a minimum-underlying-limit condition · passenger liability reduced · passenger liability
sitting on an **e-hailing** form · the quotation covering fewer vehicles than the schedule · a
lower sum insured, with the average warning · agreed value not carried across · contents quoted
with an exclusion · financed assets with no credit shortfall · no goods in transit on a fleet.

**Wording traps:** third-party liability carrying a fire or explosion sub-limit · motor security
wording that contradicts itself · more than one insurer named on the quotation.

**Conditions:** warranties and conditions precedent listed out (surge arrestor, electrical CoC,
fire equipment, linked alarm) · subject to survey · conditional on claims experience.

**Timing and opportunity:** profit share or savings fund detected, with the forfeiture warning ·
a current schedule that is roughly ten months old or more · **telematics excess waiver present,
confirm Cartrack is on the approved list** · **tracking condition present, the Cartrack angle** ·
cross-border and territorial terms present.

---

## 3. What it cannot do, honestly

- **It cannot match hand-work on a messy or photographed schedule.** No text layer means OCR, and
  OCR on an iPhone photo of a faded fax is not a basis for a figure that goes to a client.
- **It cannot make the cover judgement.** It flags patterns in text. It does not decide whether a
  reduced limit matters for this client, which is the thing that wins deals.
- **It does not compare sums insured item by item** against the current schedule. This is the
  single biggest gap, and it is the check that caught the two most valuable findings of the year.
- **It does not verify arithmetic.** It reads totals; it does not test whether the sections sum to
  them, or whether the annual column divided by twelve equals the monthly column.
- **It does not model excesses at all.**
- **It does not reconcile a vehicle register** by registration number.
- **It does not read claims histories.**
- **It knows nothing about the taxonomy in document 3** beyond the twenty-five text rules above.
- **It cannot tell you it failed.** A parser that finds nothing returns nothing, and a blank field
  in Review looks the same whether the document did not contain the figure or the parser could not
  find it.

### And the real state of play

**The last commit to the portal is 28 July 2026.** Since then the division has produced roughly
thirteen comparisons: Powerflow's PI addendum, Integral rounds two and three, Idol, Lomaen,
CS Continental round two, Gear Lab, Vuyos, Wes-Kaap round six, Cordiguard, Arboretum, Gateway,
Bakers and Tshenolo. **Every one of them was done by hand.**

So the portal encodes the method as it stood in July. Everything learned since then, which is most
of document 3, is in the deal notes and not in the tool. That is the gap to close, and the list
below is ordered by what actually caught something.

---

## 4. Build spec, prioritised by what has actually caught things

Each item below cites the live finding that justifies it. Nothing speculative is on the list.

### Priority 1: the checks that found the most money

**1.1 Item-by-item sum insured diff against the current schedule.**
Extract every sum insured from the current schedule and from each quote, match by section and item
label, and report any item differing by more than a small tolerance, sorted by rand difference.

> **Evidence.** Gateway School: the current policy carries rent at **R21,677,345**; two quotes
> matched it; the cheapest quote carried **R2,167,734**, short **R19,509,611**. Vuyos Funerals:
> one premises at **R15,000,000** on the policy and **R1,500,000** at the cheapest insurer, which
> was the entire R13,500,000 gap between that quote and the other two. **In both cases the
> cheapest quote was cheapest partly because it was not quoting the same policy**, and in both
> cases a machine would have found it instantly.

Output must include the **average warning** in rands: if a loss occurs at the under-stated item,
settlement is roughly (quoted SI / true SI) in the rand.

**1.2 An arithmetic verifier.**
Three tests, run on every document:

- do the section premiums sum to the stated total, to the cent;
- does the annual column divided by twelve equal the monthly column **for every block**;
- does VAT reconcile at 15% of the pre-VAT figure.

> **Evidence.** One insurer's quotes divide the **Sasria block by ten instead of twelve**, which
> was found independently on **Lomaen Medical and Vuyos Funerals**, so it is systemic in that
> spreadsheet, not a one-off. On Vuyos the same document also carried **one premises of glass in
> the annual column instead of five**, understating by R44,079.60, and correcting both moved that
> quote from the middle of the field to the most expensive. An earlier working figure had to be
> withdrawn because of it.

**1.3 Vehicle register reconciliation, matched on registration.**
Match vehicles across documents on **registration number**, never on sum insured. Report: count
per class, registrations present on one document and not another, transposed characters,
registrations reading `TBA` or `Required`, and **model years that differ between quotes for the
same vehicle**.

> **Evidence.** Matching on sum insured produced a **wrong answer on Integral Trading** and had to
> be corrected: an earlier pass reported about R9.36m unquoted when the true figure was R4,838,555
> across seven items. Gateway had **two transposed registrations** (`XYG685GP` for `YXG685GP`,
> `HG38XBGP` for `HG38BXGP`), which is worse than a blank because it looks complete. Tshenolo's two
> quotes disagree by **R4,580,901** on the same seventy vehicles and carry **different model years
> for two cars**. Hamisa's Kgahlisa quote covered **four of seven vehicles**, R1,384,003 unquoted.

**1.4 Sasria cross-checks.**
Three of them:

- **declared Sasria value against the scheduled sums insured**, and name the difference;
- **category sanity**: private cars must not be declared as goods vehicles, a school's buildings
  must not be declared residential;
- **Sasria as a fleet-identity test.** Sasria is a statutory rate on declared values, so two
  documents landing within a few hundred rand of each other are covering the same risk.

> **Evidence.** Tshenolo declares **R59,436,465** against a fleet of R61,174,651, and the
> difference is exactly the two buses; its commercial quote declares fifteen private cars as
> **"Goods Vehicles M2"**, R372,300 out. Lomaen declares **R0** against "commercial 3,500kg and
> over" while scheduling two Hinos. Gateway's school buildings are recorded as **"Residential"**.
> And the identity test is how the Bakers question was settled: **R31,732.51 against R31,511.54**,
> R221 apart, proving the two documents covered the same 215 vehicles.

### Priority 2: the checks that decide recommendations

**2.1 An excess model.**
Extract the excess basis per item, then **compute the effective excess across a range of claim
sizes** and report the crossover. Apply loadings. Flag conditional penalty excesses separately,
because they behave as exclusions.

> **Evidence.** Tshenolo: **4.5% of vehicle value minimum R5,000** against **10% of claim minimum
> R5,000**, crossing over at about **R450,000**, so neither quote is simply better and the
> recommendation turns on the claim profile. CS Continental: a base excess that looks worse
> (10% minimum R30,000) but is bought down by three reducers to a **flat R5,000 inner excess**.
> Integral: one hijack at the dearer excess **eats 33 months of the saving**. Gateway: **+25% of
> the claim** where the required tracker is absent.

**2.2 Liability basis and limit extraction.**
For every liability section: occurrence or claims-made, retro date, **per-event against aggregate**,
sub-limits, and the presence or absence of a **work away** extension. The audit already reads retro
dates; this extends it to structure.

> **Evidence.** **Work away** alone accounts for three of the best findings of the year: Lomaen
> Medical (a business that installs x-ray machines at hospitals, with an explicit work-away
> exclusion), Vuyos Funerals (every funeral is at a church or a graveside), Cordiguard (a guarding
> company's only liability is at other people's premises). Tshenolo's third party reads as R7.5m
> and is **R5m**, because passenger and fire sit inside the aggregate.

**2.3 A conditions-precedent register.**
One table per account: every condition the cover depends on, whether the schedule records it as
satisfied, and a count. Tracking required against tracking fitted is the main one and should be
counted explicitly.

> **Evidence.** Gateway: **24 of 25 vehicles** record a tracking device as required, none fitted,
> **written as a warranty on the policy they hold today**, on buses carrying special-needs
> children. Tshenolo: 63 of 70. Cordiguard: all 25. CS Continental: all nine fields blank.
> Bakers: three vehicles with no theft cover today. This register is simultaneously the most
> serious service finding and the Cartrack lead.

**2.4 Bonus and fund quantification.**
The audit already detects a profit share or fund. Make it **quantify**: pull the projected bonus
amount and the date, and express it against the monthly saving.

> **Evidence.** CS Continental: a projected **R42,637.61** bonus against a **R61.77/mo** saving,
> so the bonus was worth **57 years** of it, and the correct recommendation was not to move that
> policy. Bakers: **R562,632.03** across two policies. And the trap in the other direction: a fund
> quote's "annual savings R1,768,416.95" is the client's **own money**, reconciling only with
> sequential commission deduction.

### Priority 3: credibility checks, cheap to build

**3.1 Entity and admin checker.** Insured names compared across every document, including how many
entities each names · VAT number format (South African is ten digits starting with 4) · company
registration format · placeholder dates · insurer named in the footer against the insurer on the
title · two documents sharing one quote number.

> **Evidence.** Gear Lab quoted **two different companies**, a 2000 registration and a 2025
> registration at the same address, and printed a **7-digit VAT number**. Gateway did the same.
> CS Continental's quote carried **the incumbent insurer's own registration and VAT in the
> policyholder fields**. Bryte-titled quotes footed *"Quotation, Hollard Insurance Company"* on two
> unrelated accounts. `01/01/3000` appears on Gear Lab and Arboretum. Two Arboretum PDFs share one
> quote number and **the premium did not move when the limit was corrected**.

**3.2 Claims record extraction and the "is this quote rated on it" test.** Pull the claims
disclosure off the incumbent's schedule, compute a rough loss ratio against premium, and then
search each quote for whether it says it was **rated on** that record or merely **asks for** it.

> **Evidence.** CS Continental: about **150%** over 24 months, on the incumbent's own schedule.
> Idol: 58 losses, 96%. The reverse matters too: Bakers projects a bonus on both policies, which
> requires a ratio at or under 30%, so the recent record is good. And the decisive use of it: on
> Integral, the **only** quote that printed the R6,500,000 loss on its face landed R5,795.73/mo
> **above** the quote still reading *"Loss History: Tba"*, which is proof the unrated number will
> move.

**3.3 A scan quality gate.** Before extracting, count distinct grey values per page. Two means a
dead pure black-and-white scan with the figures gone. **Refuse to extract and say so**, rather than
returning numbers nobody should trust.

> **Evidence.** Arboretum was blocked for two weeks on a scan with **two grey values**; a rescan
> with 200+ made every sum insured legible and unblocked the deal. Gateway, Bakers' GIT schedule
> and one Hamisa schedule were all read as page images for the same reason.

### Priority 4: the integration that has never been built

The portal generates its own report, and the packs are generated separately by the
`/cartrack-proposal` skill in the launcher repository. **These are two renderers for one
deliverable**, and the packs are the ones that go to clients.

The right shape is: **portal produces the verified data, the skill renders the pack.** The portal's
job should end at "reconciled, with findings"; the pack builder should consume that. Until then,
any change to the house table components has to be made twice, and the portal's report will drift
from the packs.

The reverse handoff already half-exists: `sendToBook()` encodes a deal for the RM System. The loop
described in the project instructions is *pipeline opens a deal → schedules go to the portal →
portal produces the pack and a "reconciled" verification → outcome flows back to the pipeline*.
Only the last link is built.

---

## 5. What should not be automated

Worth writing down, because the temptation runs the other way.

- **Whether a reduction in cover matters.** That is a judgement about this client's operations, and
  it is the thing the packs are actually bought for.
- **Whether an insurer will honour a limit its own wording contradicts.** That needs a written
  answer from the underwriter. The honest output is the question.
- **Valuation.** Nine tanker trailers at R56,047 are obviously wrong; the right number needs a
  valuer.
- **Anything that depends on a fact only the client knows.** Do they cross borders. Do they run
  night shifts. Whose are the bicycles. Several findings this year turned on one answer from an RM.

**The design rule for every item above: produce a checked number or an honest blank.** The fleet
catalogue's reconcile-or-total guard already works this way, and it is the reason that part of the
tool is trusted. A tool that guesses plausibly is worse than no tool, because the pack is read with
the insurer's own quote open beside it, and a number that appears on neither document loses the
deal.
