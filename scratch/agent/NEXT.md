# NEXT work unit (after s682 section-2 provenance capture)

HYPOTHESIS-ID: m3-post-exit-fs-stall

Add authoritative-parser attribution to the existing phase-scoped E9 probe,
then rerun the same one-window section-2 audit. The s682 probe proved that all
62 output E9 commands were submitted, but it did not join individual output
addresses to the RT64 parser. Do not alter command decoding, range submission,
or FULL_SYNC behavior.

## Competing hypotheses

- **H-parser-advance-mismatch:** submitted output E9 commands are skipped by
  RT64's authoritative parser before its raw-opcode fetch.
- **H-output-not-parser-visible:** the bridge sees E9 bytes in an output range,
  but the RT64 range/pending-command boundary prevents that exact address from
  reaching parser dispatch.
- **H-walker-nonexecuted-path:** the six-command walker sees E9s in guest DL
  paths that L_1090 never executes; this explains walker/guest divergence but
  not necessarily the plateau.

## Discriminating measurement

At RT64's raw-opcode fetch, record each authoritative E9's physical address
against the active per-task emitted-address vector. The first 64 tasks after
the real section-2 `start-match` must retain all current controls: four boot
chains, one `[e9-prov-latch]`, 64 `scope=sec2` records, and matching
`dl-sync-probe2` rows.

- Submitted E9 address with no authoritative raw fetch: H-parser-advance-mismatch.
- Authoritative raw fetch at an emitted address but no handler/state line:
  H-output-not-parser-visible is refuted; isolate handler dispatch next.
- Walker E9 > guest while emitted E9s are authoritatively fetched:
  H-walker-nonexecuted-path.

## Commands

    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer zsh -c 'cd build && cmake --build . -j8'
    env BUDGET_S=2400 TARGET_PULSED=1 SEC2_SETTLE_S=0 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh
