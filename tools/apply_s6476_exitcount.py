"""s6476 G1c: ROGUESQ_DD_SUBLOG=1 also prints per-exit counts of buildGridCellMesh (0x8004B930).
Exits (all jump to L_8004C294): e0=B990 label-path (flag 0x20&0x40 on cell+0x14), e1=B9CC (cell variant bits&3==0),
e2=BA48 (flag 0x40 set / after mapCellGeometry), e3=BB3C, e4=BB54, e5=BD68 (byte+0x30>=2), e6=BEB0 (byte+0x30!=0), e7=normal fall-through.
Discriminates H-bgcm-gate: which early exit dominates and whether its share differs dd2 vs dd3. Idempotent."""
import re
TAG = "PATCH: s6476 exitcount"
def apply10(text):
    if TAG in text: return text, 0
    start = text.index("RECOMP_FUNC void buildGridCellMesh(uint8_t* rdram, recomp_context* ctx) {")
    end = text.index("L_8004C294:\n", start)
    body = text[start:end]
    k = [0]
    def rep(m):
        i = k[0]; k[0] += 1
        return "%sg_s6476[%d]++; /* %s */\n%s" % (m.group(1), min(i, 6), TAG, m.group(0))
    body2 = re.sub(r"^( *)goto L_8004C294;\n", rep, body, flags=re.M)
    n = k[0]
    tail = "    g_s6476[7]++; /* %s */\n" % TAG
    text = text[:start] + body2 + tail + text[end:]
    first = text.index("RECOMP_FUNC void ")
    text = text[:first] + "uint32_t g_s6476[8]; /* %s */\n" % TAG + text[first:]
    return text, n
OLD = '        for (int i = 0; i < 8; i++) g_s6474[i] = 0; } }\n'
NEW = ('        { extern uint32_t g_s6476[8]; fprintf(stderr, "[exitlog] /30builds e0=%u e1=%u e2=%u e3=%u e4=%u e5=%u e6=%u e7fall=%u /* '
       + TAG + ' */\\n", g_s6476[0], g_s6476[1], g_s6476[2], g_s6476[3], g_s6476[4], g_s6476[5], g_s6476[6], g_s6476[7]);\n'
       '          for (int i = 0; i < 8; i++) g_s6476[i] = 0; }\n')
def apply9(text):
    if TAG in text or "PATCH: s6474 subcount" not in text: return text, 0
    assert text.count(OLD) == 1
    return text.replace(OLD, NEW + OLD), 1
if __name__ == "__main__":
    import pathlib
    base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
    for name, fn in (("funcs_9.c", apply9), ("funcs_10.c", apply10)):
        p = base / name; t = p.read_text(); t2, n = fn(t)
        if n: p.write_text(t2)
        print(name, "x%d" % n)
