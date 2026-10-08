# Next work unit: M5 - name the unwatched writer of allocator tail 0x801499B4 (=0x801F9D10 while head 0x801499E4 == 0)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4230: fillSampleStreamRange+8136 is `lw $a0,0($v1)` at 0x8008FD60 with head==0, tail=0x801F9D10 (probe [s4230-FD60], 1 of 6 stale runs). Watched guest stores (rs64_m5_writer_parity, retargeted by tools/apply_s4230_listwatch.py) show only boot init before the crash.
Hypotheses: (a) host-side bulk write (osPiStartDma/memcpy/save/overlay copy) over 0x801499B0..E8; (b) guest store site without the writer_parity call (sb/sh/swl/swr/sdc/etc); (c) our own zero-init (pc 0x80000420/24 'D' stores) ordered after a legit tail write, so head is cleared after tail was set.
Discriminator: in ONE build, add (1) a host-side watch in the DMA/memcpy helpers (lib/N64ModernRuntime + src) for physical overlap with 0x1499B0..0x1499E8 (log pc/caller/len), (2) a per-VI or 1 ms poll of the 3 words logging first change with last-guest-pc, (3) positive control: log any DMA overlapping 0x80000000..0x80200000. Run scratch/agent/s4230_listwatch.sh (6 stale runs). Outcome a => host log names the copy; b => poll fires with no host hit; c => head write by 0x8008F8C8 after tail nonzero. Edits under lib/ need submodule-patches/export.sh + commit.
