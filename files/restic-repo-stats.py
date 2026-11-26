#!/usr/bin/env python3

"""Repository statistics for restic: snapshot list, latest-snapshot restore
size, repository deduplicated size, and du-style per-directory size and
file-count breakdowns, computed from the output of `restic snapshots`,
`restic stats` and `restic ls --json`."""

import json
import subprocess
import sys

TOP = 10


def restic(*args):
    return subprocess.run(("restic",) + args, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True)


def human_size(num):
    if num < 1000:
        return f"{num} B"
    for unit in ("kB", "MB", "GB", "TB"):
        num /= 1000
        if num < 1000:
            return f"{num:.0f} {unit}" if num >= 10 else f"{num:.1f} {unit}"
    return f"{num:.0f} PB"


def breakdown(lines):
    counts = {}
    sizes = {}
    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("type") != "file":
            continue
        parts = entry["path"].strip("/").split("/")
        for depth in range(1, len(parts)):
            prefix = "/".join(parts[:depth])
            counts[prefix] = counts.get(prefix, 0) + 1
            sizes[prefix] = sizes.get(prefix, 0) + (entry.get("size") or 0)
    return counts, sizes


def main():
    rc = 0

    for title, args in (
        ("Snapshots", ("snapshots", "--compact")),
        ("Latest snapshot restore size", ("stats", "--mode", "restore-size", "latest")),
        ("Repository raw data (deduplicated)", ("stats", "--mode", "raw-data")),
    ):
        print(f"=== {title} ===")
        result = restic(*args)
        if result.stdout.strip():
            print(result.stdout.rstrip())
        if result.returncode != 0:
            rc = 1
            print(result.stderr.strip(), file=sys.stderr)
        print()

    listing = restic("ls", "--json", "latest")
    if listing.returncode != 0:
        print(listing.stderr.strip(), file=sys.stderr)
        return 1

    counts, sizes = breakdown(listing.stdout.splitlines())
    print("=== Files count by directory (latest snapshot) ===")
    for path, count in sorted(counts.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))[:TOP]:
        print(f"{path}: {count} files")
    print()
    print("=== Size by directory (latest snapshot) ===")
    for path, size in sorted(sizes.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))[:TOP]:
        print(f"{path}: {human_size(size)}")

    return rc


if __name__ == "__main__":
    sys.exit(main())
