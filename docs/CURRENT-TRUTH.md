# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background: [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); audio inventory and
de-stubbing contract: [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 4269 (2026-10-08, maintenance compaction).

## Current state (as of s4268)

Per-session chains (s4164-s4268: object-path parity, zero-volume save artifact,
gap/stall instrument ladder, private-DMEM A/B) are archived verbatim in
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md). Only
durable conclusions are kept here.

**Route.** The validated native route boots through attribution, N64 logo, intro
cinematic, Factor 5 logo, title VI 1024 (`0x00790400`) and hangar VI 512
(`0x006AB400`) on the real-audio/LLE/ungated/solo/spin-yield route.
`ROGUESQ_AUDIO_UCODE=0` is the silent control. VI 640 is the ~52-56 s intro, not
a stuck state. Hangar geometry/colour artifacts remain.

**Audio output is real.** With a fresh 7F save the real ucode produces nonzero PCM
at title (s4225). The long "zero payload / zero volume" boundary (s4164-s4224)
was a stale persisted port save (`build/saves` 0x48 = 00 00 00; retail 7F7F7F),
closed s4224. Reset `build/saves` before any audio A/B; `RS64_EEP_TRACE=1`.
The "unrecompiled gap" 0x8002A120..0x8002B18F is libultra EEPROM/controller code
replaced natively by librecomp. The AI byte-order artifact (s4239) is fixed
(`p[i ^ 3]`, `queue_samples ^3`); 876/894 title AI buffers FNV-match ucode output.
Residual: ~3x RMS vs retail at title (unaligned phases, single-run); the
19-buffer constant -33 hangar entry transient is benign prefill (retail does it).

**M5 de-stubs landed.** A11 waitForAnyAudioSlot yield (default 2000), A12 countdown
yielding spin (`ROGUESQ_AUDIO_WAIT_NOPUMP` unset=2; s4192), A15 spin-yield default
on, A13 drain-tick gate (dormant on title+hangar), A14 status-03 wait (never
entered), A9/A10 voice-base/song-tick guards (0 fires). Declared-size staging
(0x800) qualified equal to legacy 0xF80; task-contract guard rejects
ucode_data_size 0 or >0xFC0. `ROGUESQ_AUDIO_PRIVATE_DMEM` defaults ON (s4256;
=0 restores `g_lle_task_mutex` serialisation): audio 25-36 tasks/s at t=18-30
vs 7-8/s with the lock (gfx LLE holds the mutex for whole DLs, s4248/s4249).
Object-path parity (0x8008F900..0x8008F93C, s4175-s4191) is closed
parity-clean; add no more witnesses there.

**Audio gap at t~19-28 s = host renderer, not audio (s4258-s4268).** Gap seconds
are RT64 `send_dl` taking 0.2-0.9 s per gfx task (healthy 12-20 ms), persisting
in a single-arm run (no 2-instance contention). >=95% is `processDisplayLists`
CPU, waits ~0 (s4267). Hotspot (s4268): `State::checkRDRAM` XXH3-hashing a
tracked framebuffer set that grows 3 -> 56 (1.8 -> 13 MB per fullSync). ORIGIN of
the extra framebuffers is UNNAMED (A bogus LLE colour-image sets, B legit
per-effect fbs never pruned, C alias duplicates). Guest-side chain behind it: tid
3 waits on 0x8011A818 sent only by tid 0 (s4261); completions fan out from
`spTaskSchedulerThread`/`dpInterruptHandlerThread` (s4263).

**Crash families (M3, parked).** The VI-640-intro crash (fillSampleStreamRange
+8136/+8292/+932 NULL or wild ptr; RT64 copyToRAM) is independent of private DMEM
and of the audio ucode (s4252/s4255/s4256: pooled ~2/13 vs ~4/21); writer
unnamed. Allocator head==0/tail!=0 (s4230) did not recur in 6 stale runs; parked
wait-for-recurrence (`tools/apply_s4234_entryprobe.py`). Crash PCs 0x80001b08 and
the early `spTaskSchedulerThread+9632`/0x8000834c were OUR zero-extended
`MEM_x(...,0x8...u)` diagnostics (s4229, class closed); last-guest-pc is not the
fault site (use the host pc-symbol).
**REGEN WARNING (s4204):** the full `N64Recomp -> fixup_game_funcs.py` flow aborts
at the s3290 E088 anchor and a regen clobbers the live patched RecompiledFuncs.
Patch the live tree with `tools/apply_s*.py`; do not regen.

## Next steps

Work only the first applicable item. One monotonic sequence.

1. **Name the ~50 tracked framebuffers behind the RT64 stall**
   (scratch/agent/NEXT.md): one-shot framebuffer-map dump + creation log at
   framebuffer_manager.cpp:95 (`ROGUESQ_S4268`); positive control = initial 3
   entries at t~3 s. If bogus LLE colour-image sets: name the writer (ORIGIN). If
   legit: prune in lib/rt64 (`export.sh` + commit).
2. **Resume M5 plan steps** (docs/M5-AUDIO-PLAN.md Step 9/10) once the stall is
   explained; measure default-arm audio task rate t=18-28 with an `=0` control.
3. **M3 pre-publication guard runtime qualification:** blocked on a host with
   `mips64-elf-gcc`/`mips64-elf-ld` and a `PatchesLib` target; no host-only work.
4. **Generated-symbol renaming sweep** (slug `generated-symbol-renaming-sweep`),
   only when 1-3 are inapplicable; mapping-only edits do not reset the
   engineering-change gate.

## Live hypotheses

| Hypothesis | Status |
|---|---|
| RT64 fb-set growth origin | A bogus LLE colour-image / B legit unpruned / C alias duplicates: open (s4269). |
| VI-640 intro crash writer | Open; independent of private DMEM and audio ucode (silent-ucode arm crashes equally, s4252). |
| M5 producer provenance | Port hangar source span is zero because ROM-DMA data (`pi_rom_to_rdram`) is cleared by the legitimate `rs_memset` (0x800078E0/EC); producer setup/object/loop/load-use state is retail-parity (s4150-s4189). No mitigation authorised. |
| Allocator list head==0 | Single-source s4230, not reproduced (s4231/s4234); parked. |
| M3 sentinel ownership | H1 at source scope; runtime unqualified (no MIPS toolchain). |

## Durable evidence boundary

Retail (oracle: tools/oracle/README.md, physical-address watches, whole-RDRAM
positive control) reaches title/hangar and attributes writer PCs; the port matches
it at every witnessed producer boundary. The qualified consumer comparison used
same-build declared/real, declared/silent and legacy/real arms. A route failure
invalidates a null; it never proves absence.

## Superseded conclusions

- s4222/s4223 "port misses code that fills the source block" and every
  zero-volume/zero-payload conclusion s4164-s4221: stale-save artifact (s4224).
- s4235-s4238 AI-output statistics (clipping, 13x hot, DC ramp, identical
  buffers): host byte-order instrument artifact (s4239); ramp magnitude was the
  byte-swapped logger (s4240).
- s4259 "host message late"; s4253 "head->next / cache-recycle" and "t~28 s
  private-DMEM crash is an audio race" (s4254: VI-640 intro, chain intact); s4245
  "stale-ring / half-rate"; s4262 "tid-0 send gate" (it is task-completion
  fan-out, s4263); s4248/s4249 lock wait as the cause of the *residual* dip
  (private DMEM fixed that part; residual is host-renderer side).
- s4179 H-earlier-producer-mismatch (KSEG-only guard artifact, s4180).
- s4075 missing-store (fixup omitted witness); s4088 detail hook (s4089); s4149
  route-invalid (s4150); s3579-s3584 byte-vs-word comparison; s4226 "A12
  refuted / no hangar" (save-dependent flow and input mismatch, s4227).
- Overlay/menu-only explanation, intrinsic VI-640 flakiness, missing-input and
  wait-return explanations, global-zero image-DMA, route-wide PCM-gap, force-zero
  default policy, s327 "only decrementer" (A12 pump was a silent skip).
- s4228/s4231/s4232 early-crash PCs: our diagnostic probes (s4229).
- "Full regen flow works": broken since s4204 (see regen warning).

## Durable operating rules

Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX
assumptions. The qualified graphics path is LLE-only. Interpreter limits,
null-GBI guards and similar defenses are safety mechanisms, not explanations.
MusyX/MORT audio is partially stubbed; MusyX data must not reach stock `aspMain`.

Every instrument needs independent ground truth, a same-run positive control,
a phase-scoped budget and two evidence lines before its result becomes truth.
Phase-gate animated comparisons on VI transitions; batch A/B arms in one
build/run. A counter proving a branch ran is not a positive control.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake` (but see REGEN WARNING). Never hand-edit generated functions for behaviour
changes. If `lib/` changes, run `./submodule-patches/export.sh` and commit. Never
run submodule update, checkout, clean or hard reset. Kill runs with SIGKILL and
run from `build/`. A mitigation-shaped change needs an `ORIGIN:` line naming the
writer and whether its value is legitimate.

## Evidence index

[M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md),
[M5-S3801-IMAGE-STAGE-BOUNDARY.md](M5-S3801-IMAGE-STAGE-BOUNDARY.md),
[M5-S3802-SOURCE-WRITER-CENSUS.md](M5-S3802-SOURCE-WRITER-CENSUS.md),
[M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md](M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md),
[M5-CURRENT-TRUTH-ARCHIVE-s4269.md](M5-CURRENT-TRUTH-ARCHIVE-s4269.md).
Detailed counts remain in `PORTING-STATE.md`.
