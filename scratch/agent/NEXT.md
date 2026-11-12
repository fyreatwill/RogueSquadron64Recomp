# NEXT: audio hot-plug on the system-default route (s7199 follow-up)
HYPOTHESIS-ID: audio-hotplug
Context: s7199 landed the hot-plug handler (main.cpp audio_hotplug_apply / audio_hotplug_note_queue) and proved it on a NAMED
route with a real CoreAudio removal (tools/audio_hotplug_agg.c; arms scratch/s7199/arms.zsh). Untested: ROGUESQ_AUDIO_DEVICE=default
while the macOS DEFAULT output itself is removed.
Unit:
 1. Add `setdefault <name>|restore` to tools/audio_hotplug_agg.c (save the old default output UID to a file first; ALWAYS
    restore it at the end of the script, also on failure: trap EXIT). This briefly changes the owner's system output.
 2. Arms (owner env as in scratch/s7199/arms.zsh, ROGUESQ_AUDIO_DEVICE=default, aggregate = system default, destroy at 15 s):
    hotplug=1 vs hotplug=0, plus ctl (no destroy).
Hypotheses:
- H-sdl-heals: SDL3 migrates the default stream; hotplug=0 keeps 115 bufs/s and 0 trims after the destroy. Then the handler is a
  no-op on this route (check it does not reopen needlessly; a needless reopen costs ~120-170 ms of audio-thread block).
- H-dead-default: hotplug=0 drops to ~13 bufs/s with trims (like the s7199 named route); hotplug=1 recovers (removed-event or
  drain-stall) within 0.5 s.
Discriminator: per-second bufs/trims in [s7198-q] (ROGUESQ_AI_STALL_TEST=100000 arms the logger) and the [s7199-hotplug] reopen lines.
After this, the audio host-robustness thread closes; go back to CURRENT-TRUTH Next steps (owner-look items, then ITERATION 3c ladder).
