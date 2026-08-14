# NEXT work unit (s1141)

HYPOTHESIS-ID: m3-generated-boundary-anomaly

Perform one bounded static boundary audit of the generated
`forwardToNpcGeneratorSpawn` range. Do not build or run the game. Determine
whether guest `0x80078894` is a real second MIPS function entry coalesced into
the `forwardToNpcGeneratorSpawn` C body or dead code after the emitted return:

```sh
rg -n 'forwardToNpcGeneratorSpawn|80077AC0|80077AF0|80078894|800789FC' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs /Users/williambuckley/Documents/Tools/N64Recomp --glob '!funcs_*.c' --glob '!PORTING-STATE.md'
sed -n '19660,19725p;22440,22470p' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_18.c
```

Competing hypotheses and the discriminating measurement:

- H-coalesced-real: the ROM/decomp or function table identifies a distinct
  entry near `0x80077AF0`, proving the emitted C return/body boundary is a
  generated target defect.
- H-dead-tail: no distinct entry exists and the host C return makes
  `0x80078894` unreachable; the anomaly is not a live frame-contract cause.
- H-wrong-target: the overlay table assigns `0x80078894` to an unintended
  host function/range; identify the concrete map mismatch.

The discriminating measurement is the exact ROM/decomp function boundary plus
the generated overlay-table entry and host reachability at `0x80078894`.
Record one row for the site with target, entry, and exit stack evidence. Do
not add a mitigation. If `H-dead-tail` wins, close the static frame-contract
thread and select a runtime-origin probe.
