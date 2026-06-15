# The Qorum Method

> **A governance-first approach to AI-assisted software development.**
> Let an AI implement and an AI review — but bound what can merge without a human.

*Qorum, not quorum.* Consensus is the mechanism; **governance is the point.** The dropped letter is deliberate — this isn't about getting AIs to agree, it's about deciding, per change, how much autonomy is safe.

**Status:** v0. Tool-agnostic; works with Claude Code, Cursor, Codex, or plain humans.

---

## The problem

You ship with AI agents now. One writes the code, maybe another reviews it. That is fast — and quietly dangerous, because the two failure modes feed each other:

1. **You are the only human.** A solo dev has no second pair of eyes. "Just review your own PRs" is the discipline everyone says they have and nobody keeps at 11pm.
2. **An AI reviewer that can approve anything is worse than no reviewer.** If your automated reviewer rubber-stamps a `.github/workflows` change, a secret-handling tweak, or a 2,000-line refactor, you have *manufactured* the feeling of review without the substance of it.

The usual answers are "add a human reviewer" (you don't have one) or "trust the AI" (you shouldn't, uniformly). The Qorum Method is the third answer: **decide, per change, how much autonomy is safe — and make the unsafe cases require a human sign-off — and, once you harden it, physically so.**

## The idea in one paragraph

Separate three **roles** — Implementer, Reviewer, Approver — and classify every change into a **risk tier**. Low-risk changes self-merge after an automated review. Medium-risk changes self-merge after review plus a short cooldown and a notification. High-risk changes — large diffs, protected paths, anything that can hurt you — **must not merge without the human Approver**, and the automated Reviewer is *not allowed to clear them*. The gate is the part you can't talk yourself out of at 11pm.

## The three roles

| Role | Who can hold it | May do | May **not** do |
|---|---|---|---|
| **Implementer** | An AI agent, or you | Branch, implement, open PR | Approve its own work; merge High-risk |
| **Reviewer** | A *different* agent (or you) | Review, request changes, approve **Low/Medium** | Approve **High**; propose new architecture; implement |
| **Approver** | A human, always | Approve/merge **any** tier, especially High | — |

The single load-bearing invariant: **the Reviewer may clear Low and Medium, but only the human Approver clears High.** Everything else is detail you can tune.

> Roles are not accounts. You can run all three as yourself with discipline, or map them to separate identities (e.g. distinct GitHub accounts + branch protection) for hard enforcement. See [`docs/identity-hardening.md`](docs/identity-hardening.md). Start with roles; harden later.

## The risk gate

Three tiers. Defaults below — tune them in [`examples/qorum.yml`](examples/qorum.yml).

### 🟢 Low — self-merge after review
All of:
- `changed_files ≤ 5`, no deletions, no binaries
- touches **no protected path**
- carries a low-risk label (`docs`, `chore`, `priority-low`, …)

### 🟡 Medium — self-merge after review + cooldown + notify
- `changed_files ≤ 20`, `deletions ≤ 3`
- touches normal implementation code (no protected paths)
- → Reviewer approves → notify your channel → wait out a short cooldown (e.g. 60s, your STOP window) → merge

### 🔴 High — human Approver required (self-merge forbidden)
Any of:
- `changed_files > 20`, `deletions ≥ 4` (anything past Medium's limit), or `diff_lines > 1000`
- touches a **protected path** (see below)
- adds binaries; carries a critical label (`priority-critical`, `breaking`, `migration`, …)

**Protected paths** are the things a wrong change can't be undone from. Sensible defaults:
`.github/workflows/**` · CI/CD config · `**/*.env`, `*.key`, `*.pem`, anything auth/secret · dependency manifests (`package.json`, `requirements.txt`, lockfiles) · DB migrations · infra-as-code · `.gitignore` · **the gate config itself**. The list in [`examples/qorum.yml`](examples/qorum.yml) is a starting point — extend it with your stack's equivalents.

> **When in doubt, escalate — never silently downgrade.** Unsure between Low and Medium → Medium; unsure between Medium and High → High. The bias is always toward the safer tier.

## The Reviewer is a checker, not an architect

If you use an AI as the Reviewer, constrain it — an unconstrained reviewer drifts into redesigning your code, which is both expensive and a way to *miss the actual review*. Bound it to a fixed checklist and short output:

1. Is the diff valid and self-consistent?
2. Does it violate a stated rule (your conventions / risk policy)?
3. What risk tier is this? (Low / Medium / High)
4. Regression risk?
5. Inconsistency between the issue, the PR description, and the code?

No new design. No "you could also add…". No essays. (See the drop-in prompt in [`AGENTS.md`](AGENTS.md).)

## Self-merge preconditions (Low & Medium)

Before an Implementer self-merges, **all** of:
- Reviewer has approved (≥1), by a *different* role than the author
- No unresolved change-requests
- Squash merge only
- Delete the branch on merge
- Checks pass

## Quickstart

Qorum is a convention your agents follow, not a program you install — nothing runs on its own. Enforcement is your agents' compliance, plus (optionally) branch protection.

1. Copy [`AGENTS.md`](AGENTS.md) into your repo (or its contents into `CLAUDE.md` / `.cursor/rules/`). This teaches your agents the roles, the gate, and the Reviewer checklist.
2. Copy [`examples/qorum.yml`](examples/qorum.yml) to `.qorum.yml` at your repo root and edit the thresholds + protected paths.
3. (Optional, recommended once it's working) Enforce in the platform, not just in prose: branch protection requiring 1 approval, dismiss-stale-approvals, block force-push. See [`docs/identity-hardening.md`](docs/identity-hardening.md).

That's it. You now have a reviewer who moves fast on the safe 80% and is barred from waving through the dangerous 20% — by rule now, by branch protection once you add it.

## Why this exists

This was extracted from a one-person company that runs its development as a small AI org: one agent implements, a second reviews under hard constraints, and a human only sees the exceptions. The method wasn't designed on a whiteboard — it's what was left standing after the failures. See [`docs/rationale.md`](docs/rationale.md).

## License

MIT © 2026 Shigeki Yamazaki. See [`LICENSE`](LICENSE).
