# NEXT work unit (s2099)

HYPOTHESIS-ID: m5-audio-image-task-contract

## Work unit

Perform one bounded generated-source data-flow audit of the two exact
writeback paths selected in s2098. Start at the initial task-descriptor DMA
into `0x340..0x34F`, trace every read/write feeding DMEM `0x3F0` and `0x570`
before `L_1830`, and resolve the origins and uses of the destination fields
read at `[r2+0x44]` and `[0x348]+0x100`. Join the resulting intervals to the
qualified s2097 rows (`0x6F0/0x300`, `0xCB0/0x198`, zero payload, and changed
span `0x340..0xFCF`). This remains read-only; do not change runtime behavior
or add an instrument until independent retail ground truth has been asked for.

## Competing hypotheses and discriminator

- **H-InputZero** — the `0x3F0`/`0x570` inputs are zero-filled or otherwise
  legitimately silent in the observed treatment, so `L_1830` can produce the
  zero `0x6F0..0x9F0` payload even though it is an output transform.
- **H-RSPWriteLoss** — the input path supplies nonzero data and the generated
  transform should preserve some nonzero output, so the zero payload occurs
  after the guest computation or in the DMA snapshot/copy boundary.
- **H-ABI-Destination** — `[r2+0x44]` and/or `[0x348]+0x100` are task or
  command fields whose semantic contract is not host audio output staging;
  the source classification alone cannot identify the intended destination.

The discriminator is one complete data-flow table for both exact paths:
initial DMA source and destination, every intervening store, the values/ranges
read by `L_1830`, the resulting `0x6F0` interval, each destination-field
origin, and the matching observed row counts. A preserved nonzero source path
selects `H-RSPWriteLoss`; a zero/untouched input path selects `H-InputZero`;
an unresolved destination-field meaning retains `H-ABI-Destination` at the
ABI scope. Do not infer from `dmem_changed` or `source_nz` alone.

## Exact commands

```sh
rg -n '0x340|0X340|0x3F0|0X3F0|0x570|0X570|0x6F0|0X6F0|0xCB0|0XCB0|0x348|0X348|DO_DMA_READ|DO_DMA_WRITE|SET_DMA_MEM|SET_DMA_DRAM' build/factor5_ucode/factor5_ucode_b_recompiled.c
rg -n -C 10 'ori.*0x3F0|ori.*0x570|ori.*0x6F0|ori.*0xCB0|0x348\)|DO_DMA_READ|DO_DMA_WRITE' build/factor5_ucode/factor5_ucode_b_recompiled.c
awk '/^\[audtask-dma-range\]/ {d="";l="";p="";o="";for(i=1;i<=NF;i++){if($i~/^dmem=/)d=$i;if($i~/^len=/)l=$i;if($i~/^payload_nz=/)p=$i;if($i~/^output_overlap=/)o=$i} if(d=="dmem=0x6F0" || d=="dmem=0xCB0") print d,l,p,o}' scratch/s73_post_a_scene/m5-audio-step6r3-treatment/run.log | sort | uniq -c
rg -n -m 8 '^\[audtask-abi\]|^\[audtask-join\]' scratch/s73_post_a_scene/m5-audio-step6r3-treatment/run.log
```

If the static table cannot establish input values or destination semantics,
stop before adding a port counter: first run the retail oracle whole-RDRAM
positive control and a phase-gated physical watch for the corresponding task
descriptor/output fields. No output routing, task field, canary, gate, wait,
guard, queue policy, or default dispatch change is authorized by this unit.
