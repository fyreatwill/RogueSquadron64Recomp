# NEXT work unit

HYPOTHESIS-ID: fresh-idiom-class-audit

## s453 close-out: `S392_H3A`/`S393_H3B` — CLOSED, all 50 sites redundant, no code change

Full mechanistic verification (not sampling): all 29 `S392_H3A` sites (in `updateHangarBayScene`)
and all 21 `S393_H3B` sites (in `hangarTickCameraOrbit`) are already protected by earlier-applied
guard families (`HANGAR_BAY_DEREF_GUARD`/"G"-family from s132, a few `S284`/`S285` sites, one
shared-join-point case). No patch applied — adding guards would only create dead, always-skipped
duplicates. Closure comment left in `fixup_game_funcs.py` (N64Recomp repo, untracked, no
`export.sh` needed). Full detail: `docs/CURRENT-TRUTH.md` item -290, `PORTING-STATE.md` Session
453.

**This closes the `funcs_40.c`/`funcs_27.c`-gated orphan-sweep inventory (item -282, opened s445)
except `BREADCRUMB7`** (a diagnostic, not a crash guard — deliberately out of scope, optional,
lowest priority; `grep -n 'BREADCRUMB7' fixup_game_funcs.py` if a future session wants to close it
out, but it is not required before considering the arc done).

## This session's work unit: open a FRESH M3 idiom-class audit

The tracked backlog that has driven the last ~9 sessions (s445-453, `static5-rename-orphan-sweep`)
is now empty. Per strategic priority #3 (`docs/CURRENT-TRUTH.md` USER DIRECTIVE), M3 crash work
continues only as systematic idiom-class audits — the s282/s445 discovery method: grep-enumerate a
whole idiom class across the live `RecompiledFuncs/*.c` tree, classify every site (needs-guard /
already-guarded / confirmed-safe), guard or prove dead, close the class. This session's job is to
FIND the next class, not assume one.

**Known false start, don't just repeat it**: s389-397 ran a "codebase-wide frequency scan for the
next comparable idiom class" and got a negative result (`docs/PROJECT-OVERVIEW.md` §14) — but that
scan predates the s427 duplicate-symbol-name split (the ~13,770-line merged blob that later turned
out to hide real function boundaries) and the whole s426-453 arc that came after it. The post-s427
function-name landscape is different now; a fresh scan is not guaranteed to hit the same dead end.

### Discriminating measurement

Before building anything, name 2-4 candidate idiom classes and the ONE measurement that would
show each is (a) worth auditing (multiple unguarded live sites) vs (b) already closed/dead
(everything's covered or unreachable) vs (c) not applicable (pattern doesn't actually appear).
Candidates to consider (verify counts before committing to one, don't assume):
1. Other fixed-offset register-reload idioms besides `-0x25A4` — grep for other suspicious
   negative-offset loads off `$s0`-`$s7`/`$gp`-style base registers across `RecompiledFuncs/*.c`
   that read the way `-0x25A4($sN)` did (a "reload a saved global/table pointer, then dereference
   without a range check" shape), tally raw hit counts per offset value, look for the next
   highest-frequency offset that ISN'T already mostly guarded.
2. A different function-scope sweep for guards still hardcoded to a stale `funcs_NN.c`/
   `static_N_0xADDR` gate that this whole arc's method (items -261..-290) hasn't touched yet —
   grep `fixup_game_funcs.py` for `if p.name == "funcs_` across ALL its patch blocks (not just the
   ones already swept) and cross-check each gated filename still contains the code it thinks it
   does, the same check that opened items -284/-286/-288/-289/-290.
3. If neither of the above turns up a live class, consider whether M3 crash work has genuinely run
   dry for now and it's legitimate to reassess against strategic priority #2 (M5 audio) — but M5 is
   marked DONE/CLOSED, no new lead — so check for a NEW audio-adjacent lead first before declaring
   BLOCKED; don't manufacture work.

### Method (same as every session in this arc)

1. Grep-enumerate raw candidate sites for the chosen idiom, get an exact count (don't trust an old
   session's remembered count).
2. Raw regen if needed (delete `RecompiledFuncs/funcs_*.c` → `make_elf.py` → `N64Recomp`, NO fixup
   yet) to get a clean baseline tree, OR work against the existing built tree if it's current
   (check mtimes) — a fresh regen is safer if in doubt.
3. Standalone Python scan: tree-wide anchor-uniqueness check per site BEFORE writing any patch
   (`SystemExit`-on->1-match hard guard, s446-era discipline) — and this session's own lesson:
   build the address-extraction regex to match ONLY `// 0xADDR:` comment prefixes, not any
   `0x[hex]` substring anywhere in the anchor text, or immediate-offset text inside a disassembly
   comment (e.g. `0x8($v0)`) will falsely match and corrupt line-range resolution.
2b. **Before assuming a site needs a fresh guard, check whether it's already redundant** — s453's
   method: identify the register actually dereferenced at the site's real endpoint (not
   necessarily the last line of whatever anchor text you first write down), then scan a window
   before AND after that point for an already-applied guard block validating that same register,
   including across a shared `goto`-target join if the site's own control flow jumps into one.
   Don't assume "same reg" always sits within the specific 4-line span you first guessed — expand
   the search window if you get an AMBIGUOUS/UNRESOLVED classification rather than treating it as
   NEEDS_GUARD by default.
4. Ungate/patch only genuinely-uncovered sites + `SystemExit`-on-`n>1` guard.
5. Full regen → build → audit fixup report → `strings` → live-verify (full armed-var list) → queue
   a confirmation soak.
6. **Expected result per item -287's established baseline for this whole guard-idiom family: 0
   fires is the norm, not an open question** — don't spend a session chasing a positive control
   for a guard family that's already had one (item -287, s449).

## Process notes carried forward

- `tools/probe.sh`'s exit code is trustworthy on its own now (exit 3 on a detected `[CRASH]`, s447).
- `fixup_game_funcs.py` lives in the sibling `N64Recomp` repo
  (`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`), NOT in this repo — it is
  not git-tracked by RogueSquadron64Recomp and needs no `export.sh`.
- Watch for DOUBLY-orphaned gates (file AND function-name-regex referencing a dead old
  `static_N_0xADDR` name) — confirmed pattern across several families now. Check, don't assume.
- Before ungating any family whose patch body contains a bare `goto LABEL` (not a label the patch
  itself defines), grep for that label's OWN defining block and confirm it is not independently
  orphaned — a build failure ("undeclared label") is the symptom if you skip this check. It can
  also come back CLEAN (already proven live by other already-ungated guards in the same file) —
  check first, don't assume either outcome.
- The near-`0x80000000`/`BREADCRUMB6` "near-zero guest pointer" crash family (`si_addr=0x3800000xx`,
  `pc-symbol=buildPositionAndCallTransformHelper+...`) is a recurring, fully-catalogued background
  crash signature unrelated to this whole orphan-sweep effort — if a future confirm soak hits it
  again, do not re-investigate, just note the occurrence.
- Scratch analysis scripts from s453 (`N64Recomp/scratch_classify3.py`,
  `scratch_verify_no_reassign.py`) are a reusable template for the "is this site already redundant"
  check — adapt rather than rewrite from scratch for the next idiom class.
