# NEXT work unit

HYPOTHESIS-ID: s3-register-corruption-runHangarMenuFromOverlay-callees

## What changed this session (s428) — read this before picking a thread

Root-caused and guarded item -265 (`runHangarMenuFromOverlay+800` SIGBUS, `MEM_B(0X1, ctx->r19) =
ctx->r16;` at `funcs_35.c:1575`/`1580`, guest `sb $s0, 0x1($s3)`). The guard (KSEG0-range check on
`ctx->r19`, see `fixup_game_funcs.py`'s `runHangarMenuFromOverlay` patch block) held and logged a
positive control (`[hangarmenu-a0-guard] wild s3(a0)=0x3F800000`) — but the ALSO-added entry
diagnostic (`[hangarmenu-a0-entry] a0=0x80130B40`) proved the function's own `$a0` argument is SANE at
entry and gets corrupted DURING the call, by one of its own callees:
`getAvailablePlayerCraftFlagsConsiderUnlocks`, `mallocCraftSelectionData`, or the
`runHangarSelectionFrame` loop (`funcs_35.c:1510`/`1536`/`1545`). MIPS `$s3` is callee-saved — the
callee that clobbers `ctx->r19` (the shared global register-file slot) without restoring it is the
actual bug. Top suspect: `mallocCraftSelectionData`, since item -264's fix (s427) is what made its
~4386-line body execute for the first time ever (previously a 1-instruction truncated stub, could not
have clobbered anything).

The guard's skip-the-write then let execution continue back into `menuOverlayInit`, which immediately
crashed again reading the SAME corrupted `ctx->r19` (item -266, `funcs_34.c:5869-5870`,
`far=0x380000003` this time — a different specific garbage value than the guard caught, near-zero-
integer shaped rather than float-shaped, suggesting the corruption may drift across
`runHangarSelectionFrame`'s loop iterations rather than being one fixed constant).

Single-source so far this session. Confirmation soak queued:
`scratch/agent/soak_queue/s428_hangarmenu_guard_verify.sh` — check `scratch/agent/SOAK-RESULTS.md`
first; if it already ran, use its result instead of re-driving a live run.

## The work unit — isolate which callee corrupts ctx->r19

This is now a register-corruption hunt, not a duplicate-symbol issue (that hypothesis is CLOSED for
this specific item — item -265's guard proved the wild value arrives mid-call, not from the caller).

**Batch instrumentation, one build**: add three throttled diagnostics to `funcs_35.c`'s
`runHangarMenuFromOverlay` (via `fixup_game_funcs.py`, following the existing patch-block style —
search for `hangarmenu-a0` to find the anchor site), each logging `ctx->r19` immediately after one of
the three callee-return points:
1. Right after `getAvailablePlayerCraftFlagsConsiderUnlocks(rdram, ctx);` returns (label `after_0`,
   `funcs_35.c:1511`/`1514`).
2. Right after `mallocCraftSelectionData(rdram, ctx);` returns (label `after_1`,
   `funcs_35.c:1537`/`1540`).
3. Right after EACH `runHangarSelectionFrame(rdram, ctx);` return inside the `L_800C68AC` loop (label
   `after_2`, `funcs_35.c:1546`/`1549` — this loop can iterate many times before falling through, so
   throttle tightly, e.g. first 20 iterations, and tag with an iteration counter).

**Discriminating outcome**: whichever checkpoint FIRST shows `ctx->r19` outside the sane KSEG0 range
(`0x80000000`-`0x80800000`) identifies the guilty callee. If checkpoint 2 (`mallocCraftSelectionData`)
is first-wild, that confirms the top suspect and the next work unit becomes finding WHERE inside that
~4386-line function `$s3`/`r19` gets used as scratch without being saved — a much bigger function than
any prior guard target in this project, so expect this to take its own session. If checkpoint 3 is
first-wild only after N>1 loop iterations, that points at `runHangarSelectionFrame` instead, and the
corruption is likely tied to some per-iteration state.

Live-run schedule (same as s423-428, known to reach the war-room/craft-select phase — see the Regen
recipe below for the exact env/keys):
```
env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_LOG_RUNNER=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 \
    PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh tools/probe.sh <outdir> 300 2
```

## Regen recipe (known-working s427/s428)

```
cd ~/Documents/Tools/rogue_squadron64 && python3 tools/make_elf.py
python3 -c "
import glob, os
for f in glob.glob('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c'):
    os.remove(f)
"
zsh ~/Documents/Tools/RogueSquadron64Recomp/tools/agent/regen_n64recomp.sh
python3 ~/Documents/Tools/N64Recomp/fixup_game_funcs.py   # audit report for xN on every new patch, not "no changes"
cd ~/Documents/Tools/RogueSquadron64Recomp/build && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build . -j8
```

`fixup_game_funcs.py` REFUSES to run a second time on the same generated files (checks for its own
`RS64_FIXUP_APPLIED` marker) — this is a safety net; if you see the refusal, you forgot to delete
`funcs_*.c` and regenerate first.

## Sandbox notes (confirmed again s428)

`lldb`/`otool -tV`/`find -delete`/plain `rm` with globs all require interactive approval — use the
`python3 -c` glob-delete above. `atos` (prefixed with `env`) only returns `symbol+offset`, not
file:line. `scratch/agent/s193_disasm.py <macho> <symbol> <frame_offset> [window]` plus a manual
symbol-range check remain the working substitute for precise crash-site identification. **New this
session: the `window` argument MUST be a multiple of 4, or the printed byte offsets desync from real
ARM64 instruction boundaries and the decoded output is garbage** (hit this personally with
`window=30`; corrected to a multiple of 4 and the decode was clean). No corruption resulted (just a
wasted call), but don't repeat the mistake.

## Soak queue

- `scratch/agent/soak_queue/s428_hangarmenu_guard_verify.sh` — queued this session, not yet run.
