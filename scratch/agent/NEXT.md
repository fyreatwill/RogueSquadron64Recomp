# NEXT (s7967)
HYPOTHESIS-ID: post-preset-class-ladder
s7966 closed class DI (two instances: per-pid save/atomic temps + flock single-instance guard, second copy runs no-save; gate S7966_DI,
e2e tools/s7966_di_e2e.zsh). Do not redo DI, RO (s7964), AN (s7963), PS (s7962), SD (s7961), DR (s7960), RD (s7959), FW (s7958),
CK (s7954), LC (s7953), TF (s7955), EV.
An src/ edit needs the FULL sweep (`python3 -u tools/s7651_gate_sweep.py --jobs 2`, ~28 min: run it in the background).
0. `python3 tools/crash_reports.py --since 2026-11-26`; fold new SOAK-RESULTS lines.
1. Ladder 3c, new host class CS (game folder inside a cloud-synced folder: iCloud Desktop & Documents, Dropbox, OneDrive).
   librecomp's own save-failure dialog already blames "Dropbox or similar", and the owner's tree lives under ~/Documents.
   Hypotheses: H-evict (iCloud "Optimize Mac Storage" evicts the ROM/save to a dataless placeholder; first open blocks on a download
   or fails EDEADLK/ETIMEDOUT offline -> boot hang or zero-filled save), H-conflict (the sync client sees the rename-over and writes
   "rs64.n64.us.1.0 2.bin" conflict copies, or reverts the save from another Mac), H-temp-upload (our per-pid .temp.<pid> /
   .bak.temp.<pid> / .rs64_instance.lock get uploaded and litter other machines), H-moot (nothing breaks).
   Discriminator, offline first: is ~/Documents iCloud-managed on this Mac (`brctl status`, `ls -lO@` for com.apple.fileprovider /
   SF_DATALESS flags on build/)? Then a harness that opens a dataless file (create one with `brctl evict <file>` on a COPY under an
   iCloud folder, never the owner's save) through open_input_file_with_backup and reports bytes/errno/latency; control = the same copy
   materialised. If no sync client is active here, the class is H-moot for this host: record that with the measurement and write the
   one-line owner note (README) about keeping the game folder out of synced folders if evicted reads are shown to fail.
