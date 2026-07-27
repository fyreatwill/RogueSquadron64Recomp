# NEXT work unit — M3: instrument `tickAllAudioChannels` to find where the key-on chain gate really is (s107)

s106 confirmed (2 independent soaks, one with a clean positive control)
that `musyxInitVoiceFromSample`'s ENTIRE call chain —
`tickAudioChannel`, `serviceVoicePoolFrame`, and the leaf function
itself — never executes once, even in a run where the surrounding
MusyX per-tick DMA system is proven actively running. Read
PORTING-STATE.md's Session 106 entry before doing anything else; this
file only has the actionable summary.

## What's confirmed (do not re-derive)

- `musyxInitVoiceFromSample` (`funcs_24.c:5753`, guest `0x80092128`) is
  a verbatim-copy writer of `voice+0x34 = sampleDesc+0x4` — confirmed
  by 3 matching offsets against `musyxRenderVoiceSamples`'s own reads
  (s105). No arithmetic bug in this function if it's the right one.
- Its two call sites: `funcs_22.c:3667` inside
  `soundMacroOpPlaySampleKeymap` (one static caller anywhere in the
  tree: `funcs_23.c:3081`, inside `tickAudioChannel`); `funcs_26.c:1418`
  inside `startStreamedSampleVoice` (one static caller:
  `funcs_26.c:11256`, inside `serviceVoicePoolFrame`).
- `serviceVoicePoolFrame` (`funcs_26.c:10932`, guest `0x8009B5A8`) has
  **zero** static or address-taken references anywhere in
  `RecompiledFuncs/*.c` — same "invisible to grep, must be an indirect
  call" shape as `musyxSynthFrame`'s own caller (s95-s101). Don't trust
  a caller-grep here; entry counters are the only reliable test.
- `tickAudioChannel` DOES have exactly one known static caller:
  `tickAllAudioChannels` (`funcs_23.c:4050`, guest not yet noted — grep
  the function's own boilerplate comment to get it). **Not yet
  instrumented.**
- Landed `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1` (`N64Recomp/
  fixup_game_funcs.py`) with entry counters (capped at first 20 fires)
  on `tickAudioChannel` (funcs_23.c) and `serviceVoicePoolFrame`
  (funcs_26.c). Both patched exactly x1 in the expected file — confirm
  this is still true after any further edits to the same script (`grep
  -c` each anchor in its target file post-regen).
- Two soaks this session
  (`scratch/s73_post_a_scene/s106_voicechain{,2}/run.log`):
  - Soak 1: died early (RT64 `loadDrawState` abort, the already-known
    15th crash class) before reaching the DMA window — controls
    (`fill-range-args`/`musyx-dma-call`) also read 0/0, so this run is
    uninformative, not evidence either way. Discard it as a data point.
  - Soak 2: reached `vi_width=640` @ 141.9s, died to the 11th
    `do_rom_read` recurrence (byte-identical, `devAddr=0x6C676672`/
    `0x77696E67`). **Positive control clean this time**:
    `fill-range-args` fired 7x, `musyx-dma-call` fired 17x. Against
    that, `tick-audio-channel`=0, `service-voice-pool-frame`=0,
    `init-voice-sample`=0.
- Combined with s105's own soak (0/0 for `init-voice-sample` across an
  even longer span, boot through crash) — **two independent soaks**
  now agree the whole chain never fires. This is a real null, not an
  untested instrument, per iron rule 1 (positive control now exists on
  the *surrounding* system).
- This does **NOT** yet distinguish s105's two hypotheses:
  1. This scene/song's active voices were all already playing before
     capture began; no genuinely *new* key-on occurs during any of the
     observed run (boot through crash) via this mechanism.
  2. The `G_BASE-0x6908`/`voiceIdx*0x88` offset match between
     `musyxInitVoiceFromSample` and `musyxRenderVoiceSamples` was
     coincidental — wrong struct entirely, true writer still unlocated.
  Both remain fully consistent with "the whole chain reads 0/0".

## The work unit

1. **Read `tickAllAudioChannels`'s own body** (`funcs_23.c:4050`) to
   find: (a) its own caller(s) (grep `RecompiledFuncs/*.c` for a
   literal call — if that also comes back empty, this may be another
   indirect-call case, same as `serviceVoicePoolFrame`); (b) what
   condition (if any) gates whether it calls `tickAudioChannel` for a
   given channel — a loop over a fixed channel count with an
   active/inactive flag check is the likely shape.
2. **Add an entry counter on `tickAllAudioChannels` itself** (same
   `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1` gate, same cap-at-20 style) —
   this settles, in the SAME soak as the existing two counters, whether
   the gate is one hop higher (the whole per-channel tick system
   unreached) or whether `tickAllAudioChannels` runs but its own
   internal call to `tickAudioChannel` is conditionally skipped. If (1)
   found a static caller, no separate instrument is needed there yet —
   the entry counter answers the "does it run" question directly
   regardless of call mechanism.
3. **Regen order**: `python3 /Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py`
   → N64Recomp (`python3 -c "import subprocess; subprocess.run(['./build/N64Recomp', 'rogue_squadron.toml'], cwd='/Users/williambuckley/Documents/Tools/N64Recomp')"`)
   → `fixup_game_funcs.py` → `cmake --build`. **Full regen from ELF,
   not a bare fixup re-run** — idempotency bug still unfixed (see
   Tooling note below). Verify the fixup report shows each patch
   applied exactly `x1` in its expected file before rebuilding.
4. Rebuild: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j 8` — exit clean (only pre-existing format/sign warnings).
5. Soak (same repro shape, reuse the full flag set):
   `env ROGUESQ_LOG_MUSYX_DMA_CALL=1 ROGUESQ_LOG_FILL_RANGE_ARGS=1 ROGUESQ_LOG_INIT_VOICE_SAMPLE=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_THREAD_RESUME=0 PROBE_MODE=start_only HOLD_S=30 zsh run_mission_keys.sh <tag> 30 12`
   (run from `scratch/s73_post_a_scene/`; backgrounds past the 120s
   foreground timeout — wait for the completion notification rather
   than polling). **If a run dies before `vi_width=640`/~140s without
   `fill-range-args`/`musyx-dma-call` firing at least once, that run is
   uninformative (per this session's soak 1) — retry rather than
   drawing any conclusion from it.**
6. **Interpret**: if `tickAllAudioChannels` fires but never reaches
   `tickAudioChannel`, source-read the gating condition next (likely
   points to hypothesis 1 — a per-channel "is this channel active"
   check that's never true here). If `tickAllAudioChannels` itself
   never fires, the search moves one hop higher still (whoever should
   call it — likely `musyxSynthFrame`'s own body or a sibling
   per-VI-retrace function, both already partially read in s101-s102 —
   re-check those for a call/reference to `tickAllAudioChannels` before
   assuming a 3rd indirect-call mystery).
7. **If this eventually confirms hypothesis 1** (voices already active,
   no new key-on ever needed): the search for `voice+0x34`'s corruption
   needs to pivot away from "who writes it at init" entirely — since
   nothing ever (re-)initializes it during the captured window, the bad
   value must already be present in the voice slot at whatever point it
   WAS written (likely during an earlier, uncaptured moment, or the
   struct's memory was never zeroed/initialized before first use —
   check for an uninitialized-read explanation next, not another writer
   search).

## Housekeeping note — not this session's job, but flag it

`docs/CURRENT-TRUTH.md` is now well past the ~35 KB `CLAUDE.md` budget
(accumulating since the s85 saga, now s106 on top). A future session
should do a dedicated pruning pass — migrate durable mechanism/
architecture material to `docs/PROJECT-OVERVIEW.md`, keep only current
status + next steps in CURRENT-TRUTH. Per ITERATION.md, compressing
CURRENT-TRUTH does not itself count as "ADVANCED" — pair it with a
real work unit if attempted, don't spend a whole iteration on it alone.

## Tooling note — still not fixed, still cheap

`fixup_game_funcs.py` is **not idempotent** by construction (every
patch's anchor regex matches text left unchanged after insertion). A
full ELF regen has now avoided the duplication symptom four times in a
row (s103-s106) as a workaround. If a session touches
`fixup_game_funcs.py` again, consider actually fixing it: make each
patch's anchor regex also require a negative lookahead that the match
is **not** immediately followed by `    { // PATCH:`. Test by running
the script twice in a row on an already-regenerated tree and confirming
the 2nd run reports 0/"no changes needed" for every already-landed
patch.

## Do not

- Do not re-instrument or re-soak `musyxInitVoiceFromSample`,
  `tickAudioChannel`, or `serviceVoicePoolFrame` in isolation again —
  their 0/0 is now a confirmed null (2 independent soaks, one with a
  clean positive control on the surrounding system), not an untested
  instrument. The open question is one hop higher
  (`tickAllAudioChannels`), not these three.
- Do not re-read or re-instrument `musyxKeyOnVoice` for this bug —
  cleared s105 (writes an unrelated RSP command-list struct).
- Do not re-instrument `initSampleStreamBlockCache`, `fillSampleStreamRange`'s
  own arithmetic, or `acquireSampleStreamBlock` — all cleared s103/s104.
- Do not re-instrument `musyxSynthFrame`, `submitDmaRequestBatch`, or
  `setupSongRenderBuffers` — all cleared s102/s103.
- Do not treat a soak that dies before `vi_width=640`/~140s (with
  `fill-range-args`/`musyx-dma-call` both reading 0) as evidence for or
  against anything — it never reached the window under test (this
  session's soak 1). Retry instead of interpreting it.
- Do not cite `ra=0x00000000` as corruption evidence (refuted s92).
- Do not re-open "random/race/stomp" framings for the `devAddr`
  corruption — 7+ independent lines of evidence against all three.
- Do not compare a raw `ctx->rN` (`gpr`/`uint64_t`) value against 32-bit
  literal bounds in any new guard — always truncate through `U32()`
  first for comparisons; for pointer *arithmetic*, never truncate.
- Do not trust a `fixup_game_funcs.py` "patched xN" report without
  checking which file(s) it patched, **and do a full ELF regen first**
  if the tree may already carry prior patches.
- `N64Recomp/fixup_game_funcs.py` is untracked in N64Recomp's own git,
  by design — do not attempt to commit it there; the durable record
  lives in `PORTING-STATE.md`/`CURRENT-TRUTH.md` in this repo.
