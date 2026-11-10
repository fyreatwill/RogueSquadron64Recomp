# NEXT: owner reports first; otherwise N64Recomp memory-access + integer branch-likely lowering census
HYPOTHESIS-ID: n64recomp-mem-branch-census
Context: s7082 closed the warning set, s7083 control flow, s7084 FPU, s7085 integer (tools/s7085_int_census.py,
tools/s7085_int_test/run_test.py; the ddivu /0 C-UB gap was fixed in recomp.h). Pristine front-end output: scratch/s7082/regen
(regenerate with tools/regen_front.sh if cleaned). Model the census on tools/s7085_int_census.py (shape table + mutation
negative control + a positive-control site) and the host test on tools/s7085_int_test/.
Unit (offline, one bounded change):
1. Loads/stores: lb/lbu/lh/lhu/lw/lwu/ld/sb/sh/sw/sd/ll/sc/cache/sync. Check MEM_B/MEM_BU use ^3, MEM_H/MEM_HU ^2, MEM_W none,
   LD/SD word order (high word at +0), lwu zero-extends, ll/sc lowering (sc must write 1 to rt), cache/sync are no-ops.
   Count sites per shape; list any unaligned constant offsets on lh/lw (address error on retail).
2. %hi/%lo pairs: every RELOC_HI16/LO16 or lui+addiu/lw constant pair, check the lo16 is sign-extended (addiu -0x6F00 style)
   and the pair targets one symbol (relocatable sections only).
3. Integer branch-likely (beql/bnel/blezl/bgtzl/bltzl/bgezl/bgezall/bltzall): delay slot only inside the taken block, then
   goto skip; non-likely branches: delay slot on both paths. Count per op.
4. Host test: MEM_* swizzle against a big-endian byte array at all alignments, LD/SD round trip, lwu vs lw, sc result.
Discriminator: per shape {matches, differs but unreachable, differs and live}. Positive control: a known ld/sd site
(u64DivU64's callers or the libultra osGetTime path) and a known beql must be enumerated and classified.
