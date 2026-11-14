// s7362 class AM two-arm control. librecomp-shaped rdram (4 GB PROT_NONE, first 8 MB RW) with a sentinel page mapped
// 2 GB BELOW rdram (stand-in for host memory). Each arm runs the s6094/s6088 bucketlog `rd` lambda in a forked child:
// pre (rdram + (int64_t)(int32_t)g) must read the sentinel = host memory, post (rdram + (g - 0x80000000u)) the guest word.
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
#include <cstdint>
#include <cstdio>
static uint8_t* rdram;
static uint32_t rd_pre(uint32_t g) { if (g < 0x80000000u || g >= 0x90000000u || (g & 3u)) return 0u; const uint8_t* q = rdram + (int64_t)(int32_t)g; return ((uint32_t)q[0 ^ 3] << 24) | ((uint32_t)q[1 ^ 3] << 16) | ((uint32_t)q[0x2 ^ 3] << 8) | (uint32_t)q[3 ^ 3]; }
static uint32_t rd_post(uint32_t g) { if (g < 0x80000000u || g >= 0x90000000u || (g & 3u)) return 0u; const uint8_t* q = rdram + (g - 0x80000000u); return ((uint32_t)q[0 ^ 3] << 24) | ((uint32_t)q[1 ^ 3] << 16) | ((uint32_t)q[0x2 ^ 3] << 8) | (uint32_t)q[3 ^ 3]; }
static int arm(const char* name, uint32_t (*f)(uint32_t), uint32_t g, uint32_t want_guest, uint32_t host_sentinel, bool want_host) {
    pid_t p = fork();
    if (p == 0) { uint32_t v = f(g); _exit(v == want_guest ? 10 : v == host_sentinel ? 20 : 30); }
    int st = 0; waitpid(p, &st, 0);
    const char* what = WIFSIGNALED(st) ? "FAULT" : WEXITSTATUS(st) == 10 ? "GUEST" : WEXITSTATUS(st) == 20 ? "HOST" : "OTHER";
    bool ok = want_host ? (!WIFSIGNALED(st) && WEXITSTATUS(st) == 20) : want_guest ? (!WIFSIGNALED(st) && WEXITSTATUS(st) == 10) : (WIFSIGNALED(st) || WEXITSTATUS(st) != 20);
    printf("%s %-4s g=0x%08X -> %s\n", ok ? "PASS" : "FAIL", name, g, what);
    return ok ? 0 : 1;
}
int main() {
    const size_t G = 1ull << 30;
    // reserve 6 GB, put rdram at +2 GB so rdram - 2 GB is a mappable host page
    uint8_t* base = (uint8_t*)mmap(nullptr, 6 * G, PROT_NONE, MAP_ANON | MAP_PRIVATE, -1, 0);
    if (base == MAP_FAILED) { puts("mmap failed"); return 2; }
    rdram = base + 2 * G;
    if (mprotect(rdram, 8u << 20, PROT_READ | PROT_WRITE) || mprotect(base, 8u << 20, PROT_READ | PROT_WRITE)) { puts("mprotect failed"); return 2; }
    const uint32_t g = 0x80123450u, phys = g - 0x80000000u, guest = 0x8BADF00Du, host = 0x0057AC4Bu;
    for (int k = 0; k < 4; k++) { rdram[(phys + k) ^ 3] = (uint8_t)(guest >> (24 - 8 * k)); base[(phys + k) ^ 3] = (uint8_t)(host >> (24 - 8 * k)); }
    int bad = 0;
    bad += arm("pre", rd_pre, g, guest, host, true);
    bad += arm("post", rd_post, g, guest, host, false);
    bad += arm("post", rd_post, 0x8FFFFFFCu, 0, host, false);   // top of the accepted range (phys 256 MB, RW in librecomp, PROT_NONE here): contained = never the host sentinel
    printf("s7362 ctl %s\n", bad ? "FAIL" : "PASS");
    return bad;
}
