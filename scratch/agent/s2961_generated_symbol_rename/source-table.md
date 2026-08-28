# s2961 generated-symbol source table

| Address | Generated entry | Classification | Evidence |
|---|---|---|---|
| `0x800B47C4` | `fake_func_800B47C4` | H-Fragment | The complete body is exactly three valid instructions: `lui $at, 0x8010`, `lwc1 $f0, -0x5B08($at)`, and `swc1 $f0, 0x120($v0)`. There is no stack-frame prologue or return. The next entry starts at `0x800B47D0` with `menuControllerInput`'s `addiu $sp, $sp, -0x198`; the companion map separately records this 12-byte fake record and the following 0x38E4-byte body. Searches found no caller or independent lookup of the fake symbol. The companion m2c source is keyed to the larger controller routine and supplies no exact semantic name for this fragment. Preserve the placeholder. |

The body is valid executable code, so it is not a mechanically proven data
gap. Its missing callable boundary and lack of an exact semantic name rule out
H-Callable. The adjacent boundary and companion evidence select H-Fragment.

Next census address: `0x800B58B4`.
