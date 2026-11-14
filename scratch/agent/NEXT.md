# NEXT (s7360): idiom-class audit - class AK, unterminated guest-RAM string reads
HYPOTHESIS-ID: host-guest-string-read
Context: s7359 closed class AJ (unbounded string copies; census tools/s7359_strcopy_census.py, helper src/main/rs64_apf.h,
control tools/s7359_apf_ctl.cpp). Next idiom in the same family: host code that reads a GUEST string (rdram bytes, ^3
byte-swapped, possibly unterminated or pointing at junk) with an unbounded scan.
Idiom (class AK): in host C++ we own (src/, lib/N64ModernRuntime/{librecomp,ultramodern}/src, our lib/rt64 '+' lines, fixup-
injected C): `%s` / strlen / strcmp / strchr / std::string(ptr) / fputs applied to a pointer into rdram (TO_PTR, rdram + x,
MEM_B loops without a cap), and byte loops `while (MEM_BU(..)) ++i` with no length cap or no top-of-RAM check.
Hypotheses: H-safe (every guest string read is length-capped and range-checked), H-diag (only env-gated diagnostics scan
unbounded), H-overrun (a default-on path scans past rs64_ram_top / reads ^3-unswapped text: fix with a capped copy).
Method: tools/s7360_gueststr_census.py; classify CAPPED (explicit i < N and address < ram_top) / G / B / ?; controls as s7359.
Second line: for each B, plant an unterminated string at the end of guest RAM (a test lever in a separate build dir or an
ASan build) and show pre-fix over-read vs post-fix bounded. Then 260 s dd8 smoke: `env SECS=260 zsh scratch/s7326/run.zsh s7360_dd8 ''`.
Exit: PORTING-STATE s7360, CURRENT-TRUTH item 27y -> closed, commit.
