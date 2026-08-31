# Session 3337 — M5 early callback-table store writer

## Work unit

The fresh retail oracle rerun was unavailable in this checkout because its
debugger-enabled core and Rice plugin are absent. The prior independent retail
capture passed the whole-RDRAM and callback-table controls, reached title/hangar,
and observed retail writes of both `0x80003250` and `0x8009123C` at
`0x80007928`. The port was rebuilt after admitting only the exact
`0x80007928` store event outside target-phase gating; no runtime behavior was
changed.

## Results

The port run passed the host boundary control (132 rows), audio-task join
control (2,633 rows), and reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`. It produced no `[CRASH]` or `[ABORT]` marker.

The ungated store rows included:

```
phase=2 width=320 origin=0x000280 pc=0x80007928 value=0x80003250
phase=2 width=320 origin=0x6DD280 pc=0x80007928 value=0x8009123C
```

The second row occurred at about 177 ms. The adjacent callback census changed
from an empty table to `[80003250,8009123C,0,0]` at the same early phase. Later
stores of `0x8009123C` were also observed in phase 3, while the known
initializer registration of `0x8009B5A8` remained target-gated and legitimate.

## Discriminator outcome

This selects `H-PortEarlyStore`: the observed `0x8009123C` occupant is written
by the generated `registerSiCallback` store during boot/phase 2, before the
later direct registration callsites. It refutes a clean-store explanation and
does not support a census-only transient for this transition. The exact caller
that supplies `0x8009123C` to `registerSiCallback` remains unresolved because
the store PC is inside the callee. No M5 contract change or mitigation is
authorized.

Evidence is two-line but asymmetric: this port store/census capture plus the
prior independent retail callback-table/PC capture from Session 3336.
