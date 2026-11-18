// s7589 class HR positive control, injected with DYLD_INSERT_LIBRARIES (no game rebuild).
// A background thread leaks, every RS64_HRPLANT_S seconds (default 30): one fd (dup(2)), one parked pthread, one Mach
// receive port. The outside sampler (tools/s7589_hrsample.zsh) must see +2 fd/min, +2 threads/min, +2 ports/min on top of
// the game's own slope. RS64_HRPLANT_DELAY=<s> holds the plant off, so one run has a game-only window and a
// game+plant window (in-run toggle, no cross-run A/B); an unplanted arm then reads the game alone. Banner "[s7589-hrplant]" on stderr, one per leak.
#include <pthread.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <mach/mach.h>
static void *park(void *a) { (void)a; for (;;) pause(); return 0; }
static void *leaker(void *a) {
  (void)a; const char *e = getenv("RS64_HRPLANT_S"); int s = e ? atoi(e) : 30; if (s < 1) s = 30;
  const char *d = getenv("RS64_HRPLANT_DELAY"); if (d && atoi(d) > 0) sleep(atoi(d));
  fprintf(stderr, "[s7589-hrplant] armed every %d s\n", s);
  for (int n = 1;; n++) { sleep(s);
    int fd = dup(2); pthread_t t; int tr = pthread_create(&t, 0, park, 0); mach_port_t p = MACH_PORT_NULL;
    kern_return_t kr = mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &p);
    fprintf(stderr, "[s7589-hrplant] n=%d fd=%d thr=%d port=0x%x kr=%d\n", n, fd, tr, p, kr); }
  return 0; }
__attribute__((constructor)) static void s7589_plant(void) { pthread_t t; pthread_create(&t, 0, leaker, 0); pthread_detach(t); }
