# NEXT work unit — capture repaired scheduler receive identity

HYPOTHESIS-ID: vi640-maudtask-type2-writer

Session 3259 established that the former crash was the `s2948` probe reading
`MEM_HU(ctx->r17, 0x22)` after the generated scheduler had set `r17=1` as a
state value. The external `s2950` KSEG0 guard is now applied and the rebuilt
30-second run has no crash markers.

## Competing hypotheses

- `H-SpMsgMutated`: the accepted target-phase scheduler message has type 2 or
  otherwise carries a mutated message descriptor.
- `H-OtherOsTask`: a non-target task/message is accepted at the scheduler
  receive boundary.
- `H-Type2AbsentAtRecv`: the repaired port reaches the target wall but no
  accepted type-2 message is present at `0x80019CD0`.

## Discriminator

Run the repaired Debug binary from `build/` with `ROGUESQ_RECV_TRACE=1` and
the existing phase controls. The discriminating row must include caller,
message pointer, type byte, output slot, and `89F/28D44`, and must occur after
the VI-640 wall. Type 2 selects `H-SpMsgMutated`; a valid non-type-2 accepted
message selects `H-OtherOsTask`; a valid VI-640 wall with no type-2 row selects
`H-Type2AbsentAtRecv`. A pre-wall crash is unevaluable and requires a new
fault-site audit.

## Exact start

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
sh -c 'env ROGUESQ_RECV_TRACE=1 ROGUESQ_LOG_ALL=1 ./RogueSquadron64Recomp > ../scratch/agent/s3260_scheduler_identity.log 2>&1 & p=$!; sleep 60; kill -9 "$p" 2>/dev/null || true; wait "$p" 2>/dev/null || true'
```

Do not add another source field or repeat the old unguarded probe. If the
repaired run does not reach VI 640, classify it as unevaluable and audit only
the new fault site.
