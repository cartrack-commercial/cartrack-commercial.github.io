"""Markdown -> Cartrack house-design HTML blocks."""
import re, html

def esc(s):
    return html.escape(s, quote=False)

def inline(s):
    s = esc(s)
    s = re.sub(r'`([^`]+)`', r'<code class="mono" style="background:var(--ink-50);padding:0 3px;border-radius:2px;font-size:8.6px">\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'<i>\1</i>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', s)
    s = s.replace('...', '&hellip;')
    return s

RULE = re.compile(r'^-{3,}\s*$')
TABLE = re.compile(r'^\s*\|')
H = re.compile(r'^(#{1,4})\s+(.*)$')
BUL = re.compile(r'^(\s*)[-*]\s+(.*)$')
NUM = re.compile(r'^(\s*)(\d+)\.\s+(.*)$')
QUOTE = re.compile(r'^>\s?(.*)$')

def _callout_cls(txt):
    if '🚨' in txt or 'Handling note' in txt or 'never' in txt.lower()[:60]:
        return 'warn'
    if txt.strip().startswith('<b>Evidence.</b>') or 'Evidence.' in txt[:40]:
        return 'verdict'
    if '⚠' in txt:
        return 'verdict'
    return 'info'

def parse(md):
    """Return (title, subtitle_lines, sections) where each section is
       {'title':str,'blocks':[block]} and block is a dict."""
    lines = md.split('\n')
    title = None
    sections = []
    cur = None
    pre = []                     # blocks before the first '##'
    i = 0
    n = len(lines)

    def out():
        return cur['blocks'] if cur is not None else pre

    while i < n:
        ln = lines[i]

        if RULE.match(ln):
            i += 1; continue

        m = H.match(ln)
        if m:
            lvl, txt = len(m.group(1)), m.group(2).strip()
            if lvl == 1 and title is None:
                title = txt; i += 1; continue
            if lvl == 2:
                cur = {'title': txt, 'blocks': []}
                sections.append(cur); i += 1; continue
            if lvl == 3:
                out().append({'t': 'html', 'h': f'<h3 style="margin:11px 0 5px">{inline(txt)}</h3>'})
                i += 1; continue
            out().append({'t': 'html', 'h': f'<div class="eyebrow ink" style="margin:9px 0 4px">{inline(txt)}</div>'})
            i += 1; continue

        if ln.startswith('```'):
            i += 1; buf = []
            while i < n and not lines[i].startswith('```'):
                buf.append(lines[i]); i += 1
            i += 1
            body = esc('\n'.join(buf))
            out().append({'t': 'html', 'h':
                '<div class="callout excess" style="white-space:pre;font-family:var(--font-mono);'
                'font-size:8.1px;line-height:1.45;overflow:hidden">' + body + '</div>'})
            continue

        if QUOTE.match(ln):
            buf = []
            while i < n and QUOTE.match(lines[i]):
                buf.append(QUOTE.match(lines[i]).group(1)); i += 1
            txt = ' '.join(x.strip() for x in buf if x.strip())
            h = inline(txt)
            out().append({'t': 'html', 'h': f'<div class="callout {_callout_cls(h)}">{h}</div>'})
            continue

        if TABLE.match(ln):
            rows = []
            while i < n and TABLE.match(lines[i]):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            if len(rows) >= 2 and set(rows[1][0].replace(' ', '')) <= set('-:'):
                head, body = rows[0], rows[2:]
            else:
                head, body = rows[0], rows[1:]
            out().append({'t': 'table', 'head': head, 'rows': body})
            continue

        if BUL.match(ln) or NUM.match(ln):
            ordered = bool(NUM.match(ln))
            items = []
            while i < n:
                m2 = NUM.match(lines[i]) if ordered else BUL.match(lines[i])
                if not m2:
                    # continuation line of the previous item
                    if items and lines[i].startswith(('  ', '\t')) and lines[i].strip():
                        items[-1] += ' ' + lines[i].strip(); i += 1; continue
                    break
                items.append(m2.group(3) if ordered else m2.group(2))
                i += 1
            tag = 'ol class="num-list"' if ordered else 'ul class="sq"'
            close = 'ol' if ordered else 'ul'
            lis = ''.join(f'<li>{inline(x)}</li>' for x in items)
            out().append({'t': 'html', 'h': f'<{tag} style="margin:6px 0 8px;{"margin-left:16px" if ordered else ""}">{lis}</{close}>'})
            continue

        if not ln.strip():
            i += 1; continue

        buf = [ln]
        i += 1
        while i < n and lines[i].strip() and not (RULE.match(lines[i]) or TABLE.match(lines[i])
                or H.match(lines[i]) or BUL.match(lines[i]) or NUM.match(lines[i])
                or QUOTE.match(lines[i]) or lines[i].startswith('```')):
            buf.append(lines[i]); i += 1
        txt = ' '.join(x.strip() for x in buf)
        out().append({'t': 'html', 'h': f'<p>{inline(txt)}</p>'})

    return title, pre, sections


def table_html(head, rows, first_bold=True):
    ncol = len(head)
    ths = ''.join(f'<th>{inline(h)}</th>' for h in head)
    body = ''
    for r in rows:
        r = (r + [''] * ncol)[:ncol]
        tds = []
        for j, c in enumerate(r):
            cell = inline(c)
            if j == 0 and first_bold:
                tds.append(f'<td><div class="item">{cell}</div></td>')
            else:
                tds.append(f'<td>{cell}</td>')
        body += '<tr>' + ''.join(tds) + '</tr>'
    return f'<table><thead><tr>{ths}</tr></thead><tbody>{body}</tbody></table>'
