#!/usr/bin/env python3
"""s7955 class TF (settings.txt text format): BOM, CRLF, no trailing newline, shell-style trailing comments.
Builds tools/test_settings.cpp against src/main/rs64_settings.cpp (must PASS) and against a planted mutant copy with
the s7955 BOM strip and comment strip removed (must FAIL on exactly the s7955 cases) -> the cases bite.
controls.json side: nlohmann skips a UTF-8 BOM and treats CR as whitespace (probed s7955), no change needed."""
import os, re, subprocess, sys, tempfile
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(R, "src/main/rs64_settings.cpp"); T = os.path.join(R, "tools/test_settings.cpp")
def run(src, d, tag):
    exe = os.path.join(d, tag)
    c = subprocess.run(["c++", "-std=c++17", "-w", "-I", os.path.join(R, "src/main"), T, src, "-o", exe], capture_output=True, text=True)
    if c.returncode: print(f"{tag} BUILD FAIL\n{c.stderr[:400]}"); sys.exit(1)
    o = subprocess.run([exe], capture_output=True, text=True).stdout
    m = re.search(r"(PASS|FAIL) (\d+) cases, (\d+) fail", o); return m.group(1), int(m.group(3))
with tempfile.TemporaryDirectory() as d:
    st, nf = run(SRC, d, "real")
    s = open(SRC).read()
    mut = s.replace('if (raw.compare(0, 3, "\\xEF\\xBB\\xBF") == 0) raw.erase(0, 3);', "")
    mut = re.sub(r"if \(!v\.empty\(\) && \(v\.front\(\) == '\"'.*?\n    \}\n", "", mut, count=1, flags=re.S)
    if mut.count("s7955") != s.count("s7955") or mut == s: pass
    planted = mut != s and "raw.erase(0, 3)" not in mut and "vraw[i] == '#'" not in mut
    mp = os.path.join(d, "mut.cpp"); open(mp, "w").write(mut)
    ms, mf = run(mp, d, "mutant")
print(f"REAL {st} fail={nf}")
print(f"CONTROL planted={'ok' if planted else 'NOT-APPLIED'} mutant={ms} fail={mf}")
ok = st == "PASS" and nf == 0 and planted and ms == "FAIL" and mf >= 9
print("VERDICT CLOSED" if ok else "VERDICT OPEN"); sys.exit(0 if ok else 1)
