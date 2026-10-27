"""s6517: log the terrain-grid descriptor (0x80136DC0 +0/+4) and its header (0x80136FC4) at every keyed
streamTerrainGridCellsByDistance entry, and every store the level loader makes to the descriptor (0x80043E58/E64).
Observation only; answers which load set the table base the EMPTY pass reads.
"""
from pathlib import Path

P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
T = P.read_text()
MARK = "PATCH: s6517 desc owner"
if MARK in T:
    print("s6517 already applied")
    raise SystemExit(0)


def rep(old, new, expect=1):
    global T
    n = T.count(old)
    assert n == expect, (old[:80], n)
    T = T.replace(old, new)


rep(
    "        s6505_key = __atomic_add_fetch(&s6505_invocation_key, 1u, __ATOMIC_RELAXED);\n",
    "        s6505_key = __atomic_add_fetch(&s6505_invocation_key, 1u, __ATOMIC_RELAXED);\n"
    "        fprintf(stderr, \"[desc-ent] key=%u d0=%08X d4=%08X hdr=%08X hdr1C=%08X a0=%08X ra=%08X\\n\", s6505_key, (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80136DC0u), (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80136DC4u), (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80136FC4u), (uint32_t)MEM_W(0x1C, (int64_t)(int32_t)(uint32_t)MEM_W(0, (int64_t)(int32_t)0x80136FC4u)), (uint32_t)ctx->r4, (uint32_t)ctx->r31); /* " + MARK + " */\n",
)
rep(
    "    { MEM_W(0X4, ctx->r4) = ctx->r2; RS64_S5798_ST(0x80043E64u, 0X4, ctx->r4, 4); }\n",
    "    { MEM_W(0X4, ctx->r4) = ctx->r2; RS64_S5798_ST(0x80043E64u, 0X4, ctx->r4, 4); }\n"
    "    fprintf(stderr, \"[desc-st] pc=80043E64 fn=%s d0=%08X d4=%08X hdr=%08X ra=%08X key=%u\\n\", __func__, (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80136DC0u), (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80136DC4u), (uint32_t)ctx->r3, (uint32_t)ctx->r31, (unsigned)__atomic_load_n(&s6505_invocation_key, __ATOMIC_RELAXED)); /* " + MARK + " */\n",
)
P.write_text(T)
print("s6517 applied")
