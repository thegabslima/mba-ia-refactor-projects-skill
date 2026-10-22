---
name: refactor-arch
description: Audits a backend codebase for architecture, security and quality anti-patterns, prints a severity-ranked report, and - only after the user confirms - refactors it to the MVC pattern and validates that the app still boots and its endpoints still respond. Technology-agnostic (Python/Flask, Node/Express, Java, Go, PHP, ...). Use when the user asks to audit, refactor or restructure a legacy project into MVC, or invokes /refactor-arch.
---

# refactor-arch

Three sequential phases: **1 Analysis -> 2 Audit (pause) -> 3 Refactoring + validation**.
The skill is only a method. All technology knowledge lives in `references/`; read the files named in each phase **before** doing that phase's work.

| File | Used in | Content |
|------|---------|---------|
| `references/project-analysis.md` | Phase 1 | How to detect language, framework, database, domain, architecture level |
| `references/anti-patterns-catalog.md` | Phase 2 | Anti-patterns, detection signals, severity, deprecated APIs |
| `references/report-template.md` | Phase 2 | Exact format of the audit report |
| `references/mvc-architecture.md` | Phase 3 | Target MVC rules and folder layouts per stack |
| `references/refactoring-playbook.md` | Phase 3 | Before/after transformations, one per anti-pattern |

## Ground rules

- Work on the project in the current directory. Never touch files outside it (except `reports/`, see Phase 3 step 1).
- **Phases 1 and 2 are read-only.** Do not edit, create or delete any file until the user confirms at the end of Phase 2.
- Be concrete: every finding needs the real file and exact line range, read from the code, never guessed. Re-open the file if unsure.
- Never invent a stack. If a heuristic does not match, say "not detected" and explain what you checked.
- Never print "✓" for something you did not actually run and observe.
- Do not add dependencies unless there is no standard-library/framework alternative; if you add one, list it in the final summary.

## Phase 1 - Project analysis

1. Read `references/project-analysis.md`.
2. Enumerate source files (ignore dependency, build, VCS and cache folders listed in that file) and count them and their lines.
3. Detect language, framework (+ version), dependencies, database/ORM, domain, current architecture level, entry point, and how to run it.
4. Print exactly this block (fill every field):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language>
Framework:     <framework + version>
Dependencies:  <main runtime deps>
Domain:        <what the app does, 1 line>
Architecture:  <level + 1 line justification>
Source files:  <N> files analyzed (~<L> lines)
DB tables:     <tables/collections, or "none">
Entry point:   <file / run command>
================================
```

## Phase 2 - Architecture audit

1. Read `references/anti-patterns-catalog.md` and `references/report-template.md`.
2. Read **every** source file fully. For each catalog entry, apply its detection signals; record each hit with file + line range.
3. Classify severity strictly with the catalog (CRITICAL / HIGH / MEDIUM / LOW). Check the deprecated-API table for the detected stack.
4. Print the report using the template: summary counts, then findings **ordered CRITICAL -> HIGH -> MEDIUM -> LOW**, then the total. Group repeated occurrences of one anti-pattern into one finding listing all locations.
5. End with the confirmation prompt and **stop**. Do not continue until the user answers:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

If the answer is not an explicit yes, make no changes. Offer to save the report only.

## Phase 3 - Refactoring

Run only after an explicit "y".

1. **Save the audit.** Write the Phase 2 report to `reports/audit-<project-folder-name>.md` at the repository root (git top-level; else the current directory). This is the only file written before the code changes.
2. **Baseline.** Install dependencies, boot the original app, call every route found in Phase 1 (happy path + one error case each) and record status code + JSON keys. If the app cannot boot, record why. Stop it afterwards.
3. **Plan.** Read `references/mvc-architecture.md` and pick the layout for the stack. Adapt to the architecture level found in Phase 1 (flat monolith -> create all layers; already layered -> only move/fix what is wrong, do not rename things for taste). Keep the original run command working.
4. **Transform.** Read `references/refactoring-playbook.md`. Apply patterns in this order so the app stays runnable: config/secrets -> database access + models -> controllers -> routes/views -> centralized error handling -> entry point (composition root) -> cleanup (dead code, constants, deprecated APIs). Delete the old files that were fully replaced.
5. **Preserve the public contract**: same URLs, HTTP methods, status codes and JSON shapes. The only allowed deviations are security fixes (e.g. no password hash or secret in a response, protected admin routes, SQL injection removed). Keep a list of every deviation.
6. **Validate** (all required):
   - install dependencies and boot the app; capture startup output; it must run without errors;
   - call every endpoint again and compare with the baseline; explain each difference;
   - re-run the catalog detection signals over the new code; list any anti-pattern still present (do not claim "zero" unless a search proves it);
   - if something fails, fix and re-run (max 3 rounds), then report honestly what still fails.
7. Print this summary:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<tree of the new layout>

## Changes
<one line per playbook pattern applied>

## Deviations from the original contract
<list, or "none">

## Validation
  ✓/✗ Application boots without errors
  ✓/✗ <N>/<M> endpoints respond as in baseline
  ✓/✗ Anti-patterns remaining: <none | list>
================================
```

Do not commit or push unless the user asks.
