import pathlib

p = pathlib.Path('/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_9.c')
t = p.read_text()
tag = 'PATCH: s6511 full span grid'
if tag in t:
    print('already')
    raise SystemExit

needle = 'static uint32_t s6509_dc0_n; /* PATCH: s6509 DC0 legitimacy */\n'
assert t.count(needle) == 1
t = t.replace(needle, needle +
    'static uint32_t s6511_wfull[4], s6511_wfirst[4], s6511_wlast[4]; /* ' + tag + ' */\n', 1)

old = 's6500_wlast[i] = value & 0xffu; s6500_wcount[i]++;\n      if (addr >= 0x80130DB0u && addr < 0x80130DC8u) s6500_wmask[i] |= 1u << (addr - 0x80130DB0u);'
new = 's6500_wlast[i] = value & 0xffu; s6500_wcount[i]++;\n      if (addr >= 0x80130DB0u && addr < 0x80132DB0u) { if (!s6511_wfull[i]) s6511_wfirst[i] = addr; s6511_wlast[i] = addr; s6511_wfull[i]++; }\n      if (addr >= 0x80130DB0u && addr < 0x80130DC8u) s6500_wmask[i] |= 1u << (addr - 0x80130DB0u);'
assert t.count(old) == 1
t = t.replace(old, new, 1)

needle = 'fprintf(stderr, "[postring] key=%u seq=%u ring=%u stores=%u non127=%u tbl=", s6505_key, s6497_seq, s6500_seq[ri], s6500_stores[ri], s6500_non127[ri]);'
assert t.count(needle) == 1
replacement = '''{ uint32_t h = 2166136261u, nz = 0; for (uint32_t gi = 0; gi < 0x2000u; gi++) { uint32_t gv = (uint8_t)MEM_B(0, (int64_t)(int32_t)(0x80130DB0u + gi)); h ^= gv; h *= 16777619u; if (gv != 0x7fu) nz++; } fprintf(stderr, "[span-grid] key=%u seq=%u dim=64x64 bytes=8192 hash=%08x non127=%u full=%u:%08x..%08x,%u:%08x..%08x,%u:%08x..%08x,%u:%08x..%08x\\n", s6505_key, s6497_seq, h, nz, s6511_wfull[0], s6511_wfirst[0], s6511_wlast[0], s6511_wfull[1], s6511_wfirst[1], s6511_wlast[1], s6511_wfull[2], s6511_wfirst[2], s6511_wlast[2], s6511_wfull[3], s6511_wfirst[3], s6511_wlast[3]); } ''' + needle
t = t.replace(needle, replacement, 1)
p.write_text(t)
print('updated')
