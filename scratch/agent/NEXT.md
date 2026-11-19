# NEXT (s7649)
HYPOTHESIS-ID: mk8-conclusion-revalidation

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7648 closed class MK8 (docs/MK8-KEY-ALIAS-CENSUS.md): no default-on code aliases dd>1 data, but 229 DIAGNOSTIC host
sites key or bound addresses at 8 MB. s7647 showed a dd>1 conclusion (TS-4) can be an alias artefact of such a key.
Work unit (offline, bounded):
1. `python3 tools/s7648_mk8_census.py -v > /tmp/mk8.txt` -> the D/D* functions and their log tags ([m5-*], [s4209], [f5-*],
   [e9prov], [inline-*], [dl-sync-probe], [s4779-*], [s5229], fs-slot ...).
2. For every CLOSED item in CURRENT-TRUTH / PROJECT-OVERVIEW whose evidence was gathered at dd>1 (DRAW_DISTANCE>=2, OSMEM 12,
   DLPOOLX, spill) AND whose evidence came from one of those tags: table it (item, tag, dd, could the keyed address be >= 8 MB?).
   Most M5 audio work predates dd>1 (dd1 only: safe). G5b/G5h/G1c-era RSP/DL instruments are the likely risk.
3. Each at-risk conclusion: either show the keyed data is provably < 8 MB (static arena address), or re-key the instrument to
   0x1FFFFFF with a same-run old-key arm (s7647 pattern) and rerun once (queue as a soak if it needs the screen).
Hypotheses: H-none (no closed conclusion depends on an aliasing diag key at dd>1) vs H-some (>=1 must be reopened).
Rules: never launch under lldb; never touch build/saves; one game at a time; SIGKILL only; pre-create R dirs for g1e_owner_quiet_arms.
