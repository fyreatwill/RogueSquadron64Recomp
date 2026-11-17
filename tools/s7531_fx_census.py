#!/usr/bin/env python3
"""s7531 class FX census: the RT64 half of class FW (tools/s7530_fw_census.py).  Same scanner, same
definitions (scalar latch holding a guest address / guest-derived position; functional read = not a
decl, not a pure write, not inside a logging statement), applied to lib/rt64/src/hle + lib/rt64/src/gbi
with an RT64 rule table.

  python3 tools/s7531_fx_census.py              # table of non-auto rows, exit 1 on any FAIL
  python3 tools/s7531_fx_census.py --controls   # planted fixtures, mutation control, coverage control
"""
import os, re, sys, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7530_fw_census as fw

# render added in-session; contrib/ (mupen64plus-core, boost, spirv-cross) is third-party, not RS64 latch code.
ROOTS = ["lib/rt64/src/hle", "lib/rt64/src/gbi", "lib/rt64/src/render"]
I, S, Q, D, P, G, Z = ("hle/rt64_interpreter.cpp", "hle/rt64_state.cpp", "hle/rt64_present_queue.cpp",
                       "hle/rt64_rdp.cpp", "hle/rt64_rsp.cpp", "gbi/rt64_gbi_rdp.cpp", "gbi/rt64_gbi_f3dfactor5.cpp")
RULES = [
    # --- functional, compare-only edge detectors on a guest address (value never dereferenced) ----------
    (S, "g_rs64LastSyncedViAddress", "H-canon",
     "VI_FULLSYNC swap detector: compares newVI.fbAddress() with the last SYNCED address and re-sets on every change; "
     "never dereferenced. A stale-equal value only suppresses a 'swap' edge and the >100 ms 'stalled' fallback fires instead",
     {"verify": r"if \(addressChanged\) \{\s*g_rs64LastSyncedViAddress = viAddress;"}),
    (S, "s_lastPresentedDrawn", "H-canon",
     "drawnChanged edge on the last-drawn colour image, re-set on every change; compare-only, staticViRefresh covers a held value",
     {"verify": r"if \(drawnChanged\) \{\s*s_lastPresentedDrawn = curDrawn;"}),
    (G, "lastTask", "H-canon", "shade-ordinal map is cleared and re-keyed on every task change (s-ordinal reset); host task id",
     {"verify": r"task != lastTask\) \{ next\.clear\(\); lastTask = task; \}"}),
    # --- E9 provenance plumbing: every reader is ROGUESQ_LOG_E9_* gated ----------------------------------
    (I, "s_rs64_pending_start_address", "H-instrument-only",
     "set only when an E9 straddles a submit (834), cleared to ~0 after the pending command completes (707); readers are "
     "rs64LogE9Boundary* and rs64_e9prov_* (dpc_bridge, each returns unless ROGUESQ_LOG_E9_PROVENANCE) - feeds logs/counters",
     {"verify": r"s_rs64_pending_start_address = 0xFFFFFFFFu;\s*s_rs64_pending_submit_serial = 0;",
      "envoff": "ROGUESQ_LOG_E9_PROVENANCE"}),
    (I, "s_rdp_advance_first_consumer_order", "H-instrument-only",
     "zeroed in rs64_rdp_advance_reset; accessor read only by dpc_bridge [e9-task-join] fprintf",
     {"verify": r"s_rdp_advance_first_consumer_order = 0;"}),
    (I, "s_rdp_advance_first_consumer_address", "H-instrument-only", "see s_rdp_advance_first_consumer_order",
     {"verify": r"s_rdp_advance_first_consumer_address = 0xFFFFFFFFu;"}),
    # --- log gates / budgets -----------------------------------------------------------------------------
    (Z, "s_op01_last_ram", "H-instrument-only",
     "op02 #1 decodes the latched matrix only to fprintf it (proof-of-read diagnostic)", {"verify": r"op02 matrix from"}),
    (G, "lastOrigin", "H-instrument-only", "hangar dump budget reset per VI origin", {}),
    (I, "prev", "H-instrument-only", "[rdphist] per-interval delta (rs64RdpHist gate), host counters", {"verify": r"if \(rs64RdpHist\(\)\)"}),
    (I, "lastReport", "H-instrument-only", "decoded-op report cadence (host count)", {}),
    (I, "lastWidth", "H-instrument-only", "ROGUESQ_LOG_TRI_DISPATCH phase-row budget", {"verify": r"ROGUESQ_LOG_TRI_DISPATCH"}),
    (P, "lastWidth", "H-instrument-only", "probeEnabled phase-row budget", {}),
    (Q, "s_lastLogDrawn", "H-instrument-only", "s7376 wide-phase present diag (try-lock log line) change gate", {}),
    (D, "g_rs64LastRGBA32Seq", "H-instrument-only", "[tmem-draw] log only", {}),
    (D, "g_rs64LastRGBA32Addr", "H-instrument-only", "[tmem-draw] log only", {}),
    (S, "lastPhase", "H-instrument-only", "phase-ordinal change detectors for log budgets (3 function statics)", {}),
    (S, "g_ost_last_ctx", "H-instrument-only", "[ost-wb] CTX_CHANGED_PRE compare -> counter + fprintf only", {}),
    (S, "g_vifsLastFireDecisionSnapshot", "H-instrument-only",
     "crash-snapshot accessor rs64_get_vifs_crash_snapshot (main.cpp fault printer); host decision ordinal", {}),
    ("render/rt64_native_target.cpp", "last_phase", "H-instrument-only", "[g1d-native] phase log budget", {}),
    ("render/rt64_native_target.cpp", "lastPhase", "H-instrument-only",
     "floor readback budget, only under ROGUESQ_FLOOR_PIPE_DIR (diagnostic)", {"verify": r"floorDir && phase >= 4", "envoff": "ROGUESQ_FLOOR_PIPE_DIR"}),
    ("render/rt64_render_target.cpp", "last_phase", "H-instrument-only", "[g1d-target] phase log budget", {}),
    ("render/rt64_vi_renderer.cpp", "s_lastCols", "H-instrument-only", "[g1d-vishape] change log; sdSize set from live cols", {}),
    ("render/rt64_vi_renderer.cpp", "s_lastLines", "H-instrument-only", "see s_lastCols", {}),
]


def census(files, rules=RULES, binary=fw.BINARY):
    return fw.census(files, rules, binary)


def controls():
    res = []
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "fixture_latch.cpp")
        open(p, "w").write("static uint32_t g_planted_addr = 0;\nvoid set(uint32_t a){ g_planted_addr = a; }\n"
                           "void use(uint8_t* rdram){ rdram[g_planted_addr] = 1; }\n")
        rows, fails = census([p])
        res.append(("planted functional latch -> UNCLASSIFIED", fails == 1 and rows[0][3] == "UNCLASSIFIED", rows))
        # mutation control: strip the VI-sync re-set from a copy of rt64_state.cpp -> the H-canon row must FAIL
        src = "lib/rt64/src/" + S
        mut = os.path.join(d, "hle", "rt64_state.cpp")
        os.makedirs(os.path.dirname(mut))
        txt = open(src, errors="replace").read()
        txt2 = re.sub(r"g_rs64LastSyncedViAddress = viAddress;", "(void)viAddress;", txt)
        open(mut, "w").write(txt2)
        rows, fails = census([mut])
        bad = [r for r in rows if r[2] == "g_rs64LastSyncedViAddress"]
        res.append(("mutation: re-set removed -> FAIL-check", txt2 != txt and bad and bad[0][3] == "FAIL-check", bad))
    # coverage control: with NO rules the scanner must see the 20 functional RT64 latches
    rows, fails = census(fw.files_under(ROOTS), rules=[])
    res.append(("coverage: rule-less RT64 census sees >=25 UNCLASSIFIED", fails >= 25, "fails=%d" % fails))
    rows, fails = census(fw.files_under(ROOTS))
    res.append(("live RT64 census 0 fails", fails == 0, [r for r in rows if r[3] in ("UNCLASSIFIED", "FAIL-check")]))
    rows, fails = fw.census(fw.files_under(fw.ROOTS))
    res.append(("FW (s7530) live census still 0 fails", fails == 0, "fails=%d" % fails))
    ok = True
    for name, good, detail in res:
        print("control %-56s %s %s" % (name, "PASS" if good else "FAIL", "" if good else detail))
        ok &= bool(good)
    print("controls: %d/%d PASS" % (sum(1 for r in res if r[1]), len(res)))
    return 0 if ok else 1


def main():
    if "--controls" in sys.argv:
        sys.exit(controls())
    rows, fails = census(fw.files_under(ROOTS))
    from collections import Counter
    cnt = Counter(r[3] for r in rows)
    for r in rows:
        if r[3] not in ("instr-only(auto)", "diag") and not r[3].startswith("group"):
            print("%-34s %5d %-34s %-18s %s" % (r[0].replace("lib/rt64/src/", ""), r[1], r[2], r[3], r[4][:100]))
    print("summary: sites=%d %s fails=%d" % (len(rows), dict(cnt), fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
