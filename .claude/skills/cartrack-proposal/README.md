# cartrack-proposal: Claude Code skill

Builds branded **Cartrack Insurance** client proposals and RM playbooks as A4 PDFs.
Invoke in Claude Code with `/cartrack-proposal`, or just describe the task
("build a Cartrack client proposal for X"). Two document types share one design
system: the client-facing **proposal** and the internal **RM playbook**.

## Install
Nothing to install when working in this repo: Claude Code picks the skill up from
`.claude/skills/` at session start. To use it in other projects too, copy this whole
`cartrack-proposal/` folder into `~/.claude/skills/` on your machine.

## Requirements
- **Chrome or Chromium.** `build.py` renders the PDF headless and looks for it automatically:
  Chrome on macOS or Windows, Playwright's Chromium, or a system Chromium on Linux. If yours is
  somewhere else, set the `CARTRACK_CHROME` environment variable to the browser's full path.
- **Python 3**, standard library only. No pip installs.

## Files
- `SKILL.md`: the instructions Claude follows (workflow + component cheat-sheet).
- `build.py`: content HTML → self-contained A4 PDF (fonts/logos/CSS embedded as base64).
- `assets/cartrack.css`: the full design system.
- `assets/template.html`: client-proposal template.
- `assets/playbook-template.html`: RM-playbook template.
- `assets/fonts/`, `assets/logos/`: self-hosted Saira/IBM Plex fonts and Cartrack logos.

## Quick manual build (Claude does this for you)
```
cp assets/template.html myclient_content.html      # edit the figures/text
python3 build.py myclient_content.html myclient.pdf --client-logo logo.png --title "..."
```
