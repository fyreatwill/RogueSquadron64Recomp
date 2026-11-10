# NEXT: owner reports first; otherwise misnomer check of the menu-overlay "player craft" block 0x800B80B4-0x800BE3E8
HYPOTHESIS-ID: generated-symbol-misnomer-fixes
Context (s7075): block 0x800B2630-0x800B4618 closed. Names in 0x800B80B4-0x800BE3E8 (menu_overlay.txt lines ~549-575) read
like flight code (playerVwingMainUpdate, integrateTieInterceptorPhysics, spawnTieInterceptorParticles, handleNabooFlightInput,
handleNabooActionButtons, computeNabooBankingOrientation, initVwingHudAndSlotState, updateVwingTrailGeometry) but live in the
MENU overlay, so they are most likely the hangar / craft-select model viewer animations.
Hypotheses per name: H-viewer (hangar craft model animation: keyframes, material/thruster flicker, rotation by stick) vs
H-flight (real flight logic duplicated into the menu, e.g. a demo/attract flight). Discriminator: menu-overlay callers
(dispatch table? runMenuShipSelectScreen?), controller reads (stick -> rotate model vs -> craft velocity), and calls into
the mission-side physics/weapon code (none expected under H-viewer).
Method: python3 tools/s7075_fnsum.py 0x800B80B4 0x800BE3E8 [--asm]; callers:
  mips64-elf-objdump -d -j .ovl.menu ../rogue_squadron64/build/roguesquadron.elf > scratch/s7076/menu.asm and awk for "jal <addr>"
  (restrict to .ovl.menu: the 3 overlays share 0x800A5130).
If misnomer: rename via the scratch/s7075 recipe (renames.tsv, files.txt, cnt.py before/after, regex \b over live
RecompiledFuncs + symbol_files + syms toml + tools/*.py), fixup_preempt_point.py must still say 6, rebuild,
scratch/s7075/run.zsh with s7076 (L6 dd1 4:3 NOCAP + 1 s samples). Note L6 boots through the hangar? samples need the renamed
fns: if none show, add a hangar-scroll arm (scratch/s6995/arm.zsh) as the positive control.
If all hold: close the menu-overlay misnomer thread and take the next G rung.
