# NEXT (s7362): idiom-class audit - class AM, raw `rdram + <expr>` host pointer arithmetic
HYPOTHESIS-ID: host-rdram-raw-offset
Context: s7361 closed class AL: MEM_x / TO_PTR with sign-extended bases cannot leave librecomp's 4 GB reservation (512 MB RW);
the hole was zero-extended bases (fixed, regen gate in regen_replay.sh). Raw `rdram + X` (and `&rdram[X]`, `rdram[X]`) bypasses
both protections: X is whatever the author computed.
Idiom (class AM): host code forming a host pointer as rdram + X where X is not provably in [0, 512 MB) (or [0, 8 MB) for game RAM).
Enumerate: `grep -rnE 'rdram *\+|&rdram\[|rdram\[' src lib/N64ModernRuntime/librecomp/src lib/N64ModernRuntime/ultramodern/src`
(73 `rdram +` lines) + the --gen tree (injected code) + lib/rt64 '+' lines that touch RDRAM.
Hypotheses: H-safe (every X is masked/range-checked or a constant), H-trust (unchecked but derived from a masked/known-good source:
classify the provenance), H-hole (an X a guest value can push past 512 MB: fix with a mask/range check).
Method: tools/s7362_rdramraw_census.py: per site, X provenance MASK (& 0x..), CHECKED (dominating compare within the function),
CONST, PHYS (x - 0x80000000 after a KSEG0 test), B (none). Planted controls per kind. Second line: for each B, a fork/ASan harness like
tools/s7361_zext_ctl.sh (pre escapes, post bounded). Then 260 s dd8 smoke: `env SECS=260 zsh scratch/s7326/run.zsh s7362_dd8 ''`.
Exit: PORTING-STATE s7362, CURRENT-TRUTH 27za -> closed, commit; any lib/ edit -> ./submodule-patches/export.sh first.
