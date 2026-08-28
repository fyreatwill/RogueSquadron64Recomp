# Session 3062 generated-symbol rename

Candidate: `0x800C63C0`, selected from the unresolved project-TOML
placeholder set after the `0x80017B48` neighborhood was already synchronized.

Result: exact identity confirmed and the stale project symbol was renamed to
`getAvailableShipsForLevel`. The rename table now also carries the two
already-confirmed semantic identities `rs_crc32` (`0x800824F8`) and
`setHudSecondaryWeaponInfo` (`0x800BFDC4`) so a regenerated placeholder is
renamed in the same bounded pass.

## Six-surface comparison

1. Companion symbol files: `main_overlay.txt` maps `0x800C63C0` to
   `getAvailableShipsForLevel`; the mission-overlay map independently gives
   the same identity and describes it as returning the available ships for a
   level.
2. Generated body: the current generated snapshot defines
   `getAvailableShipsForLevel` at `0x800C63C0`, with extent `0xA8` and a
   table-based available-craft result.
3. Callers: generated callsites invoke the semantic body from the hangar and
   mission-selection paths; the adjacent `0x800C6234` sibling remains
   `getAvailableShipsForLevelAlt`.
4. Generated header: `funcs.h` declares `getAvailableShipsForLevel`.
5. Overlay registration: `recomp_overlays.inl` registers the same semantic
   symbol at the `0x800C63C0` overlay offset and `0xA8` size.
6. Project TOML: the stale `func_800C63C0` entry is now
   `getAvailableShipsForLevel` at the same VRAM and size. The menu overlay's
   separate duplicate address remains `getAvailablePlayerCraftFlagsIgnoreUnlocks`.

## Hypothesis result

`H-ExactIdentity` selected. `H-BoundaryOnly` and `H-MappingDrift` are rejected
for this candidate. The committed change is regeneration-safe: the project
TOML and rename tool now agree, and the rename tool's batch includes the two
previously confirmed semantic mappings as controls.
