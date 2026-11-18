/* s7578: force-included into every C TU of the build_ubsanc arm (tools/build_ubsanc.sh). Positive control for the runtime
 * signed-overflow witness over the generated game C: with ROGUESQ_S7578_PLANT=1, the first constructor to run does one
 * INT_MAX + 1 in a RecompiledFuncs-flag TU, so UBSan must print "s7578_ubsanc_plant.h:... signed integer overflow". */
#include <stdlib.h>
#include <stdio.h>
#include <limits.h>
__attribute__((weak)) int rs64_s7578_plant_done;
static void __attribute__((constructor, used)) rs64_s7578_plant(void) {
    const char* e = getenv("ROGUESQ_S7578_PLANT");
    if (!e || e[0] != '1' || rs64_s7578_plant_done) return;
    rs64_s7578_plant_done = 1;
    volatile int x = INT_MAX; int y = x + (e[0] - '0');
    fprintf(stderr, "[s7578-plant] fired y=%d\n", y);
}
