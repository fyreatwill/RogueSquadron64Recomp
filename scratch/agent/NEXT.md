# NEXT (s7968)
HYPOTHESIS-ID: post-preset-class-ladder
s7967 closed class CS: an iCloud placeholder save that cannot be read now means "no save this session", not "empty save". Online
eviction costs only ~1 s. Gate S7967_CS, e2e tools/s7967_cs_e2e.zsh (it uploads a COPY of the save to a probe folder in the owner's
iCloud and deletes it after). Do not redo CS, DI (s7966), RO (s7964), AN (s7963), PS (s7962), SD (s7961), DR (s7960), RD (s7959),
FW (s7958), CK (s7954), LC (s7953), TF (s7955), EV.
An src/ or lib/ edit needs the FULL sweep (`python3 -u tools/s7651_gate_sweep.py --jobs 2`, ~28 min: run it in the background).
0. `python3 tools/crash_reports.py --since 2026-11-26`. Fold any new SOAK-RESULTS lines.
1. Ladder 3c, new host class XF: the game folder is on a non-APFS volume, such as an exFAT/FAT32 USB stick or an SMB share. Owners
   often copy games to a stick.
   Hypotheses:
   - H-rename: rename-over-existing is not atomic, or fails on FAT/exFAT. Then finalize_output_file_with_backup fails, or leaves
     neither the file nor the .bak.
   - H-flock: flock returns ENOTSUP on msdos/exfat/smbfs. Then the s7966 lock reads "unavailable", which is fine, or "busy", which
     would make every launch run no-save.
   - H-fsync: F_FULLFSYNC is not supported, and the s7429 finalize path errors.
   - H-xattr: AppleDouble `._` files appear next to saves/ and controls.json, and a loader trips on them.
   - H-moot.
   Discriminator, all offline and no game needed first: `hdiutil create -size 64m -fs ExFAT` and `-fs MS-DOS` (FAT32) images, mount
   them, then run tools/s7967_cs/harness.cpp write/read cycles (pi.cpp save sequence) and tools/s7966_di/hdr_test.cpp (lock +
   atomic writer) on each. The APFS image is the control. Then one e2e boot per FS from a private game copy on the image, checking
   the [s7964-ro] / [s7966-di] lines and that a save written with saving on survives a SIGKILL + relaunch. Fix what breaks, and add a
   gate.
