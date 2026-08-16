# NEXT work unit (s1714)

HYPOTHESIS-ID: external-retail-entry-boundary

Mandatory 15-title REVISIT. Last-15 titles after s1713 are all
sweep-scoped (s1699–s1713: synchronized / confirmed-symbol / fake
fragment). Do not resume the generated-symbol census this iteration.

s1698 classified attract-512 input in a `--secs 125` window: A/Start/
C-up/L do `512→1024` at 126.4 s origin `0x00790400`/`800` (title-like;
same pair as the B-route intermediate 1024), but the flush cut off at
the WIDTH change so the 1024 destination is unevaluable. Z/C-down/
C-left/C-right/R/D-pad stayed on attract 512 through 125.8 s. Z-on-
attract `512→1024` at 128.3 s (s1666, after a 126.4 s Z press) is
still single-source.

New angle: same B-route→attract recipe as s1698, later flush after
126.4 s and before the known ~135 s Rice/core death so the 1024
destination and the 128.3 s Z leave become evaluable.

Do not repeat hangar hold/A/B/Z, valid D-pad on hangar, post-viewer
C/L/R, post-B intermediate A/Start/Z, post-arrival A/Start/Z/C/L/R/
D-pad on the 640 B-frontend, or attract-512 A/Start/Z/C/L/R/D-pad in
the 119–125 s window as the *question*. Reuse that recipe only as the
carrier that reaches attract 512, then observe past 126.4 s.

Competing hypotheses and discriminator:

- H1: A/Start/C-up/L 1024 is a new classified route (mission-path
  `loadOverlay` `0x80000B20` / interior `0x80000B70` elevated vs hold,
  or hangar-frame PCs increment, or viewer `0x800C9BF0` fires).
- H2: the 1024 is the same B-route intermediate / title-like 1024 and
  returns to hangar 512 or attract without mission entry (H3-shaped
  frontend, not H1).
- H3: Z at 119/123 independently reproduces s1666's 128.3 s
  `512→1024` (second source) or stays on 512 through ~133 s (refutes
  the s1666 single-source leave as schedule-specific).
- H4: the later flush is unevaluable (Rice dies before destination,
  controls fail, or the 1024 never appears).

Discriminator: six concurrent Rice arms (hold + A + Start + C-up + L
+ Z) copied from `scratch/agent/s1698_attract512_input/run_pc.sh`
with `--secs 133` instead of 125. Arm ALL of: whole-RDRAM
`--watch-write 0x0:0x800000 --hit-cap 10000`, PIF, `--vi-trace`,
`--vi-poll`, hangar-frame + viewer + `loadOverlay` PCs. Do not add
the stay-512 C-down/C-left/C-right/R/D-pad arms; those are closed.

```sh
# reuse s1698 launcher; only change OUT and --secs
# ELEVEN + 55/58/63:b reaches attract 512 at ~117.7 s
# candidates still at 119/123 (after attract arrival)
# --secs 133: after 126.4 WIDTH and 128.3 Z-leave, before ~135 Rice death
```

Expected splits:

- H1: a leave arm increments hangar-frame or viewer or elevates
  `0x80000B70` vs same-run hold after 126.4 s.
- H2: leave arms show `512→1024` then `1024→512` hangar (or stay on
  the title-like 1024) with viewer 0 and B70 matching hold.
- H3: Z either does `512→1024` at ~128.3 s (confirms s1666) or stays
  512 through the flush (leaves s1666 single-source / schedule-bound).
- H4: no WIDTH change, Rice death before flush, or a failed
  whole-RDRAM/PIF/VI control.

Sweep resumes after this revisit at `npcDebrisFieldUpdate` /
`func_800D5208` at `0x800D5208` (size `0xDD8`).
