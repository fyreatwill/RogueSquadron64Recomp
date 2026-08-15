# NEXT work unit (s1230)

HYPOTHESIS-ID: external-retail-entry-route

The s1229 installed Mupen64Plus 2.6.0 UI audit selected H2 for an external
command/reset route. Its source sequence is `CoreStartup`, `ROM_OPEN`, plugin
attach, optional `STATE_LOAD` only for `--savestate`, then `EXECUTE`; core ROM
open still loads EEPROM/SRAM according to ROM database/config.

Work unit: inspect the actual retail EEPROM file and the core's ROM-open
save-media path. Confirm file existence/size/content, identify whether it is a
formatted blank image, and map its filename/selected save type to this ROM.
Do not build, run, or write a target state.

Competing hypotheses and discriminator:
- H1: a nonblank retail EEPROM is loaded during `ROM_OPEN` and can explain the
  missing transition as persistent save-media state.
- H2: the EEPROM is missing/blank, or the existing file is not selected for
  this ROM; save-media state does not explain the missing transition.
- H3: the core's ROM database selects a different save type/path than the
  observed file, so the current oracle's save-media comparison is invalid.

Discriminator: compare the actual EEPROM bytes and size with the core's blank
EEPROM format, then verify the ROM database/save-path selection. Nonblank and
selected selects H1; blank/missing selects H2; a path/type mismatch selects H3.

Exact commands:
```
find "$HOME/Library/Application Support/Mupen64Plus/save" -maxdepth 1 -type f -print -exec stat -f '%N %z bytes' {} \\
  \\\;
xxd -g 1 "$HOME/Library/Application Support/Mupen64Plus/save/Star Wars - Rogue Squadron (U) (-47CAC4E2.eep" | head -20
rg -n -C 8 "open_eep_file|get_eeprom_path|ROM_SETTINGS\\.savetype|M64CMD_ROM_OPEN" \\
  /var/folders 2>/dev/null | rg "mupen64plus-bundle-src-2.6.0|open_eep_file|get_eeprom_path|ROM_SETTINGS.savetype|M64CMD_ROM_OPEN" | head -180
rg -n -i "rogue|squadron|47cac4e2|eeprom|savetype" \\
  /opt/homebrew/share/mupen64plus/mupen64plus.ini \\
  "$HOME/Library/Application Support/Mupen64Plus/mupen64plus.cfg"
```
