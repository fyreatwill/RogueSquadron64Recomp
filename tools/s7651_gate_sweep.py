#!/usr/bin/env python3
"""s7651 gate sweep: run every closed-class census (tools/s7*_census.py + EXTRA_GATES) in one pass and say which have gone RED.

s7651 found 4 "closed" rerun-after-change gates (s7375, s7430, s7533, s7535) exiting nonzero after later sessions added code
in their scope (G6b controls, G6c stand-ins, s7535-s7647 instruments): nothing re-ran them, so CURRENT-TRUTH still called
them closed. This runs them all (with --controls when the tool takes it), 6 at a time, 600 s cap each (RS64_GATE_CAP; s7659), and classifies:
  GREEN      exit 0 and no HOLLOW signal (s7720)
  HOLLOW     (s7720) exit 0 but a nonzero open-class count in the output, or an unpassed --check/--strict/--gate flag
  NEEDS-ARGS argparse usage / IndexError on sys.argv / missing input file: the tool needs an input (not a drift signal)
  RED        any other nonzero exit: drift or a real defect, triage by hand
  NEEDS-INPUT (s7655) a tool listed in NEEDS_INPUT printing its exact "input absent" text (other failures stay RED)
  REPORT     (s7657) a tool listed in REPORT whose source has no exit path: a summariser of one frozen capture, not a gate
s7657: the two-source censuses s7631/s7632/s7633 run with no args regenerate their scan/AST json from the live tree
(tools/ast_cache.fresh_census_args), so they gate the current code, not the s763x snapshot; --help prints this text.
Positive control (iron rule 1): a planted tool that exits 1 must read RED and one that exits 0 GREEN, else exit 3.
s7656 cache: every tool runs under tools/gate_trace.py (audit hook records each file it opens for reading, each directory it
lists, each glob); its verdict is cached in build/gate_sweep_cache.json keyed on (argv, size+mtime of every read file incl. the
tool itself, every listed directory's names, every glob's matches). Spawns: nm/objdump/zstd-class tools are keyed on their file
arguments; cc/c++/clang also on the exact header list clang writes to CC_PRINT_HEADERS_FILE; a program a compiler built in
the same run is allowed; git, shells and anything else keep the tool uncacheable (their reads are invisible). Cache control (iron rule 1): a planted tool reading a temp input must read GREEN, then a cache
HIT, then RED after the input is edited (else exit 3). --no-cache re-proves everything.
--new-red-vs FILE: exit 1 only for RED gates NOT listed (first column) in FILE, the committed allowed-RED baseline.
Usage: s7651_gate_sweep.py [--jobs N] [--only REGEX] [--tsv OUT] [--no-cache] [--new-red-vs FILE]
exit 0 iff no (new) RED (NEEDS-ARGS allowed)."""
import concurrent.futures as cf, glob, hashlib, shutil, json, os, re, subprocess, sys, tempfile, threading, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rs64_zopen import resolve as zresolve  # s7948

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARGS_SIG = re.compile(r"IndexError: list index out of range|usage: |error: unrecognized arguments|error: the following arguments"
                      r"|FileNotFoundError|No such file or directory|struct\.error: unpack_from")


# s7655: tools that report on runtime inputs the sweep cannot supply. Keyed by tool AND the exact text it prints when the input
# is absent: if the tool's message changes (or it fails another way) it reads RED again.
NEEDS_INPUT = {
    "s7316_data_bound_census.py": (re.compile(r"ram_dumps=0\s*$"), "needs --ram rdram dumps (ROGUESQ_RDRAM_DUMP_DIR): G values unread"),
    "s7573_guard_census.py": (re.compile(r"^no game logs\s*$", re.M), "needs game stderr logs (LOG... or --retained DIR)"),
    # s7657: the s7215 run.log (ROGUESQ_VI_SHAPE_LOG=1, 21:9 long route) was never retained: scratch/s7215 holds 0 shape lines
    "s7753_rdp_output_gate.py": (re.compile(r"^NEEDS-INPUT ", re.M), "needs the retained s7751 snaps (tools/s7753_capture_snaps.zsh) + a built game"),
    "s7756_hstate_gate.py": (re.compile(r"^NEEDS-INPUT ", re.M), "needs the retained s7754 hangar snap pairs (tools/s7754_capture_route.zsh) + a built game"),
    "s7215_shape_census.py": (re.compile(r"L = open\(sys\.argv\[1\].*\n(.*\n)?IndexError: list index out of range"),
                              "needs a ROGUESQ_VI_SHAPE_LOG=1 run.log (scratch/s7215/r.zsh); the s7215 log was not kept"),
}

# s7657: offline summarisers of ONE captured run / regen output. They have no failing exit (always 0), so a GREEN would be
# vacuous and their frozen inputs cannot drift with the code. Verified per run: if the source gains any exit path the tool is
# run like any other gate again.
REPORT = {  # s7722: each re-run and read by hand (scratch/s7722/*.out); all H-report (no open-class row by construction)
    "s7031_offmap_census.py": "s7722 H-report: band/ring share table of one [s7030]/[s7031] run.log; s7803 checked: no run.log/.zst in scratch/s7030, scratch/s7031 or scratch/agent/m6/g1_lvl*s703[01]* (summary + keys.log.gz only), no open class; s7951: g1_lvl4s7031L4A/run.log.gz is s7056's tag L4a (case-insensitive fs reused the dir; summary tag=g1_lvl4s7031L4a), not s7031's L4A run, so no s7031 input survives",
    "s7283_commit_census.py": "s7949 H-report: argv-loop summariser of [s7283-mtl] lines in scratch/agent/m6/g1_lvl*s7009<TAG>/*.log; bare it ran 0 tags and printed nothing (scored GREEN until s7949); none of the 21 s7277 tags' logs survive raw or .zst, no open class",
    "s7210_field_census.py": "s7722 H-report: per-swap scissor field-bit table of one G5B_FRAME .cap; s7803 checked: the ER169/FC1 .cap (22-30 GB caps) are not in scratch/s7210, only the tool's outputs, no open class",
}
EXIT_PATH = re.compile(r"\bsys\.exit\(|\bexit\(|\breturn [1-9]\b|raise SystemExit")


# s7656: NEEDS-ARGS gates whose input lives on disk: run with that input so they count. Used only when every path exists.
# (argv, regex the output must contain, else RED): s7409/s7410 exit 0 even on CONTROL FAIL, so the text is the gate.
ARGS = {
    # s7722: ex-REPORT censuses that carry open-class rows (unexplained jal targets / missed jump tables), now gates over the
    # retained pristine front-end pass; RED controls in PORTING-STATE s7722 (extra jal line, one mutated case label).
    "s7082_jal_census.py": (["scratch/s7082/regen.work/n64recomp.log.gz", "scratch/s7082/regen", "--check", "--plant"],
                            r"CONTROL PASS\nVERDICT PASS"),
    "s7083_lowering_census.py": (["scratch/s7082/regen", "rogue_squadron.z64", "--check"], r"VERDICT PASS"),
    # s7719: fresh regen_front + RS64_REPLAY_TREE_ONLY replay into a temp dir, then s7423 forward + --reverse with controls (~2.6 min,
    # one CPU). Replaces the hand-run s7421/s7423 drift check that needed a retained replay tree (last one s7558).
    # s7740: --strict adds byte identity live vs replay (any differing/one-sided source file = RED; planted edit/extra controls).
    # s7741: strict ucode regen: build/factor5_ucode == fresh RSPRecomp + tools/ucode_fixed patches byte-for-byte, 4 planted ctls.
    # s7771: jal/j-to-interior census over raw ELF words; GATE RED on any new code-site mid-function target (mutation ctl s7771).
    "s7771_jal_target_census.py": (["--gate", "--controls"], r"GATE GREEN code_site_nonstart=\d+ known=\d+ new=0\nCONTROLS PASS"),
    # s7772: every .text->overlay start_ovl jal site must be generated as LOOKUP_FUNC (a direct call binds one overlay silently).
    "s7772_ovl_lookup_audit.py": (["--controls", "--gate"], r"in_function_nonlookup=0 .*\nCONTROLS PASS .*\nGATE GREEN in_function_nonlookup=0"),
    # s7773: overlay fn-pointer words/lui-pairs held in resident .text must be the classified NPC spawners; no target a start in >1 overlay.
    "s7773_ovl_fnptr_audit.py": (["--controls", "--gate"], r"multi_start=0 resident=\d+ resident_known=\d+ new_candidates=0\nCONTROLS PASS .*\nGATE GREEN new_candidates=0"),
    "s7741_ucode_regen_gate.py": (["--controls"], r"CONTROL PASS\n(.*\n)*VERDICT GREEN: \d+ files, live == regen byte-for-byte"),
    # s7742: fixup_factor5_ucode.py idempotent on main/ucode_b/boot, fresh-regen ucode_b+boot == live, overlays refused; strip+red ctls.
    "s7742_fixup_idem_gate.py": (["--controls"], r"CONTROL PASS\n(.*\n)*VERDICT GREEN: fixup idempotent on 3 CMake files"),
    # s7743: the 9 overlay ucode files are fixup splice inputs + s7091 oracle (per-overlay marker-strip ctls must fire).
    "s7743_ovl_consumers.py": ([], r"verdict=H-tool-input a_not_fired=0 b_not_seen=0"),
    # s7753: end-to-end ucode OUTPUT gate: retained s7751 snaps replayed through the live factor5_ucode_lean.cpp.o must equal the
    # live RDP tail byte-for-byte; ctls TG_FIX=0 (differs, cxd4 length), CAP=65536 (strict prefix, cap_fires=1), 1-byte flip.
    "s7753_rdp_output_gate.py": (["--controls"], r"(?=[\s\S]*CONTROL PASS snaps=21)(?=[\s\S]*VERDICT GREEN: 21/21 tasks replay == live)"),
    # s7756: the hangar tasks s7753 excludes (H-state): live tail vs our ucode on END-of-task RAM must render within 1 LSB (s7755);
    # ctl CAP=2048 truncates the end replay and must read >=2 LSB px, plus s7755's flip + shade+16 ctls per pair.
    "s7756_hstate_gate.py": (["--controls"], r"(?=[\s\S]*CONTROL PASS pairs=6)(?=[\s\S]*VERDICT GREEN: 6/6 hangar H-state pairs)"),
    # s7762: owner docs (OWNER-REVIEW-QUEUE, OWNER-OPT-INS): every named path exists, every ROGUESQ_* name is read by live code.
    "s7762_owner_doc_check.py": (["--controls"], r"CONTROL PASS[\s\S]*OWNER-REVIEW-QUEUE.md names=\d+ paths_missing=0 names_stale=0\n[\s\S]*OWNER-OPT-INS.md names=\d+ paths_missing=0 names_stale=0"),
    "s7719_regen_gate.py": (["--strict"], r"VERDICT H-mirrored \(.*live == replay byte-for-byte"),
    # s7719: these three print "OPEN n" yet exit 0 without --check, so the s7718 sweep scored OPEN 19/22/6 as GREEN.
    "s7363_hostarr_census.py": (["--check"], r"\nOPEN 0\b"),
    "s7364_heapbuf_census.py": (["--rt64", "--check", "-q"], r"OPEN 0 keys 0"),
    "s7366_lockset_census.py": (["--check"], r"\nOPEN 0\b"),
    "s7409_fodd_census.py": (["../N64Recomp/RecompiledFuncs", "--plant"], r"CONTROL PASS"),   # planted FR0 MIXED row
    "s7410_csave_census.py": (["../N64Recomp/RecompiledFuncs", "--plant"], r"CONTROL PASS"),  # dropped ldc1 restore
    "s7091_ucode_insn_census.py": (["scratch/s7091/pristine", "build/factor5_ucode", "--controls"], None),  # rc 1 = unexplained
    # s7657: the d8 holder dump is only kept gzipped; --selftest proves classes A-E on the built-in synthetic listing (rc 2 FAIL)
    "s7317_field_compare_census.py": (["--selftest"], r"SELFTEST .* PASS"),
    # s7658: the three s7655/s7657 NEEDS-INPUT gates now carry a retained input captured once (NEEDS_INPUT stays the fallback
    # when the files are absent, e.g. a fresh clone). Planted controls in PORTING-STATE s7658.
    "s7215_shape_census.py": (["scratch/s7215/shape_lines.txt.zst"], r"without a mode switch within 1000 lines: 0"),
    "s7316_data_bound_census.py": (["--ram", "scratch/s7316/ram/rdram_0002000_fb80A62B80_1M5.bin.zst",
                                    "scratch/s7316/ram/rdram_0008000_fb8098AA00_1M5.bin.zst"], r"unclassified=0 .*ram_dumps=2"),
    "s7573_guard_census.py": (["--gate", "--retained", "scratch/s7573/retained"], r"GATE PASS"),
    # s7717: closed-class gates whose names lack the _census suffix, so discovery never ran them (s7427 had drifted RED unseen).
    # Planted controls first, then the class verdict; both must print.
    "s7427_env_policy_order.py": (["--control"], r"CONTROL PASS[\s\S]*VERDICT H-ordered"),   # env-policy order (class CJ)
    "s7424_stale_objects.py": (["--control"], r"CONTROL PASS[\s\S]*VERDICT H-fresh"),       # stale build objects
    "s7425_build_options.py": (["--control"], r"PASS[\s\S]*VERDICT H-intended"),           # CMake option cache drift
}
# s7718: the rest of the offline gates outside the s7*_census.py name pattern (scratch/s7718/classification.tsv lists all
# 100 candidates). LIVE = verdict over the live tree / build (control AND verdict regexes, lookahead so print order is free;
# s7412/s7413 also pin their harvest size, since both had silently lost coverage to later fixup idioms while still exiting 0).
# CONTROL-ONLY = scorers of runtime logs run on their synthetic/mutant controls: proves the tool, not a class (no log input).
S7718_LIVE = {
    's7336_host_arena_table.py': (['--control'], '(?=[\\s\\S]*control .* PASS)'),
    's7375_nolock_threads.py': (['--check'], '(?=[\\s\\S]*\\nOPEN 0\\b)'),
    's7377_present_lock_table.py': (['--check'], '(?=[\\s\\S]*line\\tstate\\torigin)'),
    's7408_cvt_contract.py': ([], '(?=[\\s\\S]*VERDICT in-range EQ.*control PASS)'),
    's7411_unaligned_contract.py': ([], '(?=[\\s\\S]*CONTROL PASS)(?=[\\s\\S]*VERDICT H-equal)'),
    's7412_int_emission.py': ([], '(?=[\\s\\S]*CONTROL PASS)(?=[\\s\\S]*VERDICT H-equal)(?=[\\s\\S]*skipped lui x\\d{1,3}\\b)'),
    's7413_aligned_ldst.py': ([], '(?=[\\s\\S]*CONTROL PASS)(?=[\\s\\S]*VERDICT H-equal)(?=[\\s\\S]*harvest: (?:9\\d|1\\d\\d)\\d{3} pure sites)'),
    's7414_fp_compare.py': ([], '(?=[\\s\\S]*VERDICT H-equal CONTROL PASS REACH CLEAN)'),
    's7415_fp_arith.py': ([], '(?=[\\s\\S]*CONTROL PASS)(?=[\\s\\S]*VERDICT H-equal)'),
    's7416_ctrl_flow.py': ([], '(?=[\\s\\S]*CONTROL structural=PASS mutants=PASS)'),
    's7418_opcode_residue.py': ([], '(?=[\\s\\S]*VERDICT H-equal.*CONTROL PASS)'),
    's7419_dis_agree.py': (['--controls'], '(?=[\\s\\S]*CONTROL plain objdump[^\\n]*PASS)(?=[\\s\\S]*VERDICT H-clean)'),
    's7428_config_precedence.py': ([], '(?=[\\s\\S]*CONTROL PASS)(?=[\\s\\S]*VERDICT H-env-wins)'),
    's7430_file_growth.py': (['--control'], '(?=[\\s\\S]*CONTROL PASS)(?=[\\s\\S]*VERDICT H-bounded)'),
    's7485_overread_bound.py': ([], '(?=[\\s\\S]*VERDICT EJ-bounded)'),
    's7520_elf_vs_rom.py': (['--controls'], '(?=[\\s\\S]*ctl \\S+: PASS)(?=[\\s\\S]*diffs=0)'),
    's7527_host_replace_audit.py': (['--controls'], '(?=[\\s\\S]*no REVIEW rows\\s+PASS)'),
    's7565_comp_chain.py': (['--controls', '--check'], '(?=[\\s\\S]*controls 8/8)'),
    'audit_service_msg_stack.py': ([], '(?=[\\s\\S]*unaudited stack-payload sends: 0)'),
}
S7718_CONTROL_ONLY = {
    'audit_delay_slot_branch_in_slot.py': (['--selftest'], 'selftest ok'),
    'audit_dma_event_wrappers.py': (['--selftest'], 'rows: 4 expected: 4'),
    'audit_host_wrappers.py': (['--selftest'], 'rows: 3 expected: 3'),
    'audit_lwl_lwr_split.py': (['--selftest'], 'selftest ok'),
    'audit_mmio_lui.py': (['--selftest'], 'selftest ok'),
    'audit_narrow_base.py': (['--selftest'], 'positive control hits: 2 negative: 0'),
    'audit_overlay_alias_calls.py': (['--selftest'], 'selftest ok'),
    'audit_thread_queue_wrappers.py': (['--selftest'], 'rows: 4 expected: 4'),
    'audit_time_interrupt_wrappers.py': (['--selftest'], 'rows: 4 expected: 4'),
    'audit_timer_virtual_cache_wrappers.py': (['--selftest'], 'rows: 4 expected: 4'),
    'audit_uint32_s32_base.py': (['--selftest'], 'positive control hits: 1 negative: 0'),
    'g1d_floor_attachment.py': (['--selftest'], 'selftest ok'),
    'g1d_floor_depth.py': (['--selftest'], 'selftest ok'),
    'g1d_floor_mesh.py': (['--selftest'], 'selftest ok'),
    's7675_ghost_score.py': (['--selftest'], '-> PASS'),
    's7510_pi_dma_shape.py': (['--controls'], 'controls PASS'),
    's7511_ai_dma_shape.py': (['--controls'], 'controls PASS'),
    's7512_vi_shape.py': (['--controls'], 'controls PASS'),
    's7514_time_shape.py': (['--controls'], 'PASS'),
    's7515_eep_shape.py': (['--controls'], 'PASS'),
    's7519_store_side.py': (['--controls'], 'PASS'),
    's7520_code_bytes.py': (['--controls'], 'PASS'),
    's7521_ucode_bytes.py': (['--controls'], 'PASS'),
    's7522_imem_residency.py': (['--controls'], 'PASS'),
    's7532_undo_score.py': (['--controls'], 'controls: 4/4 PASS'),
    's7533_fz_score.py': (['--controls'], 'controls: 5/5 PASS'),
    's7535_ga_score.py': (['--controls'], 'controls: 6/6 PASS'),
    's7536_splate_score.py': (['--controls'], 'PASS'),
    's7539_gb_score.py': (['--controls'], 'controls 8/8'),
    's7541_gb_score.py': (['--controls'], 'controls 9/9'),
    's7551_gk_score.py': (['--controls'], 'controls 4/4'),
    's7552_gl_score.py': (['--controls'], 'controls 5/5'),
    's7553_gm_score.py': (['--controls'], 'controls 5/5'),
}
# s7720 hollow-GREEN scan: these parse --check/--strict (exit 1 on unreviewed / stale / failed rows) but the sweep ran them bare,
# so rc was 0 whatever they found. Passing with the flag (rc 0): s7362 s7365 s7375 s7377 s7378 s7392 s7399 s7558 s7565.
# FAILING with it at s7720 (were GREEN): s7374 s7380 s7381 s7382 s7383 s7384 s7557 - see tools/gate_sweep_allowed_red.txt.
S7720_CHECK = {t: (["--check"], None) for t in (
    "s7362_rdramraw_census.py", "s7365_invalidation_census.py", "s7378_shared_res_census.py", "s7392_mesg_census.py",
    "s7399_evpayload_census.py", "s7558_gr_census.py", "s7374_lazy_static_census.py", "s7380_condvar_census.py",
    "s7381_spin_census.py", "s7382_thread_qos_census.py", "s7383_atomic_order_census.py", "s7384_static_state_census.py")}
S7720_CHECK["s7557_gq_census.py"] = (["--strict"], None)
# s7936: the s7392-s7399 rows re-captured as scratch/s7936/<tool>/run.log.zst (originals pruned 2026-11-23).
# s7723: one-capture scorers (s7718 NEEDS-INPUT) whose capture is still retained on disk under scratch/ (gitignored, so on a
# fresh clone the paths are absent and the tool falls back to NEEDS-ARGS like before). Read compressed via tools/rs64_zopen.py.
# Each regex needs the tool's own control AND its clean verdict; tools/s7723_retained_controls.py mutates one control/open row
# per input and proves every row then reads RED (PORTING-STATE s7723).
S7723_RETAINED = {
    "s7392_mq_report.py": (["scratch/s7936/s7392_run/run.log.zst", "--known"],
                           r"(?=[\s\S]*CONTROL PASS \(guest=1 ext=1\))(?=[\s\S]*VERDICT H-none-on-route drops=0)"),
    "s7393_cq_report.py": (["scratch/s7936/s7393_own/run.log.zst"], r"(?=[\s\S]*\nCONTROL PASS)(?=[\s\S]*VERDICT H-none)"),
    "s7394_bd_report.py": (["scratch/s7936/s7394_ownfix/run.log.zst", "--fix"],
                           r"(?=[\s\S]*FIX-ARM CONTROL PASS)(?=[\s\S]*-> PASS)(?=[\s\S]*VERDICT H-none)"),
    "s7396_tq_report.py": (["scratch/s7936/s7396_own/run.log.zst"], r"(?=[\s\S]*control=PASS rows=\d+)(?=[\s\S]*VERDICT H-none)"),
    "s7397_timer_report.py": (["scratch/s7936/s7397_own/run.log.zst"], r"(?=[\s\S]*=> PASS)(?=[\s\S]*VERDICT H-none)"),
    "s7399_evp_report.py": (["scratch/s7936/s7399_own/run.log.zst"],
                            r"(?=[\s\S]*CONTROL PASS \(delivery flagged=1)(?=[\s\S]*VERDICT H-none mismatches=0)"),
    "s7516_pak_shape.py": (["--controls", "--ctl", "scratch/s7516_fm_levels/log_l12.txt.zst"] +
                           ["scratch/s7516_fm_levels/log_l%d.txt.zst" % l for l in (1, 7, 10)], r"\(ctl\) rows=\d+ .* bad=0 ctl_ok=1"),
    "s7517_vi_feat.py": (["--controls", "--ctl", "scratch/s7517_fn_levels/log_l1.txt.zst"] +
                         ["scratch/s7517_fn_levels/log_l%d.txt.zst" % l for l in (7, 10, 12)], r"bad=0 ctl_ok=1"),
    "s7518_cache_shape.py": (["--controls", "--ctl", "scratch/s7518_fo_levels/log_l1.txt.zst"] +
                             ["scratch/s7518_fo_levels/log_l%d.txt.zst" % l for l in (7, 10, 12)], r"ctl_flagged=1"),
    "s7528_evict_score.py": (["--controls", "scratch/s7528_evict/log_old.txt.zst", "scratch/s7528_evict/log_new.txt.zst"],
                             r"(?=[\s\S]*old_must_fail=PASS)(?=[\s\S]*new_must_pass=PASS)"),
    # UBSan arms (scratch/s7579/san_<arm>.<pid>; p2 = the planted bounds arm)
    "s7579_bounds_report.py": (["scratch/s7579"], r"control_fired=1 real_sites=0 arms_with_logs=2"),
    # s7801: NSZombie census (was NEEDS-ARGS since s7726) over the retained s7727 hangar abort/re-entry route (zdef = default,
    # zown0 = ROGUESQ_MTL_OWN=0 over-release control); the tool reads *.zst since s7801. Pins control 364 + 0 zombies per segment.
    "s7726_zombie_census.py": (["--arm", "scratch/s7727/zdef/run.log.zst", "--control", "scratch/s7727/zown0/run.log.zst",
                                "--mark", "hangarmenu-a0-entry", "--segments", r"hangarmenu-a0-entry|initMission\] call"],
                               r"(?=[\s\S]*s7726 CONTROL PASS: control MTLTextureDescriptorInternal zombies=364\n)"
                               r"(?=[\s\S]*default segments=7 zombies_per_segment=0,0,0,0,0,0,0,0\n)"
                               r"(?=[\s\S]*s7726 VERDICT H-clean: default arm 0 zombies \(boot\+flight\))"),
}
# s7724: the /usr/bin/sample profiler scorers (classes CP/CR/CS/CT/CU) over the retained scratch/s7435 capture (8 x 12 s windows,
# busy-on/off diag-quiet flips in run.tlog, sample_N.txt.zst read via rs64_zopen). Each prints CONTROL ... PASS from the planted
# rs64_diag_spin_us 500 us/swap control; a control FAIL exits 3. s7437/s7438 verdict tokens are the tool's own (the ledger's
# H-known / H-closed was the hand prior-closure check on these same numbers). s7434 has no control: REPORT-class (H-no-control).
# s7935: scratch/s7435 was pruned 2026-11-23; re-captured as scratch/s7935 (same recipe, env S7431_ARM=S7935 zsh
# tools/s7433_probe_cost.sh). All 5 verdicts reproduce; only s7433's probe number moved (s7435 0.1x -> 0.0925, still H-free).
_CP = r"(?=[\s\S]*(?:^|\n)CONTROL ctrl delta [\d.]+ [a-z/]+ vs expected [\d.]+[^\n]*: PASS)"
S7724_RETAINED = {
    "s7433_probe_cost.py": (["scratch/s7935"], _CP + r"(?=[\s\S]*\nVERDICT H-free probe 0\.0[89]\d* ms/frame)"),
    "s7435_spin_cost.py": (["scratch/s7935"], _CP + r"(?=[\s\S]*\nVERDICT H-tail \(total 0\.04\d* core\))"),
    "s7436_alloc_cost.py": (["scratch/s7935"], _CP + r"(?=[\s\S]*\nVERDICT H-free \(allocator total 0\.01\d* core)"),
    "s7437_tmem_hash.py": (["scratch/s7935"], _CP + r"(?=[\s\S]*\nVERDICT H-candidate \(hash total 0\.5\d* ms/frame)"),
    "s7438_rt64_terms.py": (["scratch/s7935"], _CP + r"(?=[\s\S]*\nVERDICT terms >= 0\.2 ms/f for prior-closure check: Gfx RT64::TMEMHasher::hash 0\.4)"),
    # s7724: ASan+UBSan flight arms (p = plant arm, l7, w15), logs as .zst; control=PASS needs both plants in arm p, a NEW group exits 1
    "s7467_san_report.py": (["scratch/s7467r", "p", "l7", "w15", "--plant", "p", "--known", "tools/s7467_san_reviewed.tsv"],
                            r"(?=[\s\S]*\ns7467 new_groups=0\n)(?=[\s\S]*\ns7467 control=PASS)"),
    # s7724: stand-in flicker scorer, L1 (toggle window 1 vs forced-off window 2 + synthetic painted-square control). The tool always
    # exits 0, so the regex pins the frozen capture's numbers (ledger s7624 table: 3879.1 / 4351.2, control 1927 >= 1056).
    "s7624_flicker_score.py": (["scratch/s7624/log_L1f.txt.zst", "scratch/s7624/fb_L1", "--control"],
                               r"(?=[\s\S]*win=1 frames=90 .*per_triplet=3879\.1 .*label_alternations=89/89)"
                               r"(?=[\s\S]*win=2 frames=90 .*per_triplet=4351\.2 )(?=[\s\S]*found in-square 1927 \(need >= 1056\) -> PASS)"),
}
# s7802: the RDP-output and hangar H-state gates read NEEDS-INPUT from s7780 to s7801 although every input was retained: the
# snaps were zstd-compressed (2026-11-21 14:24) and both gates tested only the raw *.bin path. They resolve *.zst via
# tools/rs64_zopen.py since s7802; run with their planted controls and pinned to the full input count, so losing one reads RED.
# A fresh clone (no scratch/) still falls back to NEEDS_INPUT above.
S7802_RETAINED = {
    "s7753_rdp_output_gate.py": (["--controls"], r"(?=[\s\S]*\nCONTROL PASS snaps=21\n)(?=[\s\S]*\nVERDICT GREEN: 21/21 )"),
    "s7756_hstate_gate.py": (["--controls"], r"(?=[\s\S]*\nCONTROL PASS pairs=6\n)(?=[\s\S]*\nVERDICT GREEN: 6/6 )"),
    # planted: one absent among the real set -> RED, all absent -> NEEDS-INPUT, a .zst-only input resolves (both gates)
    "s7802_retained_input_controls.py": ([], r"CONTROLS PASS 6/6"),
}
ARGS.update(S7802_RETAINED)
# s7803: ex-REPORT s7441 rs64 census. Its raw-only sample_*.txt glob read windows=0 on every retained capture once the samples
# were zstd'd; it reads .zst since s7803 and has a --gate mode pinning the s7441 claims on the post-fix s7442 capture, with the
# pre-fix s7439 capture as the same-run planted RED (rs64SkipDraw 0.0075 ms/f before the latch).
S7803_RETAINED = {
    "s7441_rs64_census.py": (["scratch/s7935", "--gate", "--plant"],  # s7935: s7439/s7442 pruned; planted REDs replace the pre-fix control
                             r"(?=[\s\S]*\nPLANT skipdraw \S+ hits=\d+ PASS)(?=[\s\S]*\nPLANT reviewed \S+ hits=\d+ PASS)(?=[\s\S]*GATE dir=scratch/s7935 windows=8 rs64SkipDraw_incl=0\.0000 named_ge_0\.003=0 -> PASS)(?=[\s\S]*\nVERDICT GREEN)"),
}
ARGS.update(S7803_RETAINED)
# s7804: static+filesystem lint closing the s7801-s7803 class: a swept or CURRENT-TRUTH-cited tool that does not import rs64_zopen
# and names a capture literal matching a zst-only retained file reads RED. Same-run controls: planted zst-only glob RED, the same
# with zopen ZOPEN, raw-only dir GREEN. First run found s7415 (5 soak logs skipped), s7616 --witness-sample, s7763 --offline.
S7804_LINT = {"s7804_zst_blind_lint.py": ([], r"(?=[\s\S]*\('RED', 'ZOPEN', 'GREEN'\) PASS\n)(?=[\s\S]*\nVERDICT GREEN: 0 tools )")}
ARGS.update(S7804_LINT)
# s7805: argv-borne companion of s7804: every doc/ledger-cited `tools/X.py ... scratch/...` whose scratch arg survives only as .zst
# is run once; FileNotFoundError = RED. Same-run control: planted raw-opener RED, zopen-opener GREEN. First run: 11 RED -> zopen.
S7805_CITED = {"s7805_cited_cmd_zst_check.py": ([], r"(?=[\s\S]*\('RED', 'GREEN'\) PASS\n)(?=[\s\S]*\nVERDICT GREEN: 0 cited )")}
ARGS.update(S7805_CITED)
# s7808: the gcc-built findAndUnlinkSmallestEntry patch is never called in play (s7806/s7807), so its recompiled body
# (RecompiledPatches/patches.c rs64_find_body) is executed offline on synthetic pools against a native model AND the recompiled
# retail body (0x8002221C). Controls: mutant reference differs, planted pool byte detected, planted sltu->sleu patch body H-differ.
S7808_FIND = {"s7808_find_body_diff.py": (["--controls"], r"(?=[\s\S]*\nCONTROLS PASS\n)(?=[\s\S]*\nVERDICT H-equal\n)(?=[\s\S]*\nPLANTED-PATCH CONTROL PASS )")}
ARGS.update(S7808_FIND)
S7809_PATCH_CLASS = {"s7809_patch_class_diff.py": (["--controls"], r"(?=[\s\S]*\nCLASSIFIER CONTROLS PASS )(?=[\s\S]*\[setRngSeed\] PLANTED-PATCH CONTROL PASS )(?=[\s\S]*\[isCinematicActive\] PLANTED-PATCH CONTROL PASS )(?=[\s\S]*\nCLASS VERDICT GREEN )")}
ARGS.update(S7809_PATCH_CLASS)
S7810_HOST_OVR = {"s7810_host_override_diff.py": (["--controls"], r"(?=[\s\S]*\nCENSUS CONTROL PASS )(?=[\s\S]*R2-SCANNER CONTROL PASS )(?=[\s\S]*PLANTED-MUTANT CONTROL PASS )(?=[\s\S]*PRE-FIX \(s7810 revert\) CONTROL PASS )(?=[\s\S]*\nCLASS VERDICT GREEN )")}
ARGS.update(S7810_HOST_OVR)
S7812_RECOMP_H = {"s7812_recomp_h_census.py": (["--controls"], r"(?=[\s\S]*\nMEM TEST PASS total_bad=0 hollow_ops=\[\])(?=[\s\S]*\nCONTROLS PASS)(?=[\s\S]*\nCLASS VERDICT GREEN open=0)")}
ARGS.update(S7812_RECOMP_H)
S7813_CALLEE = {"s7813_callee_census.py": (["--controls"], r"(?=[\s\S]*\nMEM host sites \d+ raw_open 0)(?=[\s\S]*hollow=no)(?=[\s\S]*\nCONTROLS PASS)(?=[\s\S]*\nCLASS VERDICT GREEN open=0)")}
ARGS.update(S7813_CALLEE)
S7814_INCLUDE = {"s7814_include_census.py": (["--controls"], r"(?=[\s\S]*\nCONTROLS PASS)(?=[\s\S]*\nCLASS VERDICT GREEN open=0 mismatch=0)")}
ARGS.update(S7814_INCLUDE)
# s7815: 31 elementwise VU ops (ours, both flavours) vs patched cxd4 + vendored CEN64; stock-cxd4 six-op signature + VMADN mutant controls (~31 s)
S7815_VU = {"s7815_vu_gate.py": ([], r"(?=[\s\S]*\nCONTROLS PASS\n)(?=[\s\S]*\nVU VERDICT GREEN)")}
ARGS.update(S7815_VU)
# s7858: det-pair dt pins must survive a [vi-poll] splice into a 0x800FA738 hit line (s7857/v14 shifted 118 pins one tick).
S7858_PINS = {"test_s7858_det_pins_splice.py": ([], r"(?=[\s\S]*splice  : PASS)(?=[\s\S]*control : PASS)")}
ARGS.update(S7858_PINS)
# s7861: det verdict fork= classifier (audio-clock vs unclassified), synthetic score cases incl. negatives.
S7861_VERDICT = {"test_s7856_det_verdict.py": ([], r"FAILURES 0")}
ARGS.update(S7861_VERDICT)
S7862_TABLE = {"s7862_det_sweep_table.py": ([], r"TABLE OK rescored=\d+ hand=\d+ mismatch=0")}  # s7862 det sweep table; --control plants a mismatch
ARGS.update(S7862_TABLE)
S7863_SONGN = {"s7863_song_end_threshold.py": (["--control"], r"CONTROL PASS\nVERDICT SAME buffer count in all \d+ song windows")}  # s7863 audio-clock forks: same song-end buffer count; planted -1% rate caught
ARGS.update(S7863_SONGN)
S7864_AIHIST = {"s7864_ai_per_vi_hist.py": (["--control"], r"VERDICT PASS \(controls PASS\)")}  # s7864 AI buffers/VI histogram; planted +1/100 VI must move it
ARGS.update(S7864_AIHIST)
S7865_AIDMA = {"s7865_ai_dma_rate.py": ([], r"controls: .* -> PASS")}  # s7865 mupen gap-free AI rate vs retail; floor/planted controls
ARGS.update(S7865_AIDMA)
S7925_WAITPAIR = {"s7922_transition_table.py": (["scratch/s7925_mmark/ring_q4.txt.zst", "scratch/s7921_oracle5/oracle.log", "--waits"],
                  r"agreement wait-vs-hold pairing (\d+)/\1; mutation control \(shift 1\) \d+/\d+ -> PASS; wait_pairs_port_longer=0")}  # s7925 G5c: port MusyX wait rows pair = hold ordinal pairing; shift-1 mutation must break it
ARGS.update(S7925_WAITPAIR)
S7928_GATEW = {"s7928_gate_writers.py": (["scratch/s7928_gatew2/ring_q4.txt", "--oracle", "scratch/s7928_oracle/oracle.log"],
               r"retail calls 8 \(waits 8/8\) port calls 7 \(gate set 6\); last caller retail mainGameLoop@E360 port mainGameLoop@E360 -> FLIGHT-ENTRY MATCH")}  # s7928: port takes retail's flight-entry MusyX wait (s7927 SKIPPED superseded)
ARGS.update(S7928_GATEW)
S7931_ROUTE = {"s7931_route_pair.py": (["scratch/s7931_port/ring_nf.txt", "scratch/s7931_route/port7.3/oracle.log", "--control", "scratch/s7931_port/ring_fc.txt"],
               r"common prefix 6/6 \(retail 6, port 7\) -> SEQ-MATCH; mutation prefix 3/6 differs\(ok\); control ring prefix 4/6 differs\(ok\)")}  # s7931: same owner save -> port and retail take the same transition sequence; FORCE arm + drop-one mutation are controls
ARGS.update(S7931_ROUTE)
S7950_DETPAIR = {
    # s7950: ex-NEEDS-ARGS det-pair census tools over their retained captures (s7826 lvl2 / s7836 lvl3 flight). Output reproduces the
    # ledger scores byte-for-byte (scratch/s7826/score_pose_s7827.txt, scratch/s7836/hud_census.txt); both carry same-run planted controls.
    "s7827_tri_yshift_census.py": (["scratch/s7826/retail.bin.zst", "scratch/s7826/port.bin.zst", "--win", "3521:3825,4378:4702", "--controls",
                                    "--pose", "3623:3825,4516:4702"],
                                   r"controls PASS \(A mode 0, B mode 2\)\nVERDICT: world-tri dy mode = 0 quanta[\s\S]*port  H-pitch  rms 0\.107 px[\s\S]*pose controls PASS; VERDICT pose: H-pitch"),
    "s7836_hud_elem_census.py": (["scratch/s7836/ret/retail.bin.zst:retail:3300:4300", "scratch/s7836/port.bin.zst:port:4060:5160", "--control"],
                                 r"REST retail b=\(230\.25,183\.25\)x973 s=\(243\.0,190\.75\)x970[\s\S]*REST port b=\(230\.0,184\.25\)x725 s=\(242\.75,192\.0\)x719[\s\S]*CONTROL PASS"),
}
ARGS.update(S7950_DETPAIR)
S7932_RETAIN = {"s7893_retained_manifest.py": (["--check"], r"(?=[\s\S]*s7893 retained=\d+ manifest=\d+ missing=0)(?=[\s\S]*s7932 sweep-argv retained=(?:[1-9]\d{2,}) missing=0)(?=[\s\S]*s7933 sweep-trace retained=(?:[1-9]\d{2,}) missing=0)")}  # s7933: third source = the gates' traced reads (build/gate_sweep_cache.json); s7932: '%d' ARGS literals were unprotected from the 7-day prune (glob 'l*d'); second source = the sweep's own argv
ARGS.update(S7932_RETAIN)
# s7934: gate_trace.py now records stat-only paths ("stats"); controls = tracer selftest + sweep fingerprint planted arms
S7934_STATKEY = {"s7934_stat_key_check.py": (["--controls"], r"(?=[\s\S]*tracer CONTROLS PASS)(?=[\s\S]*CONTROL fingerprint delete=CHANGED resize=CHANGED same=EQUAL mutation=EQUAL PASS)")}
ARGS.update(S7934_STATKEY)
S7953_LC = {"s7953_locale_census.py": (["--witness", "scratch/s7953"], r"(?=[\s\S]*CONTROL planted_source=FIRED planted_dylib_import=FIRED drop_reviewed=FIRED/FIRED PASS)(?=[\s\S]*WITNESS base samples=\d+ C=\d+ changed_comma=0 stress samples=\d+ C=\d+ changed_comma=0 plant samples=\d+ C=\d+ changed_comma=1 PASS)(?=[\s\S]*open=0 dylibs=\d+ import_open=0)")}
ARGS.update(S7953_LC)  # s7953 class LC (process locale)
S7954_CK = {"s7954_clock_census.py": ([], r"(?=[\s\S]*WITNESS cxx=\S+ hrc_is_steady_clock=1 hrc_is_steady=1 system_is_steady=0 PASS)(?=[\s\S]*CONTROL planted_source=FIRED drop_reviewed=FIRED hrc_not_steady=FIRED\(\+\d+\) planted_object=FIRED PASS)(?=[\s\S]*open=0 stale=0 wall_objects=\d+ obj_open=0)(?=[\s\S]*VERDICT CLOSED)")}
ARGS.update(S7954_CK)  # s7954 class CK (wall clock in intervals/pacing)
S7955_TF = {"s7955_settings_textfmt.py": ([], r"(?=[\s\S]*REAL PASS fail=0)(?=[\s\S]*CONTROL planted=ok mutant=FAIL fail=(?:9|[1-9]\d))(?=[\s\S]*VERDICT CLOSED)")}
ARGS.update(S7955_TF)  # s7955 class TF (settings.txt BOM / CRLF / trailing comment)
S7957_PL = {"s7957_preset_load_gate.py": ([], r"(?=[\s\S]*CONTROL pre_aborts=5/5 PASS)(?=[\s\S]*FIX post_survives=5/5 PASS)(?=[\s\S]*VERDICT CLOSED)")}
ARGS.update(S7957_PL)  # s7957 RT64 preset library load vs malformed json
S7958_FW = {"s7958_fw_gate.py": ([], r"(?=[\s\S]*CONTROL old_bad=[1-9]\d* \(empty=\d+\) PASS)(?=[\s\S]*FIX new_bad=0 nodir_reports_fail=True PASS)(?=[\s\S]*CENSUS owner_writers=5 audio_atomic=True PASS)(?=[\s\S]*VERDICT CLOSED)")}
ARGS.update(S7958_FW)  # s7958 class FW owner-state file writers (audio_device.txt in-place)
S7959_RD = {"s7959_rd_gate.py": ([], r"(?=[\s\S]*CONTROL old_bad=[1-9]\d* PASS)(?=[\s\S]*FIX new_bad=0 cases=\d+ PASS)(?=[\s\S]*CONTROLS remap_loaded=1 partial=\d+ trusted_wrong=0 PASS)(?=[\s\S]*VERDICT CLOSED)")}
ARGS.update(S7959_RD)  # s7959 class RD owner-state file readers (audio_device.txt empty -> default route)
S7960_DR = {"s7960_dr_gate.py": ([], r"(?=[\s\S]*CONTROL old_bad=[1-9]\d* PASS)(?=[\s\S]*FIX new_bad=0 cases=\d+ PASS)(?=[\s\S]*CENSUS .* PASS)(?=[\s\S]*VERDICT CLOSED)")}
ARGS.update(S7960_DR)  # s7960 class DR data-root split (launch from another folder found no ROM/save)
S7961_SD = {"s7961_sd_gate.py": ([], r"(?=[\s\S]*CONTROL old_bad=1 PASS)(?=[\s\S]*FIX new_bad=0 PASS)(?=[\s\S]*MUTANT .* PASS)(?=[\s\S]*VERDICT CLOSED)")}
ARGS.update(S7961_SD)  # s7961 class SD settings.txt follows the data-root rule
S7962_PS = {"s7962_ps_gate.py": ([], r"(?=[\s\S]*CONTROL old_bad=1 PASS)(?=[\s\S]*FIX new_bad=0 .*PASS)(?=[\s\S]*MUTANT .* PASS)(?=[\s\S]*UNIT roundtrip=5/5 PASS)(?=[\s\S]*VERDICT CLOSED)")}
ARGS.update(S7962_PS)  # s7962 class PS shell-quoted host paths (apostrophe folder)
S7723_RETAINED_CTL = {"s7723_retained_controls.py": ([], r"CONTROLS PASS bad=0 skipped=0")}  # planted RED per row above
ARGS.update(S7723_RETAINED_CTL)
ARGS.update(S7720_CHECK)
ARGS.update(S7723_RETAINED)
ARGS.update(S7724_RETAINED)
ARGS.update(S7718_LIVE)
ARGS.update(S7718_CONTROL_ONLY)
# s7717: swept although not named s7*_census.py (each needs an ARGS row above).
EXTRA_GATES = ("s7922_transition_table.py", "s7427_env_policy_order.py", "s7424_stale_objects.py", "s7425_build_options.py", "s7719_regen_gate.py", "s7741_ucode_regen_gate.py", "s7742_fixup_idem_gate.py", "s7743_ovl_consumers.py", "s7753_rdp_output_gate.py", "s7756_hstate_gate.py", "s7762_owner_doc_check.py", "s7772_ovl_lookup_audit.py", "s7773_ovl_fnptr_audit.py") + tuple(S7718_LIVE) + tuple(S7718_CONTROL_ONLY) + tuple(S7723_RETAINED) + tuple(S7724_RETAINED) + tuple(S7723_RETAINED_CTL) + tuple(S7802_RETAINED) + tuple(S7803_RETAINED) + tuple(S7804_LINT) + tuple(S7805_CITED) + tuple(S7808_FIND) + tuple(S7809_PATCH_CLASS) + tuple(S7810_HOST_OVR) + tuple(S7812_RECOMP_H) + tuple(S7813_CALLEE) + tuple(S7814_INCLUDE) + tuple(S7815_VU) + tuple(S7858_PINS) + tuple(S7861_VERDICT) + tuple(S7862_TABLE) + tuple(S7863_SONGN) + tuple(S7864_AIHIST) + tuple(S7865_AIDMA) + tuple(S7928_GATEW) + tuple(S7931_ROUTE) + tuple(S7950_DETPAIR) + tuple(S7932_RETAIN) + tuple(S7934_STATKEY) + tuple(S7955_TF) + tuple(S7957_PL) + tuple(S7958_FW) + tuple(S7959_RD) + tuple(S7960_DR) + tuple(S7961_SD) + tuple(S7962_PS)  # s7956: s7955 row was unswept (name not *_census.py)
# s7720 hollow-GREEN scan: s7719 found s7363/s7364/s7366 printing "OPEN 19/22/6" yet exiting 0 (they only fail under --check),
# so rc 0 alone scored them GREEN. A GREEN gate is re-scored HOLLOW (blocks like RED) when (a) its full output carries a nonzero
# open-class count, or (b) its source parses a --check/--strict/--gate flag the sweep did not pass. HOLLOW_OK holds hand-reviewed
# exceptions: tool -> (regex every flagged token must match, reason); an unreviewed new token reads HOLLOW again.
HOLLOW_KEYS = r"OPEN|UNCLASSIFIED|UNRESOLVED|UNEXPLAINED|UNAUDITED|UNREVIEWED|MISMATCH(?:ES)?|FAIL(?:S|ED|URES?)?|RED|NEW|REVIEW|DRIFT(?:ED)?|BAD"
# s7721: open-class words found by enumerating every count token in all 196 captured outputs (scratch/s7721/keys.tsv)
HOLLOW_KEYS += r"|MISSING|STALE|RACES?|NEED_FIX|NEED_REVIEW|UNMATCHED|DEFECTS?|UNGUARDED|DISAGREE(?:S|MENTS?)?|LEAK(?:S|ED)?|ORPHANS?|VIOLATIONS?|UNCOVERED|FOLDED|ERRORS?|REGRESS(?:ED|IONS?)?|BROKEN|WRONG"
# key-first "OPEN 19" / "open=3" / "UNREVIEWED: 2"; number-first "8 new mismatch" only when not itself a value (no "=12 open") and
# the key carries no count of its own ("94060 bad 0" is bad=0). Lines naming a control / plant / mutant / selftest are skipped:
# a control is meant to show nonzero counts.
HOLLOW_RE = re.compile(r"(?<![\w-])(?:(?P<k1>" + HOLLOW_KEYS + r")(?:[ \t]*[=:]?[ \t]*)(?P<n1>[1-9]\d*)\b"
                       r"|(?<![\w=:.+-])(?P<n2>[1-9]\d*)[ \t]+(?P<k2>" + HOLLOW_KEYS + r")\b(?![ \t]*[=:]?[ \t]*\d))", re.I)
CONTROL_LINE = re.compile(r"control|plant|mutant|mutated|selftest|fixture|negative|positive", re.I)
OUTDIR = os.environ.get("RS64_SWEEP_OUTDIR")  # s7720: keep every gate's full output (capture once, re-score offline)
FLAG_RE = re.compile(r"""["'](--check|--strict|--gate)["']""")
HOLLOW_OK = {  # s7720, each read by hand in scratch/s7720/out/<tool>.out
    "s7086_mem_branch_census.py": (r"^== mismatches: \d+ \(0 outside data_gap_/fake_func_\)$", "all mismatches in data_gap_/fake_func_ (the tool's own bound)"),
    "s7091_ucode_insn_census.py": (r"^region: resident [+-]\d+ [+-]\d+ splice-breaks \d+ unexplained \d+$", "per-control region lines under 'control dup/drop/splice-drop'"),
    "s7093_su_census.py": (r"on the synthetic set: bad \d+ \(must be > 0\)$", "pre-fix template on synthetic cases, must be > 0"),
    "s7392_mesg_census.py": (r"^SUMMARY .* missing=0$|\tREVIEW:[A-Z/-]+: ", "need_review counts risky sites; missing=0 = all reviewed (--check enforces); s7720b: counts inside a REVIEW:<verdict> row are the reviewer's prose ('10 fails in BOTH arms')"),
    "s7558_gr_census.py": (r"^UNGATED by verdict \{.*\} tags \d+ open/undoc 0$", "s7720b: 'tags N open/undoc 0' = N tags, 0 open (--check rc 0)"),
    "s7416_ctrl_flow.py": (r"^BAD \d+ by class \{'DATA_GAP\(callers=0\)': \d+, 'FIXUP_PATCH': \d+\}$", "BAD all classified; UNEXPLAINED is the gate"),
    "s7542_gc_census.py": (r"^PASS ", "control result lines"),
    "s7556_gp_census.py": (r"PASS \(bad=\d+\)$", "planted-control table"),
    "s7594_sg_census.py": (r"^\[ctl\] .* PASS$", "control line"),
    "s7085_int_census.py": (r"^\s*(ddivu|divu?)\s+UNGUARDED\s+\d+$", "s7721: 3 constant-divisor 32-bit divides + 2 ddivu fixed in recomp.h DDIVU (docs/N64RECOMP-WARNING-CENSUS.md s7085 rows); the gate is real_bad"),
    "s7359_strcopy_census.py": (r"^\d+ sites: .*ACC/UNGUARDED \d+", "s7721: every ACC/UNGUARDED row carries its type-bound proof; 'unresolved 0 orphan 0' is the gate"),
    "s7632_dd_census.py": (r"^== .*: scan=\d+ ast=\d+ joint=\d+ gate-agree=\d+ disagree=\d+ ", "s7721: a disagreeing pair with either side ALWAYS is classified via the union (always[]), the rest are off-default in both; OPEN default-on rows is the gate"),
    "s7633_hb_census.py": (r"^== .*: scan=\d+ ast=\d+ joint=\d+ gate-agree=\d+ disagree=\d+ ", "s7721: same join as s7632; OPEN default-on rows is the gate"),
    "s7648_mk8_census.py": (r"^\[s7648\] unclassified=3$", "the 3 planted ctl sites (tmp paths); a real one exits 1"),
    # s7723: the retained s7392 capture's nonzero rows are the planted control queue 801161F8 (guest S + ext host-thread
    # halves = "CONTROL PASS (guest=1 ext=1)") and the --known classified families (KNWN, tools/s7392_mesg_reviewed.tsv)
    "s7392_mq_report.py": (r"^(KNWN |[ES] mq=801161F8 (CONTROL|ext:host-thread) )", "s7723: planted control queue + KNWN families"),
}


def hollow_reason(name, src, argv, out):
    toks = []
    if OUTDIR:
        os.makedirs(OUTDIR, exist_ok=True)
        open(os.path.join(OUTDIR, name + ".out"), "w").write(out)
    for line in out.split("\n"):
        if not CONTROL_LINE.search(line) and HOLLOW_RE.search(line):
            toks.append(line.strip()[:160])
    if not out.strip():  # s7949: exit 0 with no output ran nothing (s7283 bare: 0 argv tags), a vacuous GREEN
        return "exit 0 with empty output: the gate checked nothing"
    unused = sorted({f for f in FLAG_RE.findall(src) if f not in argv})
    ok = HOLLOW_OK.get(name)
    if ok:
        toks = [t for t in toks if not re.search(ok[0], t)]
        unused = [f for f in unused if not re.search(ok[0], "flag " + f)]
    if not toks and not unused:
        return None
    parts = ([f"unused {' '.join(unused)}"] if unused else []) + ([f"{len(toks)} nonzero: {toks[0]}"] if toks else [])
    return "; ".join(parts)[:200]


TRACER = os.path.join(ROOT, "tools", "gate_trace.py")
CACHE_PATH = os.path.join(ROOT, "build", "gate_sweep_cache.json")
CACHE, CACHE_LOCK, STATS = {}, threading.Lock(), {"hit": 0, "miss": 0, "uncacheable": 0}
USE_CACHE = True
# s7659: per-gate cap. Cold AST regen measured 240 s max (s7607) at load 8-14 = 80% of the old 300 s; a timeout reads RED
# and blocks stop_gate, so the default is 600 s (a hung gate still dies). RS64_GATE_CAP overrides.
GATE_CAP = int(os.environ.get("RS64_GATE_CAP", "600"))


def fingerprint(argv, tr):
    h = hashlib.sha256(("\0".join(argv) + "\1").encode())
    st = os.stat(os.path.abspath(__file__))  # a classifier change in this sweep invalidates every entry
    h.update(f"s{st.st_size}\0{st.st_mtime_ns}\n".encode())
    for r in tr["reads"]:
        try:
            st = os.stat(r)
            h.update(f"r{r}\0{st.st_size}\0{st.st_mtime_ns}\n".encode())
        except OSError:
            h.update(f"r{r}\0missing\n".encode())
    for d in tr["dirs"]:
        try:
            h.update(f"d{d}\0{chr(0).join(sorted(os.listdir(d)))}\n".encode())
        except OSError:
            h.update(f"d{d}\0missing\n".encode())
    for g in tr["globs"]:
        h.update(f"g{g}\0{chr(0).join(sorted(glob.glob(g, recursive=True)))}\n".encode())
    for t in tr.get("stats", []):  # s7934: stat-only paths (exists/isfile/getsize): key on existence, type and file size
        try:
            st = os.stat(t)
            h.update(f"t{t}\0{'d' if os.path.isdir(t) else 'f' + str(st.st_size)}\n".encode())
        except OSError:
            h.update(f"t{t}\0missing\n".encode())
    return h.hexdigest()


# s7656: spawns whose output is a pure function of their file arguments (and, for compilers, the headers clang reports via
# CC_PRINT_HEADERS_FILE) can be keyed; anything else (git, a shell, an arbitrary program) keeps the tool uncacheable.
PURE = {"nm", "objdump", "llvm-objdump", "mips64-elf-objdump", "otool", "zstd", "llvm-nm"}
COMPILERS = {"cc", "c++", "clang", "clang++"}  # Apple cc/c++ are clang; gcc does not honour CC_PRINT_HEADERS_FILE
IFLAGS = ("-I", "-isystem", "-iquote", "-include", "-F")


def spawn_inputs(tr, hdr_lines):
    """-> (cacheable, extra_reads, extra_dirs, why) for the trace's subprocesses."""
    reads, dirs, outs, cwds, compiled = set(), set(), set(), {ROOT}, False
    for sp in tr.get("spawn", []):
        argv, cwd = sp["argv"], sp["cwd"]
        cwds.add(cwd)
        a0 = argv[0] if argv else ""
        a0abs = os.path.normpath(os.path.join(cwd, a0)) if "/" in a0 else None
        base = os.path.basename(a0)
        if sp.get("shell"):
            return False, (), (), f"shell spawn {a0[:40]}"
        if base in COMPILERS:
            if not sp.get("env_ok"):
                return False, (), (), f"{base} with a custom env (no header list)"
            compiled = True
        elif base not in PURE and not (a0abs and a0abs in outs):
            return False, (), (), f"spawns {base}"
        nxt_out = False
        for i, t in enumerate(argv[1:]):
            if nxt_out:
                outs.add(os.path.normpath(os.path.join(cwd, t)))
                nxt_out = False
                continue
            if t == "-o":
                nxt_out = True
                continue
            for f in IFLAGS:
                if t.startswith(f) and len(t) > len(f):
                    t = t[len(f):]
                    break
            if t.startswith("-"):
                continue
            q = os.path.normpath(os.path.join(cwd, t))
            if os.path.isfile(q):
                reads.add(q)
            elif os.path.isdir(q):
                dirs.add(q)  # an -I dir: a new header there can shadow a later one
    if compiled:  # env_ok held for every compile, so an empty list means no #include (s7607's header-less witness .c)
        for h in hdr_lines:
            h = h.strip().lstrip(". ") if h.startswith(".") and not h.startswith("./") and not h.startswith("../") else h.strip()
            if not h:
                continue
            if os.path.isabs(h):
                reads.add(h)
            else:
                reads.update(os.path.normpath(os.path.join(c, h)) for c in cwds)
    reads -= outs
    return True, sorted(reads), sorted(dirs), ""


def traced(path, a):
    """Run path with args a under the tracer; return (rc, out, trace-or-None)."""
    fd, tf = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.unlink(tf)
    try:
        p = subprocess.run([sys.executable, TRACER, path] + a, cwd=ROOT, capture_output=True, text=True, errors="replace",
                           timeout=GATE_CAP, env=dict(os.environ, RS64_GATE_TRACE=tf, CC_PRINT_HEADERS="1",
                                                 CC_PRINT_HEADERS_FILE=tf + ".hdr"))
        rc, out = p.returncode, p.stdout + p.stderr
        try:
            tr = json.load(open(tf))
        except (OSError, ValueError):
            tr = None
        if tr is not None:
            try:
                hdr = open(tf + ".hdr", errors="replace").read().splitlines()
            except OSError:
                hdr = []
            ok, er, ed, why = spawn_inputs(tr, hdr)
            tr["spawn_ok"], tr["why"] = ok, why
            tr["reads"] = sorted(set(tr["reads"]) | set(er))
            tr["dirs"] = sorted(set(tr["dirs"]) | set(ed))
        return rc, out, tr
    finally:
        for f in (tf, tf + ".hdr"):
            if os.path.exists(f):
                os.unlink(f)


OUTS = {}  # s7949: basename -> (src, argv, out) of the scored run, cached so later rule edits re-score cache hits
TIMES = {}  # s7659: per-gate wall seconds (cache hit ~0), printed as the slowest gates vs GATE_CAP


def run(path):
    t = time.time()
    try:
        return _run(path)
    finally:
        TIMES[os.path.basename(path)] = time.time() - t


def _run(path):
    key = os.path.abspath(path)
    if USE_CACHE:
        with CACHE_LOCK:
            ent = CACHE.get(key)
        if ent and ent.get("args_row") == repr(ARGS.get(os.path.basename(path))) and fingerprint(ent["argv"], ent["trace"]) == ent["fp"] \
                and "out" in ent:  # s7948: ARGS edit invalidates; s7949: pre-s7949 entries (no stored output) are misses
            row = tuple(ent["row"])
            name = os.path.basename(path)
            if name in REPORT or name in NEEDS_INPUT:  # s7949: a classification row edited since the hit: rescore
                row = None
            elif row[1] == "GREEN":  # s7949: hollow rules edited after the entry was written apply to the cached output
                hr = hollow_reason(name, open(path, errors="replace").read(), ent["argv"], ent["out"])
                if hr:
                    row = (name, "HOLLOW", row[2], hr)
            if row is not None:
                with CACHE_LOCK:
                    STATS["hit"] += 1
                return row
    row, argv, tr = run_uncached(path)
    cacheable = tr is not None and tr.get("complete") and tr.get("spawn_ok") and row[2] != "timeout"
    with CACHE_LOCK:
        STATS["miss" if cacheable else "uncacheable"] += 1
        if cacheable:
            CACHE[key] = {"argv": argv, "trace": tr, "fp": fingerprint(argv, tr), "row": list(row),
                          "args_row": repr(ARGS.get(os.path.basename(path))), "out": OUTS.get(os.path.basename(path), "")}
        else:
            CACHE.pop(key, None)
    return row


def run_uncached(path):
    src = open(path, errors="replace").read()
    rep = REPORT.get(os.path.basename(path))
    if rep and not EXIT_PATH.search(src):
        return (os.path.basename(path), "REPORT", "-", rep), [], {"reads": [os.path.abspath(path)], "dirs": [], "globs": [],
                                                                     "complete": True, "spawn_ok": True}
    a = ["--controls"] if "--controls" in src else []
    fixed, must = ARGS.get(os.path.basename(path), (None, None))
    if fixed is not None:
        # s7948: a missing input used to fall back to a bare run that read NEEDS-ARGS (allowed), so the s7925 WAITPAIR gate went
        # silently hollow when its ring was zstd'd (ring_q4.txt -> .zst). A row whose path inputs are missing is RED.
        miss = [x for x in fixed if "/" in x and not zresolve(os.path.join(ROOT, x.split(":")[0]))]  # s7950: PATH:kind:F0:F1 specs  # s7724: bare arm names are not paths;
        # zresolve: rs64-scratch-compress.sh (cron, 6 h) zstd --rm's >64k logs/txt/bin, and zopen tools read the raw path's .zst
        if miss:
            return (os.path.basename(path), "RED", "-", "ARGS input missing: " + " ".join(miss)), list(fixed), None
        a = list(fixed)
    else:
        must = None
    try:
        rc, out, tr = traced(path, a)
        OUTS[os.path.basename(path)] = out
    except subprocess.TimeoutExpired:
        return (os.path.basename(path), "RED", "timeout", f"timeout {GATE_CAP} s"), a, None
    tail = " | ".join(l.strip() for l in out.strip().split("\n")[-2:])[:200]
    if rc == 0 and must and not re.search(must, out):
        return (os.path.basename(path), "RED", rc, f"output lacks /{must}/: {tail}"), a, tr
    if rc == 0:
        hr = hollow_reason(os.path.basename(path), src, a, out)
        return (os.path.basename(path), "HOLLOW", rc, hr) if hr else (os.path.basename(path), "GREEN", rc, tail), a, tr
    if "--controls" in a and "unrecognized arguments: --controls" in out:  # mentions --controls in text only: retry bare
        a = []
        rc, out, tr = traced(path, a)
        OUTS[os.path.basename(path)] = out
        tail = " | ".join(l.strip() for l in out.strip().split("\n")[-2:])[:200]
        if rc == 0:
            hr = hollow_reason(os.path.basename(path), src, a, out)
            return (os.path.basename(path), "HOLLOW", rc, hr) if hr else (os.path.basename(path), "GREEN", rc, tail), a, tr
    ni = NEEDS_INPUT.get(os.path.basename(path))
    if ni and ni[0].search(out.strip()[-400:]):
        return (os.path.basename(path), "NEEDS-INPUT", rc, ni[1]), a, tr
    if fixed is not None:  # s7948: a tool given its ARGS row that still reports missing args/input is broken, not NEEDS-ARGS
        return (os.path.basename(path), "RED", rc, "ARGS row given, tool still fails: " + tail), a, tr
    return (os.path.basename(path), "NEEDS-ARGS" if ARGS_SIG.search(out[-3000:]) else "RED", rc, tail), a, tr


def cache_control(d):
    """Planted tool reading an input file: GREEN, then a cache hit, then RED once the input changes; a spawning tool is
    never cached. Uses its own cache dict so the real cache is untouched."""
    global CACHE, USE_CACHE
    saved, CACHE = CACHE, {}
    su, USE_CACHE = USE_CACHE, True  # s7659: the control tests the cache itself; --no-cache used to fail it (exit 3)
    s0 = dict(STATS)
    try:
        inp, tool = os.path.join(d, "cc_input.txt"), os.path.join(d, "cc_input_census.py")
        open(inp, "w").write("ok\n")
        open(tool, "w").write(f"import sys\nprint('cc')\nsys.exit(0 if open({inp!r}).read().strip() == 'ok' else 1)\n")
        r1 = run(tool)[1]
        h1 = STATS["hit"]
        r2 = run(tool)[1]
        hit = STATS["hit"] == h1 + 1
        time.sleep(0.01)
        open(inp, "w").write("broken\n")
        r3 = run(tool)[1]
        sp = os.path.join(d, "cc_spawn_census.py")
        open(sp, "w").write("import subprocess, sys\nsubprocess.run(['true'])\nprint('cc')\n")
        run(sp)
        spawn_uncached = os.path.abspath(sp) not in CACHE
        # compiler control: the tool reads only its .c; the header reaches the key via CC_PRINT_HEADERS alone
        hd, cs, ct = os.path.join(d, "cch"), os.path.join(d, "cc_m.c"), os.path.join(d, "cc_compile_census.py")
        os.makedirs(hd, exist_ok=True)
        open(os.path.join(hd, "cc_h.h"), "w").write("#define CC_OK 1\n")
        open(cs, "w").write('#include "cc_h.h"\nint x[CC_OK ? 1 : -1];\n')
        open(ct, "w").write("import subprocess, sys\nprint('cc')\n"
                            f"sys.exit(subprocess.run(['clang', '-fsyntax-only', '-I', {hd!r}, {cs!r}]).returncode)\n")
        c1 = run(ct)[1]
        hc = STATS["hit"]
        c2 = run(ct)[1]
        chit = STATS["hit"] == hc + 1
        time.sleep(0.01)
        open(os.path.join(hd, "cc_h.h"), "w").write("#define CC_OK 0\n")
        c3 = run(ct)[1]
        # s7678 import control: the verdict lives in an imported rows module; editing it must invalidate the entry even
        # when the import is served from __pycache__ (the s7677 stale-RED defect)
        md, mt = os.path.join(d, "cc_mod_rows.py"), os.path.join(d, "cc_import_census.py")
        open(md, "w").write("OK = True\n")
        open(mt, "w").write("import sys\nfrom cc_mod_rows import OK\nprint('cc')\nsys.exit(0 if OK else 1)\n")
        import py_compile  # pre-compile: the traced first run must load from __pycache__ only, never open the .py
        py_compile.compile(md, doraise=True)
        i1 = run(mt)[1]
        hi = STATS["hit"]
        i2 = run(mt)[1]
        ihit = STATS["hit"] == hi + 1
        time.sleep(0.01)
        open(md, "w").write("OK = False\n")
        i3 = run(mt)[1]
        got = (r1, r2, hit, r3, spawn_uncached, c1, c2, chit, c3, i1, i2, ihit, i3)
        return got == ("GREEN", "GREEN", True, "RED", True, "GREEN", "GREEN", True, "RED",
                       "GREEN", "GREEN", True, "RED"), got
    finally:
        CACHE = saved
        USE_CACHE = su
        STATS.update(s0)


def unswept(args, extra):
    """s7932: an ARGS row that discovery never runs (s7928's row sat in ARGS, not EXTRA_GATES, for a session)."""
    return sorted(k for k in args if not (re.match(r"s7\d+_.*_census\.py$", k) or k in extra))


def main():
    global USE_CACHE, CACHE
    if "--help" in sys.argv or "-h" in sys.argv:  # s7657: used to run a full sweep
        print(__doc__)
        sys.exit(0)
    t0 = time.time()
    USE_CACHE = "--no-cache" not in sys.argv
    if USE_CACHE:
        try:
            CACHE = json.load(open(CACHE_PATH))
        except (OSError, ValueError):
            CACHE = {}
    newvs = sys.argv[sys.argv.index("--new-red-vs") + 1] if "--new-red-vs" in sys.argv else None
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 2
    only = re.compile(sys.argv[sys.argv.index("--only") + 1]) if "--only" in sys.argv else None
    tsv = sys.argv[sys.argv.index("--tsv") + 1] if "--tsv" in sys.argv else None
    with tempfile.TemporaryDirectory() as d:
        bad, good = os.path.join(d, "ctl_red_census.py"), os.path.join(d, "ctl_green_census.py")
        open(bad, "w").write("import sys\nprint('UNCLASSIFIED 1')\nsys.exit(1)\n")
        open(good, "w").write("print('ok')\n")
        # s7655: NEEDS-INPUT is keyed by name + text: the right text reads NEEDS-INPUT, the same name failing otherwise reads RED
        ni_ok, ni_bad = os.path.join(d, "s7573_guard_census.py"), os.path.join(d, "ni", "s7573_guard_census.py")
        os.makedirs(os.path.dirname(ni_bad))
        open(ni_ok, "w").write("import sys\nprint('no game logs')\nsys.exit(1)\n")
        open(ni_bad, "w").write("import sys\nprint('OPEN 1')\nsys.exit(1)\n")
        c = {r[0]: r[1] for r in map(run, (bad, good))}
        c["ni_text"], c["ni_other"] = run(ni_ok)[1], run(ni_bad)[1]
        # s7657: REPORT holds only while the tool has no exit path: the same name failing via sys.exit must read RED
        rp_ok, rp_bad = os.path.join(d, "rp", "s7031_offmap_census.py"), os.path.join(d, "rq", "s7031_offmap_census.py")
        for f, body in ((rp_ok, "print('table')\n"), (rp_bad, "import sys\nprint('table')\nsys.exit(1)\n")):
            os.makedirs(os.path.dirname(f))
            open(f, "w").write(body)
        c["rep_noexit"], c["rep_exit"] = run(rp_ok)[1], run(rp_bad)[1]
        # s7720: the s7718 hollow row (OPEN 19, rc 0) must read HOLLOW, OPEN 0 GREEN, an unpassed --check HOLLOW
        for k, body in (("hol_open", "print('s7363 hostarr census')\nprint('OPEN 19')\n"), ("hol_zero", "print('OPEN 0 fail=0')\n"),
                        ("hol_flag", "import sys\nif '--check' in sys.argv: sys.exit(1)\nprint('table')\n"),
                        ("hol_s7721", "print('SUMMARY missing=3')\nprint('race=1')\n"),
                        ("hol_empty", "import sys\nfor t in sys.argv[1:]: print(t)\n")):
            f = os.path.join(d, k, "s9999_" + k + "_census.py")
            os.makedirs(os.path.dirname(f))
            open(f, "w").write(body)
            c[k] = run(f)[1]
        # s7948: an ARGS row whose input path is missing must read RED, not fall back to a bare NEEDS-ARGS run
        f = os.path.join(d, "am", "s9998_argmiss_census.py")
        os.makedirs(os.path.dirname(f))
        open(f, "w").write("import sys\nprint(open(sys.argv[1]).read())\n")
        ARGS["s9998_argmiss_census.py"] = (["scratch/s9998_absent/in.txt"], None)
        c["args_missing"] = run(f)[1]
        # s7948: a present input the tool still cannot open (plain open of a raw path that survives only as .zst) must read RED
        os.makedirs(os.path.join(ROOT, "scratch", "s9998_ctl"), exist_ok=True)
        zp = os.path.join(ROOT, "scratch", "s9998_ctl", "in.txt.zst")
        subprocess.run(["zstd", "-qf", "-o", zp, "-"], input=b"x\n", check=True)
        ARGS["s9998_argmiss_census.py"] = (["scratch/s9998_ctl/in.txt"], None)
        c["args_zst_plainopen"] = run(f)[1]
        shutil.rmtree(os.path.dirname(zp))
        del ARGS["s9998_argmiss_census.py"]
        for k in list(CACHE):  # controls never persist
            if k.startswith(os.path.abspath(d)):
                del CACHE[k]
        ccpass, cc = cache_control(d)
    cpass = c == {"ctl_red_census.py": "RED", "ctl_green_census.py": "GREEN", "ni_text": "NEEDS-INPUT", "ni_other": "RED",
                 "rep_noexit": "REPORT", "rep_exit": "RED",
                 "hol_open": "HOLLOW", "hol_zero": "GREEN", "hol_flag": "HOLLOW", "hol_s7721": "HOLLOW", "hol_empty": "HOLLOW",
                 "args_missing": "RED", "args_zst_plainopen": "RED"}
    print("[s7651] control planted red/green ->", c, "PASS" if cpass else "FAIL")
    print("[s7656] cache control read: green/green/hit/red-after-edit, spawn-uncached, compile: green/green/hit/red-after-header-edit, import: green/green/hit/red-after-module-edit ->", cc, "PASS" if ccpass else "FAIL")
    us_ctl = unswept({"s7999_plant_census.py": 0, "s9999_plant_gate.py": 0, "x.py": 0}, ("x.py",))
    us = unswept(ARGS, EXTRA_GATES)
    print("[s7932] unswept ARGS rows: planted ->", us_ctl, "PASS" if us_ctl == ["s9999_plant_gate.py"] else "FAIL",
          "| real ->", len(us), " ".join(us))
    if not (cpass and ccpass) or us_ctl != ["s9999_plant_gate.py"]:
        sys.exit(3)
    if us:
        sys.exit(1)
    for k in ("hit", "miss", "uncacheable"):
        STATS[k] = 0
    tools = sorted(os.path.join(ROOT, "tools", f) for f in os.listdir(os.path.join(ROOT, "tools"))
                   if (re.match(r"s7\d+_.*_census\.py$", f) or f in EXTRA_GATES) and (not only or only.search(f)))
    with cf.ThreadPoolExecutor(jobs) as ex:
        rows = sorted(ex.map(run, tools))
    from collections import Counter
    for name, cls, rc, tail in rows:
        if cls != "GREEN":
            print(f"  {cls:10s} rc={rc} {name}  {tail}")
    if tsv:
        with open(tsv, "w") as o:
            o.writelines(f"{n}\t{c}\t{r}\t{t}\t{TIMES.get(n, 0):.1f}\n" for n, c, r, t in rows)
    if USE_CACHE:
        live = {os.path.abspath(t) for t in tools}
        if not only:  # drop entries for deleted tools
            CACHE = {k: v for k, v in CACHE.items() if k in live}
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        json.dump(CACHE, open(CACHE_PATH + ".tmp", "w"))
        os.replace(CACHE_PATH + ".tmp", CACHE_PATH)
    slow = sorted(((TIMES.get(r[0], 0), r[0]) for r in rows), reverse=True)[:5]
    print(f"[s7659] slowest gates (s, cap {GATE_CAP}):", " ".join(f"{n}={v:.0f}" for v, n in slow))
    print("[s7651] gates", len(rows), dict(Counter(r[1] for r in rows)))
    print(f"[s7656] cache {'on' if USE_CACHE else 'off'} hit={STATS['hit']} miss={STATS['miss']} "
          f"uncacheable={STATS['uncacheable']} wall={time.time() - t0:.1f}s")
    red = [r[0] for r in rows if r[1] in ("RED", "HOLLOW")]  # s7720: HOLLOW blocks like RED
    if newvs:
        allowed = {l.split()[0] for l in open(newvs) if l.strip() and not l.startswith("#")} if os.path.exists(newvs) else set()
        new = [n for n in red if n not in allowed]
        print(f"[s7656] new RED vs {os.path.relpath(newvs, ROOT)}: {len(new)} {' '.join(new)}")
        sys.exit(1 if new else 0)
    sys.exit(1 if red else 0)  # NEEDS-ARGS / NEEDS-INPUT allowed


if __name__ == "__main__":
    main()
