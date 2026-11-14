// s7354 class AE control: does ThreadSanitizer see happens-before through moodycamel::LightweightSemaphore (mach semaphore_t on
// macOS), the primitive ultramodern uses to hand the CPU between guest threads? Build/run:
//   clang++ -std=c++17 -fsanitize=thread -g -O1 -I lib/N64ModernRuntime/thirdparty/concurrentqueue tools/s7354_sem_ctl.cpp -o /tmp/s7354_sem_ctl
//   /tmp/s7354_sem_ctl sem   -> handoff only via LightweightSemaphore (correctly synchronised program)
//   /tmp/s7354_sem_ctl mutex -> same handoff under a std::mutex flag (TSan-visible)       /tmp/s7354_sem_ctl none -> real race
// If TSan reports a race in `sem`, guest-thread rows synced by that semaphore are TSan blind-spot false positives.
#include "concurrentqueue.h"
#include "lightweightsemaphore.h"
#include <thread>
#include <mutex>
#include <cstring>
#include <cstdio>
#include <unistd.h>
static int payload;
int main(int argc, char** argv) {
    const char* mode = argc > 1 ? argv[1] : "sem";
    moodycamel::LightweightSemaphore go(0, 0);   // maxSpins 0: always block in semaphore_wait (the guest-thread path)
    std::mutex m; bool ready = false;
    std::thread t([&] {
        if (!strcmp(mode, "sem")) go.wait();
        else if (!strcmp(mode, "mutex")) { for (;;) { std::lock_guard<std::mutex> l(m); if (ready) break; } }
        else usleep(1000);
        std::printf("payload=%d\n", payload);
    });
    usleep(20000);
    payload = 42;
    if (!strcmp(mode, "sem")) go.signal();
    else if (!strcmp(mode, "mutex")) { std::lock_guard<std::mutex> l(m); ready = true; }
    t.join();
}
