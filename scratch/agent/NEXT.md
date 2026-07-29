# NEXT work unit — trace the guest-`0x80000000` fault inside
# `heapFreeListDequeue` and tighten `DEQUEUE_GUARD`'s boundary if it's the
# cause.

## Where the investigation stands (s266)

s266 executed s265's prescribed plan: re-ran `run_breadcrumb1.sh` until a
`submitSceneNodeRender`-range crash recurred (hit on attempt 3 of 3), used
`[CRASH][last-guest-pc]` to localize it to the EXACT source line
(`funcs_4.c`, guest `0x80010E40`), identified it as a 2nd, previously
unguarded occurrence of s197's "cached free-list head" idiom (s197 originally
guarded only 1 of what may be several inlined copies — same under-scoping
mistake s131 already caught once before for the sibling
`findAndUnlinkSmallestEntry` idiom), and landed `CACHE2_GUARD`
(`N64Recomp/fixup_game_funcs.py`). Full regen clean, build clean. 2 post-fix
soaks: 1 clean, 1 crash — but the crash was a DIFFERENT bug, not a recurrence
of what `CACHE2_GUARD` targets (0 fires of `CACHE2_GUARD` either soak). See
`PORTING-STATE` Session 266 for full detail.

**The new, higher-priority finding**: soak 2 crashed with
`[CRASH][pc-symbol] sym=heapFreeListDequeue+16188` — verified via
`s264_symrange.py` (`cd RogueSquadron64Recomp && python3
scratch/agent/s264_symrange.py` — note: this script hardcodes path
`build/RogueSquadron64Recomp` and only ever reports symbols near
`submitSceneNodeRender`/`heapFreeListDequeue` by name; for a NEW function
you'll need to adapt the one-off inline-python approach used this session,
see Session 266's write-up) that native offset 16188 genuinely falls inside
`heapFreeListDequeue`'s own address range (0 to 21608, next symbol
`_do_lwl`) — this is a REAL crash inside that function's body, not a
misattribution (unlike the original `heapFreeListDequeue`-symbol crash s264
refuted two sessions ago).

The fault address is guest `0x80000000` EXACTLY (`si_addr=0x380000000` =
RDRAM base `0x300000000` + `0x80000000` — cross-check any register dump
against `x_n = 0x0000000080000000`, not the base pointer itself). This is
**NOT** item -49's KSEG0-zero-extension bug (`CURRENT-TRUTH` item -49,
`0x80630062`) — different exact value, different site, do not conflate.

**Working hypothesis (unverified)**: `DEQUEUE_GUARD`
(`scratch/agent/fixup_game_funcs.py` — actually `N64Recomp/fixup_game_funcs.py`,
search for `_dequeue_guard_patch`) checks
`r4_lo < 0x80000000u || r4_lo >= 0x80800000u` before calling
`heapFreeListDequeue`. That check treats `r4_lo == 0x80000000` as a VALID
address (it's not strictly less than the lower bound), so if the actual
corrupt/sentinel value flowing into this call is precisely the KSEG0 segment
base (`0x80000000`) rather than literal guest `0x0`, it sails through
`DEQUEUE_GUARD` silently — consistent with `DEQUEUE_GUARD` showing 0 fires
across 3 independent soaks (s263, s264, s266) despite a crash still reaching
`heapFreeListDequeue`'s body from one of its two guarded call sites (this
soak's `[CRASH][last-guest-pc]=0x80010cdc` matches
`DEQUEUE_GUARD` site 2's own delay-slot address, `0x80010CDC`, exactly).

## The next work unit

1. **Confirm the hypothesis before touching the guard.** Add a targeted,
   scoped diagnostic inside `heapFreeListDequeue` (funcs_3.c, entry ~line
   15571) that dumps every pointer/field dereferenced in its body alongside
   its value, gated behind a new env var (same pattern as every other
   `ROGUESQ_LOG_*` guard/tracer in this codebase) — or, cheaper: since
   `DEQUEUE_GUARD` ALREADY checks `ctx->r4` (`a0`) at the call site and never
   fires, add a SEPARATE, narrower log (not a guard, just an unconditional
   `fprintf` gated by a new env var, e.g. `ROGUESQ_LOG_DEQUEUE_ARG_TRACE`)
   that prints `ctx->r4`'s exact value at both `DEQUEUE_GUARD` sites
   (`0x800104A8`/`0x80010CD8`) on EVERY call (not just failures) for one soak.
   If `ctx->r4 == 0x80000000` shows up right before a crash, the hypothesis
   is confirmed with a same-run positive control (the trace fires on every
   call, satisfying iron rule 1). If `heapFreeListDequeue`'s OWN internal
   pointer chase (not the a0 argument itself) is what holds `0x80000000`
   instead, the trace will show a valid-looking a0 and the bug is deeper
   inside the function — read the function body around offset 16188 (use
   `s193_disasm.py` against the crash `pc` for the ARM64 side, or just read
   `funcs_3.c` — same instruction-comment index applies) to find which
   specific field this is.
2. **Only after confirming**, fix at the actual gap: either tighten
   `DEQUEUE_GUARD`'s lower bound (`<=0x80000000u` instead of `<0x80000000u`)
   if the a0 argument itself is the culprit, or add a new guard inside
   `heapFreeListDequeue`'s own body at the specific internal dereference if
   it's a different pointer. Full delete-all regen (`make_elf.py` →
   `N64Recomp` → `fixup_game_funcs.py` → `cmake --build`), then soak-verify
   per iron rule 4 (at least 2 independent runs with no recurrence, or a
   clean guard-fire-and-recover).
3. **If budget remains after that**: `CACHE2_GUARD` was scoped to the ONE
   occurrence this session's crash hit (guest `0x80010E38`-`0x80010E40`).
   Given the sibling `findAndUnlinkSmallestEntry` idiom turned out to be
   inlined 9 times (s131's GUARD2/GUARD3), it's plausible the CACHE idiom is
   ALSO inlined more than the 2 occurrences now guarded (s197's original +
   this session's CACHE2). Worth a source-read of `submitSceneNodeRender`
   grepping for the `lw $vX, 0x63B0($vX)` / `lw $vX, 0x0($vX)` pattern
   (reload-global-then-deref) to count how many total copies exist, matching
   the same generalization s131 did — but only if the guest-`0x80000000`
   investigation above is resolved or budgeted out first (it's the actual
   live crash blocker right now).

## Do NOT do this iteration

- Do NOT conflate the guest-`0x80000000` fault with item -49's
  KSEG0-zero-extension bug (`0x80630062`) — different exact value, different
  function, confirmed distinct.
- Do NOT cite `x0`/`x8`/`x9`/`x11 = 0x0000000300000000` as crash-matching
  evidence for ANYTHING — constant RDRAM base pointer (s219, item -60).
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
  `CACHE2_GUARD`/`MATLIST_GUARD1-3`/`COMPOSE_NPC_GUARD1-9` — all verified not
  regressing and not the current blocker. `DEQUEUE_GUARD` may need its bound
  tightened (see above) but don't touch it without first confirming via step
  1's trace.
- Do NOT idle across a Stop-hook turn boundary waiting on a background
  soak — block with `TaskOutput(task_id, block=true, timeout<=480000)` in
  the SAME turn.
- Do NOT assume `s264_symrange.py` takes command-line args — it doesn't; it
  hardcodes `build/RogueSquadron64Recomp` as the path and only reports
  `submitSceneNodeRender`/`heapFreeListDequeue` by name. For a new symbol,
  either edit the script or write a one-off inline-python snippet (see
  Session 266's write-up for a working template).

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64`, `N64Recomp`
  needs cwd `N64Recomp`, `fixup_game_funcs.py` needs cwd `N64Recomp` (or an
  absolute path — either works, but re-running the SAME already-patched
  files a 2nd time in a row makes every regex match 0 and looks like a
  regression when it's just non-idempotent re-application; always regen from
  fresh `funcs_*.c` before checking match counts).
- Delete `funcs_*.c` before regen via:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
  (`rm`/`find -delete` are sandbox-blocked).
- Background launches do NOT inherit a prior foreground `cd` — always
  launch soak drivers by full absolute path when using
  `run_in_background: true`.
- Cross-turn waiting does not work under the Stop hook — use
  `TaskOutput(task_id, block=true, timeout<=480000)` synchronously in the
  same turn.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT
  `scratch/agent/`. Current-best baseline: `run_breadcrumb1.sh` — now also
  arms `ROGUESQ_LOG_SCENE_NODE_CACHE_GUARD`/`ROGUESQ_LOG_SCENE_NODE_CACHE2_GUARD`.
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets, verifiable
  with `s264_symrange.py` + `s193_disasm.py` (no `nm`/`atos`/`otool`/
  `lldb`/`dwarfdump` on this sandbox's Bash allowlist).
- Redirecting shell output (`>`) only works to paths under one of the 3
  session working directories (`RogueSquadron64Recomp`, `N64Recomp`,
  `rogue_squadron64`) — `/tmp` is blocked. Use
  `scratch/agent/*.log` for capturing tool output you want to grep later.
- `CURRENT-TRUTH.md` is ~460KB+, ~13x the ~35KB target in CLAUDE.md. A
  dedicated pruning session is now 8+ consecutive sessions overdue —
  still not this iteration's job unless the localization work above is a
  quick null with clear leftover budget.
