# NEXT work unit — re-run `dequeueguard1` unchanged to get the 2nd
# independent data point on s263's crash-free result (iron rule 4). NO
# CODE CHANGES this iteration unless the re-run itself surfaces a new gap.

## Where the investigation stands (s263)

s263 executed s196's 66-session-overdue prescription: sourced-read
`submitSceneNodeRender` (delegated to a subagent, then independently
verified by reading `heapFreeListDequeue` itself, `funcs_3.c:15571`) and
found a genuinely new, previously-unguarded gap: `heapFreeListDequeue`
unconditionally dereferences its first argument (`a0`) at native
`0x8000D118` with ZERO null check anywhere in its body, and both call
sites in `submitSceneNodeRender` (`0x800104A8`, `0x80010CD8`) pass a
freshly-loaded, never-validated node field (`ctx->r17+4`) straight into
that argument. This is DIFFERENT from the 5 existing guards in this
function (`SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
`MATLIST_GUARD1-3`), which all validate the node pointer `ctx->r17`
itself, not this `+4` field — a field that can be a legitimate valid-range
node's own field reading exactly NULL, matching the crash's own repeated
`x0=x9=0x0000000300000000` (guest 0x0) fault signature.

Added `DEQUEUE_GUARD` (env var `ROGUESQ_LOG_SCENE_NODE_DEQUEUE_GUARD`,
`N64Recomp/fixup_game_funcs.py`, 2 sites, both `after_7`/`after_17` bail
targets). Build clean (fixup report: `DEQUEUE_GUARD patched x2`, no
anomalies; `cmake --build` 0 errors, 46 expected DDIV warnings; `strings`
count = 1).

**Soak result (`dequeueguard1`, `scratch/s73_post_a_scene/dequeueguard1/run.log`,
164M lines)**: 3 attempts. 1st/2nd died pre-title-screen to the unrelated,
already-catalogued 23rd crash class (`waitForAnyAudioSlot+244`) — per
established convention, discarded/not counted. **3rd attempt survived the
FULL 293s scripted run (268s hold, all 5 stick inputs delivered) with ZERO
crash** — longest survival in this investigation's history (previous best
143.1s, s261). All 3 phase transitions reached in one run for the first
time (`vi_width=1024`@45.5s, `=512`@74.8s, `=640`@142.9s).

**But `DEQUEUE_GUARD` itself got 0 fires** — the null-field condition it
guards never actually occurred this run. This means the crash-free result
is NOT proof the guard fixed anything; it's a null result on the
instrument, with a genuinely positive but UNEXPLAINED outcome alongside it
(iron rule 1: not confirmed). `renderUnlitMeshFaces` was STILL never
called (0/0 on `unlit-mesh-tracer`), so item -49's GUARD2 (s262) remains
completely untested either way.

## The next work unit

**Just re-run the soak. Do not add a new guard or edit any code this
iteration unless the re-run itself surfaces a new, specific gap to fix.**

1. Launch `zsh /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/scratch/s73_post_a_scene/run_dequeueguard1.sh`
   in the background (full absolute path — background launches do not
   inherit a prior foreground `cd`). Read the first output line for
   `pid NNNNN`.
2. If it dies pre-title-screen to `waitForAnyAudioSlot` again (check
   `grep -n "pc-symbol" .../dequeueguard1/run.log`), that's the unrelated
   23rd class — discard and re-run, same as s263 (up to ~3 attempts is
   normal per precedent, not a budget violation; the 18th-class hypothesis
   clock only starts once a run actually gets INTO the mission).
3. Once a run reaches at least `vi_width=1024` (45s mark), it counts as a
   real attempt on the 18th-class question. Block on the process with a
   SEPARATE Bash call (`run_in_background: true`, `until ! kill -0 <pid>
   2>/dev/null; do sleep 10; done; echo done`), then
   `TaskOutput(task_id=..., block=true, timeout=480000)` in the SAME turn
   (cross-turn waiting does not survive the Stop hook — see below).
4. Check 3 things in the resulting log: (a) any `[CRASH]` line at all —
   if none and driver reports `hold done wall=...`/`done wall=...` with no
   `exit=2`, that's a 2nd clean run, promote the conclusion; (b)
   `grep -c "scene-node-dequeue-guard"` — expect 0 again if clean, but if
   nonzero even on a clean run that's useful (guard fired but run
   recovered — means the field WAS null and the guard's bail path works);
   (c) `grep -c "unlit-mesh-tracer"` and `renderunlit-guard` fires — if
   `renderUnlitMeshFaces` finally gets called, that's GUARD2's first real
   test, check its fire count and whether the run continues past it.

## Discriminating outcomes

- **2nd clean run (no crash, DEQUEUE_GUARD still 0 fires)**: iron rule 4
  satisfied — "18th class no longer reproduces on this scripted-input
  path" becomes a real, two-source conclusion. Move `DEQUEUE_GUARD` from
  "plausible fix, unverified by firing" to "the run environment changed
  such that the bug no longer triggers, cause of the CHANGE still
  uncertain (could be this session's regen incidentally shifting
  timing/layout)." New top priority becomes: get a soak that reaches
  `renderUnlitMeshFaces` for GUARD2's first-ever real test (increase
  `HOLD_S` further, or investigate why the 3rd `vi_width=640` transition
  doesn't lead into the scene that calls it).
- **Crashes again, exact same `heapFreeListDequeue`/`submitSceneNodeRender`
  shape, `DEQUEUE_GUARD` still silent**: 2nd consecutive miss on this
  hypothesis (budget rule 8 ceiling). STOP adding guards blind — write a
  fresh hypothesis/evidence table into this file: what does the crash's
  new native offset say, does the backtrace differ at all, is there a
  THIRD gap in this same free-list idiom neither this session nor s123/
  s131/s136/s197/s253 caught? Consider re-reading `heapFreeListDequeue`'s
  own body more carefully (it's ~800+ lines, `funcs_3.c:15571`+) rather
  than re-reading `submitSceneNodeRender` a 3rd time.
- **Crashes at a genuinely different site/function**: real forward
  progress regardless of DEQUEUE_GUARD's fire count — follow the new
  crash, same as every prior session in this chain has done.

## Do NOT do this iteration

- Do NOT add a 3rd guard to this free-list idiom without first getting
  the 2nd soak's result — you don't yet know if the 1st guard needs
  strengthening or if the class is just gone/racy.
- Do NOT re-touch `SCENE_NODE_LIST_GUARD`/`GUARD2`/`GUARD3`/cache-guard/
  `MATLIST_GUARD1-3` — all confirmed NOT the mechanism (0 fires across
  every recurrence including s263's).
- Do NOT treat s263's crash-free run as "18th class fixed" yet — single
  sample, guard itself didn't fire, could be coincidence/timing.
- Do NOT treat `renderUnlitMeshFaces` GUARD2 (s262) as confirmed OR
  refuted — still zero same-run data either way after 2 more sessions.
- Do NOT use a crash symbol's native `+N` offset as a source line number
  or guest address — confirmed drifting across many sessions.
- Do NOT idle across a Stop-hook turn boundary waiting on a background
  soak — block with `TaskOutput(..., block=true)` in the SAME turn.
- If 2 consecutive soak attempts die to the unrelated 23rd class
  (`waitForAnyAudioSlot`) again, a 3rd attempt is normal (matches s263's
  own pattern) — don't treat that as a budget violation, but if it
  happens a 4th+ time in a row, that itself may be worth a note (is the
  23rd class less racy than believed in the current build?).

## Environment notes (carried forward, all still valid)

- Regen commands: `make_elf.py` needs cwd `rogue_squadron64`, `N64Recomp`
  needs cwd `N64Recomp`, `fixup_game_funcs.py` needs cwd `N64Recomp`,
  `cmake --build` needs cwd `RogueSquadron64Recomp`.
- Delete `funcs_*.c` before regen via:
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
  (`rm`/`find -delete` are sandbox-blocked).
- Background launches do NOT inherit a prior foreground `cd` — always
  launch soak drivers by full absolute path when using
  `run_in_background: true`.
- Cross-turn waiting does not work under the Stop hook — use
  `TaskOutput(task_id, block=true, timeout=<=480000)` synchronously in the
  same turn, never end a turn hoping for a notification while
  `scratch/agent/STATUS` is still `WORKING`.
- Soak driver scripts live under `scratch/s73_post_a_scene/`, NOT
  `scratch/agent/`. The current-best baseline script is now
  `run_dequeueguard1.sh` (supersedes `run_preloopguard1.sh`).
- `+N` crash-symbol offsets are NATIVE (ARM64) code offsets, NOT guest
  MIPS addresses, and drift build-to-build for the identical bug.
- `CURRENT-TRUTH.md` is ~455KB+ (growing), ~13x the ~35KB target in
  CLAUDE.md. A dedicated pruning session is now 5+ consecutive sessions
  overdue — still not this iteration's job unless the soak re-run itself
  is a quick null (in which case, and ONLY if there's clear leftover
  budget, consider it as a 2nd unit, but the soak re-run is the priority).
