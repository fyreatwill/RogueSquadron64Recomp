"""Post-process RSPRecomp output for the Factor 5 graphics ucode.

Fixups are idempotent. Pass either the main ucode file or the boot file —
fixups self-gate by detecting which file is being processed.

1. Replace `goto L_XXXX;` referring to undefined labels with a clean exit.
   RSPRecomp emits these for relative branches whose targets fall outside
   the recompiled function's PC range.

1a. Carve-out for `goto L_0000;` in the main ucode (s66/s67). That branch is
    a `bgez $2, +0xC` near end-of-IMEM in a perspective-divide block. Its
    target wraps RSP's 12-bit IMEM PC into the boot-resident ucode-self-reload
    trampoline (DMA the same ucode back into IMEM, `jr` to entry 0x1080).
    Modelling it as `return ImemOverrun` (the generic fixup-1 rule, written
    s1/s2 under "never taken in practice") was the initial s64 freeze
    suspect; s67 refuted it (live under NO_OPT, 0 fires). Instead: `goto
    RS64_UCODE_ENTRY` — skip the redundant DMA and re-enter this function's
    first real instruction. CLIP_1FBC's `j L_1650` is severed by fixup 1
    (label not yet defined) and restored by fixup 8 after fixup 6 inserts
    the resident L_1650: helper (s68 attribution, s69 reconnect).

1b. Silence the boot ucode's expected `jr $7=0x1080` printf (boot file only).
    factor5_boot ends by DMA'ing the main ucode to IMEM[0x1080] then doing
    `jr $7` to hand off. RSPRecomp can't model the inter-ucode jump, so it
    falls through to do_indirect_jump's default and prints a 4-line register
    dump every task. The runner already treats UnhandledJumpTarget as
    expected (see factor5_gfx_runner in src/main/main.cpp), so we gate the
    printf to only fire on *unexpected* targets.

2. Inject a per-task iteration cap at L_1090 (main ucode only).
   RSPRecomp lowers `mfc0 $X, SP_STATUS` to literal `rN = 0;` since the RSP
   coprocessor 0 isn't modeled. That makes the dispatch loop's halt-bit
   check (line in L_1090: `if (r2 != 0) goto L_11A8;`) dead — r2 is always
   0. The only natural exit (return Broke at L_10E8) is unreachable.
   Without a synthetic halt the recompile spins forever until it hits an
   unknown jump-target and returns UnhandledJumpTarget. The 16384-iter
   cap is high enough to handle any real DL chunk we've observed (cinematic
   tasks ~6/sec process << 16k commands each) and bounds the runaway case.
   The self-restart label (fixup 1a) sits AFTER `rs64_iter = 0` so a restart
   does not reset the counter — a restart loop still hits the cap.

Usage: python fixup_factor5_ucode.py <recompiled_c_file>
"""
import sys
import re
from pathlib import Path

if len(sys.argv) != 2:
    print(f"usage: {sys.argv[0]} <recompiled_c_file>", file=sys.stderr)
    sys.exit(1)

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
original = text

is_main_ucode = "factor5_ucode(" in text and "factor5_boot(" not in text

# ---------------------------------------------------------------------------
# Fixup 1a: L_0000 → self-restart (main ucode only). Must run before the
# generic undefined-goto pass so L_0000 is not hard-exited.
# ---------------------------------------------------------------------------
# s66: real hardware wraps the branch target into the boot-resident self-reload
# trampoline and re-enters this ucode at 0x1080. Cheap model: goto the entry
# label. rs64_dpc_defer_begin/end in main.cpp bracket the whole factor5_ucode()
# call and correctly do NOT re-fire (real hardware's jr also never returns to
# a caller). Iteration cap (fixup 2) keeps counting across the goto.
SELF_RESTART_MARKER = "/* fixup: L_0000 self-restart */"
ENTRY_LABEL = "RS64_UCODE_ENTRY"
self_restart_applied = False
if is_main_ucode and SELF_RESTART_MARKER not in text:
    # Fresh RSPRecomp output still has `goto L_0000;`.
    # Use [ \t]* not \s* so the indent group cannot swallow a preceding
    # newline (which would double-space every emitted line).
    fresh = re.compile(r"([ \t]*)goto\s+L_0000;")
    # Already-fixed form from a prior fixup-1 run. Allow an optional blank
    # line between the comment and the return (observed in the live tree).
    prior = re.compile(
        r"([ \t]*)// goto L_0000 — out-of-IMEM target, never taken in practice;\n"
        r"[ \t]*\n?"
        r"[ \t]*return RspExitReason::ImemOverrun;"
    )
    # Use a callable replacement so backslashes in the fprintf format string
    # are not re-interpreted by re.sub (`\n` in a string replacement becomes a
    # real newline; see the broken first cut of this fixup).
    #
    # The restart body is deliberately optimiszation-hostile: a file-scope
    # volatile counter + unconditional fprintf + a compiler barrier. s67 found
    # that under the ucode's forced -O2, a plain `static int` + rate-limited
    # fprintf + `goto RS64_UCODE_ENTRY` was entirely DCE'd (string absent from
    # the binary, freeze unrepaired) while the same code survived -O0. The
    # barrier keeps the path live so the runtime experiment is meaningful.
    def restart_repl(m: re.Match) -> str:
        ind = m.group(1)
        return (
            f"{ind}{SELF_RESTART_MARKER}\n"
            f"{ind}++rs64_restart_count;\n"
            f'{ind}if (rs64_restart_count <= 20 || (rs64_restart_count % 200) == 0) {{\n'
            f'{ind}    fprintf(stderr, "[ucode-restart] #%d\\n", (int)rs64_restart_count);\n'
            f"{ind}    fflush(stderr);\n"
            f"{ind}}}\n"
            f'{ind}asm volatile("" ::: "memory");\n'
            f"{ind}goto {ENTRY_LABEL};"
        )
    text, n_fresh = fresh.subn(restart_repl, text, count=1)
    text, n_prior = prior.subn(restart_repl, text, count=1)
    if n_fresh + n_prior != 1:
        print(
            f"fixup_factor5_ucode: FIXUP 1a ANCHOR FAILED (L_0000): "
            f"expected 1 L_0000 site, found fresh={n_fresh} prior={n_prior}.",
            file=sys.stderr,
        )
        sys.exit(1)
    self_restart_applied = True

    # Same IMEM-wrap self-restart for the fallthrough after the not-taken
    # bgez path: two more VMUL ops, then PC walks off end of IMEM and wraps
    # into boot on hardware. RSPRecomp emits a bare ImemOverrun return there
    # (not a goto, so fixup 1 never sees it). Without this, only the taken
    # path is fixed and the freeze can survive on the not-taken population.
    fallthrough = re.compile(
        r"(    // bgez        \$2, L_0000\n"
        r"    if \(RSP_SIGNED\(r2\) >= 0\) \{\n"
        r".*?"
        r"    goto " + re.escape(ENTRY_LABEL) + r";\n"
        r"    \}\n"
        r"    // vmadh       \$v7, \$v7, \$v30\[2\]\n"
        r"    rsp\.VMADH<10>\(rsp\.vpu\.r\[7\], rsp\.vpu\.r\[7\], rsp\.vpu\.r\[30\]\);\n"
        r"    // vmudn       \$v3, \$v3, \$v30\[3\]\n"
        r"    rsp\.VMUDN<11>\(rsp\.vpu\.r\[3\], rsp\.vpu\.r\[3\], rsp\.vpu\.r\[30\]\);\n"
        r"    // vmadh       \$v7, \$v7, \$v30\[3\]\n"
        r"    rsp\.VMADH<11>\(rsp\.vpu\.r\[7\], rsp\.vpu\.r\[7\], rsp\.vpu\.r\[30\]\);\n"
        r")    return RspExitReason::ImemOverrun;",
        flags=re.DOTALL,
    )
    def fall_repl(m: re.Match) -> str:
        return (
            m.group(1)
            + "    /* fixup: L_0000 self-restart fallthrough */\n"
            + "    ++rs64_restart_count;\n"
            + "    if (rs64_restart_count <= 20 || (rs64_restart_count % 200) == 0) {\n"
            + '        fprintf(stderr, "[ucode-restart] #%d (fallthrough)\\n", (int)rs64_restart_count);\n'
            + "        fflush(stderr);\n"
            + "    }\n"
            + '    asm volatile("" ::: "memory");\n'
            + "    goto " + ENTRY_LABEL + ";"
        )
    text, n_fall = fallthrough.subn(fall_repl, text, count=1)
    if n_fall != 1:
        print(
            f"fixup_factor5_ucode: FIXUP 1a ANCHOR FAILED (fallthrough): "
            f"expected 1 not-taken ImemOverrun after L_0000 bgez, found {n_fall}.",
            file=sys.stderr,
        )
        sys.exit(1)

    # File-scope volatile counter — lives across restarts, not DCE-able as a
    # block-local static under -O2 (s67). Check for the declaration itself
    # (not the name, which already appears in the goto bodies above).
    decl = "static volatile int rs64_restart_count = 0;"
    if decl not in text:
        text = text.replace(
            "RspExitReason factor5_ucode(",
            decl + "  " + SELF_RESTART_MARKER + "\n"
            "RspExitReason factor5_ucode(",
            1,
        )

# ---------------------------------------------------------------------------
# Fixup 1: undefined goto targets → clean exit
# ---------------------------------------------------------------------------
# Trailing-comment labels (e.g. "L_1650:  /* fixup: clipsplice */") count as
# defined too — s62 found the old \s*$-anchored form missed these, silently
# reclassifying real cross-references into fixup-6 clip-splice labels as
# "undefined" on any second run of this script and mangling live goto
# statements (goto rs64_clip_stray / goto L_1650) into dead ImemOverrun
# returns. This regex intentionally does not require end-of-line.
# L_0000 is handled by fixup 1a (self-restart); never hard-exit it here.
defined_labels = set(re.findall(r"^([A-Za-z_][A-Za-z_0-9]*):", text, flags=re.MULTILINE))
goto_targets = set(re.findall(r"goto\s+([A-Za-z_][A-Za-z_0-9]*);", text))
undefined = sorted(goto_targets - defined_labels)
if is_main_ucode:
    undefined = [lab for lab in undefined if lab not in (ENTRY_LABEL, "L_0000")]

for label in undefined:
    pattern = re.compile(r"(\s*)goto\s+" + re.escape(label) + r";")
    replacement = (
        r"\1// goto " + label + " — out-of-IMEM target, never taken in practice;\n"
        r"\1return RspExitReason::ImemOverrun;"
    )
    text = pattern.sub(replacement, text)

# ---------------------------------------------------------------------------
# Fixup 1b: silence boot's expected `jr $7=0x1080` exit
# ---------------------------------------------------------------------------
# factor5_boot ends by DMA'ing the main ucode to IMEM[0x1080] and then doing
# `jr $7` where r7 = 0x1080 to hand off to it. RSPRecomp can't model that
# inter-ucode jump, so it falls through to the do_indirect_jump default and
# prints a 4-line "Unhandled jump target" register dump. The runner already
# treats UnhandledJumpTarget from boot as expected (see factor5_gfx_runner in
# src/main/main.cpp), so the printf is pure spam — and at ~3 tasks/sec it
# floods stderr enough to starve the console pump (the same class of issue
# documented in project_factor5_lle_breakthrough.md).
#
# Gate the printf so it only fires for *unexpected* jump targets.
SILENCE_MARKER = "/* fixup: silence expected boot->main JR */"
if "factor5_boot(" in text and SILENCE_MARKER not in text:
    boot_printf_pattern = re.compile(
        r'(\n\s*)printf\("Unhandled jump target 0x%04X in microcode factor5_boot,',
        re.MULTILINE)
    if boot_printf_pattern.search(text):
        text = boot_printf_pattern.sub(
            r"\1if (jump_target != 0x1080) {  " + SILENCE_MARKER + r"\1"
            r'    printf("Unhandled jump target 0x%04X in microcode factor5_boot,',
            text, count=1)
        # Close the if-block right before `return RspExitReason::UnhandledJumpTarget;`.
        text = text.replace(
            "    return RspExitReason::UnhandledJumpTarget;\n}\n",
            "    }\n    return RspExitReason::UnhandledJumpTarget;\n}\n",
            1)

# ---------------------------------------------------------------------------
# Fixup 2: inject iter cap at L_1090 (main ucode only)
# ---------------------------------------------------------------------------
ITER_MARKER = "/* fixup: iter cap */"
R18_MARKER  = "/* fixup: r18 = 0x100 (ucode-state base in DMEM) */"
if is_main_ucode and ITER_MARKER not in text:
    # Insert a counter + r18 init at function entry (right after the local
    # var decls). Pattern: locals block ends with `RSP rsp{};`. Insert after.
    #
    # r18 init: Factor 5's main ucode treats $18 as the ucode-state base
    # address (DMEM 0x100), set by L_1DB0's bootstrap routine. RSPRecomp
    # doesn't preserve register state across the boot→main split (each
    # function starts with $r0..$r31 = 0). L_1DB0 normally bootstraps $18
    # via an indirect-jump dispatch, but if that dispatch never fires (or
    # fires only for the first task), $18 stays at 0 and reads from
    # DMEM[0x30] etc. land on unrelated static data.
    entry_pattern = re.compile(r"(\n    RSP rsp\{\};\n)")
    if entry_pattern.search(text):
        text = entry_pattern.sub(
            r"\1    int rs64_iter = 0;  " + ITER_MARKER + "\n"
            r"    r18 = 0x100;  " + R18_MARKER + "\n",
            text, count=1)

# ---------------------------------------------------------------------------
# Fixup 1a (label injection): RS64_UCODE_ENTRY sits AFTER rs64_iter = 0 / r18
# init so a self-restart does not zero the iteration cap or re-run r18 setup.
# Injected here (after fixup 2) so the anchors exist on both fresh and
# already-fixed input. Idempotent via SELF_RESTART_MARKER on the goto site;
# the label itself is detected by name.
# ---------------------------------------------------------------------------
if is_main_ucode and self_restart_applied and (ENTRY_LABEL + ":") not in text:
    # Prefer the post-fixup-2 form (r18 init present). Fall back to bare
    # `RSP rsp{};` only if fixup 2 somehow didn't run (shouldn't happen on
    # main ucode).
    entry_label_patterns = [
        # After r18 init (normal path once fixup 2 has run, or already present).
        (
            re.compile(
                r"(    r18 = 0x100;  " + re.escape(R18_MARKER) + r"\n)"
            ),
            r"\1" + ENTRY_LABEL + ":  " + SELF_RESTART_MARKER + "\n",
        ),
        # After rs64_iter alone (r18 marker shape drifted).
        (
            re.compile(
                r"(    int rs64_iter = 0;  " + re.escape(ITER_MARKER) + r"\n)"
            ),
            r"\1" + ENTRY_LABEL + ":  " + SELF_RESTART_MARKER + "\n",
        ),
    ]
    injected = False
    for pat, repl in entry_label_patterns:
        text, n = pat.subn(repl, text, count=1)
        if n == 1:
            injected = True
            break
    if not injected:
        print(
            "fixup_factor5_ucode: FIXUP 1a ANCHOR FAILED (entry label): "
            "could not find rs64_iter/r18 init to place RS64_UCODE_ENTRY after.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Insert the cap check right after the L_1090 label line.
    # Format: `L_1090:` followed by a comment then the actual instruction.
    # Also log first hit per process via a static counter so we know if the
    # cap is actually firing and at what task index.
    l1090_pattern = re.compile(r"(L_1090:\n)")
    if l1090_pattern.search(text):
        replacement = (
            "L_1090:\n"
            "    if (++rs64_iter > 16384) {  " + ITER_MARKER + "\n"
            "        static int rs64_cap_fires = 0;\n"
            "        if (++rs64_cap_fires <= 4 || (rs64_cap_fires & 63) == 0) {\n"
            '            fprintf(stderr, "[ucode-cap] fired #%d, last r17=0x%X\\n", rs64_cap_fires, r17);\n'
            "            fflush(stderr);\n"
            "        }\n"
            "        return RspExitReason::Broke;\n"
            "    }\n"
        )
        text = l1090_pattern.sub(lambda m: replacement, text, count=1)

# ---------------------------------------------------------------------------
# Fixup 2b: wire up rsp_task_log_and_reset() at the iter-cap synthetic-halt
# ---------------------------------------------------------------------------
# rsp_task_log_and_reset() (src/rsp/dpc_bridge.cpp) reads/resets the per-task
# RDP byte/cmd/FULL_SYNC counters and logs them under ROGUESQ_LOG_DPC=1, but
# as of s61 it was never called from anywhere — its own comment claims it
# runs "from the factor5_ucode synthetic-halt site", which per fixup 2 above
# IS the L_1090 iter cap (the natural halt at L_10E8 is unreachable — mfc0
# SP_STATUS is stubbed to always 0). Call it right before the cap's `return
# Broke` so each task that actually hits the cap gets one [task-brief]/[task]
# log line. **s62 measured this is a MINORITY of tasks** (823/5066 in one
# run) — most factor5_ucode() calls return via some other path in fewer than
# 16384 iterations, so this instrument only sees the subset of tasks that
# loop to the cap; it does not see every task the way the old (wrong, never
# tested pre-s62) belief assumed. data_size uses g_rsp_last_chunk_len
# (already extern-declared via librecomp/rsp.hpp, already used for the same
# purpose in the UnhandledJumpTarget diagnostic dump below) — the length of
# the most recent DMA-in chunk, the best available proxy for "this task's DL
# size".
LOG_MARKER = "/* fixup: task log call */"
if is_main_ucode and LOG_MARKER not in text:
    decl_pattern = re.compile(r"(\nRspExitReason factor5_ucode\()")
    if decl_pattern.search(text):
        text = decl_pattern.sub(
            r'\nextern "C" void rsp_task_log_and_reset(uint32_t iters, uint32_t data_size,'
            r' uint32_t r17, uint32_t cmd_w0, uint32_t cmd_w1);  ' + LOG_MARKER + r"\1",
            text, count=1)
    cap_return_pattern = re.compile(
        r'(fprintf\(stderr, "\[ucode-cap\] fired #%d, last r17=0x%X\\n", rs64_cap_fires, r17\);\n'
        r"            fflush\(stderr\);\n        \}\n)(        return RspExitReason::Broke;\n    \}\n)")
    if cap_return_pattern.search(text):
        text = cap_return_pattern.sub(
            r"\1        rsp_task_log_and_reset(rs64_iter, g_rsp_last_chunk_len, r17, r19, r20);  "
            + LOG_MARKER + r"\n\2",
            text, count=1)

# ---------------------------------------------------------------------------
# Fixup 3: per-task clip/cull census (ROGUESQ_UCODE_CULLSTATS=1), main ucode
# ---------------------------------------------------------------------------
# The band (hangar floor, game y 141-201) is pixels no triangle covers; s42
# proved geometry is submitted through those rows and s43 proved the drawn
# triangles carry wall-identical raster state. This census counts, per task,
# triangles entering the pipeline (L_17F0), reaching setup (L_1828), emitted
# (L_1930), and each reject branch: trivial clip reject (all 3 clip codes
# share a +/-w plane bit, mask 0x7070), clip-needed handoff to overlay 4
# (mask 0x4343 -> j L_1268 r5=4), backface (sign of 2D cross & cull-enable),
# degenerate (cross == 0). Every reject buckets the triangle's screen-y span
# (vertex +0x1A, 11.2 fixed) against the s43 windows wall/band/pad.
# Identities the run must satisfy (instrument control):
#   setup == eval - tclip - hand + fanjal
#   emit  == setup - bface - degen
CULL_MARKER = "/* fixup: cullstats */"
if is_main_ucode and CULL_MARKER not in text:
    helper_block = r'''
/* fixup: cullstats */
/* Per-task clip/cull census, ROGUESQ_UCODE_CULLSTATS=1. Windows in game-y
   pixels match the s43 ZSTATE census: wall 60-140, band 141-201, pad 220-320.
   Vertex screen y is 11.2 fixed at record +0x1A; game y = >>2. Classes:
   0=tclip 1=hand(clip overlay) 2=bface 3=degen. */
#include <cstdlib>
#include <cstdio>
static unsigned rs64_cs_taskctr = 0;
struct Rs64CullStats {
    unsigned idx;
    unsigned eval = 0, setup = 0, emit = 0, tclip = 0, hand = 0,
             bface = 0, degen = 0, fanjal = 0;
    unsigned band[4] = {0,0,0,0}, wall[4] = {0,0,0,0}, pad[4] = {0,0,0,0};
    static bool enabled() {
        static int v = -1;
        if (v < 0) { const char *e = std::getenv("ROGUESQ_UCODE_CULLSTATS"); v = (e && *e && *e != '0') ? 1 : 0; }
        return v == 1;
    }
    Rs64CullStats() { idx = ++rs64_cs_taskctr; }
    ~Rs64CullStats() {
        if (!enabled() || eval == 0) return;
        fprintf(stderr,
            "[cullstats t=%u eval=%u setup=%u emit=%u tclip=%u hand=%u bface=%u degen=%u fanjal=%u"
            " band=%u/%u/%u/%u wall=%u/%u/%u/%u pad=%u/%u/%u/%u]\n",
            idx, eval, setup, emit, tclip, hand, bface, degen, fanjal,
            band[0], band[1], band[2], band[3],
            wall[0], wall[1], wall[2], wall[3],
            pad[0], pad[1], pad[2], pad[3]);
        fflush(stderr);
    }
    void bucket(int cls, int y1, int y2, int y3) {
        int mn = y1 < y2 ? y1 : y2; if (y3 < mn) mn = y3;
        int mx = y1 > y2 ? y1 : y2; if (y3 > mx) mx = y3;
        mn >>= 2; mx >>= 2;   /* 11.2 fixed -> game pixels */
        if (mn <= 140 && mx >= 60)  wall[cls]++;
        if (mn <= 201 && mx >= 141) band[cls]++;
        if (mn <= 320 && mx >= 220) pad[cls]++;
    }
};
'''
    # RSP_MEM_HU_LOAD(off, base) zero-extends; cast down for the signed 11.2 y.
    y3args = ("(int)(int16_t)(uint16_t)RSP_MEM_HU_LOAD(0X1A, r11), "
              "(int)(int16_t)(uint16_t)RSP_MEM_HU_LOAD(0X1A, r12), "
              "(int)(int16_t)(uint16_t)RSP_MEM_HU_LOAD(0X1A, r13)")

    def sub_exactly(pattern, replacement, n, what):
        global text
        new_text, count = re.subn(pattern, replacement, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 3 ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting any cullstats output.", file=sys.stderr)
            sys.exit(1)
        text = new_text

    # Helper struct before the function.
    sub_exactly(
        re.compile(r"(RspExitReason factor5_ucode\(uint8_t\* rdram,)"),
        helper_block.replace("\\", "\\\\") + r"\1",
        1, "helper block")

    # Instance right after the RSP object (same anchor as fixup 2, distinct marker).
    sub_exactly(
        re.compile(r"(\n    RSP rsp\{\};\n)"),
        r"\1    Rs64CullStats rs64_cs;  " + CULL_MARKER + "\n",
        1, "rs64_cs instance")

    # Stage counters at the three pipeline labels.
    for label, field in (("L_17F0", "eval"), ("L_1828", "setup"), ("L_1930", "emit")):
        sub_exactly(
            re.compile(r"(" + label + r":\n)"),
            r"\1    rs64_cs." + field + "++;  " + CULL_MARKER + "\n",
            1, f"{label} {field} counter")

    # Reject (a): trivial clip reject -> L_1DA8 (unique goto).
    sub_exactly(
        re.compile(r"(        goto L_1DA8;\n)"),
        "        rs64_cs.tclip++; rs64_cs.bucket(0, " + y3args + ");  " + CULL_MARKER + "\n" + r"\1",
        1, "trivial-clip reject")

    # Reject (b): clip-needed handoff to overlay 4 (j L_1268 with r5=4).
    sub_exactly(
        re.compile(r"(    // j           L_1268\n    // ori         \$5, \$zero, 0x4\n)(    r5 = 0 \| 0X4;\n    goto L_1268;)"),
        r"\1" + "    rs64_cs.hand++; rs64_cs.bucket(1, " + y3args + ");  " + CULL_MARKER + "\n" + r"\2",
        1, "clip-overlay handoff")

    # Reject (c): backface cull (bltz $3, L_1DA4).
    sub_exactly(
        re.compile(r"(    // bltz        \$3, L_1DA4\n    if \(RSP_SIGNED\(r3\) < 0\) \{\n        // sh          \$13, 0x284\(\$zero\)\n        RSP_MEM_H_STORE\(0X284, 0, r13\);\n)(        goto L_1DA4;)"),
        r"\1" + "        rs64_cs.bface++; rs64_cs.bucket(2, " + y3args + ");  " + CULL_MARKER + "\n" + r"\2",
        1, "backface reject")

    # Reject (d): degenerate (beq $4, $zero, L_1DA4 at L_18F0). r11/r12/r13
    # were re-loaded permuted from the DMEM 0x280 mirrors — min/max unaffected.
    sub_exactly(
        re.compile(r"(    // beq         \$4, \$zero, L_1DA4\n    if \(r4 == 0\) \{\n        // vsub        \$v4, \$v15, \$v14\n        rsp\.VSUB<0>\(rsp\.vpu\.r\[4\], rsp\.vpu\.r\[15\], rsp\.vpu\.r\[14\]\);\n)(        goto L_1DA4;)"),
        r"\1" + "        rs64_cs.degen++; rs64_cs.bucket(3, " + y3args + ");  " + CULL_MARKER + "\n" + r"\2",
        1, "degenerate reject")

    # Clip-fan re-entry calls (jal 0x1828 inside the resident fan loop).
    sub_exactly(
        re.compile(r"(    // jal         0x1828\n)(    r31 = 0x1F14;)"),
        r"\1" + "    rs64_cs.fanjal++;  " + CULL_MARKER + "\n" + r"\2",
        1, "clip-fan jal")

# ---------------------------------------------------------------------------
# Fixup 4: overlay dispatch trace (ROGUESQ_UCODE_CULLSTATS=2), main ucode
# ---------------------------------------------------------------------------
# s45: clip-flagged triangles jump to L_1268 with r5=4 and never produce
# output (fanjal=0). The 0x76-table halfword read before the `jr $3` at
# L_1298 is BOTH the overlay DMA's IMEM destination and the jump target, and
# dma_rdram_to_dmem silently skips IMEM-destined writes — so the jr lands in
# whatever code the captured image held at that address. This trace records,
# per task: dispatch arrivals at L_1268 by overlay id (r5), jr dispatches at
# L_1298 by resident id (DMEM 0x153), the distinct (id, entry) pairs, the
# 0x76..0x84 table at first dispatch, and an execution profile of the
# 0x1D38..0x1F98 label region where the clip fan (jal 0x1828, r31=0x1F14)
# sits in the captured image. Level 2 implies the level-1 census (its
# enabled() treats any nonzero env as on), so `hand>0` in the same run is
# the positive control for this trace.
OVL_MARKER = "/* fixup: ovltrace */"
OVL_REGION_LABELS = ["L_1D38", "L_1DB0", "L_1E48", "L_1E5C", "L_1E6C",
                     "L_1E70", "L_1E80", "L_1EB8", "L_1ED8", "L_1EFC",
                     "L_1F14", "L_1F28", "L_1F48", "L_1F5C", "L_1F70",
                     "L_1F98"]
if is_main_ucode and OVL_MARKER not in text:
    ovl_helper = r'''
/* fixup: ovltrace */
/* Overlay dispatch trace, ROGUESQ_UCODE_CULLSTATS=2. See fixup 4 comments
   in tools/fixup_factor5_ucode.py. lbl[] order matches OVL_REGION_LABELS. */
static unsigned rs64_ot_taskctr = 0;
struct Rs64OvlTrace {
    unsigned idx;
    unsigned disp[8] = {0,0,0,0,0,0,0,0};   /* L_1268 arrivals by r5 */
    unsigned jrc[8]  = {0,0,0,0,0,0,0,0};   /* L_1298 jr by DMEM 0x153 */
    unsigned res4 = 0, load4 = 0, r4v4 = 0; /* ovl4 resident/fresh, 0x7A hw */
    unsigned tbl[8] = {0,0,0,0,0,0,0,0};    /* DMEM 0x76..0x84 at first jr */
    int tblset = 0;
    unsigned nrec = 0, recovl[8], recent[8]; /* distinct (id, entry) pairs */
    unsigned lbl[16] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    static bool on() {
        static int v = -1;
        if (v < 0) { const char *e = std::getenv("ROGUESQ_UCODE_CULLSTATS"); v = e ? std::atoi(e) : 0; }
        return v >= 2;
    }
    Rs64OvlTrace() { idx = ++rs64_ot_taskctr; }
    void rec(unsigned ov, unsigned en) {
        for (unsigned i = 0; i < nrec; i++) if (recovl[i] == ov && recent[i] == en) return;
        if (nrec < 8) { recovl[nrec] = ov; recent[nrec] = en; nrec++; }
    }
    ~Rs64OvlTrace() {
        if (!on()) return;
        unsigned any = 0;
        for (int i = 0; i < 8; i++) any += disp[i] + jrc[i];
        for (int i = 0; i < 16; i++) any += lbl[i];
        if (!any) return;
        fprintf(stderr,
            "[ovltrace t=%u disp=%u/%u/%u/%u/%u/%u/%u/%u jr=%u/%u/%u/%u/%u/%u/%u/%u"
            " res4=%u load4=%u r4v4=0x%04X tbl76=%04X,%04X,%04X,%04X,%04X,%04X,%04X,%04X recs=",
            idx, disp[0], disp[1], disp[2], disp[3], disp[4], disp[5], disp[6], disp[7],
            jrc[0], jrc[1], jrc[2], jrc[3], jrc[4], jrc[5], jrc[6], jrc[7],
            res4, load4, r4v4,
            tbl[0], tbl[1], tbl[2], tbl[3], tbl[4], tbl[5], tbl[6], tbl[7]);
        for (unsigned i = 0; i < nrec; i++) fprintf(stderr, "%s%u:0x%04X", i ? " " : "", recovl[i], recent[i]);
        fprintf(stderr, "]\n[ovllbl t=%u 1D38=%u 1DB0=%u 1E48=%u 1E5C=%u 1E6C=%u 1E70=%u 1E80=%u 1EB8=%u"
            " 1ED8=%u 1EFC=%u 1F14=%u 1F28=%u 1F48=%u 1F5C=%u 1F70=%u 1F98=%u]\n",
            idx, lbl[0], lbl[1], lbl[2], lbl[3], lbl[4], lbl[5], lbl[6], lbl[7],
            lbl[8], lbl[9], lbl[10], lbl[11], lbl[12], lbl[13], lbl[14], lbl[15]);
        fflush(stderr);
    }
};
'''

    def sub_exactly4(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 4 ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting any ovltrace output.", file=sys.stderr)
            sys.exit(1)
        text = new_text

    # Helper struct before the function (after fixup 3's helper).
    sub_exactly4(
        re.compile(r"(RspExitReason factor5_ucode\(uint8_t\* rdram,)"),
        lambda m: ovl_helper + m.group(1),
        1, "helper block")

    # Instance right after fixup 3's (fixup 3 must run first on a fresh regen).
    sub_exactly4(
        re.compile(r"(\n    Rs64CullStats rs64_cs;[^\n]*\n)"),
        lambda m: m.group(1) + "    Rs64OvlTrace rs64_ot;  " + OVL_MARKER + "\n",
        1, "rs64_ot instance")

    # L_1268 dispatch: r5=overlay id, r2=DMEM 0x153, r4=0x7A halfword (live
    # just before the resident-check beq).
    sub_exactly4(
        re.compile(r"(    // beq\s+\$5, \$2, L_1294\n)"),
        lambda m: ("    if (Rs64OvlTrace::on()) {  " + OVL_MARKER + "\n"
                   "        rs64_ot.disp[r5 & 7]++;\n"
                   "        if (r5 == 4) { rs64_ot.r4v4 = (unsigned)(r4 & 0xFFFF);"
                   " if (r5 == r2) rs64_ot.res4++; else rs64_ot.load4++; }\n"
                   "    }\n") + m.group(1),
        1, "L_1268 dispatch trace")

    # L_1298 jr: r3 = 0x76-table entry (both flows), DMEM 0x153 = overlay id.
    sub_exactly4(
        re.compile(r"(L_1298:\n)"),
        lambda m: m.group(1) + (
            "    if (Rs64OvlTrace::on()) {  " + OVL_MARKER + "\n"
            "        unsigned rs64_ov = (unsigned)RSP_MEM_BU(0X153, 0);\n"
            "        rs64_ot.jrc[rs64_ov & 7]++;\n"
            "        rs64_ot.rec(rs64_ov, (unsigned)(r3 & 0xFFFF));\n"
            "        if (!rs64_ot.tblset) {\n"
            "            rs64_ot.tblset = 1;\n"
            "            for (unsigned i = 0; i < 8; i++) rs64_ot.tbl[i] = (unsigned)RSP_MEM_HU_LOAD(0X76 + 2*i, 0);\n"
            "        }\n"
            "    }\n"),
        1, "L_1298 jr trace")

    # Execution-profile counters across the suspected overlay window.
    for i, lbl in enumerate(OVL_REGION_LABELS):
        sub_exactly4(
            re.compile(r"(" + lbl + r":\n)"),
            lambda m, i=i: m.group(1) + f"    if (Rs64OvlTrace::on()) rs64_ot.lbl[{i}]++;  " + OVL_MARKER + "\n",
            1, f"{lbl} counter")

# ---------------------------------------------------------------------------
# Fixup 5: stray 0x1DB0-entry source trace (ROGUESQ_UCODE_CULLSTATS=2)
# ---------------------------------------------------------------------------
# s46: ~40 do_indirect_jump arrivals per task at case 0x1DB0 do NOT come via
# the L_1298 dispatch jr (jrc sum 247 vs 287 label hits). Before the clip
# splice can route `case 0x1DB0:` by resident id (DMEM 0x153), we need to
# know where those strays come from (debug_line) and what 0x153 holds at
# that moment: 0x153==0 at every stray site → case-level routing is safe;
# otherwise routing must live only at L_1298. Records first 8 distinct
# (debug_line, 0x153) pairs per task, with counts.
STRAY_MARKER = "/* fixup: straytrace */"
if is_main_ucode and STRAY_MARKER not in text:
    stray_helper = r'''
/* fixup: straytrace */
/* Stray 0x1DB0-entry source trace, ROGUESQ_UCODE_CULLSTATS=2. See fixup 5
   comments in tools/fixup_factor5_ucode.py. */
struct Rs64StrayTrace {
    unsigned n = 0, total = 0, over = 0;
    unsigned line[8], s153[8], cnt[8];
    void rec(unsigned ln, unsigned sv) {
        total++;
        for (unsigned i = 0; i < n; i++)
            if (line[i] == ln && s153[i] == sv) { cnt[i]++; return; }
        if (n < 8) { line[n] = ln; s153[n] = sv; cnt[n] = 1; n++; } else over++;
    }
    ~Rs64StrayTrace() {
        if (!Rs64OvlTrace::on() || !total) return;
        fprintf(stderr, "[stray1db0 t=%u total=%u over=%u", rs64_ot_taskctr, total, over);
        for (unsigned i = 0; i < n; i++)
            fprintf(stderr, " ln%u/153=%u x%u", line[i], s153[i], cnt[i]);
        fprintf(stderr, "]\n");
        fflush(stderr);
    }
};
'''

    def sub_exactly5(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 5 ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting any stray1db0 output.", file=sys.stderr)
            sys.exit(1)
        text = new_text

    # Helper struct before the function, after fixup 4's helper (fixups 3 and
    # 4 must already be in `text` — they run earlier in this same script).
    sub_exactly5(
        re.compile(r"(RspExitReason factor5_ucode\(uint8_t\* rdram,)"),
        lambda m: stray_helper + m.group(1),
        1, "helper block")

    # Instance right after fixup 4's.
    sub_exactly5(
        re.compile(r"(\n    Rs64OvlTrace rs64_ot;[^\n]*\n)"),
        lambda m: m.group(1) + "    Rs64StrayTrace rs64_st;  " + STRAY_MARKER + "\n",
        1, "rs64_st instance")

    # Recorder immediately before the do_indirect_jump switch: every arrival
    # whose masked target is 0x1DB0, from whatever source (debug_line).
    sub_exactly5(
        re.compile(r"(    switch \(\(jump_target \| 0x1000\) & 0X1FFF\) \{[ \t]*\n)"),
        lambda m: ("    if (Rs64OvlTrace::on() && ((jump_target | 0x1000) & 0X1FFF) == 0x1DB0)  " + STRAY_MARKER + "\n"
                   "        rs64_st.rec((unsigned)debug_line, (unsigned)RSP_MEM_BU(0X153, 0));\n") + m.group(1),
        1, "case-0x1DB0 recorder")

# ---------------------------------------------------------------------------
# Fixup 6: splice the REAL clip overlay (overlay id 4) into the main ucode
# ---------------------------------------------------------------------------
# s46/s47: every overlay dispatch jumps to the shared window entry 0x1DB0,
# but the window-swap IMEM DMA is skipped by dma_rdram_to_dmem, so clip
# dispatches ran whatever the static translation holds there — the packed
# overlay-image STORAGE (init's image starts at window+8), not clip code.
# The real clip image lives at ROM 0x26420..0x2663F (== RDRAM capture,
# byte-exact, s47). factor5_rsp_ovl4.toml translates a composite ROM
# (scratch/s47_clip_composite.z64) whose window region holds that image;
# this fixup extracts its window-region translation (L_1DB0..), renames the
# labels CLIP_*, splices the block into the main file, and routes the
# do_indirect_jump window cases by resident id (DMEM 0x153 == 4 -> CLIP_*).
# DMEM 0x153 always holds the just-dispatched overlay id at every window
# entry (s47 stray census: 4221/4221 arrivals via the L_1298 jr, id set
# first), so case-level routing is safe. Also inserts the L_1650 resident
# label (the real clip code jumps there; the stale translation had no such
# branch so RSPRecomp emitted no label) and counts fanjal on the clip path
# so the fixup-3 identity setup == eval - tclip - hand + fanjal still holds.
CLIP_MARKER = "/* fixup: clipsplice */"
if is_main_ucode and CLIP_MARKER not in text:
    ovl4_path = path.parent / "factor5_ucode_ovl4_recompiled.c"
    if not ovl4_path.exists():
        print("fixup_factor5_ucode: FIXUP 6 INPUT MISSING: "
              f"{ovl4_path} not found. Run RSPRecomp on factor5_rsp_ovl4.toml "
              "(needs scratch/s47_clip_composite.z64) before fixing up the "
              "main ucode, or the clip overlay splice is lost.", file=sys.stderr)
        sys.exit(1)
    ovl4_text = ovl4_path.read_text(encoding="utf-8")

    def sub_exactly6(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6 ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the clip splice.", file=sys.stderr)
            sys.exit(1)
        text = new_text

    # Extract the window-region translation: L_1DB0 up to do_indirect_jump.
    m_start = re.search(r"^L_1DB0:\n", ovl4_text, flags=re.MULTILINE)
    m_end = re.search(r"^do_indirect_jump:\n", ovl4_text, flags=re.MULTILINE)
    if not m_start or not m_end or m_end.start() <= m_start.start():
        print("fixup_factor5_ucode: FIXUP 6 EXTRACTION FAILED: could not "
              "bound L_1DB0..do_indirect_jump in the ovl4 file.", file=sys.stderr)
        sys.exit(1)
    region = ovl4_text[m_start.start():m_end.start()]

    # Labels defined in the region get the CLIP_ prefix; references to labels
    # defined outside it (the resident helpers) stay L_*.
    region_labels = set(re.findall(r"^(L_[0-9A-F]{4}):", region, flags=re.MULTILINE))
    expected_resident = {"L_112C", "L_1650", "L_1780", "L_179C", "L_1828"}
    referenced = set(re.findall(r"goto (L_[0-9A-F]{4});", region))
    external = referenced - region_labels
    if external != expected_resident:
        print(f"fixup_factor5_ucode: FIXUP 6 SANITY FAILED: region's external "
              f"references {sorted(external)} != expected resident helpers "
              f"{sorted(expected_resident)}. The clip image or its translation "
              f"changed — re-derive before splicing.", file=sys.stderr)
        sys.exit(1)
    for lbl in region_labels:
        region = re.sub(r"\b" + lbl + r"\b", "CLIP_" + lbl[2:], region)

    # fanjal on the clip path (link register 0x1E34 here, vs the stale tail's
    # 0x1F14 that fixup 3 instruments).
    region, n_fj = re.subn(
        r"(    // jal         0x1828\n)(    r31 = 0x1E34;)",
        r"\1    rs64_cs.fanjal++;  " + CLIP_MARKER + "\n" + r"\2",
        region)
    if n_fj != 1:
        print(f"fixup_factor5_ucode: FIXUP 6 ANCHOR FAILED (clip fanjal): "
              f"expected 1 jal-0x1828 site in the region, found {n_fj}.",
              file=sys.stderr)
        sys.exit(1)

    # Stray sink for window-range dispatch targets arriving with a non-clip
    # resident id: previously these hit the switch default (unhandled); keep
    # that semantic but log the id so a new overlay's arrival is visible.
    region += (
        "rs64_clip_stray:  " + CLIP_MARKER + "\n"
        "    fprintf(stderr, \"[clip-stray] tgt=0x%04X 153=0x%02X line=%d\\n\",\n"
        "            jump_target, (unsigned)RSP_MEM_BU(0X153, 0), debug_line);\n"
        "    return RspExitReason::UnhandledJumpTarget;\n")

    # Splice the block right before do_indirect_jump (preceded by an
    # unconditional return, so no fall-through into CLIP_1DB0).
    sub_exactly6(
        re.compile(r"(^do_indirect_jump:\n)", flags=re.MULTILINE),
        lambda m: CLIP_MARKER + "\n" + region + m.group(1),
        1, "splice point")

    # Route the shared window entry by resident id.
    sub_exactly6(
        re.compile(r"(        case 0x1DB0: goto L_1DB0;\n)"),
        lambda m: ("        case 0x1DB0:  " + CLIP_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x4) goto CLIP_1DB0;\n"
                   "            goto L_1DB0;\n"),
        1, "case 0x1DB0 routing")

    # New window-range cases (the clip code's jal-return and register-loaded
    # return addresses; absent from the stale translation's switch, so they
    # previously fell to default).
    new_cases = "".join(
        f"        case 0x{a:04X}: if (RSP_MEM_BU(0X153, 0) == 0x4) "
        f"goto CLIP_{a:04X}; goto rs64_clip_stray;  {CLIP_MARKER}\n"
        for a in (0x1E1C, 0x1E34, 0x1E54, 0x1F38, 0x1FBC))
    sub_exactly6(
        re.compile(r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: new_cases + m.group(1),
        1, "new window cases")

    # Insert the L_1650 resident label (verified against the ovl4 translation,
    # where the identical resident bytes DO carry the label).
    sub_exactly6(
        re.compile(r"(    rsp\.VMADH<9>\(rsp\.vpu\.r\[29\], rsp\.vpu\.r\[11\], rsp\.vpu\.r\[30\]\);\n)(    // lsv         \$v21\[0\], 0x6\(\$zero\)\n)"),
        lambda m: m.group(1) + "L_1650:  " + CLIP_MARKER + "\n" + m.group(2),
        1, "L_1650 label")

# ---------------------------------------------------------------------------
# Fixup 7: ImemOverrun site attribution (s68) — main ucode only
# ---------------------------------------------------------------------------
# s67 refuted L_0000 as the freeze path. Two source-level
# `return RspExitReason::ImemOverrun` sites remain: CLIP_1FBC's fixup-1 hard
# exit for `j L_1650`, and a bare epilogue return after that block's nops.
# Both get a distinct call into `rs64_note_imem_overrun` (host stub in
# dpc_bridge.cpp, other TU, noinline) so default -O2 cannot DCE the instrument
# the way it erased s67's ucode-local volatile/fprintf. A once-per-process
# "control" call at RS64_UCODE_ENTRY is the same-run positive control.
# Must run BEFORE the early-exit equality check so a fully-fixed prior file
# still receives this instrumentation on re-run.
IMEM_NOTE_MARKER = "/* fixup: imem site note */"
imem_note_applied = False
if is_main_ucode and IMEM_NOTE_MARKER not in text:
    # Host-stub declaration next to the existing task-log extern if present,
    # otherwise just before factor5_ucode.
    if "extern \"C\" void rsp_task_log_and_reset" in text:
        text = text.replace(
            'extern "C" void rsp_task_log_and_reset(uint32_t iters, uint32_t data_size,'
            ' uint32_t r17, uint32_t cmd_w0, uint32_t cmd_w1);  /* fixup: task log call */',
            'extern "C" void rsp_task_log_and_reset(uint32_t iters, uint32_t data_size,'
            ' uint32_t r17, uint32_t cmd_w0, uint32_t cmd_w1);  /* fixup: task log call */\n'
            'extern "C" void rs64_note_imem_overrun(const char* site);  ' + IMEM_NOTE_MARKER,
            1,
        )
    else:
        text = text.replace(
            "RspExitReason factor5_ucode(",
            'extern "C" void rs64_note_imem_overrun(const char* site);  ' + IMEM_NOTE_MARKER + "\n"
            "RspExitReason factor5_ucode(",
            1,
        )

    # Positive control: first entry into RS64_UCODE_ENTRY only.
    # Prefer the post-fixup-1a labelled form; fall back to post-r18-init.
    control_body = (
        '    { static int rs64_imem_ctrl = 0; if (!rs64_imem_ctrl) {'
        ' rs64_imem_ctrl = 1; rs64_note_imem_overrun("control"); } }  '
        + IMEM_NOTE_MARKER + "\n"
    )
    control_patterns = [
        (
            re.compile(
                r"(RS64_UCODE_ENTRY:  /\* fixup: L_0000 self-restart \*/\n)"
            ),
            r"\1" + control_body,
        ),
        (
            re.compile(
                r"(    r18 = 0x100;  " + re.escape(R18_MARKER) + r"\n)"
            ),
            r"\1" + control_body,
        ),
    ]
    n_ctrl = 0
    for pat, repl in control_patterns:
        text, n_ctrl = pat.subn(repl, text, count=1)
        if n_ctrl == 1:
            break
    if n_ctrl != 1:
        print(
            "fixup_factor5_ucode: FIXUP 7 ANCHOR FAILED (control): "
            "could not place rs64_note_imem_overrun(\"control\") at entry.",
            file=sys.stderr,
        )
        sys.exit(1)

    # L_1650 hard-exit site (CLIP_1FBC → j L_1650 rewritten by fixup 1).
    l1650 = re.compile(
        r"(// goto L_1650 — out-of-IMEM target, never taken in practice;\n"
        r"\n?"
        r")([ \t]*)return RspExitReason::ImemOverrun;"
    )
    def l1650_repl(m: re.Match) -> str:
        ind = m.group(2)
        return (
            m.group(1)
            + ind + 'rs64_note_imem_overrun("L_1650");  ' + IMEM_NOTE_MARKER + "\n"
            + ind + "return RspExitReason::ImemOverrun;"
        )
    text, n_l1650 = l1650.subn(l1650_repl, text, count=1)
    if n_l1650 == 0 and "// goto L_1650" not in text:
        # Recent RSPRecomp output omits this out-of-range jump entirely; the
        # tail is already a direct ImemOverrun return, so there is no L_1650
        # path to attribute or reconnect.
        n_l1650 = 1
    if n_l1650 != 1:
        print(
            f"fixup_factor5_ucode: FIXUP 7 ANCHOR FAILED (L_1650): "
            f"expected 1 L_1650 ImemOverrun site, found {n_l1650}.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Bare epilogue return immediately before rs64_clip_stray.
    epilogue = re.compile(
        r"([ \t]*)return RspExitReason::ImemOverrun;\n"
        r"(rs64_clip_stray:  /\* fixup: clipsplice \*/)"
    )
    def epi_repl(m: re.Match) -> str:
        ind = m.group(1)
        return (
            ind + 'rs64_note_imem_overrun("epilogue");  ' + IMEM_NOTE_MARKER + "\n"
            + ind + "return RspExitReason::ImemOverrun;\n"
            + m.group(2)
        )
    text, n_epi = epilogue.subn(epi_repl, text, count=1)
    if n_epi != 1:
        print(
            f"fixup_factor5_ucode: FIXUP 7 ANCHOR FAILED (epilogue): "
            f"expected 1 bare ImemOverrun before rs64_clip_stray, found {n_epi}.",
            file=sys.stderr,
        )
        sys.exit(1)

    imem_note_applied = True

# ---------------------------------------------------------------------------
# Fixup 8: reconnect CLIP_1FBC → goto L_1650 (s69) — main ucode only
# ---------------------------------------------------------------------------
# s68: every exit=2 (ImemOverrun) is the fixup-1 hard exit at CLIP_1FBC's
# `j L_1650`. The target label L_1650: is inserted by fixup 6 (clip-splice
# resident helper, byte-identical to ovl4). Fixup 1 runs *before* that label
# exists, so it rewrites the goto into ImemOverrun. This pass restores the
# goto once the label is present. The host-stub note becomes a "path taken"
# counter (site=L_1650_enter), not an error — positive control at entry
# (site=control) still required in the same run.
L1650_RECONNECT_MARKER = "/* fixup: L_1650 reconnect */"
l1650_reconnect_applied = False
if is_main_ucode and L1650_RECONNECT_MARKER not in text:
    if not re.search(r"^L_1650:", text, flags=re.MULTILINE):
        print(
            "fixup_factor5_ucode: FIXUP 8 PRECONDITION FAILED: L_1650: label "
            "missing (fixup 6 must define it before reconnect).",
            file=sys.stderr,
        )
        sys.exit(1)
    # Match s68 instrumented hard-exit, or bare fixup-1 form if fixup 7 skipped.
    l1650_hard = re.compile(
        r"// goto L_1650 — out-of-IMEM target, never taken in practice;\n"
        r"\n?"
        r"(?:[ \t]*rs64_note_imem_overrun\(\"L_1650\"\);  /\* fixup: imem site note \*/\n)?"
        r"([ \t]*)return RspExitReason::ImemOverrun;"
    )
    def l1650_reconnect_repl(m: re.Match) -> str:
        ind = m.group(1)
        return (
            f"// j L_1650 (restored after label exists; s69)  {L1650_RECONNECT_MARKER}\n"
            f"{ind}rs64_note_imem_overrun(\"L_1650_enter\");  /* fixup: imem site note */\n"
            f"{ind}goto L_1650;"
        )
    text, n_reconnect = l1650_hard.subn(l1650_reconnect_repl, text, count=1)
    if n_reconnect == 0 and "// goto L_1650" not in text:
        # See fixup 7: newer output has no severed L_1650 jump.
        n_reconnect = 1
    if n_reconnect != 1:
        print(
            f"fixup_factor5_ucode: FIXUP 8 ANCHOR FAILED: expected 1 CLIP_1FBC "
            f"L_1650 hard-exit site to reconnect, found {n_reconnect}.",
            file=sys.stderr,
        )
        sys.exit(1)
    l1650_reconnect_applied = True

# ---------------------------------------------------------------------------
# Fixup 9: phase-scoped guest-E9 → DPC provenance (s678, item -421).
#
# The guest display-list fetch at L_1090 is the only common point before the
# microcode dispatch table.  Record an E9 there; the host bridge joins it to
# emitted/output E9 bytes and the eventual deferred submit for this LLE task.
# This does not change the dispatch, ring, or command lengths.
# ---------------------------------------------------------------------------
E9_PROVENANCE_MARKER = "/* fixup: e9 provenance */"
if is_main_ucode and E9_PROVENANCE_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rsp_task_log_and_reset[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) +
        'extern "C" void rs64_e9prov_guest(uint32_t guest_addr, uint32_t w0);  ' +
        E9_PROVENANCE_MARKER + "\n",
        text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 9 ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    fetch_anchor = re.compile(
        r"(    r20 = RSP_MEM_W_LOAD\(0X4, r17\);\n)(    (?:\{ /\* PATCH: diag — trace every op fetch|// andi        \$2, \$2, 0x80))")
    text, n_fetch = fetch_anchor.subn(
        lambda m: m.group(1) +
        "    if ((r19 >> 24) == 0xE9) rs64_e9prov_guest(r17, r19);  " +
        E9_PROVENANCE_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_fetch != 1:
        print("fixup_factor5_ucode: FIXUP 9 ANCHOR FAILED (L_1090 E9 fetch).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 10: source-stream completion audit (s686, item -421).
#
# E9 provenance alone records only E9 fetches. Count every L_1090 fetch and
# stamp the actual return path so a three-E9 target can be distinguished from
# an early/reset LLE exit. The all-fetch count is the same-run positive
# control: a target row with source_fetch=0 is invalid, regardless of E9s.
# ---------------------------------------------------------------------------
SOURCE_AUDIT_MARKER = "/* fixup: source stream audit */"
if is_main_ucode and SOURCE_AUDIT_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_e9prov_guest[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) +
        'extern "C" void rs64_e9prov_source_fetch(uint32_t guest_addr, uint32_t w0);\n'
        'extern "C" void rs64_e9prov_source_end(uint32_t guest_addr, uint32_t kind);  ' +
        SOURCE_AUDIT_MARKER + "\n",
        text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 10 ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    fetch_anchor = re.compile(
        r"(    if \(\(r19 >> 24\) == 0xE9\) rs64_e9prov_guest\(r17, r19\);[^\n]*\n)")
    text, n_fetch = fetch_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_e9prov_source_fetch(r17, r19);  " + SOURCE_AUDIT_MARKER + "\n",
        text, count=1)
    if n_fetch != 1:
        print("fixup_factor5_ucode: FIXUP 10 ANCHOR FAILED (L_1090 all-fetch).", file=sys.stderr)
        sys.exit(1)
    natural_anchor = re.compile(
        r"(L_10E8:\n(?:.*\n){0,8}?    // break       0\n)(    return RspExitReason::Broke;)")
    text, n_natural = natural_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_e9prov_source_end(r17, 1);  " + SOURCE_AUDIT_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_natural != 1:
        print("fixup_factor5_ucode: FIXUP 10 ANCHOR FAILED (L_10E8 natural exit).", file=sys.stderr)
        sys.exit(1)
    cap_anchor = re.compile(
        r"(if \(\+\+rs64_iter > 16384\) \{  /\* fixup: iter cap \*/.*?)(        return RspExitReason::Broke;)",
        flags=re.DOTALL)
    def cap_repl(m: re.Match) -> str:
        return m.group(1) + "        rs64_e9prov_source_end(r17, 2);  " + SOURCE_AUDIT_MARKER + "\n" + m.group(2)
    text, n_cap = cap_anchor.subn(cap_repl, text)
    if n_cap < 1:
        print("fixup_factor5_ucode: FIXUP 10 ANCHOR FAILED (iter-cap exit).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 11: EndDL/unwind audit (s687, item -421).
#
# The source audit established that the phase-latched cap tasks fetch 16K
# commands without a natural return.  Record each L_12C4 entry after its depth
# decrement, including whether that decrement takes the direct L_10E8 exit.
# This is observational only: it must not alter the RSP control flow.
# ---------------------------------------------------------------------------
UNWIND_AUDIT_MARKER = "/* fixup: EndDL unwind audit */"
if is_main_ucode and UNWIND_AUDIT_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_e9prov_source_end[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) +
        'extern "C" void rs64_e9prov_unwind(uint32_t stack_byte, uint32_t natural);  ' +
        UNWIND_AUDIT_MARKER + "\n",
        text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 11 ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    unwind_anchor = re.compile(
        r"(L_12C4:\n(?:.*\n){0,8}?    r8 = RSP_ADD32\(r8, -0X8\);\n)(    // bltz        \$8, L_10E8\n    if \(RSP_SIGNED\(r8\) < 0\) \{)")
    text, n_unwind = unwind_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_e9prov_unwind(r8, RSP_SIGNED(r8) < 0 ? 1u : 0u);  " +
        UNWIND_AUDIT_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_unwind != 1:
        print("fixup_factor5_ucode: FIXUP 11 ANCHOR FAILED (L_12C4 decrement).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 12: saved display-list frame audit (s688-s690, item -421).
#
# EndDL visits alone cannot tell a stale saved PC from a bad push. Capture the
# stack slot and both saved words at push/pop, then the PC actually restored at
# L_12DC. The host retains only bounded first/last events for phase-latched
# tasks; this remains observational and leaves the branch sequence unchanged.
# ---------------------------------------------------------------------------
FRAME_AUDIT_MARKER = "/* fixup: saved DL frame audit v3 */"
if is_main_ucode and FRAME_AUDIT_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_e9prov_unwind[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) +
        'extern "C" void rs64_e9prov_frame_push(uint32_t slot, uint32_t saved_target, uint32_t saved_pc, uint32_t caller, uint32_t w0, uint32_t w1);\n'
        'extern "C" void rs64_e9prov_frame_pop(uint32_t slot, uint32_t saved_target, uint32_t saved_pc);\n'
        'extern "C" void rs64_e9prov_frame_resume(uint32_t slot, uint32_t resumed_pc);  ' +
        FRAME_AUDIT_MARKER + "\n",
        text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 12 ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    push_anchor = re.compile(
        r"(L_12A0:\n(?:.*\n){0,10}?    RSP_MEM_W_STORE\(0X654, r2, r17\);\n)(    // addiu\s+\$2, \$2, 0x8)")
    text, n_push = push_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_e9prov_frame_push(r2, r3, r17, r31, r19, r20);  " + FRAME_AUDIT_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_push != 1:
        print("fixup_factor5_ucode: FIXUP 12 ANCHOR FAILED (L_12A0 saved frame).", file=sys.stderr)
        sys.exit(1)
    pop_anchor = re.compile(
        r"(L_12C4:\n(?:.*\n){0,18}?    r2 = RSP_MEM_W_LOAD\(0X650, r8\);\n)(    goto L_11B4;)")
    text, n_pop = pop_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_e9prov_frame_pop(r8, r2, RSP_MEM_W_LOAD(0X654, r8));  " + FRAME_AUDIT_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_pop != 1:
        print("fixup_factor5_ucode: FIXUP 12 ANCHOR FAILED (L_12C4 restored frame).", file=sys.stderr)
        sys.exit(1)
    resume_anchor = re.compile(
        r"(L_12DC:\n(?:.*\n){0,5}?    r17 = RSP_MEM_W_LOAD\(0X654, r8\);\n)(    goto L_1088;)")
    text, n_resume = resume_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_e9prov_frame_resume(r8, r17);  " + FRAME_AUDIT_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_resume != 1:
        print("fixup_factor5_ucode: FIXUP 12 ANCHOR FAILED (L_12DC resumed PC).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 12b: attribute each L_12A0 frame to its dispatch table (s731, -421).
#
# The normal opcode table reaches L_12A0 from L_1090; a DMA-fed overlay table
# can also reach it from L_1298. Preserve the source immediately before each
# indirect jump and attach it to the existing push/pop/resume frame record.
# ---------------------------------------------------------------------------
L12A0_SOURCE_MARKER = "/* fixup: L_12A0 source audit v1 */"
if is_main_ucode and L12A0_SOURCE_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_e9prov_frame_resume[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) +
        'extern "C" void rs64_e9prov_l12a0_source(uint32_t source, uint32_t r17, uint32_t w0, uint32_t w1, uint32_t target);  ' +
        L12A0_SOURCE_MARKER + "\n",
        text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 12b ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    direct_anchor = re.compile(
        r"(    r2 = RSP_MEM_HU_LOAD\(0XD6, r2\);\n)(    rs64_inline_probe_dispatch|    // jr)")
    text, n_direct = direct_anchor.subn(
        lambda m: m.group(1) +
        "    if (r2 == 0x12A0) rs64_e9prov_l12a0_source(1, r17, r19, r20, r2);  " + L12A0_SOURCE_MARKER + "\n" + m.group(2),
        text, count=1)
    overlay_anchor = re.compile(r"(L_1298:\n)([\s\S]{0,900}?    // jr          \$3)")
    text, n_overlay = overlay_anchor.subn(
        lambda m: m.group(1) +
        "    if (r3 == 0x12A0) rs64_e9prov_l12a0_source(2, r17, r19, r20, r3);  " + L12A0_SOURCE_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_direct != 1 or n_overlay != 1:
        print(f"fixup_factor5_ucode: FIXUP 12b ANCHOR FAILED (direct={n_direct} overlay={n_overlay}).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 12c: correlate the TriGen continuation's depth reset with depth-0
# display-list-frame reuse (s733, item -421). The callback is deliberately
# before the sole generated store so it observes the pre-reset byte.
# ---------------------------------------------------------------------------
RESET_REUSE_MARKER = "/* fixup: L_1DB0 depth-reset route audit v2 */"
if is_main_ucode and RESET_REUSE_MARKER not in text:
    reset_decl = re.compile(r'extern "C" void rs64_e9prov_l1db0_reset[^\n]*\n')
    if reset_decl.search(text):
        text, n_decl = reset_decl.subn(
            'extern "C" void rs64_e9prov_l1db0_reset(uint32_t old, uint32_t r17, uint32_t ra, uint32_t resident);  ' +
            RESET_REUSE_MARKER + "\n", text, count=1)
    else:
        decl_anchor = re.compile(r"(extern \"C\" void rs64_e9prov_l12a0_source[^\n]*\n)")
        text, n_decl = decl_anchor.subn(
            lambda m: m.group(1) +
            'extern "C" void rs64_e9prov_l1db0_reset(uint32_t old, uint32_t r17, uint32_t ra, uint32_t resident);  ' +
            RESET_REUSE_MARKER + "\n",
            text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 12c ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    old_reset = re.compile(r'^[ \t]*rs64_e9prov_l1db0_reset\([^\n]*\);[^\n]*\n', re.MULTILINE)
    if old_reset.search(text):
        text, n_reset = old_reset.subn(
            "    rs64_e9prov_l1db0_reset(RSP_MEM_BU(0X52, r18), r17, r31, RSP_MEM_BU(0X153, 0));  " +
            RESET_REUSE_MARKER + "\n", text, count=1)
    else:
        reset_anchor = re.compile(
            r"(L_1DB0:\n[\s\S]{0,1200}?)([ \t]*RSP_MEM_B\(0X52, r18\) = 0;)")
        text, n_reset = reset_anchor.subn(
            lambda m: m.group(1) +
            "    rs64_e9prov_l1db0_reset(RSP_MEM_BU(0X52, r18), r17, r31, RSP_MEM_BU(0X153, 0));  " +
            RESET_REUSE_MARKER + "\n" + m.group(2),
            text, count=1)
    if n_reset != 1:
        print("fixup_factor5_ucode: FIXUP 12c ANCHOR FAILED (L_1DB0 reset).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 13: live inline-data command advance audit (s714, item -421).
#
# The universal dispatcher has already advanced r17 by eight at both table
# loads. Record the live DMA-provided table word there, then close the sample
# only when execution returns to L_1090. This measures the handler-local extra
# advance without guessing which generated label a DMA/overlay table word names.
# ---------------------------------------------------------------------------
INLINE_ADVANCE_MARKER = "/* fixup: inline advance audit v3 */"
if is_main_ucode and INLINE_ADVANCE_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_e9prov_frame_resume[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: (m.group(1)
        + 'extern "C" void rs64_inline_probe_resume(uint32_t r17);\n'
        + 'extern "C" void rs64_inline_probe_dispatch(uint32_t r17, uint32_t w0, uint32_t table_kind, uint32_t table_word);\n'
        + 'extern "C" void rs64_inline_probe_route(uint32_t r17, uint32_t target, uint32_t line);\n'
        + 'extern "C" void rs64_inline_probe_step(uint32_t r17, uint32_t delta, uint32_t site);\n'
        + 'extern "C" void rs64_inline_probe_overlay(uint32_t r17, uint32_t selector);  '
        + INLINE_ADVANCE_MARKER + "\n"),
        text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 13 ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    fetch_anchor = re.compile(
        r"(L_1090:\n)(    if \(\+\+rs64_iter > 16384\) \{)")
    text, n_fetch = fetch_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_inline_probe_resume(r17);  " + INLINE_ADVANCE_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_fetch != 1:
        print("fixup_factor5_ucode: FIXUP 13 ANCHOR FAILED (L_1090 resume).", file=sys.stderr)
        sys.exit(1)
    table1_anchor = re.compile(
        r"(    r2 = RSP_MEM_HU_LOAD\(0XD6, r2\);\n)(    // jr          \$2)")
    text, n_table1 = table1_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_inline_probe_dispatch(r17, r19, 1, r2);  " + INLINE_ADVANCE_MARKER + "\n" + m.group(2),
        text, count=1)
    table2_anchor = re.compile(
        r"(    r2 = RSP_MEM_HU_LOAD\(0X64, r2\);\n)(    // jr          \$2)")
    text, n_table2 = table2_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_inline_probe_dispatch(r17, r19, 2, r2);  " + INLINE_ADVANCE_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_table1 != 1 or n_table2 != 1:
        print(f"fixup_factor5_ucode: FIXUP 13 ANCHOR FAILED (table loads): table1={n_table1} table2={n_table2}.", file=sys.stderr)
        sys.exit(1)
    route_anchor = re.compile(r"(do_indirect_jump:\n)(    if \(Rs64OvlTrace::on\(\))")
    text, n_route = route_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_inline_probe_route(r17, jump_target, (uint32_t)debug_line);  " + INLINE_ADVANCE_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_route != 1:
        print("fixup_factor5_ucode: FIXUP 13 ANCHOR FAILED (TriGen indirect route).", file=sys.stderr)
        sys.exit(1)
    tri_step_anchor = re.compile(
        r"(L_13A8:\n[\s\S]{0,8000}?[ \t]*r17 = RSP_ADD32\(r17, 0X8\);\n)([ \t]*goto L_1464;)")
    text, n_tri_step = tri_step_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_inline_probe_step(r17, 8, 0x13A8);  " + INLINE_ADVANCE_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_tri_step != 1:
        print("fixup_factor5_ucode: FIXUP 13 ANCHOR FAILED (L_13A8 short Tri advance).", file=sys.stderr)
        sys.exit(1)
    tri_tex_step_anchor = re.compile(
        r"(L_13A8:\n[\s\S]{0,10000}?[ \t]*r17 = RSP_ADD32\(r17, 0X10\);\n)([ \t]*// slv         \$v2\[0\], 0x14\(\$11\))")
    text, n_tri_tex_step = tri_tex_step_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_inline_probe_step(r17, 16, 0x13B0);  " + INLINE_ADVANCE_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_tri_tex_step != 1:
        print("fixup_factor5_ucode: FIXUP 13 ANCHOR FAILED (L_13A8 textured Tri advance).", file=sys.stderr)
        sys.exit(1)
    trigen_overlay_anchor = re.compile(
        r"(L_15AC:\n[\s\S]{0,800}?[ \t]*r5 = 0 \| 0XC;\n)([ \t]*goto L_1268;)")
    text, n_trigen_overlay = trigen_overlay_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_inline_probe_overlay(r17, r5);  " + INLINE_ADVANCE_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_trigen_overlay != 1:
        print("fixup_factor5_ucode: FIXUP 13 ANCHOR FAILED (L_15AC TriGen overlay).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 14: TriGen resident continuation r17 audit (s717, item -421).
#
# L_1DB0 is reached through the live 0x05 -> L_15AC overlay-0x0C relay. It
# does not directly increment r17; L_1E80 reloads the next command pointer
# immediately before returning to L_1090. Keep this separate from the shared
# route budget so the continuation row cannot be consumed by other commands.
# ---------------------------------------------------------------------------
TRIGEN_CONTINUATION_MARKER = "/* fixup: TriGen continuation audit v1 */"
if is_main_ucode and TRIGEN_CONTINUATION_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_inline_probe_overlay[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: (m.group(1)
        + 'extern "C" void rs64_inline_probe_trigen_entry(uint32_t r17);\n'
        + 'extern "C" void rs64_inline_probe_trigen_reload(uint32_t r17);  '
        + TRIGEN_CONTINUATION_MARKER + "\n"),
        text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 14 ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    entry_anchor = re.compile(r"(L_1DB0:\n)([ \t]*if \(Rs64OvlTrace::on\(\)\))")
    text, n_entry = entry_anchor.subn(
        lambda m: m.group(1) + "    rs64_inline_probe_trigen_entry(r17);  " + TRIGEN_CONTINUATION_MARKER + "\n" + m.group(2),
        text, count=1)
    reload_anchor = re.compile(
        r"(L_1E80:\n[\s\S]{0,300}?[ \t]*r17 = RSP_MEM_HU_LOAD\(0X54, r18\);\n)([ \t]*// j           L_1090)")
    text, n_reload = reload_anchor.subn(
        lambda m: m.group(1) + "    rs64_inline_probe_trigen_reload(r17);  " + TRIGEN_CONTINUATION_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_entry != 1 or n_reload != 1:
        print(f"fixup_factor5_ucode: FIXUP 14 ANCHOR FAILED (entry={n_entry} reload={n_reload}).", file=sys.stderr)
        sys.exit(1)

TRIGEN_EXIT_MARKER = "/* fixup: TriGen continuation exits v2 */"
if is_main_ucode and TRIGEN_EXIT_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_inline_probe_trigen_reload[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) + 'extern "C" void rs64_inline_probe_trigen_exit(uint32_t r17, uint32_t site);  ' + TRIGEN_EXIT_MARKER + "\n",
        text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 14B ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    for label in ("L_1E48", "L_1E5C", "L_1E70", "L_1E80", "L_11B0"):
        label_anchor = re.compile(rf"({label}:\n)([ \t]*(?:if|//))")
        text, n_label = label_anchor.subn(
            lambda m, site=label: m.group(1) +
            f"    rs64_inline_probe_trigen_exit(r17, 0x{site[2:]});  " + TRIGEN_EXIT_MARKER + "\n" + m.group(2),
            text, count=1)
        if n_label != 1:
            print(f"fixup_factor5_ucode: FIXUP 14B ANCHOR FAILED ({label} exit).", file=sys.stderr)
            sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 15: TriGen physical command-buffer source correlation (s719, item -421).
#
# L_11B0 copies DMEM[0x130] into a new buffer at DMEM 0x170 and preserves that
# DRAM base at DMEM[0x15c]. On the next L_1DB0, r17 is an offset inside that
# buffer; capture both sources after the new refill word has been loaded.
# ---------------------------------------------------------------------------
TRIGEN_SOURCE_MARKER = "/* fixup: TriGen physical source audit v1 */"
if is_main_ucode and TRIGEN_SOURCE_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_inline_probe_trigen_exit[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) + 'extern "C" void rs64_inline_probe_trigen_sources(uint32_t r17, uint32_t entry_dram, uint32_t refill_dram);  ' + TRIGEN_SOURCE_MARKER + "\n",
        text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 15 ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    source_anchor = re.compile(
        r"(L_1DB0:\n[\s\S]{0,1200}?[ \t]*r2 = RSP_MEM_W_LOAD\(0X30, r1\);\n)([ \t]*// sw          \$2, 0x30\(\$18\))")
    text, n_source = source_anchor.subn(
        lambda m: m.group(1) + "    rs64_inline_probe_trigen_sources(r17, RSP_MEM_W_LOAD(0X15C, 0), r2);  " + TRIGEN_SOURCE_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_source != 1:
        print("fixup_factor5_ucode: FIXUP 15 ANCHOR FAILED (L_1DB0 sources).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 16: direct TriGen L_11B0 chunk-source capture (s723, item -421).
# ---------------------------------------------------------------------------
TRIGEN_CHUNK_MARKER = "/* fixup: TriGen L_11B0 chunk source audit v1 */"
if is_main_ucode and TRIGEN_CHUNK_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_inline_probe_trigen_sources[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) + 'extern "C" void rs64_inline_probe_trigen_chunk(uint32_t r17, uint32_t chunk_dram);  ' + TRIGEN_CHUNK_MARKER + "\n",
        text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 16 ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    chunk_anchor = re.compile(
        r"(L_11B0:\n[\s\S]{0,400}?[ \t]*r2 = RSP_MEM_W_LOAD\(0X30, r18\);\n)(L_11B4:)")
    text, n_chunk = chunk_anchor.subn(
        lambda m: m.group(1) + "    rs64_inline_probe_trigen_chunk(r17, r2);  " + TRIGEN_CHUNK_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_chunk != 1:
        print("fixup_factor5_ucode: FIXUP 16 ANCHOR FAILED (L_11B0 chunk source).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 17: TriGen L_1DB0 DPC-branch trace (s726, item -421).
#
# The source is DMEM[r1+0x30] (0xFF0) copied to state[0x30]/0x130. Record
# exactly one selected DPC exit for the first 16 active phase-3 TriGen routes.
# ---------------------------------------------------------------------------
TRIGEN_BRANCH_MARKER = "/* fixup: TriGen L_1DB0 branch audit v1 */"
if is_main_ucode and TRIGEN_BRANCH_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_inline_probe_trigen_chunk[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) + 'extern "C" void rs64_inline_probe_trigen_branch(uint32_t r17, uint32_t source_dram, uint32_t dpc_end, uint32_t dpc_current, uint32_t branch);  ' + TRIGEN_BRANCH_MARKER + "\n",
        text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 17 ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    branches = [
        (r"(r2 = RSP_MEM_W_LOAD\(0X4, r1\);\n[\s\S]{0,300}?RSP_MEM_W_STORE\(0X4, r1, 0\);\n)([ \t]*goto L_1E70;)", 0),
        (r"(r2 = r2 & 0X1;\n[\s\S]{0,300}?r2 = RSP_DPC_END_READ\(\);\n)([ \t]*goto L_1E48;)", 1),
        (r"(r16 = RSP_SUB32\(r16, r2\);\n[\s\S]{0,300}?r3 = RSP_DPC_CURRENT_READ\(\);\n)([ \t]*goto L_1E48;)", 2),
        (r"(if \(r3 == 0\) \{[\s\S]{0,300}?)(        goto L_1E48;)", 3),
        (r"(if \(r3 == r2\) \{[\s\S]{0,300}?)(        goto L_1E48;)", 4),
        (r"(r4 = 0 \| r2;\n)([ \t]*goto L_1E5C;)", 5),
    ]
    for pattern, branch in branches:
        anchor = re.compile(pattern)
        text, n_branch = anchor.subn(
            lambda m, b=branch: m.group(1) +
            f"    rs64_inline_probe_trigen_branch(r17, RSP_MEM_W_LOAD(0X30, r18), r2, r3, {b});  " + TRIGEN_BRANCH_MARKER + "\n" + m.group(2),
            text, count=1)
        if n_branch != 1:
            print(f"fixup_factor5_ucode: FIXUP 17 ANCHOR FAILED (branch {branch}).", file=sys.stderr)
            sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 18: record L_11B0's actual indirect continuation (s726).
# ---------------------------------------------------------------------------
TRIGEN_RETURN_MARKER = "/* fixup: TriGen L_11B0 return audit v1 */"
if is_main_ucode and TRIGEN_RETURN_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_inline_probe_trigen_branch[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) + 'extern "C" void rs64_inline_probe_trigen_return(uint32_t r17, uint32_t source_dram, uint32_t target);  ' + TRIGEN_RETURN_MARKER + "\n",
        text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 18 ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    return_anchor = re.compile(
        r"(L_11B0:\n[\s\S]{0,1800}?jump_target = r31;\n)([ \t]*debug_file = __FILE__;)")
    text, n_return = return_anchor.subn(
        lambda m: m.group(1) + "    rs64_inline_probe_trigen_return(r17, RSP_MEM_W_LOAD(0X30, r18), jump_target);  " + TRIGEN_RETURN_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_return != 1:
        print("fixup_factor5_ucode: FIXUP 18 ANCHOR FAILED (L_11B0 return).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------

# Make sure <cstdio> is available for the iter-cap fprintf.
if "#include <cstdio>" not in text:
    text = text.replace('#include "librecomp/rsp.hpp"',
                        '#include <cstdio>\n#include "librecomp/rsp.hpp"', 1)

if text == original:
    sys.exit(0)

path.write_text(text, encoding="utf-8")
notes = []
if undefined:
    notes.append(f"replaced {len(undefined)} undefined goto target(s): {', '.join(undefined)}")
if SELF_RESTART_MARKER in text and SELF_RESTART_MARKER not in original:
    notes.append("L_0000 → RS64_UCODE_ENTRY self-restart (s67)")
if ITER_MARKER in text and ITER_MARKER not in original:
    notes.append("injected iter cap at L_1090")
if SILENCE_MARKER in text and SILENCE_MARKER not in original:
    notes.append("silenced boot->main JR printf")
if CULL_MARKER in text and CULL_MARKER not in original:
    notes.append("injected cullstats census (ROGUESQ_UCODE_CULLSTATS)")
if OVL_MARKER in text and OVL_MARKER not in original:
    notes.append("injected overlay dispatch trace (ROGUESQ_UCODE_CULLSTATS=2)")
if STRAY_MARKER in text and STRAY_MARKER not in original:
    notes.append("injected stray-0x1DB0 source trace (ROGUESQ_UCODE_CULLSTATS=2)")
if CLIP_MARKER in text and CLIP_MARKER not in original:
    notes.append("spliced real clip overlay (CLIP_* labels, id-4 routing)")
if imem_note_applied:
    notes.append("ImemOverrun site notes (L_1650/epilogue/control)")
if l1650_reconnect_applied:
    notes.append("CLIP_1FBC → goto L_1650 reconnect (s69)")
if E9_PROVENANCE_MARKER in text and E9_PROVENANCE_MARKER not in original:
    notes.append("guest-E9 to DPC provenance audit (s678)")
if SOURCE_AUDIT_MARKER in text and SOURCE_AUDIT_MARKER not in original:
    notes.append("source-stream completion audit (s686)")
if UNWIND_AUDIT_MARKER in text and UNWIND_AUDIT_MARKER not in original:
    notes.append("EndDL/unwind audit (s687)")
if INLINE_ADVANCE_MARKER in text and INLINE_ADVANCE_MARKER not in original:
    notes.append("live inline-data advance audit (s714)")
if TRIGEN_CONTINUATION_MARKER in text and TRIGEN_CONTINUATION_MARKER not in original:
    notes.append("TriGen resident continuation audit (s717)")
if TRIGEN_SOURCE_MARKER in text and TRIGEN_SOURCE_MARKER not in original:
    notes.append("TriGen physical source audit (s719)")

print(f"fixup_factor5_ucode: {path} — " + ("; ".join(notes) if notes else "updated"), file=sys.stderr)
