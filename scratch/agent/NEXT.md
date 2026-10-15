# Next work unit

HYPOTHESIS-ID: m5-retrace-audio-cadence-boundary

(Refreshed s4898 after the maintenance iteration; CURRENT-TRUTH was compacted
to 33 KB and no experiment ran. The work unit below is unchanged and is still
the next one to run.)

Instrument one same-build port run at the two `osRecvMesg` callsites named by
s4873 (`0x800198F4` and `0x80019928`) and join every phase-gated return to the
retrace queue `0x80114388`, the audio-done queue `0x80149670`, and the next
`musyxSynthFrame` entry. Keep title and hangar route controls, SP and PCM
controls, and the existing passive crash breadcrumbs. Build once, then run
one qualified capture; do not add a counter without putting it in this table.

Competing hypotheses and discriminator:

* H1: the port retrace handler receives two retrace-queue messages per VI;
  the joined return table shows two `0x80114388` returns per VI while the
  audio-done queue remains one per VI.
* H2: retrace delivery is one per VI, but one retrace return causes two synth
  entries; the table shows one retrace return and two synth entries with no
  second audio-done message.
* H3: the extra synth cadence is driven by audio-done delivery; the table
  shows the extra `0x80149670` return/message immediately before the extra
  synth entry.

The discriminating measurement is the complete per-VI ordered join table
`queue -> osRecvMesg return -> synth entry`, with counts for each queue and
the delta from the preceding VI. A route/control failure is invalid, not a
hypothesis result.

Commands:

```text
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Run the existing qualified image-route recipe from `build/` with the new
phase-gated callsite/queue join enabled, capture stdout/stderr to
`scratch/agent/soak_results/s4898_m5_retrace_audio_cadence.log`, and kill the
process group with SIGKILL at the watchdog limit. Positive controls are title
and hangar VI transitions, nonzero PCM, and SP enter/return rows.
