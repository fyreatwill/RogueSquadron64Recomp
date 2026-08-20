# NEXT work unit (s1998) — write the M5 audio de-stubbing plan

HYPOTHESIS-ID: m5-audio-plan

## Single work unit

Create `docs/M5-AUDIO-PLAN.md`. This is a bounded documentation/change
unit: survey every audio stub, trap, disabled gate, timeout, and host-side
shortcut currently in force, then specify an incremental de-stubbing sequence
with a phase-gated validation soak and positive control for every step. Do not
change runtime behavior or build/run the game in this unit.

The older "M5 closed" state was based on dummy-video retail watches never
reaching `musyxInitVoiceFromSample`; the current directive explicitly reopens
M5, and the Rice eleven-Start hangar recipe is the required validation path.

## Competing hypotheses

- **H-MORT-path:** the first real blocker is the missing MORT audio RSP path;
  host-side gates can be removed only after a MORT task format/ABI and RSP
  recompile boundary are identified.
- **H-degenerate-host-path:** the current immediate-`Broke` audio-task stub,
  disabled callbacks, and timeout/shortcut gates create the voice-slot and
  wait states; the first safe step can be a reversible host-side de-stub with
  no MORT code.
- **H-MusyX-mismatch:** generic `aspMain` is not compatible with this game's
  MusyX-formatted tasks, so any plan that enables stock audio before naming
  the MORT/MusyX boundary is invalid and would reproduce the known audio
  thread hang.
- **H-scheduler-independent:** the s1997 status-3 hang is a cooperative
  scheduler starvation issue independent of audio implementation; audio
  planning may still be productive, but must not claim it explains that hang
  without a separate control.

## Discriminating measurement

The plan itself must contain one complete inventory table with one row per
stub/trap/gate/shortcut: file and symbol, current behavior, guest contract,
MORT versus MusyX ownership, writer/consumer, proposed reversible change,
same-run positive control, VI phase, soak command, and rollback. The outcome
that splits the hypotheses is the first row whose contract is fully
independent and testable: a pure host gate selects a host-only first step;
an MORT-owned task selects an RSP/MORT artifact first; a MusyX/aspMain
format mismatch rejects generic audio enablement; and an absent control
blocks de-stubbing rather than producing a null result.

## Exact inspection commands

```sh
rg -n -i "audio|musyx|mort|M_AUDTASK|aspMain|audioDrain|waitForAnyAudioSlot|tickMusyX|RspExitReason::Broke|audio.*stub|stub.*audio|audio.*timeout" src lib docs tools
rg -n "ROGUESQ_.*AUDIO|ROGUESQ_DRAIN|waitForAnyAudioSlot|tickMusyXIfActive|M_AUDTASK|aspMain" src lib tools
sed -n '1,260p' src/main/main.cpp
sed -n '1,220p' src/rsp/aspMain.cpp
sed -n '1,260p' docs/PROJECT-OVERVIEW.md
sed -n '1,240p' tools/oracle/README.md
```

Read only bounded windows around grep hits in generated files and submodules.
The plan must preserve the known constraint that MusyX is not stock `aspMain`,
must name every current audio shortcut, and must give one soak recipe per
future step before any implementation begins.
