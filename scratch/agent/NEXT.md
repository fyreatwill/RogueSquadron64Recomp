# NEXT work unit (audit the 640-only direct mode state)

HYPOTHESIS-ID: m3-vi640-transition-writer

The s804 same-run trace fired all three reachable direct callers, but every
post-640 request was width 640 and the selector route stayed silent. Do one
bounded read-only source audit before adding another instrument: enumerate
every writer and gate for `0x80128E40`, `0x80128E90`, `0x80128DF0`, and
`0x80128C90`, then identify the smallest state predicate that could prevent a
1024 row from reaching a direct caller.

## Competing hypotheses

- H-mode-buffer-writer: a direct buffer is initialized or overwritten with a
  640-only OS_VI_MODE row on this recipe. Prediction: a concrete store/copy
  site writes the 640 row after the 1024-capable table is available.
- H-state-gate: the direct callers are given the right buffer, but a pending
  flag or state byte prevents the 1024-producing branch. Prediction: one
  conditional around the direct call has a state byte/word with a reachable
  640-only value and no later writer in the tested path.
- H-missing-dispatch: a call or return path that would publish the 1024 mode is
  absent or mis-dispatched before the direct callers. Prediction: source shows
  a distinct 1024-producing caller/return path that cannot reach any of the
  three traced sites.

## Discriminating measurement

The audit's writer/gate map is the discriminator: a post-table 640 store
selects H-mode-buffer-writer; a live conditional with no 1024-producing write
selects H-state-gate; a distinct unreachable 1024 publisher selects
H-missing-dispatch. Do not build until the audit names one concrete site and
its positive control.

## Exact commands

```sh
rg -n -S "80128C90|80128DA0|80128DF0|80128E40|80128E90|osViSetMode_recomp|viMode|pendingVi|716C|7170" \
  ../N64Recomp/RecompiledFuncs/funcs_4.c ../N64Recomp/RecompiledFuncs/funcs_5.c \
  ../N64Recomp/RecompiledFuncs/funcs_*.c src
rg -n -S "0x80128C90|0x80128DA0|0x80128DF0|0x80128E40|0x80128E90" \
  ../rogue_squadron64 ../N64Recomp docs
```

If a concrete writer is found, the following unit must add one batched,
regeneration-safe marker at that writer and retain `osViSetMode`, selector,
and oracle whole-RDRAM/VI positive controls. Use `PROBE_PHASE_WIDTH=640`
and `PROBE_LEAVE_OK=1`; never compare animating scenes by stopwatch.
