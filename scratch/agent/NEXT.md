# NEXT work unit (s2134) — retail voice-codec/MORT boundary census

HYPOTHESIS-ID: m5-mort-boundary

## Work unit

Run one retail-oracle ground-truth capture before adding any port-side
instrument or creating a MORT artifact. Use the whole-RDRAM positive control,
the qualified title/hangar VI gates, and execution watches at the named
voice-sample/decode/filter functions, `musyxSynthFrame`, and
`osAiSetNextBuffer`. This is one oracle experiment; do not build the port or
change the audio arm, task ABI, output routing, waits, guards, or defaults.

## Competing hypotheses and discriminator

- `H-RetailMORTDecoderLive`: after the hangar gate, one or more of
  `decodeAndFillVoiceBlock`, `filterVoiceSampleBlock`, `applyVoiceDelayFilter`,
  `runVoiceLatticeFilter`, `renderVoiceAudioBlock`, `audioMixStereoBlock8`, or
  `audioCompandS16` execute, and the same run also observes
  `musyxSynthFrame` plus `osAiSetNextBuffer`. This selects the retail
  voice-codec/MORT boundary as live and identifies the first port artifact
  boundary to reproduce.
- `H-RetailVoicePipelineNoDecoder`: the independent whole-RDRAM control and
  title/hangar gates pass, `musyxSynthFrame` and `osAiSetNextBuffer` execute,
  but every named decoder/filter watch is zero after the hangar gate. This
  rules out the current MORT-codec execution theory at the covered retail
  route; it does not prove that the port image is correct.
- `H-CoverageFailure`: the whole-RDRAM watch does not reach its threshold, or
  the title/hangar VI gates are absent. This selects no decoder hypothesis;
  all zero execution-watch results are unevaluable.

The discriminating table is keyed by phase/origin and execution-watch PC:
whole-RDRAM positive-control callbacks; title `1024 @ 0x00790400`; hangar
`512 @ 0x006AB400`; counts for the seven named decode/filter functions;
`musyxSynthFrame` at `0x8009123C`; and `osAiSetNextBuffer` at `0x80029E80`.
`H-RetailMORTDecoderLive` requires the decoder/filter hits and the two known
pipeline hits in the same hangar-covered run. A positive control or phase
gate missing selects `H-CoverageFailure`, never a null decoder result.

## Exact commands

    cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp
    test -x tools/oracle/build/rs64_oracle
    tools/oracle/build/rs64_oracle \
      --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
      --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
      --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
      --secs 70 --hit-cap 64 \
      --watch-write 0x0:0x800000 \
      --watch-pc 0x8009C904,0x8009D7D0,0x8009D8C4,0x8009D980,0x8009DB44,0x8009DC98,0x8009DD7C,0x8009123C,0x80029E80 \
      --first-watch 0 --vi-trace \
      --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
      > scratch/agent/oracle_s2134_mort_boundary.log 2>&1

Inspect only bounded evidence:

    grep -a -E '\[oracle\] positive|\[vi\]|\[hit\]|exec-prev|done:' scratch/agent/oracle_s2134_mort_boundary.log | tail -120

The work unit ends when the table selects one hypothesis. If the oracle
binary/core/ROM setup fails or a phase gate is absent, record
`H-CoverageFailure`; do not substitute a port run.
