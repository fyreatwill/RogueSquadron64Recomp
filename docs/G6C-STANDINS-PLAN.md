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

## Step 2 result (s7623)

Landed as designed with option 1 (top 1 MB of the spill arena): convertMat3x4ToN64Mtx's only caller, traverseSceneGraphRecursive,
converts a stack copy into `*0x8011DC5C`, so the RSP never reads the instance. L1 dd2: `[standins] 47 objects, 47 KB` (80 items:
25 without a model name, 8 probe droids dropped, 0 names unresolved), ~22 submits per frame; dd1 off; dd4 tog alternates. 3/3 arms
alive, 0 stalls, clean frames. PORTING-STATE s7623.

## Step 3 result (s7624): H-culled — the plan's far-plane assumption was wrong

`ROGUESQ_STANDINS=frame` (alternate submit calls) + `ROGUESQ_STANDINS_DUMP=40:46:90` (fb dumps every swap: window 1 toggling,
window 2 forced off), L1 and L4 dd4 FPS60 16:9, scored by tools/s7624_flicker_score.py (synthetic 6x6 flicker control PASS on both).
- addNpcToVisibilityBucket returns 1 only when transformVec3ToNpcLocalWithScale passes and the node is linked (linked list, no cap).
  Accepted: L1 93 of 40018 submits, L4 361 of 151825 (0.2%). Of later spawns, 2/9 (L1) and 10/59 (L4) were ever accepted first.
- Flicker per triplet, toggle vs forced-off: L1 3879 vs 4351, L4 1807 vs 2207: no excess; no persistent hot pixels.
- "Risks: our far plane ... no port of upstream's far_check is needed" (above) is refuted. Upstream hooks the same test at
  0x8001E078 (far: $f0 *= dd for render callers) and 0x8001DCEC/0x8001DD38 (the +-125 camera-space box, constants 0x8000093C /
  0x80000940, widened by dd), and keeps translations past convertMat3x4ToN64Mtx's fixed-point reach through RT64's HLE far-matrix
  table. That last part is the HLE dependency the H-portable reading missed: on our LLE path a widened box would overflow the
  N64 matrix. Our dd bundle widens neither bound (only s7134 widens the x half-extent under ASPECT).
Next (step 3b): per stand-in call, log which bound rejects (box low/high, far, frustum side) and the camera-space distance; then
widen only for stand-in calls (flag around our mips_call). Box overflow candidate for LLE: draw a far stand-in at
cam + (p - cam)/k with scale 1/k (same projection, inside the matrix reach), checking depth against terrain.

## Step 3b result (s7625): H-far; the bucket now accepts, the draw path does not draw

tools/apply_s7625_viewtest_reason.py tags each of the 21 exits of transformVec3ToNpcLocalWithScale; while rs64_vt_on (our call
only) the host tallies `[standins-why]`. Exits sum to calls (instrument fires on every path). View near 0.117, far 30.8 (L1) /
27.8 (L4) at dd4 = retail object far; box consts +-125. Stand-ins at camera distance 40-110 (median 67 L1, 85 L4).
| run (130 s, dd4) | calls | behind | far | side | box | pass |
|---|---|---|---|---|---|---|
| L1 retail far | 42796 | 16126 | 18325 | 6660 | 1534 | 151 |
| L4 retail far | 161033 | 61471 | 53368 | 39641 | 5794 | 759 |
Fix (tools/apply_s7625_standins_far.py): after the far load at 0x8001DD9C / 0x8001E074, $f0 *= rs64_vt_farmul, which the host sets
to ROGUESQ_STANDINS_FAR (default dd) around its own addNpcToVisibilityBucket call only. Box runs before far on the radius path, so
a widened far cannot pass anything past the fixed-point reach. Same-run tog: L1 pass 0.41% -> 29.6%, L4 0.47% -> 24.2%.
Note: `added` ~= 2 x pass: addNpcToVisibilityBucket also accepts via 0x80057D28 -> 0x80057E74 without the test (code read).
Pixels with far on (frame toggle + dumps): no flicker excess, L1 4068 vs 4206 off, L4 1813 vs 2129, control PASS, hot px 0,
with 294 / 255 accepts in the toggling window. So accepted stand-ins draw nothing: the next limit is after the bucket.
Next (step 3c): selectMeshLodAndSubmitForRender. Upstream (toml_hooks.c) skips the per-frame flag toggle at 0x80058264 and
re-scales the instance matrix at 0x80058304 for objects past the stock far ($f22 -> $f22 + $f20) - i.e. the game shrinks the
mesh scale toward 0 at its far plane. Log per stand-in in that function: $f22, $f20, LOD chosen, submit or not.

## Step 3c result (s7626): stand-ins reach the display list; earlier pixel nulls had no stimulus

Stand-ins do not use selectMeshLodAndSubmitForRender (only probe droids do), so the upstream 0x80058264/0x80058304 hooks do not apply.
tools/apply_s7626_sg_probe.py (3 parts, ROGUESQ_STANDINS_LOG=1) follows them after the bucket, with every other node as control:
- traverseSceneGraphRecursive visits and converts them (L1 81591 conversions in 130 s; camera z 42-121; packed t*2^24 <= 2.10e9 < 2^31).
- processSceneNode: their meshes carry flags 0x00100018 (prebuilt DL, the most common real-object value), so every leaf queues
  mesh+0x34 with its matrix (L13C -> LFE8) and no face renderer runs, the same as real objects of those flags.
- beginFrameDLChunk reads 100% of the queued stand-in entries (65390/65390; others 51266/51266).
The s7624/s7625 pixel windows (dumps at 40-46 s after the first submit) fell where stand-in draws are ~0 (L1 0; L4 ~60/s for 2 s);
stand-ins draw at 9-19 s. ROGUESQ_STANDINS_PULL=<D> scales a stand-in's camera-space matrix to depth D (same screen place and size)
to separate depth loss / terrain occlusion from RSP loss. Next: pixel test at 10/16 s, PULL=3 vs true depth (soak s7626_standins_pixels).

## Step 3d result (s7627): stand-ins produce RDP pixels
Soak s7626_standins_pixels (L1 dd4, STANDINS=frame, dumps 90 swaps at 10 s toggling / 16 s forced off, HOLD=150; HOLD=60 never
reached the mission). Flicker px per triplet, window 1 vs window 2: P (PULL=3) 1071 vs 107.5 (hot mask 881 px); N (true depth)
547 vs 108 (hot 36 px); C real-object control (ROGUESQ_STANDINS_CTL=1: real prebuilt-DL nodes get a zero 3x3 on off-arm calls in
window 1, ours never added) 180891 vs 107.5. Synthetic control PASS in all arms; window-1 stand-in draws 1547-1558/s (P), 900/s (N).
So the RSP/RDP path draws them, at true depth too; terrain occlusion makes the true-depth footprint smaller. Next: step 3 proof sheet.

## Step 3 proof (s7628): stand-ins are visible early, by eye, on two levels
Recipe scratch/s7628_standins_proof.sh (g1e harness, HOLD=150, STANDINS=frame, dumps 10/16 s): arms L1 dd2, L1 dd4, L4 dd2, L4 dd4,
4/4 alive, 0 fatal, vi_stalls30s=0. Flicker px/triplet window 1 vs forced-off window 2: L1 dd2 650.8 vs 44.5, L1 dd4 557.8 vs 107.4,
L4 dd2 143.1 vs 155.4, L4 dd4 1755.9 vs 161.3; synthetic control PASS in all four. Eye check with tools/s7628_standins_sheet.py
(adjacent on/off swaps, motion-rejected diff, crop on the densest 32 px cell):
- L1 dd2: a far bunker drawn in the haze at true depth (same model as the near bunker), absent in the paired frame.
- L4 dd4: a row of far city towers (up to 1949 diff px) drawn where the paired frame shows bare hills: the pop-in G6c targets.
- L1 dd4: the top pairs are cliff-texture shimmer and laser bolts, not stand-ins. s7626 N-arm (547) is the same shimmer.
- L4 dd2: no stand-in shapes; at dd2 these objects are inside the game's own spawn radius.
So the scorer's excess alone is not proof; scene shimmer that happens to alternate gives a false excess. Dumped swap n shows the
state of call n-1: stand-ins appear in the frames labelled on=0. Spawn timing ([standins-spawn], early_s >= 0): L1 10-11 items
shown 2-62 s before the game spawned them, L4 19 items 0.2-5 s. Owner sheet: docs/owner_sheet_s7628_standins_on_off.jpg.
Next: 300 s holds, STANDINS=1 dd4, all 19 levels (queued one level per recipe).


## Scorer shimmer filter (s7629)
tools/s7628_standins_sheet.py now ranks pairs by CLUSTERED diff pixels (`--cluster 16`, default; `--cluster 0` = s7628 scorer):
only pixels in 8x8 blocks with >= 16 set survive. Median clustered px per pair on the s7628 eye-labelled arms: L1 dd2 bunker 153,
L4 dd4 towers 1298, L1 dd4 cliff shimmer 0, L4 dd2 (no stand-ins) 0; raw medians were 520 / 1619 / 428 / 150, so raw L1 dd4
shimmer outscored the real L1 dd2 bunker's lower pairs. The bunker crop now lands on a 32x16 box instead of the full lower half.
Control (`--control`, synthetic 24x24 block painted into every ON frame): 44/44 pairs per arm keep >= 382 added px with the
filter vs >= 401 without it (the motion mask is most of the loss), PASS in all 4 arms. Rejected first: a window-2 (forced-off)
shimmer-cell map; window 2 is ~360 frames after window 1 and its cells did not predict window 1's shimmer (L1 dd4 kept ~500 px at
every rate/floor while the L4 towers lost up to half).
