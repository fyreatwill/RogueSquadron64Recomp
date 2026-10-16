#!/usr/bin/env python3
"""s5046: undo the s5041 free-census / s5042 free-poison hooks in generated funcs_0.c (rs_malloc wrap, rs_free calls).
Used to test whether those compiled-in (env-off) hooks regressed the keyed title->hangar route. The apply_* scripts
stay in tools/ but are dropped from RS64_REPLAY so a regen does not reintroduce them. Idempotent."""
from pathlib import Path
R = Path(__file__).resolve().parents[1]
p = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c")
s = p.read_text()
for l in ['    rs64_s5042_poison(rdram, U32(ctx->r4), U32(ctx->r31)); /* PATCH: s5042 free poison */\n',
          '    rs64_s5041_free(U32(ctx->r4), U32(ctx->r31)); /* PATCH: s5041 free census */\n',
          'extern void rs64_s5042_poison(uint8_t*, uint32_t, uint32_t);\n',
          'extern void rs64_s5041_free(uint32_t, uint32_t);\nextern void rs64_s5041_malloc(uint32_t);\n']:
    s = s.replace(l, '')
a = ("RECOMP_FUNC void rs_malloc_s5041_inner(uint8_t* rdram, recomp_context* ctx);\n"
     "RECOMP_FUNC void rs_malloc(uint8_t* rdram, recomp_context* ctx) { rs_malloc_s5041_inner(rdram, ctx); rs64_s5041_malloc(U32(ctx->r2)); } /* PATCH: s5041 malloc wrap */\n"
     "RECOMP_FUNC void rs_malloc_s5041_inner(uint8_t* rdram, recomp_context* ctx) {\n")
s = s.replace(a, "RECOMP_FUNC void rs_malloc(uint8_t* rdram, recomp_context* ctx) {\n")
p.write_text(s)
f = R / "tools/fixup_game_funcs_vendored.py"
t = f.read_text()
for n in ['    "apply_s5041_free_census.py",\n', '    "apply_s5042_free_poison.py",\n']:
    t = t.replace(n, '')
f.write_text(t)
print("ok")
