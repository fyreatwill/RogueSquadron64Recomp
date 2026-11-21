# NEXT (s7773)
HYPOTHESIS-ID: ovl-fnptr-alias-audit
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Unit (offline, one bounded idiom-class audit; sibling of s7772): function-pointer WORDS (and lui+addiu/ori pairs) whose value is
a function start in an overlay (.ovl.mission/menu/cinematic, shared VMA from 0x800A5130), consumed by jalr.
Risk: a pointer stored in an always-resident table (.data/.bss of .text, or the heap) survives an overlay swap; after the swap
get_function either aborts (address not a start in the new overlay: loud) or, if the address IS a start in the new overlay,
silently runs the new overlay's function (hardware would do the same, so only a retail bug - but a port-only path if our swap
order differs from hardware).
Hypotheses: H-local (every such pointer lives in the overlay's own data and dies with it), H-resident-safe (resident pointers
exist but are re-written on each overlay load before use), H-stale (a resident pointer can outlive its overlay).
Discriminator: extend tools/s7772_ovl_lookup_audit.py (or a new s7773 tool) to enumerate (a) raw 32-bit words in every non-code
and code section equal to an overlay function start, (b) lui/addiu|ori pairs forming one, each tagged by the section holding it
(own overlay vs resident) and, for resident ones, whether the target address is a start in more than one overlay (silent case).
Controls: a planted resident word equal to 0x800C58A0 must be listed resident/unique; a known overlay-local table entry listed
local. Runtime side: [s7520] kind= rows already flag get_function into the overlay window against the last-registered section;
grep retained logs for any mismatch (positive control: ROGUESQ_S7528_CTL=1 run prints ctl_hit).
Outcome: H-local/H-resident-safe -> class CLOSED + gate in s7651 sweep; H-stale -> name the writer, fix at the writer.
