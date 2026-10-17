# Next: M3 DMA/event host-wrapper guest-pointer census
HYPOTHESIS-ID: m3-idiom-class-audits

Competing hypotheses for this unit:

- H-wrapper-safe: every live host wrapper either uses `TO_PTR`/`_arg` translation
  or passes through an existing range guard; no unvalidated guest pointer is
  dereferenced.
- H-wrapper-raw: at least one live wrapper dereferences a guest pointer without
  translation or range validation; that site is a live M3 class member.
- H-wrapper-dead: raw-looking pointer arguments occur only in no-pak/no-op
  wrappers or unreachable declarations, so they are not a live member.

Discriminating measurement: one source census over all `osViSwapBuffer`, EEPROM,
controller, and PFS/pak wrappers, with each pointer-bearing argument classified
as translated, range-checked, raw-dereferenced, or no-op. A positive-control
self-test must find a synthetic raw dereference and a synthetic translated
wrapper; the live result selects H-wrapper-raw only if a reachable wrapper has a
raw dereference, otherwise it selects H-wrapper-safe/dead with the exact
no-op/dead sites listed.

Run exactly:

    python3 tools/audit_host_wrappers.py --selftest
    python3 tools/audit_host_wrappers.py .

This unit covers `osPiStartDma`, `osDpSetNextBuffer`, and `osSetEventMesg`,
including their runtime callees. Competing hypotheses:

- H-dma-safe: all guest buffers/queues are translated or range-checked.
- H-dma-raw: a reachable DMA/event wrapper raw-dereferences a guest pointer.
- H-dma-noop: the apparent pointer-bearing path is an intentional no-op or
  stores an address without dereferencing it.

Discriminator: one source census with a positive-control self-test, classifying
each pointer argument and callee edge as translated, range-checked, raw, or
no-op. A reachable raw dereference selects H-dma-raw; otherwise the complete
table closes the class as safe/no-op.

Run exactly:

    python3 tools/audit_dma_event_wrappers.py --selftest
    python3 tools/audit_dma_event_wrappers.py .

If raw is found, name its writer and legitimacy before adding any guard. If no
raw site is found, update the ledger and move to the next M3 idiom class; no
runtime build or soak is authorized for this source audit.
