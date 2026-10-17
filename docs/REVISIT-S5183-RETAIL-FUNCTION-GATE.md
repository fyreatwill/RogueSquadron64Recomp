# Session 5183 retail function-entry gate

The qualified retail-oracle route passed the whole-RDRAM positive control and
both mission VI phase controls. The new containing-function entry watch at
`0x8008FAAC` fired 145,268 times, while the old interior-site watch at
`0x800903F0` fired zero times. Adjacent writer watches fired 1,205 times.

This selects `H-retail-branch-diff` for this single source: retail enters
`fillSampleStreamRange` but does not reach the previously watched interior
branch. It does not prove a port defect or close the boundary, because the
port-side join and a second independent attribution source were not part of
this work unit. The earlier `H-retail-function-absent` interpretation is
superseded for the containing function, while the exact interior consumer
remains unresolved.

The run used `scratch/agent/s5183_retail_entry_function_gate.sh`; its raw
trace is intentionally outside version control because it is multi-gigabyte.
