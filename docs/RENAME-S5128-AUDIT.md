# Session 5128 rename audit: `__osExceptionPreamble`

Candidate: companion symbol `__osExceptionPreamble = 0x8002B5F0`.

The companion map places the next entry at `__osException = 0x8002B600`,
giving a bounded span. The generated tree contains no generated prologue,
body, placeholder symbol, or overlay record for `0x8002B5F0`; the targeted
search found no generated reference to this address or symbol. The bounded
rename helper changed zero references and reported:

```text
renamed 0 references in 0 files
candidate 0x8002B5F0 __osExceptionPreamble: already-synchronized
```

This selects the host-wrapper/ABI-boundary outcome. Preserve the runtime ABI
name; no source rename, build, or soak was warranted. Companion-map,
generated-tree, overlay-record, and caller-count checks agree.
