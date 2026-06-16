# What Qorum looks like in practice

The README explains the gate in the abstract. This page is the concrete version: what the gate is actually *for*, and what happened when this repo's own gate was run on itself.

## What it's for (the shape of the problem)

You're moving fast with AI. An agent opens a change, another agent reviews it, you merge. Most of the time that's fine — a typo fix, a copy tweak, a small refactor. The gate's whole job is to *not* slow those down.

The problem is the small fraction that **isn't** fine — and looks identical on the way in:

- a one-line change to a CI workflow that can read your secrets
- a "quick" edit to how an API key gets loaded
- a dependency bump that quietly pulls in something new
- a 1,500-line refactor the reviewer only skimmed

To a fast AI reviewer, all of these arrive as confident green checkmarks. Qorum's answer isn't "review harder." It's: **classify every change by risk, let the safe ones flow, and make the dangerous ones — anything touching CI, secrets, dependencies, migrations, or anything irreversible — stop and wait for a human.** The reviewer AI is not allowed to clear those — by rule, and with branch protection, it can't.

That's the whole thing: **the safe majority moves at AI speed; the risky few can't be waved through.**

## What actually happened in this repo (the gate, on itself)

This repo was built by the same setup it describes — one AI implements, a second AI reviews under hard constraints, a human approves — so it was pointed at itself. Three rounds, in the open:

**Round 1 — the gate had a blind spot.** The reviewer AI checked the gate's own rules and found a case that fell through entirely: a change deleting exactly 4 lines matched *no* tier. "Low" required zero deletions, "Medium" allowed up to 3, "High" only triggered at 5 or more. Four was unclassified — a hole in a tool whose entire job is classification. The author hadn't noticed. Fixed by making High catch anything past Medium's limit. → commit [`c873605`](https://github.com/shiyamaz/qorum-method/commit/c873605)

**Round 2 — the docs were right, the config wasn't.** The README said large diffs and dependency files are High-risk. But the actual `.qorum.yml` — the file people copy — was missing the line-count threshold and several dependency manifests. Anyone copying the config would have had weaker protection than the docs promised. Fixed by putting the rules into the file people actually use. → commit [`c540b95`](https://github.com/shiyamaz/qorum-method/commit/c540b95)

**Round 3 — and where the human said stop.** The reviewer kept going, now pushing to soften every confident sentence into a hedge. Some of that was right — a made-up "80% / 20%" statistic got cut. Some of it was the reviewer sanding the voice off an opinionated doc. The human took the honest fixes and declined the rest. That call — *when AI review stops being worth following* — is exactly the kind of thing the gate reserves for a person. → commit [`6b4804a`](https://github.com/shiyamaz/qorum-method/commit/6b4804a)

The point isn't that the gate is perfect. It's that the blind spots were found, named, and fixed in the open — and the last word stayed human.

## The honest caveat

The code gate above is the part that's actually been exercised. Pointing the same three tiers at non-code decisions — strategy, hiring, pricing — is the same *shape*, but it hasn't been exercised the same way (see [`beyond-code.md`](beyond-code.md)). Use the structure; derive your own tiers from what's genuinely reversible in your work.
