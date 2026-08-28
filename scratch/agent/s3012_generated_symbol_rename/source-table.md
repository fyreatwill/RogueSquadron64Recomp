# Session 3012 static symbol audit

Address: `0x80018ED4`

| Source | Result |
|---|---|
| Companion map | No entry in the companion symbol files or source/m2c material. The adjacent entries are `packMtxRowFloatToFixed` at `0x80018E60` and `zmemcpy` at `0x80018EF4`. |
| Generated definition | The generated body is a 0x20-byte cache-invalidation loop (`addu`, `cache 0x0D`, decrement by 0x10, `jr $ra`). It is emitted as label `L_80018ED4` inside `packMtxRowFloatToFixed`, not as a standalone `RECOMP_FUNC`. |
| Generated callers | No direct caller, `jal`, or function-pointer reference to `0x80018ED4` was found. The only references are the local label and its loop back-edge. |
| Overlay registration | No registration exists for the fragment. The overlay table registers the adjacent named functions only. |
| Project symbol TOML | Retains placeholder `func_80018ED4` with size `0x20`. |

Conclusion: this is a valid callable-looking cache helper but its identity is
ambiguous. There is no exact companion name, standalone generated entry, or
caller evidence supporting a semantic rename. Preserve the placeholder and do
not synthesize a name.
