# M5 s4937 — retail auxiliary ownership lookup

The bounded static lookup searched the companion symbol files, decomp tree,
generated `funcs_*.c`, and project symbols for all three destinations from
s4936. It made no runtime or build changes.

| destination | store site | static owner/evidence | result |
|---|---|---|---|
| `0x80149702` | `0x800917C4`, `sb` | `D_80149702` in `undefined_syms_auto.txt`; companion notes identify it as the MusyX double-buffer toggle | named synth-route auxiliary state |
| `0x80149988` | `0x80091698`, `sh` | `D_80149988` in `undefined_syms_auto.txt`; `musyxSynthFrame` reads/writes output-block state | named synth-route auxiliary state |
| `0x8014998A` | `0x800916A4`, `sh` | `D_8014998A` in `undefined_syms_auto.txt`; `waitForMusyXAudioTaskDone` is documented as busy-spinning on this halfword | named synth wait/countdown state |
| `0x800A1778` | `0x800917F4`, `sw` | no companion symbol or named data definition; the only current generated reference is this store, adjacent to the countdown stores in `musyxSynthFrame` | route-family ownership, field name unresolved |

The generated code proves the stores are in `musyxSynthFrame` at
`funcs_24.c` lines 7996–8009, 8224–8228, and 8272–8276. The companion
`main_overlay.txt` describes that function as the per-frame MusyX synth tick
and names the route/task object `aspTask` at `0x80149470`; it does not name
`0x800A1778`.

This selects H-route-state over H-render-or-input for the captured writer:
the named destinations are audio-synth state and the unresolved destination is
written by the same synth tick. Exact semantics for `0x800A1778` remain
single-source static evidence; no value filter, rewrite, or mitigation is
authorized. The next discriminator must join this store with the port's
`musyxSynthFrame`/`aspTask` route state in a phase-gated run.
