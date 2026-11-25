#!/usr/bin/env python3
"""s7954 class CK census: no interval, deadline or pacing decision in the game process may read the WALL clock.

Why: the wall clock (time(), gettimeofday, CLOCK_REALTIME, std::chrono::system_clock) steps when NTP corrects it, when the
owner changes the time zone/DST is irrelevant (UTC) but a manual set or a sleep/wake resync is not. A VI deadline, present
pacing wait or freeze detector computed from it would stall (backward step) or burst (forward step) for the size of the
step. Monotonic sources (steady_clock, mach_absolute_time, CLOCK_MONOTONIC/UPTIME_RAW, SDL_GetTicks/PerformanceCounter,
CLOCK_THREAD_CPUTIME_ID) are immune.

Lines of evidence:
 1. WITNESS: compile a probe with the build's own CMAKE_CXX_COMPILER (build/CMakeCache.txt) and check
    std::chrono::high_resolution_clock IS steady_clock (libc++ aliases it when a monotonic clock exists). ultramodern's VI
    deadline (events.cpp) and RT64's present pacing (rt64_timer.cpp) use high_resolution_clock, so this one fact decides
    whether ~40 pacing sites are monotonic. If the alias ever fails, every high_resolution_clock site is reclassified WALL.
 2. SOURCE scan of src/, lib/N64ModernRuntime/{librecomp,ultramodern}, lib/rt64/src (minus contrib) and the live
    ../N64Recomp/RecompiledFuncs (fixup-injected diagnostics): every WALL call must match a REVIEWED row (file, substring)
    whose class is LABEL (printed timestamp only), CADENCE (diag dump throttle in an env-gated instrument) or ARM (env==2
    A/B arm alternation, opt-in). Unreviewed WALL = OPEN.
 3. OBJECT imports (nm -u of build/*.a members): every object importing a wall symbol (_time, _gettimeofday,
    system_clock::now, condition_variable::__do_timed_wait<system_clock>) must be explained by line 2 (reviewed sites), by
    a condition_variable wait (libc++ on Apple routes wait_for through system_clock; Darwin libpthread converts the absolute
    deadline back to a relative kernel timeout at entry, so only a step inside that sub-us window matters: single-source,
    source reading), or by REVIEWED_OBJ (contrib zip timestamps, demo code).
Controls (always): planted `std::chrono::system_clock::now()` source line -> OPEN; dropping one REVIEWED row -> its sites
OPEN; witness mutation (pretend high_resolution_clock is not steady) -> pacing sites reclassified WALL -> OPEN; planted
object import of _gettimeofday in an unexplained object -> OPEN. Exit 1 on any open row or failed control.
"""
import os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = ["src", "lib/N64ModernRuntime/librecomp", "lib/N64ModernRuntime/ultramodern", "lib/rt64/src"]
RECOMP = os.path.normpath(os.path.join(ROOT, "..", "N64Recomp", "RecompiledFuncs"))
EXTS = (".c", ".cc", ".cpp", ".h", ".hpp", ".mm", ".m", ".inl")
STR = re.compile(r'"(?:[^"\\]|\\.)*"')
WALL = re.compile(r"\bsystem_clock\b|\bgettimeofday\s*\(|\bCLOCK_REALTIME\b|\bCFAbsoluteTimeGetCurrent\b|\bNSDate\b|"
                  r"(?<![\w.>])time\s*\(\s*(?:NULL|nullptr|0|)\s*\)|\bclock\s*\(\s*\)")
HRC = re.compile(r"\bhigh_resolution_clock\b")
MONO = re.compile(r"\bsteady_clock\b|\bmach_absolute_time\b|\bCLOCK_MONOTONIC(?:_RAW)?\b|\bCLOCK_UPTIME_RAW\b|"
                  r"\bSDL_GetTicks(?:NS)?\b|\bSDL_GetPerformanceCounter\b|\bCLOCK_THREAD_CPUTIME_ID\b|\bmach_wait_until\b")
CVWAIT = re.compile(r"\.wait_for\s*\(|\.wait_until\s*\(")
GETTOD_RECOMP = re.compile(r"\bgettimeofday\b")

# (file, substring) -> (class, reason). Substrings are matched against the comment/string-stripped line.
REVIEWED = {
    ("src/main/main.cpp", "rs64_s7593_epoch()"): ("LABEL", "s7593 quit/poll log 'wall=' epoch, printed only"),
    ("src/main/upstream_compat.cpp", "run start pid="): ("LABEL", "s6892 log header timestamp"),
    ("src/rsp/s7095_dpc_model.cpp", "time_t t = time(nullptr)"): ("CADENCE", "ROGUESQ_S7095_DPC 5 s dump"),
    ("src/rsp/s7097_edit_census.cpp", "time_t t = time(nullptr)"): ("CADENCE", "ROGUESQ_S7097_EDIT 5 s dump"),
    ("src/rsp/s7096_fwd_cover.cpp", "time_t t = time(nullptr)"): ("CADENCE", "ROGUESQ_S7096_FWD 5 s dump"),
    ("src/rsp/s7526_v2p_twin.cpp", "time_t t = time(nullptr)"): ("CADENCE", "ROGUESQ_S7526_TWIN 5 s dump"),
    ("src/rsp/s7523_slow_rdp.cpp", "time_t t = time(nullptr)"): ("CADENCE", "ROGUESQ_S7523_SLOWRDP 5 s dump"),
    ("src/rsp/s7535_ga_chk.cpp", "const time_t now = time(nullptr)"): ("CADENCE", "ROGUESQ_S7535_GA_CHK 5 s dump"),
    ("src/rsp/s7324_rcp_spill.cpp", "const time_t now = time(nullptr)"): ("CADENCE", "rs64_s7324_on==2 per-second control"),
    ("src/rsp/s7094_dma_shape.cpp", "const time_t now = time(nullptr)"): ("CADENCE", "ROGUESQ_S7094_DMASHAPE 5 s dump"),
    ("src/rsp/dpc_bridge.cpp", "== 2 ? (int)((time(nullptr) / 10) & 1)"): ("ARM", "env==2 10 s A/B alternation (trim/tmem/lbfast/pcache/hgather/batch/cdiag)"),
    ("src/rsp/dpc_bridge.cpp", "== 2 ? ((time(nullptr) / 10) & 1) != 0"): ("ARM", "env==2 10 s A/B alternation (wm/walk/coal)"),
    ("src/rsp/dpc_bridge.cpp", "== 2 ? (bool)((time(nullptr) / 10) & 1)"): ("ARM", "env==2 10 s A/B alternation (rstat)"),
    ("lib/rt64/src/gbi/rt64_gbi_rdp.cpp", "std::chrono::system_clock::now().time_since_epoch()).count()"): ("ARM", "ROGUESQ_SEAM_TOG / s_mode==2 arm alternation"),
    ("lib/rt64/src/hle/rt64_rdp.cpp", "const time_t now = time(nullptr)"): ("CADENCE", "[g1e-lrep] per-second census print"),
    ("lib/rt64/src/hle/rt64_rdp_tmem.cpp", "const time_t now = time(nullptr)"): ("CADENCE", "tmem provenance/scan per-second prints"),
    ("lib/rt64/src/hle/rt64_rdp_tmem.cpp", "== 2) ? int((time(nullptr) / 10) & 1)"): ("ARM", "env==2 10 s A/B alternation (tscan/mode)"),
    ("RecompiledFuncs", "extern long time(long*)"): ("LABEL", "ROGUESQ_LOG_HUDBIT log timestamps (fixup-injected)"),
    ("RecompiledFuncs", "gettimeofday"): ("LABEL", "ROGUESQ_LOG_HUDBIT log timestamps (fixup-injected)"),
}
# objects whose wall-symbol import is explained without a first-party source site
REVIEWED_OBJ = {"miniz_zip.c.o": "zip entry mtime", "miniz.c.o": "zip entry mtime", "implot_demo.cpp.o": "ImPlot demo (never shown)"}
WALL_SYMS = ("_time", "_gettimeofday", "__ZNSt3__16chrono12system_clock3nowEv", "__do_timed_wait")
WITNESS_SRC = r'''#include <chrono>
#include <type_traits>
#include <cstdio>
int main(){ printf("hrc_is_steady_clock=%d hrc_is_steady=%d system_is_steady=%d\n",
 (int)std::is_same<std::chrono::high_resolution_clock,std::chrono::steady_clock>::value,
 (int)std::chrono::high_resolution_clock::is_steady,(int)std::chrono::system_clock::is_steady); }
'''


def strip(line):
    line = STR.sub('""', line)
    i = line.find("//")
    return line if i < 0 else line[:i]


def witness():
    cxx = "/usr/bin/c++"
    try:
        for l in open(os.path.join(ROOT, "build", "CMakeCache.txt")):
            if l.startswith("CMAKE_CXX_COMPILER:"):
                cxx = l.split("=", 1)[1].strip()
    except OSError:
        pass
    with tempfile.TemporaryDirectory() as td:
        src, exe = os.path.join(td, "w.cpp"), os.path.join(td, "w")
        open(src, "w").write(WITNESS_SRC)
        r = subprocess.run([cxx, "-std=c++20", src, "-o", exe], capture_output=True, text=True)
        if r.returncode:
            return None, cxx, r.stderr.strip()[:200]
        out = subprocess.run([exe], capture_output=True, text=True).stdout.strip()
    d = dict(kv.split("=") for kv in out.split())
    return d, cxx, out


def files():
    out = []
    for d in SCAN:
        for dp, dn, fn in os.walk(os.path.join(ROOT, d)):
            dn[:] = [x for x in dn if x != "contrib"]
            out += [(os.path.relpath(os.path.join(dp, f), ROOT), os.path.join(dp, f)) for f in fn if f.endswith(EXTS)]
    if os.path.isdir(RECOMP):
        out += [("RecompiledFuncs/" + f, os.path.join(RECOMP, f)) for f in sorted(os.listdir(RECOMP)) if f.endswith(".c")]
    return sorted(out)


def load():
    items = []
    for rel, p in files():
        try:
            items.append((rel, open(p, errors="replace").read()))
        except OSError:
            pass
    return items


def scan(items, reviewed, hrc_steady):
    rows, mono, cv, hits = [], 0, 0, {k: 0 for k in reviewed}
    srcwall = set()
    for rel, txt in items:
        key_file = "RecompiledFuncs" if rel.startswith("RecompiledFuncs/") else rel
        for n, raw in enumerate(txt.splitlines(), 1):
            if rel.startswith("RecompiledFuncs/") and "time" not in raw:
                continue
            line = strip(raw) if not rel.startswith("RecompiledFuncs/") else raw
            w = WALL.search(line) or (not hrc_steady and HRC.search(line))
            if rel.startswith("RecompiledFuncs/") and not w and GETTOD_RECOMP.search(line):
                w = True
            if not rel.startswith("RecompiledFuncs/"):
                mono += len(MONO.findall(line)) + (len(HRC.findall(line)) if hrc_steady else 0)
                cv += len(CVWAIT.findall(line))
            if not w:
                continue
            srcwall.add(os.path.basename(rel))
            k = next((k for k in reviewed if k[0] == key_file and k[1] in raw and (k[0] != "RecompiledFuncs" or "ROGUESQ_LOG_HUDBIT" in raw)), None)  # generated diag lines must carry their env gate
            if k:
                hits[k] += 1
            rows.append((rel, n, reviewed[k][0] if k else "OPEN", raw.strip()[:150]))
    return rows, mono, cv, hits, srcwall


def objects():
    """(member, [wall syms]) for every build/*.a member importing a wall symbol."""
    res = []
    b = os.path.join(ROOT, "build")
    archives = []
    for dp, dn, fn in os.walk(b):
        dn[:] = [x for x in dn if not x.startswith(("RogueSquadron64Recomp_", "build_")) and x != "CMakeFiles"]
        archives += [os.path.join(dp, f) for f in fn if f.endswith(".a")]
    for a in sorted(archives):
        r = subprocess.run(["nm", "-A", "-u", a], capture_output=True, text=True)
        per = {}
        for l in r.stdout.splitlines():
            m = re.match(r".*?:([^:]+\.o):\s+(\S+)$", l.strip())
            if not m:
                continue
            sym = m.group(2)
            if sym in WALL_SYMS[:3] or (WALL_SYMS[3] in sym and "system_clock" in sym):
                per.setdefault(m.group(1), set()).add(sym if "__do_timed_wait" not in sym else "cv_timed_wait<system_clock>")
        res += [(os.path.relpath(a, b) + ":" + o, sorted(s)) for o, s in per.items()]
    return res


def classify_objects(objs, srcwall, cvsrc):
    out = []
    for name, syms in objs:
        o = name.rsplit(":", 1)[1]
        src = o[:-2]  # foo.cpp.o -> foo.cpp
        if o in REVIEWED_OBJ:
            why = "REVIEWED_OBJ " + REVIEWED_OBJ[o]
        elif src in srcwall:
            why = "source sites"
        elif set(syms) <= {"__ZNSt3__16chrono12system_clock3nowEv", "cv_timed_wait<system_clock>"} and src in cvsrc:
            why = "CVWAIT"
        else:
            why = "OPEN"
        out.append((name, syms, why))
    return out


def summarize(items, reviewed, hrc_steady):
    rows, mono, cv, hits, srcwall = scan(items, reviewed, hrc_steady)
    return rows, mono, cv, hits, srcwall, sum(1 for r in rows if r[2] == "OPEN")


def main():
    items = load()
    cvsrc = {os.path.basename(rel) for rel, txt in items if not rel.startswith("RecompiledFuncs/") and CVWAIT.search(txt)}
    cvsrc |= {"plume_metal.cpp"} if os.path.exists(os.path.join(ROOT, "lib/rt64/src/contrib/plume/plume_metal.cpp")) and \
        CVWAIT.search(open(os.path.join(ROOT, "lib/rt64/src/contrib/plume/plume_metal.cpp"), errors="replace").read()) else set()
    w, cxx, wout = witness()
    hrc_steady = bool(w) and w.get("hrc_is_steady_clock") == "1" and w.get("hrc_is_steady") == "1"
    wit_ok = bool(w) and hrc_steady and w.get("system_is_steady") == "0"
    print(f"WITNESS cxx={cxx} {wout} {'PASS' if wit_ok else 'FAIL'}")
    rows, mono, cv, hits, srcwall, nopen = summarize(items, REVIEWED, hrc_steady)
    for r in rows:
        if r[2] == "OPEN" or "-v" in sys.argv:
            print(f"  {r[2]:7s} {r[0]}:{r[1]}: {r[3]}")
    unused = [k for k, v in hits.items() if v == 0]
    for k in unused:
        print(f"  STALE reviewed row (0 sites): {k}")
    by = {}
    for r in rows:
        by[r[2]] = by.get(r[2], 0) + 1
    raw_objs = objects()
    objs = classify_objects(raw_objs, srcwall, cvsrc)
    for name, syms, why in objs:
        if why == "OPEN" or "-v" in sys.argv:
            print(f"  OBJ {why:13s} {name} {','.join(syms)}")
    oopen = sum(1 for o in objs if o[2] == "OPEN")
    # controls
    plant = items + [("src/main/s7954_plant.cpp", "auto t0 = std::chrono::system_clock::now();\n")]
    c1 = summarize(plant, REVIEWED, hrc_steady)[5] == nopen + 1
    k0 = ("src/rsp/dpc_bridge.cpp", "== 2 ? (int)((time(nullptr) / 10) & 1)")
    drop = {k: v for k, v in REVIEWED.items() if k != k0}
    c2 = summarize(items, drop, hrc_steady)[5] == nopen + hits.get(k0, 0) and hits.get(k0, 0) > 0
    hrc_sites = sum(len(HRC.findall(strip(l))) for rel, t in items if not rel.startswith("RecompiledFuncs/") for l in t.splitlines())
    c3n = summarize(items, REVIEWED, False)[5] - nopen
    c3 = c3n > 0
    c4 = sum(1 for o in classify_objects(objects_plant(raw_objs), srcwall, cvsrc) if o[2] == "OPEN") == oopen + 1
    print(f"CONTROL planted_source={'FIRED' if c1 else 'DARK'} drop_reviewed={'FIRED' if c2 else 'DARK'} "
          f"hrc_not_steady={'FIRED' if c3 else 'DARK'}(+{c3n}) planted_object={'FIRED' if c4 else 'DARK'} "
          f"{'PASS' if c1 and c2 and c3 and c4 else 'FAIL'}")
    print(f"SUMMARY mono_sites={mono} hrc_sites={hrc_sites} cv_waits={cv} wall_sites={len(rows)} "
          + " ".join(f"{k}={v}" for k, v in sorted(by.items()))
          + f" open={nopen} stale={len(unused)} wall_objects={len(objs)} obj_open={oopen}")
    ok = wit_ok and nopen == 0 and not unused and oopen == 0 and c1 and c2 and c3 and c4
    print("VERDICT " + ("CLOSED" if ok else "RED"))
    return 0 if ok else 1


def objects_plant(objs):
    return list(objs) + [("libplanted.a:s7954_unexplained.cpp.o", ["_gettimeofday"])]


if __name__ == "__main__":
    sys.exit(main())
