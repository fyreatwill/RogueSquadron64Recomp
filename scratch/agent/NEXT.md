# NEXT work unit (s2086)

HYPOTHESIS-ID: m5-caller-argument-provenance

## Work unit

Perform one bounded caller/callee ABI provenance audit for the active
`0x800903F0` edge. First run a fresh retail oracle capture with the whole-RDRAM
positive control and caller/callee PC watches; then inspect the generated MIPS
and companion mapping for `0x800903F0` and `0x8008FAAC`. Do not add a port
instrument, build, or runtime behavior change in the first arm. Determine what
the caller places in `a1`/`a2`, what the callee actually consumes, and whether
the seven out-of-range source intervals are expected non-DRAM arguments, a
mislabeled field, or corruption at the call boundary.

## Competing hypotheses and discriminator

- **H-LegitimateNonDramArgs** — the active caller deliberately passes scalar,
  tag, or string-word values in `a1`/`a2`; the source witness's `a1_dram`
  label is semantically wrong for this call.
- **H-CalleePointerContract** — the callee consumes `a1` as a DRAM/RDRAM
  pointer and `a2` as a byte count, so the caller's raw values are invalid at
  the call boundary and the upstream writer is the open boundary.
- **H-AlternateRegisterContract** — the generated signature or mapping assigns
  the source pointer to another argument/register, so the current witness is
  logging the wrong field even though the call's real pointer is valid.

The discriminator is one static crosswalk table with caller instruction,
register value, callee parameter use, companion-symbol meaning, and retail
PC-hit control. If the callee uses `a1` only as a scalar/tag and retail reaches
the same caller/callee PCs, select H-LegitimateNonDramArgs. If the callee
dereferences `a1` as a source pointer while the caller computes the observed
wild values, select H-CalleePointerContract. If the callee's pointer use is in
another register/parameter, select H-AlternateRegisterContract. A missing
retail PC hit is unevaluable unless the whole-RDRAM control and the expected
title/hangar VI phases both fire.

## Ground truth and exact commands

Read `tools/oracle/README.md` before driving the oracle. Run the fresh retail
control from the repo root (adjust only the two external paths if needed):

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --secs 65 --watch-write 0x0:0x800000 \
  --watch-pc 0x800903F0:0x800903F4 \
  --watch-pc 0x8008FAAC:0x8008FAB0 \
  --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  > scratch/agent/s2086_oracle/run.log 2>&1
```

The oracle must report whole-RDRAM hits, a title `1024 @ 0x00790400` VI, a
hangar `512 @ 0x006AB400` VI, and caller/callee PC hits before the crosswalk
is interpreted. Locate the generated and mapping sites without reading large
files wholesale:

```sh
rg -n -C 12 '800903F0|8008FAAC|fillSampleStreamRange' RecompiledFuncs syms docs tools
```

No wait, guard, task, canary, gate, output-routing, or host behavior change is
authorized. If the static crosswalk cannot distinguish the three hypotheses,
stop and write the evidence table into this file rather than adding another
diagnostic field.
