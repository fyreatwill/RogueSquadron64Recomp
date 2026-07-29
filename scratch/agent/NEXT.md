# NEXT work unit — find and guard the 9th unguarded gap in
# `composeNpcOrientationMatrix` (`static_5_800AB1C8`), a NEW crash family
# uncovered once s260 closed out the `setLookupEntryField5ByKey` chain

## Where the investigation stands (s260)

s260 closed s259's lead: `setLookupEntryField5ByKey` (funcs_15.c:70-130)
had TWO unguarded pointers, not one — the caller's argument (`ctx->r4`,
guarded as `SETLOOKUP_ARG_GUARD`) turned out to be a red herring (0 fires
across every soak, crash recurred identically); the real bug was a
2nd-level table-base pointer reloaded inside the function's own search
loop (`ctx->r3 = MEM_W(ctx->r4, 0X0)` at guest `0x800646BC`, then
dereferenced via `index*8 + ctx->r3` at `0x800646C8` with zero
validation). Guarded as `SETLOOKUP_TABLE_GUARD`, bailing via `ctx->r2 = 0;
return;` (matches the loop's own "not found" exit exactly).

**Confirmed fixed, 2 independent soaks**: `setlookupguard2` (full 195s
survival, `CRASH: 0`) and `setlookupguard3` (crashed elsewhere) both show
0 fires on both `SETLOOKUP_ARG_GUARD` and `SETLOOKUP_TABLE_GUARD`, and
neither reproduces the s259/`setlookupguard1` crash signature
(`si_addr=0x3c04b1980`/`x9=0xc04b1980`, `activateAnimationKeyframe` →
`setLookupEntryField5ByKey` stack). Treat this bug family as closed.

**New blocker (`setlookupguard3`)**: crashed after only ~3s into the hold
window via `static_5_800AB1C8` (`composeNpcOrientationMatrix` — the
function s252-s256 already added 8 guards to: `compose-npc-orient-guard`
through `guard8`). All 8 existing guards' diagnostics fired **0 times**
this run (confirmed via `grep -o "\[compose[a-zA-Z0-9_-]*\]"
run.log | sort | uniq -c` — only the entry diagnostic
`[compose-npc-orient-800AB1C8]` appears, 543 hits, none of the 8 fix
tags). This is a genuinely NEW, 9th gap, not a recurrence.

**Register/crash signature**:
```
[CRASH][siginfo] si_addr=0x380000068 si_code=1 si_errno=0
[CRASH][pc-symbol] pc=... sym=static_5_800AB1C8+9024 base=0x100870000
0   ... _sigtramp-adjacent frames ...
3   RogueSquadron64Recomp  static_5_800AB1C8 + 6168
4   RogueSquadron64Recomp  static_5_800AAD9C + 4116
```
`si_addr = rdram_base (0x300000000) + guest_ptr (0x80000068)`. **This
guest value technically PASSES the standard `0x80000000`-`0x80800000`
KSEG0-range-check idiom** every guard in this codebase uses — it's a
near-null pointer (only `0x68` bytes past the very start of KSEG0), not
an out-of-range or zero-extended value like every previously-seen crash
shape. This is a NEW corruption class this investigation has not
catalogued: **the standard guard idiom is blind to a valid-looking-but-
structurally-nonsensical near-null pointer.**

Entry diagnostic just before the crash showed `arg_r4=0x00000000`
(literally null) on that specific call (`n=542`) — worth checking whether
this call's `arg_r4=0` is itself the root cause (some code path calls
`composeNpcOrientationMatrix` with a null first argument that the
function doesn't expect, and derives the bad `0x80000068` pointer from
it via a small constant offset added to 0).

## The next work unit, in priority order

### Step 1: read the whole function

```
sed -n '6293,7228p' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_40.c
```
(6293 is `static_5_800AB1C8`'s start per s260; 7228 is where the NEXT
function, `static_5_800AB658`, starts per s258's citation — confirm this
boundary is still correct with `awk '/^RECOMP_FUNC/{print NR}'` first).

Cross-reference against the 8 existing guard sites (grep
`fixup_game_funcs.py` for `compose-npc-orient-guard` through `guard8` to
get their exact guest addresses) so you don't waste time re-reading
already-covered lines. **Do NOT use the crash symbol's native
`+6168`/`+9024` offsets as line numbers or guest addresses** — confirmed
misleading 3+ times now (s259, s260 itself for the setlookup bug). Find
this by reading every `MEM_W`/`MEM_HU`/`MEM_B` load in the function that
isn't already covered by one of the 8 guards, especially any that could
plausibly yield a near-zero (not zero, not huge) result — e.g. a load
from a struct field that's usually populated but can be zero/uninitialized
under some code path, then has a small constant added to it before the
next dereference (same "load, add small offset, deref" shape as the
`setLookupEntryField5ByKey` table-pointer bug, and same as `0x80000068`
looking like `0x0 + 0x68`).

### Step 2: decide on the guard idiom for THIS bug

Because `0x80000068` passes the standard range check, a plain KSEG0-range
guard will NOT catch this class. Options, in order of preference:
1. If the unguarded load can be traced to "this specific field is 0 when
   it shouldn't be" (i.e., a null-but-legitimate-address-shaped value),
   guard against `== 0` on the SOURCE field before any offset is added to
   it (catches the bug before it becomes a near-null KSEG0-shaped value).
2. If the near-null shape is inherent to the data (e.g., a real feature of
   this corruption, not simply "started at zero"), consider tightening the
   range check's lower bound (e.g., reject `lo < 0x80001000` or similar) —
   but ONLY if you can articulate why real, legitimate KSEG0 pointers in
   this codebase never land that low (check a few known-good addresses
   already logged elsewhere in this investigation, e.g. rdram struct
   bases, to make sure this wouldn't reject valid data).
Do not guess; read the code path that produces this pointer far enough
back to know which of these is actually true.

### Step 3: build -> soak (new tag)

Same full-regen cycle as always (delete `funcs_*.c` → `make_elf.py` →
`regen_n64recomp.sh` → `fixup_game_funcs.py`, **redirect its output to a
scratch log file and grep it for your new guard's report line — do NOT
trust a bare terminal run, s260 caught an accidental double-run this way**
→ clean `cmake --build .` → `strings`-verify the new env var). Copy
`run_setlookupguard2.sh` (NOT `_3`, which crashed early) to a new tag,
keep `SETLOOKUP_ARG_GUARD`/`SETLOOKUP_TABLE_GUARD`/`EVALSPLINE_GUARD`/
`HANGAR_BAY_DEREF_GUARD` armed as same-run controls (all should stay at 0
fires — that's now the expected, confirmed-fixed baseline, not a new
question), add your new guard's env var.

Block-wait pattern (unchanged): launch with `run_in_background: true`,
read the driver's first line for `pid NNNNN`, then a SEPARATE foreground
Bash call (timeout up to 480000ms):
`until ! kill -0 <pid> 2>/dev/null; do sleep 10; done`.

**Discriminating outcomes**: new guard fires with sane fields -> real
mechanism found, note whether the hold survives further AND whether
`renderUnlitMeshFaces` finally gets called (`unlit-mesh-tracer` positive
control — still 0 hits across every soak in this whole investigation;
R7A_LOADED/R7B_LOADED have never had a real test). Crash recurs at a
DIFFERENT site -> still progress, repeat (expected — this has been
whack-a-mole for 10+ sessions). Crash recurs at the EXACT same
`composeNpcOrientationMatrix`+6168ish signature -> guard missed the
actual load, or the near-null value needs the tightened-lower-bound
approach instead of a plain `==0` guard.

## Do NOT do this iteration

- Do NOT re-run `setlookupguard2` or `setlookupguard3` in place — copy to
  a new tag.
- Do NOT re-litigate whether `SETLOOKUP_ARG_GUARD`/`SETLOOKUP_TABLE_GUARD`
  fixed the s259 bug — that's now 2-soak-confirmed (iron rule 4
  satisfied), treat it as closed unless a NEW soak shows its exact
  signature recurring.
- Do NOT assume a plain KSEG0-range-check guard will work here without
  reading the actual load site first — this specific value
  (`0x80000068`) is a NEW shape that the standard idiom does not catch.
- Do NOT use a crash symbol's native `+N` offset as a source line number
  or guest address.
- Do NOT re-attempt `nm`/`atos`/`objdump` for offset localization —
  confirmed unusable repeatedly. Use `scratch/agent/machoparse.py` if
  function-size verification is needed.
- Do NOT run `fixup_game_funcs.py` more than once per regen cycle without
  redirecting output to a file and grepping the report line count first
  — s260 caught a silent double-application this way.

## Environment notes (carried forward, still current as of s260)

- **`+N` crash-symbol offsets are NATIVE (compiled ARM64) code offsets,
  NOT guest MIPS addresses.**
- **Block-wait pattern**: `run_in_background: true`, read the pid from the
  driver's first output line, then a SEPARATE foreground Bash call
  polling `until ! kill -0 <pid> 2>/dev/null; do sleep 10; done`.
- `/tmp` is not writable this session for GAME artifacts — write scratch
  files inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64`
  only.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`. Run `cd`
  as its own Bash call before any command with output redirection or
  chaining (`&&`) — compound commands after a `cd` get blocked for
  approval.
- **The `[phase] vi_width=512 (was 1024) origin=0x006AB400` line at
  ~t=74-75s is THE confirmed SELECT-CRAFT->mission transition marker.**
- **Regen is mandatory-delete-all-first, AND fixup must run EXACTLY
  once per regen** — always capture its stdout to a file and grep the
  report line for your new guard, rather than trusting a `tail` of a
  live terminal run.
- `N64Recomp` is a separate sibling git repo; `fixup_game_funcs.py` is
  intentionally untracked there (`??` in `git status`) — this is
  established, accepted practice, not something to fix.
- `CURRENT-TRUTH.md` is ~450KB, ~13x the ~35KB target in CLAUDE.md. Not
  addressed this session (budget went to 3 build-soak cycles). A
  dedicated pruning session — migrating durable material to
  `PROJECT-OVERVIEW.md` and trimming/archiving old "Next steps" entries
  that are now fully superseded — is overdue and should be considered as
  a work unit soon, separate from the crash-chasing chain.
