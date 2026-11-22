#!/usr/bin/env python3
"""s7808: runtime qualification of the gcc-built findAndUnlinkSmallestEntry patch body.

s7807 found the patch is never called in play (lvl1 dd3, L4/L1 dd4), so the gcc-compiled
body (patches/dl_finder.c -> patches.elf -> N64Recomp -> RecompiledPatches/patches.c
rs64_find_body) was static-verified only. This harness executes that recompiled body on a
synthetic RDRAM, differentially against two independent references:
  REF    a native C model of the retail loop (largest non-empty size, ties -> later node,
         unlink, push on the used list at 0x80128EF8, return payload +0x14)
  RETAIL the recompiled retail function findAndUnlinkSmallestEntry_s6088_inner
         (0x8002221C, ../N64Recomp/RecompiledFuncs/funcs_6.c), i.e. ROGUESQ_FIND_OFF=1
Each trial builds random bucket lists (sizes incl. 0 and ties, random used list), then calls
every implementation repeatedly until it returns 0, comparing r2 and the whole pool region
after every call. Controls: a MUTANT reference (ties -> earlier node) must disagree, and a
planted single-byte pool corruption must be detected by the comparator.

  python3 tools/s7808_find_body_diff.py [--trials N]     rc 0 = H-equal + controls PASS
"""
import argparse, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATCHES = os.path.join(ROOT, "RecompiledPatches", "patches.c")
FUNCS6 = os.path.join(ROOT, "..", "N64Recomp", "RecompiledFuncs", "funcs_6.c")
INC = [os.path.join(ROOT, p) for p in ("include", "RecompiledPatches", "lib/N64ModernRuntime/N64Recomp/include",
                                       "lib/N64ModernRuntime/librecomp/include",
                                       "lib/N64ModernRuntime/ultramodern/include")]


def extract(path, head):
    lines = open(path).read().split("\n")
    s = next(i for i, l in enumerate(lines) if l.startswith(head))
    e = next(i for i in range(s + 1, len(lines)) if lines[i] in ("}", ";}"))
    first_fn = next(i for i, l in enumerate(lines) if l.startswith("RECOMP_FUNC") or l.startswith("static void"))
    return "\n".join(lines[:first_fn]), "\n".join(lines[s:e + 1])


HARNESS = r"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef struct { uint64_t r[32]; } dummy_t;
extern void patch_body(uint8_t* rdram, recomp_context* ctx);
extern void retail_body(uint8_t* rdram, recomp_context* ctx);
#define RD 0x01000000u
#define A(x) ((x) - 0x80000000u)
static uint32_t rw(uint8_t* m, uint32_t a) { return *(uint32_t*)(m + A(a)); }
static void ww(uint8_t* m, uint32_t a, uint32_t v) { *(uint32_t*)(m + A(a)) = v; }
static uint16_t rh(uint8_t* m, uint32_t a) { return *(uint16_t*)(m + (A(a) ^ 2)); }
static void wh(uint8_t* m, uint32_t a, uint16_t v) { *(uint16_t*)(m + (A(a) ^ 2)) = v; }
#define CNT 0x80128EF0u
#define USED 0x80128EF8u
#define BK 0x80128F00u
#define ARR 0x80200000u
#define POOL 0x80300000u
static uint64_t st = 88172645463325252ull;
static uint32_t rnd(void) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (uint32_t)st; }
static uint32_t ref(uint8_t* m, int mutant) {
    uint32_t cnt = rh(m, CNT), bk = rw(m, BK), best = 0;
    for (uint32_t i = 0; i < cnt; i++)
        for (uint32_t n = rw(m, bk + 4 * i); n; n = rw(m, n)) {
            uint16_t sz = rh(m, n + 8); if (!sz) continue;
            if (!best) best = n;
            else if (mutant ? (sz > rh(m, best + 8)) : !(sz < rh(m, best + 8))) best = n;
        }
    if (!best) return 0;
    uint32_t next = rw(m, best), prev = rw(m, best + 4);
    if (prev) ww(m, prev, next); else ww(m, bk + 4 * rh(m, best + 10), next);
    if (next) ww(m, next + 4, prev);
    uint32_t head = rw(m, USED);
    ww(m, best + 4, 0); ww(m, best, head); if (head) ww(m, head + 4, best);
    ww(m, USED, best);
    return rw(m, best + 0x14);
}
static void build(uint8_t* m, int trial) {
    memset(m + A(CNT), 0, 0x20); memset(m + A(ARR), 0, 0x100); memset(m + A(POOL), 0, 0x8000);
    uint32_t cnt = (trial % 17 == 0) ? 0 : 1 + rnd() % 12, e = POOL;
    wh(m, CNT, (uint16_t)cnt); ww(m, BK, ARR);
    for (uint32_t i = 0; i < cnt; i++) {
        uint32_t len = rnd() % 6, prev = 0;
        for (uint32_t k = 0; k < len; k++, e += 0x20) {
            uint32_t r = rnd() % 10;
            uint16_t sz = r < 2 ? 0 : (r < 5 ? (uint16_t)(0x100 * (1 + rnd() % 3)) : (uint16_t)(1 + rnd() % 0x400));
            ww(m, e + 4, prev); wh(m, e + 8, sz); wh(m, e + 10, (uint16_t)i); ww(m, e + 0x14, 0x80400000u + (e - POOL));
            ww(m, e + 0xC, rnd()); ww(m, e + 0x10, rnd());
            if (prev) ww(m, prev, e); else ww(m, ARR + 4 * i, e);
            prev = e;
        }
    }
    uint32_t used = 0, ul = rnd() % 4;
    for (uint32_t k = 0; k < ul; k++, e += 0x20) { ww(m, e, used); ww(m, e + 4, 0); wh(m, e + 8, 0x77); if (used) ww(m, used + 4, e); used = e; }
    ww(m, USED, used);
}
static int same(uint8_t* a, uint8_t* b) {
    return !memcmp(a + A(CNT), b + A(CNT), 0x20) && !memcmp(a + A(ARR), b + A(ARR), 0x100) && !memcmp(a + A(POOL), b + A(POOL), 0x8000);
}
static void call(void (*f)(uint8_t*, recomp_context*), uint8_t* m, uint32_t* r2) {
    recomp_context c; memset(&c, 0, sizeof c);
    c.r29 = (gpr)(int32_t)0x80700000; c.r31 = (gpr)(int32_t)0x80022000;
    for (int i = 1; i < 32; i++) if (i != 29 && i != 31) (&c.r0)[i] = (gpr)(int32_t)(0xDEAD0000u | i);
    f(m, &c); *r2 = (uint32_t)c.r2;
}
int main(int argc, char** argv) {
    int trials = argc > 1 ? atoi(argv[1]) : 20000;
    uint8_t *mp = calloc(1, RD), *mr = calloc(1, RD), *mf = calloc(1, RD), *mm = calloc(1, RD);
    long calls = 0, nonnull = 0, ties = 0, prevnz = 0, empty = 0, bad_patch = 0, bad_retail = 0, mut_diff = 0, plant_det = 0, plants = 0;
    for (int t = 0; t < trials; t++) {
        build(mp, t); memcpy(mr + A(CNT), mp + A(CNT), 0x20); memcpy(mr + A(ARR), mp + A(ARR), 0x100); memcpy(mr + A(POOL), mp + A(POOL), 0x8000);
        memcpy(mf + A(CNT), mp + A(CNT), 0x20); memcpy(mf + A(ARR), mp + A(ARR), 0x100); memcpy(mf + A(POOL), mp + A(POOL), 0x8000);
        memcpy(mm + A(CNT), mp + A(CNT), 0x20); memcpy(mm + A(ARR), mp + A(ARR), 0x100); memcpy(mm + A(POOL), mp + A(POOL), 0x8000);
        int mutdone = 0;
        for (int k = 0; k < 64; k++) {
            /* coverage: does the ref's pick have a tie / a non-null prev? */
            { uint32_t cnt = rh(mr, CNT), bk = rw(mr, BK), best = 0; int tie = 0;
              for (uint32_t i = 0; i < cnt; i++) for (uint32_t n = rw(mr, bk + 4 * i); n; n = rw(mr, n)) { uint16_t sz = rh(mr, n + 8); if (!sz) continue; if (best && sz == rh(mr, best + 8)) tie = 1; if (!best || !(sz < rh(mr, best + 8))) best = n; }
              if (best) { ties += tie; prevnz += rw(mr, best + 4) != 0; } }
            uint32_t rp, rr, rf, rm;
            call(patch_body, mp, &rp); call(retail_body, mf, &rf);
            rr = ref(mr, 0); calls++;
            if (!mutdone) { rm = ref(mm, 1); if (rm != rr || !same(mm, mr)) { mut_diff++; mutdone = 1; } }
            if (rp != rr || !same(mp, mr)) { if (bad_patch++ < 5) fprintf(stderr, "PATCH MISMATCH trial=%d call=%d r2=%08X ref=%08X\n", t, k, rp, rr); break; }
            if (rf != rr || !same(mf, mr)) { if (bad_retail++ < 5) fprintf(stderr, "RETAIL MISMATCH trial=%d call=%d r2=%08X ref=%08X\n", t, k, rf, rr); break; }
            if (!rr) { empty++; break; }
            nonnull++;
        }
        if (t % 97 == 0) { /* planted corruption: comparator must see one flipped pool byte */
            plants++; uint32_t off = A(POOL) + rnd() % 0x8000; mp[off] ^= 0x40; if (!same(mp, mr)) plant_det++; mp[off] ^= 0x40; }
    }
    printf("trials=%d calls=%ld nonnull=%ld empty_returns=%ld tie_picks=%ld prev_nonnull_picks=%ld\n", trials, calls, nonnull, empty, ties, prevnz);
    printf("patch_mismatch=%ld retail_mismatch=%ld\n", bad_patch, bad_retail);
    printf("CONTROL mutant_trials_differ=%ld/%d plant_detected=%ld/%ld\n", mut_diff, trials, plant_det, plants);
    int ctl = mut_diff > trials / 10 && plant_det == plants && plants > 0 && ties > 0 && prevnz > 0 && empty > 0;
    int ok = bad_patch == 0 && bad_retail == 0;
    printf("CONTROLS %s\nVERDICT %s\n", ctl ? "PASS" : "FAIL", !ctl ? "HOLLOW" : (ok ? "H-equal" : "H-differ"));
    return !ctl ? 3 : (ok ? 0 : 1);
}
"""

STUBS = r"""
#include <stdint.h>
unsigned char* g_rs64_s7475_bm; int g_rs64_s7484_on; int g_rs64_s7488_on; unsigned int g_rs64_s7488_cnt[4096];
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=20000)
    ap.add_argument("--keep", default="")
    ap.add_argument("--plant", action="store_true", help="internal: mutate the patch body (sltu -> <=)")
    ap.add_argument("--controls", action="store_true", help="also run the planted-mutant patch body; it must read H-differ")
    a = ap.parse_args()
    ppre, pbody = extract(PATCHES, "static void rs64_find_body(uint8_t* rdram, recomp_context* ctx) {")
    rpre, rbody = extract(FUNCS6, "RECOMP_FUNC void findAndUnlinkSmallestEntry_s6088_inner(uint8_t* rdram, recomp_context* ctx) {")
    if "0x80801174" not in pbody or "0x8002221C" not in rbody:
        print("EXTRACT FAIL (addresses moved)"); return 2
    pbody = pbody.replace("static void rs64_find_body(", "void patch_body(", 1)
    if a.plant:  # flip the size comparison: ties keep the earlier node -> must be caught
        n0 = pbody.count("ctx->r3 = ctx->r3 < ctx->r5 ? 1 : 0;")
        if n0 == 0:
            print("PLANT SITE MISSING"); return 2
        pbody = pbody.replace("ctx->r3 = ctx->r3 < ctx->r5 ? 1 : 0;", "ctx->r3 = ctx->r3 <= ctx->r5 ? 1 : 0;")
    rbody = rbody.replace("RECOMP_FUNC void findAndUnlinkSmallestEntry_s6088_inner(", "void retail_body(", 1)
    d = a.keep or tempfile.mkdtemp(prefix="s7808_")
    os.makedirs(d, exist_ok=True)
    srcs = {"p.c": ppre + "\n" + pbody + "\n", "r.c": rpre + "\n" + rbody + "\n",
            "h.c": '#include "recomp.h"\n' + HARNESS}
    for n, s in srcs.items():
        open(os.path.join(d, n), "w").write(s)
    inc = sum((["-I", p] for p in INC), [])
    exe = os.path.join(d, "s7808")
    # unresolved hook functions (all gated off by the zeroed globals) -> weak no-op stubs
    objs = []
    for n in srcs:
        o = os.path.join(d, n[:-2] + ".o")
        r = subprocess.run(["cc", "-O1", "-w", "-std=gnu11", "-Wno-error=implicit-function-declaration", "-c", os.path.join(d, n), "-o", o] + inc, capture_output=True, text=True)
        if r.returncode:
            print(r.stderr[-3000:]); return 2
        objs.append(o)
    nm = subprocess.run(["nm", "-u"] + objs, capture_output=True, text=True).stdout
    undef = sorted({l.split()[-1].lstrip("_") for l in nm.split("\n") if l.strip() and not l.endswith(":")})
    known = {"memcmp", "memcpy", "memset", "calloc", "printf", "fprintf", "atoi", "getenv", "puts", "putchar",
             "stderrp", "fwrite", "fputc", "patch_body", "retail_body", "bzero"}
    stub = STUBS
    defined_globals = {"g_rs64_s7475_bm", "g_rs64_s7484_on", "g_rs64_s7488_on", "g_rs64_s7488_cnt"}
    for u in undef:
        if u in known or u in defined_globals:
            continue
        # data hooks (g_*) must read as zero = every diagnostic gate off; functions are no-ops
        stub += (f"long long {u}[512];\n" if u.startswith("g_") else f"int {u}() {{ return 0; }}\n")
    open(os.path.join(d, "s.c"), "w").write(stub)
    r = subprocess.run(["cc", "-O1", "-w", "-std=gnu89", os.path.join(d, "s.c"), "-o", exe] + objs, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-3000:]); return 2
    print(f"stubbed={len([u for u in undef if u not in known and u not in defined_globals])} dir={d}")
    r = subprocess.run([exe, str(a.trials)], capture_output=True, text=True)
    sys.stdout.write(r.stdout); sys.stderr.write(r.stderr[:600])
    if a.controls and not a.plant:
        c = subprocess.run([sys.executable, os.path.abspath(__file__), "--plant", "--trials", str(min(a.trials, 3000))],
                           capture_output=True, text=True)
        ok = c.returncode == 1 and "VERDICT H-differ" in c.stdout
        print(f"PLANTED-PATCH CONTROL {'PASS' if ok else 'FAIL'} (rc={c.returncode})")
        if not ok:
            return 3
    return r.returncode


if __name__ == "__main__":
    _rc = main()
    for _d in __import__("glob").glob(os.path.join(tempfile.gettempdir(), "s7808_*")):
        __import__("shutil").rmtree(_d, ignore_errors=True)
    sys.exit(_rc)
