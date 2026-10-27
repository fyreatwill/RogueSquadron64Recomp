"""s6493b G1c: on stream-fn return, ROGUESQ_FORFACE_LOG dumps window words 0x80132DB0/B4/B8/BC + 24 table bytes at 0x80130DB0
(first 25 empty returns and first 8 non-empty returns as control). Run after apply_s6493_stream_cum.py. Idempotent."""
import pathlib
p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
TAG = "PATCH: s6493b emptydump"
if TAG in t: print("already"); raise SystemExit
old = "ctx->r2 = ADD32(ctx->r9, 0); g_s6493[ctx->r2 ? 11 : 10]++; /* PATCH: s6493 streamcum */\n"
assert t.count(old) == 1
new = old + r'''    if (getenv("ROGUESQ_FORFACE_LOG")) { static int ne6493 = 0, nn6493 = 0; int emp = (ctx->r2 == 0); if (emp ? (ne6493++ < 25) : (nn6493++ < 8)) {
      int8_t tb[24]; for (int i = 0; i < 24; i++) tb[i] = (int8_t)MEM_B(0, (int64_t)(int32_t)(0x80130DB0 + i));
      fprintf(stderr, "[streamdump] %s w=%d,%d,%d,%d tbl=", emp ? "EMPTY" : "ok", (int)MEM_W(0, (int64_t)(int32_t)0x80132DB0), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB4), (int)MEM_W(0, (int64_t)(int32_t)0x80132DB8), (int)MEM_W(0, (int64_t)(int32_t)0x80132DBC));
      for (int i = 0; i < 24; i++) fprintf(stderr, "%d,", tb[i]); fprintf(stderr, "\n"); } } /* ''' + TAG + " */\n"
t = t.replace(old, new); p.write_text(t); print("ok")
