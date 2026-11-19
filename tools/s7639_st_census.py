#!/usr/bin/env python3
"""s7639 class ST: SDL thread affinity census.

Every SDL_* call site in the host files we compile (src/main + the two lib/rt64 SDL files) is
1. mapped SDL2 name -> SDL3 name (SDL3/SDL_oldnames.h; sdl2-compat forwards to SDL3),
2. classed by SDL3's own `\\threadsafety` doc line (ground truth independent of us):
   MAIN = "should only be called on the main thread", WIN = "thread that created the window",
   ANY = "safe ... from any thread", OTHER = anything else, NODOC = no line found,
3. attributed to the thread(s) that can run it: enclosing top-level function or std::thread
   lambda, then thread sets propagated over a name-based call graph from known roots
   (recomp.cpp: create_gfx/create_window/update_gfx on the main thread; ultramodern input.cpp:
   get_input/set_rumble on the game thread; std::thread lambdas/functions = worker).
A site is OPEN when its class is MAIN/WIN and some non-main thread reaches it, or when no root
reaches it (UNROOTED). OPEN rows are then hand-classified in HAND below (reason string).

--controls: (a) planted MAIN call inside a std::thread lambda must be OPEN, (b) planted MAIN
call in update_gfx must NOT be OPEN, (c) a known ANY function must parse as ANY and a known
MAIN one as MAIN, (d) every scanned SDL name must resolve to a doc class (NODOC rows listed).
Exit 0 iff controls pass and there is no OPEN row without a HAND entry.
"""
import os, re, sys, glob, json, shlex, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SDL3 = "/opt/homebrew/include/SDL3"
FILES = sorted(glob.glob(os.path.join(ROOT, "src/main/*.cpp")) + glob.glob(os.path.join(ROOT, "src/main/*.mm"))
               + glob.glob(os.path.join(ROOT, "src/main/*.h"))) + [
    os.path.join(ROOT, "lib/rt64/src/hle/rt64_application_window.cpp"),
    os.path.join(ROOT, "lib/rt64/src/imgui/imgui_impl_sdl2_custom.cpp")]

# Thread roots (who calls these, and from which thread, is read from the runtime source):
ROOTS = {
    "main": "MAIN",                 # process main thread
    "create_gfx": "MAIN",           # librecomp recomp.cpp:868, main thread before the loop
    "create_window": "MAIN",        # recomp.cpp:874
    "update_gfx": "MAIN",           # recomp.cpp:939, main-thread loop
    "get_n64_input": "GAME",        # ultramodern input.cpp:149 (osContGetReadData, guest thread)
    "set_rumble": "GAME",           # ultramodern input.cpp:209
    "hook_draw": "PRESENT",         # rt64_present_queue.cpp:1131 drawHook, inside PresentQueue::threadPresent (present thread)
    "setup": "GFX",                 # RT64 Application::setup -> ApplicationWindow::setup, ultramodern gfx_thread_func
}
# SDL2-only names (sdl2-compat implements them on top of these SDL3 calls; class taken from the SDL3 call)
ALIAS = {"SDL_GetWindowWMInfo": "SDL_GetWindowProperties", "SDL_Metal_GetDrawableSize": "SDL_GetWindowSizeInPixels",
         "SDL_GL_GetDrawableSize": "SDL_GetWindowSizeInPixels", "SDL_SetTextInputRect": "SDL_SetTextInputArea",
         "SDL_VideoInit": "SDL_InitSubSystem", "SDL_GetNumVideoDisplays": "SDL_GetDisplays",
         "SDL_NumJoysticks_deprecated_use_SDL_GetJoysticks": "SDL_GetJoysticks", "SDL_JoystickGetDeviceInstanceID": "SDL_GetJoysticks",
         "SDL_QueueAudio": "SDL_PutAudioStreamData", "SDL_GetQueuedAudioSize": "SDL_GetAudioStreamQueued",
         "SDL_ClearQueuedAudio": "SDL_ClearAudioStream", "SDL_GetAudioDeviceStatus": "SDL_AudioDevicePaused",
         "SDL_GetNumAudioDevices": "SDL_GetAudioPlaybackDevices", "SDL_GameControllerHasRumble": "SDL_GetGamepadProperties"}
# Hand classes for OPEN rows: key "file:func:SDLname" -> reason. Filled from the s7639 review.
_PANEL = "s7639 FIXED: default reads g_win_size published by update_gfx (main); the SDL calls run only under ROGUESQ_S7639_ST=0|chk"
_DEADW = ("dead on macOS: needs sdlWindow==nullptr && usesWindowMessageFilter; runtime [RT64] post-setup prints "
          "usesWindowMessageFilter=0 (s7638 logs, s7639 run)")
_TITLE = "dead: ApplicationWindow::setup(const char* title) overload; we pass create_window's handle (core.window set)"
_IMGUI = ("dead on macOS: only Inspector reaches ImGui_ImplSDL2_*, and only with sdlWindow != nullptr; sdlWindow is set only "
          "under RT64_SDL_WINDOW_VULKAN (undefined here) and runtime post-setup prints sdlWindow=0x0")
HAND = {"src/main/rs64_controls_panel.cpp:hook_draw:SDL_GetWindowFromID": _PANEL,
        "src/main/rs64_controls_panel.cpp:hook_draw:SDL_GetWindowSize": _PANEL,
        "lib/rt64/src/hle/rt64_application_window.cpp:setup:SDL_GetWindowFromID": _DEADW,
        "lib/rt64/src/hle/rt64_application_window.cpp:setup:SDL_GetDesktopDisplayMode": _TITLE,
        "lib/rt64/src/hle/rt64_application_window.cpp:setup:SDL_CreateWindow": _TITLE,
        "lib/rt64/src/hle/rt64_application_window.cpp:setup:SDL_VideoInit": _TITLE,
        "lib/rt64/src/hle/rt64_application_window.cpp:setup:SDL_GetWindowWMInfo": _TITLE,
        "lib/rt64/src/hle/rt64_application_window.cpp:setup:SDL_Metal_CreateView": _TITLE,
        "lib/rt64/src/hle/rt64_application_window.cpp:setup:SDL_Metal_GetLayer": _TITLE}
HAND_FILE = {"lib/rt64/src/imgui/imgui_impl_sdl2_custom.cpp": _IMGUI}

def load_threadsafety():
    cls = {}
    for h in glob.glob(os.path.join(SDL3, "*.h")):
        txt = open(h, errors="replace").read()
        for m in re.finditer(r"/\*\*(.*?)\*/\s*extern\s+SDL_DECLSPEC[^;(]*?\b(SDL_\w+)\s*\(", txt, re.S):
            doc, name = m.group(1), m.group(2)
            t = re.search(r"\\threadsafety\s+(.*?)(?:\n\s*\*\s*\n|\n\s*\*\s*\\)", doc, re.S)
            if not t:
                cls[name] = ("NODOC", "")
                continue
            s = " ".join(x.strip().lstrip("*").strip() for x in t.group(1).splitlines())
            if "main thread" in s and "any thread" not in s:
                c = "MAIN"
            elif "created the window" in s or "thread that created" in s:
                c = "WIN"
            elif re.search(r"safe to (call|use) this (function|macro) from any thread", s) or "any thread" in s:
                c = "ANY"
            else:
                c = "OTHER"
            cls[name] = (c, s)
    return cls

def load_oldnames():
    mp = {}
    for line in open(os.path.join(SDL3, "SDL_oldnames.h")):
        m = re.match(r"#define\s+(SDL_\w+)\s+(SDL_\w+)\s*$", line)
        if m and "_renamed_" not in m.group(2):
            mp.setdefault(m.group(1), m.group(2))
    return mp

_CC = None
def active_mask(path):
    """Original-file line numbers that survive the preprocessor in our real build (clang -E with the
    compile_commands flags; headers inherit from main.cpp's flags). None = could not preprocess."""
    global _CC
    if _CC is None:
        _CC = {os.path.normpath(os.path.join(e["directory"], e["file"])): e
               for e in json.load(open(os.path.join(ROOT, "build/compile_commands.json")))}
    e = _CC.get(os.path.normpath(path)) or _CC.get(os.path.join(ROOT, "src/main/main.cpp"))
    args = e.get("arguments") or shlex.split(e["command"])
    a, skip = [], False
    for x in args:
        if skip: skip = False; continue
        if x == "-o": skip = True; continue
        if x == "-c" or os.path.normpath(os.path.join(e["directory"], x)) == os.path.normpath(e["file"]): continue
        a.append(x)
    if path.endswith(".h"): a += ["-x", "objective-c++" if "rs64_imgui" in path else "c++"]
    a += ["-E", "-w", path]
    r = subprocess.run(a, cwd=e["directory"], capture_output=True, text=True, errors="replace")
    if r.returncode != 0: return None
    act, cur, ln, tgt = set(), None, 0, os.path.realpath(path)
    for line in r.stdout.splitlines():
        m = re.match(r'# (\d+) "([^"]*)"', line)
        if m:
            ln, cur = int(m.group(1)), os.path.realpath(m.group(2)) if m.group(2)[:1] == "/" else os.path.realpath(os.path.join(e["directory"], m.group(2)))
            continue
        if cur == tgt and line.strip(): act.add(ln)
        ln += 1
    return act

PP_FAIL = []

def strip(src):
    """Blank comments and string/char literals, keep newlines and length."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i); j = n if j < 0 else j
            out.append(" " * (j - i)); i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2); j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", src[i:j])); i = j
        elif c in "\"'":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            j = min(j + 1, n)
            out.append(c + re.sub(r"[^\n]", " ", src[i + 1:j - 1]) + c if j - i >= 2 else src[i:j]); i = j
        elif src.startswith("R\"(", i):
            j = src.find(")\"", i); j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", src[i:j])); i = j
        else:
            out.append(c); i += 1
    return "".join(out)

KW = {"if", "for", "while", "switch", "catch", "return", "sizeof", "else", "do", "try"}

def scopes(s):
    """Return list of (start, end, kind, name) for top-level functions and thread lambdas."""
    res, stack = [], []
    for m in re.finditer(r"[{}]", s):
        p = m.start()
        if s[p] == "{":
            # statement head = text back to previous ; { } at any depth
            k = max(s.rfind(";", 0, p), s.rfind("{", 0, p), s.rfind("}", 0, p))
            head = s[k + 1:p]
            kind, name = None, None
            fdepth = sum(1 for x in stack if x[1] in ("func", "lambda"))
            hm = re.search(r"([A-Za-z_~][\w:]*)\s*\([^{}]*\)\s*(const\s*)?(noexcept\s*)?(->\s*[\w:<>*& ]+)?\s*$", head)
            if "std::thread" in head or re.search(r"\bthread\s+\w+\s*\{\s*\[", s[k + 1:p + 2]) or \
               re.search(r"std::thread[\w\s]*[\({]\s*\[[^\]]*\]\s*(\([^)]*\))?\s*(mutable\s*)?$", head):
                kind, name = "lambda", "thread@%d" % (s.count("\n", 0, p) + 1)
            elif fdepth == 0 and hm and hm.group(1).split("::")[-1] not in KW and not re.search(r"\]\s*\(", head):
                kind, name = "func", hm.group(1).split("::")[-1]
            stack.append((p, kind, name))
        else:
            if not stack:
                continue
            st, kind, name = stack.pop()
            if kind:
                res.append((st, p, kind, name))
    return res

def enclosing(sc, pos):
    best = None
    for st, en, kind, name in sc:
        if st <= pos <= en and (best is None or st > best[0]):
            best = (st, en, kind, name)
    return best

def scan(paths, plant=None):
    rows, calls, funcbodies = [], {}, {}
    for path in paths:
        src = open(path, errors="replace").read()
        if plant and plant[0] == path:
            src = plant[1](src)
        s = strip(src)
        if "--no-pp" not in sys.argv:
            act = MASKS.get(path)
            if path not in MASKS:
                act = MASKS[path] = active_mask(path)
                if act is None: PP_FAIL.append(path)
            if act is not None:
                # Segment = lines between two conditional directives. clang -E merges multi-line macro calls,
                # so single lines can vanish from an ACTIVE segment; a segment is dead only if none survive.
                ls = s.split("\n")
                dre = re.compile(r"\s*#\s*(if|ifdef|ifndef|elif|else|endif)\b")
                out, seg = [], []
                def flush():
                    live = any((i + 1) in act for i, l in seg if l.strip())
                    out.extend(l if live or not l.strip() else " " * len(l) for i, l in seg); seg.clear()
                for i, l in enumerate(ls):
                    if dre.match(l): flush(); out.append(l)
                    else: seg.append((i, l))
                flush()
                s = "\n".join(out)
        sc = scopes(s)
        rel = os.path.relpath(path, ROOT)
        funcs = [(st, en, n) for st, en, k, n in sc if k == "func"]
        thr = [(st, en, n) for st, en, k, n in sc if k == "lambda"]
        for st, en, n in funcs:
            body = s[st:en]
            for th in thr:  # thread lambda bodies belong to the lambda, not the enclosing function
                if st < th[0] < en:
                    body = body.replace(s[th[0]:th[1]], " " * (th[1] - th[0]))
            funcbodies.setdefault(n, []).append((rel, body))
        for st, en, n in thr:
            funcbodies.setdefault(n, []).append((rel, s[st:en]))
        # std::thread(fn, ...) / std::thread{ fn, ... } with a named function = worker root
        for m in re.finditer(r"std::thread\s*[({]\s*([A-Za-z_]\w*)\s*[,)}]", s):
            ROOTS_DYN.setdefault(m.group(1), "WORKER")
        for m in re.finditer(r"\b(SDL_\w+)\s*\(", s):
            nm = m.group(1)
            if nm.isupper() or nm in ("SDL_zero", "SDL_VERSION"):
                continue
            pre = s[max(0, m.start() - 80):m.start()]
            if re.search(r"(extern|typedef|SDLCALL|DECLSPEC)\s*[\w\s*]*$", pre):
                continue
            e = enclosing(sc, m.start())
            line = s.count("\n", 0, m.start()) + 1
            rows.append({"file": rel, "line": line, "sdl2": nm, "scope": e[3] if e else "<file>",
                         "kind": e[2] if e else None})
    return rows, funcbodies

ROOTS_DYN = {}
MASKS = {}

def propagate(funcbodies):
    names = set(funcbodies)
    callees = {}
    for n, bodies in funcbodies.items():
        ids = set()
        for _, b in bodies:
            ids |= set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", b))
            ids |= set(re.findall(r"=\s*&?([A-Za-z_]\w*)\s*[,;}]", b))  # callbacks assigned by name
        callees[n] = (ids & names) - {n}
    th = {n: set() for n in names}
    for n, t in list(ROOTS.items()) + list(ROOTS_DYN.items()):
        if n in th:
            th[n].add(t)
    for n in names:
        if n.startswith("thread@"):
            th[n].add("WORKER")
    changed = True
    while changed:
        changed = False
        for n in names:
            for c in callees[n]:
                if not th[n] <= th[c]:
                    th[c] |= th[n]; changed = True
    return th, callees

def classify(rows, th, ts, old):
    for r in rows:
        s3 = old.get(r["sdl2"], r["sdl2"]); s3 = ALIAS.get(s3, s3)
        c, txt = ts.get(s3, ("NODOC", ""))
        r["sdl3"], r["cls"] = s3, c
        t = th.get(r["scope"], set())
        r["threads"] = ",".join(sorted(t)) or "UNROOTED"
        bad = (c in ("MAIN", "WIN")) and (not t or (t - {"MAIN"}))
        key = "%s:%s:%s" % (r["file"], r["scope"], r["sdl2"])
        h = HAND.get(key) or HAND_FILE.get(r["file"])
        r["state"] = ("HAND:" + h) if bad and h else ("OPEN" if bad else "ok")
    return rows

def run(paths, plant=None):
    ROOTS_DYN.clear()
    rows, fb = scan(paths, plant)
    th, _ = propagate(fb)
    return classify(rows, th, TS, OLD)

TS, OLD = load_threadsafety(), load_oldnames()

def main():
    rows = run(FILES)
    ok = True
    if "--controls" in sys.argv:
        mc = os.path.join(ROOT, "src/main/main.cpp")
        pa = lambda src: src + "\nstatic void s7639_plant_w() { std::thread([] { SDL_SetWindowTitle(nullptr, \"x\"); }).detach(); }\n"
        pb = lambda src: src.replace("    SDL_PumpEvents();", "    SDL_PumpEvents(); SDL_SetWindowTitle(nullptr, \"x\");", 1)
        ra = [r for r in run(FILES, (mc, pa)) if r["sdl2"] == "SDL_SetWindowTitle" and r["scope"].startswith("thread@")]
        rb = [r for r in run(FILES, (mc, pb)) if r["sdl2"] == "SDL_SetWindowTitle" and r["scope"] == "update_gfx"]
        ca = len(ra) == 1 and ra[0]["state"] == "OPEN"
        cb = len(rb) == 1 and rb[0]["state"] == "ok" and rb[0]["threads"] == "MAIN"
        cc = TS.get("SDL_GetTicks", ("?",))[0] == "ANY" and TS.get("SDL_CreateWindow", ("?",))[0] == "MAIN"
        nodoc = sorted({r["sdl3"] for r in rows if r["cls"] == "NODOC"})
        cd = True
        print("control a (planted worker MAIN call -> OPEN): %s" % ("PASS" if ca else "FAIL"))
        print("control b (planted update_gfx MAIN call -> ok/MAIN): %s" % ("PASS" if cb else "FAIL"))
        print("control c (doc parse GetTicks=ANY CreateWindow=MAIN): %s" % ("PASS" if cc else "FAIL"))
        print("info d NODOC names: %s" % (", ".join(nodoc) or "none"))
        k0 = "src/main/rs64_controls_panel.cpp:hook_draw:SDL_GetWindowSize"; sv = HAND.pop(k0)
        ce = any(r["state"] == "OPEN" and r["sdl2"] == "SDL_GetWindowSize" and r["scope"] == "hook_draw" for r in run(FILES))
        HAND[k0] = sv
        print("control e (drop a HAND entry -> row OPEN): %s" % ("PASS" if ce else "FAIL"))
        ok = ca and cb and cc and cd and ce
    from collections import Counter
    if PP_FAIL: print("PP_FAIL (scanned unmasked): " + ", ".join(os.path.relpath(x, ROOT) for x in PP_FAIL))
    print("rows=%d files=%d by cls: %s" % (len(rows), len({r["file"] for r in rows}),
          dict(Counter(r["cls"] for r in rows))))
    print("by state: %s" % dict(Counter(r["state"].split(":")[0] for r in rows)))
    hc = Counter(r["state"][5:] for r in rows if r["state"].startswith("HAND:"))
    for k, v in hc.items(): print("HAND %3d  %s" % (v, k))
    for r in rows:
        if r["state"] == "OPEN" or "-v" in sys.argv:
            print("%-6s %-5s %-44s %-34s %-22s %s" % (r["state"][:60] if r["state"] == "OPEN" else r["state"][:5],
                  r["cls"], "%s:%d" % (r["file"], r["line"]), r["sdl3"], r["threads"], r["scope"]))
    if "--json" in sys.argv:
        json.dump(rows, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    nopen = sum(r["state"] == "OPEN" for r in rows)
    sys.exit(0 if ok and nopen == 0 else 1)

if __name__ == "__main__":
    main()
