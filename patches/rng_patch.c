// s6277 C-patch qualification #2: argument passing + a guest store. Re-implements
// setRngSeed (0x80003460: *(u32*)0x80003470 = a0). The reserved libc name `rand`
// cannot be patched: N64Recomp strict mode looks up the renamed `rand_recomp` in the
// reference symbols and fails (s6277). The host-side fixup (fixup_patches_host.py)
// shadow-checks every call (stored seed == a0). Not a behaviour change.
typedef unsigned int uint32_t;

#define RECOMP_PATCH __attribute__((section(".recomp_patch")))

extern volatile uint32_t rng_seed;  // 0x80003470, see syms.ld

RECOMP_PATCH void setRngSeed(uint32_t seed) {
    rng_seed = seed;
}
