#!/usr/bin/env python3
"""s7641 class CF: framework-callback thread census.

Every place our compiled host code hands a callback to a framework that invokes it on a thread of the
framework's choosing (Metal command-buffer / drawable handlers, SDL event watch / filter, SDL virtual-joystick
callbacks, libdispatch blocks, atexit / at_quick_exit) is grep-enumerated over the non-contrib TUs in
build/compile_commands.json (plus plume's own plume_*.cpp/.mm). Each site needs a HAND row saying which
thread delivers it (framework docs: Metal handlers = Metal's private dispatch threads, NOT serialised; SDL3
SDL_AddEventWatch "may call this callback at any time from any thread"; dispatch_get_main_queue = main) and
how the state the body touches is synchronised. A site without a HAND row is OPEN.

Runtime witness (not our code): Thread Sanitizer on plume_metal.cpp, tools/s7641_tsan_build.sh + tools/s7641_tsan_run.zsh <tag> <binary> [ENV=..].

--controls: (a) a planted Metal completion handler in a temp file must be OPEN, (b) dropping a HAND row must
make that site OPEN, (c) removing the s7641 gate from the drawable-index write must be reported FIX_MISSING,
(d) site count >= 20 (the enumeration is not silently empty). Exit 0 iff controls pass and nothing is OPEN.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT = re.compile(r'\b(addCompletedHandler|addScheduledHandler|addPresentedHandler|SDL_AddEventWatch|SDL_SetEventFilter|'
                 r'SDL_AddHintCallback|SDL_AddTimer|dispatch_async_f|dispatch_async|dispatch_sync|dispatch_after|'
                 r'dispatch_data_create|at_quick_exit|atexit|set_terminate)\s*\(|\.(Rumble|Update|SetLED|RumbleTriggers|'
                 r'SendEffect|callback)\s*=')

_MAINQ = "main queue: body runs on the main thread (s7588/s7640 audited)"
_EXIT = "process-exit thread; body only flushes/prints atomics or restores stderr (class AF s7355 covers exit paths)"
_METAL_TSAN = ("Metal private thread; TSan (s7641) reports only the metal-cpp block byref copy at registration vs the "
               "handler read, identical in both arms: Metal's own handoff is invisible to TSan (registration precedes commit)")
HAND = {
    "plume_apple.mm:dispatch_async:dispatch_async(dispatch_get_main_queue(), ^{ rs64S7588RunBlock(body); });": _MAINQ,
    "plume_apple.mm:dispatch_sync:dispatch_sync(dispatch_get_main_queue(), updateBlock);": _MAINQ,
    "plume_apple.mm:dispatch_async:dispatch_async(dispatch_get_main_queue(), ^{": _MAINQ,
    "plume_metal.cpp:dispatch_data_create:const dispatch_data_t dispatchData = dispatch_data_create(data, size, dispatch_get_main_qu":
        "empty destructor block ^{}: touches nothing",
    "plume_metal.cpp:addPresentedHandler:drawableMtl->addPresentedHandler([presentId, drainBegin](MTL::Drawable *d) {":
        "opt-in only (PRESENT_RING/INFLIGHT/DRAIN/VI_LOCK); body: atomics, g_rs64DrainMutex, pring mutex, g_rs64InflightMutex; "
        "g_rs64LastShown plain double written only here (DRAIN_HITCH opt-in, single writer, readers none off-handler)",
    "plume_metal.cpp:addScheduledHandler:presentBuffer->addScheduledHandler([drawableMtl, rs64S](MTL::CommandBuffer* cmdBuffer) {":
        "present(); rs64S stamp is owned by this command buffer (scheduled -> completed ordered by Metal); " + _METAL_TSAN,
    "plume_metal.cpp:addCompletedHandler:presentBuffer->addCompletedHandler([drawableMtl, presentId, this, rs64S](MTL::CommandBuffe":
        "s7641 FIXED: currentAvailableDrawableIndex was a plain uint32_t RMW here vs the present thread's read in acquireTexture "
        "(TSan: 2 reports, completed handlers on two Metal threads + acquireTexture); now atomic CAS, ROGUESQ_S7641_CF=0 = old. "
        "lastPresentedId under its mutex",
    "plume_metal.cpp:addCompletedHandler:interfaceCommandList->mtl->addCompletedHandler([rs64WaitBuf, rs64Commit](MTL::CommandBuffe":
        "opt-in stage stamps: std::atomic stores only; " + _METAL_TSAN,
    "plume_metal.cpp:addCompletedHandler:interfaceCommandList->mtl->addCompletedHandler([c0](MTL::CommandBuffer* cmdBuffer) {":
        "opt-in: rs64AtomicMax / fetch_add only; " + _METAL_TSAN,
    "plume_metal.cpp:addCompletedHandler:interfaceCommandList->mtl->addCompletedHandler([signalFence](MTL::CommandBuffer* cmdBuffer":
        "dispatch_semaphore_signal: thread-safe by API; " + _METAL_TSAN,
    "rt64_file_dialog.cpp:dispatch_async_f:dispatch_async_f(dispatch_get_main_queue(), c, [](void *p) {": _MAINQ + " (s7640 NFD_Init)",
    "rt64_file_dialog.cpp:dispatch_async_f:dispatch_async_f(dispatch_get_main_queue(), nullptr, rs64NfdQuit);": _MAINQ + " (s7640 NFD_Quit)",
    "rt64_application_window.cpp:SDL_SetEventFilter:SDL_SetEventFilter(&ApplicationWindow::sdlEventFilter, this);":
        "dead on macOS: needs sdlWindow != nullptr; runtime post-setup prints sdlEventFilterInstalled=0 (s7639 _DEADW)",
    "main.cpp:at_quick_exit:if (pl == \"crash\") std::at_quick_exit([] { fprintf(stderr, \"[s7593] plant crash\\n\"); fflus": "test plant; " + _EXIT,
    "main.cpp:at_quick_exit:if (pl == \"hang\") std::at_quick_exit([] { fprintf(stderr, \"[s7593] plant hang\\n\"); fflush(": "test plant; " + _EXIT,
    "main.cpp:Rumble:d.Rumble = rs64_rumble_vpad_cb;":
        "ROGUESQ_RUMBLE_TEST only; SDL calls it from the SDL_RumbleGamepad caller (rs64_rumble_tick, main per s7639); body atomics + fprintf",
    "main.cpp:SDL_AddEventWatch:SDL_AddEventWatch([](void*, SDL_Event* ev) -> int {":
        "SDL3: any thread that pushes an event (SDL_PushEvent sites run on main/audio/game threads); body: std::atomic flags "
        "(g_rs64_fs_toggle, g_rs64_disp_ev, g_rs64_disp_removed, function-static counters) + fprintf only",
    "main.cpp:atexit:s6979se::init(); std::atexit([] { rs64_stderr_async_restore(); }); std::at_quick_exit([] {": _EXIT,
    "upstream_compat.cpp:atexit:std::atexit(vi_boundary_summary);": _EXIT,
    "upstream_compat.cpp:at_quick_exit:std::at_quick_exit(vi_boundary_summary);": _EXIT,
    "dpc_bridge.cpp:atexit:std::atexit(rs64_m4_y8000_atexit);": _EXIT,
}


def files():
    cc = json.load(open(os.path.join(ROOT, "build/compile_commands.json")))
    keep = lambda f: not re.search(r'/contrib/(?!plume/plume_)|factor5_ucode|RecompiledFuncs|/build/', f)
    return sorted({e["file"] for e in cc if keep(e["file"])})


def scan(paths, text_override=None):
    rows = []
    for f in paths:
        src = (text_override or {}).get(f)
        if src is None:
            try: src = open(f, errors="ignore").read()
            except OSError: continue
        for i, l in enumerate(src.split("\n"), 1):
            if l.strip().startswith("//"): continue
            m = PAT.search(l)
            if not m: continue
            key = "%s:%s:%s" % (os.path.basename(f), m.group(1) or m.group(2), l.strip()[:90])
            rows.append({"site": "%s:%d" % (os.path.relpath(f, ROOT), i), "key": key})
    return rows


def classify(rows, hand):
    for r in rows: r["state"] = "ok" if r["key"] in hand else "OPEN"
    return rows


def fix_present(src):
    w = [l for l in src.split("\n") if re.search(r'\bcurrentAvailableDrawableIndex\s*=\s*\(', l)]
    return bool(w) and all("rs64S7641Old()" in l for l in w)


def main():
    fs = files()
    rows = classify(scan(fs), HAND)
    pm = os.path.join(ROOT, "lib/rt64/src/contrib/plume/plume_metal.cpp")
    psrc = open(pm).read()
    fixed = fix_present(psrc)
    ok = True
    if "--controls" in sys.argv:
        plant = os.path.join(ROOT, "scratch/s7641/plant_cf.cpp")
        body = "void f(MTL::CommandBuffer* b){ b->addCompletedHandler([this](MTL::CommandBuffer*){ plainField++; }); }\n"
        ca = [r["state"] for r in classify(scan([plant], {plant: body}), HAND)] == ["OPEN"]
        drop = dict(HAND); k = next(iter(k for k in HAND if "acquire" not in k and "SDL_AddEventWatch" in k)); drop.pop(k)
        cb = any(r["state"] == "OPEN" and r["key"] == k for r in classify(scan(fs), drop))
        mut = psrc.replace("if (rs64S7641Old()) currentAvailableDrawableIndex", "currentAvailableDrawableIndex")
        cc_ = fixed and not fix_present(mut)
        cd = len(rows) >= 20
        for n, v in (("a planted Metal handler -> OPEN", ca), ("b drop HAND row -> OPEN", cb),
                     ("c ungated index write -> FIX_MISSING", cc_), ("d sites >= 20", cd)):
            print("control %s: %s" % (n, "PASS" if v else "FAIL")); ok &= v
        classify(rows, HAND)
    print("files=%d sites=%d ok=%d OPEN=%d fix_s7641=%s" % (len(fs), len(rows), sum(r["state"] == "ok" for r in rows),
          sum(r["state"] == "OPEN" for r in rows), "present" if fixed else "FIX_MISSING"))
    stale = set(HAND) - {r["key"] for r in rows}
    for k in sorted(stale): print("STALE HAND row (site gone or edited): " + k)
    for r in rows:
        if r["state"] == "OPEN" or "-v" in sys.argv:
            print("%-5s %-52s %s" % (r["state"], r["site"], HAND.get(r["key"], r["key"])[:150]))
    ok &= fixed and not any(r["state"] == "OPEN" for r in rows) and not stale
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
