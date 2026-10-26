// Qualification patch for the C-patch pipeline (s6269). Re-implements the pure
// leaf isCinematicActive (0x800AF540: return *(u32*)0x800B0934 != 0) exactly;
// the host-side fixup adds a power-of-two call log so "the patch is live" is
// observable. Not a behaviour change.
typedef unsigned int uint32_t;

#define RECOMP_PATCH __attribute__((section(".recomp_patch")))

extern volatile uint32_t cinematic_flag;  // 0x800B0934, see syms.ld

RECOMP_PATCH int isCinematicActive(void) {
    return cinematic_flag != 0;
}
