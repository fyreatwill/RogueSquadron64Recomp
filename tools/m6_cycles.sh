#!/bin/zsh
# Count mission re-entries in a run.log: hangar (0x6AB400) VI-origin entries seen after the first mission origin (0x690400).
# Usage: tools/m6_cycles.sh run.log [--selftest]   (same logic as mcycles() in scratch/agent/m6_god_common.sh)
mc() { grep -a '^\[vi\] update_screen' "$1" | grep -o 'origin=0x[0-9A-Fa-f]*' | uniq | awk '/690400/ {m=1} m && /6AB400/ {n++} END {print n+0}'; }
if [ "${2:-}" = "--selftest" ] || [ "${1:-}" = "--selftest" ]; then
  t=$(mktemp); printf '[vi] update_screen origin=0x006AB400\n[vi] update_screen origin=0x00690400\n[vi] update_screen origin=0x006AB400\n[vi] update_screen origin=0x00690400\n[vi] update_screen origin=0x006AB400\n' > $t
  [ "$(mc $t)" = 2 ] && echo "selftest OK" || echo "selftest FAIL"; rm -f $t; [ "${1:-}" = "--selftest" ] && exit 0
fi
mc "$1"
