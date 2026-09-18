# User Stories: Zip Multiple Jupyter Notebooks for Sharing

**Area:** Platform
**Source:** ClickUp task [869ek92hu](https://app.clickup.com/t/869ek92hu) — `Zip_notebooks.ipynb`, written by [[Hendrie_Kritzinger|Hendrie]], awaiting feedback from [[Donovan|Don]]
**Author:** Chess | **Date:** 2026-08-27
**Status:** Draft — for script review

---

## Context
- **Product:** Internal script for the Customer Success / Data Science team
- **Target user:** CS data scientist (e.g., [[Hendrie_Kritzinger|Hendrie]]) who needs to hand off a set of notebooks to another user
- **User JTBD:** Share multiple related Jupyter notebooks as one file instead of attaching each separately

These stories are written against the actual script attached to the ClickUp task (reviewed 2026-08-28), not a guessed spec.

---

## Story 1: Bundle a Hardcoded List of Notebooks into a Single Zip Archive

**As a** CS data scientist,
**I want to** list the notebook filenames I want bundled and run the script,
**So that** I get a single timestamped zip file containing them, ready to share instead of sending each notebook separately.

### INVEST Check
- [x] **Independent** — Self-contained script functionality, no other stories required
- [x] **Negotiable** — Whether the file list should stay hardcoded vs. parameterized is open for discussion
- [x] **Valuable** — Removes the manual, error-prone step of attaching notebooks one by one
- [x] **Estimable** — Small, well-scoped script behavior
- [x] **Small** — Fits well within a single review/fix cycle
- [x] **Testable** — Clear pass/fail criteria below

### Acceptance Criteria

**AC1: Happy path — bundle a valid notebook set**
Given `NOTEBOOK_FILES` contains two or more filenames that exist in the current working directory,  
When the script runs,  
Then a single `.zip` file is created in the current working directory containing each listed file, unmodified, and each added file is printed to output.

**AC2: Output naming and location**
Given the script has successfully bundled the notebooks,  
When the zip file is written,  
Then it is named `notebooks_YYYYMMDD_HHMMSS.zip` (current timestamp) and saved in the same directory the script is run from — this is fixed, not configurable.

**AC3: Missing file is skipped with a warning**
Given a filename in `NOTEBOOK_FILES` does not exist in the current working directory,  
When the script runs,  
Then it prints a "Warning - not found, skipping" message naming the missing file(s), and continues bundling the remaining valid files rather than stopping.

### Edge Cases (confirmed against the script)
- Only one filename in the list → zips fine as a single-file archive; no minimum-count check exists
- Two runs within the same second → timestamp collision is theoretically possible but extremely unlikely in practice, since granularity is to the second
- `NOTEBOOK_FILES` is empty → **not handled** — see Story 2, AC1

### Technical Notes
- File selection is a hardcoded Python list edited directly in the notebook cell — there's no CLI argument, folder scan, or UI. Each new share requires opening and editing the script.
- No exception handling around the zip write itself (e.g., disk full, permission denied) — an I/O error would raise an unhandled Python traceback.

### Out of Scope
- Sending/transmitting the zip to the recipient (email, upload, etc.) — this story covers bundling only
- A UI, CLI, or self-serve interface — that would be a separate enhancement, not part of this script as written

---

## Story 2: Gaps to Address Before Sign-Off

**As a** [[Donovan|Don]] reviewing this script,
**I want to** know where the current implementation can silently produce a wrong or incomplete result,
**So that** I can decide whether these gaps block sign-off or are acceptable for a first internal-use version.

### INVEST Check
- [x] **Independent** — These are review findings, not new functionality requests
- [x] **Negotiable** — Don and [[Hendrie_Kritzinger|Hendrie]] can decide which of these are worth fixing now vs. later
- [x] **Valuable** — Prevents someone silently sharing an incomplete or unintended zip
- [x] **Estimable** — Each finding is a small, isolated fix
- [x] **Small** — Individually trivial changes
- [x] **Testable** — Clear pass/fail criteria below

### Findings (Acceptance Criteria framed as "should" — none of these currently hold)

**AC1: Empty file list should not silently produce an empty zip**
Given `NOTEBOOK_FILES` is an empty list,  
When the script runs,  
Then it currently creates an empty `.zip` with no warning or error — **this should instead print a clear "no files specified" message and skip zip creation.**

**AC2: Non-notebook files should be flagged**
Given `NOTEBOOK_FILES` includes a filename that isn't a `.ipynb` (e.g., a stray `.csv`),  
When the script runs,  
Then it currently zips it without complaint — **this should either warn that a non-notebook file was included, or be an accepted, intentional behavior if the script is meant to zip any file type (worth confirming with [[Hendrie_Kritzinger|Hendrie]], since the task name implies notebooks specifically).**

**AC3: Duplicate filenames should not produce a malformed archive**
Given `NOTEBOOK_FILES` contains the same filename twice,  
When the script runs,  
Then it currently writes two entries with the same `arcname` into the zip — **this should be deduplicated or flagged, since some zip tools handle duplicate entries unpredictably.**

### Technical Notes
- None of the above cause the script to crash today — they're silent correctness gaps, not bugs that surface an error
- Recommend wrapping the `zipfile.ZipFile` write loop in a try/except so a mid-run I/O failure reports a clear message instead of an unhandled traceback

### Out of Scope
- Retry logic or automatic re-fetch of missing files
- Logging/telemetry beyond console output

---

## Story Dependencies

```
Story 1 (documents current behavior) ──→ Story 2 (findings against that behavior)
```

## Suggested Review Ordering
1. Story 1 — confirm this matches what [[Hendrie_Kritzinger|Hendrie]] intended (especially the hardcoded file list — is that acceptable for v1?)
2. Story 2 — decide with [[Hendrie_Kritzinger|Hendrie]] which findings block sign-off vs. can ship as-is for internal use

---

## Related Context
- **Script reviewed:** `Zip_notebooks.ipynb`, attached to [ClickUp task 869ek92hu](https://app.clickup.com/t/869ek92hu)
- **Related people:** [[Hendrie_Kritzinger|Hendrie]] (author), [[Donovan]] (reviewer)
