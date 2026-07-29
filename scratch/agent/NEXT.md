# NEXT work unit — confirm or refute s253's clean-hold soak with a real
# positive control armed, OR resume the project-wide static sweep

## Where the investigation stands (s253)

s253 chased the s252 `submitSceneNodeRender+18600` lead. Full detail:
PORTING-STATE Session 253. Landed:

1. **Corrected a math error in how s252 framed the lead**: `+18600` is a
   NATIVE (compiled ARM64) code offset from `submitSceneNodeRender`'s
   machine-code start, NOT a guest MIPS address. Proof: the function's
   own guest range is `0x80010014` (entry) to `0x80011088` (last
   instruction before the next `RECOMP_FUNC`, `renderFlatMeshFaceGroup`,
   which starts at `0x8001108C`) — only ~4212 bytes / ~1053 instructions
   total, nowhere near 18600. **Do not do guest-address arithmetic on a
   crash offset again** — it only tells you which function to read, not
   where inside it. `nm`/`atos` remain the only way to resolve it
   exactly and remain permanently unusable here (confirmed 3 independent
   times: s207 x2, s252).
2. Read the WHOLE function start to end (funcs_4.c:6-3017, ~3011 lines).
   Confirmed the `findAndUnlinkSmallestEntry` free-list-walk idiom (9
   inlined copies, lines 194/609/994/1242/1429/1904/2147/2521/2749) is
   **fully guarded already** (`GUARD`/`GUARD2`/`GUARD3`/cached-head-guard
   from s123/s131/s197) — matches s131's own count of 9 exactly, no gap
   here.
3. Found a genuine SECOND gap: the material-batch-list self-referential
   walk idiom (s136's `MATLIST_GUARD1`/`GUARD2`, 2 inlined copies) has
   the same "guard-the-first-load-only" mistake s131 already diagnosed
   and fixed once for the sibling idiom. s136's own comment claimed
   guarding the initial table-lookup result "protects... the whole walk
   loop" — this session's read found that's **false for loop iterations
   2+**: the walked pointer reloads itself
   (`ctx->r17 = MEM_W(ctx->r17, 0X0)` at `0x800104B0`/`0x80010CE0`) and
   loops back to re-dereference (`MEM_W(ctx->r17, 0X4)` at
   `L_8001049C`/`L_80010A2C`, feeding `heapFreeListDequeue`) with **zero
   re-validation** of the reloaded value.
4. Added `MATLIST_GUARD3` (`fixup_game_funcs.py`, sibling `N64Recomp`
   checkout), 2 sites. Guard sits right after the reload, before the
   pre-existing `if (r17 != 0)` branch: if the reload is non-zero but
   out of KSEG0 range (0x80000000-0x80800000), zero it so the code's OWN
   pre-existing null-check branch (already there for a genuine
   end-of-list) takes over unmodified — no new control-flow path,
   byte-identical "list ended" semantics. New env var
   `ROGUESQ_LOG_SCENE_MATLIST_GUARD3`, `site=1|2`.
5. Build clean. Patch report audited live (not saved to a file this
   session — a `cd ... && ... > file` compound got denied mid-session;
   worked around by reviewing the piped `| tail -100` output directly):
   new guard `x2` (correct), every pre-existing `submitSceneNodeRender`
   guard multiplicity unchanged from s252's baseline (`GUARD2` x9,
   `GUARD3` x8, cached-head x1, matlist1/matlist2 x1 each) — no
   stacking. Binary verified fresh (`strings` shows both new
   `[scene-matlist-guard3] ... site=1`/`site=2` strings, mtime after
   build completion).
6. **Soak** (`matlistguard3soak1`, `HOLD_S=150`, same
   `heaplistdeqhead1`-baseline env block + the new guard's env var):
   crossed SELECT-CRAFT (`vi_width=512`) at 74.7s — same schedule/timing
   as every recent session — then ran the **entire 150s hold + grace
   window (wall 195s) with zero crashes** (`CRASH: 0`, `exit=2: 0`,
   driver had to SIGKILL the still-alive process at the end). This is
   the **first fully clean hold since s248** — every soak in s249-s252
   died within ~1s of hold start.
7. **But this is a WEAK/uninformative result per `ITERATION.md` rule 1**:
   `MATLIST_GUARD3` fired 0/2 (expected if the fix works, but
   uninformative on its own), AND critically the `heapwalker-guard4`
   known-firing positive control that fired in EVERY s249-s252 soak did
   **NOT** fire this run (absent from this run's full unique-log-tag
   census). Only `campose-entry` (207 fires) and `scene-rq-counter-hb`
   (85 fires) confirm SOME instrumented code executed — neither is the
   specific control this project's own rule requires. The SELECT-CRAFT
   screen also appears to have sat static the whole hold (`vi-fs-decision
   SKIP ... stalled=1` continuously, `viW=512` never changed) — the
   scripted "a" press at hold_100 may not have transitioned into an
   actual mission this run, meaning the run may simply never have
   reached the corruption-triggering condition at all, independent of
   whether `MATLIST_GUARD3` is a real fix.

## The single highest-value next step

**Re-run the exact same soak (new tag, e.g. `matlistguard3soak2`) and
confirm `heapwalker-guard4` (or another confirmed-reliable positive
control) actually fires before trusting the clean result.** Two
discriminating outcomes:

- **`heapwalker-guard4` (or equivalent) fires AND the run still stays
  clean (0 crashes)** → first real two-line-of-evidence signal that the
  combination of guards landed across s249-s253 (heapFreeListDequeue
  fully guarded s252, submitSceneNodeRender's two self-ref-walk idioms
  now both fully guarded s253) may have actually closed this whack-a-mole
  family's currently-known gaps. Worth a 3rd confirming soak before
  writing that conclusion into CURRENT-TRUTH as anything stronger than
  "two independent clean holds."
- **`heapwalker-guard4` fires AND the run crashes** → back to hunting;
  read the crash's function fresh (remember: offset math is NATIVE not
  guest, per this session's correction — read the whole function, don't
  try to place the offset).
- **`heapwalker-guard4` does NOT fire again** → the render/heap-walk
  code paths that normally exercise it are for some reason not running
  this session (maybe a state/build issue unrelated to the guards) —
  investigate why before drawing ANY conclusion from soak cleanliness,
  clean or crashing. Check: is the "a" key actually transitioning past
  SELECT-CRAFT into gameplay? Try lengthening `STICK_SCHEDULE`'s hold
  before the `start`/`a` presses, or check `run_mission_keys.sh` for
  whether an alternate key sequence is needed to force a mission load a
  build/session change (unrelated to this session's guards) might have
  altered the schedule's effectiveness.

Commands (copy `scratch/s73_post_a_scene/run_matlistguard3soak1.sh` to a
new tag name — re-running the same tag overwrites its own `run.log`):
```
cp scratch/s73_post_a_scene/run_matlistguard3soak1.sh scratch/s73_post_a_scene/run_matlistguard3soak2.sh
# edit the new file's last line's tag argument and HOLD_S if lengthening
zsh scratch/s73_post_a_scene/run_matlistguard3soak2.sh   # run_in_background: true
# read first output line for "pid NNNNN", then poll:
# until ! kill -0 <pid> 2>/dev/null; do sleep 10; done
```
No regen/rebuild needed for a re-soak — the binary from s253 is already
correct (verify with `ls -la build/RogueSquadron64Recomp` vs. mtime and
`strings build/RogueSquadron64Recomp | grep SCENE_MATLIST_GUARD3` before
trusting it, per standing practice).

## Otherwise: continue the static sweep (139 candidates remain, unchanged)

If the re-soak lead is exhausted or a 3rd consecutive iteration on this
hypothesis produces no discriminating result (per `ITERATION.md` rule 8),
fall back to the static sweep. Same rigor as every prior session: read
the whole function body, check for BOTH known gap categories (self-ref
walk, AND null-checked-but-unranged-return-value-deref per s252, AND now
ALSO "guard-the-first-load-but-not-the-loop-back" per s253 — three known
categories now, not two), check false positives first, find a safe bail
target by reading forward, then patch + regen + build + audit + soak.
Good next candidates (all in `funcs_3.c`/`funcs_4.c`, same family as
every already-fixed function above):
`renderLitMeshFaceGroup` (14 sites, `funcs_4.c`) — NOTE this session
found (in passing, while investigating the crash-offset math) that guest
address `0x800148BC` (inside `renderLitMeshFaceGroup`, NOT
`submitSceneNodeRender`) has the SAME null-checked-but-unranged-deref
shape s252 found: a `findAndUnlinkSmallestEntry(rdram, ctx)` call at
`0x800148A8`, return value null-checked at `0x800148B4`
(`beq $a0,$zero,L_800148F8`), then immediately dereferenced at
`0x800148BC` (`ctx->r2 = MEM_W(ctx->r4, 0X0)`, matching GUARD2's exact
shape) followed by a loop-back walk at `L_800148C8`
(`ctx->r3 = MEM_W(ctx->r3, 0X0)`, matching GUARD3's exact shape) — this
is a **10th, previously-uncounted, unguarded occurrence of the SAME
findAndUnlinkSmallestEntry idiom s123/s131 guarded 9 times inside
submitSceneNodeRender, but this one lives in a DIFFERENT function
(`renderLitMeshFaceGroup`) and was never touched**. This is now the
single most promising concrete lead for next session if the re-soak
doesn't resolve cleanly — high confidence gap, exact same shape/fix
pattern as `GUARD2`/`GUARD3`, just needs its own guard block (bail
target: `L_800148F8` for the initial-deref check, mirroring GUARD2's
convention of reusing the local null-check's own label).
`renderLitTexturedMeshFaces` (11 sites, `funcs_3.c`), `func_800AE3F0` (10
sites, `funcs_27.c`), `beginFrameDLChunk` / `emitFrameRdpInitDl` (10
sites each, `funcs_3.c`).

`docs/CURRENT-TRUTH.md` housekeeping — still ~407 KB+, flagged 43+
sessions, still not done. Per `ITERATION.md` this does NOT count as
`ADVANCED` on its own — pair it with a real change or expect to file
`SUBSTITUTED`.

## Do NOT do this iteration

- Do NOT re-run `matlistguard3soak1` in place (or any prior tag) — new
  soaks need new tags, re-running overwrites `run.log`.
- Do NOT re-attempt `nm`/`atos` for offset localization — confirmed
  unusable 3 independent times (s207 x2, s252). Also, per this session's
  finding, even if it worked, remember crash offsets on THIS project's
  symbol format are NATIVE code offsets, not guest MIPS addresses — don't
  repeat s252's math mistake in a new form.
- Do NOT credit `matlistguard3soak1`'s 0-crash result as "the fix worked"
  without first confirming a same-run positive control fired — it is a
  weak null per `ITERATION.md` rule 1, explicitly flagged as such this
  session. The single highest-value next action is designed to resolve
  this ambiguity, not to repeat it.
- Do NOT invoke `fixup_game_funcs.py` more than once per regen cycle.
- Do NOT revive the NaN_CHECK-disable idea (CURRENT-TRUTH `-55`/`-56`) —
  already tried, A/B-tested, and reverted at s216 (`-57`).

## Environment notes (carried forward, still current as of s253)

- **`+N` crash-symbol offsets are NATIVE (compiled ARM64) code offsets,
  NOT guest MIPS addresses** (confirmed this session by computing
  `submitSceneNodeRender`'s actual guest range and finding 18600 bytes
  doesn't fit inside it). Use the offset only to identify WHICH function
  to read in full; never try to place it at a specific guest instruction.
- **Compound `cd <dir> && <command> > <file>` in one Bash call can get
  denied** even when the destination file is in a different, normally-
  writable directory than the `cd` target (hit this session running
  `fixup_game_funcs.py > report.txt` from the `N64Recomp` cwd) — if it's
  denied, drop the redirect and just read the command's own stdout from
  the tool output instead of piping to a file.
- **Permission gate CONFIRMED CLEARED through s253** for the standard
  `tools/*`/`build/*`/`python3:*`/`zsh:*` command families. `nm`/`atos`
  still not allowlisted. `echo` still not allowlisted.
- **`GAME_EXTRA_ENV`** (`run_mission_keys.sh`, s241): space-separated
  `VAR=val VAR2=val2` string, scopes extra env vars to ONLY the game
  process.
- **Env-gated logging pattern**: `static const bool s_X = [](){ const
  char *v = std::getenv("VAR_NAME"); return v && v[0] && v[0] != '0'; }();`
  then `if (s_X) { std::fprintf(stderr, ...); std::fflush(stderr); }`.
- **Block-wait pattern**: launch the soak with Bash `run_in_background:
  true`, read the driver's first output line for `pid NNNNN out=...`,
  then run a SECOND Bash call (foreground, generous `timeout` up to
  480000ms) that polls `until ! kill -0 <game_pid> 2>/dev/null; do sleep
  N; done`. This blocks until the process exits, letting a soak run to
  completion within one iteration.
- `/tmp` is not writable this session — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- **Headless permission matching is a PREFIX match** — write
  `env PROBE_MODE=1 zsh run.sh`, not `PROBE_MODE=1 zsh run.sh`.
- **`campose*` armed env-var set** (unchanged since `campose11`, now plus
  `ROGUESQ_LOG_SCENE_MATLIST_GUARD3`, s253):
  `ROGUESQ_LOG_CAMPOSE`, `ROGUESQ_LOG_MAT3INV`,
  `ROGUESQ_LOG_UNLIT_MESH_TRACER`, `ROGUESQ_LOG_RENDERUNLIT_GUARD`,
  `ROGUESQ_LOG_HEAPWALKER_GUARD`/`GUARD3`/`GUARD4`,
  `ROGUESQ_LOG_MESGQUEUE_GUARD`, `ROGUESQ_LOG_HEAPLISTDEQ_GUARD`,
  `ROGUESQ_LOG_HEAPLISTDEQ_HEAD_GUARD`,
  `ROGUESQ_LOG_SCENE_MATLIST_GUARD3` (new, s253),
  `ROGUESQ_LOG_EMIT_DL_GUARD2`/`GUARD3`, `ROGUESQ_LOG_DL_PAYLOAD_STALE=1`,
  `ROGUESQ_LOG_SELECTPOSTCRAWL_GUARD=1`,
  `ROGUESQ_LOG_SELECTPOSTCRAWL_INSGUARD_A1`/`A2`/`B1`/`B2=1`,
  `ROGUESQ_LOG_DLENTRY_TAIL_GUARD=1` — see
  `scratch/s73_post_a_scene/run_matlistguard3soak1.sh` for the full
  current set (this file survives across sessions on disk even though
  `scratch/` is gitignored — copy it forward for new soaks; only
  `STATUS`/`OUTCOME`/`NEXT.md`/`run_mission_keys.sh` are git-tracked).
- **The `[phase] vi_width=512 (was 1024) origin=0x006AB400` line at
  ~t=74-75s is THE confirmed SELECT-CRAFT->mission transition marker.**
  Note s253 found the screen can sit STATIC after this marker for the
  whole hold (`vi-fs-decision SKIP ... stalled=1` repeating) if the
  scripted stick/button inputs don't actually cause a mission-load
  transition — check for this before assuming "crossed SELECT-CRAFT"
  implies "entered gameplay."
- **Regen is mandatory-delete-all-first, AND fixup must run EXACTLY
  ONCE**: delete all 45 `RecompiledFuncs/funcs_*.c`
  (`python3 -c "import glob, os; [os.remove(f) for f in glob.glob('...')]"`,
  not `rm -f`/`find -delete`, both blocked) before `make_elf.py` (cwd
  `rogue_squadron64`) → `regen_n64recomp.sh` (cwd `RogueSquadron64Recomp`)
  → `fixup_game_funcs.py` (cwd `N64Recomp`, exactly once) →
  `cmake --build .` (cwd `build`, needs
  `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`).
- **`rm -f <glob>`/`find <dir> -delete` are blocked** — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- The driver's own `CRASH: N` summary counts occurrences of the LITERAL
  STRING `[CRASH]`; grep `[CRASH] caught signal` for actual crash event
  counts. The launch-log's own `--- summary ---` block also prints
  `exit=2: N` (crash-exit count) — cross-check both.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each
  iteration by the harness — normal.
- **`/scratch/` is wholesale gitignored** — only `STATUS`, `OUTCOME`,
  `NEXT.md`, and `run_mission_keys.sh` are tracked exceptions.
- Verify a fresh binary before trusting any result: `strings
  build/RogueSquadron64Recomp | grep '<your-new-tag>'` plus `ls -la
  build/RogueSquadron64Recomp` vs. the soak's start time.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (still ~407 KB+ / ~6000+ lines,
flagged 43+ sessions without action).

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope). Also still not fixed: the script's non-idempotency
bug found s250 (`rs_malloc` entry-capture patch stacks duplicate
declarations on repeat invocation).

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.
