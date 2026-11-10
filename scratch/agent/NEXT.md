# NEXT: owner reports first; otherwise finish the "player anim" pair, then LEAVE the rename thread
HYPOTHESIS-ID: generated-symbol-misnomer-fixes
Context (s7079): the mission "player HUD tracking" family was the controller-input layer (5 renames,
scratch/s7079/renames.tsv). setPlayerSlotPositionVec3 holds. Two names remain unchecked:
advancePlayerAnimationPhase 0x80062B04 (callers 0x80062818, 0x800AAE14, 0x800AEC34, 0x800AF448, 0x800AF460; it calls
activateTextSlotItemKeyframe) and getPlayerSlotAnimChannelCount 0x80063F70 (reads a0+1100).
Hypotheses: H-text (a0 is a text-slot item, so TextSlot names) vs H-player (a0 is the 672-byte player record
0x80137DB8 or a craft object). Discriminator: what each caller passes in a0 (trace back the lui/addiu or the load).
Disassembly: mips64-elf-objdump -d ../rogue_squadron64/build/roguesquadron.elf > /tmp/all.dis.
Method as s7079 (renames.tsv -> tools/apply_symbol_renames.py --dry-run then apply; fixup_preempt_point.py says 6;
cmake build; sed s7079->s7080 scratch/s7079/run.zsh and run it).
CHURN WARNING: s7077-s7079 were rename-only (read as no engineering change by the loop counter). After this pair,
close the misnomer thread and take an engineering rung (a code/tool change), not more renames.
