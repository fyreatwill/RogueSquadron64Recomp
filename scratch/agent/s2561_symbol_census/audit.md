# Session 2561 — generated-symbol census at `0x8009C2C8`

| Field | Result |
|---|---|
| Project symbol span | `fake_func_8009C2C8`, `0x8009C2C8–0x8009C2CF`, size `0x8` |
| Generated declaration/table | `funcs.h` and `recomp_overlays.inl` retain the same fake symbol and span |
| Generated body | `mul.s $f2,$f2,$f4`; `add.s $f0,$f0,$f2` |
| Previous complete symbol | `stopVoice` ends at `0x8009C2C7` |
| Next complete symbol | `computeVoicePanCoefficients` begins at `0x8009C2D0` |
| Companion symbol result | `main_overlay.txt` retains `fake_func_8009C2C8`; no accompanying human function entry |
| Exact/source/m2c/caller search | No exact definition, m2c body, or independent caller found in the available repositories |
| Semantic candidate | None defensible; this is a floating-point accumulation fragment, not a complete callable body |
| Decision | `H-data-or-boundary` / `H-no-match`; leave placeholder unchanged |

The generated implementation and project symbol/table inputs independently
bound the same eight-byte fragment. The companion decomp symbol file and
repository search provide the second static line of evidence for the absence
of a human mapping. This remains a static, single-source result: it does not
prove reachability or whether the original compiler represented it as a split
basic-block entry.

No build, runtime probe, generated-code edit, or symbol rename was performed.
