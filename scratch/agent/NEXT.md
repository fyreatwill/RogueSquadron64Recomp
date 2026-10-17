# Next: confirm hangar flake fix, then classify remaining unsigned-base audit hits
HYPOTHESIS-ID: hangar-flake-fault-class
1. Read SOAK-RESULTS.md tail for s5094_hangar_unsigned_base_fix. PASS (>=2 hangar arrivals, 0 CRASH, buttons_port>0) => move root cause to confirmed in CURRENT-TRUTH. A CRASH at updateHangarBayScene again => the fix did not apply; check `python3 tools/agent/disasm_at.py updateHangarBayScene 76424 8 4` for movk lsl #32.
2. Run `zsh scratch/agent/audit_unsigned_base.sh`; classify the remaining hits (funcs_0:5690, funcs_23:7982, funcs_24 7611-7923 & 9697, funcs_29:12502-3): fix with S32() in the fixup scripts if the arg order is (off, base) with an unsigned base, or prove them benign.
3. Regen-safety: confirm the fixup repair branch triggers (report line "AC8C0 port log unsigned base repaired") on a copy with the stale form.
