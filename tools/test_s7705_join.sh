#!/bin/zsh
# s7706: fixture test for tools/s7705_join.py (IN/PAST split, boot control, post-boot counts incl. stale hits).
# Mutation control: the s7705 version (git show 6b4a962f4:tools/s7705_join.py) must MISS the stale post-boot hit.
set -u
R=${0:A:h:h}; T=$(mktemp -d /tmp/s7706join.XXXX); fail=0
mk() { mkdir -p $T/$1; print -r -- "$2" > $T/$1/run.log; print -r -- "$3" > $T/$1/s7702.log; }
SK='[ost-wb] SKIP_WILD_W #1 tag=color addr=0x9B6000 w=768 siz=2 rows=0..340
[ost-wb] SKIP_WILD_W #2 tag=color addr=0xB80800 w=768 siz=2 rows=0..340'
CTL='hit src=timg img=colour@0x9B6000 cur=0 w=768 age=lt5s n=10 loaded=1 rows=25..339 t=12.2..16.6'
mk ctl "$SK" "$CTL"
mk past "$SK" "$CTL
hit src=dma_gfx img=z@0xB80800 cur=0 w=768 age=lt50ms n=5 loaded=1 rows=340..383 t=46.6..58.4"
mk fresh "$SK" "$CTL
hit src=timg img=colour@0xB80800 cur=0 w=768 age=lt50ms n=5 loaded=1 rows=10..20 t=50.0..51.0"
mk stale "$SK" "$CTL
hit src=timg img=colour@0xB80800 cur=0 w=768 age=stale n=5 loaded=1 rows=10..20 t=80.0..81.0"
mk noctl "$SK" "hit src=dma_gfx img=z@0xB80800 cur=0 w=768 age=lt50ms n=5 loaded=1 rows=340..383 t=46.6..58.4"
mk otherw "$SK" "$CTL
hit src=timg img=colour@0xB80800 cur=0 w=1024 age=lt50ms n=5 loaded=1 rows=10..20 t=50.0..51.0"
chk() { # name expected-rc expected-summary-substrings...
  local n=$1 erc=$2; shift 2
  out=$(python3 ${J:-$R/tools/s7705_join.py} $T/$n | tail -1); python3 ${J:-$R/tools/s7705_join.py} $T/$n >/dev/null; rc=$?
  [[ $rc == $erc ]] || { print "FAIL $n rc=$rc want $erc"; fail=1; }
  for w in "$@"; do [[ " $out " == *" $w "* ]] || { print "FAIL $n missing '$w' in: $out"; fail=1; }; done
  print "ok   $n: $out"
}
chk ctl    0 ctl_boot_in=1 in=1 past=0 fresh_in_after_boot=0 in_after_boot=0
chk past   0 in=1 past=1 fresh_in_after_boot=0 in_after_boot=0
chk fresh  0 in=2 fresh_in_after_boot=1 in_after_boot=1
chk stale  0 in=2 fresh_in_after_boot=0 in_after_boot=1
chk noctl  1 ctl_boot_in=0 past=1
chk otherw 0 in=1 in_after_boot=0
# mutation control: the old tool has no in_after_boot field, so the stale post-boot hit is invisible in its summary
git -C $R show 6b4a962f4:tools/s7705_join.py > $T/old.py
o=$(python3 $T/old.py $T/stale | tail -1)
if [[ "$o " == *" in_after_boot="* || $o != *fresh_in_after_boot=0* ]]; then print "FAIL mutation: old tool output unexpected: $o"; fail=1
else print "ok   mutation: old tool reports '$o' (stale post-boot hit missed) -> new field catches it"; fi
rm -rf $T
(( fail )) && { print "RESULT FAIL"; exit 1; }; print "RESULT PASS 6/6 + mutation"; exit 0
