# NEXT: join framebuffer dumps to flight phase, then dd1-vs-dd8 sheet
HYPOTHESIS-ID: g1c-dd8-limit

Single work unit: write one offline joiner that maps each `[fbdump] n=...`
record in the s6468p dd1/dd8 run logs to the surrounding VI width/origin and
flight-phase records, then select only rows with origin `0x00690400`, width
512, and a common phase-relative flight window. Generate a new owner sheet and
score terrain fraction plus HUD presence from those joined rows.

Competing outcomes:

- dd8 has more legitimate distant terrain while craft/HUD stay present: H-terrain.
- dd8 has missing/invalid far geometry or a crash in the matched window:
  H-address-limit; do not mitigate until the writer/value is identified.
- matched dd1/dd8 frames remain unavailable or their scores agree after the
  join: the current capture still cannot discriminate; change the capture
  phase key before interpreting the draw-distance effect.

Positive controls: the joiner must report nonzero matched flight dumps for both
arms, and the existing framebuffer-hash/terrain controls must fire. Equal dump
ordinal alone is not a key. Exact starting points are
`scratch/agent/m6/g1_lvl1s6468p_d1` and
`scratch/agent/m6/g1_lvl1s6468p_d8`; use the fixed position-pin build recipe
in `scratch/agent/s6468_dd8_sheet.sh` only if a fresh capture is required.
