# Next work unit (s4356): M5 Step 10 audio-task rate

HYPOTHESIS-ID: m5-step10-audio-task-rate

Session 4355 qualified the selector boundary with a source audit and an
independent retail read/write witness. The broad target watch saw 820 writes,
but every sampled store PC/address was confined to `0x1535AC..0x1535BC`; the
upper selected range `0x1535C4..0x1545C0` remained unwritten while C904 ran
3,107 times. Whole-RDRAM writes (10,820), title/hangar VI progression, and
40,179 target-range reads qualified the route.

Competing hypotheses:

- H-audio-rate-divergence: real-audio and silent-control task rates diverge in
  the title-to-hangar phase, identifying the next M5 service boundary.
- H-audio-rate-equivalent: both arms have the same task rate; audio task rate
  is not the next discriminator and the plan should move to the next decoder
  boundary.
- H-instrument-boundary: phase, task, or whole-RDRAM controls fail, so no rate
  comparison is valid.

Discriminating measurement: build/run both audio arms in one phase-qualified
capture (or two simultaneously scheduled oracle captures if the task-rate
watch is only available there), count audio tasks during t=18–28 s after VI
1024 arms, and retain the silent arm as the positive route control. A clear
rate difference selects H-audio-rate-divergence; equal qualified counts select
H-audio-rate-equivalent; missing phase/task/whole-RDRAM controls select
H-instrument-boundary.

Required pre-build ground-truth check: read the task-watch options in
`tools/oracle/README.md` and identify the existing task PC/config used by the
M5 plan. Do not change decoder, RSP, AI, or runtime behavior.

Exact source audit already completed in s4355:

```
rg -n -C 100 '0x8009C0D8|0x8009C0E4|0x8009C904|0x8009C950|0x11C8|0x198\(' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c
```
