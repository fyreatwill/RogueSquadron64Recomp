#!/bin/zsh
# s7815: every elementwise VU op (live in the LLE gfx ucode + dead siblings) vs cxd4, both shipped flavours.
# Live librecomp headers copied each run; cxd4 vu/*.c compiled unmodified. usage: zsh run.sh [MUTANT] [REPS] [NEON_MAC 0|1] [CX_SSE 0|1]
# CX_SSE=1 builds cxd4's main ARCH_MIN_SSE2 path through its own bundled sse2neon (USE_SSE2NEON); 0 = its scalar C path.
# MUTANT: none | madh_carry | mulf_round | addc_vco | lt_cmp | cl_vce | mrg_sel | madn_clamp (both flavours patched)
cd "$(dirname $0)"; ROOT=../..; INC=$ROOT/lib/N64ModernRuntime/librecomp/include/librecomp
CX=${CXD4:-$ROOT/../rs64-oracle/src/mupen64plus-rsp-cxd4}; M=${1:-none}; REPS=${2:-1000}; NM=${3:-0}; CS=${4:-0}
T=/tmp/s7815_${M}_${NM}_$CS; rm -rf $T; mkdir -p $T/cx/vu
cp $INC/rsp_vu.hpp $INC/rsp_vu_impl.hpp $T/
cp $CX/vu/*.c $CX/vu/*.h $T/cx/vu/; cp $CX/my_types.h $T/cx/; mkdir -p $T/cx/sse2neon
# cxd4's bundled SSE2NEON.h predates _mm_cmplt_epi16 etc.; shim it to the maintained sse2neon (standard Intel semantics)
echo "#include \"$PWD/$ROOT/lib/N64ModernRuntime/thirdparty/sse2neon/sse2neon.h\"" > $T/cx/sse2neon/SSE2NEON.h
awk '/^#define RSP_MEM_B\(offset/{on=1} on{print} on&&/^static inline void RSP_MEM_H_STORE/{h=1} h&&/^}/{exit}' $INC/rsp.hpp > $T/dmem_block.inc
# Optional third arm: CEN64 header-only kernels (CEN64_DIR = a clone of github.com/n64dev/cen64; never built or run, 7 headers copied)
CEN=${CEN64_DIR:-$PWD/cen64}; CENF=-DCEN64=0   # vendored copies (cen64/README); CEN64_DIR may point at a full clone
CH=$CEN; [ -d $CEN/arch/x86_64/rsp ] && CH=$CEN/arch/x86_64/rsp
if [ -f $CH/vch.h ]; then mkdir -p $T/s7815_cen64; : > $T/s7815_cen64/common.h
  for h in clamp vabs vch vcr vmrg vmuln vmull; do cp $CH/$h.h $T/s7815_cen64/; done; CENF=-DCEN64=1
else echo "[s7815] no CEN64 clone at $CEN: third arm skipped (git clone --depth 1 https://github.com/n64dev/cen64 $CEN)"; fi
I=$T/rsp_vu_impl.hpp
case $M in
  madh_carry) perl -0pi -e 's/(auto RSP::VMADH\(.*?)hi = vsubq_u16\(hi, vcltq_u16\(m, lo\)\);/$1;/s; s/(auto RSP::VMADH\(.*?)hi = _mm_sub_epi16\(hi, omask\);/$1;/s' $I;;
  mulf_round) perl -0pi -e 's/(auto RSP::VMULF\(.*?)round = _mm_slli_epi16\(round, 15\);/$1round = _mm_slli_epi16(round, 14);/s' $I;;
  addc_vco)   perl -0pi -e 's/(auto RSP::VADDC\(.*?)VCOL = _mm_cmpeq_epi16\(VCOL, zero\);/$1;/s' $I;;
  lt_cmp)     perl -0pi -e 's/(auto RSP::VLT\(.*?)lt = _mm_cmplt_epi16\(vs, vte\);/$1lt = _mm_cmpgt_epi16(vs, vte);/s' $I;;
  cl_vce)     perl -0pi -e 's/(auto RSP::VCL\(.*?)lec2 = _mm_and_si128\(VCE, lec2\);/$1lec2 = _mm_and_si128(zero, lec2);/s' $I;;
  mrg_sel)    perl -0pi -e 's/(auto RSP::VMRG\(.*?)ACCL = _mm_blendv_epi8\(vt\(e\), vs, VCCL\);/$1ACCL = _mm_blendv_epi8(vs, vt(e), VCCL);/s' $I;;
  madn_clamp) perl -0pi -e 's/(auto RSP::VMADN\(.*?)cmask = _mm_and_si128\(smd, shi\);/$1cmask = shi;/s; s/(auto RSP::VMADN\(.*?)RS64_NCLAMPU\(vd\);/$1vd = ACCL;/s' $I;;
esac
[ $M != none ] && cmp -s $INC/rsp_vu_impl.hpp $I && { echo "MUTANT $M did not apply"; exit 3; }
CXF=; [ $CS = 1 ] && CXF="-DUSE_SSE2NEON -D__ARM_NEON__"
for f in vu multiply add select logical divide; do clang -c -O2 -w ${=CXF} $T/cx/vu/$f.c -o $T/cx_$f.o || exit 2; done
if [ $CS = 1 ]; then nm $T/cx_vu.o | grep -q ' _V_result' && { echo "cxd4 built the scalar path despite CX_SSE=1"; exit 4; }
else nm $T/cx_vu.o | grep -q ' _V_result' || { echo "cxd4 built the SSE path (no V_result)"; exit 4; }; fi
clang++ -std=c++20 -O2 -w -DRS64_RSP_NEON_MAC=$NM -DCX_SSE=$CS $CENF -I$T -I$ROOT/lib/N64ModernRuntime/thirdparty/sse2neon harness.cpp $T/cx_*.o -o $T/h || exit 2
echo "[s7815] mutant=$M reps=$REPS neon_mac=$NM cx_sse=$CS"; $T/h $REPS
