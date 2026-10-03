# M5 s3747 — remaining host RDRAM write census

The bounded source census searched `src/`, the host-side librecomp sources and
headers, and ultramodern sources for target literals, direct `rdram` pointer
assignments, host-buffer copies, and `MEM_*`/`SD` writes. It was run with:

    tools/audit-host-rdram-writes.sh > /tmp/rs64-host-rdram-writes-s3747.txt

The scan found 11 target-literal occurrences, all in the existing M5
diagnostic read/watch code in `src/main/main.cpp` and
`src/main/upstream_compat.cpp`; no
production host writer contains a literal for `0x128C92` or
`0x128CD0..0x128CD4`. Direct `rdram[...] =` assignments are confined to the
existing diagnostic fill markers in `main.cpp` and `dpc_bridge.cpp`. The
remaining host-buffer writes use the generic `MEM_*` macros and are the PI ROM,
PI SRAM, zmemcpy, RSP-DMA, runtime initialization, controller, flash, and
overlay/configuration paths already covered or excluded by the s3746 API census.

This is a static source result, not a runtime writer-PC attribution. It rules
out a literal-target direct host writer in the scanned production sources, but
it cannot rule out a computed-pointer write through a generic macro or an
external library. The platform-native writer-PC watch remains the only way to
resolve that residual possibility. No mitigation was added.

ORIGIN: no corruption value was changed. The observed zero route state remains
owned by the existing guest clear/source path; this iteration only enumerated
possible host-side writers.
