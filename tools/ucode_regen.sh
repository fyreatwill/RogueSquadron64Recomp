#!/bin/zsh
# s7091: rebuild build/factor5_ucode/*.c from a FRESH RSPRecomp pass + the committed tools/ucode_fixed/*.patch.
# Why: build/ is gitignored and tools/fixup_factor5_ucode.py cannot rebuild the fixed ucode from a fresh pass
# (its blocks anchor on text that later blocks inserted or rewrote; tools/s7091_ucode_regen.py regen shows
# which). The patches are the exact pristine->live delta; their content is audited by
# tools/s7091_ucode_insn_census.py (0 unexplained retail-instruction changes, s7091).
#   tools/ucode_regen.sh verify    # regenerate into scratch/ucode_regen and byte-compare with build/factor5_ucode
#   tools/ucode_regen.sh restore   # same, then copy into build/factor5_ucode (refuses to overwrite a differing
#                                  # file unless FORCE=1; back up first)
#   tools/ucode_regen.sh snapshot  # after a deliberate fixup edit: refresh the patches from build/factor5_ucode
set -e
cd "${0:A:h}/.."
mode=${1:-verify}
RSPRECOMP=${RSPRECOMP:-../N64Recomp/build/RSPRecomp}
out=scratch/ucode_regen; pri=$out/pristine; res=$out/result
rm -rf $out; mkdir -p $pri $res
for t in factor5_rsp*.toml factor5b_rsp.toml factor5_boot_rsp.toml; do
  b=$(sed -n 's/^output_file_path = "build\/factor5_ucode\/\(.*\)".*/\1/p' $t)
  sed "s#^output_file_path = \".*\"#output_file_path = \"$pri/$b\"#" $t > ./ucode_regen_tmp_$t
  $RSPRECOMP ./ucode_regen_tmp_$t > $out/$t.log 2>&1 || { rm -f ./ucode_regen_tmp_$t; echo "RSPRecomp failed: $t"; exit 1; }
  rm -f ./ucode_regen_tmp_$t
done
cp $pri/*.c $res/
if [[ $mode == snapshot ]]; then
  for p in tools/ucode_fixed/*.patch; do
    b=${p:t:r}
    diff -u $pri/$b build/factor5_ucode/$b | sed "1s#.*#--- a/$b#;2s#.*#+++ b/$b#" > $p || true
    echo "refreshed $p"
  done
  exec python3 tools/s7091_ucode_insn_census.py $pri build/factor5_ucode --controls
fi
for p in tools/ucode_fixed/*.patch; do patch -s $res/${p:t:r} < $p; done
bad=0
for f in $res/*.c; do
  b=${f:t}
  if cmp -s $f build/factor5_ucode/$b; then echo "SAME $b"; else echo "DIFF $b"; bad=1; fi
done
python3 tools/s7091_ucode_insn_census.py $pri $res > $out/census.txt 2>&1 && echo "census: $(grep '^verdict' $out/census.txt)" || { echo "census FAILED"; cat $out/census.txt | head; exit 1; }
if [[ $mode == restore ]]; then
  mkdir -p build/factor5_ucode
  for f in $res/*.c; do
    b=${f:t}
    if [[ -e build/factor5_ucode/$b ]] && ! cmp -s $f build/factor5_ucode/$b && [[ ${FORCE:-0} != 1 ]]; then
      echo "refusing to overwrite differing build/factor5_ucode/$b (FORCE=1 to override)"; exit 1
    fi
    cp $f build/factor5_ucode/$b
  done
  echo restored
fi
exit $bad
