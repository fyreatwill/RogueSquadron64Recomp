# NEXT work unit (s1698)

HYPOTHESIS-ID: external-retail-entry-boundary

Mandatory 15-title REVISIT. After s1697 the last-15 titles (s1683–s1697)
are all sweep-scoped (synchronized / confirmed-symbol / fake-fragment
census). Do not resume the generated-symbol sweep.

Remaining unused lead from CURRENT-TRUTH Next steps #2: any input on the
attract 512 the 640 B-frontend times out into (`0x00690400` /
`0x00690800` at ~117.7 s). Z-on-attract `512→1024` at 128.3 s is still
single-source because the s1666 hold died at 135 s.

Do not repeat hold/A/B/Z on hangar, valid D-pad on hangar, post-viewer
C/L/R, post-B intermediate A/Start/Z, or post-arrival A/Start/Z/C/L/R/D-pad
on the 640 B-frontend. Those are classified.

Sweep resume after this revisit: `func_800D1578` /
`advancePlayerAtStLocomotion` at `0x800D1578` (size `0x1B8`).

Competing hypotheses and discriminator:

- H1: a press on that attract 512 reaches mission-path PC `loadOverlay`
  `0x80000B20` / interior `0x80000B70` (elevated vs hold) or otherwise
  leaves into a new classified route (mission / viewer / hangar cancel).
- H2: the press is ignored (same attract 512 origin `0x00690400` and no
  new VI/PC vs hold through the flush).
- H3: the press changes VI/origin/PC without mission entry (hangar
  cancel, viewer, or a new frontend). Includes independently confirming
  Z-on-attract `512→1024`.
- H4: the recipe is unevaluable (no 117.7 s attract arrival, failed
  whole-RDRAM/PIF/hangar controls, or the ~135 s Rice/core death eats
  the flush).

Discriminator: concurrent Rice arms (hold + A/Start/Z + C/L/R + D-pad)
on the same B-route that s1682 used, with presses only after the
117.7 s `640→512` attract arrival. Whole-RDRAM, PIF, VI, and watched
frontend/mission PCs in every arm.

Copy `scratch/agent/s1682_broute_640_clr_dpad/run_pc.sh` into a new
`scratch/agent/s1698_attract512_input/` directory. Change:

- `OUT` to that new directory
- `--secs 125` so the oracle exits before the known ~135 s Rice/core
  death and flushes `[oracle] watch pc` lines (s1682 batch 1 at 160 s
  died first)
- press suffix `119:<btn>,123:<btn>` so both land inside 117.7–125 s
- keep `B_ROUTE` (`eleven-Start + 55:b,58:b,63:b`) and the same
  `--watch-write` / `--watch-pc` / `--vi-trace --vi-poll --pif-trace`
  set as s1682

Expected same-run positive controls (must fire in every arm):

- whole-RDRAM `--watch-write 0x0:0x800000 --hit-cap 10000` reaches
  the 10,000-callback threshold
- hangar-frame PCs `0x800AAD9C` / `0x800AB0EC` / `0x800AB1C4` fire
- B delivered as pad word `0x40000000` around 56/59/64 s
- `1024→640` at ~96.4 s origin `0x00696100`/`0x00696600`
- `640→512` at ~117.7 s origin `0x00690400`/`0x00690800` **before**
  the 119 s candidate press

Expected splits:

- H1: a candidate elevates `0x80000B70` vs hold, or leaves to a
  mission/viewer VI+PC the hold arm does not take.
- H2: every candidate matches hold through 125 s (still attract 512
  `0x00690400`; viewer 0; B70 not elevated vs hold).
- H3: VI/origin/PC diverge without mission entry. If Z (and only Z)
  does `512→1024` inside the 119–125 s window, that independently
  confirms the s1666 128.3 s single-source lead.
- H4: attract 512 never arrives, or PC summaries are missing because
  the 135 s death fired.

Do not mix in an M4 DMEM destination in the same run. Alternative only
if this attract-512 recipe is actually blocked this iteration: a new M4
RDRAM destination from a DMEM→RDRAM transfer other than `0xD60`.
