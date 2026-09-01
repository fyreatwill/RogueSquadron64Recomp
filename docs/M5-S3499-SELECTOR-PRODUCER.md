# M5 Session 3499 — selector producer comparison

The independent retail oracle ran first with a whole-RDRAM write control,
Rice video, title-driving Start presses, and execution watches covering the
predecessor range plus `0x80091060`/`0x80091074`. The control recorded
1,013,172 writes; the selector boundary was live at title origin
`0x00790400`, including 1,661 executions of the producer entry.

The port used the qualified `ROGUESQ_AUTOPILOT=1`, real-image, LLE-only,
spin-yield route. Title, selector-load, and selector-writer controls all
fired. The new witness at `0x80091038` recorded 1,024 producer rows alongside
1,024 load and writer rows. Port producer inputs included alternating
`a0=0x801772F0`/`0x80175960` and `a1=0/1/...`; retail rows at the same title
boundary showed `a0=0x801772F0`, `a1=0x2`, `a2=0x1`, with the known retail
selector source family.

The first measured producer/input class differs across runtimes. This selects
`H-ProducerDivergence` and rules out an absent producer hook or downstream-only
explanation at this boundary. It does not identify the caller or writer that
supplies the differing `musyxBuildVoiceCommandList` inputs.

The first port launch was invalid because it used the Windows-style
`build/Debug` path. A corrected run without autopilot crashed at `0x8000834C`
before title. Neither is selector evidence; the final qualified run is the
result above.

ORIGIN: the producer witness is diagnostic-only. Its table-word byte-order
formatting was corrected after capture and the executable rebuilt; the
selection relies only on independently controlled execution and register
fields, and no selector, task field, audio state, or output was rewritten.
