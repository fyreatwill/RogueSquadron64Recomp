# Next work unit

HYPOTHESIS-ID: H-alloc-window-sched-switch

s4710: retail (boot/attract, 180 s) performs exactly ONE allocateSongChannelArray call (count 20, base 0x80169460, ra 0x8009193c); no count-32 alloc observed. Port's first alloc matches.
Open: who calls allocateSongChannelArray with count 32 in the PORT, and when? Retail cannot answer past attract (oracle does not reach hangar).

Unit: regen with s1927 slot-alloc patch (fixup_game_funcs_vendored.py ~35322 is present in source but NOT in the current binary; check why: `grep -n "s1927" tools/fixup_game_funcs_vendored.py`), run port to hangar with ROGUESQ_LOG_VI_CALLERS=1 and log every slot-alloc (old/new/count + ra). Discriminator: ra of the count-32 call and whether it follows a song start that retail issues too.
Scripts: scratch/agent/s4709/{run.sh,port.sh}. Avoid dumping oracle stdout into context (redirect to file via script).
