# NEXT (s7560)
HYPOTHESIS-ID: regen-fidelity-drift

19b(a) CLOSED s7559 (H-layout: 35 new rows SLOTPERM = s7487 slot order, 0 open LOST; docs/REGEN-VERIFY.md s7559).
Unit: 19b(b), the host-code census debt that stops tools/regen_replay.sh before it can print "ok":
  python3 tools/s7363_hostarr_census.py --rt64 --check          -> OPEN 27 (rows from s7480-s7535 host code, e.g. s7535_ga_chk g_st[16])
  python3 tools/s7364_heapbuf_census.py --rt64 --check -q       -> OPEN 71 keys 41
  python3 tools/s7366_lockset_census.py --check                 -> OPEN 82 (e.g. s7523_slow_rdp scan_bad unlocked@102)
  (--gen scratch/s7558/replay variants: 0 open.)
Per row: H-bounded (index provably in range: write the verdict row in the *_reviewed.tsv with the reason) /
H-real (a real out-of-range or unlocked access: fix the code, re-run) / H-analyser (census misreads an idiom: fix the census,
add a control). Discriminator: read each site; use --emit-open to stub rows. Controls: each census's --selftest/--controls must
still pass and a planted unbounded subscript must come back OPEN. Done when regen_replay.sh scratch/s7560/replay runs to "ok".
Then 19b(c): fold s7558_b40_ab when SOAK-RESULTS has it, then ask the owner about the B40 default.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
