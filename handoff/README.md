# Handoff pack, Cartrack Insurance Commercial Division

21 September 2026.

| # | Document | What it covers |
|---|---|---|
| 1 | `01-rm-system.md` | The RM System: architecture, the seven tables, the write path, and the six decisions that look odd and are load-bearing. |
| 2 | *(circulated as a file, not committed)* | The security position: the anon key, RLS, the client-side PIN gate, why RLS alone cannot close it, and the Supabase Auth path. |
| 3 | `03-comparison-method.md` | The quote comparison method: the seven steps, the findings taxonomy, decisive cover by client type, excess structures, and the Cartrack lead. |
| 4 | `04-portal.md` | The comparison portal: what it does, what it cannot do, and a prioritised build spec drawn from checks that have actually caught something. |

**Document 2 is deliberately absent from this repository.** It summarises weaknesses in a live
system, and all three repositories are currently public. It is handed over as a file.

Read 3 before 4. Read 1 before touching any code in `cartrack-rm-system`.

## Branded PDFs

Each document also renders as a branded A4 PDF on the house design system (Saira + IBM Plex,
coloured mastheads because these are internal documents, INTERNAL classification on the cover).

`handoff/build/build_handoff.py` does it. It converts the markdown to the house components and
**paginates by measuring real layout in headless Chromium** rather than estimating, because
`cartrack.css` sets `.page{overflow:hidden}` and a mis-estimated page clips silently. Tables that
do not fit are split row by row with the header repeated.

    python3 handoff/build/build_handoff.py

Document 2's PDF is produced but, like its markdown, is **not committed**.
