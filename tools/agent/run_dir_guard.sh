#!/bin/sh
# s7951: refuse a run dir whose name differs from an EXISTING sibling only by letter case.
# macOS APFS here is case-insensitive, so TAG=...L4a silently reused (and later overwrote) the s7031 run dir ...L4A:
# the s7031 census log was lost and the dir now holds s7056's run under s7031's name (census s7951: 1/2365 dirs).
# usage: run_dir_guard.sh <parent_dir> <name>   rc 0 = ok (absent, or exact same name = deliberate re-run)
#                                               rc 3 = case-only collision, prints "run_dir_collision=<existing>"
# s7952: one-arg form run_dir_guard.sh <path> splits it (trailing slash ok) for launchers that take a whole OUTDIR.
if [ $# -eq 1 ]; then p=$(dirname "$1"); n=$(basename "$1"); else p=$1; n=$2; fi
[ -d "$p" ] || exit 0
hit=$(ls -1 "$p" 2>/dev/null | awk -v n="$n" 'tolower($0) == tolower(n) && $0 != n {print; exit}')
[ -z "$hit" ] && exit 0
echo "run_dir_collision=$hit"
exit 3
