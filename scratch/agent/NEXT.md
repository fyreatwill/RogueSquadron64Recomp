# NEXT (s7647)
HYPOTHESIS-ID: g5b-slot-recycle

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7646 (CURRENT-TRUTH item 32): PI refills of bytes a gfx DL reads happen ONLY at dd>1 (dd1 0, dd4 L4 4912 / L5 2267 per 120 s).
H-slot-recycle: the level-data chunk cache (256-B ROM chunks issued by guest thread 1 into 0x153000 / 0x195000-0x1CB000) has
too few slots for the dd>1 cell window, so a slot still referenced by the current/next DL is evicted and refilled.
Competitors: H-window (the cache is large enough, but the dd>1 cell list requests a chunk for a cell already dropped from the
cache's own visibility rule, i.e. the extended cells bypass the cache's "in use" pinning), H-dlref (the DL keeps a stale
pointer into a slot that the cache considers free at retail too, harmless at dd1 only because the slot is never reused in
time).
Work unit (offline first, then ONE build):
1. Find the cache: grep the generated code / PORTING-STATE for the thread-1 loader that issues 256-byte osPiStartDma
   (ROM 0x2F0000-0x4B0000) into 0x195000+ (try `grep -n '0x100' ` near osPiStartDma callers in RecompiledFuncs, or arm
   ROGUESQ_S7518 [cache] op=dma0 n=100 logging for 5 s; NOTE it prints the same ctx->r31 that read 0 in s7646, so if ra=0
   there too, walk thread 1's entry point instead: OSThread id 1's entry from osCreateThread, then its PI callers).
   Name the slot table, slot count, and the in-use / LRU rule.
2. One build, arms L4 dd1/dd4: log per frame (a) chunk requests, (b) evictions of a slot whose chunk a DL fetched in the
   last 2 tasks (= the s7646 stale event, now attributed to a cache decision), (c) slot count in use.
   Outcome: evictions-of-referenced only at dd4 and slots in use == capacity -> H-slot-recycle; fix = more slots carved
   from the dd>1 spill area (0x80800000+, gfx-reachable below 0x81000000) behind the dd policy, then compare
   rd.after.pi (should fall to ~0) and the G5b drop detector at dd4. Slots in use < capacity -> H-window / H-dlref.
Rules: never launch under lldb; never touch build/saves; one game at a time; SIGKILL only.
