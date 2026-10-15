# Session 5021 — recovered `allocateDisplayListBuffer` instruction window

The preserved generated snapshot at
`scratch/agent/s389_verify/before_current_applied/funcs_3.c:996-1157` is a
source-backed copy of the complete `0x80007D74..0x80007E58` entry. It supplies
the stack-frame setup/teardown, the `findAndUnlinkSmallestEntry` call, the
branch-likely fall-through at `0x80007DF4`, and the active-queue stores at
`0x80007E18..0x80007E3C` that the earlier assembly slice omitted.

`patches/heap_guard_asm.S` was reconstructed from that window without guards
or padding. The Homebrew MIPS assembler/linker produced:

```
.recomp_patch  0x80801000  0xe8
allocateDisplayListBuffer  0x80801000
```

The target disassembly has 58 instructions, ending at `jr $ra` plus its
`addiu $sp, $sp, 0x18` delay slot, matching the original span exactly. This
selects H1 over the incomplete-slice H3: the recovered source exists and the
assembly is structurally complete.

The direct external `jal findAndUnlinkSmallestEntry` does not pass the current
`build/N64Recomp patches.toml` step: N64Recomp reports `No function found for
jal target: 0x8002221C` and clears the generated output. This is an integration
limitation of the direct-call form, not evidence against the recovered
instruction window. The override remains disabled; no runtime behavior was
changed. The next unit is to make the exact source-backed call representable to
N64Recomp while preserving the `0xe8` span, or document that the current
recompiler cannot consume this faithful assembly form.
