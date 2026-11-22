#!/bin/zsh
# s7816: build the VU-fixed cxd4 RSP plugin the retail oracle scripts load by default (RS64_ORACLE_RSP overrides).
# Stock cxd4 has 5 VU defects (s7815: VCR, VCH, VABS, VMRG, VMADN/VMADL clamp); tools/s7815_vu_ops/patch_cxd4.sh fixes them in a
# copy. The rs64-oracle tree is never modified. arm64 builds cxd4's scalar path (V_result present), which is what the patch covers.
# usage: zsh tools/oracle/build_cxd4_patched.sh [out_dir]   (FIXES=0 builds an unpatched copy, the build-equivalence control)
set -e
cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
O=${1:-/Users/williambuckley/Documents/Tools/rs64-oracle-cxd4p}
API=/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/src/api
zsh tools/s7815_vu_ops/patch_cxd4.sh $O
rm -rf $O/projects/unix/_obj
make -C $O/projects/unix all -j2 APIDIR=$API 2>&1 | grep -v 'not officially supported' | tail -2
nm $O/projects/unix/mupen64plus-rsp-cxd4.dylib | grep -q ' _V_result' || { echo "built the SSE path: patch does not cover it"; exit 4; }
echo "built $O/projects/unix/mupen64plus-rsp-cxd4.dylib"
