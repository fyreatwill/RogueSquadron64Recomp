#!/usr/bin/env python3
"""Disassemble a window around SYMBOL+OFFSET of the host binary via lldb.
usage: disasm_at.py SYMBOL OFFSET [BEFORE=16] [AFTER=4]  (instructions)"""
import subprocess, sys
sym, off = sys.argv[1], int(sys.argv[2], 0)
before = int(sys.argv[3]) if len(sys.argv) > 3 else 16
after = int(sys.argv[4]) if len(sys.argv) > 4 else 4
binp = "build/RogueSquadron64Recomp"
start = max(0, off - before * 4)
cmd = ["lldb", "-b", "-o",
       f"disassemble -s '{sym}+{start}' -c {before + after}", binp]
print(subprocess.run(cmd, capture_output=True, text=True).stdout)
