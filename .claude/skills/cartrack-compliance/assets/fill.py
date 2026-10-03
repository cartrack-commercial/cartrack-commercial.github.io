import pymupdf as fitz, sys, re
FILL=(0.914,0.929,0.973); BORDER=(0.71,0.74,0.84)
SKIP={re.sub(r"\s","",x) for x in [
  "FSP NAME","FSP NUMBER","REPORTING PERIOD","ISSUED","EFFECTIVE DATE","VERSION",
  "REF","CATEGORY","DEFINED TERM","BASIS OF RECORD","NUMBER","TERM","MEANING UNDER THE CODE",
  "STAGE","ACTION","OWNER","TURNAROUND","OBLIGATION","REQUIREMENT"]}
def norm(t): return re.sub(r"\s","",t.replace(" "," ")).upper()
def greyish(sp):
    c=sp.get("color",0); r,g,b=(c>>16)&255,(c>>8)&255,c&255
    return abs(r-g)<18 and abs(g-b)<18 and 55<=r<=150
def is_cap(sp):
    t=sp["text"].strip(); L=[c for c in t if c.isalpha()]
    if len(L)<2 or not all(c.isupper() for c in L): return False
    u=norm(t)
    if u.startswith("FSPNO") or u in SKIP: return False
    if "SIGNATURE" in u or "AUTHORISED" in u: return False
    return greyish(sp)
def run(inp,outp):
    doc=fitz.open(inp); n=0
    for pno,pg in enumerate(doc):
        W=pg.rect.width; RIGHT=W-34; MID=W/2
        spans=[sp for b in pg.get_text("dict")["blocks"] for l in b.get("lines",[]) for sp in l["spans"] if sp["text"].strip()]
        caps=[sp for sp in spans if is_cap(sp)]
        for sp in caps:
            x0,y0,x1,y1=sp["bbox"]
            same=[s for s in caps if s is not sp and abs(s["bbox"][1]-y0)<6 and s["bbox"][0]>x1]
            right=(min(s["bbox"][0] for s in same)-8) if same else (RIGHT if x0>MID-30 else (MID-12 if any(abs(s["bbox"][1]-y0)<6 and s["bbox"][0]>=MID-30 for s in caps) else RIGHT))
            right=max(right,x0+70)
            w=fitz.Widget(); w.rect=fitz.Rect(x0-2,y1+3,right,y1+19)
            w.field_type=fitz.PDF_WIDGET_TYPE_TEXT; w.field_name=f"f{pno}_{n}"
            w.fill_color=FILL; w.border_color=BORDER; w.border_width=0.5; w.text_fontsize=10
            pg.add_widget(w); n+=1
        try: tabs=pg.find_tables()
        except Exception: tabs=None
        for t in (tabs.tables if tabs else []):
            ys=sorted({round(c[1],0) for c in t.cells if c}); hy=ys[0] if ys else None
            for c in t.cells:
                if not c: continue
                r=fitz.Rect(c)
                if r.height<8 or r.width<24 or r.width>160: continue
                if hy is not None and abs(r.y0-hy)<2: continue
                if pg.get_textbox(r).strip(): continue
                w=fitz.Widget(); w.rect=fitz.Rect(r.x0+1,r.y0+1,r.x1-1,r.y1-1)
                w.field_type=fitz.PDF_WIDGET_TYPE_TEXT; w.field_name=f"t{pno}_{n}"
                w.field_value="0"; w.text_fontsize=10
                w.fill_color=FILL; w.border_width=0
                pg.add_widget(w); n+=1
    doc.save(outp, garbage=3, deflate=True); return n
print("widgets:", run(sys.argv[1],sys.argv[2]))
