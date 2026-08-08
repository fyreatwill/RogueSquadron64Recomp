# NEXT work unit

HYPOTHESIS-ID: item-314-loop-scoped-audio-voice-guard

## s487 summary: closed item -314's own deferred 6-site remainder

`musyxMixActiveVoices` (3 sites) and `musyxSynthFrame` (1 site) — the 6 mid-loop `0x801496F8` reload
sites s484 deliberately left unguarded — now have a new `AUDIO_VOICE_BASEPTR_LOOP_GUARD` (2 site
anchors, `funcs_24.c`): `musyxMixActiveVoices`'s loop-head reload gets a `goto`-to-per-iteration-
increment guard (skips only that voice, continues the loop — transitively covers its other 2
same-iteration reloads too); `musyxSynthFrame`'s single reload gets a `goto`-past-the-array-walk
guard (skips only that countdown pass, preserves later unrelated work in the same call). **Item -314
is now fully covered, 20/20** (14/20 via s484's `AUDIO_VOICE_BASEPTR_ENTRY_GUARD` + these 6/20).

Build-verified (funcs_*.c deleted, full regen pipeline, `cmake --build` against the CORRECT build
dir — `RogueSquadron64Recomp/build`, not `N64Recomp/build`, a mistake caught and corrected this
session), all 13 sibling guard families unregressed. 1st live-verify soak
(`s487_audio_voice_baseptr_loop_manual`) clean: 0 fires on the new guard or any sibling,
`hangarbay-entry` positive control reached n=2600, crash at 113.1s byte-identical to the already-
catalogued `tickWrappingTimerAccumulatorList`/`memcpy_recomp+288` family (`last-guest-pc=0x80054780`,
same as s462's confirm) — unrelated, filed not chased. **2nd independent confirm queued**
(`scratch/agent/soak_queue/s487_audio_voice_baseptr_loop_confirm.sh`) — the loop will run it and
append a verdict to `SOAK-RESULTS.md`; fold that in at the start of next session (read list #3)
before picking a new work unit. If it comes back clean too, mark item -314 formally CLOSED (2/2) in
`docs/CURRENT-TRUTH.md` and `docs/PROJECT-OVERVIEW.md` §20 — that's a small doc-only edit, not a full
work unit on its own; pair it with a fresh work unit in the same session per the options below.

## This session's next work unit (after folding in the s487 confirm verdict)

No untried high-expected-value instruction-pattern scan and no un-investigated high-recurrence
breadcrumb remain queued. Two options, in order of preference:

1. **Recommended: fresh M3 idiom-class scan from scratch**, following the s465/s477 precedent:
   grep-enumerate every `lui`+`lw` (and, if that comes back dry, `lui`+`sw`) global reload across all
   50 `funcs_*.c` files not already covered by a named guard, rank by frequency, pick the top fresh
   bucket, direct-source-read at least 2 instances before proposing a fix (same standard every prior
   bucket in this lineage has used).

2. **Alternative**: the M5 lead-check cadence (every 3+ sessions, last checked s478 — now 9 sessions
   overdue) is well past due. Spend 15-20 minutes re-reading `docs/M5-AUDIO-PLAN.md` and grepping for
   any new stub/trap/gate discovered incidentally during the s481-487 arc (none flagged so far, but
   the arc's own guards touch several MusyX audio functions directly and may have surfaced one) before
   defaulting to option 1.

## Regen/build/soak recipe (same as always — NOTE the build-dir gotcha from s487)
`python3 -c "import glob,os; [os.remove(f) for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c')]"`
→ `cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py` → `cd ~/Documents/Tools/N64Recomp
&& ./build/N64Recomp rogue_squadron.toml` → `python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py`
(check the report for the expected counts, no errors) → **`cd
/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build`** (the actual game project's build
dir — NOT `~/Documents/Tools/N64Recomp/build`, which is the N64Recomp CLI tool's own build and will
silently report `ninja: no work to do` if you build it by mistake, as s487 did on its first attempt) →
`DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8`. Arm every sibling
guard env var per the standing rule (passive instruments are free) — see
`scratch/agent/soak_queue/done/s487_audio_voice_baseptr_loop_manual.sh` for the current full list.

## Soak queue status
1 queued: `scratch/agent/soak_queue/s487_audio_voice_baseptr_loop_confirm.sh` (item -314's 2nd
independent confirm). The loop will run it between iterations; read the verdict from
`scratch/agent/SOAK-RESULTS.md` at the start of next session.
