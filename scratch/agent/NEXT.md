# NEXT work unit (s1933) — consume entry-2 soak

HYPOTHESIS-ID: vi1024-guest-never-requests

s1932 landed `[synth-exit]` and
`[vi-cb-after]` (live in the
binary; same AUDIOTICK_TRACE
stride as `[synth-entry]` /
`[vi-cb-loop]`). Same-run
control passed (both fire from
n=0). The 180s inline run was
the **#6-dead** flavor (no
`#7/#8`, no `menu-entry`
siten=2): last logged n=1024
on entry/exit/loop/after
completed, so H-synth-never-returned
and H-stuck-later-slot are
REFUTED for that logged
iteration. That is **not** the
s1931 entry-2 answer.

Do **not** rebuild.
Do **not** change the stride.
Do **not** re-run s1932's
#6-dead log as if it were
entry 2. No force-zero.

## Work unit — consume the queued soak

Read the new
`scratch/agent/SOAK-RESULTS.md`
line for
`s1932_entry2_synth_exit`
(enqueued this session; loop
runs it between iterations).
Log:
`scratch/agent/soak_results/s1932_entry2_synth_exit_*/run.log`.

If the queue line is missing,
the soak did not run — enqueue
is already in
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
babysit. #6-dead (no `#7/#8`,
no entry 2) = UNEVALUABLE for
this split — same, enqueue.

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
