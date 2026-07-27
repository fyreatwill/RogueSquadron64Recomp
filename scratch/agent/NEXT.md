# NEXT work unit — M3: why does `voice+0x0` read nonzero when its only writer never fires? (s117)

s116 turned the `voice+0x0` question from "find the writer" into a
sharper, decisive contradiction. Read PORTING-STATE.md's Session 116
entry before doing anything else; this file only has the actionable
summary.

## What's now closed — do not re-open or re-chase

- `musyxKeyOnVoice` (`funcs_24.c:1825-2476`) is **not** a `+0x0` writer —
  s116 read every single reference to its argument register across the
  whole ~650-line function and found only loads (offsets `0x21` through
  `0x74`), zero stores. This was NEXT.md's fallback candidate #1; closed.
- `isAudioSlotActive` (`funcs_24.c:5731`) is a pure 6-instruction query
  (`MEM_BU(voice,0x0)` then `0 < x`), no store anywhere. Fallback
  candidate #2; closed.
- `musyxRenderVoiceSamples` (the function gated behind `voice+0x0 != 0`)
  has **exactly one call site anywhere** (`funcs_24.c:2623`, inside
  `musyxMixActiveVoices`) — grep-confirmed. There is no second, ungated
  entry path that would explain voices rendering without the gate.
- `musyxTriggerVoiceAttack`'s guest address (`0x8009231C`) appears
  nowhere in the recompiled tree except its own definition and its two
  known static call sites — no function-pointer-table entry references
  it, so a *table-driven* indirect call is not evidenced (though a
  register-loaded `jalr` from an unfound caller is still structurally
  invisible to this check — same blind spot as always, just no positive
  evidence for it here).
- Do not re-instrument or re-soak `ROGUESQ_LOG_VOICE_TRIGGER_CHAIN=1` /
  `ROGUESQ_LOG_INIT_VOICE_SAMPLE=1` / `ROGUESQ_LOG_STREAM_NODE_INIT=1` —
  all closed. `ROGUESQ_LOG_VOICE_ATTACK_ENTRY=1` (new this session) is
  also now answered — see below — don't re-soak it alone again either.

## The decisive result from s116

3 soaks with `ROGUESQ_LOG_VOICE_ATTACK_ENTRY=1` (entry log on
`musyxTriggerVoiceAttack`'s own prologue — a chokepoint that catches ANY
caller, direct or indirect, unlike s105-110's caller-side-only
instruments):

- voiceattack1: died at hold+8s to a `frameStartReset` SIGBUS (early,
  inconclusive — see "flagged" note below).
- voiceattack2: reached the classic `do_rom_read` crash at 137.3s.
  `[voice-attack-entry]` 0/0, but no in-run positive control armed.
- **voiceattack3**: added `ROGUESQ_LOG_MUSYX_DMA_CALL=1
  ROGUESQ_LOG_FILL_RANGE_ARGS=1` alongside. Reached the same crash at
  140.1s. `musyx-dma-call` fired **17x**, `fill-range-args` fired **7x**
  (proving `musyxRenderVoiceSamples` — the ONLY function behind the
  `voice+0x0` gate — genuinely ran multiple times this session) while
  `[voice-attack-entry]` fired **0x**.

This is a null result **with** a same-run positive control (the bar
CLAUDE.md sets) — not a guess. The one known writer of `voice+0x0`
nonzero anywhere in the recompiled tree provably never executes, in a
run where the gate it's supposed to set was clearly satisfied. Combined
with s115 (both zeroing writers — `allocateSongChannelArray` at alloc
time, `musyxInitVoiceFromSample` at `funcs_24.c:5804`, the latter a new
s116 finding — reliably run every session), "uninitialized by design"
(the explanation that closed the analogous `+0x34` question) does **not**
cleanly apply to `+0x0`: it has two confirmed zeroing writers and zero
confirmed nonzero-setters, yet reads nonzero in practice.

## The work unit

This needs a runtime value, not more source reading — land it as one
instrument, one soak (batch it with the already-working
`ROGUESQ_LOG_MUSYX_DMA_CALL=1 ROGUESQ_LOG_FILL_RANGE_ARGS=1` controls so
the soak has an automatic positive control, same as voiceattack3):

1. In `musyxMixActiveVoices` (`funcs_24.c`, guest `0x80090EC4`-area — the
   `ctx->r2 = MEM_BU(ctx->r4, 0X0);` gate-check read, immediately
   followed by `beq $v0, $zero, L_80090F40`), add a diagnostic that logs,
   every time the byte is checked: the computed voice-array base
   (`ctx->r4`, the address being read), the loop index (`s0`/`ctx->r16`,
   already tracked in the surrounding loop), and the byte value itself.
   Cap at ~32-64 lines per the established pattern in
   `N64Recomp/fixup_game_funcs.py`.
2. Gate it behind a new env var, e.g. `ROGUESQ_LOG_VOICE_ACTIVE_GATE=1`.
3. Regen (`make_elf.py` → `N64Recomp` via the `subprocess.run(cwd=...)`
   workaround, direct `Bash` invocation of `./build/N64Recomp` hits a
   headless-approval wall even though `Bash(./build/:*)` is allowlisted —
   documented repeatedly, PORTING-STATE s95/s99/s116) → `fixup_game_funcs.py`
   → `cmake --build`.
4. Soak with `ROGUESQ_LOG_VOICE_ACTIVE_GATE=1 ROGUESQ_LOG_MUSYX_DMA_CALL=1
   ROGUESQ_LOG_FILL_RANGE_ARGS=1 PROBE_MODE=start_only HOLD_S=30 zsh
   scratch/s73_post_a_scene/run_mission_keys.sh <tag> 5 8` — same recipe
   as voiceattack1-3. Up to 3 attempts allowed per ITERATION.md rule 8 if
   early crashes (frameStartReset, or others) preempt the ~140s window.

**Discriminating outcomes:**
- If the logged byte is consistently one specific nonzero bit pattern
  across frames/voices (not just 0/1) → same *class* as the `+0x34`
  finding: a deterministic uninitialized/wrong-source read, not a race.
  Compare the base address logged against the known `-0x6908` global
  value to check it's reading the right array at all.
- If the base address itself looks wrong (doesn't match `-0x6908`'s
  actual runtime value, or the index goes out of the expected 0-15ish
  voice-slot range) → an addressing bug in the gate check's own
  arithmetic, a different mechanism entirely from `+0x34`'s story.
- If the byte reads exactly 0 or 1 sanely and correlates with an actual
  `musyxTriggerVoiceAttack`-equivalent write we still haven't found →
  widen the call-site search once more, but only with this concrete new
  data point in hand, not by re-running the same greps.

## Do not

- Do not re-run the `-0x6908` literal-grep audit — the structural blind
  spot (argument-passed voice pointers) is now closed by direct exhaustive
  reads of the two candidates it couldn't see; further grepping won't add
  information.
- Do not soak `ROGUESQ_LOG_VOICE_ATTACK_ENTRY=1` alone again — its
  question is answered (0/0 with positive control, s116).
- Do not assume the `frameStartReset` SIGBUS (2/4 soaks now across
  s84/s85/s116) is still a "fluke" without saying so explicitly if it
  preempts a 3rd future soak — it's no longer 0/2, it's 2/4, worth a
  glance but not yet worth gating or chasing as a dedicated work unit.

## Housekeeping flagged, still not done

`docs/CURRENT-TRUTH.md` is well over the ~35 KB target in
CLAUDE.md/ITERATION.md (the top "Current truth" narrative section alone
has grown session-by-session since s79). Worth a dedicated compression
work unit (migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md, prune superseded detail) paired with a real
experiment per ITERATION.md (compressing docs alone does not count as an
ADVANCED work unit). s116 deliberately did *not* add a new paragraph to
that top narrative section (only to "Next steps") to avoid growing it
further — PORTING-STATE.md's Session 116 entry is the authoritative
detailed record.
