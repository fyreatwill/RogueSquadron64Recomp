# NEXT: G1e — what binds lvl5 FPS60 dd4 at ~56 tasks/s once the Gfx thread is at 5.2 ms (ASYNC+NODRAIN)
HYPOTHESIS-ID: g1e-gfx-overlap

s6709: ASYNC+NODRAIN qualified (lvl1 dd1, lvl10 dd4, lvl5 dd4: 0 crash, 0 stall, frames sane). Same-run lvl5 dd4:
Gfx 9.56 -> 5.16 ms/task, 51.6 -> 55.9 tasks/s, p10 30 -> 42; worker keeps up (pend_jobs 2.0). lvl10 dd4 already 59.5.
The Gfx thread is now ~30% of a 16.7 ms frame, so the lvl5 dd4 shortfall is elsewhere.

## Hypotheses
- H-guest: the game thread's guest CPU per frame at dd4 (terrain cell build/submit, more objects) exceeds 16.7 ms in busy
  seconds -> game-thread busy ms/frame ~ 16-20 in the dip seconds, low tasks/s seconds = high busy seconds.
- H-wait: the game thread waits on something else (audio task / SP busy while the Gfx task still holds the RSP, msg queue
  for dp_complete) -> busy is low but wall between frames is high; time sits in osRecvMesg blocks.
- H-audio-rsp: audio RSP tasks queue behind gfx on the single SP thread -> aud task latency spikes in dip seconds.

## Work unit (ONE build, ONE run)
1. Add to the existing [g1b] line in lib/N64ModernRuntime/ultramodern/src/events.cpp (edit under lib/ -> run
   ./submodule-patches/export.sh + commit): per second, game-thread busy ms (thread CPU time of the guest main/game thread
   via thread_info or clock_gettime(CLOCK_THREAD_CPUTIME_ID) sampled at each gfx task submit), blocked-in-osRecvMesg ms
   on the game thread, and audio task count + mean SP-queue wait. Positive control: busy + blocked ~= wall per second.
2. Run `zsh scratch/agent/s6708_nd.zsh ndtog_dd4b 5 4` (same 3 arms). Correlate per second tasks/s against busy/blocked/audio
   wait in the as=3 arm. The term that co-varies with the low seconds selects the hypothesis.
3. Side check, same build, queue as a soak: hangar route + menus with ASYNC=1 NODRAIN=1 (fbd every 300 VI) for H-race in
   fb-effect scenes the in-flight sheets did not cover.
