"""s6480 G1c: census of the material/link pool at *0x80136FCC (12-byte rows {prev,next,type,...}, built by 0x80041EF0 with
n = level-data count) printed with the exitlog: rows scanned up to the last free-list-pattern row, how many carry link!=0xFFFF,
and how many of those point at a type==1 row. Idempotent."""
TAG = "PATCH: s6480 poolcensus"
P9 = "/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c"
OLD = '        for (int i = 0; i < 8; i++) g_s6476[i] = 0; }\n'
NEW = '''        { /* ''' + TAG + ''' */
          int32_t pb = (int32_t)MEM_W((int32_t)0x80130000, 0x6FCC); uint32_t nf = 0, nl = 0, nt1 = 0, nfree = 0, last = 0, scan = 0;
          if (pb > 0x80000000 && pb < 0x80700000) { for (uint32_t i = 0; i < 6000 && (uint32_t)pb + 12u * i + 12u < 0x80700000u; i++) { scan = i + 1;
              uint32_t pr = MEM_HU(pb, 12*i), nx = MEM_HU(pb, 12*i+2); if (nx == i + 1 && (pr == i - 1 || (i == 0 && pr == 0xFFFF))) { nfree++; last = i; }
              else if (nx != 0xFFFF && nx < 6000) { nl++; if (MEM_HU(pb, 12*nx+4) == 1) nt1++; } else if (nx != 0xFFFF) { nl++; } } }
          fprintf(stderr, "[poolcensus] base=%08x scan=%u freepattern=%u lastfree=%u linked(non-FFFF,non-free)=%u of-which-type1=%u\\n", (uint32_t)pb, scan, nfree, last, nl, nt1); }
'''
def apply9(t):
    if TAG in t or "PATCH: s6476 exitcount" not in t: return t, 0
    assert t.count(OLD) == 1
    return t.replace(OLD, NEW + OLD), 1
