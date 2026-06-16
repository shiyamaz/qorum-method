# Agent rules: The Qorum Method

Drop this into your repo so AI agents follow the gate. Works as `AGENTS.md` (Codex and others),
or copy the contents into `CLAUDE.md` (Claude Code) or `.cursor/rules/` (Cursor).

---

## Roles

- **Implementer** — branches, implements, opens PRs. Never approves its own work. Never merges a High-risk PR.
- **Reviewer** — reviews and approves **Low/Medium** PRs only. Must be a *different* role than the Implementer. Never approves High. Never proposes new architecture. Never implements.
- **Approver** — a human. The only role that may clear **High**.

**Invariant (non-negotiable): the Reviewer may clear Low and Medium; only the human Approver clears High.**

## Risk tiers (classify every PR before merge)

Read `.qorum.yml` for this repo's thresholds and protected paths. Default logic:

- **🟢 Low** — `changed_files ≤ 5`, no deletions, no binaries, no protected path, low-risk label → self-merge after review.
- **🟡 Medium** — `changed_files ≤ 20`, `deletions ≤ 3`, no protected path → review, then notify, then wait the cooldown, then self-merge.
- **🔴 High** — `>20` files, `≥4` deletions, `>1000` diff lines, **any protected path**, binaries, or a critical label → **human Approver required. Do not self-merge.**

**When unsure, escalate — never downgrade: Low↔Medium → Medium, Medium↔High → High.**

**Scope:** this gate is per-change. Cumulative risk across changes — several Low changes hitting the same secret, customer, release, or budget — is out of scope from a single diff; escalate that at the portfolio level (a human reviewing everything in flight), not here.

## Self-merge preconditions (Low & Medium only)

All of: Reviewer approved (≥1, different role than author) · no unresolved change-requests · squash merge · delete branch on merge · checks pass.

## Reviewer prompt (use verbatim when asking an AI to review)

```
Review this PR. Look ONLY at:
- diff validity and internal consistency
- violations of this repo's stated rules / risk policy
- risk tier (Low / Medium / High) per .qorum.yml
- regression risk
- inconsistency between issue, PR description, and code

Output rules:
- bullet points only, under ~300 words
- classify the risk tier explicitly
- do NOT propose new designs or "you could also add..." ideas
- if the diff exceeds the review-size cap, ask for a summary or a split first
```

### Signs the Reviewer has drifted (re-assert the constraints if you see these)
- long alternative-design proposals in a review
- rising "you could also add…" suggestions
- output routinely over ~300 words
- references to code unrelated to the diff
