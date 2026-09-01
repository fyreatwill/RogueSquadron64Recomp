"""Add the regeneration-safe allocation-edge witness for the selector path."""
from pathlib import Path


TARGET = Path("/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_23.c")
MARKER = "PATCH: s3528 selector allocation edge"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if MARKER in text:
        print("apply_s3528: already present")
        return
    decl = ('extern void rs64_m5_selector_alloc_edge(const char* stage, uint32_t pc, '
            'uint32_t a0, uint32_t a1, uint32_t a2, uint32_t a3, uint32_t v0, '
            'uint32_t s0, uint32_t s1, uint32_t s2);\n')
    include = '#include "funcs.h"\n'
    if text.count(include) != 1:
        raise SystemExit("apply_s3528: funcs.h anchor count != 1")
    text = text.replace(include, include + decl, 1)
    start = text.index("RECOMP_FUNC void allocateSongChannelArray(")
    end = text.find("\nRECOMP_FUNC ", start + 1)
    if end < 0:
        end = len(text)
    body = text[start:end]
    pcs = ["8008F0D0", "8008F210", "8008F23C"]
    for i, pc in enumerate(pcs):
        call = "    rs_malloc(rdram, ctx);\n"
        if body.count(call) <= i:
            raise SystemExit(f"apply_s3528: allocation anchor {i} missing")
        pos = body.find(call)
        for _ in range(i):
            pos = body.find(call, pos + len(call))
        pre = (f'    rs64_m5_selector_alloc_edge("pre{i}", 0x{pc}u, U32(ctx->r4), '
               'U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r2), '
               'U32(ctx->r16), U32(ctx->r17), U32(ctx->r18)); '
               f'/* {MARKER} */\n')
        body = body[:pos] + pre + body[pos:]
        after_label = f"    after_{i}:\n"
        if body.count(after_label) != 1:
            raise SystemExit(f"apply_s3528: after label {i} count != 1")
        post = (f'    rs64_m5_selector_alloc_edge("post{i}", 0x{pc}u, U32(ctx->r4), '
                'U32(ctx->r5), U32(ctx->r6), U32(ctx->r7), U32(ctx->r2), '
                'U32(ctx->r16), U32(ctx->r17), U32(ctx->r18)); '
                f'/* {MARKER} */\n')
        body = body.replace(after_label, after_label + post, 1)
    TARGET.write_text(text[:start] + body + text[end:], encoding="utf-8")
    print("apply_s3528: inserted allocation-edge witness x6")


if __name__ == "__main__":
    main()
