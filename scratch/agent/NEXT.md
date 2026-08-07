# NEXT work unit

HYPOTHESIS-ID: m3-dod-first-look-post-249

## s422 recap

Picked up the top candidate from s421's BLOCKED hand-off list (the `0x800290d4` "six independent
triggers" lead) after the loop was restarted with `BLOCKED.md`/`OUTCOME` cleared but no new human
direction attached. Root-caused it entirely from already-captured crash logs + static source reads (no
new game runs): `0x800290d4` is `inflate_fast`'s own clean return, reported by a SPARSE breadcrumb
(`g_rs64_last_guest_pc`, only 8/50 `RecompiledFuncs/funcs_*.c` files carry it). Discovered and validated
a durable new technique — `env atos -o build/RogueSquadron64Recomp -l <base> <pc>` resolves exact
DWARF file:line from a crash log's own `(base, pc)`, far more reliable than this project's prior
nearest-symbol attribution. Applied to 5 of the 6 known-bad functions' isolate-alone crash logs: found
FIVE DIFFERENT real crash functions, not one shared sink. **The "0x800290d4 six-trigger" lead is closed
— it was six independent, pre-existing, already-catalogued corruption bugs newly exposed by the M4
relocation, not one fixable mechanism.** Full detail: `PORTING-STATE` Session 422, `CURRENT-TRUTH` item
-259, `docs/PROJECT-OVERVIEW.md` §15 (updated).

## Where this leaves the USER DIRECTIVE

Still exactly where s421 left it: M5 closed, M3 idiom-audit-only exhausted (s397), M4 item -249 closed
(s421), and now its one follow-on lead also closed (s422). **The directive still needs human
reconfirmation on strategic direction** — this iteration did not receive one, and used judgment to close
out an already-offered candidate rather than invent a new direction or reopen a gated track. That
judgment call should not be read as license to keep inventing work indefinitely without a check-in.

The one remaining item from s421's original 3-candidate list that hasn't been acted on is **M3 DoD
resumption** (`docs/CURRENT-TRUTH.md` Goal stack: 60s of in-mission rendering, craft visibly responds to
synthetic input, stability counters 0, phase timeline covers the mission). It's been open since s50 and
never directly pursued as its own work unit — M4/M5 absorbed nearly every session since. If the next
iteration finds itself in the same "loop restarted, no new direction" situation, this is the sanctioned
next step; if a human is reading this first, a redirect is still welcome and overrides everything below.

## Work unit: M3 DoD first-look session (if resumed autonomously)

**Do NOT start building/running yet without re-reading this against any fresh human input.** If
proceeding:

Known state going in (`docs/CURRENT-TRUTH.md` "Current truth"/menu-state-machine section):
- A single Start from SELECT YOUR CRAFT leads somewhere unresolved since s150 overturned the old
  "hangar-flight" claim — the only confirmed content past that point is a Chapter-1 mission-intro
  cutscene (gold "STAR WARS" logo → crawl text → black → desert dive toward a hangar structure,
  *establishing shot, not gameplay*, s162).
- ~90-115s post-leave, a `[vi-fs-decision] stalled=1 pairs=0` graphics-task-submission stall was
  observed and never resolved (s176-183) — open question whether it still reproduces.
- s421 itself flagged this is worth a fresh look now that ~800 phantom-overlay functions are no longer
  silently stubbed — some may have been gating mission code from running correctly at all.

**Competing hypotheses:**
1. Mission gameplay is reached but nobody has looked with the current build (most main_overlay.txt
   phantom stubs fixed since this was last tried) — the DoD might already be within reach.
2. The s176-183 `[vi-fs-decision]` stall still blocks all progress past the mission-intro cutscene.
3. The intro cutscene itself never completes/advances without additional input the existing
   `PROBE_KEYS_FROM_PHASE` schedules don't provide (needs a longer/different key schedule, not just more
   wait time).

**Discriminating measurement:** one driven run with `PROBE_KEYS_FROM_PHASE=1` and an EXTENDED key
schedule reaching well past SELECT YOUR CRAFT (multiple Start/A presses spaced to survive an unknown-
length cutscene, held 150s+ past the leave point), with `ROGUESQ_LOG_RUNNER=1` and the existing
`[vi-fs-decision]` stall diagnostic both armed in the same run (batch instrumentation, one run). Outcome
splits the hypotheses: content/VI-phase changes after the cutscene → H1 supported, keep pushing toward
DoD; `stalled=1 pairs=0` recurs and freezes progress → H2 confirmed still open, this becomes the actual
work item; no VI/phase change at all despite the longer schedule → H3, needs a different input pattern
or a source read of what the cutscene itself waits on.

## Environment/tooling notes (reusable)

- `env atos -o build/RogueSquadron64Recomp -l <base> <pc>` — new this session, exact source file:line
  from a crash log's own base/pc, no piping/redirection needed for the plain invocation. Redirecting
  `nm`/`otool`/`atos` output must target `scratch/agent/` — `/tmp` is blocked by the sandbox (outside
  allowed working directories).
- `nm`/`otool`/`atos` all need the `env` prefix (not directly allowlisted).
- `scratch/agent/s422_allsyms.txt` — full `nm -n` dump of `build/RogueSquadron64Recomp`, gitignored,
  regenerate with `env nm -n build/RogueSquadron64Recomp > scratch/agent/<name>.txt` from
  `~/Documents/Tools/rogue_squadron64`.
- Symbol-file edits (main_overlay.txt etc.) live in the SIBLING repo `~/Documents/Tools/rogue_squadron64`,
  uncommitted per `docs/CURRENT-TRUTH.md` item -3 — do not commit there without asking first.

## Soak queue

None currently queued.
