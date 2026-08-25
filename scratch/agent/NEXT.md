# NEXT work unit (s2334) — M5 descriptor-to-filter voice boundary

HYPOTHESIS-ID: m5-descriptor-filter-boundary

## Work unit

Run one ground-truth-first, no-behavior-change descriptor-entry/writer/callsite
census. Keep the qualified Factor 5 image arm, silent control, eleven-Start
route, `ROGUESQ_DRAIN_INLOOP_TICK=1`, and the host-positive filter/voice span
control. Do not repeat the upstream PC census, output metadata join, or add
writeback, address remapping, slot values, guards, defaults, or a consumer.

The s2333 result leaves the first unresolved edge at render/key-on to
descriptor entry/writer to filter call: target render-stage/key-on rows are
positive, while descriptor and real filter rows are zero. The requested retail
`0x8009C4E8` updater PC remains an explicit zero in the retail table.

## Competing hypotheses and discriminating measurement

- H-DescriptorWriterAbsent: the port reaches target render/key-on work but never
  enters or stores a voice descriptor. Retail descriptor/key-on PCs are
  positive; both port arms have target render/key-on rows but zero
  `[init-desc]` rows and zero descriptor-bearing lifecycle events.
- H-DescriptorPriorOrdinal: the port emits descriptor rows, but they belong to
  the prior audio ordinal. Target descriptor events have no same-ordinal join,
  the prior-ordinal signature is present, and real filter rows remain zero.
- H-FilterCallGated: target descriptor rows are same-ordinal and target key-on
  rows are positive, but real `[filter-voice-audit]` rows remain zero while
  retail filter caller/callee PCs are positive and no post-descriptor filter
  event occurs.
- H-CoverageInvalid: retail whole-RDRAM, physical target-window, title/hangar,
  task/gate/status, named retail descriptor/filter PCs, either port arm, task /
  DMA / guest-receive / PCM controls, or the host-positive audit is absent.

The discriminator is one table keyed by `(arm, phase, width, origin, audio
ordinal, row, event)` containing retail execution counts for
`musyxRenderVoiceSamples=0x8008FFAC`, `musyxInitVoiceFromSample=0x80092230`,
`musyxTriggerVoiceAttack=0x8009231C`, key-on sites
`0x80090B68,0x80090C28`, `updateVoiceChannelParamsLarge=0x8009D740`, and
`filterVoiceSampleBlock=0x8009D7D0`; port render-stage/render-end, all
`m5-keyon-*`, descriptor, host-positive, real-filter, slot/status/lifecycle,
task/image completion, and PCM source/consumer rows; plus signed deltas and
same-ordinal versus prior classification. Select H-DescriptorWriterAbsent
only with qualified controls and zero descriptor rows in both arms. Select
H-DescriptorPriorOrdinal only with positive descriptor rows, no same-ordinal
descriptor join, the prior signature, and zero real filter rows. Select
H-FilterCallGated only with positive same-ordinal descriptor/key-on rows and
zero real filter rows. Any missing positive control selects H-CoverageInvalid.

## Exact commands

Create `scratch/agent/run_s2335_m5_descriptor_filter_boundary.sh`. Its retail
oracle preflight must run first with whole-RDRAM, physical
`0x00165000:0x0016B000`, task/output/gate/wait/status watches, title/hangar
origins, named task/output writer controls, and `--watch-pc` for every retail
PC in the table above. Require positive whole-RDRAM/target/status/title/hangar,
positive retail render/filter and at least one descriptor/key-on control, and
keep the known-zero `0x0001498A` watch explicitly zero. Record
`0x8009C4E8` as a requested zero-only PC; do not fail the preflight for that
route-specific zero.

The port arms must retain `[audtask-abi]`, `[audtask-dma-row]`,
`[audtask-dma-range]`, image-stage/image-join, guest-receive, PCM
source/consumer, `[m5-audio-event]`, slot/status fields, `[m5-keyon-*]`,
`site=render-stage`, `site=render-end`, `[init-desc]`, and both
`[filter-voice-audit-control]` and real `[filter-voice-audit]` rows. Run both
arms from one build with the validated sequential input recipe.

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2335_m5_descriptor_filter_boundary.sh
    zsh scratch/agent/run_s2335_m5_descriptor_filter_boundary.sh s2335_m5_descriptor_filter_boundary
