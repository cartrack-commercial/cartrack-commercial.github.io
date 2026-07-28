#!/usr/bin/env python3
"""
Cartrack Insurance proposal builder.
Wraps a content-only HTML fragment (the .page divs) with the design-system
CSS, self-hosted fonts and logos (all base64-embedded), then renders A4 PDF
via headless Chrome. Output is self-contained and portable.

Usage:
  python3 build.py CONTENT.html OUTPUT.pdf [--client-logo PATH] [--title "..."]

In CONTENT.html use these placeholder tokens where logos go:
  {{CARTRACK_WHITE}}  {{CARTRACK_DARK}}  {{CARTRACK_MARK}}  {{CARTRACK_MARK_WHITE}}  {{CLIENT_LOGO}}
Everything else is normal HTML using classes from assets/cartrack.css
(see assets/template.html for copy-paste blocks).
"""
import base64, glob, os, pathlib, sys, subprocess, argparse

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE / "assets"

def find_chrome():
    # CARTRACK_CHROME env var wins; then Mac Chrome; then Playwright/Linux chromium.
    cands = [os.environ.get("CARTRACK_CHROME"),
             "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/opt/pw-browsers/chromium",
             *sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"), reverse=True),
             "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"]
    for c in cands:
        if c and pathlib.Path(c).exists():
            return c
    sys.exit("build.py: no Chrome/Chromium found — set CARTRACK_CHROME to the binary path")

CHROME = find_chrome()

def b64(p, mime):
    return f"data:{mime};base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()

def font_face(family, weight, path):
    return (f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};"
            f"font-display:swap;src:url({b64(path,'font/woff2')}) format('woff2')}}")

FONTS = [
    ("Saira",600,"fonts/saira/saira-600.woff2"), ("Saira",700,"fonts/saira/saira-700.woff2"),
    ("Saira",800,"fonts/saira/saira-800.woff2"),
    ("IBM Plex Sans",400,"fonts/plex-sans/plex-sans-400.woff2"),
    ("IBM Plex Sans",600,"fonts/plex-sans/plex-sans-600.woff2"),
    ("IBM Plex Sans",700,"fonts/plex-sans/plex-sans-700.woff2"),
    ("IBM Plex Mono",400,"fonts/plex-mono/plex-mono-400.woff2"),
    ("IBM Plex Mono",600,"fonts/plex-mono/plex-mono-600.woff2"),
]
LOGOS = {
    "{{CARTRACK_WHITE}}":      ("logos/cartrack-insurance-horizontal-white.png","image/png"),
    "{{CARTRACK_DARK}}":       ("logos/cartrack-insurance-horizontal.png","image/png"),
    "{{CARTRACK_MARK}}":       ("logos/cartrack-insurance-mark.png","image/png"),
    "{{CARTRACK_MARK_WHITE}}": ("logos/cartrack-insurance-mark-white.png","image/png"),
}

def build(content_path, out_pdf, client_logo=None, title="Cartrack Insurance"):
    content = pathlib.Path(content_path).read_text()
    # inner body only, if a full doc was passed
    if "<body" in content:
        content = content.split("<body",1)[1].split(">",1)[1].rsplit("</body>",1)[0]
    for tok,(rel,mime) in LOGOS.items():
        content = content.replace(tok, b64(ASSETS/rel, mime))
    # client logo: embed if given, else blank (any client-chip block referencing it just shows empty)
    content = content.replace("{{CLIENT_LOGO}}", b64(client_logo,"image/png") if client_logo else "")
    css = (ASSETS/"cartrack.css").read_text()
    head = "".join(font_face(f,w,ASSETS/p) for f,w,p in FONTS) + css
    html = (f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>{title}</title>"
            f"<style>{head}</style></head><body>{content}</body></html>")
    out_pdf = pathlib.Path(out_pdf).resolve()
    full_html = out_pdf.with_suffix(".html")
    # never clobber the input content file if it shares the output stem
    if full_html.resolve() == pathlib.Path(content_path).resolve():
        full_html = out_pdf.with_name(out_pdf.stem + ".rendered.html")
    full_html.write_text(html)
    flags = [CHROME,"--headless","--disable-gpu","--no-pdf-header-footer"]
    if sys.platform.startswith("linux"):
        flags += ["--no-sandbox","--disable-dev-shm-usage"]
    subprocess.run(flags + [f"--print-to-pdf={out_pdf}", full_html.as_uri()],
                   check=True, capture_output=True)
    print(f"OK  {out_pdf}  ({out_pdf.stat().st_size} bytes)")
    print(f"    preview: {full_html}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("content"); ap.add_argument("output")
    ap.add_argument("--client-logo", default=None); ap.add_argument("--title", default="Cartrack Insurance")
    a = ap.parse_args()
    build(a.content, a.output, a.client_logo, a.title)
