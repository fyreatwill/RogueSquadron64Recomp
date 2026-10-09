# Next work unit (s4335): field-dump the retail descriptor boundary

HYPOTHESIS-ID: m5-step9-retail-boundary-map

The s4334 retail census passed all controls. Exact C88C remained absent, while
C904 (1,059), D7D0 (3,748), D8C4 (3,748), DB44 (937), DC98 (3,748), and DD7C
(29,984) executed in the mapped region. C904 is the next retail descriptor
candidate; these are lifetime counts, not yet a phase-specific field result.

Competing hypotheses:

- H-retail-counterpart: C904 is the retail descriptor-helper counterpart and
  its phase-gated fields can be compared to port C88C rows.
- H-retail-inner-boundary: C904 executes, but its fields are not the port
  descriptor; the counterpart is another boundary in the C904-to-D7D0 chain.
- H-oracle-invalid: a repeat loses the whole-RDRAM, title, or hangar controls.

Discriminator: run one retail oracle census with whole-RDRAM, VI trace, and
`--pc-field-dump 0x8009C904` phase-gated to `0x006AB400:512` and
`0x006AB800:512`. Nonzero stable rows with valid object/descriptor fields
select H-retail-counterpart; controls intact but zero/invalid C904 fields
select H-retail-inner-boundary; missing controls select H-oracle-invalid. Do
not change runtime behavior.

Suggested command shape:

`tools/oracle/build/rs64_oracle ... --watch-write 0x0:0x800000 --watch-pc 0x8009C904 --pc-field-dump 0x8009C904 --pc-phase-log-width 0x006AB400:512 --pc-phase-log-width 0x006AB800:512 --vi-trace ...`

Do not change decoder, RSP, AI, or game-path behavior. Keep all comparison
rows phase-gated on VI origin `0x006AB400` and width 512.
