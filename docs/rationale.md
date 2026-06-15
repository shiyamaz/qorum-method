# Why the Qorum Method exists

This isn't a framework someone designed on a whiteboard and then looked for a use for. It's the
residue of running a one-person company as a small AI development org for months, and watching where
things actually broke.

## The setup

One human. Several AI agents. The temptation, when you're solo, is one of two extremes:

- **Be the bottleneck.** Review and merge everything yourself. Safe, but then the second agent that
  "reviews" your code is theater — you're still the only judgment in the loop, and you're tired.
- **Trust the machine.** Let an AI implement and an AI approve, end to end. Fast, until the day an
  automated reviewer cheerfully approves a change to the CI config, the secret-handling path, or a
  thousand-line refactor it didn't really read.

Both fail. The first wastes the whole point of having agents. The second manufactures the *feeling*
of review without its substance — which is more dangerous than no review, because it lowers your guard.

## The thing that was left standing

What survived contact with reality was narrow and boring — which is what makes it hard to wriggle out of:

1. **Roles, not vibes.** The one who writes is not the one who clears. Even if both are "me," the
   separation has to be structural, because the author is the worst judge of their own change.

2. **Risk is not uniform — so autonomy shouldn't be either.** A typo fix and a migration are not the
   same event. Granting them the same amount of "the AI can just merge this" is the actual mistake.
   The gate's whole job is to spend autonomy where it's cheap and withhold it where it's expensive.

3. **The reviewer's power must be bounded by what it can clear.** An AI reviewer that can approve a
   protected-path change is not a reviewer; it's a liability with a green checkmark. So: it may clear
   the safe tiers and is *structurally forbidden* from clearing the dangerous one. The human stays in
   the loop precisely — and only — where it matters.

4. **The bias is always toward the safer tier.** When in doubt, escalate. The cost of an unnecessary
   60-second cooldown is nothing. The cost of a wrongly-Low'd secret change can be unrecoverable.

## The honest part

Most "how I work with AI agents" writing is a highlight reel — the wins, the speedups, the clever
prompt. The gate comes from the other side: the changes that *shouldn't* have merged and almost did.
It exists because the failures were specific and repeatable, and a rule you can't argue yourself out
of at 11pm is worth more than a principle you'll forget.

If you take one thing: **don't ask your AI reviewer to be trustworthy. Bound what it's allowed to
wave through, and the trust question stops mattering.**
