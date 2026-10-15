# M5 s4893 — callback teardown reachability

The Debug target was rebuilt once and run on the qualified real-audio/LLE/
ungated/solo/spin-yield route. The corrected capture enabled the existing
callback-entry, callback-table, PCM-boundary, audio-return, SP, and phase
controls in one run.

The route passed independent controls: title VI 1024, hangar VI 512, 1,271
phase-5 `sp-complete-return` rows, 94 nonzero PCM-source rows, 524 PCM
consumer rows, and 524 audio-return rows. There were no crash or abort rows.

The `shutdownAudioEngine` entry probe (`s4771-cb`) recorded 9 entries across
phases 2 through 5. The callback-table trace recorded 12 deregistration
enter/exit pairs, including the `0x8009123C` synth callback and the adjacent
`0x8009B5A8` callback. The entry and deregistration evidence is independent of
the route/PCM controls and establishes that the covered route does reach the
teardown boundary and continues into later title/hangar work.

The `s4782-shut` helper emitted a `shutdownMusyXVoices` row but no
`shutdownAudioEngine` row, even though the `s4771-cb` entry probe fired for
that function. Therefore this run does not provide a direct
`shutdownAudioEngine` return marker; that missing row is an instrumentation
gap, not evidence of a non-return.

Conclusion: H1 is selected at route level — teardown entry, callback-table
deregistration, and downstream continuation are observed. H2 is rejected by
the entry rows and H3 is rejected by the successful deregistration and
downstream controls. The exact function-return boundary remains open.

ORIGIN: diagnostic-only generated entry/table probes and existing PCM/SP/VI
controls. No callback table, teardown, or audio behavior was changed.
