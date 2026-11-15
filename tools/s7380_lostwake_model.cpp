// s7380 class AV positive control: the RT64 thread-destructor stop pattern, OLD (flag store + notify, no lock) vs NEW
// (flag store + empty critical section on the waiter mutex + notify). A delay is injected inside the waiter's predicate
// after it reads running==true (the window between predicate check and block). The destructor's store+notify lands in
// that window. OLD: the notify is lost, join() would hang -> detected by a 300 ms watchdog. NEW: the empty critical
// section cannot start until the waiter has blocked (wait releases the mutex atomically), so the notify always lands.
// build: clang++ -std=c++17 -O1 -pthread tools/s7380_lostwake_model.cpp -o /tmp/s7380_model && /tmp/s7380_model
// exit 0 iff OLD hangs in every trial (control fires) and NEW never hangs.
#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdio>
#include <mutex>
#include <thread>

using namespace std::chrono_literals;

static bool trial(bool fixed) {
    std::mutex m;
    std::condition_variable cv;
    std::atomic<bool> running{true}, inWindow{false}, done{false};
    std::thread t([&] {
        std::unique_lock<std::mutex> lk(m);
        cv.wait(lk, [&] {
            if (!running) return true;
            inWindow = true;
            std::this_thread::sleep_for(50ms); // injected: predicate already decided "keep waiting"
            return false;
        });
        done = true;
    });
    while (!inWindow) std::this_thread::yield();
    running = false;                            // ~WorkloadQueue: threadsRunning = false;
    if (fixed) { std::scoped_lock<std::mutex> l(m); }
    cv.notify_all();
    const auto t0 = std::chrono::steady_clock::now();
    while (!done && std::chrono::steady_clock::now() - t0 < 300ms) std::this_thread::sleep_for(1ms);
    const bool hung = !done;
    if (hung) { { std::scoped_lock<std::mutex> l(m); } cv.notify_all(); } // rescue so join returns
    t.join();
    return hung;
}

int main() {
    int oldHung = 0, newHung = 0;
    const int N = 20;
    for (int i = 0; i < N; ++i) oldHung += trial(false);
    for (int i = 0; i < N; ++i) newHung += trial(true);
    std::printf("s7380 model: OLD hung %d/%d (control), NEW hung %d/%d\n", oldHung, N, newHung, N);
    return (oldHung == N && newHung == 0) ? 0 : 1;
}
