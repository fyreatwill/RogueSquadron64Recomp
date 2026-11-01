# NEXT: G3 -- lvl3 one-frame lag: compare the per-frame time snapshot (osGetTime-derived) port vs retail
HYPOTHESIS-ID: g3-lvl3-frame-lag

s6751: from the rngSeed=1 poke at the 640->512 flight switch, the rand call sequence is identical in both arms for 75
calls / 12 game frames (caller, value, calls per frame). Then the NPC gate transformVec3ToNpcLocalWithScale (0x8001DC34,
called from advanceNpcOnCurvedPath at 0x8006C010, result at 0x8006C018) flips for NPCs ..fc90 (1->0), ..2700 (0->1) and
later ..fbb0 (1->0) one game frame LATER in the port, every time. So whatever that gate tests (a point vs the object in
advanceNpcOnCurvedPath's $a1, probably the player craft) is one frame behind in the port.
The per-frame step is clock-based: frame tick 0x800AF35C bumps 0x8013889C after timeSnapshotFiller (0x8000BC00:
awaitFrameSyncMesgBlock, osGetTime 0x8002BF00, readBufferSwapState, three cvt/div.s ratios into a struct at its $a0 =
caller sp+0x10, fields read back at sp+0x2C/0x30).
Hypotheses:
- H-time-dt: the snapshot's dt/ratio fields differ (port osGetTime/osGetCount timebase, or 2-VI frame period measured
  differently: port update_screen 61-62/s), so the player moves a different distance per frame and crosses the gate later.
- H-sim: snapshot fields identical, but the player/NPC position arithmetic differs (float path in the port).
- H-start: the player starts the flight one frame behind (one extra/missing frame before the first rand row).
Discriminator (one port build, one retail run, same recipe as s6751):
1. Oracle: extend --exec-trace rows with N words at $sp+OFF (e.g. RS64_XTRACE_SP=0x10:10) and add
   --exec-trace-also 0x800AF374 (just after timeSnapshotFiller returns; struct at sp+0x10..0x37). Also log the player
   position: find advanceNpcOnCurvedPath's $a1 object (print $a1 at 0x8006BEC8) and dump its position words.
2. Port: matching marker rows in tools/fixup_rand_trace.py at 0x800AF374 (sp+0x10 words) and the $a1 object.
3. Commands: port  env AP=6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,42.5:w640,50:start SECS=95
   CAP0=200 SAVE_FROM=scratch/s6750/lvl3.eep XE="ROGUESQ_DEBUG_WRITE=80003470:1:512:65 ROGUESQ_RAND_TRACE=$PWD/scratch/s6752/port_rand.txt"
   zsh tools/g3_port_capture.sh scratch/s6752/port ; retail: copy scratch/s6751/retail.sh (D=scratch/s6752), SECS=115.
   python3 tools/g3_rand_align.py <retail oracle.log> <port txt> 0
Outcomes: snapshot fields differ per frame -> H-time-dt (fix the port's osGetTime/count timebase or frame-sync delivery
so dt matches retail's); identical fields but player position drifts -> H-sim (bisect the position update);
first-frame position already one step behind -> H-start.
