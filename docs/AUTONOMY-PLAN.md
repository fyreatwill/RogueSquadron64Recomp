# Rogue Squadron 64 Recomp — Autonomous Operation Plan

> **For the agent receiving this:** you are the Claude instance that has run this project for 43
> sessions. This document was prepared from your own `PROJECT-OVERVIEW.md`, `CURRENT-TRUTH.md` and
> `PORTING-STATE.md`. It does two things: (1) installs a harness so you run unattended — no human
> "continue" between turns, automatic resume after usage-limit windows — and (2) fixes the operating
> contract so each unit of work is problem-shaped instead of session-shaped. Execute Part A top to
> bottom in your next session, then the loop takes over. Nothing here changes your investigation
> method — it *enforces* the rules you already derived the hard way.

**Why this exists (evidence from your own log):** all 43 sessions ended the same way — a NEXT list
written to disk, then a stop that only a human "continue" could break. Roughly 4 in 10 sessions were
consumed by avoidable process failures rather than the intrinsic problem: instruments that failed
their own controls (s40 produced zero usable conclusions; five sessions tuned knobs against the
wrong phase; five more attributed the band by centroid), environment failures that burned whole
sessions before being detected (three session-entries in a no-display sandbox where the game could
not run; three sessions on a phantom Screen Recording blocker; one run that "burned its full budget
before the problem showed up in the verdict"), and boring-config blind spots (two sessions of
profiling before anyone checked `-O0`). The harness below makes every one of those a fail-fast
preflight or an enforced rule instead of a lost session.

---

## As-built deviations (Part A executed 2026-07-26)

The harness is installed and differs from the text below in six places, all forced by what the repo
and the machine actually are. **The files on disk are authoritative; this document is the rationale.**

1. **Submodule patches live in `submodule-patches/`, not `patches/`.** `patches/` already exists and
   is the MIPS-side game-patch source tree (`Makefile`, `heap_guards.c`, `patches.ld`) that the
   build compiles. There are **four** patches, not two: `lib/rt64` has its own modified nested
   submodules `src/contrib/hlslpp` and `src/contrib/plume` (a 94-line `plume_metal.cpp` addition),
   whose changes a `git -C lib/rt64 diff` does not capture. `apply.sh` is idempotent (detects
   already-applied via `--reverse --check`) and `export.sh` was added to re-export after `lib/` edits.
2. **The Stop gate is a deterministic command hook** (`tools/agent/stop_gate.sh`), not a prompt hook.
   It checks the artifacts rather than the agent's account of them: `STATUS` reads exactly
   `DONE`/`BLOCKED`; a commit actually landed this iteration (HEAD moved off
   `scratch/agent/ITER_START_HEAD`, which `loop.sh` writes); the working tree is clean outside
   `scratch/` and `build/`; the iteration's commits touch **both** `PORTING-STATE.md` and
   `docs/CURRENT-TRUTH.md`; `NEXT.md` is non-empty; and `BLOCKED.md` is non-empty when `STATUS=BLOCKED`.
   The stuck-detector and the `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` idea are implemented in-script as
   `STOP_GATE_BLOCK_CAP` (default 8): at cap−2 the gate orders a BLOCKED write-up, at cap it lets go.
3. **Permission rules use Claude Code's `Tool(prefix:*)` form**, and `Read`/`Edit`/`Write` are scoped
   to the repo path rather than `*`. The deny list was widened beyond `git submodule update` to
   `git clean`, `git reset --hard`, `git restore lib/`, `git submodule foreach/deinit` and
   `rm -rf lib/` — same intent, more of the ways the patches can die. `.gitignore` had `/.claude`
   ignored wholesale; it is now `/.claude/*` with `!/.claude/settings.json` so the harness is
   versioned, and `/scratch/` was added.
4. **Preflight matches the real `winctl`**, which prints exactly `yes`/`no` for `trusted` (the
   plan's grep for `true|trusted` would have passed on the string "trusted" in a usage line). One
   check was added: each submodule patch must still be applied. A submodule with *no* local
   modifications is a hard fail (the patches were wiped); a submodule that merely diverges from its
   exported patch is a warning telling you to run `export.sh`.
5. **`loop.sh` does not burn an iteration on a usage-limit window** (it decrements the counter before
   sleeping) and gives up into `BLOCKED.md` after `MAX_LIMIT_WAITS` (12) consecutive waits instead of
   sleeping forever. A preflight failure or an agent-set `STATUS=BLOCKED` exits the loop with a
   notification rather than looping.
6. **The Part B ladder is in `docs/CURRENT-TRUTH.md`** as "Goal stack — work strictly top-down",
   inserted above the s38 "Next steps" list.

---

## Quickstart for William (one-time, ~15 minutes at the keyboard)

1. Put this file in the repo as `docs/AUTONOMY-PLAN.md`.
2. Start one **interactive** Claude Code session in the repo and say:
   *"Read docs/AUTONOMY-PLAN.md and execute Part A."* Stay nearby for this one session — it will
   trigger the macOS permission dialogs (Accessibility / Screen Recording for the new terminal
   context) exactly once, and you should approve the initial git commit.
3. After Part A's smoke test passes, from a Terminal **on the logged-in desktop** (not SSH, not a
   detached context) run:

   ```bash
   caffeinate -dis tools/agent/loop.sh
   ```

   and walk away. `caffeinate -d` keeps the display awake — a locked/asleep screen breaks window
   capture. Disable auto-lock for the run, or set it very long.
4. You will be interrupted only by a macOS notification when the agent is **blocked** on something
   only you can do (a permission dialog, a physical test, a judgment call). Fix it, delete
   `scratch/agent/BLOCKED.md`, rerun the loop command.
5. Progress is visible without talking to the agent: `git log --oneline` (one commit per
   iteration), `scratch/agent/loop.log`, and the docs themselves.
6. **Retire the Grok handoffs.** The entire 43-session log contains zero trace of anything Grok did
   — whatever it produced either didn't stick or bypassed the ledger, and anything outside the
   ledger gets re-derived later at full cost. The loop turns a usage-limit window into a sleep
   instead of a handoff. If wall-clock speed ever matters more than cost, a Max plan shortens the
   sleeps; nothing in this document depends on it.

---

## Part A — one-time setup (agent executes, in order)

### Task A1: make the working state durable

The standing warnings say `lib/N64ModernRuntime` and `lib/rt64` carry **uncommitted working-tree
patches** (the shared-DMEM serialization, the overlay loader, the RT64 assert-guard chain). Right
now a stray `git submodule update` or checkout destroys months of work.

- [ ] In each patched submodule, export the diff into the parent repo:

  ```bash
  mkdir -p patches
  git -C lib/N64ModernRuntime diff > patches/N64ModernRuntime.patch
  git -C lib/rt64 diff > patches/rt64.patch
  ```

- [ ] Create `patches/apply.sh`:

  ```bash
  #!/bin/bash
  # Re-apply the submodule working-tree patches after any submodule reset.
  set -e
  cd "$(dirname "$0")/.."
  git -C lib/N64ModernRuntime apply --check ../../patches/N64ModernRuntime.patch && \
    git -C lib/N64ModernRuntime apply ../../patches/N64ModernRuntime.patch
  git -C lib/rt64 apply --check ../../patches/rt64.patch && \
    git -C lib/rt64 apply ../../patches/rt64.patch
  echo "patches applied"
  ```

  ```bash
  chmod +x patches/apply.sh
  ```

- [ ] Commit everything currently uncommitted in the parent repo (source, tools, docs, patches) on a
  branch named `autonomy`. From here on, **every iteration ends with a commit** (Task A4's
  contract). Verify: `git status` is clean afterward except `build/` and `scratch/` (add both to
  `.gitignore` if not already there).

### Task A2: create `.claude/settings.json` (permissions + stop gate)

Permission prompts are silent "continue" bottlenecks — in headless mode they become denials. This
allowlist covers the entire build/run/measure loop; the Stop hook is what keeps a turn going until
the iteration contract is met.

- [ ] Create `.claude/settings.json` in the repo root:

  ```json
  {
    "permissions": {
      "allow": [
        "Read(*)",
        "Edit(*)",
        "Write(*)",
        "Bash(cmake *)",
        "Bash(make *)",
        "Bash(ninja *)",
        "Bash(python3 *)",
        "Bash(scratch/venv/bin/python *)",
        "Bash(tools/*)",
        "Bash(build/*)",
        "Bash(./RogueSquadron64Recomp *)",
        "Bash(git add *)",
        "Bash(git commit *)",
        "Bash(git diff *)",
        "Bash(git log *)",
        "Bash(git status *)",
        "Bash(git apply *)",
        "Bash(grep *)",
        "Bash(rg *)",
        "Bash(awk *)",
        "Bash(sed *)",
        "Bash(ls *)",
        "Bash(mkdir *)",
        "Bash(cp *)",
        "Bash(mv *)",
        "Bash(kill *)",
        "Bash(pkill *)",
        "Bash(screencapture *)",
        "Bash(clang *)",
        "Bash(timeout *)",
        "Bash(caffeinate *)"
      ],
      "deny": [
        "Bash(git submodule update *)",
        "Bash(git checkout -- lib/*)",
        "Bash(git push *)"
      ]
    },
    "env": {
      "CLAUDE_CODE_STOP_HOOK_BLOCK_CAP": "50"
    },
    "hooks": {
      "Stop": [
        {
          "hooks": [
            {
              "type": "prompt",
              "prompt": "You are gating the end of an autonomous investigation iteration for the RS64 recomp project. Allow stopping ONLY if ALL of these are true: (1) the file scratch/agent/STATUS contains exactly DONE or BLOCKED; (2) this turn appended a session entry to PORTING-STATE.md and updated the 'Next steps' (and, if any conclusion was overturned, the 'Overturned conclusions' section) of docs/CURRENT-TRUTH.md; (3) the changes were committed to git. If any condition is unmet, respond {\"ok\": false, \"reason\": \"<name the specific unmet condition and instruct: finish the current experiment, update the docs, write STATUS, and commit>\"}. If the transcript shows the agent is stuck repeating the same failing action more than 3 times, instruct it to write STATUS=BLOCKED with a BLOCKED.md explaining what it needs instead of retrying."
            }
          ]
        }
      ]
    }
  }
  ```

  The `deny` entries make the standing warning ("never `git submodule update --force`") and the
  patch-destruction risk structurally impossible rather than advisory. `git push` is denied because
  there is no remote in this workflow; remove if one is added deliberately.

### Task A3: create the preflight — fail in 5 seconds, not 5 hours

Every environment failure class that previously burned a session becomes a check here. The loop
runs this before every iteration.

- [ ] Create `tools/agent/preflight.sh`:

  ```bash
  #!/bin/bash
  # Fail fast on every environment failure that has previously burned a session:
  # no-GUI sandbox (s6-s7), Accessibility silently absent, Screen Recording /
  # locked screen, ROM not beside the binary (silent "place your ROM" VI), bare
  # CLT without metal, missing PIL venv.
  set -u
  cd "$(dirname "$0")/../.."
  fail() { echo "[preflight] FAIL: $1"; exit 1; }

  [ "$(launchctl managername)" = "Aqua" ] \
    || fail "not a GUI (Aqua) session - run the loop from Terminal on the logged-in desktop"

  [ -x build/winctl ] || fail "build/winctl missing - rebuild: clang -O1 -fobjc-arc -framework Cocoa -framework CoreGraphics -o build/winctl tools/winctl.m"

  build/winctl trusted 2>/dev/null | grep -qi "true\|trusted" \
    || fail "Accessibility not granted to this terminal context (winctl trusted)"

  t="$(mktemp -d)/pf.png"
  screencapture -x "$t" 2>/dev/null
  [ -s "$t" ] || fail "screencapture wrote nothing - Screen Recording permission or locked screen"

  ls build | grep -qiE '\.(z64|n64|v64)$' \
    || fail "ROM not in build/ next to the executable (silent dead-VI trap)"

  [ -d "${DEVELOPER_DIR:-/Applications/Xcode.app/Contents/Developer}" ] \
    || fail "full Xcode not found - metal shader rebuilds will fail (set DEVELOPER_DIR)"

  scratch/venv/bin/python -c "import PIL" 2>/dev/null \
    || fail "scratch/venv python lacks PIL - image decoders will fail"

  echo "[preflight] OK"
  ```

  ```bash
  chmod +x tools/agent/preflight.sh
  ```

- [ ] Adjust the `winctl trusted` grep to match the tool's actual output (you wrote winctl; check
  it), then run the preflight once and make it pass before continuing.

### Task A4: create the iteration contract

This file is the prompt every headless iteration receives. It is the operating system of the
project; the Stop hook in A2 enforces its exit contract.

- [ ] Create `tools/agent/ITERATION.md`:

  ```markdown
  # RS64 recomp — autonomous iteration

  You are continuing the Rogue Squadron 64 static-recomp investigation. You have
  no memory of previous iterations; the docs are your memory.

  ## Read first, in this order — nothing else
  1. docs/CURRENT-TRUTH.md   (state, config, next steps, superseded conclusions)
  2. scratch/agent/NEXT.md   (the single next work unit, if it exists)
  Do NOT read PORTING-STATE.md except to grep for a specific fact; it is 43
  sessions long and roughly two dozen of its conclusions are superseded.

  ## Do exactly one work unit
  A work unit is ONE experiment or ONE bounded change, chosen from the top of
  CURRENT-TRUTH "Next steps" (or NEXT.md if present). Before building anything:
  - Write down (in NEXT.md) the 2-4 competing hypotheses and the DISCRIMINATING
    measurement — the one whose outcome splits them. If you cannot name what
    each possible outcome would prove, redesign before running.
  - Batch instrumentation: one build carrying every counter you will want, one
    run collecting all of them. Never spend a build-run cycle per counter.

  ## Iron rules (each one bought with multiple lost sessions)
  1. A null result is WORTHLESS until the instrument passes a positive control
     in the same run ("mark everything" must visibly fire). A counter proving
     the branch ran is NOT a control.
  2. No cross-run A/B on animating scenes. Phase-gate on VI transitions
     (PROBE_PHASE_WIDTH / PROBE_KEYS_FROM_PHASE=1), never a stopwatch. Toggle
     within a single run where possible.
  3. Scope every counter and log budget to the phase. Run-lifetime budgets read
     as false zeros in later phases.
  4. Two independent lines of evidence before any conclusion enters
     CURRENT-TRUTH. One source = label it "single-source" explicitly.
  5. Check the boring thing first: build flags, env vars, stale schedules,
     "working as designed" — before instrumenting the exotic thing.
  6. Regeneration order: make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
     cmake. New diagnostics in build/factor5_ucode/*.c or RecompiledFuncs/ go
     into the fixup scripts or they die at the next regen.
  7. Kill runs with SIGKILL, never SIGTERM. Capture paths must not start with
     "." in the final component. Run the game from build/ with the ROM present.
  8. Budget rule: if this is the 3rd consecutive iteration on the same
     hypothesis with no discriminating result, STOP experimenting. Write the
     hypothesis/evidence table into NEXT.md, pick the highest-information-value
     next probe, or go BLOCKED with a specific question.

  ## Exit contract (the Stop hook enforces this)
  Before you may stop, ALL of:
  1. Append a dated session entry to PORTING-STATE.md: what ran, what it
     showed, what it rules out. Include failed experiments — a documented dead
     end is a result.
  2. Update docs/CURRENT-TRUTH.md: next-steps reordered; any overturned
     conclusion moved to the superseded section WITH why it was believable.
  3. Rewrite scratch/agent/NEXT.md for the next iteration: the single next work
     unit, exact commands, expected discriminating outcomes.
  4. git add -A && git commit (message: "iter: <one-line finding>").
  5. Write scratch/agent/STATUS: DONE (work unit finished), or BLOCKED (also
     write scratch/agent/BLOCKED.md: what you need, from whom, and what you
     already tried — specific enough that a human can act in 2 minutes).
  Never end on a plan or a promise. If the experiment failed, run the fixed
  version now, in this iteration.
  ```

### Task A5: create the loop driver

- [ ] Create `tools/agent/loop.sh`:

  ```bash
  #!/bin/bash
  # Unattended driver. Run from a Terminal INSIDE the logged-in desktop session:
  #   caffeinate -dis tools/agent/loop.sh
  # Each iteration is a fresh context; state lives in the docs (CURRENT-TRUTH,
  # NEXT.md), which is exactly what they were built for. Usage-limit windows
  # become sleeps, not handoffs.
  set -u
  cd "$(dirname "$0")/../.."
  mkdir -p scratch/agent
  ITER_CAP="${ITER_CAP:-40}"
  SLEEP_ON_LIMIT="${SLEEP_ON_LIMIT:-1800}"

  n=0
  while [ "$n" -lt "$ITER_CAP" ]; do
    n=$((n+1))

    if [ -f scratch/agent/BLOCKED.md ]; then
      osascript -e 'display notification "RS64 agent blocked - see scratch/agent/BLOCKED.md" with title "RS64 loop"'
      echo "[loop] BLOCKED - fix it, delete scratch/agent/BLOCKED.md, rerun."
      exit 2
    fi

    if ! tools/agent/preflight.sh; then
      { echo "# Blocked by preflight, $(date)"; tools/agent/preflight.sh 2>&1; } \
        > scratch/agent/BLOCKED.md
      continue
    fi

    echo "[loop] iteration $n starting $(date)" | tee -a scratch/agent/loop.log
    echo WORKING > scratch/agent/STATUS

    out="$(claude -p "$(cat tools/agent/ITERATION.md)" \
           --permission-mode acceptEdits \
           --output-format json 2>&1)"
    rc=$?
    printf '%s\n' "$out" >> scratch/agent/loop.log

    if [ $rc -ne 0 ] || printf '%s' "$out" | grep -qiE 'usage limit|rate.?limit|overloaded|resets at'; then
      echo "[loop] limit or error (rc=$rc) - sleeping ${SLEEP_ON_LIMIT}s" | tee -a scratch/agent/loop.log
      sleep "$SLEEP_ON_LIMIT"
    fi
  done
  echo "[loop] iteration cap ($ITER_CAP) reached $(date)" | tee -a scratch/agent/loop.log
  ```

  ```bash
  chmod +x tools/agent/loop.sh
  ```

  Notes: `acceptEdits` + the A2 allowlist covers the whole loop without prompts. If a needed
  command still gets denied in headless runs, add it to the allowlist — do not reach for
  `--dangerously-skip-permissions` first. Hooks (including the Stop gate) run in `-p` mode.

### Task A6: create the repo-root `CLAUDE.md`

Every fresh context — interactive or headless — auto-loads this. It is the 30-second version of
what a new session must never violate.

- [ ] Create `CLAUDE.md` in the repo root:

  ```markdown
  # RS64 Recomp — session rules

  Read docs/CURRENT-TRUTH.md before doing ANY work. PORTING-STATE.md is the
  append-only log; ~two dozen of its conclusions are superseded — never act on
  it without checking CURRENT-TRUTH. Project overview: docs/PROJECT-OVERVIEW.md.
  Autonomous-operation contract: tools/agent/ITERATION.md.

  Hard rules:
  - Regen: make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake. The fixup
    step is NOT optional. Hand-edits to generated code go in the fixup scripts.
  - NEVER run git submodule update; lib/ carries uncommitted patches
    (patches/*.patch, patches/apply.sh restores them).
  - Kill the game with SIGKILL, not SIGTERM. Run it from build/ with the ROM
    beside it. Metal rebuilds need DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer.
  - A null result without a same-run positive control is not a result.
  - End every working session by updating PORTING-STATE.md + CURRENT-TRUTH.md
    and committing.
  ```

### Task A7: smoke-test the harness

- [ ] Seed `scratch/agent/NEXT.md` with a deliberately small work unit:
  *"Retire the dead knobs (FORCE_PAL15, FORCE_SHADE_WHITE, wrap-forwarding leftovers) that have sat
  in the NEXT lists of sessions 20–23; verify the build still runs to the title screen with a
  phase-gated capture."* (This clears a four-session-old debt and exercises build + run + capture +
  docs + commit end to end.)
- [ ] Run one bounded iteration: `ITER_CAP=1 tools/agent/loop.sh`.
- [ ] Verify all of: preflight passed; the knob removal happened; a new PORTING-STATE entry and a
  CURRENT-TRUTH update exist; a commit landed; STATUS reads DONE. If any check fails, fix the
  harness (not the contract) and repeat.
- [ ] Only after this passes, hand William the quickstart above.

---

## Part B — milestone ladder (so the loop never idles)

Copy this ladder into `docs/CURRENT-TRUTH.md` as the goal stack above "Next steps". Work strictly
top-down; a milestone is done only when its definition-of-done is met and documented.

**M1 — hangar band root cause and fix** *(current; s43 state: texture decode, submission gap, and
raster-state rejection all eliminated — the band pixels are gaps between triangles).* Next
experiment per s43: instrument the LLE ucode's clip/cull path — per gfx task, count triangles
evaluated / culled / clipped / emitted, and bucket the *discarded* ones by projected y-span overlap
with the band rows (game y ≈ 141–201). Add the counters via `tools/fixup_factor5_ucode.py` so they
survive regen. Positive control: totals must reconcile with s42's y-histogram (~7,000 triangles per
capture). Discriminator: a discard population overlapping the band rows names the clip/cull
mechanism (then identify which plane/precision path); a null — with its control passed — pushes the
question upstream into the DL the game builds, where the parked s32 anomaly (39 of 55 I4 uploads
sampling 64×128 past `masks=6/6`) becomes the next lead.
*Done when:* mechanism traced input → code path → pixels, fix applied, and the s41 mark-vertices
mode-2 probe shows band rows receiving geometry, with other phases unchanged.

**M2 — post-`-O2` regression sweep and soak.** Phase-gated `regress.sh` across all six known scenes
against the s23 baselines, plus three 10-minute driven hangar soaks. *Done when:* per-phase metrics
within baseline bands and all stability counters (UnhandledJumpTarget, defer-drop, dmem-race,
missing-func, asserts) at 0.

**M3 — first gameplay.** Extend the driven key schedule past SELECT GAME into mission 1. Expect new
failure classes: mission-overlay DMA (watch missing-func / UnhandledJumpTarget), a new VI phase to
add to the timeline, possibly new ucode ops. Each new failure is its own work unit — return to the
M1-style method. *Done when:* 60 seconds of in-mission rendering, craft visibly responds to
synthetic input, stability counters 0, and the phase timeline in CURRENT-TRUTH covers the mission.

**M4 — parked correctness items**, one work unit each: outdoor `baseFixed = −32768` zero-shade root
cause (currently masked, not fixed); the S=0 triangles in the 640 attribution phase; the I4
`sample=64x128` anomaly if M1 didn't consume it.

**M5 — audio de-stubbing (investigation first, not code).** The MusyX audio ucode already
recompiles (`factor5_ucode_b_recompiled.c` sits in the build as a never-called artifact). First
work unit: a design doc only — how audio tasks would run LLE alongside gfx (they share the `dmem[]`
serialization you built in s5), what bridges RSP audio output to SDL, and what the audio-gate
byte reversal implies. Gate M5 behind M2: audio re-enters exactly the shared-state territory that
cost three sessions before the recursive mutex.

---

## Part C — standing speed rules (beyond the harness)

1. **Capture once, analyze many.** Any question answerable from a dump (DL bytes, RDP stream,
   TMEM-at-upload, decoded textures) gets asked offline against a saved capture — a game run costs
   minutes and is nondeterministic; re-running the analyzer against a file costs nothing. Prefer
   adding one dump flag over adding three counters.
2. **Batch counters into one build.** The s35 pattern — two instruments co-run in one capture
   specifically to kill the cross-run confound — is the default, not the exception.
3. **The ledger is the only memory.** Fresh iterations read CURRENT-TRUTH only. Keep it under
   ~35 KB: when it grows, migrate durable material to PROJECT-OVERVIEW.md and prune. PORTING-STATE
   stays append-only. Any work done outside this repo's ledger (another AI, a manual session)
   either gets written into PORTING-STATE or it did not happen.
4. **No parallel game runs.** One window, one capture target, one machine — runs stay serial;
   parallelism goes into offline analysis and doc work only.
