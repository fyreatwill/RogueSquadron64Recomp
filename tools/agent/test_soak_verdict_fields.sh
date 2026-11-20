#!/bin/zsh
# s7697 class DN self-test for tools/agent/soak_verdict_fields.sh: alive=/crash= alias keys, alive_na, canonical keys unchanged.
cd ${0:A:h}/../.. || exit 1
T=$(mktemp -d); V=tools/agent/soak_verdict_fields.sh; n=0; bad=0
chk() { local f=$1 want=$2; local got=$(zsh $V $f); n=$((n+1)); [[ " $got " == *" $want "* ]] || { bad=$((bad+1)); print "FAIL $f want '$want' got '$got'"; }; }
print 'tag=cut_L1 alive=1 crash=0 fb=105 pre_in_cine=0' > $T/alias_ok
print 'tag=cut_L1 alive=0 crash=3' > $T/alias_bad
print 'tag=t alive_at_end=1 crashlines=0 vi_stalls30s=0' > $T/canon
print 'tag=t alive_at_end=0 alive=1 crashlines=2 crash=0 vi_stalls30s=0' > $T/canon_wins
print 'tag=t rebuilds=4 levels=1,' > $T/none
chk $T/alias_ok 'alive=1/1'; chk $T/alias_ok 'crash_arms=0'; chk $T/alias_ok 'alive_na=0'
chk $T/alias_bad 'alive=0/1'; chk $T/alias_bad 'crash_arms=1'
chk $T/canon 'alive=1/1'; chk $T/canon 'stall_arms=0'; chk $T/canon 'alive_na=0'
chk $T/canon_wins 'alive=0/1'; chk $T/canon_wins 'crash_arms=1'
chk $T/none 'alive=0/1'; chk $T/none 'alive_na=1'
# positive control: the real s7696 soak logs that were misread
for L in scratch/agent/soak_results/s7696_cut_L{1,4}_*.log(N); do chk $L 'alive=1/1'; chk $L 'crash_arms=0'; done
rm -rf $T; print "soak_verdict_fields selftest: $((n-bad))/$n rows ok, bad=$bad"; [ $bad = 0 ]
