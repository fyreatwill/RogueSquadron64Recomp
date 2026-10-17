# Session 5127 rename audit: `osDpSetStatus`

Candidate: companion symbol `osDpSetStatus = 0x8002B5E0`.

The companion map places the next entry at `__osExceptionPreamble =
0x8002B5F0`, giving a bounded span. The generated tree contains no generated
prologue, body, placeholder symbol, or overlay record for `0x8002B5E0`; it
contains only two direct calls to `osDpSetStatus_recomp` at
`funcs_3.c:20660` and `funcs_5.c:6875`.

The bounded rename helper changed zero references and reported:

```text
renamed 0 references in 0 files
candidate 0x8002B5E0 osDpSetStatus: already-synchronized
```

This selects the host-wrapper/ABI-boundary outcome. Preserve
`osDpSetStatus_recomp`; no source rename, build, or soak was warranted.
Independent companion-map, generated-tree, overlay-record, and caller-count
checks agree.
