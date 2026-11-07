#!/bin/zsh
# s6941 G1e: bit-exactness of the RS64_RSP_NEON_MAC=1 multiply-op bodies (librecomp rsp_vu_impl.hpp) against the SSE ones.
# usage (repo root): zsh tools/g1e_nmac_equiv.zsh [cases]; MUTANT=1 must FAIL (positive control). Exit 1 = arms diverge.
cd ${0:A:h}/..; O=scratch/nmac_equiv; mkdir -p $O
L=lib/N64ModernRuntime
F=(-std=c++20 -O2 -w -fno-strict-aliasing -fms-extensions -I$L/librecomp/include -I$L/ultramodern/include -I$L/N64Recomp/include -I$L/thirdparty/sse2neon -I$L/thirdparty -Iinclude)
clang++ $F -DTAG=old -DRSP=RS64_RSP_EQ_OLD -DRS64_RSP_NEON_MAC=0 -c tools/g1e_nmac_op.cpp -o $O/old.o || exit 2
clang++ $F -DTAG=new -DRSP=RS64_RSP_EQ_NEW -DRS64_RSP_NEON_MAC=1 ${MUTANT:+-DRS64_EQ_MUTANT} -c tools/g1e_nmac_op.cpp -o $O/new.o || exit 2
clang++ -std=c++20 -O2 tools/g1e_nmac_equiv.cpp $O/old.o $O/new.o -o $O/eq || exit 2
$O/eq ${1:-200000}
