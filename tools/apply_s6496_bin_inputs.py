"""s6496 G1c: log binPolygonIntoTerrainGrid inputs. Records the last polygon (5 verts x 3 floats @ a0, stride 0xC), the
divisor 0x80136DD0 and the number of bin calls since the previous stream-fn return; prints it on every [streamdump] line.
Run after apply_s6493b_empty_dump.py. Idempotent."""
import pathlib
p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
TAG = "PATCH: s6496 bininputs"
if TAG in t: print("already"); raise SystemExit
g = "uint32_t g_s6493[16];"
assert t.count(g) == 1
t = t.replace(g, "static float s6496_v[15]; static uint32_t s6496_a0, s6496_n, s6496_tot; static float s6496_div; /* " + TAG + " */\n" + g, 1)
hdr = "RECOMP_FUNC void binPolygonIntoTerrainGrid(uint8_t* rdram, recomp_context* ctx) {\n    uint64_t hi = 0, lo = 0, result = 0;\n"
assert t.count(hdr) == 1
t = t.replace(hdr, hdr + r'''    { s6496_a0 = (uint32_t)ctx->r4; for (int i = 0; i < 15; i++) { uint32_t w = (uint32_t)MEM_W(0, (int64_t)(int32_t)(s6496_a0 + 4 * i)); memcpy(&s6496_v[i], &w, 4); }
      uint32_t d = (uint32_t)MEM_W(0, (int64_t)(int32_t)0x80136DD0); memcpy(&s6496_div, &d, 4); s6496_n++; s6496_tot++; } /* ''' + TAG + " */\n", 1)
old = "int8_t tb[24]; for (int i = 0; i < 24; i++) tb[i] = (int8_t)MEM_B(0, (int64_t)(int32_t)(0x80130DB0 + i));\n"
assert t.count(old) == 1
t = t.replace(old, old + r'''      fprintf(stderr, "[binin] nbin=%u tot=%u div=%g a0=%08x v=", s6496_n, s6496_tot, s6496_div, s6496_a0); for (int i = 0; i < 15; i++) fprintf(stderr, "%g,", s6496_v[i]); fprintf(stderr, "\n"); s6496_n = 0; /* ''' + TAG + " */\n", 1)
p.write_text(t); print("ok")
