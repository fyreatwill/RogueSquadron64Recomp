# NEXT work unit (s1215)

HYPOTHESIS-ID: retail-entry-strategy

Work unit: use the validated state lifecycle for one paired debugger-enabled
retail reachability comparison. The control runs the documented 6-second Start
cadence from boot; the state arm saves after the 320 boot phase, loads that
state, then applies the same cadence. Do not arm M4 target watches unless a
later VI width/origin phase is reached.

Competing hypotheses and discriminator:

- H1: loading a 320-boot state preserves execution and the cadence reaches a
  later VI phase; the state route is a usable retail-entry strategy.
- H2: load succeeds but the state arm remains at width 320 like the control;
  the route works technically but does not provide the missing entry state.
- H3: load succeeds but whole-RDRAM or PIF/VI controls disappear afterward;
  the route disrupts the oracle instrumentation and is unusable.

Discriminator: phase-gated VI width/origin plus post-load whole-RDRAM and PIF
controls in the paired arms. A later phase selects H1; width 320 selects H2;
missing post-load controls selects H3.

Exact implementation/test commands (run from the repository root):

    tools/oracle/build.sh
    env ORACLE_STATE_REACH=1 tools/oracle/build/rs64_oracle --core "$HOME/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib" --rom rogue_squadron.z64 --secs 70 --watch-write 0x0:0x800000 --pif-trace --vi-trace --state-path scratch/agent/oracle-reach.st

The reachability arm must save/load at a phase boundary, report both return
codes, and keep the whole-RDRAM positive control plus PIF/VI traces active. Run
the undriven and state-driven arms concurrently if the harness supports it;
otherwise one invocation must emit both arms from one built binary.
