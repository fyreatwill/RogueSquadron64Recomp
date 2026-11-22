#!/bin/zsh
# s7815: copy cxd4 to <out> and fix the five VU defects the s7815 harness found (ours == CEN64 on all five).
# The rs64-oracle tree is never modified. usage: zsh patch_cxd4.sh <out_dir>
set -e
SRC=${CXD4:-$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4}; O=${1:?out dir}
rm -rf $O; mkdir -p $O; cp -R $SRC/. $O/; rm -f $O/projects/unix/*.o(N) $O/projects/unix/*.dylib(N)
V=$O/vu
# scalar (non-SSE) cxd4 path only: the SSE path shares the select/add helpers but has its own multiply clamps.
FIX=${FIXES:-12345}   # subset of fixes to apply (ablation), default all
# 1 VMADN/VMADL (SIGNED_CLAMP_AL): clamp iff ACC is outside s32 (ACCH != sign of ACCM), not "clamped ACCM != raw ACCM",
#   which misses out-of-range lanes whose raw ACCM already equals 0x7FFF/0x8000.
[[ $FIX == *1* ]] && perl -0pi -e 's/cond\[i\] = \(temp\[i\] != VACC_M\[i\]\);/cond[i] = (VACC_H[i] != (VACC_M[i] >> 15));/' $V/multiply.c
# 2 VCR: merge() computes fail + cmp*diff and needs cmp in {0,1}; do_cr passed sn in {0,-1} (do_ch converts it with >>15).
[[ $FIX == *2* ]] && perl -0pi -e 's/(VC\[i\] \^= sn\[i\]; \/\* if \(sn == ~0\) \{VT = ~VT;\} else \{VT =  VT;\} \*\/\n    merge\(cmp, sn, le, ge\);)/VC[i] ^= sn[i];\n    for (i = 0; i < N; i++) sn[i] = (u16)(sn[i]) >> 15;\n    merge(cmp, sn, le, ge);/' $V/select.c
# 3 VMRG clears VCO
[[ $FIX == *3* ]] && perl -0pi -e 's/(INLINE static void do_mrg.*?vector_copy\(VD, VACC_L\);)/$1\n    vector_wipe(cf_ne);\n    vector_wipe(cf_co);/s' $V/select.c
# 4 VABS: only vs<0 && vt==0x8000 saturates, and only vd (ACCL keeps the wrapped 0x8000)
[[ $FIX == *4* ]] && perl -0pi -e 's/(res\[i\] \*= nez\[i\];\n)    for \(i = 0; i < N; i\+\+\)\n        res\[i\] -= cch\[i\];\n    vector_copy\(VACC_L, res\);\n    vector_copy\(VD, VACC_L\);/$1    vector_copy(VACC_L, res);\n    for (i = 0; i < N; i++)\n        res[i] -= cch[i] & neg[i];\n    vector_copy(VD, res);/' $V/add.c
# 5 VCH: the cxd4 cch hack keeps -(-32768) at 0x7FFF and threads through eq/le; replaced by a CEN64 transcription
[[ $FIX == *5* ]] && python3 - $V/select.c <<'PYEOF'
import sys
p = sys.argv[1]; s = open(p).read()
a = s.index('INLINE static void do_ch('); b = s.index('INLINE static void do_cr(')
body = """INLINE static void do_ch(pi16 VD, pi16 VS, pi16 VT)
{ /* s7815: scalar transcription of CEN64 rsp_vch (arch/x86_64/rsp/vch.h); -(-32768) wraps to 0x8000 */
    register unsigned int i;
    for (i = 0; i < N; i++) {
        i16 sn = ((VS[i] ^ VT[i]) < 0) ? ~0 : 0;
        i16 nvt = (i16)((VT[i] ^ sn) - sn);
        i16 diff = (i16)(VS[i] - nvt);
        int dz = (diff == 0), vtn = (VT[i] < 0);
        int ge = sn ? vtn : (diff >= 0);
        int le = sn ? (diff <= 0) : vtn;
        int vce = sn && (diff == -1);
        VACC_L[i] = (sn ? le : ge) ? nvt : VS[i];
        VD[i] = VACC_L[i];
        cf_clip[i] = ge; cf_comp[i] = le; cf_ne[i] = !(dz | vce); cf_co[i] = sn ? 1 : 0; cf_vce[i] = vce;
    }
}

"""
open(p, 'w').write(s[:a] + body + s[b:])
PYEOF
[[ $FIX == *1* ]] && cmp -s $SRC/vu/multiply.c $V/multiply.c && { echo "fix 1 did not apply"; exit 3; }
[[ $FIX == *4* ]] && cmp -s $SRC/vu/add.c $V/add.c && { echo "fix 4 did not apply"; exit 3; }
[[ $FIX == *[235]* ]] && cmp -s $SRC/vu/select.c $V/select.c && { echo "fix 2/3/5 did not apply"; exit 3; }
true
echo "patched cxd4 -> $O"
