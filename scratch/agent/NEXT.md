# NEXT work unit (s2064)

HYPOTHESIS-ID: m5-audio-image-output-contract

## Work unit

Perform one bounded static audit of the generated Factor 5 image-task return
and reserved-DMEM contract. Determine whether any generated image-task store
can reach the `0xF80..0xF8F` canary gap, and which generated return edge
produces `RspExitReason::Broke`. Cross-reference the fixup anchors that add
task caps or return handling. Do not add a runtime guard, skip, or guest
behavior change; this is an origin audit for the s2063 canary/exit result.

## Competing hypotheses and discriminator

- **H-CanaryLegitimateTaskOutput** — generated image code intentionally writes
  the reserved DMEM gap or uses it as task output, and its reachable natural
  `Broke` edge is part of the guest task contract. The canary failure is
  legitimate task semantics.
- **H-CanarySyntheticCap** — a fixup-injected cap/return path (including the
  known image-task return anchors) causes the observed `Broke` and canary
  result; no generated guest store owns the gap.
- **H-CanaryDmaOrStagingAlias** — generated pointer arithmetic or the initial
  ucode-data DMA reaches the gap because the task layout or address conversion
  is wrong, without an intentional reserved-gap store.
- **H-RouteUnevaluable** — the generated source, fixup anchors, or effective
  address flow cannot be classified exhaustively; do not select a theory or
  add a mitigation.

The discriminator is an exhaustive source-level table of every generated
DMEM store whose evaluated address/span could overlap `0xF80..0xF8F`, every
`return RspExitReason::Broke`, and the fixup source/anchor responsible for each
reachable edge. An explicit or proven indirect gap store paired with the
natural return selects H-CanaryLegitimateTaskOutput. No generated gap store,
with the canary/return introduced only by fixup or host task framing, selects
H-CanarySyntheticCap. A gap-reaching DMA/pointer path selects
H-CanaryDmaOrStagingAlias. Missing effective-address proof selects
H-RouteUnevaluable.

## Exact commands

Use the already-built generated source; do not regenerate or run a soak for
this static unit. Read only bounded windows and preserve the command output:

```sh
rg -n 'RSP_MEM_(B|H|W)_STORE|RSP_MEM_(B|H|W)\(|0xF8[0-9A-F]|0xFC0|return RspExitReason::Broke|L_1090|L_10E8|L_1328|break' \
  build/factor5_ucode/factor5_ucode_b_recompiled.c
sed -n '1,220p' build/factor5_ucode/factor5_ucode_b_recompiled.c
sed -n '500,555p' build/factor5_ucode/factor5_ucode_b_recompiled.c
rg -n 'L_1090|L_10E8|canary|source_end|RspExitReason::Broke|0xF80' \
  tools/fixup_factor5_ucode.py lib/N64ModernRuntime/librecomp/src/rsp.cpp
git diff --check
```

The audit must report the effective DMEM destination for every store, not
just literal matches. If the table cannot distinguish a generated store from
host canary framing, stop with H-RouteUnevaluable. ORIGIN: s2063 established
zero-only image-DMA/PCM joins; this unit attributes the remaining canary and
`Broke` behavior without changing runtime behavior.
