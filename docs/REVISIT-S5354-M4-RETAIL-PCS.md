# Session 5354 — retail M4 samples at the mapped PCs

Recipe: `tools/oracle/run_m4_retail_pcs.sh` (cxd4 with `RS64_RSP_MID_STRIDE=1`,
`RS64_RSP_MID_PCS=0x12C,0x7F0`, rdplog video, README press schedule, 75 s).
The cxd4 patch (outside this repo, `rs64-oracle/.../module.c`): PC filter on
`(pc & 0xFFF)` in `rs64_rsp_mid_sample`, and fflush every 4096 records.

Controls (same run): whole-RDRAM watch 10,000 callbacks; VI widths
320 -> 640 -> 1024 -> 512 (`0x006ab400` at 38.4 s, the port's hangar origin);
filter live (only PCs 300/2032 present); gfx-task/sync join 2172 == 2172.
The first attempt used the port's autopilot press schedule and never left 1024
(not evidence); the README schedule fixed it.

| width | gfx tasks | tasks w/ -32768 mid | samples @0x12C (-32768) | samples @0x7F0 (-32768) | task-end -32768 |
|---|---|---|---|---|---|
| 320 | 40 | 0 | 1040 (0) | 0 | 0 |
| 640 | 425 | 371 | 1,165,557 (12,050) | 125,377 (9,928) | 0 |
| 1024 | 1050 | 247 | 2,460,236 (754) | 87,340 (1,703) | 0 |
| 512 | 657 | 657 | 3,719,295 (61,195) | 1,435,299 (54,382) | 0 |

Verdict: the port's transient `0x8000` lanes at the mapped PCs are present in
retail in every hangar task and absent at task end (second line: s5335 stride-256
retail, 1,215 tasks). Port transient is legitimate; M4 closed, no mitigation.
