# NEXT work unit — M3: enumerate static writers of `voice+0x34` (s111)

s110 guarded the 17th hangar-tick class (`updateHangarBayScene`, 5 separate
guard sites in one function — source-read found the family's usual single
bad-pointer shape repeats 5 times here, not once). Landed clean (0/5
negative control), and the soak reached the ~140s DMA window alive for
only the 2nd time ever (after s101) — zero hangar-tick-family crashes this
run. It then died to the 10th recurrence of the same `do_rom_read`
corruption chain that's blocked M3 since s85. Read PORTING-STATE.md's
Session 110 entry before doing anything else; this file only has the
actionable summary.

## Why this is the next work unit

The hangar-tick-family guard program (5 classes deep: 16th/12th/11th/14th/
17th) now has **two independent soaks** (s101, s110) reaching the DMA
window with zero family crashes — reaching the window is no longer the
bottleneck it was for s102-s109. The actual, unchanged M3 blocker is the
`do_rom_read`/`fillSampleStreamRange` corruption chain (10 occurrences
since s85, always byte-identical: `devAddr=0x6C676672
dramAddr=0x80195190 bytes=0x600`, confirmed deterministic not a race).
s110 also **retired the tick-audio-channel investigative thread**
(5 sessions — s105, s106, s107, s108, s110 — all null on
`tickAudioChannel`/`serviceVoicePoolFrame`/`musyxInitVoiceFromSample`/
`musyx-gate1`, and s110's null is the first to co-occur with the process
actually alive through the whole target window, ruling out "didn't run
long enough"). Continuing to chase callers one hop at a time down that
chain is no longer a good bet — pivot to a direct, no-soak-required
source search.

## What's confirmed (do not re-derive)

- The corrupted field is `voice+0x34` (a per-voice-slot struct, base
  pattern `G_BASE-0x6908 + voiceIdx*0x88`, established s105 via three
  independent offset checks against `musyxRenderVoiceSamples`).
  `fillSampleStreamRange` computes `entry.devAddr` as a sum of two other
  fields sourced from a *different* linked list than
  `acquireSampleStreamBlock` manages (s103); its own arguments are
  **already corrupted at function entry** (s104, `ROGUESQ_LOG_FILL_RANGE_
  ARGS=1`, byte-for-byte match to the batch's known corrupted `devAddr`).
- **Cleared as writers** (do not re-instrument): `acquireSampleStreamBlock`
  (s103, never entered this scene), `initSampleStreamBlockCache`/node
  allocator (s104, only ever writes fields `0x0`/`0x4`/`0x14`, and every
  node-reclaim path recomputes `0x8` fresh before use), `musyxKeyOnVoice`
  (s105, writes a different global entirely), `musyxInitVoiceFromSample`
  (s105/106, does a clean verbatim copy, both call sites build their
  source struct fresh from local data — 0/0 across 2 soaks, one with a
  positive control on the surrounding system).
- **Retired, do not resume** (s110): the `tickAudioChannel`/
  `tickAudioSequencerFrame`/`tickAllAudioChannels`/`serviceVoicePoolFrame`/
  `musyx-gate1` countdown-divider chain. 5 sessions null, including one
  (s110) where the process ran the full target window alive. The chain is
  real and correctly instrumented (per s106/s107's own source reads) — it
  just never executes in the hangar-bay-selection scene, which is
  strong evidence the whole "corruption enters via a key-on/trigger event"
  framing was a coincidental structural match, not the actual mechanism.
- The hangar-tick-family guard program is not queued for further work
  unless a class recurs — see CURRENT-TRUTH item 0b. Do not re-soak the
  five guarded classes in isolation.
- `fixup_game_funcs.py` is still not idempotent (flagged since s102, hit
  again firsthand s110 — a bare *second run* to check its own report,
  no logic change, duplicated every patch and broke the build). Always
  do a full ELF regen before running it, and run it exactly **once** per
  regen — do not re-run it "just to check the report."

## The work unit

1. **Grep-enumerate every static write to offset `0x34` off a
   voice-slot-shaped base pointer**, across all of
   `N64Recomp/RecompiledFuncs/*.c`. Concretely:
   - Start broad: `grep -n "0X34)" N64Recomp/RecompiledFuncs/*.c` for any
     `MEM_W(..., 0X34)` (or `MEM_W(0X34, ...)`, check both call-argument
     orders used in this codebase) assignment, then narrow by checking
     each hit's base register traces back to a `G_BASE-0x6908 +
     voiceIdx*0x88`-shaped computation (the s105-confirmed voice-slot
     address pattern) rather than an unrelated struct that happens to
     share offset `0x34`.
   - `musyxInitVoiceFromSample` is already a confirmed writer (s105,
     `voice+0x34 = sampleDesc+0x4`) — use its exact base-pointer
     computation as the template for recognizing the same base elsewhere.
   - This is a source-read/grep task, not a soak — no build or run
     required to produce the candidate list.
2. **For each new candidate**, source-read (not soak) to classify it the
   same way s105 classified `musyxInitVoiceFromSample`'s two call sites:
   does it build its written value from a fresh, locally-sourced struct
   (unlikely to be the bug), or copy/derive it from something that could
   plausibly be a name/tag/index field misread as a ROM offset (matches
   the "lg?r"/"wi?g" corruption shape characterized s102)?
3. **If a plausible candidate emerges**, that becomes next session's
   instrumentation target (one new `ROGUESQ_LOG_*` diagnostic, one soak).
   **If the grep turns up nothing beyond the already-cleared writers**,
   that's a real, useful result too — it would mean the corruption enters
   through something that is *not* a direct `MEM_W(..., 0x34)` store in
   the recompiled guest code at all (e.g. an LLE RSP-side write via
   `MEM_W`/DMA from microcode, or the `-O2` recompiler folding an
   equivalent store into a different instruction shape that a literal
   `0x34` offset grep would miss) — write that down explicitly rather than
   treating "grep found nothing" as inconclusive.

## Also flagged (s110, not this session's job)

- **New, unexplained observation**: 385 lines of `Unhandled jump target
  0x1883 in microcode factor5_ucode` fired in the s110 soak — the first
  time this specific diagnostic (distinct from the guest-side
  `UnhandledJumpTarget` family metric, always 0 in every prior soak) has
  ever read nonzero. This is the RSP MusyX audio-microcode LLE path,
  which M5's notes describe as "recompiles but is never called" — this
  run suggests it may actually run and hit unimplemented jump targets.
  Not chased this session; worth a dedicated look eventually (M5-adjacent,
  gated behind M2 per the goal stack, so likely not immediately next).
- The two single-occurrence classes that blocked s108/s109 (probable-18th
  `heapFreeListDequeue`-area, 19th `MetalFramebuffer`/
  `createTileCopyRecord`) did not recur in s110. Still below the
  2nd-recurrence bar — watch passively, do not instrument yet.
- The 14th class's guard (`ROGUESQ_LOG_DLENTRY_GUARD`) and the new 17th
  class's guard (`ROGUESQ_LOG_HANGAR_BAY_SCENE_GUARD`) still have no
  positive control. Leave both armed in every soak; a free fire is a
  bonus, not a reason to design a soak around chasing it.

## Tooling note — bit us again this session, still cheap to fix

`fixup_game_funcs.py` is **not idempotent** by construction (every
patch's anchor regex matches text left unchanged after insertion). s110
hit this from a new angle: running the script a *second* time with no
logic change, purely to print its own report for a sanity check, silently
duplicated every patch and broke the build (`redefinition of label
'L_dlentry_guard_exit'` in an unrelated file, `funcs_3.c`). The existing
workaround (full ELF regen before every fixup run) still works, but this
is now the 8th session in a row dodging the same bug. If a session
touches `fixup_game_funcs.py` again, consider actually fixing it: make
each patch's anchor regex also require a negative lookahead that the
match is **not** immediately followed by `    { // PATCH:`. Test by
running the script twice in a row on an already-regenerated tree and
confirming the 2nd run reports 0/"no changes needed" for every
already-landed patch.

## Housekeeping flagged, not this session's job either

`docs/CURRENT-TRUTH.md` is now ~106 KB, roughly 3x the ~35KB target in
CLAUDE.md/ITERATION.md, and grew again this session. This has been
flagged for several sessions running without action — worth a dedicated
compression work unit (migrate durable mechanism/architecture material to
PROJECT-OVERVIEW.md, prune superseded detail more aggressively,
especially the now-closed hangar-tick-family guard narration which could
collapse to a short table) paired with a real experiment per ITERATION.md
(compressing docs alone does not count as an ADVANCED work unit).

## Do not

- Do not re-soak the five already-guarded classes (16th, 12th, 11th,
  14th, 17th) in isolation — treat them as closed pending an eventual
  positive control that arrives for free from an unrelated soak.
- Do not instrument the probable-18th or 19th classes yet — both are
  single-occurrence; wait for a 2nd hit.
- Do not resume the tick-audio-channel/`musyx-gate1` investigative
  thread — retired s110 after 5 null sessions, one with a full-window-alive
  null. If a future soak's evidence changes (e.g. one of those counters
  finally fires), that's new information and can reopen the question —
  but don't design a soak around chasing it again.
- Do not run `fixup_game_funcs.py` more than once per ELF regen, even
  just to view its report — do a fresh `make_elf.py`/`N64Recomp` regen
  first if you need to re-run it for any reason.
- Do not cite `ra=0x00000000` as corruption evidence (refuted s92); do not
  re-open "random/race/stomp" framings for the `devAddr` corruption (10+
  independent lines of evidence against all three, now including 2
  sessions — s101, s110 — where the corruption recurred byte-identical
  after reaching the window through entirely different guard states).
- `N64Recomp/fixup_game_funcs.py` is untracked in N64Recomp's own git, by
  design — do not attempt to commit it there; the durable record lives in
  `PORTING-STATE.md`/`CURRENT-TRUTH.md` in this repo.
