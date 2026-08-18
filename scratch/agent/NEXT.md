# NEXT work unit (s1920) — why advanceVideoFrame skips swap→init after #8

HYPOTHESIS-ID: vi1024-guest-never-requests

s1919 named s844 `#10` as `advanceVideoFrame` `0x80018378` →
`initVideoSubsystem` and selected H-never-entered: the 180s
staller fires `#7/#8` as `applyPendingViChanges` and never
reaches the swap→init pair. Do **not** re-run
`s790_postsec2_reachability.sh` as a reachability re-confirm.
Do **not** rename `func_800F7130` this iteration — item 1
still has a live discriminator. Ask (b) is still human-only.

## Work unit — why the post-#8 swap→init pair never runs

s844 `#9` (width 2, only `swapBufferWithViMode`) then
`[vi-arg] 0x80018378` then `#10` (1024, `initVideoSubsystem`)
is one `advanceVideoFrame` path:

```
L_80018264: waitOnVideoQueue; $s0=0; awaitFrameSync
            *(u8*)0x80128EAD == 0  → L_800182B0
            else walk *(u8*)(0x80128EAA+$s0)
L_800182B0: signalFrameSync; bne $s0, byte, L_80018264
            jal swapBufferWithViMode          // #9
            waitOnVideoQueue; clearPending; clearPostSwap
            jal initVideoSubsystem            // #10
```

The staller already did this pair twice (`#2+#3`, `#5+#6`)
and never a third time after `#8`.

Competing hypotheses (one instrument, one 180s-capable run):

- H-advance-dead: `advanceVideoFrame` stops entering
  `L_80018264` after `#8`. SELECTS: the stall is upstream
  of the swap gate (thread parked / not scheduled).
- H-loop-no-B0: the loop keeps running but never reaches
  `L_800182B0` (table walk never takes the B0 exits).
  SELECTS: the 0x80128EAA table / `$s2=3` / `$s1=4`
  comparison is the gate.
- H-B0-mismatch: `L_800182B0` is reached but
  `$s0 != *(u8*)0x80128EAD`, so it branches back to
  `L_80018264` and skips swap. SELECTS: the byte (or `$s0`)
  is the gate.
- H-swap-ran: swap is entered after `#8` but
  `[osViSetMode]` missed `#9`. REFUTE if the new site
  field (unconditional) stays silent — already weak.

**Discriminating measurement**

One fprintf in `advanceVideoFrame` at `L_800182B0` *and*
at the `bne $s0, $v0` fallthrough, plus a loop-head
counter at `L_80018264`. Fields on one line: `n`,
`byte_0x80128EAD`, `$s0`, `took_B0`, `took_swap`.
Put it in `tools/fixup_game_funcs.py` (generated
`funcs_4.c`). Gate on `ROGUESQ_LOG_VI_CALLERS` (already
wired). One build, one s790-shaped run with
`PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180`.

Same-run positive control: the loop-head counter must
be nonzero before `#6` (the second swap+init already
proved the path is live at 6.9s) **and** the `#5+#6`
pair must show `took_swap=1`. Then read the post-`#8`
rows:

- counter freezes at `#8` → H-advance-dead
- counter climbs, `took_B0=0` → H-loop-no-B0
- `took_B0=1` and `took_swap=0` → H-B0-mismatch
  (dump byte and `$s0`)
- `took_swap=1` after `#8` → H-swap-ran; inspect
  why `#9`/`#10` are missing

Do not add a second counter family. The gate table is
the whole unit.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect` (TOML
`0xB44` already matches generated `rom_size`; no bump).
Four-step already complete in s1906–s1917.

## Do not repeat

- Naming the `#10` osViSetMode site (s1919) — closed.
- The s844-HEAD full code-content audit (s1890) — closed.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed.
- H3a-lowpower (s1902) — closed.
- `vi1024-early-crash-not-stall` (s1918) — closed.
- A same-recipe `s790` run with no new measurement axis.
- Ask (b) from s1891 — still human-only.
