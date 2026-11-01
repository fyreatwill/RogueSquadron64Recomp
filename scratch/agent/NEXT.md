# NEXT: G3 -- lvl3 combat desync: compare the rand call sequence port vs retail from the flight switch
HYPOTHESIS-ID: g3-lvl3-rng-desync

s6750: mission 3 flight matches retail for ~6 s of lit flight, then the arms split at the first enemy hit on the player.
rngSeed (0x80003470) = 1 written at the 640->512 flight switch in both arms (oracle --debug-write 80003470:1:512:85, port
ROGUESQ_DEBUG_WRITE=80003470:1:512:65) flips which arm is damaged but does not remove the split. Retail makes 0 rand
calls during its 4.3 s flight load, so retail state at the first flight frame is fully set by the poke.
Hypotheses:
- H-port-rand-count: the port calls rand a different number of times (during its 0.5 s load, or per flight frame).
- H-time: enemy fire/AI keys on osGetCount / VI count / wall time, not game frames (port update_screen 61-62/s).
- H-sim: same rand sequence and timing, but the port's hit/bolt arithmetic differs.
Discriminator (one port build, one retail run):
1. Port: log the first ~3000 rand calls after the flight switch: call index, update_screen #, returned value, $ra
   (fixup hook on rand 0x80003430 in tools/fixup_*.py, or a runtime hook; gate on ROGUESQ_DEBUG_WRITE having fired).
2. Retail: env RD=rng3 SECS=125 XA="--debug-write 80003470:1:512:85 --ordinal-join" zsh scratch/s6750/rng.sh
   (watch 0 is a dummy so the 10000-hit control removal does not truncate; add $ra via --watch-pc 0x80003430 if needed).
3. Align the sequences from the poke. The first differing index (and its $ra) names the term: extra/missing port calls
   -> H-port-rand-count (name the caller); identical sequence up to the hit frame -> H-time / H-sim (then compare the
   hit test inputs at that frame).
Saves: owner save sha 1dd1dec4...; mupen .eep cmp-equal to scratch/s6747/oracle.eep.
