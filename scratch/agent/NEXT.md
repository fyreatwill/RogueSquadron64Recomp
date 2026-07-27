# NEXT work unit — M3: hypothesis (b) is unreachable via musyxInitVoiceFromSample; pick a different comparison source or pivot to the refute-branch (s120)

s119 caught a design flaw in its own predecessor's plan (musyxInitVoiceFromSample's
entry-point ctx->r4 is voiceIdx, not a pointer — comparing it would have been
meaningless) before running anything, then ran the corrected instrument twice.
Read PORTING-STATE.md's Session 119 entry before doing anything else; this file
only has the actionable summary.

## What's now closed — do not re-open or re-chase

- `musyxKeyOnVoice` (read-only, s116), `isAudioSlotActive` (pure query, s116),
  the caller-side chokepoint chain (`musyxTriggerVoiceAttack` own-entry, s116),
  hypothesis (b) from s117 (addressing-arithmetic bug in the gate check's own
  `base+idx*0x88`, refuted 3 ways: s117/s118/s119's stride checks) are all
  closed. Do not re-instrument or re-test any of these.
- Byte-for-byte identity between a `voice+0x0` hit and a same-run
  `musyx-dma-call` corrupted `devAddr` was tested and refuted (s118). Do not
  re-run that exact comparison.
- Do not re-run `voicegate4`/`voicegate5`'s exact shape (`ROGUESQ_LOG_VOICE_
  ACTIVE_GATE=1 ROGUESQ_LOG_INIT_VOICE_SAMPLE=1 ROGUESQ_LOG_MUSYX_DMA_CALL=1
  PROBE_MODE=start_only HOLD_S=30`) expecting `musyxInitVoiceFromSample` to
  fire — 2/2 soaks got 0 fires despite the gate-check side clearly executing
  (5 hits each, ~n=68,700-68,800). This is now a well-supported null: that
  function does not run on the menu-only path these driven soaks exercise.
  A 3rd identical attempt is not a new experiment.
- The `[init-voice-slot-ptr]` instrument itself (`N64Recomp/
  fixup_game_funcs.py`, `_init_voice_slot_ptr_patch`, anchored on
  `funcs_24.c:5901`'s `ADD32(ctx->r6, ctx->r4)`) is correctly designed and
  ready to use — the problem is the call site never fires, not the
  instrument. Keep it armed (free), don't rebuild it.

## Two open branches — pick ONE, source-read before committing

**Branch (b-alt): find a more-frequently-called known-good voice-pool
pointer to compare against.** The goal is unchanged from s118/s119's
hypothesis (b) — does `musyxMixActiveVoices`'s `ctx->r4` at the gate check
match the real voice-pool base, or does it diverge — but `musyxInitVoiceFromSample`
is the wrong call site to pair it with (too rare in this code path, 0/3 soaks
now). Before instrumenting, source-read `musyxKeyOnVoice` (`funcs_24.c`,
already confirmed read-only in s116) to check: does IT receive/compute the
same `G_BASE-0x6908 + idx*0x88` base as an argument or local, on a call
frequency closer to `musyxMixActiveVoices`'s (it's a per-key-event function,
not per-tick, so check actual call frequency before committing — this branch
is dead if it's just as rare). If a viable frequent call site exists, log its
computed base next to `[voice-active-gate-nz]`'s `base=` field in the same
run; if they match, (b) is refuted (branch below); if they diverge, (b) is
confirmed.

**Branch (a): hunt the allocator/table that owns the `0x88`-strided region
directly**, independent of ever catching a voice-pool call site alive. s118
found the corrupted content is a real texture/asset-name table
(`explo_tex`/`atpt_load`/etc., matching `main_overlay.txt`'s
`loadExplosionTextures` comment). Grep `N64Recomp/RecompiledFuncs/*.c` for
stores near the `0x88` stride literal and the `G_BASE-0x6908` global's
neighborhood (same technique as s104's node-allocator hunt for `voice+0x34`)
to find what allocates/writes into `base=0x80171D50`-class addresses. This
branch does not require a soak to start — it's a source-read/grep task first,
instrument only once a candidate writer is found.

**Recommendation:** branch (a) has a clearer path to a source-level answer
without depending on driven-soak luck (the hangar-tick crash family has now
killed 2 consecutive attempts before the DMA window on unrelated crashes —
s119). Prefer (a) unless branch (b-alt)'s frequency check looks promising
after a quick source read.

## Regen reminder (unchanged mechanics)

1. `python3 <rogue_squadron64>/tools/make_elf.py` (absolute path, no `cd`)
2. `N64Recomp rogue_squadron.toml` via `subprocess.run(cwd='/Users/williambuckley/Documents/Tools/N64Recomp')`
   (direct `Bash ./build/N64Recomp` hits the headless-approval wall)
3. `python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   (verify "patched x1" — full ELF regen required every time, not idempotent, s102)
4. `cmake --build build -j8` with `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`
5. Soak via `env <FLAGS> PROBE_MODE=start_only HOLD_S=30 zsh
   scratch/s73_post_a_scene/run_mission_keys.sh <tag> 5 8` (`env` prefix
   required, rule 10). Up to 3 attempts per rule 8 if hangar-tick-family
   crashes preempt — but if 2 consecutive attempts already converge on the
   same null (as s119's did), stop rather than mechanically burning the 3rd.

## Do not

- Do not re-test byte-for-byte identity between `voice+0x0` and `devAddr`
  corruption (refuted s118).
- Do not treat the hangar-tick-family crash lottery (17th class, `frameStartReset`,
  or any of the other ~10 catalogued classes) as this session's target — it's
  a known, uninvestigated obstacle to reaching the DMA window, not the M3
  voice-corruption question itself. Catalogue any new class, don't chase it.
- Do not spend a whole work unit on `docs/CURRENT-TRUTH.md` compression alone
  (flagged every session since s116, still ~122 KB) — only pair it with a
  real experiment, per ITERATION.md.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is ~122 KB, well over the ~35 KB target. Migrate
durable mechanism/architecture material to PROJECT-OVERVIEW.md and prune
superseded detail, paired with a real experiment.

`/Users/williambuckley/Documents/Tools/N64Recomp` is its own git checkout,
not a `lib/` submodule, with uncommitted changes across s90-119
(`fixup_game_funcs.py` plus regenerated `RecompiledFuncs/*.c`). Same posture
as the `rogue_squadron64` sibling checkout flagged since s54. Worth asking
the user whether/how to commit that history.
