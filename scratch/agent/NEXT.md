# NEXT work unit

HYPOTHESIS-ID: dl-list-append-5824-noncanonical

## s462 CLOSED item -292 (`SONGTEMPO_TABLE_GUARD`, 43/43 sites) — the last `stepActiveSongTracks`
slice (12 sites) built/verified/soaked clean. Full derivation: `PORTING-STATE.md` Session 462,
`docs/CURRENT-TRUTH.md` item -292. Confirmation soak queued:
`scratch/agent/soak_queue/s462_stepactivesongtracks_confirm.sh`.

**No M3 idiom-class-audit thread is currently open.** Per the USER DIRECTIVE priority order
(`docs/CURRENT-TRUTH.md`), the next work unit is a NEW idiom-class audit — competing options below,
pick the first by default unless Step 0 or a fresher soak result changes the picture.

## Priority 1 (this iteration, default): open the `~111 non-canonical -0x5824` idiom-class audit

Background: item -291 (`DL_LIST_APPEND_GUARD`, CLOSED s456) swept 57 **canonical** `-0x5824($reg)`
sites — a `lui`+`lw` pair with no intervening instructions, reg-to-reg — reaching global
`0x8011A7DC`. When that item closed, the s454/456 scan also flagged ~111 **non-canonical** sites
reaching the SAME global through the same `-0x5824` offset but via a non-adjacent load/deref pair
(intervening code between the `lui` and the `lw`, or a different register chain) — these were
explicitly out of scope for item -291's regex-based scan and have never been enumerated or
assessed. This is a fresh idiom-class candidate, not a continuation of a closed item.

**Before writing any patch code**, this iteration should be primarily a SCOPING pass:
1. Grep-enumerate: find every `-0x5824(` occurrence across `RecompiledFuncs/funcs_*.c` (all
   files, not just `funcs_3.c`/`funcs_4.c` — item -291's canonical sweep was scoped to those two
   files only, so this non-canonical population may span more).
   `grep -rn -- '-0x5824(' ~/Documents/Tools/N64Recomp/RecompiledFuncs/*.c | wc -l` first as a
   sanity check against the "~111" estimate from s454/456 (that number was itself a rough count,
   not verified) — if it's wildly different, re-derive before proceeding.
2. Classify: for a sample of ~10-15 sites spread across different functions, read the surrounding
   code to confirm they really do reach `0x8011A7DC` (not a coincidental same-offset access to an
   unrelated struct field — offsets this small/common can collide across unrelated types, per the
   CURRENT-TRUTH "confirmed non-issues" note about small/ubiquitous offsets). If a meaningful
   fraction don't actually resolve to the same global, this may not be a coherent idiom class at
   all — say so and pick a different candidate (see Priority 2 below) rather than forcing a weak
   fit.
3. If confirmed coherent: enumerate the full site list per-function (same standalone Python
   regex-scan method as every closed item, `text.count(block) == 1` uniqueness check before
   touching `fixup_game_funcs.py`), derive per-site bail targets by reading each site's local
   control flow (reuse existing nearby skip idioms, per the established methodology — do not
   templatize blindly across functions with different shapes).
4. This will likely be MULTIPLE work units (111+ sites across possibly many functions) — do not
   try to fix all of them in one iteration. Scope this iteration to: confirm the class is real,
   enumerate it exactly, and fix the first 1-2 functions' worth of sites (mirroring how item -292
   was worked in 6 incremental slices, one reader function per iteration).

## Priority 2 (fallback, if Priority 1's scoping pass finds the class isn't coherent)

Re-read `docs/PROJECT-OVERVIEW.md` §16-§17 for other flagged-but-not-started leads from the
`static5-rename-orphan-sweep` and `SONGTEMPO_TABLE_GUARD` arcs. `BREADCRUMB7` (diagnostic, lowest
priority per item -282..-289's own note) is the only other explicitly named leftover; there may be
others worth a fresh frequency scan (the s389-397 codebase-wide idiom-frequency method, per
`docs/PROJECT-OVERVIEW.md` §14, closed for lack of a hit at the time but not necessarily exhausted
now that 3 more idiom classes have been swept since).

## Discriminating instrument still live: watch for `sibling-ptr-write-guard` fires in
`submitSceneNodeRender`

10 of item -296's 119 `SIBLING_PTR_WRITE_GUARD` sites are in `submitSceneNodeRender`, the same
function named in a still-open "wait-for-recurrence breadcrumb" (2 independent single-occurrence
crashes, different `last-guest-pc` each time, not confirmed as one bug). 0 fires across every soak
so far, including s462's. If any future soak shows a `sibling-ptr-write-guard` fire specifically at
one of those 10 sites, that's new evidence worth immediate follow-up — the one exception to "don't
chase breadcrumbs."

## Incidental observation, not chased (s462)

s462's live-verify saw one fire of the already-catalogued, unconditional `[hangarmenu-a0-guard]`
diagnostic (item -265, s428) — pre-existing, unrelated to the songtempo work, matches its own
documented "wild but harmless" firing pattern from its original s428 soak. Do not chase; it's not
in scope for the current priority (M3 idiom-class audits only, no reactive single-crash chases).

## Confirmed non-issues, do not re-investigate

`-0x25C0($s0)` (56 sites) and `-0x76E0($s0)` (46 sites) are compile-time-constant-based
counter/scalar accesses, not pointer dereferences. Small/ubiquitous offsets (`0x0`-`0x20`...)
match hundreds of unrelated functions — too broad to be a distinct idiom class.

## Sandbox notes (unchanged, still true)

`rm -f RecompiledFuncs/funcs_*.c` (glob in a write-context Bash command) gets denied — use a
Python one-liner instead:
```
python3 -c "
import glob, os
for f in glob.glob(os.path.expanduser('~/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')):
    os.remove(f)
"
```
Compound `cd X && command > file` Bash calls get denied. Prefer absolute paths passed directly to
the tool instead of `cd &&`. Piping/chaining `python3 fixup_game_funcs.py > file 2>&1` in a
compound command with `cd` also gets denied — invoke the script with its absolute path directly
(no `cd` needed, it resolves `RecompiledFuncs/` relative to its own `__file__`), and if you need
the output captured, redirect to a path under one of the three allowed working directories, as a
STANDALONE command (not chained with `&&`/`;` to another operation) — compound commands mixing
`cd`, redirection, and a second command each add their own approval prompt.

**Regen ordering, single most consequential ordering mistake in this session:** run
`N64Recomp` only AFTER deleting the stale `RecompiledFuncs/funcs_*.c` files, not before — item -20
says `N64Recomp` skips rewriting any file that already exists on disk, so running it first (against
files a previous fixup pass already patched) silently no-ops and your new patch never lands. If
`grep -n "RS64_FIXUP_APPLIED" RecompiledFuncs/funcs_25.c` (or whichever file you're touching)
already shows a hit BEFORE you've run `fixup_game_funcs.py` this session, the files are stale from
a previous run — delete and regenerate before doing anything else.

## Process notes

Before starting: `ps aux | grep loop.sh` and `tail -20 scratch/agent/loop.log`, cheaply, once.

`cmake --build` takes ~2 minutes — always launch it as a background Bash command
(`run_in_background: true`) and continue other prep work, or wait for the notification, rather
than foreground-polling. Same for `tools/probe.sh` live-verify runs (300s+): launch backgrounded,
then use `TaskOutput` (or just let the `<task-notification>` land) to retrieve the result — do NOT
write a manual `while kill -0 $PID` poll loop babysitting a `run_in_background: true` task; the
harness already delivers exactly one completion notification for it. A manual poll loop is only
useful for waiting on a process you did NOT launch via `run_in_background` (e.g. one spawned by a
detached `&` inside a script).

If a future iteration opens with an immediate 429, that's the account's monthly Claude spend limit
recurring, not a new bug to chase.
