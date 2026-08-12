# NEXT work unit (after s706: test whether dummy video is the oracle's remaining boot-route difference)

HYPOTHESIS-ID: m3-oracle-boot-environment

Do not add a target watch or alter the E9 tracer. Use the existing
`--vi-poll` witness to run a concurrent three-arm retail oracle comparison:
current dummy-video control, `mupen64plus-video-glide64mk2.dylib`, and
`mupen64plus-video-rice.dylib`. Use debugger=1/emulator=0, the existing RSP
HLE, separate config directories, and the 6..56-second eleven-Start schedule.
First smoke-test each video plugin for a clean 5-second run; if a plugin needs
a display/context and cannot initialize, record that measured failure and do
not treat its missing phase trace as a null.

## Competing hypotheses

- **H-dummy-video-route:** either real-video arm reaches 640/1024/0x6ABxxx
  while the dummy control remains 320.
- **H-core-environment-route:** every initialized arm reports the initial 320
  control but never a phase transition.
- **H-video-plugin-unavailable:** a real-video arm fails before its direct
  initial-320 control because the headless host cannot provide its required
  context; it is explicitly uninstrumented, so no phase null is claimed for it.

## Discriminating measurement

The positive control is a visible initial `--vi-poll` width=320 sample in each
initialized arm; each arm must also retain `--vi-trace`, `--pif-trace`, and
`--watch-write 0:0x800000`. A real-video 640/1024/0x6ABxxx result confirms
H-dummy-video-route; live 320-only polling in all initialized arms refutes it
and supports H-core-environment-route; an initialization failure confirms only
H-video-plugin-unavailable.

## Commands

    tools/oracle/build.sh
    # Smoke-test dummy, Glide64MK2, and Rice for 5s, then launch all initialized
    # arms concurrently for 70s with the explicit DEBUGGER=1 core path.
    # Capture logs under scratch/agent/s707_oracle_video_ab/.
