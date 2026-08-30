# Session 3282 — menuOverlayInit re-enters; 17 s jal is a second mainGameLoop call

HYPOTHESIS-ID: m5-osvimode-menu-entry-vs-jal

## Competing hypotheses

- `H-MenuWaitBeforeTick`: `menuOverlayInit` entry `0x800C58A0` fires
  well before 17 s; jal `0x800C5A18` is delayed until ~17 s.
- `H-LateMenuEntry`: first `0x800C58A0` exec is at ~17 s, immediately
  before the jal. Port's 320-phase `menu-entry` is the wrong-time
  invocation.
- `H-MenuReentry`: two (or more) `0x800C58A0` entries; the 17 s jal
  belongs to a later activation.
- `H-EntryCoverageInvalid`: whole-RDRAM control or title 1024 gate
  missing, or neither PC fires.

## What ran

One independent retail Rice oracle, 25 s, eleven-Start. Watches are
physical. Exec watches armed at first VI (no `--pc-phase-log-width`).
Exact recipe in `scratch/agent/NEXT.md` (pre-run).

```
tools/oracle/build/rs64_oracle
  --watch-write 0x0:0x800000
  --watch-pc 0x800C58A0,0x800C5A18
  --secs 25 --hit-cap 10000 --vi-trace --vi-poll
  --video rice
```

No audio behavior change. No M5 Step 3. No `PatchesLib` build.

Capture: `scratch/agent/s3282_menu_entry_vs_jal.log`.

## Same-run positive controls

- Whole-RDRAM watch reached 10000 and was removed (`rc=0`); index 1
  remained armed.
- `[gpr-ctl]` fired (first breakpoint, a write at `0x8002b608`).
- Exec watch at jal `0x800C5A18` fired twice (lifetime
  `execution watch hits: 4` across both PCs). The 17.0 s jal is
  enough to prove the watch.
- Title `1024 @ 0x00790800` at 17.3 s, then `0x00790400`.
- 1462 VI, 25.1 s wall / 24.4 s emulated. `rc=0`.

## VI

| t | event |
|---|---|
| 0.7 s | 0 → 320 |
| 1.7 s | 320 @ `0x006ba280` |
| 2.3 s | 320 → 640 @ `0x0066A500` |
| 6.4–16.5 s | still 640; origins cycle |
| 17.3 s | 640 → 1024 @ `0x00790800` |

## Exec hits

| t | pc | `prev_pc` | live VI | `$a1` | `$a2` | `$v0` |
|---|---|---|---|---:|---:|---|
| 2.0 s | `0x800C58A0` entry | `0x8003E08C` (`mainGameLoop` jal) | 320 @ `0x006dd280` | 9 | 0 | `0x1` |
| 2.0 s | `0x800C5A18` jal | `0x800C5A14` (fall-through) | 320 @ `0x006dd280` | — | — | `0x8000` |
| 17.0 s | `0x800C58A0` entry | `0x8003E13C` (`mainGameLoop` jal) | 640 @ `0x0062c200` | 2 | 0 | `0x0` |
| 17.0 s | `0x800C5A18` jal | `0x800C5A14` (fall-through) | 640 @ `0x0062c200` | — | — | `0x28000` |

`exec-prev` lifetime: entry `prev=0x8003e08c n=1`, `prev=0x8003e13c n=1`;
jal `prev=0x800c5a14 n=2`. Both entries are `mainGameLoop`
(`0x8003DFA0`, size `0x5BC`), not cinematic overlay-alias.

Generated `mainGameLoop` sites that `jal 0x800C58A0`:

| site | delay-slot args | this run |
|---|---|---|
| `0x8003E08C` | `$a1=9`, `$a2=0` | 2.0 s entry |
| `0x8003E0CC` | `$a1=2`, `$a2=0xB` | no entry |
| `0x8003E13C` | `$a1` 1 or 2, `$a2=$s0` | 17.0 s entry |
| `0x8003E220` / `E434` / `E494` / `E4EC` / `E530` | later sites | no entry |

The 17 s jal is the post-cinematic `0x8003E13C` call, not a delayed
jal inside the 2.0 s activation, and not the `0x8003E0CC`
`(s3, 2, 0xB)` site (that site produced zero entries).

s3278's port `menu-jal` n=1 during VI 320 matches the 2.0 s first
activation. The port never reaches `0x8003E13C`.

## Classification

- `H-EntryCoverageInvalid` refuted: 10000-write control, title 1024,
  both PCs fired, `[gpr-ctl]` fired.
- `H-MenuWaitBeforeTick` refuted: first entry at 2.0 s hits the jal
  in the same 0.1 s bucket. The 17 s jal is not a wait inside that
  invocation.
- `H-LateMenuEntry` refuted: first `0x800C58A0` is at 2.0 s (VI 320),
  not at 17 s.
- `H-MenuReentry` selected: two entries, two immediate jals. The
  1024-edge tick is the second `mainGameLoop` activation (`$a1=2` at
  `0x8003E13C`). Combined with s3278: the port ran the first
  activation and is missing the second.

Because `0x8003E13C` executed at 17.0 s, the first call returned
before that. The occupant of the 15 s gap (cinematic inner loop vs
a long first `menuOverlayInit`) is the next discriminator.
