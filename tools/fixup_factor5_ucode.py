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
is_shade_ucode = is_main_ucode or "factor5_ucode_ovl20(" in text

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
# Fixup 6b: splice resident overlay 12 (id 0x0C) into the main ucode
# ---------------------------------------------------------------------------
# s738: the live section-2 L_1DB0 reset is the main bootstrap image, not the
# overlay-12 TriGen image at ROM 0x26670. factor5_rsp_ovl12.toml translates a
# composite whose window holds that image; this fixup extracts L_1DB0..,
# renames labels OVL12_*, splices the block, and routes DMEM 0x153 == 0xC.
# Must run after fixup 6 so case 0x1DB0 is already in the clip-routed form.
# Jal returns through resident L_122C / internal L_1FD4 need window cases.
OVL12_MARKER = "/* fixup: ovl12splice */"
if is_main_ucode and OVL12_MARKER not in text:
    ovl12_path = path.parent / "factor5_ucode_ovl12_recompiled.c"
    if not ovl12_path.exists():
        print("fixup_factor5_ucode: FIXUP 6b INPUT MISSING: "
              f"{ovl12_path} not found. Run RSPRecomp on factor5_rsp_ovl12.toml "
              "(needs scratch/s47_trigen_composite.z64) before fixing up the "
              "main ucode, or the overlay-12 splice is lost.", file=sys.stderr)
        sys.exit(1)
    ovl12_text = ovl12_path.read_text(encoding="utf-8")

    def sub_exactly6b(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6b ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the overlay-12 splice.", file=sys.stderr)
            sys.exit(1)
        text = new_text

    m_start = re.search(r"^L_1DB0:\n", ovl12_text, flags=re.MULTILINE)
    m_end = re.search(r"^do_indirect_jump:\n", ovl12_text, flags=re.MULTILINE)
    if not m_start or not m_end or m_end.start() <= m_start.start():
        print("fixup_factor5_ucode: FIXUP 6b EXTRACTION FAILED: could not "
              "bound L_1DB0..do_indirect_jump in the ovl12 file.", file=sys.stderr)
        sys.exit(1)
    region = ovl12_text[m_start.start():m_end.start()]

    region_labels = set(re.findall(r"^(L_[0-9A-F]{4}):", region, flags=re.MULTILINE))
    expected_resident = {"L_122C", "L_1268"}
    referenced = set(re.findall(r"goto (L_[0-9A-F]{4});", region))
    external = referenced - region_labels
    if external != expected_resident:
        print(f"fixup_factor5_ucode: FIXUP 6b SANITY FAILED: region's external "
              f"references {sorted(external)} != expected resident helpers "
              f"{sorted(expected_resident)}. The overlay-12 image or its "
              f"translation changed — re-derive before splicing.", file=sys.stderr)
        sys.exit(1)
    for lbl in region_labels:
        region = re.sub(r"\b" + lbl + r"\b", "OVL12_" + lbl[2:], region)

    sub_exactly6b(
        re.compile(r'(extern "C" void rsp_task_log_and_reset\([^\n]*\n)'),
        lambda m: m.group(1) +
        'extern "C" void rs64_e9prov_ovl_route(uint32_t resident, uint32_t target);  ' +
        OVL12_MARKER + "\n",
        1, "ovl_route declaration")

    sub_exactly6b(
        re.compile(r"(^do_indirect_jump:\n)", flags=re.MULTILINE),
        lambda m: OVL12_MARKER + "\n" + region + m.group(1),
        1, "splice point")

    sub_exactly6b(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x4\) goto CLIP_1DB0;\n"
            r"            goto L_1DB0;\n)"),
        lambda m: ("        case 0x1DB0:  " + CLIP_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x4) {"
                   " rs64_e9prov_ovl_route(0x4, 0x1DB0); goto CLIP_1DB0; }\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0xC) {"
                   " rs64_e9prov_ovl_route(0xC, 0x1DB0); goto OVL12_1DB0; }\n"
                   "            goto L_1DB0;\n"),
        1, "case 0x1DB0 overlay-12 routing")

    sub_exactly6b(
        re.compile(
            r"(        case 0x1FBC: if \(RSP_MEM_BU\(0X153, 0\) == 0x4\) "
            r"goto CLIP_1FBC; goto rs64_clip_stray;  /\* fixup: clipsplice \*/\n)"),
        lambda m: ("        case 0x1FBC:  " + OVL12_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x4) goto CLIP_1FBC;\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0xC) {"
                   " rs64_e9prov_ovl_route(0xC, 0x1FBC); goto OVL12_1FBC; }\n"
                   "            goto rs64_clip_stray;\n"),
        1, "shared case 0x1FBC")

    ovl12_only = "".join(
        f"        case 0x{a:04X}: if (RSP_MEM_BU(0X153, 0) == 0xC) {{ "
        f"rs64_e9prov_ovl_route(0xC, 0x{a:04X}); goto OVL12_{a:04X}; }} "
        f"goto rs64_clip_stray;  {OVL12_MARKER}\n"
        for a in (0x1DD8, 0x1DF4, 0x1F9C, 0x1FAC, 0x1FCC))
    sub_exactly6b(
        re.compile(r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: ovl12_only + m.group(1),
        1, "overlay-12 window cases")

# ---------------------------------------------------------------------------
# Fixup 6c: route overlay 24 (emit @ 0x12A0) and overlay 28 (r17+=32)
# ---------------------------------------------------------------------------
# s742: skipped IMEM writer of the post-s739 UJ storm is overlay 0x24
# (ROM 0x27260, dest 0x12A0, emit) plus overlay 0x28 (ROM 0x27348, dest
# 0x1DB0, addiu $17,32 then restore-DMA of main L_12A0). Do not overwrite
# main L_12A0 — overlay 28 exists to put DL-push back. factor5_rsp_ovl24.toml
# translates a composite whose 0x12A0 range holds the emit image; this
# fixup extracts L_12A0..end-of-overlay, renames OVL24_*, splices the
# block, and routes DMEM 0x153 == 0x24 at dest 0x12A0 (and the handshake
# / jal-return cases). Resident 0x28 at dest 0x1DB0 is the seven-instruction
# overlay: r17 += 32; goto L_10D8. The restore DMA is a no-op in C.
OVL24_MARKER = "/* fixup: ovl24route */"
OVL24_END = 0x1384  # dest 0x12A0 + inclusive 0xE3 + 1
if is_main_ucode and OVL24_MARKER not in text:
    ovl24_path = path.parent / "factor5_ucode_ovl24_recompiled.c"
    if not ovl24_path.exists():
        print("fixup_factor5_ucode: FIXUP 6c INPUT MISSING: "
              f"{ovl24_path} not found. Run make_clip_composite.py 24 and "
              "RSPRecomp on factor5_rsp_ovl24.toml before fixing up the "
              "main ucode, or the overlay-24 route is lost.", file=sys.stderr)
        sys.exit(1)
    ovl24_text = ovl24_path.read_text(encoding="utf-8")

    def sub_exactly6c(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6c ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the overlay-24 route.", file=sys.stderr)
            sys.exit(1)
        text = new_text

    m_start = re.search(r"^L_12A0:\n", ovl24_text, flags=re.MULTILINE)
    after = [(int(m.group(1), 16), m.start())
             for m in re.finditer(r"^L_([0-9A-F]{4}):", ovl24_text, flags=re.MULTILINE)
             if int(m.group(1), 16) >= OVL24_END]
    if not m_start or not after:
        print("fixup_factor5_ucode: FIXUP 6c EXTRACTION FAILED: could not "
              "bound L_12A0..first-label-past-overlay in the ovl24 file.",
              file=sys.stderr)
        sys.exit(1)
    region = ovl24_text[m_start.start():after[0][1]]
    # Drop the unreachable main-image tail RSPRecomp emits after jr $ra.
    last_jr = None
    for last_jr in re.finditer(
            r"    goto do_indirect_jump;\n(?:    // [^\n]*\n    [^\n]*\n)?",
            region):
        pass
    if last_jr:
        region = region[:last_jr.end()]

    region_labels = set(re.findall(r"^(L_[0-9A-F]{4}):", region, flags=re.MULTILINE))
    expected_external = {"L_112C", "L_1268", "L_15D0", "L_17F0"}
    referenced = set(re.findall(r"goto (L_[0-9A-F]{4});", region))
    external = referenced - region_labels
    if external != expected_external:
        print(f"fixup_factor5_ucode: FIXUP 6c SANITY FAILED: region's external "
              f"references {sorted(external)} != expected resident helpers "
              f"{sorted(expected_external)}. The overlay-24 image or its "
              f"translation changed — re-derive before routing.", file=sys.stderr)
        sys.exit(1)
    if "L_12A0" not in region_labels or "L_12AC" not in region_labels:
        print("fixup_factor5_ucode: FIXUP 6c SANITY FAILED: missing emit "
              "entry/handshake labels "
              f"{sorted(region_labels)}.", file=sys.stderr)
        sys.exit(1)
    for lbl in region_labels:
        region = re.sub(r"\b" + lbl + r"\b", "OVL24_" + lbl[2:], region)

    sub_exactly6c(
        re.compile(r'(extern "C" void rs64_e9prov_ovl_route\([^\n]*\n)'),
        lambda m: m.group(1) +
        'extern "C" void rs64_e9prov_l1298_12a0_res(uint32_t resident);  ' +
        OVL24_MARKER + "\n",
        1, "l1298_12a0_res declaration")

    sub_exactly6c(
        re.compile(r"(^do_indirect_jump:\n)", flags=re.MULTILINE),
        lambda m: OVL24_MARKER + "\n" + region + m.group(1),
        1, "splice point")

    # Shared vertex-helper entry that overlay 24 jumps to (mid L_15C4).
    sub_exactly6c(
        re.compile(r"(    // jal         0x1780\n    r31 = 0x15D8;\n)"),
        lambda m: "L_15D0:  " + OVL24_MARKER + "\n" + m.group(1),
        1, "L_15D0 label")

    sub_exactly6c(
        re.compile(r"(L_1298:\n)"),
        lambda m: m.group(1) +
        "    if (r3 == 0x12A0) rs64_e9prov_l1298_12a0_res(RSP_MEM_BU(0X153, 0));  " +
        OVL24_MARKER + "\n",
        1, "L_1298 dest-0x12A0 resident")

    ovl24_addrs = sorted(int(lbl[2:], 16) for lbl in region_labels)
    existing_12a0 = re.compile(r"        case 0x12A0: goto L_12A0;\n")
    sub_exactly6c(
        existing_12a0,
        lambda m: ("        case 0x12A0:  " + OVL24_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x24) {"
                   " rs64_e9prov_ovl_route(0x24, 0x12A0); goto OVL24_12A0; }\n"
                   "            goto L_12A0;\n"),
        1, "case 0x12A0 overlay-24 routing")

    for addr in ovl24_addrs:
        if addr == 0x12A0:
            continue
        pat = re.compile(rf"        case 0x{addr:04X}: goto L_{addr:04X};\n")
        if pat.search(text):
            sub_exactly6c(
                pat,
                lambda m, a=addr: (
                    f"        case 0x{a:04X}:  " + OVL24_MARKER + "\n"
                    f"            if (RSP_MEM_BU(0X153, 0) == 0x24) {{"
                    f" rs64_e9prov_ovl_route(0x24, 0x{a:04X}); goto OVL24_{a:04X}; }}\n"
                    f"            goto L_{a:04X};\n"),
                1, f"case 0x{addr:04X} shared overlay-24 routing")

    ovl24_only = "".join(
        f"        case 0x{a:04X}: if (RSP_MEM_BU(0X153, 0) == 0x24) {{ "
        f"rs64_e9prov_ovl_route(0x24, 0x{a:04X}); goto OVL24_{a:04X}; }} "
        f"goto rs64_clip_stray;  {OVL24_MARKER}\n"
        for a in ovl24_addrs
        if a != 0x12A0 and not re.search(
            rf"        case 0x{a:04X}:", text))
    if ovl24_only:
        sub_exactly6c(
            re.compile(r"(        case 0x12A0:  /\* fixup: ovl24route \*/\n)"),
            lambda m: ovl24_only + m.group(1),
            1, "overlay-24 handshake/return cases")

    sub_exactly6c(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x4\) \{"
            r" rs64_e9prov_ovl_route\(0x4, 0x1DB0\); goto CLIP_1DB0; \}\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0xC\) \{"
            r" rs64_e9prov_ovl_route\(0xC, 0x1DB0\); goto OVL12_1DB0; \}\n"
            r"            goto L_1DB0;\n)"),
        lambda m: ("        case 0x1DB0:  " + CLIP_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x4) {"
                   " rs64_e9prov_ovl_route(0x4, 0x1DB0); goto CLIP_1DB0; }\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0xC) {"
                   " rs64_e9prov_ovl_route(0xC, 0x1DB0); goto OVL12_1DB0; }\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x28) {"
                   " rs64_e9prov_ovl_route(0x28, 0x1DB0); "
                   "r17 = RSP_ADD32(r17, 0X20); goto L_10D8; }  " +
                   OVL24_MARKER + "\n"
                   "            goto L_1DB0;\n"),
        1, "case 0x1DB0 overlay-28 routing")

# ---------------------------------------------------------------------------
# Fixup 6d: 0x1364 clip-stray predecessor (s744)
# ---------------------------------------------------------------------------
# s743: case 0x1364 routes only when DMEM 0x153==0x24; 4434 clip-strays
# arrive with 153==0x04. Static: clip image has no 0x1364; the only
# r31=0x1364 writer is OVL24_135C (jal L_17F0). L_17F0's hand path
# (r5=4; goto L_1268) stores 0x153=4 and enters CLIP_1DB0 with that $ra
# saved at 0x50($18); CLIP_1E48 jr's it back. This fixup names that
# writer live: count the jal, count CLIP_1E48 $ra, and log every
# do_indirect_jump to 0x1364 (line/r31/r30/resident/last ovl-route).
# Widening is fixup 6e, after this predecessor instrument lands.
OVL24_1364PRED_MARKER = "/* fixup: ovl24-1364pred */"
if is_main_ucode and OVL24_1364PRED_MARKER not in text:
    def sub_exactly6d(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6d ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    sub_exactly6d(
        re.compile(r'(extern "C" void rs64_e9prov_l1298_12a0_res\([^\n]*\n)'),
        lambda m: m.group(1) +
        'extern "C" void rs64_e9prov_ovl24_jal17f0(void);\n'
        'extern "C" void rs64_e9prov_clip_1e48_ra(uint32_t ra);\n'
        'extern "C" void rs64_e9prov_1364_jump(uint32_t line, uint32_t r31, '
        'uint32_t r30, uint32_t resident);  ' +
        OVL24_1364PRED_MARKER + "\n",
        1, "1364-pred declarations")

    sub_exactly6d(
        re.compile(r"(OVL24_135C:\n    // jal         0x17F0\n    r31 = 0x1364;\n)"),
        lambda m: m.group(1) +
        "    rs64_e9prov_ovl24_jal17f0();  " + OVL24_1364PRED_MARKER + "\n",
        1, "OVL24_135C jal L_17F0")

    sub_exactly6d(
        re.compile(
            r"(CLIP_1E48:\n    // lhu         \$ra, 0x50\(\$18\)\n"
            r"    r31 = RSP_MEM_HU_LOAD\(0X50, r18\);\n)"),
        lambda m: m.group(1) +
        "    rs64_e9prov_clip_1e48_ra(r31);  " + OVL24_1364PRED_MARKER + "\n",
        1, "CLIP_1E48 saved $ra")

    sub_exactly6d(
        re.compile(
            r"(    if \(\(\(jump_target \| 0x1000\) & 0X1FFF\) == 0x1DB0\) "
            r"rs64_e9prov_l1db0_predecessor\([^\n]*\n)"),
        lambda m: m.group(1) +
        "    if (((jump_target | 0x1000) & 0X1FFF) == 0x1364) "
        "rs64_e9prov_1364_jump((uint32_t)debug_line, r31, r30, "
        "RSP_MEM_BU(0X153, 0));  " + OVL24_1364PRED_MARKER + "\n",
        1, "do_indirect_jump 0x1364")

# ---------------------------------------------------------------------------
# Fixup 6e: route 0x1364 for clip-resident return (s745)
# ---------------------------------------------------------------------------
# s744: CLIP_1E48 jr of OVL24_135C jal L_17F0 returns to 0x1364 with
# DMEM 0x153==0x04 (L_17F0 handed to clip; dest 0x1DB0). IMEM 0x1364 is
# still the overlay-24 emit image. Fixup 6c's ovl24-only case required
# 0x153==0x24 and turned that legitimate return into [clip-stray].
# Widen only 0x1364 — not a bare always-OVL24. After overlay 28 restores
# main L_12A0, IMEM 0x1364 is main bytes; keep the 0x24|0x04 gate.
# ORIGIN: CLIP_1E48 jr of a ROM clip dispatch; route, not a guard.
OVL24_1364CLIP_MARKER = "/* fixup: ovl24-1364clip */"
if is_main_ucode and OVL24_1364CLIP_MARKER not in text:
    def sub_exactly6e(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6e ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    sub_exactly6e(
        re.compile(
            r"        case 0x1364: if \(RSP_MEM_BU\(0X153, 0\) == 0x24\) \{ "
            r"rs64_e9prov_ovl_route\(0x24, 0x1364\); goto OVL24_1364; \} "
            r"goto rs64_clip_stray;  /\* fixup: ovl24route \*/\n"),
        lambda m: (
            "        case 0x1364: if (RSP_MEM_BU(0X153, 0) == 0x24 || "
            "RSP_MEM_BU(0X153, 0) == 0x04) { "
            "rs64_e9prov_ovl_route(0x24, 0x1364); goto OVL24_1364; } "
            "goto rs64_clip_stray;  " + OVL24_1364CLIP_MARKER + "\n"),
        1, "case 0x1364 clip-resident return")

# ---------------------------------------------------------------------------
# Fixup 6f: remaining ovl24-only clip-resident returns (s746)
# ---------------------------------------------------------------------------
# s745: routing 0x1364 for 0x24||0x04 killed that stray (4454->0) and
# kept boot dl06=2/2/0, but the same class leaked at 0x1320/0x1330/
# 0x1344 with 153=0x04 (n=3681/1165/485, all line=400). Writer: after
# CLIP_1E48 returns to the now-routed OVL24_1364, that label loads $ra
# from 0xB30 (saved by OVL24_1358 before jal L_17F0) and goto L_112C;
# L_112C jr $30 of that $ra while clip is still resident. Clip dest is
# 0x1DB0, so IMEM 0x12A0..0x1384 is still ovl24. Widen every remaining
# ovl24-only clip-stray case to 0x24||0x04. Shared cases that fall
# through to main L_* stay 0x24-only. Not a bare always-OVL24.
# ORIGIN: L_112C jr of the OVL24_1358-saved $ra after the 6e 0x1364
# clip-resident return. Legitimate ROM emit continuation; route.
OVL24_04RET_MARKER = "/* fixup: ovl24-04ret */"
if is_main_ucode and OVL24_04RET_MARKER not in text:
    def sub_exactly6f(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6f ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    sub_exactly6f(
        re.compile(
            r"        case 0x([0-9A-F]{4}): if \(RSP_MEM_BU\(0X153, 0\) == 0x24\) \{ "
            r"rs64_e9prov_ovl_route\(0x24, 0x\1\); goto OVL24_\1; \} "
            r"goto rs64_clip_stray;  /\* fixup: ovl24route \*/\n"),
        lambda m: (
            f"        case 0x{m.group(1)}: if (RSP_MEM_BU(0X153, 0) == 0x24 || "
            f"RSP_MEM_BU(0X153, 0) == 0x04) {{ "
            f"rs64_e9prov_ovl_route(0x24, 0x{m.group(1)}); goto OVL24_{m.group(1)}; }} "
            f"goto rs64_clip_stray;  " + OVL24_04RET_MARKER + "\n"),
        10, "remaining ovl24-only clip-resident returns")

# ---------------------------------------------------------------------------
# Fixup 6g: splice resident overlay 14 (id 0x14) at dest 0x1DB0 (s748)
# ---------------------------------------------------------------------------
# s747: [clip-stray] 0x1DF4/00 is leftover $ra after skipped ovl14 DMA
# (L_1268 r5=0x14, dest 0x1DB0) falls into main L_1DB0, which writes
# 153=0 and j L_11B0. Overlay 14 is a vector loop (ROM 0x26AB8, 0x220 B),
# not a 0x1DF4 owner. factor5_rsp_ovl14.toml translates a composite
# whose window holds that image; this fixup extracts L_1DB0..,
# renames labels OVL14_*, splices the block, and routes DMEM 0x153 ==
# 0x14 at dest 0x1DB0 plus the three jr-$ra jal-returns. Overlay 18
# is the successor residual — do not splice it here.
# ORIGIN: dest 0x1DB0 / 153==0x14 is the skipped ovl14 image.
# The 0x1DF4 stray is leftover $ra after that skip. Route, not a
# 0x1DF4 widen.
OVL14_MARKER = "/* fixup: ovl14splice */"
if is_main_ucode and OVL14_MARKER not in text:
    ovl14_path = path.parent / "factor5_ucode_ovl14_recompiled.c"
    if not ovl14_path.exists():
        print("fixup_factor5_ucode: FIXUP 6g INPUT MISSING: "
              f"{ovl14_path} not found. Run make_clip_composite.py 14 and "
              "RSPRecomp on factor5_rsp_ovl14.toml before fixing up the "
              "main ucode, or the overlay-14 splice is lost.", file=sys.stderr)
        sys.exit(1)
    ovl14_text = ovl14_path.read_text(encoding="utf-8")

    def sub_exactly6g(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6g ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the overlay-14 splice.", file=sys.stderr)
            sys.exit(1)
        text = new_text

    m_start = re.search(r"^L_1DB0:\n", ovl14_text, flags=re.MULTILINE)
    m_end = re.search(r"^do_indirect_jump:\n", ovl14_text, flags=re.MULTILINE)
    if not m_start or not m_end or m_end.start() <= m_start.start():
        print("fixup_factor5_ucode: FIXUP 6g EXTRACTION FAILED: could not "
              "bound L_1DB0..do_indirect_jump in the ovl14 file.", file=sys.stderr)
        sys.exit(1)
    region = ovl14_text[m_start.start():m_end.start()]

    region_labels = set(re.findall(r"^(L_[0-9A-F]{4}):", region, flags=re.MULTILINE))
    expected_resident = {"L_1268"}
    referenced = set(re.findall(r"goto (L_[0-9A-F]{4});", region))
    external = referenced - region_labels
    if external != expected_resident:
        print(f"fixup_factor5_ucode: FIXUP 6g SANITY FAILED: region's external "
              f"references {sorted(external)} != expected resident helpers "
              f"{sorted(expected_resident)}. The overlay-14 image or its "
              f"translation changed — re-derive before splicing.", file=sys.stderr)
        sys.exit(1)
    for need in ("L_1DB0", "L_1E28", "L_1E94", "L_1EEC"):
        if need not in region_labels:
            print("fixup_factor5_ucode: FIXUP 6g SANITY FAILED: missing "
                  f"{need} in ovl14 region {sorted(region_labels)}.",
                  file=sys.stderr)
            sys.exit(1)
    for lbl in region_labels:
        region = re.sub(r"\b" + lbl + r"\b", "OVL14_" + lbl[2:], region)

    sub_exactly6g(
        re.compile(r"(^do_indirect_jump:\n)", flags=re.MULTILINE),
        lambda m: OVL14_MARKER + "\n" + region + m.group(1),
        1, "splice point")

    sub_exactly6g(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x4\) \{"
            r" rs64_e9prov_ovl_route\(0x4, 0x1DB0\); goto CLIP_1DB0; \}\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0xC\) \{"
            r" rs64_e9prov_ovl_route\(0xC, 0x1DB0\); goto OVL12_1DB0; \}\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x28\) \{"
            r" rs64_e9prov_ovl_route\(0x28, 0x1DB0\); "
            r"r17 = RSP_ADD32\(r17, 0X20\); goto L_10D8; \}  "
            r"/\* fixup: ovl24route \*/\n"
            r"            goto L_1DB0;\n)"),
        lambda m: ("        case 0x1DB0:  " + CLIP_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x4) {"
                   " rs64_e9prov_ovl_route(0x4, 0x1DB0); goto CLIP_1DB0; }\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0xC) {"
                   " rs64_e9prov_ovl_route(0xC, 0x1DB0); goto OVL12_1DB0; }\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x14) {"
                   " rs64_e9prov_ovl_route(0x14, 0x1DB0); goto OVL14_1DB0; }  " +
                   OVL14_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x28) {"
                   " rs64_e9prov_ovl_route(0x28, 0x1DB0); "
                   "r17 = RSP_ADD32(r17, 0X20); goto L_10D8; }  "
                   "/* fixup: ovl24route */\n"
                   "            goto L_1DB0;\n"),
        1, "case 0x1DB0 overlay-14 routing")

    ovl14_only = "".join(
        f"        case 0x{a:04X}: if (RSP_MEM_BU(0X153, 0) == 0x14) {{ "
        f"rs64_e9prov_ovl_route(0x14, 0x{a:04X}); goto OVL14_{a:04X}; }} "
        f"goto rs64_clip_stray;  {OVL14_MARKER}\n"
        for a in (0x1E28, 0x1E94, 0x1EEC))
    sub_exactly6g(
        re.compile(r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: ovl14_only + m.group(1),
        1, "overlay-14 jal-return cases")

# ---------------------------------------------------------------------------
# Fixup 6h: splice resident overlay 18 (id 0x18) at dest 0x1DB0 (s749)
# ---------------------------------------------------------------------------
# s748: dest 0x1DB0 / 153==0x18 is the skipped ovl14 successor. Overlay 18
# is a vector loop (ROM 0x26CD8, 0x220 B) that exits j L_1268; ori $5, 0x10.
# factor5_rsp_ovl18.toml translates a composite whose window holds that
# image; this fixup extracts L_1DB0.., renames labels OVL18_*, splices
# the block, and routes DMEM 0x153 == 0x18 at dest 0x1DB0 plus the two
# jr-$ra jal-returns (0x1EEC already ovl14-only — widen, do not
# overwrite; 0x1F40 is ovl18-only). Overlay 0x10 is the successor
# residual — do not splice it here.
# ORIGIN: dest 0x1DB0 / 153==0x18 is the skipped ovl18 image.
# Leftover-$ra L_11B0 strays are after that skip falls into L_1DB0.
# Route, not a 0x1DF4/0x1E28 widen.
OVL18_MARKER = "/* fixup: ovl18splice */"
if is_main_ucode and OVL18_MARKER not in text:
    ovl18_path = path.parent / "factor5_ucode_ovl18_recompiled.c"
    if not ovl18_path.exists():
        print("fixup_factor5_ucode: FIXUP 6h INPUT MISSING: "
              f"{ovl18_path} not found. Run make_clip_composite.py 18 and "
              "RSPRecomp on factor5_rsp_ovl18.toml before fixing up the "
              "main ucode, or the overlay-18 splice is lost.", file=sys.stderr)
        sys.exit(1)
    ovl18_text = ovl18_path.read_text(encoding="utf-8")

    def sub_exactly6h(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6h ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the overlay-18 splice.", file=sys.stderr)
            sys.exit(1)
        text = new_text

    m_start = re.search(r"^L_1DB0:\n", ovl18_text, flags=re.MULTILINE)
    m_end = re.search(r"^do_indirect_jump:\n", ovl18_text, flags=re.MULTILINE)
    if not m_start or not m_end or m_end.start() <= m_start.start():
        print("fixup_factor5_ucode: FIXUP 6h EXTRACTION FAILED: could not "
              "bound L_1DB0..do_indirect_jump in the ovl18 file.", file=sys.stderr)
        sys.exit(1)
    region = ovl18_text[m_start.start():m_end.start()]

    region_labels = set(re.findall(r"^(L_[0-9A-F]{4}):", region, flags=re.MULTILINE))
    expected_resident = {"L_1268"}
    referenced = set(re.findall(r"goto (L_[0-9A-F]{4});", region))
    external = referenced - region_labels
    if external != expected_resident:
        print(f"fixup_factor5_ucode: FIXUP 6h SANITY FAILED: region's external "
              f"references {sorted(external)} != expected resident helpers "
              f"{sorted(expected_resident)}. The overlay-18 image or its "
              f"translation changed — re-derive before splicing.", file=sys.stderr)
        sys.exit(1)
    for need in ("L_1DB0", "L_1EEC", "L_1F40"):
        if need not in region_labels:
            print("fixup_factor5_ucode: FIXUP 6h SANITY FAILED: missing "
                  f"{need} in ovl18 region {sorted(region_labels)}.",
                  file=sys.stderr)
            sys.exit(1)
    for lbl in region_labels:
        region = re.sub(r"\b" + lbl + r"\b", "OVL18_" + lbl[2:], region)

    sub_exactly6h(
        re.compile(r"(^do_indirect_jump:\n)", flags=re.MULTILINE),
        lambda m: OVL18_MARKER + "\n" + region + m.group(1),
        1, "splice point")

    sub_exactly6h(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x4\) \{"
            r" rs64_e9prov_ovl_route\(0x4, 0x1DB0\); goto CLIP_1DB0; \}\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0xC\) \{"
            r" rs64_e9prov_ovl_route\(0xC, 0x1DB0\); goto OVL12_1DB0; \}\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x14\) \{"
            r" rs64_e9prov_ovl_route\(0x14, 0x1DB0\); goto OVL14_1DB0; \}  "
            r"/\* fixup: ovl14splice \*/\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x28\) \{"
            r" rs64_e9prov_ovl_route\(0x28, 0x1DB0\); "
            r"r17 = RSP_ADD32\(r17, 0X20\); goto L_10D8; \}  "
            r"/\* fixup: ovl24route \*/\n"
            r"            goto L_1DB0;\n)"),
        lambda m: ("        case 0x1DB0:  " + CLIP_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x4) {"
                   " rs64_e9prov_ovl_route(0x4, 0x1DB0); goto CLIP_1DB0; }\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0xC) {"
                   " rs64_e9prov_ovl_route(0xC, 0x1DB0); goto OVL12_1DB0; }\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x14) {"
                   " rs64_e9prov_ovl_route(0x14, 0x1DB0); goto OVL14_1DB0; }  " +
                   OVL14_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x18) {"
                   " rs64_e9prov_ovl_route(0x18, 0x1DB0); goto OVL18_1DB0; }  " +
                   OVL18_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x28) {"
                   " rs64_e9prov_ovl_route(0x28, 0x1DB0); "
                   "r17 = RSP_ADD32(r17, 0X20); goto L_10D8; }  "
                   "/* fixup: ovl24route */\n"
                   "            goto L_1DB0;\n"),
        1, "case 0x1DB0 overlay-18 routing")

    # 0x1EEC is already an ovl14-only case — widen to 0x14||0x18.
    sub_exactly6h(
        re.compile(
            r"        case 0x1EEC: if \(RSP_MEM_BU\(0X153, 0\) == 0x14\) \{ "
            r"rs64_e9prov_ovl_route\(0x14, 0x1EEC\); goto OVL14_1EEC; \} "
            r"goto rs64_clip_stray;  /\* fixup: ovl14splice \*/\n"),
        lambda m: (
            "        case 0x1EEC: if (RSP_MEM_BU(0X153, 0) == 0x14) { "
            "rs64_e9prov_ovl_route(0x14, 0x1EEC); goto OVL14_1EEC; } "
            "if (RSP_MEM_BU(0X153, 0) == 0x18) { "
            "rs64_e9prov_ovl_route(0x18, 0x1EEC); goto OVL18_1EEC; } "
            "goto rs64_clip_stray;  " + OVL18_MARKER + "\n"),
        1, "widen 0x1EEC ovl14||ovl18")

    # 0x1F40 is ovl18-only (jal L_1F64 return).
    sub_exactly6h(
        re.compile(r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: (
            "        case 0x1F40: if (RSP_MEM_BU(0X153, 0) == 0x18) { "
            "rs64_e9prov_ovl_route(0x18, 0x1F40); goto OVL18_1F40; } "
            "goto rs64_clip_stray;  " + OVL18_MARKER + "\n" + m.group(1)),
        1, "overlay-18 jal-return 0x1F40")

# ---------------------------------------------------------------------------
# Fixup 6i: splice resident overlay 10 (id 0x10) at dest 0x1DB0 (s750)
# ---------------------------------------------------------------------------
# s749: dest 0x1DB0 / 153==0x10 is the skipped ovl18 successor. Overlay 10
# is a vector loop (ROM 0x268A0, 0x214 B) that exits j L_1268; ori $5, 0x1C
# and also j L_15D0; ori $30, 0x1F40. No jals. factor5_rsp_ovl10.toml
# translates a composite whose window holds that image (extra target
# 0x1F40 required so L_1F40 exists); this fixup extracts L_1DB0..,
# renames labels OVL10_*, splices the block, and routes DMEM 0x153 ==
# 0x10 at dest 0x1DB0. Fixup 6j routes the L_15D0 handshake return at
# 0x1F40. Overlay 0x1C is the successor residual — do not splice it
# here.
# ORIGIN: dest 0x1DB0 / 153==0x10 is the skipped ovl10 image.
# Leftover-$ra L_11B0 strays are after that skip falls into L_1DB0.
# Route dest 0x1DB0 here; 6j owns the 0x1F40 handshake.
OVL10_MARKER = "/* fixup: ovl10splice */"
if is_main_ucode and OVL10_MARKER not in text:
    ovl10_path = path.parent / "factor5_ucode_ovl10_recompiled.c"
    if not ovl10_path.exists():
        print("fixup_factor5_ucode: FIXUP 6i INPUT MISSING: "
              f"{ovl10_path} not found. Run make_clip_composite.py 16 and "
              "RSPRecomp on factor5_rsp_ovl10.toml before fixing up the "
              "main ucode, or the overlay-10 splice is lost.", file=sys.stderr)
        sys.exit(1)
    ovl10_text = ovl10_path.read_text(encoding="utf-8")

    def sub_exactly6i(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6i ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the overlay-10 splice.", file=sys.stderr)
            sys.exit(1)
        text = new_text

    m_start = re.search(r"^L_1DB0:\n", ovl10_text, flags=re.MULTILINE)
    m_end = re.search(r"^do_indirect_jump:\n", ovl10_text, flags=re.MULTILINE)
    if not m_start or not m_end or m_end.start() <= m_start.start():
        print("fixup_factor5_ucode: FIXUP 6i EXTRACTION FAILED: could not "
              "bound L_1DB0..do_indirect_jump in the ovl10 file.", file=sys.stderr)
        sys.exit(1)
    region = ovl10_text[m_start.start():m_end.start()]

    region_labels = set(re.findall(r"^(L_[0-9A-F]{4}):", region, flags=re.MULTILINE))
    expected_resident = {"L_1268", "L_15D0"}
    referenced = set(re.findall(r"goto (L_[0-9A-F]{4});", region))
    external = referenced - region_labels
    if external != expected_resident:
        print(f"fixup_factor5_ucode: FIXUP 6i SANITY FAILED: region's external "
              f"references {sorted(external)} != expected resident helpers "
              f"{sorted(expected_resident)}. The overlay-10 image or its "
              f"translation changed — re-derive before splicing.", file=sys.stderr)
        sys.exit(1)
    for need in ("L_1DB0", "L_1F40", "L_1FBC"):
        if need not in region_labels:
            print("fixup_factor5_ucode: FIXUP 6i SANITY FAILED: missing "
                  f"{need} in ovl10 region {sorted(region_labels)}.",
                  file=sys.stderr)
            sys.exit(1)
    for lbl in region_labels:
        region = re.sub(r"\b" + lbl + r"\b", "OVL10_" + lbl[2:], region)

    sub_exactly6i(
        re.compile(r"(^do_indirect_jump:\n)", flags=re.MULTILINE),
        lambda m: OVL10_MARKER + "\n" + region + m.group(1),
        1, "splice point")

    sub_exactly6i(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x4\) \{"
            r" rs64_e9prov_ovl_route\(0x4, 0x1DB0\); goto CLIP_1DB0; \}\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0xC\) \{"
            r" rs64_e9prov_ovl_route\(0xC, 0x1DB0\); goto OVL12_1DB0; \}\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x14\) \{"
            r" rs64_e9prov_ovl_route\(0x14, 0x1DB0\); goto OVL14_1DB0; \}  "
            r"/\* fixup: ovl14splice \*/\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x18\) \{"
            r" rs64_e9prov_ovl_route\(0x18, 0x1DB0\); goto OVL18_1DB0; \}  "
            r"/\* fixup: ovl18splice \*/\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x28\) \{"
            r" rs64_e9prov_ovl_route\(0x28, 0x1DB0\); "
            r"r17 = RSP_ADD32\(r17, 0X20\); goto L_10D8; \}  "
            r"/\* fixup: ovl24route \*/\n"
            r"            goto L_1DB0;\n)"),
        lambda m: ("        case 0x1DB0:  " + CLIP_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x4) {"
                   " rs64_e9prov_ovl_route(0x4, 0x1DB0); goto CLIP_1DB0; }\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0xC) {"
                   " rs64_e9prov_ovl_route(0xC, 0x1DB0); goto OVL12_1DB0; }\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x14) {"
                   " rs64_e9prov_ovl_route(0x14, 0x1DB0); goto OVL14_1DB0; }  " +
                   OVL14_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x18) {"
                   " rs64_e9prov_ovl_route(0x18, 0x1DB0); goto OVL18_1DB0; }  " +
                   OVL18_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x10) {"
                   " rs64_e9prov_ovl_route(0x10, 0x1DB0); goto OVL10_1DB0; }  " +
                   OVL10_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x28) {"
                   " rs64_e9prov_ovl_route(0x28, 0x1DB0); "
                   "r17 = RSP_ADD32(r17, 0X20); goto L_10D8; }  "
                   "/* fixup: ovl24route */\n"
                   "            goto L_1DB0;\n"),
        1, "case 0x1DB0 overlay-10 routing")

# ---------------------------------------------------------------------------
# Fixup 6j: route ovl10 L_15D0 handshake return at 0x1F40 (s751)
# ---------------------------------------------------------------------------
# s750: dest-0x1DB0 / 153==0x10 is LIVE; leftover /00 L_11B0 strays
# went to 0. New stray is [clip-stray] tgt=0x1F40 153=0x10 line=1421
# (L_1778 jr $30). ovl10 at IMEM 0x1F38 is j L_15D0; ori $30, 0x1F40;
# 0x1F40 is lhu $10, 0x56($18). 6h already owns 153==0x18 → OVL18_1F40
# (jal L_1F64 return). Widen, do not overwrite. Do not splice overlay
# 0x1C here. Independent of 6i's marker so an already-spliced file
# still gets the label + route.
# ORIGIN: ovl10 ori $30, 0x1F40; j L_15D0 at IMEM 0x1F38. L_1778
# jr $30 is the legitimate return into ovl10. Route to OVL10_1F40.
OVL10_1F40_MARKER = "/* fixup: ovl10_1f40 */"
if is_main_ucode and OVL10_1F40_MARKER not in text:
    def sub_exactly6j(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6j ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the ovl10 0x1F40 handshake.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    if "OVL10_1F40:" not in text:
        sub_exactly6j(
            re.compile(
                r"(OVL10_1F38:\n"
                r"    // j           L_15D0\n"
                r"    // ori         \$30, \$zero, 0x1F40\n"
                r"    r30 = 0 \| 0X1F40;\n"
                r"    goto L_15D0;\n"
                r"    // ori         \$30, \$zero, 0x1F40\n"
                r"    r30 = 0 \| 0X1F40;\n)"
                r"(    // lhu         \$10, 0x56\(\$18\)\n)"),
            lambda m: m.group(1) + "OVL10_1F40:\n" + m.group(2),
            1, "insert OVL10_1F40 label")

    sub_exactly6j(
        re.compile(
            r"        case 0x1F40: if \(RSP_MEM_BU\(0X153, 0\) == 0x18\) \{ "
            r"rs64_e9prov_ovl_route\(0x18, 0x1F40\); goto OVL18_1F40; \} "
            r"goto rs64_clip_stray;  /\* fixup: ovl18splice \*/\n"),
        lambda m: (
            "        case 0x1F40: if (RSP_MEM_BU(0X153, 0) == 0x18) { "
            "rs64_e9prov_ovl_route(0x18, 0x1F40); goto OVL18_1F40; } "
            "if (RSP_MEM_BU(0X153, 0) == 0x10) { "
            "rs64_e9prov_ovl_route(0x10, 0x1F40); goto OVL10_1F40; } "
            "goto rs64_clip_stray;  " + OVL10_1F40_MARKER + "\n"),
        1, "widen 0x1F40 ovl18||ovl10")

# ---------------------------------------------------------------------------
# Fixup 6k: splice resident overlay 0x1C at dest 0x1DB0 (s752)
# ---------------------------------------------------------------------------
# s751: dest 0x1DB0 / 153==0x1C is the skipped ovl10 successor. Overlay
# 0x1C is a vector loop (ROM 0x26EF8, 0x20C B) that exits j L_1268;
# ori $5, 0x20 at IMEM 0x1ECC and has jals returning to 0x1ED4 / 0x1F0C.
# factor5_rsp_ovl1c.toml translates a composite whose window holds that
# image; this fixup extracts L_1DB0.., renames labels OVL1C_*, splices
# the block, and routes DMEM 0x153 == 0x1C at dest 0x1DB0 only.
# Do not add jal-return cases until dest-0x1DB0 is LIVE. Do not name
# this overlay ovl28 — that id is the r17+=32 restore route. Overlay
# 0x20 dest is 0x12A0 (table 0x2157); do not splice it here.
# ORIGIN: dest 0x1DB0 / 153==0x1C is the skipped ovl1c image.
# The 0x1F40/00 stray is leftover $30 after that skip falls into
# main L_1DB0. Route, not a 0x1F40 widen to 153==0.
OVL1C_MARKER = "/* fixup: ovl1csplice */"
if is_main_ucode and OVL1C_MARKER not in text:
    ovl1c_path = path.parent / "factor5_ucode_ovl1c_recompiled.c"
    if not ovl1c_path.exists():
        print("fixup_factor5_ucode: FIXUP 6k INPUT MISSING: "
              f"{ovl1c_path} not found. Run make_clip_composite.py 0x1C and "
              "RSPRecomp on factor5_rsp_ovl1c.toml before fixing up the "
              "main ucode, or the overlay-0x1C splice is lost.", file=sys.stderr)
        sys.exit(1)
    ovl1c_text = ovl1c_path.read_text(encoding="utf-8")

    def sub_exactly6k(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6k ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the overlay-0x1C splice.", file=sys.stderr)
            sys.exit(1)
        text = new_text

    m_start = re.search(r"^L_1DB0:\n", ovl1c_text, flags=re.MULTILINE)
    m_end = re.search(r"^do_indirect_jump:\n", ovl1c_text, flags=re.MULTILINE)
    if not m_start or not m_end or m_end.start() <= m_start.start():
        print("fixup_factor5_ucode: FIXUP 6k EXTRACTION FAILED: could not "
              "bound L_1DB0..do_indirect_jump in the ovl1c file.", file=sys.stderr)
        sys.exit(1)
    region = ovl1c_text[m_start.start():m_end.start()]

    region_labels = set(re.findall(r"^(L_[0-9A-F]{4}):", region, flags=re.MULTILINE))
    expected_resident = {"L_1268"}
    referenced = set(re.findall(r"goto (L_[0-9A-F]{4});", region))
    external = referenced - region_labels
    if external != expected_resident:
        print(f"fixup_factor5_ucode: FIXUP 6k SANITY FAILED: region's external "
              f"references {sorted(external)} != expected resident helpers "
              f"{sorted(expected_resident)}. The overlay-0x1C image or its "
              f"translation changed — re-derive before splicing.", file=sys.stderr)
        sys.exit(1)
    for need in ("L_1DB0", "L_1ECC", "L_1ED4", "L_1F0C"):
        if need not in region_labels:
            print("fixup_factor5_ucode: FIXUP 6k SANITY FAILED: missing "
                  f"{need} in ovl1c region {sorted(region_labels)}.",
                  file=sys.stderr)
            sys.exit(1)
    for lbl in region_labels:
        region = re.sub(r"\b" + lbl + r"\b", "OVL1C_" + lbl[2:], region)

    sub_exactly6k(
        re.compile(r"(^do_indirect_jump:\n)", flags=re.MULTILINE),
        lambda m: OVL1C_MARKER + "\n" + region + m.group(1),
        1, "splice point")

    sub_exactly6k(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x4\) \{"
            r" rs64_e9prov_ovl_route\(0x4, 0x1DB0\); goto CLIP_1DB0; \}\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0xC\) \{"
            r" rs64_e9prov_ovl_route\(0xC, 0x1DB0\); goto OVL12_1DB0; \}\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x14\) \{"
            r" rs64_e9prov_ovl_route\(0x14, 0x1DB0\); goto OVL14_1DB0; \}  "
            r"/\* fixup: ovl14splice \*/\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x18\) \{"
            r" rs64_e9prov_ovl_route\(0x18, 0x1DB0\); goto OVL18_1DB0; \}  "
            r"/\* fixup: ovl18splice \*/\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x10\) \{"
            r" rs64_e9prov_ovl_route\(0x10, 0x1DB0\); goto OVL10_1DB0; \}  "
            r"/\* fixup: ovl10splice \*/\n"
            r"            if \(RSP_MEM_BU\(0X153, 0\) == 0x28\) \{"
            r" rs64_e9prov_ovl_route\(0x28, 0x1DB0\); "
            r"r17 = RSP_ADD32\(r17, 0X20\); goto L_10D8; \}  "
            r"/\* fixup: ovl24route \*/\n"
            r"            goto L_1DB0;\n)"),
        lambda m: ("        case 0x1DB0:  " + CLIP_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x4) {"
                   " rs64_e9prov_ovl_route(0x4, 0x1DB0); goto CLIP_1DB0; }\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0xC) {"
                   " rs64_e9prov_ovl_route(0xC, 0x1DB0); goto OVL12_1DB0; }\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x14) {"
                   " rs64_e9prov_ovl_route(0x14, 0x1DB0); goto OVL14_1DB0; }  " +
                   OVL14_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x18) {"
                   " rs64_e9prov_ovl_route(0x18, 0x1DB0); goto OVL18_1DB0; }  " +
                   OVL18_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x10) {"
                   " rs64_e9prov_ovl_route(0x10, 0x1DB0); goto OVL10_1DB0; }  " +
                   OVL10_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x1C) {"
                   " rs64_e9prov_ovl_route(0x1C, 0x1DB0); goto OVL1C_1DB0; }  " +
                   OVL1C_MARKER + "\n"
                   "            if (RSP_MEM_BU(0X153, 0) == 0x28) {"
                   " rs64_e9prov_ovl_route(0x28, 0x1DB0); "
                   "r17 = RSP_ADD32(r17, 0X20); goto L_10D8; }  "
                   "/* fixup: ovl24route */\n"
                   "            goto L_1DB0;\n"),
        1, "case 0x1DB0 overlay-0x1C routing")

# ---------------------------------------------------------------------------
# Fixup 6l: route ovl1c jal-return at 0x1E18 (s753)
# ---------------------------------------------------------------------------
# s752: dest-0x1DB0 / 153==0x1C is LIVE; stray 0x1F40/00 went to 0.
# New residual is Unhandled jump target 0x1E18 n=5879 from
# OVL1C_1F9C jr $ra. ovl1c jal at IMEM 0x1E10 sets r31=0x1E18
# and goto OVL1C_1F0C; the callee returns via OVL1C_1F9C jr $ra.
# Label OVL1C_1E18 already exists (6k sequential label after the
# delay slot). There is no case 0x1E18. Independent of 6k's
# marker so an already-spliced file still gets the route. Do not
# add the other jal-return cases (0x1E2C/0x1E6C/...) until 0x1E18
# is LIVE. Do not splice overlay 0x20 (dest 0x12A0).
# ORIGIN: ovl1c jal at IMEM 0x1E10 → callee 0x1F0C, return 0x1E18.
# OVL1C_1F9C jr $ra is the legitimate return into OVL1C_1E18.
# Route, not a default-allow of 0x1E18 for every resident.
OVL1C_1E18_MARKER = "/* fixup: ovl1c_1e18 */"
if is_main_ucode and OVL1C_1E18_MARKER not in text:
    def sub_exactly6l(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6l ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the ovl1c 0x1E18 jal-return.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    if "OVL1C_1E18:" not in text:
        print("fixup_factor5_ucode: FIXUP 6l PRECONDITION FAILED: "
              "OVL1C_1E18: missing. Run fixup 6k (make_clip_composite.py "
              "0x1C + RSPRecomp on factor5_rsp_ovl1c.toml) first.",
              file=sys.stderr)
        sys.exit(1)

    sub_exactly6l(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: (
            "        case 0x1E18: if (RSP_MEM_BU(0X153, 0) == 0x1C) { "
            "rs64_e9prov_ovl_route(0x1C, 0x1E18); goto OVL1C_1E18; } "
            "goto rs64_clip_stray;  " + OVL1C_1E18_MARKER + "\n" + m.group(1)),
        1, "case 0x1E18 overlay-0x1C jal-return")

# ---------------------------------------------------------------------------
# Fixup 6m: route ovl1c jal-return at 0x1E2C (s754)
# ---------------------------------------------------------------------------
# s753: dest-0x1E18 / 153==0x1C is LIVE; UJ 0x1E18 went 5879→0.
# New residual is Unhandled jump target 0x1E2C n=3213 from
# OVL1C_1F9C jr $ra. After the 0x1E18 return, OVL1C_1E18 jals
# callee 0x1F0C with r31=0x1E2C. Label OVL1C_1E2C already
# exists (6k sequential label after the delay slot). There is
# no case 0x1E2C. Independent of 6l's marker so an already-
# routed 0x1E18 file still gets this case. Do not add the
# later jal-return cases (0x1E6C/0x1E7C/0x1E8C/0x1EA8/
# 0x1EBC/0x1ECC/0x1F04) until 0x1E2C is LIVE. Do not splice
# overlay 0x20 (dest 0x12A0).
# ORIGIN: ovl1c jal at OVL1C_1E18 → callee 0x1F0C, return
# 0x1E2C. OVL1C_1F9C jr $ra is the legitimate return into
# OVL1C_1E2C. Route, not a default-allow of 0x1E2C for every
# resident.
OVL1C_1E2C_MARKER = "/* fixup: ovl1c_1e2c */"
if is_main_ucode and OVL1C_1E2C_MARKER not in text:
    def sub_exactly6m(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6m ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the ovl1c 0x1E2C jal-return.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    if "OVL1C_1E2C:" not in text:
        print("fixup_factor5_ucode: FIXUP 6m PRECONDITION FAILED: "
              "OVL1C_1E2C: missing. Run fixup 6k (make_clip_composite.py "
              "0x1C + RSPRecomp on factor5_rsp_ovl1c.toml) first.",
              file=sys.stderr)
        sys.exit(1)

    sub_exactly6m(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: (
            "        case 0x1E2C: if (RSP_MEM_BU(0X153, 0) == 0x1C) { "
            "rs64_e9prov_ovl_route(0x1C, 0x1E2C); goto OVL1C_1E2C; } "
            "goto rs64_clip_stray;  " + OVL1C_1E2C_MARKER + "\n" + m.group(1)),
        1, "case 0x1E2C overlay-0x1C jal-return")

# ---------------------------------------------------------------------------
# Fixup 6n: route ovl1c 1ED4 trampoline return at 0x1F04 (s755)
# ---------------------------------------------------------------------------
# s754: dest-0x1E2C / 153==0x1C is LIVE; UJ 0x1E2C went 3213→0.
# New residual is Unhandled jump target 0x1F04 n=3185 from
# OVL1C_1F9C jr $ra. OVL1C_1ED4 saves $ra into $30 then jals
# callee 0x1F0C with r31=0x1F04. Label OVL1C_1F04 already
# exists (6k sequential label after the delay slot). There is
# no case 0x1F04. Independent of 6m's marker so an already-
# routed 0x1E2C file still gets this case. Do not add the
# later $30-return cases (0x1E6C/0x1E7C/0x1E8C/0x1EA8/
# 0x1EBC/0x1ECC) until 0x1F04 is LIVE. Do not splice overlay
# 0x20 (dest 0x12A0).
# ORIGIN: ovl1c OVL1C_1ED4 saves $ra to $30, jals 0x1F0C
# with return 0x1F04. OVL1C_1F9C jr $ra is the legitimate
# return into OVL1C_1F04, which then jr $30 to the original
# caller. Route, not a default-allow of 0x1F04 for every
# resident.
OVL1C_1F04_MARKER = "/* fixup: ovl1c_1f04 */"
OVL1C_1F04_CASE_ONLY = (
    "        case 0x1F04: if (RSP_MEM_BU(0X153, 0) == 0x1C) { "
    "rs64_e9prov_ovl_route(0x1C, 0x1F04); goto OVL1C_1F04; } "
    "goto rs64_clip_stray;  " + OVL1C_1F04_MARKER + "\n")
if is_main_ucode:
    # 6q widens this case and used to drop OVL1C_1F04_MARKER, so a
    # later re-run of this file re-inserted a duplicate 0x1F04 case.
    # Treat any existing 0x1F04 route as already-applied, and strip
    # a leftover 6n-only duplicate if the widened form is also present.
    if "case 0x1F04:" in text:
        if text.count("case 0x1F04:") > 1:
            text, n_dup = re.subn(re.escape(OVL1C_1F04_CASE_ONLY), "", text)
            if n_dup != 1 or text.count("case 0x1F04:") != 1:
                print("fixup_factor5_ucode: FIXUP 6n SANITY FAILED: "
                      "duplicate case 0x1F04 could not be reduced to the "
                      "widened ovl1c||ovl20 form.", file=sys.stderr)
                sys.exit(1)
    elif OVL1C_1F04_MARKER not in text:
        def sub_exactly6n(pattern, repl_fn, n, what):
            global text
            new_text, count = pattern.subn(repl_fn, text)
            if count != n:
                print(f"fixup_factor5_ucode: FIXUP 6n ANCHOR FAILED ({what}): "
                      f"expected {n} substitution(s), made {count}. "
                      f"Regen changed the code shape — re-derive the anchors "
                      f"before trusting the ovl1c 0x1F04 trampoline return.",
                      file=sys.stderr)
                sys.exit(1)
            text = new_text

        if "OVL1C_1F04:" not in text:
            print("fixup_factor5_ucode: FIXUP 6n PRECONDITION FAILED: "
                  "OVL1C_1F04: missing. Run fixup 6k (make_clip_composite.py "
                  "0x1C + RSPRecomp on factor5_rsp_ovl1c.toml) first.",
                  file=sys.stderr)
            sys.exit(1)

        sub_exactly6n(
            re.compile(
                r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
            lambda m: OVL1C_1F04_CASE_ONLY + m.group(1),
            1, "case 0x1F04 overlay-0x1C trampoline return")

# ---------------------------------------------------------------------------
# Fixup 6o: route ovl1c $30-return at 0x1E6C (s756)
# ---------------------------------------------------------------------------
# s755: dest-0x1F04 / 153==0x1C is LIVE; UJ 0x1F04 went 3185→0.
# New residual is OVL1C_1F04 jr $30: Unhandled jump target
# 0x1EA8 n=1609 and 0x1E6C n=1570. Label OVL1C_1E6C already
# exists (6k sequential label after the delay slot). There is
# no case 0x1E6C. Independent of 6n's marker so an already-
# routed 0x1F04 file still gets this case. Do not add the
# sibling $30-return 0x1EA8 (or 0x1E7C/0x1E8C/0x1EBC/0x1ECC)
# until 0x1E6C is LIVE. Do not splice overlay 0x20 (dest
# 0x12A0).
# ORIGIN: ovl1c jal at IMEM 0x1E60 sets r31=0x1E6C and
# goto OVL1C_1ED4. The trampoline saves that into $30,
# returns through OVL1C_1F04, then jr $30. OVL1C_1F04
# jr $30 is the legitimate return into OVL1C_1E6C.
# Route, not a default-allow of 0x1E6C for every resident.
OVL1C_1E6C_MARKER = "/* fixup: ovl1c_1e6c */"
if is_main_ucode and OVL1C_1E6C_MARKER not in text:
    def sub_exactly6o(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6o ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the ovl1c 0x1E6C $30-return.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    if "OVL1C_1E6C:" not in text:
        print("fixup_factor5_ucode: FIXUP 6o PRECONDITION FAILED: "
              "OVL1C_1E6C: missing. Run fixup 6k (make_clip_composite.py "
              "0x1C + RSPRecomp on factor5_rsp_ovl1c.toml) first.",
              file=sys.stderr)
        sys.exit(1)

    sub_exactly6o(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: (
            "        case 0x1E6C: if (RSP_MEM_BU(0X153, 0) == 0x1C) { "
            "rs64_e9prov_ovl_route(0x1C, 0x1E6C); goto OVL1C_1E6C; } "
            "goto rs64_clip_stray;  " + OVL1C_1E6C_MARKER + "\n" + m.group(1)),
        1, "case 0x1E6C overlay-0x1C $30-return")

# ---------------------------------------------------------------------------
# Fixup 6p: route ovl1c $30-return at 0x1EA8 (s757)
# ---------------------------------------------------------------------------
# s756: dest-0x1E6C / 153==0x1C is LIVE; UJ 0x1E6C went 1570→0.
# Sibling leftover is Unhandled jump target 0x1EA8 n=1403 from
# OVL1C_1F04 jr $30. Label OVL1C_1EA8 already exists (6k
# sequential label after the delay slot). There is no case
# 0x1EA8. Independent of 6o's marker so an already-routed
# 0x1E6C file still gets this case. Do not add the $6==0
# landings (0x1E7C/0x1E8C/0x1EBC/0x1ECC) until they fire.
# Do not splice overlay 0x20 (dest 0x12A0). Do not widen
# 0x1E6C to 153==0x20.
# ORIGIN: ovl1c jal at IMEM 0x1E9C sets r31=0x1EA8 and
# goto OVL1C_1ED4. The trampoline saves that into $30,
# returns through OVL1C_1F04, then jr $30. OVL1C_1F04
# jr $30 is the legitimate return into OVL1C_1EA8.
# Route, not a default-allow of 0x1EA8 for every resident.
OVL1C_1EA8_MARKER = "/* fixup: ovl1c_1ea8 */"
if is_main_ucode and OVL1C_1EA8_MARKER not in text:
    def sub_exactly6p(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6p ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the ovl1c 0x1EA8 $30-return.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    if "OVL1C_1EA8:" not in text:
        print("fixup_factor5_ucode: FIXUP 6p PRECONDITION FAILED: "
              "OVL1C_1EA8: missing. Run fixup 6k (make_clip_composite.py "
              "0x1C + RSPRecomp on factor5_rsp_ovl1c.toml) first.",
              file=sys.stderr)
        sys.exit(1)

    sub_exactly6p(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: (
            "        case 0x1EA8: if (RSP_MEM_BU(0X153, 0) == 0x1C) { "
            "rs64_e9prov_ovl_route(0x1C, 0x1EA8); goto OVL1C_1EA8; } "
            "goto rs64_clip_stray;  " + OVL1C_1EA8_MARKER + "\n" + m.group(1)),
        1, "case 0x1EA8 overlay-0x1C $30-return")

# ---------------------------------------------------------------------------
# Fixup 6q: route overlay 0x20 emit at dest 0x12A0 (s759)
# ---------------------------------------------------------------------------
# s758: overlay 0x20 is dest 0x12A0 emit (ROM 0x27108, 0x158 B), not
# restore and not a 0x1DB0 sibling. Table desc 0x2157. First word
# lbu $2, -4($17). Body jals still-resident OVL1C_1ED4 six times,
# then L_17F0 / L_112C, exits j L_1268; ori $5, 0x28. Do not
# overwrite L_12A0 or OVL24_12A0. factor5_rsp_ovl20.toml translates
# a composite whose 0x12A0 range holds the emit image; this fixup
# extracts L_12A0..0x13F7, renames OVL20_*, rewrites jal 0x1ED4 to
# OVL1C_1ED4, routes DMEM 0x153 == 0x20 at dest 0x12A0 and the
# shared 0x12A0-window cases, and keeps OVL1C_1ED4 / 0x1F04
# reachable at 153==0x20. ORIGIN: OVL1C_1ECC is j L_1268; ori $5,
# 0x20. Table dest 0x12A0. Route, not an overwrite.
OVL20_MARKER = "/* fixup: ovl20route */"
OVL20_END = 0x13F8  # dest 0x12A0 + inclusive 0x157 + 1
if is_main_ucode and OVL20_MARKER not in text:
    ovl20_path = path.parent / "factor5_ucode_ovl20_recompiled.c"
    if not ovl20_path.exists():
        print("fixup_factor5_ucode: FIXUP 6q INPUT MISSING: "
              f"{ovl20_path} not found. Run make_clip_composite.py 0x20 and "
              "RSPRecomp on factor5_rsp_ovl20.toml before fixing up the "
              "main ucode, or the overlay-0x20 route is lost.", file=sys.stderr)
        sys.exit(1)
    ovl20_text = ovl20_path.read_text(encoding="utf-8")

    def sub_exactly6q(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6q ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the overlay-0x20 route.", file=sys.stderr)
            sys.exit(1)
        text = new_text

    if "OVL1C_1ED4:" not in text or "OVL1C_1F04:" not in text:
        print("fixup_factor5_ucode: FIXUP 6q PRECONDITION FAILED: "
              "OVL1C_1ED4/OVL1C_1F04 missing. Run fixup 6k/6n first.",
              file=sys.stderr)
        sys.exit(1)

    m_start = re.search(r"^L_12A0:\n", ovl20_text, flags=re.MULTILINE)
    after = [(int(m.group(1), 16), m.start())
             for m in re.finditer(r"^L_([0-9A-F]{4}):", ovl20_text, flags=re.MULTILINE)
             if int(m.group(1), 16) >= OVL20_END]
    if not m_start or not after:
        print("fixup_factor5_ucode: FIXUP 6q EXTRACTION FAILED: could not "
              "bound L_12A0..first-label-past-overlay in the ovl20 file.",
              file=sys.stderr)
        sys.exit(1)
    region = ovl20_text[m_start.start():after[0][1]]
    exit_m = None
    for exit_m in re.finditer(r"    goto L_1268;\n", region):
        pass
    if not exit_m:
        print("fixup_factor5_ucode: FIXUP 6q EXTRACTION FAILED: no "
              "goto L_1268 exit in the ovl20 region.", file=sys.stderr)
        sys.exit(1)
    region = region[:exit_m.end()]

    region_labels = set(re.findall(r"^(L_[0-9A-F]{4}):", region, flags=re.MULTILINE))
    expected_external = {"L_112C", "L_1268", "L_17F0", "L_1ED4"}
    referenced = set(re.findall(r"goto (L_[0-9A-F]{4});", region))
    external = referenced - region_labels
    if external != expected_external:
        print(f"fixup_factor5_ucode: FIXUP 6q SANITY FAILED: region's external "
              f"references {sorted(external)} != expected resident helpers "
              f"{sorted(expected_external)}. The overlay-0x20 image or its "
              f"translation changed — re-derive before routing.", file=sys.stderr)
        sys.exit(1)
    for need in ("L_12A0", "L_12BC", "L_13F0"):
        if need not in region_labels:
            print("fixup_factor5_ucode: FIXUP 6q SANITY FAILED: missing "
                  f"{need} in ovl20 region {sorted(region_labels)}.",
                  file=sys.stderr)
            sys.exit(1)
    for lbl in region_labels:
        region = re.sub(r"\b" + lbl + r"\b", "OVL20_" + lbl[2:], region)
    region, n_1ed4 = re.subn(r"goto L_1ED4;", "goto OVL1C_1ED4;", region)
    if n_1ed4 != 6:
        print("fixup_factor5_ucode: FIXUP 6q SANITY FAILED: expected 6 "
              f"jal-0x1ED4 rewrites, made {n_1ed4}.", file=sys.stderr)
        sys.exit(1)

    sub_exactly6q(
        re.compile(r"(^do_indirect_jump:\n)", flags=re.MULTILINE),
        lambda m: OVL20_MARKER + "\n" + region + m.group(1),
        1, "splice point")

    ovl20_addrs = sorted(int(lbl[2:], 16) for lbl in region_labels)
    routed = set()
    for addr in ovl20_addrs:
        pat24 = re.compile(
            rf"(        case 0x{addr:04X}:  /\* fixup: ovl24route \*/\n"
            rf"            if \(RSP_MEM_BU\(0X153, 0\) == 0x24\) \{{"
            rf" rs64_e9prov_ovl_route\(0x24, 0x{addr:04X}\); "
            rf"goto OVL24_{addr:04X}; \}}\n"
            rf"            goto L_{addr:04X};\n)")
        if pat24.search(text):
            sub_exactly6q(
                pat24,
                lambda m, a=addr: (
                    f"        case 0x{a:04X}:  " + OVL24_MARKER + "\n"
                    f"            if (RSP_MEM_BU(0X153, 0) == 0x24) {{"
                    f" rs64_e9prov_ovl_route(0x24, 0x{a:04X}); "
                    f"goto OVL24_{a:04X}; }}\n"
                    f"            if (RSP_MEM_BU(0X153, 0) == 0x20) {{"
                    f" rs64_e9prov_ovl_route(0x20, 0x{a:04X}); "
                    f"goto OVL20_{a:04X}; }}  " + OVL20_MARKER + "\n"
                    f"            goto L_{a:04X};\n"),
                1, f"case 0x{addr:04X} shared ovl24+ovl20")
            routed.add(addr)
            continue
        pat04 = re.compile(
            rf"(        case 0x{addr:04X}: if \(RSP_MEM_BU\(0X153, 0\) == 0x24 \|\| "
            rf"RSP_MEM_BU\(0X153, 0\) == 0x04\) \{{ "
            rf"rs64_e9prov_ovl_route\(0x24, 0x{addr:04X}\); "
            rf"goto OVL24_{addr:04X}; \}} "
            rf"goto rs64_clip_stray;  /\* fixup: ovl24-(?:04ret|1364clip) \*/\n)")
        if pat04.search(text):
            sub_exactly6q(
                pat04,
                lambda m, a=addr: (
                    f"        case 0x{a:04X}: if (RSP_MEM_BU(0X153, 0) == 0x20) {{ "
                    f"rs64_e9prov_ovl_route(0x20, 0x{a:04X}); "
                    f"goto OVL20_{a:04X}; }} "
                    f"if (RSP_MEM_BU(0X153, 0) == 0x24 || "
                    f"RSP_MEM_BU(0X153, 0) == 0x04) {{ "
                    f"rs64_e9prov_ovl_route(0x24, 0x{a:04X}); "
                    f"goto OVL24_{a:04X}; }} "
                    f"goto rs64_clip_stray;  " + OVL20_MARKER + "\n"),
                1, f"case 0x{addr:04X} ovl24-04ret + ovl20")
            routed.add(addr)
            continue
        pat_bare = re.compile(
            rf"        case 0x{addr:04X}: goto L_{addr:04X};\n")
        if pat_bare.search(text):
            sub_exactly6q(
                pat_bare,
                lambda m, a=addr: (
                    f"        case 0x{a:04X}:  " + OVL20_MARKER + "\n"
                    f"            if (RSP_MEM_BU(0X153, 0) == 0x20) {{"
                    f" rs64_e9prov_ovl_route(0x20, 0x{a:04X}); "
                    f"goto OVL20_{a:04X}; }}\n"
                    f"            goto L_{a:04X};\n"),
                1, f"case 0x{addr:04X} bare + ovl20")
            routed.add(addr)

    ovl20_only = "".join(
        f"        case 0x{a:04X}: if (RSP_MEM_BU(0X153, 0) == 0x20) {{ "
        f"rs64_e9prov_ovl_route(0x20, 0x{a:04X}); goto OVL20_{a:04X}; }} "
        f"goto rs64_clip_stray;  {OVL20_MARKER}\n"
        for a in ovl20_addrs if a not in routed)
    if ovl20_only:
        sub_exactly6q(
            re.compile(r"(        case 0x12A0:  /\* fixup: ovl24route \*/\n)"),
            lambda m: ovl20_only + m.group(1),
            1, "overlay-0x20 handshake/return cases")

    sub_exactly6q(
        re.compile(
            r"        case 0x1F04: if \(RSP_MEM_BU\(0X153, 0\) == 0x1C\) \{ "
            r"rs64_e9prov_ovl_route\(0x1C, 0x1F04\); goto OVL1C_1F04; \} "
            r"goto rs64_clip_stray;  /\* fixup: ovl1c_1f04 \*/\n"),
        lambda m: (
            "        case 0x1F04: if (RSP_MEM_BU(0X153, 0) == 0x1C) { "
            "rs64_e9prov_ovl_route(0x1C, 0x1F04); goto OVL1C_1F04; } "
            "if (RSP_MEM_BU(0X153, 0) == 0x20) { "
            "rs64_e9prov_ovl_route(0x20, 0x1F04); goto OVL1C_1F04; } "
            "goto rs64_clip_stray;  " + OVL1C_1F04_MARKER + " "
            + OVL20_MARKER + "\n"),
        1, "widen 0x1F04 ovl1c||ovl20")

    sub_exactly6q(
        re.compile(r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: (
            "        case 0x1ED4: if (RSP_MEM_BU(0X153, 0) == 0x20) { "
            "rs64_e9prov_ovl_route(0x20, 0x1ED4); goto OVL1C_1ED4; } "
            "goto rs64_clip_stray;  " + OVL20_MARKER + "\n" + m.group(1)),
        1, "case 0x1ED4 ovl20 trampoline keep")

# ---------------------------------------------------------------------------
# Fixup 6r: route 0x13B8 for overlay-0x20 clip-resident return (s760)
# ---------------------------------------------------------------------------
# s759: dest 0x12A0 / 153==0x20 is LIVE, but 419 [clip-stray] tgt=0x13B8
# 153==0x04 arrive after OVL20 jal L_17F0 (IMEM 0x13B0, r31=0x13B8).
# L_17F0 hand is r5=4; goto L_1268, so dest becomes clip 0x1DB0 and
# CLIP_1E48 jr's the saved $ra. Clip dest does not overwrite IMEM
# 0x12A0..0x13F7, so 0x13B8 is still the ovl20 emit image. 6q's
# ovl20-only case required 153==0x20 and turned that legitimate
# return into [clip-stray]. Same class as s744/s745 0x1364.
# Widen only 0x13B8 — do not steal ovl24 0x1364's 0x24||0x04 arm,
# and do not blanket-widen 0x13C0/0x13D8/0x13F0 (jal L_112C
# siblings). ORIGIN: CLIP_1E48 jr of a ROM clip dispatch; route,
# not a guard.
OVL20_13B8CLIP_MARKER = "/* fixup: ovl20-13b8clip */"
if is_main_ucode and OVL20_13B8CLIP_MARKER not in text:
    def sub_exactly6r(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6r ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    sub_exactly6r(
        re.compile(
            r"        case 0x13B8: if \(RSP_MEM_BU\(0X153, 0\) == 0x20\) \{ "
            r"rs64_e9prov_ovl_route\(0x20, 0x13B8\); goto OVL20_13B8; \} "
            r"goto rs64_clip_stray;  /\* fixup: ovl20route \*/\n"),
        lambda m: (
            "        case 0x13B8: if (RSP_MEM_BU(0X153, 0) == 0x20 || "
            "RSP_MEM_BU(0X153, 0) == 0x04) { "
            "rs64_e9prov_ovl_route(0x20, 0x13B8); goto OVL20_13B8; } "
            "goto rs64_clip_stray;  " + OVL20_13B8CLIP_MARKER + "\n"),
        1, "case 0x13B8 clip-resident return")

# ---------------------------------------------------------------------------
# Fixup 6s: route 0x13C0 for overlay-0x20 jal-L_112C return (s761)
# ---------------------------------------------------------------------------
# s760: 0x13B8/04 419->0, residual [clip-stray] tgt=0x13C0 153=0x04
# n=643 line=400. OVL20_13B8 jal L_112C sets r31=0x13C0; L_112C
# copies r31->r30 (delay slot of beq $10,$zero,L_11A0 and fallthrough);
# L_11A0 jr $30. Same class as s745 0x1364 / s760 0x13B8.
# 0x13C0 itself is restore-regs then j OVL20_133C — do not widen
# 0x13D8 / 0x13F0 / 0x133C this step, and do not steal ovl24
# 0x1364's 0x24||0x04 arm. ORIGIN: L_11A0 jr of OVL20 jal L_112C;
# 0x04 arm is that return. Route, not a guard.
OVL20_13C0CLIP_MARKER = "/* fixup: ovl20-13c0clip */"
if is_main_ucode and OVL20_13C0CLIP_MARKER not in text:
    def sub_exactly6s(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6s ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    sub_exactly6s(
        re.compile(
            r"        case 0x13C0: if \(RSP_MEM_BU\(0X153, 0\) == 0x20\) \{ "
            r"rs64_e9prov_ovl_route\(0x20, 0x13C0\); goto OVL20_13C0; \} "
            r"goto rs64_clip_stray;  /\* fixup: ovl20route \*/\n"),
        lambda m: (
            "        case 0x13C0: if (RSP_MEM_BU(0X153, 0) == 0x20 || "
            "RSP_MEM_BU(0X153, 0) == 0x04) { "
            "rs64_e9prov_ovl_route(0x20, 0x13C0); goto OVL20_13C0; } "
            "goto rs64_clip_stray;  " + OVL20_13C0CLIP_MARKER + "\n"),
        1, "case 0x13C0 jal-L_112C return")

# ---------------------------------------------------------------------------
# Fixup 6t: route ovl1c $30-return at 0x1EBC (s762)
# ---------------------------------------------------------------------------
# s761: 0x13C0/04 643->0 and all clip-stray 0; ovl20 04-return
# class CLOSED. Residual is Unhandled jump target 0x1EBC n=557
# + 0x1E7C n=69 from OVL1C_1F04 jr $30 (line 4987). First UJ
# is before the first sec2 row. Label OVL1C_1EBC already exists
# (6k sequential label after the delay slot). There is no case
# 0x1EBC. Independent of 6p's marker so an already-routed
# 0x1EA8 file still gets this case. Do not add the sibling
# $30-returns 0x1E7C / 0x1E8C / 0x1ECC this step. Do not
# widen 0x1E6C to 153==0x20. Do not touch ovl20 dest 0x12A0
# or the 0x13C0/0x13B8 04-arms.
# ORIGIN: ovl1c jal at IMEM 0x1EAC sets r31=0x1EBC and
# goto OVL1C_1ED4. The trampoline saves that into $30,
# returns through OVL1C_1F04, then jr $30. OVL1C_1F04
# jr $30 is the legitimate return into OVL1C_1EBC.
# Route, not a default-allow of 0x1EBC for every resident.
OVL1C_1EBC_MARKER = "/* fixup: ovl1c_1ebc */"
if is_main_ucode and OVL1C_1EBC_MARKER not in text:
    def sub_exactly6t(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6t ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the ovl1c 0x1EBC $30-return.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    if "OVL1C_1EBC:" not in text:
        print("fixup_factor5_ucode: FIXUP 6t PRECONDITION FAILED: "
              "OVL1C_1EBC: missing. Run fixup 6k (make_clip_composite.py "
              "0x1C + RSPRecomp on factor5_rsp_ovl1c.toml) first.",
              file=sys.stderr)
        sys.exit(1)

    sub_exactly6t(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: (
            "        case 0x1EBC: if (RSP_MEM_BU(0X153, 0) == 0x1C) { "
            "rs64_e9prov_ovl_route(0x1C, 0x1EBC); goto OVL1C_1EBC; } "
            "goto rs64_clip_stray;  " + OVL1C_1EBC_MARKER + "\n" + m.group(1)),
        1, "case 0x1EBC overlay-0x1C $30-return")

# ---------------------------------------------------------------------------
# Fixup 6u: route ovl1c $30-return at 0x1ECC (s763)
# ---------------------------------------------------------------------------
# s762: dest-0x1EBC / 153==0x1C is LIVE; UJ 0x1EBC went 557->0.
# Residual is Unhandled jump target 0x1ECC n=2016 + 0x1E7C
# n=68 from OVL1C_1F04 jr $30 (line 4987). First UJ is before
# the first sec2 row. Label OVL1C_1ECC already exists (6k
# sequential; j L_1268; ori $5, 0x20 — the ovl20-dispatch
# exit). There is no case 0x1ECC. Independent of 6t's marker
# so an already-routed 0x1EBC file still gets this case. Do
# not add the sibling $30-return 0x1E7C (or 0x1E8C) this
# step. Do not widen 0x1E6C to 153==0x20. Do not touch ovl20
# dest 0x12A0 or the 0x13C0/0x13B8 04-arms.
# ORIGIN: ovl1c jal at IMEM 0x1EBC sets r31=0x1ECC and
# goto OVL1C_1ED4. The trampoline saves that into $30,
# returns through OVL1C_1F04, then jr $30. OVL1C_1F04
# jr $30 is the legitimate return into OVL1C_1ECC (the
# ovl20-dispatch exit). Route, not a default-allow of
# 0x1ECC for every resident — a wrong 153 arm would
# dispatch ovl20 from a non-ovl1c resident.
OVL1C_1ECC_MARKER = "/* fixup: ovl1c_1ecc */"
if is_main_ucode and OVL1C_1ECC_MARKER not in text:
    def sub_exactly6u(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6u ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the ovl1c 0x1ECC $30-return.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    if "OVL1C_1ECC:" not in text:
        print("fixup_factor5_ucode: FIXUP 6u PRECONDITION FAILED: "
              "OVL1C_1ECC: missing. Run fixup 6k (make_clip_composite.py "
              "0x1C + RSPRecomp on factor5_rsp_ovl1c.toml) first.",
              file=sys.stderr)
        sys.exit(1)

    sub_exactly6u(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: (
            "        case 0x1ECC: if (RSP_MEM_BU(0X153, 0) == 0x1C) { "
            "rs64_e9prov_ovl_route(0x1C, 0x1ECC); goto OVL1C_1ECC; } "
            "goto rs64_clip_stray;  " + OVL1C_1ECC_MARKER + "\n" + m.group(1)),
        1, "case 0x1ECC overlay-0x1C $30-return")

# ---------------------------------------------------------------------------
# Fixup 6v: route ovl1c $30-return at 0x1E7C (s764)
# ---------------------------------------------------------------------------
# s763: dest-0x1ECC / 153==0x1C is LIVE; UJ 0x1ECC went 2016->0.
# Residual is Unhandled jump target 0x1E7C n=91 from OVL1C_1F04
# jr $30 (line 4987). First UJ is after leave and before the
# first sec2 row. Label OVL1C_1E7C already exists (6k sequential;
# jal 0x1ED4 r31=0x1E8C). There is no case 0x1E7C. Independent
# of 6u's marker so an already-routed 0x1ECC file still gets
# this case. Do not add the sibling $30-return 0x1E8C this
# step. Do not widen 0x1E6C to 153==0x20. Do not touch ovl20
# dest 0x12A0 or the 0x13C0/0x13B8 04-arms.
# ORIGIN: ovl1c jal at IMEM 0x1E70 sets r31=0x1E7C and
# goto OVL1C_1ED4. The trampoline saves that into $30,
# returns through OVL1C_1F04, then jr $30. OVL1C_1F04
# jr $30 is the legitimate return into OVL1C_1E7C.
# Route, not a default-allow of 0x1E7C for every resident.
OVL1C_1E7C_MARKER = "/* fixup: ovl1c_1e7c */"
if is_main_ucode and OVL1C_1E7C_MARKER not in text:
    def sub_exactly6v(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6v ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the ovl1c 0x1E7C $30-return.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    if "OVL1C_1E7C:" not in text:
        print("fixup_factor5_ucode: FIXUP 6v PRECONDITION FAILED: "
              "OVL1C_1E7C: missing. Run fixup 6k (make_clip_composite.py "
              "0x1C + RSPRecomp on factor5_rsp_ovl1c.toml) first.",
              file=sys.stderr)
        sys.exit(1)

    sub_exactly6v(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: (
            "        case 0x1E7C: if (RSP_MEM_BU(0X153, 0) == 0x1C) { "
            "rs64_e9prov_ovl_route(0x1C, 0x1E7C); goto OVL1C_1E7C; } "
            "goto rs64_clip_stray;  " + OVL1C_1E7C_MARKER + "\n" + m.group(1)),
        1, "case 0x1E7C overlay-0x1C $30-return")

# ---------------------------------------------------------------------------
# Fixup 6w: route ovl1c $30-return at 0x1E8C (s765)
# ---------------------------------------------------------------------------
# Residual UJ 0x1E8C is the return from OVL1C_1E7C's jal 0x1ED4.
# OVL1C_1ED4 saves that return into $30 and OVL1C_1F04 restores it.
# This is the legitimate overlay-0x1C continuation, so route it by
# resident id rather than allowing the target for every overlay.
OVL1C_1E8C_MARKER = "/* fixup: ovl1c_1e8c */"
if is_main_ucode and OVL1C_1E8C_MARKER not in text:
    def sub_exactly6w(pattern, repl_fn, n, what):
        global text
        new_text, count = pattern.subn(repl_fn, text)
        if count != n:
            print(f"fixup_factor5_ucode: FIXUP 6w ANCHOR FAILED ({what}): "
                  f"expected {n} substitution(s), made {count}. "
                  f"Regen changed the code shape — re-derive the anchors "
                  f"before trusting the ovl1c 0x1E8C $30-return.",
                  file=sys.stderr)
            sys.exit(1)
        text = new_text

    if "OVL1C_1E8C:" not in text:
        print("fixup_factor5_ucode: FIXUP 6w PRECONDITION FAILED: "
              "OVL1C_1E8C: missing. Run fixup 6k (make_clip_composite.py "
              "0x1C + RSPRecomp on factor5_rsp_ovl1c.toml) first.",
              file=sys.stderr)
        sys.exit(1)

    sub_exactly6w(
        re.compile(
            r"(        case 0x1DB0:  /\* fixup: clipsplice \*/\n)"),
        lambda m: (
            "        case 0x1E8C: if (RSP_MEM_BU(0X153, 0) == 0x1C) { "
            "rs64_e9prov_ovl_route(0x1C, 0x1E8C); goto OVL1C_1E8C; } "
            "goto rs64_clip_stray;  " + OVL1C_1E8C_MARKER + "\n" + m.group(1)),
        1, "case 0x1E8C overlay-0x1C $30-return")

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
RESET_REUSE_MARKER = "/* fixup: L_1DB0 depth-reset route audit v5 */"
if is_main_ucode:
    text = re.sub(r'^.*(?:rs64_e9prov_l1db0_predecessor|uint32_t rs64_e9prov_from_l1298|rs64_e9prov_from_l1298 = [01];).*\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'  /\* fixup: L_1DB0 depth-reset route audit v[0-9]+ \*/', '', text)
if is_main_ucode and RESET_REUSE_MARKER not in text:
    reset_decl = re.compile(r'extern "C" void rs64_e9prov_l1db0_reset[^\n]*\n')
    if reset_decl.search(text):
        text, n_decl = reset_decl.subn(
            'extern "C" void rs64_e9prov_l1db0_reset(uint32_t old, uint32_t r17, uint32_t ra, uint32_t resident);\n' +
            'extern "C" void rs64_e9prov_l1db0_predecessor(uint32_t target, uint32_t line, uint32_t ra, uint32_t resident, uint32_t r17, uint32_t from_l1298);  ' +
            RESET_REUSE_MARKER + "\n", text, count=1)
    else:
        decl_anchor = re.compile(r"(extern \"C\" void rs64_e9prov_l12a0_source[^\n]*\n)")
        text, n_decl = decl_anchor.subn(
            lambda m: m.group(1) +
            'extern "C" void rs64_e9prov_l1db0_reset(uint32_t old, uint32_t r17, uint32_t ra, uint32_t resident);\n' +
            'extern "C" void rs64_e9prov_l1db0_predecessor(uint32_t target, uint32_t line, uint32_t ra, uint32_t resident, uint32_t r17, uint32_t from_l1298);  ' +
            RESET_REUSE_MARKER + "\n",
            text, count=1)
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 12c ANCHOR FAILED (declaration).", file=sys.stderr)
        sys.exit(1)
    entry_decl = re.compile(r"(    Rs64OvlTrace rs64_ot;[^\n]*\n)")
    text, n_entry = entry_decl.subn(
        lambda m: m.group(1) + "    uint32_t rs64_e9prov_from_l1298 = 0;  " + RESET_REUSE_MARKER + "\n",
        text, count=1)
    if n_entry != 1:
        print("fixup_factor5_ucode: FIXUP 12c ANCHOR FAILED (predecessor local).", file=sys.stderr)
        sys.exit(1)
    l1298_anchor = re.compile(r"(L_1298:\n[\s\S]{0,900}?)([ \t]*// jr          \$3)")
    text, n_l1298 = l1298_anchor.subn(
        lambda m: m.group(1) + "    rs64_e9prov_from_l1298 = 1;  " + RESET_REUSE_MARKER + "\n" + m.group(2),
        text, count=1)
    if n_l1298 != 1:
        print("fixup_factor5_ucode: FIXUP 12c ANCHOR FAILED (L_1298 predecessor).", file=sys.stderr)
        sys.exit(1)
    switch_anchor = re.compile(r"(    switch \(\(jump_target \| 0x1000\) & 0X1FFF\) \{[ \t]*\n)")
    text, n_switch = switch_anchor.subn(
        lambda m: "    if (((jump_target | 0x1000) & 0X1FFF) == 0x1DB0) rs64_e9prov_l1db0_predecessor(jump_target, (uint32_t)debug_line, r31, RSP_MEM_BU(0X153, 0), r17, rs64_e9prov_from_l1298);  " + RESET_REUSE_MARKER + "\n" +
        "    rs64_e9prov_from_l1298 = 0;  " + RESET_REUSE_MARKER + "\n" + m.group(1),
        text, count=1)
    if n_switch != 1:
        print("fixup_factor5_ucode: FIXUP 12c ANCHOR FAILED (predecessor switch).", file=sys.stderr)
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
# Fixup 13b: phase-scoped Factor 5 state census. Keep this separate from the
# inline-advance marker so an existing generated file can gain the probe
# without replaying older fixups.
# ---------------------------------------------------------------------------
F5_STATE_MARKER = "/* fixup: F5 state census v1 */"
if is_main_ucode and F5_STATE_MARKER not in text:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_inline_probe_resume[^\n]*\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) +
        'extern "C" void rs64_f5_state_probe(uint32_t r17, uint32_t w0, uint32_t w1);  ' +
        F5_STATE_MARKER + "\n",
        text, count=1)
    state_anchor = re.compile(
        r"(    r20 = RSP_MEM_W_LOAD\(0X4, r17\);\n)"
        r"(    if \(\(r19 >> 24\) == 0xE9\) rs64_e9prov_guest)"
    )
    text, n_state = state_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_f5_state_probe(r17, r19, r20);  " + F5_STATE_MARKER + "\n" +
        m.group(2),
        text, count=1)
    if n_decl != 1 or n_state != 1:
        print(f"fixup_factor5_ucode: FIXUP 13b ANCHOR FAILED (decl={n_decl} state={n_state}).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 18: record L_11B0's actual indirect continuation (s726).
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Fixup 19: capture the final shade accumulator and VGE selection (s1014).
# ---------------------------------------------------------------------------
M4_ACCUM_MARKER = "/* fixup: M4 accumulator probe v2 */"
m4_migrated = False
if is_shade_ucode and M4_ACCUM_MARKER in text and text.count('rs64_m4_accum_probe(&rsp, 12, r9, rdram);') == 1:
    needle = '    rsp.VGE<3>(rsp.vpu.r[6], rsp.vpu.r[6], rsp.vpu.r[29]);\n    // lqv'
    text = text.replace(needle, '    rsp.VGE<3>(rsp.vpu.r[6], rsp.vpu.r[6], rsp.vpu.r[29]);\n    rs64_m4_accum_probe(&rsp, 12, r9, rdram);  /* fixup: M4 accumulator probe v2 */\n    // lqv', 1)
if is_shade_ucode and M4_ACCUM_MARKER not in text:
    text = text.replace(
        'rs64_m4_accum_probe(&rsp, 1);  /* fixup: M4 accumulator probe v1 */',
        'rs64_m4_accum_probe(&rsp, 1, r9, rdram);  /* fixup: M4 accumulator probe v2 */')
    text = text.replace(
        'rs64_m4_accum_probe(&rsp, 10);  /* fixup: M4 accumulator probe v1 */',
        'rs64_m4_accum_probe(&rsp, 10, r9, rdram);  /* fixup: M4 accumulator probe v2 */')
    text = text.replace(
        'rs64_m4_accum_probe(&rsp, 11);  /* fixup: M4 accumulator probe v1 */',
        'rs64_m4_accum_probe(&rsp, 11, r9, rdram);  /* fixup: M4 accumulator probe v2 */')
    text = text.replace(
        'rs64_m4_accum_probe(&rsp, 12);  /* fixup: M4 accumulator probe v1 */',
        'rs64_m4_accum_probe(&rsp, 12, r9, rdram);  /* fixup: M4 accumulator probe v2 */')
    text = text.replace(
        'extern "C" void rs64_m4_accum_probe(void *rsp, uint32_t stage);  /* fixup: M4 accumulator probe v1 */',
        'extern "C" void rs64_m4_accum_probe(void *rsp, uint32_t stage, uint32_t r9, const uint8_t *rdram);  /* fixup: M4 accumulator probe v2 */')
    old_vge = '    rsp.VGE<3>(rsp.vpu.r[6], rsp.vpu.r[6], rsp.vpu.r[29]);\n    rs64_m4_accum_probe(&rsp, 12, r9, rdram);  /* fixup: M4 accumulator probe v2 */'
    text = text.replace(old_vge, old_vge, 1)
    # The second branch has the same VGE but no probe after the first fixup pass.
    needle = '    rsp.VGE<3>(rsp.vpu.r[6], rsp.vpu.r[6], rsp.vpu.r[29]);\n    lqv'
    text = text.replace(needle, '    rsp.VGE<3>(rsp.vpu.r[6], rsp.vpu.r[6], rsp.vpu.r[29]);\n    rs64_m4_accum_probe(&rsp, 12, r9, rdram);  /* fixup: M4 accumulator probe v2 */\n    lqv', 1)
    record = '    rsp.SSV<14>(rsp.vpu.r[26], r9, 0X25);\n'
    text = text.replace(record, record + '    rs64_m4_accum_probe(&rsp, 13, r9, rdram);  /* fixup: M4 accumulator probe v2 */\n', 1)
    if 'rs64_m4_accum_probe(&rsp, 13, r9, rdram);' not in text:
        print("fixup_factor5_ucode: FIXUP 19 migration failed (record).", file=sys.stderr)
        sys.exit(1)
    if 'rs64_m4_accum_probe(&rsp, 12, r9, rdram);' not in text:
        print("fixup_factor5_ucode: FIXUP 19 migration failed (VGE).", file=sys.stderr)
        sys.exit(1)
    if 'probe v1' in text:
        print("fixup_factor5_ucode: FIXUP 19 migration left v1 marker.", file=sys.stderr)
        sys.exit(1)
    m4_migrated = True
if is_shade_ucode and M4_ACCUM_MARKER not in text and not m4_migrated:
    decl_anchor = re.compile(r"(extern \"C\" void rs64_inline_probe_resume[^\n]*\n|#include \"librecomp/rsp_vu_impl\.hpp\"\n)")
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) +
        'extern "C" void rs64_m4_accum_probe(void *rsp, uint32_t stage, uint32_t r9, const uint8_t *rdram);  ' + M4_ACCUM_MARKER + "\n",
        text, count=1)
    control = re.compile(
        r"(    rsp\.VMADH<0>\(rsp\.vpu\.r\[2\], rsp\.vpu\.r\[1\], rsp\.vpu\.r\[2\]\);\n)"
    )
    text, n_control = control.subn(
        lambda m: m.group(1) +
        "    rs64_m4_accum_probe(&rsp, 1, r9, rdram);  " + M4_ACCUM_MARKER + "\n",
        text, count=1)
    target = re.compile(
        r"(    // ldv         \$v29\[0\], 0x60\(\$zero\)\n)"
        r"(    rsp\.LDV<0>\(rsp\.vpu\.r\[29\], 0, 0XC\);\n)"
        r"(    // vmadh       \$v6, \$v4, \$v0\n)"
        r"(    rsp\.VMADH<0>\(rsp\.vpu\.r\[6\], rsp\.vpu\.r\[4\], rsp\.vpu\.r\[0\]\);\n)"
    )
    text, n_target = target.subn(
        lambda m: m.group(1) + m.group(2) +
        "    rs64_m4_accum_probe(&rsp, 10, r9, rdram);  " + M4_ACCUM_MARKER + "\n" +
        m.group(3) + m.group(4) +
        "    rs64_m4_accum_probe(&rsp, 11, r9, rdram);  " + M4_ACCUM_MARKER + "\n",
        text, count=1)
    vge = re.compile(
        r"(    rsp\.VGE<3>\(rsp\.vpu\.r\[6\], rsp\.vpu\.r\[6\], rsp\.vpu\.r\[29\]\);\n)"
    )
    text, n_vge = vge.subn(
        lambda m: m.group(1) +
        "    rs64_m4_accum_probe(&rsp, 12, r9, rdram);  " + M4_ACCUM_MARKER + "\n",
        text, count=2)
    record = re.compile(r"(    rsp\.SSV<14>\(rsp\.vpu\.r\[26\], r9, 0X25\);\n)")
    text, n_record = record.subn(
        lambda m: m.group(1) +
        "    rs64_m4_accum_probe(&rsp, 13, r9, rdram);  " + M4_ACCUM_MARKER + "\n",
        text, count=1)
    if (n_decl, n_control, n_target, n_vge, n_record) != (1, 1, 1, 2, 1):
        print(f"fixup_factor5_ucode: FIXUP 19 ANCHOR FAILED (decl={n_decl} control={n_control} target={n_target} vge={n_vge}).", file=sys.stderr)
        sys.exit(1)

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
# Fixup 20: phase-gated 0x8000-Y emit vs clip-reject (s1856).
# L_17F0 entry classifies vertex +0x1A == 0x8000 against +0x24 clip codes.
# L_112C walks the 0xD60..r16 command buffer for 0xC8|flags YL/YM/YH.
# ---------------------------------------------------------------------------
M4_Y8000_MARKER = "/* fixup: M4 y8000 */"
if is_main_ucode and M4_Y8000_MARKER not in text:
    decl_anchor = re.compile(
        r'(extern "C" void rs64_m4_accum_probe\(void \*rsp, uint32_t stage, uint32_t r9, const uint8_t \*rdram\);  /\* fixup: M4 accumulator probe v2 \*/\n)'
    )
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) +
        'extern "C" void rs64_m4_y8000_entry(uint32_t y11, uint32_t y12, uint32_t y13, '
        'uint32_t c13, uint32_t c12, uint32_t c11);\n'
        'extern "C" void rs64_m4_y8000_flush(uint32_t r16);  ' + M4_Y8000_MARKER + "\n",
        text, count=1)
    entry_anchor = re.compile(
        r"(    r3 = RSP_MEM_HU_LOAD\(0X24, r11\);\n)"
        r"(    // and         \$7, \$6, \$2\n)"
    )
    text, n_entry = entry_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_m4_y8000_entry((uint32_t)RSP_MEM_HU_LOAD(0X1A, r11), "
        "(uint32_t)RSP_MEM_HU_LOAD(0X1A, r12), "
        "(uint32_t)RSP_MEM_HU_LOAD(0X1A, r13), r6, r2, r3);  " +
        M4_Y8000_MARKER + "\n" + m.group(2),
        text, count=1)
    flush_anchor = re.compile(
        r"(    r10 = RSP_ADD32\(r16, -0XD60\);\n)"
        r"(    // beq         \$10, \$zero, L_11A0\n)"
    )
    text, n_flush = flush_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_m4_y8000_flush(r16);  " + M4_Y8000_MARKER + "\n" + m.group(2),
        text, count=1)
    if (n_decl, n_entry, n_flush) != (1, 1, 1):
        print(f"fixup_factor5_ucode: FIXUP 20 ANCHOR FAILED "
              f"(decl={n_decl} entry={n_entry} flush={n_flush}).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 21: writer-attestation for the hangar hologram-beam triangle-order
# check (s1967/s1968). L_1930 (emit) stores the RDP command header byte
# (0xC8|flags) at *(u8*)(state) = r10 via `sb $10, 0x0($16)`. Hooking this
# exact store lets rs64_m4_y8000_flush's walker tell a genuinely-written
# header from a stale/leftover byte at the same offset: if flush finds a
# 0xC8-class header at an offset this store never touched this frame, the
# offset was never really written and the "malformed triangle" found in
# s1967 is a stale-buffer misread, not a writer bug.
# ---------------------------------------------------------------------------
M4_STORE_MARKER = "/* fixup: M4 store attest */"
if is_main_ucode and M4_STORE_MARKER not in text:
    decl_anchor = re.compile(
        r'(extern "C" void rs64_m4_y8000_flush\(uint32_t r16\);  /\* fixup: M4 y8000 \*/\n)'
    )
    text, n_decl = decl_anchor.subn(
        lambda m: m.group(1) +
        'extern "C" void rs64_m4_y8000_store(uint32_t r16);  ' + M4_STORE_MARKER + "\n",
        text, count=1)
    store_anchor = re.compile(
        r"(    // sb          \$10, 0x0\(\$16\)\n"
        r"    RSP_MEM_B\(0X0, r16\) = r10;\n)"
    )
    text, n_store = store_anchor.subn(
        lambda m: m.group(1) +
        "    rs64_m4_y8000_store(r16);  " + M4_STORE_MARKER + "\n",
        text, count=1)
    if (n_decl, n_store) != (1, 1):
        print(f"fixup_factor5_ucode: FIXUP 21 ANCHOR FAILED "
              f"(decl={n_decl} store={n_store}).", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Fixup 22: phase-keyed image-task source/field audit (M5 step 7).
# This arm is intentionally isolated to factor5_ucode_b: it records the
# source, transform, writeback, and destination spans without changing the
# microcode's control flow or DMA arguments.
# ---------------------------------------------------------------------------
IMAGE_STAGE_MARKER = "/* fixup: image-stage audit */"
is_image_ucode = "RspExitReason factor5_ucode_b(" in text
if is_image_ucode and IMAGE_STAGE_MARKER not in text:
    decl_anchor = re.compile(r'(#include "librecomp/rsp.hpp"\n)')
    text, n_decl = decl_anchor.subn(
        r'\1extern "C" void rs64_audio_image_stage(uint32_t stage, uint8_t* rdram, '
        r'uint32_t r2, uint32_t field348, uint32_t field44, uint32_t dest);  '
        + IMAGE_STAGE_MARKER + "\n",
        text, count=1)

    def image_stage(pattern, replacement, what):
        global text
        text, count = re.subn(pattern, replacement, text, count=1)
        if count != 1:
            print(f"fixup_factor5_ucode: FIXUP 22 ANCHOR FAILED ({what}): "
                  f"expected 1 substitution, made {count}.", file=sys.stderr)
            sys.exit(1)

    image_stage(
        re.compile(r"(L_1104:\n)"),
        r"\1    rs64_audio_image_stage(0, rdram, r2, RSP_MEM_W_LOAD(0X348, 0), 0, 0);  "
        + IMAGE_STAGE_MARKER + "\n",
        "pre-transform source")
    image_stage(
        re.compile(r"(    r7 = 0 \| 0X6F0;\n)(    goto L_1830;)"),
        r"\1    rs64_audio_image_stage(1, rdram, r2, RSP_MEM_W_LOAD(0X348, 0), 0, 0);  "
        + IMAGE_STAGE_MARKER + r"\n\2",
        "transform output")
    image_stage(
        re.compile(r"(    r7 = 0 \| 0X2FF;\n)(    goto L_13B0;)"),
        r"\1    rs64_audio_image_stage(2, rdram, r2, RSP_MEM_W_LOAD(0X348, 0), "
        r"RSP_MEM_W_LOAD(0X44, r2), r6);  " + IMAGE_STAGE_MARKER + r"\n\2",
        "0x6F0 writeback")
    image_stage(
        re.compile(r"(    r6 = RSP_ADD32\(r6, 0X100\);\n)(    goto L_13B0;)"),
        r"\1    rs64_audio_image_stage(3, rdram, r2, RSP_MEM_W_LOAD(0X348, 0), 0, r6);  "
        + IMAGE_STAGE_MARKER + r"\n\2",
        "0xCB0 writeback")
    if n_decl != 1:
        print("fixup_factor5_ucode: FIXUP 22 ANCHOR FAILED (declaration).", file=sys.stderr)
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
if OVL12_MARKER in text and OVL12_MARKER not in original:
    notes.append("spliced overlay-12 TriGen (OVL12_* labels, id-0xC routing)")
if OVL14_MARKER in text and OVL14_MARKER not in original:
    notes.append("spliced overlay-14 vector loop (OVL14_* labels, id-0x14 routing)")
if OVL18_MARKER in text and OVL18_MARKER not in original:
    notes.append("spliced overlay-18 vector loop (OVL18_* labels, id-0x18 routing)")
if OVL10_MARKER in text and OVL10_MARKER not in original:
    notes.append("spliced overlay-10 vector loop (OVL10_* labels, id-0x10 routing)")
if OVL10_1F40_MARKER in text and OVL10_1F40_MARKER not in original:
    notes.append("routed ovl10 L_15D0 handshake return (0x1F40 / 153==0x10)")
if OVL1C_MARKER in text and OVL1C_MARKER not in original:
    notes.append("spliced overlay-0x1C vector loop (OVL1C_* labels, id-0x1C routing)")
if OVL1C_1E18_MARKER in text and OVL1C_1E18_MARKER not in original:
    notes.append("routed ovl1c jal-return 0x1E18 / 153==0x1C")
if OVL1C_1E2C_MARKER in text and OVL1C_1E2C_MARKER not in original:
    notes.append("routed ovl1c jal-return 0x1E2C / 153==0x1C")
if OVL1C_1F04_MARKER in text and OVL1C_1F04_MARKER not in original:
    notes.append("routed ovl1c 1ED4 trampoline return 0x1F04 / 153==0x1C")
if OVL1C_1E6C_MARKER in text and OVL1C_1E6C_MARKER not in original:
    notes.append("routed ovl1c $30-return 0x1E6C / 153==0x1C")
if OVL1C_1EA8_MARKER in text and OVL1C_1EA8_MARKER not in original:
    notes.append("routed ovl1c $30-return 0x1EA8 / 153==0x1C")
if OVL1C_1EBC_MARKER in text and OVL1C_1EBC_MARKER not in original:
    notes.append("routed ovl1c $30-return 0x1EBC / 153==0x1C")
if OVL1C_1ECC_MARKER in text and OVL1C_1ECC_MARKER not in original:
    notes.append("routed ovl1c $30-return 0x1ECC / 153==0x1C")
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
if M4_Y8000_MARKER in text and M4_Y8000_MARKER not in original:
    notes.append("M4 0x8000-Y emit vs clip-reject census (s1856)")
if IMAGE_STAGE_MARKER in text and IMAGE_STAGE_MARKER not in original:
    notes.append("image-task source/field audit (M5 step 7)")

print(f"fixup_factor5_ucode: {path} — " + ("; ".join(notes) if notes else "updated"), file=sys.stderr)
