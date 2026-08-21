# NEXT work unit (s2079)

HYPOTHESIS-ID: m5-port-fill-crash-origin

## Work unit

Perform one bounded port crosswalk of the `fillSampleStreamRange` crash label,
the generated symbol range, and the separate `0x8000B650` last-guest-PC marker.
This is a source/metadata audit only: do not build, run the game, change task
fields, output routing, canary handling, waits, guards, gate stores, or host
behavior. The purpose is to classify the port-only boundary exposed by s2078
before another C88=1 treatment arm is considered.

## Competing hypotheses and discriminator

- **H-StaleLastGuestPC** — `0x8000B650` is outside the generated
  `fillSampleStreamRange` interval, and the `+336`/`+6464` labels resolve to
  different guest addresses. The port's last-PC breadcrumb is stale or comes
  from an unrelated guest-side event; it is not a retail fill contract.
- **H-HostCopyReadback** — the function label is a host-stack or host-boundary
  context, and existing RT64 copy/readback diagnostics identify the fault while
  the guest symbol arithmetic remains valid. The crash is port-host-side, not
  a missing retail call site.
- **H-SymbolCrosswalkMismatch** — the generated symbol/overlay metadata maps
  the function or offsets differently from `syms/rogue_squadron.syms.toml`.
  A contradictory generated range or overlay mapping selects this and requires
  metadata repair before any treatment change.

The discriminator is one exact address table plus the existing crash-family
and host-boundary breadcrumbs: symbol base, declared size, base+336,
base+6464, and whether `0x8000B650` lies in that interval. A consistent range
that excludes `0x8000B650` selects H-StaleLastGuestPC; a matching host
copy/readback attribution selects H-HostCopyReadback; contradictory generated
metadata selects H-SymbolCrosswalkMismatch. Do not infer from the retail PC
null again; s2078 already qualified that null with whole-RDRAM, PIF, VI, and
slot-cycle controls.

## Exact commands

Run from the repository root:

```sh
rg -n -C 2 'name = "fillSampleStreamRange"|fillSampleStreamRange|8000B650|last-guest-pc|fillSampleStreamRange\+(336|6464)' \
  syms docs src lib tools scratch/agent/soak_results PORTING-STATE.md | head -240
printf 'fillSampleStreamRange+336 = 0x%08X\n' $((0x8008FAAC + 336))
printf 'fillSampleStreamRange+6464 = 0x%08X\n' $((0x8008FAAC + 6464))
printf 'fillSampleStreamRange end = 0x%08X\n' $((0x8008FAAC + 0x500))
```

Record the exact symbol base/size, the two offset addresses, the location of
`0x8000B650` relative to the declared interval, and any independent host
copy/readback attribution. If the address table selects H-StaleLastGuestPC,
the next unit after this audit may add one regeneration-stable host/guest
boundary witness; it may not change a wait, guard, task ABI, or output route.
