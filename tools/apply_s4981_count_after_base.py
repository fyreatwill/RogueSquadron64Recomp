#!/usr/bin/env python3
"""s4981: publish the song-channel voice count AFTER the voice-array base in allocateSongChannelArray.
ORIGIN: guest stores count (0x8008F0CC sh -0x6900) before rs_malloc and the base (0x8008F0EC sw -0x6908) after;
the port's mixer runs on another host thread inside that window, so count 32 meets the old 18-voice base and walks
into name-string memory (s4577/s4578/s4980: 9 kind=bad hits, index 30 -> 0x801724C0). The s147 reorder in the
upstream fixup never reached the live tree (marker absent in funcs_23.c). Moves the count store (and the lhu reload
that feeds the voiceCount==0 branch) after both pointer stores, with a release fence. Idempotent."""
import re, sys
from pathlib import Path
p = Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c")
s = p.read_text()
if "PATCH: s4981" in s:
    print("already applied"); raise SystemExit(0)
fs = s.index("RECOMP_FUNC void allocateSongChannelArray(")
fe = s.index("\nRECOMP_FUNC ", fs + 10) if "\nRECOMP_FUNC " in s[fs + 10:] else len(s)
body = s[fs:fe]
L = body.split("\n")
def idx(sub, start=0):
    for i in range(start, len(L)):
        if sub in L[i]: return i
    raise SystemExit(f"anchor missing: {sub}")
c0 = idx("// 0x8008F0C8: lui"); c1 = idx("// 0x8008F0D0: jal")      # count block [c0,c1)
r0 = idx("// 0x8008F0D8: lui"); r1 = idx("// 0x8008F0E0: lui")      # reload block [r0,r1)
e = idx("rs64_m5_lowfield_store('W', 0x8008F0ECu")
assert c0 < c1 < r0 < r1 < e, (c0, c1, r0, r1, e)
cblk, rblk = L[c0:c1], L[r0:r1]
assert sum("MEM_H(-0X6900" in x for x in cblk) == 1 and sum("MEM_HU(ctx->r3, -0X6900" in x for x in rblk) == 1
new = L[:c0] + L[c1:r0] + L[r1:e + 1]
new += ["    __atomic_thread_fence(__ATOMIC_RELEASE); /* PATCH: s4981 count published after base */"] + cblk + rblk + L[e + 1:]
p.write_text(s[:fs] + "\n".join(new) + s[fe:])
print("applied")
