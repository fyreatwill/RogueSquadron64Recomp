# NEXT work unit — statically qualify the HMT tuple roles before another run

HYPOTHESIS-ID: m5-preclear-caller-input-producer

Use the generated MIPS body and the HMT format notes to classify which
captured fields are pointers, indices, counts, or scalar payloads, then make
one regeneration-safe replacement of the provisional `bad` classifier. Do
not run the game until the role map makes each possible `bad` outcome
interpretable; then rebuild and run one canonical real-audio capture.

Competing hypotheses and the discriminator:

- `H-HmtInputValid`: every role-mapped pointer is mapped and the crash is a
  later dereference or route issue.
- `H-HmtInputMalformed`: a role-mapped pointer/count violates the HMT contract
  immediately before `parseHmtMaterials+3588`; its producer is next.
- `H-HmtRoleUnknown`: the static body cannot distinguish a field role, so no
  malformed-input conclusion is permitted and the probe must move to the
  exact crash dereference.

The single discriminating table is the role-mapped `[m5-hmt-input]` table plus
the existing positive control and VI/crash markers. Each row includes the
classified pointer/index/count tuple, stack context, return address, and the
first contract violation.

Before building, inspect `funcs_6.c` around `0x80022A00-0x80022BFC` and update
the regeneration hook in `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
Then run the normal make_elf -> N64Recomp -> fixup -> cmake order and capture
under `scratch/agent/s3550_m5_hmt_role_table/`, using the validated real-audio
route and SIGKILL cleanup. Do not change audio, PCM, image-task, output, or
texture-record writes.
