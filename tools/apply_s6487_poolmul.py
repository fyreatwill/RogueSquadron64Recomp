"""s6487 G1c: ROGUESQ_POOLMUL=<k> multiplies the row count n passed to allocAndInitDoublyLinkedNodePool12 (0x80041EF0) by k in
load_level_hmp (0x80044554). Discriminates H-pool-exhaustion (flood-fill/list nodes run out at dd>1 -> link==FFFF) from H-data.
Default (unset) is retail. ORIGIN: diagnostic lever, no mitigation. Idempotent."""
TAG = "PATCH: s6487 poolmul"
OLD = '''    // 0x80044554: jal         0x80041EF0
    // 0x80044558: addu        $a0, $a0, $v0
    ctx->r4 = ADD32(ctx->r4, ctx->r2);
    allocAndInitDoublyLinkedNodePool12(rdram, ctx);'''
NEW = '''    // 0x80044554: jal         0x80041EF0
    // 0x80044558: addu        $a0, $a0, $v0
    ctx->r4 = ADD32(ctx->r4, ctx->r2);
    { /* ''' + TAG + ''' */ static int pm = -1; if (pm < 0) { const char* e = getenv("ROGUESQ_POOLMUL"); pm = (e && e[0]) ? atoi(e) : 1; if (pm < 1) pm = 1; }
      if (pm > 1) { uint32_t n0 = (uint32_t)ctx->r4, n1 = n0 * (uint32_t)pm; if (n1 > 0xFFFE) n1 = 0xFFFE; ctx->r4 = (int32_t)n1; fprintf(stderr, "[poolmul] n %u -> %u\\n", n0, n1); } }
    allocAndInitDoublyLinkedNodePool12(rdram, ctx);'''
def apply9(t):
    if TAG in t or OLD not in t: return t, 0
    assert t.count(OLD) == 1
    return t.replace(OLD, NEW), 1
