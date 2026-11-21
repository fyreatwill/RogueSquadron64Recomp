# NEXT (s7772)
HYPOTHESIS-ID: ovl-aliased-lookup-audit
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Unit (offline first, one bounded audit): s7771 found 82 .text jal sites whose target address is a function START in one overlay
and MID-FUNCTION (or start of a different function) in another (list: `python3 tools/s7771_jal_target_census.py` start_ovl rows;
e.g. mainGameLoop+0xEC -> 0x800C58A0 = menu start / mission interior; loadDatFile+0x864 -> 0x800AE98C cinematic-only start).
N64Recomp emits LOOKUP_FUNC for them. Question: does the runtime lookup resolve by the overlay currently loaded at that VMA
(hardware semantics), or by a first-registered / last-registered table entry?
Hypotheses: H-loaded (librecomp section_addresses + loaded-section table, correct), H-first (a static vram->func map: one overlay
wins regardless of what is loaded = wrong body when another overlay is mapped), H-abort (lookup of an address not a start in the
loaded overlay aborts; matches hardware only if the call never happens with that overlay mapped).
Discriminator: read lib/N64ModernRuntime librecomp overlays.cpp get_function / LOOKUP_FUNC path (read only; no lib edits without
export.sh), then one positive control offline if possible (unit test calling the lookup for 0x800C58A0 with menu vs mission
marked loaded). Each mainGameLoop site: confirm the mode branch guarding it matches the overlay where the target is a start.
Outcome: H-loaded + guards consistent -> class CLOSED; otherwise fix in librecomp (export.sh + commit).
