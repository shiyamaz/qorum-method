#!/usr/bin/env python3
"""qorum-classify — classify a change's risk tier from a git diff and .qorum.yml.

This is the *mechanical* gate (the code layer): it reads the signals that live in a
diff — files changed, deletions, total lines, and whether any protected path is
touched — and prints the tier with the reasons that set it.

It does NOT read PR labels (those aren't in the diff). Pass them with --labels if you
want label rules applied; otherwise a "Low-by-size" change is reported as Medium,
because the gate escalates when it can't confirm a lower tier.

For non-code decisions (strategy, hiring, pricing) there is no diff to count — use the
Qorum skill (../skill/qorum/SKILL.md) for those; classification there is judgment.

Usage:
    python3 tools/qorum_classify.py [BASE_REF] [--config .qorum.yml] [--labels docs,priority-low]

BASE_REF defaults to the merge-base with origin/main, falling back to HEAD~1.
Requires PyYAML (pip install pyyaml).
"""
import argparse
import fnmatch
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("qorum-classify needs PyYAML:  pip install pyyaml")


def git(*args, required=False):
    """Run a git command. If `required` and it fails, exit non-zero (fail-closed)."""
    p = subprocess.run(("git",) + args, capture_output=True, text=True)
    if p.returncode != 0:
        if required:
            sys.exit(
                f"git {' '.join(args)} failed (rc={p.returncode}): {p.stderr.strip()}\n"
                "refusing to classify (fail-closed)."
            )
        return ""
    return p.stdout.strip()


def default_base():
    for cand in ("origin/main", "main"):
        mb = git("merge-base", "HEAD", cand)
        if mb:
            return mb
    return git("rev-parse", "HEAD~1") or "HEAD"


def path_matches(path, pattern):
    # Treat ** as * so simple globs work with fnmatch; also match the basename.
    flat = pattern.replace("**/", "").replace("/**", "").replace("**", "*")
    return fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, flat) or \
        fnmatch.fnmatch(path.split("/")[-1], flat)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base", nargs="?", help="base ref (default: merge-base with origin/main)")
    ap.add_argument("--config", default=".qorum.yml")
    ap.add_argument("--labels", default="", help="comma-separated PR labels")
    args = ap.parse_args()

    try:
        cfg = yaml.safe_load(open(args.config)) or {}
    except FileNotFoundError:
        sys.exit(f"config not found: {args.config}")

    base = args.base or default_base()
    labels = {l.strip() for l in args.labels.split(",") if l.strip()}

    numstat = git("diff", "--numstat", base, "HEAD", required=True)
    if not numstat:
        print(f"No changes vs {base}.")
        return

    files, adds, dels, binary, touched = [], 0, 0, False, []
    protected = cfg.get("protected_paths", [])
    for line in numstat.splitlines():
        a, d, path = (line.split("\t") + ["", "", ""])[:3]
        files.append(path)
        if a == "-" or d == "-":
            binary = True
        else:
            adds += int(a or 0)
            dels += int(d or 0)
        if any(path_matches(path, p) for p in protected):
            touched.append(path)

    diff_lines = adds + dels
    low = cfg.get("tiers", {}).get("low", {})
    med = cfg.get("tiers", {}).get("medium", {})
    crit = set(cfg.get("critical_labels", []))
    low_lbls = set(cfg.get("low_risk_labels", []))

    reasons, tier = [], None

    # --- High triggers -------------------------------------------------
    if touched:
        tier, reasons = "HIGH", [f"protected path touched: {', '.join(sorted(set(touched)))}"]
    elif binary:
        tier, reasons = "HIGH", ["binary file added/changed"]
    elif labels & crit:
        tier, reasons = "HIGH", [f"critical label: {', '.join(labels & crit)}"]
    elif len(files) > med.get("max_changed_files", 20):
        tier, reasons = "HIGH", [f"{len(files)} files > medium limit {med.get('max_changed_files', 20)}"]
    elif dels > med.get("max_deletions", 3):
        tier, reasons = "HIGH", [f"{dels} deletions > medium limit {med.get('max_deletions', 3)}"]
    elif diff_lines > med.get("max_diff_lines", 1000):
        tier, reasons = "HIGH", [f"{diff_lines} diff lines > medium limit {med.get('max_diff_lines', 1000)}"]

    # --- Low (only if it clearly qualifies) ----------------------------
    if tier is None:
        low_ok = (
            len(files) <= low.get("max_changed_files", 5)
            and dels <= low.get("max_deletions", 0)
            and diff_lines <= low.get("max_diff_lines", 1000)
        )
        needs_label = low.get("requires_low_risk_label", True)
        has_low_label = bool(labels & low_lbls)
        if low_ok and (not needs_label or has_low_label):
            tier, reasons = "LOW", [f"{len(files)} files, {dels} deletions, {diff_lines} lines; no protected path"]
        elif low_ok and needs_label and not has_low_label:
            tier = "MEDIUM"
            reasons = ["size is Low-eligible, but no low-risk label confirmed → escalated (bias: never downgrade)"]

    # --- Medium (the default) ------------------------------------------
    if tier is None:
        tier, reasons = "MEDIUM", [f"{len(files)} files, {dels} deletions, {diff_lines} lines; within medium limits"]

    icon = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}[tier]
    verdict = {
        "LOW": "self-merge after review",
        "MEDIUM": "review → notify → cooldown → self-merge",
        "HIGH": "human Approver required — self-merge forbidden",
    }[tier]

    print(f"{icon} {tier}  ({verdict})")
    print(f"   base: {base}")
    for r in reasons:
        print(f"   - {r}")
    if not labels:
        print("   note: labels not provided (--labels); label rules not applied")
    sys.exit(2 if tier == "HIGH" else 0)


if __name__ == "__main__":
    main()
