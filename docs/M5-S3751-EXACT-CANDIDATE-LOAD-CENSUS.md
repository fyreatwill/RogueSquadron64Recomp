# M5 session 3751 — exact candidate load census

Retail mupen64plus passed the whole-RDRAM positive control with 10,012 writes,
reached both target VI phases, and executed `0x800B4B08` once plus the three
`0x8008F548/5F0/640` consumers. Exact-field watches also fired four times
each at `0x128C92` and `0x128CD0..D3`.

One regenerated build hooked all nine bounded candidate loads. The qualified
real-audio port reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, with 1,024 target source-reader rows and 512
source-range-writer rows. The silent arm reached both target phases and
emitted no target source rows. The exact-hook positive control fired in both
arms, but neither arm produced a target-phase row with effective base
`0x80128C70`; the only control row used base `0x80130B40`.

This selects `H-RouteStateNotSource` for the complete candidate set and
refutes `H-RouteStateSourceKey`. `H-RouteStateStale` is unelected because no
candidate reads the exact object at all. The route fields remain unresolved
metadata or belong to a different producer/read class.

ORIGIN: diagnostic-only load hooks and source-DMA joins; no guest value,
branch, DMA, or rendering behavior was changed.

Evidence: `scratch/agent/oracle_s3751.log`,
`scratch/agent/s3751_realb/run.log`, and
`scratch/s3751_silentb/run.log`.
