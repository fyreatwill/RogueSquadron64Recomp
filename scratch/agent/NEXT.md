# Next work unit: M5 port entry/setup census for retail earlier-writer families

HYPOTHESIS-ID: m5-port-earlier-writer-entry

Run one batched, phase-gated port capture to determine where the retail
earlier-writer families disappear. Cover guest entry/setup/call edges for
`0x80007670` and `0x8001E2C0`, retaining the exact source-span stores and the
real/silent controls. Do not change port behavior or suppress the legitimate
`0x800078EC` zero fill.

Competing hypotheses:

- `H-PortFamilyNeverEntered`: neither earlier family is reached on the
  qualified port route; the boundary is before family entry.
- `H-PortFamilyEnteredWrongArgs`: a family is entered, but its destination or
  value arguments do not target `0x1797B0..0x179A48`.
- `H-PortFamilyWritesThenClear`: an earlier port family writes a nonzero span,
  followed by the legitimate zero fill at `0x800078EC`.

Discriminator: phase-scoped entry counts plus writer/setup arguments and exact
span scalar-store rows in the same run. No entry selects `H-PortFamilyNeverEntered`;
entry without a target-span argument selects `H-PortFamilyEnteredWrongArgs`;
nonzero target-span stores followed by `0x800078EC` select
`H-PortFamilyWritesThenClear`. Missing whole-RDRAM control or either target
phase is unevaluable.

Use the rebuilt binary and adapt
`scratch/agent/run_s3737_m5_retail_writer_join.sh`. Keep the oracle
`--watch-write 0x0:0x800000`, both source watches, both phase snapshots, and
real/silent `ROGUESQ_AUDIO_UCODE=1/0` arms. Enable the existing writer setup,
input-writer, source-writer, source-transition, and phase logs in one capture.
