# NEXT work unit — M3: instrument the `musyxSynthFrame` countdown/period gate (s108)

s107 found that the "unlocated indirect caller" framing for `tickAllAudioChannels`
was wrong — every hop is a real static call, found by source-reading (not
grepping for `LOOKUP_FUNC`/`jalr`). The whole chain is provably gated by a
per-tick countdown divider that lives inside `musyxSynthFrame` itself.
Read PORTING-STATE.md's Session 107 entry before doing anything else; this
file only has the actionable summary.

## What's confirmed (do not re-derive)

- `tickAllAudioChannels` (`funcs_23.c:4061`) has exactly one static caller:
  `tickAudioSequencerFrame` (`funcs_23.c:6654`), called unconditionally
  partway through that function's body.
- `tickAudioSequencerFrame` has exactly 3 static call sites, all inside
  `musyxSynthFrame` (`funcs_24.c:3097`, confirmed running every soak via
  `musyx-dma-call`/`fill-range-args`). Each site has the SAME gate shape:
  ```
  countdown = G_BASE-0x68EC (a fixed global, 4 bytes)
  countdown -= 1
  store countdown back to G_BASE-0x68EC
  if (countdown != 0) skip tickAllActiveSongs + tickAudioSequencerFrame
  else { countdown = G_BASE-0x68E8 (period, reloaded); call tickAllActiveSongs; call tickAudioSequencerFrame; }
  ```
  (see funcs_24.c ~3505-3545, ~3635-3680, ~3765-3810 for the 3 near-identical
  copies — register allocation differs slightly between them, don't assume
  a single regex anchor covers all 3; s107's patches only touched
  `tickAudioSequencerFrame`/`tickAllAudioChannels` themselves, not these
  call sites, so this is still unpatched territory).
- `tickAudioSequencerFrame` ALSO has its own independent gate at its own
  entry, before reaching the call to `tickAllAudioChannels`:
  `if (MEM_W(rdram, 0x80142038) == 0) return;` (funcs_23.c:6681-6685).
- Landed `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1` entry counters (same shared
  flag, cap-at-20 style) on `tickAudioSequencerFrame` (logs `n` +
  `gate2038` value) and `tickAllAudioChannels` (logs `n` + channel-count
  byte at `0x80141AD0`), in `N64Recomp/fixup_game_funcs.py`. Both patched
  exactly x1 in `funcs_23.c`. Verify this is still true (`grep -c` the
  anchor comments) if you touch this script again.
- One soak this session (`scratch/s73_post_a_scene/s107_voicechain/run.log`):
  reached `vi_width=640` at 151.1s (past the ~140s window), died to the
  same `do_rom_read` SIGSEGV a 12th time. Positive control clean:
  `musyx-dma-call`=17, `fill-range-args`=7. Both new counters: **0/0**.
  `tick-audio-channel`/`service-voice-pool-frame`/`init-voice-sample`
  (s106's counters, still armed): also 0/0, consistent.
- This is 1 soak, not 2 — do not yet treat "the countdown gate is the
  block" as fully closed the way s106's 3-counter null was (that had 2
  independent soaks). One more soak at the countdown-value instrument
  described below would bring this to the same 2-soak standard.

## The work unit

1. **Add a capped entry log inside `musyxSynthFrame` at ONE of the 3 gate
   sites** (pick the first, ~funcs_24.c:3505-3520) that fires on EVERY
   entry to that code region (i.e. place it right where the countdown is
   loaded, before the decrement-and-compare, unconditionally — not inside
   either branch) — same `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1` flag, cap at
   first 20 fires (this will fire far more often than the other counters,
   once per `musyxSynthFrame` call, likely 60/sec — the cap matters more
   here than anywhere else so far). Log: `n`, the countdown value BEFORE
   decrement, and the period value at `G_BASE-0x68E8` (read fresh, not
   decremented). This settles in one soak whether: (a) the countdown is
   sane and just slow (e.g. period=300, fires every 5s — a 150s soak
   should have seen ~30 firings, so if it's this and still 0/0, the soak
   is too short or something else is wrong), (b) the countdown is frozen
   at a nonzero value across many logged entries (never actually
   decrementing — arithmetic/store bug or a duplicate/shadow global), or
   (c) the period is enormous/corrupted (matches this investigation's
   established "structured wrong-value" family).
2. **Regen order**: `python3 /Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py`
   → N64Recomp (`python3 -c "import subprocess; subprocess.run(['./build/N64Recomp', 'rogue_squadron.toml'], cwd='/Users/williambuckley/Documents/Tools/N64Recomp')"`)
   → `fixup_game_funcs.py` → `cmake --build`. **Full regen from ELF, not
   a bare fixup re-run** — idempotency bug still unfixed (see Tooling
   note below). Verify the fixup report shows each patch applied exactly
   `x1` in its expected file before rebuilding — funcs_24.c is a large,
   repetitive file (3 near-identical gate copies), a prime spot for an
   anchor accidentally matching more than one site.
3. Rebuild: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j 8` — exit clean (only pre-existing format/sign warnings).
4. Soak (same repro shape, reuse the full flag set):
   `env ROGUESQ_LOG_MUSYX_DMA_CALL=1 ROGUESQ_LOG_FILL_RANGE_ARGS=1 ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1 ROGUESQ_LOG_THREAD_RESUME=0 PROBE_MODE=start_only HOLD_S=30 zsh run_mission_keys.sh s108_musyx_gate 30 12`
   (run from `scratch/s73_post_a_scene/`; backgrounds past the 120s
   foreground timeout — wait for the completion notification, or block
   on `--- done ---` appearing in the output file, rather than polling
   with short sleeps).
5. **Interpret** per the (a)/(b)/(c) branches in step 1. If (a) and the
   period looks small/sane, do NOT re-run the same soak shape hoping for
   a lucky capture — the countdown-value log itself already answers the
   question (you'll see it decrementing sanely across ~20 logged
   entries) without needing to catch tickAudioSequencerFrame actually
   fire. If (c), this is a 5th instance of the "structured corrupted
   value" family this investigation keeps finding (devAddr, fill-range
   args, now potentially this) — worth explicitly noting the parallel in
   PORTING-STATE, not chasing it as a 6th independent bug without
   checking whether it's the SAME corrupted source value first (compare
   the corrupted period value, if any, against the known
   `0x6C676672`/`0x77696E67` pattern byte-for-byte).

## Housekeeping note — not this session's job, but flag it (still true)

`docs/CURRENT-TRUTH.md` is at ~99 KB, well past the ~35 KB `CLAUDE.md`
budget. A future session should do a dedicated pruning pass — migrate
durable mechanism/architecture material to `docs/PROJECT-OVERVIEW.md`,
keep only current status + next steps in CURRENT-TRUTH. Per ITERATION.md,
compressing CURRENT-TRUTH does not itself count as "ADVANCED" — pair it
with a real work unit if attempted, don't spend a whole iteration on it
alone.

## Tooling note — still not fixed, still cheap

`fixup_game_funcs.py` is **not idempotent** by construction (every
patch's anchor regex matches text left unchanged after insertion). A
full ELF regen has now avoided the duplication symptom five times in a
row (s103-s107) as a workaround. If a session touches
`fixup_game_funcs.py` again, consider actually fixing it: make each
patch's anchor regex also require a negative lookahead that the match
is **not** immediately followed by `    { // PATCH:`. Test by running
the script twice in a row on an already-regenerated tree and confirming
the 2nd run reports 0/"no changes needed" for every already-landed
patch.

## Do not

- Do not re-instrument or re-soak `musyxInitVoiceFromSample`,
  `tickAudioChannel`, `serviceVoicePoolFrame`, `tickAudioSequencerFrame`,
  or `tickAllAudioChannels` in isolation again — all now read a
  consistent 0/0 (2 independent soaks for the first three, 1 for the
  last two) against a proven-active surrounding system. The open
  question is the countdown/period gate INSIDE `musyxSynthFrame`, one
  hop further up.
- Do not re-read or re-instrument `musyxKeyOnVoice` for this bug —
  cleared s105 (writes an unrelated RSP command-list struct).
- Do not re-instrument `initSampleStreamBlockCache`, `fillSampleStreamRange`'s
  own arithmetic, or `acquireSampleStreamBlock` — all cleared s103/s104.
- Do not re-instrument `musyxSynthFrame`'s own DMA-batch call site,
  `submitDmaRequestBatch`, or `setupSongRenderBuffers` — all cleared
  s102/s103. The NEW instrument for this session is a DIFFERENT part of
  `musyxSynthFrame` (the 3 tick-divider gate sites), not these.
- Do not treat a soak that dies before `vi_width=640`/~140s (with
  `fill-range-args`/`musyx-dma-call` both reading 0) as evidence for or
  against anything — it never reached the window under test (s106's
  soak 1). Retry instead of interpreting it.
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
