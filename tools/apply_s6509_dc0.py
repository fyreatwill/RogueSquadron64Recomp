"""s6509: classify every live 0x80042DC0 target/value in the keyed probe."""
import pathlib

p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
tag = "PATCH: s6509 DC0 legitimacy"
if tag in t:
    old = 'fprintf(stderr, "[dc0-store] n=%u addr=0x%08X value=0x%02X index=%s%u span_accept=1\\n", s6509_dc0_n, addr, value & 0xffu, idx == 0xFFFFFFFFu ? "OUT:" : "", idx == 0xFFFFFFFFu ? addr : idx);'
    new = 'fprintf(stderr, "[dc0-store] n=%u addr=0x%08X value=0x%02X index=%s%u span_mode=%s\\n", s6509_dc0_n, addr, value & 0xffu, idx == 0xFFFFFFFFu ? "OUT:" : "", idx == 0xFFFFFFFFu ? addr : idx, (getenv("ROGUESQ_DRAW_DISTANCE") && atof(getenv("ROGUESQ_DRAW_DISTANCE")) != 1.0) ? "active_accept" : "disabled");'
    assert t.count(old) == 1
    p.write_text(t.replace(old, new, 1))
    print("updated")
    raise SystemExit

needle = "static uint32_t s6500_wmask[4], s6505_startmask[4]; /* PATCH: s6507 writer diff */\n"
assert t.count(needle) == 1
t = t.replace(needle, needle +
    "static uint32_t s6509_dc0_n; /* " + tag + " */\n", 1)

old = "      if (addr >= 0x80130DB0u && addr < 0x80130DC8u) s6500_wmask[i] |= 1u << (addr - 0x80130DB0u);\n"
assert t.count(old) == 1
new = old + (
    "      if (pc == 0x80042DC0u && getenv(\"ROGUESQ_FORFACE_LOG\")) {\n"
    "        uint32_t idx = (addr >= 0x80130DB0u && addr < 0x80130DC8u) ? (addr - 0x80130DB0u) : 0xFFFFFFFFu;\n"
    "        if (s6509_dc0_n < 512u) fprintf(stderr, \"[dc0-store] n=%u addr=0x%08X value=0x%02X index=%s%u span_mode=%s\\n\", s6509_dc0_n, addr, value & 0xffu, idx == 0xFFFFFFFFu ? \"OUT:\" : \"\", idx == 0xFFFFFFFFu ? addr : idx, (getenv(\"ROGUESQ_DRAW_DISTANCE\") && atof(getenv(\"ROGUESQ_DRAW_DISTANCE\")) != 1.0) ? \"active_accept\" : \"disabled\");\n"
    "        s6509_dc0_n++;\n"
    "      }\n"
)
t = t.replace(old, new, 1)
p.write_text(t)
print("ok")
