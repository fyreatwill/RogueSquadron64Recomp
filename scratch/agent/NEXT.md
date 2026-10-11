# NEXT: who changes the voice-count halfword 0x80149700 from 18 to 32?
HYPOTHESIS-ID: m5-audio-destub
Context (s4577): the bad abort's a0 is voice-array base 0x801714D0 + 30*0x88, i.e. an index past the 18-voice array into a name-string table. The mixer loop bound (halfword 0x80149700) reads 18 at jal 80000 and 32 at the bad call (81166); the last visible guest store to it is the allocator sh 0x8008F0CC. Do not revisit tbl render records / voice words 0..7 (s4571-s4576 closed).
Competing hypotheses:
 H-host-write: a host-side write (PI DMA, memcpy in librecomp/ultramodern/rt64) overwrites 0x80149700; predicted by a logged host range overlapping phys 0x149700 at the change point.
 H-unhooked-guest-store: a guest store path the S4299 filter/hook skips (swl/swr or a store outside the hooked macro) writes 32; predicted by a polled change with no host range and no hook row.
 H-misread: s4540 and s4571 read different words; predicted by a polled 0x80149700 that stays 18 at the bad call.
Discriminator (ONE build): in rs64_s4540_call (funcs_24.c, via a new tools/apply_s4578_*.py) poll MEM_HU(0x80149700) every call; on first change print call index, old/new, words 0x801496F8..0x8014971F and the s4577 CB ring. In the host PI DMA/memcpy path log (phys dst, len, vi_w) for any range overlapping 0x149700..0x149720. Positive control: the allocator sh 0x8008F0CC must appear as a polled change at the n=5 alloc (15->18) in the same run.
Outcomes: poll=32 + overlapping DMA range -> H-host-write (name the source; does retail DMA there?); poll=32 + no range -> H-unhooked-guest-store (enumerate store macros the hook misses); poll=18 at bad call -> H-misread (s4540 `count` is not the loop bound; fix instrument).
Recipe: copy scratch/agent/s4577_ring.sh to s4578 (3 arms). If lib/ is edited run ./submodule-patches/export.sh and commit.
