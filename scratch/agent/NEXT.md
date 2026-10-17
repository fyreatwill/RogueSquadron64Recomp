# Next: M3 remaining timer/virtual/cache host-wrapper guest-pointer census
HYPOTHESIS-ID: m3-idiom-class-audits

Competing hypotheses:

- H-host-safe: timer/virtual/cache wrappers translate every guest pointer before
  dereference or forward it to a runtime callee that does so.
- H-host-raw: a reachable timer/virtual/cache wrapper raw-dereferences a guest
  pointer without translation or range validation.
- H-host-noop: pointer-looking arguments are only stored, forwarded, or
  intentionally returned as no-op/error paths.

Discriminating measurement: one source census over `osSetTimer`,
`osStopTimer`, `osVirtualToPhysical`, `osInvalDCache`, `osWritebackDCache`,
`osPiGetCmdQueue`, and their runtime callees. The positive control must
classify synthetic translated, raw, and no-op bodies correctly. A reachable
raw dereference selects H-host-raw; otherwise the complete live table selects
H-host-safe/noop.

Run exactly:

    python3 tools/audit_timer_virtual_cache_wrappers.py --selftest
    python3 tools/audit_timer_virtual_cache_wrappers.py .

If raw is found, name its writer and state whether the value is legitimate
before adding any guard. If no raw site is found, update the ledger and move to
the next M3 idiom class; no runtime build or soak is authorized for this source
audit.
