#!/usr/bin/env python3
"""s7656 gate tracer: run a census tool as __main__ under a sys.addaudithook that records every file it OPENS for reading
and every directory it LISTS, so tools/s7651_gate_sweep.py can cache the tool's verdict keyed on exactly what it read.

Usage: RS64_GATE_TRACE=<out.json> gate_trace.py <tool.py> [args...]   (the tool's exit code and output pass through)
Trace JSON: {"reads": [...abs paths...], "dirs": [...], "globs": [...patterns...], "spawn": [argv0...], "complete": bool}
complete=False when the tool exited via os._exit or the trace could not be written; the sweep never caches those.
Each subprocess.Popen is recorded as {argv, cwd, env_ok, shell}; the sweep decides which spawns it can key (s7656: toolchain
binaries keyed on their file arguments, compilers also on the CC_PRINT_HEADERS header list) and leaves the rest uncacheable. Known gap: os.stat / os.path.exists raise no audit event, so a tool whose verdict depends only on whether a
path EXISTS (never opened, never listed) is invalidated only by its other inputs; the sweep's --no-cache re-proves everything."""
import json, os, runpy, sys

OUT = os.environ.pop("RS64_GATE_TRACE", None)
reads, dirs, globs, spawn = set(), set(), set(), []
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
        json.dump({"reads": sorted(reads), "dirs": sorted(dirs), "globs": sorted(globs), "spawn": spawn,
                   "complete": complete}, f)
    os.replace(tmp, OUT)


def main():
    tool = os.path.abspath(sys.argv[1])
    sys.argv = [tool] + sys.argv[2:]
    sys.path[0] = os.path.dirname(tool)
    reads.add(tool)
    sys.addaudithook(_hook)
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
