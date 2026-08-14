# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); detailed session records stay
in the ledger. Reviewed through s1139 (2026-08-14).

## Current state

- Overlay dispatch is sufficiently fixed for mission entry and post-sec2
  outdoor presentation. The original boot/menu explanation is closed.
- Product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations are OFF. Any new mitigation requires an `ORIGIN:` naming the
  writer and assessing whether the value is legitimate.
- Phase-gated port captures can reach VI width 1024 with independent
  emit/raw/dispatch/match controls. Pre-chain crashes are disjoint families;
  they do not classify parser loss.
- Ordinary late E9 producer/consumer identity is established. Synthetic
  FULL_SYNC was absent in the decisive capture. Remaining deltas are
  boundary/span-shaped and the residual extended condition is unclassified.
- The recurring `slotDispatcherIter+872` SIGBUS is the generated prologue
  spill of guest `$sp` at `funcs_8.c:22810`. Direct callers and statically
  addressed indirect targets are balanced; `0x8010B350` is compiled data with
  no generated writer. General runtime caller-frame corruption remains open.
  The register-dump probe is landed and binary-verified; phase-positive
  no-event soaks did not classify the site.
- M5 audio de-stubbing is closed. Audio remains stubbed; do not reopen without
  a genuinely new lead.
- The port-side VI 640-to-1024 transition is lifecycle-driven. The host logger
  observes committed VI state correctly; the active mode bytes, copied records,
  and pending masks are ordinary runtime state, not an unobserved host write.
- Retail oracle controls remain healthy in completed runs: whole-RDRAM,
  scheduled PIF input, and VI callback/poll controls pass. The latest targeted
  M4 arm passed the whole-RDRAM control (10,000 callbacks, removed cleanly)
  and delivered all scheduled presses through 56 seconds, but stalled before
  any later VI transition at width 320/origin `0x006dd280`; its targeted
  `0x688:0x710` watch had zero hits and is unevaluable for the shaded phase.
  No hangar watch conclusion is valid.
- The no-target retail audit reproduced the post-56-second stall with the same
  whole-RDRAM control and all eleven presses. A process sample found the main
  emulation thread in `gen_interrupt → vi_vertical_interrupt_event → nanosleep`
  for 763/777 samples. This rules out the M4 target watch as the launch cause,
  but is single-run evidence for a core/emulator progress stall and does not
  make the retail M4 ownership watch evaluable.
- The independent `--oracle-emulator 1` audit also stopped at the initial VI
  width 320/origin `0x006dd280` after delivering all eleven presses. Its
  whole-RDRAM control reached 10,000 callbacks and was removed successfully;
  no later VI transition occurred through 180 seconds. This reproduces the
  stall across execution modes, but does not distinguish core scheduling from
  debugger/watch overhead and does not evaluate the M4 target range.
- The debugger-off, `--oracle-emulator 1`, VI-poll audit stayed at width 320 /
  origin `0x006dd280` for the full 180-second bound. All eleven presses were
  delivered and VI polling remained active, so debugger/watch overhead is
  ruled out as the launch cause. The core scheduling/state-path boundary is
  still open; the shaded M4 range remains unevaluable.

## Retail VI descriptor boundary

The active static chain is now:

`osTvType=1` → `rsViModeType=0` → NTSC descriptor index bytes →
`gameConfig+0x44=0x1800` → selector `A/B/C=1/0/0` → copied-record offset
`0xF0` → index-0 descriptor → width 320.

Evidence and boundaries:

- `librecomp::init` writes `osTvType=1`; `setViModeType` reads that address,
  not `osResetType`.
- The NTSC index window is ROM-backed and contains mixed 320/640/1280
  descriptors. The active selector must choose one of the 320 records.
- `gameConfig+0x44` has no audited writer and is `0x00001800` in the retail
  image. Its relevant bits produce selector bytes `A/B/C=1/0/0`.
- `initVideoSubsystem` initially loads the NTSC index-0 record into `sp+0x108`.
  The alternate overwrite families require `s7==0`; boot's stack-derived
  `s7` is nonzero, so index 0 is preserved.
- The four-record copy writes table offsets `0x00/0x50/0xA0/0xF0`, then
  reaches `osViSetMode_recomp` without an intervening selector or record store.
- At `0x8001B720`, generated code selects among `0x80128D50`, `0x80128DA0`,
  `0x80128DF0`, and `0x80128E40` using only stack bytes `0x15F` and `0x17F`.
  Boot's established `0x15F=0`/`0x17F=0` state selects `0x80128E40`, exactly
  `base+0xF0`.
- The host `osViSetMode_recomp` forwards `ctx->r4` unchanged to `osViSetMode`;
  the runtime stores the pointer and control, while the VI commit reads
  `common_regs->width` from that mode. No host-side width rewrite exists. This
  closes the active-descriptor pointer/consumer boundary with independent
  generated-code and host-runtime evidence.

## M4 zero-shade boundary

Independent Factor 5 command-reference and same-combiner evidence refute RT64
shade lane/order as the cause. The VTXCOLOR payload is nonzero, while decoded
shade is the fixed `0xFFFF8000` RGB / `0x00008000` alpha sentinel. Retail ROM
and generated code show the shaded emitter reads geometry/vector data rather
than the nearby color field. The missing-lighting/vector numeric origin before
`vmadh v6,v4,v0` remains unresolved. The prior controlled-null recipe is
superseded by the paired capture below; no mitigation is authorized.

The paired accumulator capture now has a valid port-side result. The independent
VMADH control fired 8 rows, and phase-6 target task 201 produced 16 complete
pre/post/VGE tuples and completed records. A local model matched the VMADH
result on all 128 lanes; VGE changed 0/128 lanes. The target records used
`r9` values in `0x00000670..0x000006C0`, with the captured output range at
`r9+0x18..0x4F`. The run did not reach VI-1024 (it remained at 640), so this
does not yet establish retail reachability or ownership of that range.

## M3 indirect-call frame audit

The s1140 whole-class source census found 144 static `jal 0x8003E8DC`
sites in 72 generated caller functions. 143 sites have an ordinary balanced
caller contract: each caller saves/restores `$ra`, has matching negative and
positive `$sp` adjustments, and calls the generated `slotDispatcherIter`
entry directly. `slotDispatcherIter` itself uses `sp -= 0x38`, saves `$ra` at
`0x34($sp)`, restores it, and returns with `sp += 0x38`. Its update callback
and `destroyNpcSlotByIndex`'s destructor callback are the only relevant
`LOOKUP_FUNC` sites; both expand to the standard `get_function(int32_t)` ABI
and invoke the returned `(rdram, ctx)` function pointer.

One site, guest `0x80078894`, is a generated-source anomaly rather than a
balanced reachable caller: it occurs in the `forwardToNpcGeneratorSpawn`
block after an unconditional emitted C `return` at `0x80077AEC`, before a
second `sp -= 0x118` prologue. The overlay table maps the named function at
`0x80077AC0` across this range, so static text alone cannot establish whether
the original MIPS entry was intentionally coalesced. This is single-source
static evidence and remains open as a mapping/generation follow-up; it is not
evidence of runtime stack corruption.

## Superseded conclusions

- s1105's `H-gate-stale-or-unseen-writer` was superseded by s1106's corrected
  physical-byte sample, which repeatedly observed nonzero `0x8011A8A0` at SP
  send boundaries. The old result was believable because the static census
  found no generated nonzero writer, but it did not measure non-generated
  runtime stores.
- s1119's claim that `setViModeType` maps `osResetType` was superseded by the
  generated load and symbol evidence showing `osTvType` at `0x80000300`.
- Earlier width-320 explanations based on a fixed selector, bad mode table,
  or a host logger mismatch are closed by the static chain and independent
  retail controls above.

## Evidence ledger summary

| Sessions | Durable result |
|---|---|
| s820–s880 | Post-sec2 accounting, breadcrumb, coalescer, and oracle routes classified or parked. |
| s881–s951 | M3 idiom inventories closed the audio-channel-field thread. |
| s952–s983 | Dispatcher stack-spill family localized; oracle callback work repaired later. |
| s984–s1013 | Shade decode/source/emission audits moved M4 to accumulator numeric origin. |
| s1014–s1038 | M4 controls repaired; controlled captures remained null and the recipe closed. |
| s1039–s1056 | Retail input/cadence controls passed; width-320 caller and selector dispatch were state-shaped. |
| s1057–s1079 | Hangar/selector/demo/controller boundaries were traced to the pre-main-loop state gate. |
| s1080–s1099 | Generated and retail-oracle audits localized the pre-main-loop path and closed callback delay-slot ambiguity. |
| s1100–s1111 | Port submit/gate probes passed controls but repeated captures lacked the VI-1024 phase; writer attribution stayed open. |
| s1112–s1117 | VI lifecycle and retail-oracle setup were corrected; retail remained width 320 with positive controls. |
| s1118–s1124 | Mode table, TV-type input, selector state, and mixed descriptor widths were reconciled. |
| s1125–s1129 | Boot config `0x1800`, selector `1/0/0`, preserved index 0, and boot-first ordering were resolved. |
| s1130–s1131 | First consumer ordering was resolved; this maintenance pass compacted the live file and migrated durable detail. |
| s1132 | Traced the active VI pointer to copied-table `base+0xF0` and closed host width-rewrite as a cause. |
| s1133 | Static census found `frameStartReset` fully regenerated with 14 call sites and overlay registration; no active fixup restoration exists, closing regeneration omission. |
| s1134–s1135 | Defined and executed the paired M4 port capture; VMADH model and VGE/store path matched on 128 lanes with an independent control. |
| s1137 | Reproduced the retail post-press stall with no M4 target watch; whole-RDRAM control and input passed, but the run never left VI width 320 and sampled in the core's VI-event sleep path. |
| s1138 | Reproduced the width-320 stall with `--oracle-emulator 1`; whole-RDRAM control and all eleven presses passed, so the stall is not specific to the prior execution mode. |
| s1140 | Audited all 144 static calls to `slotDispatcherIter`: 143 caller contracts balance; one `0x80078894` site is after an emitted return in a coalesced generated block and needs boundary resolution. |

## Ranked next steps

1. Resolve the single-source `forwardToNpcGeneratorSpawn` range anomaly:
   compare the ROM/decomp function boundaries and generated overlay entry for
   `0x80077AC0..0x80078DF4`, determining whether `0x80078894` belongs to a
   second MIPS function coalesced into unreachable C. If it is a generated
   target defect, identify the regeneration/fixup correction; if it is dead or
   intentionally coalesced, close it and proceed to a runtime-origin probe for
   the recurring `slotDispatcherIter+872` SIGBUS. Do not add a guard from this
   census.

The bounded frameStart/regeneration census is closed: `frameStartReset` is
present in generated output with its 0x8000A6CC body, 14 generated call sites,
the `funcs.h` declaration, and the overlay registration at offset 0xA28C with
size 0x190. The active fixup script contains no executable frameStart/reset
or site-restoration rule; its mentions are historical comments. This selects
H-regenerated and rules out regeneration omission as the explanation for the
isolated SIGBUS. The remaining fault-origin question is runtime-side and does
not justify a mitigation from this census.

## Method and safety rules

- Before runtime instrumentation, consult `tools/oracle/README.md` and
  `docs/F5-UCODE-REFERENCE.md`; arm a whole-RDRAM positive control.
- Gate animated comparisons on VI transitions; scope counters and log budgets
  to the phase; batch all instrumentation into one build/run.
- Use SIGKILL, launch from `build/`, and use capture paths whose final
  component does not begin with `.`. Queue repeat soaks rather than babysit.
- Diagnostics in generated code belong in fixup scripts. Regeneration order is
  `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then CMake.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. Changes under `lib/` require patch export.
- A null result is worthless without a positive control in the same run.
  Before any mitigation, name the writer and assess legitimacy with an
  `ORIGIN:` line.
