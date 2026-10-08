# Next work unit: name the gate that suppresses tid 0's sends to 0x8011A818/0x8011A7E8/0x80128CF0 in audio-gap seconds (s4263)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4262: in gap seconds tid 0 loops at full VI rate and still sends to 6 other queues, but the triple 0x8011A818 / 0x8011A7E8 / 0x80128CF0 drops 30/s -> 1-2/s together (2 arms). Guest ra is 0 in the native wrapper, so the send site is unnamed.
Hypotheses: (A1) the gate is a counter/flag word in guest RDRAM (frame-skip / "previous task still pending") that stays set during the gap; (A2) the gate depends on a completion posted to 0x8011A420 or 0x80128D10 whose payload differs; (A3) host-side timing (the gate reads a time/VI count that our VI pacing makes stale).
Discriminator: grep the generated C (build/RecompiledFuncs) for the function that loads 0x8011A818 and 0x8011A7E8 back to back; list its branch conditions and the RDRAM words they read; dump those words once per second with the s4262 table (healthy vs gap, same run). Positive control: the words change between healthy seconds.
Reuse scratch/agent/s4262_send.sh (2 arms, ROGUESQ_S4262=1).
