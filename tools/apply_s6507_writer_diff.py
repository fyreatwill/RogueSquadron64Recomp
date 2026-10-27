"""s6507: join the keyed writer interval to changed span-table bytes."""
import pathlib

p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
tag = "PATCH: s6507 writer diff"
if tag in t:
    print("already")
    raise SystemExit

needle = "static uint32_t s6505_invocation_key; /* PATCH: s6505 invocation join */\n"
assert t.count(needle) == 1
t = t.replace(needle, needle +
    "static uint32_t s6500_wmask[4], s6505_startmask[4]; /* " + tag + " */\n"
    "static uint8_t* s6505_rdram;\n"
    "static uint32_t s6505_table_diff(uint32_t ri) {\n"
    "    uint8_t* rdram = s6505_rdram;\n"
    "    uint32_t m = 0;\n"
    "    for (uint32_t i = 0; i < 24; i++)\n"
    "        if ((uint8_t)MEM_B(0, (int64_t)(int32_t)(0x80130DB0u + i)) != s6500_tbl[ri][i]) m |= 1u << i;\n"
    "    return m;\n"
    "}\n", 1)

old = "static void s6500_note_writer(uint32_t pc, uint32_t value) {\n"
assert t.count(old) == 1
t = t.replace(old, "static void s6500_note_writer(uint32_t pc, uint32_t value, uint32_t addr) {\n", 1)
old = ("      s6500_wlast[i] = value & 0xffu; s6500_wcount[i]++; }\n}\n")
assert t.count(old) == 1
new = ("      s6500_wlast[i] = value & 0xffu; s6500_wcount[i]++;\n"
       "      if (addr >= 0x80130DB0u && addr < 0x80130DC8u) s6500_wmask[i] |= 1u << (addr - 0x80130DB0u);\n"
       "    }\n}\n")
t = t.replace(old, new, 1)

old = "for (int i = 0; i < 4; i++) s6505_start[i] = s6500_wcount[i];"
assert t.count(old) == 1
t = t.replace(old, old + "\n        for (int i = 0; i < 4; i++) s6505_startmask[i] = s6500_wmask[i];", 1)

for pc, value, addr in (("0x80042DB4u", "ctx->r3", "ctx->r2"),
                        ("0x80042DC0u", "ctx->r3", "ctx->r21"),
                        ("0x80042EBCu", "ctx->r2", "ctx->r19"),
                        ("0x80042EC4u", "ctx->r2", "ctx->r21")):
    old = "s6500_note_writer(" + pc + ", U32(" + value + "));"
    assert t.count(old) >= 1, (pc, old)
    t = t.replace(old, "s6500_note_writer(" + pc + ", U32(" + value + "), U32(" + addr + "));" )

old = ("s6500_wcount[0] - s6505_start[0], s6500_wcount[1] - s6505_start[1], "
       "s6500_wcount[2] - s6505_start[2], s6500_wcount[3] - s6505_start[3], "
       "s6500_wlast[0], s6500_wlast[1], s6500_wlast[2], s6500_wlast[3]);")
assert t.count(old) == 1
new = ("s6500_wcount[0] - s6505_start[0], s6500_wcount[1] - s6505_start[1], "
       "s6500_wcount[2] - s6505_start[2], s6500_wcount[3] - s6505_start[3], "
       "s6500_wlast[0], s6500_wlast[1], s6500_wlast[2], s6500_wlast[3]); "
       "fprintf(stderr, \" diff=%08x masks=%08x,%08x,%08x,%08x interval=%08x,%08x,%08x,%08x\\n\", "
       "s6505_table_diff(ri), s6500_wmask[0], s6500_wmask[1], s6500_wmask[2], s6500_wmask[3], "
       "s6500_wmask[0] ^ s6505_startmask[0], s6500_wmask[1] ^ s6505_startmask[1], "
       "s6500_wmask[2] ^ s6505_startmask[2], s6500_wmask[3] ^ s6505_startmask[3]);")
t = t.replace(old, new, 1)

p.write_text(t)
print("ok")
