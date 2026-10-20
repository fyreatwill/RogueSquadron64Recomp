Single next work unit (s5622): fold s5620_nopoke_{f,g} (grep '\[hudbit\|\[cco\]' run.log), THEN add a ROGUESQ_LOG_HUDBIT log in setObjectiveBoolean (0x800C7540, tools/apply_s5618_hudbit_log.py style, in fixup replay list) printing id+value for ids 0x64/0x6D and a positive control (log ALL ids for first 20 calls). Rebuild, queue 2 unpoked soaks.
Outcomes: 0x64/0x6D set before hudbit4 => find the caller of that setObjectiveBoolean (script vs level code); never set yet bit 4 fires => other writer of flagword (watch 0x8010C9E0 write PC). All-ids control must fire or the run is void.
Static fact (s5621): lv2 calls setHudEnableBit4 only if objective boolean 0x64/0x6D == 1.
HYPOTHESIS-ID: m6-mission-endurance
