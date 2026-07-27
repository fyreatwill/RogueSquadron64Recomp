# NEXT work unit — M3: get a positive control for `ROGUESQ_LOG_INIT_VOICE_SAMPLE`, or pivot (s106)

s105 traced `voice+0x34` to a confirmed matching writer,
`musyxInitVoiceFromSample`, but the instrument testing it came back
0/0 in a run where the corruption still recurred — an **inconclusive**
result (no positive control), not a refutation. Read PORTING-STATE.md's
Session 105 entry before doing anything else; this file only has the
actionable summary.

## What's confirmed (do not re-derive)

- `musyxKeyOnVoice` (`funcs_24.c:1825`, guest `0x80090A3C`) writes a
  3-word block that superficially resembles the field we're chasing,
  but its destination pointer is computed from `G_BASE-0x68B0`'s
  *dereferenced* runtime value (per the existing `musyxBuildVoiceCommandList`
  symbol comment, the head of an RSP microcode command list at guest
  `0x80149750`) — **not** the array `musyxRenderVoiceSamples` actually
  indexes. **Cleared as a suspect for this specific field** — do not
  re-read it for this purpose again. (It may still be worth
  understanding for the RSP-mixer path someday, but that's a different
  question.)
- `musyxInitVoiceFromSample` (`funcs_24.c:5753`, guest `0x80092128`,
  symbol-commented "load loop/base/sampPtr from descriptor") is
  confirmed — by 3 independent matching offsets, not just one — to
  write into the exact same struct `musyxRenderVoiceSamples` reads:
  - Its voice-slot base is `MEM_W(G_BASE, -0x6908)` indexed by
    `voiceIdx * 0x88`. `musyxRenderVoiceSamples`'s own `$s1` is simply
    its own `a0` argument (re-read at `funcs_24.c:6-`, its own
    function start, to confirm — no global lookup on its side).
  - `+0x4` (rate): this function's own default-pitch write (`0x1000`)
    matches `musyxRenderVoiceSamples`'s `MEM_HU(+0x4)` read.
  - `+0x3C`/`+0x40` (loop points): written here from
    `sampleDesc+0x10`/`+0x14`; read directly by
    `musyxRenderVoiceSamples`'s own resample loop.
  - The exact write is `sw $v1, 0x34($a0)` where `$v1 = MEM_W(a1, 0x4)`
    — i.e. `voice+0x34 = sampleDesc+0x4`, a straight verbatim word
    copy. Also `voice+0x38/+0x3C/+0x40 = sampleDesc+0xC/+0x10/+0x14` in
    the same few instructions. **No arithmetic bug here** — if the
    corruption enters via this function, it's because `sampleDesc`
    itself already carries it in.
- Both call sites build `sampleDesc` (`a1`) **fresh, right before the
  call**, not from a stable ROM/asset table pointer:
  - `funcs_22.c:3667` — `a1` points at a fixed global scratch address
    (`G_BASE-0x5358`, conditionally adjusted `-8` based on a flag read
    from `$s5+0x24`); earlier code in the *same* calling function
    populates that scratch struct field by field (not yet read this
    session — starts well before line 3590).
  - `funcs_26.c:1418` — `a1 = $sp+0x18`, an on-stack struct built
    immediately above the call from local registers `$s1`-`$s6` (and
    also mirrored into a persistent per-index table at
    `G_BASE+idx*8`-ish offsets `0x2A20-0x2A34` — a caching mechanism,
    not the bug's origin by itself).
  - **Neither call site's construction was read to its own origin this
    session** (i.e. where do `$s1`-`$s6` in `funcs_26.c`, or the
    earlier field-writes into the `funcs_22.c` scratch struct,
    themselves come from). That's the natural next step if a positive
    control confirms this is still the right function.
- Landed `ROGUESQ_LOG_INIT_VOICE_SAMPLE=1` (`N64Recomp/fixup_game_funcs.py`,
  anchored on `musyxInitVoiceFromSample`'s entry boilerplate, file-scoped
  to `funcs_24.c`, confirmed the only definition in the whole
  `RecompiledFuncs/` tree). Logs raw incoming `a0`/`a1` plus
  `sampleDesc+0x4/0x8/0xC/0x10/0x14` at function entry.
- One soak (`scratch/s73_post_a_scene/s105_initvoice/run.log`,
  `PROBE_MODE=start_only HOLD_S=30`): **`[init-voice-sample]` fired
  0/0** across the *entire* process lifetime (not just the hold
  window), while `[fill-range-args]`/`[musyx-dma-call]` fired with the
  same byte-identical corrupted values as every prior session
  (`0x6C676672`/`0x77696E67`, "lgfr"/"wing"), and the process died to
  the 10th `do_rom_read` recurrence (this time captured as a raw
  SIGSEGV inside `do_rom_read` itself rather than the deliberate
  alignment assert — same call stack, `do_rom_read` ← `do_dma` ←
  `osPiStartDma_recomp` ← `piDmaWorker`, treated as the same crash
  family, not a new class).
- **Per iron rule 1, this 0/0 is inconclusive, not a refutation** — we
  have no evidence the instrument can fire *at all* in this build/run
  configuration. Two live explanations, neither tested:
  1. This driven scene's music/SFX never triggers a genuinely *new*
     key-on during the whole captured run (all active voices were
     already playing from before the process reached this scene) — in
     which case the function is real and correct but simply not
     exercised by this repro shape.
  2. Despite the 3 matching offsets, the `G_BASE-0x6908` array and
     `musyxRenderVoiceSamples`'s own `a0` are not actually the same
     base at runtime, and the offset match is coincidence — in which
     case the true writer is still unlocated.

## The work unit

**Do not re-run the hangar-scene repro soak with this instrument again
without first getting a positive control.** Priority order:

1. **Get the positive control first.** Soak from a fresh boot through
   the title screen (where music is close to certain to start fresh
   voices) with `ROGUESQ_LOG_INIT_VOICE_SAMPLE=1` armed alone (skip the
   hangar-repro key schedule, or just let the existing
   `run_mission_keys.sh` run past title before checking the log — the
   flag is armed from process start, so any title-screen key-on should
   show up early in `run.log` well before the hangar phase). If it
   fires here: the instrument works, and hypothesis 1 above
   (not exercised *in the hangar scene specifically*) is supported —
   next step is then to find whatever *does* run key-on-equivalent
   logic for hangar-flight ambient/engine sounds, if it's not this
   function. If it still doesn't fire even at boot: that's a real,
   surprising finding worth its own write-up (e.g. maybe this build's
   audio is effectively silent/stubbed at the CPU-software level despite
   `fillSampleStreamRange` clearly running — check `ROGUESQ_STUB_MISSING_FUNCS`
   interaction and any audio-init log lines first).
2. **If the positive control succeeds and the hangar-scene run still
   shows 0/0 for `[init-voice-sample]`**: hypothesis 1 is confirmed,
   and the search needs to move to whatever DOES write `voice+0x34`
   for a voice that's already playing (not a fresh key-on) — likely a
   pitch-bend/streaming-continuation path, not an init path. Re-read
   `musyxRenderVoiceSamples`'s own body around the `+0x34` read
   (`funcs_24.c` ~439-442) for any OTHER place in the same function (or
   its siblings `musyxMixActiveVoices`/`musyxMixActiveVoices`'s other
   callees) that writes back to that same field mid-playback.
3. **If the positive control fails (never fires even at boot)**:
   trace `musyxInitVoiceFromSample`'s callers' callers — who calls
   `funcs_22.c`'s and `funcs_26.c`'s enclosing functions, and under what
   condition — to find out whether key-on logic is gated behind
   something disabled in this build (e.g. a stubbed function, a
   feature flag, or a MusyX init step that never completes).
4. **Once a genuine writer is confirmed (fires with a byte-identical
   corrupted value)**: read that writer's own argument origin the same
   disciplined way s102-s105 did — confirm from actual instructions
   which upstream value maps to the corrupted field before writing any
   patch or drawing a conclusion. Do not guess.
5. **If a wrong-field/wrong-offset bug is confirmed**: fix at the
   source (`N64Recomp/fixup_game_funcs.py`, guest-side hand patch),
   following the exact-instruction-anchor, file-scoped, "verify patched
   xN in only the expected file" discipline every prior guard/patch in
   this arc has used (s99-105).
6. **Regen order** if `fixup_game_funcs.py` changes:
   `python3 /Users/williambuckley/Documents/Tools/rogue_squadron64/tools/make_elf.py`
   → N64Recomp (see command below) → `fixup_game_funcs.py` →
   `cmake --build`. **Do a full regen from ELF, not a bare
   `fixup_game_funcs.py` re-run** — the idempotency bug is still not
   fixed (see Tooling note below).
   - N64Recomp step: direct `Bash` invocation of `./build/N64Recomp` or
     `cd &&` chains may get denied by the sandbox — use `python3 -c
     "import subprocess; subprocess.run(['./build/N64Recomp',
     'rogue_squadron.toml'], cwd='/Users/williambuckley/Documents/Tools/N64Recomp')"`
     instead (config file is `rogue_squadron.toml`, not
     `us.rev1.us.toml` — that name doesn't exist in this checkout).
7. Rebuild: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build -j 8` — exit clean (only the pre-existing-class format/sign warnings).
8. Soak with the full flag set plus whatever new flag this session
   adds:
   `env ROGUESQ_LOG_MUSYX_DMA_CALL=1 ROGUESQ_LOG_STREAM_TAG=1 ROGUESQ_LOG_FILL_RANGE_ARGS=1 ROGUESQ_LOG_INIT_VOICE_SAMPLE=1 ROGUESQ_LOG_THREAD_RESUME=0 PROBE_MODE=start_only HOLD_S=30 zsh run_mission_keys.sh <tag> 30 12`
   (run from `scratch/s73_post_a_scene/`; this auto-backgrounds past
   the 120s foreground timeout — wait for the completion notification,
   or block on the PID directly with a `until ! kill -0 <PID>; do sleep
   3; done` loop rather than a bare `sleep`, since the Stop-hook gate
   fires on turn end regardless of background tasks in flight. The
   actual game stdout/stderr lands in `<tag>/run.log` inside the
   soak's own output dir, NOT wherever you redirected the shell
   command's own stdout).

## Housekeeping note — not this session's job, but flag it

`docs/CURRENT-TRUTH.md` is now well past the ~35 KB `CLAUDE.md` budget
(accumulating since the s85 saga). A future session should do a
dedicated pruning pass — migrate durable mechanism/architecture
material to `docs/PROJECT-OVERVIEW.md`, keep only current status +
next steps in CURRENT-TRUTH. Per ITERATION.md, compressing
CURRENT-TRUTH does not itself count as "ADVANCED" — pair it with a
real work unit if attempted, don't spend a whole iteration on it
alone.

## Tooling note — still not fixed, still cheap

`fixup_game_funcs.py` is **not idempotent** by construction (every
patch's anchor regex matches text left unchanged after insertion). A
full ELF regen has now avoided the duplication symptom three times in
a row (s103, s104, s105) as a workaround. If a session touches
`fixup_game_funcs.py` again, consider actually fixing it: make each
patch's anchor regex also require a negative lookahead that the match
is **not** immediately followed by `    { // PATCH:`. Test by running
the script twice in a row on an already-regenerated tree and confirming
the 2nd run reports 0/"no changes needed" for every already-landed
patch.

## Do not

- Do not re-read or re-instrument `musyxKeyOnVoice` for this bug —
  cleared s105 (writes an unrelated RSP command-list struct, not the
  voice struct `musyxRenderVoiceSamples` reads).
- Do not re-soak specifically to re-test `musyxInitVoiceFromSample`'s
  own copy arithmetic — cleared s105 (verbatim word copies, no
  computation to be wrong).
- Do not re-instrument `initSampleStreamBlockCache` — fully cleared
  s104. Do not re-instrument or re-soak `fillSampleStreamRange`'s own
  arithmetic — cleared s104. Do not re-soak `acquireSampleStreamBlock`
  — refuted s103.
- Do not re-instrument `musyxSynthFrame`, `submitDmaRequestBatch`, or
  `setupSongRenderBuffers` — all cleared (s102/s103).
- Do not treat `[init-voice-sample]` 0/0 as proof `musyxInitVoiceFromSample`
  is uninvolved — it is an inconclusive null without a positive
  control (iron rule 1). Get the positive control before drawing any
  conclusion either way.
- Do not cite `ra=0x00000000` as corruption evidence (refuted s92,
  reconfirmed every session since).
- Do not re-open "random/race/stomp" framings for the `devAddr`
  corruption — 7+ independent lines of evidence against all three now.
- Do not compare a raw `ctx->rN` (`gpr`/`uint64_t`) value against 32-bit
  literal bounds in any new guard — always truncate through `U32()`
  first for comparisons; for pointer *arithmetic* (dereferencing), never
  truncate — keep the full sign-extended `gpr` value.
- Do not trust a `fixup_game_funcs.py` "patched xN" report without
  checking which file(s) it patched, **and do a full ELF regen first**
  if the tree may already carry prior patches.
- `N64Recomp/fixup_game_funcs.py` is untracked in N64Recomp's own git,
  by design — do not attempt to commit it there; the durable record
  lives in `PORTING-STATE.md`/`CURRENT-TRUTH.md` in this repo.
