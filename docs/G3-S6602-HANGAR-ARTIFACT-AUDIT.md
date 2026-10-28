# G3 Session 6602 — same-phase hangar artifact audit

The current Debug binary ran the same keyed route with retail 4:3, ASPECT
16:9, and ASPECT 21:9. Each arm reached its expected hangar/flight phase and
completed a 130-second verification hold with zero crash lines and zero
30-second VI stalls.

| arm | hangar-phase width | dumps | result |
|---|---:|---:|---|
| retail | 512 | 475 | clean image control |
| 16:9 | 796 | 354 | striped interior band visible |
| 21:9 | 1024 | 255+ | striped interior band visible |

The retail phase transition was `512 @ 0x006AB400`. Wide arms use allocator-
dependent origins, but their width transitions were `796 @ 0x00A631B8` and
`1024 @ 0x00B20400`, respectively. All arms fired `[fbdump]`, `[vi]`,
`[tricnt]`, and `[rt64drawn]` controls.

At dump ordinal 1150, a row-to-row roughness scan found no interior high-
roughness run in retail, a 16:9 run around x=269..334, and a 21:9 run around
x=347..639. Contact sheets are `scratch/agent/s6602_hangar_capture/*_hangar.png`.

This selects a wide-only framebuffer/stride family over identical game
geometry, but does not name the writer. The triangle/drawn counters report
task ordinals and do not yet join an RDP command to the dumped framebuffer.
No mitigation was landed.
