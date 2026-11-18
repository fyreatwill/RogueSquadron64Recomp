// s7591 class MR runtime witness (DYLD_INSERT_LIBRARIES, no game rebuild): every RS64_HR_S (5) s log the task's send urefs on the
// host port name to RS64_HR_OUT. The name is fetched once (one ref, ours). Positive control RS64_HR_PLANT=<n>: the probe itself
// leaks n mach_host_self() refs per sample after 30 s, so its d column must step +n per sample even when the game leaks none.
// Build: clang -dynamiclib -O1 -o tools/s7591_hostrefs.dylib tools/s7591_hostrefs.c
#include <mach/mach.h>
#include <mach/mach_time.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
static void *thr(void *a) {
  (void)a; const char *o = getenv("RS64_HR_OUT"); FILE *f = fopen(o ? o : "/tmp/rs64_hostrefs.log", "w"); if (!f) return 0;
  const char *e = getenv("RS64_HR_S"); int s = e ? atoi(e) : 5; if (s < 1) s = 5;
  const char *pe = getenv("RS64_HR_PLANT"); int plant = pe ? atoi(pe) : 0;
  mach_port_t h = mach_host_self(); mach_port_urefs_t prev = 0; int planted = 0;
  for (int t = 0;; t += s) {
    if (plant > 0 && t >= 30) { for (int i = 0; i < plant; i++) (void)mach_host_self(); planted += plant; }
    mach_port_urefs_t r = 0; kern_return_t k = mach_port_get_refs(mach_task_self(), h, MACH_PORT_RIGHT_SEND, &r);
    fprintf(f, "t=%d urefs=%u d=%d planted=%d kr=%d\n", t, r, t ? (int)r - (int)prev : 0, planted, k); fflush(f); prev = r;
    sleep(s);
  }
}
__attribute__((constructor)) static void init(void) { pthread_t t; pthread_create(&t, 0, thr, 0); pthread_detach(t); }
