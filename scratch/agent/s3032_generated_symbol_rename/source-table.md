# Generated-symbol audit: `0x8006ACA4`

| Evidence field | Observation | Selection |
|---|---|---|
| Companion symbol/source | `main_overlay.txt` contains only `fake_func_8006ACA4 = 0x8006ACA4`; the companion tree has no source/name entry for this address. | No exact human identity. |
| Generated boundary/body | `funcs_16.c` emits a `0xC`-byte token containing `lwc1 f0, 0x10(fp)`, `lwc1 f2, 0(v0)`, and `add.s f0, f0, f2`, then closes without `jr`, `return`, or a callable epilogue. The next callable starts at `0x8006ACB0`. | Inline instruction fragment, not a callable. |
| Direct callers | `rg` finds no generated call/reference to `fake_func_8006ACA4` beyond its definition, header, and overlay registration. | Consistent with a non-callable fragment. |
| Header declaration | `funcs.h` declares `fake_func_8006ACA4`, as generated for the fragment token. | Registration artifact; not proof of callability. |
| Overlay registration | `recomp_overlays.inl` registers the token at offset `0x0006A864`, size `0xC`, matching the three instructions. | Exact size confirms the fragment boundary. |
| Project symbol TOML | `syms/rogue_squadron.syms.toml` retains `fake_func_8006ACA4`, VRAM `0x8006ACA4`, size `0xC`. | No synchronization is safe. |
| Build | `cmake --build build --config Debug --target RecompiledFuncs -- -j2` completed with `[100%] Built target RecompiledFuncs`. | Generated target remains valid. |

## Decision

Selected **H-inline-fragment**. Preserve `fake_func_8006ACA4`; do not invent a
semantic name or synchronize the project symbol TOML. This closes the exact
companion-identity, callable-boundary, and local-duplicate hypotheses for this
address.
