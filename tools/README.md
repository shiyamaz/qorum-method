# tools/ — the mechanical gate

`qorum_classify.py` is the **code layer** of Qorum: it reads the signals that live in a
git diff and prints the risk tier, with the reasons that set it. It's the small "it
actually runs" piece — the `.qorum.yml` you copied finally has a consumer.

```bash
pip install pyyaml
python3 tools/qorum_classify.py                       # vs merge-base with origin/main
python3 tools/qorum_classify.py HEAD~1                 # vs a specific base
python3 tools/qorum_classify.py --config .qorum.yml --labels docs,priority-low
```

Output is one of `🟢 LOW`, `🟡 MEDIUM`, `🔴 HIGH`, the verdict (self-merge / cooldown /
human required), and the reasons. Exit code is `2` for HIGH (so CI can fail-closed) and
`0` otherwise.

## What it does and doesn't read

It reads from the diff: files changed, deletions, total lines, binaries, and whether any
**protected path** is touched. It does **not** read PR labels — those aren't in a diff.
Pass them with `--labels` to apply label rules; without them, a change that's
*Low by size* is reported as **Medium**, because the gate escalates when it can't confirm
a lower tier (bias: never downgrade).

## Scope

This is the **mechanical** gate — tiers here are arithmetic (counts and paths), so a CLI
fits. For **decisions that aren't code** (strategy, hiring, pricing, a customer doc) there
is no diff to count; the tier is a judgment. Use the Qorum skill
([`../skill/qorum/SKILL.md`](../skill/qorum/SKILL.md)) for those.

This script is intentionally dependency-light (PyYAML only) and unpackaged — copy it,
read it, adapt it. It is not a substitute for platform enforcement; for the hard cases,
also wire in branch protection (see [`../docs/identity-hardening.md`](../docs/identity-hardening.md)).
