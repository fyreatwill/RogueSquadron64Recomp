#!/usr/bin/env python3
"""s7089: remove the duplicated call blocks the s3531 selector-setup-contract patch left in reapplyAudioConfig.

The s3531 block in fixup_game_funcs_vendored.py prepended its replacement to every needle containing "jal",
including the two multi-line needles whose replacement already holds the whole original block. The live
funcs_24.c therefore ran, per reapplyAudioConfig call (retail 0x80091C88, one jal each):
  * initFactor5Mutex twice (osCreateMesgQueue(q,1) + osSendMesg(q,0) on the Factor 5 mutex 0x80149990):
    a thread woken by the first send keeps its token while the second create+send hands out another;
  * osAiSetFrequency twice (same a0, idempotent).
Retail executes each once (objdump 0x80091CAC / 0x80091CB8). This drops the second copy of each block,
leaving the s3531 contract logging in place. The vendored rule is fixed too, so a fresh regen never has it.
Idempotent. Usage: fixup_s7089_dupcall.py <RecompiledFuncs dir>
"""
import pathlib, sys

DUPS = [
    ('    initFactor5Mutex(rdram, ctx);\n',
     '    // 0x80091CAC: jal         0x80091FC4\n'
     '    // 0x80091CB0: addu        $s3, $a2, $zero\n'
     '    ctx->r19 = ADD32(ctx->r6, 0);\n'
     '    initFactor5Mutex(rdram, ctx);\n'),
    ('    rs64_m5_selector_setup_contract("ai-return", 0x80091CBCu, U32(ctx->r31), U32(ctx->r4), U32(ctx->r5), '
     'U32(ctx->r6), U32(ctx->r7), U32(ctx->r16), U32(ctx->r17), U32(ctx->r18), U32(ctx->r2)); '
     '/* PATCH: s3531 selector setup contract */\n',
     '    // 0x80091CB8: jal         0x80029D20\n'
     '    // 0x80091CBC: nop\n'
     '\n'
     '    osAiSetFrequency_recomp(rdram, ctx);\n'),
]


def main():
    base = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "../N64Recomp/RecompiledFuncs")
    p = base / "funcs_24.c"
    t = p.read_text()
    removed = 0
    for lead, block in DUPS:
        bad = lead + block
        n = t.count(bad)
        if n > 1:
            raise SystemExit(f"fixup_s7089_dupcall: {n} copies of a duplicated block, expected <= 1")
        if n == 1:
            t = t.replace(bad, lead, 1)
            removed += 1
    # post-condition: each retail call appears exactly once in reapplyAudioConfig
    i = t.find('RECOMP_FUNC void reapplyAudioConfig(')
    j = t.find('RECOMP_FUNC void ', i + 1)
    body = t[i:j if j > 0 else len(t)]
    for call in ('initFactor5Mutex(rdram, ctx);', 'osAiSetFrequency_recomp(rdram, ctx);'):
        if body.count(call) != 1:
            raise SystemExit(f"fixup_s7089_dupcall: {call} appears {body.count(call)}x in reapplyAudioConfig")
    if removed:
        p.write_text(t)
    print(f"fixup_s7089_dupcall: removed {removed} duplicated block(s); reapplyAudioConfig calls each once")


if __name__ == '__main__':
    main()
