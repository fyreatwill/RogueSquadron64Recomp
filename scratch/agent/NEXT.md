# Next work unit (s4428): was the earlier copy into a live block?

HYPOTHESIS-ID: m5-selector-copy-lifetime

Session 4427 selected H-residual for the post-publish window. The bytes at
the first title `0x80091064` were already `mat_` / `ltex`. The only earlier
CPU stores are four `sb` each at `0x80007670`, the store in the bounded copy
`0x80007640`, called from `0x80022B44` with length 16. Destinations were
already `0x80171CE0` (origin `0x00696600`, t=7.3s) and `0x80173B20` (same
origin, t=9.4s). The table publish of those pointers is the later `sw v0`
at `0x8008F228` / `0x8008F264` (this run: width 640, origin `0x00790A00`).
s4426 showed that publish value is the malloc return `header+16`.

Malloc reads a halfword at header+0 and tests bits `0x1` and `0x8`. The size
word is at header+4. Do not assign names to those bits beyond what the
`andi` tests. The two headers are `0x80171CD0` and `0x80173B10`.

Competing hypotheses:

- H-write-into-free: at the `sb`, the header still has the large free size
  (`0x232C0` on the first block in s4426). The copy writes memory malloc
  later returns uncleared.
- H-previous-owner: at the `sb` the header is a small allocated block, and a
  later store marks it free before the establishing malloc returns the same
  user pointer.
- H-not-a-fresh-split: the header fields are unchanged between the `sb` and
  the establishing `sw`. That contradicts s4426's fresh split for this run.
- H-join-failure: the four `sb` rows, the two establishing stores, or the
  title `0x80091064` load are missing, so the header sample has no window.

Discriminating measurement: one retail oracle capture. Sample the header
halfword and size word at each of the four `sb` rows and at both
establishing stores, and log every store to those eight header bytes with
PC, value, width, and origin. A free-size header at the `sb` selects
H-write-into-free. An allocated header at the `sb` plus a later free-store
before the `sw` selects H-previous-owner. Identical header fields at the
`sb` and the `sw` select H-not-a-fresh-split. Do not rewrite heap state.

Exact commands:

1. The oracle binary must be newer than `tools/oracle/rs64_oracle.c`. The
   s4427 repeat-store and comma-separated `RS64_MEM_DUMP` prints are already
   there. Add a header sample on the existing user-word store rows when
   `pc==0x80007670` and on the establishing `sw` rows, or an equivalent
   one-run sample of physical `0x171CD0` (half) and `0x171CD4` (word), and
   `0x173B10` / `0x173B14`. Rebuild only if the source is newer.
2. Run from the repo root with `--oracle-emulator 1`, Rice, the Start-press
   schedule, `--secs 25`, `--exec-no-defer`, whole-RDRAM watch 0, the two
   table watches, the two user-word watches, and header-byte watches.
   Print `0x80091064` only at `0x00790400:1024` and `0x00790800:1024`. Do
   not arm execution from `0x00790500` or `0x00790A00`.
3. Kill with SIGKILL only if the oracle overruns. Require the whole-RDRAM
   line, both `0x80171CE0` / `0x80173B20` store rows, the four `sb` rows,
   and one title `0x80091064` row whose `v0` is one of those pointers
   before interpreting a header value.
