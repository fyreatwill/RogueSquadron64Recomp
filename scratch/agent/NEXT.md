# NEXT (s7974)
HYPOTHESIS-ID: post-preset-class-ladder
s7973 was the maintenance iteration (CURRENT-TRUTH 26 KB, backlog item 14 = this unit). Run this unit now.
s7972 closed class NS (full data volume: writers fail cleanly) and fixed controls.json/audio_device.txt following the s7969
relocated exe copy (gate S7972_NS). Do not redo NS, MP, SW, UE, XF, CS, DI, RO, AN, PS, SD, DR, RD, FW, CK, LC, TF, EV.

## Work unit: NS-2 fresh install on a full volume (ROM store fails -> misleading "Place your ROM", no boot)
s7972 boot arm (scratch/s7972/new_boot.log): ROM given as rogue_squadron.z64 only, volume full before launch ->
"[s7357-io] storing the ROM copy failed", "[ROM] Imported rogue_squadron.z64", then "[ROM] Place your Rogue Squadron ... ROM
named 'rogue_squadron.z64' next to the executable and restart." while that file IS there. Game sits at the prompt.
Hypotheses:
- H-store-required: the boot path loads the ROM only from the stored copy (config_path / stored_filename), so a failed store
  = no ROM, whatever validate said. Outcome: grep recomp.cpp load path; booting works when the store is skipped via a mutant.
- H-message: the "Place your ROM" text is chosen without knowing the store failed (wrong cause shown to the user).
Fix candidates: boot from the validated in-memory ROM when the store fails (s7357 comment already claims this) and say once
"could not store the ROM copy (disk full): running from rogue_squadron.z64"; or a clear disk-full message. Prefer booting.
Positive control: same image NOT full -> boots (stored copy written); mutant env restoring the old path -> prompt.
## Commands
1. Read lib/N64ModernRuntime/librecomp/src/recomp.cpp around validate (line ~436 write_file) and the caller that prints
   "[ROM] Imported" / "Place your" (src/main). Edits under lib/ -> ./submodule-patches/export.sh + commit.
2. Extend tools/s7972_ns_e2e.zsh boot arms (or a new s7973 e2e): boot must reach [phase] vi_width>0 / gfx tasks on the full
   image, and on the not-full control; old exe must show the prompt.
3. Gate row (extend S7972_NS or a new S7973 row), full sweep --jobs 2 after the last game run.
