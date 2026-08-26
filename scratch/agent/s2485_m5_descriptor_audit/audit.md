# s2485 — later scheduler descriptor audit

## Question

Determine whether the stable later-task pointer `0x800377C8` is a normal guest
`OSTask`, a scheduler wrapper, or unresolved from the generated tree.

## Static census

- `syms/rogue_squadron.datasyms.toml` names `0x800377C8` as `gspTask`.
- The companion `rogue_squadron64` symbol file independently types `gspTask`
  as `OSTask` with size `0x40`.
- `spTaskSchedulerThread` constructs `0x800377C8` at `0x80019E0C`, passes it as
  the sole argument to `osSpTaskYielded` at `0x80019E14`, and uses the return
  value only as the yielded-status result. The same loop then loads and starts
  the separately held task pointer at `0x801372D8` (the corrected generated
  address expression is `0x80128D38`) through `osSpTaskLoad` and
  `osSpTaskStartGo`.
- The exhaustive generated-tree search found no guest-word read or write at
  `0x800377C8` or at its `0x40`-byte span. There is no wrapper-specific field
  access, copy, or alternate consumer attributable to this pointer.
- `OSTask` in the runtime is exactly a 0x40-byte union containing the sixteen
  32-bit guest fields: type/flags, boot code and size, ucode and size, ucode
  data and size, dram stack and size, output buffer and size, data pointer and
  size, and yield-data pointer and size. This is consistent with the symbol
  type and the ABI of `osSpTaskYielded`.

## Hypothesis result

`H-DescriptorIsOSTask` selected at the static descriptor boundary. The symbol
type and the API call provide two independent lines of evidence; the absence
of generated field accesses rules out a generated wrapper-specific access
pattern, but does not identify who populates the descriptor or whether its
fields are subsequently consumed by the host implementation.

## Next discriminator

Capture the 16 guest words at `0x800377C8..0x80037804` at the scheduler's
`osSpTaskYielded` call, joined to the event payload and the later
`osSpTaskLoad`/`osSpTaskStartGo` argument. A normal `OSTask` should show the
documented field pattern and a later consumer should use the same descriptor
identity or a field-derived task identity; all-zero/unstable words with no
writer join would select an unresolved population boundary instead.
