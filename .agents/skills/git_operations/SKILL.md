---
name: git_operations
description: Formatting Pull Request summaries and branch naming conventions
---

# Git Operations & Repository Skills

## 📝 Pull Request & Diff Summaries
When summarizing a git diff for a PR, keep summaries brief, highly readable, and structured into exactly two sections, followed by a one-liner commit message. Wrap the entire PR summary output inside a markdown code block.

```markdown
# Reason for Change
*(Brief and human readable explanation of why the change was necessary)*

# Changes Made
*(Bulleted list of exact changes that are human-readable)*

**Suggested Commit:** `brief description`  
**Suggested Branch Name:** `branch name`
```

## Refactoring vs. Behavior Changes
Never mix behavior changes with refactoring when touching the code.
