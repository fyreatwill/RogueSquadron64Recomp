# NEXT work unit

## s388 recap

Closed out both live follow-up items from the fixup-scope backport thread. This iteration resolved
Option B from s387's NEXT.md: the `musyxSynthFrame`/`initN64RspMixer` `synth-rearm-ptr` ownership
question. Confirmed directly against the generated `funcs_24.c` (line-boundary grep, not just re-trusting
s384's inference) that the `0x800919D4` anchor is unambiguously inside `initN64RspMixer` (starts line
4396, anchor at line 4580, no intervening `RECOMP_FUNC` boundary; `musyxSynthFrame` starts line 3146 and
ends well before). Converted the patch in `fixup_game_funcs.py` from file-scope to function-scope on
`initN64RspMixer`, using the same body-boundary idiom as every other function-scoped patch in the script.
Verified via the standard byte-identical regen-diff protocol: fresh 45-file unpatched baseline, ran
pre-edit and post-edit script against separate copies, diffed the 374-line fixup report (zero diff) and
the full 45-file SHA-256 tree listing (zero diff) — expected, since the anchor is the sole occurrence of
that text in the file, so narrowing the search window doesn't change what gets matched. Build clean, soak
clean (0 crash markers over 15,750 log lines, `[present-1024]`/`w=512` markers and VI update counter
progressing continuously over 110s as a positive control). No `lib/` files touched (edit lives in the
standalone N64Recomp tool checkout, untracked by git there). `HYPOTHESIS-ID post-backport-followups` is
now CLOSED — both s387 follow-up items resolved, the whole fixup-scope-backport thread (opened s377, closed
s386, follow-ups s387-388) has no remaining live work.

## This iteration's work unit: M3 idiom-class audit (strategic-priority item 3)

Per the standing strategic-priority order, with M5 audio work fully closed (s376) and the sanctioned
tooling backport thread now fully closed (s388), the next work unit is a **new** M3 systematic
idiom-class audit — the s282-288 `-0x25A4` model: grep-enumerate a whole idiom class of guard/crash sites,
classify every site, guard or prove dead, close the class. Do NOT reactively chase a single breadcrumb.

### Step 1 — find a live candidate (do this first, it's cheap)

`scratch/agent/SOAK-RESULTS.md`'s tail as of s388 has been quiet since s369 — the only entries since then
(s379, s386, s388) are manual batch-verification soaks from the backport thread, not idiom-hunting soaks,
so they don't tell us what's currently recurring. Before picking an idiom class:

1. Scan `scratch/agent/soak_results/*.log` (the raw logs, not just the one-line verdicts in
   SOAK-RESULTS.md) for crash-marker patterns across the last ~15-20 soaks: grep for
   `SIGSEGV|SIGBUS|SIGTRAP|Assertion|UnhandledJumpTarget` plus any `last-guest-pc=` / checkpoint-style
   breadcrumb output near the crash, and tally which function/address recurs most.
2. Cross-reference against `PORTING-STATE.md` sessions 350-369 (drainMeshReleaseQueue / heap-walker /
   ring-buffer threads — search don't read linearly) to see which crash family was still open when the
   backport work displaced it, and whether soaks since s369 (if any exist beyond the manual ones) already
   moved it forward.
3. Pick ONE idiom class with the most evidence density (highest count of independent hits across distinct
   soak runs) as this session's target. Write down the class definition precisely (e.g. "every unguarded
   tail-scan loop matching pattern X across all functions", not just one function) before starting the
   grep-enumerate step.

### Step 2 — grep-enumerate and classify

Follow the s282-288 model: grep the full idiom pattern across all of `RecompiledFuncs/`, produce one line
per site with file/function/address, classify each as (a) already guarded, (b) needs a guard, (c) provably
dead code, or (d) needs more investigation. Do not guard a single site reactively — enumerate the whole
class first, then batch the guards into one patch set with one regen-diff-build-soak verification cycle,
same protocol as the backport batches.

## Iteration budget

HYPOTHESIS-ID: m3-idiom-audit-fresh (NEW slug — pivoted from `post-backport-followups`, which is now
closed with both items resolved). This is iteration 1 of the new slug.
