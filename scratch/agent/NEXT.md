# NEXT work unit (s984)

HYPOTHESIS-ID: oracle-pif-callback-runtime

**First check, before anything else:** is `~/Documents/Tools/rs64-oracle` in
this session's `.claude/settings.json` `permissions.additionalDirectories`?
Test with `cat ~/Documents/Tools/rs64-oracle/README.md` (an allowlisted
command whose only failure mode left is the directory-sandbox block). s983
found it hard-blocked (`ls`/`cat`/`grep`/`Read` all refuse the path; `nm` is
not allowlisted and is auto-denied headless) — new since s982, which
successfully drove LLDB against a path under it.

## If the oracle is now reachable

Resume the original planned unit exactly:

Run one bounded external-oracle binary-level callback-entry probe against the
corrected dylib. Do not add another callback marker or edit the recomp
runtime. Competing hypotheses (H-pif-core-entry / H-pif-binary-target /
H-pif-harness) and the discriminating measurement are unchanged from the
s982 write-up in `docs/CURRENT-TRUTH.md` Next work unit section. Exact
command:

`env DYLD_LIBRARY_PATH=/Users/williambuckley/Documents/Tools/rs64-oracle/iter974-alllto/projects/unix /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-alllto/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/build/Debug/rogue_squadron.z64 --secs 8 --watch-write 0x0:0x800000 --watch-read 0x1fc00000:0x1fc01000 --vi-poll --vi-trace`

## If the oracle is still blocked

Do NOT substitute a second consecutive iteration on this thread (s983 already
used the one legitimate substitution). Two options:

1. Go BLOCKED: write `scratch/agent/BLOCKED.md` asking a human to add
   `/Users/williambuckley/Documents/Tools/rs64-oracle` to
   `permissions.additionalDirectories` in `.claude/settings.json` (mirroring
   the existing `N64Recomp`/`rogue_squadron64` entries), or to say the oracle
   thread should be abandoned/redirected.
2. Pivot `HYPOTHESIS-ID` to backlog item 4 (M4 zero-shade root cause) as a
   real, budgeted work unit — read PORTING-STATE.md Sessions 19–20
   (2026-07-25/26, grep `baseFixed`) first; do not restart that investigation
   cold or duplicate its existing conclusions.

## Housekeeping already done in s983 (do not repeat)

The `runInMissionFrame` callback table at `0x8010B350` (backlog #1's last
open indirect-target edge from s954) is now closed: it is static `data`
(`roguesquadron.yaml`, `bss` starts at `0x8010B6D0`) with zero generated-code
writers (exhaustive `0x4CB0`-offset grep across `N64Recomp/RecompiledFuncs`).
Backlog #1's remaining open question is the general caller-frame/`$sp`
corruption mechanism for `slotDispatcherIter+872`, which has no queued static
lead — it needs a runtime instrument, not another source sweep.
