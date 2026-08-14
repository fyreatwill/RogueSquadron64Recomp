
---

# CONTEXT BUDGET — PORTING-STATE.md is multi-MB and append-only

`PORTING-STATE.md` is currently ~4 MB and grows every iteration; never read it
whole. `docs/CURRENT-TRUTH.md` is kept compact (currently ~11 KB, capped near
60 KB). Reading them whole is wasteful on any runner and fatal on a small-window
one.

1. **NEVER `Read` PORTING-STATE.md.** Use
   `grep -n "<pattern>" PORTING-STATE.md | tail -20` for line numbers, then
   `sed -n 'START,ENDp'` for a window of at most 60 lines.
2. **NEVER read a whole file over ~600 lines.** Grep for the symbol, then read
   a bounded window around the hit.
3. `docs/CURRENT-TRUTH.md` is the one large file you may read in full, once.
4. Never `cat` a run log — they reach 380,000 lines. Use `grep -c`,
   `grep -n ... | head`, or `tail -50`.
5. Prefer one bash command returning a computed answer over three returning
   text you must then read.

NOTE ON PROVENANCE: this file was written while chasing grok's early-cancel
bug and the context-exhaustion explanation for that bug was REFUTED (a
2-turn cancel at 60k tokens). The guidance above stands on its own merits for
a multi-MB ledger; it is NOT a fix for the cancel, and must not be cited as one.
