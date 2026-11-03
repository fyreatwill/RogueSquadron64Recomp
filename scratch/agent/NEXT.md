# NEXT: FPS60 frame-locked tick counters - the REST of the class (beyond the s6820 despawn grace)
HYPOTHESIS-ID: g3-fps60-tick-timers

State (s6820): out-of-range despawn grace (24 handlers, 21 ticks) fixed under FPS60 (tools/fixup_fps60_despawn.py);
TIE re-create 41 VI vs 30 Hz 40, off arm 20. Seeds 2/3 queued (soak_queue/s6820_despawn_s2/s3).
First: fold SOAK-RESULTS s6820_despawn_s2/s3: `python3 tools/g3_spawn_bt.py scratch/s6820/b60fix_s{2,3}.rand.txt
scratch/s6820/b60nodsp_s{2,3}.rand.txt` -> expect TIE re-create dVI ~41 (fix) vs 20 (off) on both seeds. If not, reopen.
Step 1 (offline, ONE pass): enumerate every OTHER per-object integer tick counter in the per-tick NPC/projectile/HUD
update functions: load (lbu/lb/lhu/lh/lw) -> addiu +-1 -> store same field -> compare (slti/sltiu/beq/bne vs constant or
vs 0) within ~8 instructions, excluding the 24 s6820 sites (tag "s6820 fps60 despawn"). s6820 scan already saw
npcPowerGeneratorUpdate 0x80077D44/88 (stack, slti 8 = loop index, likely not a timer), tickHudInstanceTargetingAndSpawns
0x800FD0E8 (slti 2), highScoreBubbleSort (loop). Classify each: loop index (ignore) / per-tick timer (frame-locked) /
event counter. Script it as tools/g3_tick_counter_audit.py so the table is reproducible.
Hypotheses for what remains:
  H-none: the despawn grace was the only gameplay-relevant tick timer -> close the class with the table.
  H-more: other per-tick timers (fire cooldowns, AI state durations, HUD blink) exist -> fix them with the same
    rs64_tick_dt scaling (reuse rs64_despawn_ticks-style helper), one build, a30 / b60fix / b60off arms on lvl14 s1.
Discriminator: the audit table; a fix arm must show the timer's period in game seconds equal to 30 Hz.
