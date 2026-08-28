# s2898 generated-symbol sweep: `0x80006C00..0x80007910`

| Address | Project/companion boundary | Generated body | Call/reference evidence | Classification | Action |
|---|---|---|---|---|---|
| `0x80007064` (`func_80007064`, generated `static_3_80007064`) | 12-byte split tail inside complete `signalServiceWorkerStop`; companion says the split symbol is not real | `addiu $v0,1; jr $ra; addiu $sp,0x18`, the preceding body's return/restore | No independent call or lookup target; duplicate split artifact | H-DataGap | `data_gap_80007064`; generated header/body references changed (2) |
| `0x8000737C` (`fake_func_8000737C`) | 4-byte record between `getServiceMessagePayload` and `installPeriodicCallback` | Isolated `addu $sp,$fp,$zero`; no prologue/return | No independent call/lookup target; no semantic companion name | H-DataGap | `data_gap_8000737C`; generated snapshot already synchronized |
| `0x800074D8` (`fake_func_800074D8`) | 8-byte record between `periodicCallbackWorker` and `u64DivU64` | `lui $a0,0x8000; addiu $a0,0x5A4`; no callable boundary | No independent call/lookup target; no semantic companion name | H-DataGap | `data_gap_800074D8`; generated snapshot already synchronized |
| `0x8000751C` (`fake_func_8000751C`) | 4-byte record between `floatToInt` and `rs_strcasecmp` | Isolated `lhu $v1,0x2($v0)`; no prologue/return | No independent call/lookup target; companion identifies following real function | H-DataGap | `data_gap_8000751C`; generated snapshot already synchronized |
| `0x80007908` (`fake_func_80007908`) | 8-byte record between `heapWalker` and `registerSiCallback` | `addiu $v0,2; lui $at,0x801A`; no callable boundary | No independent call/lookup target; no semantic companion name | H-DataGap | `data_gap_80007908`; generated snapshot already synchronized |

All five records are bounded split fragments, not callable bodies. H-Callable
and H-Ambiguous were rejected; the next unresolved placeholder is after
`0x80007910`.
