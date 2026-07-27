# NEXT work unit — M3: read how factor5_ucode's RSP dispatch handles jump target 0x1883 (s112)

s111 retired the "enumerate static writers of `voice+0x34`" work unit with
a **decisive null**, via grep/source-read only (no build, no soak — exactly
as NEXT.md's own step 1 specified). Read PORTING-STATE.md's Session 111
entry before doing anything else; this file only has the actionable
summary.

## Why this is the next work unit

s111's grep was exhaustive: the entire voice array (`G_BASE-0x6908 +
voiceIdx*0x88`) is addressed from exactly one file (`funcs_24.c`, 21
load sites of the base pointer, all mapped to their 14 enclosing
functions), and within that file exactly one write to offset `0x34`
exists anywhere — the already-cleared `musyxInitVoiceFromSample`
(s105/s106). No other function, guarded or not, touches offset 0x34 at
all except as a read. **The corruption does not enter via any
`MEM_W(...,0x34)` store in guest C.** That closes the "static guest-C
write" branch of the M3 blocker question for good — do not re-grep this,
do not re-instrument any of the 14 cleared functions.

The one candidate NEXT.md itself anticipated for exactly this outcome:
an LLE RSP-side write via the MusyX audio microcode (`factor5_ucode`),
which has its own independent RDRAM write path this session's grep
cannot see by construction (it's not in `RecompiledFuncs/*.c` at all).
This gained real, independent support from s110 (a *different* session,
*before* this null was known): 385 lines of `Unhandled jump target 0x1883
in microcode factor5_ucode` fired for the first time ever in that soak's
log — every prior soak's version of this diagnostic read 0. M5's own
notes describe the recompiled MusyX ucode as "recompiles but is a
never-called artifact" — s110's evidence contradicts that assumption.

## What's confirmed (do not re-derive)

- `voice+0x34` has exactly one guest-C writer (`musyxInitVoiceFromSample`,
  `funcs_24.c:5881`), already cleared (s105/s106, clean verbatim copy,
  0/0 with positive control).
- No other function among the 14 that touch the voice array (via the
  `G_BASE-0x6908` global slot, `funcs_24.c` only) writes offset 0x34 —
  most never reference it at all; `musyxKeyOnVoice` reads it 3x but that's
  a different, already-cleared global per s105; `musyxRenderVoiceSamples`
  reads it once (the exact corrupted read feeding `fillSampleStreamRange`,
  s103/s104) but never writes it.
- `fillSampleStreamRange`'s own arguments are corrupted at function entry
  (s104) — the bug is upstream of every guest-C function characterized so
  far, all the way back to the voice+0x34 field itself, which nothing in
  guest C ever writes with a bad value.
- The `tickAudioChannel`/`musyx-gate1` investigative thread is retired
  (s110, 5 null sessions) — do not resume it.
- The hangar-tick-family guard program (5 classes: 16th/12th/11th/14th/
  17th) is closed pending an eventual free positive control — do not
  re-soak it in isolation (s101/s110 both reached the DMA window clean).
- `fixup_game_funcs.py` is still not idempotent — full ELF regen before
  every fixup run, run it exactly once per regen.

## The work unit

1. **Read, don't instrument yet.** Find where `Unhandled jump target
   0x1883 in microcode factor5_ucode` is emitted — likely
   `build/factor5_ucode/factor5_ucode_recompiled.c` (s110 cited line 230
   for the message) or wherever the RSP dispatch loop for this ucode
   lives. Identify: what jump table / dispatch mechanism is `0x1883`
   supposed to select, and what does "unhandled" mean here — does
   execution fall through to garbage, skip the instruction, or abort?
2. **Read `docs/factor5-ucode-dispatch.md`** (already exists in this repo)
   for the documented dispatch mechanism before guessing at the code.
   Check `tools/fixup_factor5_ucode.py` and `tools/decode_factor5_table.py`
   / `tools/disasm_factor5_full.py` for any existing tooling that already
   decodes this table — don't re-derive decode logic that already exists.
3. **Determine whether this ucode path can write to the voice array's
   RDRAM address range at all.** The RSP ucode operates on `dmem[]` and
   RDRAM via its own `MEM_W`-equivalent macros (see
   `include/rsp_dpc_macros.h`) — trace whether a MusyX audio RSP task's
   output writes into the same RDRAM region as the guest-C voice array
   (`G_BASE-0x6908`-relative), or into a completely different region
   (e.g. only ucode-private DMEM/output buffers that never reach RDRAM).
   If the address ranges provably never overlap, that's a real result
   that refutes hypothesis (a) — write it down and reopen hypothesis (b)
   (a runtime-computed store offset in guest C that a literal grep can't
   see) instead of assuming ucode involvement.
4. **Only if the source read shows a plausible RDRAM write path**, design
   one narrowly-targeted instrument (e.g. log every RSP-side RDRAM store
   this ucode task performs, gated to fire only during the ~140s DMA
   window) and soak once. Name the discriminating outcome before running:
   does a logged RSP write's target address/timing match the known
   `devAddr=0x6C676672 dramAddr=0x80195190` corruption window?

## Do not

- Do not re-grep or re-instrument any of the 14 functions in `funcs_24.c`
  characterized this session — that question is closed.
- Do not resume the `tickAudioChannel`/`musyx-gate1` chain (retired s110).
- Do not re-soak the five hangar-tick-family guarded classes in isolation.
- Do not design an RSP-ucode instrument before reading
  `docs/factor5-ucode-dispatch.md` and the existing decode tooling — this
  is new investigative surface for the M3 thread, don't guess at
  mechanisms that may already be documented.
- Do not run `fixup_game_funcs.py` more than once per ELF regen.
- Do not cite `ra=0x00000000`, or re-open "random/race/stomp" framings for
  the `devAddr` corruption (refuted s92, 10+ independent lines of evidence
  against, including 2 sessions reaching the window through entirely
  different guard states and recurring byte-identical).

## Housekeeping flagged, not this session's job either

`docs/CURRENT-TRUTH.md` is ~107 KB, still roughly 3x the ~35KB target in
CLAUDE.md/ITERATION.md. Flagged for several sessions running without
action — worth a dedicated compression work unit (migrate durable
mechanism/architecture material to PROJECT-OVERVIEW.md, prune superseded
detail, especially the now-closed hangar-tick-family guard narration)
paired with a real experiment per ITERATION.md (compressing docs alone
does not count as an ADVANCED work unit).
