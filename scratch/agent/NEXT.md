# NEXT work unit — M3: find a computed-offset write to voice+0x34 in guest C (s113)

s112 retired the "RSP MusyX ucode writes voice+0x34" hypothesis with a
**decisive source-level refutation**, no build, no soak. Read
PORTING-STATE.md's Session 112 entry before doing anything else; this file
only has the actionable summary.

## Why this is the next work unit

s111 enumerated every **literal-offset** guest-C write to `voice+0x34`
(`MEM_W(0X34, ...)` textual grep) and found exactly one, already cleared
(`musyxInitVoiceFromSample`). It then guessed the corruption must come
from the RSP MusyX audio ucode instead. s112 read the actual call graph
and refuted that: `factor5_ucode` (the function whose `0x1883` diagnostic
s110 saw fire) is the **graphics** ucode, called every task
(`src/main/main.cpp:407`) — it has nothing to do with audio. The real
MusyX ucode, `factor5_ucode_b`, is **provably dead code**: `main.cpp:76`
only declares it `extern`, and a `grep -rn "factor5_ucode_b(" src/` finds
zero call sites anywhere. There is no RSP-side write path into MusyX
voice state at all, because the audio ucode never runs.

That leaves exactly the branch NEXT.md flagged at s111 as hypothesis (b):
**a runtime-computed (non-literal) offset store** into the voice struct
that a grep for the literal text `0x34` cannot find by construction — e.g.
a byte/word copy loop indexed by a variable field offset, a `memcpy`-
shaped helper, or a struct-copy where the destination pointer is offset by
a variable at runtime (`MEM_W(rdram, someVariableOffset, ...)` where
`someVariableOffset` is never the literal `0x34` in source text but
evaluates to it at runtime).

## What's confirmed (do not re-derive)

- `voice+0x34` has exactly one **literal-offset** guest-C writer
  (`musyxInitVoiceFromSample`, `funcs_24.c:5881`), already cleared
  (s105/s106, clean verbatim copy, 0/0 with positive control).
- No other function among the 14 that touch the voice array (via the
  `G_BASE-0x6908` global slot, `funcs_24.c` only) has a **literal**
  `0x34` write. `musyxKeyOnVoice` reads it 3x (different, already-cleared
  global, s105); `musyxRenderVoiceSamples` reads it once (the exact
  corrupted read feeding `fillSampleStreamRange`, s103/s104) but never
  writes it.
- **The RSP-ucode branch is closed, not just parked** (s112): `factor5_ucode`
  = graphics ucode (runs constantly, unrelated dispatch table per
  `docs/factor5-ucode-dispatch.md`); `factor5_ucode_b` = the actual MusyX
  ucode, confirmed **never called anywhere in `src/`**. Do not revisit RSP
  ucode as a write-path candidate without new evidence that changes this
  call-graph fact.
- The `0x1883` unhandled-jump-target diagnostic is an artifact of the
  graphics ucode's own dispatch (target falls mid-instruction between
  `L_1828`/`L_18F0`, non-4-aligned) — plausibly itself a downstream
  symptom of stray corrupted register state, not a new mechanism. Not
  investigated further; low priority unless it recurs with a discriminable
  pattern.
- `fillSampleStreamRange`'s own arguments are corrupted at function entry
  (s104) — the bug is upstream of every guest-C function characterized so
  far, all the way back to the voice+0x34 field itself.
- The `tickAudioChannel`/`musyx-gate1` investigative thread is retired
  (s110, 5 null sessions) — do not resume it.
- The hangar-tick-family guard program (5 classes: 16th/12th/11th/14th/
  17th) is closed pending an eventual free positive control — do not
  re-soak it in isolation (s101/s110 both reached the DMA window clean).
- `fixup_game_funcs.py` is still not idempotent — full ELF regen before
  every fixup run, run it exactly once per regen.

## The work unit

1. **Read, don't instrument yet.** In `N64Recomp/RecompiledFuncs/funcs_24.c`
   (and any of the other 13 functions touching the voice array), search for
   writes that reference the voice-slot base pointer with a **non-literal**
   offset — i.e. any `MEM_W(rdram, <expr>, ...)` or equivalent store where
   `<expr>` is a computed value (register arithmetic, loop index, a field
   read from another struct) rather than a literal hex immediate. Look
   specifically for copy-loop shapes (`for`/`while` with an incrementing
   store address) that could land on offset `0x34` for some iteration
   without ever spelling `0x34` in source.
2. **Cross-check against the two already-known consumers.** Both
   `fillSampleStreamRange`'s corrupted arguments and
   `acquireSampleStreamBlock`'s cache-key argument (s103) trace back to
   this same field. If a computed-offset writer exists, its target
   expression should be traceable to the same voice-slot base pattern
   (`G_BASE-0x6908 + voiceIdx*0x88`) or to whatever intermediate struct
   sits between the voice array and these two functions' arguments.
3. **If no computed-offset writer is found in guest C either**, the
   remaining candidates are: (c) the corruption is written by MusyX's own
   asset data at load time (a bad ROM/asset table entry, not a runtime
   store bug), or (d) it enters through a completely different subsystem
   that happens to alias the same RDRAM address (an unrelated writer with
   a wrong computed address, not voice-array-aware at all — revisit the
   s94-s95 "unlocated indirect caller of `submitDmaRequestBatch`" angle,
   but this time hunting for an indirect *writer into the voice array*,
   not the DMA-batch populator, which s102 already cleared as innocent).
   Name which of (c)/(d) is more supported by the existing evidence
   (structured tag-like byte patterns in the corrupted values, per s102)
   before choosing a next probe.
4. **Only if a plausible computed-offset writer is found**, design one
   narrowly-targeted instrument and soak once. Name the discriminating
   outcome before running: does the writer's logged target offset/value
   match the known `devAddr=0x6C676672 dramAddr=0x80195190` corruption
   signature?

## Do not

- Do not re-grep for literal `0x34` writes — that question is closed
  (s111).
- Do not re-investigate the RSP ucode as a write path — closed (s112):
  `factor5_ucode_b` (real MusyX ucode) never runs; `factor5_ucode` (what
  s110's diagnostic actually fired in) is graphics-only.
- Do not resume the `tickAudioChannel`/`musyx-gate1` chain (retired s110).
- Do not re-soak the five hangar-tick-family guarded classes in isolation.
- Do not run `fixup_game_funcs.py` more than once per ELF regen.
- Do not cite `ra=0x00000000`, or re-open "random/race/stomp" framings for
  the `devAddr` corruption (refuted s92, 10+ independent lines of evidence
  against).

## Housekeeping flagged, not this session's job either

`docs/CURRENT-TRUTH.md` is well over the ~35KB target in CLAUDE.md/
ITERATION.md. Flagged for many sessions running without action — worth a
dedicated compression work unit (migrate durable mechanism/architecture
material to PROJECT-OVERVIEW.md, prune superseded detail, especially the
now-closed hangar-tick-family guard narration and the now-closed RSP-ucode
detour) paired with a real experiment per ITERATION.md (compressing docs
alone does not count as an ADVANCED work unit).
