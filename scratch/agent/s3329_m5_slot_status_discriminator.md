# Session 3329 — M5 route and MusyX voice-slot discriminator

The retail oracle was run first with a whole-RDRAM write watch, title/hangar
press schedule, slot/status watches, and consumer PCs. The whole-RDRAM positive
control passed 10,000 callbacks and the run reached title VI-1024 at 17.3 s;
it was bounded before hangar, so it supplies title ground truth only for this
iteration. Existing Session 3327 remains the independent hangar control.

The port Debug target was rebuilt after adding the diagnostic
`ROGUESQ_LOG_M5_VOICE_SLOTS` poller. It samples the actual MusyX voice table at
`0x80154620`, stride `0x1228`, active byte `+0x4620`, using max count
`0x800A5121`, and logs mask changes every 10 ms. The same run retained route,
task, and PCM controls and used:

    ROGUESQ_AUTOPILOT='60:start,90:start,120:start'
    PROBE_PHASE_WIDTH=1024 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1

The run passed the port controls (`audtask-dispatch` 105 rows and
`pcm-boundary` 244 rows), reached title 1024 at 50.3 s, and reached hangar
512 / `0x006AB400` at 94.2 s. Route commits included seq=10 at 1024/0x790400
and seq=12 at 512/0x6AB400. The voice probe observed max=1 and active mask 0
through title and the hangar entry; no active voice was held full or leaked.

This selects `H-PortHangarReachable`, refutes `H-VICommitAbsent` and
`H-VoiceReapingAbsent` as blockers for this recipe, and supersedes the
Session-3328 interpretation that the 1,578-entry cinematic dispatcher pool
was an audio-slot pool. It authorizes no audio contract change or mitigation.
The run later hit the known abort/crash path after continued hangar capture;
that does not invalidate the earlier phase controls.
