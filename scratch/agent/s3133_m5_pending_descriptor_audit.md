# Session 3133 pending-request/descriptor census

## Scope

The census searched the companion decomp, this project, symbols, generated
artifacts, and registration text for the pending feature word, selector bytes,
descriptor addresses, named VI helpers, and the consumer/publication PCs.
Closed wrapper callers were excluded.

## Results

| Item | Available evidence | Classification |
|---|---|---|
| `0x80128E90` pending word | Companion `undefined_syms_auto.txt:364` names `D_80128E90`; project `upstream_compat.cpp:1038` reads it only for an existing diagnostic | No game writer/reader body available |
| `0x8012A862`, `0x8012A864`, `0x8012A865` selector bytes | Project `upstream_compat.cpp:1038-1039` reads them only for the diagnostic; no companion source reference | No game writer/reader body available |
| `0x80137340`, `0x80137370` descriptor candidates | No generated/decomp reference found | Not established as descriptors |
| `requestViFeatureChange` (`0x8001B7B8`) | Named in `main_overlay.txt`; no body, callers, or data-flow references in source | Known entry only; no transition edge |
| `applyPendingViChanges` (`0x8001B7F0`) | Named in `main_overlay.txt` and project symbol TOML; no body/data-flow references | Known entry only; no transition edge |
| `selectAndApplyViMode` (`0x8001BB6C`) | Named in `main_overlay.txt` and project symbol TOML; no new caller/data-flow edge | Previously exhausted selector/wrapper area |
| VI consumer/publication (`0x80034F38:0x80035B00`, `0x80035788`) | Companion symbol files identify `viMgrMain`, `__osViSwapContext`, and `__osViNext`; source bodies are `INCLUDE_ASM` stubs | Consumer is retail-qualified, but upstream input edge is not statically recoverable |

The expected generated snapshot is absent: there is no
`RogueSquadron64Recomp/RecompiledFuncs` directory and no matching generated C
file elsewhere under `Tools`. The companion tree has no decompiled bodies for
the relevant libultra functions, only assembly-inclusion stubs. Available text
therefore cannot enumerate writers/readers or prove a transition edge.

## Discriminator outcome

`H-StaticInsufficient` selected. No exact new PC is authorized for an oracle
watch. The falsifying experiment is to restore or provide the matching
generated MIPS snapshot (or an equivalent disassembly/data-flow listing) and
repeat the census; a complete body with a new transition-capable edge would
select `H-NewStaticEdge`.

No build, run, oracle capture, runtime instrumentation, or behavior change was
performed.
