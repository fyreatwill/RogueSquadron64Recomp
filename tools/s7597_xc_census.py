#!/usr/bin/env python3
"""s7597 class XC: every host site that can raise a C++ exception out to std::terminate (rc134) in the shipped host code.

Scope: src/, librecomp/src, ultramodern/src, lib/rt64/src (skips tests/tools/contrib/examples/demos), // comments stripped.
Kinds:
  parse   nlohmann json::parse(...) / `stream >> json` (parse_error)         ok when allow_exceptions=false or inside a try
  throw   explicit `throw X`                                                  classified per row
  jat     nlohmann `.at(` on json (out_of_range / type_error)                 classified per row
  dent    directory_entry member query with NO error_code (is_regular_file(), is_directory(), exists(), file_size(),
          status(), symlink_status(), is_symlink(), last_write_time()) -- the s7597 XC-1 defect shape (ELOOP/EACCES -> throw)
  thread  std::thread construction (std::system_error on thread-creation failure); `static std::thread` / call_once /
          one-shot latches are 'once' by pattern, the rest are rows
(class FS, tools/s7596_fs_census.py, covers std::filesystem:: free functions.)
Every site must match a ROW (file, kind, line substring) -> verdict, else OPEN.
--controls: (1) plant the pre-s7597 throwing `mod_path.is_regular_file()` into a copy of mods.cpp, (2) drop one row;
both must report OPEN. Exit 0 only if 0 open + 0 stale and both controls fire.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ["src", "lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src", "lib/rt64/src"]
SKIP = re.compile(r"/(tests?|tools|contrib|examples?|demos?)/")
EXT = (".cpp", ".cc", ".c", ".h", ".hpp", ".mm")
KINDS = [
    ("parse", re.compile(r"json::parse\s*\(|>>\s*(json_out|jroot|j|json)\b")),
    ("throw", re.compile(r"\bthrow\s+[\w:]")),
    ("jat", re.compile(r"\b(j|jsonObj|json)\.at\(")),
    ("dent", re.compile(r"\.(is_regular_file|is_directory|exists|file_size|status|symlink_status|is_symlink|last_write_time)\(\)")),
    ("thread", re.compile(r"std::thread\s*(\(|\{|\w+\s*[({])|make_unique<std::thread>|new std::thread")),
]
ONCE = re.compile(r"static std::thread|call_once|exchange\(true\)|if \(first\)|if \(!started\)|static const bool started")

G = "gated: env-gated diagnostic/plant thread, off in the owner recipe"
ROWS = {
    # parse
    ("src/main/rs64_bindings_json.h", "parse", "const json j = json::parse(text, nullptr, false)"): "ok: s7655 G6b controls.json: allow_exceptions=false + is_discarded check; every later j[...] / get<> is behind contains() / is_*() (G6b garbage-file controls)",
    ("librecomp/src/mod_manifest.cpp", "parse", "json::parse(manifest_data.begin(), manifest_data.end(), nullptr, false)"): "ok: allow_exceptions=false + is_discarded check (witness mod_dir_garbage/mod_dir_types alive)",
    ("librecomp/src/mods.cpp", "parse", "input_file >> json_out"): "ok: read_json try/catch parse_error; mods.json read every boot (witness mj_garbage/array/types/dir/bin alive)",
    ("librecomp/src/mod_manifest.cpp", "parse", "input_file >> json_out"): "ok: same read_json try/catch (mod config storage)",
    ("rt64/src/common/rt64_user_configuration.cpp", "parse", "stream >> jroot"): "ok: try/catch nlohmann::detail::exception",
    ("rt64/src/render/rt64_texture_cache.cpp", "parse", "json::parse(databaseBytes"): "ok: inside try (texture-pack database, inspector only)",
    # throw
    ("librecomp/src/pi.cpp", "throw", "ROM DMA write unimplemented"): "guest-fatal: osPiStartDma OS_WRITE to cart ROM; retail never writes ROM, only corrupt guest state reaches it; terminate goes through the SIGABRT report",
    ("ultramodern/src/events.cpp", "throw", "Failed to initialize the renderer"): "fatal-anyway: renderer setup failed, show_renderer_error dialog shown first; nothing to run",
    ("ultramodern/src/threads.cpp", "throw", "Invalid thread priority!"): "dead: switch over the ThreadPriority enum, every caller passes an enumerator",
    ("ultramodern/src/threads.cpp", "throw", "No threads left to run!"): "fatal-anyway: guest scheduler empty = guest deadlock; terminate prints the report",
    ("ultramodern/src/threads.cpp", "throw", "ultramodern::thread_terminated{}"): "ok: caught in _thread_func (threads.cpp wait_for_resumed/run_thread_function try) and recomp.cpp entrypoint try",
    ("rt64/src/render/rt64_shader_compiler.cpp", "throw", "Failed to get shader compiler error"): "gated: DXC shader compiler, RT64 dev shader compile path; Metal build uses precompiled shaders",
    ("rt64/src/render/rt64_shader_compiler.cpp", "throw", "Shader compilation error"): "gated: same DXC path",
    # jat
    ("rt64/src/preset/rt64_preset.cpp", "jat", "j.at("): "gated-dev: preset JSON (inspector presets only)",
    ("rt64/src/preset/rt64_preset.h", "parse", "i >> jroot"): "gated-dev: PresetLibrary::load, NO try (malformed preset file would terminate); only rt64_preset_inspector.h F1 inspector calls it",
    ("rt64/src/preset/rt64_preset_draw_call.cpp", "jat", "jsonObj.at(\"filter\")"): "gated-dev: preset JSON",
    ("rt64/src/shared/rt64_hlsl_json.cpp", "jat", "j.at("): "gated-dev: hlsl vector from_json, preset/config JSON; user config read is inside the try above",
    # dent
    ("librecomp/src/mods.cpp", "dent", "s7597_old ? mod_path.is_regular_file()"): "gated: ROGUESQ_S7597_MODSCAN=0 old-form arm only (XC-1 fix)",
    ("librecomp/src/mods.cpp", "dent", "(s7597_old ? mod_path.is_directory()"): "gated: same old-form arm",
    # thread
    ("src/main/rt64_render_context.cpp", "thread", "std::thread([c = cmd]"): "once: stall self-sample, s_sd_sampled latch (one per run)",
    ("src/main/upstream_compat.cpp", "thread", "std::thread([rdram] {"): G,
    ("librecomp/src/pi.cpp", "thread", "std::thread([ms] {"): "gated: s7969 save-rewrite test plant, only under ROGUESQ_S7969_SAVE_TICK_MS>0 (default off)",
    ("src/main/upstream_compat.cpp", "thread", "std::thread([]() {"): G,
    ("src/main/upstream_compat.cpp", "thread", "std::thread([] {"): G,
    ("src/main/upstream_compat.cpp", "thread", "std::thread([s4580_id]"): "gated: s4580::on() VI-recv census, one per blocked recv; off by default",
    ("librecomp/src/recomp.cpp", "thread", "std::thread game_thread{"): "boot: single game thread",
    ("librecomp/src/pi.cpp", "thread", "save_context.saving_thread = std::thread{"): "boot: single saving thread",
    ("src/main/main.cpp", "thread", "std::thread(s4578_poll, rdram)"): G,
    ("src/main/main.cpp", "thread", "std::thread([rdp, mode]()"): "gated: ROGUESQ_GODMODE3, s_god3 latch",
    ("src/main/main.cpp", "thread", "std::thread(reader).detach(); std::thread(writer)"): "boot: async stderr pair (s6979), once at startup",
    ("src/main/main.cpp", "thread", "std::thread([at]"): G,
    ("src/main/main.cpp", "thread", "std::thread([ct]"): G,
    ("src/main/main.cpp", "thread", "std::thread([] { for (int i = 0; i < 100000; i++) s7354_race_ctl_var++; })"): G,
    ("src/main/main.cpp", "thread", "std::thread([] {"): G,
    ("src/main/main.cpp", "thread", "std::thread([mt]"): G,
    ("ultramodern/src/mesgqueue.cpp", "thread", "std::thread([] {"): G,
    ("ultramodern/src/events.cpp", "thread", "std::thread(run, f, us)"): "gated: ROGUESQ_G1E_THREADS sampler, inside a static-init lambda (once)",
    ("ultramodern/src/threads.cpp", "thread", "context->host_thread = std::thread{"): "bounded: one host thread per guest osStartThread; guest thread count is fixed (~10, class TH s7592)",
    ("ultramodern/src/threads.cpp", "thread", "thread_cleaner_thread = std::thread{"): "boot: single cleaner",
    ("librecomp/src/mods.cpp", "thread", "make_unique<std::thread>(&ModContext::dirty_mod_configuration_thread_process"): "boot: single mod-config thread",
    ("ultramodern/src/timer.cpp", "thread", "timer_context.thread = std::thread{"): "boot: single timer thread",
    ("ultramodern/src/events.cpp", "thread", "events_context.sp.gfx_thread = std::thread{"): "boot: single",
    ("ultramodern/src/events.cpp", "thread", "events_context.sp.task_thread = std::thread{"): "boot: single",
    ("ultramodern/src/events.cpp", "thread", "events_context.vi.thread = std::thread{"): "boot: single",
    ("ultramodern/src/events.cpp", "thread", "std::thread{ [] {"): "boot: single helper (VI-side), started once in init_events",
    ("rt64/src/hle/rt64_present_queue.cpp", "thread", "new std::thread(&PresentQueue::threadLoop"): "boot: single",
    ("rt64/src/hle/rt64_workload_queue.cpp", "thread", "new std::thread(&WorkloadQueue::"): "boot: render + idle threads",
    ("rt64/src/render/rt64_framebuffer_renderer.cpp", "thread", "t_s7384Planted"): G,
    ("rt64/src/render/rt64_raster_shader.cpp", "thread", "make_unique<std::thread>(&RasterShaderUber::threadCreatePipelines"): "boot: fixed pipeline-thread pool",
    ("rt64/src/render/rt64_texture_cache.cpp", "thread", "make_unique<std::thread>(&StreamThread::loop"): "boot: fixed stream pool",
    ("rt64/src/render/rt64_texture_cache.cpp", "thread", "uploadThread = std::make_unique<std::thread>"): "boot: single",
    ("rt64/src/render/rt64_buffer_uploader.cpp", "thread", "new std::thread(&BufferUploader::threadLoop"): "boot: single per uploader",
    ("rt64/src/render/rt64_raster_shader_cache.cpp", "thread", "make_unique<std::thread>(&CompilationThread::loop"): "boot: fixed compile pool",
}
FIXED = ["XC-1 s7597: mods.cpp scan_mod_folder throwing directory_entry::is_regular_file/is_directory + iterator ++ aborted "
         "boot (rc134) on a mods/ symlink loop (ELOOP) or a link into an unreadable folder (EACCES); now ec forms + [s7597-io] skip"]


def short(path):
    return path.replace("lib/N64ModernRuntime/", "").replace("lib/rt64/", "rt64/")


def census(plant=False, drop=None):
    rows = dict(ROWS)
    if drop: rows.pop(drop)
    seen, open_, counts = set(), [], {}
    for d in DIRS:
        for dp, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(dp, f); rel = os.path.relpath(p, ROOT)
                if not f.endswith(EXT) or SKIP.search("/" + rel): continue
                text = open(p, errors="replace").read()
                if plant and rel.endswith("librecomp/src/mods.cpp"):
                    text = text.replace("        if (s7597_reg) {", "        if (mod_path.is_regular_file()) { // planted_control", 1)
                for ln, line in enumerate(text.split("\n"), 1):
                    code = re.sub(r"//.*", "", line) if "planted_control" not in line else line
                    bare = re.sub(r'"([^"\\]|\\.)*"', '""', code)
                    for kind, rx in KINDS:
                        if not rx.search(bare): continue
                        counts[kind] = counts.get(kind, 0) + 1
                        if kind == "thread" and ONCE.search(code): continue
                        cands = [k for k in rows if k[0] == short(rel) and k[1] == kind and k[2] in code]
                        key = max(cands, key=lambda k: len(k[2])) if cands else None
                        if key: seen.add(key)
                        else: open_.append(f"{rel}:{ln} {kind} {line.strip()[:90]}")
    stale = [k for k in rows if k not in seen]
    return open_, stale, counts, len(seen)


def main():
    o, st, counts, n = census()
    print(f"[s7597-xc] sites {counts} rows matched={n}/{len(ROWS)} open={len(o)} stale={len(st)}")
    verd = {}
    for v in ROWS.values(): verd[v.split(":")[0]] = verd.get(v.split(":")[0], 0) + 1
    print("[s7597-xc] verdicts", verd)
    for x in o: print("  OPEN", x)
    for k in st: print("  STALE", k)
    for x in FIXED: print("  FIXED", x)
    ok = not o and not st
    if "--controls" in sys.argv:
        c1 = census(plant=True)[0]; c2 = census(drop=next(iter(ROWS)))[0]
        f1, f2 = any("planted_control" in x for x in c1), len(c2) >= 1
        print(f"[s7597-xc] controls plant={'FIRED' if f1 else 'MISSED'} drop={'FIRED' if f2 else 'MISSED'} ({int(f1)+int(f2)}/2)")
        ok = ok and f1 and f2
    sys.exit(0 if ok else 1)


main()
