#!/bin/zsh
# s7455 class DK self-test for tools/agent/summary_field.sh. Each row: expected exit, args. The "old" column re-runs the
# prefix check the recipes used, to show it false-passes on the same input (mutation control: the hazard is real here).
cd ${0:A:h}/../.. || exit 1
T=$(mktemp -d); SF=tools/agent/summary_field.sh; n=0; bad=0
chk() { local want=$1; shift; zsh $SF "$@" 2>/dev/null; local got=$?; n=$((n+1)); [ $got = $want ] || { bad=$((bad+1)); print "FAIL want=$want got=$got: $*"; }; }
print 'tag=t att=1 mission_t=40s hold=120s inits=12 flight_s=130 launches=1 mission_restarts=0 alive_at_end=1 vi_stalls30s=0 crashlines=0 exitrc=held' > $T/a
print 'tag=t att=1 mission_t=40s died_in_verify=1 inits=1 launches=1 mission_restarts=3 alive_at_end=0 vi_stalls30s=0 crashlines=1 exitrc=134' > $T/b
print 'tag=t allattempts-failed deaths=5 fatal_total=0' > $T/c
chk 1 $T/a inits eq 1;  chk 0 $T/a inits eq 12; chk 0 $T/a inits ge 1;  chk 1 $T/a inits le 1
chk 0 $T/a mission_restarts eq 0; chk 0 $T/a crashlines eq 0; chk 0 $T/a alive_at_end eq 1; chk 0 $T/a exitrc is held
chk 1 $T/a exitrc eq 1   # non-numeric value under a numeric op fails
chk 1 $T/b exitrc eq 1;  chk 0 $T/b exitrc eq 134; chk 0 $T/b exitrc ne 0
chk 1 $T/b restarts eq 3 # key must match exactly: mission_restarts is not restarts
chk 1 $T/b mission_restarts eq 0; chk 0 $T/b crashlines ge 1; chk 0 $T/b inits eq 1
chk 1 $T/c alive_at_end eq 1   # missing key fails
{ cat $T/a; print 'shots=      26'; } > $T/d; chk 0 $T/d crashlines eq 0; chk 1 $T/d shots eq 26   # trailing extra line (s5745); its "shots=      26" has an empty value -> rejected
chk 1 $T/nofile crashlines eq 0; chk 2 $T/a crashlines approx 0
# mutation control: the old prefix idioms false-pass on these same files (must, or the test proves nothing)
grep -q 'inits=1' $T/a && print "old-prefix control: grep inits=1 passes inits=12 (hazard reproduced)" || { bad=$((bad+1)); print "FAIL control inits"; }
S=$(<$T/b); [[ $S == *exitrc=1* ]] && print "old-prefix control: *exitrc=1* passes exitrc=134 (hazard reproduced)" || { bad=$((bad+1)); print "FAIL control exitrc"; }
grep -q 'restarts=3' $T/b && print "old-prefix control: grep restarts=3 passes mission_restarts=3 (hazard reproduced)" || { bad=$((bad+1)); print "FAIL control restarts"; }
rm -rf $T; print "summary_field selftest: $((n-bad))/$n rows ok, bad=$bad"; [ $bad = 0 ]
