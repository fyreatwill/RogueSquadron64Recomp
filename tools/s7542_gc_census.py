#!/usr/bin/env python3
"""s7542 class GC census: every HOST-side write into guest RDRAM, classified by when it lands relative to the signal that
tells the guest about it.  Class GA (s7535: F5 LLE DMA after early sp_complete) and GB (s7538-s7541: RT64 fullSync after
dp_complete) were two instances; GC asks whether any other host writer lands in guest RAM after its signal (or with no
signal at all, while the guest runs) in a place the guest reads.

Write idioms (comments stripped), one site per match:
  memw   MEM_W/H/B/D(..) (op)=          memfn  memcpy/memmove/memset/std::copy/std::fill into rdram/RDRAM/TO_PTR
  idx    rdram[..] / RDRAM[..] (op)=     cast   *(T*)(rdram + ..) = / *reinterpret_cast<T*>(rdram + ..) =
  ptr    non-const T* p = &rdram[..] / rdram + .. / TO_PTR(..) (a guest pointer; writes through p belong to the function)
  field  TO_PTR(T, x)->f (op)= / ++ / --  (a store into a guest struct field)
  atomic __atomic_store/exchange/compare_exchange/fetch on an rdram pointer
  fbwb   copyNativeToRAM( call (RT64 colour/depth writeback)     dma  DO_DMA_WRITE / dma_dmem_to_rdram( (RSP DMEM->RDRAM)
  mq     TO_PTR(OSMesg, ..)[..] =  (message stored into a guest OSMesgQueue)
Classes (OK):
  H-before          the write completes before the message/flag that tells the guest (PI DMA, audio RSP task, drained RT64)
  H-guest-thread    runs on the guest thread inside a recompiled-call replacement (synchronous by construction); check:
                    the game imports the _recomp entry (nm -u libRecompiledFuncs.a) or the function is called only from one
  H-init            before the guest's first instruction (runtime init) or a mod/patch loader (none loaded in this port)
  H-late-noreader   lands after the signal, measured: no guest reader (s6938 + s7541_wbw_rwait WBW censuses)
  H-lever           an owner/test lever (env opt-in) that pokes a guest variable from a host thread by design; race audited
  H-latent-FIXED(opt-in)  late write with a measured consequence, fixed behind an owner opt-in (class GA)
  H-diag            only under a diagnostic / harness env (named in the check)
  H-def             the write primitive itself (ordering decided at its call sites, each classified separately)
  not-guest         the destination is host memory (e.g. RT64's rdramData shadow vector), not guest RDRAM
OPEN: H-late-reader (lands after the signal and the guest reads it).  UNCLASSIFIED / FAIL-check -> exit 1.

  python3 tools/s7542_gc_census.py             # rows + summary; exit 1 on FAIL / UNCLASSIFIED / OPEN
  python3 tools/s7542_gc_census.py --list      # bare site list
  python3 tools/s7542_gc_census.py --controls  # planted fixture, mutation controls, nm control, coverage control
"""
import os, re, sys, tempfile
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7538_gb_census as gb
import s7530_fw_census as fw
import s7533_fz_census as fz

REPO = gb.REPO
ROOTS = ["src/main", "src/rsp", "lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/librecomp/include/librecomp",
         "lib/N64ModernRuntime/ultramodern/src", "lib/rt64/src", "build/factor5_ucode"]
RD = r'(?:app->core\.RDRAM|rdram_ptr|rdram|RDRAM|TO_PTR\([^()]*\)|PTR\([^()]*\))'
OPW = r'\s*(?:[-+|&^]|<<|>>)?=(?!=)'
IDIOMS = [
    ("memw", r'\bMEM_[WHBD]\s*\((?:[^()]|\([^()]*\))*\)' + OPW),
    ("memfn", r'\b(?:std::)?(?:memcpy|memmove|memset|copy|fill)\s*\(\s*(?:\([^()]*\)\s*)?&?\s*' + RD + r'(?![\w.])'),
    ("mq", r'\bTO_PTR\(\s*OSMesg\s*,[^()]*\)\s*\[[^]]*\]' + OPW),
    ("idx", r'(?<![\w.>])' + RD + r'\s*\[[^]]*\]' + OPW),
    ("cast", r'\*\s*(?:\(\s*[\w:]+(?:\s*\*)+\s*\)|reinterpret_cast<[^>]*\*>)\s*\(\s*&?\s*' + RD + r'\s*[+\[][^;]*?\)' + OPW),
    ("ptr", r'(?<!const )\b[A-Za-z_][\w:]*\s*\*\s*\w+\s*=\s*(?:\([^()]*\)\s*|reinterpret_cast<[^>]*>\s*\(\s*)?&?\s*' + RD),
    ("field", r'\bTO_PTR\([^()]*\)\s*->\s*\w+(?:\.\w+|\[[^]]*\])*\s*(?:[-+|&^]?=(?!=)|\+\+|--)'),
    ("atomic", r'\b__atomic_(?:store_n|store|exchange_n|compare_exchange_n|fetch_\w+|\w+_fetch)\s*\(\s*&?\s*' + RD + r'\b'),
    ("fbwb", r'\bcopyNativeToRAM\s*\('),
    ("dma", r'\bDO_DMA_WRITE\s*\(|\bdma_dmem_to_rdram\s*\('),
]
PAT = re.compile("|".join("(?P<%s>%s)" % k for k in IDIOMS))
LIB = gb.LIB


def sites(path, over=None):
    t = gb.read(path, over or {})
    spans = fz.func_spans(t)
    out, seen = [], set()
    for m in PAT.finditer(t):
        kind = m.lastgroup
        ln = t.count("\n", 0, m.start()) + 1
        if (ln, kind) in seen:                      # one site per (line, idiom)
            continue
        seen.add((ln, kind))
        enc = [s for s in spans if s[0] <= m.start() <= s[1]]
        fn = enc[-1] if enc else (0, len(t), "<file>")
        out.append(dict(path=path, line=ln, kind=kind, fn=fn[2], body=t[fn[0]:fn[1] + 1], off=m.start() - fn[0], src="",
                        text=t[m.start():m.start() + 60].replace("\n", " ")))
    return out


gb.sites = sites                                    # reuse the GB census engine (classify / run_checks / census)

from s7542_gc_rules import RULES, OK                # noqa: E402  (rule table kept in its own module)
gb.OK = OK


def census(files, rules=None, over=None, lib=LIB, quiet=False):
    rows, st = gb.census(files, rules=RULES if rules is None else rules, over=over, lib=lib, quiet=True)
    st["open"] = sum(1 for r in rows if r[2] == "H-late-reader")
    if not quiet:
        for s, mode, cls, why, fails in rows:
            print("%s:%d %s [%s] %s -> %s%s" % (s["path"], s["line"], s["kind"], s["fn"], mode, cls,
                  ("  FAILED " + "; ".join(fails)) if fails else ""))
            if cls in ("H-late-reader", "FAIL-check", "UNCLASSIFIED"):
                print("      " + s["text"] + " | " + why[:300])
        print("summary: sites=%d rows=%d unclassified=%d fail=%d open=%d  %s" % (
            st["sites"], len(rows), st["unclassified"], st["fail"], st["open"], dict(Counter(r[2] for r in rows))))
    return rows, st


def files():
    return [f for f in gb.files_under(ROOTS) if not (f.startswith("build/") and not f.endswith(".c"))]


def controls():
    fl = files()
    tests = []
    with tempfile.TemporaryDirectory() as d:
        # 1 planted fixture: one write per idiom in an unknown function (+ a comment + a const read) -> 9 UNCLASSIFIED
        fx = os.path.join(d, "gc_fixture.cpp")
        open(fx, "w").write(
            "void gc_fake_writer(uint8_t* rdram) {\n // rdram[1] = 2; in a comment\n const uint8_t* q = rdram + 4;\n"
            " MEM_W(0, a) = 1;\n memcpy(rdram + 8, s, 4);\n TO_PTR(OSMesg, mq->msg)[0] = m;\n rdram[3 ^ 3] = 1;\n"
            " *reinterpret_cast<float*>(rdram + 16) = 1.0f;\n uint8_t* p = rdram + 32;\n"
            " __atomic_store_n(&rdram[40], 1, 0);\n copyNativeToRAM(&RDRAM[0], 1, 1);\n DO_DMA_WRITE(r7);\n}\n")
        rel = os.path.relpath(fx, REPO)
        rows, st = census([rel], quiet=True)
        kinds = sorted(r[0]["kind"] for r in rows)
        tests.append(("planted fixture: 9 idioms -> 9 UNCLASSIFIED sites, comment + const read skipped (%s)" % ",".join(kinds),
                      st["sites"] == 9 and st["unclassified"] == 9 and len(set(kinds)) == 9))
        # 2 mutation: PI rom read moved after its completion message -> the pi rom H-before row FAILs
        pip = "lib/N64ModernRuntime/librecomp/src/pi.cpp"
        src = open(os.path.join(REPO, pip), errors="replace").read()
        a = "            recomp::do_rom_read(rdram, rdram_address, physical_addr, size);\n"
        b = "            else ultramodern::enqueue_external_message_src(mq, s7398_msg, false, ultramodern::EventMessageSource::Pi);\n"
        mut = src.replace(a, "").replace(b, b + a) if a in src and b in src else src
        m2 = os.path.join(d, "pi_late.cpp"); open(m2, "w").write(mut)
        rows, _ = census(fl, over={pip: m2}, quiet=True)
        tests.append(("mutation: PI rom do_rom_read moved after its Pi message -> do_rom_read rom row FAIL-check",
                      mut != src and any(r[0]["fn"] == "do_rom_read" and r[1] == "rom" and r[2] == "FAIL-check" for r in rows)))
        # 3 mutation: an env gate removed from a diag writer -> that row FAILs
        mp = "src/main/main.cpp"
        msrc = open(os.path.join(REPO, mp), errors="replace").read()
        m3 = os.path.join(d, "main_nogate.cpp"); mm = msrc.replace('"ROGUESQ_FORCE_SEL"', '"X_REMOVED"')
        open(m3, "w").write(mm)
        rows, _ = census([mp], over={mp: m3}, quiet=True)
        tests.append(("mutation: FORCE_SEL gate renamed -> start_level_poller diag rows FAIL-check",
                      mm != msrc and any(r[0]["fn"] == "start_level_poller" and r[2] == "FAIL-check" for r in rows)))
        # 4 mutation: the audio task's run_task moved after sp_complete is not text-local; instead delete the drain in
        # rt64_render_context task_exit -> the drained-writeback H-before row FAILs
        rcp = gb.RC
        rsrc = open(os.path.join(REPO, rcp), errors="replace").read()
        m4 = os.path.join(d, "rc_nodrain.cpp"); rr = rsrc.replace("rdpq::drain(); if (rdpq::task_async)", "if (rdpq::task_async)")
        open(m4, "w").write(rr)
        rows, _ = census(fl, over={rcp: m4}, quiet=True)
        tests.append(("mutation: drain() removed from task_exit -> fullSync writeback 'drained' rows FAIL-check",
                      rr != rsrc and any(r[0]["fn"] == "fullSync" and r[1] == "drained" and r[2] == "FAIL-check" for r in rows)))
        # 5 delete a classified site's rule -> unclassified > 0
        rules2 = [r for r in RULES if not (r[0].endswith("cont.cpp") and r[1] == "osContGetReadData_recomp")]
        _, st5 = census(fl, rules=rules2, quiet=True)
        tests.append(("rule deleted (osContGetReadData_recomp) -> %d UNCLASSIFIED" % st5["unclassified"], st5["unclassified"] >= 5))
    # 6 nm control: a lib that no longer imports osContGetReadData -> guest-thread rows FAIL
    imp = gb.nm_imports(LIB)
    gb._nm["fakegc"] = imp - {"osContGetReadData_recomp"}
    rows, _ = census(fl, lib="fakegc", quiet=True)
    tests.append(("nm control: osContGetReadData_recomp not imported -> its guest-thread rows FAIL-check",
                  len(imp) > 100 and sum(1 for r in rows if r[0]["fn"] == "osContGetReadData_recomp" and r[2] == "FAIL-check") >= 5))
    # 7 coverage + live
    _, st0 = census(fl, rules=[], quiet=True)
    rows1, st1 = census(fl, quiet=True)
    tests.append(("coverage: rule-less census -> all %d sites UNCLASSIFIED" % st0["sites"],
                  st0["unclassified"] == st0["sites"] >= 80 and st1["sites"] == st0["sites"]))
    tests.append(("live census: 0 unclassified, 0 FAIL-check, 0 open", st1["unclassified"] == 0 and st1["fail"] == 0 and st1["open"] == 0))
    ok = 0
    for name, passed in tests:
        ok += passed
        print("%s  %s" % ("PASS" if passed else "FAIL", name))
    print("controls %d/%d" % (ok, len(tests)))
    return 0 if ok == len(tests) else 1


def main():
    if "--controls" in sys.argv:
        sys.exit(controls())
    if "--list" in sys.argv:
        for f in files():
            for s in sites(f):
                print("%s:%d %s [%s] %s" % (s["path"], s["line"], s["kind"], s["fn"], s["text"]))
        return
    _, st = census(files())
    sys.exit(1 if (st["unclassified"] or st["fail"] or st["open"]) else 0)


if __name__ == "__main__":
    main()
