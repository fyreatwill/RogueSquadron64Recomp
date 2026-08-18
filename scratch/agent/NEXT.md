# NEXT work unit (s1935) — consume entry-2 soak

HYPOTHESIS-ID: vi1024-guest-never-requests

s1934 consumed both queued
`s1933_entry2_synth_exit` and
`s1933_entry2_synth_exit_b`.
Both died before `menu-entry`
siten=2. Same-run control
passed (tick 2/2/2,
`took_swap=1` twice,
`slot-alloc` ends
`0x8018D4A0/16`,
`[synth-exit]` n last=1280,
`[vi-cb-after]` n last=1152).
Zero `menu-entry` siten=2;
`osViSetMode` ends at `#6`.
Arm A is `findTileCopyId`
`height>0` SIGABRT (~27s,
last-guest-pc `0x8000b650`).
Arm B is catalogued
`fillSampleStreamRange+6464`
SIGBUS (~29s, last-guest-pc
`0x8000b650`). Last logged
synth completed; crash is
inside a later unlogged
window. **UNEVALUABLE** for
the entry-2 three-way split.
s1933 already closed last-
logged completion on the
crash flavor; this extends
it through n=1280 and adds
the `findTileCopyId`
signature. Still not the
s1931 entry-2 answer.

Do **not** rebuild.
Do **not** change the stride.
Do **not** re-read the crash
or #6-dead logs as entry 2.
No force-zero.

## Work unit — consume the queued soaks

Read the new
`scratch/agent/SOAK-RESULTS.md`
lines for
`s1934_entry2_synth_exit`
and/or
`s1934_entry2_synth_exit_b`
(enqueued this session; loop
runs up to two between
iterations). Logs:
`scratch/agent/soak_results/s1934_entry2_synth_exit_*/run.log`
and
`scratch/agent/soak_results/s1934_entry2_synth_exit_b_*/run.log`.

If both queue lines are
missing, the soaks did not
run — enqueue is already in
`scratch/agent/soak_queue/`
or `done/`; do not babysit a
repeat.

Same-run positive control:

- `site=tick-entry` / `tick-jal` /
  `tick-exit` 2/2/2 with
  `took_swap=1` twice
- `slot-alloc` ends
  `0x8018D4A0 count=16`
- `menu-entry` siten=2 AND
  `menu-spin` climbs
- `[vi-cb-loop]` n last > 0
  **and** `[synth-exit]` n last
  > 0 **before** entry 2 (if
  `synth-exit` is 0 the site
  missed)
- `[vi-cb-after]` n last > 0
  before entry 2 (same)

Then, after `menu-entry`
siten=2:

- last is `[synth-entry]`
  n=2560 (or later) with no
  matching `[synth-exit]` →
  H-synth-never-returned
- `[synth-exit]` fires for
  that n AND `[vi-cb-after]`
  does not increment past the
  last pre-spin value →
  H-stuck-later-slot
- `[synth-exit]` AND
  `[vi-cb-after]` both fire
  for that iteration AND
  `[vi-cb-loop]` stays frozen
  while `update_screen`
  climbs → H-recv-starved

Crash-family (no entry 2) =
UNEVALUABLE — enqueue, do not
babysit. `findTileCopyId`
SIGABRT (no entry 2) =
UNEVALUABLE — same, enqueue.
#6-dead (no `#7/#8`, no
entry 2) = UNEVALUABLE for
this split — same, enqueue.
s1932 last-logged n=1024
(#6-dead), s1933 last-logged
n=1152 (crash), and s1934
last-logged n=1280 (crash +
`findTileCopyId`) are closed
for those flavors.

**If both s1934 soaks miss
`menu-entry` siten=2 again,
do not enqueue a sixth
identical hunt.** Pivot: the
discriminator is the recv
after the VI-cb slot walk
(static CFG of
`viRetraceHandlerThread`
after `musyxSynthFrame`, or
a host-side hook that does
not need 180s `#7/#8`
survival). Five hunts since
s1931 have missed that
flavor.

Join key is log order: first
`menu-entry` siten=2 vs last
`[synth-entry]` /
`[synth-exit]` /
`[vi-cb-after]` /
`[vi-cb-loop]`.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

- Last-logged n=1280 completion
  on the crash / findTileCopyId
  flavors (s1934) — closed for
  those flavors; not the
  entry-2 answer.
- Last-logged n=1152 completion
  on the crash flavor (s1933)
  — closed for that flavor;
  not the entry-2 answer.
- Last-logged n=1024 completion
  on the #6-dead flavor (s1932)
  — closed for that flavor;
  not the entry-2 answer.
- VI-cb during the spin (s1931)
  — closed (H-viretrace-blocked).
- Mix-alive vs mix-dead vs
  song-loop after entry 2
  (s1930) — closed
  (H-mix-dead-during-spin).
- Cursor rarity / which jal
  re-attacks (s1929) — closed.
- Why playing-state never ends
  (s1928) — closed.
- Who writes slot+0 = 0x02 (s1927)
  — closed (H-keyon).
- Which slot index stays nonzero
  (s1926) — closed.
- Why `anyAudioSlotActive` returns
  0 (s1925) — closed (H-slot-stuck).
- Naming the two tick parents
  (s1923) — closed.
- AVF entry vs exit vs prologue
  after `#6` (s1921) — closed.
- Tick entry vs jal vs exit after
  AVF #2 (s1922) — closed.
- Entry 2 spin vs pre-spin vs
  early-return (s1924) — closed.
- Naming the `#10` osViSetMode
  site (s1919) — closed.
- The `0x80128EAD` / `$s0`
  swap-gate table (s1920) — closed.
- The s844-HEAD full code-content
  audit (s1890) — closed.
- The `ROGUESQ_SKIP_HANGAR_PROBE`
  A/B (s1890) — closed.
- H3a-lowpower (s1902) — closed.
- `vi1024-early-crash-not-stall`
  (s1918) — closed.
- A same-recipe `s790` run with no
  new measurement axis.
- Another gate-byte / slot-byte
  force-zero without `ORIGIN:`.
- Ask (b) from s1891 — still
  human-only.
