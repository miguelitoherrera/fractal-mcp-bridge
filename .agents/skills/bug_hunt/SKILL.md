---
name: bug_hunt
description: Protocols for hunting and reporting bugs across categories (functional, KISS, DRY, tests)
---

# Bug Hunt Protocol

When asked to **"go on a bug hunt"**, perform an all-encompassing search for bugs within the repository across the following four categories:

1. **Functional Bugs (Most Important):** Look for logic errors, off-by-one errors, null/undefined issues, race conditions, incorrect conditionals, missing edge cases, wrong variable usage, broken control flow, and any code that simply won't work as intended. This is by far the most important category.
2. **KISS Violations:** Overly complex solutions where simpler ones exist. Unnecessary abstractions, premature generalizations, or convoluted logic.
3. **DRY Violations:** Duplicated logic that should be extracted. Copy-and-pasted code with minor variations.
4. **Missing Tests:** New functionality or bug fixes lacking appropriate test coverage.

## Reporting Format
DO NOT report:
* Code formatting or style issues (handled automatically with Ruff)
* Minor type issues (handled automatically with Ruff/Mypy)
* Nitpicks that don't affect correctness or maintainability.

For each issue found, report:
* **File and line number**
* **Severity:** critical/high/medium/low
* **Category:** the items 1 thru 4.
* **Description:** what the issue is and why it matters.
* **Suggestion:** how to fix it.

Group the structured list by severity (critical first, then high, then medium, then low). Report all issues observed.
