#!/bin/zsh
# s7770 self-test for the stop_gate.sh rename-census rule. Runs the gate's OWN snippet text (extracted between its
# "# s7770:" marker and the next "# --- OUTCOME" line) with block() stubbed, so a later gate edit is what gets tested.
# Rows: fake census called=0/1 x sweep/other slug, then the REAL census on the live syms (must block) and on a copy with
# send_mesg reverted to func_8002BB34 (mutation control: must pass, called=1).
cd ${0:A:h}/../.. || exit 1
T=$(mktemp -d); n=0; bad=0
SNIP=$(awk '/^# s7770: a NEXT.md/{p=1} /^# --- OUTCOME/{p=0} p' tools/agent/stop_gate.sh)
[ -n "$SNIP" ] || { print "FAIL: snippet not found in stop_gate.sh"; exit 1; }
run() { # want(block|pass) slug census_cmd
  local want=$1 slug=$2; mkdir -p $T/ag; print "HYPOTHESIS-ID: $slug" > $T/ag/NEXT.md
  local got; got=$(AG=$T/ag RS64_RENAME_CENSUS_CMD="$3" bash -c 'block() { echo BLOCK; exit 0; }; '"$SNIP"'; echo PASS')
  n=$((n+1)); [ "$got" = "${(U)want}" ] || { bad=$((bad+1)); print "FAIL want=$want got=$got slug=$slug cmd=$3"; }
}
print 'print "SUMMARY placeholders=2 called=0 unref=1 tail=1"' > $T/c0; print 'print "SUMMARY placeholders=3 called=1 unref=1 tail=1"' > $T/c1
run block generated-symbol-renaming-sweep "zsh $T/c0"
run pass  generated-symbol-renaming-sweep "zsh $T/c1"
run pass  owner-review-queue "zsh $T/c0"
run pass  generated-symbol-renaming-sweep "false"            # census failed -> no SUMMARY -> never block on a broken tool
run block generated-symbol-renaming-sweep "python3 tools/s7770_placeholder_census.py --quiet"
sed 's/name = "send_mesg"/name = "func_8002BB34"/' syms/rogue_squadron.syms.toml > $T/syms.toml
grep -q func_8002BB34 $T/syms.toml || { bad=$((bad+1)); print "FAIL mutation not planted"; }
run pass  generated-symbol-renaming-sweep "python3 tools/s7770_placeholder_census.py --quiet --syms $T/syms.toml"
python3 tools/s7770_placeholder_census.py --quiet --controls >/dev/null || { bad=$((bad+1)); print "FAIL census controls"; }; n=$((n+1))
rm -rf $T; print "rename_census_gate selftest: $((n-bad))/$n rows ok, bad=$bad"; [ $bad = 0 ]
