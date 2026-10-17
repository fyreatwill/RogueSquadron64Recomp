# Session 5126 rename audit: `osDpGetCounters`

Candidate: companion symbol `osDpGetCounters = 0x8002B590`.

The companion map places the next entry at `osDpSetStatus = 0x8002B5E0`, giving
the bounded candidate span. The generated tree contains no generated prologue,
body, placeholder symbol, or overlay record for `0x8002B590`; it contains only
the `osDpGetCounters_recomp` ABI calls at `funcs_3.c:20318` and
`funcs_3.c:20788`.

The bounded rename helper changed zero references and reported:

```text
renamed 0 references in 0 files
candidate 0x8002B590 osDpGetCounters: already-synchronized
```

This selects the host-wrapper/ABI-boundary outcome. Preserve
`osDpGetCounters_recomp`; no source rename, build, or soak was warranted.
Independent companion-map, generated-tree, overlay-record, and caller-count
checks agree.
