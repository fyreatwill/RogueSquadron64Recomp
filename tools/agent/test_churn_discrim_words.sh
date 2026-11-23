#!/bin/zsh
# s7859 self-test for stop_gate.sh's churn-guard discrimination regex (DISCRIM_RE). Rows: expected grep exit, text.
# Positive rows include the s7858 entry's real "Rules out:" line (the false block that motivated the widening);
# negative rows (control) are plain instrument-landing text that must still NOT count as a discrimination.
cd ${0:A:h}/../.. || exit 1
RE=$(sed -n "s/^[[:space:]]*DISCRIM_RE='\(.*\)'\$/\1/p" tools/agent/stop_gate.sh)
[ -n "$RE" ] || { print "FAIL DISCRIM_RE not found in stop_gate.sh"; exit 1; }
n=0; bad=0
chk() { n=$((n+1)); print -r -- "$2" | grep -qE "$RE"; local got=$?; [ $got = $1 ] || { bad=$((bad+1)); print "FAIL want=$1 got=$got: $2"; }; }
chk 0 'Rules out: port FPU/FMA mismatch at t892 (no such mismatch exists), oracle nondeterminism.'
chk 0 'This selects'
chk 0 'H-fma refuted by objdump census'
chk 0 'which ruled out H-spill'
chk 0 'closes the class'
chk 1 'Instrument: port lines now carry tick= (new rs64_s7858_tick).'
chk 1 'Next: continue the sweep 15 16.'
chk 1 'the selector byte'            # word boundary: "selector" is not "selects"
print "test_churn_discrim_words: $((n-bad))/$n"
[ $bad = 0 ]
