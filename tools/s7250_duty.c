/* s7250: calibrated CPU slow-down for timing controls. Battery runs (s7249) were ~1.40x slower per task because
   macOS Low Power Mode (pmset powermode 1 on battery, 2 on AC) caps clocks; changing powermode needs sudo, and
   taskpolicy is 1.0x (utility) or ~3.2x (background), so neither reproduces it. This duty-cycles a pid with
   SIGSTOP/SIGCONT: run (P - S) us, stopped S us, so throughput falls by P/(P-S). S/P = 1 - 1/factor.
   usage: s7250_duty <pid> <factor> [period_us=4000]   exits when the pid dies; leaves it running (SIGCONT) on exit. */
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>
#include <mach/mach_time.h>
static pid_t g_pid;
static void cont(int s){ (void)s; kill(g_pid, SIGCONT); _exit(0); }
static void nap(long us){ struct timespec t = { us / 1000000, (us % 1000000) * 1000 }; nanosleep(&t, NULL); }
int main(int argc, char **argv){
  if (argc < 3) { fprintf(stderr, "usage: %s pid factor [period_us]\n", argv[0]); return 2; }
  g_pid = atoi(argv[1]); double f = atof(argv[2]); long P = argc > 3 ? atol(argv[3]) : 4000;
  if (f < 1.0) f = 1.0; long S = (long)(P * (1.0 - 1.0 / f) + 0.5);
  signal(SIGTERM, cont); signal(SIGINT, cont); signal(SIGHUP, cont);
  fprintf(stderr, "[s7250] duty pid=%d factor=%.3f period=%ldus stop=%ldus\n", (int)g_pid, f, P, S);
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
  mach_timebase_info_data_t tb; mach_timebase_info(&tb);
  double t0 = (double)mach_absolute_time(), stopped = 0; long n = 0;
  while (kill(g_pid, 0) == 0) {
    if (S > 0) { uint64_t a = mach_absolute_time(); kill(g_pid, SIGSTOP); nap(S); kill(g_pid, SIGCONT);
      stopped += (double)(mach_absolute_time() - a); }
    nap(P - S);
    if (++n % 2500 == 0) { double el = mach_absolute_time() - t0;
      fprintf(stderr, "[s7250] cycles=%ld achieved factor=%.3f (stopped %.1f%%)\n", n, el / (el - stopped), 100.0 * stopped / el); }
  }
  { double el = mach_absolute_time() - t0; if (el > stopped)
      fprintf(stderr, "[s7250] end cycles=%ld achieved factor=%.3f period_us=%.0f\n", n, el / (el - stopped), n ? el * tb.numer / tb.denom / 1000.0 / n : 0); }
  return 0;
}
