# NEXT work unit (s1970) — filterVoiceSampleBlock whole-idiom audit

HYPOTHESIS-ID: hangar-filter-voice-sample-block-idiom-audit

## What s1969 settled

The DPC writer control and RT64 consumer census both fired in the live hangar
window. Five hundred consumer rows reached `drawTris`; 153 rows overlapped the
captured beam-cone box, all with coherent `blend=0x0055`, coverage, and z-mode
fields. H1 is refuted as a single-source consumer-state explanation. H3 is
unavailable: the retail oracle has no screenshot or equivalent LLE `L_17F0`
path. The known `filterVoiceSampleBlock+220` / `last-guest-pc=0x8000834c`
SIGBUS remains the next actionable systematic M3 audit.

## Single next work unit

Complete one whole-idiom audit of `filterVoiceSampleBlock` at guest VRAM
`0x8009D7D0` (syms entry size `0xEC`) and all three generated callers. Enumerate
every caller argument setup, selector/table load, source-buffer base, and
derived output address/length; classify each as fixed, caller-owned, table-
indexed, or unbounded. Build one regeneration-safe batch probe covering the
callee entry and every caller edge, with one row schema containing caller PC,
voice/index bytes, source/output bases, requested span, and the range class.
Do not add a guard or skip. The writer/legitimacy question is open: name the
writer for every value before proposing any behavior change.

## Competing hypotheses and discriminating measurement

- **H-filter-local-range:** the callee's fixed filter arithmetic reaches outside
  its caller-owned source/output span; selecting evidence is a callee row whose
  effective range is invalid while the caller supplied a valid base.
- **H-caller-contract:** one caller supplies a malformed voice record, selector,
  base, or count; selecting evidence is a caller-specific invalid input before
  the callee's fixed walk, with the other callers staying in-range.
- **H-audio-host-or-stale-pc:** every guest range is in-range and the crash is
  host decode/audio state or stale breadcrumb attribution; selecting evidence is
  all rows passing the guest range contract plus a crash with no invalid guest
  span.

**Discriminator:** one static enumeration plus one build/run carrying all three
caller probes and the callee range calculation. A caller-specific bad input
selects H-caller-contract; a callee-only bad effective span selects
H-filter-local-range; all in-range rows leave only H-audio-host-or-stale-pc.
The hangar-entry/control row must fire in the same run; a crash before that
control is unevaluable and must be enqueued, not interpreted.

## Ground truth and exact commands

Before building, re-read `tools/oracle/README.md` and use the retail positive
controls only to verify the driven hangar phase; do not treat a null audio
watch as evidence unless the whole-RDRAM control fires. Then enumerate and
classify the complete generated idiom with:

```sh
rg -n "filterVoiceSampleBlock|0x8009D7D0|0x8000834C|drainMeshReleaseQueue" syms docs tools
rg -n "voice|sample|selector|0x17C|0x88" RecompiledFuncs tools/fixup_game_funcs.py tools/fixup_factor5_ucode.py
```

Batch the probe through the regeneration path (`make_elf.py` -> N64Recomp ->
`fixup_game_funcs.py` -> CMake), then build:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run from `build/` with the hangar recipe and a non-dot capture path; arm the
existing passive breadcrumbs and SIGKILL watchdog through `tools/probe.sh`.
The run must phase-gate on `width=512` and origin `0x006AB400`/`0x006AB800`,
not on elapsed time. Do not repeat the consumer census or the `0xD60` mode
scan; this unit is the complete `filterVoiceSampleBlock` idiom class.
