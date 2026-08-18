# NEXT work unit (s1919) — who issues osViSetMode 1024

HYPOTHESIS-ID: vi1024-guest-never-requests

s1918 closed `vi1024-early-crash-not-stall` (H3 SELECTED).
Do **not** re-run `s790_postsec2_reachability.sh` as a
reachability re-confirm. Do **not** rename `func_800F7130`
this iteration unless this unit is blocked — the 15-title
window now contains s1918, so the sweep is allowed but item 1
has a live discriminator. Ask (b) is still human-only.

## Work unit — name the s844 1024 osViSetMode caller

s844 publishes 1024 via `[osViSetMode #10] mode_ptr=0x80128DA0
type=0x08000000 ctrl=0x0000324E width=1024` at 79.6s /
`update_screen #4715`, immediately after `#8` (same
`0x80128E40` 640 yScale `0x02000612`) and `#9` (width 2).
The two 180s stallers (173130, 180331) fire that same `#8`
descriptor at ~45s / `#2816` and then never issue `#9`/`#10`.

Competing hypotheses (discriminated by naming the caller and
checking whether it is entered in a staller; prefer offline
+ one existing-log grep before any new run):

- H-never-entered: the function that issues width=1024
  `osViSetMode` is never called in 173130/180331. SELECTS:
  the stall is upstream of the VI submit (scene/state never
  reaches the transition).
- H-entered-640: that function runs in the stallers but
  submits width 640 (the `#8` precursor) and does not take
  the 1024 branch. SELECTS: the caller is live; the 1024
  argument/selector is not.
- H-host-drop: guest writes a 1024 descriptor and calls
  `osViSetMode_recomp`, but the existing `[osViSetMode]`
  log misses it. SELECTS only if a new same-run control
  shows s844 `#10` *and* a staller `#10` that the old logs
  lacked — currently weak, because stallers already log
  `#1–#8` on the same channel that recorded s844 `#10`.
- H-s844-env-only: s844's 16 `osViSetMode` lines are an
  env/recipe difference, not a guest-behavior difference.
  REFUTED if stallers' `#1–#6` match s844's `#1–#6`
  descriptors (they do — s1918 table).

**Discriminating measurement**

1. Offline, no new run first: find the host log site for
   `[osViSetMode` and every guest caller of
   `osViSetMode` / `osViSetMode_recomp`. Record whether the
   current log line already carries `ra` / guest PC. If it
   does, grep s844 for `#10`'s ra and grep 173130/180331
   for that same ra/function.
2. Only if the log line has no caller: add `ra` (and guest
   PC if cheap) to that one fprintf, one build, one `s790`
   run. Same-run positive control: the new field must appear
   on boot `#1` width=320 *and* on the `#6` 640/`0x80128DA0`
   line. Then read whether a later `#10` width=1024 appears
   (regression healed) or the run matches 173130 (`#8` then
   silence) and report the last caller's ra.

Do not add a second counter. The caller identity is the
whole table.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect` (TOML
`0xB44` already matches generated `rom_size`; no bump).
Four-step already complete in s1906–s1917.

## Do not repeat

- The s844-HEAD full code-content audit (s1890) — closed.
- The `ROGUESQ_SKIP_HANGAR_PROBE` A/B (s1890) — closed.
- H3a-lowpower (s1902) — closed.
- `vi1024-early-crash-not-stall` (s1918) — closed: H3
  selected, H1/H2/H4 refuted. Do not rebuild the `[phase]`
  timeline.
- A same-recipe `s790` run with no new measurement axis.
- Ask (b) from s1891 — still human-only.
