# s7527 class FU: manual classification of game-called replaced libultra rows (exec'd by s7527_host_replace_audit.py).
# Every reason names the reproducing host path or the readers (the tool's own G-join / O-join, or a closed class + session).
J_G = 'G-join: every absolute global it writes has readers only in replaced libultra (s7402 BL + this tool)'
J_MQ = 'O-join: its MQ/thread/timer objects have 0 direct field loads/stores in recompiled code (all access via replaced calls)'
NOPAK = ('H-canon', 'no-pak: host returns PFS_ERR_NOPACK / -1, retail with no Controller Pak inserted fails at the same call '
         'before any helper runs; save is EEPROM (osEeprom*), rumble/pfs paths are retail-equivalent to an empty slot')
ANNOT = {
    'rspbootTextStart': ('H-canon', 'RSP boot microcode bytes (data, not CPU code; never a CPU call target); game stores its address '
                         'in OSTask.ucode_boot; host RSP runs the task ucode directly (s7521 FR: every IMEM image compiled or routed)'),
    '__ll_div': ('H-canon', 'pure 64-bit arithmetic, librecomp math_routines.cpp; only caller lldiv (printf path)'),
    '__ll_mul': ('H-canon', 'pure 64-bit arithmetic, librecomp math_routines.cpp; only caller lldiv'),
    '__ull_div': ('H-canon', 'pure 64-bit arithmetic; only caller _Litob (sprintf)'),
    '__ull_rem': ('H-canon', 'pure 64-bit arithmetic; only caller _Litob (sprintf)'),
    '__osDisableInt': ('H-canon', 'interrupt mask around musyxSynthFrame; host guest threads run one at a time (ultramodern), '
                       'thread-queue/RT64-writeback races closed s7492 EQ'),
    '__osRestoreInt': ('H-canon', 'pair of __osDisableInt (same reason)'),
    '__osContRamRead': NOPAK, '__osContRamWrite': NOPAK, '__osPfsSelectBank': NOPAK,
    'osPfsFindFile': NOPAK, 'osPfsReadWriteFile': NOPAK, 'osMotorInit': NOPAK, 'osMotorStart': NOPAK, 'osMotorStop': NOPAK,
    'osPfsInitPak': NOPAK, 'osPfsRepairId': NOPAK, 'osPfsAllocateFile': NOPAK, 'osPfsDeleteFile': NOPAK,
    'osAiSetFrequency': ('H-canon', 'AI regs -> host audio rate; G2 audio fidelity CLOSED (owner listen 2026-10-22); ' + J_G),
    'osAiSetNextBuffer': ('H-canon', 'AI DMA -> host audio queue; hdwrBugFlag readers replaced only; M5/G2 closed'),
    'osContInit': ('H-canon', 'controller init; __osContinitialized readers replaced only; pad contract s7400 CONTFIX PASS'),
    'osContStartQuery': ('H-canon', '__osContLastCmd readers replaced only; status errno (+3, game-read) written by host, s7400'),
    'osContGetQuery': ('H-canon', 'O-join: game reads gControllerStatuses +3 (errno) only; host writes OSContStatus, s7400 CONTFIX'),
    'osContStartReadData': ('H-canon', 'same as osContStartQuery'),
    'osContGetReadData': ('H-canon', 'O-join: pollControllerInputs reads gControllerPads button/x/y/errno; host writes all, s7400'),
    'osCreateMesgQueue': ('H-canon', 'ultramodern writes the guest OSMesgQueue; ' + J_MQ),
    'osSendMesg': ('H-canon', J_MQ), 'osRecvMesg': ('H-canon', J_MQ), 'osJamMesg': ('H-canon', J_MQ),
    'osCreateThread': ('H-canon', '__osActiveQueue readers replaced only; ' + J_MQ + '; thread queues s7492 EQ'),
    'osStartThread': ('H-canon', J_MQ), 'osStopThread': ('H-canon', J_MQ), 'osDestroyThread': ('H-canon', J_MQ),
    'osSetThreadPri': ('H-canon', J_MQ), 'osYieldThread': ('H-canon', 'host yield; ' + J_MQ),
    'osSetTimer': ('H-canon', 'O-join: installPeriodicCallback timer 0x801128F0 has 0 direct field reads; host timer posts the msg'),
    'osSetEventMesg': ('H-canon', 'host event table; PRENMI (preNmiResetThread) never posted, inert s7401/s7403'),
    'osViSetEvent': ('H-canon', 'host VI event; __osViDevMgr/vi readers replaced only (G-join)'),
    'osCreatePiManager': ('H-canon', '__osPiDevMgr readers replaced only (G-join); host PI DMA is synchronous'),
    'osPiStartDma': ('H-canon', 'O-join: piDmaWorker OSIoMesg 0x80111274 0 direct field reads; DMA bytes/cache shape s7518 FO'),
    'osCreateViManager': ('H-canon', '__osViDevMgr/viRetraceMsg readers replaced only (G-join)'),
    'osViBlack': ('H-canon', 'writes __osViNext context; readers replaced only (G-join: __osViNext/__osViCurr repl_readers only)'),
    'osViSetMode': ('H-canon', 'same as osViBlack; host vi.cpp + upstream_compat mode path'),
    'osViSetSpecialFeatures': ('H-canon', 'same as osViBlack'),
    'osViSwapBuffer': ('H-canon', 'same as osViBlack; swap/origin contract measured many times (s7096 forwarding)'),
    'osViGetCurrentField': ('H-canon', 'retail reads VI_CURRENT bit0; oracle s2199/s2211: 415/415 watched retail returns = 0; host 0'),
    'osDpSetStatus': ('H-canon', 'DPC_STATUS write -> librecomp dp.cpp'),
    'osDpGetCounters': ('H-dead', 'host zeroes the 4 counters; only caller submitGfxFrame profiler path, profiler gate 0 (s7514 FK)'),
    'osEepromProbe': ('H-canon', 'host save type 16K = retail cart EEPROM'),
    'osEepromLongRead': ('H-canon', 'host EEPROM file read (owner save; ROGUESQ_NO_SAVE_WRITE)'),
    'osEepromLongWrite': ('H-canon', 'host EEPROM write (suppressed by ROGUESQ_NO_SAVE_WRITE in tests)'),
    'osGetTime': ('H-canon', 's7514 FK: 46875.0 ticks/ms monotone; osClockRate scaled s7402 BL'),
    'osInitialize': ('H-canon', 'osClockRate *=3/4 restored s7402 BL (CLOCKFIX); exception vectors 0x80000000-0x18C unread; '
                     'bzero(osAppNMIBuffer) readers unreachable (s7403 BM) and host RDRAM starts zero'),
    'osInvalDCache': ('H-dead', 'host memory coherent; D-cache contract closed s7518 FO'),
    'osWritebackDCache': ('H-dead', 'same as osInvalDCache (s7518 FO)'),
    'osWritebackDCacheAll': ('H-dead', 'same as osInvalDCache (s7518 FO)'),
    'osInvalICache': ('H-dead', 'host executes recompiled code; code bytes == ROM image s7520 FQ'),
    'osVirtualToPhysical': ('H-canon', 'KSEG0/KSEG1 mask = retail for direct-mapped addresses; only caller _VirtualToPhysicalTask'),
    'osSpTaskLoad': ('H-canon', 'with the s7524 V2P path credited; default port skips it: measured s7524-s7526, render input '
                     'H-same (same-run twin), V2P stays opt-in (owner row)'),
    'osSpTaskStartGo': ('H-canon', 'host RSP task start; O-join gspTask: game never reads task flags +4'),
    'osSpTaskYield': ('H-canon', 'host yield request; same O-join'),
    'osSpTaskYielded': ('H-canon', 'retail writes OS_TASK_YIELDED into task flags +4; O-join: 0 game readers of +4'),
}
# Retail helpers whose skip is proven unobservable (lifts the mechanical H-gap). name -> {helper: reason}
HELPER_OK = {
    'osInitialize': {'bzero': 'zeroes osAppNMIBuffer 0x8000031C (cold boot); readers unreachable s7403 BM; host RDRAM zero'},
    'osPfsAllocateFile': {'__osPfsDeclarePage': 'pak inode write; unreachable (no pak: host NOPACK at osPfsInitPak)'},
    'osPfsDeleteFile': {'__osPfsReleasePages': 'pak inode write; unreachable (no pak)'},
    'osPfsInitPak': {'__osIdCheckSum': 'pak id checksum; unreachable (no pak)'},
    'osPfsRepairId': {'__osIdCheckSum': 'pak id checksum; unreachable (no pak)'},
}
