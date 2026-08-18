# NEXT work unit (s1922) — why runVideoFrameTick never jals a 3rd time

HYPOTHESIS-ID: vi1024-guest-never-requests

s1921 selected H-not-called: `advanceVideoFrame` is
entered twice, both calls return (`entryn=2`/`exitn=2`),
then `runVideoFrameTick` never jals `0x8001818C` again.
s1920's loop `n=3` was the inner swap-wait, not a third
call. Do **not** re-run a reachability-only `s790`. Do
**not** rename `func_800F7130` — item 1 still has a live
discriminator. Ask (b) is still human-only.

## Work unit — tick entry vs jal vs exit after AVF #2

Sole function that jals `0x8001818C` is `runVideoFrameTick`
(`funcs_0.c`). Static callers of `runVideoFrameTick`
(`jal 0x80001354`): `funcs_8.c` (two sites),
`funcs_27.c`, `funcs_34.c`. After AVF call 2 returns,
three hypotheses, one instrument:

- H-tick-not-called: the 2nd `runVideoFrameTick` returns;
  no 3rd entry. SELECTS: stall is in a caller / scheduler
  after the 2nd tick returns.
- H-tick-stuck-post-jal: the 2nd tick never returns after
  AVF exits (blocked in the post-jal tail at
  `0x800014F8` / `L_800015E8`). SELECTS: stall is inside
  that second tick after the jal.
- H-tick-stuck-pre-jal: a 3rd tick enters but never jals
  `0x8001818C` (blocked in the prologue:
  `partitionFramebufferMemory` / `coalesceFreeHeapBlocks`
  / setup). SELECTS: stall is the pre-jal tail.

**Discriminating measurement**

Keep existing `[avf-gate]` entry/exit/loop/B0/swap rows.
Add `[avf-gate]` `site=tick-entry` at
`runVideoFrameTick` start (after the existing
`[frametick-top]` block, or reuse it if that env is on)
and `site=tick-exit` at `L_800015E8` / `jr $ra`, plus
`site=tick-jal` immediately before
`advanceVideoFrame(rdram, ctx);`. Same tag, same
`ROGUESQ_LOG_VI_CALLERS` gate. Put them in
`N64Recomp/fixup_game_funcs.py` (generated `funcs_0.c`).
One build, one s790-shaped run with
`PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180`
(`scratch/agent/s1921_avf_entry_exit.sh` recipe is
fine; copy to `s1922_rvft_gate.sh`).

Same-run positive control: `site=tick-entry`,
`site=tick-jal`, `site=tick-exit` must all fire on the
first two ticks (s1921 already proved those two AVF
calls return), and `site=swap took_swap=1` must appear
twice. Then read the post-AVF-#2 counts:

- tick-entry=2, tick-exit=2, tick-jal=2 → H-tick-not-called
- tick-entry=2, tick-exit=1, tick-jal=2 → H-tick-stuck-post-jal
- tick-entry>=3, tick-jal=2 → H-tick-stuck-pre-jal

Do not add a second counter family. Existing
`[frametick-top]` is gated on
`ROGUESQ_LOG_REAPPLYDISPLAYMODE_REACH` and is entry-only
— do not treat it as this table.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect` (TOML
`0xB44` already matches generated `rom_size`; no bump).
Four-step already complete in s1906–s1917.

## Do not repeat

- Naming the `#10` osViSetMode site (s1919) — closed.
- The `0x80128EAD` / `$s0` swap-gate table (s1920) — closed.
- AVF entry vs exit vs prologue after `#6` (s1921) — closed.
- The s844-HEAD full code-content audit (s1890) — closed.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed.
- H3a-lowpower (s1902) — closed.
- `vi1024-early-crash-not-stall` (s1918) — closed.
- A same-recipe `s790` run with no new measurement axis.
- Ask (b) from s1891 — still human-only.
