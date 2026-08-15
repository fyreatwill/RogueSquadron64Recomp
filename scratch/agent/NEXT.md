# NEXT work unit (s1214)

HYPOTHESIS-ID: retail-entry-strategy

Work unit: add one bounded savestate lifecycle to `tools/oracle/rs64_oracle.c`
using the installed core API, and run one smoke test that proves save and load
can be invoked without losing debugger callbacks or the existing positive
controls. Do not yet use the state to classify M4 target watches.

Competing hypotheses and discriminator:

- H1: `M64CMD_STATE_SAVE` and `M64CMD_STATE_LOAD` work in the oracle lifecycle;
  a saved file exists and the same run reports whole-RDRAM plus debugger/VI
  controls on both sides of the load.
- H2: the API calls are present but cannot create or restore a compatible state
  from this ROM/core setup; the route is unusable and the returned error/log
  identifies the missing lifecycle condition.
- H3: state save/load works but disrupts debugger callbacks or positive-control
  delivery; the smoke test shows which control disappears after the load.

Discriminator: one state file plus the return codes and post-load control
counts from the same oracle process. A successful API symbol lookup alone is
not a positive result.

Exact implementation/test commands (run from the repository root):

    rg -n 'CoreDoCommand|M64CMD_(STATE_SAVE|STATE_LOAD|RESET)|whole|pif|vi' tools/oracle/rs64_oracle.c
    tools/oracle/build.sh
    env ORACLE_STATE_SMOKE=1 tools/oracle/build/rs64_oracle --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom build/Debug/rogue_squadron.z64 --secs 20 --watch-write 0x0:0x800000 --pif-trace --vi-poll --state-path scratch/agent/oracle-smoke.st

The smoke must save after ROM/plugin/debugger setup, load the same path, and
report both return codes and control counts. If H1 is selected, the following
unit can use the state for a paired 60-second oracle reachability comparison;
if H2 or H3 is selected, record the exact failing lifecycle/control and pivot
before arming M4 watches.
