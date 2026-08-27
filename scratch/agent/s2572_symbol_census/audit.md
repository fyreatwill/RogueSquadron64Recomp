# Session 2572 symbol census: `0x8010721C`

## Discriminator table

| Evidence | Result | Selection |
|---|---|---|
| Active generated span | `0x8010721C–0x8010721F`, one instruction: `addiu $sp, $sp, -0x58` | Four-byte fragment, not a complete callable body |
| Immediate predecessor | `lvc_calculateFriendliesSaved` reaches its `jr`/delay-slot tail at `0x8010720C–0x80107218`; the target follows at `0x8010721C` | Boundary-adjacent fragment |
| Immediate successor | `lvd_initializeObjectTracking` starts at `0x80107220` with its own prologue and has size `0x70` | Established function boundary; do not absorb target into successor |
| Companion symbol entry | `fake_func_8010721C = 0x8010721C`; comment says real function is `lvd_initializeObjectTracking` | Explicit placeholder, no human candidate |
| Exact source/m2c/caller search | No exact address, `fake_func_8010721C`, or `0x10721C` match beyond generated/project symbol records and the companion entry | No independent mapping |
| Semantic candidate | A lone stack-pointer adjustment does not identify a distinct game function | No defensible invented name |

## Result

`H-data-or-boundary` is selected over `H-human-candidate`,
`H-already-mapped`, and `H-uncertain`. The placeholder remains unchanged. This
is a static, single-source boundary classification; it is not a reachability or
liveness claim. The next unresolved companion placeholder is `0x80107EA4`.
