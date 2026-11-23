#!/usr/bin/env python3
"""s7842 G3 det sweep: bit-exact operand log of the flight chase-camera step (updatePlayerVehicleByControlMode), so the
port can be replayed against the retail oracle twin word for word (the s7101 chaselog prints %.6g, not bits).
Site A, 0x8004D6C8 (after vec3Length(target - pos)): `A fc=<0x8011A890> f0=<dist> f20=<dt> s2=<+0x10,+0x14,+0x18,+0x94,+0x98,
+0x9C,+0xA4> sp=<+0x20,+0x24,+0x28>`. Site B, 0x8004D7B4 (add.s f2,f2,f0 = cam y += speed*dt*dir.y): `B fc= f2=<y> f0=<product>
sp=<+0x70,+0x74,+0x78> s98=<+0x98>`. All hex words. Env ROGUESQ_S7842_CHASEHEX=<path>. Measurement only; unset = untouched.
Retail twin: RS64_ORACLE_FPR=0,2,20 RS64_ORACLE_SPW=20,24,28,70,74,78 RS64_ORACLE_PEEK=138468,13846c,138470,1384ec,1384f0,1384f4,1384fc
rs64_oracle --watch-pc 0x8004D6C8,0x8004D7B4 (tools/oracle/rs64_oracle.c s7842 FPR/SPW print). Scorer scratch/s7842/chase_cmp.py.
Positive control: one A and one B line per chase tick in flight. Idempotent; in fixup_game_funcs_vendored.py's RS64_REPLAY."""
import pathlib, sys
BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs")
MARK = "PATCH: s7842 chasehex"
OPEN = ('static FILE* f7842 = (FILE*)1; if (f7842 == (FILE*)1) { const char* e = getenv("ROGUESQ_S7842_CHASEHEX"); '
        'f7842 = (e && *e && *e != \'0\') ? fopen(e, "w") : NULL; if (f7842) setvbuf(f7842, NULL, _IOFBF, 1 << 16); }\n')
W = '(uint32_t)MEM_W(%s, (int64_t)(int32_t)%s)'
def words(base, offs): return ', '.join(W % (hex(o).upper().replace('0X', '0x'), base) for o in offs)
A = ('    { /* ' + MARK + ' A */ ' + OPEN +
     '      if (f7842) { uint32_t s2 = (uint32_t)ctx->r18, sp = (uint32_t)ctx->r29;\n'
     '        fprintf(f7842, "A fc=%u f0=%08X f20=%08X s2=%08X,%08X,%08X,%08X,%08X,%08X,%08X sp=%08X,%08X,%08X\\n", '
     '(uint32_t)MEM_W(0, (int64_t)(int32_t)0x8011A890u), ctx->f0.u32l, ctx->f20.u32l, ' + words('s2', [0x10, 0x14, 0x18, 0x94, 0x98, 0x9C, 0xA4]) +
     ', ' + words('sp', [0x20, 0x24, 0x28]) + '); } }\n')
ANCHOR_A = "    // 0x8004D6C8: lui         $at, 0x8004\n"
ANCHOR_B = "    // 0x8004D7B4: add.s       $f2, $f2, $f0\n"
n = 0
for p in sorted(BASE.glob("funcs_*.c")):
    s = p.read_text()
    if ANCHOR_B not in s:
        continue
    if MARK in s:
        print("s7842 chasehex: already applied", p.name); sys.exit(0)
    assert s.count(ANCHOR_A) == 1 and s.count(ANCHOR_B) == 1, p
    # site B shares site A's FILE*: hoist the handle into a file-scope static
    s = s.replace(ANCHOR_A, A.replace('static FILE* f7842 = (FILE*)1; ', '') + ANCHOR_A, 1)
    Bc = ('    { /* ' + MARK + ' B */ if (f7842 == (FILE*)1) { const char* e = getenv("ROGUESQ_S7842_CHASEHEX"); '
          'f7842 = (e && *e && *e != \'0\') ? fopen(e, "w") : NULL; if (f7842) setvbuf(f7842, NULL, _IOFBF, 1 << 16); }\n'
          '      if (f7842) { uint32_t s2 = (uint32_t)ctx->r18, sp = (uint32_t)ctx->r29;\n'
          '        fprintf(f7842, "B fc=%u f2=%08X f0=%08X sp=%08X,%08X,%08X s98=%08X\\n", (uint32_t)MEM_W(0, (int64_t)(int32_t)0x8011A890u), '
          'ctx->f2.u32l, ctx->f0.u32l, ' + words('sp', [0x70, 0x74, 0x78]) + ', ' + words('s2', [0x98]) + '); } }\n')
    s = s.replace(ANCHOR_B, Bc + ANCHOR_B, 1)
    FN = "RECOMP_FUNC void updatePlayerVehicleByControlMode("   # anchored on the function, not the include block: other replay
    assert s.count(FN) == 1, p                                    # steps also insert after #include, so that position is order-dependent
    s = s.replace(FN, 'static FILE* f7842 = (FILE*)1; /* ' + MARK + ' handle */\n' + FN, 1)
    p.write_text(s); n += 1
print("s7842 chasehex: %d file(s)" % n)
