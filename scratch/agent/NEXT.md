# NEXT (s7975)
HYPOTHESIS-ID: post-preset-class-ladder
s7974 closed NS-2 (validated ROM kept in memory when the store fails; boots on a full volume; gate S7974_NS2).
Do not redo NS, NS-2, MP, SW, UE, XF, CS, DI, RO, AN, PS, SD, DR, RD, FW, CK, LC, TF, EV.

## Work unit: class RN — the ROM a real owner actually has (names, dumps, formats)
main.cpp ~15899 tries only 4 candidate names (rogue_squadron.z64, "rogue squadron.z64", RogueSquadron.z64, rs64.z64) and
DISCARDS every select_rom result except Good, then prints the same "Place your ... ROM named 'rogue_squadron.z64'" text.
Owners usually have a No-Intro name ("Star Wars - Rogue Squadron (USA).z64"), a .v64/.n64 byteswapped dump, a (Rev 1) / PAL
dump (IncorrectVersion / IncorrectRom), or a .zip.
Hypotheses (one e2e, arms = fixtures in a private game folder, no full image needed):
- H-silent: wrong version/region/format gets the generic "Place your ROM" text with no cause (validation error swallowed).
- H-byteswap-ok: .v64/.n64 content under a candidate name already boots (select_rom byteswaps) -> moot for that arm.
- H-name: a correct ROM under the No-Intro name is never tried -> prompt with the right file present.
Arms: ctl (rogue_squadron.z64, boots), noIntro (No-Intro .z64 name only), v64 (byteswapped bytes as rogue_squadron.v64 and as
rogue_squadron.z64), wrongver (header-patched copy: internal name kept, 1 byte changed -> IncorrectVersion), notrom (zeros),
zip (zipped ROM). Score: boot marker [si-thr]/[dpc-fwd] (s7974 e2e), prompt text, and whether the stated cause matches.
Fix candidates: scan the folder for *.z64/*.v64/*.n64 (bounded, size 8-64 MB) after the fixed names; print the select_rom
error per candidate ("wrong version: this port needs USA v1.0"); keep the old text as the last resort. Mutant env for old path.
## Commands
1. Copy tools/s7974_ns2_e2e.zsh as tools/s7975_rn_e2e.zsh (plain temp dir instead of hdiutil images); pre-fix exe for old arm.
2. Gate tools/s7975_rn_gate.py + sweep row S7975_RN; full sweep --jobs 2 after the last game run.
