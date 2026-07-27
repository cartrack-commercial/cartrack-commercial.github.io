# Wes-Kaap Busdiens — comparison project history & build handover

*Written 24 Jul 2026, on closing the working chat. Everything needed to continue this deal
without that chat lives in this folder, the deal memory, and the `/cartrack-proposal` skill.*

Deal: **Wes-Kaap Busdiens CC** (Vredenburg; trading as WES-KAAP TOERE, weskaaptoere.co.za —
daily commuter, WCED scholar transport, charter). RM: **Bronwyn**. Broker: Cartrack Insurance
Agency (Pty) Ltd, FSP 17266. ±R13.1m fleet, 34 buses.

---

## The three rounds

### Round 1 — original comparison (docs of 23 Jun – 8 Jul)
- Santam current (STM-STP0041, 23 Jun): **R43,946.83/mo** all-in. R2.5m fare-paying +
  R2.5m unauthorised + R2.5m third-party passenger liability, verified item-by-item across the fleet.
- Old Mutual / ONE-OMART (TOURS/1267000.1, 8 Jul): R42,343.16 — but pax liability only
  R1m **non**-fare-paying; no unauthorised cover.
- King Price / VAPS (VAPS52095 r21373, 7 Jul): R44,768.32 — **no** passenger liability at all;
  added windscreen R5,520 + roadside R7,760.
- **Finding:** both proposals cut the decisive cover. Recommendation: don't move; send both
  back to quote fare-paying pax liability at R2.5m.

### Round 2 — both re-quoted (21 Jul, folder `new o7-21/`)
- OM rev .3: **R45,454.19** — added a dedicated Fare-Paying Passenger Liability section,
  **R2.5m per vehicle** on clean wording (matched Santam).
- KP rev 21387: **R49,599.98** — added passenger liability R4,831.66, **but on an RTU
  e-hailing form** (covers an "e-hailing fare-paying passenger", excludes vehicles "in use for
  a non-e-hailing platform"), limits R75k/seat / **R2.0m/event** / R10m p.a.
- **Finding:** OM = genuine like-for-like at +R1,507/mo; KP = most expensive AND its pax cover
  likely doesn't respond for a scheduled bus operator. The "VAPS letter" became the gate.
- Client (via Bronwyn) then asked to strip SASRIA + roadside from KP; analysis showed roadside
  alone (a fair cut — Santam has none) made KP cheapest, and advised keeping SASRIA.

### Round 3 — the benchmark moved (folder `New 24 July/`, docs of 23–25 Jul)
- New Santam schedule (print 25 Jun) revealed the client's **real** current premium:
  **R37,535.20** — bus SASRIA had been stripped off the current policy in June
  (R6,956.59 → R544.96, pro-rata credit on the schedule). Old R43,947 benchmark dead.
- OM rev .4 (23 Jul): **R37,304.63** — bus/taxi SASRIA removed (R8,205.21 → R55.65).
  −R230.57/mo vs current. Unauthorised pax **still not taken** (open ask).
- KP r21389 (23 Jul): **R33,928.03** — roadside removed as asked, SASRIA → R551.01,
  windscreen R5,520 kept. **−R3,607.17/mo ≈ −R43,286/yr** vs current. E-hailing wording and
  R2.0m/event **unchanged through two revisions** — the letter remains the gate.
  Optional: windscreen off → R28,408.03 (−R9,127/mo), glass claims then for client's account.

### Final standings (24 Jul)
| | All-in/mo | vs current | Pax liability |
|---|---|---|---|
| King Price r21389 | R33,928.03 | −R3,607.17 | R2.0m/event, e-hailing form ⚠ |
| Old Mutual .4 | R37,304.63 | −R230.57 | R2.5m/vehicle, clean ✓ |
| Santam current | R37,535.20 | benchmark | R2.5m/vehicle ✓ |

**Outstanding before signature:** (1) VAPS written confirmation that pax liability responds for
scheduled commuter/scholar/charter ops + lift to R2.5m/event; (2) OM to add unauthorised
passenger R2.5m; (3) client's written SASRIA sign-off (no riot cover on buses — their choice);
(4) client's keep/cut decision on KP windscreen. Also pending: Bronwyn's surname + email for
the proposal contact card.

## Method (how the comparison was done)

1. **Read every schedule page-by-page** (85p Santam, 42–49p OM, 33–38p VAPS) and reconcile
   the all-in totals to the cent — never compare headline "Total Premium" lines (Santam's
   R34,091.26 headline is pre-fees/SASRIA/VAT; the true figure is the "Total 15% VAT incl").
2. **Verify the decisive cover per item, not per summary** — Santam's R2.5m pax liability was
   confirmed on ~10 individual bus items; OM's on all 32 FPPL items; KP's wording read in full
   (that's how the e-hailing exclusion was caught — schedule p10, r21389 p10).
3. **Reconcile every round's delta** — each new total was explained line-by-line (round 3 moved
   *only* by SASRIA and roadside; anything unexplained would be a red flag).
4. **Evidence beyond the schedules** — the client's own website (weskaaptoere.co.za) proves
   scheduled/no-e-hailing operations; cited against the KP wording.
5. Key catch-outs for future rounds: KP third-party has a **R1m fire/explosion sub-limit**;
   Santam prices pax liability *inside* the motor rate ("in motor"); OM bundles fees.

## Deliverables (all in the deal folder, final)

- Round 1: `WesKaap_Busdiens_Comparison_Internal.pdf` (superseded, kept as history)
- Round 2: `WesKaap_Busdiens_Comparison_Internal_REVISED_21Jul2026.pdf`,
  `WesKaap_Busdiens_Comparison_CLIENT_21Jul2026.pdf`,
  `WesKaap_Busdiens_Renewal_Report_INTERNAL_21Jul2026.pdf` (5-page "fun" flagship with
  cartoons + charts — source HTML/cartoons were session files, not retained; PDFs final)
- Round 3 (current): `WesKaap_Busdiens_RM_Playbook_24Jul2026.pdf` (internal, RM-only) and
  `WesKaap_Busdiens_Client_Proposal_24Jul2026.pdf` (+ matching `.html` previews)

## The code — where it lives & how to rebuild

- **Build system (durable):** the `/cartrack-proposal` skill at
  `~/.claude/skills/cartrack-proposal/` — templates, CSS, fonts, logos, `build.py`
  (headless Chrome). This is the way to build any future round.
- **Current doc sources (this folder):** `weskaap_playbook_content.html`,
  `weskaap_proposal_content.html`. Rebuild:
  `python3 ~/.claude/skills/cartrack-proposal/build.py <content>.html <out>.pdf --title "..."`
- `wkt_logo.png` — client "logo" from their site (it's a photo, not a mark; proposal uses a
  text tile instead).
- Round-1/2 HTML sources and the four Nano Banana cartoons were scratchpad files and are gone;
  regenerate images via `node ~/nano-banana-2/generate.mjs "prompt"` if ever needed.
- If system Chrome headless breaks again (it did on 21 Jul): install puppeteer + its
  chrome-headless-shell (`npm i puppeteer && npx puppeteer browsers install
  chrome-headless-shell`) and print via a small script — that was the working fallback.

The deal's living memory (for future chats) is in Claude's memory file
`weskaap-busdiens-comparison.md` — it carries the full current state and points here.
