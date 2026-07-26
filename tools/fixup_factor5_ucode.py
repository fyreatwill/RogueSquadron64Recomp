"""Post-process RSPRecomp output for the Factor 5 graphics ucode.

Three fixups, all idempotent. Pass either the main ucode file or the boot
file — fixups self-gate by detecting which file is being processed.

1. Replace `goto L_XXXX;` referring to undefined labels with a clean exit.
   RSPRecomp emits these for relative branches whose targets fall outside
   the recompiled function's PC range. Factor 5's main ucode has one such
   case: a `bgez $2, +0xC` near end-of-IMEM in a perspective-divide block
   whose target wraps past 0x04002000.

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

# ---------------------------------------------------------------------------
# Fixup 1: undefined goto targets → clean exit
# ---------------------------------------------------------------------------
defined_labels = set(re.findall(r"^([A-Za-z_][A-Za-z_0-9]*):\s*$", text, flags=re.MULTILINE))
goto_targets = set(re.findall(r"goto\s+([A-Za-z_][A-Za-z_0-9]*);", text))
undefined = sorted(goto_targets - defined_labels)

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
is_main_ucode = "factor5_ucode(" in text and "factor5_boot(" not in text
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

if text == original:
    sys.exit(0)

path.write_text(text, encoding="utf-8")
notes = []
if undefined:
    notes.append(f"replaced {len(undefined)} undefined goto target(s): {', '.join(undefined)}")
if ITER_MARKER in text and ITER_MARKER not in original:
    notes.append("injected iter cap at L_1090")
if SILENCE_MARKER in text and SILENCE_MARKER not in original:
    notes.append("silenced boot->main JR printf")
if CULL_MARKER in text and CULL_MARKER not in original:
    notes.append("injected cullstats census (ROGUESQ_UCODE_CULLSTATS)")
if OVL_MARKER in text and OVL_MARKER not in original:
    notes.append("injected overlay dispatch trace (ROGUESQ_UCODE_CULLSTATS=2)")

# Make sure <cstdio> is available for the iter-cap fprintf.
if "#include <cstdio>" not in text:
    text = text.replace('#include "librecomp/rsp.hpp"',
                        '#include <cstdio>\n#include "librecomp/rsp.hpp"', 1)
    path.write_text(text, encoding="utf-8")
print(f"fixup_factor5_ucode: {path} — " + "; ".join(notes), file=sys.stderr)
