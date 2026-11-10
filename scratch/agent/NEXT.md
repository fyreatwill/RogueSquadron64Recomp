# NEXT: owner reports first; otherwise misnomer check of the main-segment "player slot" anim family
HYPOTHESIS-ID: generated-symbol-misnomer-fixes
Context (s7077): menu-overlay misnomer thread CLOSED. animateCraftSelectFlags (menu 0x800C4C8C) loops over items and calls
setPlayerSlotAnimationFlag 0x80063CFC, samplePlayerAnimChannel 0x80061F34, activateAnimationKeyframe 0x80061C74 and
getPlayerSlotFieldAt34 0x80063C3C with a0=5. Menus have no player, so "player slot" may be a generic anim-channel/HMT slot table.
Hypotheses: H-generic (slot = generic animation/HMT channel index, used by menu + mission alike) vs H-player (slot 0..n
really are player/wingman entities and 5 is a menu-reserved one). Discriminator: the table base and stride the functions
index, every caller's a0 values (grep jal over main + both overlays), and what is stored at slot+0x34.
Method: python3 tools/s7075_fnsum.py <start> <stop> [--asm] over 0x80061C00-0x80063D80; symbols from
../rogue_squadron64/symbol_files/*.txt. If misnomer: scratch/s7078/renames.tsv, tools/apply_symbol_renames.py --dry-run then
apply; fixup_preempt_point.py must still say 6; rebuild; sed s7077->s7078 of scratch/s7077/run.zsh and run it.
If all hold: close the misnomer thread and take the next G rung.
