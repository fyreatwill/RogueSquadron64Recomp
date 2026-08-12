# NEXT work unit (after s684 span attribution)

HYPOTHESIS-ID: m3-post-exit-fs-stall

Replace the false fixed-8-byte output E9 scan with a parser-derived
phase-scoped FULL_SYNC count, then rerun one 64-task section-2 window. s684
proved the apparent missing E9s were inline data inside executed raw `0xCE`
20-word commands; do not alter decoding, submission, or FULL_SYNC behavior.

## Competing hypotheses

- **H-rsp-starvation:** the authoritative parser sees only the known ~3 real
  FULL_SYNCs in the section-2 window, so starvation originates before RT64
  parses the submitted output.
- **H-dispatch-loss:** raw parser E9 fetches exceed `State::fullSync` calls,
  so a remaining loss is between parser fetch and FULL_SYNC handling.
- **H-probe-scope-bug:** boot controls or the section-2 latch disagree with
  the new parser-derived count, invalidating the phase join.

## Discriminating measurement

At RT64, record one phase-scoped per-task pair: raw `0xE9` fetches and actual
`GBI_RDP::fullSync` calls, with four boot controls, one section-2 latch, 64
target rows, and matching `dl-sync-probe2` rows. Remove the bridge's
fixed-8-byte E9 scan from the decision path; it cannot distinguish RDP command
boundaries from triangle inline data.

- Raw E9 and `fullSync` agree at ~3 across the target: H-rsp-starvation
  supported.
- Raw E9 exceeds `fullSync`: H-dispatch-loss supported.
- Any boot control or phase latch mismatch: H-probe-scope-bug supported.

## Commands

    env DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer zsh -c 'cd build && cmake --build . -j8'
    env BUDGET_S=2400 TARGET_PULSED=1 SEC2_SETTLE_S=8 POST_PULSE_HOLD_S=15 MAX_HOLD_S=45 zsh scratch/agent/s670_postsec2_pulse_freeroll.sh
