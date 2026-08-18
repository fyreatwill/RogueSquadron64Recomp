# NEXT work unit (s1923) — which caller issued the two ticks

HYPOTHESIS-ID: vi1024-guest-never-requests

s1922 selected H-tick-not-called: `runVideoFrameTick`
entered twice, both calls jal'd `0x8001818C` and
returned (`tickn=2`/`jaln=2`/`exitn=2`). No 3rd entry.
Do **not** re-run a reachability-only `s790`. Do
**not** rename `func_800F7130` — item 1 still has a live
discriminator. Ask (b) is still human-only.

## Work unit — name the two `jal 0x80001354` sites

Four static sites, three functions:

| site | function | guest jal |
|---|---|---|
| mgl-a | `mainGameLoop` | `0x8003E29C` (flag `0x2000000` set; overlay-0 + `applyLevelScreenAndCameraSettings`) |
| mgl-b | `mainGameLoop` | `0x8003E360` (flag clear; overlay-0 + `0x800BF358` + apply) |
| mission | `initSceneForMission` | `0x800A9C70` |
| menu | `menuOverlayInit` | `0x800C5A18` (then `clearSceneBssRegion` `0x8003DF20`, not `mainGameLoop`) |

`mainGameLoop` is a real loop (`j L_8003E114`). The two
init functions are one tick per entry.

Keep existing `[avf-gate]` tick-entry/jal/exit and
AVF entry/exit/loop/B0/swap. Add, same tag, same
`ROGUESQ_LOG_VI_CALLERS` gate, in
`N64Recomp/fixup_game_funcs.py`:

- `site=mgl-entry` at `mainGameLoop` start (do **not**
  reuse `[maingameloop-entry]` / `ROGUESQ_LOG_MAINGAMELOOP_REACH`)
- `site=mgl-jal-a` / `site=mgl-jal-b` immediately before
  each `runVideoFrameTick(rdram, ctx);`
- `site=mission-entry` + `site=mission-jal`
- `site=menu-entry` + `site=menu-jal`

Print `tickn`/`jaln` plus a per-site counter. One
build, one s790-shaped 180s run (`s1922_rvft_gate.sh`
recipe; copy to `s1923_tick_caller.sh`).

Same-run positive control: `site=tick-entry` /
`tick-jal` / `tick-exit` must still fire 2/2/2 with
`took_swap=1` twice. Then read the two tick-jal
parents:

- both ticks `mgl-jal-*`, `mgl-entry` keeps climbing
  after tick 2, no more `mgl-jal-*` → H-mgl-skip
  (loop alive, both jal branches dead)
- both ticks `mgl-jal-*`, `mgl-entry` frozen after
  the last tick → H-mgl-dead (loop not re-entered)
- both ticks `menu-jal` and/or `mission-jal`,
  `mgl-entry=0` → H-caller-init (boot inits did the
  VI setup; `mainGameLoop` never started)
- mixed init + mgl, then mgl frozen or skip →
  H-caller-mixed; follow the last parent's post-return
  counts
- `mgl-entry>=1` but zero `mgl-jal-*` on the two
  ticks → the inits issued them; mgl is alive but
  has not taken a jal yet (same table: does
  `mgl-entry` keep climbing?)

Do not add a second counter family.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect` (TOML
`0xB44` already matches generated `rom_size`; no bump).
Four-step already complete in s1906–s1917.

## Do not repeat

- AVF entry vs exit vs prologue after `#6` (s1921) — closed.
- Tick entry vs jal vs exit after AVF #2 (s1922) — closed.
- Naming the `#10` osViSetMode site (s1919) — closed.
- The `0x80128EAD` / `$s0` swap-gate table (s1920) — closed.
- The s844-HEAD full code-content audit (s1890) — closed.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed.
- H3a-lowpower (s1902) — closed.
- `vi1024-early-crash-not-stall` (s1918) — closed.
- A same-recipe `s790` run with no new measurement axis.
- Ask (b) from s1891 — still human-only.
