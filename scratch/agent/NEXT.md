# NEXT: audio output hot-plug (s7198 follow-up)
HYPOTHESIS-ID: audio-hotplug
Context: s7197 posts AI anyway when the device stops pulling; s7198 caps the stuck queue at 150 ms (ROGUESQ_AI_BACKLOG_MS).
Both handle a device that is STUCK. main.cpp (open_audio_output ~7971, audio_route_apply_cycle ~8000, set_frequency ~8060)
has no SDL_AUDIODEVICEREMOVED / SDL_AUDIODEVICEADDED handling. When an output really disconnects (HDMI TV off, Bluetooth
headset gone), SDL2 marks the opened device disconnected and nobody reopens a device. Audio stays dead until F9 or a rate change.
First, fold soak s7198_backlog_L4 from SOAK-RESULTS (expect trims=0 and peak [s7198-q] ms << 150 in mission).
Unit (one build, all arms):
 1. Find the SDL event pump (grep SDL_PollEvent in src/main). On SDL_AUDIODEVICEREMOVED with iscapture==0 and which==audio_device:
    close and reopen (the preferred name falls back to the default; see open_audio_output). On SDL_AUDIODEVICEADDED whose name
    matches g_audio_route_pref while we run on the fallback: reopen onto it. Log [s7199-hotplug]. Hold audio_device_mutex.
    ROGUESQ_AUDIO_HOTPLUG=0 = old.
 2. Forced arm ROGUESQ_AUDIO_REMOVE_TEST=<sec>: SDL_PushEvent a synthetic SDL_AUDIODEVICEREMOVED for the open device (and, if
    feasible, SDL_GetAudioDeviceStatus before and after).
 3. Arms (owner env, 60 s, test at 15 s, [s7198-q] logger via ROGUESQ_AI_STALL_TEST=100000): hotplug=0 vs default vs ctl.
Hypotheses:
- H-reopen-ok: the default arm reopens (new device id); bufs/s returns to ~115 within 1 s and queued stays ~30 ms.
- H-reopen-race: the reopen races queue_samples/get_frames_remaining (mutex gap) -> crash or a 0-id window. Fix the locking.
- H-sdl-heals: SDL2 on macOS already migrates a default-device stream itself (CoreAudio default-device follow). Then only
  named-pref devices need the handler. Discriminate with the hotplug=0 arm on the "<system default>" route vs a named route.
Discriminator: device id plus bufs/s and queued after the event, per arm.
