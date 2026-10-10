# NEXT: classify [s4532-fill] kind=bad, else sweep

HYPOTHESIS-ID: odd-dma-node-field

The probe is already linked. Do not rebuild. Before this unit, read new `scratch/agent/SOAK-RESULTS.md` lines. The queued recipe is `scratch/agent/soak_queue/s4532_fill_devaddr.sh`. Its game log is `scratch/s4532_fill_edge_*`.

Context: PORTING-STATE s4532. The odd DMA is raw_r7 `0x6C637265`, size `0x300`, at the 512-to-640 edge. `fillSampleStreamRange` writes that devAddr. FE04 is not it (size constant `0x600`, confirmed by a same-run ctl). FE98 writes node+8 and sizes from node+0x10. FB64 writes node+8+node+0x10. Run A controls: FE98 `dev=0x00F00C00` `w8=00F00C00` `w10=00000100`, then FB64 `dev=0x00F00D00` on the same node `0x80192F10`. The value is not legitimate. Do not add a skip.

If the soak log contains `[s4532-fill] kind=bad`:

- site `FE98` and `dev=0x6C637265` and `w8` equals dev and `w10` equals size: selects H-FE98. node+8 is the garbage field. Stop. Do not add a skip.
- site `FB64` and `dev=0x6C637265` and `w8+w10` equals dev: selects H-FB64. The addend that is not a small ROM offset or a small cursor is the garbage field. Stop. Do not add a skip.
- site `FE04`: contradicts the size-constant result. Quote the size field and stop.
- no such line, and the crash is the `do_rom_read` odd assert: selects H-other. The request was not this value at the three stores. Do not re-instrument in that iteration.
- crash stack is `fillSampleStreamRange` and there is no `kind=bad`: the parked bus error. Do not treat it as this join.

If the soak did not crash, or it died before VI 1024: the edge was not reached. Do not re-run the recipe. Take the generated-symbol sweep:

```
python3 tools/rename_generated_symbols.py \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
  --start-address 0x8000A000 --end-address 0x8000B000
```

Change `HYPOTHESIS-ID` to `generated-symbol-renaming-sweep` in that case. A row that renames is H2. Every row `already-synchronized` is H3 and the next lead is `0x8000B000..0x8000C000`. If the last fifteen session titles are all sweep titles, do CURRENT-TRUTH item 2 instead.
