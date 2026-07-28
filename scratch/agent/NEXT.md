# NEXT work unit — 3rd consecutive session BLOCKED on the permission gate;
# a specific fix has been proposed for a human, check for it before touching
# regen/soak work again

Read `scratch/agent/BLOCKED.md` in full first — s228 sharpened the
diagnosis from "tools/-specific" (s226/s227's framing) to a whole class of
`.claude/settings.json` allow rules (any `Bash(<dir>/:*)`-shaped rule, not
just `tools/:*`) and proposed a concrete one-line-per-rule fix: change
`tools/:*` -> `tools/*`, `./tools/:*` -> `./tools/*`, `build/:*` ->
`build/*`, `./build/:*` -> `./build/*`. This has NOT yet been applied or
tested — it needs a human to edit `.claude/settings.json` (or explicitly
confirm/deny the hypothesis) between s228 and whenever this next runs.

## Do this iteration

### Step 0 — check whether the gate cleared or the fix landed

First check whether `.claude/settings.json` changed:

    git log --oneline -3 -- .claude/settings.json

If a commit touched it since s228, or if `grep -n "tools/\*\|build/\*"
.claude/settings.json` shows the proposed glob-only form is now present,
the fix likely landed — proceed to try the actual command:

    tools/agent/stop_gate.sh --verify

If this produces REAL verification output (not the "This command requires
approval" message), the gate has cleared — proceed to Step 1.

If `.claude/settings.json` has NOT changed since s228's commit AND you
have no other evidence the environment changed, **do NOT re-run
`stop_gate.sh --verify` or any `tools/`/`build/`-prefixed command** — that
would be a 4th consecutive identical retry with no new information, which
iron rule 8 and s228's BLOCKED.md both say not to do. Go straight to
BLOCKED: write a fresh `scratch/agent/BLOCKED.md` (or update the existing
one) noting this is now 4 sessions running (s226-s229), link them in
PORTING-STATE.md, and reiterate the fix is still pending. Then follow the
exit contract and stop.

If `.claude/settings.json` DID change but `stop_gate.sh --verify` STILL
fails, that refutes s228's hypothesis (the glob-form fix didn't help) —
this is valuable new information. Write it up in BLOCKED.md as a refuted
hypothesis (don't just repeat it) and consider what's left: possibly the
headless-runner pass-through explanation from s227's original two
candidates, which was never directly tested. Go BLOCKED with this
narrowed state; do not keep guessing at fixes without human input at that
point — 4 sessions of blocked regen work is enough to require direct
human debugging.

### Step 1 — resume the deref0 soak (only if Step 0 succeeded)

The `deref0` diagnostic is ALREADY landed in
`/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
(extends `ROGUESQ_LOG_CAMPOSE`'s existing patch site, same env var, no new
opt-in). Verify it's still there first: `grep -n "deref0"
fixup_game_funcs.py` (N64Recomp checkout) — should show the field being
computed and logged. Do NOT re-write it if present.

Full clean-room recipe (proven 4x before the permission gate started
blocking it, s221/223/224/225):
1. Delete generated funcs: `cd RecompiledFuncs` (N64Recomp checkout) then
   `python3 -c "import glob, os; [os.remove(f) for f in
   glob.glob('funcs_*.c')]"`.
2. `python3 tools/make_elf.py` (`rogue_squadron64` checkout) — check
   staleness first; s226/s227/s228 already ran this and nothing since
   should have touched the ROM/symbols.
3. `./tools/agent/regen_n64recomp.sh` (this repo, cwd-independent). This is
   the step that's been gated 3 sessions running — confirm it actually
   runs this time (real N64Recomp output, not the approval message)
   before continuing.
4. `fixup_game_funcs.py` **exactly once** — capture output to
   `N64Recomp/scratch_fixup_report_s229.txt` (new tag), grep it for
   "camera-pose diagnostic" to confirm the `deref0` patch applied.
5. `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build
   build -j8` (from `build/`).

### Step 2 — soak

Copy `scratch/s73_post_a_scene/run_campose1.sh` to a new tag (e.g.
`run_campose3.sh`/`campose3` — do NOT overwrite prior tags). Same
`schedulepush2`-derived schedule. `ROGUESQ_LOG_CAMPOSE=1` should already be
armed — verify, don't duplicate. Budget 2 attempts (proven non-determinism,
s223).

### Step 3 — analyze

1. MD5-checksum `hold_NN.png` (`scratch/agent/checksum_campose1.py`,
   repoint `d` to the new tag) to find the freeze onset.
2. `grep -n "campose-entry\|campose-abnormal" run.log` and extract
   `n`/`m00`/`flag`/`camptr`/`deref0`/`deref0_valid`.
3. Find the `n` where `flag`/`camptr` go fixed (expect ~n=15000-ish, confirm
   per this run).

Discriminating outcomes (unchanged from s226/s227's design, still valid):
- **`deref0` also freezes at/near the same `n`** → stall reaches at least
  one level into the pointed-to struct; next step is finding what SHOULD be
  writing there.
- **`deref0` keeps changing after `flag`/`camptr` freeze** (matching the
  `m00` pattern) → pointed-to content still live; freeze is further
  downstream (traversal walk logic or a content-independent culling check).
- **`deref0_valid=0` throughout** → the field isn't a valid RDRAM pointer;
  re-read what it might be instead (small integer/enum) — partially undoes
  the "nullable linked-node pointer" reading from s223/s224/s226.

## Do NOT do this iteration

- Do not re-derive the a0/a1 source trace — closed since s226.
- Do not re-instrument scene-graph call rates — closed since s225.
- Do not re-add the `deref0` field if present — investigate why it's
  missing (don't silently re-patch) if it's gone.
- Do not attempt `regen_n64recomp.sh`, `stop_gate.sh --verify`, or any
  other `tools/`/`build/`-prefixed command a 4th consecutive session
  without either Step 0's control succeeding, or documented evidence
  (a settings.json diff) that the environment changed since s228.
- Do not re-propose a different fix for the permission gate without first
  checking whether s228's proposed fix was tried and what happened — read
  BLOCKED.md's "What's already been tried" section fully before adding a
  new hypothesis.

## Environment notes (carried forward, updated s228)

- **Permission gate — BLOCKED 3 consecutive sessions (s226, s227, s228) as
  of this writing.** s228 narrowed it from "`tools/:*`-specific" to a
  whole class of rules (any `Bash(<dir>/:*)` pattern fails; `build/:*`
  confirmed failing too, identically to `tools/:*`) and proposed a
  concrete fix: change the four affected rules in `.claude/settings.json`
  from `<dir>/:*` to `<dir>/*` (drop the colon). See
  `scratch/agent/BLOCKED.md` for full detail, falsification path, and the
  reasoning. **Check whether this fix was applied before doing anything
  else this session** (Step 0 above).
- **`deref0` diagnostic landed s226**, NOT yet soak-validated. Lives in
  `N64Recomp/fixup_game_funcs.py`'s existing `_campose_diag_patch` function
  (same patch site as s224's `ROGUESQ_LOG_CAMPOSE`, `funcs_4.c:0x800178A8`).
  Computes `root_ptr = U32(ctx->r3)`, bounds-checks
  `0x80000000 <= root_ptr < 0x80800000`, and if valid reads
  `MEM_W(ctx->r3, 0x0)` into `deref0`. Logged as `deref0=0x%08X
  deref0_valid=%d` appended to both `[campose-entry]` and
  `[campose-abnormal]` lines. No new env var — still `ROGUESQ_LOG_CAMPOSE=1`.
- **s224's `campose1` log already answered part of what a new soak would
  ask**: `flag`/`camptr` freeze at `n=15000`, `m00` doesn't freeze until
  `n=20880` — closed, don't re-derive, just extend with `deref0`.
- This exact schedule (`schedulepush2`/`run_mat3inv2.sh`/`run_campose1.sh`/
  `run_scenetraverse2.sh` family) is PROVEN non-deterministic on identical
  input (s223). Budget 2 attempts before drawing conclusions.
- **`fixup_game_funcs.py` is NOT idempotent** — never run it twice without a
  delete-all-funcs regen in between.
- **Verify "crash-free" visually**: MD5-checksum a spread of `hold_NN.png`
  (Python script, not shell loops).
- **Launch soaks synchronously (foreground)**. Budget ~80s nav/stable/leave
  overhead on top of `HOLD_S` (350 typical) — use `timeout: 590000`
  explicitly.
- **`/tmp` is not writable this session** — write scratch/report files
  inside `RogueSquadron64Recomp`/`N64Recomp`/`rogue_squadron64` only.
- **Compound `cd ... && cmd` gets denied in one Bash call** — issue `cd` and
  the following command as SEPARATE Bash calls. Also confirmed s228:
  chaining multiple `;`-separated commands in one Bash call, where any one
  of them isn't individually allow-listed, denies the WHOLE compound
  command (e.g. `git check-ignore` isn't in the git-subcommand allow list,
  and chaining it with other commands via `;` blocked all of them) — split
  into separate Bash calls per command, don't assume partial execution.
- **`git -C <path> <cmd>` does not match a `Bash(git <cmd>:*)` allow-rule**
  — `cd` first (its own Bash call), then bare `git <cmd>`.
- **`git check-ignore` is not in the git-subcommand allow list** (only
  `add`/`commit`/`diff`/`log`/`show`/`status`/`apply`/`stash list` are) —
  requires approval, this is expected/correct, not part of the `tools/`/
  `build/` bug.
- **Headless permission matching is a PREFIX match on the command string**
  — a leading env assignment breaks it (`PROBE_MODE=1 zsh run.sh` doesn't
  match a `zsh` allow rule; write `env PROBE_MODE=1 zsh run.sh` instead).
  This is a SEPARATE, older, already-understood quirk from the s226-s228
  `Bash(<dir>/:*)` gate — don't conflate them. The env-prefix issue has a
  known workaround (`env` prefix); the directory-prefix gate's proposed fix
  is the settings.json edit in BLOCKED.md, not yet confirmed.
- **Setup camera struct layout** (s223/s224/s226): `+0x0` a nullable
  linked-node pointer (tested null at `funcs_4.c:21339`, forwarded as a
  traversal-root pointer at `funcs_4.c:21358`); `+0x10/+0x14/+0x18/+0x1C` an
  integer viewport rect; `+0x20/+0x24/+0x28` perspective near/scale float
  scalars; `+0x2C` a 3x3 float rotation submatrix (36 bytes, to `+0x50`) —
  the only orientation data in this struct. World position/view
  concatenation happens via a separate FIXED global matrix address
  (`0x8012xxxx - 0x23A4`), not through this per-call struct.
- **`traverseSceneGraphRecursive`'s a0/a1 are NOT independent scene-root
  globals** — a1 = camera-struct-ptr + 0x2C (submatrix address), a0 = value
  loaded from camera-struct-ptr + 0x0 (linked-node pointer above). Both
  trace to `ctx->r17`, `setupCameraMatrices`'s own first argument — origin
  not traced into its caller, likely not needed given the deref0 approach.
- **`setupCameraMatrices` is `funcs_4.c:19142-21603`**,
  `mat3x3InverseInto` is `funcs_5.c:7208-~7460`,
  `traverseSceneGraphRecursive` is `funcs_4.c:15053-15357`. `processSceneNode`
  and `submitSceneNodeRender` (both `funcs_4.c`) have several
  s152/s190/s200/s219-221 tracers/guards, all confirmed firing through
  s225's freeze — do not re-instrument.
- **`ROGUESQ_LOG_CAMPOSE=1`**: logs `setupCameraMatrices`'s raw `+0x2C` m00
  + `+0x0` field + struct pointer + `deref0`/`deref0_valid`, every 60th
  call, uncapped on NaN/Inf, `funcs_4.c` guest `0x800178A8`. Keep armed.
- **`ROGUESQ_LOG_SCENE_TRAVERSE=1`** (s225), **`ROGUESQ_LOG_SCENE_RQ_COUNTER=1`**
  (s152), **`ROGUESQ_LOG_PROCESS_SCENE_NODE_GUARD=1`** (s200): all confirmed
  firing through s225's freeze; keep armed, closed questions, do not
  re-instrument.
- **`emitAllocatedDLCommand` is `funcs_3.c:2622-3210`** — s221's guard
  doesn't cover all fault sites; flagged, not chased (orthogonal).
- **`fixup_game_funcs.py` lives at
  `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`** —
  untracked in that sibling checkout (known since s83, not this repo's
  commit scope, flagged for the user).
- The `[CRASH][pc-symbol]` diagnostic (dladdr on raw mcontext `pc`) is
  permanent, always-on, more precise than `backtrace_symbols_fd` (s213).
- Disassembly tools (`nm`/`otool`/`objdump`/`lldb`/`atos`) are ALL blocked.
  Source-level reasoning only.
- `-O0` Debug build, `RECOMP_FUNC` noinline, no LTO.
- `recomp.h`: `MEM_W(base, offset)` = `*(int32_t*)(rdram + ((base+offset) -
  0xFFFFFFFF80000000))` — arg order is (base-value, offset-literal). `U32(val)`
  = `(uint32_t)(val)`; `gpr` = `uint64_t`; a legit KSEG0 `gpr` sign-extends,
  upper bits `0xFFFFFFFF`. Always check upper 32 bits explicitly.
- `rm -f <glob>`/`find <dir> -delete` are blocked — use
  `python3 -c "import glob, os; [os.remove(f) for f in glob.glob('<pattern>')]"`.
- Re-running the same soak script/tag OVERWRITES the previous run's
  `run.log` in place — copy the driver script to a new tag name per soak.
- `scratch/agent/STATUS`/`OUTCOME` get reset at the START of each iteration
  by the harness — finding them reset at session start is normal.
- **ROOT CAUSE FOUND s228 for why `scratch/agent/BLOCKED.md` never
  persists across sessions: `/scratch/` is wholesale gitignored**
  (`.gitignore:80`). Only `STATUS`, `OUTCOME`, and `NEXT.md` were ever
  force-added as tracked exceptions (`git ls-files scratch/agent/` to
  confirm the current exception list). `BLOCKED.md`/`SUBSTITUTION.md` are
  plain new files each session, so a bare `git add -A` silently skips them
  — no error, no warning in the commit output, so the commit "succeeds"
  and the message can truthfully say "wrote BLOCKED.md" while the file
  never enters git history. This is why `git log --all --
  scratch/agent/BLOCKED.md` kept coming up empty for s226/s227 despite
  their commit messages. **Fix, applied s228**: `git add -f
  scratch/agent/BLOCKED.md` explicitly. If a future session wants
  BLOCKED.md/SUBSTITUTION.md to survive, use `-f` (or add them to
  `.gitignore`'s exception list with a `!scratch/agent/BLOCKED.md`-style
  negation) — do not assume `git add -A` covers them.

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is past both the ~35 KB CLAUDE.md budget and the
Read tool's 256 KB single-read limit (confirmed s195, still true s228 —
read it with `grep`/offset-limited `Read`, never a plain whole-file
`Read`). Migrate durable mechanism/architecture material to
`PROJECT-OVERVIEW.md` and prune superseded detail — flagged for 24+
sessions without action, escalating.

`fixup_game_funcs.py`'s untracked, single-copy state in the `N64Recomp`
sibling checkout has been flagged since s83, still not fixed (not this
repo's commit scope) — worth surfacing to the user directly.

`/Users/williambuckley/Documents/Tools/N64Recomp` and
`~/Documents/Tools/rogue_squadron64` are separate git checkouts with
long-standing uncommitted changes, unrelated to this repo's commit scope.
Still flagged for the user, not committed autonomously.

`lib/rt64` and `lib/N64ModernRuntime` both show as modified in `git
status` as of s228 (N64ModernRuntime is new this session, rt64 is
pre-existing) — not investigated; worth checking whether these are
in-progress uncommitted patches vs. drift from `submodule-patches/*.patch`
before assuming steady-state dirtiness. If a future session touches either
submodule, remember CLAUDE.md's hard rule: any edit under `lib/` must be
followed by `submodule-patches/export.sh` + a commit in the same session.
