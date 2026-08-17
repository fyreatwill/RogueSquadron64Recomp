# NEXT work unit (s1792)

HYPOTHESIS-ID: external-retail-entry-boundary

Mandatory 15-title REVISIT. Last-15 ledger titles after s1791 are
s1777–s1791, all sweep-scoped (`confirmed` / `synchronized`).
s1776 selected H1-submitGfx: leave adds `submitGfxFrame` +105/+103
on the attract A/Start title-like 1024 (`0x00790400`/`800` at
126.3–126.4 s). The extra presenter's caller is still unnamed.
New angle: watch the generated `submitGfxFrame` *callers* that
s1776 did not arm.

Generated call sites (13 / 12 functions). Already classified or
already in the s1776 set — do not re-arm as the discriminator:

- `cinematicLoopBody` `0x800A5D80` (s1744)
- `runInMissionFrame` `0x800FA6A4` (s1744)
- `runHangarSelectionFrame` `0x800AAD9C` (s1776 hangar; keep as control)
- `runMenuShipSelectScreen` `0x800C131C` (s1776 ship-select drop; keep as control)
- `runMenuModelViewerScreen` `0x800C28F0` (s1760 case 9 stays 1)

Unwatched callers (the discriminator):

- `runIdleFramesAndLoadSaveData` `0x8006D900` (main `.text`; two jals)
- `tickCraftSelectScreen` `0x800AF3C0`
- `menuControllerInput` `0x800B47D0`
- `runMenuRandomBackdropScreen` `0x800BF830`
- `menuSubtype02Handler` `0x800C30C8`
- `runResultsTextScreenLoop` `0x800C5EF8`
- `runModelViewerLoop` `0x800C9BF0`

Competing hypotheses:

- H1: one unwatched overlay screen loop (`0x800AF3C0` /
  `0x800B47D0` / `0x800BF830` / `0x800C30C8` / `0x800C5EF8` /
  `0x800C9BF0`) rises ~+105 and matches `submitGfxFrame`.
- H2: main-text `runIdleFramesAndLoadSaveData` `0x8006D900` is
  the extra presenter.
- H3: no unwatched caller rises; `submitGfxFrame` still +105
  (indirect / already-classified caller, or a PC this set missed).
- H4: the extra +105 is split across two or more unwatched
  callers (no single source).

Exact commands (clone `scratch/agent/s1776_maintext_pcs/run_pc.sh`;
do not extend `--secs 133`):

```
# three concurrent Rice arms; whole-RDRAM / PIF / VI controls
# PCS = 7 unwatched callers + hangar + loadOverlay + ship-select
#       + submitGfxFrame (must still show +105)
PCS="0x8006D900,0x800AF3C0,0x800B47D0,0x800BF830,0x800C30C8,0x800C5EF8,0x800C9BF0,0x800AAD9C,0x80000B20,0x800C131C,0x8000C07C"
# hold:  B_ROUTE
# a:     B_ROUTE,119:a,123:a
# start: B_ROUTE,119:start,123:start
# artifacts: scratch/agent/s1792_submitgfx_callers/
```

Expected splits:

- H1: exactly one overlay caller +~105; `submitGfxFrame` +~105;
  hangar ~flat; ship-select still drops.
- H2: `0x8006D900` +~105; overlay callers flat or down.
- H3: all seven unwatched callers flat or down; `submitGfxFrame`
  still +105. Then the next revisit needs `$ra` / jal-site
  watches, not another entry-PC set.
- H4: two or more unwatched callers rise and their deltas sum
  to ~+105.

Do not reopen the s1744 six-entry, s1760 jump-table, or s1776
main-text 11-PC recipes. After this revisit the sweep resumes at
leftover `func_800E71D0` / `transformCraftAnchorsApplySubFx3`
(`0x800E71D0`, size `0x1C0`).
