# NEXT (s7326): do spill blocks leak across the retail scene reset?
HYPOTHESIS-ID: spill-scene-reset-leak
Context (s7325): the retail scene-change bulk free (coalesceFreeHeapBlocks 0x800022F8: frees every persistent-heap block whose header
tag lacks 0x80, no rs_free) cannot release spill-arena blocks (0x81000000+, not in the guest chain). Arm e (dd8 21:9 L4) heapsync #8
logged 1 live non-persistent spill block (initWaterSprayEffectAndSfx 0x2FD0) after a reset. The [s7325] heapsync stderr line already
prints spill live / nonpersist count+bytes+owners at every sync that dropped heap blocks (ROGUESQ_S7317_ALLOCMAP=1).
Hypotheses:
- H-leak: non-persistent spill blocks survive each reset and are never rs_free'd later -> spill live bytes ratchet up per scene change
  (retail would have reclaimed them); eventual spill exhaustion -> NULL rs_malloc at dd>1 after long play.
- H-freed-later: the game frees them explicitly afterwards (the block is owned by an object that is torn down by rs_free) -> no growth.
- H-persistent-only: survivors are all tag 0x80 in steady state; the one s7325 datum was transient.
Discriminator (ONE build, ONE run): add to rs64_s7325_heapsync a per-sync list of surviving non-persistent spill ptrs and, in the
spill free hook (rs64_s6569_isspill), mark when one of those ptrs is later freed (time since the reset). Route with MANY scene changes:
hangar -> mission -> abort -> hangar -> mission x3 at dd8 21:9 (see G5i abort recipe in PORTING-STATE s6995) or the forced-level
route repeated; log spill live/nonpersist after every sync. Positive control: a synthetic spill block allocated with a1=0 right
before a sync (ROGUESQ_S7326_CTL=1, rs_malloc via the spill path) must appear in the survivor list.
Outcomes: H-leak -> free non-persistent spill blocks in heapsync (retail semantics), qualify two arms (fix on/off) with spill live
bytes per scene change and a 300 s hold; H-freed-later / H-persistent-only -> close item 21.
Parallel open (item 22): 46 audio reads of song-channel arrays freed 0-14 ms earlier at the scene transition
(waitForMusyXAudioTaskDone via musyxNoopStub) - is the wait real?
