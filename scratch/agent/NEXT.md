# NEXT (s7522)
HYPOTHESIS-ID: rsp-imem-window-residency

First: fold s7521_fr_levels from SOAK-RESULTS if it ran (score 0 -> FR CLOSED 6 levels in CURRENT-TRUTH item 20; 1 -> read
scratch/s7521_fr_levels/out.txt LIVE rows: L1DB0-PATHA-UNDER-OVL0 means the overlay-0 placement difference went live (port runs
mtc0 DPC_START/END where hardware skips them: fix the route in tools/fixup_factor5_ucode.py together with the DPC model's start);
3 -> a ctl did not fire on some arm ([s7521-ctl] lines); 4 -> no [s7521-sum]).

Class FS = FR's gap: at EVERY port dispatch into a windowed IMEM address (0x12A0..0x15CF and 0x1DB0..0x1FFF, the dispatch switch
near main.c line 5860 and the splice gotos), is the code the port runs the image hardware has resident? Model the hardware window
contents from the IMEM DMA stream (src/rsp/s7521_ucode_watch.cpp already sees every IMEM DMA; add ovl28's restore as a modelled
DMA when the 0x28 route runs), and at each dispatch compare the port's chosen route (DMEM 0x153 + case) with the modelled image.
Hypotheses: H-canon (route == resident image every time), H-dead (mismatch only on paths whose bytes are equal across images),
H-live (port runs another overlay's code). Ctl: env forces DMEM 0x153 wrong for one dispatch (route != model must row).
Runs: L4 dd1 + L15 dd8 21:9 via tools/g1e_owner_quiet_arms.zsh (+ROGUESQ_G1E_PROBES=1), then a levels soak.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
