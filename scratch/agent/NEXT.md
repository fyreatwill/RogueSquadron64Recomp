# Next work unit: repair the oracle phase gate for predecessor context

HYPOTHESIS-ID: m5-step4-object-field-producer

Use the s4178 build and port witness. Change only the oracle phase gates in
`scratch/agent/run_s4175_m5_object_entry.sh` from `0x00790400`/`0x006AB400`
to the observed retail origins `0x00790800`/`0x006AB800`, then rerun the
paired route with the existing port gates and positive controls.

Competing hypotheses:

- H-entry-context-match: qualified oracle rows let the port snapshot be
  compared with retail-like predecessor context, moving the mismatch
  downstream.
- H-earlier-producer-mismatch: qualified rows show divergence already at
  `0x8008F900`, keeping the source boundary at or before that PC.
- H-oracle-breakpoint-path: corrected origin gates still produce no
  `pc-field-row` for `0x8008F900`, so the oracle exact-PC capture path is the
  blocker rather than the game route.

The discriminator is qualified nonzero oracle `pc-field-row` output for
`0x8008F900` plus the same-run port join: a row enables the context
comparison; another absent row selects the oracle breakpoint-path hypothesis.
Missing positive controls or phases rejects the run. No audio, gate, writer,
payload, or mitigation behavior change is authorized.

No rebuild is needed for the recipe-only arm. Edit the two oracle-origin
arguments, run `zsh scratch/agent/run_s4175_m5_object_entry.sh`, and require
`pc-field-summary pc=0x8008f900 hits>0` before interpreting context. Keep all
existing positive controls and passive breadcrumbs.

Use [F5-UCODE-REFERENCE.md](../../docs/F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. MusyX/MORT audio
remains partially stubbed; do not send MusyX data to stock `aspMain`.

Every instrument needs independent ground truth, a same-run positive control,
a phase-scoped budget, and two evidence lines before its result becomes truth.
Phase-gate animated comparisons on VI transitions. A counter proving a branch
ran is not a positive control.
