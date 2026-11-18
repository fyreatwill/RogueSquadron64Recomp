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
Runtime witness in a SEPARATE working folder (copy build/ binary + ROM + a COPY of build/saves into scratch/s7595/w/; NEVER touch
build/saves, never clear ROGUESQ_NO_SAVE_WRITE in build/): arms chmod 0555 save dir, a 0-byte save file, a truncated save, a full
tmpfs-like small disk image (hdiutil create -size 1m) as save dir; record boot ok, save-write result lines, quit flush rc, and
whether the original save bytes survive (sha256 before/after). Positive control: a plant that forces update_save_file to fail once
must print the failure line. NOTE: NO_SAVE_WRITE gates update_save_file, so the write arms need it off INSIDE scratch/s7595/w only.
