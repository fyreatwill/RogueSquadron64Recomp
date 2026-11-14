#!/bin/zsh
# s7360 class AK two-arm control: post = live print.cpp (must print 5 PASS), pre = print.cpp with the s7360 block stripped
# (must abort with heap-buffer-overflow on the cross-top send).
cd "${0:A:h}/.." || exit 1
J=lib/N64ModernRuntime/thirdparty
INC=(-Ilib/N64ModernRuntime/librecomp/include -Ilib/N64ModernRuntime/librecomp/include/librecomp -Ilib/N64ModernRuntime/ultramodern/include
     -Ilib/N64ModernRuntime/N64Recomp/include -I$J/concurrentqueue -I$J)
mkdir -p scratch/s7360
python3 -c "
s=open('lib/N64ModernRuntime/librecomp/src/print.cpp').read(); a=s.index('    // s7360 class AK'); b=s.index('    u32 type = (u32)ctx->r6;')
open('scratch/s7360/print_pre.cpp','w').write(s[:a]+s[b:])"
clang++ -std=c++20 -g -fsanitize=address $INC tools/s7360_rdbsend_ctl.cpp lib/N64ModernRuntime/librecomp/src/print.cpp -o scratch/s7360/ctl_post || exit 1
clang++ -std=c++20 -g -fsanitize=address $INC tools/s7360_rdbsend_ctl.cpp scratch/s7360/print_pre.cpp -o scratch/s7360/ctl_pre || exit 1
scratch/s7360/ctl_post >/dev/null || { echo "post FAIL"; exit 1; }
scratch/s7360/ctl_pre 2>&1 | grep -q 'heap-buffer-overflow' || { echo "pre did NOT overflow: control invalid"; exit 1; }
echo "s7360 ctl: post 5/5 PASS, pre heap-buffer-overflow -> PASS"
