#!/usr/bin/env python3
"""s7810: class closure for HOST (C/C++) definitions that replace a recompiled game function.

Sibling of s7809 (gcc C-patch bodies). RECOMP_FUNC is weak on clang, so a strong host definition with the
same name as a generated RECOMP_FUNC silently replaces the recompiled retail body. This tool:

  (1) CENSUS: every `void NAME(uint8_t* rdram, recomp_context* ctx) {` DEFINITION under src/ and
      lib/N64ModernRuntime/{librecomp,ultramodern}/src, intersected with every RECOMP_FUNC name in
      ../N64Recomp/RecompiledFuncs. Each member needs a ROWS entry; an unrowed member reads RED.
  (2) DIFFERENTIAL (class a): the host body (extracted verbatim from its source file, compiled as C++ with
      its diagnostic hooks stubbed) vs the recompiled retail body (compiled as C), on identical random guest
      state. Compared after every call: callee-saved regs (s0-s8, gp, sp, ra) and RDRAM (the dst/src windows
      +-64 B every call, the whole 8 MB every 64 trials). r2 is NOT in the contract (void function); instead
      every generated call site is scanned for a read of r2 after the call before a write (must be 0).
      Input classes: len 0, 1..15, >=16 with same 16-alignment (retail's 16-byte block path), mixed alignment,
      overlap forward/backward (incl. multiples of 16 so the block path runs on overlap), sign-extended and
      zero-extended KSEG0 pointers, host diag path on/off (s7490 hook path with marked bytes).
      Out-of-RAM inputs (KSEG1, >8 MB, len past the end) are a DOCUMENTED delta, not compared: the host skips
      and logs, retail would write outside the 8 MB guest RAM; each is checked to take the skip path.
  Controls: planted host mutant (len off by one) must read H-differ; a planted 1-byte RAM corruption must be
  seen by the comparator; a planted unrowed host override must read RED in the census; every coverage
  counter > 0.

  python3 tools/s7810_host_override_diff.py [--trials N] [--controls]     rc 0 = GREEN
"""
import argparse, os, re, shutil, subprocess, sys, tempfile, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RF = os.path.join(ROOT, "..", "N64Recomp", "RecompiledFuncs")
HOST_DIRS = [os.path.join(ROOT, "src"), os.path.join(ROOT, "lib/N64ModernRuntime/librecomp/src"),
             os.path.join(ROOT, "lib/N64ModernRuntime/ultramodern/src")]
INC = [RF] + [os.path.join(ROOT, p) for p in ("include", "lib/N64ModernRuntime/N64Recomp/include",
                                       "lib/N64ModernRuntime/librecomp/include",
                                       "lib/N64ModernRuntime/ultramodern/include")]
DEF_RE = re.compile(r'^(?:extern "C" )?(?:static )?void (\w+)\(uint8_t\* ?rdram, recomp_context\* ?ctx\) ?\{', re.M)
ROWS = {"zmemcpy": dict(cls="a", host="src/main/upstream_compat.cpp", retail_addr="0x80018EF4")}


def census(extra_src=None):
    host = {}
    for d in HOST_DIRS:
        for p in glob.glob(os.path.join(d, "**", "*.c*"), recursive=True):
            if not p.endswith((".c", ".cpp", ".cc")):
                continue
            for m in DEF_RE.finditer(open(p, errors="replace").read()):
                if not m.group(0).startswith("static"):
                    host.setdefault(m.group(1), []).append(os.path.relpath(p, ROOT))
    if extra_src:
        for m in DEF_RE.finditer(extra_src):
            host.setdefault(m.group(1), []).append("<planted>")
    rec = {}
    for p in glob.glob(os.path.join(RF, "*.c")):
        for m in re.finditer(r"^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC void (\w+)\(", open(p).read(), re.M):
            rec[m.group(1)] = os.path.basename(p)
    both = sorted(set(host) & set(rec))
    red = [f"{n}: host override of RECOMP_FUNC ({','.join(host[n])}) has no class row" for n in both if n not in ROWS]
    return both, host, rec, red


def extract(text, head_re):
    m = re.search(head_re, text, re.M)
    if not m:
        return None
    e = re.compile(r"^;?\}$", re.M).search(text, m.end())
    return text[m.start():e.end()] if e else None


def r2_readers(rec_files):
    """Generated call sites of zmemcpy that read r2 after the call before writing it (contract: must be 0)."""
    sites = reads = 0
    bad = []
    for f in rec_files:
        L = open(f).read().split("\n")
        for i, l in enumerate(L):
            if "zmemcpy(rdram, ctx);" not in l or l.lstrip().startswith("RECOMP_FUNC"):
                continue
            sites += 1
            for j in range(i + 1, min(i + 400, len(L))):
                t = re.sub(r"//.*", "", L[j])
                if re.match(r"^\s*(L_\w+:|RECOMP_FUNC|;?\}$)", t) or "(rdram, ctx);" in t or re.search(r"\b(return;|goto )", t):
                    break  # label (join point), next call, function end: conservative stop
                hit = None
                for m in re.finditer(r"ctx->r2\b(\s*=(?!=))?", t):
                    if m.group(1):
                        rhs = t[m.end():].split(";", 1)[0]
                        hit = "read" if re.search(r"ctx->r2\b", rhs) else "write"
                    else:
                        hit = "read"
                    break
                if hit == "read":
                    reads += 1; bad.append(f"{os.path.basename(f)}:{j+1}: {L[j].strip()[:140]}"); break
                if hit == "write":
                    break
    return sites, reads, bad


PRELUDE = r"""
#include "recomp.h"
#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cstring>
extern "C" { uint32_t rs64_ram_top = 0x80800000u; unsigned char* g_rs64_s7475_bm = nullptr; int g_rs64_s7484_on = 0;
             volatile uint32_t g_rs64_last_guest_pc = 0; long HOOKS = 0, MARKHITS = 0; }
static uint64_t s_s7490_rmark = 0, s_s7490_wmark = 0;
static bool s7490_zhook() { return true; }
static inline bool s7490_marked(uint32_t a) { const uint32_t o = a - 0x80000000u; return o < 0x800000u && ((g_rs64_s7475_bm[o >> 3] >> (o & 7u)) & 1u); }
static void s7490_pre(uint32_t, uint32_t) { HOOKS++; }
extern "C" int rs64_s7484_load(uint32_t, uint32_t, int, const char*) { MARKHITS++; return 0; }
extern "C" int rs64_s7475_store(uint32_t, uint32_t, int, const char*) { MARKHITS++; return 0; }
extern "C" void rs64_f5_host_write_begin(const uint8_t*, uint32_t, uint32_t, const char*) {}
extern "C" void rs64_m5_host_write_census(uint8_t*, uint32_t, uint32_t, const char*) {}
extern "C" void rs64_g1d_blk_dma(const char*, uint32_t, uint32_t, uint32_t, uint32_t) {}
#define zmemcpy host_fn
"""

HARNESS = r"""
#include "recomp.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <signal.h>
#include <setjmp.h>
static sigjmp_buf JB; static void onseg(int sig) { (void)sig; siglongjmp(JB, 1); }
void host_fn(uint8_t* rdram, recomp_context* ctx);
void retail_fn(uint8_t* rdram, recomp_context* ctx);
extern unsigned char* g_rs64_s7475_bm; extern int g_rs64_s7484_on; extern long HOOKS, MARKHITS;
#define RD 0x00800000u
static uint64_t st = 0x9E3779B97F4A7C15ull;
static uint32_t rnd(void) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (uint32_t)st; }
static void mkctx(recomp_context* c, uint64_t salt) {
    memset(c, 0, sizeof *c); uint64_t s = salt;
    for (int i = 1; i < 32; i++) { s = s * 6364136223846793005ull + 1442695040888963407ull; (&c->r0)[i] = s; }
    c->r29 = (gpr)(int32_t)0x80700000; c->r31 = (gpr)(int32_t)0x80022000;
}
static int regs_ok(recomp_context* p, recomp_context* r) {
    for (int i = 16; i <= 23; i++) if ((&p->r0)[i] != (&r->r0)[i]) return 0;
    for (int i = 28; i <= 31; i++) if ((&p->r0)[i] != (&r->r0)[i]) return 0;
    return 1;
}
static int win_same(uint8_t* a, uint8_t* b, uint32_t lo, uint32_t n) {
    uint32_t s = lo >= 64 ? lo - 64 : 0, e = lo + n + 64 > RD ? RD : lo + n + 64; return !memcmp(a + s, b + s, e - s);
}
int main(int argc, char** argv) {
    int trials = argc > 1 ? atoi(argv[1]) : 20000; setvbuf(stdout, NULL, _IONBF, 0);
    uint8_t *mh = (uint8_t*)malloc(RD), *mr = (uint8_t*)malloc(RD), *bm = (uint8_t*)calloc(1, RD / 8);
    for (uint32_t i = 0; i < RD; i++) mh[i] = mr[i] = (uint8_t)(i * 2654435761u >> 13);
    for (uint32_t i = 0; i < RD / 8; i += 1 + rnd() % 64) bm[i] = (uint8_t)rnd();
    long bad = 0, plants = 0, plant_det = 0, fulls = 0, r2diff = 0, oob = 0, oob_ok = 0;
    enum { LEN0, SHORT, BLOCK, MIXED, OVL_F, OVL_B, OVL16, ZEXT, DIAG, NC };
    const char* cn[NC] = {"len0", "len1_15", "block16_aligned", "len16_mixed_align", "overlap_fwd", "overlap_bwd", "overlap_block16", "zero_ext_ptr", "diag_marked_path"};
    long cov[NC] = {0};
    for (int t = 0; t < trials && bad == 0; t++) {
        uint32_t k = rnd() % 10, len, d, s;
        switch (k) {
        case 0: len = 0; break;
        case 1: case 2: len = 1 + rnd() % 15; break;
        case 3: case 4: len = 16 + rnd() % 300; break;
        default: len = (rnd() % 4 == 0) ? 1 + rnd() % 0x8000 : rnd() % 600; break;
        }
        s = 0x100 + rnd() % (RD - 0x10000);
        if (k == 3 || (k == 9 && rnd() % 2)) d = (0x100 + rnd() % (RD - 0x10000)) & ~0xFu, d |= s & 0xF;  /* same 16-alignment */
        else if (k == 5) d = s + 1 + rnd() % (len + 1 ? len + 1 : 1);                                         /* forward overlap */
        else if (k == 6) { if (s < len + 0x200) s += len + 0x200; } if (k == 6) d = s - 1 - rnd() % (len + 1 ? len + 1 : 1);                                         /* backward overlap */
        else if (k == 7) d = s + 16 * (1 + rnd() % 4), len = len < 16 ? len + 48 : len;                       /* overlap, block path */
        else d = 0x100 + rnd() % (RD - 0x10000);
        if (d + len >= RD - 64) d = RD - 64 - len - 1;
        int zext = rnd() % 5 == 0, diag = rnd() % 3 == 0;
        if (len == 0) cov[LEN0]++; else if (len < 16) cov[SHORT]++;
        else if (((d ^ s) & 0xF) == 0) cov[BLOCK]++; else cov[MIXED]++;
        if (len && d > s && d < s + len) cov[OVL_F]++;
        if (len && d < s && d + len > s) cov[OVL_B]++;
        if (len >= 16 && d != s && ((d ^ s) & 0xF) == 0 && (d > s ? d < s + len : s < d + len)) cov[OVL16]++;
        if (zext) cov[ZEXT]++;
        g_rs64_s7475_bm = diag ? bm : NULL; g_rs64_s7484_on = diag; long mh0 = MARKHITS;
        uint64_t salt = ((uint64_t)rnd() << 32) | rnd();
        recomp_context ch, cr; mkctx(&ch, salt); mkctx(&cr, salt);
        uint64_t D = zext ? (uint64_t)(0x80000000u + d) : (uint64_t)(int64_t)(int32_t)(0x80000000u + d);
        uint64_t S = zext ? (uint64_t)(0x80000000u + s) : (uint64_t)(int64_t)(int32_t)(0x80000000u + s);
        ch.r4 = cr.r4 = D; ch.r5 = cr.r5 = S; ch.r6 = cr.r6 = len;
        signal(SIGSEGV, onseg); signal(SIGBUS, onseg);
        if (sigsetjmp(JB, 1)) { bad++; printf("MISMATCH host FAULT trial=%d k=%u d=%X s=%X len=%u zext=%d diag=%d\n", t, k, d, s, len, zext, diag); break; }
        host_fn(mh, &ch); retail_fn(mr, &cr);
        if (diag && MARKHITS > mh0) cov[DIAG]++;
        if (ch.r2 != cr.r2) r2diff++;
        int full = (t % 64 == 63) || t == trials - 1; if (full) fulls++;
        if (!regs_ok(&ch, &cr) || !win_same(mh, mr, d, len) || !win_same(mh, mr, s, len) || (full && memcmp(mh, mr, RD))) {
            bad++; printf("MISMATCH trial=%d k=%u d=%X s=%X len=%u zext=%d diag=%d\n", t, k, d, s, len, zext, diag);
        }
        if (t % 97 == 0) { plants++; uint32_t off = rnd() % RD; mh[off] ^= 0x10; if (memcmp(mh, mr, RD)) plant_det++; mh[off] ^= 0x10; }
    }
    /* documented delta: out-of-RAM inputs must take the host skip path (RAM untouched) */
    g_rs64_s7475_bm = NULL; g_rs64_s7484_on = 0;
    { uint8_t* snap = (uint8_t*)malloc(RD); memcpy(snap, mh, RD);
      const uint64_t cases[][3] = { {(uint64_t)(int64_t)(int32_t)0xA0001000u, (uint64_t)(int64_t)(int32_t)0x80001000u, 32},
                                    {(uint64_t)(int64_t)(int32_t)0x80001000u, (uint64_t)(int64_t)(int32_t)0xA0400000u, 32},
                                    {(uint64_t)(int64_t)(int32_t)0x807FFFF0u, (uint64_t)(int64_t)(int32_t)0x80001000u, 32},
                                    {(uint64_t)(int64_t)(int32_t)0x80900000u, (uint64_t)(int64_t)(int32_t)0x80001000u, 4},
                                    {0x0000000180001000ull, (uint64_t)(int64_t)(int32_t)0x80001000u, 4} };
      for (unsigned i = 0; i < sizeof cases / sizeof cases[0]; i++) { recomp_context c; mkctx(&c, i); c.r4 = cases[i][0]; c.r5 = cases[i][1]; c.r6 = cases[i][2];
          host_fn(mh, &c); oob++; if (!memcmp(snap, mh, RD) && c.r2 == c.r4) oob_ok++; }
      free(snap); }
    int covok = 1; printf("trials=%d full_compares=%ld", trials, fulls);
    for (int i = 0; i < NC; i++) { printf(" %s=%ld", cn[i], cov[i]); if (!cov[i]) covok = 0; }
    printf("\nmismatch=%ld r2_differs(void, not contract)=%ld hooks=%ld CONTROL plant_detected=%ld/%ld oob_skip=%ld/%ld\n",
           bad, r2diff, HOOKS, plant_det, plants, oob_ok, oob);
    int ctl = covok && plants > 0 && plant_det == plants && oob_ok == oob;
    printf("CONTROLS %s\nVERDICT %s\n", ctl ? "PASS" : "FAIL", bad ? "H-differ" : (!ctl ? "HOLLOW" : "H-equal"));
    return bad ? 1 : (!ctl ? 3 : 0);
}
"""
PLANT = ("uint32_t len = (uint32_t)len_full;", "uint32_t len = (uint32_t)len_full + (len_full ? 1u : 0u);")
# pre-fix control: the s7810 fix reverted (raw zero-extended pointer into MEM_BU) must read H-differ (host FAULT)
PREFIX = ("gpr dest_reg = (gpr)(int64_t)(int32_t)(uint32_t)ctx->r4;", "gpr dest_reg = ctx->r4;")


def build_and_run(trials, plant, d, rec_file):
    host_src = open(os.path.join(ROOT, ROWS["zmemcpy"]["host"])).read()
    hb = extract(host_src, r'^extern "C" void zmemcpy\(uint8_t\* rdram, recomp_context\* ctx\) \{')
    rb = extract(open(rec_file).read(), r"^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC void zmemcpy\(")
    if not hb or not rb or ROWS["zmemcpy"]["retail_addr"] not in rb:
        return 2, "EXTRACT FAIL (host or retail zmemcpy moved)"
    if plant:
        a, b = PLANT if plant == 1 else PREFIX
        if a not in hb:
            return 2, "PLANT SITE MISSING"
        hb = hb.replace(a, b)
    rb = re.sub(r"^(?:__attribute__\(\(weak\)\) )?RECOMP_FUNC void zmemcpy\(", "void retail_fn(", rb, count=1, flags=re.M)
    rpre = open(rec_file).read().split("RECOMP_FUNC", 1)[0]
    srcs = {"h.cpp": PRELUDE + hb.replace('extern "C" void zmemcpy(', 'extern "C" void host_fn(') + "\n",
            "r.c": rpre + "\n" + rb + "\n", "x.c": HARNESS}
    inc = sum((["-I", p] for p in INC), [])
    objs = []
    for n, s_ in srcs.items():
        open(os.path.join(d, n), "w").write(s_)
        o = os.path.join(d, n.split(".")[0] + ".o")
        cc = ["c++", "-std=c++17"] if n.endswith(".cpp") else ["cc", "-std=gnu11"] + (["-Dmain=rs64_guest_main_"] if n == "r.c" else [])
        r = subprocess.run(cc + ["-O1", "-w", "-c", os.path.join(d, n), "-o", o] + inc, capture_output=True, text=True)
        if r.returncode:
            return 2, f"COMPILE FAIL {n}:\n" + r.stderr[-2000:]
        objs.append(o)
    nm = subprocess.run(["nm", "-u"] + objs, capture_output=True, text=True).stdout
    defined = subprocess.run(["nm", "-g", "--defined-only"] + objs, capture_output=True, text=True).stdout
    dset = {l.split()[-1] for l in defined.split("\n") if l.strip() and not l.endswith(":")}
    undef = sorted({l.split()[-1].lstrip("_") for l in nm.split("\n") if l.strip() and not l.endswith(":")}
                   - {x.lstrip("_") for x in dset})
    known = {"memcmp", "memcpy", "memset", "calloc", "malloc", "free", "printf", "fprintf", "atoi", "getenv", "puts",
             "putchar", "stderrp", "fwrite", "fputc", "fflush", "bzero", "__stderrp", "signal", "sigsetjmp", "siglongjmp", "setvbuf", "__stdoutp"}
    stub = "".join(f"long long {u}[4096];\n" if u.startswith("g_") else f"int {u}() {{ return 0; }}\n"
                   for u in undef if u not in known and not u.startswith("Z") and not u.startswith("_Z"))
    open(os.path.join(d, "s.c"), "w").write(stub)
    exe = os.path.join(d, "x")
    r = subprocess.run(["c++", "-O1", "-w", "-x", "c", os.path.join(d, "s.c"), "-x", "none", "-o", exe] + objs,
                       capture_output=True, text=True)
    if r.returncode:
        return 2, "LINK FAIL:\n" + r.stderr[-2000:]
    env = {k: v for k, v in os.environ.items() if not k.startswith("ROGUESQ_")}
    r = subprocess.run([exe, str(trials)], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=20000)
    ap.add_argument("--controls", action="store_true")
    a = ap.parse_args()
    both, host, rec, red = census()
    print(f"host defs={len(host)} recomp funcs={len(rec)} overrides={len(both)}")
    for n in both:
        print(f"  CLASS {ROWS.get(n, {}).get('cls', 'UNCLASSIFIED'):<12} {n}  host={','.join(host[n])} retail={rec[n]}")
    rc = 0
    if a.controls:
        planted = 'extern "C" void evalCubicSplineAtTime(uint8_t* rdram, recomp_context* ctx) {\n}\n'
        ok = any("evalCubicSplineAtTime" in x for x in census(planted)[3])
        print(f"CENSUS CONTROL {'PASS' if ok else 'FAIL'} (planted unrowed host override reads RED)")
        if not ok:
            red.append("census control failed"); rc = 3
    if "zmemcpy" in both:
        rf = os.path.join(RF, rec["zmemcpy"])
        sites, reads, bad = r2_readers(glob.glob(os.path.join(RF, "*.c")))
        print(f"[zmemcpy] r2 contract: call_sites={sites} r2_read_after_call={reads}")
        for b in bad[:10]:
            print("  R2READ " + b)
        if a.controls:  # scanner control: a synthetic real reader must count, a goto-guarded one must not
            td = tempfile.mkdtemp(prefix="s7810r_"); fp = os.path.join(td, "f.c")
            open(fp, "w").write("RECOMP_FUNC void a(uint8_t* rdram, recomp_context* ctx) {\n    zmemcpy(rdram, ctx);\n    ctx->r4 = ADD32(ctx->r2, 0);\n;}\n"
                                "RECOMP_FUNC void b(uint8_t* rdram, recomp_context* ctx) {\n    zmemcpy(rdram, ctx);\n        goto after_0;\n    ctx->r4 = ctx->r2;\n;}\n")
            cs, cr, _ = r2_readers([fp]); shutil.rmtree(td, ignore_errors=True)
            ok = cs == 2 and cr == 1
            print(f"[zmemcpy] R2-SCANNER CONTROL {'PASS' if ok else 'FAIL'} (sites={cs} readers={cr}, want 2/1)")
            if not ok:
                red.append("r2 scanner control failed"); rc = max(rc, 3)
        if reads or sites == 0:
            red.append(f"zmemcpy r2 contract: {reads} readers / {sites} sites")
        d = tempfile.mkdtemp(prefix="s7810_")
        try:
            r, out = build_and_run(a.trials, False, d, rf)
            print(f"[zmemcpy] rc={r}\n  " + out.replace("\n", "\n  "))
            if r:
                red.append(f"zmemcpy differential rc={r}"); rc = max(rc, r)
            if a.controls:
                r2, out2 = build_and_run(min(a.trials, 3000), True, d, rf)
                ok = r2 == 1 and "VERDICT H-differ" in out2
                print(f"[zmemcpy] PLANTED-MUTANT CONTROL {'PASS' if ok else 'FAIL'} (rc={r2}) {out2.splitlines()[0] if out2 else ''}")
                if not ok:
                    red.append("zmemcpy planted mutant not detected"); rc = max(rc, 3)
                r3, out3 = build_and_run(min(a.trials, 3000), 2, d, rf)
                ok = r3 == 1 and "host FAULT" in out3
                print(f"[zmemcpy] PRE-FIX (s7810 revert) CONTROL {'PASS' if ok else 'FAIL'} (rc={r3}) {out3.splitlines()[0] if out3 else ''}")
                if not ok:
                    red.append("zmemcpy pre-fix revert not detected"); rc = max(rc, 3)
        finally:
            if not os.environ.get("S7810_KEEP"):
                shutil.rmtree(d, ignore_errors=True)
            else:
                print("kept " + d)
    if red:
        rc = rc or 1
        for x in red:
            print("RED " + x)
    print("CLASS VERDICT " + ("GREEN (every host override == recompiled retail on in-RAM inputs)" if rc == 0 else "RED"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
