# NEXT: RESUME — run the mapped TLUT-return witness on a bounded dd4 route
HYPOTHESIS-ID: g1c-dd-phase2

Checkpoint status (s6599): do not rerun the completed retail arm. Its outer log
ended `rc=0`; the dd4 outer log is empty, so the dd4 arm stopped before a
witness-phase result and remains unevaluable. Resume with one direct bounded
dd4 launch and an explicit SIGKILL watchdog; do not treat the prior wrapper
termination as a null result.

One work unit: use the persistent witness at generated `0x80049660` and
classify the value saved into `r17/r4` immediately before the mapped faulting
store `0x800496A8`.

Competing hypotheses:
- H-return-wild: `getTextureTlutEntry` returns `0x951335B0`.
- H-between-store: the return is valid, but another generated write changes
  `r4` before `0x800496A8`.
- H-host-alias: the guest value is valid and only host address conversion makes
  the faulting address wild.
- H-stale: the return is a stale object whose lifetime differs in dd4.

Discriminator: `[hudptrr] stage=tlut_return val=...` immediately before the
mapped store. `val=0x951335B0` selects H-return-wild; a valid return followed
by the store selects H-between-store; a host-only mismatch selects H-host-alias;
valid returns in both arms with different lifetime/route timing select H-stale.
The existing material/TLUT read rows and active player-record store rows are
positive controls and must fire in the same run.

Commands:

```sh
python3 tools/apply_s6595_hudptrread.py
cmake --build build --config Debug --target RogueSquadron64Recomp
# Launch one dd4 route with s6591_run.sh's environment, a SIGKILL watchdog,
# and output at scratch/agent/m6/s6599_dd4_direct/run.log.
rg -n 'hudptrr|hudptrw|SIGBUS|Bus error|summary|mission_verified' \
  scratch/agent/m6/s6599_dd4_direct/run.log
```

Keep `ROGUESQ_HUDPTRWATCH=1`; do not add a guard or skip. If the shared
wrapper again retries without a durable result, use a direct single-launch
variant with the same environment and an explicit SIGKILL watchdog, then record
the output as incomplete if it fails before the witness phase.
