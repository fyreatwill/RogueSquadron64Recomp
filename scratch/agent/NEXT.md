# Next work unit: M5 A11 pre-title slot-0 0x02 stall — who should clear it?

HYPOTHESIS-ID: m5-a11-pretitle-slot-stall

s4195: waitForAnyAudioSlot's 500k cap fired once in phase 3 (width 640, origin 0x62BD00) with slot-0 status byte stuck 0x02
(base 0x8018D4A0) after 8M `[avf-gate] site=slot-byte` reads. Hypotheses: H-no-producer (nothing runs the 0x02->0x00
writer pre-title; audio worker/tick gated off: stub artifact), H-slow (writer runs but needs more than 500k iterations;
cap too small), H-retail-same (retail also spins briefly here). Discriminator: in ONE run, log writers of the slot-0 byte
(existing `[avf-gate] site=slot-sb` stores) plus tick/serviceVoicePoolFrame entry counters within phase 3, compared with a
concurrent ROGUESQ_WAITFORSLOT_GUARD_CAP=5000000 arm of the same recipe to see whether the byte ever clears.
Template: scratch/agent/s4195_voice_guard_class.sh. Cap=5M clears it -> H-slow; never clears -> H-no-producer, name the gate.
Optionally check retail wait duration with tools/oracle/README.md (boot phase only).
