# Next work unit: classify the queued M5 status-03 service-reaping capture

HYPOTHESIS-ID: m5-status03-service-reaping-contract

Read the new `scratch/agent/SOAK-RESULTS.md` verdict and inspect only the
queued run's `verdict.txt`, `retail-summary.txt`, and `port-summary.txt`.
Require the same-run positive controls: retail whole-RDRAM, retail title and
hangar, and port title and hangar. Then classify the hangar rows:

- Hworker-clears: qualified worker entry, `service-store`/`status-writer` at
  `0x8009B7EC` with old status `0x03` and value zero, followed by worker and
  shutdown/drain return.
- Hworker-missing: all route controls pass and status-03 worker/read activity
  is present, but no legitimate zeroing writer is observed.
- Hroute-invalid: any required control or either paired route is absent; writer
  nulls are unevaluable.

Do not force-clear status 03 or enqueue another recipe. No build is needed
unless the queued result identifies a diagnostic coverage failure that can be
fixed in the existing regeneration-safe probe.
