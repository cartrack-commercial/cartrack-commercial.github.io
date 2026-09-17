# Eminent Wealth app — starter brief

*Paste this at the start of the new chat. Written 12 Aug 2026 from what the Cartrack RM System
taught us, including everything that broke on 12 August.*

---

## Who and what

Anne Kruger (annekruger3010@gmail.com) is building an internal web app for **Eminent Wealth** —
a **separate business** from Cartrack Insurance Commercial. Anne already runs three apps for
Cartrack; this one reuses the *build pattern* but must share **none** of the data.

Anne is not a developer. Explain in plain language, avoid jargon, and when something is a
judgement call, give a recommendation rather than a menu of options.

**Afrikaans messages to RMs/staff:** informal, English words mixed in. Anne's standing preference.

---

## The build pattern (proven — reuse it)

- **One single-file HTML app.** Everything in `index.html`: markup, CSS, JS in one file. Sounds
  wrong, is right for this — no build step, no toolchain, no node_modules, nothing to break.
- **Hosted on GitHub Pages.** `<org>/<repo>` → `<org>.github.io/<repo>/`.
- **Deploy = commit and push to `main`.** Pages rebuilds in 1–2 minutes. No pipeline.
- **Version stamp:** `const APP_VERSION='v2026.MM.DDx'` shown on the sign-in screen, bumped every
  push. When someone says "it's not working", the first question is which version they're on.
- **Service worker** (`sw.js`) for the home-screen icon and offline shell. **Network-first**, with
  `skipWaiting()` + `clients.claim()` so a fix reaches phones immediately. Bump the `CACHE` name
  on every deploy.

---

## Data: Supabase

- **Its own Supabase project.** Not a corner of the Cartrack one. Different business, different
  people, and if these are separate legal entities it is a POPIA matter, not just tidiness.
  It also caps the blast radius when something goes wrong — and something will.
- **Billing is per organization ($25/mo Pro), not per project**; extra projects ≈ $10/mo each.
  So: one org, projects inside it.
- **Turn on Pro before real data goes in.** The free plan has **no automated backups of any kind**.
  Pro gives 7 days of daily backups; point-in-time recovery is a paid add-on on top. See "12 August"
  below for why this is not optional.
- **Free projects pause after a week of inactivity** — fine for a daily tool, a trap for a
  quarterly one.

**Shape that worked:** a small number of wide tables, each row owned by a person, plus a `config`
table used as a general key/value store (settings, journals, snapshots). Route app-level keys like
`deals:<person>` to real tables in one `_route()` function, so the rest of the app just does
`sGet(key)` / `sSet(key, value)` and never thinks about SQL.

---

## Authentication — do NOT copy the RM System here

The RM System uses a **client-side PIN gate** and a single shared anon key. Every device can
technically write every other person's data; Row Level Security is the only real protection.
That is acceptable for an internal sales pipeline. **It is not acceptable for an app holding
client financial information.**

For Eminent Wealth, use **Supabase Auth** (real accounts) with **RLS policies keyed to the
signed-in user**. Decide this on day one — retrofitting auth after the data model is set is
painful.

---

## Coding patterns worth carrying across

These are the parts of the RM System that earned their place.

**1 · Merge-safe writes.** Never delete-all-then-insert a person's rows. Upsert row by row and
delete only what genuinely disappeared. A wholesale replace is how you lose a day's work when two
devices save at once.

**2 · Durable outbox.** Phones freeze a tab the moment it is backgrounded and kill the in-flight
save. Write a durable flag *before* the network attempt, retry on a timer, and show a banner while
anything is unsent. Never report success for a write that never left the device.

**3 · Two-phase boot.** Paint the sign-in screen first, load data behind it. Fetch independent
things concurrently, not one after another. Load rarely-used data lazily on the tab that needs it.
This took the RM System from ~14s to under half a second on a bad connection.

*But:* keep any wait that protects data. Two in the RM System are load-bearing — config must land
before a PIN screen (or a real PIN looks unset and gets overwritten), and everything must land
before the app opens (or a half-loaded list gets saved over the real one).

**4 · A write guard.** Refuse any save that would empty a collection or drop more than half of it
in one go. A person deletes one thing at a time; nothing legitimate looks like that. Only apply it
once a collection has 3+ rows so small lists still behave normally. **This is the single highest-value
thing in the whole list.**

**5 · Snapshot before overwriting.** Copy the previous value to a `snapshot:<key>` row before
replacing it, at most once per key per 10 minutes. Reconstruction from logs gets the names and
numbers back; a snapshot gets the *exact rows* back, notes and all.

**6 · A change journal.** Log every meaningful action to a separate table, one row per person per
day. It is cheap, and on 12 August it was one of only two records that survived — see below.

**7 · Live refresh.** Re-fetch on tab focus and on a timer. A tab left open all day showing
yesterday's data is its own kind of data loss.

**8 · Prove emptiness before writing on it.** A failed read and an empty table look identical
downstream. Track whether each read was actually *answered* by the server, and never let anything
write on the basis of "looks empty" without that proof.

---

## What broke on 12 August 2026 — read this before writing any save logic

The RM System had a `seedIfEmpty()` that wrote a built-in starter dataset when a person's data
looked empty. A performance change replaced its "re-read from the server first" check with a check
against already-loaded state.

When a Supabase read failed, the fallback cache was empty, so the app stored an empty list — which
is indistinguishable from an empty table. The seed then wrote three rows over live books.
**Every RM lost weeks of work.**

It was recoverable only because two side-records happened to exist for unrelated reasons: the
change journal, and payroll months that get seeded from everyone's book. There was **no database
backup** — the project was on the free plan. That was luck, not design.

**The four rules that came out of it:**

1. Anything that writes on emptiness needs **positive proof** of emptiness.
2. **Refuse destructive-shaped writes** rather than trusting every caller to be careful.
3. **Snapshot before overwriting.** Reconstruction loses the parts people care about most.
4. **Backups on before real data goes in.** Everything above is written by the same person who
   causes the bugs; a database backup is independent of that.

---

## Design

The Cartrack apps use "Compliance DS" — Saira + IBM Plex, near-black `#0B0C0F`, brand orange
`#F47735`. **That is Cartrack's identity, not a house style. Do not reuse it here.**

Eminent Wealth needs its own palette and type. Keep the *structure* that works — dark header with
role/tab bar, card-based lists, tabular figures for money, one accent colour used sparingly — and
replace the brand entirely. Ask Anne for Eminent Wealth's logo and colours before designing.

Money: always right-aligned, tabular figures, two decimals. Green when the client pays less, red
when it costs more. Never invert that.

---

## Decide these before writing code

1. **What does the app actually do**, and who uses it — how many people, on phones or desktop?
2. **What must it remember between people or devices?** If nothing, it may not need a database at
   all. Cartrack's Premium Comparison portal deliberately does everything in the browser, so
   client documents never leave the laptop — a real advantage for anything holding client data.
3. **Does it hold client financial information?** If yes: real auth, RLS per user, Pro plan with
   backups, from day one.
4. **Repo name and GitHub org**, so the Pages URL is settled early.
5. **Eminent Wealth's branding** — logo files and colours.

---

## Working style Anne expects

- Verify against real files and real output; never assert a figure that has not been checked.
- Say plainly when something is wrong, including when it is your own mistake, and lead with the fix.
- Commit and push working changes; do not leave work only in a scratch directory. *(Learned the
  hard way — a container recycle on 12 August destroyed four unsaved document sources.)*
- Test before declaring something fixed, and say what was tested.
