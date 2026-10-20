Single next work unit (s5644): follow the started speech voice downstream of alloc. Build ONE instrument (env ROGUESQ_LOG_HUDBIT, fixup script) carrying ALL of:
 (1) consumer of osSendMesg queue 0x80154650 (grep funcs_26.c for 0X4650 / who calls osRecvMesg on it): count recvs + message value;
 (2) slot byte +0x1200 and word +0x120C of slot 0..3 sampled every 600 ticks of tickSpeechSubsystem (does state advance past 1, or reset to 0/-1 = voice killed);
 (3) initMusyXVoiceSlot (0x8009BE40) args/return + whether sample-ROM DMA (osPiStartDma) is issued for the clip's sample addr (log PI DMA count/addresses in the 2 s after each alloc);
 (4) count of ADPCM/loop commands in audio cmd lists whose sample addr lies in speech bank vs music.
Control: [aloc] entry + [spath] lines. Queue 2 soaks (copy soak_queue/done/s5642_aloc_a.sh).
H-D1 no recv of 0x80154650 msgs (consumer thread starved/not created: audio-disabled artifact => M5 de-stub target).
H-D2 recv ok but slot state reset to 0 within a tick (voice killed by reaper/slot-age logic).
H-D3 state persists but no PI DMA of sample data (sample bank load path stubbed).
H-D4 DMA ok and cmds emitted => ucode/mixer drops it (compare retail oracle AI PCM).
HYPOTHESIS-ID: g2-voice-never-requested
