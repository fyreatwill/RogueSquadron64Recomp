# Cooperative-scheduler busy-poll census (s7196)

Question (s7195 follow-up): can a guest loop that polls (OS_MESG_NOBLOCK, or osYieldThread on a RAM flag)
starve the guest thread that would end the poll? ultramodern runs one guest thread at a time. Another guest
thread runs only when the current one blocks or calls `check_running_queue`, which every osSendMesg / osJamMesg /
osRecvMesg does after draining external messages. That swap happens only to a STRICTLY higher-priority thread.
`osYieldThread_recomp` is a host `std::this_thread::yield()` (src/main/upstream_compat.cpp:738): it never
switches to another guest thread, and it does not drain external messages either.

Tools: scratch/s7196/census.py (every os{Recv,Send,Jam}Mesg call site plus its a2 flag) and scratch/s7196/asm.py
(the MIPS listing for a named function, taken from the RecompiledFuncs comments).

## Message calls: 99 sites
- osRecvMesg: 50 BLOCK, 3 NOBLOCK. The census's one "?" (pollDmaSlotStep) is BLOCK (0x8000384C li a2,1).
- osSendMesg: 7 BLOCK, 28 NOBLOCK, 9 pass-through `a2=a1` (SI/rumble wrappers). osJamMesg: 1 BLOCK, 1 NOBLOCK.
- The NOBLOCK receives are peekServiceMessage, tryRecvServiceMessage and serviceStreamingVoice. Each is ONE poll
  per call, and none of their callers retries until it succeeds:
  - mainEventQueueWorker (pri 0x20) polls, then runs one asset-load step. It goes back to a BLOCK
    recvServiceMessage when it is idle.
  - pollServiceMessageByte and menuSubtype02Handler poll once per frame.
  - serviceVoicePoolFrame runs once per audio frame.
- No NOBLOCK send sits in a loop that retries until it succeeds. A failed send is dropped, which matches libultra.

## osYieldThread sites: 29 (20 direct, plus the yieldThreadRet1 / yieldCurrentThread / yieldFromSpThread / yieldFromGfxFrame wrappers)
| Class | Sites | Verdict |
|---|---|---|
| `recv(BLOCK); [clear flag]; yield` | siServiceThread x3, waitDmaSlotComplete, pollDmaSlotStep, piDmaWorker, periodicCallbackWorker, musyxSynthFrame, bufferArbiterProducerScanWait x2, advanceVideoFrame x2, waitOnVideoQueue, bufferArbiterAllocSlot x2, acquireFreeBufferSlot, waitForPostSwapAck, viRetraceHandlerThread | SAFE: the block is where the scheduling happens. The yield is a no-op |
| a yield inside a loop that does work in chunks | tickBackdropLoaderWorker, mainEventQueueWorker, setupAssetDma | SAFE: each pass makes progress or calls an OS function |
| **spin on another thread's RAM flag** | waitForSerialIdle (`while *(u8*)0x80110741`) | Producer siServiceThread, **pri 0x76**. It sets the flag at 0x80002EC8 and clears it at 0x80002F38. In between, its only receive is on the SI completion, which osContStartReadData enqueued synchronously, so it never blocks with the flag set. The callers are the save-pak paths in funcs_2.c (save service, pri 4). SAFE |
| **spin on the DMA ring** | submitDmaSlot, waitDmaSlotComplete, pollDmaSlotStep: `while dispatchPendingPiDmaToWorker()==1 yieldThreadRet1()` | Producer piDmaWorker, **pri 0x78**. If busy (0x801126B8) is set, the dispatch returns 1 WITHOUT any OS call, so the spin never enters the scheduler. SAFE only while piDmaWorker cannot block with busy set. Its PI receive is fed by do_dma's synchronous completion, **except in the unknown-region paths, which posted no completion (fixed below)** |

Thread priorities, read statically from the osCreateThread / registerServiceWorker arguments:
- 0x7F thread3_video, 0x7A audio, 0x78 piDmaWorker, 0x76 siServiceThread, 0x75 VI retrace
- 0x20 DMA-slot / mainEventQueueWorker, 0x14 periodic callback
- 0xA mainBootstrapWorker / main loop and texture-cache loader, 9 idle

Every spin waits on a producer of higher priority than the spinner, so equal-priority round-robin never matters
(that is the one osYieldThread behaviour of real hardware we lack).

**Verdict: H-none for guest-produced polls. The class is closed, with one runtime hazard fixed:**
- librecomp/src/pi.cpp `do_dma`: a PI DMA read or write to an unmapped region only printed `[WARN]` and never
  posted the completion. On hardware the PI interrupt still fires.
- With the completion missing, piDmaWorker stays blocked with busy=1, and every DMA-ring spinner then livelocks
  without ever yielding to a guest thread.
- Fix: the completion is now posted (default on). `ROGUESQ_PI_UNK_COMPLETE=0` restores the old behaviour.
- `ROGUESQ_PI_UNK_TEST=N` sends the completion of the Nth ROM read through that path, as a forced arm.
- Two-arm qualification: s7196 entry in PORTING-STATE.md.
