# NEXT: are the -38 cell bytes an in-table field
HYPOTHESIS-ID: g1c-span-reject-predicate

s6515 selected H-both. On dd4 EMPTY, every logged return clears through both
`0x80042D8C` (span -128 < cell+3 -38) and `0x80042DA4` (cell+4 about -38 <
plane 127). s1 is 42-64% of those clears. dd1 EMPTY and both arms' nonempty
returns clear only through the first compare, with cell+3 109. The cell
record that supplies +3/+4 is the open input.

One Debug build, one pinned dd1/dd4 run. At the `0x80042D6C` index load
(`lhu` from s2, masked `0x1FFF`; cell = `[t0+4] + index*30`), log the index,
table base, cell address, and bytes +0..+5 for s0 clears, s1 clears, and
passes. Keep `[span-base]`. Do not add a guard or change behavior.

- H-legit-outer: indices sit inside the table and +3/+4 are stable per index.
  dd4 EMPTY bytes are about -38; dd1 s0 bytes are 109.
- H-bad-index: the cell address falls outside the table, so -38 is not a
  cell field.
- H-shared-template: one index supplies the -38 bytes for the dd4 EMPTY clears.

A null is invalid unless `[span-base]` fires in both arms, nonempty rows
still show `npass>0`, and the logged +3 byte reproduces -38 on dd4 EMPTY and
109 on dd1 s0.

Commands:

    python3 tools/apply_s6516_cell_record.py
    DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s6516_cell_record.sh
