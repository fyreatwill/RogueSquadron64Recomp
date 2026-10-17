#!/usr/bin/env python3
"""Fail if the built funcs_26.c lacks the s4296 A14 spin-yield patch.

Without it shutdownMusyXVoices blind-spins on slot-0 status 03 and starves the
voice-pool worker (the s5085 mission 'stall'). Re-apply with
tools/apply_s4296_a14_spin_yield.py, then rebuild."""
import sys
from pathlib import Path

p = Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs" / "funcs_26.c"
ok = "PATCH: s4296 A14 spin yield" in p.read_text(errors="replace")
print(("OK" if ok else "MISSING") + f": s4296 A14 yield in {p}")
sys.exit(0 if ok else 1)
