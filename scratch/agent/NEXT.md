# NEXT: who readies audio thread 0x3001494b0 (pri 122, entry 0x8008ED70) before alloc #2, and is it runnable in retail during reapplyAudioConfig?
HYPOTHESIS-ID: m5-audio-destub
Context (s4581): allocator thread preempted at rs_malloc lock osRecvMesg by already-queued pri-122 audio thread (see PORTING-STATE s4581).
Hypotheses: H-ai-event (our timer-driven AI/VI osSendMesg readies it; retail AI cadence would rarely land here); H-retail-same (retail also preempts, and its mixer tolerates the window via state we mis-initialise); H-stop (retail audio thread is stopped/blocked on a handshake during reapplyAudioConfig that we skip).
Discriminator (ONE build): in schedule_running_thread + mesgqueue send paths log (when target==0x3001494b0) caller backtrace, queue ptr, ts relative to [s4579-A]; also log the audio thread's own blocking recv queue. Add oracle check: retail mupen run with exec watch at 0x8008ED70 across reapplyAudioConfig (positive control: whole-RDRAM watch). Outcome: readied by timer send -> H-ai-event; readied by guest send before A -> compare retail ordering.
Recipe: scratch/agent/s4581_switch.sh.
