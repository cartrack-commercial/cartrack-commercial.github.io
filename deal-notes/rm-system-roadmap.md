# RM System roadmap (ideas list, 2 Sept 2026)

Anne asked "what other cool features can we build?" Ordered by pain removed. Hours are rough, on the
current single-file app. Nothing here is committed to; Bernard's list and RM suggestions still to come.

## Stop the "my clients are gone" messages
- **Nightly data-health alert (4h).** Compare each RM's book to yesterday's snapshot; banner in Command
  View if anything dropped.
- **Undo per RM (6h).** "Restore yesterday's version" button per RM book, from existing snapshots.
- **Change history on a client (5h).** Who changed what, when. Answers the Klada R460,634 question.

## Payroll and commission (Lourie)
- **Comm stat import (10h).** Paste the UMA statement, app matches names and fills the commission column.
- **Missing-from-comm-stat list (3h).** Book clients with no commission this month = lapse / non-payment / name mismatch.
- **RM payslip view (4h).** Each RM sees their own month's breakdown, read-only.

## Pipeline and selling
- **Renewal calendar (6h).** Anniversary date per Active Client; next 60 days per RM.
- **Quote comparison tracker (4h).** Which insurer quotes are in / outstanding / how long waiting.
- **Tracking leads to Cartrack sales (5h).** Log unit leads from comparisons (Cordiguard 25, Wes-Kaap 10,
  CS Meat 12), hand to fitment, status back.
- **Leaderboard that counts what matters (2h).** Premium written, renewals kept, unit leads.

## Management
- **Weekly one-pager for Brendan (5h).** New / lost / renewals due / payroll total / book size per RM.
- **Loss-ratio flag per client (4h).** Capture claims; red mark above 60% of premium.

## Comparison portal (52h scoped earlier)
- Phase 1 reconciliation engine (all-in to the cent, headline traps, per-vehicle matching).
- **Insurer quirk library:** Bryte Sasria ÷10, ONE copying subtotals as sums insured, King Price
  e-hailing wording, Santam "Total Premium" before fees.

## Do first
- **Supabase Auth with real logins (20h, parked).** Everything else sits on data anyone with the anon key can read or delete.
- **Version nag (1h).** Old build shows a banner on every screen until refreshed.

**Suggested next 25k block (~30h):** data-health alert, undo per RM, comm stat import, renewal calendar, version nag.
