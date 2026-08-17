# NEXT work unit (s1872)

HYPOTHESIS-ID: m4-accumulator-boundary-revisit

Mandatory 15-title REVISIT. After s1871 the last-15 titles are
s1857–s1871, all sweep (`confirmed the leftover … symbol` /
`synchronized`). Do not start leftover `func_800F2208`. Re-attempt
the parked M4 hangar/512 live-`0x8000` Y window with a new gate,
not another VI 640 walk.

s1856 selected H-never-live on VI 640 attribution LLE
(single-source). The s1602 `0xFFFF8000` sentinel was hangar-shaped;
hangar 512 (origins `0x006ab400` / `0x006ab800`) is still unchecked.
Reuse the existing s1856 instrument (fixup 20 +
`rs64_m4_y8000_*` in `src/rsp/dpc_bridge.cpp`). Do not re-walk the
ovl20 consumer table, the 32-byte `0xD60` shape, or VMADH/VGE.

Competing hypotheses (same split as s1856, now gated on hangar 512):

- H-clip-reject: a live `+0x1A == 0x8000` reaches `L_17F0` at VI
  512 but every such triangle is clip-rejected; no flushed `0xD60`
  command has YL/YM/YH `0x8000`.
- H-zero-height-emit: at least one flushed `0xC8|flags` at VI 512
  has YL = YM = YH = `0x8000`.
- H-on-screen-emit: at least one flushed command at VI 512 has one
  or two Ys equal to `0x8000` and the three Ys are not equal.
- H-never-live: `n_flush > 0` at VI 512 and no `L_17F0` entry in
  that window sees `+0x1A == 0x8000`.

Exact commands:

```
# Attribution LLE only. Gate the existing counters on hangar 512.
# Do not treat attract 512 as hangar — require origin
# 0x006ab400 / 0x006ab800 (or an explicit hangar-frame PC).
# If the default port path never reaches hangar 512, that is
# UNEVALUABLE; use the eleven-Start hangar-entry recipe (s707,
# s1496 / PROJECT-OVERVIEW §35) rather than lowering the gate
# onto attract 512.

mkdir -p scratch/agent/s1872_m4_y8000_hangar512
cd build
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_SOLO=1 \
    ROGUESQ_M4_Y8000_WIDTH=512 \
    ./RogueSquadron64Recomp \
    > ../scratch/agent/s1872_m4_y8000_hangar512/run.log 2>&1 &
# watchdog; SIGKILL the process group; do not SIGTERM
```

Same-run positive controls (must fire before any H-* is selected):

- `[lle-force]` plus `[lle send_dl …] gate=attr exit=1`
- `[m4-y8000] mark flush-site` with `viw=512` (or a pre-hangar
  width, then a later `viw=512` summary)
- `[m4-y8000] mark entry` at VI 512
- last summary `n_flush > 0` while width is 512

Expected splits:

- H-clip-reject: `n_y8000_entry > 0` and `n_y8000_any == 0`
- H-zero-height-emit: `n_y8000_equal > 0`
- H-on-screen-emit: `n_y8000_mixed > 0`
- H-never-live: `n_flush > 0` and `n_y8000_entry == 0`
- UNEVALUABLE: no hangar-512 origin / no `n_flush` at 512 —
  do not promote attract-512 zeros

Parked until after this revisit: leftover `func_800F2208`
(`0x800F2208`, `0x108`) → companion/generated
`isVectorWithinConeAndRange`; TOML still leftover.
