#!/usr/bin/env python3
"""s7315: retail-side RAM-size / upper-bound idiom census (complements s6862 HEAP-ADDR-AUDIT, which reads host-patch C literals
only, and s6992's 0xFF000000 pointer-mask class). Reads the original MIPS comments in the live RecompiledFuncs tree and lists
every retail instruction that builds a RAM-size-shaped constant with lui (0x003F/0x0040/0x007F/0x0080/0x00FF high halves, or
KSEG0 tops 0x8040..0x8100) and every osMemSize (0x80000318) load. For each site it prints the function, the low-half ori/addiu
that completes the constant, and the first later instruction that consumes the register, then looks the site up in VERDICT.
Exit 1 if a site is unclassified. Usage: tools/s7315_retail_bound_census.py [--all]"""
import pathlib, re, sys

GEN = pathlib.Path(__file__).resolve().parents[2] / "N64Recomp" / "RecompiledFuncs"
INS = re.compile(r"^\s*// (0x[0-9A-F]{8}): (\w+)\s*(.*)$")
FN = re.compile(r"^RECOMP_FUNC void (\w+)\(")
HI = {0x3F, 0x40, 0x7F, 0x80, 0xFF} | set(range(0x8040, 0x8101))
# (function, constant) -> verdict. Constant is the full 32-bit value after the completing ori/addiu (or the lui alone).
VERDICT = {
    ("partitionFramebufferMemory", 0x80400000): "4 MB-mode framebuffer top (flag 0x2000 at *0x8010FCB0+0x44); follows mode, not heap",
    ("partitionFramebufferMemory", "osMemSize"): "framebuffer top = 0x80000000|osMemSize; follows OSMEM_MB (FB stays < 16 MB at OSMEM<=16)",
    ("getUsableRdramSize", 0x00400000): "returns 4 MB when the 4 MB-mode flag is set",
    ("getUsableRdramSize", "osMemSize"): "else returns osMemSize",
    ("resetGameSettingsAndMissionStats", 0x00400000): "settings+0x23 = (usable > 4 MB) expansion-pak flag; true for 8 and 12 MB alike",
    ("applyRgbaTintToMeshVertices", 0x80808081): "divide-by-255 multiply magic, not an address",
    ("buildAndRegisterDefaultMaterial", 0x80808081): "divide-by-255 multiply magic, not an address",
    ("initIdleDemoTimersAndSave", 0x00400000): "same settings+0x23 expansion-pak flag as resetGameSettingsAndMissionStats",
    ("tickAllAudioChannels", 0x00800000): "MusyX 16.16 value 128.0 compared with a channel value, not an address",
    ("tickAllAudioChannels", 0x00400000): "MusyX 16.16 value 64.0 (centre pan) seed, not an address",
    ("computeVoiceVolumePanCoefficients", 0x00800000): "MusyX 16.16 128.0 compare (volume/pan table end), not an address",
    ("requestMissionTransitionMode", 0x00400000): "mission transition flag bit, not an address",
    ("resetMusyXEngineState", 0x003F0000): "MusyX 16.16 volume default 63.0, not an address",
}
AUDIO = ("soundMacro", "seqCmd", "tickAudioChannel", "tickAllAudioChannels", "resetMusyX", "computeVoiceVolumePan",
         "startStreamedSampleVoice")
def rule(fn, c, use):
    """Generic rules for non-address constants; returns a verdict or None."""
    op = use.split()[1] if use else None
    if isinstance(c, str) or c >= 0x80000000: return None
    if op in ("or", "and") and bin(c).count("1") <= 2: return "single/paired flag bit set or tested with or/and, not an address"
    if c in (0x7F0000, 0x3F0000) and fn.startswith(AUDIO): return "MusyX 16.16 volume/pitch limit (127.0/63.0), not an address"
    if c == 0xFF0000: return "byte-field mask/value (DL opcode or 8-bit id in bits 16-23), not an address"
    if (c & 0xFFFF) != 0 and c not in (0x400000, 0x800000): return "small non-size constant (bit field / fixed-point / mask)"
    return None
def const(lui, nxt):
    v = (lui << 16) & 0xFFFFFFFF
    if nxt and nxt[0] == "ori": v |= nxt[1]
    elif nxt and nxt[0] == "addiu": v = (v + (nxt[1] - 0x10000 if nxt[1] & 0x8000 else nxt[1])) & 0xFFFFFFFF
    return v

SELFTEST = """RECOMP_FUNC void s7315FakeHeapBound(uint8_t* rdram, recomp_context* ctx) {
    // 0x80001000: lui         $at, 0x8080
    // 0x80001004: sltu        $v0, $a0, $at
    // 0x80001008: lw          $v1, 0x318($t0)
"""
sites = []
srcs = [(f, f.read_text(errors="replace")) for f in sorted(GEN.glob("funcs_*.c"))]
if "--selftest" in sys.argv: srcs = [("selftest", SELFTEST)]
for f, text in srcs:
    fn, prog = None, []
    for line in text.splitlines():
        m = FN.match(line)
        if m: fn = m.group(1); continue
        m = INS.match(line)
        if m and (not prog or prog[-1][0] != m.group(1)): prog.append((m.group(1), m.group(2), m.group(3), fn))
    for i, (pc, op, args, fn) in enumerate(prog):
        a = [x.strip() for x in args.split(",")]
        if op == "lui" and len(a) == 2:
            imm = int(a[1], 16)
            if imm not in HI: continue
            reg, nxt, use = a[0], None, None
            for pc2, op2, args2, _ in prog[i + 1:i + 12]:
                b = [x.strip() for x in args2.split(",")]
                if op2 in ("ori", "addiu") and len(b) == 3 and b[0] == reg and b[1] == reg and nxt is None:
                    nxt = (op2, int(b[2].replace("-", ""), 16) if not b[2].startswith("-") else (0x10000 - int(b[2][1:], 16)))
                    continue
                if reg in b[1:] or (op2 in ("multu", "mult", "and", "or", "sltu", "slt") and reg in b):
                    use = f"{pc2} {op2} {args2}"; break
                if b and b[0] == reg: break
            sites.append((fn, pc, const(imm, nxt), use))
        elif op == "lw" and a[-1:] and a[-1].startswith("0x318("):
            sites.append((fn, pc, "osMemSize", None))
bad = 0
for fn, pc, c, use in sites:
    key = (fn, c)
    v = VERDICT.get(key)
    if v is None: v = rule(fn, c, use)
    if v is None: bad += 1
    if v is None or "--all" in sys.argv:
        cs = c if isinstance(c, str) else f"0x{c:08X}"
        print(f"{'UNCLASSIFIED' if v is None else 'ok'} {fn} {pc} {cs} use=[{use}] :: {v or ''}")
print(f"sites={len(sites)} unclassified={bad}")
sys.exit(1 if bad else 0)
