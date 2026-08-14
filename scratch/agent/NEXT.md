# NEXT work unit (s984)

HYPOTHESIS-ID: m4-zero-shade-origin

The oracle fallback is unavailable in this environment: `/Users/williambuckley/Documents/Tools/rs64-oracle` does not exist, and `.claude/settings.json` does not grant it. This iteration pivots once to M4 item 4.

## One work unit

Perform a bounded static decode/origin audit of the outdoor `baseFixed=-32768` shade population. Compare the checked-in RT64 RDP shade-word assembly and vertex reconstruction with the independent Factor 5 reference's `VTXCOLOR`/`MOVEMEM` semantics and the existing s19/s20 evidence. Do not build, run, or change the mitigation in this unit.

## Competing hypotheses and discriminating measurement

- H-decode-layout: RT64 assembles the eight RDP shade words with a wrong lane/order/sign convention; a corrected decode would explain outdoor zeros while boot triangles only appear healthy accidentally.
- H-f5-stream: the LLE/RSP stream really supplies the near-zero shade words for this population; RT64's decode is structurally correct, so the writer is upstream in Factor 5 state emission.
- H-game-light-state: the F5 stream is correctly carrying game-produced values, but the game's light/vertex-color state is legitimately or accidentally initialized to the near-zero values before terrain draws.

Discriminating measurement for this unit: independently verify the RT64 reconstruction equations and word-lane order against the RDP field layout used by the reference, then check whether the existing good-vs-zero evidence uses the same combiner and decode path. Outcomes: a lane/order mismatch selects H-decode-layout; a matching decoder with raw zero words selects H-f5-stream or H-game-light-state, which remain split and require the next batched positive-control runtime probe of F5 color-state writes versus shade decode.

Exact audit commands:

`sed -n '430,540p' lib/rt64/src/gbi/rt64_gbi_rdp.cpp`

`rg -n "VTXCOLOR|MOVEMEM|shade|color" docs/F5-UCODE-REFERENCE.md docs/PROJECT-OVERVIEW.md`

`sed -n '19,90p' PORTING-STATE.md` is forbidden; use only the already-read s19/s20 windows and targeted grep if needed.

Expected result: no source change unless the equations contradict the reference. If they match, record the audit as a non-mitigation result and make the next unit a phase-gated, same-run probe that marks every F5 color-state update and pairs it with scoped shade-raw samples.
