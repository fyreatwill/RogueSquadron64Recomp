// s7361 class AL two-arm control. Real recomp.h MEM_x macros over a librecomp-shaped rdram: 4 GB PROT_NONE
// reservation with the first 8 MB RW (as recomp.cpp). Each idiom runs pre (s7361-removed text) and post (fixed text)
// in a forked child: post must read the planted guest word, pre must fault (zero-extended -> rdram + 4 GB).
#include <cstdint>
#include <cstdio>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
#include "recomp.h"
static uint8_t* rdram;
typedef int (*fn)();
static int run(fn f) { pid_t p = fork(); if (p == 0) { _exit(f() == 1 ? 0 : 3); } int st; waitpid(p, &st, 0);
    return WIFSIGNALED(st) ? -WTERMSIG(st) : WEXITSTATUS(st); }
#define PLANT(a, v) (*(int32_t*)(rdram + ((a) - 0x80000000u)) = (v))
// idiom 1: s6126 osSendMesg [pi-slot-send] uint32_t m
static int i1_pre()  { uint32_t m = 0x801107E0u; return MEM_W(8, m) == 0x1234; }
static int i1_post() { uint32_t m = 0x801107E0u; return MEM_W(8, (int32_t)m) == 0x1234; }
// idiom 2: s3308 stage_adv int32 + unsigned offset
static int i2_pre()  { return MEM_W(0x934u, S32(0x800B0000u)) == 0x5678; }
static int i2_post() { return MEM_W(0x934, S32(0x800B0000u)) == 0x5678; }
// idiom 3: s6311 unsigned literal base
static int i3_pre()  { int q = 1; return MEM_W(q * 4, 0x80138D20u) == 0x9ABC; }
static int i3_post() { int q = 1; return MEM_W(q * 4, (int32_t)0x80138D20u) == 0x9ABC; }
// idiom 4: s6480 signed base + unsigned index
static int i4_pre()  { int32_t pb = (int32_t)0x80200000u; uint32_t i = 1; return MEM_W(pb, 12*i) == 0x7777; }
static int i4_post() { int32_t pb = (int32_t)0x80200000u; uint32_t i = 1; return MEM_W(pb, (int32_t)(12*i)) == 0x7777; }
int main() {
    rdram = (uint8_t*)mmap(nullptr, 4096ull << 20, PROT_NONE, MAP_ANON | MAP_PRIVATE, -1, 0);
    if (rdram == MAP_FAILED || mprotect(rdram, 8u << 20, PROT_READ | PROT_WRITE)) { puts("mmap failed"); return 2; }
    PLANT(0x801107E8u, 0x1234); PLANT(0x800B0934u, 0x5678); PLANT(0x80138D24u, 0x9ABC); PLANT(0x8020000Cu, 0x7777);
    fn pre[] = {i1_pre, i2_pre, i3_pre, i4_pre}, post[] = {i1_post, i2_post, i3_post, i4_post};
    int ok = 0;
    for (int k = 0; k < 4; k++) {
        int a = run(pre[k]), b = run(post[k]);
        bool pass = a < 0 && b == 0;   // pre killed by a signal, post read the planted word
        printf("idiom %d: pre=%s post=%s -> %s\n", k + 1, a < 0 ? "fault" : (a == 0 ? "READ-OK" : "wrong"), b == 0 ? "read-ok" : "FAIL",
               pass ? "PASS" : "FAIL");
        ok += pass;
    }
    printf("s7361 ctl %d/4\n", ok);
    return ok == 4 ? 0 : 1;
}
