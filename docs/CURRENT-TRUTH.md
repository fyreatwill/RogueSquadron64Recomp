# Rogue Squadron 64 Recomp — current truth

Compact operational handoff, maintained at Session 5134 (2026-10-17). The
chronological ledger is `PORTING-STATE.md`; durable background belongs in
`docs/PROJECT-OVERVIEW.md`; per-topic evidence is in the `docs/M5-S*.md` and
`docs/RENAME-S*.md` audit files.

## Headline

The validated route boots through attribution, N64 logo, intro, Factor 5 logo,
title (`0x00790400`, VI 1024), hangar (`0x006AB400`, VI 512), and mission
origins (`0x00690400` and later `0x00620400`, VI 512). Audio is active on the
qualified image route; the silent `ROGUESQ_AUDIO_UCODE=0` path is only a
control. Mission input reaches the game and changes the player vehicle state.

The current bounded work is the generated-symbol renaming sweep. The last
candidates, `cosf = 0x8002B190`, `osCreateMesgQueue = 0x8002B300`, and
`osCreateThread = 0x8002B330`, were already synchronized: `cosf` has its
generated body, exact `0x170` span, and 75 callers; the two libultra entries
are zero-size host-wrapper/ABI entries with 28 and 10 generated call sites.
`osDestroyThread = 0x8002B480` is also a zero-size host-wrapper/ABI entry with
one generated caller and no body to rename. `osDpGetCounters = 0x8002B590`
and `osDpSetStatus = 0x8002B5E0` are likewise host-wrapper/ABI entries: their
generated trees have no bodies or overlay records, with two ABI call sites
each. The preamble at `0x8002B5F0` is the same ABI-boundary case with no
generated caller. `__osException = 0x8002B600` is the same ABI-boundary case:
it has no generated body, overlay record, or direct generated caller. The next
candidate is `__osLeoInterrupt = 0x8002C500`; the intervening
`__osRestoreInt = 0x8002C260` is likewise an ABI-boundary entry with an
overlay record of `rom_size = 0` and only one generated caller, with no body
to rename.

This maintenance iteration compacted the previous 611-line state file. The
removed historical narrative remains recoverable in git; durable conclusions
were retained below or in the project overview.

## Durable state

### M5 audio

- The image route produces nonzero PCM and passes title, hangar, and mission
  phase controls. AI byte order is corrected. The audio task is not currently
  a zero-output stub, although the MusyX/MORT compatibility work is not fully
  complete.
- Mission route joins show fresh audio ordinals and row-0 resets at the
  `0x00690400 -> 0x00620400` handoff. Treat this as route reinitialization,
  not grounds for filtering.
- The voice-render range fires in retail title/hangar, but exact consumer
  `0x800903F0` remains absent in retail. The port-only mixer overrun remains
  an internal boundary; do not add a guard without a writer explanation.
- First-teardown synth deregistration is fixed. The covered route does not
  reach `shutdownAudioEngine`; callback registration is not proof of shutdown.
- The M5 plan and its execution sequence are in `docs/M5-AUDIO-PLAN.md`.

### M3 and rendering

- M3 idiom audits are closed for the previously enumerated trap/break/syscall/
  cop0, unaligned and LL/SC/cache, division, float/FCSR, memory-width,
  indirect-call, self-walk, branch-likely, variable-shift, HI/LO, 64-bit
  shift, 32-bit multiply, and 64-bit mul/div classes. Do not repeat a class
  without new recompiler or provenance evidence.
- `movz`/`movn` support is complete in N64Recomp and fixup tooling.
- The Factor 5 runaway-DL cause is known: op `0xBD` loads overlay `0x2C`
  (ROM `0x27368`, destination `0x1DB0`) without a route. The splice effect
  remains parked.
- Native hangar artifacts (rim band, holo spikes, stale right edge) remain
  localized. M4 accumulator origin, pillar references, `0x1F0D74`, odd PI
  DMA, and external retail-entry are parked pending a new discriminator.

### Generated-symbol sweep

- Continue one companion entry at a time only when semantic name, exact body
  span, and a live generated caller support a rename.
- Host wrappers and zero-span entries retain their `_recomp` ABI names. A
  rename helper result of `already-synchronized` is a no-change result, not a
  runtime issue.
- `__osGetSR = 0x8002C230` is another companion-only libultra entry: the
  helper, generated-tree search, and overlay table show no generated body or
  caller, so its ABI name is preserved. Audit: `docs/RENAME-S5132-AUDIT.md`.
- Recent classifications: `bcmp` and `bzero` were renamed with exact spans;
  EEPROM/controller entries through `__osPackReadData` were classified as
  host wrappers or ABI boundaries. Audits are `docs/RENAME-S5106-AUDIT.md`
  through `docs/RENAME-S5134-AUDIT.md`.

## Operational rules

- Read `docs/F5-UCODE-REFERENCE.md` before interpreting Factor 5 command or
  display-list behavior. The retail oracle is independent ground truth and
  requires whole-RDRAM, VI, and phase positive controls before a null matters.
- Batch all counters and A/B arms into one build/run. Phase-gate animated
  comparisons; run-lifetime zeroes are not evidence for later phases.
- A mitigation-shaped change must identify its writer and state whether the
  value is legitimate. A guard is not an explanation.
- Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
  cmake`. Generated behavior edits belong in fixup tooling or patches, not
  directly in generated C. Never reset, clean, checkout, or update a
  submodule; export submodule patches after any `lib/` edit.
- Run the game from `build/`, keep the ROM present, capture output to a file,
  and kill test processes with SIGKILL. Use the soak queue for repeat runs.
- The MIPS GCC toolchain is still absent, so PatchesLib qualification remains
  blocked; do not repeat that command until the toolchain is supplied.

## Parked and closed

- External retail-entry is qualified through title/hangar/mission on the Rice
  route; the old exact PC boundary is not a current target.
- The M4 accumulator boundary is closed at task-end granularity: hangar
  `0x8000` lane counts matched retail (port 0/1955, retail 0/576). A new
  retail cxd4 oracle run sampled mid-task state and found 0/289 hangar tasks
  with a `0x8000` lane (0/577 across all 512-wide tasks). This is
  single-source retail evidence, not a port explanation; see
  `docs/REVISIT-S5129-AUDIT.md`.
- Heap/copy/message-queue/PI-DMA and audited host-wrapper pointer classes are
  closed on the qualified keyed route with positive controls. Re-open only on
  a phase-qualified recurrence.
- The mission input thread is closed: stick state at `0x80130B88` reaches
  flight code; the player vehicle object at `0x80138458` moves normally.
- The s4296 A14 yield patch is present and guarded by
  `tools/check_a14_yield_patch.py`; the prior mission shutdown spin was traced
  to its missing generated patch, not a new audio diagnosis.

## Superseded conclusions worth retaining

- Earlier claims that M5 was fully closed were too broad: nonzero PCM proves
  route activity, not every audio contract.
- Earlier claims that the loop had no runnable target were overturned when a
  mission-qualified soak became available; use `scratch/agent/NEXT.md` and
  the soak queue rather than declaring a block from a stale backlog.
- The old exact retail-entry and stale-base voice theories are not current
  explanations. Their guarded/atomic/lock variants either remained live or
  were route-blocking; no value rewrite was authorized.

## Next steps (single monotonic backlog)

1. Audit `__osLeoInterrupt = 0x8002C500` using the bounded rename helper. Rename only
   if the generated body, exact next-entry span, semantic mapping, and live
   caller all agree; otherwise preserve the ABI name and record the
   classification.
2. Continue the companion sweep one entry per iteration while the last-15
   session preflight permits it. If the preflight makes the sweep a REVISIT,
   return to the external retail-entry or M4 boundary only with a genuinely
   new discriminator.
3. If a new M5 step is selected, write its design and validation row in
   `docs/M5-AUDIO-PLAN.md` before changing runtime behavior.
4. When MIPS GCC is supplied, configure and qualify `PatchesLib`; record
   generation, compile, and link outcomes in the ledger.

## Evidence index

Use `PORTING-STATE.md` for session detail, `docs/PROJECT-OVERVIEW.md` for
archived durable history, `docs/M5-AUDIO-PLAN.md` for the audio sequence, and
the per-session audit/soak paths named above. The next iteration must read
this file, `scratch/agent/NEXT.md`, and the tail of
`scratch/agent/SOAK-RESULTS.md` before acting.
