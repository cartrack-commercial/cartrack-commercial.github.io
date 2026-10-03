---
name: cartrack-compliance
description: Build FAIS/POPIA compliance documents for Cartrack Insurance Agency (FSP 17266) as branded, type-in fillable PDFs, and cite the right legislation while doing it. Use for due-diligence responses, registers, declarations, policies, frameworks and anything a Key Individual signs. Carries the FSCA citation map, the house print design system and the fillable-PDF build chain.
---

# Cartrack Insurance — compliance documents

Two jobs: **cite correctly**, then **build in the house style**. The citation work comes first,
because a beautiful document with a wrong section number is worse than a plain one.

## The entity (use verbatim)

- **Cartrack Insurance Agency (Pty) Ltd**, FSP **17266**, Reg **2001/008050/07**
- Directors: **J Marais, JD Allen**
- Key Individuals: **Brendan Kruger** and **Jennie Allen** — either may sign as KI
- Compliance Officer: **Daniel Opperman**
- Authline (every document): `An Authorised Financial Services Provider · FSP No. 17266 · Reg No: 2001/008050/07 · Directors: J Marais, JD Allen`

## Accuracy protocol — non-negotiable

1. **Cite primary sources only.** Act plus section number. Never a summary, never a study guide's
   paraphrase, and never from memory — including mine. I get section numbers wrong.
2. **Two-pass rule.** Build from source, then verify every citation in a separate pass.
3. **Name the source precisely.** Which Act, which Board Notice, which amendment date, which page.
   Where a document uses more than one numbering scheme, say which one you mean.
4. **An unverified figure stays marked unverified.** Never fill a confident-looking blank.
5. **Date-stamp everything.** FAIS moves — BN 194 of 2017, FAIS Notice 86 of 2018, the Joint
   Standards, the 2024 Ombud Council Rules.
6. **Never invent a regulator's contact details.** Addresses and complaint routes change. Leave the
   block fillable with a "checked on" date instead.

Start from `references/fais-citation-map.md`. It is the FSCA's own published qualifying criteria,
so it is the authoritative index of which section governs what.

## Where the source material lives

Anne's Google Drive → **My Drive / RE5** (`1tvxEft5aIhhjiBfhy3f9X8oKvu0IPrGB` — capital **I**; the
browser font renders it as a lowercase l and the wrong one 404s). Read it from Drive. The session
scratchpad has been wiped three times mid-task; do not assume local copies survive.

⚠️ **Copyright.** The F5 Academy study guide in that folder is third-party copyright, study use
only — never reproduce its prose into a deliverable or commit it here. The FSCA matrix and prep
guide are the regulator's published material and are fine. Statutory text quoted inside any of them
is law: quote it freely.

## Building the document

HTML → headless Chromium → PyMuPDF widget injection. Three steps:

```bash
# 1. author  <name>.html, linking ../assets/style.css  (copy templates/document.html)
# 2. render
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --disable-gpu --no-sandbox \
  --print-to-pdf=_out.pdf --no-pdf-header-footer "file://$PWD/<name>.html"
# 3. make it fillable
python3 assets/fill.py _out.pdf "Final Document Name.pdf"
```

`fill.py` places a text widget under every grey uppercase caption and in every empty narrow table
cell. Table-cell widgets default to `0`, which is what a nil return wants.

### Design system
Black full-bleed masthead · orange `#F47735` rule · orange circle section badges · lilac fillable
fields `#e9edf8` · meta strip · centred authline over a two-column footer. Cambria/Caladea headings,
Calibri/Carlito body, Consolas for references.

### Traps, all of which have bitten
- **The field detector overreaches.** Letter-spaced small caps render as `FSP N AM E`, so the skip
  list is compared with *all* whitespace stripped. Add new meta/table-header captions to `SKIP`.
- **Never redact to clear a value.** Searching for `"0"` and redacting hits body text too — it turned
  "Board Notice 80 of 2003" into "Board Notice 8 0 of 2 0 3". Leave the HTML input empty and let
  `fill.py` supply the default instead.
- **Long tables jump whole pages.** `style.css` sets `table{break-inside:avoid}`. For any table over
  ~8 rows, override in the document: `table{break-inside:auto} tr{break-inside:avoid}
  thead{display:table-header-group}`.
- **Orphan footers.** Wrap the closing signature block, authline and footer in one
  `<div class="keep">` with `break-inside:avoid`.
- **Always look at the rendered pages.** Render to PNG and read them. Page-fill and widget counts
  do not catch a covered meta strip.

```bash
python3 -c "
import pymupdf as fitz; d=fitz.open('Final Document Name.pdf')
print('pages:',d.page_count)
for i,p in enumerate(d):
    b=[x for x in p.get_text('blocks') if x[4].strip()]
    print(f'  p{i+1} fill={max((x[3] for x in b),default=0):.0f}/842')
    p.get_pixmap(dpi=85).save(f'_p{i+1}.png')"
```

## Writing for a due-diligence reader

- **Declare, don't merely show.** A nil register proves nothing on its own. Six Major Concerns came
  from sending an empty register with no declaration attached. Say the position in words, signed.
- **Answer in the regulator's defined terms**, not general usage — see
  `references/gcoc-complaints.md` for how "complaint" and "reportable complaint" differ, and why it
  changes what must be recorded.
- **Separate what the FSP can close from what it cannot**, and name the owner of each.
- **Where an obligation did not arise, say both things**: that it did not arise, and that the
  framework for it exists anyway.
