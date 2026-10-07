# M5 session 4155 — pre-clear provenance instrument gap

The rebuilt real-audio/LLE port and independent retail oracle were run with
the pre-clear provenance recipe. The oracle passed the whole-RDRAM positive
control and reached title VI `0x00790400/1024` and hangar VI
`0x006AB400/512`. Its watched span `0x178C80..0x178F18` had 12 nonzero bytes
in the hangar phase snapshot; the phase writer histogram was populated.

The port reached both target phases and emitted 512 sampled
`0x800078EC` clear-body rows: every sampled value was `0x00000000`. The
intended port pre-clear CPU-writer positive control emitted zero
`[field348-writer]`, `[field348-candidate]`, and `[m5-source-transition]`
rows. The instrument therefore did not observe the competing earlier-writer
arm.

`H-preclear-instrument-gap` is selected. The run does not distinguish
`H-port-preclear-absent` from `H-port-preclear-overwritten`; the zero clear
body is not evidence that no earlier nonzero writer ran. No guest, audio,
wait, cap, predicate, slot, or writeback behavior changed.

ORIGIN: the legitimate retail source-span writers and the port's
`0x800078EC` clear plus CPU-writer probes. The next work unit is to repair the
port positive control and repeat the same paired census.

Evidence: `scratch/agent/s4154_m5_preclear_provenance/` (latest run files).
