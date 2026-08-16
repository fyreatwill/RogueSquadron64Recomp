# NEXT work unit (s1682)

HYPOTHESIS-ID: external-retail-entry-boundary

Mandatory 15-title REVISIT. After s1681 the last-15 titles (s1667–s1681)
are all sweep-scoped (synchronized/confirmed). Do not resume the generated-
symbol census this iteration.

Remaining unused lead from CURRENT-TRUTH #2: C/L/R or valid D-pad **on
the arrived 640 B-frontend**. Do not repeat hold/A/B/Z, valid D-pad on
hangar, post-viewer C/L/R, post-B intermediate A/Start/Z, or post-arrival
A/Start/Z on that 640 screen. Attract-512 input (`0x00690400`) is a
separate later lead — do not confound it here.

Competing hypotheses and discriminator:

- H1: a C, L, R, or D-pad press on the arrived 640 B-frontend reaches a
  mission-path PC (`loadOverlay` `0x80000B20` / interior `0x80000B70`)
  or otherwise leaves hangar/viewer/B-frontend into a new classified
  route.
- H2: the press is ignored (same 117.7 s `640→512` attract timeout and
  origin `0x00690400` as hold).
- H3: the press changes VI/origin/PC without mission entry (e.g. cancel
  `640→1024→512` hangar like A/Start, or a new non-mission frontend).
- H4: the recipe is unevaluable (missing whole-RDRAM / PIF / hangar /
  B-route / 640-arrival controls, or the press lands after the 117.7 s
  timeout).

Discriminator: one concurrent Rice batch. Press only at 105 s and 115 s
so both land inside the ~21 s 640 window (arrival ~96 s, timeout ~117.7 s).
Do not press at 125/135 — those land on attract 512 and confound H1–H3.

```sh
# adapt scratch/agent/s1666_broute_640_post_controls/run_all.sh
# eleven-Start + B-route, Rice video, 160 s, whole-RDRAM + PIF + VI + PCs
ELEVEN="6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start"
B_ROUTE="$ELEVEN,55:b,58:b,63:b"
# arms (11 concurrent): hold + cup/cdown/cleft/cright + l + r + dup/ddown/dleft/dright
# press suffix for each candidate: ,105:<key>,115:<key>
# oracle names (verified): cup cdown cleft cright l r dup ddown dleft dright
```

Required same-run controls (all arms):

- whole-RDRAM `--watch-write 0x0:0x800000 --hit-cap 10000` must fire
- `--pif-trace` must show B as pad `0x40000000` on the way in, and the
  candidate pad after 105 s
- hangar lifecycle `320→640→1024→512` then B-route `512→1024→640` at
  ~96 s, origin `0x00696100`/`0x00696600`, **before** the 105 s press
- watch PCs: hangar-frame trio, `0x800B47D0`, `0x800C9BF0` (viewer),
  `0x80000B20`/`0x80000B70` (`loadOverlay` / +0x50)

Expected splits:

- H1: mission/loadOverlay PC fires from the 105/115 press, before timeout
- H2: VI/origin match hold through 117.7 s attract
- H3: a non-hold VI/origin/PC change with zero mission/loadOverlay from
  that press (name the new screen)
- H4: any arm misses hangar, B-route, 640 arrival, or pad delivery

Sweep resume (after this revisit only): `func_800CC9B8` /
`tickAtAtAudioAndWeaponState` at `0x800CC9B8` (size `0x164`).
