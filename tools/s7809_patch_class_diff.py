#!/usr/bin/env python3
"""s7809: class closure for the gcc-built C patch bodies in RecompiledPatches/patches.c.

s7808 runtime-qualified ONE patch body (findAndUnlinkSmallestEntry) offline. This tool closes the
whole class: it enumerates EVERY RECOMP_FUNC in patches.c and classifies it, failing RED when a
function appears that no row below accounts for (a new patch must get a row):

  (a) LIVE override with a recompiled retail twin -> differential run here (or delegated to the
      s7808 harness for findAndUnlinkSmallestEntry): the SHIPPED RECOMP_FUNC (wrapper + gcc body) and
      the recompiled retail function run on identical random guest state; compared after every call:
      the contract return register, every callee-saved register (s0-s8, gp, sp, ra) and RDRAM (watched
      windows every call, the whole 8 MB every 64 trials and at the end - a stray write persists, so
      the periodic full compare cannot miss one). Per-branch coverage counters must be > 0.
  (dead) no live entry: the function is reachable only from unused_patch_* roots, and no unused_patch_*
      name is referenced anywhere outside its own definition (src/, RecompiledPatches/, patches/).
  (b) deliberately behaviour-changing -> none exist today (a new one needs a row and a written delta).

Controls per (a) row: a planted mutant of the patch body must read H-differ, and a planted one-byte
RDRAM corruption must be seen by the comparator. Any HOLLOW (coverage 0 / control fail) fails the run.

  python3 tools/s7809_patch_class_diff.py [--trials N] [--controls]     rc 0 = all GREEN
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATCHES = os.path.join(ROOT, "RecompiledPatches", "patches.c")
RF = os.path.join(ROOT, "..", "N64Recomp", "RecompiledFuncs")
INC = [os.path.join(ROOT, p) for p in ("include", "RecompiledPatches", "lib/N64ModernRuntime/N64Recomp/include",
                                       "lib/N64ModernRuntime/librecomp/include",
                                       "lib/N64ModernRuntime/ultramodern/include")]
HELPER_RE = re.compile(r"_[0-9A-F]{8}$")

# (a) rows. setup: C lines run per trial on buffer m (both copies get the same state).
# cov: list of (name, C condition evaluated BEFORE the call on the pre-state) -> must each be > 0.
ROWS = {
    "isCinematicActive": dict(
        retail_file="funcs_29.c", retail_addr="0x800AF540", patch_addr="0x80801164",
        body=["isCinematicActive"], ret=True,
        setup="""uint32_t r = rnd(); uint32_t v = (r % 4 == 0) ? 0 : (r % 4 == 1) ? 1 : (r % 4 == 2) ? 0x80000000u : rnd();
                 ww(m, 0x800B0934u, v); ww(m, 0x800B0930u, rnd()); ww(m, 0x800B0938u, rnd());""",
        watch=[(0x800B0900, 0x80)],
        cov=[("flag_zero", "rw(m,0x800B0934u)==0"), ("flag_one", "rw(m,0x800B0934u)==1"),
             ("flag_high_bit", "rw(m,0x800B0934u)==0x80000000u"), ("flag_other", "rw(m,0x800B0934u)>1")],
        plant=("ctx->r2 = 0 < ctx->r2 ? 1 : 0;", "ctx->r2 = 1 < ctx->r2 ? 1 : 0;")),
    "setRngSeed": dict(
        retail_file="funcs_1.c", retail_addr="0x80003460", patch_addr="0x80801AB8",
        body=["setRngSeed", "rs64_seed_body"], ret=False,
        setup="""ww(m, 0x80003470u, rnd()); ww(m, 0x8000346Cu, rnd()); ww(m, 0x80003474u, rnd());
                 uint32_t s = (rnd() % 8 == 0) ? 0 : rnd(); uint64_t up = (rnd() % 2) ? ((uint64_t)rnd() << 32) : (uint64_t)(int64_t)(int32_t)s;
                 SEED = (up & 0xFFFFFFFF00000000ull) | s;""",
        watch=[(0x80003400, 0x100)],
        cov=[("seed_zero", "(uint32_t)SEED==0"), ("seed_nonzero", "(uint32_t)SEED!=0"),
             ("upper_garbage", "(uint32_t)(SEED>>32)!=(uint32_t)(((int64_t)(int32_t)(uint32_t)SEED)>>32)"), ("upper_signext_neg", "(uint32_t)SEED>=0x80000000u && (uint32_t)(SEED>>32)==0xFFFFFFFFu")],
        plant=("MEM_W(0X3470, ctx->r2) = ctx->r4;", "MEM_W(0X3474, ctx->r2) = ctx->r4;")),
}
DELEGATED = {"findAndUnlinkSmallestEntry": "tools/s7808_find_body_diff.py --controls (sweep row S7808_FIND)"}

HARNESS = r"""
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
extern void patch_fn(uint8_t* rdram, recomp_context* ctx);
extern void retail_fn(uint8_t* rdram, recomp_context* ctx);
#define RD 0x00800000u
#define A(x) ((x) - 0x80000000u)
static uint32_t rw(uint8_t* m, uint32_t a) { return *(uint32_t*)(m + A(a)); }
static void ww(uint8_t* m, uint32_t a, uint32_t v) { *(uint32_t*)(m + A(a)) = v; }
static uint64_t st = 0x9E3779B97F4A7C15ull;
static uint32_t rnd(void) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (uint32_t)st; }
static uint64_t SEED;
static const uint32_t WATCH[][2] = { @WATCH@ };
static int watch_same(uint8_t* a, uint8_t* b) {
    for (unsigned i = 0; i < sizeof WATCH / sizeof WATCH[0]; i++) if (memcmp(a + A(WATCH[i][0]), b + A(WATCH[i][0]), WATCH[i][1])) return 0;
    return 1;
}
static void setup(uint8_t* m) { @SETUP@ }
static void mkctx(recomp_context* c, uint64_t salt) {
    memset(c, 0, sizeof *c); uint64_t s = salt;
    for (int i = 1; i < 32; i++) { s = s * 6364136223846793005ull + 1442695040888963407ull; (&c->r0)[i] = s; }
    c->r29 = (gpr)(int32_t)0x80700000; c->r31 = (gpr)(int32_t)0x80022000; c->r4 = SEED;
}
static int regs_ok(recomp_context* p, recomp_context* r, int ret) {
    if (ret && p->r2 != r->r2) return 0;
    for (int i = 16; i <= 23; i++) if ((&p->r0)[i] != (&r->r0)[i]) return 0;
    for (int i = 28; i <= 31; i++) if ((&p->r0)[i] != (&r->r0)[i]) return 0;
    return 1;
}
int main(int argc, char** argv) {
    int trials = argc > 1 ? atoi(argv[1]) : 20000, ret = @RET@;
    uint8_t *mp = calloc(1, RD), *mr = calloc(1, RD);
    long bad = 0, plants = 0, plant_det = 0, fulls = 0;
    const char* cov_names[] = { @COVN@ }; long cov[@NCOV@] = {0};
    for (int t = 0; t < trials && bad == 0; t++) {
        uint64_t st0 = st; setup(mp); uint64_t seed_p = SEED; st = st0; setup(mr); SEED = seed_p;
        { uint8_t* m = mp; @COVC@ }
        uint64_t salt = ((uint64_t)rnd() << 32) | rnd();
        recomp_context cp, cr; mkctx(&cp, salt); mkctx(&cr, salt);
        patch_fn(mp, &cp); retail_fn(mr, &cr);
        int full = (t % 64 == 63) || t == trials - 1;
        if (full) fulls++;
        if (!regs_ok(&cp, &cr, ret) || !watch_same(mp, mr) || (full && memcmp(mp, mr, RD))) {
            bad++; printf("MISMATCH trial=%d r2 patch=%016llX retail=%016llX full=%d\n", t, (unsigned long long)cp.r2, (unsigned long long)cr.r2, full);
        }
        if (t % 97 == 0) { plants++; uint32_t off = rnd() % RD; mp[off] ^= 0x10; if (memcmp(mp, mr, RD)) plant_det++; mp[off] ^= 0x10; }
    }
    int covok = 1; printf("trials=%d full_compares=%ld", trials, fulls);
    for (int i = 0; i < @NCOV@; i++) { printf(" %s=%ld", cov_names[i], cov[i]); if (!cov[i]) covok = 0; }
    printf("\nmismatch=%ld CONTROL plant_detected=%ld/%ld\n", bad, plant_det, plants);
    int ctl = covok && plants > 0 && plant_det == plants;
    printf("CONTROLS %s\nVERDICT %s\n", ctl ? "PASS" : "FAIL", bad ? "H-differ" : (!ctl ? "HOLLOW" : "H-equal"));
    return bad ? 1 : (!ctl ? 3 : 0);
}
"""


def split_funcs(path):
    """name -> (start, end) line indices for every top-level function definition, plus the preamble."""
    lines = open(path).read().split("\n")
    heads = []
    for i, l in enumerate(lines):
        m = re.match(r"^(?:__attribute__\(\(weak\)\) )?(?:RECOMP_FUNC|static) void (\w+)\(uint8_t\* rdram, recomp_context\* ctx\) \{", l)
        if m:
            heads.append((m.group(1), i))
    out = {}
    for k, (n, s) in enumerate(heads):
        lim = heads[k + 1][1] if k + 1 < len(heads) else len(lines)
        e = max(j for j in range(s, lim) if lines[j] in ("}", ";}"))
        out[n] = (s, e)
    first = heads[0][1] if heads else 0
    return lines, out, "\n".join(lines[:first])


def classify(path=PATCHES, scan_refs=True):
    lines, fns, _ = split_funcs(path)
    recomp = [n for n, (s, _) in fns.items() if lines[s].startswith("RECOMP_FUNC")]
    calls = {n: set(re.findall(r"\b(\w+)\(rdram, ctx\);", "\n".join(lines[s + 1:e + 1]))) for n, (s, e) in fns.items()}
    roots = [n for n in recomp if not n.startswith("unused_patch_") and not HELPER_RE.search(n)]
    live, stack = set(), list(roots)
    while stack:
        n = stack.pop()
        if n in live:
            continue
        live.add(n)
        stack += [c for c in calls.get(n, ()) if c in fns]
    rows, red = [], []
    for n in recomp:
        if n in ROWS:
            rows.append((n, "a", "differential here"))
        elif n in DELEGATED:
            rows.append((n, "a", "delegated: " + DELEGATED[n]))
        elif n.startswith("unused_patch_") or HELPER_RE.search(n):
            if n in live:
                red.append(f"{n}: classified dead but reachable from a live root")
            rows.append((n, "dead", "callers: " + (",".join(sorted(m for m in fns if n in calls[m])) or "none")))
        else:
            red.append(f"{n}: live RECOMP_FUNC with no class row (add a ROWS/DELEGATED entry)")
            rows.append((n, "UNCLASSIFIED", ""))
    # unused_patch_* must have no reference outside its own definition line
    refs = "" if not scan_refs else subprocess.run(["grep", "-rn", "--include=*.c", "--include=*.cpp", "--include=*.h", "--include=*.inl",
                           "--include=*.S", "unused_patch_", os.path.join(ROOT, "src"), os.path.join(ROOT, "RecompiledPatches"),
                           os.path.join(ROOT, "patches")], capture_output=True, text=True).stdout
    if not scan_refs:
        refs = "\n".join(l for l in lines if "unused_patch_" in l)
    for l in refs.splitlines():
        if not re.search(r"RECOMP_FUNC void unused_patch_\w+\(", l):
            red.append("unused_patch_ referenced: " + l[:160])
    return rows, red, roots


def build_and_run(name, row, trials, plant, d):
    plines, pfns, ppre = split_funcs(PATCHES)
    rpath = os.path.join(RF, row["retail_file"])
    rlines, rfns, rpre = split_funcs(rpath)
    pbody = ""
    for b in row["body"]:
        s, e = pfns[b]
        pbody += "\n".join(plines[s:e + 1]) + "\n"
    if row["patch_addr"].upper().replace("0X", "0x") not in pbody.upper().replace("0X", "0x"):
        return 2, f"EXTRACT FAIL {name}: patch address {row['patch_addr']} moved"
    s, e = rfns[name]
    rbody = "\n".join(rlines[s:e + 1])
    if row["retail_addr"].upper() not in rbody.upper():
        return 2, f"EXTRACT FAIL {name}: retail address moved"
    fwd = "".join(f"static void {b}(uint8_t* rdram, recomp_context* ctx);\n" for b in row["body"][1:])
    pbody = re.sub(rf"^RECOMP_FUNC void {name}\(", "void patch_fn(", pbody, count=1, flags=re.M)
    if plant:
        a, b = row["plant"]
        if a not in pbody:
            return 2, f"PLANT SITE MISSING {name}"
        pbody = pbody.replace(a, b)
    rbody = re.sub(rf"^__attribute__\(\(weak\)\) RECOMP_FUNC void {name}\(", "void retail_fn(", rbody, count=1, flags=re.M)
    if "void retail_fn(" not in rbody:
        rbody = rbody.replace(f"RECOMP_FUNC void {name}(", "void retail_fn(", 1)
    cov = row["cov"]
    h = (HARNESS.replace("@WATCH@", ", ".join(f"{{0x{a:08X}u, 0x{n:X}u}}" for a, n in row["watch"]))
         .replace("@SETUP@", row["setup"]).replace("@RET@", "1" if row["ret"] else "0")
         .replace("@COVN@", ", ".join(f'"{c[0]}"' for c in cov)).replace("@NCOV@", str(len(cov)))
         .replace("@COVC@", " ".join(f"if ({c[1]}) cov[{i}]++;" for i, c in enumerate(cov))))
    srcs = {"p.c": ppre + "\n" + fwd + pbody, "r.c": rpre + "\n" + rbody + "\n", "h.c": '#include "recomp.h"\n' + h}
    for n, s_ in srcs.items():
        open(os.path.join(d, n), "w").write(s_)
    inc = sum((["-I", p] for p in INC), [])
    objs = []
    for n in srcs:
        o = os.path.join(d, n[:-2] + ".o")
        r = subprocess.run(["cc", "-O1", "-w", "-std=gnu11", "-Wno-error=implicit-function-declaration", "-c",
                            os.path.join(d, n), "-o", o] + inc, capture_output=True, text=True)
        if r.returncode:
            return 2, f"COMPILE FAIL {name} {n}:\n" + r.stderr[-2000:]
        objs.append(o)
    nm = subprocess.run(["nm", "-u"] + objs, capture_output=True, text=True).stdout
    undef = sorted({l.split()[-1].lstrip("_") for l in nm.split("\n") if l.strip() and not l.endswith(":")})
    known = {"memcmp", "memcpy", "memset", "calloc", "printf", "fprintf", "atoi", "getenv", "puts", "putchar",
             "stderrp", "fwrite", "fputc", "patch_fn", "retail_fn", "bzero"}
    # diagnostic data hooks read as zero (every gate off); hook functions are no-ops
    stub = "".join(f"long long {u}[4096];\n" if u.startswith("g_") else f"int {u}() {{ return 0; }}\n"
                   for u in undef if u not in known)
    open(os.path.join(d, "s.c"), "w").write(stub)
    exe = os.path.join(d, "x")
    r = subprocess.run(["cc", "-O1", "-w", "-std=gnu89", os.path.join(d, "s.c"), "-o", exe] + objs, capture_output=True, text=True)
    if r.returncode:
        return 2, f"LINK FAIL {name}:\n" + r.stderr[-2000:]
    env = {k: v for k, v in os.environ.items() if not k.startswith("ROGUESQ_")}  # wrapper ctl flags off
    r = subprocess.run([exe, str(trials)], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=20000)
    ap.add_argument("--controls", action="store_true", help="also run each planted patch mutant; each must read H-differ")
    a = ap.parse_args()
    rows, red, roots = classify()
    print(f"patches.c RECOMP_FUNCs={len(rows)} live_roots={','.join(sorted(roots))}")
    for n, c, why in rows:
        print(f"  CLASS {c:<12} {n}  {why}")
    rc = 0
    if a.controls:  # classifier plants: an unrowed live patch and a dead helper made reachable must both read RED
        src = open(PATCHES).read()
        td = tempfile.mkdtemp(prefix="s7809c_")
        p1 = os.path.join(td, "p1.c"); open(p1, "w").write(src + "\nRECOMP_FUNC void plantedNewPatch(uint8_t* rdram, recomp_context* ctx) {\n}\n")
        p2 = os.path.join(td, "p2.c"); open(p2, "w").write(src.replace("    rs64_seed_body(rdram, ctx);\n", "    rs64_seed_body(rdram, ctx);\n    active_queue_disjoint_00000060(rdram, ctx);\n", 1))
        p3 = os.path.join(td, "p3.c"); open(p3, "w").write(src + "\nstatic void x(void) { unused_patch_allocateDisplayListBuffer(0, 0); }\n")
        r1 = any("plantedNewPatch" in x for x in classify(p1, False)[1])
        r2 = any("active_queue_disjoint_00000060" in x and "reachable" in x for x in classify(p2, False)[1])
        r3 = any("unused_patch_ referenced" in x for x in classify(p3, False)[1])
        shutil.rmtree(td, ignore_errors=True)
        ok = r1 and r2 and r3
        print(f"CLASSIFIER CONTROLS {'PASS' if ok else 'FAIL'} unrowed={int(r1)} dead_reachable={int(r2)} unused_referenced={int(r3)}")
        if not ok:
            red.append("classifier controls failed"); rc = 3
    d = tempfile.mkdtemp(prefix="s7809_")
    try:
        for name, row in ROWS.items():
            r, out = build_and_run(name, row, a.trials, False, d)
            print(f"[{name}] rc={r}\n  " + out.replace("\n", "\n  "))
            if r:
                rc = max(rc, r if r != 1 else 1)
                red.append(f"{name}: rc={r}")
            if a.controls:
                r2, out2 = build_and_run(name, row, min(a.trials, 3000), True, d)
                ok = r2 == 1 and "VERDICT H-differ" in out2
                print(f"[{name}] PLANTED-PATCH CONTROL {'PASS' if ok else 'FAIL'} (rc={r2})")
                if not ok:
                    red.append(f"{name}: planted mutant not detected")
                    rc = max(rc, 3)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    if red:
        rc = rc or 1
        for x in red:
            print("RED " + x)
    print("CLASS VERDICT " + ("GREEN (every live patch body == retail; rest dead)" if rc == 0 else "RED"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
