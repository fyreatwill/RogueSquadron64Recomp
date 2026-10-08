#!/usr/bin/env python3
"""s4279c: s4279b showed the whole sample-stream node heap block (0x801F9CD0..0x801FB3F4, 1439 words) goes to zero
between two audio-thread ENTRYs with NO node-region store in the hooked store ring, i.e. another thread / unhooked
writer wiped it. Host poller thread (started at the first fillSampleStreamRange ENTRY): once node0.next
(0x801F9CE0) has been seen nonzero and then reads 0, sample g_rs64_last_guest_pc 16x back to back and print
[s4279-wipe]. Runs after apply_s4279b_ringdiff.py. Idempotent."""
import subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RF = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
subprocess.check_call([sys.executable, str(R / "tools" / "apply_s4279b_ringdiff.py")])
p = RF / "funcs_24.c"
s = p.read_text()
if "s4279-wipe" not in s:
    fn = r'''#include <pthread.h>
#include <unistd.h>
static uint8_t* s4279_rd = 0;
static void* s4279_poll(void* a) { uint8_t* rdram = s4279_rd; int armed = 0; (void)a;
    for (;;) { uint32_t w = (uint32_t)MEM_W(0, S32(0x801F9CE0u));
        if (!armed) { if (w) { armed = 1; fprintf(stderr, "[s4279-wipe] poller armed (node0.next=%08X)\n", w); } }
        else if (w == 0) { uint32_t pcs[16]; for (int k = 0; k < 16; k++) pcs[k] = (uint32_t)g_rs64_last_guest_pc;
            fprintf(stderr, "[s4279-wipe] node0.next became 0; last_guest_pc samples:"); for (int k = 0; k < 16; k++) fprintf(stderr, " %08X", pcs[k]);
            fprintf(stderr, " | node1.next=%08X node2.next=%08X b3e0=%08X\n", (uint32_t)MEM_W(0, S32(0x801F9CF8u)), (uint32_t)MEM_W(0, S32(0x801F9D10u)), (uint32_t)MEM_W(0, S32(0x801FB3E0u)));
            fflush(stderr); return 0; }
        usleep(5); } }
'''
    a = '#include "funcs.h"\n'
    s = s.replace(a, a + fn, 1)
    hook = "static uint32_t sh[1536]; static int dumped = 0, have = 0;"
    assert s.count(hook) == 1
    s = s.replace(hook, hook + " static int polling = 0; if (!polling) { polling = 1; s4279_rd = rdram; pthread_t th; pthread_create(&th, 0, s4279_poll, 0); pthread_detach(th); }", 1)
    p.write_text(s)
s = p.read_text()   # v2: watch the heap-block header word 0x801F9CD4 (0x1800 while allocated); node0.next is legitimately 0 when node0 is the tail
s = s.replace("uint32_t w = (uint32_t)MEM_W(0, S32(0x801F9CE0u));", "uint32_t w = (uint32_t)MEM_W(0, S32(0x801F9CD4u));").replace("node0.next=%08X", "hdr9CD4=%08X").replace("node0.next became 0", "hdr9CD4 became 0")
p.write_text(s)
print("ok")
