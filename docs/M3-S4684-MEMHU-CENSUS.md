# M3 s4684 — backward-loop zero-offset `MEM_HU` census

## Scope and method

The external generated snapshot at `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs` was scanned by `tools/census_memhu.py`. A candidate is a generated `MEM_HU(ctx->rN, 0)` load inside a label-to-backward-`goto` interval, with a different destination register. The script performs two independent textual enumerations of the direct-load set and asserts that their counts agree. It emits the complete per-site table as TSV.

Command:

```sh
python3 tools/census_memhu.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs > /tmp/memhu.tsv
```

The two enumerators agree on 1,104 direct zero-offset loads. The backward-edge analysis finds 521 loop sites, of which 440 are non-self sites in 36 generated files. The complete table is the command output after the summary line; it records file, line, function, guest PC, source and destination registers, loop target, back-edge line, and a bounded immediate-consumer classification.

## Classification result

The 440 loads are halfword reads. The generated operation assigns the 16-bit result to a GPR; none of the sites is a 32-bit pointer load. The bounded classifier is a review aid, not a runtime claim: sites marked `address-consumer-review` or `derived-scalar-review` still require inspection if a future symptom names them. This census found no site whose immediate consumer establishes a named invalid-pointer writer, and therefore authorizes no guard, skip, or mitigation and no build/run.

The heap functions are represented among the candidates (`getTotalFreeHeapSize`, `findLargestFreeHeapChunk`, `rs_malloc`, `buildHeapFreeList`, `initMainHeap`, and `coalesceFreeHeapBlocks`), but their zero-offset halfword reads are flags/status fields in heap headers. The remaining sites are asset, animation, audio, texture, geometry, menu, controller, and OS helper loops reading scalar fields or table entries. A halfword value alone cannot carry a canonical 32-bit guest pointer; pairing it with another load would require a separate site-specific writer/consumer proof, which was not found by this census.

## Decision

This selects `H-MEMHU-bounded` for the generated snapshot. `H-MEMHU-invalid` is not selected, and `H-MEMHU-unreached` is not needed: the static classification itself resolves the pointer-transition question. No runtime probe is warranted without a new named symptom or a site-specific consumer showing pointer reconstruction.
