# NEXT: owner reports first; otherwise misnomer check of the menu-overlay tile-wipe owners
HYPOTHESIS-ID: generated-symbol-misnomer-fixes
Context (s7076): block 0x800B80B4-0x800BE3E8 closed (20 renames; it is pilot-select / settings UI). Their callers still look
misnamed: allocCraftPreviewEffectObject 0x800C4DB8 and initCraftPreviewEffectWithRandom 0x800C4DF0 own the image tile-wipe
object (allocMenuImageTileWipeMesh / buildMenuImageTileWipeMesh), and spawnProjectileObject 0x800B42D4 creates the 0x800CF10C
image element. Also check the neighbours in 0x800C4B90-0x800C4F00 (loadControllerModel, loadHelmetModel).
Hypotheses per name: H-menu-wipe (they create/start the menu image tile wipe) vs H-preview (a real craft preview effect,
e.g. the hangar ship) vs H-projectile (no: menu overlay has no weapons). Discriminator: body (sizes 4988 / tile arrays /
rand&1 direction), menu-only callers, what the produced object is passed to.
Method: python3 tools/s7075_fnsum.py <start> <stop> [--asm]; callers via the .ovl.menu jal map over scratch/s7075/menu.asm
(beware: objdump labels inside menu.asm can be MISSION overlay symbols at shared addresses; take function starts from
../rogue_squadron64/symbol_files/menu_overlay.txt).
If misnomer: write scratch/s7077/renames.tsv, python3 tools/apply_symbol_renames.py scratch/s7077/renames.tsv --dry-run, then
apply; tools/fixup_preempt_point.py ../N64Recomp/RecompiledFuncs must still say 6; rebuild; sed s7076->s7077 of
scratch/s7076/run.zsh and run it (L6 dd1 4:3 NOCAP + 1 s samples).
If all hold: close the menu-overlay misnomer thread and take the next G rung.
