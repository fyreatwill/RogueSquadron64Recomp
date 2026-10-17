# Session 5192 — `__osSiDeviceBusy` audit

Candidate: `__osSiDeviceBusy = 0x80033BD0`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent searches of the generated tree found no
body, placeholder, overlay record, or direct generated caller at the
companion address. The symbol map gives `__osSiRawReadIo = 0x80033C00` as the
next entry, so the nominal span is `0x30`, but there is no generated body to
validate. Preserve the existing ABI name.

This is the `H-host-wrapper`/unmaterialized outcome, not a runtime finding.
No build or soak was warranted for this naming-only result. Continue the
bounded sweep at `__osSiRawReadIo`.
