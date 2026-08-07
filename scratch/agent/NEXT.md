# NEXT work unit

HYPOTHESIS-ID: item-278-waitresumed-uaf

## What changed session s443

Consumed `s442_freelistnext_confirm` (SOAK-RESULTS `20260807-071541`, rc=0, 347s, a real run): 4th
consecutive clean/null result on the free-list guard mechanism (0 fires across `generic-cache-guard`/
`cache-head-a1-guard`/`freelist-next-guard`, 5th counting all soaks since s434). Per iron rule 8 and
the previous NEXT.md's own budget note, did **not** queue a 6th identical confirm soak on that
mechanism — checked M5 for a fresh lead (none), then picked up item -278 (s441's single-occurrence
SIGSEGV inside `moodycamel::LightweightSemaphore::tryWait`, backtrace rooted in `idle_thread_handle`)
proactively.

Confirmed via `nm -C` that `idle_thread_handle` is a real N64 guest idle-thread function (not an
`atos`/`dladdr` misattribution — this project has a history of that failure mode). Source-read
`ultramodern`'s thread-swap handshake and found `wait_for_resumed()` derefs the CALLING thread's own
`UltraThreadContext*` with no liveness check, unlike the RESUME TARGET side which `resume_thread_tagged`
already guards (`thr_live_contains`) — the same "guard one deref, miss its sibling" idiom this whole
free-list-family campaign keeps finding. Added a diagnostic-only instrument (`[wait-resumed-dead-ctx]`,
`lib/N64ModernRuntime/ultramodern/src/threads.cpp`) — two always-on atomic counters + an unconditional
fprintf only on the bad path. Host-only C++ change, clean rebuild, verified via `nm`, no regression to
the 3 free-list guard families' site counts, `submodule-patches/export.sh` run and committed same
session.

Live-verified the standard schedule: **0 `[wait-resumed-dead-ctx]` fires** — but the process crashed
anyway at 112.3s on an UNRELATED signature (not item -278, not any free-list guard): SIGBUS,
`pc-symbol=tickWrappingTimerAccumulatorList+3888` (via `dladdr` on the real hardware fault PC, not a
breadcrumb misattribution), `last-guest-pc=0x80054750` (+0x100 into that function, a different offset
than the s433 occurrence's epilogue address `0x800547BC`), backtrace via `runHangarSelectionFrame+5396`
— a call site item -263's saga never traced (no `updateHangarBayScene` frame; does NOT resurrect item
-263, whose specific resurrection condition wasn't met). Filed as a new, uninvestigated occurrence
(`docs/CURRENT-TRUTH.md` item -280) — NOT chased this session per the no-reactive-chases rule.
Requeued: `scratch/agent/soak_queue/s443_waitresumed_confirm.sh`.

## The work unit — read the queued soak result, then branch

**Step 1: check `scratch/agent/SOAK-RESULTS.md` for the `s443_waitresumed_confirm` line.** Sanity-check
first per the s442 lesson: a real run has a nonzero `run.log` (thousands of lines) and tens-to-hundreds
of seconds runtime; an `rc=1` in under ~5s with no `run.log` is a soak-harness bug, not evidence.
Assuming it's real, the script's summary line reports `wait-resumed-dead-ctx fires=N` alongside the
usual free-list-guard/hangarbay-entry counts. Outcomes:

1. **`wait-resumed-dead-ctx` fires (N > 0)** — the first positive signal for item -278's caller-context-
   UAF hypothesis. Check whether the crash (if any) in the same run matches item -278's signature
   (SIGSEGV inside `LightweightSemaphore::tryWait`, wild 64-bit host `si_addr`/`x8`, backtrace rooted in
   `idle_thread_handle` or any other thread-swap chain). If it does: this closes the "is item -278 a
   caller-side context UAF" question with a same-run mechanism-level proof — the fix would be deciding
   what `wait_for_resumed` should safely do when `thread_context` isn't live (likely: don't wait, treat
   as already-terminated, mirroring `resume_thread_tagged`'s skip-the-signal behavior). If the fire
   happens WITHOUT a crash: the caller-context can apparently go non-live without necessarily faulting
   immediately — narrows but doesn't fully explain item -278, worth a closer look at what "not live"
   means at that moment (e.g. does the thread it belongs to still exist as an OS thread?).
2. **CRASHES with item -278's own signature again** (SIGSEGV in `LightweightSemaphore::tryWait`, wild
   64-bit host pointer, `idle_thread_handle`/thread-swap-chain backtrace) but `wait-resumed-dead-ctx`
   fires=0 — this REFUTES the caller-context-UAF hypothesis specifically (the crash recurs without the
   instrument ever detecting a dead context), meaning the corruption is elsewhere (e.g. genuinely
   inside `LightweightSemaphore`'s internal atomic/semaphore state, or a race in the native OS
   semaphore primitive itself) — redesign the instrument around that instead.
3. **CRASHES with the NEW s443 `tickWrappingTimerAccumulatorList`+`runHangarSelectionFrame+5396`
   signature again** (`last-guest-pc≈0x80054750`, `pc-symbol=tickWrappingTimerAccumulatorList+3888`) —
   a 2nd occurrence promotes this from single-source lead to a real thread worth its own item.
   `tickWrappingTimerAccumulatorList` has existing breadcrumb coverage (its epilogue address
   `0x800547BC` was seen at s433) — check whether `last-guest-pc` lands at the SAME `0x80054750` offset
   (deterministic freeze point, likely another breadcrumb-coverage gap one level deeper — check what's
   at guest offset ~0x100 into the function, e.g. a call the array-iteration loop makes) or a DIFFERENT
   offset each time (genuinely wandering, less likely to be a simple coverage gap).
4. **Clean, 0 `wait-resumed-dead-ctx` fires, full schedule** — 2nd consecutive null on this specific
   instrument (1st was s443's own crash-interrupted run, itself already a 0-fire data point, so this
   would be attempt #2 of a budget that resets fresh under iron rule 8 since this is a new
   hypothesis-id). Continue soaking per the queue unless budget hits 3.

**If SOAK-RESULTS doesn't yet have the `s443_waitresumed_confirm` line**: run it yourself (same
schedule as below), or treat s443's own live-verify (0 fires, crashed on the unrelated
tickWrappingTimerAccumulatorList signature) as the first data point and move to a fresh work unit if
budget considerations apply.

Regen recipe unchanged this session (host-only `lib/` edit, no guest code touched) — no
`make_elf.py`/`N64Recomp`/`fixup_game_funcs.py` cycle needed unless a NEW guest-code change is made.
For a `lib/N64ModernRuntime` change specifically: edit → `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer
cmake --build . -j8` from `build/` → verify via `nm -C build/RogueSquadron64Recomp` → `./submodule-patches/export.sh`
→ commit refreshed patch same session.

Live-verify command (exceeds the harness's 120s default Bash timeout, auto-backgrounds — launch it,
then use `TaskOutput` with `block=true`, timeout ~330000ms):
```
cd ~/Documents/Tools/RogueSquadron64Recomp/build && env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 \
    ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_GENERIC_CACHE_GUARD=1 ROGUESQ_LOG_CACHE_HEAD_A1_GUARD=1 \
    ROGUESQ_LOG_FREELIST_NEXT_GUARD=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh ../tools/probe.sh ../scratch/agent/soak_results/<name> 300 2
```
(`[wait-resumed-dead-ctx]` fires unconditionally whenever the instrument trips — no extra env var
needed to arm it, matching `resume_thread_tagged`'s existing always-on-counter pattern.)

## MAINTENANCE NOTE for s444

`docs/CURRENT-TRUTH.md` is now **61895 bytes**, over the 60000-byte Step-0 trigger (it was 56935 at
the start of s443; this session's item -280 entry pushed it over). **s444 MUST be a maintenance
iteration**: compact toward the ~35 KB stretch target per `tools/agent/ITERATION.md`'s Maintenance
section before picking up any experiment. Good compaction candidates: migrate the now-closed-out
detail of items -268..-277 (the free-list-guard-family saga, s432-441) to `docs/PROJECT-OVERVIEW.md`
§16 if not already fully there; the item -261..-267 slot-animation chain (s424-431) is likewise fully
closed and summarized — check whether its raw detail duplicates what's already in PROJECT-OVERVIEW.

## Sandbox lessons (carry forward)

- **New (s443): `nm -C <binary> | grep <symbol>` is a cheap, decisive way to check whether a crash
  backtrace's bottom frame is a real function (game or runtime) rather than an `atos`/`dladdr`
  nearest-symbol misattribution** — confirmed `idle_thread_handle` this way in under a minute via
  `python3 -c "import subprocess; ..."` (plain `nm` invocations are not on the Bash allowlist directly;
  route through `python3 -c` which IS allowlisted, or `strings`/`grep` on the binary for a quick
  presence check without needing full symbol demangling).
- A host-only change under `lib/N64ModernRuntime` (no guest code / no `RecompiledFuncs` touched) skips
  the ENTIRE regen pipeline — just `cmake --build . -j8` from `build/` is sufficient. Don't run
  `make_elf.py`/`N64Recomp`/`fixup_game_funcs.py` for pure C++ runtime changes; that pipeline is only
  for guest-code (`funcs_*.c`) patches.
- A queued soak result with a real, multi-thousand-line `run.log` and a normal-length runtime (tens to
  hundreds of seconds) is real evidence even if the process crashed on a DIFFERENT signature than the
  one the soak was designed to test — check ALL the armed counters/tags in the log, not just the one
  you were expecting, before concluding the run was uninformative (s443's crash was informative for
  BOTH the intended item -278 test (0 fires) AND surfaced a new, unrelated occurrence worth filing).
- Previously-recorded lessons (soak-script path depth, `funcs_*.c` glob-delete via Python one-liner,
  fixup idempotency, 300s foreground timeout, `N64Recomp/fixup_game_funcs.py` untracked, sequential
  patch ordering within one file pass, `bnel` delay-slot double-emission) still apply — see prior
  sessions' `PORTING-STATE.md` entries for detail; not restated here to keep this file lean.
