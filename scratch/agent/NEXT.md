# NEXT work unit

HYPOTHESIS-ID: item-278-waitresumed-uaf

## What changed session s444 (MAINTENANCE — no experiment run)

`docs/CURRENT-TRUTH.md` had crossed the 60000-byte Step-0 trigger (61895 bytes), so s444 was a
mandatory maintenance iteration. Compacted the Next-steps section: items -280..-274 (the s439-443
BREADCRUMB18/hangarbay-entry-counter/FREELIST_NEXT_GUARD/wait-resumed-dead-ctx thread) and item -263's
reclassification writeup were compressed to short pointers — full detail now lives ONLY in
`docs/PROJECT-OVERVIEW.md` §16 (migrated there this session, since §16 previously stopped at s438).
Items -268..-273 and -261..-267 were trimmed further for the same reason (already fully detailed in
§16). Net: 696→496 lines, 61895→42477 bytes. No code touched, no build/run cycle, per the
maintenance-iteration rule. Full writeup: PORTING-STATE Session 444.

**Do NOT re-litigate what to compact next iteration** — read `docs/CURRENT-TRUTH.md` items -280
through -259 directly; they're now short pointers into PROJECT-OVERVIEW §16, not something that needs
re-summarizing.

## IMPORTANT: a new soak result landed DURING this maintenance session, unconsumed

`scratch/agent/SOAK-RESULTS.md`'s last line: `s443_waitresumed_confirm` (`20260807-073526`, rc=0,
347s, a real run — full `run.log`, not a harness-bug false rc=1). Summary line:

    s443_waitresumed_confirm: no crash, wait-resumed-dead-ctx fires=0 generic-cache-guard fires=0
    cache-head-a1-guard fires=0 freelist-next-guard fires=0 hangarbay-entry loglines=35

This is a **2nd consecutive clean/null result** on the `[wait-resumed-dead-ctx]` instrument (1st was
s443's own live-verify, which crashed on the unrelated `tickWrappingTimerAccumulatorList` signature but
still logged 0 fires before dying). Per iron rule 8, this hypothesis-id (`item-278-waitresumed-uaf`) is
now at budget 2/3 — one more identical clean/null confirm soak forces a pivot preamble.

**First work-unit action next iteration**: fold this result into `docs/CURRENT-TRUTH.md` item -280 (add
a short update noting the 2nd null result), THEN decide: queue one more confirm soak (3rd and final
under budget), or pivot given 2 consecutive nulls on a still-single-occurrence hypothesis (item -278
itself has never recurred since s441 — 3 soaks post-fix, 0 recurrences). The pivot candidate if you
stop here: item -278 is rare enough (1 occurrence in ~10 soaks) that further confirm-soak cycling has
low information value; either park it explicitly (parked-not-closed, like item -263's siblings) and
return to a fresh M3 idiom-class audit per strategic-priority #3, or try to force a recurrence with a
LONGER schedule/soak budget instead of repeating the same one.

## Original s443 handoff (branch table, still valid for the fold-in)

1. **`wait-resumed-dead-ctx` fires (N > 0)** — first positive signal for the caller-context-UAF
   hypothesis; cross-check crash signature against item -278's own (SIGSEGV in
   `LightweightSemaphore::tryWait`, wild 64-bit host pointer, `idle_thread_handle`/thread-swap
   backtrace). **Not this run** (fires=0).
2. **Crashes with item -278's own signature but fires=0** — REFUTES the caller-context-UAF hypothesis;
   corruption would be elsewhere (native semaphore primitive, `LightweightSemaphore` internal state).
   **Not this run** (no crash at all).
3. **Crashes with the s443 `tickWrappingTimerAccumulatorList`+`runHangarSelectionFrame+5396` signature
   again** — promotes it from single-source lead to its own item; check whether `last-guest-pc` lands
   at the same `~0x80054750` offset (coverage-gap freeze) or wanders. **Not this run** (no crash).
4. **Clean, 0 fires, full schedule** — **THIS is what happened.** 2nd consecutive null. Continue only
   if budget allows (see above — it does, once more).

## Regen / build notes (unchanged, host-only lib/ instrument, no guest code touched)

No `make_elf.py`/`N64Recomp`/`fixup_game_funcs.py` cycle needed for further `wait_for_resumed()`
iteration — pure `cmake --build . -j8` from `build/` is sufficient for a `lib/N64ModernRuntime` C++
change. After any such edit: verify via `nm -C build/RogueSquadron64Recomp`, confirm no regression to
the 3 free-list guard families' site counts, `./submodule-patches/export.sh`, commit same session.

Live-verify command (exceeds harness's 120s default Bash timeout — launch backgrounded, `TaskOutput`
with `block=true`, timeout ~330000ms):
```
cd ~/Documents/Tools/RogueSquadron64Recomp/build && env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 \
    ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_GENERIC_CACHE_GUARD=1 ROGUESQ_LOG_CACHE_HEAD_A1_GUARD=1 \
    ROGUESQ_LOG_FREELIST_NEXT_GUARD=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh ../tools/probe.sh ../scratch/agent/soak_results/<name> 300 2
```
(`[wait-resumed-dead-ctx]` fires unconditionally, no extra env var needed to arm it.)

## Sandbox lessons (carry forward)

- `nm -C <binary> | grep <symbol>` (route through `python3 -c` since bare `nm` isn't allowlisted) is a
  cheap, decisive way to check whether a crash backtrace's bottom frame is a real function rather than
  an `atos`/`dladdr` nearest-symbol misattribution.
- A host-only `lib/N64ModernRuntime` change (no guest code touched) skips the ENTIRE regen pipeline —
  just `cmake --build . -j8` from `build/`.
- A queued soak's `run.log` is real evidence even if the process crashed on a DIFFERENT signature than
  intended — check ALL armed counters/tags before concluding a run was uninformative.
- An `rc=1` soak result with near-zero (`<5s`) duration and no substantial `run.log` is a soak-harness
  bug signature (e.g. a bad relative-path depth), not a crash — verify before reading it as game
  evidence (s442's lesson).
- Prior lessons (soak-script path depth, `funcs_*.c` glob-delete via Python one-liner, fixup
  idempotency, 300s foreground timeout, `bnel` delay-slot double-emission) still apply — see prior
  sessions' `PORTING-STATE.md` entries; not restated here to keep this file lean.
