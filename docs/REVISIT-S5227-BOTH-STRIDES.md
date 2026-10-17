# Session 5227 — both mission strides, one retail run

Question: during the four mission-pair VI origins, which PC stores
offset `0x22` of the stride the entry actually uses?

## Controls

Retail run `scratch/agent/s5227_both_strides/oracle.log`. The oracle
stopped itself (`killed_overrun=0`) after 420 seconds. No port rebuild.
Watch index 0 reached 10000 writes at vi=1 and was removed (`rc=0`).
All 83 write watches armed; none failed. The binary printed
`[s5225-s0]` and `[oracle] writer-pc-phase`.

VI origins present, all width 512: `0x00690400` (4452 frames),
`0x00690800` (4077), `0x00620400` (3843), `0x00620800` (4218).
Census sums equal the hit counts, 41 slots, overflow 0. Lifetime
`0x80090F3C` is present on all 41 words of the `0x80190E50` stride,
with histogram overflow 0.

## The two strides are the two fields

| Origin | Entry `s0` | Hits |
|---|---|---:|
| `0x00690400` | `0x80195190 + i*0x88` | 129420 |
| `0x00690800` | `0x80190E50 + i*0x88` | 118206 |
| `0x00620400` | `0x80195190 + i*0x88` | 115645 |
| `0x00620800` | `0x80190E50 + i*0x88` | 126849 |

Session 5225's 0400 census was the other base. Which stride sits on
0400 is not fixed across runs. Both are live in this run, on opposite
field origins. The stride an origin does not name has no phase writer
and overflow 0. That is why session 5226's tables were empty: it
watched `0x80190E50` while its 0400 census was `0x80195190`.

## Writers of the live stride

Every live-stride phase row is one of these four PCs. Overflow is 0.
Counts are the store hits, then the number of the 41 words touched.

| PC | Instruction | Offset `0x22`? | `0x00690400` | `0x00690800` | `0x00620400` | `0x00620800` |
|---|---|---|---:|---:|---:|---:|
| `0x80090F3C` | `sb $zero, 0x22($v0)` in `musyxMixActiveVoices`; `MEM_B(0x22, v0) = 0` | yes, constant 0 | 129881 / 41 | 118635 / 41 | 116045 / 41 | 127294 / 41 |
| `0x80090F8C` | `addiu $v1, $zero, 1` then `sb $v1, 0x22($v0)` in the same function, after the voice loop | yes, constant 1 | 7844 / 41 | 7166 / 41 | 6710 / 39 | 7403 / 39 |
| `0x80090720` | `sb $v0, 0x20($s0)` in `musyxRenderVoiceSamples`; `$v0` is `lbu 0($s1)` | no | 129881 / 41 | 118635 / 41 | 116045 / 41 | 127294 / 41 |
| `0x80090780` | `sb $v1, 0x21($s0)` in the same function; `$v1` is `lbu 0x6D($s1)` | no | 129881 / 41 | 118635 / 41 | 116045 / 41 | 127294 / 41 |

The address at `0x80090F3C` is `base + index*0x88`: the preceding
instructions are `sll 4`, `addu`, `sll 3` (`index * 0x88`) plus the
loaded table word. The same expression feeds `0x80090F8C`.

Inside one `musyxMixActiveVoices` iteration the order is `jal` at
`0x80090F00` into `musyxRenderVoiceSamples` (which calls
`fillSampleStreamRange` at `0x8008FAAC`, the entry read), then
`sb $zero` at `0x80090F3C`. The entry byte is the previous iteration's
residue, not the store in the same call.

## Selection

This selects H-const-zero. On the live stride, across all four
mission-pair origins, the dominant offset-`0x22` PC is `0x80090F3C`,
and the stored value is the constant 0. Retail's modal `0x00` is that
constant. The port's `0x03` is not this store.

H-const-one is a real store and is not dominant. H-other is refuted:
no third offset-`0x22` PC, overflow 0. H-not-in-pair is refuted: the
constant-0 store runs during every origin, on all 41 live words.
No guard.
