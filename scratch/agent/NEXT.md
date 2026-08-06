# NEXT work unit

## s396 recap

Finished s394's original 3-file sweep-remainder plan. `funcs_40.c` (69 raw `-0x25A4` hits) and
`funcs_19.c` (1 raw hit) both swept via the same delegated-classification methodology validated s395.
Result: **0 NEEDS-GUARD sites in either file** — `funcs_40.c` is 65 COVERED + 4 SAFE (all 69 raw hits
accounted for, matching pre-existing guard families `guard1`-`8`, `HANGARLIST_GUARD*`,
`_s284_deref_guard_sites`, `G1`-`G32`), `funcs_19.c`'s 1 hit is an unrelated same-displacement coincidence
(different `lui` base, float divisor, never a pointer — already flagged as a false positive by s284's own
comment). Verified two independent ways: the subagent's direct per-site source reads, and my own
post-hoc `grep -c -- "-0X25A4"` recount (69/1, exact match) plus an arithmetic check that every
function's COVERED+SAFE count sums exactly to its own raw-hit count. No code change, regen, build, or
soak was needed or done — this session's result IS the classification itself.

**This CLOSES the entire `-0x25A4` hangar-list-pointer idiom-class audit** (s283-s396). All three files
that ever showed a raw hit in this family (`funcs_27.c` s395, `funcs_40.c`/`funcs_19.c` s396) are now
confirmed fully covered or confirmed-safe. Full detail: `PORTING-STATE` Session 396; `docs/CURRENT-TRUTH.md`
item -246.

## This iteration's work unit: find the NEXT idiom class (the s283-style discovery step)

The `-0x25A4` audit is done. Per the user directive, M3 crash work continues ONLY as systematic
idiom-class audits — the next one needs a genuinely new candidate family, found the same way s283
originally found `-0x25A4`: a codebase-wide frequency scan for repeated unguarded global-pointer-load
displacements, not a specific crash chase.

### Step 1 — small warm-up cleanup (bounded, ~10 min, do this first since it's free)

Remove or relocate the leftover `S285_H1_8` stale-register guard in `funcs_27.c` (flagged s395,
`fixup_game_funcs.py` ~line 122483-ish — grep `S285_H1_8` to find it). It checks `ctx->r4` at a point
where `r4` still holds a value from an unrelated combine 65 lines earlier — harmless dead-weight now that
`S395_SWEEP_1` covers the real dereference, but it should not keep existing as apparent (but wrong)
protection. Either delete the guard block entirely or relocate it to the correct anchor (before
`S395_SWEEP_1`'s own guard, immediately after the real combine) — relocating is probably cleaner since it
gives the same address a second confirmed-correct check rather than removing coverage-looking code that a
future session might assume is real. Verify: `S285_H1_8`'s own diagnostic env var
(`ROGUESQ_LOG_S285_GUARD`, or whatever it's actually keyed on — check the source) still compiles and
behaves sanely. This alone is small enough to fold into Step 2/3's regen-build-soak cycle rather than
needing its own.

### Step 2 — codebase-wide displacement frequency scan (the actual discovery step)

```
cd ~/Documents/Tools/N64Recomp/RecompiledFuncs
grep -ohE 'MEM_[WBH][U]?\(ctx->[a-z0-9]+, -0X[0-9A-F]+\)' *.c | \
  sed -E 's/.*(-0X[0-9A-F]+)\).*/\1/' | sort | uniq -c | sort -rn | head -60
```

This ranks negative-displacement `MEM_*` loads by raw frequency across the WHOLE codebase (not just
`hangarInitialize`/`funcs_40.c`), the same shape `-0x25A4` had before s283 identified it. Cross-reference
the top ~10-15 displacement values against `fixup_game_funcs.py` (`grep -n '<displacement>' fixup_game_funcs.py`)
to see which are already-audited families (there are several beyond `-0x25A4` — e.g. the `Lookup`
struct-family guards from s389, `SETLOOKUP_TABLE_GUARD` from s260) and which have NO existing guard
coverage at all. The next work unit is whichever uncovered displacement has the highest raw hit count —
delegate its full per-site classification to a subagent using the exact same brief shape as this
session's (self-contained, direct source reads, cross-reference against ALL existing guards, propose
ready-to-paste tuples), then apply + regen + build + soak per the established protocol.

If the scan turns up nothing with meaningfully high frequency (i.e. the codebase's other displacement
families are all small/already covered), that itself is a valid discriminating result — write it up and
consider whether the M3 idiom-class-audit model has run its course for THIS project, at which point
Next-steps ordering (not the USER DIRECTIVE, which would need human re-confirmation) should decide the
next M3 item, or the loop should surface a BLOCKED asking the human to reprioritize between M3/M4/M5.

## Iteration budget

HYPOTHESIS-ID: m3-idiom-audit-next-family (NEW — pivoting off `m3-idiom-audit-fresh`, whose investigation
target, the `-0x25A4` family, is now fully closed as of this session. This is a genuine pivot, not a
same-thread continuation: the discriminating question changes from "is this specific family fully
guarded" to "what is the next family to audit".)
