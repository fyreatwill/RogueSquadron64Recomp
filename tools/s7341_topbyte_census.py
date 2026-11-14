#!/usr/bin/env python3
"""s7341 class P census: KSEG0 top-byte tests vs dd>1 spill pointers (0x81000000-0x81800000, s7326/s7336).
A test `(p >> 24) == 0x80`, `(p & 0xFF000000) == 0x80000000`, or a mask that keeps bit 24 without the low 24 bits
(`p & 0x01000000`, `p & 0x3F000000`) reads a spill pointer differently from a 0x80xxxxxx one.
Already closed elsewhere, re-checked here as preconditions:
  game shift form `srl/sra d, p, k>=23` reaching a compare = s7317 class A (tools/s7317_field_compare_census.py, 32 sites);
  game `& 0xFF000000 == 0x80000000` = s6993 (tools/apply_s6993_ptrmask.py, 7 sites; this tool requires all 7 patched).
Part 1 HOST: s7338 scope; every top-byte compare (direct, or via a `v = x >> 24` local compared within 8 lines) classed with
  the s7338 C/P/G/D framework, plus W (the s6993 widening itself) and hand classes below. '?' or B => exit 1.
Part 2 GAME: every `and` with a lui/ori constant M where bit 24 is set and the low 24 bits are not all set, in the generated
  RecompiledFuncs. Classed per (function, M) by the provenance of the other operand (hand-read s7341, reasons in GAME):
  F flag word / bitfield of a non-pointer record, K 6-bit packed index bitfield, Q gbi/RDP command word, A arithmetic,
  M RMW flag clear, W s6993-patched pointer test, Z 0xFF00FF00 fill mask. Unclassified => exit 1.
  Second line (s7341): in the s7317 dd8 21:9 L4 holder dump (scratch/s7317/d8_holders_all.txt.gz, 21263 holder words) the
  only spill pointers inside 0x80130B40-0x80130D00 sit at 0x80130BC0/BC4 (+0x80/+0x84), never at the flag words read here.
--controls plants a default-on host test ('?'), a gated one ('G'), an unknown game mask ('?'), and drops one s6993 patch
(precondition must fail)."""
import re, sys, glob, pathlib, importlib.util
from collections import Counter
ROOT = pathlib.Path(__file__).resolve().parents[1]
GEN = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
_s = importlib.util.spec_from_file_location("s7338", ROOT / "tools/s7338_mask_census.py")
m = importlib.util.module_from_spec(_s); _s.loader.exec_module(m)
TEST = re.compile(r">>\s*24\s*\)?\s*[!=<>]=?\s*(?:0x8[01]u?|12[89]u?)\b|0xFF000000u?\s*\)?\s*[!=]=\s*0x8[01]000000u?", re.I)
VAR = re.compile(r"\b(\w+)\s*=\s*[^;]*>>\s*24\s*\)?\s*;")
HOSTCLASS = {  # s7341 hand review
    "rs64_s6993_mask": "W",      # the s6993 widening: returns 0xF0000000 unless ROGUESQ_PTRMASK=0; the compare only picks log lines
    "rs64_s7318_bcmp": "D",      # ROGUESQ_S7318_BCMP probe (s7340 already classed it D)
    "note": "D",                 # s7324_rcp_spill.cpp ROGUESQ_S7324_RCPREF tag histogram
}
WLINE = re.compile(r"rs64_ram_top")

def host_sites(path, pgf):
    m.MASK = TEST
    rows = [r for r in m.sites(path, pgf, HOSTCLASS)]
    lines = path.read_text(errors="replace").splitlines()
    for i, l in enumerate(lines):           # `v = x >> 24;` then `v == 0x80` within 8 lines
        mv = VAR.search(l)
        if not mv: continue
        v = mv.group(1)
        cre = re.compile(r"\b%s\s*[!=<>]=?\s*(?:0x8[01]u?|12[89])\b" % re.escape(v))
        for j in range(i + 1, min(i + 9, len(lines))):
            if cre.search(lines[j]):
                m.MASK = cre
                rows += [r for r in m.sites(path, pgf, HOSTCLASS) if r[0] == j + 1]
                break
    m.MASK = TEST
    out = []
    for (ln, fn, mk, c, text) in rows:
        if c == "?" and WLINE.search(text): c = "W"
        out.append((ln, fn, mk, c, text))
    return out

INS = re.compile(r"^\s*// 0x([0-9A-F]{8}): (\w+)\s+(.*)$")
FNRE = re.compile(r"^RECOMP_FUNC void (\w+)\(")
GAME = {  # (function, mask) -> class. Producer = the other `and` operand (s7341 static read of the generated MIPS).
    ("updateEffectObjectOrientationQuat", 0x01000000): "F",   # game-state record 0x80130B40: lw 0xC(0x80130B40 + 4*idx), flag words (s1811 power-up bits OR onto 0x80130B4C)
    ("updatePlayerCraftPhysics", 0x01000000): "F",            # same 0x80130B40 + 4*idx + 0xC flag word, 7 sites (idx = craft +0xB8 player index)
    ("computeBootConfigScaledVec4", 0x01000000): "F",         # t0 = 0x80130B40 (stored at 0x8004FC74), +0xC flag word
    ("applySaveSlotToMissionState", 0x01000000): "F",         # 0x80130B40 +0x18 = 0x80130B58 flag word (s5467/s5511)
    ("createAccountProfile", 0x01000000): "F",                # same profile +0x18
    ("initDemoPlayState", 0x0100011B): "F",                   # demo-state flag word (stored constant 0x11B bits)
    ("cutsceneDispatchSlotsByFlag", 0xFF000004): "F",         # slot word 0 = kind byte + flag bit 2, compared to 4 (no ptr form)
    ("walkMeshdef0List", 0x3F000000): "K",                    # HOB meshdef link word: 6-bit 1-based indices at bits 24/18/12
    ("loadSkyHorizonHob", 0x3F000000): "K",                   # same HOB link word, srl 22 index
    ("initializeRadar", 0x3F000000): "K",                     # same HOB link word, srl 22 index
    ("appendRdpStateDl", 0x01C00000): "Q",                    # G_SETOTHERMODE field of a command word being built
    ("drawSubtitleText", 0x01C00000): "Q",                    # same othermode field
    ("emitCombinerStateAndPatch", 0x03000000): "A",           # mask of a negu result (combiner select), scalar
    ("submitGfxFrame", 0x03000000): "A",                      # same negu idiom
    ("syncMissionUnlockBitsToSettings", 0xFF8001FF): "M",     # unlock-bit field clear in profile +0xC
    ("dispatchSequencerNoteEvent", 0xFFFF00FF): "M",          # MusyX note byte replace
    ("tickAudioChannel", 0xFFF7FFFF): "M", ("tickAllAudioChannels", 0xFFFBFFFF): "M",
    ("tickAllAudioChannels", 0xFFFF0000): "M", ("tickAllAudioChannels", 0xFFFE0000): "M",   # channel flag table 0x8013D8A4
    ("update3DAudioFrame", 0xFFEFFFFF): "M", ("update3DAudioFrame", 0xFFF7FFFF): "M",
    ("menuOverlayInit", 0xFFDFFFFF): "M",
    ("processSongByHandle", 0x7FFF0000): "M",                 # song handle high half (handle id, not a pointer)
    ("updateNpcEffectIntensity", 0xFFFF0000): "A",            # stack float bits
    ("guMtxL2F", 0xFFFF0000): "A",                            # fixed-point matrix integer halves
}
S6993 = {"relocateSndPointer", "allocTextureTlutBlock", "loadTextureToMemory", "loadAndDecodeTexture",
         "getTextureAttrBySlot", "texPackTlutSlotOrAlloc"}

def game_sites(files):
    rows = []
    for f in files:
        fn, L, prev = "?", [], None
        for l in open(f, errors="replace"):
            mm = FNRE.match(l)
            if mm: fn = mm.group(1)
            mm = INS.match(l)
            if mm and mm.group(1) != prev: L.append((fn,) + mm.groups()); prev = mm.group(1)
        for i, (fn, pc, op, a) in enumerate(L):
            if op != "lui": continue
            r, v = [x.strip() for x in a.split(",")]; M = int(v, 16) << 16
            for j in range(i + 1, min(i + 4, len(L))):
                b = [x.strip() for x in L[j][3].split(",")]
                if L[j][2] == "ori" and b[0] == r and b[1] == r: M |= int(b[2], 16); break
            if not (M >> 24) & 1 or (M & 0xFFFFFF) == 0xFFFFFF: continue
            for k in range(i + 1, min(i + 10, len(L))):
                o, b = L[k][2], [x.strip() for x in L[k][3].split(",")]
                if o == "and" and r in b[1:]:
                    c = GAME.get((fn, M)) or ("W" if M == 0xFF000000 and fn in S6993 else "Z" if M == 0xFF00FF00 else "?")
                    rows.append((pathlib.Path(f).name, fn, pc, M, c)); break
                if b and b[0] == r and o != "ori": break
    return rows

def s6993_patched(files):
    return sum(pathlib.Path(f).read_text(errors="replace").count("PATCH: s6993 ptrmask") for f in files)

def main():
    pgf = m.probe_gate_fns()
    gfiles = sorted(glob.glob(str(GEN / "funcs_*.c")))
    if "--controls" in sys.argv:
        import tempfile
        d = pathlib.Path(tempfile.mkdtemp())
        t = d / "planted.cpp"
        t.write_text("static bool is_ptr(uint32_t a) {\n    return (a >> 24) == 0x80u;\n}\n"
                     "static bool seg_ok(uint32_t a) {\n    const uint32_t hi = a >> 24;\n    return hi != 0x80u;\n}\n"
                     "static void logged(uint32_t a) {\n    if (!log_e9_provenance()) return;\n    if ((a & 0xFF000000u) == 0x80000000u) a = 0;\n}\n")
        got = {(r[1], r[3]) for r in host_sites(t, pgf)}
        assert got == {("is_ptr", "?"), ("seg_ok", "?"), ("logged", "G")}, f"host control failed: {got}"
        g = d / "funcs_ctl.c"
        g.write_text("RECOMP_FUNC void s7341Fake(uint8_t* rdram, recomp_context* ctx) {\n"
                     "    // 0x80001000: lw          $v0, 0x10($a0)\n    // 0x80001004: lui         $v1, 0x100\n"
                     "    // 0x80001008: and         $v0, $v0, $v1\n    // 0x8000100C: beq         $v0, $zero, L_80001020\n}\n")
        gr = game_sites([str(g)])
        assert [r[4] for r in gr] == ["?"], f"game control failed: {gr}"
        assert s6993_patched([str(g)]) != 7, "s6993 precondition control failed"
        print("[s7341] controls: planted host tests '?' (direct + via local), gated 'G', unknown game bit-24 mask '?', "
              "s6993 precondition fails on an unpatched tree")
    rows, seen = [], set()
    for pat in m.HOST:
        for p in sorted(ROOT.glob(pat)):
            if p in seen: continue
            seen.add(p)
            for r in host_sites(p, pgf): rows.append((str(p.relative_to(ROOT)),) + r)
    cc = Counter(r[4] for r in rows)
    print(f"[s7341] class P host sites={len(rows)} files={len(seen)} " + " ".join(f"{k}={v}" for k, v in sorted(cc.items())))
    for r in rows:
        if r[4] not in "CPG" or "-v" in sys.argv: print(f"  {r[4]} {r[0]}:{r[1]} {r[2]} :: {r[5][:110]}")
    gr = game_sites(gfiles)
    gc = Counter(r[4] for r in gr)
    print(f"[s7341] class P game bit-24 masks sites={len(gr)} funcs={len({r[1] for r in gr})} " +
          " ".join(f"{k}={v}" for k, v in sorted(gc.items())))
    if "-v" in sys.argv:
        for r in gr: print(f"  {r[4]} {r[0]}:{r[1]} 0x{r[2]} mask 0x{r[3]:08X}")
    n6993 = s6993_patched(gfiles)
    print(f"[s7341] precondition s6993 ptrmask patched sites={n6993} (need 7)")
    bad = [r for r in rows if r[4] in "?B"]
    gbad = [r for r in gr if r[4] == "?"]
    for r in bad: print(f"  DEFECT/UNCLASSIFIED host {r[0]}:{r[1]} {r[2]} :: {r[5][:120]}")
    for r in gbad: print(f"  DEFECT/UNCLASSIFIED game {r[0]}:{r[1]} 0x{r[2]} mask 0x{r[3]:08X}")
    return 1 if bad or gbad or n6993 != 7 else 0

if __name__ == "__main__":
    sys.exit(main())
