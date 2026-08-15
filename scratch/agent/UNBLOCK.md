Route 3 — re-scoped after refuting the artifact-absence claim.

Evidence:

- `tools/oracle/build/rs64_oracle --help` exposes `--state-path`, and the
  oracle source implements explicit `M64CMD_STATE_SAVE`/`M64CMD_STATE_LOAD`.
- The adjacent `../rs64-oracle/src/mupen64plus-core` checkout contains the
  frontend source. Its `CoreDoCommand` implementation shows `ROM_OPEN`, plugin
  attachment, optional state load, and `EXECUTE`; no additional retail-entry
  handoff appears.
- `/opt/homebrew/bin/mupen64plus --help` exposes `--savestate`, and the local
  `scratch/agent/oracle-smoke.st` and `oracle-reach.st` files are real gzip
  savestates. Their lifecycle was already measured in sessions 1214–1215.

The claim that no local artifact exists is false. The dependency is still real:
the available artifacts are equivalent to the audited contract and do not
provide a new callable retail state source. The next work unit is therefore a
bounded generated save/account naming sweep that does not require that source.
