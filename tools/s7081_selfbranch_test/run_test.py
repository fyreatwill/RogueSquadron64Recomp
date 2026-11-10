#!/usr/bin/env python3
"""s7081 differential test for the self-branch fix.

Builds a standalone harness from a (patched) funcs_24.c: the file's preamble
plus the 4 resampler callers and their 4 helpers, compiled with the real
recomp.h. Random voice states are run three ways:
  ref  - mips_ref.py executing the retail bytes from the ELF (independent)
  on   - generated C with g_rs64_sbx_on = 1 (the s7081 fix)
  off  - generated C with g_rs64_sbx_on = 0 (the old miscompiled path)
Each case runs in a forked child so a crash is a verdict, not an abort.
Cases are split into 'exit' (one-shot sample, $s3 = 0: the 16 fixed branches)
and 'loop' (looping sample: helpers return normally; positive control that the
harness and reference agree where N64Recomp was always right).
Usage: run_test.py <funcs_24.c> [n_cases_per_kind] [seed]
"""
import os, random, re, subprocess, sys, pathlib, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mips_ref as M

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
ELF = REPO.parent / 'rogue_squadron64/build/roguesquadron.elf'
INC = REPO.parent / 'N64Recomp/include'
CALLERS = {  # caller -> (helper, sample stride in bytes, entry vram)
    'resampleVoicePointTableSamples': ('interpolatePointTableSamplesToPackedWord', 2, 0x8009264C),
    'resampleVoiceLutSamples': ('interpolateLutSamplesToPackedWord', 1, 0x800928D4),
    'resampleVoiceConstantSamples': ('interpolateConstantSamplesToPackedWord', 2, 0x80092BA8),
    'resampleVoiceLutSamplesPacked': ('packFourLutResampledSamples', 1, 0x80092E48),
}
OUT = pathlib.Path(os.environ.get('S7081_OUT', REPO / 'scratch/s7081/test'))
A0, A1, SAMP, OBUF, STK = 0x80700000, 0x80700100, 0x80701000, 0x80710000, 0x80720000
SENT = 0x807F0000  # return sentinel (never executed)
REGIONS = [(A0, 0x20), (A1, 0x10), (OBUF, 0x800), (STK - 0x40, 0x40)]

HARNESS_MAIN = r'''
#undef main
/* data the generated preamble references; all diag hooks stay off */
int g_rs64_lowfield_hook, g_rs64_synthread_hook, g_rs64_store_diag; uint32_t g_rs64_s6992_lo;
volatile int g_s6559_pend; volatile uint32_t rs64_s6843_lo, rs64_s6843_len;
#include <sys/wait.h>
#include <unistd.h>
int g_rs64_sbx_on = 1; __thread uint32_t g_rs64_sbx_target; unsigned long g_sbx_hits;
static uint32_t g_sbx_last; void rs64_sbx_hit(uint32_t fn, uint32_t t) { (void)fn; g_sbx_last = t; g_sbx_hits++; }
typedef void (*rfn)(uint8_t*, recomp_context*);
struct ent { const char* n; rfn f; };
static struct ent T[] = { FUNC_TABLE {0, 0} };
int main(int argc, char** argv) {
    g_rs64_sbx_on = atoi(argv[1]);
    FILE* seg = fopen(argv[2], "rb"); static uint8_t img[0x800000]; fread(img, 1, sizeof img, seg); fclose(seg);
    uint8_t* rdram = malloc(0x800000);
    char fn[128]; char line[1 << 16];
    while (fgets(line, sizeof line, stdin)) {
        if (strncmp(line, "case ", 5)) continue;
        int id; sscanf(line + 5, "%d %127s", &id, fn);
        recomp_context ctx; memset(&ctx, 0, sizeof ctx);
        for (int i = 0; i < 0x800000; i += 4) { uint32_t w = ((uint32_t)img[i]<<24)|((uint32_t)img[i+1]<<16)|((uint32_t)img[i+2]<<8)|img[i+3]; memcpy(rdram + i, &w, 4); }
        while (fgets(line, sizeof line, stdin) && strncmp(line, "run", 3)) {
            unsigned n; unsigned long long v; unsigned a;
            if (sscanf(line, "reg %u %llx", &n, &v) == 2) ((gpr*)&ctx)[n] = v;
            else if (sscanf(line, "w %x %llx", &a, &v) == 2) *(uint32_t*)(rdram + (a - 0x80000000u)) = (uint32_t)v;
        }
        rfn f = 0; for (int i = 0; T[i].n; i++) if (!strcmp(T[i].n, fn)) f = T[i].f;
        fflush(stdout);
        int pfd[2]; pipe(pfd);
        pid_t pid = fork();
        if (pid == 0) {
            close(pfd[0]); FILE* o = fdopen(pfd[1], "w");
            g_sbx_hits = 0; f(rdram, &ctx);
            fprintf(o, "hits %lu\ntgt %08x\n", g_sbx_hits, g_sbx_last);
            for (int i = 0; i < 32; i++) fprintf(o, "reg %d %016llx\n", i, (unsigned long long)((gpr*)&ctx)[i]);
            REGION_DUMP
            fclose(o); _exit(0);
        }
        close(pfd[1]); char buf[1 << 16]; size_t got = 0; ssize_t k;
        while ((k = read(pfd[0], buf + got, sizeof buf - 1 - got)) > 0) got += k; buf[got] = 0; close(pfd[0]);
        int st; waitpid(pid, &st, 0);
        printf("res %d %s\n%s", id, (WIFEXITED(st) && WEXITSTATUS(st) == 0) ? "ok" : "crash", (WIFEXITED(st) && !WEXITSTATUS(st)) ? buf : "");
        printf("end\n");
    }
    return 0;
}
'''


def build(funcs_c):
    OUT.mkdir(parents=True, exist_ok=True)
    s = pathlib.Path(funcs_c).read_text()
    first = s.index('RECOMP_FUNC void ')
    pre = s[:first]
    bodies = []
    for name in list(CALLERS) + [h for h, _, _ in CALLERS.values()]:
        m = re.search(r'^RECOMP_FUNC void ' + name + r'\(uint8_t\* rdram, recomp_context\* ctx\) \{\n.*?^;?\}\n', s, re.S | re.M)
        if not m:
            sys.exit(f'function {name} not found')
        bodies.append(m.group(0))
    table = ' '.join(f'{{"{n}", {n}}},' for n in CALLERS)
    dump = ''.join(
        f'for (unsigned a = 0x{a:08X}u; a < 0x{a + n:08X}u; a += 4) fprintf(o, "w %08x %08x\\n", a, *(uint32_t*)(rdram + (a - 0x80000000u)));\n'
        for a, n in REGIONS)
    main = HARNESS_MAIN.replace('FUNC_TABLE', table).replace('REGION_DUMP', dump)
    tu = OUT / 'harness.c'
    tu.write_text('#include <string.h>\n' + pre + '\n'.join(bodies) + main)
    exe = OUT / 'harness'
    # same include order and flags as CMakeLists.txt's RecompiledFuncs target
    cmd = ['clang', '-O1', '-w', '-fno-strict-aliasing', '-Dmain=rs_main', '-DRS64_BYTE_WATCH',
           '-include', str(REPO / 'include/rsp_dpc_macros.h'), '-I' + str(REPO / 'include'),
           '-I' + str(REPO / 'lib/N64ModernRuntime/ultramodern/include'),
           '-I' + str(REPO / 'lib/N64ModernRuntime/librecomp/include'),
           '-I' + str(REPO / 'lib/N64ModernRuntime/N64Recomp/include'),
           '-I' + str(REPO.parent / 'N64Recomp/RecompiledFuncs'), str(tu), '-o', str(exe),
           '-Wl,-undefined,dynamic_lookup']
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit('build failed:\n' + r.stderr[-4000:])
    return exe


def make_case(rng, caller, kind):
    helper, stride, entry = CALLERS[caller]
    nsamp = rng.randint(1, 12) if kind == 'exit' else rng.randint(1, 48)
    start = SAMP + stride * rng.randint(0, 16)
    end_excl = start + stride * (nsamp - 1) + 1  # s2 = a0[0x18] - 1 = address of the last sample
    words = {}
    k = rng.randint(1, 24)  # t8 = a0[8] >> 3 iterations of 2 jal each
    rate = rng.choice([0, rng.randint(0, 0xFFFF), rng.randint(0, 0x3FFFFFFF), rng.randint(0, 0xFFFFFFFF),
                       rng.randint(0x80000000, 0xFFFFFFFF)])
    # a0[0x14]: interpolation gain for PointTable/Lut, extra pointer step for Constant/Packed (kept small there)
    step = rng.randint(0, 0xFFFF) if rng.random() < .7 else rng.randint(0, 0xFFFFFFFF)
    if caller in ('resampleVoiceConstantSamples', 'resampleVoiceLutSamplesPacked'):
        step = rng.randint(0, 3)
    a0 = [start, OBUF, 8 * k, 0, rate, step,
          end_excl, 0 if kind == 'exit' else start + stride * rng.randint(0, nsamp - 1)]
    for i, v in enumerate(a0):
        words[A0 + 4 * i] = v
    for i in range(4):
        words[A1 + 4 * i] = rng.getrandbits(32)
    mode = rng.choice([0, 1])
    # PointTable reads the mode byte at a1+0xE; the others take $a2 as passed.
    w3 = words[A1 + 0xC]
    words[A1 + 0xC] = (w3 & 0xFFFF00FF) | (mode << 8)
    for i in range(0, 0x200, 4):
        words[SAMP + i] = rng.getrandbits(32)
    regs = [0] * 32
    for i in range(1, 32):
        regs[i] = M.sx32(rng.getrandbits(32))
    regs[4], regs[5], regs[6] = M.sx32(A0), M.sx32(A1), mode
    regs[29], regs[31] = M.sx32(STK), M.sx32(SENT)
    return regs, words


def main():
    funcs_c = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 7081
    exe = build(funcs_c)
    base = M.Mem()
    loaded = M.load_segment(base, ELF)
    seg = OUT / 'seg.bin'
    seg.write_bytes(bytes(base.b))
    rng = random.Random(seed)
    cases = []
    for caller in CALLERS:
        for kind in ('exit', 'loop'):
            for _ in range(n):
                cases.append((caller, kind) + make_case(rng, caller, kind))
    # reference
    refs = []
    for caller, kind, regs, words in cases:
        mem = M.Mem(); mem.b[:] = base.b
        for a, v in words.items():
            mem.wr(a, 4, v)
        try:
            r, steps = M.run(mem, regs, CALLERS[caller][2], SENT)
            dump = {a: mem.rd(a, 4) for ra, rn in REGIONS for a in range(ra, ra + rn, 4)}
            refs.append(('ok', r, dump, steps))
        except (MemoryError, TimeoutError) as e:
            refs.append(('ref-' + type(e).__name__, None, None, 0))
    script = ''.join(
        f'case {i} {c}\n' + ''.join(f'reg {j} {v & M.M64:x}\n' for j, v in enumerate(regs)) +
        ''.join(f'w {a:x} {v:x}\n' for a, v in words.items()) + 'run\n'
        for i, (c, k, regs, words) in enumerate(cases))
    results = {}
    for arm in ('1', '0'):
        p = subprocess.run([str(exe), arm, str(seg)], input=script, capture_output=True, text=True)
        out = {}
        for blk in p.stdout.split('end\n'):
            m = re.match(r'res (\d+) (\w+)\n', blk)
            if not m:
                continue
            regs = {int(a): int(b, 16) for a, b in re.findall(r'^reg (\d+) ([0-9a-f]+)$', blk, re.M)}
            mem = {int(a, 16): int(b, 16) for a, b in re.findall(r'^w ([0-9a-f]+) ([0-9a-f]+)$', blk, re.M)}
            hits = re.search(r'^hits (\d+)$', blk, re.M)
            tg = re.search(r'^tgt ([0-9a-f]+)$', blk, re.M)
            out[int(m.group(1))] = (m.group(2), regs, mem, int(hits.group(1)) if hits else 0, int(tg.group(1), 16) if tg else 0)
        results[arm] = out
    # compare
    table = {}
    examples = []
    for i, (c, k, _, _) in enumerate(cases):
        ref = refs[i]
        for arm in ('1', '0'):
            got = results[arm].get(i)
            key = (c, k, 'on' if arm == '1' else 'off')
            t = table.setdefault(key, {'match': 0, 'mismatch': 0, 'crash': 0, 'refskip': 0, 'hits': 0})
            if ref[0] != 'ok':
                t['refskip'] += 1; continue
            if got is None or got[0] != 'ok':
                t['crash'] += 1; continue
            t['hits'] += got[3] > 0
            if got[3]: t.setdefault('tg', set()).add(got[4])
            bad = [j for j in range(1, 32) if got[1].get(j) != ref[1][j]] + \
                  [a for a in ref[2] if got[2].get(a) != ref[2][a]]
            if bad:
                t['mismatch'] += 1
                if len(examples) < 6 and arm == '1':
                    examples.append((i, c, k, bad[:6]))
            else:
                t['match'] += 1
    print(f'ELF sections loaded: {[(n, hex(a), hex(s)) for n, a, s in loaded]}')
    print(f'{"caller":34s} {"kind":5s} {"arm":4s} match mismatch crash refskip sbx_hit_cases')
    for key, t in table.items():
        print(f'{key[0]:34s} {key[1]:5s} {key[2]:4s} {t["match"]:5d} {t["mismatch"]:8d} {t["crash"]:5d} {t["refskip"]:7d} {t["hits"]:5d}  targets {" ".join("%08X" % x for x in sorted(t.get("tg", ())))}')
    steps = [r[3] for r in refs if r[0] == 'ok']
    print(f'ref steps per case: min {min(steps)} max {max(steps)}')
    for e in examples:
        print('ON-ARM MISMATCH example', e)
    on_bad = sum(t['mismatch'] + t['crash'] for k, t in table.items() if k[2] == 'on')
    print('VERDICT on-arm', 'PASS' if on_bad == 0 else f'FAIL ({on_bad})')
    return 0 if on_bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
