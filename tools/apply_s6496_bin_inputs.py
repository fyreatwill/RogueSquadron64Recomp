"""s6497 G1c: log rasterizer bounds/store range and join them to stream returns.
Run after apply_s6493b_empty_dump.py. Idempotent."""
import pathlib
p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
TAG = "PATCH: s6497 rasterizerbounds"
if TAG in t: print("already"); raise SystemExit
g = "uint32_t g_s6493[16];"
assert t.count(g) == 1
t = t.replace(g, "static float s6496_v[15]; static uint32_t s6496_a0, s6496_n, s6496_tot; static float s6496_div; "
              "static uint32_t s6497_seq, s6497_ret_seq, s6497_first, s6497_last; "
              "static int32_t s6497_x0, s6497_x1, s6497_z0, s6497_z1; /* " + TAG + " */\n" + g, 1)
hdr = "RECOMP_FUNC void binPolygonIntoTerrainGrid(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n"
assert t.count(hdr) == 1
t = t.replace(hdr, hdr + r'''    { s6497_seq++; s6497_first = 0; s6497_last = 0; s6497_x0 = s6497_x1 = s6497_z0 = s6497_z1 = 0; }
    { s6496_a0 = (uint32_t)ctx->r4; for (int i = 0; i < 15; i++) { uint32_t w = (uint32_t)MEM_W(0, (int64_t)(int32_t)(s6496_a0 + 4 * i)); memcpy(&s6496_v[i], &w, 4); }
      uint32_t d = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80136DD0); memcpy(&s6496_div, &d, 4); s6496_n++; s6496_tot++; } /* ''' + TAG + " */\n", 1)
old = "    // 0x800429C0: addu        $a1, $zero, $zero\n"
assert t.count(old) == 1
t = t.replace(old, r'''    { s6497_x0 = (int32_t)MEM_W(0, (int64_t)(int32_t)0x80132DB0); s6497_x1 = (int32_t)MEM_W(0, (int64_t)(int32_t)0x80132DB4); s6497_z0 = (int32_t)MEM_W(0, (int64_t)(int32_t)0x80132DB8); s6497_z1 = (int32_t)MEM_W(0, (int64_t)(int32_t)0x80132DBC); } /* ''' + TAG + " */\n" + old, 1)
old = "int8_t tb[24]; for (int i = 0; i < 24; i++) tb[i] = (int8_t)MEM_B(0, (int64_t)(int32_t)(0x80130DB0 + i));\n"
assert t.count(old) == 1
t = t.replace("    // 0x80042A74: sb          $a2, 0x0($v1)\n",
              "    // 0x80042A74: sb          $a2, 0x0($v1)\n"
              "    { if (!s6497_first) s6497_first = U32(ctx->r3); s6497_last = U32(ctx->r3); } /* " + TAG + " */\n", 1)
t = t.replace("    // 0x80042A78: sb          $a2, 0x0($v0)\n",
              "    // 0x80042A78: sb          $a2, 0x0($v0)\n"
              "    { if (!s6497_first) s6497_first = U32(ctx->r2); s6497_last = U32(ctx->r2); } /* " + TAG + " */\n", 1)
t = t.replace("    ctx->r2 = ADD32(ctx->r9, 0); g_s6493[ctx->r2 ? 11 : 10]++; /* PATCH: s6493 streamcum */\n",
              "    ctx->r2 = ADD32(ctx->r9, 0); s6497_ret_seq = s6497_seq; g_s6493[ctx->r2 ? 11 : 10]++; /* PATCH: s6493 streamcum */\n", 1)
t = t.replace(old, old + r'''      fprintf(stderr, "[streamdump] %s seq=%u ret=%u bounds=%d,%d,%d,%d stores=%08x..%08x w=%d,%d,%d,%d tbl=", emp ? "EMPTY" : "ok", s6497_seq, s6497_ret_seq, s6497_x0, s6497_x1, s6497_z0, s6497_z1, s6497_first, s6497_last, (int)MEM_W(0, (int64_t)(int32_t)0x80132DB0), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB4), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB8), (int)MEM_W(0, (int64_t)(int32_t)0x80132DBC));
''', 1)
p.write_text(t); print("ok")
