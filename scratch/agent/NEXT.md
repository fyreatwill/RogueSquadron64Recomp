# NEXT work unit — audit unmasked release/fade voice-table index

HYPOTHESIS-ID: m3-next-audio-idiom-audit

Next work unit: perform one complete static census of every direct caller of
`musyxStartVoiceRelease` and `beginVoiceFadeRelease`, and of every generated
load of synth-voice `+0x67` that is passed as their voice-table index.
Session 3599 showed release uses unmasked `a0` with no KSEG0 guard and fade
uses unmasked `a0` with a KSEG0 guard; `tickAudioChannel` loads
`MEM_BU(s0, 0x67)` before the release JAL. On the big-endian packed handle
at record `+0x64`, byte `+0x67` is the slot. Enumerate every writer of that
byte/word, every caller argument, reset/free ordering versus the `-1`
sentinel, and the consumer bound in the `0x88` voice table.
Do not repeat the closed `+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`,
`+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT publication, mix-table,
pan-input, or hangar-Y audits. Do not change runtime code unless a concrete
invalid writer/value is identified; any mitigation needs an ORIGIN line
naming the writer and assessing legitimacy.

Competing hypotheses and discriminator:

- H-NextClassGap: a live release/fade call can pass `0xFF` from the `-1`
  packed-handle low byte, or another out-of-range index, into the `0x88`
  voice table.
- H-NextClassComplete: every caller argument is a slot below the live
  count or is structurally gated before the JAL, and only runtime
  allocator legitimacy remains.
- H-NextClassUnevaluable: aliases or mixed layouts prevent a complete
  object-level classification of the index source.

Discriminator: the single complete caller/`+0x67` census across
`funcs_22.c` through `funcs_24.c`. Select Gap only with a concrete
out-of-range or sentinel-as-index edge; select Complete only when all
edges are covered; otherwise select Unevaluable.

Exact checks before any build:

    grep -n 'musyxStartVoiceRelease\|beginVoiceFadeRelease' ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c ../N64Recomp/RecompiledFuncs/funcs_24.c
    grep -n 'MEM_BU(.*0[Xx]67)' ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c ../N64Recomp/RecompiledFuncs/funcs_24.c

No build or runtime run is expected for this static audit. If the census is
complete, write a new `docs/M3-S<session>-...md` evidence note and update
CURRENT-TRUTH, the ledger, status, outcome, and commit.
