# Next work unit (s4379): ordinal-join actual payload writers

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4378 qualified both payload ranges and found writers outside the
previous candidate set. Do one batched retail-oracle capture; do not build the
port.

Competing hypotheses:

- H-writer-after-publication: an observed payload writer runs after the
  `0x80033FCC` task publication and overwrites the published payload.
- H-writer-before-publication: observed payload writes precede publication;
  the payload difference is upstream selector/decode output.
- H-writer-watch-boundary: the observed PCs are still not the complete writer
  set, so the apparent ordering is an instrument boundary.

Discriminating measurement: watch physical ranges `0x178C80:0x179A48` and
`0x1E2FC0:0x1E3300`, phase-gate writer PCs `0x8008F7D4`, `0x80091374`, and
the nearby range-specific sites from s4378, and use `--ordinal-join` with the
typed `0x80033FCC` task publication. A qualified after-publication count for
an observed writer selects H-writer-after-publication; qualified before-only
writes select H-writer-before-publication; live payload writes with no joined
observed writer selects H-writer-watch-boundary. Require the whole-RDRAM
positive control, all three VI buckets, at least 1,000 valid type-2 rows, and
nonzero writer hits before interpreting a null.

Exact command: `zsh scratch/agent/run_s4379_m5_payload_writer_ordinal.sh`.
The script must include both payload watches, `--watch-pc 0x80033FCC`,
`--pc-task-dump 0x80033FCC --pc-task-type 2`, `--ordinal-join`, the three
phase buckets, and `--pc-hist-watch 1 --pc-hist-watch 2`. Kill with SIGKILL
after 75 seconds and capture from the repo root.
