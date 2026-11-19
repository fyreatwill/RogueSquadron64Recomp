# G6c far-object stand-ins — design (s7621)

Owner request 2026-11-18: port upstream's draw-only stand-ins (MikeSemicolonD `origin/main:src/game/static_standins.cpp`,
428 lines) so buildings, turrets and ground units the game has not spawned yet stop popping in at draw distance > 1.
Read-only reference: `git show origin/main:<path>`. Never merge or cherry-pick.

## What upstream does (cited)

- One hook: `rogue_squadron.toml` `[[patches.hook]] func = "runInMissionFrame" before_vram = 0x800FAC68` ->
  `rs64_th_runInMissionFrame_800FAC68` (toml_hooks.c:640) -> `rs64_standins_submit(rdram, ctx)` (static_standins.cpp:362).
- `rs64_standins_submit`, once per mission frame, after the render broadcast:
  1. Returns unless `rs64_draw_dist() > 1.0` and the level DAT pointer `*0x801375D8` is a guest pointer.
  2. **Rebuild** on a new DAT, a new level `*0x80130B70` or a restart (mission frame `*0x8013889C` goes back): for every DAT item
     (`dat+0` count, `dat+4` list), pick the model name (item `+0x5C` for 8 subtypes, else a per-subtype table of 30 string
     addresses in the handlers' rodata `0x800A6A40..0x800A8890`, `0x8003D518`), find the loaded model in the meshdef hash
     (`0x801394B0` 25 u16 chain heads, `0x80139020` 12-byte entries; same walk as walkMeshdef0List 0x80056EB0), and build in a
     **host region** a 0x50-byte prop state block (pose from item `+0x10..+0x24`, composeEulerRotationXYZ 0x80059D78, path
     start via getLevelDatItemByName 0x80047B48 + sampleTerrainSurfaceAtWorldXz 0x80068180 for walkers/transports) plus a model
     instance (0xC header, 0x4C nodes, 0x5C leaves, root matrix by mat34CrossRowsAndCopyPos[Ptr] 0x80059B50 / 0x80059C24).
  3. **Submit**: walk the DAT grid (`*0x801375D8+0x14 * +0x18` cells, heads at `+0x1C`, entries at `*0x80136FCC`, type 3 = item
     still unspawned). For each stand-in whose item is still linked, unspawned (`item+6 == 0xFFFF`), has health at this
     difficulty (`item+0x6C + 4*(*0x80137CE4 & 3)` > 0) and passes isDatItemConditionMet 0x80065828 (skipped in cutscenes,
     `*0x80130B39`), call addNpcToVisibilityBucket 0x80057C8C(view = `*$s2`, inst, state, radius). Probe droids (subtype 0x0E)
     go through selectMeshLodAndSubmitForRender 0x80058068 with a size bonus instead.
- Nothing the game reads is written: all writes go to the host region (upstream `RS64_HR_STANDINS` 0x80A5C000..0x80B00000).

The other two upstream hooks the G6 brief names (selectMeshLodAndSubmitForRender 0x80058264 / 0x800582F0) are **not stand-in
hooks**: they belong to upstream's own object far-plane widening (`s_past_stock_far`, set by its view-test hook `far_check` at
0x8001E078) and keep a far-only object's model flag toggle and depth-scaled matrix out of gameplay. We do not port them (see
"risks": only the probe-droid path reaches that code, and step 2 drops probe droids).

## Design question: H-portable vs H-hle

**H-portable selected (code read, single-source until step 2 runs).** Every input is guest RAM written by the game itself (DAT,
meshdef hash, grid, difficulty, objective flags) and every output is a call into the game's own recompiled functions
(`get_function(vram)` via upstream's `mips_call`, util/mips_call.h). Nothing touches RT64 HLE state, matrices from the HLE
path, or the renderer: the stand-in enters the game's visibility bucket and is converted to a display list by the game's own
setupCameraMatrices, which our LLE F5 ucode then draws like any spawned prop. H-hle would require a read of RT64 or HLE
matrix state; there is none in the 428 lines (includes: mips_call.h, rdram_words.h, host_ram_map.h, recomp.h only).

## Address check against our build (same ROM, US 1.0)

All 17 code addresses resolve to the same function entry (or the same offset) in `syms/rogue_squadron.syms.toml`:

| upstream | ours | same |
|---|---|---|
| 0x800FAC68 hook site | runInMissionFrame+0x5C4, `L_800FAC68:` in funcs_42.c, right after the `slotDispatcherIter(a1=4 render)` broadcast, before `jal linkHudNodeAndComputeScreenPos` | yes |
| 0x80057C8C addToBucket | addNpcToVisibilityBucket+0 | yes |
| 0x80058068 selectLod | selectMeshLodAndSubmitForRender+0 | yes |
| 0x80059D78 / 0x80059C24 / 0x80059B50 | composeEulerRotationXYZ / mat34CrossRowsAndCopyPosPtr / mat34CrossRowsAndCopyPos | yes |
| 0x80065828 / 0x80047B48 / 0x80068180 | isDatItemConditionMet / getLevelDatItemByName / sampleTerrainSurfaceAtWorldXz | yes |
| 0x8004736C (comment) | updateActiveGridCellState+4 (ours starts 0x80047368) | yes (comment only) |
| data 0x801375D8, 0x801394B0, 0x80139020, 0x80137CE4, 0x80136FCC, 0x80130B39, 0x80130B70, 0x8013889C, rodata 0x800A6A40.. | same ROM, BSS/rodata layout identical | to be proven in step 2 (the rebuild's "[standins] N objects" count > 0 is the control) |

`get_function` exists in our librecomp (overlays.cpp:965, `extern "C"`), and the generated code already uses `LOOKUP_FUNC`, so
`mips_call` works unchanged.

**What differs: host memory.** Upstream's region 0x80A5C000..0x80B00000 is ours to lose: at dd>1 our bundle (main.cpp, modelled
by tools/s7336_host_arena_table.py) sets guest top 0x80C00000 (OSMEM 12), DL pool 0x80C00000..0x81000000, spill
0x81000000..0x81800000 = rs64_ram_top (librecomp RAMTOP 24 ceiling). No free byte. Options, in order:
1. **Carve the top 1 MB of the spill arena** (0x81700000..0x81800000, spill cap 7 MB while STANDINS=1), add it to the s7336 table
   as arena "standins". Safe only if (a) nothing the RSP reads lives there, and (b) spill peak < 7 MB at dd4.
2. If (a) fails (setupCameraMatrices emits a pointer to the instance's node matrix rather than copying it into the DL pool, so the
   RSP would read > 16 MB): carve 1 MB from the bottom of the DL pool (0x80C00000..0x80D00000) instead, below the 24-bit span.
Step 2 decides with one read of the bucket->DL conversion (convertMat3x4ToN64Mtx 0x80018DEC's destination) plus a DL scan for
any address in the region.

## Hook mapping onto our pipeline

- New host file `src/main/rs64_standins.cpp`: upstream's logic, with `rs64_draw_dist()` replaced by our parsed
  `ROGUESQ_DRAW_DISTANCE` (the dd bundle sets it), `rs64_snapshot_add_range` and `rs64_npc_draw_only_mark` dropped (upstream
  save-state/replay; we have neither), and the region from option 1/2. Gate `ROGUESQ_STANDINS=1` AND dd > 1; otherwise the
  function returns before any read.
- New `tools/apply_s76xx_standins.py`: inserts `rs64_standins_submit(rdram, ctx);` (guarded by a cached `rs64_standins_on()`)
  directly after the `L_800FAC68:` label in runInMissionFrame, so both the broadcast path and the `beq` skip path run it, exactly
  like upstream's before_vram hook. Idempotent marker, asserts the anchor once; appended to `RS64_REPLAY` in
  tools/fixup_game_funcs_vendored.py (docs/REGEN-VERIFY.md rule: RS64_REPLAY only, never inline).
- dd1 / STANDINS unset: the inserted call is one cached-bool test; retail untouched.

## Risks to measure in step 2

- **Bucket capacity (L-budget).** addNpcToVisibilityBucket has a fixed bucket; extra entries could push real objects out.
  Count bucket fill per frame on/off.
- **FPS60.** runInMissionFrame runs per game tick; at FPS60 the submit runs twice as often, which is right (one submit per
  rendered frame). Confirm with a per-frame submit counter == render broadcasts.
- **Our far plane.** Our dd scales the camera far (apply_s6031_far / s7310 cap 32767), so the stock view test already passes far
  objects; a stand-in culled by it is a correct cull. No port of upstream's far_check is needed.
- **Probe droids**: dropped in step 2 (they need selectMeshLod and upstream's 0x80058264/0x800582F0 gameplay-protection hooks).
- **Double draw**: a stand-in whose item spawns the same frame. Upstream's grid-link + `item+6` tests cover it; verify on/off
  frames show no doubled object at the spawn moment.

## Steps

1. (s7621) This doc.
2. Implement hook + region (decide option 1/2 first), opt-in. In-run positive control: `[standins] N objects, K KB` with N > 0
   and a per-second submitted count > 0 at dd2 on L1, and 0 calls at dd1 in the same build. Bucket fill and spill peak logged.
3. Same-run on/off frames (`ROGUESQ_STANDINS=tog` alternating mach seconds, phase-gated) at dd2 and dd4 on 2+ levels: object
   pixels at distance before the real spawn, no doubling.
4. 300 s holds on all 19 levels with it on (soak queue), then an owner sheet. Owner decides default at dd>1.
