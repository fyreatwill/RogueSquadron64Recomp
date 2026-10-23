# NEXT: fold m6_lvl1_hold660_r3, m6_lvl3_hold660, m6_lvl6_hold660 verdicts
HYPOTHESIS-ID: g4-mission-soaks
Read SOAK-RESULTS.md tail. Any crashlines>0 / vi_stalls30s>0 / alive_at_end=0: capture lldb backtrace, name writer, root-cause. All clean: queue lvl2,4,5,7,8,9 holds (same recipe), then secondary: title-boot plume SIGSEGV si_addr=0x58 loop under lldb.
