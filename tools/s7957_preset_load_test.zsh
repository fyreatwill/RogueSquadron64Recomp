#!/bin/zsh
# s7957 gate: RT64 preset library load survives malformed json. Same-run arms:
#   pre  = pre-fix header copy (scratch/s7957/rt64_preset_pre.h, or tools/s7957_rt64_preset_pre.h): bad files must abort (rc 134)
#   post = live lib/rt64/src/preset/rt64_preset.h: bad files return ok=0, n=0, rc 0; valid file loads n=2 on both.
cd "${0:A:h}/.."
T=$(mktemp -d /tmp/s7957XXXX); fails=0
PRE=tools/s7957_rt64_preset_pre.h
for arm in pre post; do
  if [[ $arm == pre ]]; then H="$PWD/$PRE"; else H="$PWD/lib/rt64/src/preset/rt64_preset.h"; fi
  c++ -std=c++17 -O0 -DPRESET_HDR="\"$H\"" -Ilib/rt64/src -Ilib/rt64/src/contrib -Ilib/rt64/src/contrib/hlslpp/include \
      tools/s7957_preset_load_test.cpp -o $T/t_$arm 2>$T/cc_$arm.txt || { echo "BUILD FAIL $arm"; head -5 $T/cc_$arm.txt; exit 1; }
done
print -r '{"presets":[{"name":"a"},{"name":"b"}]}' > $T/valid.json
print -r '{"presets":[{"name":"a"},' > $T/trunc.json
print -r '{"presets":[{"name":5}]}' > $T/types.json
print -r '{"presets":7}' > $T/notarr.json
mkdir $T/dir.json
printf '\xef\xbb' > $T/bin.json
for f in valid trunc types notarr dir bin; do
  for arm in pre post; do
    out=$($T/t_$arm $T/$f.json 2>/dev/null); rc=$?
    want=""
    if [[ $f == valid ]]; then want="rc=0 RESULT ok=1 n=2"
    elif [[ $arm == post ]]; then want="rc=0 RESULT ok=0 n=0"
    else want="abort"; fi
    got="rc=$rc $out"
    if [[ $want == abort ]]; then [[ $rc -ne 0 && -z $out ]] && v=PASS || v=FAIL
    else [[ $got == "$want" ]] && v=PASS || v=FAIL; fi
    # notarr: nlohmann iterates a number as a single element -> may not throw; report rather than fail the pre arm
    [[ $v == FAIL && $f == notarr && $arm == pre ]] && v=INFO
    [[ $v == FAIL ]] && fails=$((fails+1))
    echo "$v $f $arm $got (want $want)"
  done
done
rm -rf $T
echo "VERDICT $([[ $fails -eq 0 ]] && echo PASS || echo FAIL) fails=$fails"
[[ $fails -eq 0 ]]
