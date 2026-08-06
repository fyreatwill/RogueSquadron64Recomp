# NEXT work unit

## s376 ran the designated source-only H1/H2/H3 pass — all three REFUTED, thread CLOSED

Full write-up: `docs/CURRENT-TRUTH.md` item -230, `PORTING-STATE.md` Session 376. One-paragraph
version: `HYPOTHESIS-ID m5-audio-vi640to1024-trigger-site` (why C88-reversed never re-triggers the
VI 640→1024 transition) is closed by elimination, not solved. H1 (reset-branch divergence) refutes
because `reapplyAudioConfig` always returns 0 regardless of gate state (`funcs_24.c:5148-5149`). H2
(shared-mutable-state collision) refutes because the tick functions' write targets
(`funcs_25.c:5744-5800`, `funcs_26.c:4194-4354`/`0x80153414`) are disjoint from everything the
scene-transition chain reads. H3 (external completion-wait) refutes because every one of the ~65
gate-byte references across `funcs_21-26.c` is inside the already-known MusyX guard-and-return idiom
— no poll site exists in `funcs_0.c`/`funcs_3.c`/`funcs_4.c`. Only H4 (diffuse frame-timing effect,
no single site) remains, and it was judged not worth a build+soak: s373 already showed real audio
stays 100% silent in the *working* baseline regardless, so even a confirmed H4 fix wouldn't produce
working audio. **No M5 audio thread remains open** — reopening needs a genuinely new lead.

## This iteration's work unit: fixup_game_funcs.py function-scope-match backport (sanctioned tooling)

Per `docs/CURRENT-TRUTH.md`'s USER DIRECTIVE section: "Sanctioned tooling work unit, counts as
ADVANCED whenever picked up: backport function-scoped matching (the BREADCRUMB10+ slice idiom) to
the ~100 file-scoped-only guard patches in fixup_game_funcs.py, per the 2026-08-04 analysis in that
file's header comment." This is a bounded code-quality/robustness task, not a hypothesis chase — no
HYPOTHESIS-ID budget applies in the usual sense, but one is still named below per the exit contract.

### What "file-scoped" vs "function-scoped" means here
Read the 2026-08-04 header-comment note in `~/Documents/Tools/N64Recomp/fixup_game_funcs.py` (top of
file) and the newer BREADCRUMB10+ patches (search for `BREADCRUMB10` onward in that file) to see the
function-scoped idiom in practice: those patches split the target `.c` file into per-function slices
(via the existing `func_re`/`parts` splitting machinery already in the script, see the "split into
functions, check goto/label consistency" block) and apply their regex anchor only within the named
function's slice, so an identical anchor string appearing in a DIFFERENT function of the same file
cannot be mismatched onto it. The ~100 older guard patches instead apply their regex directly against
the whole file's text — safe today only because each anchor string has so far been unique
file-wide, a property overlay re-chunking could break silently.

### Concrete steps
1. In `fixup_game_funcs.py`, enumerate every older guard patch that matches file-scoped (search for
   patches that call `re.subn`/`re.sub` directly against the whole-file `text` variable rather than a
   per-function `body` slice — the BREADCRUMB10+ patches show the target pattern to convert to).
2. For each, identify which named function it's anchored inside (should be discoverable from the
   patch's own context/comment, or by finding which function's body contains the anchor string today).
3. Convert each to the function-scoped idiom: locate the function's slice via the existing
   `func_re`/`parts` splitting already in the script, apply the regex only within that slice, and
   reassemble exactly as the BREADCRUMB10+ patches already do (copy their exact mechanism, don't
   reinvent it).
4. This is a mechanical, low-risk transform (same regex, narrower scope) but touches ~100 patch
   call-sites — batch it: convert all of them in one pass, then ONE full regen
   (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` -> `cmake`) to confirm the patch report
   still shows the expected `xN` counts (per the item -20 standing rule: audit for anything other
   than the expected count) and the build still succeeds.
5. A short soak (not a full validation campaign — this is a refactor of the patching mechanism, not
   game logic; the emitted C should be byte-identical in content, just differently scoped) confirming
   no new crash class is sufficient. If any patch's expected count changes after the conversion, STOP
   and investigate that one site specifically before continuing — a silently-changed count means the
   scoping changed which occurrences get matched, which is exactly the bug class this backport exists
   to prevent.

### Expected outcome
Either: all ~100 patches convert cleanly, patch-report counts are unchanged, one regen+build+short
soak confirms no regression — write up as ADVANCED (tooling hardening landed). Or: converting
surfaces a patch whose anchor is NOT actually unique per-function (a real latent bug the file-scoped
form was masking) — that's also a valid, valuable result, write it up as such and guard/fix that one
site same as any other guard patch.

## Iteration budget

HYPOTHESIS-ID: fixup-scope-backport (iteration 1 — this is a bounded tooling task, not expected to
need a multi-iteration hypothesis budget; if it turns out to be larger than expected, split it into
multiple bounded sub-batches across iterations rather than letting it sprawl).
