# M5 s4935 — retail writer context

The bounded retail oracle capture ran for 240 seconds with whole-RDRAM and VI
controls, `--watch-pc 0x80091784`, `--pc-field-dump 0x80091784`, and the
independent `--pc-task-dump 0x80033FCC --pc-task-type 2` decoder.

Controls were positive: whole-RDRAM activity passed its threshold and VI
polling reached the 512-wide hangar and mission origins, including
`0x00690400` and `0x00620400`. The writer executed 12,077 times. Its
phase-gated context retained `s0=0x80149470`, used rotating small `s1`
selectors, and repeatedly carried mission values `a1=0x142`, `a2=2`.
The independent task decoder reported `rows=0/8192`, `phase_hits=0`, and no
type-2 rows at `0x80033FCC`.

This selects H-auxiliary-writer over H-task-writer for this capture: the
`0x80091784` execution is real in all three route buckets, but these fields do
not expose an OSTask publication boundary. It is single-source retail
evidence. The writer's ultimate store target remains open; no runtime
mitigation or value filtering is authorized.
