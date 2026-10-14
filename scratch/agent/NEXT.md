# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4874 result: the port walks synth 2x/VI because slots 1 and 2 of the VI-retrace callback table (0x8011A8A4) both hold 0x8009123C; retail holds one. Retail order at every reinit: dereg(synth) from the jalr at 0x80091EF4 (inside waitForMusyXAudioTaskDone) -> reapplyAudioConfig (0x8008EB5C) -> register. Port order: reapply registers first, dereg arrives later (variable delay).
Open: who calls the port's dereg and why it is late/absent before reapply (ra=0 in S4700_CB rows; no wait-entry row under ROGUESQ_LOG_M5_GATE_CONTRACT).
Hypotheses: (H-ORDER) the dereg path (musyxNoopStub -> waitForMusyXAudioTaskDone, gated by the audio gate byte / s4562 pause / pump patch) runs on the game thread after reapply because the gate byte is set late; (H-SKIP) the port never reaches the retail dereg site and the dereg we see is shutdown-path/other; (H-RACE) host-thread timing.
Discriminator (one build): in tools/fixup_game_funcs_vendored.py add, behind ROGUESQ_LOG_S4700_CB, g_rs64_last_guest_pc + a counter at entries of waitForMusyXAudioTaskDone (0x80091EB0), musyxNoopStub, reapplyAudioConfig (0x80091C88), and findAndZeroTableSlotMatching, logged with the VI ordinal; also patch the jalr at 0x80091EF4. Order of those rows per reinit vs retail (dereg, reapply, register) selects H-ORDER (wait-entry after reapply) / H-SKIP (never) / H-RACE (order varies run to run). Positive control: reapply entry must fire at each route edge.
Do NOT change dispatch or dereg semantics before the writer is named (rule 11). Reuse: scratch/agent/run_s4876_route.sh; oracle recipes in PORTING-STATE s4874.
