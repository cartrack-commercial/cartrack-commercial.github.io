import pymupdf as fitz, sys, re
FILL=(0.914,0.929,0.973); BORDER=(0.71,0.74,0.84)
SKIP={re.sub(r"\s","",x) for x in [
  # meta-strip labels only. Table headers are white-on-black, so greyish() already excludes them —
  # do NOT add field captions like DATE or VERSION here, they are real fields elsewhere.
  "FSP NAME","FSP NUMBER","REPORTING PERIOD","ISSUED","EFFECTIVE DATE"]}
def norm(t): return re.sub(r"\s","",t.replace(" "," ")).upper()
def greyish(sp):
    c=sp.get("color",0); r,g,b=(c>>16)&255,(c>>8)&255,c&255
    return abs(r-g)<18 and abs(g-b)<18 and 55<=r<=150
def rules(pg):
    """horizontal rules — used to detect signature lines"""
    return [d["rect"] for d in pg.get_drawings()
            if d["rect"].height<3.5 and d["rect"].width>110]
def under_sig_line(sp, rr):
    """True if a horizontal rule sits just above this caption (a signature line)"""
    x0,y0,x1,y1=sp["bbox"]
    for r in rr:
        if r.y1 <= y0 and (y0-r.y1) < 14 and r.x0 <= x0+12 and r.x1 >= x1-12:
            return True
    return False
def run(inp,outp,table_default=""):
    doc=fitz.open(inp); n=0
    for pno,pg in enumerate(doc):
        W=pg.rect.width; RIGHT=W-34; MID=W/2
        rr=rules(pg)
        spans=[sp for b in pg.get_text("dict")["blocks"] for l in b.get("lines",[]) for sp in l["spans"] if sp["text"].strip()]
        caps=[]
        for sp in spans:
            t=sp["text"].strip(); L=[c for c in t if c.isalpha()]
            if len(L)<2 or not all(c.isupper() for c in L): continue
            u=norm(t)
            if u.startswith("FSPNO") or u in SKIP: continue
            if "SIGNATURE" in u or "AUTHORISED" in u: continue
            if not greyish(sp): continue
            if under_sig_line(sp, rr): continue          # <- signature-line captions
            caps.append(sp)
        for sp in caps:
            x0,y0,x1,y1=sp["bbox"]
            same=[s for s in caps if s is not sp and abs(s["bbox"][1]-y0)<6 and s["bbox"][0]>x1]
            right=(min(s["bbox"][0] for s in same)-8) if same else (RIGHT if x0>MID-30 else (MID-12 if any(abs(s["bbox"][1]-y0)<6 and s["bbox"][0]>=MID-30 for s in caps) else RIGHT))
            right=max(right,x0+70)
            rect=fitz.Rect(x0-2,y1+3,right,y1+19)
            pre=pg.get_textbox(rect).strip()             # keep any pre-filled value
            # a wrapped caption fragment is not a value: drop all-caps / parenthetical leftovers
            if pre and (pre.startswith("(") or pre.replace(" ","").isupper() or "\n" in pre): pre=""
            w=fitz.Widget(); w.rect=rect
            w.field_type=fitz.PDF_WIDGET_TYPE_TEXT; w.field_name=f"f{pno}_{n}"
            if pre: w.field_value=pre
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
                if table_default: w.field_value=table_default
                w.text_fontsize=10; w.fill_color=FILL; w.border_width=0
                pg.add_widget(w); n+=1
    doc.save(outp, garbage=3, deflate=True); return n
if __name__=="__main__":
    td = sys.argv[3] if len(sys.argv)>3 else ""
    print("widgets:", run(sys.argv[1],sys.argv[2],td))
