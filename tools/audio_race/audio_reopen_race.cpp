// s6739: positive control for the audio_device_mutex fix in src/main/main.cpp.
// Thread A reopens the SDL audio device (like set_frequency on the game thread); thread B polls
// SDL_GetQueuedAudioSize (like get_remaining_audio_bytes on the events thread). Arm "unlocked"
// is the pre-s6739 code and is expected to crash; arm "locked" holds one mutex around every call.
// Build: c++ -std=c++17 -O1 tools/audio_race/audio_reopen_race.cpp -I/opt/homebrew/include \
//          -L/opt/homebrew/lib -lSDL2 -o /tmp/audio_reopen_race
// Run:   /tmp/audio_reopen_race unlocked|locked [reopens]
#include <SDL2/SDL.h>
#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstring>
#include <mutex>
#include <thread>

static SDL_AudioDeviceID dev = 0;
static std::recursive_mutex mtx;
static std::atomic<bool> stop{false};
static bool locked = false;

static void open_dev(int freq) {
    SDL_AudioSpec want{};
    want.freq = freq; want.format = AUDIO_S16SYS; want.channels = 2; want.samples = 1024;
    dev = SDL_OpenAudioDevice(nullptr, 0, &want, nullptr, 0);
    if (dev) SDL_PauseAudioDevice(dev, 0);
}

int main(int argc, char** argv) {
    locked = argc > 1 && !strcmp(argv[1], "locked");
    const int reopens = argc > 2 ? atoi(argv[2]) : 400;
    if (SDL_Init(SDL_INIT_AUDIO) != 0) { fprintf(stderr, "SDL_Init: %s\n", SDL_GetError()); return 2; }
    open_dev(22047);
    unsigned long polls = 0;
    std::thread poller([&] {
        while (!stop.load()) {
            if (locked) { std::lock_guard<std::recursive_mutex> l(mtx); if (dev) SDL_GetQueuedAudioSize(dev); }
            else if (dev) SDL_GetQueuedAudioSize(dev);
            polls++;
        }
    });
    static int16_t buf[2048];
    for (int i = 0; i < reopens; i++) {
        if (locked) mtx.lock();
        if (dev) { SDL_CloseAudioDevice(dev); dev = 0; }
        open_dev(i & 1 ? 22047 : 48000);
        if (dev) SDL_QueueAudio(dev, buf, sizeof buf);
        if (locked) mtx.unlock();
        std::this_thread::sleep_for(std::chrono::microseconds(200));  // let the poller interleave in both arms
    }
    stop = true; poller.join();
    printf("arm=%s reopens=%d polls=%lu survived\n", locked ? "locked" : "unlocked", reopens, polls);
    SDL_Quit();
    return 0;
}
