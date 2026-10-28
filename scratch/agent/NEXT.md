# NEXT: 16:9 flight radar anchor
HYPOTHESIS-ID: g1d-hud-anchor-right

s6609 closed the owner-sheet question. Retail, 16:9 and 21:9 hangar+flight
windows were paired with VI-bounded sources (`docs/owner_sheet_s6609_aspect.png`).
Extra width is additional scene. The left shield is x 44..71 at every width.
The flight radar's right edge is retail 476, 16:9 794 (clipped, width 73 vs
89), 21:9 991 (whole, inset 32). Those are exactly 476+334 and 476+515.

The logged anchor pairs are `142,334` at fb 796 and `256,515` at fb 1024
(`A, A+RA` from `rs64_g1d_apply_aspect_policy`). `tools/apply_s6155_hudcpos.py`
does `n = x - A`; left items keep `n`, right items get `n + second`. If the
game already added `A` before that hook, the right edge becomes retail+second.
second=`fbw-512` would preserve the retail inset (796 -> 760, 1024 -> 988).
The current second term overshoots 796 by 50 px and clips, and overshoots
1024 by only 3 px. Per-sprite f4 was not logged; this run is the test.

ONE work unit: change only the second `ROGUESQ_HUD_ANCHOR` number from
`A+RA` to `fbw-512` in `src/main/main.cpp` (`rs64_g1d_apply_aspect_policy`).
Do not change `ROGUESQ_SHIFT_REGION` or `ROGUESQ_LOG_REGION` in the same arm.
Rebuild the game target only (the patch already reads the env). No regen.

Hypotheses:
- H-anchor: the s6155 right-half add is the writer. After the change, 16:9
  radar right edge moves from 794 to about 760 (inset ~35, width ~89) and
  21:9 moves from 991 to about 988. Left shield stays x 44..71.
- H-not-live: the boxes matched the constants by coincidence. The radar box
  does not move. Revert the constant in this same iteration.
- H-other-hud: the radar moves as predicted but another right-edge HUD
  element (the green reticle) leaves the frame or doubles its error. Then
  the single second-term is not safe for every right-half sprite; report
  which element and do not keep the change.

Discriminator: radar bounding box on the VI-bounded flight source, same
route as s6609, 16:9 and 21:9, one binary. Positive control: left shield
box unchanged, and both arms reach flight (phase width 796 or 1024, height
444) with 0 crash lines. Retail inset 35 from s6609 is the control; do not
spend a third run unless the wide arms fail to reach flight.

```sh
# edit main.cpp second anchor term, then:
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
# screen unlocked (ioreg CGSSessionScreenIsLocked / IOConsoleLocked)
# reuse scratch/agent/s6609_capture_run.py env with ROGUESQ_ASPECT=16:9 then 21:9
# SIGKILL after the flight window shot. Measure green-left and red-right boxes.
```

Do not touch the 21:9 level-select tear in this unit. It is next-steps item 2:
source and window both torn on n=1400/1500/1600, absent at 16:9 and retail,
so the writer is still unnamed. No cull.

The 21:9 fb-flip-range log missed the hangar copy because it keeps only 64
lines per phase and the hangar stayed in phase 4. Do not read that absence
as "RT64 never copied 1024x336".
