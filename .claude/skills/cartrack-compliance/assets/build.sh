#!/bin/bash
# build.sh <form-basename> <Output Name.pdf>
S=/tmp/claude-0/-home-user-cartrack-commercial-github-io/06e46c5c-057b-5f71-bba8-5c5b727605a7/scratchpad/telesure-response
CH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
"$CH" --headless --disable-gpu --no-sandbox --print-to-pdf="$S/_$1.pdf" --no-pdf-header-footer "file://$S/forms/$1.html" 2>/dev/null
cd "$S" && python3 fill.py "_$1.pdf" "$2" "$3" 2>&1 | grep widgets
python3 - "$2" "$1" <<'PY'
import pymupdf as fitz, sys
S="/tmp/claude-0/-home-user-cartrack-commercial-github-io/06e46c5c-057b-5f71-bba8-5c5b727605a7/scratchpad/telesure-response"
d=fitz.open(f"{S}/{sys.argv[1]}")
TOP,BOT=34,808
print(f"  pages={d.page_count}")
for i,p in enumerate(d):
    b=[x for x in p.get_text("blocks") if x[4].strip()]
    w=[x.rect.y1 for x in p.widgets()]
    low=max(max((x[3] for x in b),default=0), max(w,default=0))
    gap=BOT-low
    flag=" <-- GAP" if gap>90 and i<d.page_count-1 else ""
    print(f"  p{i+1} ends {low:.0f}  gap {gap:.0f}{flag}")
    p.get_pixmap(dpi=78).save(f"{S}/_v_{sys.argv[2]}_{i+1}.png")
PY
