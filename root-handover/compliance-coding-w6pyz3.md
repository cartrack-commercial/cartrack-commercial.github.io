# Handover: compliance-coding-w6pyz3

Written 17 October 2026 for Anné Kruger, Root Innovations, from the chat whose working branch is
`claude/compliance-coding-w6pyz3` (session https://claude.ai/code/session_015sV4nGEUE4bNBwFjmtHiWn).
This file is committed on branch `root-handover` in folder `root-handover/` of the launcher
repository, uploaded to OneDrive at Root Innovations/Handovers/, and accompanied by the package
`compliance-coding-w6pyz3.zip` (stripped sources, README inside).

Names are deliberately absent. The client is "the FSP" (a Category I financial services provider,
the insurance division of a national telematics company). Its people are referred to by role. The
counterparty is "the insurer" (a large short-term insurer running an outsource-partner due diligence).

## 1. What this chat was for

From early July 2026 (first dated deliverable 14 July) to 9 October 2026, this chat supported the
FSP's regulatory compliance work while Anné had no access to any of the FSP's systems and worked
only from her personal Gmail, a second employer's Outlook, her Mac and her Google Drive. Three
workstreams: first, assembling, correcting and sending a 13-section, 40-document pack for the
insurer's outsource-partner due diligence (July); second, evaluating a compliance SaaS vendor's
pilot and building an in-house alternative, a demo app and a 38-obligation register (September);
third, reading the insurer's 24-page findings report, finding the cause of all six Major Concern
findings, building four signable documents to close them, and sending the response to the division
head on 9 October. Along the way the chat produced a reusable compliance document build chain and a
citation map from the regulator's own qualifying criteria, both committed to the repository.

## 2. What I did myself

Facts, dated. Items the assistant produced are in section 3; this list is Anné's own work and
decisions.

- 10 to 15 July 2026: reviewed every page of the branded pack PDFs one document at a time and
  directed the layout fixes (signature blocks moved to the correct page, sections kept together,
  orphaned footers removed). On 15 July caught that the privacy policy still carried an orphaned
  footer after the assistant had reported it fixed; she was right.
- July 2026: reconciled 27 source documents emailed by the division head against a 21-file shared
  folder and the assembled pack; identified the one genuinely missing document (a conflict-of-
  interest declaration) and had it built in the house style.
- 14 July 2026: sent Section 1 of the pack (shareholder and corporate structure) to the division head.
- 15 July 2026, 15:55 SAST: sent the complete pack as a 5.2 MB zip of 13 numbered folders, 40 files
  (31 built, 7 evidence documents from the business, 2 intentional duplicates), with a written note
  that the cyber-security questionnaire was still outstanding. That note is on record.
- July 2026: commissioned a six-slide compliance presentation rebuilt from the division head's own
  content; rejected a first version that had drifted off brief and said so in one line.
- 24 August 2026: delivered a fillable debit-order authority form in the house style (19 fields).
- September 2026: evaluated a compliance SaaS vendor's pilot proposal (11 pages) and its hosting,
  data-protection and backup policy (6 pages); established that nothing had been signed and that
  the documents carried no IP, non-compete, non-circumvention or confidentiality terms. The
  division head declined the vendor on that assessment.
- 21 September 2026: delivered a compliance obligation register of 38 obligations across 7 pillars
  (CIPC 4, SARS 6, FSCA and FAIS 14, POPIA 5, Labour 6, Procurement 2, one to confirm), 3 sheets,
  with only 7 statuses pre-filled because only 7 were verified.
- 21 September 2026: sent a three-document handover of the commercial division's year to the
  incoming division lead; acknowledged the same day.
- 22 September 2026: received the insurer's 24-page due-diligence report (a scan with no text
  layer). Asked the right first question: what was missed, and whose side was it on. Searched her
  own sent mail and established that of the 13 planned section emails only 2 had ever gone (14 and
  15 July), so the complaints section had carried a nil register with no declaration.
- 2 October 2026: requested that the division take over the RM System database (Supabase Pro, USD
  25 a month) from her personal account by 9 October. Followed up 9 October 04:07 with the IT lead
  and a second IT contact copied. Outcome 9 October 11:25: the division head chose to keep it as is
  until it can be migrated safely.
- 3 October 2026: obtained the role confirmations (complaints officer, two key individuals,
  compliance officer, no ombud liaison appointed) and decided the response would go to the division
  head only, not to the second key individual.
- 3 October 2026: uploaded the FSCA qualifying-criteria matrix and prep guide to a dedicated Drive
  folder so the source material survives the session, and set the copyright boundary on a
  third-party study guide (study use only, never into deliverables).
- 8 October 2026: decided the two-email structure (one forwardable evidence pack, one internal) and
  that the response would go as individual files named to the checklist items, not an archive.
- 9 October 2026, 01:49 and 01:50 SAST: sent both emails from Gmail in a browser after Outlook
  failed to show the drafts. The division head forwarded the pack email at 01:51.

## 3. What was built

Each item: what it does, who uses it, state, where it lives, what it is built with, reuse verdict.

1. Due-diligence pack, 13 sections, 40 files. The FSP's evidence set for the insurer. Submitted
   15 July 2026; the division head onward-forwarded, destination not visible. Lives in Gmail sent
   mail (thread `19f660e4670758dd`, attachment "by section" zip, 15 July 15:44, 5.2 MB) and on the
   Mac in the Compliance folder. The HTML sources sat in a local repository with no remote and were
   destroyed by a container reset in September 2026; only the rendered PDFs survive. Built with
   HTML and a CSS print design system, headless Chromium, PyMuPDF for fillable fields. Reuse: the
   31 built documents as templates after stripping entity details throughout; the 7 evidence
   documents (CIPC record, two audit reports, compliance monitoring, two AFS submissions, ISO 27001
   certificate) not at all.

2. Compliance print design system and build chain: `style.css`, `fill.py`, `build.sh`,
   `templates/document.html`. Renders a branded A4 document, injects type-in fields under
   captions and in empty table cells, skips meta-strip labels and captions under signature rules,
   reports per-page fill and writes a PNG of every page. Live. Lives in
   `.claude/skills/<client>-compliance/assets/` and `templates/` on branch
   `claude/compliance-coding-w6pyz3` (folder name carries the client slug). Python 3, pymupdf,
   Chromium. Reuse: as is; contains no client data. Stripped copy in the package.

3. Compliance skill, `SKILL.md` plus `references/fais-citation-map.md` and
   `references/gcoc-complaints.md`. The citation map re-keys the FSCA RE5 qualifying-criteria
   matrix (14 January 2025, version 1) by topic so a citation starts from the regulator's index;
   the complaints reference records General Code of Conduct Part XI ss16 to 19 with the s16 defined
   terms, verified 2 October 2026 against two independent copies of the Code. Live, committed 3
   October (`5ac90f6`), fixes 9 October (`b34f22f`). Reuse: after stripping the entity block in
   SKILL.md and one paragraph in gcoc-complaints.md that names roles. Stripped copy in the package.

4. Four due-diligence response documents, signable, type-in fillable: Nil Complaints Return and
   Declaration (13 rows deriving the reportable figure, 17 fields), Complaints Handling
   Responsibility Schedule (roles, escalation, turnaround), TCF in Complaints Handling Evidence Map
   (six outcomes to controls to documents), POPIA and PAIA Compliance Addendum (data-subject
   rights, s22 notification of both regulator and data subject, version control, dual approval).
   Sent 9 October 2026 as attachments to the pack email. Sources in the session scratchpad, which
   is volatile. Reuse: after stripping; stripped HTML in the package, PDFs excluded.

5. Organogram, one landscape page in the house style, rendered from the FSP's spreadsheet. Sent 9
   October as Annexure B. It is a staff chart (two directors, head of company, general sales
   manager, seven teams, headcount 70), not a shareholder organogram. Reuse: not at all; it is
   personal data of 70 employees.

6. Compliance obligation register, `.xlsx`, 38 obligations, 3 sheets (register, evidence index of
   40 rows, how-to), dropdown statuses, conditional formatting on status and on next-due within 90
   days. Delivered 21 September 2026; on the Mac Compliance folder (16 KB, 21 September 13:31).
   The build script was lost to a reset. Built with openpyxl. Reuse: as is after clearing the 7
   pre-filled statuses and the entity name; the obligations themselves are generic South African.

7. Demo compliance app, single HTML page, six tabs (overview, obligations, people and FAIS,
   evidence, audit trail, where to prove it), three-state theming, clearly marked demo data with
   invented names and masked identity numbers. Live as a private Artifact at
   https://claude.ai/artifact/SqDwiVP6xULd8KZAFkmMkV; local source lost to a reset but the page is
   readable back from the Artifact. Reuse: after stripping brand tokens.

8. Compliance presentation, 6 slides, `.pptx`, rebuilt from the division head's own deck. Delivered
   July 2026; local source lost. Reuse: not at all; client content.

9. Debit order authority, fillable PDF, 19 fields. Delivered 24 August 2026; on the Mac. Reuse:
   after stripping.

10. Repository working memory, `CLAUDE.md` on branch `claude/compliance-coding-w6pyz3`. Records
    the client's deals, policy numbers, premiums, people and roles, the due-diligence findings, the
    dates of everything, and the accuracy protocol. Reuse: not at all as a file; the method
    sections (accuracy protocol, build traps) are reproduced in the package SKILL.md.

11. Unsent Gmail drafts as at 17 October 2026: `r3203196410834962143`, a one-line reply on the pack
    thread meant to carry the 5.2 MB zip that never attached; `r1216228675132162654`, a Supabase
    chase superseded by Anné's own 9 October follow-up. Neither was sent.

12. Related but not built here: the proposal skill `.claude/skills/<client>-proposal/` (merged 28
    July 2026 from the Mac, used for quote-comparison packs) and the two application repositories
    (RM System, Premium Comparison) referenced in CLAUDE.md.

## 4. Proof points

- Assembled and sent a 40-document, 13-section regulatory due-diligence pack for a Category I
  brokerage with 61 registered representatives in 5 working days, 10 to 15 July 2026.
- Of the 40 documents, every one built in this chat scored No Concern in the insurer's report.
  Final scoreboard: 26 No Concern, 4 Limited Concern, 6 Major Concern. All 6 Major were one section.
- Traced all 6 Major Concern findings to a single cause in under an hour by searching sent mail:
  2 of 13 planned section emails had gone, and a nil register went with no declaration.
- Read a 24-page scanned report with no text layer by rendering every page as an image; identified
  that it used two different numbering schemes and contradicted itself on the representative files
  (Limited Concern in the checklist, Major Concern in the narrative), and that it misnamed the FSP
  twice.
- Produced 4 signable documents in one working day (22 September) closing 6 Major Concern findings
  and 3 recommendations; rebuilt the nil declaration on 2 October on the correct provisions
  (ss16 to 19, not s17 as the insurer had cited) after reading the regulator's own matrix.
- Identified that the document submitted twice as a "shareholder organogram" was a 70-person staff
  chart, the probable reason it was recorded as not submitted.
- Caught a separation-of-duties gap: the complaints officer was also a key individual, so
  "escalate to the KI" was not independent; rerouted to the second KI and the compliance officer.
- Built a 38-obligation register across 7 pillars with 7 verified statuses and 31 left honestly
  blank; built a demo app with 100 percent invented personal data.
- Vendor review: 17 pages of vendor documents read; 0 IP, non-compete, non-circumvention or
  confidentiality clauses found; the only NDA reference was for a session never held.
- Build chain hardened by inspection: 3 defects found only by rendering pages (fields covering the
  meta strip, a redaction that turned "80 of 2003" into "8 0 of 2 0 3", stray fields under
  signature lines); 5 traps documented for the next person.
- Worked through 4 container resets that wiped local files, including one that destroyed a
  repository with no remote; after the second, all working memory moved into a committed file.
- Sent the final response at 01:49 and 01:50 on 9 October; the division head forwarded it at 01:51.

## 5. Skills and methods this chat shows

- Primary-source discipline for regulatory citations: Act and section only, never a summary;
  a two-pass build-then-verify rule; the regulator's published qualifying criteria used as the
  index of which provision governs what; refusal to invent a regulator's contact details.
- Evidence reconciliation: knowing the difference between holding a document and having proved
  something to a third party. "A nil position must be declared, not merely shown." Answering in
  the Code's own defined terms (reportable complaint, compensation payment, goodwill payment).
- Reading scanned documents as images; noticing when a report runs two numbering schemes.
- Email forensics with the Gmail API: establishing what was sent, when, with which attachments;
  distinguishing drafts from sent mail; knowing Outlook for Mac does not show API-created drafts.
- Print layout for compliance documents: A4 page rules, break-inside control, keeping signature
  blocks with footers, splitting an oversized section rather than forcing it; verifying by looking
  at rendered pages, not widget counts.
- PDF field injection with PyMuPDF: caption detection by colour and case, geometric detection of
  signature rules, table-cell defaults, and the failure modes of each.
- Judgement calls: not copying the second key individual without instruction; not writing "none"
  for an unappointed function on a regulatory document; not correcting employee-name typos without
  authority; keeping an internal tickbox out of anything forwardable; separating a forwardable
  evidence email from an internal one; stating her own share of a mistake plainly and once.
- Copyright boundary: regulator criteria and statutory text are reusable; a training provider's
  prose is not, and must not enter a repository.
- Working memory kept in a committed file after losing uncommitted work twice; durable source
  material kept in a cloud drive with recorded identifiers.
- Register switching: informal Afrikaans for one reader, formal English for anything forwardable.

## 6. Where I stopped

State as at 17 October 2026, checked against the mailbox.

- The pack email (thread `1a11e470a43f7331`) went 9 October 01:49 with 5 attachments: the four
  response documents and the organogram. The 5.2 MB section zip did not attach. The body says the
  balance of the pack is "enclosed in the archive"; no archive has been sent. The one-line reply
  draft `r3203196410834962143` on that thread is still unsent. The division head replied "Fyi" at
  01:51 (1.08 MB, so he forwarded it with attachments; to whom is not visible from Gmail). First
  action on return: attach the 15 July 15:44 zip to that draft and send, or confirm the division
  head has the July zip already. Do not forward the 15 July email itself; it carries the internal
  checklist.
- The internal email (thread `1a11e4bdc43ebdfc`) went 01:50. No reply as at 17 October. The two
  role decisions (dual-role escalation; ombud liaison placed with the complaints officer), who
  signs which document, who the Information Officer is and whether registration is done, and who
  chases the cyber questionnaire, representative files and backup evidence, are all unanswered.
- The four documents are unsigned. The POPIA addendum has a deliberately blank Information
  Regulator contact block with a "date checked" field.
- Item 3.1 (shareholder organogram) is not closed. Needed from the division head: who holds the
  shares in the FSP, in what percentages, up to the ultimate holding company. Then build a one-page
  ownership diagram in the house style. Never assert the shareholding from memory.
- Supabase: the RM System database remains in Anné's personal account on her card; the 13 October
  debit will have run. The division head deferred migration on 9 October. Draft
  `r1216228675132162654` is superseded and can be deleted.
- Next steps that were agreed in principle and not started: response text for all ten findings
  written to drop into the insurer's blank feedback boxes; a one-page remediation tracker
  (finding, response, owner, evidence, date); chasing emails to IT and HR ready to forward; a
  complaints register template with the s16 categorisation columns; a challenge to the insurer on
  its two errors.
- Earlier offers never taken up: Supabase schema and row-level-security policies for an in-house
  compliance system; written questions to the SaaS vendor.

Check first if returning after six months:

- The repository branch `claude/compliance-coding-w6pyz3` may have been merged, rebased or deleted;
  the skill folder and CLAUDE.md live there. `root-handover` carries this file.
- The Artifact link is private and may have been unpublished.
- The Drive folder identifier for the RE5 material (`1tvxEft5aIhhjiBfhy3f9X8oKvu0IPrGB`, capital I)
  and the three file identifiers inside it may have changed if the folder was moved or re-uploaded.
- The Chromium path in the build script is container-specific; set CHROME to a local binary.
- The FSCA qualifying criteria were version 1 of 14 January 2025; check for a newer version. The
  General Code of Conduct, the 2024 Ombud Council Rules and the Information Regulator's contact
  details all move; re-verify before citing.
- Supabase Pro pricing (USD 25 a month in October 2026) and whether the database was ever migrated.
- People: Anné handed the commercial division to an incoming lead on 21 September 2026; the IT lead
  and the insurer's reviewer may have moved; the division head's role may have changed.
- The session scratchpad is gone; only the repository, OneDrive and the package survive.
- The 15 July zip survives only in Gmail sent mail and on the Mac; confirm both still exist.
- The vendor's pilot proposal was valid for 60 days from issue and has expired.

## 7. What must never be reused from this chat

Kinds and locations only; no values are written here.

- Representatives' personal data: a competence register of 61 representatives with identity
  numbers, examination outcomes and CPD records, inside the 15 July zip in Gmail sent mail and in
  the Mac Compliance folder; also as a standalone spreadsheet in the same folder.
- Employee personal data: the organogram spreadsheet and its rendered PDF, about 70 names with
  internal staff numbers, in the 15 July zip, the Mac folder, the session scratchpad, and attached
  to the 9 October pack email.
- Client policy data in CLAUDE.md on the working branch: client names, policy numbers, premiums,
  vehicle registrations, claims history, a private client's family details, and quote-comparison
  figures for six client files. Never copy that file into another company's work.
- A private client's identity number, used as the password to a current-policy PDF, in a `.docx`
  in the deal folder and in the chat uploads; and quote passwords in a relationship manager's
  28 July email. Delete the uploads; do not carry the docx across.
- Supabase: the anonymous key embedded in the RM System client code in its own repository, and the
  project itself in Anné's personal Supabase account. Rotate the keys if the project is ever
  transferred.
- Anné's own personal data that surfaced in mailbox searches: a tax number and PAYE reference in a
  2022 sent email; home-loan and vehicle-finance correspondence; medical and school account
  statements; bank transaction notifications. All in the personal Gmail.
- The second employer's mailbox contents (client lists, health enrolments, payroll lists) seen only
  because that account was connected; nothing from it belongs to Root Innovations.
- The insurer's due-diligence report (24 pages, uploaded 22 September) and the vendor's two PDFs:
  third-party confidential material. Do not reproduce or redistribute.
- The third-party RE5 study guide (154 pages, in the Drive RE5 folder): copyright, study use only.
- The FSP's logo PNG and brand wordmark: client brand assets.
- The commit trailers on the working branch carry a session URL; that is fine, but the branch
  history names the client in paths and commit messages.

## 8. Lessons

- A nil register is not an answer. Six Major Concern findings came from sending an empty register
  with no signed declaration. Declare, in the regulator's defined terms, and sign it.
- Do not send a zip to a checklist reviewer. The organogram was inside the zip and was recorded as
  not submitted. Send individual files named to the item numbers.
- Check what the item actually asks for. "Shareholder organogram" means ownership, not reporting
  lines. Two submissions of the wrong chart cost a Limited Concern.
- Do not take the auditor's citation on trust. The report said s17; the framework is ss16 to 19,
  and s16 holds the definition that decides what must be reported.
- Commit early. A local repository with no remote was destroyed by a container reset and the HTML
  sources of 31 documents went with it. After the second reset everything went into a committed
  file; the handover you are reading exists because of that rule.
- Render and look. Three field-placement bugs were invisible to counts and obvious on the page. One
  redaction shortcut corrupted body text in a compliance document and was only seen by eye.
- Drafts made through the Gmail API do not appear in Outlook for Mac. A week was lost assuming
  drafts had been deleted. Always open Gmail in a browser.
- The API cannot attach a 5 MB file; the one attachment that mattered was the one that did not go.
  After sending, read the sent message's attachment list before telling anyone it went.
- Flag an outstanding item once, in writing, where it will be found later. The 15 July note about
  the cyber questionnaire was the only thing that showed it was not her omission.
- When one person holds two roles, the escalation route collapses. Write the independent route
  down before a reviewer finds the gap.
- Keep the internal tickbox and the internal email out of anything that can be forwarded. Split
  by audience, not by old versus new.
- Working for a company where a close relative is the decision-maker reads as helping at home. One
  arm's-length engagement is needed before this counts as a track record for Root Innovations.
