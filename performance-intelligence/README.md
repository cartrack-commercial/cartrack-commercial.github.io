# Commercial Performance Intelligence — dummy edition

The Cartrack Insurance **call-centre floor** got an analytics pack from the actuary
("CIA Performance Intelligence v1.1": Executive → nine questions → journey → month →
month-on-month → inefficiencies at three levels → analytics → forward view → island/agent
drill-down → roadmap). This folder is **the same coding applied to the Commercial division**
(the RM pipeline), populated with **simulated data on a fictional roster** so the approach can
be shown before any real numbers are put behind it.

Live at `https://cartrack-commercial.github.io/performance-intelligence/` once merged to `main`.

## What is real and what is not

| Real | Simulated |
|---|---|
| The design system, page structure, chart primitives, filters, mask toggle, three-level drill-down — the floor pack's coding, one to one | Every number, every RM, every desk assignment |
| The RM System's vocabulary: 7 pipeline stages, 4 lead sources, 8 lost reasons, 7-day stale rule, 12.5% brokerage | Insurer turnaround times, segments (the live deal record has no segment field), the desks |
| Insurer / UMA names, the working-day calendar (Jul 23 · Aug 21) | The "findings" — they are what the pack *would* say if the data looked like this |

**Nothing here touches Supabase or any live RM data.** The generator only borrows field names
from the RM System's source so the app can be pointed at the real tables later without a rewrite.
The RM names are fictional on purpose: this repo is served publicly, and fake performance flags
next to real names would read as a real performance record.

## Files

- `index.html` — the app. Single file, no build step, no dependencies beyond the Montserrat
  webfont. Data is embedded between `/*@@BB@@*/ … /*@@/BB@@*/`.
- `build_data.py` — simulates a row-level pipeline (leads, first-contact attempts, stage dates,
  quotes, proposals, decisions, the two blind desks, the book), aggregates it into the `BB` blob
  and injects it into `index.html`. Seeded (`SEED = 20260907`) so it is reproducible.

```
python3 build_data.py          # regenerate and rewrite index.html
python3 build_data.py --json   # print the blob instead
```

Deep links: `index.html#p=<code>` opens a page (`a q j m c i v x n f g p r`).
Self-check: `index.html#smoke` renders every page / month / filter / RM and reports
`SMOKE OK` in the bottom-left corner.

## How the floor pack's concepts map to Commercial

| Floor pack | Commercial edition |
|---|---|
| Agent | RM |
| Island (team / channel) | Desk (Fleet & Transport, SME Commercial, Private Client, Dealerships, Renewal Book, Coastal, Key Accounts, untagged) |
| Calls | Touches (first-contact attempts + stage chasing), with book-servicing activity counted separately |
| Reach | Contact (first conversation) |
| Quote | Schedules received → Proposal presented (two stages, because the RM controls the second) |
| Policy | Deal bound (stage 7), **linked to its lead** — the funnel closes, which the floor's cannot |
| Islands 4 & 5 with no call records | Desk 4 Dealerships & Desk 5 Renewal Book with no pipeline records |
| One-and-done dialling | One-touch leads |
| Headline: second-attempt rule | Headline: fourteen-day proposal rule (schedules in → proposal out) |
| Quote-equivalent | Proposal-equivalent, plus **rand-equivalent** (possible because win rate and deal size are measured) |
| Assumed quote-to-sale slider | Measured win-rate slider, adjustable |

## Definitions the app uses (so the real-data version stays honest)

Pipeline stage rates are **cohort rates with a maturity window**, never period ratios
(period ratios can exceed 100% when proposals lag schedules across a month boundary):

- contact rate = leads reached ÷ leads touched, within the month
- schedule rate = schedules received within 21 days of first contact ÷ contacted (matured)
- proposal rate = proposal within 14 days of schedules received ÷ schedules (matured)
- win rate = bound within 21 days of the proposal ÷ proposals (matured)
- stale = open deal with no activity in 7 days (the RM System's own `STALE_DAYS`)
- "matured" = the deal's window has fully elapsed by the data cut (7 Sep 2026)

Counts (touches, leads, schedules, proposals, bound, premium) are period counts by event date.
The July cohort funnel on the nine-questions page follows the leads opened in July to the cut.

## Pointing it at the real pipeline (the next step)

Replace `simulate()` in `build_data.py` with a reader over the RM System's Supabase tables:

- `deals` → one row per deal with `rm`, `stage`, `stageEntryDate`, `createdAt`, `lastActivity`,
  `leadSource`, `premium`, `won`/`lost` + `reason`; stage-date history gives `contacted`, `meet`,
  `sched`, `mkt`, `prop`, `dec`.
- the per-RM activity log → `touches` (date, hour, deal, kind).
- `portfolio` → the book, renewals (`status`, `renewal`), insurer, broker fee.

Everything downstream of `simulate()` — aggregation, benchmarks, ledger, tests — and the whole
of `index.html` stays as it is. Fields the live record does not have yet (segment, sale class,
a chosen lead source, per-insurer quote dates) are listed on the app's *nine questions* and
*roadmap* pages as the fixes that would unlock them.

## Live edition

The live version of this pack is `cartrack-rm-system/intelligence.html`. It keeps these pages and definitions and
replaces the embedded blob with a client-side aggregation of a payload the RM System writes to `sessionStorage`
after the Command View sign-in (see the CLAUDE.md in the launcher repo for the payload contract). This dummy edition
stays as the version safe to send outside the division.
