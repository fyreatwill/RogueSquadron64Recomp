# NEXT work unit (s2654) — M5 PCM publication edge: static OSTask output_buff audit

HYPOTHESIS-ID: m5-pcm-publication-edge

## Context

The generated-symbol-renaming sweep is CLOSED (s2653). M5 de-stubbing is now
the active thread (backlog #1). The blocking open question, established by
s2617–s2620, is: the generated tree has no direct static reference to the
retail PCM destination spans (`0x166450:0x169450`, `0x1798B0:0x179A48`), and
the host writer witness returns only zero-valued `kind=2, pc=0` rows. The
`H-ContractGap` hypothesis is selected but the missing edge is unlocated.

## Competing hypotheses and discriminator

- `H-OutputBuffNull`: the OSTask `output_buff` field submitted by the guest is
  null or zero; the Factor 5 image writes to it but the DMA produces zero bytes
  or an invalid destination, so the host PCM consumer never gets nonzero data.
- `H-OutputBuffValid`: `output_buff` is a legitimate RDRAM pointer that maps to
  the retail PCM span; the image DMA actually writes to it; the gap is in the
  host read-back (PCM consumer join logic) rather than the RSP write.
- `H-ImagePCMSilent`: the image task computes audio but writes zeros because
  its input data (voice/sequencer tables) is not populated by the port guest;
  the image DMA is well-formed but the payload is legitimately zero.
- `H-PortFuncMissing`: the port-side equivalent of retail `0x800078EC`
  (`rs_memset` writing the PCM span) is never called because the guest function
  that submits the OSTask with a valid `output_buff` is blocked or not reached.

The discriminating observation is a static read of the OSTask structure fields
submitted for `M_AUDTASK`: specifically the `output_buff` field value and its
relation to the known retail PCM span addresses. This distinguishes
`H-OutputBuffNull` from `H-OutputBuffValid` without a build, and narrows the
scope of any runtime experiment needed to split the remaining hypotheses.

## Exact checks (static analysis — no build needed)

1. In the generated mission funcs, find where the OSTask for `M_AUDTASK` is
   populated. Grep for `osSpTaskLoad\|osCreateMesgQueue\|M_AUDTASK\|0x0007\|
   musyx.*submit\|musyxSynthFrame\|submitAudioTask` in the generated source.
2. Read the OSTask struct field layout (from libultra headers or companion
   source) to identify `output_buff` byte offset within the task block.
3. Grep the generated funcs for stores at `output_buff` offset from whatever
   base pointer is used when constructing the audio task. Record the value
   expression — is it a compile-time constant, a pointer arithmetic expression,
   or a guest memory address?
4. Compare the recovered address expression against the retail PCM spans:
   `0x166450:0x169450` (12 288 bytes) and `0x1798B0:0x179A48` (0x198 bytes),
   adjusted for RDRAM physical-to-KSEG0 offset (`+0x80000000`).
5. If a concrete pointer is found, check if it overlaps the RDRAM range that
   the oracle confirmed receives retail writes. If it is zero or null, that
   selects `H-OutputBuffNull`.

## Expected discriminating outcomes

- Static match between `output_buff` and retail span → `H-OutputBuffValid`;
  the next step is a runtime DMA-payload readback on a title run.
- Static null/zero `output_buff` → `H-OutputBuffNull`; next step is tracing
  the guest allocator that should provide it.
- No static OSTask construction site found → record the search boundary and
  pivot to the runtime instrument from s2616 (`audtask-dma-*` rows) to read
  the task fields at dispatch time.

Do not build anything this iteration. Do not repeat the title-zero census
(already done in s2619). Do not revisit `0x80094648`.
