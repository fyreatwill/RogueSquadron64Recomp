# Next work unit

HYPOTHESIS-ID: rt64-opt-frame-limiter

s4907: RT64 was built -O0; `ROGUESQ_RT64_OPT` (-O2 on the rt64 target) cut gfx task cost 23 -> 8.5 ms, but the gfx task rate is still 30/s. Find what limits the port to 30 swaps/s now.

Hypotheses:
- H-guest-O0: recompiled guest code (-O0, Debug) is the CPU-bound limiter -> main thread busy ~30 ms/frame.
- H-frame-limiter: the game's own retrace-per-frame divider holds 30 Hz by design; retail swaps at 1 retrace/fb-change (s4901) but port shows 2.
- H-sleep-paced: VI thread / scheduler sleeps in the port (ultramodern) quantise the gfx task to 2 VIs.

Discriminating measurement (ONE build, both binaries concurrent): per-second counters of (a) osViSwapBuffer fb changes, (b) retrace messages delivered, (c) game-thread busy ms vs blocked-in-osRecvMesg ms, on the -O2 rt64 binary; control = a deliberate sleep arm must raise the metric it should. Outcomes: busy ~33 ms -> H-guest-O0 (then test -O2 on ONE recomp TU class with caution; see s67 DCE caveat in PORTING-STATE); mostly blocked in osRecvMesg on retrace -> H-frame-limiter / H-sleep-paced.

Binaries: build/RogueSquadron64Recomp (-O2 rt64) vs build/RogueSquadron64Recomp_O0. Recipe template: scratch/agent/run_s4907_o2.sh. If a cmake reconfigure regenerates shaders and fails on 'metal', run `zsh scratch/agent/s4907_touch_shaders.sh` first.
