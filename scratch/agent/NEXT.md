# NEXT (s7648)
HYPOTHESIS-ID: mk8-key-alias-audit

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7647 closed TS-4 as an artefact: the instrument keyed RDRAM addresses `& 0x7FFFFF` while dd>1 data lives above 8 MB (RSP mask
0x1FFFFF8). Class MK8 (idiom-class audit, ladder item 3 model): every other 8 MB-masked address key/lookup in our host code may
alias the same way at dd>1 -- in diagnostics (false conclusions) or, worse, in behaviour (wrong guard/lookup).
Work unit (offline first):
1. Enumerate: `grep -n -e '0x7FFFFFu' -e '0x007FFFFFu' src/main/main.cpp src/rsp/dpc_bridge.cpp src/main/rt64_render_context.cpp`
   (127 sites at s7647) plus lib/ (`grep -rn 0x7FFFFF lib/N64ModernRuntime lib/rt64/src | grep -v third_party`).
2. Classify each: (a) default-on behaviour vs diag-only; (b) can its input be >= 0x80800000 / phys >= 8 MB at dd>1 (DLPOOLX arena,
   OSMEM 12 heap, spill arena, wide FB)? (c) alias consequence. Write the table into docs/MK8-KEY-ALIAS-CENSUS.md.
3. Any default-on site that can alias: fix to the 25-bit physical key (rs64_s7327_mask semantics), =0 restores old, with a same-run
   positive control (a planted read above 8 MB that the old key would alias). Diag sites: fix or annotate.
Hypotheses: H-mk8-diag-only (all aliasing sites are diagnostics; 0 behaviour fixes) vs H-mk8-live (a default-on lookup aliases at
dd>1, a candidate for G5b drops).
Rules: never launch under lldb; never touch build/saves; one game at a time; SIGKILL only; pre-create R dirs for g1e_owner_quiet_arms.
