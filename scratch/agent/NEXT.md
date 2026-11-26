# NEXT (s7969)
HYPOTHESIS-ID: post-preset-class-ladder
s7968 closed class XF: on exFAT/FAT32 (fskit) save rename, flock and fsync behave as on APFS; only AppleDouble `._*` sidecars in
mods/ were opened as mods (now skipped, ROGUESQ_S7968_XF=0 = old). Gate S7968_XF, e2e tools/s7968_xf_e2e.zsh (makes its own images
under /tmp). Do not redo XF, CS (s7967), DI (s7966), RO (s7964), AN (s7963), PS (s7962), SD (s7961), DR (s7960), RD (s7959),
FW (s7958), CK (s7954), LC (s7953), TF (s7955), EV.
An src/ or lib/ edit needs the FULL sweep (`python3 -u tools/s7651_gate_sweep.py --jobs 2`, ~28 min: run it in the background).
0. `python3 tools/crash_reports.py --since 2026-11-26`. Fold any new SOAK-RESULTS lines.
1. Ladder 3c, new host class UE: the volume holding the game folder goes away mid-run (USB stick pulled, `diskutil eject`, or the
   stick's sleep). Follows XF: owners who copy to a stick will pull it.
   Hypotheses:
   - H-sigbus: the executable's pages are mapped from the vanished device; the next page-in SIGBUSes (crash report, no save flush).
     Expected and mostly unfixable, but measure it: time-to-death, and whether a crash report names it.
   - H-savefail: the exe survives (pages resident), but the next save write fails: does the game show the "Failed to write" dialog
     once, or spam it every save, or hang in the quit flush?
   - H-hang: a read/write on the dead mount blocks forever (EIO vs block) and the game freezes rather than failing.
   - H-moot.
   Discriminator: tools/s7968_xf_e2e.zsh's image setup (256 MB ExFAT image, private game copy, owner save COPIED). Arms, one game at a
   time, saving ON: (a) `hdiutil detach -force` at 10 s, watch 20 s more: alive/dead, signal, last stderr lines, crash report;
   (b) exe copied to /tmp but saves/ on the image (symlink, as s7967 did) so only the data volume vanishes: then trigger a save
   (how: grep s7429_save_quit.sh for the unforced-write recipe) and count "Failed to" lines and the quit-flush time after SIGTERM-free
   quit (Cmd-Q not available headless: use the existing ROGUESQ quit-flush path, grep "quit flush"). APFS image detach = control.
   Fix only what is ours (e.g. repeated dialogs, a hang); add a gate.
