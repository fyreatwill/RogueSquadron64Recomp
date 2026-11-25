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
# s7924 class DO: freeze_arms through the real ring path (ring file -> ring_stalls.py -> tag line -> verdict). Planted 60 Hz rings:
# steady -> 0; a 1.5 s hold with gen frozen -> 1; a 17 s hold with gen advancing every row (animating title, s7923) -> 0.
mk() { python3 - "$1" "$2" <<'PY'
import sys; out, kind = sys.argv[1], sys.argv[2]; t = [1.7e9]; g = [0]; L = []
def run(n, vi, step):
    for i in range(n): L.append('Q %.6f id=%d wl=0 skip=0 vi=%s fb=%s gen=%d' % (t[0], len(L), vi, vi, g[0])); t[0] += 1/60; g[0] += step
for k in range(120): run(1, 'A' if k % 2 else 'B', 1)
if kind == 'frozen': run(90, 'C', 0)
if kind == 'anim': run(1020, 'D', 1)
for k in range(120): run(1, 'A' if k % 2 else 'B', 1)
open(out, 'w').write('\n'.join(L) + '\n')
PY
}
tl() { print "tag=fz_$2 alive_at_end=1 crashlines=0 $(python3 ${3:-tools/agent/ring_stalls.py} $1 30)" > $T/tl_$2; }
for k in steady frozen anim; do mk $T/ring_$k $k; tl $T/ring_$k $k; done
chk $T/tl_steady 'freeze_arms=0'; chk $T/tl_steady 'freeze_na=0'; chk $T/tl_frozen 'freeze_arms=1'; chk $T/tl_anim 'freeze_arms=0'
chk $T/tl_frozen 'stall_arms=0'   # 1.5 s is far under vi_stalls30s: the freeze is visible ONLY through freeze_arms
# mutation: a scorer without the s7923 animating rule reads the 17 s title as a freeze (proves the anim check above has teeth)
sed 's/^    if len(G) < 2: return False$/    return False/' tools/agent/ring_stalls.py > $T/rs_noanim.py; grep -q '^    return False$' $T/rs_noanim.py || { bad=$((bad+1)); print 'FAIL noanim sed did not apply'; }
tl $T/ring_anim anim_mut $T/rs_noanim.py; chk $T/tl_anim_mut 'freeze_arms=1'
# FREEZE_MS knob: at 2000 ms the 1.5 s planted freeze no longer counts
n=$((n+1)); [[ " $(env FREEZE_MS=2000 zsh $V $T/tl_frozen) " == *" freeze_arms=0 "* ]] || { bad=$((bad+1)); print 'FAIL FREEZE_MS=2000'; }
# positive control: the real s7696 soak logs that were misread
for L in scratch/agent/soak_results/s7696_cut_L{1,4}_*.log(N); do chk $L 'alive=1/1'; chk $L 'crash_arms=0'; done
rm -rf $T; print "soak_verdict_fields selftest: $((n-bad))/$n rows ok, bad=$bad"; [ $bad = 0 ]
