# NEXT: fold the s6835 boot-freeze hunts (with the new [stall-dump])
HYPOTHESIS-ID: boot-freeze-capture

Context: s6814 a30_s2 froze at boot (fs=39, VI held on 0x6BA280, audio flowing). s6835 localized it offline to
advanceVideoFrame's drain loop 0x80018264 (after partitionFramebufferMemory(640,480) at fs~40): it waits for no arbiter slot
(0x80128EAA, count 0x80128EAD) in state 3/4; viRetraceHandlerThread (thread 8011CD28) clears those every VI under the
frame-sync mutex 0x80128D10. Freeze rate 1 in 43 boots. Passive [stall-dump] (default on) now prints slot states and the
waiting thread of each queue on any >=600-VI fullsync stall (hunts use 300).
Step 1: SOAK-RESULTS tail; `grep -a stall-dump scratch/s6835/hunt_{c,d}/*freeze*.tail.log`; the soak result logs.
Outcomes (game thread = 80163E20, retrace = 8011CD28):
- 0x80128D10 valid=0 with mtq=8011CD28 (retrace parked on the mutex, game parked on 0x80128CF0) -> H-lost-mutex: a
  token was received twice / a send lost; read ultramodern message_queue send/recv for the NOBLOCK-send path
  (signalFrameSyncMesgNonblock / retrace unlock use osSendMesg NOBLOCK) and fix.
- 0x80114388 mtq=8011CD28 with valid=0 for the whole stall (retrace never woken) -> H-lost-vi: VI event delivery to the
  guest stopped while update_screen runs; read ultramodern events.cpp VI path.
- retrace cycling (slot states change between the two dumps) but game still on 0x80128CF0 -> H-lost-post (0x80037808 flag
  race between waitOnVideoQueue's sb and the retrace check).
- 22/22 clean again: rate < 1/65; record it, leave the passive dump on (it costs nothing) and take the next engineering rung
  (owner items pending: FPS60 feel, G1d/G3c sheets; otherwise ITERATION 3c ladder / G5 rename sweep).
