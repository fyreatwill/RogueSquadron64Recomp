# NEXT (s7423)
HYPOTHESIS-ID: live-stale-patch

Class CF (CURRENT-TRUTH Next steps item 1): the binary is built from LIVE RecompiledFuncs
(/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs), not the regen. s7422 found live funcs_9 missing two
chain-applied lines (s6497 bounds read + s6789 g3e kind 8 before `// 0x800429C0`). s7421 proved only 0 LOST live->regen.
1. Regen tree: /tmp/s7422/R (fresh, = /tmp/s7421/R2 byte-identical). If gone: cp -R /tmp/s7420/front X; tools/regen_replay.sh X
   (or tools/regen_front.sh first).
2. Per function present in both, list statements in regen not in live (normalised lines, ignore the "/* PATCH: sN */" label and
   pure reorder). Use tools/s7421_regen_drift.py rows as the join; write tools/s7423_live_stale.py.
3. Classify each regen-only statement: DIAG (env-gated log/trace), BEHAVIOUR (changes guest state / control flow / a default-on
   fix), LABEL/ORDER. Positive control: the two known funcs_9 lines must be listed as DIAG.
4. For each BEHAVIOUR row: is the shipped build missing it? (grep the built object/strings or the live source); fix by
   re-applying the chain to live for that file (keep a backup) and rebuild; or prove it is superseded.
Hypotheses: H-diag (every regen-only statement is diagnostic) vs H-behaviour (>=1 behaviour patch missing from the built tree).
