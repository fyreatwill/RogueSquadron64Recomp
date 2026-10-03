# M5 s3768 — retail writer families versus port edges

The bounded static audit identified the retail source-span writer families and
their generated port bodies:

| Retail PC/family | Generated port body | Static role |
|---|---|---|
| `0x80007670` | `rs_strncpy` in `funcs_2.c` | byte padding after string termination |
| `0x8001E2C0` | `initTextureLUTAndAllocBuffers` in `funcs_6.c` | zeroes texture-table records at stride `0x24` |
| `0x8001FACC`–`0x8001FD2C` | `loadTextureToMemory` in `funcs_6.c` | populates texture-table record fields and derived offsets |

The generated port therefore has corresponding code edges, but the qualified
s3767 target-phase capture did not show those edges writing either target
buffer (`0x178C80` title or `0x1797B0` hangar). Its only target-span writer was
the later zero-valued `0x800078EC` `rs_strncpy` padding loop, after the
legitimate `0x8008F2CC` clear. The independent retail arm passed its whole-
RDRAM control, reached both target phases, and recorded the writer families
and nonzero title snapshots.

This selects `H-M5-RetailWriterPortEdgeAbsent` for the measured target-buffer
phase, not a global claim that the generated functions are unreachable. It
refutes `H-M5-RetailWriterHasPortEdge` for the joined target buffers. The
evidence does not distinguish a missing execution edge from a buffer/route
identity mismatch, so `H-M5-RetailWriterJoinMismatch` remains open.

ORIGIN: no mitigation, clear suppression, value injection, or guest state
change was made. The observed `0x800078EC` writer is legitimate zero padding;
the missing nonzero writer remains unexplained.

Evidence: `docs/M5-S3767-POSTCLEAR-PRODUCER-ORDER.md`,
`docs/M5-S3670-REMAINING-STORE-CONTEXT.md`, the generated bodies in
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/`, and
`scratch/agent/s3767_m5_postclear_order/image.log` plus `oracle.log`.
