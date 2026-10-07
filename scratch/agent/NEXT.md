# Next work unit: M5 Step 4 hangar writer qualification

HYPOTHESIS-ID: m5-audio-step4-hangar-writer

Session 4074 qualified the isolated default image after the concurrent image /
silent pair was route-invalid. The image-only arm passed the retail
whole-RDRAM/title/hangar controls and reached hangar with DMEM change, two
DMAs, image exit at `0x1328`, SP completion, and guest receive; stage-3 and
PCM source/consumer payloads were zero. The gate stayed zero.

Competing hypotheses:

- H94648-writer: retail's `0x80094648` writer/value/destination class is the
  hangar source boundary and the port has a corresponding gate/output row.
- Hother-writer: retail reaches hangar with the named class absent or
  non-matching, so another ranked writer class owns the missing output.
- Hcoverage: retail whole-RDRAM/title/hangar or isolated image phase coverage
  fails, making writer nulls unevaluable.

Discriminating measurement: one same-build retail-gated isolated image capture
with the existing phase-keyed task/PCM joins plus the retail writer/value
watch for `0x80094648` and its destination. H94648-writer requires retail
hangar attribution and a matching port gate/PCM row; Hother-writer requires
valid controls with no matching `0x80094648` attribution; Hcoverage is selected
by any missing whole-RDRAM, title, hangar, or isolated-image gate.

Exact implementation: start from the existing retail oracle and isolated image
driver, batch the single `0x80094648` writer/value/destination watch with the
existing task/PCM joins, run from `build/`, retain
`PROBE_PHASE_WIDTH=1024` and `PROBE_KEYS_FROM_PHASE=1`, and SIGKILL the
process group. Do not change the gate; there is no behavior rollback arm for
this qualification capture.
