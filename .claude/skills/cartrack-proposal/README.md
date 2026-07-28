# cartrack-proposal — Claude Code skill

Builds branded **Cartrack Insurance** client proposals and RM playbooks as A4 PDFs.
Invoke in Claude Code with `/cartrack-proposal`, or just describe the task
("build a Cartrack client proposal for X"). Two document types share one design
system: the client-facing **proposal** and the internal **RM playbook**.

## Install
Copy this whole `cartrack-proposal/` folder into `~/.claude/skills/` on the target
machine. It's picked up automatically at the next Claude Code session start.

## Requirements
- **Google Chrome** — `build.py` renders the PDF via headless Chrome and expects it at
  `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`. If Chrome is elsewhere,
  edit the `CHROME` path near the top of `build.py`.
- **Python 3** (standard library only — no pip installs needed).
- macOS assumed (paths use the macOS Chrome location).

## Files
- `SKILL.md` — the instructions Claude follows (workflow + component cheat-sheet).
- `build.py` — content HTML → self-contained A4 PDF (fonts/logos/CSS embedded as base64).
- `assets/cartrack.css` — the full design system.
- `assets/template.html` — client-proposal template.
- `assets/playbook-template.html` — RM-playbook template.
- `assets/fonts/`, `assets/logos/` — self-hosted Saira/IBM Plex fonts and Cartrack logos.

## Quick manual build (Claude does this for you)
```
cp assets/template.html myclient_content.html      # edit the figures/text
python3 build.py myclient_content.html myclient.pdf --client-logo logo.png --title "..."
```
