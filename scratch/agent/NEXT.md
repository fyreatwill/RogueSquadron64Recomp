# NEXT work unit — root-cause/guard `processSceneNode+8772`, the KSEG0
zero-extension bug, now the confirmed dominant soak-blocker

Read `docs/CURRENT-TRUTH.md`'s `-48` next-steps item (top of the list) and
PORTING-STATE Session 199 in full before doing anything else (`grep -n
"^## Session 199" PORTING-STATE.md`). Also read Session 194's original
register-file decode of this exact crash (`grep -n "^## Session 194"
PORTING-STATE.md`) — it already did the hard part (identifying the bug
mechanism from the ARM64 register dump, no disassembler needed), do not
re-derive it from scratch.

## Why this is the next work unit

s199 added a defensive guard for the (then-)top-priority `runVideoFrameTick
+1568` SIGBUS and ran 3 soaks to test it. 2 of the 3 soaks were informative
and passed cleanly through that crash's two prior death points
(decisionN=8972, 15418) with zero recurrence — suggestive, not yet
confirmed (this project's own bar, applied to the 18th class in s195-s198,
is 3 consecutive clean passes; only 2 landed this session). But the 3rd
soak died to something else entirely: a SIGBUS at decisionN=9788 that is a
**byte-for-byte match** to s194's single-occurrence `processSceneNode+8772`
crash (`si_addr=0x380630062`, same low 20 bits, same duplicated-frame
backtrace shape). s194 already decoded the mechanism directly from the
ARM64 register file: `far` = `x0/x8` (rdram host base) + `x9`
(`0x80630062`, a KSEG0-tagged guest pointer that's **zero-extended**, not
**sign-extended** — the normal `MEM_W`/`ADD32` path always sign-extends
32-bit guest addresses to `0xFFFFFFFF80xxxxxx` before subtracting the KSEG0
base; here something added the raw, zero-extended value directly, producing
a ~2 GB wild offset instead of a valid ~8 MB one). Two occurrences, exact
match, ~50 decisions apart (9741, 9788) — this is now BOTH the
best-characterized AND the most-recently-blocking crash in the project, so
it outranks the still-unconfirmed `runVideoFrameTick+1568` guard follow-up.

## Do this, in order

1. **Read `processSceneNode`'s full recompiled C body**
   (`N64Recomp/RecompiledFuncs/funcs_4.c:13759-14873`, ~1100 lines — this is
   a big function, read it in chunks, don't try one 256 KB `Read` call).
   Look specifically for a pointer computation that does NOT go through
   `S32(...)`/`ADD32(...)`/`MEM_W(...)`'s sign-extend convention — i.e. a
   raw `ctx->rN + ctx->rM` used directly as a `MEM_W`/`MEM_H`/`MEM_B` base,
   or a 32-bit load whose result gets used as a pointer without going
   through the normal `S32`/sign-extension path first. The bug signature
   (`x9=0x0000000080630062`, top 32 bits zero) means the specific
   instruction either does an unsigned load (`lwu`, if the recompiler ever
   emits one) or manually zero-extends where the original MIPS intended
   sign-extension — grep for unusual-looking casts/`(uint32_t)`/`U32(...)`
   near pointer arithmetic in this function as a starting point.
2. **Cross-check against the two known crash instances** to narrow the
   search: `lr=processSceneNode+8772` in both s194 and s199 (this is the
   RETURN address into `processSceneNode`, not the actual faulting `pc` —
   the fault itself is one level deeper, in an unresolved leaf/inlined
   helper the unwinder can't name). `decisionN` was 9741 (s194) and 9788
   (s199) — close enough that the specific scene-node/asset that triggers
   this is probably loaded/walked at a fairly fixed point during mission
   startup (not a random late-game state). If a source read alone doesn't
   pin the exact statement, consider a bounded per-call counter/log
   (`ROGUESQ_LOG_PROCESS_SCENE_NODE_PTR`, one line per pointer computed
   without the normal sign-extend path) to narrow it empirically, batched
   into the SAME build as any guard you add — don't spend a separate
   build-run cycle just to locate it if you can guard defensively instead.
3. **Guard the deref** once located: same RDRAM-range-sanity-check +
   logged-bail pattern as every other guard in this project
   (`rs_malloc`/`rs_free`/`scene-node-ptr`/`scene-node-cache`/s199's new
   `video-frame-tick-guard`). New env var suggestion:
   `ROGUESQ_LOG_PROCESS_SCENE_NODE_GUARD`. If the exact call site can't be
   isolated with confidence, a broader defensive pass across
   `processSceneNode`'s pointer derefs (same "trade precision for
   coverage" tradeoff s199 used for `runVideoFrameTick`) is an acceptable
   fallback — but try for precision first this time, since the register
   evidence already narrows the search a lot more than `runVideoFrameTick
   +1568` ever did.
4. Regenerate (`make_elf.py` -> `N64Recomp` -> `fixup_game_funcs.py` ->
   `cmake --build build -j8`, `DEVELOPER_DIR=/Applications/Xcode.app/
   Contents/Developer` for Metal), verify the patch applied exactly once
   (grep the regenerated `funcs_4.c` for your new guard, count should match
   the number of sites you patched — `fixup_game_funcs.py` is
   non-idempotent).
5. Soak (copy `scratch/agent/run_videoframetickguard2.sh` — it's a clean,
   working driver with the full standard env block plus
   `ROGUESQ_LOG_VIDEO_FRAME_TICK_GUARD=1` already set from s199 — add your
   new guard's env var, rename the tag). Discriminating outcomes:
   - **Guard fires with sane fields, soak reaches further than
     decisionN=9788 or completes clean** → strong positive signal, write up
     as likely-fixed pending a 2nd soak.
   - **Guard fires but crash still happens right after** → bail target is
     unsafe, needs a different reentry point.
   - **0 fires, crash recurs at the SAME +8772 offset** → guard missed the
     actual faulting site, don't guess again — narrow further with the
     counter/log approach from step 2 before re-guessing.
   - **0 fires, no recurrence, dies to something else** → informative clean
     pass; if it's a THIRD clean pass on `runVideoFrameTick+1568`'s old
     death zone (see item -47.5 in CURRENT-TRUTH), that completes THAT
     item's 3-pass bar as a nice side effect — note it either way.
6. Whatever the outcome, update `PORTING-STATE.md` (new session entry),
   `docs/CURRENT-TRUTH.md` (both `-48` and `-47.5` entries' status), and
   this file, per the exit contract.

## Do not

- Do not re-touch the s123/s131 `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`,
  the s197 `SCENE_NODE_CACHE_GUARD`, the s190 `scene-node-ptr-guard`, the
  s196 `REINTERPRET_TILE_GUARD`, or s199's new `video-frame-tick-guard` — all
  correct-per-spec, all still 0-fire, none has new evidence against it this
  session. Only revisit `video-frame-tick-guard` if a soak while working
  THIS item happens to reach past decisionN~9800 and either fires it or
  reproduces `+1568` again (informative either way, log it, don't
  proactively chase it).
- Do not repeat s193's hand-rolled ARM64 decoder approach — already proven
  untrustworthy once, and this session's register-file evidence (from s194)
  makes it unnecessary for this specific bug anyway.
- Do not chase the 23rd-class `waitForAnyAudioSlot` SIGSEGV or the
  `evalCubicSplineAtTime` SIGBUS family this iteration unless THIS
  session's soak dies to one of them AGAIN after exhausting budget on
  `processSceneNode+8772` — both remain open, flagged, lower priority.

## Environment notes (carried forward, still current)

- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`) confirmed STILL blocked
  as of s199 (`otool -tv` returns "This command requires approval", no
  human present in this non-interactive session to clear it) — re-verify
  fresh next session only if something about the environment seems to have
  changed; otherwise trust this citation and don't re-spend the check.
- The crash handler dumps siginfo + full ARM64 register file on every
  SIGSEGV/SIGBUS/SIGABRT (`src/main/main.cpp`) — check `[CRASH][siginfo]`/
  `[CRASH][mcontext]`/`[CRASH][vifs-snapshot]` lines first, plus the
  backtrace lines immediately below them. This is how s194 root-caused
  `processSceneNode+8772`'s mechanism with zero disassembly — use the same
  approach for the actual faulting `pc` (one frame deeper than the `lr`
  the backtrace shows) if you need to narrow further.
- `N64Recomp/fixup_game_funcs.py` is non-idempotent — running it twice
  duplicates every patch.
- Any edit under THIS repo's `lib/` needs `./submodule-patches/export.sh` +
  commit in the SAME session. `N64Recomp` and `rogue_squadron64` are
  SEPARATE checkouts outside this repo, NOT `lib/` submodules — their
  uncommitted changes (including s199's `fixup_game_funcs.py` guard) are
  flagged for the user, not this session's call to commit.
- Re-running the same soak script/tag overwrites the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
  `run.log` files are multi-GB; NEVER `Read` or `cat` them whole — always
  `grep`/`sed -n` for specific line ranges.
- Running scripts under `RogueSquadron64Recomp/tools/agent/*.sh` /
  `scratch/agent/*.sh` directly gets denied — prefix with `zsh`.
- Compound `cd ... && zsh ...`/`cd ... && cmake ...` gets denied in ONE
  Bash call, and even a single `cd foo && git status` in one call can get
  auto-flagged for approval on some directories — prefer separate Bash
  calls (one `cd`, then the next command in its own call; cwd persists
  across calls) or wrap the whole thing in `zsh -c "..."` (matches the
  `Bash(zsh:*)` allow rule as a single command).
- Block on a soak by launching with `run_in_background: true` and calling
  `TaskOutput(task_id, block=true, timeout=300000-480000)` — do not end the
  turn while a background soak is still running. A `<task-notification>`
  also arrives automatically on completion.
- Heredocs get rejected by this session's Bash tool — use the Write tool
  instead, including for large PORTING-STATE.md appends (write a tmpfile
  with the Write tool, then `cat tmpfile >> PORTING-STATE.md` — the file
  itself is over 1.2MB, too large for the Edit tool's read-first
  requirement, and over the Read tool's 256KB single-read limit).
- `/scratch/` is entirely gitignored except `scratch/agent/NEXT.md`,
  `OUTCOME`, `STATUS` — new soak scripts/logs never need `git add`.
- `scratch/agent/STATUS`/`OUTCOME` get reset to `WORKING`/deleted at the
  START of each iteration by the harness — finding them in that state at
  session start is normal, not evidence of a crashed prior session.
- Uninformative soaks happen (s199 soak 1 died at decisionN=440 to an
  unrelated known crash, before even reaching VI width 1024) — don't
  read too much into a single early/unrelated death; just re-run once
  more, same as s199 did.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is now well over the ~35 KB CLAUDE.md budget and
exceeds the Read tool's 256 KB single-read limit (confirmed s195, still
true s199 — read it with `grep`/`sed -n`, never a plain whole-file `Read`).
Migrate durable mechanism/architecture material to `PROJECT-OVERVIEW.md`
and prune superseded detail, paired with a real experiment — flagged for
many sessions without action, escalating.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this session's commit
scope. Still flagged for the user, not committed autonomously.
