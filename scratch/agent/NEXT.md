# NEXT (s7646)
HYPOTHESIS-ID: ts4-gfx-pi-dl-stream

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

TS-4 (s7645, CURRENT-TRUTH item 32): gfx tasks fetch DL bytes (DMEM 0x170) that guest PI DMAs write during the same task; 71/120 s
on L4 dd2 in the stale order (task read first, then PI replaced). H-clean refuted. Open: H-live (port timing: our gfx task runs
~95% of wall time, so streamed level data lands mid-task far more often than on hardware; a candidate for G5b terrain drops,
which the owner sees only at dd>1) vs H-retail (the same overlap is benign on hardware, e.g. the chunks are next-frame data in a
slot the current DL no longer references).
Work unit, ONE build, ONE recipe:
1. Add to the gfx mode: (a) for the stale-order case, whether the task re-fetched the same range later in the task (consumed both
   old and new) and (b) for rd.after.pi, the issuer: record the guest thread / ra at osPiStartDma (not g_rs64_last_guest_pc).
2. Arms L4 + L5 at dd1 and dd4 (FPS60 16:9, 120 s, `ROGUESQ_S7644_RSPDMA=2 ROGUESQ_S7644_RSPDMA_CTL=1`) via
   tools/g1e_owner_quiet_arms.zsh (mkdir -p $R first: the recipe does not create it).
Outcomes: rd.after.pi / stale-order near 0 at dd1 and large at dd4 -> H-live leads, next build a fix arm (guest PI ROM read into a
range the running gfx task has read or will fetch waits for task end, ROGUESQ_S7646_PISYNC=1) and compare G5b drop counts. Equal
at dd1 and dd4 -> the overlap does not explain dd-only drops; close TS-4 as H-retail-like and return to owner items.
Rules: never launch under lldb; never touch build/saves; one game at a time; SIGKILL only.
