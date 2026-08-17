# NEXT work unit (s1776)

HYPOTHESIS-ID: external-retail-entry-boundary

Mandatory 15-title REVISIT. Last-15 after s1775 are s1761–s1775, all
sweep-scoped (`confirmed` / `synchronized`). Do not continue the
generated-symbol sweep this iteration.

The 126.3 s attract A/Start title-like 1024 (`0x00790400`/`800`) is
H3-stop-tick: not a new `cinematicLoopBody`, `runMenuContentStateMachine`,
`runInMissionFrame` (s1744), or `menuOverlayInit` jump-table case
(s1760). Extra menu dest +1 is reproduced. New angle: main-text
screen/frame handlers that `mainGameLoop` uses outside those overlay
tables.

Competing hypotheses:

- H1: leave adds a main-text presenter (`submitGfxFrame` `0x8000C07C`
  and/or `runVideoFrameTick` `0x80001354` and/or
  `swapBufferWithViMode` `0x8001BA9C` / `applyPendingViChanges`
  `0x8001B7F0`) after 126.3 s.
- H2: leave adds an extra `mainGameLoop` `0x8003DFA0` or
  `applyLevelScreenAndCameraSettings` `0x8006B000` entry (new outer
  iteration / screen-settings apply).
- H3: no main-text handler increases; leave only stops the
  overlay-aliased ticks (H3-stop-tick extends to main text).
- H4: leave adds `emitFrameRdpInitDl` `0x80008D20` (new camera/viewport
  bake for the 1024) without H1/H2.

Discriminator: three concurrent Rice arms copied from
`scratch/agent/s1744_1024_overlay_pcs/run_pc.sh` (`--secs 133`,
whole-RDRAM 10k, PIF/`[pad]`, `--vi-trace`, `--vi-poll`). Hangar
frame, `loadOverlay` entry/menu dest, and `0x800C131C` stay as
same-run controls (s1760: `0x800C131C` is 257 hold / 79 leave,
nonzero). New PCs only — do not re-arm the s1744 six-entry set or
the s1760 11-way table. A and Start are the two leave sources.

```
PCS="0x800AAD9C,0x80000B20,0x80000BA8,0x800C131C,0x8003DFA0,0x8000C07C,0x80001354,0x8006B000,0x8001B7F0,0x8001BA9C,0x80008D20"
# hold:  $B_ROUTE
# a:     $B_ROUTE,119:a,123:a
# start: $B_ROUTE,119:start,123:start
# copy the rest of s1744 run_pc.sh (core/rom/video/watches/vi/pif)
# write artifacts under scratch/agent/s1776_maintext_pcs/
```

Expected splits:

- H1: a presenter PC's leave count exceeds hold after the 126.3 s
  WIDTH change; controls still fire (`0x800C131C` nonzero, whole-RDRAM
  ≥10k, PIF B-pad, hangar frame ~60).
- H2: `0x8003DFA0` or `0x8006B000` leave > hold; presenters do not
  uniquely increase.
- H3: every new main-text PC is flat or down; only the known
  overlay-aliased ticks drop.
- H4: `0x80008D20` leave > hold and H1/H2 presenters/`mainGameLoop`
  do not.

Do not extend `--secs 133`. Do not repeat §35 classified routes.
After this revisit, resume the sweep at
`playDualTextureAttachmentCueMode0` / `func_800E4034` (`0x800E4034`,
size `0x1C`).
