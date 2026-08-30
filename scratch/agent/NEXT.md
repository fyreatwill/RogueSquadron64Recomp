# NEXT work unit — locate the first missing post-viewer continuation edge

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

## Resume context

Session 3304 landed the completion-aware SP-yield lifecycle. The default
matched SENT/SRET through n=100 and returned from `runMenuModelViewerScreen`;
the request-only rollback reproduced E70/E80F and the third-submit stall.
Default then returned from `waitForAnyAudioSlot` and reached
`menuOverlayInit`'s `0x800C5D30` post-wait branch with `$v0=1` and slot type
12, but never published title width 1024 in 120 seconds. Retail Session 3283
independently reaches `menuOverlayInit` return `0x800C5D94`, caller
continuation `0x8003E094`, and cinematic entry `0x800A5D80`.

## Competing hypotheses

- `H-MenuFallthroughStalls`: the port takes `0x800C5D38` but stalls in
  `getSecondaryWeaponForCraftLevel` or `zmemcpy` before function return.
- `H-MenuReturnsMainStalls`: the port reaches `0x800C5D94` and
  `0x8003E094`, but main-loop work never reaches the cinematic jal at
  `0x8003E10C`.
- `H-CinematicEntryStalls`: the port reaches the cinematic jal/entry but the
  cinematic never returns to the second menu activation/title publisher.
- `H-CoverageInvalid`: the run misses the default-arm row, pre=1/post=0
  reset, SP completion, 640 phase, viewer entry, or viewer return.

## Discriminator

Use one default build and one run with every edge in the table enabled at
once: `0x800C5D30` branch decision, `0x800C5D38`, the calls and returns at
`0x800C5D40` and `0x800C5D5C`, function return `0x800C5D94`, caller
continuation `0x8003E094`, cinematic jal `0x8003E10C`, cinematic entry and
return, and the second `menuOverlayInit` entry. Existing
`ROGUESQ_LOG_M5_CALLER_EDGE=1` already covers the menu function/branch edges;
add only the missing main/cinematic edges through the regeneration-safe fixup
script, with one phase-scoped table and a mark-every-edge positive control.

The first absent edge after a present predecessor selects one of the three
hypotheses. Cinematic return plus second menu entry without 1024 proves the
missing boundary is later and must name that successor in the same table.
Any missing positive control selects `H-CoverageInvalid`; do not interpret a
null.

## Exact commands

Inspect the existing s2046 fixup hook and add the full main/cinematic edge
table in its owning fixup script, then regenerate in the required order:

```sh
rg -n "s2046_m5_caller_edge|0x8003E094|0x8003E10C|0x800A5D80" \
  ../N64Recomp/fixup_game_funcs.py ../N64Recomp/RecompiledFuncs -g '*.py' -g 'funcs_*.c'
(cd ../rogue_squadron64 && python3 tools/make_elf.py)
(cd ../N64Recomp && ./build/N64Recomp rogue_squadron.toml)
(cd ../N64Recomp && python3 fixup_game_funcs.py)
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
  cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/s3305_postviewer_continuation/run.sh
```

The run script must start from `build/`, arm
`ROGUESQ_LOG_SP_YIELDED_AB=1`, `ROGUESQ_LOG_EVENT_WIRING=1`,
`ROGUESQ_LOG_M5_POSTWAIT=1`, `ROGUESQ_LOG_M5_CALLER_EDGE=1`, and the new
table gate, wait on edge predicates rather than elapsed animation state, and
end with SIGKILL.
