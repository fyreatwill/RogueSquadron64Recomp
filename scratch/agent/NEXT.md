# NEXT: generated-symbol sweep 0x8000A000..0x8000B000, unless the queued soak faults in copyToRAM

HYPOTHESIS-ID: generated-symbol-renaming-sweep

Context: PORTING-STATE s4531. The wild-width allow is parked. The firing event is SETCIMG `0xFFFB0408`/`0x41130393` (width 1033, fmt 7, addr `0x130393`) at RDRAM `0x4E2958`. `nativeReadbackBufferSize` equals `bufferOffset+bufferSize` (1400748). The death on that run is `fillSampleStreamRange+15116`, not `copyToRAM`. Do not add a skip. Do not enable `ROGUESQ_DROP_GARBAGE_CIMG`. Do not repeat a VI-512 run to arm `[s4298-odd]`: s4531 run A already reached VI 512 with `[rom-read]` 12450 and `[s4298-odd]` 0.

Before this unit, read new `scratch/agent/SOAK-RESULTS.md` lines. The queued recipe is `scratch/agent/soak_queue/s4532_allow_copytoram.sh`. Its game log is under `scratch/s4532_allow_copytoram_*`, not under `scratch/agent/`.

Exception, checked first: if that log's `[CRASH][pc-symbol]` contains `copyToRAM` AND the log has an `ALLOW_WILD_FL` line, do not sweep. Stay on `allow-wild-fl-writeback`. No rebuild. Read only that allow line and compare `nativeReadbackBufferSize` with `bufferOffset+bufferSize`.

- Equal, and the stack is `copyToRAM`: refutes H-short for that event too. The source pointer is then the open question. Do not add a skip.
- `nativeReadbackBufferSize` smaller than `bufferOffset+bufferSize`: selects H-short for that event. Still do not add a skip in that iteration; name the writer (already the s4531 SETCIMG unless the words differ) and stop.
- No allow line, or `pc-symbol` is not `copyToRAM`: the exception does not apply. Do the sweep below.

Sweep: one bounded lead, `0x8000A000..0x8000B000` (exclusive end), the lead s3796 named. Confirm the companion directory exists before running. If the last fifteen `## Session` titles are all sweep titles (they contain "synchronized", "confirmed ... symbol", or are a sweep-scoped census), do not take this step: do CURRENT-TRUTH item 2 (external retail-entry boundary) or the M4 accumulator boundary instead.

```
python3 tools/rename_generated_symbols.py \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  --companion-dir /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files \
  --start-address 0x8000A000 --end-address 0x8000B000
```

A row that renames is H2. Every row `already-synchronized` is H3 and the next lead is `0x8000B000..0x8000C000`. A tool failure or a missing companion file is not a census. A mapping-only edit does not reset the no-engineering gate; record the census, and do not chain another sweep in the same iteration.
