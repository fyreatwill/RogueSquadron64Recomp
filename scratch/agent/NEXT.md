# NEXT work unit

## s375 ran s374's own discriminating measurement — mechanism REFUTED, HYPOTHESIS-ID CLOSED

Full write-up: `docs/CURRENT-TRUTH.md` item -229, `PORTING-STATE.md` Session 375. One-paragraph
version: the single-token-mutex-deadlock mechanism s374 proposed for the C88-reversed pre-title
"hang" is refuted. Batched trace instrumentation around `initFactor5Mutex`/`factor5MutexAcquire`/
`factor5MutexRelease` (`fixup_game_funcs.py`, `funcs_24.c`, kept in the tree, inert/env-gated under
the shipped default), one soak with C88 temporarily reversed (`ROGUESQ_LOG_F5MUTEX=1`, reverted
before commit, default rebuilt clean): `factor5MutexAcquire` entered and exited **9131/9131** times,
perfectly balanced, continuing steadily hundreds of seconds past the 2.2s point where `[phase]
vi_width=` sticks at 640 — it never blocks. Bonus finding: `initFactor5Mutex` (claimed "every video
frame" in items -227/-228) actually fired only **6 times** in the whole 180s run — that specific
framing is now flagged suspect, not re-asserted. **What's confirmed instead**: C88-reversed is not a
hang/deadlock at all — the process stays fully alive (mutex cycling, DMA ring progressing,
`musyxSynthFrame` ticking) but never re-triggers the VI 640→1024 framebuffer-swap transition. This is
the exact benign `pairs=0`/`SET_COLOR_IMAGE`-never-re-emitted plateau PROJECT-OVERVIEW §10 already
characterized for the cutscene-locked-camera case — the open question is why C88-reversed never
*exits* that state the way the gate=0 baseline does.

## This iteration's work unit: SOURCE-ONLY trace of what drives the VI 640→1024 transition (no build)

Per the project's own convention (source pass before spending a build+soak cycle — this is what s374
did and it correctly narrowed the field before s375 spent the soak), do not build yet.

**Question**: under the gate=0 (shipped) baseline, `setDisplayMode`'s gate site is reversed (live)
but `reapplyDisplayMode`'s (C88) is force-zeroed, and title-reach works 3/3 (s343/s344). Under
C88-ALSO-reversed, title-reach is 0/6. Something that differs between "audio gate force-zeroed at
the end of `reapplyDisplayMode`" and "audio gate genuinely live" structurally blocks whatever
advances the game out of the post-cutscene/pre-title state. Find that trigger.

### Competing hypotheses (name what confirms/refutes each before reading further)

- **H1 — reset-branch divergence**: `reapplyDisplayMode`'s conditional song/voice/stream reset block
  (`resetSongSubsystemCounter`, `initSongSequencerPools`, `resetMusyXEngineState`,
  `clearStreamedVoiceFlags`, `reset3DAudioLists` — `funcs_23.c:9905-10009`, item -227) only runs when
  `reapplyAudioConfig` returns 0. If a genuinely-live audio gate changes that return value (real vs.
  stubbed audio state), the branch — or specific calls inside it — might be skipped, and one of those
  calls (or code downstream of them) might be what actually clears a "scene busy"/"waiting on audio"
  flag the transition logic reads. CONFIRMS if: tracing `reapplyAudioConfig`'s return-value logic
  shows it depends on gate-byte-adjacent state that's different once the gate is genuinely 1.
  REFUTES if: `reapplyAudioConfig`'s return path is unconditional/gate-independent.
- **H2 — shared-mutable-state collision** (the project's own documented recurring hurdle class,
  PROJECT-OVERVIEW §4.4): under gate=1, `tickMusyXIfActive`'s newly-live `tickActiveSongs`/
  `tickAndReap3DAudioVoices` calls run real logic for the first time ever and may write/decrement a
  counter or list also read by the video-frame-tick or scene-transition logic. CONFIRMS if: grepping
  those two functions' write targets turns up an address also read by `runVideoFrameTick` or whatever
  function actually calls `SET_COLOR_IMAGE`/advances the scene. REFUTES if: their write sets are
  disjoint from any transition-logic read set.
- **H3 — real completion-condition wait**: some code (possibly NOT on the audio call chain at all —
  the logo/intro state machine, a loading-complete check) polls a "has audio finished
  initializing/loading" flag that's only meaningful once the gate is genuinely live, and that flag
  never resolves because the underlying MusyX engine is still fundamentally degenerate beneath the
  gate (per s371: PCM is 100% zero even when "live"). CONFIRMS if: a wait/poll loop referencing the
  gate byte (`0x800A0F50`) or an adjacent audio-state global is found OUTSIDE the already-traced
  `waitForAnyAudioSlot`/mutex call chain. REFUTES if: no such external poll exists.
- **H4 — red herring, no single trigger exists**: the "640→1024 transition" isn't one call site at
  all but an emergent effect of overall frame timing/ordering that shifts once real audio processing
  consumes cycles differently — no single guarded site to find. This is the fallback if H1-H3 all
  refute; if reached, the next move is a build+soak with broader instrumentation (frame-timing
  histogram), not more source reading.

### Where to start (no build required for this pass)
1. Read `funcs_23.c` around `reapplyAudioConfig`'s full body and return-value construction
   (`funcs_24.c:5046` onward) — does its return value structurally depend on the gate byte or on
   `factor5MutexAcquire`/`Release` call outcomes?
2. Read `tickActiveSongs`/`tickAndReap3DAudioVoices` (already partially traced s174/s373) for write
   targets — cross-reference against globals `runVideoFrameTick` or whatever function actually calls
   `SET_COLOR_IMAGE` reads (item -195/PROJECT-OVERVIEW §10 names `submitGfxFrame`,
   `emitFrameRdpInitDl`, `advanceVideoFrame`, `runVideoFrameTick` as the relevant call chain — start
   there).
3. Grep the whole `RecompiledFuncs/` tree for reads of `0x800A0F50` (the gate byte) OUTSIDE the
   already-documented `tickMusyXIfActive`/`waitForAnyAudioSlot`/mutex chain — any hit is a candidate
   H3 site.

Write down which hypothesis each finding supports/refutes as you go — this pass's job is to narrow
to ONE testable mechanism (like s374 did), not to solve it outright. If a clear single candidate
emerges, next iteration's work unit is the build+soak that confirms it (same pattern as s374→s375).
If nothing testable emerges after this one source pass, that itself is a result — write up why H1-H3
were checked and refuted, and decide between H4 (broader instrumentation) or pivoting fully to M3
per the strategic-priority fallback.

## Iteration budget

HYPOTHESIS-ID: m5-audio-vi640to1024-trigger-site (iteration 1 of budget — new thread, previous
HYPOTHESIS-ID m5-audio-destub-c88-pretitle-hang CLOSED this session on a clean refutation, not
exhausted budget, so this is a fresh 3-iteration allowance).
