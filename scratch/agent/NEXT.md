# NEXT work unit (s2195) — test pairwise logging interactions

HYPOTHESIS-ID: m5-a1-retail-writer-census

## Work unit

Run a self-contained four-arm, phase-gated pairwise logging test from the repo
root. All arms use the same qualified image/LLE recipe and writer control.
`quiet` leaves optional logs unset; `slot-event` enables
`ROGUESQ_LOG_SLOT_DISPATCH=1` and `ROGUESQ_LOG_EVENT_WIRING=1`;
`slot-audio` enables `ROGUESQ_LOG_SLOT_DISPATCH=1` and
`ROGUESQ_LOG_AUDIO_RETURN=1`; and `event-audio` enables
`ROGUESQ_LOG_EVENT_WIRING=1` and `ROGUESQ_LOG_AUDIO_RETURN=1`. The watchdog
kills an arm with SIGKILL after the second-origin phase plus 15 seconds, on a
180-second deadline, and exits nonzero if an arm logs a crash marker.

Exact command:

```sh
zsh scratch/agent/run_s2195_m5_log_pair_ab.sh
```

Parse the complete table after the run:

```sh
for arm in quiet slot-event slot-audio event-audio; do
  echo "=== $arm ==="
  grep -a '\[m5-writer-parity-control\]' "scratch/agent/s2195_m5_log_pair_ab/$arm.log" | wc -l
  grep -a '\[phase\] vi_width=640' "scratch/agent/s2195_m5_log_pair_ab/$arm.log"
  grep -a '\[m5-writer-parity\]' "scratch/agent/s2195_m5_log_pair_ab/$arm.log"
  grep -a -E '\[(CRASH|ABORT)\]|\[last-guest-pc\]|\[pc-symbol\]' "scratch/agent/s2195_m5_log_pair_ab/$arm.log" | tail -12
done
```

## Competing hypotheses and discriminator

- H-SlotEventInteraction: `slot-event` reaches `0x00696600` or changes the
  post-first-origin boundary while `quiet` does not.
- H-SlotAudioInteraction: the same discriminator selects `slot-audio`.
- H-EventAudioInteraction: the same discriminator selects `event-audio`.
- H-NoPairInteraction: all four arms pass controls and the first 640 phase but
  miss `0x00696600`; pairwise logging interaction is insufficient, so another
  source remains open.
- H-CoverageFailure: any arm lacks its writer control or first 640 phase;
  reject the comparison rather than treating missing rows as nulls.

The discriminator is one same-iteration table per arm containing positive
control count, both 640 origins, termination/last-guest-PC outcome, all
enabled optional-log positive counts, and all six target writer-PC sets at each
observed origin. A pair outcome selects its named interaction only if controls
pass and it reaches the second origin or changes the shared boundary; four
valid misses select H-NoPairInteraction. Do not add a port guard, mitigation,
task rewrite, or audio-default flip.
