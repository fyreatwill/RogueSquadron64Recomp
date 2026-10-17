# Session 5125 rename audit: `osDestroyThread`

Candidate: companion symbol `osDestroyThread = 0x8002B480`.

The companion map names the entry, but the generated snapshot contains only
the `osDestroyThread_recomp` ABI declaration and one direct call site. Its
overlay entry has `rom_size = 0`; there is no generated prologue/body or exact
generated span at the companion address. The next companion entry is
`osDpGetCounters = 0x8002B590`.

The bounded rename helper changed zero references and reported:

```text
renamed 0 references in 0 files
candidate 0x8002B480 osDestroyThread: already-synchronized
```

This selects the host-wrapper/ABI-boundary outcome. Preserve
`osDestroyThread_recomp`; no source rename, build, or soak was warranted.
Independent companion-map, generated-tree, overlay-record, and caller-count
checks agree.
