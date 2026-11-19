#!/usr/bin/env python3
"""s7640 class AT: AppKit thread-affinity census (static half; runtime half = Apple's Main Thread Checker, scratch/s7640/run.zsh).

Scope: every Objective-C translation unit in build/compile_commands.json (.m/.mm) plus the CA::MetalLayer calls in
plume_metal.cpp. For each top-level function / method body (scopes from s7639_st_census, preprocessor-masked the same way):
  1. AppKit uses = message sends / property reads on AppKit classes (NSApplication/NSWindow/NSView/NSScreen/panels) or
     selectors only AppKit objects answer; Metal/Foundation/QuartzCore/ImGui-Metal sends are thread-safe (ANY).
  2. guard = the use sits inside a block posted to dispatch_get_main_queue() / rs64S7588Post, or inside the true branch of
     `if ([NSThread isMainThread])`.
  3. threads = from HAND_ROOTS (each cites where the runtime calls it) or, for extern "C" bridges called from src/main,
     the s7639 call-graph thread sets of the calling C++ functions.
OPEN = unguarded AppKit use reached by a non-main thread (or by no known root), without a DEAD entry.
--controls: (a) planted unguarded AppKit getter in a Gfx-rooted function -> OPEN, (b) same call inside a main-queue block ->
ok, (c) dropping the s7640 fix's DEAD entry re-opens NFD_Init. Exit 0 iff controls pass and nothing is OPEN.
"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib
st = importlib.import_module("s7639_st_census")
ROOT = st.ROOT

APPKIT_CLS = r"\b(NSApplication|NSApp|NSWindow|NSView|NSScreen|NSOpenPanel|NSSavePanel|NSAlert|NSEvent|NSCursor|NSMenu)\b"
APPKIT_SEL = r"\b(keyWindow|contentView|backingScaleFactor|toggleFullScreen|activationPolicy|setActivationPolicy|screens|" \
             r"safeAreaInsets|maximumFramesPerSecond|isOnActiveSpace|occlusionState|styleMask|isKeyWindow|runModal|" \
             r"beginSheetModalForWindow|makeKeyAndOrderFront)\b"

# Who calls each ObjC-side function, from which thread (read from the runtime source; s7639 roots + RT64 call sites).
HAND_ROOTS = {
    "NFD_Init": {"GFX"},       # rt64_file_dialog.cpp FileDialog::initialize <- RT64::Application ctor <- RT64Context ctor
                               # (src/main/rt64_render_context.cpp:502) <- create_render_context <- gfx_thread_func (MTC backtrace s7640)
    "NFD_Quit": {"GFX"},       # FileDialog::finish <- Application dtor (render context teardown, Gfx Thread)
    "NFD_OpenDialogN": {"PRESENT"}, "NFD_OpenDialogMultipleN": {"PRESENT"}, "NFD_SaveDialogN": {"PRESENT"},
    "NFD_PickFolderN": {"PRESENT"},  # FileDialog::get* <- rt64_state.cpp:4401-4465 / preset inspector (inspector UI)
    "getScaleFactor": {"MAIN"},     # plume_apple.mm: called only from isMainThread branches and main-queue blocks (checked below)
    "CocoaWindow": {"GFX"}, "updateWindowAttributesInternal": {"GFX", "PRESENT"}, "updateRefreshRateInternal": {"GFX", "PRESENT"},
    "getWindowAttributes": {"GFX", "PRESENT"}, "getRefreshRate": {"PRESENT"}, "toggleFullscreen": {"MAIN", "GFX"},
                               # MetalSwapChain ctor (Gfx, plume_metal.cpp:2116), needsResize/getRefreshRate per present
}
# NFD file dialogs are reached only when RT64's inspector is up: rt64_application.cpp:555/589 gate on userConfig.developerMode,
# which rt64_render_context.cpp:515 sets only from debug || dev_mode_on; runtime [RT64] post-setup prints developerMode=0.
_DEVMODE = "dead: inspector only (developerMode=0 in every s7640 run, rt64_application.cpp:555/589 gate)"
DEAD = {"NFD_Init": "s7640 FIXED: FileDialog::initialize runs it on the main queue (ROGUESQ_S7640_AT=0 = old); MTC 0 reports",
        "NFD_Quit": "s7640 FIXED: FileDialog::finish posts it to the main queue",
        "NFD_OpenDialogN": _DEVMODE, "NFD_OpenDialogMultipleN": _DEVMODE, "NFD_SaveDialogN": _DEVMODE,
        "NFD_PickFolderN": _DEVMODE,
        "rs64_s7640_at_plant": "positive control: runs only under ROGUESQ_S7640_AT_PLANT=1 (MTC must report it)"}

def objc_files():
    cc = json.load(open(os.path.join(ROOT, "build/compile_commands.json")))
    fs = sorted({os.path.normpath(os.path.join(e["directory"], e["file"])) for e in cc if e["file"].endswith((".m", ".mm"))})
    return fs + [os.path.join(ROOT, "lib/rt64/src/contrib/plume/plume_metal.cpp")]

def obj_scopes(s):
    """Functions incl. ObjC methods/C functions; also map block bodies posted to the main queue and isMainThread branches."""
    res = []
    for stt, en, kind, name in st.scopes(s):
        if kind == "func": res.append((stt, en, name))
    for m in re.finditer(r"^[-+]\s*\([^)]*\)\s*(\w+)[^{;]*\{", s, re.M):  # ObjC methods
        p = s.index("{", m.start()); d = 0
        for j in range(p, len(s)):
            d += {"{": 1, "}": -1}.get(s[j], 0)
            if d == 0: res.append((p, j, m.group(1))); break
    return res

def match_brace(s, p):
    d = 0
    for j in range(p, len(s)):
        d += {"{": 1, "}": -1}.get(s[j], 0)
        if d == 0: return j
    return len(s)

def guarded_spans(s):
    sp = []
    # blocks assigned to a variable then posted, or posted inline
    posted_vars = set(re.findall(r"dispatch_(?:a?sync)\s*\(\s*dispatch_get_main_queue\(\)\s*,\s*(\w+)\s*\)", s)) | \
                  set(re.findall(r"rs64S7588Post\s*\(\s*(\w+)\s*\)", s))
    for m in re.finditer(r"dispatch_a?sync\s*\(\s*dispatch_get_main_queue\(\)\s*,\s*\^\s*\{", s):
        p = s.index("{", m.end() - 1); sp.append((p, match_brace(s, p)))
    for v in posted_vars:
        for m in re.finditer(r"\b%s\s*=\s*\^\s*\{" % re.escape(v), s):
            p = s.index("{", m.end() - 1); sp.append((p, match_brace(s, p)))
    for m in re.finditer(r"if\s*\(\s*\[\s*NSThread\s+isMainThread\s*\]\s*\)\s*\{", s):
        p = m.end() - 1; sp.append((p, match_brace(s, p)))
    return sp

def bridge_threads():
    """Thread sets of src/main C++ functions (s7639 call graph), to attribute extern "C" ObjC bridges by their callers."""
    st.ROOTS_DYN.clear()
    _, fb = st.scan(st.FILES)
    th, _ = st.propagate(fb)
    return fb, th

def run(plant=None):
    fb, th = bridge_threads()
    rows = []
    for path in objc_files():
        src = open(path, errors="replace").read()
        if plant and plant[0] == path: src = plant[1](src)
        s = st.strip(src)
        rel = os.path.relpath(path, ROOT)
        gs = guarded_spans(s)
        sc = obj_scopes(s)
        pats = [APPKIT_CLS, APPKIT_SEL] if not path.endswith(".cpp") else []
        for pat in pats:
            for m in re.finditer(pat, s):
                pos = m.start()
                if re.match(r"\s*\*", s[m.end():m.end() + 2]) and not re.search(r"\[\s*$", s[max(0, pos - 3):pos]):
                    # a type in a declaration (NSWindow *w = ...) is not a call; its receiver uses are caught by selectors
                    if m.group(1) not in ("NSApp",): continue
                if re.search(r"(#import|@interface|@class)[^\n]*$", s[max(0, pos - 60):pos]): continue
                enc = [x for x in sc if x[0] <= pos <= x[1]]
                if not enc: continue
                f = max(enc, key=lambda x: x[0])[2]
                g = any(a <= pos <= b for a, b in gs)
                if f in HAND_ROOTS: t = set(HAND_ROOTS[f])
                else:
                    t = set()
                    for caller, bodies in fb.items():
                        if any(re.search(r"\b%s\s*\(" % re.escape(f), b) for _, b in bodies): t |= th.get(caller, set())
                if f == "getScaleFactor": g = True  # every caller is guarded (checked by control d)
                line = s.count("\n", 0, pos) + 1
                bad = not g and (not t or (t - {"MAIN"}))
                state = ("DEAD:" + DEAD[f]) if bad and f in DEAD else ("OPEN" if bad else "ok")
                rows.append(dict(file=rel, line=line, tok=m.group(1), func=f, guarded=g,
                                 threads=",".join(sorted(t)) or "UNROOTED", state=state))
        if path.endswith("plume_metal.cpp"):
            for m in re.finditer(r"\blayer->(\w+)\s*\(", s):
                line = s.count("\n", 0, m.start()) + 1
                rows.append(dict(file=rel, line=line, tok="CAMetalLayer." + m.group(1), func="(MetalSwapChain)", guarded=False,
                                 threads="GFX,PRESENT", state="ok:CA-ANY"))
    # dedupe to one row per (file, line, func)
    seen, out = set(), []
    for r in rows:
        k = (r["file"], r["line"], r["func"])
        if k not in seen: seen.add(k); out.append(r)
    return out

def getscale_callers_guarded():
    p = os.path.join(ROOT, "lib/rt64/src/contrib/plume/plume_apple.mm")
    s = st.strip(open(p, errors="replace").read()); gs = guarded_spans(s)
    calls = [m.start() for m in re.finditer(r"\bgetScaleFactor\s*\(\s*nsWindow", s)]
    return len(calls), sum(any(a <= c <= b for a, b in gs) for c in calls)

def main():
    rows = run(); ok = True
    from collections import Counter
    if "--controls" in sys.argv:
        mm = os.path.join(ROOT, "lib/rt64/src/contrib/plume/plume_apple.mm")
        HAND_ROOTS["rs64PlantA"] = {"GFX"}; HAND_ROOTS["rs64PlantB"] = {"GFX"}
        pa = lambda src: src + "\nstatic void rs64PlantA() { NSWindow *w = [[NSApplication sharedApplication] keyWindow]; (void)w; }\n"
        pb = lambda src: src + ("\nstatic void rs64PlantB() { dispatch_async(dispatch_get_main_queue(), ^{ "
                                "NSWindow *w = [[NSApplication sharedApplication] keyWindow]; (void)w; }); }\n")
        ra = [r for r in run((mm, pa)) if r["func"] == "rs64PlantA"]
        rb = [r for r in run((mm, pb)) if r["func"] == "rs64PlantB"]
        ca = bool(ra) and all(r["state"] == "OPEN" for r in ra)
        cb = bool(rb) and all(r["state"] == "ok" for r in rb)
        sv = DEAD.pop("NFD_Init"); cc = any(r["func"] == "NFD_Init" and r["state"] == "OPEN" for r in run()); DEAD["NFD_Init"] = sv
        n, g = getscale_callers_guarded(); cd = n > 0 and n == g
        print("control a (planted unguarded AppKit in Gfx fn -> OPEN, %d rows): %s" % (len(ra), "PASS" if ca else "FAIL"))
        print("control b (same call in main-queue block -> ok, %d rows): %s" % (len(rb), "PASS" if cb else "FAIL"))
        print("control c (drop NFD_Init fix entry -> OPEN): %s" % ("PASS" if cc else "FAIL"))
        print("control d (getScaleFactor callers guarded %d/%d): %s" % (g, n, "PASS" if cd else "FAIL"))
        ok = ca and cb and cc and cd
    print("rows=%d files=%d by state: %s" % (len(rows), len({r["file"] for r in rows}),
          dict(Counter(r["state"].split(":")[0] + (":" + r["state"].split(":")[1][:6] if r["state"].startswith("ok:") else "") for r in rows))))
    for k, v in Counter((r["func"], r["threads"], r["guarded"], r["state"][:70]) for r in rows).most_common():
        if "-v" in sys.argv or not k[3].startswith("ok"): print("%3d %-32s %-14s guarded=%d %s" % (v, k[0], k[1], k[2], k[3]))
    if "-v" in sys.argv:
        for k, v in Counter((r["file"], r["func"], r["threads"], r["guarded"]) for r in rows if r["state"].startswith("ok")).items():
            print("  ok %3d %s %s %s guarded=%d" % (v, k[0], k[1], k[2], k[3]))
    sys.exit(0 if ok and not any(r["state"] == "OPEN" for r in rows) else 1)

if __name__ == "__main__":
    main()
