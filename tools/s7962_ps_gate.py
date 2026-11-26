#!/usr/bin/env python3
"""s7962 class PS (owner folder paths: spaces / non-ASCII / apostrophe / >255-char total). e2e scratch/s7962/e2e.zsh,
tools/s7962_ps_e2e.zsh: ROM, save (EEPROM b0..7), settings.txt, data root were fine in a 307-char
"Rogue Squadron ü/William's Games/..." folder (old and new); the crash-handler symbol table loaded 0 symbols when the exe
itself sat there (popen "nm -n '%s'": the apostrophe closed the quote) -> new 29057, same as the plain-dir control.
CONTROL: the pre-fix source (fdfb97972) puts a bare '%s' path into a shell command -> bad.
FIX: current host sources have no '%s' inside a popen/system command string and both sites use rs64_shell_quote.
MUTANT: re-planting the old nm format in a copy of main.cpp must be caught.
UNIT: rs64_shell_quote round-trips hostile names through /bin/sh (compiled here).
CENSUS: every fixed-size char[] fed by a path-ish snprintf in host code, with its size (all >=512, env-gated diagnostics)."""
import os, re, subprocess, sys, tempfile, glob
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
FILES = ["src/main/main.cpp", "src/main/rt64_render_context.cpp"]
DIRS = ["src/main", "lib/N64ModernRuntime/librecomp/src", "lib/N64ModernRuntime/ultramodern/src"]
SHELL = re.compile(r"""(popen|system|nm -n|/usr/bin/sample)[^\n]*'%s""")
def bad(srcs): return 1 if any(SHELL.search(s) for s in srcs) else 0
old = [subprocess.check_output(["git", "show", f"fdfb97972:{p}"], cwd=root, text=True) for p in FILES]
new = [open(os.path.join(root, p)).read() for p in FILES]
uses = all("rs64_shell_quote(" in s for s in new)
mut0 = new[0].replace('const std::string cmd = "nm -n " + rs64_shell_quote(exe_path) + " 2>/dev/null";',
                      'char cmd[4096]; snprintf(cmd, sizeof(cmd), "nm -n \'%s\' 2>/dev/null", exe_path);')
ob, nb, mb = bad(old), bad(new), bad([mut0] + new[1:])
print(f"CONTROL old_bad={ob} {'PASS' if ob == 1 else 'FAIL'}")
print(f"FIX new_bad={nb} uses_quote={uses} {'PASS' if nb == 0 and uses else 'FAIL'}")
print(f"MUTANT replanted_bad={mb} changed={mut0 != new[0]} {'PASS' if mb == 1 and mut0 != new[0] else 'FAIL'}")
names = ["William's Games", "a''b", "sp ace/ü", "'", "x'; echo PWNED; '"]
with tempfile.TemporaryDirectory() as t:
    c = os.path.join(t, "q.cpp"); e = os.path.join(t, "q")
    open(c, "w").write('#include "%s/src/main/rs64_shell_quote.h"\n#include <cstdio>\nint main(int n,char**v){std::fputs(rs64_shell_quote(v[1]).c_str(),stdout);}\n' % root)
    subprocess.check_call(["c++", "-std=c++17", c, "-o", e])
    rt = 0
    for nmv in names:
        q = subprocess.check_output([e, nmv], text=True)
        got = subprocess.check_output(["/bin/sh", "-c", "printf %s " + q], text=True)
        rt += got == nmv
print(f"UNIT roundtrip={rt}/{len(names)} {'PASS' if rt == len(names) else 'FAIL'}")
cen = []
for d in DIRS:
    for f in sorted(glob.glob(os.path.join(root, d, "*.cpp"))):
        L = open(f, errors="replace").read().split("\n")
        for i, l in enumerate(L, 1):
            m = re.search(r"char (\w*(path|fn|fp|file|dpath|ipath)\w*)\[(\d+)\]", l)
            if not m: continue
            fmt = " ".join(L[i - 1:i + 2]); fmt = fmt[fmt.find(m[1] + "["):]
            sm = re.search(r'snprintf\(' + m[1] + r',[^"]*"([^"]*)"', fmt)
            takes_str = bool(sm and "%s" in sm[1])  # a %s here may carry an owner/env path
            cen.append((os.path.relpath(f, root), i, m[1], int(m[3]), takes_str))
small = [c for c in cen if c[3] < 512 and c[4]]  # a path-carrying buffer below 512 bytes
for c in cen: print(f"CENSUS {c[0]}:{c[1]} {c[2]}[{c[3]}] takes_%s={int(c[4])}")
print(f"CENSUS path_buffers={len(cen)} path_carrying_below_512={len(small)} {'PASS' if cen and not small else 'FAIL'}")
ok = ob == 1 and nb == 0 and uses and mb == 1 and mut0 != new[0] and rt == len(names) and cen and not small
print("VERDICT", "CLOSED" if ok else "OPEN"); sys.exit(0 if ok else 1)
