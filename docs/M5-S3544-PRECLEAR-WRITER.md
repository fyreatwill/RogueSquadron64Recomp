# M5 session 3544 — pre-clear writer attribution

The widened source-span scalar-store census ran from process start through
the target clears on the real-audio LLE/spin-yield/autopilot route. Its
positive control fired, and the port reached title VI 1024 and hangar VI 512.

The census recorded 268 overlapping stores to the hangar source span during
the preceding width-640 phase, including 104 nonzero stores. The last
nonzero event before the hangar clear was:

```
phase=3 width=640 origin=0x00696100
pc=0x8001FAF8 phys=0x17992E len=2 value=0x0000000F value_nz=1
```

The subsequent phase-qualified `rs_memset` entered with
`dst=0x801797B0`, `len=0x298`, and `pre_nz=155`, then exited with `pre_nz=0`.
The title clear independently entered with `pre_nz=0`. The source-range
writer rows and the pre-clear snapshot are two same-run observations joined
by phase and event order; the retail ground-truth capture independently
reached both target phases and recorded nonzero writes to the corresponding
range.

This selects `H-PortPrephaseCPU` and rules out `H-CarriedInitialState` for
this run. The observed PCs are the existing generated scalar-store sites in
the texture-record construction family (`0x8001FACC`–`0x8001FD2C`); their
individual metadata writes are legitimate operations at their executed
destinations. This result identifies a pre-clear CPU writer at the address
boundary, but does not yet establish why the port's source-range contents
differ from retail or which higher-level producer selected that destination.

The capture was diagnostic only: no audio, PCM, image-task, or output state
was changed.
