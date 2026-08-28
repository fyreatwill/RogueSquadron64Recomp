# s2903 retail overlay/state handoff boundary

## Instrument validity

The same oracle invocation watched all of physical RDRAM (`0x000000..0x800000`)
and the four candidate execution PCs. The whole-RDRAM control produced 10,000
writes. The VI trace reached title (`1024`, origins `0x00790400/0x00790800`)
and hangar (`512`, origins including `0x006AB400`). The run therefore makes
the candidate nulls evaluable.

## Candidate table

| Candidate | Lifetime hits | Target-phase hits | Predecessor evidence | Decision |
|---|---:|---:|---|---|
| `mainGameLoop` `0x8003DFA0` | 1 | 0 | `0x80000DB0` at boot | absent at title/hangar |
| `loadOverlay` `0x80000B20` | 4 | 0 | `0x8003E008`, `0x8003E074`, `0x8003E0FC`, `0x8003E120` | absent at title/hangar |
| `runIdleFramesAndLoadSaveData` `0x8006D900` | 1 | 0 | `0x8003E010` at boot | absent at title/hangar |
| `setUnlockBitAndPersist` `0x8006E360` | 1 | 0 | `0x800A6598` at pre-title | absent at title/hangar |

## Verdict

The positive control and target VI phases passed, but none of the four
candidate PCs executed in either target phase. This selects H-NoBoundaryHit
for this candidate set. It is single-source oracle evidence: the VI route and
execution census are independent measurements in the same retail run, but no
second runtime/oracle source was added. No port instrumentation or behavior
change is authorized. The exhausted broad range `0x8003D000..0x80040000` was
not repeated.

Raw capture: `oracle.log` in this directory.
