# Next work unit (s4314): extend the keyed retail/port read comparison to 16,384 rows

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4313): the independent retail oracle passed the whole-RDRAM control,
title VI 1024, and hangar VI 512. It recorded 1,438,563 target reads with no
crash, and the first 4,096 keyed `(PC,address,value)` rows exactly match the
qualified port sequence. The previous 256-row ceiling is therefore extended
without finding a divergence.

State (s4312): the exact seeded-save/boot-key route with
`ROGUESQ_M4_Y8000_WIDTH=512` reached VI 512 at 42.2 s. The adjacent-range and
phase-gated read controls both fired; the target block was freed at guest PC
`0x80095D54`; and 4,096 writer plus 4,096 read rows were captured with zero
requested-vs-post mismatches and no crash marker. The extended port route is
qualified.

State (s4310): the corrected boot-relative seeded-save/key route reached VI 512
at 42.0 s, passed the adjacent-range and phase-gated read positive controls,
and captured 256 target reads plus 256 selected writer rows with 0 mismatches.
The target block `0x8017D910` was freed by `waitForAnyAudioSlot` at guest PC
`0x80095D54` before the hangar phase. The first port read
`0x8008FCE8: 0x17D9E0 -> 0x8017D9F8` matches the independent retail boundary.
Port-only reuse before the first consumer read is therefore ruled out; the
later consumer traversal/layout divergence remains open.

Competing hypotheses:

- H-free-before-consumer: selected at the first-read boundary; the shared free
  precedes the port read and its PC/address/value match retail.
- H-port-reuse-before-consumer: ruled out at that boundary by the free/read
  join and the matched first value.
- H-retail-reclaims-different: remains possible only after row 4,096; the
  4,096-row keyed comparison is parity-clean.

Discriminator: extend both keyed target sequences from 4,096 to 16,384 rows,
retaining the whole-RDRAM positive control and VI-512 phase gate. A first
keyed mismatch names the later divergence; equality through 16,384 further
qualifies parity. A route/control failure is invalid and proves nothing. Do
not add a guard or skip.

Before any build, inspect the existing port free/read join and confirm its
positive-control and phase-gating fields. Batch all three hypotheses in one
instrument/build/run; do not make an A/B arm or mitigation.

Before any build, inspect `tools/oracle/README.md` and preserve the same
whole-RDRAM positive control and phase-gated target watch. Batch the 16,384-row
cap change and keyed output in one build/run. The port-side 4,096-row result is at
`scratch/agent/s4312_port_free_read_join/run2/run.log`. A missing positive
control or no VI 512 is invalid; do not add a guard or skip.
