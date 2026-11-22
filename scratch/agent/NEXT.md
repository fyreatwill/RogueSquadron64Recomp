# NEXT (s7812)
(s7811 spent on the s7420 census contract fix; this unit is still untouched and still next.)
HYPOTHESIS-ID: fixup-behaviour-delta-class
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
s7810 closed the host-override class (tools/s7810_host_override_diff.py, sweep row S7810_HOST_OVR; zmemcpy zero-extended-pointer
fault fixed). s7809 closed the gcc C-patch class. Note: ../N64Recomp/rogue_squadron.toml has NO stubs/ignored lists today (the
upstream_compat.cpp "zmemcpy is stubbed in rogue_squadron.toml" comment is historical), so there is no stub class.
Unit: the third sibling = fixup-script edits that CHANGE generated behaviour by default (early returns, skipped stores, value
overrides, guards) as opposed to diagnostics gated off by default. BORING FIRST: `grep -n 'fixup.*class\|behaviour-changing\|default-on guard' PORTING-STATE.md | tail`
to check whether an earlier session already closed this census; if closed, take the next G-ladder item instead.
Method: diff raw N64Recomp output against the fixup'd RecompiledFuncs (the s7719 regen replay has both), classify every hunk as
(diag: compiled out / gated by a default-off flag) vs (behaviour: active by default). Each behaviour hunk needs an ORIGIN row
(writer named, env to disable, session) or reads RED. Controls: a planted default-on hunk with no row reads RED; a planted
default-off diag hunk reads diag.
Hypotheses: H-all-rowed (every default-on hunk already documented), H-orphan (>=1 default-on guard with no ORIGIN / no off switch),
H-hollow (classifier misses a hunk shape -> hunk count must equal the regen diff's hunk count).
