# Session 5191 — `__osSiRawStartDma` audit

Candidate: `__osSiRawStartDma = 0x80033B20`.

The bounded rename helper reported `already-synchronized` and renamed zero
references in zero files. Independent searches of the generated tree found no
body, placeholder, overlay record, or direct generated caller at the
companion address. The symbol map gives `__osSiDeviceBusy = 0x80033BD0` as
the next entry, so the nominal span is `0xAC`, but there is no generated body
to validate. Preserve the existing ABI name.

This is the `H-host-wrapper`/unmaterialized outcome, not a runtime finding.
No build or soak was warranted for this naming-only result. Continue the
bounded sweep at `__osSiDeviceBusy`.
