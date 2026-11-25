#!/usr/bin/env python3
"""s7656 gate tracer: run a census tool as __main__ under a sys.addaudithook that records every file it OPENS for reading
and every directory it LISTS, so tools/s7651_gate_sweep.py can cache the tool's verdict keyed on exactly what it read.

Usage: RS64_GATE_TRACE=<out.json> gate_trace.py <tool.py> [args...]   (the tool's exit code and output pass through)
Trace JSON: {"reads": [...abs paths...], "dirs": [...], "globs": [...patterns...], "spawn": [argv0...], "complete": bool}
complete=False when the tool exited via os._exit or the trace could not be written; the sweep never caches those.
Each subprocess.Popen is recorded as {argv, cwd, env_ok, shell}; the sweep decides which spawns it can key (s7656: toolchain
binaries keyed on their file arguments, compilers also on the CC_PRINT_HEADERS header list) and leaves the rest uncacheable.
s7934: os.stat / os.lstat raise no audit event, so a tool whose verdict depended only on whether a path EXISTS (or its size)
was invalidated only by its other inputs and its path was not manifest-protected. Both are now wrapped (genericpath's
exists/isfile/isdir/getsize and pathlib call them through the os module); paths land in "stats", keyed by the sweep on
existence/type/size. importlib uses posix.stat directly, so module lookup does not flood the list. `--selftest` = controls."""
import json, os, runpy, sys

OUT = os.environ.pop("RS64_GATE_TRACE", None)
reads, dirs, globs, stats, spawn = set(), set(), set(), set(), []
SKIP = tuple(p for p in {sys.prefix, sys.base_prefix, sys.exec_prefix, os.path.dirname(os.__file__)} if p)


def _hook(ev, args):
    try:
        if ev == "open":
            path, mode = args[0], args[1]
            if isinstance(path, int):
                return
            if isinstance(mode, str):
                if any(c in mode for c in "wax+"):
                    return
            elif isinstance(args[2], int) and args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT):
                return
            p = os.path.abspath(os.fsdecode(path))
            if p.endswith(".pyc"):
                # s7865: a module loaded by importlib.util.spec_from_file_location (s7633 -> s7632_dd_census.py) is not in
                # sys.modules, so _module_sources misses it and only its .pyc is opened: record the .py the .pyc caches.
                d, b = os.path.split(p)
                if os.path.basename(d) == "__pycache__":
                    p = os.path.join(os.path.dirname(d), b.split(".")[0] + ".py")
                else:
                    return
            if not p.startswith(SKIP):
                reads.add(p)
        elif ev in ("os.listdir", "os.scandir"):
            p = args[0] if args and args[0] is not None else "."
            if not isinstance(p, int):
                dirs.add(os.path.abspath(os.fsdecode(p)))
        elif ev == "glob.glob":
            globs.add(os.path.abspath(os.fsdecode(args[0])))
        elif ev == "subprocess.Popen":
            exe, argv, cwd, env = args
            argv = [argv] if isinstance(argv, (str, bytes)) else list(argv)
            argv = [os.fsdecode(a) if isinstance(a, bytes) else str(a) for a in argv]
            env_ok = env is None or "CC_PRINT_HEADERS_FILE" in env or b"CC_PRINT_HEADERS_FILE" in env
            spawn.append({"argv": argv, "cwd": os.path.abspath(os.fsdecode(cwd)) if cwd else os.getcwd(),
                          "env_ok": env_ok, "shell": isinstance(args[1], (str, bytes))})
        elif ev in ("os.system", "os.posix_spawn", "os.exec", "os.spawn"):
            spawn.append({"argv": ["<" + ev + ">"], "cwd": os.getcwd(), "env_ok": False, "shell": True})
    except Exception:  # never let tracing change the tool's behaviour
        pass


def _wrap_stat(name):
    """s7934: record every path the tool stats (exists/isfile/getsize/Path.exists); pass everything through unchanged."""
    orig = getattr(os, name)

    def w(path, *a, **k):
        try:
            if not isinstance(path, int) and k.get("dir_fd") is None:
                p = os.path.abspath(os.fsdecode(path))
                if not p.startswith(SKIP):
                    stats.add(p)
        except Exception:
            pass
        return orig(path, *a, **k)
    for sset in (os.supports_dir_fd, os.supports_fd, os.supports_follow_symlinks):
        if orig in sset:
            sset.add(w)  # keep shutil.rmtree's fd-based path and follow_symlinks checks behaving as before
    setattr(os, name, w)


def _module_sources():
    """s7678: an import served from a valid __pycache__ opens only the .pyc (skipped above), never the .py, so a rows
    module edit (s7600_gx_rows.py) left the census's cached RED in place. Record every loaded non-stdlib module's source."""
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if f and f.endswith(".py"):
            p = os.path.abspath(f)
            if not p.startswith(SKIP):
                reads.add(p)


def _dump(complete):
    if not OUT:
        return
    _module_sources()
    tmp = OUT + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"reads": sorted(reads), "dirs": sorted(dirs), "globs": sorted(globs), "stats": sorted(stats - reads), "spawn": spawn,
                   "complete": complete}, f)
    os.replace(tmp, OUT)


def selftest():
    """Planted stat-only tool: its path must land in stats (not reads); a tool that opens the file lands it in reads only;
    mutation = a run with the wrapper skipped records nothing."""
    import subprocess, tempfile
    ok = True
    with tempfile.TemporaryDirectory() as d:
        tgt = os.path.join(d, "probe.bin")
        open(tgt, "w").write("x")
        arms = [("exists", "import os,sys; sys.exit(0 if os.path.exists(%r) else 1)" % tgt, "stats"),
                ("getsize", "import os; print(os.path.getsize(%r))" % tgt, "stats"),
                ("pathlib", "import pathlib; print(pathlib.Path(%r).is_file())" % tgt, "stats"),
                ("open", "print(open(%r).read())" % tgt, "reads"),
                ("mutation", "import os; print(os.path.exists(%r))" % tgt, None)]
        for name, code, want in arms:
            tool, out = os.path.join(d, "arm_" + name + ".py"), os.path.join(d, name + ".json")  # arm_: "pathlib.py" shadowed the stdlib
            open(tool, "w").write(code + "\n")
            env = dict(os.environ, RS64_GATE_TRACE=out)
            if want is None:
                env["RS64_GATE_TRACE_NOSTAT"] = "1"
            subprocess.run([sys.executable, os.path.abspath(__file__), tool], env=env, capture_output=True)
            t = json.load(open(out))
            where = [k for k in ("reads", "stats") if tgt in t.get(k, [])]
            good = where == ([want] if want else [])
            ok &= good
            print(f"CONTROL s7934 {name}: {tgt.split('/')[-1]} in {where or 'nothing'} (want {want or 'nothing'}) {'PASS' if good else 'FAIL'}")
    print("CONTROLS PASS" if ok else "CONTROLS FAIL")
    return 0 if ok else 1


def main():
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    tool = os.path.abspath(sys.argv[1])
    sys.argv = [tool] + sys.argv[2:]
    sys.path[0] = os.path.dirname(tool)
    reads.add(tool)
    sys.addaudithook(_hook)
    if not os.environ.pop("RS64_GATE_TRACE_NOSTAT", None):
        for n in ("stat", "lstat"):
            _wrap_stat(n)
    rc = 0
    try:
        runpy.run_path(tool, run_name="__main__")
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else (print(e.code, file=sys.stderr) or 1))
    except BaseException:
        import traceback
        traceback.print_exc()
        rc = 1
    _dump(True)
    sys.exit(rc)


if __name__ == "__main__":
    main()
