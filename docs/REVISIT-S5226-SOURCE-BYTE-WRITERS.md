# Session 5226 — mission-entry words on the s5225 stride

Question: during retail mission origins `0x00690400` and `0x00620400`,
which PC stores offset `0x22` of `s0 = 0x80190E50 + i*0x88`?

## Controls

Retail run `scratch/agent/s5226_retail_byte_writers/oracle.log`. The
oracle stopped itself (`killed_overrun=0`) after 420.4s wall, 25189 VI.
No port rebuild. Watch index 0 reached 10000 writes at vi=1 and was
removed. All 42 write watches armed; none failed. Both mission origins
occurred. Phase frames: `0x00690400` width 512, 4259;
`0x00620400` width 512, 4111. Census sums equal the hit counts:
123839 and 124299, 41 slots, overflow 0. The same-run byte histogram
sums equal those hits. `0x03` is 0 on both origins.

## The watches were not the entry bytes

This run's `s0` on both origins is `0x80195190 + i*0x88` (`i=0..40`),
not `0x80190E50 + i*0x88`. The armed ranges were
`0x190E70 + i*0x88`, the words that contain `0x80190E50+0x22`. The
entry byte is at `0x1951B2 + i*0x88`. Counts are flat. Modal value
`0x00` (122523/123839 and 123031/124299), `0x01` on the rest except
one `0xF0` and one `0x02`. No guard.

Session 5225's census, re-read from its log, really was the
`0x80190E50` stride. The base is not stable across two qualified
Rice runs with the same Start schedule. The mix loop indexes two
pointers at `0x80149708` by the byte at `0x80149702`; these two
bases are the candidates for that pair. This run did not watch the
pointers, so that join is not made here.

## Writers of the watched stride

`writer-pc-phase` printed 82 headers and no `pc=` rows. Overflow is
0 on every header. During both exact mission origins, nothing wrote
any of the 41 words.

Lifetime writes on those words are 777904, with no histogram
overflow. Every reported PC:

| PC | Store | Offset `0x22`? | Hits | Watches |
|---|---|---|---:|---:|
| `0x80090F3C` | `sb $zero, 0x22($v0)` | yes, constant 0 | 249787 | 41 |
| `0x80090F8C` | `sb $v1, 0x22($v0)`, `$v1` is the constant 1 | yes, constant 1 | 14628 | 41 |
| `0x80090720` | `sb $v0, 0x20($s0)` | no | 249787 | 41 |
| `0x80090780` | `sb $v1, 0x21($s0)` | no | 249787 | 41 |
| `0x800909CC` | `sh $v0, 0x70($s0)` in `musyxRenderVoiceSamples`; value is the halfword loaded from `s1+0x22` | instruction offset is `0x70`, not `0x22`. Lands in watches 23..41 only | 6792 | 19 |
| `0x800909D4` | `sh $v0, 0x72($s0)`; value is the halfword from `s1+0x24` | same, not offset `0x22` | 6792 | 19 |
| `0x800078EC` | `sb $a1, 0($v0)` byte-fill | lane depends on `$v0`. Exactly 4 hits per word | 164 | 41 |
| `0x80018F5C` | `sd $t1, 0($t5)` dword copy | covers the word when the destination overlaps it | 83 | 21 |
| `0x80018F60` | `sd $t2, 0x8($t5)` | same copy | 80 | 20 |
| `0x80018F80` | `sb $t0, 0($t5)` tail of that copy | one word | 4 | 1 |

The three 249787-hit PCs are one per-voice update: offsets `0x20`,
`0x21`, and a constant 0 at `0x22`. The constant-1 store is the
post-loop flag on the same stride. None of them runs while the VI
origin is `0x00690400` or `0x00620400`. The per-watch counts are not
flat (`0x80090F3C` ranges from 1391 to 8273).

## Selection

This does not select H-const-zero, H-const-one, or H-other for the
byte the entry read. Those hypotheses need the dominant offset-`0x22`
PC of the live `s0`, and this run's live `s0` was the other stride.
It does select that fact: a qualified retail mission entry uses
`0x80195190 + i*0x88`, so the s5225 address list is not the only
retail base. No guard.

The watched stride's own offset-`0x22` lifetime writers are the
constant 0 at `0x80090F3C` and the constant 1 at `0x80090F8C`. They
are absent from both mission origins. That is evidence about the
idle stride only.
