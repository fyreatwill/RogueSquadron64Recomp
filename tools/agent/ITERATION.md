# RS64 recomp — autonomous iteration

You are continuing the Rogue Squadron 64 static-recomp investigation. You have
no memory of previous iterations; the docs are your memory.

## Read first, in this order — nothing else
1. docs/CURRENT-TRUTH.md   (state, config, next steps, superseded conclusions)
2. scratch/agent/NEXT.md   (the single next work unit, if it exists)
3. scratch/agent/SOAK-RESULTS.md  (tail -20 — verdicts from queued soaks the
   loop ran between iterations; fold new ones into the ledger like any run)
Do NOT read PORTING-STATE.md except to grep for a specific fact; it is 290+
sessions long and dozens of its conclusions are superseded.

## Step 0 — maintenance check (before choosing a work unit)
Run: `wc -c < docs/CURRENT-TRUTH.md`. If it prints more than 60000, THIS
iteration is a MAINTENANCE iteration: compact docs/CURRENT-TRUTH.md toward its
~35 KB cap — migrate durable material to docs/PROJECT-OVERVIEW.md, prune/merge
superseded and closed Next-steps items, renumber the backlog into ONE monotonic
sequence (it has had three colliding "-1/-2/…" sequences), and refresh the
stale "as of session N" headline. Git history preserves everything you delete.
A net shrink of >=200 lines counts as ADVANCED (the Stop gate knows this). Do
NOT run experiments in a maintenance iteration.

## Strategic priority (user directive, 2026-08-04)
When choosing the work unit, this order overrides Next-steps ordering:
1. Maintenance, when Step 0 triggers it.
2. **M5 audio de-stubbing.** First a design doc (docs/M5-AUDIO-PLAN.md):
   survey every audio stub/trap/gate currently in force, then plan an
   incremental de-stubbing sequence with a validation soak per step. Then
   execute it step by step. Rationale: several recurring crash families
   (waitForAnyAudioSlot boot deaths, voice-array corruption, slot reaping,
   MusyX DMA) are plausibly artifacts of the audio-disabled degenerate paths —
   de-stubbing may dissolve whole classes now being guarded one deref at a time.
3. M3 crash work — ONLY as systematic idiom-class audits (the s282–s288
   `-0x25A4` model: grep-enumerate a whole idiom class, classify every site,
   guard or prove dead, close the class). No reactive single-crash chases.
   Wait-for-recurrence breadcrumbs are passive: enqueue their soaks (see Soak
   queue below) and move on.

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
9. NEVER run `git submodule update`, `git checkout -- lib/...`, `git clean`,
   or `git reset --hard` (all denied in .claude/settings.json). lib/ carries
   uncommitted patches. If you edit anything under lib/, run
   `./submodule-patches/export.sh` and commit the refreshed patches in the
   same iteration, or the work is lost at the next reset.
10. Headless permission matching is a PREFIX match on the command string, so
   a leading env assignment breaks it: `PROBE_MODE=1 zsh run.sh` does not
   match the `zsh` allow rule and gets DENIED. Write env-prefixed commands
   as `env PROBE_MODE=1 zsh run.sh` (`env` is allowlisted). Exception:
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake ...` is
   allowlisted verbatim and works either way.

11. A MITIGATION IS NOT AN EXPLANATION. Before landing a skip / allow /
   guard / restore for a corruption or wild-value defect, name the WRITER and
   say whether the value is legitimate. s640-s659 landed four layers of
   freelist mitigation without once asking why a colour image is set at
   0x1F0D74 with width 1161 - a width this game never uses - and every one of
   those iterations passed the ADVANCED contract. The Stop gate now requires
   an `ORIGIN:` line in the session entry when the diff adds mitigation-shaped
   machinery.
12. ASK GROUND TRUTH BEFORE BUILDING AN INSTRUMENT. See the section below.
   Our runtime is the thing under test; it cannot be its own witness.
13. BUILD EVERY ARM OF AN A/B IN ONE ITERATION. A three-hypothesis work unit
   that measures one arm per iteration costs three iterations to learn what a
   single iteration could have shown. Build the arms, run them concurrently
   (one game instance uses ~50% of one core), report the comparison in this
   session's entry.
14. A DIAGNOSTIC FIELD IS NOT A WORK UNIT. Threading one join key / counter /
   ordinal per iteration - and concluding "still X-shaped, the individual
   source remains open" - is churn, not a sweep: the discriminator never
   moves (s1003-s1006 burned six iterations this way). Design the WHOLE
   discriminating table (all keys) in ONE instrument, ONE build, ONE run. A
   diagnostic-only iteration that selects nothing is not ADVANCED-worthy; the
   Stop gate flags it. If the measurement cannot discriminate, stop adding
   fields and re-read docs/F5-UCODE-REFERENCE.md or the oracle.

## Ground truth that is not our runtime
- `tools/oracle/README.md` - runs the RETAIL ROM under mupen64plus with memory
  read/write watches, so "is this address ours or the game's?" gets an
  independent answer with a PC attribution. Watches are PHYSICAL addresses;
  always arm a positive control first (a whole-RDRAM watch must fire ~1.6M
  times in 8 emulated seconds). Currently undriven: it reaches boot and
  attract only, so a null says nothing about the hangar or a mission.
- `docs/F5-UCODE-REFERENCE.md` - the Factor 5 microcode's real command table,
  its six inline-data pointer advances, and what it can and cannot emit, taken
  from GLideN64's shipped HLE implementation of this exact ucode. Read it
  before reasoning about any DL or RDP stream anomaly. It also corrects our
  own long-standing mislabelling of ops 0x01/0x02/0x03.

## Soak queue — never spend a session babysitting a repeat soak
A soak that only re-runs an existing recipe belongs to the loop, not to you.
- Enqueue: write a SELF-CONTAINED script to scratch/agent/soak_queue/<name>.sh.
  It runs from the repo root, must launch the game itself, watchdog itself,
  SIGKILL the game, and exit nonzero on a crash. Arm ALL passive
  breadcrumb/instrument env vars in every recipe unless the experiment needs
  isolation — passive instruments are free, and rotating one per soak wasted
  10 sessions (s272–s281, 0/20 hits).
- The loop runs up to 2 queued recipes between iterations (600 s hard cap
  each, then SIGKILL of the whole process group), appends one verdict line per
  run to scratch/agent/SOAK-RESULTS.md, and moves the recipe to
  soak_queue/done/. Full logs land in scratch/agent/soak_results/.
- Consume: read the new SOAK-RESULTS.md lines at session start (read list #3)
  and fold them into the ledger like any other run evidence.

## Declare your outcome honestly (the Stop hook checks this)
Write ONE of these words to `scratch/agent/OUTCOME`:

- `ADVANCED` — you ran the planned work unit and it produced a result, or you
  landed a real change (code, instrument, script, patch, or a NEW document).
  Editing existing docs is not advancing — with ONE exception: in a triggered
  MAINTENANCE iteration (Step 0), compacting CURRENT-TRUTH by >=200 net lines
  IS advancing.
- `SUBSTITUTED` — the planned work unit could NOT be run, so you did something
  else. This is legitimate ONCE. It is not a way to keep the loop fed.
- `BLOCKED` — you need a human. Write `scratch/agent/BLOCKED.md`.

If you write `SUBSTITUTED` you must also write `scratch/agent/SUBSTITUTION.md`
containing three things:
1. What specifically stopped the planned unit from running.
2. The evidence, THIS ITERATION, that it was actually stopped — a measurement,
   not a precedent. "Confirmed N times before" is not evidence; it is a
   citation of an unrefuted claim, and an unrefuted claim is not a fact.
3. The single experiment that would REFUTE your blocking explanation. If you
   cannot name one, your explanation is not falsifiable and you should treat it
   as unproven and attempt the work unit anyway.

**The loop stops itself after 2 consecutive SUBSTITUTED iterations.** That is
deliberate. If the environment will not let the work proceed, the correct move
is to surface it to the human, not to generate documentation work to stay busy.
A doc-housekeeping iteration is not a cheap iteration — it costs the same as a
real one.

## Exit contract (the Stop hook enforces this)
Before you may stop, ALL of:
1. Append a dated session entry to PORTING-STATE.md: what ran, what it
   showed, what it rules out. Include failed experiments — a documented dead
   end is a result. The heading MUST match this shape EXACTLY, because the
   Stop gate greps for it verbatim (`^+## Session `):
   `## Session N (date) — title`
   e.g. `## Session 983 (2026-08-13) — audited r4300_pc wrapper contract`.
   N is the next integer after the previous entry's number. No other shape
   satisfies the gate — not `## sNNN`, not a leading date, not a missing
   "Session" word. Sessions 877-926 drifted into these variants and every one
   of them failed this check.
2. Update docs/CURRENT-TRUTH.md: next-steps reordered; any overturned
   conclusion moved to the superseded section WITH why it was believable.
3. Rewrite scratch/agent/NEXT.md for the next iteration: the single next work
   unit, exact commands, expected discriminating outcomes — and a line
   `HYPOTHESIS-ID: <slug>` naming the active investigation thread. Keep the
   slug while pursuing the same hypothesis; change it when you pivot or close
   it. A long systematic sweep (one ranked list, one lead per session) keeps
   ONE slug for the whole campaign — do not rename it per lead. The loop
   enforces iron rule 8 with it: an ADVANCED iteration resets the counter, so
   only stalled runs count — 3 consecutive non-ADVANCED iterations on one slug
   force a pivot preamble, a 4th blocks the loop.
4. git add -A && git commit (message: "iter: <one-line finding>"). ALWAYS a new
   commit. Never `git commit --amend`, rebase, or reset onto a commit from a
   previous iteration — that deletes another session's entry from the ledger,
   and the ledger is the only memory. The gate checks this by ancestry, so an
   amend of a commit you made THIS iteration is fine and a rewrite below your
   own starting point is blocked. When in doubt, add a commit.
5. Write scratch/agent/STATUS: DONE (work unit finished), or BLOCKED (also
   write scratch/agent/BLOCKED.md: what you need, from whom, and what you
   already tried — specific enough that a human can act in 2 minutes).
6. Write scratch/agent/OUTCOME: ADVANCED, SUBSTITUTED (plus SUBSTITUTION.md),
   or BLOCKED — per the section above.
Never end on a plan or a promise. If the experiment failed, run the fixed
version now, in this iteration.
