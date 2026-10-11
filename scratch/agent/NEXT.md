# Ground-truth the retail source-table relationship
HYPOTHESIS-ID: m5-audio-destub

s4603 selected caller `0x80022B44` in the qualified VI-640 phase. It copies
five stable 16-byte, printable name-like records from `0x8062B9F8`,
`0x8062BA1C`, `0x8062BA40`, `0x8062BA64`, and `0x8062BA88` to
`0x801724C0..0x80172510`; the fourth source supplies `late` at destination
offset `0x34..0x37`. The port result is single-source for semantic identity.
Retail independently writes the same target span from `0x80007670`, but its
source-table relationship is still unknown.

Competing hypotheses:

- H-retail-equivalent: retail carries or writes the same five name-like records and the target span is the same table-copy path.
- H-port-only-source: retail reaches the target span but does not carry/write the same source records; the port source publication diverges.
- H-retail-different-table: retail uses a different stable source table or record layout while preserving the target writer contract.

Discriminating measurement: retail oracle watch of the whole-RDRAM positive
control, physical source span `0x62B9F8..0x62BA98`, and target span
`0x1724C0..0x17250C`, with VI width/origin phase logging. Same-record bytes
and source-span activity aligned with target writes select H-retail-equivalent;
target writes with no matching source records select H-port-only-source; a
stable but different retail source span selects H-retail-different-table.
Do not add a mitigation.

No build is needed. Run the independent oracle from the repo root:

```sh
mkdir -p scratch/agent/s4604_retail_source_table
env tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 60 \
  --watch-write 0x0:0x800000 \
  --watch-write 0x62B9F8:0x62BA98 \
  --watch-write 0x1724C0:0x17250C \
  --hit-cap 200 --pc-phase-quiet \
  --pc-phase-log-width 0x00790400:1024 \
  --pc-phase-log-width 0x006AB400:512 --vi-trace \
  > scratch/agent/s4604_retail_source_table/retail.log 2>&1
```
