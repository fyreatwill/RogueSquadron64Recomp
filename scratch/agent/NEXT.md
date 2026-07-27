# NEXT work unit — M3: refuse wild-width FB registration

s77: createTileCopy **found=0 never** through hangar-flight freeze; **found=1 ≥8000**
(control). Wild FB **registers**: `addr=0x530000 fbW=4030` found=1. fs freezes ~3361;
trailing high-tri `syncs=0` from #4326. s76 createTileCopy assert is intermittent.
Detail: `scratch/s73_post_a_scene/TILECOPY_ANALYSIS.md`.

## Competing hypotheses

| ID | Claim | If true, we will see… |
|----|--------|------------------------|
| G1 | Wild-width FBs in the map poison present/fullSync → freeze | after refuse gate: refuse count >0 post-leave; fs keeps rising past ~3360; black window shrinks/stops |
| G2 | Registration is a red herring; freeze is only SYNC_FULL starvation (D3) | refuse>0 but fs still plateaus ~3360 and black continues |
| G3 | Gate causes new createTileCopy found=0 on addresses that still appear in ops | record/setup found=0 >0 after gate (setup should ignore; process must not Abort) |
| G4 | Legitimate widths >1280 exist in this game | refuse fires on 512/640-era good content frames (control failure — abort the gate) |

## Discriminating measurement (one build, one soak)

In `FramebufferManager::get` (and keep `ROGUESQ_LOG_TILECOPY_FB`):

1. If `width > 1280` (or height absurd — optional): **do not insert/update** a real FB;
   log `[fb-get] REFUSE addr=… w=…` every time (or first N + every K). Prefer return
   a no-op path that callers tolerate, or skip the get at the colorImg pair site —
   match s72 threshold.
2. Keep tilecopy-fb logs (found=1 control must still fire on 512/640).
3. Soak: start_only HOLD_S=20 (death/freeze window).

```bash
# after instrument + export.sh + cmake --build build -j8:
env PROBE_MODE=start_only HOLD_S=20 ROGUESQ_LOG_TILECOPY_FB=1 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh fbgate 0 12
# offline:
#   grep -c '\[fb-get\] REFUSE'          — must be >0 (gate active)
#   grep '\[tilecopy-fb\].*found=1'      — control still fires, fbW<=1280
#   grep -c '\[tilecopy-fb\].*found=0'   — G3
#   fs max / plateau; CRASH; black snap sizes hold_06–20
```

### Outcomes

- **G1:** keep gate default-on; re-soak HOLD_S=60 + stick for craft response.
- **G2:** revert or leave gate as safety; next unit = SYNC_FULL / runner hist post-leave.
- **G3:** ensure setup ignore path handles missing (already does); assert must not fire.
- **G4:** raise threshold or whitelist; do not ship a broken gate.

## Do not

- Convert createTileCopy assert→skip without a found=0 log in-run.
- Re-open s72 OSThread writeback unless thr-resume bad=1.
- Cross-run A/B on animating hangar-flight without phase gate.
- Claim gate fixed present without same-run refuse>0 + found=1 control.
