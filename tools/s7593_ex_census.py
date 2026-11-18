#!/usr/bin/env python3
"""s7593 class EX census: every process-exit route and exit-handler registration in the code linked into the game.

Scope: src/, lib/N64ModernRuntime, lib/rt64/src (same roots as tools/s7592_th_census.py), minus sources that are not linked
into the game binary (the N64Recomp / RSPRecomp / RecompModTool tool sources, xxHash cli, spirv-cross main + tests, SPIRV-Headers
tools, stb tests/deprecated, zstd docs). Windows-only blocks (#ifdef _WIN32 ... #else/#endif) are skipped.

Sites: exit / std::exit, _exit / _Exit, quick_exit, ULTRAMODERN_QUICK_EXIT, abort, atexit / at_quick_exit, SDL event
consumers (SDL_PollEvent / SDL_WaitEvent / SDL_PeepEvents), ultramodern::quit.
Verdicts:
  no-dtor       quick_exit / ULTRAMODERN_QUICK_EXIT: no static destruction; at_quick_exit handlers (async-stderr drain) run
  dtor-race     exit()/std::exit while host threads run: static destructors race the live threads (s5380: SIGABRT)
  fatal-exit    exit()/std::exit on a fatal path (EXIT_FAILURE, after assert(false) or a FATAL print): process is dying anyway,
                a destructor race can only turn rc 1 into 134; listed, not open
  startup       exit() before any host thread exists (SDL_Init / window creation failures)
  loses-stderr  _Exit/_exit with no rs64_stderr_async_restore() in the 6 lines before it: the lines still queued in async stderr
                (s6979, default on) are lost  <- the s7593 defect shape
  drained       _Exit/_exit preceded by rs64_stderr_async_restore()
  abort-handled abort(): the SIGABRT handler drains async stderr and prints the report
  handler       atexit / at_quick_exit registration; ANNOT names the handler and why it is bounded
  consumer      SDL event consumer; ANNOT says whether it consumes SDL_QUIT and on which thread
  plant         a gated test lever (ROGUESQ_*PLANT*)
  gated-old     the pre-fix behaviour, reachable only with an =0 env lever
  dead          defined but never called
  unknown       none of the above  -> exit 1
Exit nonzero on any unknown row or any default-path loses-stderr / dtor-race row. --controls classifies a planted file first and
re-classifies the pre-s7593 ultramodern error_handling.cpp (gate removed): it must come out loses-stderr.
"""
import os, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7591_mr_census import strip

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ["src", "lib/N64ModernRuntime", "lib/rt64/src"]
SKIP = re.compile(r"(/N64Recomp/(lib|src|RSPRecomp|RecompModTool|OfflineModRecomp|LiveRecomp)/|/test/|/tests/|tests-other/|gtest|gmock|/SDL|"
                  r"/mupen64plus-core/|/examples/|/zstd/(contrib|examples|programs|tests|doc)/|Tests\.cpp$|/tools/|/im3d/|/imgui/|"
                  r"/unit_tests/|/boost-[\d.]+/|/xxHash/(tests|cli)/|/spirv-cross/main\.cpp$|/stb/(deprecated|stb_image_resize_test)/)")
EXTS = (".c", ".cc", ".cpp", ".h", ".hpp", ".m", ".mm")
SITE = re.compile(r"(?<![\w.>:])(?P<k>(?:std::)?(?:exit|_exit|_Exit|quick_exit|abort|atexit|at_quick_exit))\s*\(|"
                  r"(?P<u>ULTRAMODERN_QUICK_EXIT)\s*\(|(?P<q>ultramodern::quit)\s*\(|(?P<sdl>SDL_(?:PollEvent|WaitEvent|PeepEvents))\s*\(")
# (file suffix, text on the site line, verdict, why) - read by hand.
ANNOT = [
    ("src/main/main.cpp", "SDL_PEEKEVENT, SDL_QUIT, SDL_QUIT", "consumer",
     "s7593 main-thread SDL_QUIT peek after SDL_PumpEvents (update_gfx); default on, ROGUESQ_S7593_MAINQUIT=0 = old"),
    ("src/main/main.cpp", "SDL_GETEVENT, SDL_FIRSTEVENT, SDL_LASTEVENT", "consumer",
     "poll_input drain on the guest's osContStartReadData thread; the only SDL_QUIT consumer before s7593"),
    ("src/main/main.cpp", "std::quick_exit(EXIT_SUCCESS);", "no-dtor", "rs64_s7593_quit_now: the user quit route"),
    ("src/main/main.cpp", 'if (pl == "exit") std::exit', "plant", "ROGUESQ_S7593_PLANT=exit restores the s5380 exit() route"),
    ("src/main/main.cpp", 'if (pl == "crash") std::at_quick_exit', "plant", "ROGUESQ_S7593_PLANT=crash"),
    ("src/main/main.cpp", 'if (pl == "hang") std::at_quick_exit', "plant", "ROGUESQ_S7593_PLANT=hang"),
    ("src/main/main.cpp", "std::_Exit(1);", "plant", "ROGUESQ_PLANT_EXIT_KIND=quick/silent (s7450 scorer plants)"),
    ("src/main/main.cpp", 'if (kind == "silent") std::_Exit(1);', "plant", "ROGUESQ_PLANT_EXIT_KIND=silent"),
    ("src/main/main.cpp", "ultramodern::error_handling::quick_exit(__FILE__, __LINE__, \"s7593_plant\"", "plant",
     "ROGUESQ_PLANT_EXIT_KIND=uquick (s7593 flood + real ULTRAMODERN exit)"),
    ("src/main/main.cpp", "    exit(EXIT_FAILURE);\n}", "plant", "ROGUESQ_PLANT_EXIT_KIND=switch mimics switch_error"),
    ("src/main/main.cpp", "SDL_Init failed", "startup", "create_gfx before the game thread starts"),
    ("src/main/main.cpp", "SDL_CreateWindow failed", "startup", "create_gfx before the game thread starts"),
    ("src/main/main.cpp", "s6979se::init(); std::atexit", "handler",
     "rs64_stderr_async_restore: drains <= 300 ms then dup2 (bounded); registered for both exit and quick_exit"),
    ("src/main/upstream_compat.cpp", "std::atexit(vi_boundary_summary)", "handler", "vi_boundary_summary: 8 fprintf lines"),
    ("src/main/upstream_compat.cpp", "std::at_quick_exit(vi_boundary_summary)", "handler", "same handler, quick_exit route"),
    ("src/rsp/dpc_bridge.cpp", "std::atexit(rs64_m4_y8000_atexit)", "handler", "rs64_m4_y8000_summary: bounded print, exit() route only"),
    ("ultramodern/src/error_handling.cpp", "std::quick_exit(exit_status);", "no-dtor",
     "s7593: Apple now quick_exits too (runs the async-stderr drain); ROGUESQ_S7593_UQ_EXIT=0 = old"),
    ("ultramodern/src/error_handling.cpp", "std::_Exit(exit_status);", "gated-old", "only with ROGUESQ_S7593_UQ_EXIT=0"),
    ("librecomp/src/recomp.cpp", "void ultramodern::quit()", "dead", "no caller in src/ or lib/: the main loop's `exited` never flips"),
    ("librecomp/src/recomp.cpp", "exit(EXIT_FAILURE);", "fatal-exit", "cop0 status / switch_error / do_break after assert(false)"),
    ("librecomp/src/overlays.cpp", "std::exit(EXIT_FAILURE);", "fatal-exit", "overlay unload mismatch / missing function after assert(false)"),
    ("librecomp/src/overlays.cpp", "std::abort", "abort-handled", "fatal overlay path"),
    ("src/main/main.cpp", "abort();", "abort-handled", "FATAL prints then abort (calloc failure, syscall reached)"),
    ("thirdparty/json/json.hpp", "std::abort", "abort-handled", "JSON_THROW without exceptions"),
    ("contrib/json/json.hpp", "std::abort", "abort-handled", "JSON_THROW without exceptions"),
    ("sse2neon/sse2neon.h", "abort", "abort-handled", "unreachable intrinsic fallback"),
    ("spirv-cross/spirv_common.hpp", "abort", "abort-handled", "SPIRV_CROSS_THROW without exceptions"),
    ("spirv-cross/spirv_cross_error_handling.hpp", "abort", "abort-handled", "SPIRV_CROSS_THROW without exceptions"),
    ("jsoncpp/dist/json/json.h", "abort", "abort-handled", "assert macro"),
    ("ultramodern/include/ultramodern/error_handling.hpp", "", "no-dtor", "ULTRAMODERN_QUICK_EXIT macro / declaration"),
    ("ultramodern/src/error_handling.cpp", "void ultramodern::error_handling::quick_exit", "no-dtor", "definition"),
    ("xxHash/cli/xsum_os_specific.c", "abort", "abort-handled", "cli helper (not called by the game)"),
]

def win32_mask(raw):
    """set of line numbers inside an `#ifdef _WIN32` / `#if defined(_WIN32)` branch (until #else/#elif/#endif at depth 0)"""
    out, stack = set(), []
    for i, ln in enumerate(raw.split("\n"), 1):
        t = ln.strip()
        if re.match(r"#\s*if", t):
            stack.append(bool(re.match(r"#\s*if(def\s+_WIN32\b|\s+defined\s*\(\s*_WIN32\s*\)\s*$)", t)))
        elif re.match(r"#\s*(else|elif)", t) and stack: stack[-1] = False
        elif re.match(r"#\s*endif", t) and stack: stack.pop()
        elif any(stack): out.add(i)
    return out

def classify(path, raw):
    s = strip(raw); lines = raw.split("\n"); win = win32_mask(raw); rows = []
    for m in SITE.finditer(s):
        ln = raw.count("\n", 0, m.start()) + 1
        if ln in win: continue
        k = m.group("k") or m.group("u") or m.group("q") or m.group("sdl")
        text = lines[ln - 1]; ctx = "\n".join(lines[max(0, ln - 2):ln + 1]); before = "\n".join(lines[max(0, ln - 7):ln - 1])
        verdict, why = "unknown", ""
        hit = [a for a in ANNOT if path.endswith(a[0]) and a[1] in text] or \
              [a for a in ANNOT if path.endswith(a[0]) and a[1] and a[1] in ctx]  # the site line first, then +-1 line
        if hit: verdict, why = hit[0][2], hit[0][3]
        if verdict == "gated-old" and "ROGUESQ_" not in before: verdict, why = "unknown", ""  # the gate must really be there
        if verdict == "unknown":
            base = k.replace("std::", "")
            if base in ("quick_exit",) or m.group("u"): verdict, why = "no-dtor", "quick_exit route"
            elif base in ("_Exit", "_exit"):
                verdict = "drained" if "rs64_stderr_async_restore" in before else "loses-stderr"
            elif base == "abort": verdict = "abort-handled"
            elif base == "exit" and "EXIT_FAILURE" in text and ("assert(false)" in before or "FATAL" in before):
                verdict, why = "fatal-exit", "assert(false)/FATAL precedes"
            elif base == "exit": verdict = "dtor-race"
        rows.append((path, ln, k, verdict, why))
    return rows

def walk():
    rows = []
    for d in DIRS:
        for root, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(root, f); rel = os.path.relpath(p, ROOT)
                if not f.endswith(EXTS) or SKIP.search("/" + rel): continue
                rows += classify(rel, open(p, errors="replace").read())
    return rows

CTRL = """#include <cstdlib>
void a() { start_threads(); std::exit(0); }
void b() { std::quick_exit(0); }
void c() { std::_Exit(1); }
void d() { rs64_stderr_async_restore();
  std::_Exit(2); }
void e() { abort(); }
void f() { fprintf(stderr, "FATAL x\\n");
  exit(EXIT_FAILURE); }
#ifdef _WIN32
void g() { _Exit(3); }
#else
void h() { _exit(4); }
#endif
void i() { ULTRAMODERN_QUICK_EXIT(); }
"""
CTRL_EXPECT = ["dtor-race", "no-dtor", "loses-stderr", "drained", "abort-handled", "fatal-exit", "loses-stderr", "no-dtor"]

def controls():
    got = [r[3] for r in classify("ctrl.cpp", CTRL)]
    ok = got == CTRL_EXPECT
    eh = os.path.join(ROOT, "lib/N64ModernRuntime/ultramodern/src/error_handling.cpp"); t = open(eh).read()
    if "// ROGUESQ s7593" in t:
        pre = t[:t.index("    // ROGUESQ s7593")] + t[t.index("    std::_Exit(exit_status);"):]
        v = [r[3] for r in classify("lib/N64ModernRuntime/ultramodern/src/error_handling.cpp", pre) if "_Exit" in r[2]]
        print(f"pre-s7593 error_handling _Exit: {v}"); ok = ok and v == ["loses-stderr"]
    print(f"controls: {sum(g == e for g, e in zip(got, CTRL_EXPECT))}/{len(CTRL_EXPECT)} {'PASS' if ok else 'FAIL'} got={got}")
    return ok

def main():
    ok = controls() if "--controls" in sys.argv else True
    rows = walk(); from collections import Counter
    c = Counter(r[3] for r in rows)
    for r in rows:
        if "-v" in sys.argv or r[3] in ("unknown", "loses-stderr", "dtor-race"):
            print(f"{r[0]}:{r[1]} {r[2]} {r[3]} {r[4]}")
    openr = [r for r in rows if r[3] in ("unknown", "loses-stderr", "dtor-race")]
    print("rows=%d %s open=%d" % (len(rows), " ".join(f"{k}={v}" for k, v in sorted(c.items())), len(openr)))
    sys.exit(0 if ok and not openr else 1)

if __name__ == "__main__":
    main()
