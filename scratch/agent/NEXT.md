# NEXT work unit (s1946) — why siServiceThread stops after Start #4

HYPOTHESIS-ID: hangar-after-title-1024

s1945 selected H-poll-stopped:
`poll_input` / `get_n64_input`
die after Start #4. Last
`[pad-sdl] site=poll` n=1408
at `update_screen #1408`; last
`[host-start]` n=1309; Starts
26–56 never become pad-sdl or
pad-host. Unique
`osContStartReadData` caller
is `siServiceThread`
`0x80002E10` (`funcs_0.c`).
Loop: `L_80002EA0` Recv →
StartQuery → Recv → GetQuery →
StartReadData → Recv →
GetReadData →
`processPolledControllerData`
→ SendMesg → `L_80002EA0`.

H-title-ignores-start still
holds for the two Starts that
did reach title 1024.

## Competing hypotheses

- **H-si-recv-after-read** —
  last StartReadData ran
  (poll n=1408); the following
  `osRecvMesg` never returns,
  so GetReadData / loop-top
  never run again.
- **H-si-loop-recv** —
  the post-read Recv and
  GetReadData complete; the
  next `L_80002EA0` Recv
  never returns.
- **H-si-exited** —
  `siServiceThread` returns
  (or is destroyed) after
  the last iteration.
- **H-si-other-path** —
  the thread stays in the
  function but skips
  StartReadData (query/error
  path, or stuck earlier
  than StartReadData).

## Work unit — one rebuild

Land always-on `[si-thr]`
sites on `siServiceThread`
(fixup, not a hand-edit of
`funcs_0.c`):

- `site=loop` at `L_80002EA0`
  after the Recv returns
- `site=start-read` just
  before `osContStartReadData`
- `site=after-read-recv`
  after that Recv returns
- `site=get-read` just
  before `osContGetReadData`
- `site=send` after
  `osSendMesg`
- `site=exit` on the
  function epilogue if one
  exists (else log that
  there is no return)

Include `vi_width`/`origin`.
Rate-limit first 16 then
every 32. Do **not** edit
`lib/`. Do **not** inject
pad bits. Do **not**
default-on `ROGUESQ_SPIN_YIELD`.

Same Debug binary otherwise.
One soak: `ROGUESQ_SPIN_YIELD=1`
+ s1943 eleven-Start from boot
+ the same passive instruments
as `s1945_pad_sdl_after_title`.

```
# after the rebuild:
zsh scratch/agent/soak_queue/s1946_si_thr_after_title.sh
```

Write that script this iteration
before launching. Crash / #6-dead
/ 640 stall = enqueue another
copy, do not babysit.

Same-run positive control
(must fire **before** any
stop claim):

- tick-entry/jal/exit at least
  2/2/2 with `took_swap=1` twice
- `slot-alloc` third row
  `0x8018D4A0 count=16`
- `[spin-yield]` n=1
- `[phase] 1024 origin=0x00790400`
- `[si-thr] site=start-read`
  and `site=get-read` fire
  **before** that 1024
- at least one `[pad-sdl]`
  Return KEYDOWN and one
  `[pad-host]` Start before
  that 1024

After that control, look at
the last `[si-thr]` site
after Start #4 (`pad-host`
n=4 / poll ~1408):

- last site=`start-read`,
  no matching
  `after-read-recv` →
  **H-si-recv-after-read
  SELECTED**
- last site=`after-read-recv`
  or `get-read` or `send`,
  then a `loop` with no
  further `start-read` →
  **H-si-loop-recv SELECTED**
- `site=exit` fires →
  **H-si-exited SELECTED**
- last site is before
  `start-read` (loop /
  StartQuery / GetQuery)
  with no later start-read →
  **H-si-other-path SELECTED**
- `[phase] 512 origin=0x006AB400`
  or `0x006AB800` →
  **H-hangar-reachable SELECTED**

Do **not** repeat s1943–s1945
eleven-Start as a hangar
recipe without this SI-thread
split. Do **not** land
spin-yield as default.
Ask (b) from s1891 — still
human-only.

Run from `build/` with the ROM
present. SIGKILL.

## Sweep leftover (parked, not this unit)

`func_800F7130` → `renderNpcAnchoredProceduralEffect`
(TOML `0xB44` already matches generated `rom_size`).
Four-step already complete in s1906–s1917.

## Do not repeat

- s1942 yield off/on A/B (closed).
- s1942 from-phase-1024 Start/A
  as a hangar recipe.
- s1943–s1945 eleven-Start-from-boot
  as a hangar recipe without the
  siServiceThread stop split.
- Force-zero slots.
- `requeue_vi=true` as the only
  arm.
- Ask (b) from s1891 — still
  human-only.
