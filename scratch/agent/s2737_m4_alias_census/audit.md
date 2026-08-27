# Session 2737 M4 absolute-DMEM alias census

## Discriminator

Enumerate every generated `0xB00/B02/B04` and `0xC70/B74` memory access and
classify it by addressing mode. The competing outcomes were: (1) additional
absolute-DMEM producers or consumers outside the known M4 path, (2) only the
known producer/index-reader/indirect-consumer path, or (3) pointer-relative
hits falsely merged with M4. A complete source census plus the bounded M4
source window splits those outcomes without adding a runtime probe.

## Evidence

The generated snapshot contains one absolute-DMEM M4 table producer at
`0x8002642C..0x80026434` and one absolute-DMEM indirect consumer at
`0x80026644..0x8002664C`. The producer writes three halfwords at
`0xB00+r7`, `0xB02+r7`, and `0xB04+r7`, then advances `r7` by six. The
consumer loads the same three fields after deriving its table byte offset
from `MEM_BU(MEM_BU(0, 0xC70), 0xB74)` and masking the selected value.

The same bounded path writes the selector state at `0xC70` and `0xB74` and
reads it before the indirect load. All other generated hits found by the
census use a nonzero register base, so they are pointer-relative object
fields, not the absolute-DMEM M4 table. No additional absolute-DMEM table
writer, reader, or consumer was found.

## Result

`H-known-M4-path-localized` is selected: the absolute-DMEM producer, selector
state, and indirect consumer are a single generated path, while the other
hits are unrelated pointer-relative fields. This rules out the proposed alias
merge and does not prove which selector value is live in the qualified scene.
The remaining discriminator is dynamic producer-slot versus consumer-index
equality; no mitigation, writeback, remap, or runtime instrumentation is
authorized by this static result.

Evidence: the complete generated-snapshot `rg` census and the bounded
`funcs_7.c` window covering `0x8002642C..0x8002664C`.
