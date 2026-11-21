#!/usr/bin/env python3
"""s7777: score a ROGUESQ_S7777_DANGLE=1 (+ ROGUESQ_STORE_DIAG=1) run (src/main/upstream_compat.cpp s7777_sweep/s7777_access).
Class: resident global words (0x80000400..0x80154690) that hold an rs_malloc pointer and outlive the block (s7776's
*0x80130BB0 was one member). The runtime logs every word that turned dangling ([s7777] dangle a= v= why=f|F|N|R) and every
guest load of a word while it was dangling ([s7777] dangling-read). This tool classifies each word:
  region: main-code / main-data / overlay (0x800A5130..0x8010D200, code or data depending on the overlay) / main-bss
  sym:    the containing symbol (elf nm + symbol_files/*.txt)
  kind:   CODE-LOOKALIKE (inside a function's text: an instruction whose bits look like a heap pointer; never data-loaded)
          or DATA (a real global)
Verdicts (exit code): 0 H-all-unused (watch controls passed, 0x80130BB0 dangled = class positive control, 0 dangling reads),
1 H-latent (dangling reads > 0: rows name every (word, reader pc, fn)), 3 VOID (a control failed).
usage: s7777_dangle_score.py <run.log> [--selftest]"""
import re, sys, subprocess, glob, os

ELF = "/Users/williambuckley/Documents/Tools/rogue_squadron64/build/roguesquadron.elf"
SYMD = "/Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files"

def load_syms():
    fns, data = [], []
    try:
        out = subprocess.run(["mips64-elf-nm", "-S", "-n", ELF], capture_output=True, text=True).stdout
        for ln in out.splitlines():
            p = ln.split()
            if len(p) == 4 and p[2] in "Tt":
                a = int(p[0], 16) & 0xFFFFFFFF; fns.append((a, a + int(p[1], 16), p[3]))
    except Exception:
        pass
    for f in glob.glob(os.path.join(SYMD, "*.txt")):
        ov = os.path.basename(f)[:-4]
        for ln in open(f, errors="replace"):
            m = re.match(r"\s*(\w+)\s*=\s*0x([0-9A-Fa-f]{8})\s*;(?:.*size:\s*0x([0-9A-Fa-f]+))?", ln)
            if m:
                a = int(m[2], 16); data.append((a, a + (int(m[3], 16) if m[3] else 4), m[1], ov))
    return fns, data

ALLOC_META = (0x8010FEE8, 0x8010FF1C)  # rs_malloc arena heads / free-list words: the allocator's own bookkeeping, not owner pointers

def insn(pc):
    """the reader instruction's mnemonic (lw = pointer-width read; lhu/lh/lb = the word is not read as a pointer)"""
    try:
        out = subprocess.run(["mips64-elf-objdump", "-d", f"--start-address=0x{pc:x}", f"--stop-address=0x{pc + 4:x}", ELF], capture_output=True, text=True).stdout
        for ln in out.splitlines():
            m = re.match(r"\s*(?:ffffffff)?([0-9a-f]{8}):\s+[0-9a-f]{8}\s+(\S+)\s*(.*)", ln)
            if m and int(m[1], 16) == pc: return m[2] + " " + m[3]
    except Exception:
        pass
    return "?"

def region(a):
    if a < 0x800A5130:
        return "main-data" if 0x80037560 <= a < 0x8003A0D0 or 0x80003470 <= a < 0x80003480 else "main-code"
    if a < 0x8010D200: return "overlay"
    return "main-bss"

def classify(a, fns, data):
    f = next((n for lo, hi, n in fns if lo <= a < hi), None)
    d = [(lo, n, ov) for lo, hi, n, ov in data if lo <= a < hi]
    sym = (f"{d[-1][1]}+0x{a - d[-1][0]:X}({d[-1][2]})" if d else (f"fn:{f}" if f else "?"))
    rg = region(a)
    kind = "CODE-LOOKALIKE" if (f and not d and rg in ("main-code", "overlay")) else "DATA"
    return rg, sym, kind

DROWS = {}
def score(lines, fns, data):
    DROWS.clear()
    dang, reads, rows, sums, ctl = {}, [], {}, [], {"load": 0, "store": 0}
    for ln in lines:
        m = re.search(r"\[s7777\] watch-ctl-(load|store) PASS", ln)
        if m: ctl[m[1]] = 1; continue
        m = re.search(r"\[s7777\] dangle a=(\w+) v=(\w+) why=(\w) blk=(\w+) bsz=(\w+) ser=(\d+) age=([\d.]+) t=([\d.]+)", ln)
        if m:
            a = int(m[1], 16); dang.setdefault(a, []).append((m[3], int(m[2], 16), int(m[4], 16), int(m[6]), float(m[8]))); continue
        m = re.search(r"\[s7777\] dangling-read a=(\w+) v=(\w+) why=(\w) pc=(\w+) fn=(\S+) since=([\d.]+) t=([\d.]+)", ln)
        if m: reads.append((int(m[1], 16), int(m[4], 16), m[5], m[3], float(m[6]), float(m[7]))); continue
        m = re.search(r"\[s7777\] rdrow a=(\w+) pc=(\w+) fn=(\S+) n=(\d+)", ln)
        if m: rows[(int(m[1], 16), int(m[2], 16))] = (m[3], int(m[4])); continue
        m = re.search(r"\[s7777\] drow word=(\w+) pc=(\w+) kind=(\w) fn=(\S+) n=(\d+) same_fn=(\d) open=(\d)", ln)
        if m: DROWS[(int(m[1], 16), int(m[2], 16), m[3])] = (m[4], int(m[5]), int(m[6]), int(m[7])); continue
        m = re.search(r"\[s7777\] sum t=([\d.]+) .*tracked=(\d+) dangling=(\d+) dangle_events=(\d+) clean_reads=(\d+) dangling_reads=(\d+) stores=(\d+) reinit=(\d+)", ln)
        if m: sums.append(tuple(float(x) for x in m.groups()))
    return dang, reads, rows, sums, ctl

def report(dang, reads, rows, sums, ctl, fns, data):
    last = sums[-1] if sums else None
    print(f"sums={len(sums)} last: t={last[0] if last else '-'} tracked={int(last[1]) if last else '-'} dangle_events={int(last[3]) if last else '-'} "
          f"clean_reads={int(last[4]) if last else '-'} dangling_reads={int(last[5]) if last else '-'} stores={int(last[6]) if last else '-'} reinit={int(last[7]) if last else '-'}")
    print(f"controls: watch-load={ctl['load']} watch-store={ctl['store']} slot_table_0x80130BB0_dangled={'yes' if 0x80130BB0 in dang else 'NO'}"
          + (f" (why={dang[0x80130BB0][0][0]} t={dang[0x80130BB0][0][4]})" if 0x80130BB0 in dang else ""))
    cls = {}
    for a in sorted(dang):
        rg, sym, kind = classify(a, fns, data); cls[a] = (rg, sym, kind)
    nd = sum(1 for a in cls if cls[a][2] == "DATA"); nc = len(cls) - nd
    print(f"dangling words: {len(cls)} (DATA {nd}, CODE-LOOKALIKE {nc})")
    whys = {}
    for a in cls:
        for e in dang[a]: whys[(cls[a][2], e[0])] = whys.get((cls[a][2], e[0]), 0) + 1
    print("events by kind/why:", " ".join(f"{k[0]}/{k[1]}={v}" for k, v in sorted(whys.items())))
    for a in sorted(cls):
        if cls[a][2] != "DATA": continue
        e = dang[a]; rd = sum(n for (wa, pc), (fn, n) in rows.items() if wa == a) or sum(1 for r in reads if r[0] == a)
        print(f"  DATA {a:08X} {cls[a][0]:9s} {cls[a][1]:44s} events={len(e)} whys={''.join(sorted(set(x[0] for x in e)))} first_t={e[0][4]:.1f} v={e[0][1]:08X} blk={e[0][2]:08X} reads_while_dangling={rd}")
    readers = {}
    for (a, pc, fn, why, since, t) in reads: readers.setdefault((a, pc, fn), (why, since, t))
    for (a, pc), (fn, n) in rows.items(): readers.setdefault((a, pc, fn), ("?", 0, 0))
    for (a, pc, fn), (why, since, t) in sorted(readers.items()):
        rg, sym, kind = cls.get(a) or classify(a, fns, data)
        ins = insn(pc); cat = ("ALLOC-META" if ALLOC_META[0] <= a < ALLOC_META[1] else "NOT-PTR-READ" if not ins.startswith("lw ") and ins != "?" else
               "FRAME-REGION" if why == "R" else "STALE-PTR")
        readers[(a, pc, fn)] = (why, since, t, cat)
        print(f"  READER word={a:08X} {sym} pc={pc:08X} fn={fn} insn='{ins}' why={why} cat={cat} since_dangle={since:.2f}s t={t:.1f} n={rows.get((a, pc), ('', 1))[1]}")
    for (w, pc, k), (fn, n, same, op) in sorted(DROWS.items()):
        print(f"  DEREF word={w:08X} kind={k} pc={pc:08X} fn={fn} n={n} same_fn_as_reader={same} while_dangling={op}")
    if not (ctl["load"] and ctl["store"] and 0x80130BB0 in dang and sums):
        print("VERDICT VOID (a control failed)"); return 3
    stale = [k for k, v in readers.items() if len(v) > 3 and v[3] == "STALE-PTR"]
    derefs = [k for k, v in DROWS.items() if v[2] and v[3]]
    print(f"stale-pointer readers={len(stale)} stale derefs by the reader's own fn while dangling={len(derefs)}")
    if readers:
        print(f"VERDICT H-latent ({len(readers)} reader rows over {len(set(r[0] for r in readers))} words)"); return 1
    print("VERDICT H-all-unused"); return 0

def selftest(fns, data):
    base = ["[s7777] watch-ctl-load PASS pc=1 fn=x", "[s7777] watch-ctl-store PASS pc=1 fn=x",
            "[s7777] dangle a=80130BB0 v=80202120 why=N blk=80202110 bsz=4000 ser=5 age=9.0 t=15.0",
            "[s7777] sum t=20.0 sweeps=1 blocks=1 heap=1..2 tracked=10 dangling=1 dangle_events=1 clean_reads=5 dangling_reads=0 stores=1 reinit=0 ctl_ld=1 ctl_st=1"]
    rc = [score_rc(base, fns, data), score_rc(base + ["[s7777] dangling-read a=80130BB0 v=80202120 why=N pc=80055555 fn=f since=1.00 t=16.0"], fns, data),
          score_rc(base[1:], fns, data)]
    ok = rc == [0, 1, 3]; print(f"selftest unused/latent/dead-ctl = {rc} {'PASS' if ok else 'FAIL'}"); return 0 if ok else 2

def score_rc(lines, fns, data):
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        return report(*score(lines, fns, data), fns, data)

if __name__ == "__main__":
    fns, data = load_syms()
    if "--selftest" in sys.argv: sys.exit(selftest(fns, data))
    sys.exit(report(*score(open(sys.argv[1], errors="replace").read().splitlines(), fns, data), fns, data))
