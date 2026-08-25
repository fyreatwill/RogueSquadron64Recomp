# NEXT work unit (s2336) — M5 descriptor init callsite provenance

HYPOTHESIS-ID: m5-descriptor-callsite-provenance

## Work unit

Run one ground-truth-first, no-behavior-change callsite census for the actual
`musyxInitVoiceFromSample` function entry at `0x80092128` and its descriptor
store at `0x80092230`. Keep the qualified Factor 5 image arm, silent control,
eleven-Start route, `ROGUESQ_DRAIN_INLOOP_TICK=1`, host-positive filter/voice
control, and all task/DMA/guest-receive/PCM controls. Do not repeat the
descriptor/filter null census or add writeback, remapping, slot values, guards,
defaults, or a consumer.

## Competing hypotheses and discriminating measurement

- H-CoverageInvalid: the retail whole-RDRAM/target/status/title/hangar controls,
  named retail entry/store/key-on/filter PCs, either port arm, or the task,
  DMA, guest-receive, PCM, and host-positive controls is absent.
- H-PortInitNeverCalled: retail enters `0x80092128` and reaches the
  `0x80092230` store with positive previous-PC callers, while both port arms
  retain target render/key-on rows but have zero target init-entry and init-store
  rows.
- H-PortInitEntryEarlyReturn: a target port init-entry row is live, but no
  target store follows it; the entry row's base/descriptor fields and any
  guard/return row identify the first divergence.
- H-PortInitPriorOrdinal: target init entry/store rows exist, but only on a
  prior audio ordinal or phase; same-ordinal versus prior joins to render/key-on
  rows distinguish ownership rather than treating a count as a callsite.

The discriminator is one table keyed by `(arm, phase, width, origin, ordinal,
row, event, caller/previous-PC)` containing retail execution counts and
previous-PC histograms for `0x80092128`, `0x80092230`, `0x8009231C`,
`0x80090B68`, `0x80090C28`, `0x8009D740`, and `0x8009D7D0`; port
`[init-voice-sample]` entry payload, init-writer `m5-audio-event`, render,
key-on, slot/status/lifecycle, task/image completion, PCM, and filter rows.
Select H-PortInitNeverCalled only with qualified controls and zero target entry
and store rows in both arms. Select H-PortInitEntryEarlyReturn only with a
positive target entry and zero later store. Select H-PortInitPriorOrdinal only
with positive rows and no same-ordinal join. Any missing control selects
H-CoverageInvalid.

## Exact commands

Create `scratch/agent/run_s2336_m5_descriptor_callsite_provenance.sh`. Its
retail preflight must run first with whole-RDRAM, physical
`0x00165000:0x0016B000`, task/output/gate/wait/status watches, title/hangar
origins, the named writer controls, and `--watch-pc` for the entry/store,
trigger, key-on, decode, filter, and service PCs above. Require positive
whole-RDRAM/target/status/title/hangar and positive retail entry/store/key-on/
filter controls; keep `0x0001498A` and route-specific `0x8009C4E8` explicitly
zero-only.

The port arms must retain `[audtask-abi]`, `[audtask-dma-row]`,
`[audtask-dma-range]`, image-stage/image-join, guest-receive, PCM
source/consumer, `[m5-audio-event]`, `[init-voice-sample]`, `[m5-keyon-*]`,
`site=render-stage`, `site=render-end`, and both filter audit controls and real
rows. Run both arms from one build with the validated sequential input recipe.

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh -n scratch/agent/run_s2336_m5_descriptor_callsite_provenance.sh
    zsh scratch/agent/run_s2336_m5_descriptor_callsite_provenance.sh s2336_m5_descriptor_callsite_provenance
