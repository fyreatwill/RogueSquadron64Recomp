# NEXT work unit (resident-0C `L_1298→0x1DB0` provenance audit)

HYPOTHESIS-ID: m3-postsec2-lle-control-flow

The phase-safe s736 soak selected the TriGen relay: all 61 retained active
reset rows had `target=0x1DB0,line=615,ra=0x1088,resident=0x0C,l1298=1`.
Do one static, source/ROM-backed audit before adding another runtime counter.
Map resident id `0C` through its dispatch table entry and image source, then
compare its `L_1DB0` block with the main-image block and the documented 0x05
TriGen continuation behavior.

## Competing hypotheses

- **H-intended-resident0c-reset:** resident `0C` deliberately maps the relay
  to the `L_1DB0` continuation whose state reinitialisation is part of TriGen.
- **H-stale-main-image:** resident `0C` should dispatch a distinct overlay
  image, but the runtime executes the main/static `L_1DB0` block because the
  IMEM image was not installed or selected.
- **H-bad-table-entry:** the resident-`0C` dispatch-table entry itself maps
  this relay to `0x1DB0` when its ROM image/table maps it elsewhere.

## Discriminating measurement

Build a compact static table: resident-`0C` table slot, the ROM/IMEM bytes or
translated source that supply it, and the corresponding intended target. An
image/table target of `0x1DB0` with matching reset code selects
H-intended-resident0c-reset; a different resident image/table target selects
H-stale-main-image; an on-image table mismatch selects H-bad-table-entry.
The positive control is resident `04`, whose clip-overlay mapping is already
documented and must resolve to its known distinct `CLIP_*` routing.

## Commands

    rg -n -C 12 '0x153|0X153|0x76|0X76|resident|CLIP_|L_1298|L_1DB0' tools/fixup_factor5_ucode.py build/factor5_ucode/factor5_ucode_recompiled.c
    rg -n -C 8 '0x0C|0X0C|resident.*12|overlay.*12|0x76|0X76' factor5_rsp*.toml tools docs reference 2>/dev/null
    sed -n '1,220p' docs/F5-UCODE-REFERENCE.md
