# NEXT work unit — M3: is `voice+0x0`'s corruption the SAME source as the already-characterized `devAddr` corruption? (s118)

s117 turned the multi-session `voice+0x0` hunt into a sharper,
higher-value question by unifying it with the separate s94-102 DMA-
corruption thread. Read PORTING-STATE.md's Session 117 entry before
doing anything else; this file only has the actionable summary.

## What's now closed — do not re-open or re-chase

- `musyxKeyOnVoice` (read-only), `isAudioSlotActive` (pure query), and
  the caller-side chokepoint chain (`musyxTriggerVoiceAttack` own-entry,
  `ROGUESQ_LOG_VOICE_ATTACK_ENTRY=1`) are all closed — s116, reconfirmed
  s117. Do not re-instrument any of them.
- Do not re-run the **first** `ROGUESQ_LOG_VOICE_ACTIVE_GATE` design
  (capped at 64 total lines) — it's a known-broken instrument (exhausts
  within the first audio ticks, provably uninformative about the ~140s
  window that matters). The **second**, corrected design (uncapped
  nonzero-capture tagged `[voice-active-gate-nz]` + a 5000-check
  heartbeat tagged `[voice-active-gate-hb]`) is what's actually landed in
  `N64Recomp/fixup_game_funcs.py` right now — reuse it, extend it, don't
  replace it wholesale.
- Hypothesis (b) — a base/offset bug in the gate check's own addressing —
  is refuted twice now: once on the all-zero case (voicegate1) and once
  on the actual nonzero case (voicegate2, addresses matched base+idx*0x88
  exactly). Do not re-test this.

## The decisive result from s117

`voicegate2` (same recipe as always: `PROBE_MODE=start_only HOLD_S=30
zsh scratch/s73_post_a_scene/run_mission_keys.sh <tag> 5 8`, plus
`ROGUESQ_LOG_VOICE_ACTIVE_GATE=1 ROGUESQ_LOG_MUSYX_DMA_CALL=1
ROGUESQ_LOG_FILL_RANGE_ARGS=1`) crashed early (hold-iter 6, ~119s, a
probable-new-20th SIGBUS class — see below) but still captured the
target data before dying:

- Heartbeat (`[voice-active-gate-hb]`, every 5000th check, logged
  regardless of value) fired 26 times from n=0 to n=125000 — proves
  logging coverage survived almost the whole run, not truncated early.
- **Nonzero hits, for the first time ever**: `n=68874 idx=0x10
  base=0x80171D50 byte=0x65` ('e'), `n=68875 idx=0x11 base=0x80171DD8
  byte=0x78` ('x'), then `idx=0x11 base=0x80171DD8 byte=0x02` three more
  times (`n=68893/68911/68929`). Both hit addresses match
  `base + idx*0x88` exactly against the heartbeat's own idx=0 reading
  a few lines later (`0x801714D0`) — the read is addressing the right
  slot, it's reading real (corrupted) memory there, not garbage from a
  bad pointer computation.
- `0x65`/`0x78` are printable ASCII, not boolean 0/1 — the same general
  "structured, ASCII-shaped, not noise" signature already established
  for the DMA `devAddr` field's corruption (s94: `"wing"`/`"lg?r"`
  patterns; s102: full characterization). **Not proven identical or
  same-source** — this session only logged 1 byte at the hit, not enough
  to compare patterns directly.

## The work unit

One instrument, one soak, batching everything already working (per
CLAUDE.md: "one build carrying every counter you will want, one run
collecting all of them"):

1. In the existing `[voice-active-gate-nz]` block
   (`N64Recomp/fixup_game_funcs.py`, search for
   `s_voice_active_gate_nz_n`), widen the dump from 1 byte to ~16-32
   bytes starting at the voice-array base (`ctx->r4`) — e.g. loop
   `MEM_BU(ctx->r4, i)` for `i` in `0..0x1F` and print as hex, same
   pattern as any other raw-memory dump already in the file (check
   `ROGUESQ_LOG_FILL_RANGE_ARGS`'s style for a raw-field-dump precedent).
   Keep the existing 64-hit cap on output (still uncapped internally).
2. Also keep `ROGUESQ_LOG_MUSYX_DMA_CALL=1` armed in the same soak (it
   already dumps the corrupted `devAddr` batch entries) — this run's own
   log is the comparison target, no second soak needed if both fire.
3. Regen: `python3 <rogue_squadron64>/tools/make_elf.py` (absolute path,
   no `cd`) → `N64Recomp rogue_squadron.toml` via
   `subprocess.run(cwd='/Users/williambuckley/Documents/Tools/N64Recomp')`
   (direct `Bash ./build/N64Recomp` hits the headless-approval wall,
   documented repeatedly) → `python3
   /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   (verify "patched x1" in output, not x2+ — full ELF regen is required
   every time, `fixup_game_funcs.py` is not idempotent, s102) → `cmake
   --build build -j8` with
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`.
4. Soak: `env ROGUESQ_LOG_VOICE_ACTIVE_GATE=1 ROGUESQ_LOG_MUSYX_DMA_CALL=1
   ROGUESQ_LOG_FILL_RANGE_ARGS=1 PROBE_MODE=start_only HOLD_S=30 zsh
   scratch/s73_post_a_scene/run_mission_keys.sh voicegate3 5 8` (`env`
   prefix required for the headless permission prefix-match, rule 10).
   Up to 3 attempts allowed per ITERATION.md rule 8 if early crashes
   (the s84 `frameStartReset` fluke-that-isn't-quite-a-fluke, or the new
   probable-20th class) preempt the nonzero window again — note it does
   NOT require reaching the ~140s DMA window this time, since s117 got a
   nonzero hit at n≈68874 checks in, well before that (the check rate is
   high — ~20 per audio tick — so this happened early in real wall-clock
   terms too; do the math from the actual log if timing matters).

**Discriminating outcomes:**
- If the wider dump around a `voice+0x0` nonzero hit contains the same
  literal byte patterns as a same-run `musyx-dma-call`-logged corrupted
  `devAddr` entry (e.g. shares the `"wi_g"`/`"lg_r"` 4-byte shapes, or
  any multi-byte run matches) → **confirmed**: one shared corruption
  source with a wider blast radius than assumed; the multi-session hunt
  for `voice+0x0`'s "writer" was never going to succeed because there
  isn't one — redirect all future effort at finding the *actual*
  corruption source (the still-unlocated thing that writes text/name
  data into audio-adjacent memory), a single unified M3 blocker instead
  of two.
- If the wider dump looks like a *different* shape (e.g. a real struct
  with sane-looking neighboring fields, not text) → the ASCII
  resemblance at `+0x0` was coincidental; `voice+0x0` has its own,
  separate corruption mechanism, distinct from `devAddr`'s. Falls back
  to treating it as its own M3 sub-thread — likely needs a heap-
  overrun-source hunt from scratch (allocator sizes, adjacent struct
  bounds), not a caller/writer hunt (already exhausted, s105-116).
- If neither soak nor 2 retries reproduce a nonzero hit at all → not
  null-worthless (the mechanism already exists per s117's data), just
  bad luck this session; park per rule 8 and try again next session
  rather than burning a 3rd attempt chasing timing.

## Do not

- Do not re-chase the probable-20th crash class
  (`static_5_800AB1C8`/`800AAD9C`/`800C6854` via `menuOverlayInit`) as a
  dedicated work unit yet — 1 occurrence, catalogued, lower priority
  than the M3 unification question. Fine to note if it recurs.
- Do not treat s117's `0x65`/`0x78`/`0x02` values as proven-identical to
  `devAddr`'s corruption without the wider-dump comparison — that
  resemblance is currently "same general signature," not "same source."

## Housekeeping still flagged, still not done

`docs/CURRENT-TRUTH.md` is well over the ~35 KB target (CLAUDE.md/
ITERATION.md). s116 and s117 both deliberately avoided growing the top
narrative section further (only touching "Next steps"). Still worth a
dedicated compression pass (migrate durable mechanism/architecture
material to PROJECT-OVERVIEW.md, prune superseded detail) paired with a
real experiment — compressing docs alone does not count as an ADVANCED
work unit.

Also flagged (not autonomously actioned): `/Users/williambuckley/
Documents/Tools/N64Recomp` is its own git checkout, not a `lib/`
submodule of this repo, and has accumulated uncommitted changes across
sessions s90-117 (`fixup_game_funcs.py` plus regenerated
`RecompiledFuncs/*.c`). `git` operations there required interactive
approval this session (and likely prior sessions) did not have — same
posture as the `rogue_squadron64` sibling checkout flagged since s54.
Worth asking the user whether/how to commit that history.
