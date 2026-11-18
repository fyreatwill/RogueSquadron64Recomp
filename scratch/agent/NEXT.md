# NEXT (s7595)
HYPOTHESIS-ID: save-io-failure-census

Class SG closed s7594 (16 signal sites 0 open; HUP/QUIT/PIPE now take the flushed quit path).
Class SV = what the game does when the save file cannot be read or written: save dir missing / read-only, disk full, file
truncated or wrong size, rename failure in recomp::finalize_output_file_with_backup, a .bak but no main file. pi.cpp
update_save_file() calls ultramodern::error_handling::message_box on the SAVING THREAD on failure (does it block that thread
forever, or the guest, or show nothing fullscreen?), read_save_file() on a short/garbage file, change_save_file swap.
Census (offline, tools/s7595_sv_census.py --controls): every fopen/ofstream/ifstream/rename/remove/filesystem:: call on the save
path in librecomp/ultramodern/src, per site: error checked?, what happens on failure (message, retry, silent, abort, block).
Hypotheses: H-clean (every failure is reported once and play continues; the existing save is never destroyed), H-destroy (a
failed write leaves neither main nor .bak readable), H-block (message_box from the saving thread stalls quit/flush or the game).
Runtime witness: OWNER SAVE RULE - never clear ROGUESQ_NO_SAVE_WRITE anywhere, never touch build/saves. So runtime arms cover
the READ path only (a copied game folder scratch/s7595/w/ with its own save COPY: 0-byte file, truncated file, garbage, missing
dir, read-only dir; record boot ok + read-result lines + sha256 of the copy before/after). The WRITE path is tested offline: a small
host harness (scratch/s7595/wtest.cpp) that calls recomp::finalize_output_file_with_backup's logic on temp files under a 1 MB
hdiutil disk image (disk full) and a 0555 dir, checking main/.bak survive. Positive control: a planted failure must print the
failure line / leave the original bytes intact detectably.
