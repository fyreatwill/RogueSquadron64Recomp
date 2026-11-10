# NEXT: owner reports first; otherwise finish the menu-block misnomer check 0x800B2A98-0x800B4618
HYPOTHESIS-ID: generated-symbol-misnomer-fixes
Context (s7074): 0x800B4020-0x800B42D4 is the menu screen-fade quad family (renamed); 0x800CC850 is the live menu
element count. Fast method (s7074): objdump the ELF, NOT the RecompiledFuncs bodies (diag noise):
  mips64-elf-objdump -d -j .ovl.menu --start-address=0x... --stop-address=0x... ../rogue_squadron64/build/roguesquadron.elf
  (ELF symbols carry the OLD names; current names are in ../rogue_squadron64/symbol_files/menu_overlay.txt.)
  Strings: file off = va - 0x800A5130 + 0x10b410.
Unit, remaining candidates in this block:
 - loadNamedTextureDescriptor 0x800B2D50: sprintf "backdrop/%s" + load_asset + zmemcpy + registerHmtTextureInTable.
   H-sync-backdrop (a synchronous backdrop/named image load) vs H-generic (generic named texture). Discriminator: the
   asset path prefix it formats for every caller (buildHudAmmoReadout, createMenuTextLabels, runMenuShipSelectScreen...).
 - allocFormatTextElement 0x800B2A98 (rs_malloc+memset, element count 0x800CC850): likely another menu element ctor.
 - copyMorphTargetVertices 0x800B438C: copies u16 array a1->+20[a2+i] into a0->+20[i] and a0->+0xC->+0xC[i], count a0->+8.
 - spawnHudReticleAtMeshBounds / positionHudSpriteOffset / createHudSpritePair / layoutHudSpriteScreenRect 0x800B448C-0x800B4618
   live in the MENU overlay: H-hud (really HUD) vs H-menu-sprite. Discriminator: callers (menuControllerInput, spawnMenuListItemSprite).
If misnomer: rename via scratch/s7074/renames.tsv recipe (files.txt, before/after counts, perl \b over live tree + symbol_files +
syms toml + tools/*.py), fixup_preempt_point.py must still say 6, rebuild, scratch/s7074/run.zsh (L6 dd1 4:3 NOCAP + 1 s samples).
If all hold: close the menu-block misnomer thread and take the next G rung.
