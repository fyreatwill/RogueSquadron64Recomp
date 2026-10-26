#!/bin/zsh
# usage: from this dir. Builds simd/sisd variants of harness.cpp and diffs state hashes.
cd "$(dirname $0)"; INC=../../lib/N64ModernRuntime/librecomp/include/librecomp
for v in simd sisd; do clang++ -std=c++20 -O1 -w -I$v -I$INC -I../../lib/N64ModernRuntime/thirdparty/sse2neon harness.cpp -o /tmp/h_$v || exit 1; /tmp/h_$v > /tmp/o_$v.txt; done
diff /tmp/o_simd.txt /tmp/o_sisd.txt && echo "IDENTICAL $(wc -l < /tmp/o_simd.txt)"
