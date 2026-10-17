# Generated-symbol audit — `__osGetOneChannelData`

Session 5164 (2026-10-17) audited companion symbol `__osGetOneChannelData =
0x80030A04`.

The bounded `tools/rename_generated_symbols.py` run reported
`already-synchronized` and renamed zero references in zero files. An
independent search of the generated `RecompiledFuncs` tree found no generated
body, placeholder, overlay record, or direct generated caller at the
companion address. The next companion-map entry is `osPfsInitPak = 0x80030AA0`,
so the nominal span to that boundary is `0x9C`, but there is no generated body
to validate against it.

Classification: unmaterialized libultra/ABI entry. Preserve the ABI name;
this is not a justified generated-body rename.
