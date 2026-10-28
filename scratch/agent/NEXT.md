# NEXT: run the mapped TLUT-return witness on a bounded dd4 route
HYPOTHESIS-ID: g1c-dd-phase2

One work unit: use the persistent witness at generated `0x80049660` and
classify the value saved into `r17/r4` immediately before the mapped faulting
store `0x800496A8`. The previous dd4 wrapper cycled retries and was SIGKILLed
without a summary; do not treat that as a null result.

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
zsh scratch/agent/s6591_run.sh dd4
rg -n 'hudptrr|hudptrw|SIGBUS|Bus error|summary|mission_verified' scratch/agent/m6/s6591_dd4/run.log scratch/agent/m6/s6591_dd4/fail_att*.log
```

Keep `ROGUESQ_HUDPTRWATCH=1`; do not add a guard or skip. If the shared
wrapper again retries without a durable result, use a direct single-launch
variant with the same environment and an explicit SIGKILL watchdog, then record
the output as incomplete if it fails before the witness phase.
