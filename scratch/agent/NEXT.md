# NEXT: G1 — fold s5788_get_fire / s5788_get_nofire ([objcount] get lines in scratch/agent/m6/<tag>/run.log)

`grep -a '\[objcount\]' scratch/agent/m6/s5788_get_*/run.log | head -60`
- Control: `get` lines must appear (fail rule polls id 2). None -> route/env failed, recheck.
- H-bulk: get id=2 val>=3 appears with NO set/increase lines -> counter filled by non-function write; next: store-tag/sampling watch on 0x80138064 (rdram 0x138064) with host backtrace.
- H-unreached: set/increase lines absent but val rises -> same as bulk; check callers via funcs_44 script sites.
- H-friendly-loss: increase lines with id=2 and ra in mission script (funcs_44) -> read the condition.
Compare fire vs nofire arm (fire arm only had hudbit4 in s5787).
HYPOTHESIS-ID: g1-mission-progression
