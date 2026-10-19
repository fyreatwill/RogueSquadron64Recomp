"""s5523: log ra/a0..a2 at initMission entry and cinematicLoopBody entry. Idempotent on the LIVE tree; the same
strings are mirrored in fixup_game_funcs_vendored.py for regen (this script also patches that file, idempotently)."""
import pathlib
base = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
OLD = '"[initMission] call#%d B40=0x%02X force=%d\\n", s_n, (unsigned)MEM_BU(0xB40, S32(0X8013 << 16)), s_fs);'
NEW = '"[initMission] call#%d B40=0x%02X force=%d ra=0x%08X a0=0x%08X a1=0x%08X\\n", s_n, (unsigned)MEM_BU(0xB40, S32(0X8013 << 16)), s_fs, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5));'
A = "    // 0x800A5D80: addiu       $sp, $sp, -0xD8\n"
C = ('    { static int s_c = 0; if (s_c++ < 40) { fprintf(stderr, "[cineBody] call#%d ra=0x%08X a0=0x%08X a1=0x%08X a2=0x%08X B40=0x%02X\\n", s_c, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), U32(ctx->r6), (unsigned)MEM_BU(0xB40, S32(0X8013 << 16))); } } /* PATCH: s5523 cineBody entry log */\n')

# live tree
p = base / "funcs_42.c"; t = p.read_text()
if OLD in t:
    p.write_text(t.replace(OLD, NEW, 1)); print("funcs_42 patched")
else:
    print("funcs_42 already/missing", NEW in t)
p = base / "funcs_27.c"; t = p.read_text()
if "s5523 cineBody" in t:
    print("funcs_27 already")
else:
    assert t.count(A) == 1
    p.write_text(t.replace(A, C + A, 1)); print("funcs_27 patched")

# fixup script (source text holds the C strings with one more level of escaping)
def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')
fp = pathlib.Path(__file__).parent / "fixup_game_funcs_vendored.py"
f = fp.read_text()
if "s5523 cineBody" in f:
    print("fixup already")
else:
    o, n = esc(OLD), esc(NEW)
    assert f.count(o) == 1, f.count(o)
    f = f.replace(o, n, 1)
    blk = (
        '    if p.name == "funcs_27.c" and "PATCH: s5523 cineBody entry log" not in text:\n'
        '        _a = ' + repr(A) + '\n'
        '        if text.count(_a) == 1:\n'
        '            _code = ' + repr(C) + '\n'
        '            text = text.replace(_a, _code + _a, 1)\n'
        '            changed = True\n'
        '            report.append(f"{p.name}: s5523 cineBody entry log patched")\n\n')
    anchor = '    if p.name == "funcs_42.c" and "PATCH: s5508 initMission sel" not in text:\n'
    assert f.count(anchor) == 1
    f = f.replace(anchor, blk + anchor, 1)
    fp.write_text(f); print("fixup patched")
