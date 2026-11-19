# NEXT (s7613)
HYPOTHESIS-ID: host-static-of-host-pointer

Class RG closed s7612 (tools/s7612_rg_census.py --controls --witness: 242 candidates 0 open, R1-R7, controls 8/8, witness
PASS from the s7103/s7108 chase logs, H-clean). Its declared scope gap is the next class.
Class HP: a HOST pointer into guest RAM (TO_PTR(type, x), rdram + off, &rdram[...], reinterpret_cast<...>(rdram + ...),
OSThread* / OSMesgQueue* / OSIoMesg* views, PTR() conversions) stored in static / thread_local / file-scope / member-of-static
storage and dereferenced on a LATER call. Stale when the guest frees/reuses the object, a new level/overlay rewrites the
region, or the guest address changes while the host keeps the old view. Neither SN (token set lacks TO_PTR) nor RG (only
when the argument is a register) catches these. Rough size: ~17 static `T*` declarations in src + librecomp + ultramodern
(grep -rnE '^\s*(static|thread_local)[^;(]*\*\s*\w+' minus const char* / FILE*) plus containers of pointers.
Method: extend tools/s7611_sn_scan.py's taint set once more via its taint_re arg (new token set: TO_PTR, PTR\(, &rdram\[,
rdram \+, reinterpret_cast<[^>]*\*>\(rdram) -> tools/s7613_hp_scan.py; also enumerate every static/thread_local pointer
declaration directly (declaration census, not only stores) so a pointer assigned in an initializer is not missed.
tools/s7613_hp_census.py: rows + proof regexes, classes: base (the rdram base itself), fresh (set+used in one call: reuse the
s7612 pair_paths contract), keyed (re-derived from the live guest address before use), event, gated, BAD.
Hypotheses: H-clean, H-bad-gated, H-bad-live.
Controls: (1) plant a static OSMesgQueue* from TO_PTR used in a later call -> OPEN; (2) drop a row -> OPEN; (3) plant a
pointer declared with an initializer (static T* p = TO_PTR(...)) -> OPEN via the declaration census; (4) break one fresh
contract -> OPEN.
Second source: a runtime witness from existing logs if any default-on unit logs both the guest address and the host view;
else a compiled witness (tools/s7613_hp_witness.cpp) driving the real snippet with the guest object moved between calls.
Never touch build/saves; never clear ROGUESQ_NO_SAVE_WRITE.
