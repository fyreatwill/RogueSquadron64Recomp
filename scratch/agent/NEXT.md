# NEXT: fold m6_lvl{5,6,7,8,9}_hold660 and s5589_plume_lldb_s5982_{a,b} verdicts
HYPOTHESIS-ID: g4-mission-soaks
Read SOAK-RESULTS.md tail. Any crashlines>0 / vi_stalls30s>0 / alive_at_end=0: capture lldb backtrace, name writer, root-cause. All clean: secondary task, loop title boots under lldb until the si_addr=0x58 plume SIGSEGV recurs and read the real backtrace.
