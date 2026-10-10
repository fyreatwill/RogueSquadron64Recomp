# S4501 — `jal rs_free` (0x0C000726) class-closure tally

Scan: `scratch/agent/s4501_scan.py` (output `scratch/agent/s4501_out.txt`).
Range: ROM words for vram 0x80000400..0x8010B6D0 (offset vram-0x7FFFF400),
`rogue_squadron.z64`. Overlay ranges not scanned separately (see caveat).

Control: all six named controls (0x800F9F94, 0x800EED50, 0x800EC564,
0x8007BE50, 0x80100F84, 0x80100F90) are present in the 160 hits. Scan valid.

## Result

| Stage | Sites |
|---|---|
| Total `jal rs_free` words | 160 |
| Address cited in an S44xx/S45xx doc | 40 |
| Address cited in any other doc that mentions rs_free (S36xx, S3605 etc.) | 104 |
| **Cited in no audit doc** | **16** |

The 16 are one cluster inside the audio shutdown function at/after
0x80091DA0 (S3605 only names its entry): 0x80091DEC, DFC, E0C, E1C, E2C,
E3C, E4C, E5C, E88, E98, F4C, F5C, F6C, F7C, F8C, F9C. The other four
sites in that function (DA4, DBC, F14, F2C) are cited elsewhere.

Verdict: **H-Residual**, one function, not 16 units. The class is not closed;
it closes with one audit of the audio shutdown function's free sequence.

## Caveats

- Matching is by address text. A doc that audits a site by function name only
  would be a false "unaudited"; a doc that merely lists an address as an
  example would be a false "audited" (the six controls are cited in many
  docs as examples). So 104 is an upper bound on audited sites, 16 a lower
  bound on unaudited.
- Menu/cinematic overlays were not scanned independently; the mission image
  scan range may not include them.
