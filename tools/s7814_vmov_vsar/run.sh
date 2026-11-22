#!/bin/zsh
# s7814: VMOV / VSAR (the two live ucode VU ops with no independent-reference evidence after s6301/s7092) vs cxd4.
# Builds against the LIVE librecomp headers each run (cannot go stale). usage: zsh run.sh [MUTANT] [REPS]
# MUTANT: none | vmov_acc (ACCL = vt, no broadcast) | vmov_lane (writes lane de^1) | vsar_swap (e=8 reads ACCM)
cd "$(dirname $0)"; ROOT=../..; INC=$ROOT/lib/N64ModernRuntime/librecomp/include/librecomp
CX=$ROOT/../rs64-oracle/src/mupen64plus-rsp-cxd4/vu; M=${1:-none}; REPS=${2:-4000}
T=/tmp/s7814_$M; rm -rf $T; mkdir -p $T
cp $INC/rsp_vu.hpp $INC/rsp_vu_impl.hpp $T/
awk '/^#define RSP_MEM_B\(offset/{on=1} on{print} on&&/^static inline void RSP_MEM_H_STORE/{h=1} h&&/^}/{exit}' $INC/rsp.hpp > $T/dmem_block.inc
{ awk '/^VECTOR_OPERATION VMOV\(/{on=1} on{print} on&&/^}/{exit}' $CX/divide.c
  awk '/^VECTOR_OPERATION VSAW\(/{on=1} on{print} on&&/^}/{exit}' $CX/add.c; } > $T/cxd4_ops.inc
grep -q 'VECTOR_OPERATION VMOV' $T/cxd4_ops.inc && grep -q 'VECTOR_OPERATION VSAW' $T/cxd4_ops.inc || { echo "cxd4 extraction failed"; exit 4; }
case $M in
  vmov_acc)  perl -0pi -e 's/(auto RSP::VMOV\(r128& vd, u8 de, cr128& vt\) -> void \{\n    cr128 vte = vt\(e\);\n    vd.u16\(de\) = vte.u16\(de\);\n    )ACCL = vte;/$1ACCL = vt;/' $T/rsp_vu_impl.hpp;;
  vmov_lane) perl -0pi -e 's/vd.u16\(de\) = vte.u16\(de\);/vd.u16(de ^ 1) = vte.u16(de ^ 1);/' $T/rsp_vu_impl.hpp;;
  vsar_swap) perl -0pi -e 's/case 0x8: vd = ACCH; break;/case 0x8: vd = ACCM; break;/' $T/rsp_vu_impl.hpp;;
esac
[ $M != none ] && cmp -s $INC/rsp_vu_impl.hpp $T/rsp_vu_impl.hpp && { echo "MUTANT $M did not apply"; exit 3; }
clang++ -std=c++20 -O2 -w -I$T -I$ROOT/lib/N64ModernRuntime/thirdparty/sse2neon harness.cpp -o $T/h || exit 2
echo "[s7814] mutant=$M reps=$REPS"; $T/h $REPS
