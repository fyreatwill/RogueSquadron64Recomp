# NEXT (s7816)
HYPOTHESIS-ID: oracle-cxd4-vu-fix
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md, new
SOAK-RESULTS lines. Any crash/stall or owner report outranks the unit. G6c and all G5 items wait on the owner only.
Why: s7815 proved stock cxd4 has 5 VU defects (VCR, VCH, VABS, VMRG, VMADN/VMADL clamp) and that our LLE is byte-exact vs cxd4
once they are fixed. But every angrylion "retail oracle" run loads the STOCK plugin
../rs64-oracle/src/mupen64plus-rsp-cxd4/projects/unix/mupen64plus-rsp-cxd4.dylib (tools/g3_ai_gap_pair.sh, g3_menu_pair.sh,
g3_showroom_pair.sh, g3f_retail_pan.sh, tools/oracle/run_m4_retail_pcs.sh). The retail oracle is the bar for G3/G5 fidelity verdicts.
Unit (one build, offline-first):
 1. `zsh tools/s7815_vu_ops/patch_cxd4.sh /Users/williambuckley/Documents/Tools/rs64-oracle-cxd4p` (a NEW sibling dir; never edit
    the rs64-oracle tree), then `make -C .../rs64-oracle-cxd4p/projects/unix all` with the same flags the stock dylib was built with
    (check `make -n` in the stock dir / its _obj). NOTE patch_cxd4.sh fixes the SCALAR path only: confirm the stock dylib is the scalar
    build (nm for _V_result), else patch the SSE multiply clamps too and re-run tools/s7815_vu_gate.py with CX_SSE=1.
 2. Let the 5 scripts take `RSP=${RS64_ORACLE_RSP:-<patched dylib>}` (default the patched one: stock is wrong), document in
    tools/oracle/README.md.
 3. Re-run ONE existing retail pair with both plugins in the same session, same pose (e.g. the s7793 L1 STANDINS fidelity pair or
    g3_menu_pair), and score with the same scorer.
Hypotheses: H-negligible (oracle frames differ by <=1 LSB on a few hundred px, fidelity verdicts unchanged) / H-shift (some
port-vs-retail residual pixels in s7793/s7794 vanish: they were oracle error) / H-worse (patched oracle disagrees more: patch wrong).
Controls: stock-vs-patched oracle frame diff must be > 0 (the defects are reachable: s7752 showed 12k px <=1 LSB) and a planted
pixel must be detected by the scorer.
CPU rule: max 2 heavy jobs; one game/emulator run at a time.
