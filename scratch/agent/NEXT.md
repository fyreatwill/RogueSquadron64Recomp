# Next work unit (s4331): co-located D740 sequence witness

HYPOTHESIS-ID: m5-step9-d740-witness-contradiction

The s4330 static census found one generated `updateVoiceChannelParamsLarge`
wrapper at `0x8009C5BC`, one D740 edge inside it, no other generated reference
to the wrapper/body, and section-3 text ownership in `recomp_overlays.inl`.
That rejects a static alternate-transfer explanation for s4329's missing D740
caller rows. The next run must distinguish helper invocation/state loss from a
phase budget artifact without changing audio behavior.

Competing hypotheses:

- H-helper-not-invoked: the generated entry marker and direct marker execute, but
  the caller helper call is skipped or optimized/redirected in the host path.
- H-state-cleared: the caller helper runs and stores the tuple, but its state is
  cleared or replaced before the direct probe joins it.
- H-budget/gate: the helper runs, but its row emission is suppressed by its
  static bucket budget or phase gate while the direct probe remains visible.

Discriminator: add one bounded co-located sequence witness in the existing
`updateVoiceChannelParamsLarge` entry and D740 path. It must count/log, under
the existing VI-512 gate, (1) immediately after the wrapper-entry helper,
(2) immediately after `rs64_filter_voice_caller_probe`, and (3) immediately
before/after `rs64_filter_voice_direct_probe`, using one sequence id and no
new payload fields. Entry+post-helper absent selects H-helper-not-invoked;
entry+post-helper present but direct join absent selects H-state-cleared;
all three present with caller rows still absent selects H-budget/gate.

Build/run all arms in one iteration using the existing seeded matrix recipe;
do not run an A/B across separate animating scenes. Positive controls must be
the oracle whole-RDRAM/title/hangar controls and both existing filter controls.
Use the project's prescribed build and matrix commands from the latest M5
recipe, and do not alter decoder, RSP, AI, or game-path behavior.

Static census commands already run:

`rg -n --glob 'funcs_*.c' --glob '!*.s*' --glob '!scratch*' "8009D740|8009D7D0|updateVoiceChannelParamsLarge|filterVoiceSampleBlock" ../N64Recomp/RecompiledFuncs`

`sed -n '1768,1810p;4768,4805p' ../N64Recomp/RecompiledFuncs/funcs_27.c`
