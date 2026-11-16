"""s7479 class EG: give EVERY rs_malloc block a canary band.

s7475-s7478 canary summaries show ~80% of rs_malloc blocks have req == rounded size (noslack=9200-10000 of
rec~12500): they carry no slack, so an overrun of their request lands straight in the next block's header/body and
the canary cannot see it. This patch makes the rs_malloc wrapper pass rs64_s7479_pad(_rq) to the inner allocator
(host: _rq + ROGUESQ_S7475_PAD bytes when ROGUESQ_S7475_CANARY=1 and PAD>0, else _rq unchanged), while every hook
after it (spill, s5041, s6063 -> s7475 canary) still sees the ORIGINAL request, so [req, size) is a >=PAD-byte band
for every block. Default (PAD unset/0) is a pure pass-through: no game value changes. Idempotent; mirrored in
fixup_game_funcs_vendored.py's apply list."""
from pathlib import Path
P = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c")
MARK = "PATCH: s7479 mallocpad"
OLD = "rs64_s6127_fl(U32(ctx->r5)); rs_malloc_s5041_inner(rdram, ctx);"
NEW = ("rs64_s6127_fl(U32(ctx->r5)); { extern uint32_t rs64_s7479_pad(uint32_t); ctx->r4 = (int64_t)(int32_t)rs64_s7479_pad(_rq); } /* "
       + MARK + " */ rs_malloc_s5041_inner(rdram, ctx);")
t = P.read_text()
if MARK in t:
    print("s7479 mallocpad already present")
else:
    assert t.count(OLD) == 1, f"s7479 anchor count={t.count(OLD)}"
    P.write_text(t.replace(OLD, NEW, 1)); print("s7479 mallocpad patched")
