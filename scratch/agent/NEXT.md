# NEXT work unit — re-qualify the M5 route before the direct-writer census

HYPOTHESIS-ID: m5-direct-writer-route-qualification

Before building, reproduce the validated LLE-only real-audio route with the
established phase, callback, PCM, and static-rs_memset controls. The previous
corrected attempt crashed in `fillSampleStreamRange` before title, so first
establish that the route reaches VI 1024 and VI 512 without a crash. Do not
interpret writer absence unless both phase controls fire.

Retail command shape:

    tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --secs 180 \
      --watch-write 0x0:0x800000 --watch-pc 0x8002BEEC --watch-pc 0x800078EC \
      --pc-phase-log-width 0x006AB400:512 --pc-phase-log-width 0x00790400:1024

Port command shape, after the instrument is built, from `build/`:

    env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
      ROGUESQ_SPIN_YIELD=1 ROGUESQ_AUDIO_UCODE=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
      ROGUESQ_LOG_M5_DIRECT_WRITER=1 ROGUESQ_AUTOPILOT='3:start,6:start,9:start,12:start,16:a,20:a,24:start,28:a' \
      ./RogueSquadron64Recomp

Competing hypotheses:

- `H-RouteStable`: the established route reaches title/hangar; the prior crash
  was transient or recipe-related and the direct-writer census can resume.
- `H-AudioRouteCrash`: the real-audio route dies in `fillSampleStreamRange`
  before title, blocking the direct-writer census behind an audio defect.
- `H-LoggingRouteCrash`: only the combined logging set triggers the early
  crash; a no-log control in the same iteration reaches title/hangar.

Discriminator: same-iteration no-log and logging arms must both reach title
1024 and hangar 512 with zero crash/abort markers. Stable arms reopen the
writer census; logging-only failure selects `H-LoggingRouteCrash`; failure in
both arms selects `H-AudioRouteCrash`. A missing phase marker makes the arm
invalid, not a hypothesis result.

Exact constraints: ask the oracle before building; launch the port from
`build/` through `tools/probe.sh`; use the canonical Start schedule and
non-dot-prefixed capture paths; terminate with SIGKILL. Batch no-log and
logging arms in one iteration. Do not hand-edit generated functions.
