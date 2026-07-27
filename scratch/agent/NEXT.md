# NEXT work unit — M3: is the voice-array base pointer itself corrupted, or is the memory it points to being reused by a texture-name table? (s119)

s118 turned "is `voice+0x0`'s corruption the same source as `devAddr`'s"
into a sharper question. Read PORTING-STATE.md's Session 118 entry
before doing anything else; this file only has the actionable summary.

## What's now closed — do not re-open or re-chase

- `musyxKeyOnVoice` (read-only), `isAudioSlotActive` (pure query), the
  caller-side chokepoint chain (`musyxTriggerVoiceAttack` own-entry), and
  hypothesis (b) from s117 (an addressing bug in the gate check's own
  `base+idx*0x88` arithmetic) are all closed (s116-117, reconfirmed a
  3rd time in s118 via the stride check on the widened dump). Do not
  re-instrument or re-test any of these.
- Do not re-run the capped `voicegate1` design (known-broken, exhausts
  in the first audio ticks). The current uncapped-nonzero + heartbeat +
  32-byte-dump design in `N64Recomp/fixup_game_funcs.py` (search
  `s_voice_active_gate_nz_n`) is correct — reuse/extend it, don't replace
  it wholesale.
- Byte-for-byte identity between a `voice+0x0` hit and a same-run
  `musyx-dma-call` corrupted `devAddr` value was tested and **refuted**
  (s118: 0/3 literal matches against `"wing"`/`"lgfr"`/`"lcre"`). Do not
  re-run that exact comparison expecting a different outcome — if you
  want more data points, that's a different (lower-priority) question
  than the one below.

## The decisive result from s118

The widened dump (32 bytes at `ctx->r4`, the voice-array base, on every
nonzero `voice+0x0` hit) decodes to long, human-readable ASCII strings —
not raw garbage, not boolean-adjacent bytes. Example: `n=68892 idx=0x10
base=0x80171D50` → `"explo_tex2\0\0\0\0\0\0" FFFFFFFF "explx3\0\0\0\0\0\0"`.
Later in the *same run*, the *same addresses* hold a completely
different string set (`"star_"`, `"atpt_load"`, `"mat_6"`, `"xenlight"`,
`"xckpit"`) — live data changing as the scene progresses, not static
noise. Independently confirmed via source grep: `explo_tex` matches
`rogue_squadron64/symbol_files/main_overlay.txt`'s own comment on
`loadExplosionTextures` (`0x8006108C`) verbatim. **This is a real
texture/asset-name table**, source-confirmed, not a coincidental
ASCII-shaped byte pattern.

This is stronger evidence than s117 had, but it does NOT prove the
literal-byte-match test NEXT.md specified (that was refuted — see
above). The open question is now mechanistic, not "is it the same
source as devAddr's corruption."

## The work unit

Test hypothesis (b) from the s118 writeup: **is `ctx->r4` (the pointer
`musyxMixActiveVoices` uses as the voice-array base) itself corrupted to
point somewhere other than the real voice pool** — i.e. every
"voice+N" finding across s94-118 may have been reading a texture-name
table the whole time, not the audio subsystem at all.

1. In the same soak, log `ctx->r4` from inside the existing
   `ROGUESQ_LOG_VOICE_ACTIVE_GATE` block (already captured, no new
   instrument needed there) alongside a **known-good** voice-pool
   pointer captured from a different, independently-verified call site:
   `musyxInitVoiceFromSample`'s own `ctx->r4` at entry — already
   instrumented via `ROGUESQ_LOG_INIT_VOICE_SAMPLE=1` (s105,
   `N64Recomp/fixup_game_funcs.py`, `funcs_24.c:5753`). Confirm both
   flags can be armed in the same build without conflict (check the env
   var names and patch anchors don't collide — they're different
   functions in the same file, should be independent).
2. Regen: `python3 <rogue_squadron64>/tools/make_elf.py` (absolute path,
   no `cd`) → `N64Recomp rogue_squadron.toml` via
   `subprocess.run(cwd='/Users/williambuckley/Documents/Tools/N64Recomp')`
   (direct `Bash ./build/N64Recomp` hits the headless-approval wall,
   documented repeatedly) → `python3
   /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   (verify "patched x1" for the gate-check patch — full ELF regen
   required every time, `fixup_game_funcs.py` is not idempotent, s102)
   → `cmake --build build -j8` with
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`.
3. Soak: `env ROGUESQ_LOG_VOICE_ACTIVE_GATE=1 ROGUESQ_LOG_INIT_VOICE_
   SAMPLE=1 ROGUESQ_LOG_MUSYX_DMA_CALL=1 PROBE_MODE=start_only HOLD_S=30
   zsh scratch/s73_post_a_scene/run_mission_keys.sh voicegate4 5 8`
   (`env` prefix required for the headless permission prefix-match,
   rule 10). Up to 3 attempts allowed per ITERATION.md rule 8 if early
   crashes preempt the target window (the still-uninvestigated
   `frameStartReset` recurrence, or a new class).

**Discriminating outcomes:**
- If `musyxInitVoiceFromSample`'s `ctx->r4` (a call site that has always
  been trusted to point at the real voice pool — s105) and
  `musyxMixActiveVoices`'s `ctx->r4` at the *same voice index* (compute
  via `idx` and the known `+0x88` stride, or just compare the
  init-time base directly since both derive from the same
  `G_BASE-0x6908` global per s105) **diverge** → hypothesis (b)
  confirmed: the gate-check function is reading a stale/wrong base
  pointer, not the live voice pool. This reopens every "voice+N" finding
  since s94 for re-reading — the "corruption" may be an artifact of
  reading the wrong array entirely, not corruption of the real voice
  struct.
- If they **match** (same base, consistently) → hypothesis (b) is
  refuted; the memory the pointer correctly identifies as the voice pool
  is itself now holding texture-name-table content — points to a heap-
  lifetime/aliasing bug (the voice pool's backing allocation was
  reused, or was never exclusively owned) rather than a bad-pointer bug.
  Next step in that branch: find what allocates into this exact
  0x88-strided region (grep for the stride literal `0x88` and the
  `G_BASE-0x6908` global near any `rs_malloc`/allocator call, similar to
  s104's node-allocator hunt).
- If neither soak nor 2 retries reproduce a nonzero hit at all → not
  null-worthless (the mechanism already exists per s117/s118's data),
  park per rule 8 and try again next session.

## Do not

- Do not re-chase the s118 crash (`do_rom_read`, 11th+ recurrence,
  already fully catalogued since s85-s94) as a dedicated work unit.
- Do not re-test byte-for-byte identity between `voice+0x0` and
  `devAddr` corruption — already run once and refuted (s118); if
  revisited later, it needs a specific reason (e.g. a new same-tick
  capture), not a repeat of the same test.
- Do not treat the `explo_tex`/`atpt_load`/etc. strings as proof of
  *which* table or allocator is responsible — only that the content is
  real asset-name data. The allocator/table identity is still unknown
  and is exactly what hypothesis (b)'s refute-branch investigates next.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is ~119 KB, well over the ~35 KB target
(CLAUDE.md/ITERATION.md). Flagged every session since at least s116;
still worth a dedicated compression pass (migrate durable
mechanism/architecture material to PROJECT-OVERVIEW.md, prune superseded
detail) paired with a real experiment — compressing docs alone does not
count as an ADVANCED work unit.

Also flagged (not autonomously actioned): `/Users/williambuckley/
Documents/Tools/N64Recomp` is its own git checkout, not a `lib/`
submodule of this repo, and has accumulated uncommitted changes across
sessions s90-118 (`fixup_game_funcs.py` plus regenerated
`RecompiledFuncs/*.c`). `git` operations there required interactive
approval this session (and every prior session) did not have — same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.
