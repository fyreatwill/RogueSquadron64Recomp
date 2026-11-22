# NEXT (s7788; s7787 closed the hook pc-literal class: 257,643 literals, 4 emitters fixed, gate s7787_hook_pc_census)
HYPOTHESIS-ID: dead-emitter-census
First (any of these outranks the rest): `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers
in docs/OWNER-REVIEW-QUEUE.md, new SOAK-RESULTS lines.

Question: which fixup emitters silently emit NOTHING (or fewer sites than they intend)? s7787 found the s2586 "store" branch
dead (it keys store pcs off a tracker only branch comments set: 0 emitted) and s6336 losing one store to an s4984 rewrite.
Families: every `/* PATCH: <tag> */` marker an apply_*.py / fixup_*.py script writes, vs the count of that marker in the live
tree (N64Recomp/RecompiledFuncs) and in a fresh replay (`python3 tools/s7719_regen_gate.py --strict --keep /tmp/s7788/replay`
keeps replay.log with each script's own "patched N" report).
Hypotheses: H-clean (every emitter's in-tree count equals what its own report/intent says, 0-count ones are documented
retirements), H-dead (some emitter's pattern never matches: list it, say whether any PORTING-STATE conclusion relied on its
rows: such a null is a false zero), H-partial (an emitter matches fewer sites than its family because a later rewrite changed
the anchor, like s6336/s4984).
Unit (offline): tools/s7788_dead_emitter_census.py: harvest marker strings from tools/*.py (literal "/* PATCH: ..." and
MARKER/TAG constants), count each in the live tree; --controls: a planted marker in a temp tool with 0 tree hits must read
DEAD, a real one (s6336, 47,373) LIVE. For each DEAD/PARTIAL: grep PORTING-STATE for its tag/env var; a dead emitter that a
conclusion read as "0 events" reopens that conclusion. Fix or retire (comment + CURRENT-TRUTH note) each, rebuild if code
changes, s7719 --strict, sweep --only 's778'.
