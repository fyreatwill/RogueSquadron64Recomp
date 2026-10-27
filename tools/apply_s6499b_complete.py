"""Complete the s6499 span-store census for the two omitted stream stores."""
import pathlib

p = pathlib.Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c")
t = p.read_text()
tag = "PATCH: s6499b complete"
if tag in t:
    print("already")
    raise SystemExit
sites = [
    ("else { MEM_B(0X0, ctx->r21) = ctx->r3;", "s6499_note(U32(ctx->r21), U32(ctx->r3));"),
    ("{ MEM_B(0X0, ctx->r19) = ctx->r2;", "s6499_note(U32(ctx->r19), U32(ctx->r2));"),
]
for old, add in sites:
    count = t.count(old)
    assert count >= 1, (old, count)
    if old.startswith("else {"):
        t = t.replace(old, "else { " + add + " " + old[len("else { "):])
    else:
        t = t.replace(old, "{ " + add + " " + old[2:])
t = t.replace("/* PATCH: s6499 storecensus */\n", "/* PATCH: s6499 storecensus */\n/* " + tag + " */\n", 1)
p.write_text(t)
print("ok")
