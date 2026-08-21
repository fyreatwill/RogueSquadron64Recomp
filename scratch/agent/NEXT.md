# NEXT work unit (s2098)

HYPOTHESIS-ID: m5-audio-image-task-contract

## Work unit

Perform a bounded generated-source audit of every reachable `DO_DMA_WRITE` in
`build/factor5_ucode/factor5_ucode_b_recompiled.c`. Join each callsite's
`SET_DMA_MEM`, `SET_DMA_DRAM`, and `DO_DMA_WRITE` register path to the qualified
s2097 treatment observations: `dmem=0x6F0 len=0x300` and `dmem=0xCB0 len=0x198`,
zero payload, zero output overlap, and the final DMEM changed span
`0x340..0xFCF`. This is read-only analysis; do not build or change runtime
behavior unless the source audit finds a concrete regeneration-independent
diagnostic gap.

## Competing hypotheses and discriminator

- **H-OutputWriter** — the observed DMA writes source bytes from the generated
  task's mutated output span and their DRAM destinations are the intended
  output staging range. A nonzero expected source span with a zero host payload
  would move the boundary to DMA-copy/input semantics.
- **H-ScratchWriter** — the observed writes source untouched or zero-filled
  DMEM ranges used for scratch, metadata, or padding, not the generated output
  loops. A static mapping to those ranges confirms the zero-payload staging
  boundary.
- **H-ABI-Field** — the DMA destination or source register path is derived from
  task/voice fields whose meaning is not the host output contract. A register
  path that cannot be joined to the observed ranges without an unresolved task
  field leaves the ABI boundary open.

The discriminator is one complete callsite table: every reachable write
callsite, the register/value expressions feeding MEM/DRAM/LEN, the resulting
DMEM interval, the resulting DRAM interval, whether it intersects
`0x340..0xFCF`, and whether it matches either observed range. A source mapping
to a mutated span with nonzero expected input selects `H-OutputWriter`; a
mapping to untouched or zero-filled DMEM selects `H-ScratchWriter`; an
unresolved task/voice-field derivation selects `H-ABI-Field`. Do not infer
from a single callsite or from the zero payload alone.

## Exact commands

```sh
rg -n 'SET_DMA_MEM|SET_DMA_DRAM|DO_DMA_WRITE' build/factor5_ucode/factor5_ucode_b_recompiled.c
awk '/SET_DMA_MEM|SET_DMA_DRAM|DO_DMA_WRITE/ { for (i=NR-14; i<=NR+14; ++i) keep[i]=1 } keep[NR] { print NR ":" $0 }' build/factor5_ucode/factor5_ucode_b_recompiled.c
awk '/^\[audtask-dma-range\]/ { n=""; d=""; l=""; o=""; p=""; for(i=1;i<=NF;i++){if($i~/^n=/)n=$i;if($i~/^dmem=/)d=$i;if($i~/^len=/)l=$i;if($i~/^dram=/)o=$i;if($i~/^payload_nz=/)p=$i} if(n!="") print n,d,l,o,p }' scratch/s73_post_a_scene/m5-audio-step6r3-treatment/run.log | sort | uniq -c
```

Record the full callsite table, the matching/ambiguous rows, and the exact
reason any register path cannot be resolved. No output routing, task field,
canary, gate, wait, guard, queue policy, or default dispatch change is
authorized by this unit.
