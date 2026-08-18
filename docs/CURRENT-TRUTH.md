# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is in
[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger is the authority for session
detail. Reviewed through s1970 (2026-08-18).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu explanation is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Future mitigations need an `ORIGIN:` naming the writer
  and assessing legitimacy.
- Phase-gated port captures reached VI 1024 through s844 (2026-08-13). Late E9
  identity is established; remaining deltas are boundary/span-shaped. Post-s844
  recipes then stalled at 640 `0x00696100` (s1888–s1918). H1-flake, H3a-lowpower,
  and the `rs64_is_hangar_vi` toggle are refuted; no source change in the
  s844→HEAD window explains it. Ask (b) (clone + `git submodule update` bisect
  at `ef7a0fb9`) is still human-only. s1918 selected H3 true-stall: 2/8 `s790`
  logs live 180s with zero `osViSetMode width=1024` (s844 control: `#10` at
  79.6s `#4715`). Crash families kill some runs but are not why 1024 is missing.
- **1024 miss, closed through title-like 1024.** The `#10` issuer is
  `advanceVideoFrame` `0x80018378` → `initVideoSubsystem` (s1919). The swap
  loop dies after two `runVideoFrameTick` calls (s1920–s1922). Tick 1 is
  `menuOverlayInit`; tick 2 is `initSceneForMission`; `menu-entry` siten=2 then
  sits in `L_800C5930` `anyAudioSlotActive` (s1923–s1924). The 16-voice table
  at `0x8018D4A0` is a sane `allocateSongChannelArray` retarget; slot+0 `0x02`
  is `musyxRenderVoiceSamples` after key-on (s1926–s1927). Mix and VI-retrace
  both freeze at `.ovl.menu` + entry 2 (s1930–s1931). The walk after `#8`
  completes; the next `osRecvMesg(0x80114388)` blocks (s1935–s1938). Host VI
  keeps enqueueing that mq and never dequeues (s1939–s1941) because the spin
  is runnable (`beq v0==0`) so idle-wait never runs. `ROGUESQ_SPIN_YIELD=1`
  (env-gated `yield_self_1ms` every 100000 `L_800C5930` iters) unblocks recv1,
  resumes synth, and publishes `#9`/`#10` width-1024 origin `0x00790400`
  (s1942; H-spin-starves-idle). Default-off. ORIGIN: host VI retrace
  (legitimate) sits in `external_messages`; hardware would preempt the spin.
  Session-by-session table: `PROJECT-OVERVIEW.md` §36.
- **Hangar is reachable (s1949).** Extending the same env-gated
  `ROGUESQ_SPIN_YIELD` to `menuControllerInput` `L_800B8050`
  (`site=menuInput`, every 100000, default-off) unblocks post-1024 SI
  and publishes `[phase] 512 origin=0x006AB400` at 26.1s `#1496`.
  Captured frame is the hangar SELECT LEVEL / AMBUSH AT MOS EISLEY
  screen. Recipe: `ROGUESQ_SPIN_YIELD=1` + eleven-Start from boot.
  Do not default the yield on. ORIGIN: host VI/SI retrace (legitimate)
  sits in `external_messages`; this second `beq v0==0` spin is runnable
  so idle-wait never drains. Hardware would preempt.
- **First hangar window is short.** SIGBUS in `filterVoiceSampleBlock+220`
  (`last-guest-pc=0x8000834c`, the known `drainMeshReleaseQueue` return)
  ~4s after hangar. s1950 reproduced: 512 at 24.8s, gone at 4.3s after
  1 hangar frame, same symbol/`last-guest-pc`. Do not chase as a
  single crash.
- **The filterVoiceSampleBlock idiom audit selected a missing host-call link
  (s1970).** The complete generated tree has three direct callers; static
  inspection classified their source/output buffers as caller-owned, with
  the callee reading 13 halfwords from source and writing 40 bytes to output.
  The corrected hangar recipe reached the live `updateVoiceChannelParamsLarge`
  edge at `0x8009D740` after both positive controls. Its source
  `0x8011C748..762` and output `0x8011C7B0..7D8` were in RDRAM, but the
  callee's fixed selector path used `ra+0xD4+a0 = 0x000000D4` because the
  generated host call left `ctx->r31=0` instead of the guest link
  `0x8009D748`. The entry row repeated the same values and the SIGBUS followed
  at the invalid byte read. This selects H-filter-local-range: the writer is
  N64Recomp's direct `jal` lowering, and zero is not the legitimate guest
  return address. No guard or skip was added; the next M3 unit is a complete
  branch-and-link/RA-derived idiom audit, not a one-site mitigation.
- **M4 hangar/512 Y=0x8000 is not live (s1949).** On the first hangar
  capture: 2187 `L_17F0` entries, 3904 flushes, `y8000_entry=0`
  `y8000_any=0`, plus a recognizable 3D hangar frame. Do not re-walk
  VMADH/VGE / `0xD60` / the ovl20 table. Late-hangar Y is unsampled
  (crash cut the window).
- **Hangar hologram-beam artifact: H2 (malformed triangle command)
  REFUTED (s1967).** Extended the M4 `0xD60`-restage walker to check
  every flushed Fill-Triangle command's `YH<=YM<=YL` ordering, not just
  the Y=`0x8000` subset; zero degenerate (zero-height) triangles, but a
  recurring `order_bad` hit at offset `0xE80-0xEA8` with implausible
  Y/X values. A first pass couldn't tell a genuine bad write from a
  stale buffer read, so s1967 added a writer-attestation hook at the
  actual `L_1930` store site (`tools/fixup_factor5_ucode.py` Fixup 21)
  and re-ran: **all 14 sampled `order_bad` hits had `stored=0`** (never
  written this cycle) while every ordinary triangle showed `stored=1`
  (positive control confirmed live). The offending bytes are stale
  DMEM left over from the buffer's prior use, not a corrupted command
  reaching the RDP queue — `r16`'s write-pointer legitimately extends
  past what was freshly written that cycle. ORIGIN named: unwritten
  scratch memory, ruled not a writer bug, no mitigation applies. The
  oracle cannot help with the remaining hypotheses: no screenshot
  capability and RSP-HLE never executes guest `L_17F0`, so there is no
  oracle-side equivalent of the `0xD60` capture (confirmed, not
  assumed). H1 (blend/z — needs a `SETOTHERMODE` census, untested) and
  H3 (needs pixel ground truth neither side can supply) remain open.
  Full detail: `PORTING-STATE.md` s1967.
- **H1 mode-state census is out-of-scope in the `0xD60` restage buffer
  (s1968).** The corrected hangar-gated walker recognized 1,134 live
  `0xC8`-class triangles, with ordinary triangles `stored=1` as the same-run
  writer-attestation positive control, but found zero valid standard RDP
  `SETOTHERMODE_L/H` commands (`0xB9`/`0xBA`). Six header matches were
  rejected because their standard operands were impossible (`shift=81..242`,
  `size=90..211`); the first pass counted these false candidates and was
  fixed/re-run in the same iteration. Static generated-code evidence shows
  generic `L_10F4` source-word copies can populate the output buffer while
  `L_1930` emits its triangle headers, and there are no explicit `0xB9/0xBA`
  constants in the generated Factor 5 files. Therefore the null does not
  refute H1: this buffer has no valid mode command to associate with a
  triangle. ORIGIN: invalid candidates are stale/non-command bytes or copied
  source words with malformed operands; they are not legitimate mode state,
  and no mitigation applies. Next scope is the RT64 whole-RDP stream/draw
  state, not another `0xD60` opcode scan. Full detail: `PORTING-STATE.md`
  s1968.
- **Hangar hologram-beam artifact: H1 consumer-state explanation REFUTED
  (s1969, single-source).** The same-run DPC positive control saw 1,128 live
  restaged triangles and the new RT64 consumer census reached its 500-row cap
  at hangar VI 512/origin `0x006AB400`. Of 153 sampled consumer triangles whose
  bounds overlapped the captured beam-cone box, all had the same coherent
  coverage/blender state (`CVG_X_ALPHA=0`, `ALPHA_CVG_SEL=1`, `ZMODE=0`,
  `Z_UPD=1`, `blend=0x0055`); 95 had `Z_CMP=1` and 58 had `Z_CMP=0`. The
  consumer path is therefore reached and no incompatible draw mode was
  isolated. The frame visibly retains the blue beam artifact, but the oracle
  has no pixel witness for this LLE path, so H3 (the remaining pixel/coverage
  explanation) is unavailable rather than selected. No mitigation applies.
- Recurring `slotDispatcherIter+872` SIGBUS is the generated prologue spill of
  guest `$sp` at `funcs_8.c:22810`. Complete static audits found no reachable
  frame-overlapping writer. Runtime guest corruption remains open; no mitigation.
- Corrected `npcPowerGeneratorUpdate` is main `.text` at `0x80077AF0`;
  regenerated ELF, N64Recomp, fixups, and Debug target pass. Runtime boundary
  tests remain pre-1024 and unevaluable.
- M5 audio de-stubbing is closed. Audio remains stubbed. Dummy-video retail
  watches never reached `musyxInitVoiceFromSample`. Do not reopen without a new
  bounded plan using the Rice hangar recipe.
- **Generated-symbol sweep is effectively closed (s1966).** A full-file
  census found s1962–s1965 had only swept a small tail of the TOML;
  845 leftovers resolved in one batch (902 → 57 `func_8[01]*`). The
  remaining 57 all need genuine RE or are deliberate holds (live
  `patches/heap_guards.c` declarations, `build_redefs.py` reverts, one
  `PROJECT-OVERVIEW.md`-parked entry, overlay-VRAM collisions, and
  entries with no generated-tree match at all) — not a metadata-sync
  target anymore. Full detail: `PORTING-STATE.md` s1966.
- Retail oracle whole-RDRAM, scheduled PIF, and VI controls are healthy. Dummy
  video stays 320 / `0x006dd280`. Homebrew Rice with the eleven-Start schedule
  is the hangar-entry recipe (s707, s1496). Classified frontend routes live in
  `PROJECT-OVERVIEW.md` §35 — do not repeat them.
- Attract A/Start/C-up/L/Z title-like 1024 (`0x00790400`/`800` at 126.3–126.4 s)
  is not a new `cinematicLoopBody`, `runMenuContentStateMachine`,
  `runInMissionFrame` (s1744), or `menuOverlayInit` jump-table case (s1760).
  Extra `loadOverlay` +2 is menu dest +1 plus a skip. Leave stops the
  high-frequency overlay-aliased ticks hold's attract continues. Case 9
  `0x800C28F0` stays 1. Leave also adds `submitGfxFrame` +104/+102 vs hold
  (s1776 H1; s1792 reproduced). That extra is not a new function entry
  (s1792 H3). Callee-side `prev_pc` on `submitGfxFrame` (s1808) names it:
  `menuControllerInput` jal `0x800B8014` +276/+281 and `runInMissionFrame`
  jal `0x800FAD90` −175/−177 net +101/+104 (H2). Histogram sums equal the
  entry count on every arm. s1792's menu-input *entry* drop was overlay-aliased.
  Do not repeat the s1744 / s1760 / s1776 / s1792 / s1808 recipes.
  `runVideoFrameTick`/`swapBufferWithViMode` +1 is the extra WIDTH change.
  Rice still dies ~135 s.
- Port VI 640-to-1024 is generated state plus host VI submission.
  `applyPendingViChanges` can change `0x8011A862/64/65`; a direct `osViSetMode`
  edge can submit `0x80128DF0` without the selector consumer. Active boot
  descriptor is the index-0 320 record.
- M4 shade-lane/order is not the cause. Port VMADH matched 128/128 lanes; VGE
  changed 0/128 (s1135). Rice hangar watches: zero CPU writes to `0x688..0x710`
  and zero writes to SP-DMEM `0x04000670:0x04000720` (s1512). Generated
  `ori $9, $zero, 0x670` plus the only `SP_WR_LEN` DMA from DMEM `0xD60`
  identify `r9` as DMEM. s1602's 32-lane capture is single-source local
  consistency. s1824 selected H-rdp-consumer: after `L_1740`, `L_17F0`
  loads `0x18($vtx)` / `0x1C($vtx)` and restages those halfwords as the
  RDP triangle X/Y into the `0xD60` command buffer before `SP_WR_LEN`.
  No generated path DMAs `0x670` itself. The stored `0xFFFF8000`/
  `0x00008000` bytes are that triangle X/Y, not a separate shade DMA
  record (color is `+0x10` via `luv`). s1840 selected H-standard-edge:
  `L_17F0` writes a spec-accurate 32-byte Fill Triangle (`0xC8|flags`,
  YL/YM/YH at `+2/+4/+6`, XL scaled from the 16-bit `+0x18` X, then
  DxLDy/XH/DxHDy/XM/DxMDy) plus optional shade/tex suffixes. s1856
  selected H-never-live on VI 640 attribution LLE (single-source):
  15921 `L_17F0` entries and 9229 flushed `0xC8` headers, zero
  `+0x1A` / YL/YM/YH `== 0x8000`. s1872 hangar/512 was UNEVALUABLE
  (no hangar origin); s1949 published hangar and selected
  H-never-live there (see Durable).

## Active investigation and ranked next steps

Re-ranked s1970: the generated-symbol sweep (former #1) is now
effectively closed — 845 of 902 leftovers resolved in one session, the
remaining 57 are RE/deliberate-hold, not metadata-sync work. Items below
promote by one; all still need a new discriminator before they can be
worked, so they stay ordered by blast-radius (visual artifacts and a
known SIGBUS family first, with the newly selected M3 link-register audit
before the parked audio re-audit). Per `tools/agent/ITERATION.md`'s
strategic-priority rule, with the sweep no longer perpetually actionable,
the next session with nothing else applicable should attempt the
REVISIT (external retail-entry boundary or M4 accumulator boundary) with
a genuinely new angle rather than defaulting to sweep busywork.

1. Hangar visual artifacts on the first live hangar frame (geometry
   cracks, blue tris, hologram layering). s1967 refuted H2 (malformed
   triangle command) with writer attestation, and s1969's consumer census
   refuted H1 as a single-source result: beam-overlap triangles reached RT64
   with coherent coverage/blender state. H3 remains unavailable because the
   oracle has no screenshot or equivalent LLE `L_17F0` path. Do not add a
   mode-state mitigation, repeat the `0xD60` opcode scan, or conflate this
   with the parked M4 Y=`0x8000` question (different mechanism,
   `y8000_any` stayed 0 in s1969 too). The first hangar window remains ~4s /
   1 frame.
2. The selected M3 follow-up is a complete audit of generated direct
   `bgezal`/`bltzal` host-call lowering wherever a callee or delay-slot
   sequence consumes `$ra` as a data pointer. Enumerate every site, identify
   the writer and intended link value, and use one hangar-gated batch probe to
   distinguish missing context links from valid game data. Do not patch one
   call site until the class is classified.
3. Keep audio closed unless a new independent lead reaches audio
   initialization or voice allocation. Write a bounded plan first.
4. Revisit M3 only as a complete idiom-class audit with a named discriminator.
5. Runtime probes: `tools/oracle/README.md` + `docs/F5-UCODE-REFERENCE.md`;
   batch arms; phase-gate; SIGKILL; queue soaks. Hangar recipe is
   `ROGUESQ_SPIN_YIELD=1` + eleven-Start from boot. Ask (b) remains
   human-only.

## Durable boundaries

**M3 dispatcher/frame origin.** s1162: 144 direct `slotDispatcherIter` calls in
72 generated callers; caller entries, stack pairs, and saved-`$ra` contracts
match. No static indirect target to `0x8003E8DC`. One executable `r29`
initializer in `run_thread_function`. Writer/load classes selected H3; no next
class without a new discriminator.

**VI descriptor.** `osTvType=1` → `rsViModeType=0`; boot selector `A/B/C=1/0/0`.
Active record is base `+0xF0` (`0x80128E40`), the 320 descriptor.
`osViSetMode_recomp` forwards `ctx->r4` unchanged. Independently established.

**M4 accumulator.** Factor 5 reference data and paired combiner evidence refute
RT64 shade-ordering. VTXCOLOR is nonzero. Port VMADH matched 128 lanes; VGE
mutated none. Rice watches plus generated DMEM source reject `0x688..0x710`
as the retail CPU-written shade record. s1824: the `L_1740` `v6` store at
`0x670+0x18`/`+0x40` is consumed by `L_17F0` and restaged as RDP triangle
X/Y into DMEM `0xD60` (command header `*(u8*)(state+0x37)|0xC8`); color
is the separate `+0x10` `luv` field. The observed `0xFFFF8000`/`0x00008000`
sentinel is that XY payload. s1840: the restage is a spec-accurate
32-byte Fill Triangle (YL/YM/YH, then XL/DxLDy/XH/DxHDy/XM/DxMDy);
`0xFFFF8000` splits into X=`0xFFFF` (scaled to XL) and Y=`0x8000`
(raw s11.2). s1856: that Y is not live at `L_17F0` or in flushed
`0xD60` YL/YM/YH during VI 640 attribution LLE (H-never-live,
single-source). s1872 hangar/512 was UNEVALUABLE (no hangar origin).
s1949 published hangar `0x006AB400` and selected H-never-live there:
2187 hangar `L_17F0` entries / 3904 flushes with `y8000_any=0`, plus a
recognizable 3D hangar frame. Late-hangar Y unsampled (4s crash).

**Attract 1024 presenter.** Leave adds `submitGfxFrame` +104/+102 without a new
screen-handler entry. Callee-side `prev_pc` attributes every present: eight
ROM jals, of which `menuControllerInput` `0x800B8014` rises and
`runInMissionFrame` `0x800FAD90` drops, net matching the extra (s1808 H2).
VRAM jal/entry watches at overlay addresses are not a second source.

**Hangar RDP consumer state.** s1969: with the DPC writer-attestation control
live, `decodeTriangles` reached the actual `drawTris` consumer for 500 rows in
the hangar origin `0x006AB400` window. The 153 rows overlapping the captured
beam-cone box had `blend=0x0055`, `ZMODE=0`, `Z_UPD=1`, `CVG_X_ALPHA=0`, and
`ALPHA_CVG_SEL=1`; the sample split was 95 `Z_CMP=1` / 58 `Z_CMP=0`. This is
single-source evidence against an incompatible consumer mode, not pixel
ground truth.

**filterVoiceSampleBlock link contract.** s1970 static enumeration found the
three direct callers in `funcs_27.c`; the live hangar row was
`updateVoiceChannelParamsLarge` at `0x8009D740`. The fixed callee path computes
its indexed byte table as `$ra+0xD4+$a0`. The same-run control and the two audit
rows showed valid caller-owned source/output spans but `$ra=0`, table
`0x000000D4`, and a SIGBUS immediately after the entry. The intended link for
that `jal` is `0x8009D748`; the zero was written by the generated host-call
lowering, not by game audio data. This is a single live edge plus static
whole-tree enumeration; the next branch-and-link audit must establish whether
the same contract affects other sites.

## Superseded conclusions

Older overturned claims live in `PROJECT-OVERVIEW.md` §26, §35, and §36.
Most recent, still load-bearing for the next unit:

- s1888–s1917 "stall at 640 then crash" is superseded by s1918 — 2/8 logs
  live 180s with no crash and no `osViSetMode width=1024`.
- H-slots-stay-live is superseded by s1942 — two `yield_self_1ms` calls
  unblocked recv1 and the guest issued `#9/#10`.
- Eleven-Start-from-boot as a hangar recipe *without* yielding
  `L_800B8050` is still wrong (s1943–s1947 stay at title 1024).
- s1943 "all 11 Starts printed" as host pad consumption is superseded by
  s1944 — those were probe `[keys]` sends; only 4 rising Start edges
  reached `get_n64_input`.
- Missing 7 Starts as SDL/focus drop, `poll_input`-only drain, or a
  56s live window is superseded by s1945 — poll and host die together
  after Start #4.
- SI stop as a stuck post-`StartReadData` Recv, a thread exit, or a skip
  of `StartReadData` is superseded by s1946 — last site is `send` n=1419
  with no `loop` n=1420.
- Continuing post-1024 spin as `waitForAnyAudioSlot` / `menuOverlayInit`
  / another of the ten `jal 0x8008E57C` sites is superseded by s1947 —
  only `menuControllerInput` is live after 1024.
- s1943–s1947 "eleven-Start stays at title 1024" is superseded by s1949
  — those runs did not yield `L_800B8050`. With that yield, hangar
  `0x006AB400` publishes at 26.1s.
- Hangar/512 live `0x8000` Y parked UNEVALUABLE (s1872, s1888, s1943,
  s1944) is superseded by s1949 — hangar origin published and
  `y8000_any=0` on that window.
- s1968's first H1 census pass, which treated any `0xB9/0xBA` header as a
  mode command, is superseded by the fixed rerun: all six matches had
  impossible standard operands and were false candidates, while valid mode
  count remained zero.
- s1970's first audit attempt without the proven LLE-solo hangar environment
  stalled at VI 640 and produced no audit rows; it is recipe failure, not a
  null result. The corrected run reached VI 512 and supplied the positive
  control before selecting H-filter-local-range.

s1919–s1941 caller / slot / mix / VI-recv supersessions are archived in
§36 rather than restated here.

## Evidence ledger summary

Per-session rows through s1879 live in `PROJECT-OVERVIEW.md` §33–§35.
s1880–s1917 leftover remaps, the s1888–s1949 VI-1024 / spin-yield /
title-SI / hangar chain, and the s1950–s1959 leftover remaps live in §36.
s1961–s1965 leftover remaps are in `PORTING-STATE.md` directly (not yet
archived to §36). s1968's H1 scope result and s1970's filter audit are in
`PORTING-STATE.md` directly.
s820–s1239 closed post-sec2 / M3 / audio / VI (dummy-video retail-entry
later superseded by Rice). s1728 and s1948 are maintenance only; s1960 is
loop-infra only (unblock: grok runner balance exhausted, refuted as a
loop-stopper since the loop already runs under `RUNNER=claude` — no
porting conclusion touched, see `PORTING-STATE.md` s1960).

## Method and safety rules

- A null result is worthless without a same-run positive control. Batch all A/B
  arms in one build/run; scope budgets to the VI phase; never compare animating
  scenes by stopwatch. Read the Factor 5 reference before interpreting a DL or
  RDP anomaly. Regen: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, CMake.
  Never `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. `lib/` edits require patch export. Before any mitigation,
  name the writer and legitimacy with `ORIGIN:`.
