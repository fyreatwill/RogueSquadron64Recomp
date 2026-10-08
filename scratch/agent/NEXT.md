# Next work unit: M5 Step 9v — what is the code at 0x8002A120..0x8002B18F (retail writer 0x8002A518 fills 0x80194FC8+0x10..0x12 with 0x7F) and why does the port leave it zero?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4223 chain: zero volume <- saved stack bytes (0x800A5DF4) <- live 0x80130B60..62 <- 0x8006E0C8 copy of s4+0x10..0x12 (0x8013A5C0) <- memcpy from 0x80194FC8 whose +0x10..0x12 is 7f7f7f in retail, 00 in port. Retail writer: PC 0x8002A518 (1.4 s). funcs_*.c have no code for 0x8002A120..0x8002B18F.

Hypotheses:
- H-source-block-default-init-missing: the gap is real game code not recompiled (dropped/phantom main_overlay entry, covered by ROGUESQ_STUB_MISSING_FUNCS); the port skips the default-init.
- H-source-block-other-writer: code exists under another address/override in the port but runs with wrong input.
- H-data-not-code: 0x8002A518 is a copy loop in an overlay loaded at that VRAM at runtime (retail only).

Discriminator: (1) find the containing symbol: nearest entry <= 0x8002A518 in N64Recomp/*.txt overlay lists and RogueSquadron64Recomp/*.toml; disassemble the ROM bytes at that VRAM. (2) port: add a store watch (rs64_s4222_store_watch pattern) on 0x80194FD8..FA to name the port's writer, and log stub hits with pc in 0x8002A120..0x8002B18F. Positive control: retail writes 7f at 0x80194FD8 (3 hits seen). If the gap is stubbed, relocate the entries per docs/PROJECT-OVERVIEW.md section 15, regen (make_elf -> N64Recomp -> fixup -> cmake), soak.
