# NEXT (s7610)
HYPOTHESIS-ID: guest-code-address-keyed-host-cache

Class MK closed s7609 (tools/s7609_mk_census.py --controls --witness: 96 lines, 0 open, controls 4/4, witness PASS, H-clean).
Next idiom class OV: host caches keyed by a GUEST CODE address (vram / rom offset / section index) that survive the guest
loading different code at that address (overlay load, osPiStartDma of code into RAM, copyToRAM s5712, osInvalICache).
Candidates: librecomp overlays.cpp (func_map, code_sections_by_rom, manual_patch_symbols_by_vram, section_addresses /
loaded sections, the s7 prevbad checker), get_function / LOOKUP_FUNC paths, any src/ cache of recompiled-function pointers
by vram (jump tables, rs64 dispatch caches, s7535/s7521 ucode watch caches keyed by IMEM/DMEM address), and RSP ucode
caches keyed by text address (rsp.cpp: ucode selection by task->t.ucode).
First boring check: does RS64 load any code overlay at runtime at all (grep load_overlays / unload_overlays call counts,
osInvalICache stubs, section table size)? If it never does, OV degenerates to the ucode-cache half.
Classify every site: refreshed-on-load (load/unload path updates it), static (code never moves), diag-gated, BAD
(default-path dispatch reads a stale entry after new code lands).
Hypotheses: H-clean, H-bad-gated, H-bad-live.
Tool tools/s7610_ov_census.py --controls: (1) plant a vram-keyed function-pointer cache with no invalidation -> OPEN;
(2) drop a row -> OPEN; (3) remove the unload path's map erase -> OPEN; (4) plant a ucode cache keyed by text address with
no content hash -> OPEN. Second source: runtime witness from an existing log (overlay load/unload lines, or [s7521] ucode
rows showing one text address with two contents) or a compiled witness.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
