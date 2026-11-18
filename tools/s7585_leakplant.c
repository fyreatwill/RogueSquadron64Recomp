// s7585 class LK positive control, injected with DYLD_INSERT_LIBRARIES (no game rebuild).
// At load: 64 blocks of 1 MB malloc'd, memset (so pages count in phys_footprint), pointers dropped -> `leaks` must report
// >= 64 MB leaked and the footprint must sit ~64 MB above an unplanted arm. RS64_LEAKPLANT_MB overrides the count.
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
__attribute__((constructor)) static void s7585_plant(void) {
  const char *e = getenv("RS64_LEAKPLANT_MB"); int n = e ? atoi(e) : 64;
  for (int i = 0; i < n; i++) { volatile char *p = malloc(1 << 20); if (p) memset((void *)p, 0x5A, 1 << 20); p = 0; }
  fprintf(stderr, "[s7585-leakplant] leaked %d MB\n", n);
}
