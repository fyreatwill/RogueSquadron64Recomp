#!/usr/bin/env python3
"""s7596 class FS: every THROWING std::filesystem call (no std::error_code argument) in the shipped host code.

Scope: src/, librecomp/src, ultramodern/src, lib/rt64/src (skips tests/tools/contrib/examples/demos). A call is
std::filesystem::<fn>(...) or a directory_iterator constructor, parens balanced across lines; it is EC-form when its
argument text names an error_code variable (ec / *_ec / error_code). Path algebra (path, u8path, ...) cannot throw a
filesystem_error and is skipped. Every throwing call must match a classified ROW (file, fn, argument prefix) -> verdict.
--controls: (1) plant a throwing remove() in recomp.cpp, (2) drop one row; both must report open; exit 0 only if
the real census has 0 open + 0 stale rows and both controls fire.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRS = ["src", "lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src", "lib/rt64/src"]
SKIP = re.compile(r"/(tests?|tools|contrib|examples?|demos?)/")
EXT = (".cpp", ".cc", ".c", ".h", ".hpp", ".mm")
NONTHROW = {"path", "u8path", "directory_entry", "file_status", "perms", "copy_options", "directory_options",
            "file_type", "filesystem_error", "space_info", "status_known"}
CALL = re.compile(r"std::filesystem::(\w+)\s*([({])")
EC = re.compile(r"\b(\w*_ec|ec|error_code)\b")

# (file, fn, normalized-arg prefix) -> verdict. ok-* = cannot abort the owner's run; FIXED = was owner-reachable.
ROWS = {
    ("librecomp/src/recomp.cpp", "create_directories", "config_path / mods_directory"): "gated: ROGUESQ_S7595_DIRS=0 old-form arm only (SV-2 fix)",
    ("librecomp/src/recomp.cpp", "create_directories", "config_path / mod_config_directory"): "gated: ROGUESQ_S7595_DIRS=0 old-form arm only (SV-2 fix)",
    ("librecomp/src/pi.cpp", "create_directories", "save_file_path.parent_path()"): "gated: ROGUESQ_S7595_DIRS=0 old-form arm only (SV-1 fix)",
    ("librecomp/src/recomp.cpp", "remove", "path"): "FIXED s7596 (FS-1): check_stored_rom/load_stored_rom removed an invalid stored ROM with the throwing form at EVERY boot (check_all_stored_roms x2) -> std::terminate when it cannot be deleted; now remove_stored_rom() ec + [s7596-io]; this row is its ROGUESQ_S7596_RM=0 old-form arm",
    ("librecomp/src/mod_config_api.cpp", "absolute", "save_file_path"): "gated: mod export recomp_get_save_file_path; RS64 ships no mods; throws only if getcwd fails",
    ("librecomp/src/mod_config_api.cpp", "absolute", "mod_folder_path"): "gated: mod export; no mods",
    ("librecomp/src/mod_config_api.cpp", "absolute", "mod_file_path"): "gated: mod export; no mods",
    ("librecomp/src/mods.cpp", "absolute", "path"): "dead: _WIN32 LoadLibraryExW branch",
    ("rt64/src/hle/rt64_application.cpp", "is_directory", "dirPath"): "gated: checkDirectoryCreated runs only when userPaths non-empty; RS64 sets detectDataPath=false and no dataPath (rt64_render_context.cpp appConfig) -> isEmpty() short-circuits",
    ("rt64/src/hle/rt64_application.cpp", "create_directories", "dirPath"): "gated: same checkDirectoryCreated, unreachable with empty dataPath",
    ("rt64/src/common/rt64_user_paths.cpp", "exists", "configPath"): "gated: detectDataPath only when appConfig.detectDataPath (false in RS64)",
    ("rt64/src/render/rt64_texture_cache.cpp", "is_regular_file", "replacementDirectory.dirOrZipPath"): "gated-dev: F1 inspector 'Load pack/directory' button (texture replacement); path comes from the OS file dialog; throws only on stat errors other than ENOENT",
    ("rt64/src/render/rt64_texture_cache.cpp", "is_directory", "replacementDirectory.dirOrZipPath"): "gated-dev: same inspector texture-pack load",
    ("rt64/src/render/rt64_texture_cache.cpp", "exists", "databasePath"): "gated-dev: saveReplacementDatabase, inspector 'Save directory' button only",
    ("rt64/src/render/rt64_texture_cache.cpp", "exists", "databaseOldPath"): "gated-dev: same",
    ("rt64/src/common/rt64_filesystem_directory.h", "recursive_directory_iterator", "directoryPath"): "gated-dev: FileSystemDirectory::create, only from the inspector texture-pack load (an unreadable subfolder WOULD terminate; dev GUI only, owner never loads packs)",
    ("rt64/src/common/rt64_filesystem_directory.h", "relative", "dirIterator->path(), directoryPath"): "gated-dev: same iterator",
    ("rt64/src/common/rt64_filesystem_directory.h", "exists", "directoryPath / std::filesystem::u8path(path)"): "gated-dev: FileSystemDirectory::exists, texture packs only",
    ("rt64/src/common/rt64_filesystem_directory.h", "exists", "directoryPath"): "gated-dev: FileSystemDirectory::create, texture packs only",
    ("rt64/src/gui/rt64_debugger_inspector.cpp", "relative", "textureFilename, directoryPath"): "gated-dev: inspector texture dump UI",
}
# FS-2 (s7596): main.cpp current_path() now ec form; no row, so a reverted throwing call reads OPEN.


def short(path):
    return path.replace("lib/N64ModernRuntime/", "").replace("lib/rt64/", "rt64/")


def calls(text):
    for m in CALL.finditer(text):
        fn, op = m.group(1), m.group(2)
        if fn in NONTHROW and not fn.endswith("iterator"):
            continue
        close = ")" if op == "(" else "}"
        i, d = m.end(), 1
        while d and i < len(text):
            c = text[i]
            if c in "({": d += 1
            elif c in ")}": d -= 1
            i += 1
        args = re.sub(r"\s+", " ", text[m.end():i - 1]).strip()
        # `std::filesystem::recursive_directory_iterator dirIterator;` declarations / `static const ... endIterator;` are not calls
        yield fn, args, text.count("\n", 0, m.start()) + 1


def census(plant=False, drop=None):
    rows = dict(ROWS)
    if drop: rows.pop(drop)
    seen, open_, ecn = set(), [], 0
    for d in DIRS:
        for dp, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(dp, f); rel = os.path.relpath(p, ROOT)
                if not f.endswith(EXT) or SKIP.search("/" + rel): continue
                text = open(p, errors="replace").read()
                if plant and rel.endswith("librecomp/src/recomp.cpp"):
                    text = text.replace("void recomp::check_all_stored_roms() {", "void recomp::check_all_stored_roms() {\n    std::filesystem::remove(planted_control);", 1)
                text = re.sub(r"//[^\n]*", "", text)
                for fn, args, line in calls(text):
                    if EC.search(args): ecn += 1; continue
                    cands = [k for k in rows if k[0] == short(rel) and k[1] == fn and args.startswith(k[2])]
                    key = max(cands, key=lambda k: len(k[2])) if cands else None
                    if key: seen.add(key)
                    else: open_.append(f"{rel}:{line} {fn}({args[:60]})")
    stale = [k for k in rows if k not in seen]
    return open_, stale, ecn, len(seen)


def main():
    o, st, ecn, n = census()
    print(f"[s7596-fs] throwing rows matched={n} open={len(o)} stale={len(st)} ec_form_calls={ecn}")
    for x in o: print("  OPEN", x)
    for k in st: print("  STALE", k)
    for k, v in ROWS.items():
        if v.startswith("FIXED"): print("  ", k[0], k[1], "->", v[:110])
    ok = not o and not st
    if "--controls" in sys.argv:
        c1 = census(plant=True)[0]; c2 = census(drop=next(iter(ROWS)))[0]
        f1, f2 = any("planted_control" in x for x in c1), len(c2) >= 1
        print(f"[s7596-fs] controls plant={'FIRED' if f1 else 'MISSED'} drop={'FIRED' if f2 else 'MISSED'} ({int(f1)+int(f2)}/2)")
        ok = ok and f1 and f2
    sys.exit(0 if ok else 1)


main()
