#!/usr/bin/env python3
"""s7594 class SG: signal-disposition census.

Two lines of evidence:
  (1) source: every call to a signal-disposition / mask / raise API in the code we link (src/, librecomp, ultramodern,
      rt64/src minus tests/programs/tools/examples/demos), each matched to one classification row. Unmatched = OPEN.
  (2) binary: the signal APIs the game binary and its SDL3 dylib import (nm -u). Every imported API must be covered by a
      source row (game) or by a named external owner (SDL3). Unmatched import = OPEN.
The runtime third line is scratch/s7594/run.zsh ([s7594] disp lines + per-signal arms).

--controls: (a) a planted signal(SIGUSR1, ...) line in a temp copy must show up OPEN; (b) dropping one classification row
must turn its site OPEN; (c) a fake import must show up OPEN. rc 0 = 0 open and all controls fired.
"""
import os, re, subprocess, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = ["src", "lib/N64ModernRuntime/librecomp", "lib/N64ModernRuntime/ultramodern", "lib/rt64/src"]
SKIP = re.compile(r"/(tests?|programs|tools|examples?|doc|zlibWrapper)/|implot_demo|catch|Tests\.cpp|nfd_portal|"
                  r"mupen64plus-win32-deps|metal-cpp/Foundation/NSLock")
EXT = (".c", ".cpp", ".mm", ".m", ".h", ".hpp")
CALL = re.compile(r"(^|[^.>:_A-Za-z0-9])(signal|sigaction|sigprocmask|pthread_sigmask|sigaltstack|sigwait|sigsuspend|raise|"
                  r"kill|pthread_kill)\s*\(")

# (file suffix, substring of the line, signals, disposition / action, owner-reachable?)
ROWS = [
    ("src/main/main.cpp", "raise(SIGSEGV);", "SEGV", "ROGUESQ_PLANT_EXIT control only (s7450)", "no"),
    ("src/main/main.cpp", "o.sa_handler == SIG_DFL) sigaction(sg, &sa, nullptr);", "HUP,QUIT",
     "s7594 flag handler -> main tick -> save flush + quick_exit (=0 old: default terminate)", "yes"),
    ("src/main/main.cpp", "signal(SIGPIPE, SIG_IGN);", "PIPE", "s7594 ignore; async-stderr wr_all stops on EPIPE", "yes"),
    ("src/main/main.cpp", "signal(SIGTERM, SIG_DFL); fprintf(stderr, \"[s7594] plant", "TERM", "s7594 plant only", "no"),
    ("src/main/main.cpp", "pthread_sigmask(SIG_BLOCK, nullptr, &cur);", "-", "s7594 disposition dump: query only", "no"),
    ("src/main/main.cpp", "if (sigaction(s, nullptr, &o) != 0) continue;", "all", "s7594 disposition dump: query only", "no"),
    ("src/main/main.cpp", "sigaltstack(nullptr, &cur) == 0 && !(cur.ss_flags", "-", "s7355 altstack install (query)", "no"),
    ("src/main/main.cpp", "if (sigaltstack(&ss, nullptr) != 0)", "-", "s7355 altstack install", "no"),
    ("src/main/main.cpp", "if (sigaltstack(nullptr, &cur) != 0 ||", "-", "s7355 altstack teardown (query)", "no"),
    ("src/main/main.cpp", "if (sigaltstack(&off, nullptr) == 0)", "-", "s7355 altstack teardown", "no"),
    ("src/main/main.cpp", "signal(SIGABRT, [](int){", "ABRT", "_WIN32 only (not built on macOS)", "no"),
    ("src/main/main.cpp", "signal(sig, SIG_DFL);", "SEGV,BUS,ABRT", "crash handler re-raise with default (terminates)", "crash"),
    ("src/main/main.cpp", "raise(sig);", "SEGV,BUS,ABRT", "crash handler re-raise", "crash"),
    ("src/main/main.cpp", "sigaction(SIGSEGV, &sa, nullptr);", "SEGV", "crash reporter / wbw fault handler (s7355)", "crash"),
    ("src/main/main.cpp", "sigaction(SIGBUS, &sa, nullptr);", "BUS", "crash reporter / wbw fault handler (s7355)", "crash"),
    ("src/main/main.cpp", "sigaction(SIGABRT, &sa, nullptr);", "ABRT", "crash reporter", "crash"),
]
# imported API -> covered by game source rows or an external owner
IMPORT_OWNERS = {
    "_signal": "game rows (PIPE ignore, plant, crash re-raise)", "_sigaction": "game rows + SDL3 (INT/TERM -> SDL_QUIT)",
    "_sigaltstack": "game rows (s7355)", "_raise": "game rows", "_pthread_sigmask": "game dump + SDL3 (thread masks)",
    "_sys_signame": "game dump (data)",
}
IMPORT_RE = re.compile(r"^_(signal|sigaction|sigprocmask|pthread_sigmask|sigaltstack|raise|kill|pthread_kill|sigwait|sigsuspend|"
                       r"sys_signame)$")


def scan(root):
    hits = []
    for base in SCAN:
        for dp, dn, fn in os.walk(os.path.join(root, base)):
            for f in fn:
                if not f.endswith(EXT):
                    continue
                p = os.path.join(dp, f); rel = os.path.relpath(p, root)
                if SKIP.search("/" + rel):
                    continue
                try:
                    lines = open(p, errors="replace").read().split("\n")
                except OSError:
                    continue
                for i, ln in enumerate(lines, 1):
                    st = ln.strip()
                    if st.startswith("//") or st.startswith("*") or not CALL.search(ln):
                        continue
                    hits.append((rel, i, st))
    return hits


def classify(hits, rows):
    out = []
    for rel, i, st in hits:
        m = [r for r in rows if rel.endswith(r[0]) and r[1] in st]
        out.append((rel, i, st, m[0] if m else None))
    return out


def imports(binpath):
    try:
        o = subprocess.run(["nm", "-u", binpath], capture_output=True, text=True).stdout
    except OSError:
        return None
    return sorted({l.strip() for l in o.split("\n") if IMPORT_RE.match(l.strip())})


def report(root, rows, owners, extra_imports=(), quiet=False):
    cl = classify(scan(root), rows)
    opn = [c for c in cl if c[3] is None]
    used = {id(c[3]) for c in cl if c[3]}
    imp = imports(os.path.join(root, "build", "RogueSquadron64Recomp")) or []
    imp = sorted(set(imp) | set(extra_imports))
    imp_open = [s for s in imp if s not in owners]
    if not quiet:
        for rel, i, st, r in cl:
            print(f"{'OPEN' if r is None else 'ok  '} {rel}:{i} sig={r[2] if r else '?'} reach={r[4] if r else '?'} :: "
                  f"{r[3] if r else st[:90]}")
        for s in imp:
            print(f"{'OPEN' if s in imp_open else 'ok  '} import {s} :: {owners.get(s, '?')}")
        stale = [r for r in rows if id(r) not in used]
        for r in stale:
            print(f"note stale row (no site): {r[0]} {r[1][:50]}")
        print(f"[s7594-sg] sites={len(cl)} open={len(opn)} imports={len(imp)} imports_open={len(imp_open)}")
    return len(opn) + len(imp_open)


def controls():
    ok = 0
    tmp = tempfile.mkdtemp(prefix="s7594ctl")
    try:
        d = os.path.join(tmp, "src", "main"); os.makedirs(d)
        shutil.copy(os.path.join(ROOT, "src/main/main.cpp"), d)
        os.symlink(os.path.join(ROOT, "build"), os.path.join(tmp, "build"))
        with open(os.path.join(d, "main.cpp"), "a") as f:
            f.write("\nstatic void plant() { signal(SIGUSR1, SIG_IGN); }\n")
        a = report(tmp, ROWS, IMPORT_OWNERS, quiet=True)
        print(f"[ctl] planted site -> open={a} {'PASS' if a == 1 else 'FAIL'}"); ok += a == 1
    finally:
        shutil.rmtree(tmp)
    b = report(ROOT, [r for r in ROWS if "SIGPIPE" not in r[1]], IMPORT_OWNERS, quiet=True)
    print(f"[ctl] dropped PIPE row -> open={b} {'PASS' if b == 1 else 'FAIL'}"); ok += b == 1
    c = report(ROOT, ROWS, IMPORT_OWNERS, extra_imports=["_sigprocmask"], quiet=True)
    print(f"[ctl] fake import -> open={c} {'PASS' if c == 1 else 'FAIL'}"); ok += c == 1
    print(f"[s7594-sg] controls {ok}/3")
    return ok == 3


if __name__ == "__main__":
    n = report(ROOT, ROWS, IMPORT_OWNERS)
    c = controls() if "--controls" in sys.argv else True
    sys.exit(0 if n == 0 and c else 1)
