#!/bin/zsh
# usage: from this dir. Builds simd/sisd variants of harness.cpp and diffs state hashes.
# s7092: the variant headers are regenerated from the LIVE rsp_vu.hpp each run (the committed s6301 copies went stale
# when s6774 added r128::word(), so the harness no longer built). sisd = the SSE4_1 branch's SISD/SIMD flags flipped.
cd "$(dirname $0)"; INC=../../lib/N64ModernRuntime/librecomp/include/librecomp
mkdir -p simd sisd; cp $INC/rsp_vu.hpp simd/rsp_vu.hpp
awk 'BEGIN{n=0} /constexpr bool SISD = false;/&&n==0{print "        constexpr bool SISD = true;";n=1;next} /constexpr bool SIMD = true;/&&n==1{print "        constexpr bool SIMD = false;";n=2;next} {print}' $INC/rsp_vu.hpp > sisd/rsp_vu.hpp
cmp -s simd/rsp_vu.hpp sisd/rsp_vu.hpp && { echo "flag flip did not apply"; exit 3; }
for v in simd sisd; do clang++ -std=c++20 -O1 -w -I$v -I$INC -I../../lib/N64ModernRuntime/thirdparty/sse2neon harness.cpp -o /tmp/h_$v || exit 1; /tmp/h_$v > /tmp/o_$v.txt; done
diff /tmp/o_simd.txt /tmp/o_sisd.txt && echo "IDENTICAL $(wc -l < /tmp/o_simd.txt)"
