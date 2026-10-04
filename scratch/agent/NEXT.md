# Next work unit: retail-vs-port title-music AI output (operator redirect)

HYPOTHESIS-ID: m5-title-music-ai-parity

OPERATOR REDIRECT (2026-10-04, after session 4062). The hangar source-writer
census (`m5-source-writer-census`) is CLOSED, not paused. Session 3820 showed
retail's own hangar-phase source span `0x1798B0..` is 408 bytes, nonzero=0,
`FNV=0x762B22A5` — byte-identical to the port. A zero buffer that matches
retail is parity, not a defect, so there is no missing hangar writer to find.
Do not arm further candidate PCs against the hangar span (`0x800076A0` and
any later ranked class are cancelled).

The new question is end-to-end and starts where sound is audible on real
hardware: the title screen (VI 1024, origin `0x00790400`), which plays music.
Measure from the speaker backwards, not from a guessed writer forwards.

Competing hypotheses:

- H1: retail title-phase AI buffers (`osAiSetNextBuffer` address/length, the
  PCM at that address) are nonzero, and the port's title-phase AI buffers are
  zero -> a real port defect exists at title; the next unit walks back one hop
  (which RSP audio task wrote that PCM, and what input it read) in retail first.
- H2: retail and port title-phase AI PCM are both nonzero -> title audio is
  already being produced in the port; the problem is the host audio sink
  (librecomp `ai.cpp` drain/queue) or the real-audio arm is not selected.
- H3: retail title-phase AI PCM is also zero (or retail issues no AI buffers
  in the title phase) -> title is the wrong reference; move the same
  measurement to the first phase where retail AI PCM is nonzero (attract
  cinematic or in-mission) before any port comparison.

Discriminating measurement (ONE instrument, ONE build, ONE paired run, per
ITERATION rule 14):

- Retail oracle (mupen64plus + rsp-hle, which executes MusyX audio tasks):
  keep the whole-RDRAM, title-1024 and hangar-512 positive controls. Record,
  per VI phase bucket (pre-title / title-1024 / hangar-512), each AI_DRAM_ADDR
  + AI_LEN write and an FNV + nonzero-byte count of the RDRAM PCM at that
  address at the time of the write. If the oracle cannot observe AI register
  writes, attribute via the PC of `osAiSetNextBuffer` and read `$a0/$a1`.
- Port, qualified declared-real arm only (legacy-real is pre-target and must
  not be used), same buckets: hook `osAiSetNextBuffer_recomp`
  (`lib/N64ModernRuntime/librecomp/src/ai.cpp:75`) with the same FNV +
  nonzero count; reuse the existing `ROGUESQ_LOG_M5_AUDIO_DRAIN` /
  `ROGUESQ_LOG_M5_AI_STATE` plumbing rather than adding a parallel logger.
  Include the silent `ROGUESQ_AUDIO_UCODE=0` arm as the zero control.
- Selection: H1 = retail title nonzero AND port declared-real title zero;
  H2 = both nonzero; H3 = retail title zero/absent. Any missing control or
  target phase makes the run unevaluable, not a null.

The instrument itself (the AI-buffer FNV logging in oracle and port) is
engineering that should be committed, so this unit is not a diagnostic-only
iteration.
