#!/usr/bin/env python3
"""s7957 gate: RT64 PresetLibrary::load (F1 inspector "Load library") survives malformed preset json.
Runs tools/s7957_preset_load_test.zsh: pre-fix header copy must abort on 5 bad files (control),
live header must return false and stay alive; a valid file loads on both."""
import subprocess, sys, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = subprocess.run(["zsh", os.path.join(root, "tools/s7957_preset_load_test.zsh")], cwd=root, capture_output=True, text=True)
sys.stdout.write(p.stdout); sys.stderr.write(p.stderr)
ctl = sum(1 for l in p.stdout.splitlines() if l.startswith("PASS ") and " pre rc=134" in l)
fix = sum(1 for l in p.stdout.splitlines() if l.startswith("PASS ") and " post rc=0 RESULT ok=0 n=0" in l)
print(f"CONTROL pre_aborts={ctl}/5 {'PASS' if ctl == 5 else 'FAIL'}")
print(f"FIX post_survives={fix}/5 {'PASS' if fix == 5 else 'FAIL'}")
ok = p.returncode == 0 and ctl == 5 and fix == 5
print("VERDICT", "CLOSED" if ok else "OPEN")
sys.exit(0 if ok else 1)
