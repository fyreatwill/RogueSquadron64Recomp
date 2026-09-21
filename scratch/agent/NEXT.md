# Next: join input DMA to the interleaved image-stage task objects

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3673 selected `H-SameTaskInput` and `H-HangarZeroProducer` for the
watched source span: title rows used `0x80171CE0` with nonzero source bytes,
and hangar rows used `0x80171E70` with zero source bytes. The remaining open
boundary is whether the input-DMA route ordinal also selects the same object
for the interleaved image-stage destinations associated with
`0x80173B20`/`0x80173CB0`.

Competing hypotheses:

- H-StageSameTask: each stage-2/3 input DMA and its image-stage row carry the
  same live task data pointer and route ordinal.
- H-StageInterleaved: stage rows alternate to a different task pointer than
  the input DMA, despite the source-span match.
- H-HangarZeroStable: the hangar-zero input remains tied to `0x80171E70` in
  stage-2/3 rows.
- H-HangarZeroAlternate: stage-2/3 rows use one of the interleaved objects
  while the watched source-span input uses `0x80171E70`.

Discriminating measurement: add the active task data pointer to the bounded
`audtask-image-stage`/`audtask-image-stage-row` witness for stages 2 and 3,
then run one validated 55-second concurrent oracle/port capture. Join by
`(phase,width,origin,route_ordinal,route_row,stage)` and compare pointer plus
source/post-DMEM hash. Matching pointers select H-StageSameTask and stable
hangar `0x80171E70` selects H-HangarZeroStable; alternate pointers select the
corresponding interleaved hypotheses. Require whole-RDRAM, title, hangar,
RSP-source-hook, type-2, and stage-row positive controls. Before building,
read the existing stage callback signature and env catalog; build both no
behavioral arms in one build/run. No guest-state rewrite or mitigation.
