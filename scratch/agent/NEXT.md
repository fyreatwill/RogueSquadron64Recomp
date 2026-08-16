# NEXT work unit (s1744)

HYPOTHESIS-ID: external-retail-entry-boundary

Mandatory 15-title REVISIT. Last-15 titles after s1743 are s1729–s1743,
all sweep-scoped (synchronized / confirmed). Do not resume the
generated-symbol census. Do not extend the s1714 `--secs 133` recipe —
Rice dies ~135 s, ~7 s after the 1024 WIDTH, so a later flush cannot
see a destination VI.

New angle: identify the attract A/Start/C-up/L/Z title-like 1024
(`0x00790400`/`800` at 126.4 s) by overlay-resident PCs during the
126.4–133.5 s dwell, not by waiting for a later WIDTH.

Competing hypotheses and discriminator:

- H1: menu overlay is live on the 1024 —
  `runMenuContentStateMachine` (`0x800C1878`) or
  `runMenuShipSelectScreen` (`0x800C131C`) fire after 126.4 s on
  A/Start arms and stay 0 on hold.
- H2: cinematic overlay is live —
  `cinematicLoopBody` (`0x800A5D80`), `load_cutscene` (`0x800A6620`),
  or `tickCutsceneActionSlots` (`0x800AA658`) fire after 126.4 s.
- H3: same attract/frontend state as hold, just a different
  framebuffer — new overlay PCs stay 0 on every arm; hangar-frame /
  viewer / `0x80000B70` still match hold (s1714).
- H4: mission overlay is live — `runInMissionFrame` (`0x800FA6A4`)
  fires after 126.4 s.

Copy `scratch/agent/s1714_attract512_later_flush/run_pc.sh` to
`scratch/agent/s1744_1024_overlay_pcs/run_pc.sh`. Keep the six-arm
carrier (hold + A + Start + C-up + L + Z), `--secs 133`, whole-RDRAM
`--watch-write 0x0:0x800000 --hit-cap 10000`, PIF/`[pad]`,
`--vi-trace`, `--vi-poll`, and the s1714 hangar/viewer/`loadOverlay`
PC list as controls. APPEND these PCs (not previously watched):

```
0x800A5D80,0x800A6620,0x800AA658,0x800C1878,0x800C131C,0x800FA6A4
```

Expected splits:

- H1: menu PCs > 0 after 126.4 s on leave arms, 0 on hold.
- H2: cinematic PCs > 0 after 126.4 s on leave arms, 0 on hold.
- H3: all six new PCs stay 0; controls match s1714 hold.
- H4: `runInMissionFrame` > 0 after 126.4 s on leave arms.

Do not repeat §35 classified button/VI routes. After this revisit the
sweep resumes at `npcRadarDishInit` / `func_800DC228` (`0x800DC228`,
size `0xD8`).
