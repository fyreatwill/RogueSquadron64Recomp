# s2897 generated-symbol interval table

Interval: `0x80005960..0x80006C00` (end exclusive)

| Address | Companion boundary/name | Generated body | Call/reference evidence | Classification | Action |
|---|---|---|---|---|---|
| `0x80006BFC` | No semantic companion name; immediately before `initServiceRegistry` at `0x80006C00` | One instruction: `sw $v0, 0x18($fp)`, after the `initMemoryPack` return/delay-slot sequence | No generated `jal`, `j`, or lookup reference targets this address; only the body’s own address comments/probes occur | H-DataGap | Rename `fake_func_80006BFC` to `data_gap_80006BFC` |

The interval contains one unresolved placeholder and no callable-ambiguous
rows. The exact four-byte boundary and isolated post-return store support only
a mechanical data-gap name.
