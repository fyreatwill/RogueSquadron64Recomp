# M5 s3769 — retail family execution edges versus target buffers

The regeneration-safe family-entry census was built once and run concurrently
for image (`ROGUESQ_AUDIO_UCODE=1`) and silent (`=0`) port arms. The retail
oracle ran beside them with whole-RDRAM and title/hangar VI controls.

## Controls

The oracle whole-RDRAM positive control reached its 10,000-callback threshold,
completed 90 seconds, and reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`. Both port arms reached those same two VI phases and each
emitted all three family-entry controls. No arm emitted a crash or abort
marker.

## Discriminator

The port census was phase-gated to title `0x00790400` and hangar `0x006AB400`.
Each arm produced the same table:

| Family | Title rows | Hangar rows | Rows with target-buffer argument |
|---|---:|---:|---:|
| `rs_strncpy` (`S`) | 64 | 64 | 0 |
| `initTextureLUTAndAllocBuffers` (`I`) | 0 | 0 | 0 |
| `loadTextureToMemory` (`L`) | 64 | 64 | 0 |

The target argument test covered the title buffer `0x80178C80..0x80178F80`
and hangar buffer `0x801797B0..0x80179A48`. The S/L rows instead carried
other object pointers; the I family had no target-phase entry. The retail
oracle independently executed the corresponding PCs in the target phases,
with 1,049 S, 449 L, and 1 I hit rows in the bounded printed output.

This selects `H-M5-RetailWriterFamilyOtherObject` for S/L and
`H-M5-RetailWriterFamilyAbsentTargetEdge` for I. It refutes a shared target
buffer execution edge for the three families, but does not yet prove whether
the S/L other objects are legitimate route inputs or an identity mismatch.
The entry census does not observe every internal store destination.

ORIGIN: diagnostic entry hooks only; no pointer, clear, payload, audio gate, or
guest state was changed. The known `0x800078EC` zero padding remains the only
observed target-span writer in the prior qualified capture.

Evidence: `scratch/agent/s3769_m5_family_edge/`, the retail oracle log in that
directory, and the regenerated hooks in the companion `N64Recomp` checkout.
