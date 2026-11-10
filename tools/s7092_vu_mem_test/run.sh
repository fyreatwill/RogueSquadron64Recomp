#!/bin/zsh
# s7092: build + run the VU DMEM fast-path / divide-unit differential against the LIVE librecomp headers.
# usage: zsh run.sh [MUTANT] [DP_STEP]   MUTANT: none | ldv_lane | wrap | rcp_rom | lqv_cnt  (positive controls)
cd "$(dirname $0)"; ROOT=../..; INC=$ROOT/lib/N64ModernRuntime/librecomp/include/librecomp
CX=$ROOT/../rs64-oracle/src/mupen64plus-rsp-cxd4/vu/divide.c; M=${1:-none}; STEP=${2:-1}
T=/tmp/s7092_$M; rm -rf $T; mkdir -p $T
cp $INC/rsp_vu.hpp $INC/rsp_vu_impl.hpp $T/
awk '/^#define RSP_MEM_B\(offset/{on=1} on{print} on&&/^static inline void RSP_MEM_H_STORE/{h=1} h&&/^}/{exit}' $INC/rsp.hpp > $T/dmem_block.inc
{ echo 'static void recomp_constants_init() { using u16 = uint16_t; using u64 = uint64_t;'
  awk '/^void recomp::rsp::constants_init\(\) \{/{on=1;next} on&&/^}/{exit} on{print}' $ROOT/lib/N64ModernRuntime/librecomp/src/rsp.cpp; echo '}'; } > $T/constants_init.inc
awk '/^static const u16 div_ROM/{on=1} on{print} on&&/^NOINLINE static void do_div/{d=1} d&&/^}/{exit}' $CX > $T/cxd4_div.inc
case $M in
  ldv_lane) sed -i '' 's|vt.word(e / 4 + 1) = rs64_dmem_w(address + 4); return;|vt.word(e / 4 + 1) = rs64_dmem_w(address + 4) ^ 1; return;|' $T/rsp_vu_impl.hpp;;
  wrap)     sed -i '' 's|memcpy(\&v, RS64_DMEM_BASE + (a \& 0xFFC), 4); return v; }|memcpy(\&v, RS64_DMEM_BASE + (a \& 0x1FFC), 4); return v; }|' $T/dmem_block.inc;;
  lqv_cnt)  sed -i '' 's|cnt = (16 - (address \& 15)) / 4|cnt = (16 - (address \& 7)) / 4|' $T/rsp_vu_impl.hpp;;
  rcp_rom)  sed -i '' 's|rspReciprocals\[index\] = u16((b + 1) >> 8);|rspReciprocals[index] = u16((b + 1) >> 8) ^ (index == 300);|' $T/constants_init.inc;;
esac
[ $M != none ] && { cmp -s $INC/rsp_vu_impl.hpp $T/rsp_vu_impl.hpp && cmp -s $T/dmem_block.inc <(awk '/^#define RSP_MEM_B\(offset/{on=1} on{print} on&&/^static inline void RSP_MEM_H_STORE/{h=1} h&&/^}/{exit}' $INC/rsp.hpp) && [ $M != rcp_rom ] && { echo "MUTANT $M did not apply"; exit 3; }; }
clang++ -std=c++20 -O2 -w -I$T -I$ROOT/lib/N64ModernRuntime/thirdparty/sse2neon harness.cpp -o $T/h || exit 2
echo "[s7092] mutant=$M dp_step=$STEP"; $T/h $STEP
