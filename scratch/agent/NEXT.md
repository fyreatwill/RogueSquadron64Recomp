# NEXT work unit (s1921) — why L_80018264 never runs a 4th time

HYPOTHESIS-ID: vi1024-guest-never-requests

s1920 selected H-advance-dead: after the second
`took_swap=1` (`#5+#6`), `advanceVideoFrame` never
re-enters `L_80018264`. The `0x80128EAD` / `$s0` table
is not the gate. Do **not** re-run a reachability-only
`s790`. Do **not** rename `func_800F7130` — item 1 still
has a live discriminator. Ask (b) is still human-only.

## Work unit — entry vs exit vs prologue after #6

Sole caller is `runVideoFrameTick` `jal 0x8001818C`
(`funcs_0.c`). After swap the same call still runs
`initVideoSubsystem`, `buildAndRegisterDefaultMaterial`,
optional `buildMaterialFreeList` / `loadDebugAssets`,
then returns. Three hypotheses, one instrument:

- H-not-called: the `n=3` call returns; `runVideoFrameTick`
  never jals again. SELECTS: stall is in the caller
  (or its scheduler) after `#6`.
- H-stuck-post-swap: the `n=3` call never returns
  (blocked after `#6` in the init/material tail).
  SELECTS: stall is inside that third `advanceVideoFrame`.
- H-stuck-prologue: a 4th call enters but never reaches
  `L_80018264` (blocked on the opening `osRecvMesg` /
  `waitOnVideoQueue` / arbiter). SELECTS: stall is the
  pre-loop waits.

**Discriminating measurement**

Keep the existing `[avf-gate]` loop/B0/swap rows. Add
`site=entry` at function start and `site=exit` at the
`jr $ra` (`L_80018434` / `return`). Same tag, same
`ROGUESQ_LOG_VI_CALLERS` gate, same `n` counter.
Put both in `N64Recomp/fixup_game_funcs.py` (generated
`funcs_4.c`). One build, one s790-shaped run with
`PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180`
(`scratch/agent/s1920_avf_gate.sh` recipe).

Same-run positive control: `site=entry` and `site=exit`
must both fire on the first two calls (`#2+#3` / `#5+#6`
already proved those return), and `site=swap took_swap=1`
must appear twice. Then read the post-`#6` counts:

- entry=3, exit=3, loop=3 → H-not-called
- entry=3, exit=2, loop=3 → H-stuck-post-swap
- entry>=4, loop=3 → H-stuck-prologue

Do not add a second counter family. This run may or may
not issue `#7/#8` (s1920 lacked them; s1919 B had them);
either is evaluable for this table.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect` (TOML
`0xB44` already matches generated `rom_size`; no bump).
Four-step already complete in s1906–s1917.

## Do not repeat

- Naming the `#10` osViSetMode site (s1919) — closed.
- The `0x80128EAD` / `$s0` swap-gate table (s1920) — closed.
- The s844-HEAD full code-content audit (s1890) — closed.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed.
- H3a-lowpower (s1902) — closed.
- `vi1024-early-crash-not-stall` (s1918) — closed.
- A same-recipe `s790` run with no new measurement axis.
- Ask (b) from s1891 — still human-only.
