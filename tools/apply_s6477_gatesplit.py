"""s6477 G1c: split the buildGridCellMesh e3 gate (0x8004BB18 link==0xFFFF vs 0x8004BB34 type!=1) and record
cell+0x1E / link / type per class (min/max + first 12 distinct cell+0x1E values). Printed with the s6476 exitlog. Idempotent."""
TAG = "PATCH: s6477 gatesplit"
P = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_10.c"
HELP = '''/* %s */
uint32_t g_s6477_n[3]; uint32_t g_s6477_min[3] = {0xFFFFFFFFu,0xFFFFFFFFu,0xFFFFFFFFu}, g_s6477_max[3];
uint32_t g_s6477_pmin[3] = {0xFFFFFFFFu,0xFFFFFFFFu,0xFFFFFFFFu}, g_s6477_pmax[3];\nuint32_t g_s6477_v[3][12]; uint32_t g_s6477_vn[3]; uint32_t g_s6477_t[3]; uint32_t g_s6477_l[3];
void rs64_s6477_note(int k, uint32_t idx, uint32_t link, uint32_t type, uint32_t ptr) {
    g_s6477_n[k]++; if (ptr < g_s6477_pmin[k]) g_s6477_pmin[k] = ptr; if (ptr > g_s6477_pmax[k]) g_s6477_pmax[k] = ptr; if (idx < g_s6477_min[k]) g_s6477_min[k] = idx; if (idx > g_s6477_max[k]) g_s6477_max[k] = idx;
    g_s6477_t[k] = type; g_s6477_l[k] = link;
    for (uint32_t i = 0; i < g_s6477_vn[k]; i++) if (g_s6477_v[k][i] == idx) return;
    if (g_s6477_vn[k] < 12) g_s6477_v[k][g_s6477_vn[k]++] = idx;
}
''' % TAG
A = "            goto L_8004BB3C;\n    }\n    // 0x8004BB1C: sll         $v0, $a1, 1"
B = "    // 0x8004BB34: beq         $v1, $v0, L_8004BB44\n    if (ctx->r3 == ctx->r2) {"
def apply10(t):
    if TAG in t or "PATCH: s6476 exitcount" not in t: return t, 0
    assert t.count(A) == 1 and t.count(B) == 1
    t = t.replace(A, "            rs64_s6477_note(0, ctx->r3, ctx->r5, 0, ctx->r21); /* %s */\n" % TAG + A)
    t = t.replace(B, "    rs64_s6477_note(ctx->r3 == ctx->r2 ? 2 : 1, MEM_HU(ctx->r21, 0X1E), ctx->r5, ctx->r3, ctx->r21); /* %s */\n" % TAG + B)
    first = t.index("RECOMP_FUNC void ")
    return t[:first] + HELP + t[first:], 1
OLD = '        for (int i = 0; i < 8; i++) g_s6476[i] = 0; }\n'
NEW = ('''        { extern uint32_t g_s6477_n[3],g_s6477_min[3],g_s6477_max[3],g_s6477_v[3][12],g_s6477_vn[3],g_s6477_t[3],g_s6477_l[3],g_s6477_pmin[3],g_s6477_pmax[3]; /* ''' + TAG + ''' */
          const char* nm[3]={"BB18link=FFFF","BB34type!=1","pass"};
          for (int k=0;k<3;k++){ fprintf(stderr,"[gatelog] %s n=%u idx[min=%u max=%u] last link=%u type=%u cellptr[min=%08x max=%08x] vals:",nm[k],g_s6477_n[k],g_s6477_min[k],g_s6477_max[k],g_s6477_l[k],g_s6477_t[k],g_s6477_pmin[k],g_s6477_pmax[k]);
            for(uint32_t i=0;i<g_s6477_vn[k];i++) fprintf(stderr," %u",g_s6477_v[k][i]); fprintf(stderr,"\\n");
            g_s6477_n[k]=0; g_s6477_min[k]=0xFFFFFFFFu; g_s6477_max[k]=0; g_s6477_vn[k]=0; g_s6477_pmin[k]=0xFFFFFFFFu; g_s6477_pmax[k]=0; } }
''')
def apply9(t):
    if TAG in t or "PATCH: s6476 exitcount" not in t: return t, 0
    assert t.count(OLD) == 1
    return t.replace(OLD, NEW + OLD), 1
