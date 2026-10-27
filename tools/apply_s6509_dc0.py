"""s6509: classify every live 0x80042DC0 target/value in the keyed probe."""
import pathlib
import re

p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
tag = "PATCH: s6509 DC0 legitimacy"
if tag in t:
    if "s6509_addr = U32(ctx->r21)" in t:
        print("already")
        raise SystemExit
    if "U32(ctx->r5)" in t and "s6500_note_writer(0x80042DC0u" in t:
        t = re.sub(r'      if \(pc == 0x80042DC0u && getenv\("ROGUESQ_FORFACE_LOG"\)\) \{.*?      \}\n', '', t, count=1, flags=re.S)
        call = 's6500_note_writer(0x80042DC0u, U32(ctx->r3), U32(ctx->r21));'
        probe = '''{ uint32_t s6509_addr = U32(ctx->r21); uint32_t s6509_idx = (s6509_addr >= 0x80130DB0u && s6509_addr < 0x80130DC8u) ? (s6509_addr - 0x80130DB0u) : 0xFFFFFFFFu;
        if (getenv("ROGUESQ_FORFACE_LOG") && s6509_dc0_n < 512u) fprintf(stderr, "[dc0-store] n=%u addr=0x%08X value=0x%02X index=%s%u span_mode=%s base=0x%08X row=%u inner=%u rowoff=%u spanbase=0x%08X recon=0x%08X\\n", s6509_dc0_n, s6509_addr, U32(ctx->r3) & 0xffu, s6509_idx == 0xFFFFFFFFu ? "OUT:" : "", s6509_idx == 0xFFFFFFFFu ? s6509_addr : s6509_idx, (getenv("ROGUESQ_DRAW_DISTANCE") && atof(getenv("ROGUESQ_DRAW_DISTANCE")) != 1.0) ? "active_accept" : "disabled", U32(ctx->r5), (unsigned)U32(ctx->r30), (unsigned)U32(ctx->r20), (unsigned)(U32(ctx->r30) << 6), U32(ctx->r14), U32(ADD32(ctx->r5, ctx->r14))); s6509_dc0_n++; } }
      ''' + call
        assert t.count(call) == 2
        p.write_text(t.replace(call, probe))
        print("repaired")
        raise SystemExit
    old = 'fprintf(stderr, "[dc0-store] n=%u addr=0x%08X value=0x%02X index=%s%u span_mode=%s\\n", s6509_dc0_n, addr, value & 0xffu, idx == 0xFFFFFFFFu ? "OUT:" : "", idx == 0xFFFFFFFFu ? addr : idx, (getenv("ROGUESQ_DRAW_DISTANCE") && atof(getenv("ROGUESQ_DRAW_DISTANCE")) != 1.0) ? "active_accept" : "disabled");'
    new = 'fprintf(stderr, "[dc0-store] n=%u addr=0x%08X value=0x%02X index=%s%u span_mode=%s base=0x%08X row=%u inner=%u rowoff=%u spanbase=0x%08X recon=0x%08X\\n", s6509_dc0_n, addr, value & 0xffu, idx == 0xFFFFFFFFu ? "OUT:" : "", idx == 0xFFFFFFFFu ? addr : idx, (getenv("ROGUESQ_DRAW_DISTANCE") && atof(getenv("ROGUESQ_DRAW_DISTANCE")) != 1.0) ? "active_accept" : "disabled", U32(ctx->r5), (unsigned)U32(ctx->r30), (unsigned)U32(ctx->r20), (unsigned)(U32(ctx->r30) << 6), U32(ctx->r14), U32(ADD32(ctx->r5, ctx->r14)));'
    assert t.count(old) == 1
    t = t.replace(old, new, 1)
    helper = '''      if (pc == 0x80042DC0u && getenv("ROGUESQ_FORFACE_LOG")) {
        uint32_t idx = (addr >= 0x80130DB0u && addr < 0x80130DC8u) ? (addr - 0x80130DB0u) : 0xFFFFFFFFu;
        if (s6509_dc0_n < 512u) fprintf(stderr, "[dc0-store] n=%u addr=0x%08X value=0x%02X index=%s%u span_mode=%s base=0x%08X row=%u inner=%u rowoff=%u spanbase=0x%08X recon=0x%08X\\n", s6509_dc0_n, addr, value & 0xffu, idx == 0xFFFFFFFFu ? "OUT:" : "", idx == 0xFFFFFFFFu ? addr : idx, (getenv("ROGUESQ_DRAW_DISTANCE") && atof(getenv("ROGUESQ_DRAW_DISTANCE")) != 1.0) ? "active_accept" : "disabled", U32(ctx->r5), (unsigned)U32(ctx->r30), (unsigned)U32(ctx->r20), (unsigned)(U32(ctx->r30) << 6), U32(ctx->r14), U32(ADD32(ctx->r5, ctx->r14)));
        s6509_dc0_n++;
      }
'''
    assert t.count(helper) == 1
    t = t.replace(helper, "", 1)
    call = 's6500_note_writer(0x80042DC0u, U32(ctx->r3), U32(ctx->r21));'
    probe = '''{ uint32_t s6509_addr = U32(ctx->r21); uint32_t s6509_idx = (s6509_addr >= 0x80130DB0u && s6509_addr < 0x80130DC8u) ? (s6509_addr - 0x80130DB0u) : 0xFFFFFFFFu;
        if (getenv("ROGUESQ_FORFACE_LOG") && s6509_dc0_n < 512u) fprintf(stderr, "[dc0-store] n=%u addr=0x%08X value=0x%02X index=%s%u span_mode=%s base=0x%08X row=%u inner=%u rowoff=%u spanbase=0x%08X recon=0x%08X\\n", s6509_dc0_n, s6509_addr, U32(ctx->r3) & 0xffu, s6509_idx == 0xFFFFFFFFu ? "OUT:" : "", s6509_idx == 0xFFFFFFFFu ? s6509_addr : s6509_idx, (getenv("ROGUESQ_DRAW_DISTANCE") && atof(getenv("ROGUESQ_DRAW_DISTANCE")) != 1.0) ? "active_accept" : "disabled", U32(ctx->r5), (unsigned)U32(ctx->r30), (unsigned)U32(ctx->r20), (unsigned)(U32(ctx->r30) << 6), U32(ctx->r14), U32(ADD32(ctx->r5, ctx->r14))); s6509_dc0_n++; } }
      ''' + call
    assert t.count(call) == 2
    t = t.replace(call, probe)
    p.write_text(t)
    print("updated")
    raise SystemExit

needle = "static uint32_t s6500_wmask[4], s6505_startmask[4]; /* PATCH: s6507 writer diff */\n"
assert t.count(needle) == 1
t = t.replace(needle, needle +
    "static uint32_t s6509_dc0_n; /* " + tag + " */\n", 1)

old = "      if (addr >= 0x80130DB0u && addr < 0x80130DC8u) s6500_wmask[i] |= 1u << (addr - 0x80130DB0u);\n"
assert t.count(old) == 1
new = old
t = t.replace(old, new, 1)
call = 's6500_note_writer(0x80042DC0u, U32(ctx->r3), U32(ctx->r21));'
probe = '''{ uint32_t s6509_addr = U32(ctx->r21); uint32_t s6509_idx = (s6509_addr >= 0x80130DB0u && s6509_addr < 0x80130DC8u) ? (s6509_addr - 0x80130DB0u) : 0xFFFFFFFFu;
        if (getenv("ROGUESQ_FORFACE_LOG") && s6509_dc0_n < 512u) fprintf(stderr, "[dc0-store] n=%u addr=0x%08X value=0x%02X index=%s%u span_mode=%s base=0x%08X row=%u inner=%u rowoff=%u spanbase=0x%08X recon=0x%08X\\n", s6509_dc0_n, s6509_addr, U32(ctx->r3) & 0xffu, s6509_idx == 0xFFFFFFFFu ? "OUT:" : "", s6509_idx == 0xFFFFFFFFu ? s6509_addr : s6509_idx, (getenv("ROGUESQ_DRAW_DISTANCE") && atof(getenv("ROGUESQ_DRAW_DISTANCE")) != 1.0) ? "active_accept" : "disabled", U32(ctx->r5), (unsigned)U32(ctx->r30), (unsigned)U32(ctx->r20), (unsigned)(U32(ctx->r30) << 6), U32(ctx->r14), U32(ADD32(ctx->r5, ctx->r14))); s6509_dc0_n++; } }
      ''' + call
assert t.count(call) == 2
t = t.replace(call, probe)
p.write_text(t)
print("ok")
