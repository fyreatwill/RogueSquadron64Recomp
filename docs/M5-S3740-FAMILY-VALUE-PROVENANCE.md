# M5 s3740 — family value/call-edge provenance

The corrected batched capture used the independent retail oracle, its
whole-RDRAM positive control, title and hangar phase gates, real-audio and
silent port arms, and the existing source-DMA watches. The first build's
shared phase budget was consumed by `rs_strncpy`; it was discarded as
unevaluable. The fixed build used an independent 128-row budget for each
family/edge pair.

The fixed capture passed the oracle control (`10000` callbacks), title and
hangar snapshots, and completed without a port crash. Both port arms fired the
family-provenance control and recorded 514 rows:

| family | phase | call rows | entry rows | argument result |
|---|---:|---:|---:|---|
| `rs_strncpy` (`0x80007640`) | title 4 | 128 | 128 | all `a0`, `a1`, `a2` nonzero; setup buffers outside the qualified source span |
| `rs_strncpy` (`0x80007640`) | hangar 5 | 128 | 128 | same setup-buffer arguments in both arms; no target-span destination |
| `initTextureLUTAndAllocBuffers` (`0x8001E230`) | title 4 | 1 | 1 | exact call/entry match: `a0=a1=0x200`, `a2=0x400` |

No texture-LUT family row occurred in hangar before the scoped budget closed.
The real arm independently produced 512 qualified source writer rows, all
zero (`FNV=0x762B22A5`, `payload_nz=0`); the silent arm produced no qualified
source-DMA rows. Thus the observed family call edges do not lose values between
caller and entry, but they are shared setup activity, not the missing
qualified-route producer. This refutes `H-FamilyCallEdgeDropsValue` and the
candidate-family form of `H-FamilyValueSetupAbsent`; the first missing edge is
downstream or parallel to these setup families.

This is two-line evidence: the same-build real/silent comparison shows the
family activity is audio-independent setup, while the independent oracle and
qualified source writer show the retail/port payload boundary remains real
versus port. No behavior or writer was changed.
