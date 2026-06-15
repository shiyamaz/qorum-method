# Optional: hardening roles into identities

The gate works as a *convention* — roles and tiers your agents and you agree to follow. That's enough
to start, and you should start there. But prose discipline is breakable: at 11pm, "the Implementer
doesn't approve its own work" is one keystroke from being ignored.

When you want the gate to be *enforced* rather than *agreed*, map the three roles onto separate
identities and let the platform refuse the violations for you.

## The principle

| Role | Identity | Platform enforcement |
|---|---|---|
| Implementer | A bot/agent account (e.g. `you-impl`) | Write access; **cannot** approve its own PR (GitHub forbids self-approval) |
| Reviewer | A *separate* account (e.g. `you-review`) | Write access; its approval satisfies "Required approvals: 1" |
| Approver | You (human owner) | The only Admin; the only one who can merge High / bypass |

Because the Implementer and Reviewer are different accounts, "the author can't approve their own work"
stops being a rule you remember and becomes a thing the platform enforces.

## GitHub branch protection (works on free tier)

On `main`, a ruleset with:

- **Require a pull request before merging** — ON
- **Required approvals** — 1 (satisfied by the Reviewer identity)
- **Dismiss stale approvals when new commits are pushed** — ON (re-review after fixes)
- **Require conversation resolution before merging** — ON
- **Block force pushes** — ON
- **Block deletions** — ON
- **No bypass actors** initially — apply the rules to everyone, including yourself, until you trust them

Keep **Admin** on the human only. If an agent account could edit the ruleset, the whole gate is
advisory again.

## Local identity separation

Separate clones (or separate auth configs) per identity avoid cross-contaminating commits:

- distinct SSH keys / host aliases per identity (`~/.ssh/config`)
- per-clone `git config user.name/email` matching each account's verified email (so commits attribute
  correctly and don't show up "unverified")
- per-clone CLI auth (e.g. `GH_CONFIG_DIR` for the GitHub CLI), pinned with `direnv` so you can't
  forget to switch

## How far to go

- **Solo, low stakes:** roles-as-convention only. Don't bother with extra accounts.
- **Solo, real stakes (secrets, deploys, money):** add the Reviewer identity + branch protection. This
  is the high-leverage step — it makes self-approval *impossible*, not just discouraged.
- **Small team:** same, plus map real teammates onto the Approver role.

Start at convention. Harden the day a near-miss scares you — and it will.
