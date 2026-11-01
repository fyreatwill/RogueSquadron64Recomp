# NEXT: G1e — per-frame timeline of the serial frame loop at lvl5 FPS60 dd4 (why the budget is ~10 ms, which segment to cut)
HYPOTHESIS-ID: g1e-serial-frame

s6710: game thread (OSId 3) is serial: kick gfx task -> wait done (mq 0x8011A7E8) -> swap -> waitForPostSwapAck (0x80128CF0).
Tasks/s drops once guest cpu + gfx wait per frame exceeds ~10 ms (not 16.7). tools/g1e_gt.py, scratch/agent/s6710_gt.zsh.

## Hypotheses
- H-phase: the ack arrives late in the VI (the game starts each frame several ms after the VI edge), so only ~10 ms remain.
- H-latency: host delivery latency (SP kick -> Gfx thread start, RSP end -> DP-done osSendMesg -> game wakeup) eats ~6 ms.
- H-rsp: the RSP LLE ucode run dominates the gfx wait at dd4 (cut it: ucode hot paths / -O3 / vector ops).
- H-cpu: guest CPU per frame (~7 ms in slow seconds) dominates; find the top guest functions (sample OSId 3 host stack).

## Work unit (ONE build, ONE run)
1. Ring buffer (no per-frame stderr), dumped at exit: per frame wall stamps for VI edge, game ack recv (0x80128CF0),
   SP task kick (osSpTaskStart), Gfx thread task start, RSP end, DP-done send to 0x8011A7E8, game recv of it, osViSwapBuffer.
   Positive control: segments sum to frame-to-frame interval.
2. Same s6710 recipe (as=3 arm is the one that matters). Report per segment median/p90 in fast vs slow frames.
3. Side check still owed: hangar/menu render under ASYNC=1 NODRAIN=1 (queue as soak).
