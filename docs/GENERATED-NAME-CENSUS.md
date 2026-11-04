# Address-named generated functions

Census from s6868, by `tools/audit_addr_named_funcs.py <RecompiledFuncs> <rom>`. Static reading, single-source by method.

s6268 called the function sweep complete after counting the syms toml. The generated tree is a different list: N64Recomp
adds `static_N_` functions for branch-and-link targets, and 30 entries in `tools/rename_generated_symbols.py` had never
reached the tree, because nothing in the regen chain ran that script. `tools/regen_replay.sh` now runs it last.

After s6868 all 139 address-named functions are shape names (`data_gap_`, `noopHandler_`, `returnOne_`, `returnZero_`).
The only real function left without a name was `func_800E9AE0`, now `initNpcHealthMotionAndDetail`. That name comes from
its callees; it has no direct caller, so its role in the game is not established. `static_5_800AF6AC` became
`handleCraftSelectInput`.

`data_gap_` here means "not a function entry", not always "not code". Several of these addresses are the middle of a real
function, reached only by a `jal` decoded out of data: 0x80029270 (huft_build), 0x80045024
(computeGridTileEdgeAdjacencyMasks), 0x800E9B10 (func_800E9AE0, see the note in mission_overlay.txt), 0x80106C50
(lvc_initializeObjectTracking, three argument registers already set before it). Their bodies are copies; the enclosing
functions are untouched.

The audit cannot see pointers inside compressed overlays, so "unreferenced" means no direct site and no pointer in the raw
ROM. Sites behind `bltzal $zero` are never taken and are not counted.

## Before the s6868 renames

2494 functions, 141 address-named: decoded-data-target 18, real 1, shape-named 112, unreferenced 10

| Name | Class | Real callers | Decoded-data callers | Inside |
|---|---|---|---|---|
| fake_func_800027B8 | unreferenced | - | - | - |
| static_3_80007064 | decoded-data-target | - | data_gap_8000537C@8000537C | - |
| static_3_80029270 | decoded-data-target | - | audioCompandS16@8009EC08 | huft_build |
| static_3_80045024 | decoded-data-target | - | __OSGlobalIntMask@8003C2D8 | computeGridTileEdgeAdjacencyMasks |
| fake_func_8006ACA4 | unreferenced | - | - | - |
| static_3_8009D8BC | unreferenced | - | - | - |
| static_3_8009D978 | unreferenced | - | - | - |
| static_3_800A2114 | unreferenced | - | - | - |
| static_3_800A2218 | decoded-data-target | - | audioCompandS16@800A10BC | - |
| static_3_800A23BC | decoded-data-target | - | audioCompandS16@800A10DC | - |
| static_3_800A2558 | decoded-data-target | - | audioCompandS16@800A10FC | - |
| static_3_800A2790 | decoded-data-target | - | audioCompandS16@800A1128 | - |
| static_3_800A2924 | decoded-data-target | - | audioCompandS16@800A1148 | - |
| static_3_800A29BC | decoded-data-target | - | audioCompandS16@800A1154 | - |
| static_3_800A2B50 | decoded-data-target | - | audioCompandS16@800A1174 | - |
| static_3_800A2BE4 | decoded-data-target | - | audioCompandS16@800A1180 | - |
| static_3_800A2E98 | decoded-data-target | - | audioCompandS16@800A11B8 | - |
| static_3_800A2F28 | decoded-data-target | - | audioCompandS16@800A11C4 | - |
| static_3_800A2FE4 | decoded-data-target | - | audioCompandS16@800A1804 | - |
| static_3_800A50AC | decoded-data-target | - | audioCompandS16@800A5128 | - |
| fake_func_800AE3E4 | unreferenced | - | - | craftSelectionVoiceLineHelper loadBackdropAsset |
| static_5_800AF6AC | real | tickCraftSelectScreen@800AF41C | - | tickCutsceneObject data_gap_800AF6A8 |
| fake_func_800B2628 | unreferenced | - | - | updatePlayerCraftPhysics |
| fake_func_800B42BC | unreferenced | - | - | destroyPlayerShipRecord |
| fake_func_800B75C4 | unreferenced | - | - | menuControllerInput |
| func_800E9AE0 | unreferenced | - | - | - |
| static_4_800E9B10 | decoded-data-target | - | playerAwingInitPreamble@800B58B8 | initNpcHealthMotionAndDetail |
| static_4_80106C50 | decoded-data-target | - | lvj_checkComplexObjectives@8010A948 | lvc_initializeObjectTracking |
| static_4_801096D8 | decoded-data-target | - | lvj_checkComplexObjectives@801096D4 | - |
