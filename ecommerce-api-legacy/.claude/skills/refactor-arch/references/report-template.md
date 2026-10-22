# Audit report template (Phase 2)

Print the report exactly in this structure. Descriptions, impacts and recommendations are written in Portuguese (pt-BR); headings and severity labels stay in English.

````
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <folder name>
Stack:   <language> + <framework>
Files:   <N> analyzed | ~<L> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <AP-id> <anti-pattern name>
File: <path>:<start>-<end>   (several locations: one "File:" line each, or "a:10, b:22-30")
Description: <what is wrong, citing the concrete code (function/variable names)>
Impact: <consequence for security / maintainability / performance>
Recommendation: <fix + playbook pattern, e.g. "P2 - queries parametrizadas">

### [HIGH] ...
### [MEDIUM] ...
### [LOW] ...

## Deprecated APIs
<only if found; each is also a finding above. Otherwise: "No deprecated APIs detected (checked: ...)".>

================================
Total: <n> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
````

## Rules

1. Order: all CRITICAL, then HIGH, MEDIUM, LOW. Inside a level, most impactful first.
2. Every finding has `File:` with a real path and exact line range (`app.py:7-8`, a single line is `app.py:7`). Lines refer to the code **before** refactoring.
3. One finding per anti-pattern; list all locations of that pattern inside it.
4. Summary counts must equal the number of findings per level and the final total.
5. Minimum bar for a useful audit: >= 5 findings with at least one CRITICAL or HIGH. If fewer are found, re-read the files with the catalog signals again before concluding.
6. No finding without evidence in the code. Do not pad the list.
7. The last line is the confirmation prompt; nothing is modified until the answer is yes.
