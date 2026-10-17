# Session 5335 — M4 exact-key comparison

The corrected two-arm run passed the required same-run controls. The retail
cxd4 arm used the task-keyed `RSM1`/`RSD1` dumps, a whole-RDRAM write watch,
and VI tracing; the port arm used the phase-gated 1024-to-512 recipe with the
M4 key marks.

Retail evidence:

- whole-RDRAM watch: 10,000 callbacks;
- VI control: 320, 640, 1024, and 512 widths, with target origin
  `0x006AB800`;
- 2,091 graphics tasks, 3,032,650 mid-task records, and 2,091/2,091
  completion joins;
- 1,215 graphics tasks contained a transient `-32768` VACC lane, while all
  2,091 task-end records had zero such lanes.

Port evidence:

- phase control reached 1024 width and the target 512-wide hangar route;
- 4,096 target key rows at origin `0x006AB400`, task `959`, split evenly
  between generated PCs `0x112C` and `0x17F0`;
- the port M4 positive-control marks fired.

The declared exact key is `(VI origin,width,task serial,RSP PC,step bucket)`.
No exact cross-arm join exists in this run. Retail task serials span 1–6532,
but its observed RSP PCs are `0x0088..0x0FE8`; neither port PC (`0x112C` or
`0x17F0`) occurs in the retail stream. The phase origins also differ
(`0x006AB800` versus `0x006AB400`). Thus H1 and H2 cannot be selected. H3 is
selected: both instruments are live, but their keys are not aligned at the
claimed shared boundary. This is not evidence for a writer, corruption, or a
mitigation; the VACC-producing instruction remains unnamed.

The first cxd4 attempt in this iteration is not evidence because its recipe
omitted the whole-RDRAM positive control. It was corrected and rerun before
this result was accepted.
