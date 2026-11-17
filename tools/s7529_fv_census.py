#!/usr/bin/env python3
"""s7529 class FV census: host-side containers keyed by a guest address that are filled
when guest state appears and must be invalidated when the guest reuses the address.

Enumerates every map/set/vector declaration with an integer / PTR key in the port's
runtime sources (librecomp, ultramodern, rt64 hle, src/), then classifies each:
  diag      identifier or enclosing gate is an sNNNN diagnostic (logging-only state)
  local     function-local / per-call container (lifetime ends with the call)
  rule      explicit row in RULES below: class + key + filler + eraser + reuse event;
            the eraser regex MUST match in the file, else the row FAILS (eraser lost)
  UNCLASSIFIED  a static/global/member container with no rule -> FAIL (census incomplete)

  python3 tools/s7529_fv_census.py            # census table, exit 1 on any FAIL
  python3 tools/s7529_fv_census.py --controls # planted fixtures must be caught
"""
import os, re, sys, tempfile

ROOTS = ["lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src",
         "lib/rt64/src/hle", "src/main", "src/rsp"]
DECL = re.compile(r'(std::)?(unordered_map|map|unordered_set|set|flat_hash_map)<\s*(u?int(32|64)_t|PTR\(\w+\)|uint32_t|int32_t|int)\b')
DIAG_ID = re.compile(r'\b(g_|s_)?s\d{3,4}\w*|\bhist\b|\bseen\b|\bfires\b|\bby_pc\b|\bmode_seen\b|\bcounts\b|\btab\b|\bbypc\b|\bby\b|\brail_by_pc\b|\beps\b|\breported\b')

# (file suffix, identifier, class, key, filler, eraser_regex, reuse event / reason)
RULES = [
    ("librecomp/src/overlays.cpp", "func_map", "H-latent-fix->FIXED(s7528)", "func vram",
     "load_overlay", r"rs64_s7528_pre_load|func_map\.erase", "overlay swap at same vram: s7528 evicts overlapping sections"),
    ("librecomp/src/overlays.cpp", "code_sections_by_rom", "H-dead", "section rom addr",
     "init (static section table)", None, "ROM is immutable; filled once from the recompiled section table"),
    ("librecomp/src/overlays.cpp", "patch_code_sections_by_rom", "H-dead", "patch section rom addr",
     "init", None, "ROM is immutable"),
    ("librecomp/src/overlays.cpp", "manual_patch_symbols_by_vram", "H-dead", "patch symbol vram",
     "init", None, "static symbol table, not guest-state derived"),
    ("ultramodern/src/timer.cpp", "active_timers", "H-canon", "guest OSTimer*",
     "AddTimerAction", r"active_timers\.erase", "osStopTimer/fire erase; re-set of a live struct scanned+erased (s7397 carry path)"),
    ("rt64/src/hle/rt64_framebuffer_manager.h", "framebuffers", "H-canon", "fb rdram addr",
     "SET_COLOR_IMAGE", None, "RAMHash recheck + performDiscards (rt64_framebuffer_manager.cpp; EZ s7500/s7501 audited)"),
    ("rt64/src/hle/rt64_framebuffer_manager.h", "tileCopies", "H-canon", "tile copy id",
     "createTileCopy", None, "tileCopies.clear() in performDiscards"),
    ("rt64/src/hle/rt64_framebuffer_manager.h", "reinterpretTileCache", "H-canon", "hash",
     "reinterpret", None, "cleared per frame (reinterpretTileCache.clear)"),
    ("rt64/src/hle/rt64_shared_queue_resources.h", "colorImageAddressSet", "H-canon", "fb addr",
     "per workload", None, "cleared every workload (rt64_state.cpp colorImageAddressSet.clear)"),
    ("rt64/src/hle/rt64_framebuffer_changes.h", "changesMap", "H-canon", "change id",
     "per workload", None, "per-workload object"),
    ("rt64/src/hle/rt64_framebuffer.h", "tileCopies", "H-canon", "tile copy id", "fb", None, "owned by Framebuffer, dies with performDiscards"),
    ("rt64/src/hle/rt64_rdp_tmem.h", "hashSet", "H-dead", "tmem content hash", "texture upload", None, "content-hashed, address-free"),
    ("rt64/src/hle/rt64_rdp_tmem.h", "dumpedSet", "H-dead", "tmem content hash", "dump", None, "content-hashed, dump-only"),
    ("ultramodern/src/threads.cpp", "g_live_ctx", "H-dead", "HOST UltraThreadContext*", "ctx ctor",
     r"g_live_ctx\.erase", "host pointer, erased in dtor; not a guest address"),
    ("src/rsp/dpc_bridge.cpp", "g_cine_fb_owner_slot", "H-dead", "fb addr24", "SET_COLOR_IMAGE",
     None, "write-only: its query rt64_cine_fb_is_slot_owned has no caller in src/ or lib/ (PHASE 21 leftover)"),
    ("src/rsp/dpc_bridge.cpp", "frame_id_by_slot", "diag", "slot", "e9prov", r"frame_id_by_slot\.erase", "e9prov provenance log"),
    ("src/rsp/dpc_bridge.cpp", "frame_opcode_by_slot", "diag", "slot", "e9prov", None, "e9prov provenance log"),
    ("rt64/src/hle/rt64_game_frame.cpp", "workloadsModified", "H-canon", "workload id", "per frame",
     r"workloadsModified\.clear", "thread_local, cleared at each use"),
    ("rt64/src/hle/rt64_game_frame.cpp", "curCallHashMap", "H-canon", "call hash", "matchScene",
     r"curCallHashMap\.clear", "thread_local, cleared at each use"),
    ("rt64/src/hle/rt64_game_frame.cpp", "prevCallHashMap", "H-canon", "call hash", "matchScene",
     r"prevCallHashMap\.clear", "thread_local, cleared at each use"),
    ("rt64/src/hle/rt64_state.cpp", "colorImageAddressSet", "H-canon", "fb addr", "presentEarly",
     r"colorImageAddressSet\.clear", "thread_local, cleared at each use"),
    ("ultramodern/src/events.cpp", "symd", "diag", "host pc", "s6979b WAITI backtrace", None, "diagnostic"),
    ("ultramodern/src/threads.cpp", "m", "diag", "thread id", "Acc stats", None, "scheduling stats"),
    ("ultramodern/src/threads.cpp", "scaller", "diag", "caller", "shist", None, "scheduling stats"),
    ("src/main/upstream_compat.cpp", "byh", "local", "heap hdr", "g5a walk", None, "function-local walk index"),
    ("src/main/upstream_compat.cpp", "m", "diag", "key", "S6963U", None, "s6963 diagnostic struct"),
    ("src/main/upstream_compat.cpp", "c", "diag", "key", "S6963U", None, "s6963 diagnostic struct"),
    ("src/rsp/s7521_ucode_watch.cpp", "src28", "diag", "dma src", "s7521 watch", None, "s7521 diagnostic file"),
    ("src/main/upstream_compat.cpp", "s_s6702_free", "H-canon", "spill block addr", "spill alloc",
     r"s_s6702_free\.erase", "spill allocator free list; coalesced on release"),
    ("src/main/upstream_compat.cpp", "s_s6702_live", "H-canon", "spill block addr", "spill alloc",
     r"s_s6702_live\.erase", "rs_free -> s6702_release_locked; scene reset (s7326) releases wholesale"),
    ("src/main/upstream_compat.cpp", "s_s7326_tag", "H-canon", "spill block addr", "spill alloc",
     r"s_s7326_tag\.erase", "erased in s6702_release_locked"),
    ("src/main/upstream_compat.cpp", "s_s7326_released", "H-canon", "spill block addr", "scene reset",
     r"s_s7326_released\.erase", "erased when the block is reallocated"),
    ("src/main/upstream_compat.cpp", "s_s5041_freed", "H-canon", "freed heap ptr", "rs_free (FREE_CENSUS)",
     r"s_s5041_freed\.erase", "erased on rs_malloc of the same ptr"),
    ("src/main/upstream_compat.cpp", "s_s7317_live", "H-canon", "heap block", "rs_malloc hook",
     r"s_s7317_live\.erase", "rs_free erase + heapsync guest walk drops stale"),
    ("src/main/upstream_compat.cpp", "s_s7332_carve", "H-canon", "carve start", "heapsync",
     r"s_s7332_carve\.erase", "fallback-drop when the guest no longer carves it"),
]

def is_local(line):
    s = line.lstrip()
    return (len(line) - len(s)) > 0 and not s.startswith("static") and not s.startswith("thread_local") \
        and not re.search(r';\s*$', s) is None and not s.startswith("std::mutex")

def ident_of(line, m):
    tail = line[m.end():]
    # skip the rest of the template argument list
    depth, i = 1, 0
    while i < len(tail) and depth:
        if tail[i] == '<': depth += 1
        elif tail[i] == '>': depth -= 1
        i += 1
    mm = re.match(r'[\s&*]*(\w+)', tail[i:])
    return mm.group(1) if mm else "?"

def census(files, rules):
    rows, fails = [], 0
    for path in files:
        try: txt = open(path, errors="replace").read()
        except OSError: continue
        for ln, line in enumerate(txt.split("\n"), 1):
            code = line.split("//")[0]
            for m in DECL.finditer(code):
                ident = ident_of(code, m)
                pre = code[:m.start()]
                if pre.count("(") > pre.count(")"): continue  # function parameter
                if re.match(r'[^;]*>\s*[&*]?\s*\w+::', code[m.end():]): continue  # qualified return type
                if ident == "?" or "(" in code[m.end():m.end()+200].split(ident)[0]: continue
                if re.search(r'\b' + re.escape(ident) + r'\s*(=\s*nullptr\s*)?(,|\)\s*(const\s*)?[{;]?)\s*$', code): continue  # multi-line parameter
                if re.search(r'\b' + re.escape(ident) + r'\s*\(', code): continue  # function signature / return type
                rule = next((r for r in rules if path.endswith(r[0]) and r[1] == ident), None)
                if rule:
                    cls, why = rule[2], rule[6]
                    if rule[5] and not re.search(rule[5], txt):
                        cls, why = "FAIL-eraser-missing", "eraser /%s/ not found" % rule[5]; fails += 1
                elif DIAG_ID.search(ident) or re.search(r'\bs\d{4}', code):
                    cls, why = "diag", "sNNNN/logging-only state"
                elif is_local(line) and not line.lstrip().startswith("static"):
                    cls, why = "local", "function-local lifetime"
                else:
                    cls, why = "UNCLASSIFIED", "static/global/member with no rule"; fails += 1
                rows.append((path, ln, ident, cls, why))
    return rows, fails

def files_under(roots):
    out = []
    for r in roots:
        for dp, _, fns in os.walk(r):
            out += [os.path.join(dp, f) for f in fns if f.endswith((".cpp", ".h", ".hpp", ".c"))]
    return sorted(out)

def controls():
    ok = True
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "fixture_cache.cpp")
        open(p, "w").write("static std::unordered_map<uint32_t, int> g_planted_cache;\nvoid f(uint32_t a){ g_planted_cache[a]=1; }\n")
        rows, fails = census([p], RULES)
        c1 = fails == 1 and rows and rows[0][3] == "UNCLASSIFIED"
        print("control planted-unruled-cache:", "PASS" if c1 else "FAIL", rows)
        rules = RULES + [("fixture_cache.cpp", "g_planted_cache", "H-canon", "a", "f", r"g_planted_cache\.erase", "x")]
        rows, fails = census([p], rules)
        c2 = fails == 1 and rows[0][3] == "FAIL-eraser-missing"
        print("control ruled-but-eraser-missing:", "PASS" if c2 else "FAIL", rows)
        open(p, "a").write("void g(uint32_t a){ g_planted_cache.erase(a); }\n")
        rows, fails = census([p], rules)
        c3 = fails == 0 and rows[0][3] == "H-canon"
        print("control ruled-with-eraser:", "PASS" if c3 else "FAIL", rows)
        ok = c1 and c2 and c3
    # live: every RULES eraser must resolve, the s7528 fix must be present
    rows, fails = census(files_under(ROOTS), RULES)
    c4 = any(r[2] == "func_map" and r[3].startswith("H-latent-fix") for r in rows)
    print("control live-func_map-row-found:", "PASS" if c4 else "FAIL")
    return 0 if (ok and c4) else 1

def main():
    if "--controls" in sys.argv: sys.exit(controls())
    rows, fails = census(files_under(ROOTS), RULES)
    from collections import Counter
    cnt = Counter(r[3] for r in rows)
    for r in rows:
        if r[3] not in ("diag", "local"):
            print("%-58s %5d %-28s %-28s %s" % (r[0], r[1], r[2], r[3], r[4]))
    print("summary:", dict(cnt), "fails=%d" % fails)
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
