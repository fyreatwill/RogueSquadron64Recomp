# Next work unit: qualify the earlier producer context before 0x8008F900

HYPOTHESIS-ID: m5-step4-object-field-producer

Build one paired oracle/port measurement around the observed predecessor
`0x8008F8FC`, using the existing `0x8008F900` witness and all current positive
controls. Add a regeneration-safe predecessor snapshot only if the existing
instrument does not already expose the required fields; otherwise reuse the
current witness and change no runtime behavior. Phase-gate both sides on the
qualified origins (`0x00790800`/`0x006AB800` for retail and
`0x00790400`/`0x006AB400` for port).

Competing hypotheses:

- H-earlier-producer-context-mismatch: the predecessor context already differs,
  moving the open boundary before `0x8008F900`.
- H-entry-body-mismatch: predecessor context matches, so the divergence begins
  in the `0x8008F900` body or its immediate field loads.
- H-measurement-alias: the apparent source/branch difference is caused by
  mismatched field semantics or phase joins rather than guest state.

The discriminator is a qualified two-sided predecessor table: positive
control, both retail phases, both port phases, and nonzero predecessor rows
joined to the `0x8008F900` rows. Matching predecessor fields select the entry
body; a reproducible field divergence selects the earlier boundary; missing
controls or joins makes the run unevaluable and does not prove absence. No
audio, gate, writer, payload, or mitigation behavior change is authorized.

Use [F5-UCODE-REFERENCE.md](../../docs/F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. MusyX/MORT audio
remains partially stubbed; do not send MusyX data to stock `aspMain`.
