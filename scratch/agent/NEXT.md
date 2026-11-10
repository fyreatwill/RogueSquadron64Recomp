# NEXT: owner reports first; otherwise misnomer check of the mission-overlay "player slot" trio
HYPOTHESIS-ID: generated-symbol-misnomer-fixes
Context (s7078): the main-segment "player slot" family (table 0x8009FC10) is the 12-entry TEXT/FONT slot table;
25 PlayerSlot/PlayerAnim names became TextSlot (scratch/s7078/renames.tsv). Three mission-overlay names still say
"player slot" but do NOT reference 0x8009FC10: clearPlayerSlotHudTracking 0x800BEE18, loadPlayerSlotHudPreset
0x800BF264 (calls the former), setPlayerSlotPositionVec3 0x800B40F0.
Hypotheses: H-player (they index a real player/wingman array, names hold) vs H-other (HUD/text/camera slot or generic
object, misnomer). Discriminator: the base each indexes (lui/addiu pairs), every caller and its args (jal map of
/tmp-style objdump of .ovl.mission; regenerate with mips64-elf-objdump -d -j .ovl.mission
../rogue_squadron64/build/roguesquadron.elf), and what the stored fields are read by.
Method: same as s7078 (scratch/s7078/renames.tsv -> tools/apply_symbol_renames.py --dry-run, then apply;
fixup_preempt_point.py must still say 6; cmake build; sed s7078->s7079 of scratch/s7078/run.zsh and run it).
Also unresolved from s7078: advancePlayerAnimationPhase 0x80062B04 (calls activateTextSlotItemKeyframe, does not
index the table itself) and getPlayerSlotAnimChannelCount 0x80063F70 (reads a0+1100, not the table) - check their
callers' a0 before renaming.
If all hold: close the misnomer thread and take the next G rung.
