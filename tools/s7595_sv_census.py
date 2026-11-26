#!/usr/bin/env python3
"""s7595 class SV: save I/O failure census + offline write/read-path harness.

Census (default): every file-system call in the save path (librecomp files.cpp + pi.cpp save functions) must match a
classified row: what happens when it fails. --controls plants an unclassified call and drops a row; both must be caught.

--harness: extracts the REAL update_save_file / read_save_file text from pi.cpp and files.cpp verbatim, compiles them into a
host program with stubbed save_context/message_box (same fprintf as ultramodern + our main.cpp callback), and runs forced
failures on temp dirs (and a 1 MB disk image for disk-full). Scores per scenario: main/.bak sha256 survival, message lines,
call wall ms, thrown exceptions. Planted control (pre-s7357 unchecked close) must show the destroyed main.
The owner save (build/saves) is never touched; ROGUESQ_NO_SAVE_WRITE is not involved (the harness has no gate).
"""
import hashlib, os, re, shutil, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LR = os.path.join(ROOT, "lib/N64ModernRuntime/librecomp")
PI = os.path.join(LR, "src/pi.cpp")
FILES = os.path.join(LR, "src/files.cpp")
OUT = os.path.join(ROOT, "scratch/s7595")

CALL = re.compile(r"(?:(?<![\w:])(?:recomp::|ultramodern::error_handling::)?(std::ifstream|std::ofstream|::open|::fsync|::close|fopen|std::filesystem::\w+|open_input_file_with_backup|open_input_backup_file|open_output_file_with_backup|finalize_output_file_with_backup|create_directories|message_box)|(\.write|\.read|\.close))(?:\s+\w+)?\s*[({]")

# (file, function, call) -> failure behaviour. Verdict ok = failure reported/handled and the existing save survives.
ROWS = {
    ("files.cpp", "open_input_backup_file", "std::ifstream"): "ok: caller tests good()",
    ("files.cpp", "open_input_file_with_backup", "std::ifstream"): "ok: !good() -> falls back to .bak",
    ("files.cpp", "open_input_file_with_backup", "open_input_backup_file"): "ok: fallback",
    ("files.cpp", "open_output_file_with_backup", "std::ofstream"): "ok: caller tests good() -> message, main untouched",
    ("files.cpp", "finalize_output_file_with_backup", "std::filesystem::exists"): "ok: ec form, false -> skip bak copy",
    ("files.cpp", "finalize_output_file_with_backup", "std::filesystem::copy_file"): "ok: ec checked -> return false before rename (main intact; .bak may be short)",
    ("files.cpp", "finalize_output_file_with_backup", "::open"): "ok: fd<0 skips fsync only (rename still atomic)",
    ("files.cpp", "finalize_output_file_with_backup", "::fsync"): "ok-unchecked: durability only, rename atomic",
    ("files.cpp", "finalize_output_file_with_backup", "::close"): "ok-unchecked: read-only fd",
    ("files.cpp", "finalize_output_file_with_backup", "std::filesystem::rename"): "ok: ec -> false -> message, main intact",
    ("files.cpp", "finalize_output_file_with_backup", "std::filesystem::remove"): "ok: old-finalize arm only, ec form",
    ("pi.cpp", "update_save_file", "open_output_file_with_backup"): "ok: good() tested",
    ("pi.cpp", "update_save_file", ".write"): "ok: failbit sticky, tested after close (s7357)",
    ("pi.cpp", "update_save_file", ".close"): "ok: fail() tested -> no finalize (s7357)",
    ("pi.cpp", "update_save_file", "std::filesystem::is_directory"): "ok s7969 (class UE): error_code form, non-throwing; only classifies a failure as folder gone vs write failing",
    ("pi.cpp", "update_save_file", "finalize_output_file_with_backup"): "ok: false -> message",
    ("pi.cpp", "update_save_file", "message_box"): "ok: stderr only (ultramodern + main.cpp callback), non-blocking",
    ("pi.cpp", "read_save_file", "std::filesystem::create_directories"): "FIXED s7595 (SV-1): was the throwing form -> std::terminate at boot (rc134 0.7 s); now error_code + [s7595-io] (old form kept only under ROGUESQ_S7595_DIRS=0)",
    ("recomp.cpp", "initialize_mods", "std::filesystem::create_directories"): "FIXED s7595 (SV-2): mods/mod_config, same throwing form at boot (rc134 0.3 s); now error_code + [s7595-io]",
    ("pi.cpp", "read_save_file", "open_input_file_with_backup"): "ok: good() tested; else zero buffer",
    ("pi.cpp", "read_save_file", ".read"): "ok: gcount checked (s7357/s7429)",
    ("pi.cpp", "read_save_file", "open_input_backup_file"): "ok: good()+gcount checked",
    ("pi.cpp", "read_save_file", "message_box"): "ok s7967 (class CS): stderr only, non-blocking; unreadable cloud placeholder -> no-save notice",
}
FUNCS = {"files.cpp": None, "pi.cpp": ["update_save_file", "read_save_file", "flush_save_file"], "recomp.cpp": ["initialize_mods"]}
RECOMP = os.path.join(LR, "src/recomp.cpp")


def func_spans(text):
    """yield (name, body) for top-level function definitions."""
    for m in re.finditer(r"^[A-Za-z][\w:<>&* \t]*?\b([\w:]+)\s*\([^;{]*\)\s*\{", text, re.M):
        name = m.group(1).split("::")[-1]
        i = m.end(); d = 1
        while d and i < len(text):
            d += {"{": 1, "}": -1}.get(text[i], 0); i += 1
        yield name, m.start(), text[m.start():i]


def extract(text, name):
    for n, _, body in func_spans(text):
        if n == name:
            return body
    raise SystemExit(f"function {name} not found")


def census(plant=None, drop=None):
    rows = dict(ROWS)
    if drop: rows.pop(drop, None)
    seen, open_ = set(), []
    for fn, path in (("files.cpp", FILES), ("pi.cpp", PI), ("recomp.cpp", RECOMP)):
        text = open(path).read()
        if plant and fn == "pi.cpp":
            text = text.replace("void read_save_file() {", "void read_save_file() {\n    fopen(\"x\", \"r\");", 1)
        for name, _, body in func_spans(text):
            if FUNCS[fn] is not None and name not in FUNCS[fn]:
                continue
            body = body[body.index("{"):] if ")" in body else body  # drop the signature
            for c in CALL.finditer(re.sub(r"//.*", "", body)):
                call = c.group(1) or c.group(2)
                if call == "std::filesystem::path": continue  # value type, no I/O
                key = (fn, name, call)
                if key in rows:
                    seen.add(key)
                elif (fn, name) != ("pi.cpp", "flush_save_file"):
                    open_.append(key)
    missing = [k for k in rows if k not in seen]
    return seen, open_, missing, rows


HARNESS_HEAD = r'''
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <string>
#include <vector>
#include <fcntl.h>
#include <unistd.h>
namespace recomp {
    std::ifstream open_input_file_with_backup(const std::filesystem::path& filepath, std::ios_base::openmode mode = std::ios_base::in);
    std::ifstream open_input_backup_file(const std::filesystem::path& filepath, std::ios_base::openmode mode = std::ios_base::in);
    std::ofstream open_output_file_with_backup(const std::filesystem::path& filepath, std::ios_base::openmode mode = std::ios_base::out);
    bool finalize_output_file_with_backup(const std::filesystem::path& filepath);
}
static int g_msgs = 0;
namespace ultramodern { namespace error_handling {
    void message_box(const char* msg) { fprintf(stderr, "%s\n", msg); fprintf(stderr, "[Error] %s\n", msg); g_msgs++; }
}
    std::filesystem::path g_path;
    std::filesystem::path get_save_file_path() { return g_path; }
}
struct { std::vector<char> save_buffer; std::mutex save_buffer_mutex; std::mutex save_file_mutex;
         std::atomic<uint64_t> write_gen{0}; uint64_t saved_gen = 0; } save_context;
'''

HARNESS_MAIN = r'''
int main(int argc, char** argv) {
    // usage: h write|read|readx <save path> <fill char> <n calls>
    std::string mode = argv[1];
    ultramodern::g_path = argv[2];
    save_context.save_buffer.assign(512, argv[3][0]);
    int n = atoi(argv[4]);
    auto t0 = std::chrono::steady_clock::now();
    int thrown = 0; std::string what;
    for (int i = 0; i < n; i++) {
        try {
            if (mode == "write") { save_context.write_gen++; update_save_file(); }
            else read_save_file();
        } catch (const std::exception& e) { thrown++; what = e.what(); }
    }
    double ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count();
    std::string head(save_context.save_buffer.begin(), save_context.save_buffer.begin() + 4);
    size_t nz = 0; for (char c : save_context.save_buffer) nz += c != 0;
    printf("RESULT msgs=%d thrown=%d ms=%.2f saved_gen=%llu buf_head=%s buf_nonzero=%zu what=[%s]\n", g_msgs, thrown, ms,
           (unsigned long long)save_context.saved_gen, mode == "write" ? "-" : head.c_str(), nz, what.c_str());
    return 0;
}
'''


def build(plant):
    pi = open(PI).read()
    parts = [HARNESS_HEAD]
    for f in ("update_save_file", "read_save_file"):
        body = extract(pi, f)
        if f == "update_save_file":
            body = body.replace('if (getenv("ROGUESQ_NO_SAVE_WRITE")) { return; }', "/* gate dropped in the harness */")
            if plant:
                n = body.count("if (save_file.fail())")
                assert n == 1, n
                body = body.replace("if (save_file.fail())", "if (false && save_file.fail())")
        parts.append(body)
    parts.append(HARNESS_MAIN)
    src = os.path.join(OUT, "wtest_plant.cpp" if plant else "wtest.cpp")
    exe = src[:-4]
    open(src, "w").write("\n".join(parts))
    subprocess.check_call(["clang++", "-std=c++20", "-O1", "-w", src, FILES, "-I", os.path.join(LR, "include/librecomp"), "-o", exe])
    return exe


def sha(p):
    try:
        if os.path.isdir(p): return "DIR"
        return hashlib.sha256(open(p, "rb").read()).hexdigest()[:10]
    except FileNotFoundError: return "none"
    except PermissionError: return "noperm"
    except OSError: return "none"


def size(p):
    try: return os.path.getsize(p)
    except OSError: return -1


def run(exe, mode, path, ch, n):
    r = subprocess.run([exe, mode, path, ch, str(n)], capture_output=True, text=True, errors="replace")
    line = [l for l in r.stdout.splitlines() if l.startswith("RESULT")]
    return (line[0][7:] if line else f"NO_RESULT rc={r.returncode} err={r.stderr[-200:]!r}"), r.stderr.count("[Error] ")


def mkdisk(tag):
    img = os.path.join(OUT, f"{tag}.dmg"); mnt = os.path.join(OUT, f"mnt_{tag}")
    if os.path.exists(img): os.remove(img)
    os.makedirs(mnt, exist_ok=True)
    subprocess.check_call(["hdiutil", "create", "-size", "1m", "-fs", "HFS+", "-volname", tag, img], stdout=subprocess.DEVNULL)
    subprocess.check_call(["hdiutil", "attach", "-nobrowse", "-mountpoint", mnt, img], stdout=subprocess.DEVNULL)
    return img, mnt


def fill(mnt):
    fd = os.open(os.path.join(mnt, "fill"), os.O_WRONLY | os.O_CREAT, 0o644)
    try:
        while True:
            os.write(fd, b"\0" * 4096)
    except OSError:
        pass
    os.close(fd)
    for i in range(64):  # take the last fragments / catalog nodes too
        try:
            g = os.open(os.path.join(mnt, f"f{i}"), os.O_WRONLY | os.O_CREAT, 0o644); os.write(g, b"x" * 512); os.close(g)
        except OSError:
            break
    st = os.statvfs(mnt)
    print(f"  fill: free bytes={st.f_bavail * st.f_frsize}")


def harness():
    os.makedirs(OUT, exist_ok=True)
    exe, exep = build(False), build(True)
    res = []
    td = tempfile.mkdtemp(prefix="s7595_", dir=OUT)

    def setup(d, main=b"A" * 512, bak=b"B" * 512):
        os.makedirs(d, exist_ok=True)
        if main is not None: open(os.path.join(d, "s.bin"), "wb").write(main)
        if bak is not None: open(os.path.join(d, "s.bin.bak"), "wb").write(bak)
        return os.path.join(d, "s.bin")

    def rec(name, kind, p, out, msgs, before):
        after = (sha(p), sha(p + ".bak"), size(p), size(p + ".bak"))
        res.append(f"name={name} kind={kind} main={before[0]}->{after[0]}({after[2]}) bak={before[1]}->{after[1]}({after[3]}) {out} errlines={msgs}")
        print(res[-1])

    A, B, N = (hashlib.sha256(c * 512).hexdigest()[:10] for c in (b"A", b"B", b"N"))
    print(f"hashes A={A} B={B} N={N}")
    # --- write path ---
    for name, e, prep, n in (
        ("w_ok", exe, None, 1),
        ("w_rodir", exe, "ro", 1),
        ("w_rename_fail", exe, "rename", 1),
        ("w_main_is_dir", exe, "maindir", 1),
        ("w_rodir_x100", exe, "ro", 100),
    ):
        d = os.path.join(td, name)
        p = setup(d, main=None if prep == "maindir" else b"A" * 512)
        if prep == "maindir": os.makedirs(os.path.join(p, "x"))
        if prep == "rename": open(p + ".temp", "wb").write(b"old")
        if prep in ("ro", "rename"): os.chmod(d, 0o555)
        before = (sha(p), sha(p + ".bak"))
        out, m = run(e, "write", p, "N", n)
        os.chmod(d, 0o755)
        rec(name, "write", p, out, m, before)
    for name, e in (("w_disk_full", exe), ("w_disk_full_PLANT_unchecked_close", exep)):
        img, mnt = mkdisk(name[:12] + ("P" if e == exep else ""))
        try:
            p = setup(os.path.join(mnt, "saves"))
            open(p + ".temp", "wb").close()  # left by an earlier save: the open (O_TRUNC) succeeds, the data write cannot
            fill(mnt)
            before = (sha(p), sha(p + ".bak"))
            out, m = run(e, "write", p, "N", 1)
            rec(name, "write", p, out, m, before)
        finally:
            subprocess.call(["hdiutil", "detach", "-force", mnt], stdout=subprocess.DEVNULL)
            os.remove(img)
    # --- read path ---
    for name, main, bak, prep in (
        ("r_missing", None, None, None),
        ("r_zero_main_full_bak", b"", b"B" * 512, None),
        ("r_trunc_no_bak", b"A" * 100, None, None),
        ("r_garbage", os.urandom(512), None, None),
        ("r_bak_only", None, b"B" * 512, None),
        ("r_long", b"A" * 1000, None, None),
        ("r_unreadable_main", b"A" * 512, b"B" * 512, "chmod000"),
        ("r_main_is_dir", None, b"B" * 512, "maindir"),
        ("r_saves_is_file", None, None, "savesfile"),
        ("r_ro_parent_no_saves", None, None, "roparent"),
    ):
        d = os.path.join(td, name, "saves")
        if prep == "savesfile":
            os.makedirs(os.path.dirname(d)); open(d, "w").write("not a dir")
            p = os.path.join(d, "s.bin")
        elif prep == "roparent":
            os.makedirs(os.path.dirname(d)); os.chmod(os.path.dirname(d), 0o555)
            p = os.path.join(d, "s.bin")
        else:
            p = setup(d, main, bak)
            if prep == "chmod000": os.chmod(p, 0)
            if prep == "maindir": os.makedirs(p)
        before = (sha(p), sha(p + ".bak"))
        out, m = run(exe, "read", p, "Z", 1)
        if prep == "chmod000": os.chmod(p, 0o644)
        if prep == "roparent": os.chmod(os.path.dirname(d), 0o755)
        rec(name, "read", p, out, m, before)
    shutil.rmtree(td, ignore_errors=True)
    open(os.path.join(OUT, "harness.txt"), "w").write("\n".join(res) + "\n")
    return res


def main():
    if "--harness" in sys.argv:
        harness(); return
    seen, open_, missing, rows = census()
    for k in sorted(seen):
        print(f"{k[0]}:{k[1]}:{k[2]} -> {rows[k]}")
    print(f"SV census: rows={len(seen)} open={len(open_)} missing_rows={len(missing)} defects_open={sum(1 for k in seen if rows[k].startswith('SV-'))} fixed={sum(1 for k in seen if rows[k].startswith('FIXED'))}")
    for k in open_: print("OPEN", k)
    for k in missing: print("MISSING", k)
    if "--controls" in sys.argv:
        _, o1, _, _ = census(plant=True)
        _, o2, _, _ = census(drop=("pi.cpp", "update_save_file", ".close"))
        c1 = any(k[2] == "fopen" for k in o1); c2 = ("pi.cpp", "update_save_file", ".close") in o2
        print(f"controls: planted fopen caught={c1} dropped .close row caught={c2} -> {int(c1)+int(c2)}/2")
        if not (c1 and c2): sys.exit(1)
    sys.exit(1 if open_ or missing else 0)


if __name__ == "__main__":
    main()
