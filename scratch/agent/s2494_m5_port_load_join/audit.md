# s2494 M5 port `osSpTaskLoad` boundary

## Work unit

Added a phase-gated host probe at the port's owning `osSpTaskLoad_recomp`
implementation. The probe preserves the existing no-op behavior and logs the
task pointer plus type, data, output, and yield fields. The descriptor and
scheduler identity probes were retained as same-run controls.

## Controls and capture

- Debug target built successfully after moving the hook into the runtime's
  existing strong `osSpTaskLoad_recomp` definition; the project compatibility
  override could not link against that symbol.
- Qualified LLE route, boot-relative eight-Start schedule, title gate at 1024,
  and leave-gate capture reached the target 512 / `0x006AB400` phase.
- Port-load controls: 2 phase controls (1024 and 512); port-load rows: 512.
- Prior controls: 681 descriptor-control rows and 2 scheduler-id controls.
- The run ended in the pre-existing `recomp::do_rom_read` crash after the
  target rows had been captured; this does not invalidate the completed join.

## Joined result

At 512 / `0x006AB400`, the port emitted type-2 rows with
`task_ptr=0x80149470`, `data_ptr=0x80171E70` or `0x80173CB0`, `data_size=1`,
and zero output/yield pointers. These match the retail oracle's 477 target
rows at watched `osSpTaskLoad` PC `0x80033E3C`, which used the same task pointer
and data-pointer set (with the established retail size-1/2 variation).

The same port capture also emitted type-1 rows for `gspTask=0x800377C8`, with
graphics data/output fields. Those are the scheduler descriptor rows from
s2493, not the type-2 audio load boundary, so they must not be compared as the
retail audio task.

## Selection

`H-port-load-matches-retail` selected at the direct `osSpTaskLoad` boundary.
This refutes `H-port-load-differs-retail` and `H-port-load-not-reached` for the
qualified target phase. It also refutes the prior descriptor-to-load mismatch
as a contract defect: the descriptor and audio load are distinct legitimate
task objects. No task remap, output change, guard, or audio behavior change was
made.
