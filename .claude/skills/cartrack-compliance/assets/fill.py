import pymupdf as fitz, sys, re
FILL=(0.914,0.929,0.973); BORDER=(0.71,0.74,0.84)
SKIP={re.sub(r"\s","",x) for x in [
  # meta-strip labels only. Table headers are white-on-black, so greyish() already excludes them —
  # do NOT add field captions like DATE or VERSION here, they are real fields elsewhere.
  "FSP NAME","FSP NUMBER","REG. NUMBER","REG NUMBER","REPORTING PERIOD","ISSUED","EFFECTIVE DATE"]}
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
    pristine=fitz.open(inp)   # tables are detected here, before any field is added
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
        # textareas: a caption whose field sits on top of a full-width bordered box gets the whole box, multi-line
        for w in list(pg.widgets()):
            if w.field_type!=fitz.PDF_WIDGET_TYPE_TEXT: continue
            box=[dr["rect"] for dr in pg.get_drawings()
                 if dr["rect"].x0<40 and dr["rect"].x1>W-40 and abs(dr["rect"].y0-w.rect.y0)<8 and 25<dr["rect"].height<300]
            if not box: continue
            b=max(box,key=lambda r:r.height); name=w.field_name; pg.delete_widget(w)
            nw=fitz.Widget(); nw.rect=fitz.Rect(34,b.y0+1,W-34,b.y1-1); nw.field_type=fitz.PDF_WIDGET_TYPE_TEXT
            nw.field_name=name; nw.field_flags=fitz.PDF_TX_FIELD_IS_MULTILINE
            nw.fill_color=FILL; nw.border_color=BORDER; nw.border_width=0.5; nw.text_fontsize=10; pg.add_widget(nw)
        # checkboxes: every drawn 8-18pt square (an <input type=checkbox> prints as one)
        sq=[]
        for dr in pg.get_drawings():
            r=dr["rect"]
            if 8<=r.width<=18 and 8<=r.height<=18 and abs(r.width-r.height)<4 and not any(abs(r.x0-o.x0)<5 and abs(r.y0-o.y0)<5 for o in sq): sq.append(r)
        for r in sq:
            w=fitz.Widget(); w.rect=r; w.field_type=fitz.PDF_WIDGET_TYPE_CHECKBOX; w.field_name=f"cb{pno}_{n}"
            w.fill_color=FILL; w.border_color=BORDER; w.border_width=0.6; pg.add_widget(w); n+=1
        try: tabs=pristine[pno].find_tables()
        except Exception: tabs=None
        # a form grid is not a table: keep only compact tables with a sane cell count
        real=[t for t in (tabs.tables if tabs else []) if len(t.cells)<=80 and (t.bbox[3]-t.bbox[1])<=450]
        for t in real:
            ys=sorted({round(c[1],0) for c in t.cells if c}); hy=ys[0] if ys else None
            for c in t.cells:
                if not c: continue
                r=fitz.Rect(c)
                if r.height<8 or r.width<24 or r.width>160: continue
                if hy is not None and abs(r.y0-hy)<2: continue
                if pg.get_textbox(r).strip(): continue
                if any(x.rect.intersects(r) for x in pg.widgets()): continue
                w=fitz.Widget(); w.rect=fitz.Rect(r.x0+1,r.y0+1,r.x1-1,r.y1-1)
                w.field_type=fitz.PDF_WIDGET_TYPE_TEXT; w.field_name=f"t{pno}_{n}"
                if table_default: w.field_value=table_default
                w.text_fontsize=10; w.fill_color=FILL; w.border_width=0
                pg.add_widget(w); n+=1
    doc.save(outp, garbage=3, deflate=True); return n
if __name__=="__main__":
    td = sys.argv[3] if len(sys.argv)>3 else ""
    print("widgets:", run(sys.argv[1],sys.argv[2],td))
