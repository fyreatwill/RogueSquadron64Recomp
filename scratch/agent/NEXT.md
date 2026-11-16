# NEXT (s7493)
HYPOTHESIS-ID: m3-store-path-coverage

Fold first: soak s7492_eq_levels (L1 dd8 21:9 os_tq_link, L7 dd4 os_rt64fb, L10 dd4 os_tq_head, L12 dd4 os_rt64fb;
tools/s7492_eq_recipe.zsh). score=0 + plant DETECTED fn=<kind> on all arms -> EQ CLOSED for 6 levels (L1/L4/L15 s7492 + these).
Any os_tq_*/os_rt64fb uaf-store row with loc=F/R: chase it (free-bt + store-bt are in the log with S7475_BT=1).

Work unit: class ER, RT64 writeback liveness (seeded by the s7492 boot-time loc=N row: os_rt64fb a=80787810, n=6C30, block freed
0.24 s earlier by freeManifestSegmentAssets <- runIdleFramesAndLoadSaveData, swap#42).
Already known (s7492 run 2): ~51k writebacks per arm, ALL class O (H=0): RT64 never wrote into a LIVE rs_malloc block. The open
question is only writes into memory the game released.
Hypotheses: H-wb-live (every copyNativeToRAM target [phys, phys+bytes) is a colour/depth image the game's RDP stream set in the
current or previous frame -> the loc=N row is the game legitimately reusing released memory as a framebuffer) / H-wb-stale (RT64 writes
back a framebuffer pair whose address the game has not set for >= 2 frames -> a host writer into memory the game may own for something
else; name the frame gap and fix in RT64 by dropping pairs older than the last SetColorImage/SetDepthImage).
Instrument (ONE build): in src/rsp/dpc_bridge.cpp (or wherever the RDP stream is forwarded; grep SetColorImage / 0x3F / 0x3E) record a
ring of (frame/VI index, colour-image phys, depth-image phys); in main.cpp rs64_wbw_post look phys up: age_frames since the game last
set that exact address (kind 0 colour vs SetColorImage, kind 1 depth vs SetZImage), count per arm {age0, age1, age>=2, never}, log the
first 20 age>=2/never with phys/bytes/kind. Env ROGUESQ_S7493_WBLIVE=1. Positive control: ROGUESQ_S7493_WBLIVE_CTL=<s> makes the lookup
pretend one fresh image address was never set (must print one `never` row with CTL). Run tools/s7492_eq_recipe.zsh-style arms
L4:1 and L15:8 (+boot through hangar: the loc=N row was pre-mission, so the count must cover boot).
Outcomes: never=0 and age>=2=0 (ctl fires) -> H-wb-live, ER CLOSED and the M3 heap-audit store/load series is DONE; then take the
ITERATION 3c ladder's next open rung (CURRENT-TRUTH Next steps 2-9 are owner-look; look for an engineering action before writing any
block). Any age>=2/never row -> H-wb-stale: fix in lib/rt64 (export.sh + commit), qualify with the same two arms.
