# M3 s3595 — MusyX voice `+0x30..+0x40` field audit

## Work unit

Static census of every generated access to offsets `0x30`, `0x34`, `0x38`,
`0x3C`, `0x40`, `0x42`, and `0x44` in `../N64Recomp/RecompiledFuncs/funcs_24.c`.
No build or runtime run was performed.

## Census

The generated access list is not one object layout:

- `musyxInitVoiceFromSample` computes a voice-slot pointer from the global
  voice base plus an index-derived `0x88` stride. It initializes the slot and
  writes `+0x34`, `+0x38`, `+0x3C`, and `+0x40` as words from the sample
  descriptor, after resetting the slot's `+0x44` halfword. The index is masked
  to 16 bits, but the generated function only proves the base address range;
  it does not prove that the caller's index is below the 64-slot table bound.

- `musyxKeyOnVoice` uses `s0` as the source voice/configuration record and
  `s1` as a per-voice command/sample record. It reads source `+0x30`,
  `+0x34`, `+0x38`, `+0x3C`, `+0x40`, and `+0x44`, then writes destination
  `+0x30`, `+0x34`, `+0x38`, `+0x3C`, `+0x40`, `+0x42`, and `+0x44` with
  mixed widths. Destination `+0x3C`/`+0x3E` are byte fields in one
  descriptor layout, while `+0x3C`/`+0x40` are also word/halfword fields in
  other layouts.

- `musyxRenderVoiceSamples` reads `+0x34`, `+0x38`, `+0x3C`, and `+0x40`
  from the sample/stream descriptor and updates voice-side `+0x34`, `+0x3C`,
  `+0x40`, and `+0x30` fields. Its `r29` accesses at these offsets are stack
  saves/restores, not voice fields.

- `musyxStartVoiceRelease` computes the same global voice-table address from
  the supplied index and reads/writes `+0x30`. `setVoiceModulationParams` and
  the related fade/release path likewise compute the table address and
  access `+0x30`, without exposing an object-level bound beyond the masked
  index and base guard.

- `musyxStoreVoiceAdsrParams` computes a global voice-table slot and writes
  descriptor-derived values to `+0x30`, with adjacent `+0x28`/`+0x2A`/
  `+0x2C` fields. This is a separate voice-table layout from the command
  descriptor used by `musyxKeyOnVoice`.

- `musyxBuildVoiceCommandList`, `musyxMixActiveVoices`, and `musyxSynthFrame`
  have matching offset text only in stack-frame saves or in calls into the
  routines above; no additional unchecked voice-field writer was found.

## Result

`H-NextClassGap` is not selected: the census found no concrete wild value,
invalid writer, or demonstrably unchecked store-to-consumer edge. Reset and
cleanup stores are legitimate zero/state transitions, and descriptor values
are copied from identified inputs.

`H-NextClassComplete` is not selected: the generated code does not establish a
single shared object layout, complete caller-proven index bounds, or runtime
allocator/lifetime legitimacy for every access.

`H-NextClassUnevaluable` is selected. The independent evidence lines are (1)
the complete offset/type/base access enumeration and (2) the control-flow
derivation showing distinct global-table, source-descriptor, command-record,
and stack bases. The remaining boundary is runtime index/lifetime/value
legitimacy, not a newly identified writer. No guard or mitigation was added.
