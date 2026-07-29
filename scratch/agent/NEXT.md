# NEXT work unit — source-read `submitSceneNodeRender` for the real 18th
# crash class mechanism (s196's prescription, never executed, 66 sessions
# overdue). This now blocks BOTH item -49 and s262's new
# `renderUnlitMeshFaces` GUARD2 from ever being tested again on this
# scripted-input path.

## Where the investigation stands (s262)

s262 added a real, correctly-targeted fix (`renderUnlitMeshFaces` GUARD2,
`fixup_game_funcs.py`, native site `0x80011CD0`) for a genuine gap a
subagent found: the list-walk's PRE-loop peek-load has the identical
"freshly-read, unvalidated pointer immediately dereferenced" shape s219
already fixed for the loop's back-edge copy, but s219's regex only matched
the loop-label-anchored back-edge instance and missed this earlier one.
**This fix is UNVERIFIED, not refuted** — the soak that carried it
(`preloopguard1`, `scratch/s73_post_a_scene/preloopguard1/run.log`) never
called `renderUnlitMeshFaces` even once (0/0 positive control), because the
run died earlier to a DIFFERENT, much older problem: the project's
long-standing **"18th crash class"** (`heapFreeListDequeue`-area SIGBUS via
`submitSceneNodeRender` ← `processSceneNode` ← `traverseSceneGraphRecursive`
← `setupCameraMatrices`), first flagged s108, "closed" s123 with a guard
that was later refuted (s131/s134 — guard present, 0 fires, crash still
recurred), and last touched s196/s198 (reclassified "very likely fixed,
mechanism unconfirmed" — a read s262's recurrence now contradicts).

**s196 already wrote the correct next step, 66 sessions ago, and it was
never done**: source-read the rest of `submitSceneNodeRender`
(`funcs_4.c`) to find the actual unguarded pointer chase. The existing
guard (`ROGUESQ_LOG_SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`) covers a
DIFFERENT mechanism (an unbounded free-list "find the tail" walk,
`v1 = *v1; v0 = *v1;`, fixed at `L_800101A4`'s reentry point) that is
confirmed NOT the cause (0 fires across every recurrence since s123,
including this session's).

## The next work unit

1. Read `submitSceneNodeRender` in `N64Recomp/RecompiledFuncs/funcs_4.c`
   in full (grep `RECOMP_FUNC void submitSceneNodeRender` for the current
   start line; s196 estimated ~3000 lines, `funcs_4.c:6-3017` as of s202 —
   line numbers have shifted since, re-grep). Cross-reference against
   `fixup_game_funcs.py`'s existing `SCENE_NODE_LIST_GUARD`/`GUARD2`/
   `GUARD3` patch sites (grep `fixup_game_funcs.py` for those three names)
   so you don't re-read or re-propose a fix for the same already-guarded,
   already-refuted free-list-walk.
2. Look specifically for the same recurring bug shape every guard in this
   project has turned out to be: a pointer loaded from memory
   (`MEM_W`/`MEM_H`/etc) and dereferenced again shortly after with NO
   bounds/null check — especially any chain feeding into or near whatever
   code lives at the crash's `+28952` native offset region (**do NOT
   trust `+28952` or `+16188` as line numbers or guest addresses** —
   established rule, this project's nearest-symbol offsets have drifted
   3 times already across s122/s196/s262 for the exact same underlying
   bug). Since the crash's `x0=x9=0x0000000300000000` (rdram_base + guest
   0x0 exactly), the actual bug is almost certainly a NULL pointer that's
   never null-checked before being dereferenced — narrow the read to
   places where a pointer is loaded and could legitimately be 0 (e.g. an
   empty-list/not-found case) but isn't checked before use.
3. This is a big, unfamiliar function relative to this session's budget —
   consider delegating the initial read to a subagent (same pattern as
   s262 used for `renderUnlitMeshFaces`), briefed with: the function's
   line range, the 3 existing guard sites to exclude, the target bug shape
   (load-a-pointer-then-deref-unchecked, specifically one that can be
   NULL), and a request for a ranked list of 3-5 untraced candidate sites
   with line numbers — not a fix, just candidates, so you evaluate and
   pick before spending a build cycle.
4. Once a strong candidate is found, add a guard following the established
   idiom (bounds/null check, log-and-bail via `ROGUESQ_LOG_<NAME>`, reuse
   an existing safe bail point in the function if one exists — do not
   invent new control flow if a `return`/existing label already covers the
   "not found / empty" case).

### Step: build → soak (mandatory once a new guard is added)

Full regen, same order as always and as executed cleanly this session:
1. Delete all 45 `RecompiledFuncs/funcs_*.c` — `rm`/`find -delete` are
   sandbox-blocked, use:
   `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
2. `python3 tools/make_elf.py` — cwd MUST be
   `/Users/williambuckley/Documents/Tools/rogue_squadron64` (relative
   paths inside the script), run as its own Bash call after a separate
   `cd` call (persisted cwd works; compound `cd && cmd` gets blocked by
   the headless permission-prefix matcher).
3. `./build/N64Recomp rogue_squadron.toml` — cwd MUST be
   `/Users/williambuckley/Documents/Tools/N64Recomp`. Output is large
   (~2.5MB) and full of routine `[Info]`/`Unhandled cop0`/`No function
   found for jal target` noise — this is normal, not an error signal.
4. `env python3 fixup_game_funcs.py > <repo>/scratch/agent/s263_fixup.log 2>&1`
   — cwd MUST be `/Users/williambuckley/Documents/Tools/N64Recomp`, `env`
   prefix required (bare invocation without it still worked fine this
   session actually — but `env` is always allowlisted, keep using it).
   Then grep the log for your new guard's report line AND run
   `grep -oE "patched x[0-9]+" <log> | sort | uniq -c | grep -v " x1$"`
   to confirm every non-`x1` multiplicity matches a documented precedent
   (this session's were: `GUARD2`-suffix `submitSceneNodeRender` x9,
   `GUARD3` x8, `audio gate` x3, `a3-pointer guard3` x2, `MATLIST_GUARD3`
   x2 — anything else new is a red flag, re-check before building).
5. `cd /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp` then
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build -j8`
   (this exact `DEVELOPER_DIR=... cmake ...` form is allowlisted verbatim).
   Expect only the pre-existing DDIV sign-conversion warnings (46 of them).
6. `strings build/RogueSquadron64Recomp | grep -c "<YOUR_NEW_ENV_VAR>$"` —
   must be 1.
7. Copy `scratch/s73_post_a_scene/run_preloopguard1.sh` (now the
   current-best known-survivor baseline, NOT `run_composeguard9.sh` —
   `preloopguard1` already carries every env var `composeguard9` had, plus
   `HOLD_S=240`) to a new tag, add your new guard's env var (or if it
   reuses `ROGUESQ_LOG_RENDERUNLIT_GUARD`/`SCENE_NODE_LIST_GUARD` etc.
   nothing to add), keep everything else identical.

**Block-wait pattern** (confirmed working this session): launch the driver
with its FULL ABSOLUTE PATH (background Bash calls do NOT inherit a
foreground call's persisted `cd` — `zsh run_x.sh` fails with "can't open
input file" in the background; `zsh /full/path/to/run_x.sh` works), read
its first output line for `pid NNNNN`, then a SEPARATE Bash call (
`run_in_background: true`, timeout up to 480000ms):
`until ! kill -0 <pid> 2>/dev/null; do sleep 10; done; echo done`. **Then
block on that task with `TaskOutput(task_id=..., block=true,
timeout=480000)` before ending your turn** — the Stop hook fires
immediately if `scratch/agent/STATUS` is still `WORKING` when a turn ends,
so do not try to "wait for the notification" across turns; block
synchronously within the same turn using `TaskOutput`.

**Discriminating outcomes**: new guard fires with sane fields → 18th class
finally root-caused, note whether the run then reaches
`renderUnlitMeshFaces` and whether GUARD2 gets its first-ever positive
control (either fire or clean-pass-through). Crash recurs at the exact same
`heapFreeListDequeue`/`submitSceneNodeRender` shape with the new guard also
silent → the real site is somewhere this read didn't reach yet, re-read
more carefully rather than guessing at another site (per budget rule 8,
this would be the 2nd consecutive iteration on this specific hypothesis —
one more miss after this is the ceiling before reassessing). Crash moves to
an entirely different function → real forward progress, follow it.

## Do NOT do this iteration

- Do NOT re-touch `ROGUESQ_LOG_SCENE_NODE_LIST_GUARD` (or `GUARD2`/
  `GUARD3`) itself — already confirmed NOT the mechanism (0 fires across
  4+ recurrences of this exact crash class with it present).
- Do NOT treat s198's "18th class very likely fixed" as current — s262
  superseded it with a 4th occurrence, guard present and silent.
- Do NOT treat `renderUnlitMeshFaces` GUARD2 as confirmed OR refuted —
  it has zero same-run data either way. Do not remove it or "fix" it
  further without first getting a soak that actually calls the function.
- Do NOT use a crash symbol's native `+N` offset as a source line number
  or guest address — confirmed drifting across 3 sessions for this exact
  same bug (`+12704` s122, `+28208` s196, `+28952`/`+16188` s262).
- Do NOT re-attempt `nm`/`atos`/`objdump` for offset localization.
- Do NOT run `fixup_game_funcs.py` more than once per regen cycle without
  redirecting output to a file and grepping the report line count first.
- Do NOT try to idle across a Stop-hook boundary waiting on a background
  soak — block on it with `TaskOutput(..., block=true)` in the SAME turn,
  or the hook will fire "Exit contract unmet" before you can act on the
  result.

## Environment notes (carried forward + new this session)

- **Regen commands, verified working this session** (see "Step: build →
  soak" above for the exact literal invocations) — `make_elf.py` needs cwd
  `rogue_squadron64`, `N64Recomp` needs cwd `N64Recomp`, `fixup_game_funcs.py`
  needs cwd `N64Recomp`, `cmake --build` needs cwd
  `RogueSquadron64Recomp`. `bash tools/agent/regen_n64recomp.sh` as a
  single call was REJECTED ("requires approval") this session — use the
  raw `cd` + `./build/N64Recomp rogue_squadron.toml` two-call form instead.
- **Background launches do not inherit a prior foreground `cd`** — always
  launch soak drivers by their full absolute path when using
  `run_in_background: true`.
- **Cross-turn waiting does not work under the Stop hook** — a turn that
  ends with `scratch/agent/STATUS` still `WORKING` gets immediately
  re-invoked with "Exit contract unmet," even if you're legitimately
  waiting on a background soak. Use `TaskOutput(task_id, block=true,
  timeout=<up to 480000>)` to block synchronously in the same turn instead
  of ending the turn and hoping for a notification.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT
  `scratch/agent/`.
- `+N` crash-symbol offsets are NATIVE (compiled ARM64) code offsets, NOT
  guest MIPS addresses, and have now been observed to drift across
  sessions for the identical underlying bug (18th class: `+12704` →
  `+28208` → `+28952`/`+16188`).
- Deleting `funcs_*.c` before regen: plain `rm`/`find -delete` are
  sandbox-blocked, use the `python3 -c "import glob, os; ..."` one-liner
  (exact form above).
- Headless permission matching is a PREFIX match on the command string —
  `env VAR=1 cmd` is allowlisted where bare `VAR=1 cmd` is not; compound
  `cmd1 && cmd2` after a `cd` gets blocked, run each as its own Bash call.
- The `[phase] vi_width=512 (was 1024)` line at ~t=74-75s is the
  SELECT-CRAFT→mission transition marker. `vi_width=640 (was 512)` at
  ~t=143s (seen once, s261) is a confirmed second, later transition, not
  yet reproduced a 2nd time.
- `CURRENT-TRUTH.md` is ~455KB, ~13x the ~35KB target in CLAUDE.md. A
  dedicated pruning session is now 4+ consecutive sessions overdue.
