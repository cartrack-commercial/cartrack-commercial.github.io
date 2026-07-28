---
name: cartrack-proposal
description: >-
  Build branded Cartrack Insurance documents as PDF on the house design system (Saira +
  IBM Plex, dark/coloured mastheads, orange accent, green savings / red cost figures, stat
  cards, line-by-line tables, SWITCH/UPGRADE pills). Two document types: the client-facing
  PROPOSAL (sober, ink mastheads) and the internal RM PLAYBOOK (field edition — coloured
  mastheads, PLAY badges, RM-EYES-ONLY stamp, teardown tables, objection battlecard, "in the
  room" scripts). Use for premium comparisons, renewal proposals, policy reviews, RM playbooks.
  Fonts, logos and CSS are packaged; you only write content and render.
---

# Cartrack Insurance — client proposal builder

Produces the branded proposal look (see the ALW / Waste Carriers proposals) as an A4 PDF.
**Everything visual is already built.** Do not re-derive CSS, re-read the design system, or
rebuild fonts/logos — that is the whole point of this skill. You write content HTML and run
one command.

## Two document types — pick the template

- **Client proposal** → `assets/template.html`. What you hand the client. Sober ink-950
  mastheads, cover + exec-summary + line-by-line + next-steps/contact + sign-off.
- **RM playbook** → `assets/playbook-template.html`. Internal field guide the RM takes into the
  meeting — **RM only, never handed over**. Coloured mastheads per "play", PLAY badges, the
  RM-EYES-ONLY stamp, "what's in this pack", dense per-item teardown tables, Policy-DNA cards,
  the scoreboard, per-building pages with a "why" column, the **Naked Truth** (red-team weak
  spots + exact answers) and the **Battlecard** (objections + "in the room" scripts).

The two share one CSS and one build command. A full engagement is usually both: the client keeps
the proposal, the RM works from the playbook.

## Workflow (3 steps)

1. **Copy the template** to a working file (scratchpad or the client's folder). `<skill>` below
   is this skill's folder — `~/.claude/skills/cartrack-proposal` on Anne's Mac, or
   `.claude/skills/cartrack-proposal` inside the `cartrack-commercial.github.io` repo in
   web/cloud sessions:
   `cp <skill>/assets/template.html <name>_content.html`   (or `playbook-template.html`)
   Name the content file distinctly (e.g. `*_content.html`) — build.py writes a `<output>.html` preview beside the PDF, so a content file sharing the output stem would be at risk (build.py now guards against it, but keep them separate).
2. **Edit the body** — replace placeholder text/figures. Add or remove `.page` blocks by
   copying the component blocks (each page in the template is labelled with an HTML comment).
   Keep each page's content within one A4 sheet (overflow is clipped).
3. **Render:**
   `python3 <skill>/build.py <work>.html <out>.pdf --client-logo <logo.png> --title "..."`
   build.py embeds fonts + logos + CSS and writes both `<out>.pdf` and a browsable `<out>.html`.
   Open the `.html` in the Browser pane to verify layout before delivering the PDF.

`--client-logo` is optional; omit it and the "prepared for" tiles render empty. The tile is a
**white rounded card**, so pass the client's **colour or dark** logo (a white-only logo vanishes
on it). If you only have a white logo, either use the client's mark, or delete the `.client-chip`
wrapper and place the white logo straight on the dark masthead. Source the logo from the client's
website if not supplied (their own media library usually has both variants); save it next to the
work file so the build is repeatable.

## Logo tokens (build.py swaps these to embedded images)

`{{CARTRACK_WHITE}}` `{{CARTRACK_DARK}}` `{{CARTRACK_MARK}}` `{{CARTRACK_MARK_WHITE}}` `{{CLIENT_LOGO}}`

## Component cheat-sheet (classes in assets/cartrack.css — no need to open it)

- **Page**: `<div class="page">` (light) or add `cover` for the gradient cover. One page = one A4.
- **Masthead** (dark band, bleeds to edges): `.masthead` with `.eyebrow.on-dark` + `<h2>` +
  `<span class="client-chip sm"><img src="{{CLIENT_LOGO}}"></span>`.
- **Eyebrow**: `.eyebrow` (orange), `.eyebrow.ink` (grey), `.eyebrow.rule` (orange rule prefix).
- **Stat cards** (3-across): `.stat-band` > `.stat`. Variants: `.stat.save` (green), `.stat.cost`
  (cream/amber), `.stat.hero` (highlighted border). `.k` label · `.v` big value · `.sub` note.
- **Tables**: `<th class="r">`/`<td class="r">` right-align money. Tint the proposed column with
  `<col class="propcol">` + `class="propcol"` on its cells. `.item` = bold row label, `.desc` =
  grey sub-note. `tr.total` = bold totals row. Figures: `.neg` green (saving −), `.pos` red (+).
- **Pills**: `.pill.switch` (green), `.pill.upgrade` (amber), `.pill.review`, `.pill.same`.
- **Chips**: `.chips` > `.chip` (add `.dot` for orange dot, `.on` for filled).
- **Callouts**: `.callout` + `.rec` (recommendation/orange), `.verdict` (amber), `.warn` (red),
  `.info` (grey), `.excess` (bordered). First child `<span class="eyebrow">Label</span>`.
- **Steps**: `ul.steps` > `li` with `<span class="n">1</span>` + `.t` title + `.b` body (last n = orange).
- **Lists**: `ul.checks` (green ✓), `ul.sq` (orange square), `ol.num-list`.
- **Two columns**: `.cols` with `.col-head` headers.
- **Contact card**: `.contact` (`.k` label, `.name`, `.row` lines).
- **Sign-off**: `.sign` > `.blk` > `.line` + `.cap`.
- **Data grid**: `.df-grid` > `.df` (`.k`/`.v`) for cover metadata.
- **Footers**: `.foot` (mark + page no.) or `.foot.legal` (FSP disclosure line, `.pg` = page no.).

## Playbook-only components (in cartrack.css; see playbook-template.html)

- **Coloured mastheads**: `.masthead.orange` (game plan / battlecard), `.teal` (cover story /
  scoreboard / switch building), `.blue` (current teardown), `.purple` (current DNA), `.pink`
  (proposed teardown). Naked Truth = a full `<div class="page dark">`.
- **PLAY badge**: `<span class="play-badge">Play 03</span>` (outlined pill, top-right of masthead).
- **Audience tags**: `.aud.rm` `.aud.client` `.aud.both` `.aud.rmonly`.
- **RM stamp**: `<span class="stamp"><b>RM EYES ONLY</b>DO NOT HAND TO THE CLIENT</span>`.
- **Pack grid**: `.pack-grid` > `.pack` (`.n`/`.ti`/`.aud` + `.d`). **Run steps**: `.run` (`.n`+`.b`).
  **Jump table**: `.jump` > `.row` (`.q` + `.to`).
- **Teardown table**: add `tr.grp` (section label row: MATERIAL DAMAGE / SASRIA / FEES),
  `tr.sub` (subtotal), `tr.allin` (dark all-in total). Columns = one per item/building.
- **DNA card**: `.dna` (`.top` > `.nm` + `.fig`, `.ref`, `.cond`/`.cond.warn`/`.cond.win`, `.note`).
- **Feature card**: `.feature.lever` (cream) / `.feature.norm` (green) with `.k`+`.big`+`.sub`.
  **Big-number**: `.bignum` (`.k`/`.v`/`.sub`).
- **Dark callouts**: `.callout.dark` (Before you present / Bottom line), add `.quote` for scripts
  (In the room / Close like this).
- **Red-team cards** (Naked Truth): `.rt-grid` > `.rt` (`.n`+`.ti` red-flag, `.sub`, `.say` script).
- **Battlecard**: `.obj` (`.q` speech-bubble question + `.a` green-tick answer); `.checkgrid` > `.it`
  (☐ night-before checklist).

## House rules (match the brand)

- Money always in `<span class="num">` / right-aligned cells; tabular figures.
- **Green = client pays less, red = costs more.** Never invert. A dearer premium that buys better
  cover is an `upgrade` (amber), not a failure.
- Voice: plain, confident, decision-first. Lead with the recommendation and the number.
- Always carry the FSP 17266 disclosure and "policy wording prevails" in the legal footer.
- Cartrack is the preparer (masthead/footer/sign-off); the client logo goes in the "prepared for"
  tile only — never present the document as if the client authored it.

## Entity data (Cartrack Insurance Agency (Pty) Ltd)

Reg 2001/008050/07 · FSP 17266 · Grosvenor Corner, 13 Keyes Avenue, Rosebank, Johannesburg.

## Notes

- Renderer: build.py auto-detects headless Chrome — Mac Chrome, Playwright Chromium
  (`/opt/pw-browsers/…`, used in web/cloud sessions), or system chromium. Override with the
  `CARTRACK_CHROME` env var if needed.
- Reference of the finished look: `01 Cartrack/Commercial - RMs/Commercial Policies 16.24.50/ALW- Phillip/Design.pdf`.
- The design system this is distilled from lives at `05 Builds & Code/Claude Code/_ds/cartrack-insurance-compliance-design-sys-*` (only needed if extending the CSS).
