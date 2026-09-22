# The Quote Comparison Method

**Cartrack Insurance, Commercial Division. Handoff document 3 of 4.**
17 September 2026, revised 21 September 2026.

This is the method behind every comparison this division has produced. It was built by doing
roughly twenty five of them across transport, schools, security, funeral, medical, waste, retail
food and private client accounts, and by getting some of them wrong first.

Read this before the code. The portal at `cartrack-premium-comparison` automates part of it. The
part it automates is the arithmetic. The part that wins deals is in section 3.

---

## 1. What a comparison is actually for

An RM asks for a comparison because an insurer has quoted a lower number and the client wants to
know whether to move. The naive answer is to subtract. That answer is wrong often enough to be
dangerous, and the reason is always one of four things:

1. **The quote is not quoting the same policy.** Something is smaller, missing, or quietly dropped.
2. **The quote is cheaper because it has deleted a section**, not because it has re-rated the risk.
3. **The price is not firm**, because the insurer has not yet been given the claims record.
4. **The saving is smaller than something the client loses by moving**, usually a cash-back bonus
   or a retroactive date.

So the deliverable is not a price. It is an answer to "should this client move", with the money
reconciled to the cent and the cover compared line by line.

**The governing rule, and it is counter-intuitive:**

> **Dearer but better is still a move. Only a genuine cover GAP justifies holding.**

Credit a proposal for cover the current policy lacks. Do not treat added cover as merely "more
expensive". Half the recommendations in this book are to move to something that costs more.

---

## 2. The seven steps

### Step 1. Extract every schedule, completely

- Digital PDFs: `pdftotext -layout`, or `pymupdf` with `page.get_text()`.
- **Scans with no text layer: render the pages as images and read them.** Never guess a figure off
  a faded scan, and never work from a summary page when the item pages exist.
- **Test the scan before trusting it.** Count distinct grey values per page:
  `page.get_pixmap(colorspace=pymupdf.csGRAY)` then count unique bytes. **Two grey values means a
  pure black and white scan and the figures are gone.** Two hundred or more means it is readable.
  This test caught the Arboretum schedule: the first file was unusable, the second was fine, and
  they looked identical in a thumbnail.
- Some documents arrive as 90 to 120 page scans. Gateway was 95 pages, Vuyos 91, Integral 98,
  Bakers 108, Tshenolo 119. Budget for that.

### Step 2. Reconcile to the cent, on the all-in monthly

Compare on **all-in monthly including VAT, fees, Sasria and value-added products**. Nothing else.

⚠️ **South African schedules routinely print a "Total Premium" that is before fees, Sasria and
VAT.** Find the true all-in. Wes-Kaap Busdiens showed a Santam headline of R34,091 against a real
all-in of R43,946.83.

**Reconcile means the sections sum to the total, exactly.** If they do not, something is
misunderstood or the document is wrong. Both are worth knowing. This test has found:

- Bryte dividing the Sasria annual by **ten instead of twelve** on at least two unrelated quotes
  (Lomaen, Vuyos), which is systemic in their spreadsheet, not a typo.
- Vuyos' Bryte annual column carrying **one premises of glass instead of five**, under-counting
  R44,079.60 and changing the ranking of the quotes.
- Alpha's Sasria sections missing R6,236.60 against its own summary on one version, fixed on the
  next without comment.

### Step 2b. If you adjust a headline, print the as-quoted figure beside it

⚠️ **This is a hard rule and it was learned by losing credibility.**

The RM and the client read our pack with the insurer's own quote open next to it. A number that
appears on neither document reads as an error, and the pack loses.

Caught on Cordiguard: the pack led with ONE at about R40,208, which was the honest like-for-like on
25 vehicles, while ONE's own quote said R42,932.86 for 27. Elizabeth spotted the mismatch
immediately. **Name the gap and what causes it, every time, on the cover and in the table.**

### Step 3. Line for line, with a verdict and a plain-English reason

Every section, every limit, current against each proposal. Per line: is it better, worse, or the
same, and why it matters to this client.

### Step 4. Find the decisive cover for this client type

See section 4. This is the step that turns a spreadsheet into advice.

### Step 5. Read per item, not per summary

⚠️ **The summary page lies by omission.** Every significant finding in this book was found on an
item page or in the memoranda, not in the section totals.

- Wes-Kaap: King Price's passenger liability turned out to be **R2.0m per event on an e-hailing
  form**, on schedule page 10, for a scheduled bus operator.
- Bakers: Alpha's clean-up cover sat **only in the heavy commercial liability table**. The trailers,
  light commercials and private vehicles each carried third party liability and no clean-up at all.
  On a tanker fleet the product is in the trailer.
- Cordiguard: Bryte's item pages said third party R5,000,000 while its own wording on page 35 said
  R2,500,000 aggregate with a R1,000,000 fire and explosion sub-limit.

### Step 6. Split the deliverables

- **Client proposal**: sober, black mastheads, money on the cover, findings from page two.
- **RM playbook**: internal, coloured mastheads, RM-eyes-only stamp, teardown tables, the questions
  to put to each underwriter, and what to say in the room.

Tone in both: peer briefing, not schooling.

### Step 7. Compliance

Replacing a policy means **any reduction in cover, and any forfeiture of a bonus or fund, must be
disclosed to the client in writing before they decide.** That is the Record of Advice. Where the
recommendation is to move and something gets worse, the disclosure goes in the client pack, in the
client's own numbers, not in a footnote.

---

## 3. The findings taxonomy

This is the working IP. Every item here has been found on a live document at least once, most of
them more than once. Run a new set of quotes against this list.

### A. The client is not covered for what they actually do

The highest-value finding class. It is usually on the **current** policy, not the quote, which
makes it a reason to act rather than a criticism of a competitor.

| Pattern | Seen on | What to look for |
|---|---|---|
| **Work away exclusion on liability** | Lomaen Medical, Vuyos Funerals, Cordiguard | *"no indemnity for work done away from the insured premises"*. Fatal for anyone who installs, services, guards or buries. Lomaen installs x-ray machines at hospitals. Every funeral is at a church or a graveside. A guarding company's only liability is at other people's premises. |
| **The motor policy excludes the cargo** | Bakers Tankers | OUTsurance fleet conditions: *"no cover when the vehicle transports hazardous materials"*, on a fleet declaring diesel, petrol, paraffin and jet fuel. |
| **No liability section at all** | Tshenolo Waste | Two quotes, R461,855/mo, no public liability, no products, no employers' liability, on a business putting sharps containers into hospitals. |
| **The core operating exposure is excluded** | Gear Lab | *"Vehicle hoists and ramps: No"* on all items, plus an exception excluding loss through use of a hoist, at a gearbox workshop. The other quote covered hoists but excluded *"damage to vehicles being worked upon"*. |
| **Products and defective workmanship missing** | Powerflow, Hamisa, Lomaen, Bakers, CS Continental, Gateway | Almost never taken, almost always relevant. On Bakers the insurer itself prints *"Based on your industry type, we recommend the Defective Products optional cover, which is not currently selected."* |
| **Activity-specific exclusions** | Arboretum (Hollard) | Endorsement excluding **child molestation or sexual abuse, wrongful or excessive discipline, and bullying or harassment**, plus a memo excluding pupil-to-pupil liability, quoted to a school. |

### B. Regression dressed as an upgrade

The quote presents a bigger number that is worse cover.

| Pattern | Seen on | What to look for |
|---|---|---|
| **Passenger liability narrowed while the limit rises** | Gateway School, Wes-Kaap Busdiens | King Price printed *"Passenger liability: Private and LDV only, R3,000,000"* on 25 midibuses, against a current policy carrying R2,500,000 passenger, R2,500,000 unauthorised passenger and R2,500,000 contingent on every bus. R3m that does not respond is worse than R2.5m that does. **Twice on the same insurer.** |
| **"Passenger liability" that does not say fare-paying** | Wes-Kaap, six rounds | A bus operator needs fare-paying passenger liability named on the schedule with a seat basis. A generic limit is not it. |
| **Third party as an aggregate, not layers** | Tshenolo Waste | *"(a) passenger liability R2,500,000 (b) fire and explosion R5,000,000 (c) any other event and the aggregate of (a), (b) and (c) R5,000,000"*. Reads like R7.5m, is R5m. |
| **An umbrella that cannot attach** | Powerflow (Western), Arboretum (Hollard) | The excess layer carries a **minimum underlying limit condition** higher than the underlying actually bought. Western needed R2.5m EL and R2.5m products underneath against R1m and nil. Hollard's R17.5m umbrella needed R2.5m underlying against R1m. The layer is decorative. |
| **Retroactive date reset to inception** | Powerflow, Hamisa, CS Continental, Lomaen, Vuyos | Claims-made liability. Resetting the retro date uninsures every year of past work. Powerflow's was worse: the CAR policy added *"RUN-ON COVER: Not included"*. Lomaen's quote contradicted itself in three lines, header saying inception and body saying 01/06/2017 retained. |
| **Fire and explosion sub-limits inside the third party limit** | Twin Trans, CS Continental, Cordiguard, Idol | R5m third party that becomes R1m or R2.5m if the loss involves fire or explosion. On a fuel carrier that is the loss. |

### C. The quote is not quoting the same policy

| Pattern | Seen on | What to look for |
|---|---|---|
| **A dropped zero** | Gateway (Bryte rent R21,677,345 to R2,167,734), Vuyos (Santam Robertville R15,000,000 to R1,500,000) | Compare every sum insured against the current schedule item by item. **The cheapest quote was cheapest partly because it was not quoting the same policy, in both cases.** |
| **Vehicles or items unquoted** | Hamisa Kgahlisa (3 of 7 vehicles, R1,384,003), Integral MiWay (7 items, R4,838,555) | Match on registration, not on sum insured. Matching on value produced a wrong answer on Integral and had to be corrected. |
| **Under-insured but looks covered** | Integral (LW22DGGP R2,400,000 to R1,515,000) | Worse than an omission, because average will settle it at about 63c in the rand and nobody notices until the claim. |
| **Fewer entities named** | Bakers (CLP names 1 of 3), Integral (7 named insureds), Arboretum (ONE names 1 of 3) | Read the insured name on the quote against the insured name on the current schedule. Moving as quoted can leave whole companies uninsured. |
| **The quote copies the incumbent's errors** | Bakers tanker trailers | Nine tanker trailers at R56,047 each against an R800,000 to R1,600,000 replacement cost, and **the new quote had copied the same values across**. The under-insurance travels onto the new policy. |
| **The saving IS a deleted section** | Integral (MiWay) | MiWay was R2,612.69 dearer on motor for seven fewer vehicles, and paid for it by deleting the entire R10m public liability section. Net "saving" R2,624.04, for a smaller policy. |
| **Priced on the wrong basis entirely** | Wes-Kaap (ONE) | ONE priced the buses a second time inside its fire section as *"Miscellaneous R8,942,700"*, which was the incumbent's column 5 subtotal including a R0.00 Sasria memo line. Corrected, the quote was R2,953/mo better, not R1,289. |

### D. Arithmetic and document errors

Individually small, collectively the reason a pack is trusted.

- **Sasria divided by ten, not twelve** (Bryte, systemic, on unrelated quotes).
- **Sasria under-declared against the fleet.** Tshenolo declares R59,436,465 against a fleet of
  R61,174,651; the difference is exactly the two buses. Lomaen declares R0 against "commercial
  3,500kg and over" while scheduling two Hinos.
- **Sasria in the wrong category.** Fifteen private cars declared as "Goods Vehicles M2" (Tshenolo).
  A school's buildings declared as "Residential" (Gateway).
- **Sasria as a cross-check.** It is a statutory rate on declared values, so two documents landing
  within a few hundred rand of each other on Sasria are covering the same risk. That is how the
  Bakers 184-vehicle question was settled: R31,732.51 against R31,511.54.
- **Invalid VAT and company registration numbers.** Gear Lab printed a 7-digit VAT number; a South
  African one is 10 digits and starts with 4. Gateway's Bryte quote did the same. CS Continental's
  King Price quote carried **OUTsurance's own** registration and VAT in the policyholder fields,
  copied off the incumbent's schedule.
- **Insurer identity contradicted in the footer.** Bryte-titled quotes whose every page footer reads
  *"Quotation, Hollard Insurance Company"* (Hamisa, Lomaen). Confirm who carries the risk in
  writing.
- **Transposed registrations** (Gateway: `YXG685GP` typed `XYG685GP`). Worse than a blank, because
  it looks complete.
- **The broker fee charged twice**, once on motor and once on non-motor (Vuyos, Auto & General).
- **Placeholder dates left in.** `01/01/3000` on Gear Lab and Arboretum. `"commencing on TBA and
  ending on TBA"` on the Bakers CLP quote.
- **Two versions of the same quote in circulation.** Natsure issued Idol two, R49,000/mo apart.
  Two Hollard PDFs on Arboretum share one quote number, and **the premium did not move when the
  limit was corrected**.

### E. Conditions precedent that are not met, so the cover does not exist

This class is both a finding and the Cartrack lead. See section 5.

- **Tracking recorded as required and not installed.** The schedule says a device is required, the
  fitment field says no, and the wording says no device means no theft or hijack cover. Found on
  Gateway (24 of 25 vehicles, **written as a warranty on the policy they hold today**), Bakers
  (3 vehicles), Tshenolo (15 cars, R16.8m), Idol (23 items), Cordiguard (all 25), CS Continental
  (all 9 fields blank).
- **Survey conditions.** Lomaen's current fire section records *"survey done, stacking heights
  exceed 3m, sprinkler system waived"*, and the new quote is "subject to satisfactory survey". If
  the new surveyor will not waive it, the client is being asked to sprinkler a warehouse holding
  R73.3m of stock.
- **Inspection of older vehicles.** Bakers: 61 of 215 items are over 20 years old and the quote
  requires a full evaluation on each before comprehensive cover attaches. Tshenolo: every vehicle
  ten years and older.
- **Conditions the client cannot satisfy.** Gear Lab has never been insured, and both quotes require
  a satisfactory claims history and a previous policy schedule. Neither exists.
- **Warranties that void cover.** SAIDSA alarm linked to armed response with the arming log
  available, electrical compliance certificate, fire equipment serviced annually, SABS Class I
  lightning arrestor and Class II surge arrestor, stock raised 150mm on pallets, hazardous storage
  per OHS Act Regulation 4 and SANS 02363, waste bagged daily and removed weekly.
- 🚨 **A declared breach of the policy's own condition.** CS Continental's schedule declares
  *"Db protection (Imax LESS THAN 40kA)"* while the fire special conditions require a SANS-approved
  Imax of at least 40kA, failing which the insured carries **the first 20% of any lightning or
  power surge claim**, on R10,000,000 of plant in a refrigeration business that had already been
  paid a lightning claim. The fix costs an electrician's morning.

### F. Money that is not a saving

| Pattern | Seen on | The real arithmetic |
|---|---|---|
| **The fund is the client's own money** | Waste Carriers, Idol (OWNsurance) | The quote's "annual savings R1,768,416.95" is the contribution into the client's **own** savings fund, not a saving against the incumbent. It reconciles only with **sequential** commission deduction: premium × (1 − binder) × (1 − broker) × fund share × 12. Additive is wrong. Present it as effective annual cost under claims scenarios: zero claims, a mid case, and fund fully used. |
| **Bonus forfeiture** | CS Continental, Bakers | An OUTsurance Business OUTbonus pays up to 10% of premiums back at a claims ratio of 30% or less. CS Continental's commercial policy had R42,637.61 projected against a R61.77/mo saving: **the bonus was worth 57 years of the saving.** Bakers had two policies projecting R255,621.49 and R307,010.54, **R562,632.03 in total.** Raise it yourself before the client finds it. |
| **Add-ons billed separately** | Bakers (Alpha) | Alpha's per-vehicle rates were R12,393.38/mo **better** than the incumbent's. It was dearer overall because it billed R33,074.16/mo of additions on top, including **R17,529.16/mo of towing to buy a R30,000 limit**, which is R210,350 a year. The incumbent carried roadside, territories, pollution and passenger liability inside the rate. |
| **The saving is the broker fee** | Wes-Kaap | ONE's fleet premium was R514 better. The R1,289.62 saving was almost entirely the incumbent broker's R2,897.76/mo fee. |
| **New cover priced as if it were a saving** | Powerflow, Bakers | Powerflow: the re-market saved R410.79/mo, the PI and defective workmanship add-on cost R4,483.08/mo. **The switch pays for about a tenth of the new cover.** Say so. |
| **Cover the client already has, quoted as new** | Arboretum | ONE's R5m passenger liability was a **match** of the incumbent, not an upgrade, and an earlier version of the pack told the RM to lead with it as better. Corrected. |

### G. The price is not firm yet

Always check whether the quote says it was rated on the claims record, or merely asks for it.

- *"Loss History: Tba"* printed on the Petrosure quote after two hijackings totalling R6,500,000.
- *"Subject to a written 3 years minimum claims experience before going on risk"* (Western).
- *"Confirmation of 3 years claims experience in writing from current and/or previous insurer is
  required"* (Alpha, Natsure).
- **Rated on nothing:** Lomaen's liability section printed **"TURNOVER R0"** and **"WAGES R0"**, so
  the R5,576.00 is a placeholder that will be re-rated.
- **Turnover that contradicts the contracts.** Powerflow declared R15,000,000 turnover and a
  R6,000,000 maximum contract limit, while noting a R22,000,000 decommissioning contract. PI is
  rated on turnover.
- 🎯 **Use a rated quote to prove an unrated one will move.** MiWay was the only Integral quote that
  printed the R6,500,000 loss on its face, and it landed R5,795.73/mo **above** the unrated
  Petrosure quote. That is the evidence that Petrosure's number will rise.

### H. Loss records the client has not been told about

Read the incumbent's own claims disclosure. It is usually on the schedule.

- CS Continental: 19 fleet incidents, about R1.46m over ten years, **R968,238 in the last 24 months
  against about R645k of premium, roughly 150%**.
- Idol: 58 losses, R2,651,053 over three years, 96% over 24 months.
- Integral: R6,500,000, two trailers hijacked with their loads.
- Bakers: 43 incidents over ten years, but **both policies project a bonus, which requires a ratio
  at or under 30%**, so the recent record is good. Check the direction before assuming.

A high ratio is a gate. It also tells you which cover actually matters: on Integral the losses were
**hijackings**, which was precisely the excess the cheaper insurer would not reduce. One hijack ate
33 months of the saving.

### I. Excess structures that decide which quote actually wins

The excess is where a cheaper quote most often stops being cheaper, and it is the class most often
skipped, because it sits in a table three pages behind the premium.

| Pattern | Seen on | What to look for |
|---|---|---|
| **A percentage of VEHICLE VALUE, not of the claim** | Tshenolo Waste (Natsure), Idol (VAPS tippers) | Natsure's basic motor excess is **4.5% of the vehicle's value, minimum R5,000**. On the average truck that is about **R53,000 on every claim, however small**. Alpha's is 10% **of the claim**, minimum R5,000. Neither is simply better: **the crossover is around R450,000 of claim.** Below it the percentage-of-claim insurer is far better, above it the percentage-of-value insurer is. Work out the crossover and say where the client's actual claims fall. |
| **Loadings that stack** | Tshenolo (Natsure), Cordiguard (ONE) | **+5% for a single-vehicle accident and +5% for driving between 23:00 and 04:00, cumulative**, on a waste fleet that may well run before dawn, and on a patrol fleet that by definition works at night. The loading turns the headline excess into something else entirely. **This is a question for the RM, not an assumption.** |
| **A bad base excess bought down to a flat inner excess** | CS Continental (King Price) | On paper KP is worse: 10% of claim, minimum R30,000 on trucks, against OUTsurance's R7,610 basic. But the three reducers actually bought (own damage, theft and hijack, third party) cap it at a **flat R5,000, with third-party damage nil on eight of nine items**. On the Hino that is R8,500 better per claim. **Read the reducers before you rank the excess.** |
| **The excess the client's actual losses will hit** | Integral Trading | The losses were two **hijackings**, R6,500,000. The cheaper insurer would not reduce the hijack excess: R1m load hijacked is **R20,000 at the incumbent against R300,000**. That is +R280,000 a hijack against R101,037/yr of saving, so **one hijack eats 33 months of the saving.** Match the excess table to the claims record, not to the average case. |
| **An excess that is a penalty for something not done** | Gateway School, Integral (MiWay) | King Price adds **+25% of the claim** where the required tracking device is not fitted. MiWay adds **+15%** on a single-vehicle articulated accident with no driver or road-facing camera footage. These are conditional excesses that read as cover but behave as exclusions in the cases that matter. |
| **Excess waived for a device, and the comparison is not close** | Gateway (Auto & General), CS Continental | A&G **waives its theft excess entirely** where an approved device is fitted, about R33,750 on a R450,000 minibus. Where an insurer prices the device into the excess, the device is part of the quote, not an upsell. |

**The working rule:** never compare excesses on the basic figure alone. Compare on
(basic or percentage) + (reducers bought) + (loadings that apply to this client's operations) +
(conditional penalties they will trip), and state the crossover in rands.

---

## 4. Decisive cover by client type

Find it, lead with it, and let it decide the recommendation.

| Client type | The decisive cover | Why, and where it went wrong |
|---|---|---|
| **Tanker, fuel, dangerous goods** | Pollution and environmental impairment liability | Twin Trans: the cheaper quote dropped pollution and halved third party on a fuel tanker. Bakers: clean-up on the trucks only, nothing on 124 trailers, **on a fleet where the product is in the trailer**. |
| **Bus, scholar transport, passenger** | **Fare-paying** passenger liability, named on the schedule with a seat basis | Wes-Kaap: six rounds and still not printed. Gateway: restricted to "private and LDV only" on 21 midibuses. Vuyos: R2.5m on all four documents for 16 buses carrying mourners, a standing gap nobody had raised. |
| **General transport fleet** | Third party limit, excess structure, telematics excess waiver | Integral: the ceiling was R5m against a current R10m, and it could not be lifted. That benched the quote. |
| **Goods in transit** | Load limit, driver fidelity, theft and hijack excess, territories, high-risk-cargo carve-outs | Bakers: CLP adds a further 25% minimum R25,000 on "high risk cargo" over R1m, and its definition includes the scrap metal and batteries the client actually carries. |
| **School** | Abuse, pupil-to-pupil, teacher liability, professional indemnity for scholars | Arboretum: Hollard excluded exactly these. Gateway: the current policy prints "Schools extension: No", so King Price's schools cover was genuinely new. |
| **Security and guarding** | Public liability with **work away**, and passenger liability for guards in the vehicles | Cordiguard: PL R1,000,000 on all three quotes and the incumbent's memoranda said "excludes workaway", while its own excess table priced work away on the same page. |
| **Medical and hazardous waste** | Public liability, products, and clean-up that is not just a motor extension | Tshenolo: no liability section at all, and clean-up of R250,000 a truck on a hazardous waste fleet. **Clean-up costs are not environmental impairment liability under NEMA.** |
| **Funeral** | Work away, passenger liability, deterioration of stock | Vuyos: they refrigerate bodies, and the schedule's own grid interruption exclusion names *"deterioration of stock, food or other items"*, which is not covered anywhere. |
| **Installer or service provider at client sites** | Work away, products and defective workmanship, stock at the consignee | Lomaen: a work away exclusion on a business that installs x-ray machines in hospitals. |
| **Contractor, electrical, solar** | Defective workmanship and professional indemnity, and the interlock between them | Powerflow: defective workmanship excludes *"arising from defective design"*, PI covers design. Take one without the other and a failed installation is an arguable gap. |
| **Workshop** | Damage to vehicles being worked on, hoists and ramps, customers' vehicles in custody | Gear Lab: R50,000 on customers' vehicles where a single SUV in for a rebuild is R500k to R1.5m. |
| **Retail food and cold chain** | Deterioration of stock, machinery breakdown, surge protection, products | CS Continental: deterioration not taken anywhere, and a declared surge-protection breach. |
| **Fuel retail forecourt** | Motor traders internal, forecourt negligence and contamination | Hamisa Kgahlisa: motor traders internal cut from R3,750,000 to R250,000 on a forecourt holding customers' cars. |
| **Private client** | Agreed value on collectors, buildings not averaged, excess structure, itemised valuables | Mike Lawlor: Santam cut buildings from R38.88m to R26.38m so average would apply, and coded a 1968 Dodge Charger as a "1996 Base Coupe". |

---

## 5. The Cartrack lead, and why it is not an upsell

On nearly every account, tracking is a **condition precedent to theft and hijack cover**, not an
optional extra. The wording is usually some version of:

> "If the device is not installed or not in a working condition or the tracking subscription has
> not been paid, you will have no theft or hijack cover."

So when a schedule records a device as **required** and **not fitted**, the client has a live hole
today. That is a service finding first and a sales lead second, and it should be presented that way.

**Volumes found:** Waste Carriers 116 untracked of 228 (R87.57m of sums insured) · Gateway 24 of 25
(a warranty breach on the current policy, vehicles carrying special-needs children) · Bakers up to
179 units · Tshenolo 70 units across R79m · Idol 43 · Vuyos 54 · Cordiguard 25 · CS Continental 12.

**Three things worth knowing:**

1. **Check whether Cartrack is on the insurer's approved list.** OUTsurance names Cartrack in its
   wording. MiWay named Tracker, Netstar, SAIAS and VESA and **did not name Cartrack**, although
   Cartrack was already on 16 of that client's 18 tracked units.
2. 🚨 **Check the excess table for a competitor's brand.** Natsure's Tshenolo quote gives a **nil
   excess** on theft of a truck and trailer combination **only where a Ctrack device is operational**,
   and 10% of vehicle value for any other approved device. Cartrack is the broker on that quote. On
   the dearest truck that is R201,267 a claim. Get it changed.
3. **Some insurers will fund a device themselves.** Natsure's wording lets the insurer pay for the
   unit and the fees, own the unit, suspend the service on premium default, and receive all the
   tracking data. That is a competing offer written inside the policy.

Where we are already the incumbent, say so and protect it: Vuyos had 7 of 61 vehicles under a
tracking warranty and **all seven were Cartrack**, named on the schedule.

**Loss records also sell telematics.** Five accidental damage claims in 24 months on 9 vehicles is a
driver problem, not bad luck. MiWay adds **15% to the excess on any single-vehicle articulated
accident without driver or road-facing camera footage**, which prices the camera argument for you.

---

## 6. Structural facts to keep straight

- **Broker** advises and places. Cartrack Insurance Agency, **FSP 17266**.
- **UMA (underwriting manager)** sets terms and runs claims. Merx FSP 42991, VAPS FSP 46264,
  Natsure FSP 50704, Alpha FSP 21820, Envirosure FSP 38594, AC&E FSP 45553.
- **Insurer** carries the risk. Old Mutual Insure behind Merx, King Price behind VAPS, Guardrisk
  behind Alpha, Renasa behind OWNsurance, Compass behind Natsure, Centriq behind Envirosure,
  New National behind AC&E and CLP.

So **"King Price / VAPS" is one proposal, not two.** Getting this wrong makes a three-way look like
a five-way.

---

## 7. What the analysis cannot do, and must not pretend to

- It cannot read a schedule whose premiums are zeroed out. Arboretum's current price is still
  unknown for that reason.
- It cannot settle whether an insurer will honour a limit that its wording contradicts. That needs a
  written answer from the underwriter, and the pack should say so rather than guess.
- It cannot value an asset. Nine tanker trailers at R56,047 are obviously wrong, but the right
  number needs a valuer.
- It cannot replace the client's own knowledge of what they do. Several findings turned on a single
  answer from the RM: does the fleet cross borders, do they run night shifts, whose are the
  bicycles.

**Where a question decides the recommendation, the honest output is the question, not a guess.**

---

## 8. Standing conventions

- 🚫 **No em dashes anywhere.** Commas, colons, brackets, or a new sentence. This applies to packs,
  messages, notes and e-mails.
- 📲 **Every comparison ships with an Afrikaans WhatsApp for the RM**: informal, English words mixed
  in, the headline number, the one finding that decides it, and what the RM must do next.
- Figures are never monospace in the packs.
- People's pronouns: they/them unless stated.
