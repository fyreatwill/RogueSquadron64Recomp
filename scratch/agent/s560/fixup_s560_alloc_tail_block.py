# s560: residual freelist-walk GUARD3+GUARD4 systematic audit (item -342).
    # s559 closed GUARD3-without-GUARD4 (16 sites). Fresh grep of the same
    # walk-to-tail loop shape (L: v1=*v1; v0=*v1; bne L) found 118 total:
    # 20 already had GUARD3 (heapWalker/emit-dl/heaplistdeq/scene-node), 97
    # residual shape-matched and not already covered by another family.
    # Originally 98 residual; pruned to 97 after excluding drainMesh/reserveAndEmit/scene-node already-guarded layers. 88/98 sit immediately after
    # findAndUnlinkSmallestEntry -- the same inlined "walk allocated-node
    # next-chain to tail then splice freelist" idiom s133/s131 guarded only
    # inside emitAllocatedDLCommand + submitSceneNodeRender. Bail = each
    # site's outer null-check label (same degrade as GUARD2/3 in emit-dl:
    # skip the splice, do not write through a bad walk pointer).
    # Env: ROGUESQ_LOG_ALLOC_TAIL_GUARD3 / ROGUESQ_LOG_ALLOC_TAIL_GUARD4.
    _alloc_tail_walk_sites = [
        ("funcs_3.c", "0x800079B8", "L_800079B8", "0x800079BC", "L_800079E8"),
        ("funcs_3.c", "0x80007D10", "L_80007D10", "0x80007D14", "L_80007D40"),
        ("funcs_3.c", "0x80007E90", "L_80007E90", "0x80007E94", "L_80007EC0"),
        ("funcs_3.c", "0x80007F50", "L_80007F50", "0x80007F54", "L_80007F80"),
        ("funcs_3.c", "0x80008010", "L_80008010", "0x80008014", "L_80008040"),
        ("funcs_3.c", "0x800080D0", "L_800080D0", "0x800080D4", "L_80008100"),
        ("funcs_3.c", "0x800081A8", "L_800081A8", "0x800081AC", "L_800081DC"),
        ("funcs_3.c", "0x800081FC", "L_800081FC", "0x80008200", "L_8000822C"),
        ("funcs_3.c", "0x80008244", "L_80008244", "0x80008248", "L_80008278"),
        ("funcs_3.c", "0x800082A4", "L_800082A4", "0x800082A8", "L_800082D4"),
        ("funcs_3.c", "0x800082F4", "L_800082F4", "0x800082F8", "L_80008328"),
        ("funcs_3.c", "0x8000846C", "L_8000846C", "0x80008470", "L_8000849C"),
        ("funcs_3.c", "0x80008F5C", "L_80008F5C", "0x80008F60", "L_80008F8C"),
        ("funcs_3.c", "0x80009070", "L_80009070", "0x80009074", "L_800090A0"),
        ("funcs_3.c", "0x800091A0", "L_800091A0", "0x800091A4", "L_800091D0"),
        ("funcs_3.c", "0x800092BC", "L_800092BC", "0x800092C0", "L_800092EC"),
        ("funcs_3.c", "0x80009408", "L_80009408", "0x8000940C", "L_80009438"),
        ("funcs_3.c", "0x80009558", "L_80009558", "0x8000955C", "L_80009588"),
        ("funcs_3.c", "0x80009680", "L_80009680", "0x80009684", "L_800096B0"),
        ("funcs_3.c", "0x800097A0", "L_800097A0", "0x800097A4", "L_800097D0"),
        ("funcs_3.c", "0x800098C8", "L_800098C8", "0x800098CC", "L_800098F8"),
        ("funcs_3.c", "0x80009A04", "L_80009A04", "0x80009A08", "L_80009A34"),
        ("funcs_3.c", "0x80009BD4", "L_80009BD4", "0x80009BD8", "L_80009C04"),
        ("funcs_3.c", "0x80009CEC", "L_80009CEC", "0x80009CF0", "L_80009D1C"),
        ("funcs_3.c", "0x80009E10", "L_80009E10", "0x80009E14", "L_80009E40"),
        ("funcs_3.c", "0x80009F30", "L_80009F30", "0x80009F34", "L_80009F60"),
        ("funcs_3.c", "0x8000A0D8", "L_8000A0D8", "0x8000A0DC", "L_8000A108"),
        ("funcs_3.c", "0x8000A23C", "L_8000A23C", "0x8000A240", "L_8000A26C"),
        ("funcs_3.c", "0x8000A3A4", "L_8000A3A4", "0x8000A3A8", "L_8000A3D4"),
        ("funcs_3.c", "0x8000A518", "L_8000A518", "0x8000A51C", "L_8000A548"),
        ("funcs_3.c", "0x8000A8F8", "L_8000A8F8", "0x8000A8FC", "L_8000A928"),
        ("funcs_3.c", "0x8000AA7C", "L_8000AA7C", "0x8000AA80", "L_8000AAAC"),
        ("funcs_3.c", "0x8000ABEC", "L_8000ABEC", "0x8000ABF0", "L_8000AC1C"),
        ("funcs_3.c", "0x8000AD64", "L_8000AD64", "0x8000AD68", "L_8000AD94"),
        ("funcs_3.c", "0x8000AE94", "L_8000AE94", "0x8000AE98", "L_8000AEC4"),
        ("funcs_3.c", "0x8000AFFC", "L_8000AFFC", "0x8000B000", "L_8000B02C"),
        ("funcs_3.c", "0x8000B124", "L_8000B124", "0x8000B128", "L_8000B154"),
        ("funcs_3.c", "0x8000B294", "L_8000B294", "0x8000B298", "L_8000B2C4"),
        ("funcs_3.c", "0x8000B3EC", "L_8000B3EC", "0x8000B3F0", "L_8000B41C"),
        ("funcs_3.c", "0x8000B550", "L_8000B550", "0x8000B554", "L_8000B580"),
        ("funcs_3.c", "0x8000B8FC", "L_8000B8FC", "0x8000B900", "L_8000B92C"),
        ("funcs_3.c", "0x8000BA14", "L_8000BA14", "0x8000BA18", "L_8000BA44"),
        ("funcs_3.c", "0x8000C750", "L_8000C750", "0x8000C754", "L_8000C780"),
        ("funcs_3.c", "0x8000C874", "L_8000C874", "0x8000C878", "L_8000C8A4"),
        ("funcs_3.c", "0x8000C99C", "L_8000C99C", "0x8000C9A0", "L_8000C9CC"),
        ("funcs_3.c", "0x8000CAC0", "L_8000CAC0", "0x8000CAC4", "L_8000CAF0"),
        ("funcs_3.c", "0x8000CBE8", "L_8000CBE8", "0x8000CBEC", "L_8000CC18"),
        ("funcs_3.c", "0x8000CCE4", "L_8000CCE4", "0x8000CCE8", "L_8000CD14"),
        ("funcs_3.c", "0x8000CDF0", "L_8000CDF0", "0x8000CDF4", "L_8000CE20"),
        ("funcs_3.c", "0x8000E1B0", "L_8000E1B0", "0x8000E1B4", "L_8000E1E0"),
        ("funcs_3.c", "0x8000E350", "L_8000E350", "0x8000E354", "L_8000E380"),
        ("funcs_3.c", "0x8000E494", "L_8000E494", "0x8000E498", "L_8000E4C4"),
        ("funcs_3.c", "0x8000E5E8", "L_8000E5E8", "0x8000E5EC", "L_8000E618"),
        ("funcs_3.c", "0x8000E70C", "L_8000E70C", "0x8000E710", "L_8000E73C"),
        ("funcs_3.c", "0x8000E8A4", "L_8000E8A4", "0x8000E8A8", "L_8000E8D4"),
        ("funcs_3.c", "0x8000EA40", "L_8000EA40", "0x8000EA44", "L_8000EA70"),
        ("funcs_3.c", "0x8000EB70", "L_8000EB70", "0x8000EB74", "L_8000EBA0"),
        ("funcs_3.c", "0x8000ECB4", "L_8000ECB4", "0x8000ECB8", "L_8000ECE4"),
        ("funcs_3.c", "0x8000EE14", "L_8000EE14", "0x8000EE18", "L_8000EE44"),
        ("funcs_3.c", "0x8000F9CC", "L_8000F9CC", "0x8000F9D0", "L_8000F9FC"),
        ("funcs_3.c", "0x8000FA7C", "L_8000FA7C", "0x8000FA80", "L_8000FAAC"),
        ("funcs_3.c", "0x8000FC04", "L_8000FC04", "0x8000FC08", "L_8000FC34"),
        ("funcs_3.c", "0x8000FCD4", "L_8000FCD4", "0x8000FCD8", "L_8000FD04"),
        ("funcs_3.c", "0x8000FDF4", "L_8000FDF4", "0x8000FDF8", "L_8000FE24"),
        ("funcs_3.c", "0x8000FEAC", "L_8000FEAC", "0x8000FEB0", "L_8000FEDC"),
        ("funcs_4.c", "0x800111A8", "L_800111A8", "0x800111AC", "L_800111D8"),
        ("funcs_4.c", "0x80011310", "L_80011310", "0x80011314", "L_80011340"),
        ("funcs_4.c", "0x800114A0", "L_800114A0", "0x800114A4", "L_800114D0"),
        ("funcs_4.c", "0x800118E4", "L_800118E4", "0x800118E8", "L_80011914"),
        ("funcs_4.c", "0x80011A0C", "L_80011A0C", "0x80011A10", "L_80011A3C"),
        ("funcs_4.c", "0x80011B34", "L_80011B34", "0x80011B38", "L_80011B64"),
        ("funcs_4.c", "0x80012B50", "L_80012B50", "0x80012B54", "L_80012B80"),
        ("funcs_4.c", "0x80012CAC", "L_80012CAC", "0x80012CB0", "L_80012CDC"),
        ("funcs_4.c", "0x80012E60", "L_80012E60", "0x80012E64", "L_80012E90"),
        ("funcs_4.c", "0x8001315C", "L_8001315C", "0x80013160", "L_8001318C"),
        ("funcs_4.c", "0x800132C0", "L_800132C0", "0x800132C4", "L_800132F0"),
        ("funcs_4.c", "0x8001345C", "L_8001345C", "0x80013460", "L_8001348C"),
        ("funcs_4.c", "0x800136EC", "L_800136EC", "0x800136F0", "L_8001371C"),
        ("funcs_4.c", "0x80013A58", "L_80013A58", "0x80013A5C", "L_80013A88"),
        ("funcs_4.c", "0x80013BD4", "L_80013BD4", "0x80013BD8", "L_80013C04"),
        ("funcs_4.c", "0x80013DD4", "L_80013DD4", "0x80013DD8", "L_80013E04"),
        ("funcs_4.c", "0x80014120", "L_80014120", "0x80014124", "L_80014150"),
        ("funcs_4.c", "0x800142DC", "L_800142DC", "0x800142E0", "L_8001430C"),
        ("funcs_4.c", "0x80014538", "L_80014538", "0x8001453C", "L_80014568"),
        ("funcs_4.c", "0x800148C8", "L_800148C8", "0x800148CC", "L_800148F8"),
        ("funcs_4.c", "0x80014A6C", "L_80014A6C", "0x80014A70", "L_80014A9C"),
        ("funcs_4.c", "0x80014C4C", "L_80014C4C", "0x80014C50", "L_80014C7C"),
        ("funcs_4.c", "0x80015870", "L_80015870", "0x80015874", "L_800158A0"),
        ("funcs_4.c", "0x80015C2C", "L_80015C2C", "0x80015C30", "L_80015C5C"),
        ("funcs_4.c", "0x80015D7C", "L_80015D7C", "0x80015D80", "L_80015DAC"),
        ("funcs_4.c", "0x80015F60", "L_80015F60", "0x80015F64", "L_80015F90"),
        ("funcs_4.c", "0x800163A8", "L_800163A8", "0x800163AC", "L_800163D8"),
        ("funcs_4.c", "0x80016810", "L_80016810", "0x80016814", "L_80016840"),
        ("funcs_4.c", "0x80016B38", "L_80016B38", "0x80016B3C", "L_80016B68"),
        ("funcs_4.c", "0x80016ED8", "L_80016ED8", "0x80016EDC", "L_80016F08"),
        ("funcs_4.c", "0x80017504", "L_80017504", "0x80017508", "L_80017534"),
        ("funcs_4.c", "0x8001761C", "L_8001761C", "0x80017620", "L_8001764C"),
    ]
    _atw_g3 = 0
    _atw_g4 = 0
    for _atw_file, _atw_walk, _atw_label, _atw_peek, _atw_outer in _alloc_tail_walk_sites:
        if p.name != _atw_file:
            continue
        # GUARD3: validate OLD r3 before v1=*v1
        _g3_old = (
            f"{_atw_label}:\n"
            f"    // {_atw_walk}: lw          $v1, 0x0($v1)\n"
            f"    g_rs64_last_guest_pc = {_atw_walk}u;\n"
            f"    ctx->r3 = MEM_W(ctx->r3, 0X0);\n"
        )
        _g3_old_nobc = (
            f"{_atw_label}:\n"
            f"    // {_atw_walk}: lw          $v1, 0x0($v1)\n"
            f"    ctx->r3 = MEM_W(ctx->r3, 0X0);\n"
        )
        _g3_new = (
            f"{_atw_label}:\n"
            f"    // {_atw_walk}: lw          $v1, 0x0($v1)\n"
            f"    g_rs64_last_guest_pc = {_atw_walk}u;\n"
            f"    {{ // PATCH: unguarded free-list-walk loop-back guard (s560, residual alloc-tail GUARD3 / item -342, site={_atw_walk}) -- see fixup_game_funcs.py comment\n"
            f"        static int s_alloc_tail_guard3_enabled = -1;\n"
            f"        if (s_alloc_tail_guard3_enabled < 0) {{ const char* e = getenv(\"ROGUESQ_LOG_ALLOC_TAIL_GUARD3\"); s_alloc_tail_guard3_enabled = (e && e[0] && e[0] != '0') ? 1 : 0; }}\n"
            f"        uint32_t r3_lo = U32(ctx->r3);\n"
            f"        if (r3_lo < 0x80000000u || r3_lo >= 0x80800000u) {{\n"
            f"            if (s_alloc_tail_guard3_enabled) {{\n"
            f"                static int s_alloc_tail_guard3_n = 0;\n"
            f"                fprintf(stderr, \"[alloc-tail-guard3] n=%d site={_atw_walk} bad_r3=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard3_n, r3_lo, U32(ctx->r31));\n"
            f"                s_alloc_tail_guard3_n++;\n"
            f"            }}\n"
            f"            goto {_atw_outer};\n"
            f"        }}\n"
            f"    }}\n"
            f"    ctx->r3 = MEM_W(ctx->r3, 0X0);\n"
        )
        n3 = 0
        if text.count(_g3_old) == 1:
            text = text.replace(_g3_old, _g3_new, 1)
            n3 = 1
        elif text.count(_g3_old_nobc) == 1:
            text = text.replace(_g3_old_nobc, _g3_new, 1)
            n3 = 1
        if n3:
            changed = True
            _atw_g3 += 1
        else:
            if f"residual alloc-tail GUARD3 / item -342, site={_atw_walk}" not in text:
                report.append(f"WARNING: alloc-tail GUARD3 site={_atw_walk} in {p.name} not found")

        # GUARD4: validate NEW r3 before v0=*v1 (post-walk peek)
        _g4_old = (
            f"    // {_atw_peek}: lw          $v0, 0x0($v1)\n"
            f"    g_rs64_last_guest_pc = {_atw_peek}u;\n"
            f"    ctx->r2 = MEM_W(ctx->r3, 0X0);\n"
        )
        _g4_old_nobc = (
            f"    // {_atw_peek}: lw          $v0, 0x0($v1)\n"
            f"    ctx->r2 = MEM_W(ctx->r3, 0X0);\n"
        )
        _g4_new = (
            f"    // {_atw_peek}: lw          $v0, 0x0($v1)\n"
            f"    g_rs64_last_guest_pc = {_atw_peek}u;\n"
            f"    {{ // PATCH: unguarded peek-load on freshly-read (unvalidated) list-walk pointer (s560, residual alloc-tail GUARD4 / item -342, site={_atw_peek}) -- see fixup_game_funcs.py comment\n"
            f"        static int s_alloc_tail_guard4_enabled = -1;\n"
            f"        if (s_alloc_tail_guard4_enabled < 0) {{ const char* e = getenv(\"ROGUESQ_LOG_ALLOC_TAIL_GUARD4\"); s_alloc_tail_guard4_enabled = (e && e[0] && e[0] != '0') ? 1 : 0; }}\n"
            f"        uint32_t r3_lo = U32(ctx->r3);\n"
            f"        uint32_t r3_hi = (uint32_t)((uint64_t)ctx->r3 >> 32);\n"
            f"        if (r3_lo < 0x80000000u || r3_lo >= 0x80800000u || r3_hi != 0xFFFFFFFFu) {{\n"
            f"            if (s_alloc_tail_guard4_enabled) {{\n"
            f"                static int s_alloc_tail_guard4_n = 0;\n"
            f"                fprintf(stderr, \"[alloc-tail-guard4] n=%d site={_atw_peek} bad_r3=0x%08X hi=0x%08X ra=0x%08X\\n\", s_alloc_tail_guard4_n, r3_lo, r3_hi, U32(ctx->r31));\n"
            f"                s_alloc_tail_guard4_n++;\n"
            f"            }}\n"
            f"            goto {_atw_outer};\n"
            f"        }}\n"
            f"    }}\n"
            f"    ctx->r2 = MEM_W(ctx->r3, 0X0);\n"
        )
        n4 = 0
        if text.count(_g4_old) == 1:
            text = text.replace(_g4_old, _g4_new, 1)
            n4 = 1
        elif text.count(_g4_old_nobc) == 1:
            text = text.replace(_g4_old_nobc, _g4_new, 1)
            n4 = 1
        if n4:
            changed = True
            _atw_g4 += 1
        else:
            if f"residual alloc-tail GUARD4 / item -342, site={_atw_peek}" not in text:
                report.append(f"WARNING: alloc-tail GUARD4 site={_atw_peek} in {p.name} not found")
        if n3 or n4:
            if "#include <stdio.h>" not in text:
                text = text.replace('#include "recomp.h"\n', '#include "recomp.h"\n#include <stdio.h>\n', 1)
            if "#include <stdlib.h>" not in text:
                text = text.replace('#include "recomp.h"\n', '#include "recomp.h"\n#include <stdlib.h>\n', 1)
    if _atw_g3 or _atw_g4:
        report.append(f"{p.name}: residual alloc-tail GUARD3 patched x{_atw_g3}, GUARD4 patched x{_atw_g4}")


