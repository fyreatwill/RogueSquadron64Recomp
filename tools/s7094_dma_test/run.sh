#!/bin/zsh
# s7094: differential of the LIVE librecomp RSP DMA (rsp.hpp dma_rdram_to_dmem / dma_dmem_to_rdram, fast + slow path)
# vs the cxd4 reference (rs64-oracle mupen64plus-rsp-cxd4 su.c MT_DMA_* + SP_DMA_READ/WRITE, extracted verbatim).
# usage: zsh run.sh [MUTANT]   MUTANT: none | len2 (runtime copies raw+2 bytes: canonical class must fail) | norel (ref skips |7)
cd "$(dirname $0)"; ROOT=../..; INC=$ROOT/lib/N64ModernRuntime/librecomp/include/librecomp
SU=$ROOT/../rs64-oracle/src/mupen64plus-rsp-cxd4/su.c; M=${1:-none}; T=/tmp/s7094_$M; rm -rf $T; mkdir -p $T
awk '/^#define RSP_MEM_B\(offset/{on=1} on{print} on&&/^#define RSP_MEM_BU/{b=1} b&&/^$/{exit}' $INC/rsp.hpp > $T/rspmemb.inc
awk '/^static inline void dma_rdram_to_dmem/{on=1} on{print} on&&/^static inline void dma_dmem_to_rdram/{w=1} w&&/^}/{exit}' $INC/rsp.hpp > $T/rt_dma.inc
awk '/^static void MT_DMA_CACHE/{on=1} on{print} /^static void MT_DMA_WRITE_LENGTH/{w=1} w&&/^}/{exit}' $SU > $T/cx_mt.inc
awk '/^void SP_DMA_READ\(void\)/{on=1} on{print} /^void SP_DMA_WRITE\(void\)/{w=1} w&&/^}/{exit}' $SU > $T/cx_dma.inc
[ -s $T/rt_dma.inc -a -s $T/cx_dma.inc -a -s $T/cx_mt.inc -a -s $T/rspmemb.inc ] || { echo "extract failed"; exit 3; }
case $M in
  len2)  sed -i '' 's|rd_len += 1; // Read length is inclusive|rd_len += 2;|; s|wr_len += 1; // Write length is inclusive|wr_len += 2;|' $T/rt_dma.inc;;
  norel) sed -i '' 's/SR\[rt\] | 07;/SR[rt];/' $T/cx_mt.inc;;
esac
[ $M != none ] && cmp -s $T/rt_dma.inc <(awk '/^static inline void dma_rdram_to_dmem/{on=1} on{print} on&&/^static inline void dma_dmem_to_rdram/{w=1} w&&/^}/{exit}' $INC/rsp.hpp) && cmp -s $T/cx_mt.inc <(awk '/^static void MT_DMA_CACHE/{on=1} on{print} /^static void MT_DMA_WRITE_LENGTH/{w=1} w&&/^}/{exit}' $SU) && { echo "MUTANT $M did not apply"; exit 3; }
clang++ -std=c++20 -O2 -w -I$T harness.cpp -o $T/h || exit 2
echo "[s7094] mutant=$M rt=$(wc -l < $T/rt_dma.inc) lines cxd4=$(wc -l < $T/cx_dma.inc) lines"; $T/h $M
