# S4502 — audio shutdown `rs_free` cluster (16 "unaudited" sites) closed

Disassembly: `scratch/agent/s4500_dis.py 0x80091DA0 0x80092000`.

The 16 sites are two functions, not one: `shutdownAudioEngine` tail
(0x80091D40..0x80091EAC; sites DEC..E98) and `waitForMusyXAudioTaskDone`
(0x80091EB0..0x80091FC0; sites F4C..F9C). Both are gated on B40
(`lbu 0x800A0F50`, beq-out when zero). The "unaudited" label was an address-text
artifact: S3604/S3605 audited the same frees by `$gp`-relative offset.

| Site | Global (offset) | Audited in |
|---|---|---|
| DEC/F4C | -0x6644 | S3604 shared list |
| DFC/F5C | -0x6640 | S3604 |
| E0C | -0x6638 | S3604 shutdown-only |
| E1C | -0x663C | S3604 shutdown-only |
| E2C/F6C | -0x68A8 | S3604 |
| E3C/F7C | -0x68A4 | S3604 |
| E4C/F8C | -0x6904 | S3603 (closed) |
| E5C/F9C | -0x689C | S3604 |
| E88 | -0x6950 | S3604 shutdown-only |
| E98 | -0x69A0 | S3604 shutdown-only |
| (DA4/F14 cited elsewhere) | -0x6898 | S3605 |
| (DBC/F2C cited elsewhere) | -0x6890 | S3605 |
| (D-A0 region, -0x68D8) | -0x68D8 | S3604 |

All 12 distinct offsets map to existing audits; zero new pointers.

Verdict: H-Guarded/H-Dead hybrid. Neither function NULLs the ten words, so a
second entry would double-free, but the wait wrapper zeroes B40 afterwards and
the shutdown wrapper has no generated caller (S3604/S3605). Concurrent re-entry
and runtime B40 stay unproven, as before; no new guard needed. rs_free class
(160 sites) is closed by address and by offset.
