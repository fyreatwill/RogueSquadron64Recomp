# NEXT work unit (s2333) — M5 upstream voice-path boundary

HYPOTHESIS-ID: m5-destination-slot-keyon-contract

## Work unit

Run one ground-truth-first, no-behavior-change upstream voice-path census.
Keep the qualified Factor 5 image arm, silent control, eleven-Start route,
`ROGUESQ_DRAIN_INLOOP_TICK=1`, and the s2332 host-positive filter/voice span
control. Do not repeat the output-buffer/overlap join and do not add writeback,
address remapping, slot values, guards, defaults, or a consumer.

Join the retail upstream voice PCs and the port's existing phase-keyed render,
key-on, filter, slot/status, service, task ordinal, and PCM rows. The target is
to locate the first missing edge before the retail-live `filterVoiceSampleBlock`
callee, not to infer a null from the host-positive control alone.

## Competing hypotheses and discriminating measurement

- H-UpstreamVoiceAbsent: the port never enters the voice-render path for the
  target ordinal. Retail upstream and filter PCs are positive, while the port
  has no target-phase `render-stage`/voice-entry rows in either arm.
- H-FilterPathGated: the port reaches voice rendering/key-on setup but does not
  reach the filter path. Port target-phase render/key-on/descriptor rows are
  positive, real `[filter-voice-audit]` rows remain zero, and no same-ordinal
  lifecycle transition follows the image task.
- H-PriorOrdinalReuse: the port reaches the real filter path, but the slot and
  key-on rows attached to a target image ordinal are prior-route rows. Positive
  real filter rows plus no same-ordinal post-stage lifecycle and a retained
  prior signature select this; the host-positive control is not counted as a
  filter call.
- H-CoverageInvalid: the retail whole-RDRAM/target/status/writer or
  title/hangar controls, either port route, task/DMA/guest-receive/PCM control,
  or the host-positive filter control is absent.

The discriminator is one table keyed by `(arm, phase, width, origin, audio
ordinal, row)` with: retail execution counts for
`musyxRenderVoiceSamples=0x8008FFAC`, `updateVoiceChannelParams=0x8009C4E8`,
`decodeAndFillVoiceBlock=0x8009C904`, `filterVoiceSampleBlock=0x8009D7D0`,
and `serviceVoicePoolFrame=0x8009B5A8`; port render-stage/render-end,
key-on pointer/branch/tail, descriptor, host-positive control, real filter
row, slot/status/key-on event, task begin/end, image completion, and PCM
source/consumer rows; plus signed event deltas and same-ordinal versus prior
classification. Select H-UpstreamVoiceAbsent only with qualified controls and
zero target render-stage/voice-entry rows. Select H-FilterPathGated only with
positive target render/key-on rows and zero real filter rows. Select
H-PriorOrdinalReuse only with positive real filter rows, no same-ordinal
post-stage lifecycle, and the prior signature. Any missing positive control
selects H-CoverageInvalid.

## Exact commands

Create `scratch/agent/run_s2333_m5_voice_path_boundary.sh`. Its retail oracle
preflight must run first with whole-RDRAM, physical
`0x00165000:0x0016B000`, task/output/gate/wait/status watches, title/hangar
origins, named task/output writer PCs, and `--watch-pc` for
`0x8008FFAC,0x8009C4E8,0x8009C904,0x8009D7D0,0x8009B5A8`. Require positive
whole-RDRAM/target/status/title/hangar controls and positive retail upstream
render/filter execution before launching the port. Keep the known-zero
`0x0001498A` watch explicitly zero.

The port arms must retain `[audtask-abi]`, `[audtask-dma-row]`,
`[audtask-dma-range]`, image-stage/image-join, guest-receive, PCM
source/consumer, `[m5-audio-event]`, all slot/status/descriptor/key-on
fields, `[m5-keyon-*]`, `site=render-stage`, `site=render-end`, and both
`[filter-voice-audit-control]` and real `[filter-voice-audit]` rows. Run both
arms from one build with the validated sequential input recipe.

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2333_m5_voice_path_boundary.sh
    zsh scratch/agent/run_s2333_m5_voice_path_boundary.sh s2333_m5_voice_path_boundary
