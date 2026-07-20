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
- Built as HTML → Playwright `chromium` → PDF (A4 `.page` divs, 1123px each; render, measure `.page` heights, repaginate if any overflow).
- Design assets to rebuild: fonts `spacegrotesk-500/700`, `spacemono-400/700`, `librefranklin-400/600/700` (`.woff2`) + `cartrack-insurance-horizontal-white.png` — committed in `cartrack-premium-comparison/assets/`. Generators (`gen_*.py`) live in the session scratchpad and are **not** committed.
- Afrikaans RM messages: informal, mix in English words (Anne's standing preference). Figures must NOT be monospace — Space Grotesk (display) / Libre Franklin tabular (figures) / Space Mono (labels only).

---

## Client status (as at Jul 2026)
- **Waste Carriers & Nutri Humus** (228-vehicle fleet, Merx MRXP03339, renew 01 Aug): **BLOCKED** — cannot present until Merx answers the underwriter questions (telematics waiver / is Cartrack approved, excess table, loss ratio + fund forfeiture, tracking on 116 untracked, pollution liability, credit shortfall, territorial). RM: **Jean (he)**. Big finding = telematics excess waiver worth ~R238,990/truck, but that's Brendan→Bret's units track, kept separate.
- **Twin Trans** (Santam vs King Price/VAPS): done. King Price cheaper but drops pollution + halves third-party (R5m→R2.5m, fire/explosion R1m) — dangerous for a fuel tanker.
- **WesKaap Busdiens** (Santam vs Old Mutual vs King Price): done. All within ~R2.4k on price; both proposals weaken passenger liability (current R2.5m; OM R1m non-fare-paying; KP not taken). RM: **Bronwyn**.

## Conventions
- Commit trailers used in this project:
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` + `Claude-Session: …`
- Never put the model id in commits / code / PRs (chat only).
- People's pronouns: use they/them unless stated. **Jean = he.**
