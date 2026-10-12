# s4678 M5 key-on census

The complete generated idiom contains eight defensive early-return sites:

`0x80090CEC`, `0x80090D04`, `0x80090D30`, `0x80090D48`, `0x80090D74`,
`0x80090D8C`, `0x80090DB8`, `0x80090DD0`.

In port hangar phase 5, the batched table reached entry 12260 and normal tail
12259. Divide/guard results were:

| Sites | Divisor | Divides | Guards |
|---|---:|---:|---:|
| `0x80090CEC`, `0x80090D30`, `0x80090D74`, `0x80090DB8` | `0xC0` | 12259 each | 0 |
| `0x80090D04`, `0x80090D48`, `0x80090D8C`, `0x80090DD0` | not reached | 0 | 0 |

The normal tail ran 12259 times. Slot transitions recorded 206 `02` rows and
152 `00` rows. Retail's independent qualified hangar route reached key-on
entry/tail PCs and recorded no trap-PC hits. No early return was changed.
