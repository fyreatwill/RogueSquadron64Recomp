# M3 generated 64-bit shift census

Static census only. The retail ELF supplies the independent raw word; generated C supplies the lowering and conservative CFG reachability.

- annotation rows: **720**
- classifications: `correct`=529, `data-like/unreachable-or-zero`=191
- unique file/guest-PC sites: **678**; raw ELF decodes: **720/720**; generated lowerings present: **529/720**
- conservative CFG: **162** reachable rows, including **162** reachable nonzero-destination rows
- opcode counts: `dsll`=153, `dsll32`=67, `dsllv`=90, `dsra`=49, `dsra32`=110, `dsrav`=55, `dsrl`=60, `dsrl32`=73, `dsrlv`=63
- positive control: `funcs_2.c:5860` PC `0x800074E0`, raw=`0x0004103C`, decode=`('dsll32', 'v0', 'a0', None, 0)`, lowering=present; **PASS**

## Interpretation

No reachable nonzero-destination mismatch was found. The class is statically closed as correct or data-like/unreachable; this does not claim qualified-route reachability.

## Complete site table

| file:line | function | guest PC | raw word | ELF decode | annotation | lowering | CFG | classification |
|---|---|---:|---:|---|---|---|---|---|
| funcs_2.c:5860 | `u64DivU64` | `0x800074E0` | `0x0004103C` | `dsll32 v0 a0 None 0` | `dsll32      $v0, $a0, 0` | yes | reachable | **correct** |
| funcs_2.c:5862 | `u64DivU64` | `0x800074E4` | `0x0005183C` | `dsll32 v1 a1 None 0` | `dsll32      $v1, $a1, 0` | yes | reachable | **correct** |
| funcs_2.c:5864 | `u64DivU64` | `0x800074E8` | `0x0003183E` | `dsrl32 v1 v1 None 0` | `dsrl32      $v1, $v1, 0` | yes | reachable | **correct** |
| funcs_2.c:5868 | `u64DivU64` | `0x800074F0` | `0x0006183C` | `dsll32 v1 a2 None 0` | `dsll32      $v1, $a2, 0` | yes | reachable | **correct** |
| funcs_2.c:5870 | `u64DivU64` | `0x800074F4` | `0x0007403C` | `dsll32 t0 a3 None 0` | `dsll32      $t0, $a3, 0` | yes | reachable | **correct** |
| funcs_2.c:5872 | `u64DivU64` | `0x800074F8` | `0x0008403E` | `dsrl32 t0 t0 None 0` | `dsrl32      $t0, $t0, 0` | yes | reachable | **correct** |
| funcs_2.c:5881 | `u64DivU64` | `0x8000750C` | `0x0003103E` | `dsrl32 v0 v1 None 0` | `dsrl32      $v0, $v1, 0` | yes | reachable | **correct** |
| funcs_2.c:5884 | `u64DivU64` | `0x8000750C` | `0x0003103E` | `dsrl32 v0 v1 None 0` | `dsrl32      $v0, $v1, 0` | yes | unreachable | **correct** |
| funcs_24.c:11654 | `resampleVoicePointTableSamples` | `0x800926A0` | `0x0019CBF8` | `dsll t9 t9 None 15` | `dsll        $t9, $t9, 15` | yes | reachable | **correct** |
| funcs_24.c:11793 | `resampleVoicePointTableSamples` | `0x8009275C` | `0x000B587C` | `dsll32 t3 t3 None 1` | `dsll32      $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:11796 | `resampleVoicePointTableSamples` | `0x8009275C` | `0x000B587C` | `dsll32 t3 t3 None 1` | `dsll32      $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:11799 | `resampleVoicePointTableSamples` | `0x80092764` | `0x000B5C78` | `dsll t3 t3 None 17` | `dsll        $t3, $t3, 17` | yes | unreachable | **correct** |
| funcs_24.c:11802 | `resampleVoicePointTableSamples` | `0x80092764` | `0x000B5C78` | `dsll t3 t3 None 17` | `dsll        $t3, $t3, 17` | yes | unreachable | **correct** |
| funcs_24.c:11804 | `resampleVoicePointTableSamples` | `0x80092768` | `0x000B5878` | `dsll t3 t3 None 1` | `dsll        $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:11913 | `interpolatePointTableSamplesToPackedWord` | `0x800927F0` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:11963 | `interpolatePointTableSamplesToPackedWord` | `0x80092838` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:12013 | `interpolatePointTableSamplesToPackedWord` | `0x80092880` | `0x000B5878` | `dsll t3 t3 None 1` | `dsll        $t3, $t3, 1` | yes | reachable | **correct** |
| funcs_24.c:12140 | `resampleVoiceLutSamples` | `0x8009292C` | `0x0019CBF8` | `dsll t9 t9 None 15` | `dsll        $t9, $t9, 15` | yes | reachable | **correct** |
| funcs_24.c:12291 | `resampleVoiceLutSamples` | `0x80092A00` | `0x000B587C` | `dsll32 t3 t3 None 1` | `dsll32      $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:12294 | `resampleVoiceLutSamples` | `0x80092A00` | `0x000B587C` | `dsll32 t3 t3 None 1` | `dsll32      $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:12297 | `resampleVoiceLutSamples` | `0x80092A08` | `0x000B5C78` | `dsll t3 t3 None 17` | `dsll        $t3, $t3, 17` | yes | unreachable | **correct** |
| funcs_24.c:12300 | `resampleVoiceLutSamples` | `0x80092A08` | `0x000B5C78` | `dsll t3 t3 None 17` | `dsll        $t3, $t3, 17` | yes | unreachable | **correct** |
| funcs_24.c:12302 | `resampleVoiceLutSamples` | `0x80092A0C` | `0x000B5878` | `dsll t3 t3 None 1` | `dsll        $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:12417 | `interpolateLutSamplesToPackedWord` | `0x80092AA0` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:12473 | `interpolateLutSamplesToPackedWord` | `0x80092AF4` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:12529 | `interpolateLutSamplesToPackedWord` | `0x80092B48` | `0x000B5878` | `dsll t3 t3 None 1` | `dsll        $t3, $t3, 1` | yes | reachable | **correct** |
| funcs_24.c:12677 | `resampleVoiceConstantSamples` | `0x80092C14` | `0x0019CBF8` | `dsll t9 t9 None 15` | `dsll        $t9, $t9, 15` | yes | reachable | **correct** |
| funcs_24.c:12747 | `resampleVoiceConstantSamples` | `0x80092C78` | `0x000B587C` | `dsll32 t3 t3 None 1` | `dsll32      $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:12750 | `resampleVoiceConstantSamples` | `0x80092C78` | `0x000B587C` | `dsll32 t3 t3 None 1` | `dsll32      $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:12757 | `resampleVoiceConstantSamples` | `0x80092C88` | `0x000B5C78` | `dsll t3 t3 None 17` | `dsll        $t3, $t3, 17` | yes | unreachable | **correct** |
| funcs_24.c:12760 | `resampleVoiceConstantSamples` | `0x80092C88` | `0x000B5C78` | `dsll t3 t3 None 17` | `dsll        $t3, $t3, 17` | yes | unreachable | **correct** |
| funcs_24.c:12767 | `resampleVoiceConstantSamples` | `0x80092C98` | `0x000B5878` | `dsll t3 t3 None 1` | `dsll        $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:12770 | `resampleVoiceConstantSamples` | `0x80092C98` | `0x000B5878` | `dsll t3 t3 None 1` | `dsll        $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:12776 | `resampleVoiceConstantSamples` | `0x80092CA4` | `0x000B5878` | `dsll t3 t3 None 1` | `dsll        $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:12922 | `interpolateConstantSamplesToPackedWord` | `0x80092D6C` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:12978 | `interpolateConstantSamplesToPackedWord` | `0x80092DC0` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13034 | `interpolateConstantSamplesToPackedWord` | `0x80092E14` | `0x000B5878` | `dsll t3 t3 None 1` | `dsll        $t3, $t3, 1` | yes | reachable | **correct** |
| funcs_24.c:13149 | `resampleVoiceLutSamplesPacked` | `0x80092EA8` | `0x0019CBF8` | `dsll t9 t9 None 15` | `dsll        $t9, $t9, 15` | yes | reachable | **correct** |
| funcs_24.c:13227 | `resampleVoiceLutSamplesPacked` | `0x80092F1C` | `0x000B587C` | `dsll32 t3 t3 None 1` | `dsll32      $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:13230 | `resampleVoiceLutSamplesPacked` | `0x80092F1C` | `0x000B587C` | `dsll32 t3 t3 None 1` | `dsll32      $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:13237 | `resampleVoiceLutSamplesPacked` | `0x80092F2C` | `0x000B5C78` | `dsll t3 t3 None 17` | `dsll        $t3, $t3, 17` | yes | unreachable | **correct** |
| funcs_24.c:13240 | `resampleVoiceLutSamplesPacked` | `0x80092F2C` | `0x000B5C78` | `dsll t3 t3 None 17` | `dsll        $t3, $t3, 17` | yes | unreachable | **correct** |
| funcs_24.c:13247 | `resampleVoiceLutSamplesPacked` | `0x80092F3C` | `0x000B5878` | `dsll t3 t3 None 1` | `dsll        $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:13250 | `resampleVoiceLutSamplesPacked` | `0x80092F3C` | `0x000B5878` | `dsll t3 t3 None 1` | `dsll        $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:13256 | `resampleVoiceLutSamplesPacked` | `0x80092F48` | `0x000B5878` | `dsll t3 t3 None 1` | `dsll        $t3, $t3, 1` | yes | unreachable | **correct** |
| funcs_24.c:13426 | `packFourLutResampledSamples` | `0x80093040` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13494 | `packFourLutResampledSamples` | `0x800930AC` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13562 | `packFourLutResampledSamples` | `0x80093118` | `0x000B5878` | `dsll t3 t3 None 1` | `dsll        $t3, $t3, 1` | yes | reachable | **correct** |
| funcs_24.c:13686 | `copyVoiceSamplesS16` | `0x800931B4` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13690 | `copyVoiceSamplesS16` | `0x800931B4` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13711 | `copyVoiceSamplesS16` | `0x800931D4` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13715 | `copyVoiceSamplesS16` | `0x800931D4` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13736 | `copyVoiceSamplesS16` | `0x800931F4` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13740 | `copyVoiceSamplesS16` | `0x800931F4` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13789 | `copyVoiceSamplesS16` | `0x80093238` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13793 | `copyVoiceSamplesS16` | `0x80093238` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13814 | `copyVoiceSamplesS16` | `0x80093258` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13818 | `copyVoiceSamplesS16` | `0x80093258` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13839 | `copyVoiceSamplesS16` | `0x80093278` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13843 | `copyVoiceSamplesS16` | `0x80093278` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:13996 | `copyVoiceSamplesLut` | `0x8009334C` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:14000 | `copyVoiceSamplesLut` | `0x8009334C` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:14027 | `copyVoiceSamplesLut` | `0x80093378` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:14031 | `copyVoiceSamplesLut` | `0x80093378` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:14058 | `copyVoiceSamplesLut` | `0x800933A4` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:14062 | `copyVoiceSamplesLut` | `0x800933A4` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:14123 | `copyVoiceSamplesLut` | `0x80093400` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:14127 | `copyVoiceSamplesLut` | `0x80093400` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:14154 | `copyVoiceSamplesLut` | `0x8009342C` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:14158 | `copyVoiceSamplesLut` | `0x8009342C` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:14185 | `copyVoiceSamplesLut` | `0x80093458` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:14189 | `copyVoiceSamplesLut` | `0x80093458` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_24.c:14286 | `decodeAdpcmSampleBlock` | `0x800934E0` | `0x0018443F` | `dsra32 t0 t8 None 16` | `dsra32      $t0, $t8, 16` | yes | reachable | **correct** |
| funcs_24.c:14288 | `decodeAdpcmSampleBlock` | `0x800934E4` | `0x00184A3E` | `dsrl32 t1 t8 None 8` | `dsrl32      $t1, $t8, 8` | yes | reachable | **correct** |
| funcs_24.c:14294 | `decodeAdpcmSampleBlock` | `0x800934F0` | `0x0018503E` | `dsrl32 t2 t8 None 0` | `dsrl32      $t2, $t8, 0` | yes | reachable | **correct** |
| funcs_24.c:14349 | `decodeAdpcmSampleBlock` | `0x80093540` | `0x0018513E` | `dsrl32 t2 t8 None 4` | `dsrl32      $t2, $t8, 4` | yes | reachable | **correct** |
| funcs_24.c:14842 | `decodeAdpcmSampleBlock` | `0x8009380C` | `0x0019563E` | `dsrl32 t2 t9 None 24` | `dsrl32      $t2, $t9, 24` | yes | reachable | **correct** |
| funcs_24.c:14897 | `decodeAdpcmSampleBlock` | `0x8009385C` | `0x0019573E` | `dsrl32 t2 t9 None 28` | `dsrl32      $t2, $t9, 28` | yes | reachable | **correct** |
| funcs_24.c:14952 | `decodeAdpcmSampleBlock` | `0x800938AC` | `0x0019543E` | `dsrl32 t2 t9 None 16` | `dsrl32      $t2, $t9, 16` | yes | reachable | **correct** |
| funcs_24.c:15007 | `decodeAdpcmSampleBlock` | `0x800938FC` | `0x0019553E` | `dsrl32 t2 t9 None 20` | `dsrl32      $t2, $t9, 20` | yes | reachable | **correct** |
| funcs_24.c:15062 | `decodeAdpcmSampleBlock` | `0x8009394C` | `0x0019523E` | `dsrl32 t2 t9 None 8` | `dsrl32      $t2, $t9, 8` | yes | reachable | **correct** |
| funcs_24.c:15117 | `decodeAdpcmSampleBlock` | `0x8009399C` | `0x0019533E` | `dsrl32 t2 t9 None 12` | `dsrl32      $t2, $t9, 12` | yes | reachable | **correct** |
| funcs_24.c:15172 | `decodeAdpcmSampleBlock` | `0x800939EC` | `0x0019503E` | `dsrl32 t2 t9 None 0` | `dsrl32      $t2, $t9, 0` | yes | reachable | **correct** |
| funcs_24.c:15227 | `decodeAdpcmSampleBlock` | `0x80093A3C` | `0x0019513E` | `dsrl32 t2 t9 None 4` | `dsrl32      $t2, $t9, 4` | yes | reachable | **correct** |
| funcs_25.c:341 | `divideByMixerBaseFrequency` | `0x80093F24` | `0x0004403C` | `dsll32 t0 a0 None 0` | `dsll32      $t0, $a0, 0` | yes | reachable | **correct** |
| funcs_25.c:343 | `divideByMixerBaseFrequency` | `0x80093F28` | `0x0008453A` | `dsrl t0 t0 None 20` | `dsrl        $t0, $t0, 20` | yes | reachable | **correct** |
| funcs_27.c:6293 | `audioCompandS16` | `0x8009DEEC` | `0x00000038` | `dsll zero zero None 0` | `dsll        $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:8194 | `audioCompandS16` | `0x8009ED90` | `0x0000FFFF` | `dsra32 ra zero None 31` | `dsra32      $ra, $zero, 31` | yes | unreachable | **correct** |
| funcs_27.c:8199 | `audioCompandS16` | `0x8009ED90` | `0x0000FFFF` | `dsra32 ra zero None 31` | `dsra32      $ra, $zero, 31` | yes | unreachable | **correct** |
| funcs_27.c:8327 | `audioCompandS16` | `0x8009EDE0` | `0x00360016` | `dsrlv zero s6 at None` | `dsrlv       $zero, $s6, $at` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:8342 | `audioCompandS16` | `0x8009EDE0` | `0x00360016` | `dsrlv zero s6 at None` | `dsrlv       $zero, $s6, $at` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:8354 | `audioCompandS16` | `0x8009EDE0` | `0x00360016` | `dsrlv zero s6 at None` | `dsrlv       $zero, $s6, $at` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:8363 | `audioCompandS16` | `0x8009EDE0` | `0x00360016` | `dsrlv zero s6 at None` | `dsrlv       $zero, $s6, $at` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:8368 | `audioCompandS16` | `0x8009EDE0` | `0x00360016` | `dsrlv zero s6 at None` | `dsrlv       $zero, $s6, $at` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:8499 | `audioCompandS16` | `0x8009EEE4` | `0x00360016` | `dsrlv zero s6 at None` | `dsrlv       $zero, $s6, $at` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:9970 | `audioCompandS16` | `0x8009F610` | `0x0001FFFE` | `dsrl32 ra at None 31` | `dsrl32      $ra, $at, 31` | yes | unreachable | **correct** |
| funcs_27.c:10132 | `audioCompandS16` | `0x8009F748` | `0x0001FFFE` | `dsrl32 ra at None 31` | `dsrl32      $ra, $at, 31` | yes | unreachable | **correct** |
| funcs_27.c:11032 | `audioCompandS16` | `0x8009FB14` | `0x0000FFFB` | `dsra ra zero None 31` | `dsra        $ra, $zero, 31` | yes | unreachable | **correct** |
| funcs_27.c:11318 | `audioCompandS16` | `0x8009FD44` | `0x00000014` | `dsllv zero zero zero None` | `dsllv       $zero, $zero, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11326 | `audioCompandS16` | `0x8009FD54` | `0x00000016` | `dsrlv zero zero zero None` | `dsrlv       $zero, $zero, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11462 | `audioCompandS16` | `0x8009FE5C` | `0x00000038` | `dsll zero zero None 0` | `dsll        $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11470 | `audioCompandS16` | `0x8009FE6C` | `0x0000003A` | `dsrl zero zero None 0` | `dsrl        $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11474 | `audioCompandS16` | `0x8009FE74` | `0x0000003B` | `dsra zero zero None 0` | `dsra        $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11478 | `audioCompandS16` | `0x8009FE7C` | `0x0000003C` | `dsll32 zero zero None 0` | `dsll32      $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11490 | `audioCompandS16` | `0x8009FE94` | `0x0000003E` | `dsrl32 zero zero None 0` | `dsrl32      $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11494 | `audioCompandS16` | `0x8009FE9C` | `0x0000003F` | `dsra32 zero zero None 0` | `dsra32      $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11582 | `audioCompandS16` | `0x8009FF44` | `0x00000054` | `dsllv zero zero zero None` | `.word       0x00000054                   # dsllv       $zero, $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11590 | `audioCompandS16` | `0x8009FF54` | `0x00000056` | `dsrlv zero zero zero None` | `.word       0x00000056                   # dsrlv       $zero, $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11594 | `audioCompandS16` | `0x8009FF5C` | `0x00000057` | `dsrav zero zero zero None` | `.word       0x00000057                   # dsrav       $zero, $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11685 | `audioCompandS16` | `0x800A0010` | `0x00160017` | `dsrav zero s6 zero None` | `dsrav       $zero, $s6, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11735 | `audioCompandS16` | `0x800A0074` | `0x003A003B` | `dsra zero k0 None 0` | `.word       0x003A003B                   # dsra        $zero, $k0, 0 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11739 | `audioCompandS16` | `0x800A007C` | `0x0000003E` | `dsrl32 zero zero None 0` | `dsrl32      $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11773 | `audioCompandS16` | `0x800A00B8` | `0x00560057` | `dsrav zero s6 v0 None` | `.word       0x00560057                   # dsrav       $zero, $s6, $v0 # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11811 | `audioCompandS16` | `0x800A0104` | `0x0079007A` | `dsrl zero t9 None 1` | `.word       0x0079007A                   # dsrl        $zero, $t9, 1 # 00600000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11819 | `audioCompandS16` | `0x800A0114` | `0x0000007E` | `dsrl32 zero zero None 1` | `dsrl32      $zero, $zero, 1` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11823 | `audioCompandS16` | `0x800A011C` | `0x0000007F` | `dsra32 zero zero None 1` | `dsra32      $zero, $zero, 1` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11879 | `audioCompandS16` | `0x800A018C` | `0x00950096` | `dsrlv zero s5 a0 None` | `.word       0x00950096                   # dsrlv       $zero, $s5, $a0 # 00000080 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11923 | `audioCompandS16` | `0x800A01E4` | `0x00BA00BB` | `dsra zero k0 None 2` | `.word       0x00BA00BB                   # dsra        $zero, $k0, 2 # 00A00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11929 | `audioCompandS16` | `0x800A01F0` | `0x00BE00BF` | `dsra32 zero fp None 2` | `.word       0x00BE00BF                   # dsra32      $zero, $fp, 2 # 00A00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11959 | `audioCompandS16` | `0x800A0224` | `0x00D300D4` | `dsllv zero s3 a2 None` | `.word       0x00D300D4                   # dsllv       $zero, $s3, $a2 # 000000C0 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11961 | `audioCompandS16` | `0x800A0228` | `0x00D500D6` | `dsrlv zero s5 a2 None` | `.word       0x00D500D6                   # dsrlv       $zero, $s5, $a2 # 000000C0 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:11999 | `audioCompandS16` | `0x800A0274` | `0x000000FA` | `dsrl zero zero None 3` | `dsrl        $zero, $zero, 3` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12001 | `audioCompandS16` | `0x800A0278` | `0x00FB00FC` | `dsll32 zero k1 None 3` | `.word       0x00FB00FC                   # dsll32      $zero, $k1, 3 # 00E00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12039 | `audioCompandS16` | `0x800A02BC` | `0x01160117` | `dsrav zero s6 t0 None` | `.word       0x01160117                   # dsrav       $zero, $s6, $t0 # 00000100 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12097 | `audioCompandS16` | `0x800A0330` | `0x013A013B` | `dsra zero k0 None 4` | `.word       0x013A013B                   # dsra        $zero, $k0, 4 # 01200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12101 | `audioCompandS16` | `0x800A0338` | `0x013E013F` | `dsra32 zero fp None 4` | `.word       0x013E013F                   # dsra32      $zero, $fp, 4 # 01200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12149 | `audioCompandS16` | `0x800A0398` | `0x01530154` | `dsllv zero s3 t2 None` | `.word       0x01530154                   # dsllv       $zero, $s3, $t2 # 00000140 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12153 | `audioCompandS16` | `0x800A03A0` | `0x00000156` | `dsrlv zero zero zero None` | `.word       0x00000156                   # dsrlv       $zero, $zero, $zero # 00000140 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12155 | `audioCompandS16` | `0x800A03A4` | `0x00000157` | `dsrav zero zero zero None` | `.word       0x00000157                   # dsrav       $zero, $zero, $zero # 00000140 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12209 | `audioCompandS16` | `0x800A0410` | `0x0000017A` | `dsrl zero zero None 5` | `dsrl        $zero, $zero, 5` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12213 | `audioCompandS16` | `0x800A0418` | `0x017B017C` | `dsll32 zero k1 None 5` | `.word       0x017B017C                   # dsll32      $zero, $k1, 5 # 01600000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12217 | `audioCompandS16` | `0x800A0420` | `0x0000017E` | `dsrl32 zero zero None 5` | `dsrl32      $zero, $zero, 5` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12293 | `audioCompandS16` | `0x800A04B8` | `0x01B701B8` | `dsll zero s7 None 6` | `.word       0x01B701B8                   # dsll        $zero, $s7, 6 # 01A00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12295 | `audioCompandS16` | `0x800A04BC` | `0x01B901BA` | `dsrl zero t9 None 6` | `.word       0x01B901BA                   # dsrl        $zero, $t9, 6 # 01A00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12301 | `audioCompandS16` | `0x800A04C8` | `0x01BD01BE` | `dsrl32 zero sp None 6` | `.word       0x01BD01BE                   # dsrl32      $zero, $sp, 6 # 01A00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12327 | `audioCompandS16` | `0x800A04F4` | `0x01D301D4` | `dsllv zero s3 t6 None` | `.word       0x01D301D4                   # dsllv       $zero, $s3, $t6 # 000001C0 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12335 | `audioCompandS16` | `0x800A0504` | `0x000001D6` | `dsrlv zero zero zero None` | `.word       0x000001D6                   # dsrlv       $zero, $zero, $zero # 000001C0 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12389 | `audioCompandS16` | `0x800A0570` | `0x01FA01FB` | `dsra zero k0 None 7` | `.word       0x01FA01FB                   # dsra        $zero, $k0, 7 # 01E00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12393 | `audioCompandS16` | `0x800A0578` | `0x01FE01FF` | `dsra32 zero fp None 7` | `.word       0x01FE01FF                   # dsra32      $zero, $fp, 7 # 01E00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12417 | `audioCompandS16` | `0x800A05A8` | `0x02160217` | `dsrav zero s6 s0 None` | `.word       0x02160217                   # dsrav       $zero, $s6, $s0 # 00000200 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:12493 | `audioCompandS16` | `0x800A0634` | `0x01C701B8` | `dsll zero a3 None 6` | `.word       0x01C701B8                   # dsll        $zero, $a3, 6 # 01C00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:13835 | `audioCompandS16` | `0x800A0F68` | `0x00320038` | `dsll zero s2 None 0` | `.word       0x00320038                   # dsll        $zero, $s2, 0 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:13888 | `audioCompandS16` | `0x800A0FD0` | `0x0178017E` | `dsrl32 zero t8 None 5` | `.word       0x0178017E                   # dsrl32      $zero, $t8, 5 # 01600000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:13892 | `audioCompandS16` | `0x800A0FD8` | `0x01910197` | `dsrav zero s1 t4 None` | `.word       0x01910197                   # dsrav       $zero, $s1, $t4 # 00000180 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:13902 | `audioCompandS16` | `0x800A0FEC` | `0x01CF01D6` | `dsrlv zero t7 t6 None` | `.word       0x01CF01D6                   # dsrlv       $zero, $t7, $t6 # 000001C0 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:13908 | `audioCompandS16` | `0x800A0FF8` | `0x01F501FB` | `dsra zero s5 None 7` | `.word       0x01F501FB                   # dsra        $zero, $s5, 7 # 01E00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:13911 | `audioCompandS16` | `0x800A1000` | `0x020E0214` | `dsllv zero t6 s0 None` | `.word       0x020E0214                   # dsllv       $zero, $t6, $s0 # 00000200 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:13915 | `audioCompandS16` | `0x800A1000` | `0x020E0214` | `dsllv zero t6 s0 None` | `.word       0x020E0214                   # dsllv       $zero, $t6, $s0 # 00000200 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:13931 | `audioCompandS16` | `0x800A1020` | `0x02710278` | `dsll zero s1 None 9` | `.word       0x02710278                   # dsll        $zero, $s1, 9 # 02600000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:13968 | `audioCompandS16` | `0x800A1068` | `0x03500356` | `dsrlv zero s0 k0 None` | `.word       0x03500356                   # dsrlv       $zero, $s0, $k0 # 00000340 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:13974 | `audioCompandS16` | `0x800A1074` | `0x0375037B` | `dsra zero s5 None 13` | `.word       0x0375037B                   # dsra        $zero, $s5, 13 # 03600000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:13984 | `audioCompandS16` | `0x800A1088` | `0x03B203B8` | `dsll zero s2 None 14` | `.word       0x03B203B8                   # dsll        $zero, $s2, 14 # 03A00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:98946 | `audioCompandS16` | `0x800A17B8` | `0x00B100BE` | `dsrl32 zero s1 None 2` | `.word       0x00B100BE                   # dsrl32      $zero, $s1, 2 # 00A00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:98950 | `audioCompandS16` | `0x800A17C0` | `0x00EA00FB` | `dsra zero t2 None 3` | `.word       0x00EA00FB                   # dsra        $zero, $t2, 3 # 00E00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:98971 | `audioCompandS16` | `0x800A17E4` | `0x029802BB` | `dsra zero t8 None 10` | `.word       0x029802BB                   # dsra        $zero, $t8, 10 # 02800000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:98975 | `audioCompandS16` | `0x800A17EC` | `0x032E0357` | `dsrav zero t6 t9 None` | `.word       0x032E0357                   # dsrav       $zero, $t6, $t9 # 00000340 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:100065 | `audioCompandS16` | `0x800A1CAC` | `0x00002914` | `dsllv a1 zero zero None` | `.word       0x00002914                   # dsllv       $a1, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100147 | `audioCompandS16` | `0x800A1D28` | `0x00002D14` | `dsllv a1 zero zero None` | `.word       0x00002D14                   # dsllv       $a1, $zero, $zero # 00000500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100149 | `audioCompandS16` | `0x800A1D2C` | `0x00003416` | `dsrlv a2 zero zero None` | `.word       0x00003416                   # dsrlv       $a2, $zero, $zero # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100189 | `audioCompandS16` | `0x800A1D6C` | `0x00003817` | `dsrav a3 zero zero None` | `dsrav       $a3, $zero, $zero` | yes | unreachable | **correct** |
| funcs_27.c:100225 | `audioCompandS16` | `0x800A1DA4` | `0x00002E14` | `dsllv a1 zero zero None` | `.word       0x00002E14                   # dsllv       $a1, $zero, $zero # 00000600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100227 | `audioCompandS16` | `0x800A1DA8` | `0x00003716` | `dsrlv a2 zero zero None` | `.word       0x00003716                   # dsrlv       $a2, $zero, $zero # 00000700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100267 | `audioCompandS16` | `0x800A1DE8` | `0x00003B17` | `dsrav a3 zero zero None` | `.word       0x00003B17                   # dsrav       $a3, $zero, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100303 | `audioCompandS16` | `0x800A1E20` | `0x00002E14` | `dsllv a1 zero zero None` | `.word       0x00002E14                   # dsllv       $a1, $zero, $zero # 00000600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100305 | `audioCompandS16` | `0x800A1E24` | `0x00003816` | `dsrlv a3 zero zero None` | `dsrlv       $a3, $zero, $zero` | yes | unreachable | **correct** |
| funcs_27.c:100345 | `audioCompandS16` | `0x800A1E64` | `0x00003D17` | `dsrav a3 zero zero None` | `.word       0x00003D17                   # dsrav       $a3, $zero, $zero # 00000500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100383 | `audioCompandS16` | `0x800A1EA0` | `0x00003816` | `dsrlv a3 zero zero None` | `dsrlv       $a3, $zero, $zero` | yes | unreachable | **correct** |
| funcs_27.c:100415 | `audioCompandS16` | `0x800A1ED0` | `0x00000614` | `dsllv zero zero zero None` | `.word       0x00000614                   # dsllv       $zero, $zero, $zero # 00000600 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:100417 | `audioCompandS16` | `0x800A1ED4` | `0x00001314` | `dsllv v0 zero zero None` | `.word       0x00001314                   # dsllv       $v0, $zero, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100419 | `audioCompandS16` | `0x800A1ED8` | `0x00002114` | `dsllv a0 zero zero None` | `.word       0x00002114                   # dsllv       $a0, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100421 | `audioCompandS16` | `0x800A1EDC` | `0x00002E14` | `dsllv a1 zero zero None` | `.word       0x00002E14                   # dsllv       $a1, $zero, $zero # 00000600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100423 | `audioCompandS16` | `0x800A1EE0` | `0x00003D17` | `dsrav a3 zero zero None` | `.word       0x00003D17                   # dsrav       $a3, $zero, $zero # 00000500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100496 | `audioCompandS16` | `0x800A1F50` | `0x00000816` | `dsrlv at zero zero None` | `dsrlv       $at, $zero, $zero` | yes | unreachable | **correct** |
| funcs_27.c:100498 | `audioCompandS16` | `0x800A1F54` | `0x00001816` | `dsrlv v1 zero zero None` | `dsrlv       $v1, $zero, $zero` | yes | unreachable | **correct** |
| funcs_27.c:100500 | `audioCompandS16` | `0x800A1F58` | `0x00002916` | `dsrlv a1 zero zero None` | `.word       0x00002916                   # dsrlv       $a1, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100502 | `audioCompandS16` | `0x800A1F5C` | `0x00003916` | `dsrlv a3 zero zero None` | `.word       0x00003916                   # dsrlv       $a3, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100536 | `audioCompandS16` | `0x800A1F90` | `0x00000917` | `dsrav at zero zero None` | `.word       0x00000917                   # dsrav       $at, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100538 | `audioCompandS16` | `0x800A1F94` | `0x00001B17` | `dsrav v1 zero zero None` | `.word       0x00001B17                   # dsrav       $v1, $zero, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100540 | `audioCompandS16` | `0x800A1F98` | `0x00002D17` | `dsrav a1 zero zero None` | `.word       0x00002D17                   # dsrav       $a1, $zero, $zero # 00000500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100542 | `audioCompandS16` | `0x800A1F9C` | `0x00003F17` | `dsrav a3 zero zero None` | `.word       0x00003F17                   # dsrav       $a3, $zero, $zero # 00000700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:101518 | `audioCompandS16` | `0x800A25AC` | `0x00054D38` | `dsll t1 a1 None 20` | `dsll        $t1, $a1, 20` | yes | unreachable | **correct** |
| funcs_27.c:101597 | `audioCompandS16` | `0x800A2628` | `0x00058F38` | `dsll s1 a1 None 28` | `dsll        $s1, $a1, 28` | yes | unreachable | **correct** |
| funcs_27.c:101599 | `audioCompandS16` | `0x800A262C` | `0x00066A3A` | `dsrl t5 a2 None 8` | `dsrl        $t5, $a2, 8` | yes | unreachable | **correct** |
| funcs_27.c:101639 | `audioCompandS16` | `0x800A266C` | `0x00070C3B` | `dsra at a3 None 16` | `dsra        $at, $a3, 16` | yes | unreachable | **correct** |
| funcs_27.c:101675 | `audioCompandS16` | `0x800A26A4` | `0x0005B138` | `dsll s6 a1 None 4` | `dsll        $s6, $a1, 4` | yes | unreachable | **correct** |
| funcs_27.c:101677 | `audioCompandS16` | `0x800A26A8` | `0x0006BA3A` | `dsrl s7 a2 None 8` | `dsrl        $s7, $a2, 8` | yes | unreachable | **correct** |
| funcs_27.c:101679 | `audioCompandS16` | `0x800A26AC` | `0x0007C33C` | `dsll32 t8 a3 None 12` | `dsll32      $t8, $a3, 12` | yes | unreachable | **correct** |
| funcs_27.c:101718 | `audioCompandS16` | `0x800A26E8` | `0x0007663B` | `dsra t4 a3 None 24` | `dsra        $t4, $a3, 24` | yes | unreachable | **correct** |
| funcs_27.c:101754 | `audioCompandS16` | `0x800A2720` | `0x0005A238` | `dsll s4 a1 None 8` | `dsll        $s4, $a1, 8` | yes | unreachable | **correct** |
| funcs_27.c:101756 | `audioCompandS16` | `0x800A2724` | `0x0006E23A` | `dsrl gp a2 None 8` | `dsrl        $gp, $a2, 8` | yes | unreachable | **correct** |
| funcs_27.c:101758 | `audioCompandS16` | `0x800A2728` | `0x0008233C` | `dsll32 a0 t0 None 12` | `dsll32      $a0, $t0, 12` | yes | unreachable | **correct** |
| funcs_27.c:101760 | `audioCompandS16` | `0x800A272C` | `0x0009633E` | `dsrl32 t4 t1 None 12` | `dsrl32      $t4, $t1, 12` | yes | unreachable | **correct** |
| funcs_27.c:101796 | `audioCompandS16` | `0x800A2764` | `0x0007933B` | `dsra s2 a3 None 12` | `dsra        $s2, $a3, 12` | yes | unreachable | **correct** |
| funcs_27.c:101800 | `audioCompandS16` | `0x800A276C` | `0x000A543F` | `dsra32 t2 t2 None 16` | `dsra32      $t2, $t2, 16` | yes | unreachable | **correct** |
| funcs_27.c:101835 | `audioCompandS16` | `0x800A27A0` | `0x0006D23A` | `dsrl k0 a2 None 8` | `dsrl        $k0, $a2, 8` | yes | unreachable | **correct** |
| funcs_27.c:101837 | `audioCompandS16` | `0x800A27A4` | `0x0008563C` | `dsll32 t2 t0 None 24` | `dsll32      $t2, $t0, 24` | yes | unreachable | **correct** |
| funcs_27.c:101839 | `audioCompandS16` | `0x800A27A8` | `0x0009DA3E` | `dsrl32 k1 t1 None 8` | `dsrl32      $k1, $t1, 8` | yes | unreachable | **correct** |
| funcs_27.c:101867 | `audioCompandS16` | `0x800A27D0` | `0x0000D538` | `dsll k0 zero None 20` | `dsll        $k0, $zero, 20` | yes | unreachable | **correct** |
| funcs_27.c:101869 | `audioCompandS16` | `0x800A27D4` | `0x00027F38` | `dsll t7 v0 None 28` | `dsll        $t7, $v0, 28` | yes | unreachable | **correct** |
| funcs_27.c:101871 | `audioCompandS16` | `0x800A27D8` | `0x00042A38` | `dsll a1 a0 None 8` | `dsll        $a1, $a0, 8` | yes | unreachable | **correct** |
| funcs_27.c:101873 | `audioCompandS16` | `0x800A27DC` | `0x0005D438` | `dsll k0 a1 None 16` | `dsll        $k0, $a1, 16` | yes | unreachable | **correct** |
| funcs_27.c:101875 | `audioCompandS16` | `0x800A27E0` | `0x0007803B` | `dsra s0 a3 None 0` | `dsra        $s0, $a3, 0` | yes | unreachable | **correct** |
| funcs_27.c:101879 | `audioCompandS16` | `0x800A27E8` | `0x000AD53F` | `dsra32 k0 t2 None 20` | `dsra32      $k0, $t2, 20` | yes | unreachable | **correct** |
| funcs_27.c:101915 | `audioCompandS16` | `0x800A2820` | `0x0008403C` | `dsll32 t0 t0 None 0` | `dsll32      $t0, $t0, 0` | yes | unreachable | **correct** |
| funcs_27.c:101917 | `audioCompandS16` | `0x800A2824` | `0x000A153E` | `dsrl32 v0 t2 None 20` | `dsrl32      $v0, $t2, 20` | yes | unreachable | **correct** |
| funcs_27.c:101947 | `audioCompandS16` | `0x800A2850` | `0x0001023A` | `dsrl zero at None 8` | `dsrl        $zero, $at, 8` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:101949 | `audioCompandS16` | `0x800A2854` | `0x0003063A` | `dsrl zero v1 None 24` | `dsrl        $zero, $v1, 24` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:101952 | `audioCompandS16` | `0x800A2858` | `0x00050B3A` | `dsrl at a1 None 12` | `dsrl        $at, $a1, 12` | yes | unreachable | **correct** |
| funcs_27.c:101954 | `audioCompandS16` | `0x800A285C` | `0x00070F3A` | `dsrl at a3 None 28` | `dsrl        $at, $a3, 28` | yes | unreachable | **correct** |
| funcs_27.c:101958 | `audioCompandS16` | `0x800A2864` | `0x000B183F` | `dsra32 v1 t3 None 0` | `dsra32      $v1, $t3, 0` | yes | unreachable | **correct** |
| funcs_27.c:101988 | `audioCompandS16` | `0x800A2890` | `0x00011C3B` | `dsra v1 at None 16` | `dsra        $v1, $at, 16` | yes | unreachable | **correct** |
| funcs_27.c:101990 | `audioCompandS16` | `0x800A2894` | `0x0003543B` | `dsra t2 v1 None 16` | `dsra        $t2, $v1, 16` | yes | unreachable | **correct** |
| funcs_27.c:101992 | `audioCompandS16` | `0x800A2898` | `0x00058C3B` | `dsra s1 a1 None 16` | `dsra        $s1, $a1, 16` | yes | unreachable | **correct** |
| funcs_27.c:101994 | `audioCompandS16` | `0x800A289C` | `0x0007C43B` | `dsra t8 a3 None 16` | `dsra        $t8, $a3, 16` | yes | unreachable | **correct** |
| funcs_27.c:101996 | `audioCompandS16` | `0x800A28A0` | `0x0009FC3E` | `dsrl32 ra t1 None 16` | `dsrl32      $ra, $t1, 16` | yes | unreachable | **correct** |
| funcs_27.c:102028 | `audioCompandS16` | `0x800A28D0` | `0x0001383C` | `dsll32 a3 at None 0` | `dsll32      $a3, $at, 0` | yes | unreachable | **correct** |
| funcs_27.c:102030 | `audioCompandS16` | `0x800A28D4` | `0x0003A83C` | `dsll32 s5 v1 None 0` | `dsll32      $s5, $v1, 0` | yes | unreachable | **correct** |
| funcs_27.c:102032 | `audioCompandS16` | `0x800A28D8` | `0x0006193C` | `dsll32 v1 a2 None 4` | `dsll32      $v1, $a2, 4` | yes | unreachable | **correct** |
| funcs_27.c:102034 | `audioCompandS16` | `0x800A28DC` | `0x0008893C` | `dsll32 s1 t0 None 4` | `dsll32      $s1, $t0, 4` | yes | unreachable | **correct** |
| funcs_27.c:102036 | `audioCompandS16` | `0x800A28E0` | `0x000AFB3F` | `dsra32 ra t2 None 12` | `dsra32      $ra, $t2, 12` | yes | unreachable | **correct** |
| funcs_27.c:102109 | `audioCompandS16` | `0x800A2950` | `0x00017A3E` | `dsrl32 t7 at None 8` | `dsrl32      $t7, $at, 8` | yes | unreachable | **correct** |
| funcs_27.c:102111 | `audioCompandS16` | `0x800A2954` | `0x00046E3E` | `dsrl32 t5 a0 None 24` | `dsrl32      $t5, $a0, 24` | yes | unreachable | **correct** |
| funcs_27.c:102113 | `audioCompandS16` | `0x800A2958` | `0x0007623E` | `dsrl32 t4 a3 None 8` | `dsrl32      $t4, $a3, 8` | yes | unreachable | **correct** |
| funcs_27.c:102115 | `audioCompandS16` | `0x800A295C` | `0x000A563E` | `dsrl32 t2 t2 None 24` | `dsrl32      $t2, $t2, 24` | yes | unreachable | **correct** |
| funcs_27.c:102149 | `audioCompandS16` | `0x800A2990` | `0x00019F3F` | `dsra32 s3 at None 28` | `dsra32      $s3, $at, 28` | yes | unreachable | **correct** |
| funcs_27.c:102151 | `audioCompandS16` | `0x800A2994` | `0x0004DE3F` | `dsra32 k1 a0 None 24` | `dsra32      $k1, $a0, 24` | yes | unreachable | **correct** |
| funcs_27.c:102153 | `audioCompandS16` | `0x800A2998` | `0x00081E3F` | `dsra32 v1 t0 None 24` | `dsra32      $v1, $t0, 24` | yes | unreachable | **correct** |
| funcs_27.c:102155 | `audioCompandS16` | `0x800A299C` | `0x000B5D3F` | `dsra32 t3 t3 None 20` | `dsra32      $t3, $t3, 20` | yes | unreachable | **correct** |
| funcs_27.c:102702 | `audioCompandS16` | `0x800A2CAC` | `0x004C7A54` | `dsllv t7 t4 v0 None` | `.word       0x004C7A54                   # dsllv       $t7, $t4, $v0 # 00000240 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102784 | `audioCompandS16` | `0x800A2D28` | `0x00503354` | `dsllv a2 s0 v0 None` | `.word       0x00503354                   # dsllv       $a2, $s0, $v0 # 00000340 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102786 | `audioCompandS16` | `0x800A2D2C` | `0x005C8956` | `dsrlv s1 gp v0 None` | `.word       0x005C8956                   # dsrlv       $s1, $gp, $v0 # 00000140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102827 | `audioCompandS16` | `0x800A2D6C` | `0x0065CB57` | `dsrav t9 a1 v1 None` | `.word       0x0065CB57                   # dsrav       $t9, $a1, $v1 # 00000340 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102863 | `audioCompandS16` | `0x800A2DA4` | `0x00521E54` | `dsllv v1 s2 v0 None` | `.word       0x00521E54                   # dsllv       $v1, $s2, $v0 # 00000640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102865 | `audioCompandS16` | `0x800A2DA8` | `0x00610C56` | `dsrlv at at v1 None` | `.word       0x00610C56                   # dsrlv       $at, $at, $v1 # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102905 | `audioCompandS16` | `0x800A2DE8` | `0x006AC157` | `dsrav t8 t2 v1 None` | `.word       0x006AC157                   # dsrav       $t8, $t2, $v1 # 00000140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102944 | `audioCompandS16` | `0x800A2E20` | `0x00514C54` | `dsllv t1 s1 v0 None` | `.word       0x00514C54                   # dsllv       $t1, $s1, $v0 # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102946 | `audioCompandS16` | `0x800A2E24` | `0x00635D56` | `dsrlv t3 v1 v1 None` | `.word       0x00635D56                   # dsrlv       $t3, $v1, $v1 # 00000540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102986 | `audioCompandS16` | `0x800A2E64` | `0x006D4C57` | `dsrav t1 t5 v1 None` | `.word       0x006D4C57                   # dsrav       $t1, $t5, $v1 # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103025 | `audioCompandS16` | `0x800A2EA0` | `0x00625F56` | `dsrlv t3 v0 v1 None` | `.word       0x00625F56                   # dsrlv       $t3, $v0, $v1 # 00000740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103057 | `audioCompandS16` | `0x800A2ED0` | `0x000C0554` | `dsllv zero t4 zero None` | `.word       0x000C0554                   # dsllv       $zero, $t4, $zero # 00000540 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:103059 | `audioCompandS16` | `0x800A2ED4` | `0x00241054` | `dsllv v0 a0 at None` | `.word       0x00241054                   # dsllv       $v0, $a0, $at # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103061 | `audioCompandS16` | `0x800A2ED8` | `0x003C1C54` | `dsllv v1 gp at None` | `.word       0x003C1C54                   # dsllv       $v1, $gp, $at # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103063 | `audioCompandS16` | `0x800A2EDC` | `0x00542754` | `dsllv a0 s4 v0 None` | `.word       0x00542754                   # dsllv       $a0, $s4, $v0 # 00000740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103065 | `audioCompandS16` | `0x800A2EE0` | `0x006C3457` | `dsrav a2 t4 v1 None` | `.word       0x006C3457                   # dsrav       $a2, $t4, $v1 # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103138 | `audioCompandS16` | `0x800A2F50` | `0x000E8C56` | `dsrlv s1 t6 zero None` | `.word       0x000E8C56                   # dsrlv       $s1, $t6, $zero # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103140 | `audioCompandS16` | `0x800A2F54` | `0x002BA456` | `dsrlv s4 t3 at None` | `.word       0x002BA456                   # dsrlv       $s4, $t3, $at # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103142 | `audioCompandS16` | `0x800A2F58` | `0x0048BD56` | `dsrlv s7 t0 v0 None` | `.word       0x0048BD56                   # dsrlv       $s7, $t0, $v0 # 00000540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103144 | `audioCompandS16` | `0x800A2F5C` | `0x0065D556` | `dsrlv k0 a1 v1 None` | `.word       0x0065D556                   # dsrlv       $k0, $a1, $v1 # 00000540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103179 | `audioCompandS16` | `0x800A2F90` | `0x000FFF57` | `dsrav ra t7 zero None` | `.word       0x000FFF57                   # dsrav       $ra, $t7, $zero # 00000740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103181 | `audioCompandS16` | `0x800A2F94` | `0x002FFE57` | `dsrav ra t7 at None` | `.word       0x002FFE57                   # dsrav       $ra, $t7, $at # 00000640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103183 | `audioCompandS16` | `0x800A2F98` | `0x004FFE57` | `dsrav ra t7 v0 None` | `.word       0x004FFE57                   # dsrav       $ra, $t7, $v0 # 00000640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103185 | `audioCompandS16` | `0x800A2F9C` | `0x006FFD57` | `dsrav ra t7 v1 None` | `.word       0x006FFD57                   # dsrav       $ra, $t7, $v1 # 00000540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103225 | `audioCompandS16` | `0x800A2FDC` | `0x001306FE` | `dsrl32 zero s3 None 27` | `dsrl32      $zero, $s3, 27` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:103236 | `audioCompandS16` | `0x800A2FF0` | `0x001965FF` | `dsra32 t4 t9 None 23` | `dsra32      $t4, $t9, 23` | yes | unreachable | **correct** |
| funcs_27.c:103240 | `audioCompandS16` | `0x800A2FF8` | `0x001C823F` | `dsra32 s0 gp None 8` | `dsra32      $s0, $gp, 8` | yes | unreachable | **correct** |
| funcs_27.c:103242 | `audioCompandS16` | `0x800A2FFC` | `0x001E3438` | `dsll a2 fp None 16` | `dsll        $a2, $fp, 16` | yes | unreachable | **correct** |
| funcs_27.c:103256 | `audioCompandS16` | `0x800A3018` | `0x002D413E` | `dsrl32 t0 t5 None 4` | `.word       0x002D413E                   # dsrl32      $t0, $t5, 4 # 00200000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103260 | `audioCompandS16` | `0x800A3020` | `0x0032CBFF` | `dsra32 t9 s2 None 15` | `.word       0x0032CBFF                   # dsra32      $t9, $s2, 15 # 00200000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103264 | `audioCompandS16` | `0x800A3028` | `0x0039047E` | `dsrl32 zero t9 None 17` | `.word       0x0039047E                   # dsrl32      $zero, $t9, 17 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:103274 | `audioCompandS16` | `0x800A303C` | `0x004C1BFA` | `dsrl v1 t4 None 15` | `.word       0x004C1BFA                   # dsrl        $v1, $t4, 15 # 00400000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103280 | `audioCompandS16` | `0x800A3048` | `0x005A827C` | `dsll32 s0 k0 None 9` | `.word       0x005A827C                   # dsll32      $s0, $k0, 9 # 00400000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103284 | `audioCompandS16` | `0x800A3050` | `0x006597FE` | `dsrl32 s2 a1 None 31` | `.word       0x006597FE                   # dsrl32      $s2, $a1, 31 # 00600000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103288 | `audioCompandS16` | `0x800A3058` | `0x007208FC` | `dsll32 at s2 None 3` | `.word       0x007208FC                   # dsll32      $at, $s2, 3 # 00600000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103309 | `audioCompandS16` | `0x800A3080` | `0x00CB2FFC` | `dsll32 a1 t3 None 31` | `.word       0x00CB2FFC                   # dsll32      $a1, $t3, 31 # 00C00000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103313 | `audioCompandS16` | `0x800A3088` | `0x00E411F8` | `dsll v0 a0 None 7` | `.word       0x00E411F8                   # dsll        $v0, $a0, 7 # 00E00000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103328 | `audioCompandS16` | `0x800A30A0` | `0x01428A3A` | `dsrl s1 v0 None 8` | `.word       0x01428A3A                   # dsrl        $s1, $v0, 8 # 01400000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103336 | `audioCompandS16` | `0x800A30B0` | `0x01965FF8` | `dsll t3 s6 None 31` | `.word       0x01965FF8                   # dsll        $t3, $s6, 31 # 01800000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103353 | `audioCompandS16` | `0x800A30CC` | `0x0260DFD4` | `dsllv k1 zero s3 None` | `.word       0x0260DFD4                   # dsllv       $k1, $zero, $s3 # 000007C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103357 | `audioCompandS16` | `0x800A30D4` | `0x02AB7038` | `dsll t6 t3 None 0` | `.word       0x02AB7038                   # dsll        $t6, $t3, 0 # 02A00000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104083 | `audioCompandS16` | `0x800A31E0` | `0x000CB2FF` | `dsra32 s6 t4 None 11` | `dsra32      $s6, $t4, 11` | yes | unreachable | **correct** |
| funcs_27.c:104096 | `audioCompandS16` | `0x800A31F4` | `0x0009837F` | `dsra32 s0 t1 None 13` | `dsra32      $s0, $t1, 13` | yes | unreachable | **correct** |
| funcs_27.c:104124 | `audioCompandS16` | `0x800A3224` | `0x0004C1BF` | `dsra32 t8 a0 None 6` | `dsra32      $t8, $a0, 6` | yes | unreachable | **correct** |
| funcs_27.c:104136 | `audioCompandS16` | `0x800A323C` | `0x00035D14` | `dsllv t3 v1 zero None` | `.word       0x00035D14                   # dsllv       $t3, $v1, $zero # 00000500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104141 | `audioCompandS16` | `0x800A323C` | `0x00035D14` | `dsllv t3 v1 zero None` | `.word       0x00035D14                   # dsllv       $t3, $v1, $zero # 00000500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104147 | `audioCompandS16` | `0x800A3248` | `0x0002D414` | `dsllv k0 v0 zero None` | `.word       0x0002D414                   # dsllv       $k0, $v0, $zero # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104151 | `audioCompandS16` | `0x800A3250` | `0x00028514` | `dsllv s0 v0 zero None` | `.word       0x00028514                   # dsllv       $s0, $v0, $zero # 00000500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104173 | `audioCompandS16` | `0x800A327C` | `0x000155B8` | `dsll t2 at None 22` | `dsll        $t2, $at, 22` | yes | unreachable | **correct** |
| funcs_27.c:104201 | `audioCompandS16` | `0x800A32B4` | `0x00009838` | `dsll s3 zero None 0` | `dsll        $s3, $zero, 0` | yes | unreachable | **correct** |
| funcs_27.c:104227 | `audioCompandS16` | `0x800A32E8` | `0x000047D6` | `dsrlv t0 zero zero None` | `.word       0x000047D6                   # dsrlv       $t0, $zero, $zero # 000007C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104297 | `audioCompandS16` | `0x800A3370` | `0x00000A14` | `dsllv at zero zero None` | `.word       0x00000A14                   # dsllv       $at, $zero, $zero # 00000200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104301 | `audioCompandS16` | `0x800A3378` | `0x000008FB` | `dsra at zero None 3` | `dsra        $at, $zero, 3` | yes | unreachable | **correct** |
| funcs_27.c:104303 | `audioCompandS16` | `0x800A337C` | `0x0000087A` | `dsrl at zero None 1` | `dsrl        $at, $zero, 1` | yes | unreachable | **correct** |
| funcs_27.c:104311 | `audioCompandS16` | `0x800A338C` | `0x000006BA` | `dsrl zero zero None 26` | `dsrl        $zero, $zero, 26` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:104315 | `audioCompandS16` | `0x800A3394` | `0x000005FE` | `dsrl32 zero zero None 23` | `dsrl32      $zero, $zero, 23` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:104319 | `audioCompandS16` | `0x800A339C` | `0x00000557` | `dsrav zero zero zero None` | `.word       0x00000557                   # dsrav       $zero, $zero, $zero # 00000540 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:104339 | `audioCompandS16` | `0x800A33C4` | `0x000002FF` | `dsra32 zero zero None 11` | `dsra32      $zero, $zero, 11` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:104341 | `audioCompandS16` | `0x800A33C8` | `0x000002D4` | `dsllv zero zero zero None` | `.word       0x000002D4                   # dsllv       $zero, $zero, $zero # 000002C0 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:104357 | `audioCompandS16` | `0x800A33E8` | `0x0010163E` | `dsrl32 v0 s0 None 24` | `dsrl32      $v0, $s0, 24` | yes | unreachable | **correct** |
| funcs_27.c:104371 | `audioCompandS16` | `0x800A3404` | `0x00103057` | `dsrav a2 s0 zero None` | `.word       0x00103057                   # dsrav       $a2, $s0, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104375 | `audioCompandS16` | `0x800A340C` | `0x001037D4` | `dsllv a2 s0 zero None` | `.word       0x001037D4                   # dsllv       $a2, $s0, $zero # 000007C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104377 | `audioCompandS16` | `0x800A3410` | `0x00103B94` | `dsllv a3 s0 zero None` | `.word       0x00103B94                   # dsllv       $a3, $s0, $zero # 00000380 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104381 | `audioCompandS16` | `0x800A3418` | `0x00104316` | `dsrlv t0 s0 zero None` | `.word       0x00104316                   # dsrlv       $t0, $s0, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104395 | `audioCompandS16` | `0x800A3434` | `0x00105D78` | `dsll t3 s0 None 21` | `dsll        $t3, $s0, 21` | yes | unreachable | **correct** |
| funcs_27.c:104401 | `audioCompandS16` | `0x800A3440` | `0x001068D4` | `dsllv t5 s0 zero None` | `.word       0x001068D4                   # dsllv       $t5, $s0, $zero # 000000C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104407 | `audioCompandS16` | `0x800A344C` | `0x00107438` | `dsll t6 s0 None 16` | `dsll        $t6, $s0, 16` | yes | unreachable | **correct** |
| funcs_27.c:104411 | `audioCompandS16` | `0x800A3454` | `0x00107BD4` | `dsllv t7 s0 zero None` | `.word       0x00107BD4                   # dsllv       $t7, $s0, $zero # 000003C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104419 | `audioCompandS16` | `0x800A3464` | `0x00108B17` | `dsrav s1 s0 zero None` | `.word       0x00108B17                   # dsrav       $s1, $s0, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104423 | `audioCompandS16` | `0x800A346C` | `0x001092BE` | `dsrl32 s2 s0 None 10` | `dsrl32      $s2, $s0, 10` | yes | unreachable | **correct** |
| funcs_27.c:104429 | `audioCompandS16` | `0x800A3478` | `0x00109E3E` | `dsrl32 s3 s0 None 24` | `dsrl32      $s3, $s0, 24` | yes | unreachable | **correct** |
| funcs_27.c:104431 | `audioCompandS16` | `0x800A347C` | `0x0010A216` | `dsrlv s4 s0 zero None` | `.word       0x0010A216                   # dsrlv       $s4, $s0, $zero # 00000200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104439 | `audioCompandS16` | `0x800A348C` | `0x0010B17C` | `dsll32 s6 s0 None 5` | `dsll32      $s6, $s0, 5` | yes | unreachable | **correct** |
| funcs_27.c:104457 | `audioCompandS16` | `0x800A34B0` | `0x0010D457` | `dsrav k0 s0 zero None` | `.word       0x0010D457                   # dsrav       $k0, $s0, $zero # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104459 | `audioCompandS16` | `0x800A34B4` | `0x0010D83B` | `dsra k1 s0 None 0` | `dsra        $k1, $s0, 0` | yes | unreachable | **correct** |
| funcs_27.c:104469 | `audioCompandS16` | `0x800A34C8` | `0x0010EBBC` | `dsll32 sp s0 None 14` | `dsll32      $sp, $s0, 14` | yes | unreachable | **correct** |
| funcs_27.c:104475 | `audioCompandS16` | `0x800A34D4` | `0x0010F77A` | `dsrl fp s0 None 29` | `dsrl        $fp, $s0, 29` | yes | unreachable | **correct** |
| funcs_27.c:104517 | `audioCompandS16` | `0x800A3528` | `0x00114A96` | `dsrlv t1 s1 zero None` | `.word       0x00114A96                   # dsrlv       $t1, $s1, $zero # 00000280 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104523 | `audioCompandS16` | `0x800A3534` | `0x00115697` | `dsrav t2 s1 zero None` | `.word       0x00115697                   # dsrav       $t2, $s1, $zero # 00000680 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104537 | `audioCompandS16` | `0x800A3550` | `0x001172B8` | `dsll t6 s1 None 10` | `dsll        $t6, $s1, 10` | yes | unreachable | **correct** |
| funcs_27.c:104543 | `audioCompandS16` | `0x800A355C` | `0x00117ED4` | `dsllv t7 s1 zero None` | `.word       0x00117ED4                   # dsllv       $t7, $s1, $zero # 000006C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104553 | `audioCompandS16` | `0x800A3570` | `0x00119316` | `dsrlv s2 s1 zero None` | `.word       0x00119316                   # dsrlv       $s2, $s1, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104578 | `audioCompandS16` | `0x800A359C` | `0x0011BFFA` | `dsrl s7 s1 None 31` | `dsrl        $s7, $s1, 31` | yes | unreachable | **correct** |
| funcs_27.c:104580 | `audioCompandS16` | `0x800A35A0` | `0x0011C414` | `dsllv t8 s1 zero None` | `.word       0x0011C414                   # dsllv       $t8, $s1, $zero # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104612 | `audioCompandS16` | `0x800A35E0` | `0x0012063B` | `dsra zero s2 None 24` | `dsra        $zero, $s2, 24` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:104618 | `audioCompandS16` | `0x800A35EC` | `0x001212BE` | `dsrl32 v0 s2 None 10` | `dsrl32      $v0, $s2, 10` | yes | unreachable | **correct** |
| funcs_27.c:104636 | `audioCompandS16` | `0x800A3610` | `0x0012387A` | `dsrl a3 s2 None 1` | `dsrl        $a3, $s2, 1` | yes | unreachable | **correct** |
| funcs_27.c:104678 | `audioCompandS16` | `0x800A3664` | `0x001291BA` | `dsrl s2 s2 None 6` | `dsrl        $s2, $s2, 6` | yes | unreachable | **correct** |
| funcs_27.c:104688 | `audioCompandS16` | `0x800A3678` | `0x0012A73A` | `dsrl s4 s2 None 28` | `dsrl        $s4, $s2, 28` | yes | unreachable | **correct** |
| funcs_27.c:104696 | `audioCompandS16` | `0x800A3688` | `0x0012B87F` | `dsra32 s7 s2 None 1` | `dsra32      $s7, $s2, 1` | yes | unreachable | **correct** |
| funcs_27.c:104702 | `audioCompandS16` | `0x800A3694` | `0x0012C57E` | `dsrl32 t8 s2 None 21` | `dsrl32      $t8, $s2, 21` | yes | unreachable | **correct** |
| funcs_27.c:104704 | `audioCompandS16` | `0x800A3698` | `0x0012C9D4` | `dsllv t9 s2 zero None` | `.word       0x0012C9D4                   # dsllv       $t9, $s2, $zero # 000001C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104712 | `audioCompandS16` | `0x800A36A8` | `0x0012DB3A` | `dsrl k1 s2 None 12` | `dsrl        $k1, $s2, 12` | yes | unreachable | **correct** |
| funcs_27.c:104750 | `audioCompandS16` | `0x800A36F4` | `0x00132EB8` | `dsll a1 s3 None 26` | `dsll        $a1, $s3, 26` | yes | unreachable | **correct** |
| funcs_27.c:104754 | `audioCompandS16` | `0x800A36FC` | `0x00133797` | `dsrav a2 s3 zero None` | `.word       0x00133797                   # dsrav       $a2, $s3, $zero # 00000780 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104757 | `audioCompandS16` | `0x800A3704` | `0x0013407A` | `dsrl t0 s3 None 1` | `dsrl        $t0, $s3, 1` | yes | unreachable | **correct** |
| funcs_27.c:104761 | `audioCompandS16` | `0x800A3704` | `0x0013407A` | `dsrl t0 s3 None 1` | `dsrl        $t0, $s3, 1` | yes | unreachable | **correct** |
| funcs_27.c:104767 | `audioCompandS16` | `0x800A3710` | `0x00134DD7` | `dsrav t1 s3 zero None` | `.word       0x00134DD7                   # dsrav       $t1, $s3, $zero # 000005C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104799 | `audioCompandS16` | `0x800A3750` | `0x001395B8` | `dsll s2 s3 None 22` | `dsll        $s2, $s3, 22` | yes | unreachable | **correct** |
| funcs_27.c:104801 | `audioCompandS16` | `0x800A3754` | `0x00139A3F` | `dsra32 s3 s3 None 8` | `dsra32      $s3, $s3, 8` | yes | unreachable | **correct** |
| funcs_27.c:104813 | `audioCompandS16` | `0x800A376C` | `0x0013B57F` | `dsra32 s6 s3 None 21` | `dsra32      $s6, $s3, 21` | yes | unreachable | **correct** |
| funcs_27.c:104821 | `audioCompandS16` | `0x800A377C` | `0x0013C7BF` | `dsra32 t8 s3 None 30` | `dsra32      $t8, $s3, 30` | yes | unreachable | **correct** |
| funcs_27.c:104835 | `audioCompandS16` | `0x800A3798` | `0x0013E7D6` | `dsrlv gp s3 zero None` | `.word       0x0013E7D6                   # dsrlv       $gp, $s3, $zero # 000007C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104859 | `audioCompandS16` | `0x800A37C8` | `0x00141F54` | `dsllv v1 s4 zero None` | `.word       0x00141F54                   # dsllv       $v1, $s4, $zero # 00000740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104861 | `audioCompandS16` | `0x800A37CC` | `0x001423FA` | `dsrl a0 s4 None 15` | `dsrl        $a0, $s4, 15` | yes | unreachable | **correct** |
| funcs_27.c:104878 | `audioCompandS16` | `0x800A37EC` | `0x00144957` | `dsrav t1 s4 zero None` | `.word       0x00144957                   # dsrav       $t1, $s4, $zero # 00000140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104891 | `audioCompandS16` | `0x800A3800` | `0x001460D4` | `dsllv t4 s4 zero None` | `.word       0x001460D4                   # dsllv       $t4, $s4, $zero # 000000C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104965 | `audioCompandS16` | `0x800A3894` | `0x001511FB` | `dsra v0 s5 None 7` | `dsra        $v0, $s5, 7` | yes | unreachable | **correct** |
| funcs_27.c:104969 | `audioCompandS16` | `0x800A389C` | `0x00151BBA` | `dsrl v1 s5 None 14` | `dsrl        $v1, $s5, 14` | yes | unreachable | **correct** |
| funcs_27.c:104989 | `audioCompandS16` | `0x800A38C4` | `0x00154CB8` | `dsll t1 s5 None 18` | `dsll        $t1, $s5, 18` | yes | unreachable | **correct** |
| funcs_27.c:105005 | `audioCompandS16` | `0x800A38E4` | `0x0015743B` | `dsra t6 s5 None 16` | `dsra        $t6, $s5, 16` | yes | unreachable | **correct** |
| funcs_27.c:105038 | `audioCompandS16` | `0x800A3920` | `0x0015BF17` | `dsrav s7 s5 zero None` | `.word       0x0015BF17                   # dsrav       $s7, $s5, $zero # 00000700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105046 | `audioCompandS16` | `0x800A3930` | `0x0015D33A` | `dsrl k0 s5 None 12` | `dsrl        $k0, $s5, 12` | yes | unreachable | **correct** |
| funcs_27.c:105056 | `audioCompandS16` | `0x800A3944` | `0x0015EC7F` | `dsra32 sp s5 None 17` | `dsra32      $sp, $s5, 17` | yes | unreachable | **correct** |
| funcs_27.c:105068 | `audioCompandS16` | `0x800A395C` | `0x00160AF8` | `dsll at s6 None 11` | `dsll        $at, $s6, 11` | yes | unreachable | **correct** |
| funcs_27.c:105078 | `audioCompandS16` | `0x800A3970` | `0x0016247E` | `dsrl32 a0 s6 None 17` | `dsrl32      $a0, $s6, 17` | yes | unreachable | **correct** |
| funcs_27.c:105082 | `audioCompandS16` | `0x800A3978` | `0x00162EBC` | `dsll32 a1 s6 None 26` | `dsll32      $a1, $s6, 26` | yes | unreachable | **correct** |
| funcs_27.c:105086 | `audioCompandS16` | `0x800A3980` | `0x001638FE` | `dsrl32 a3 s6 None 3` | `dsrl32      $a3, $s6, 3` | yes | unreachable | **correct** |
| funcs_27.c:105102 | `audioCompandS16` | `0x800A39A0` | `0x00166238` | `dsll t4 s6 None 8` | `dsll        $t4, $s6, 8` | yes | unreachable | **correct** |
| funcs_27.c:105118 | `audioCompandS16` | `0x800A39C0` | `0x00168BBE` | `dsrl32 s1 s6 None 14` | `dsrl32      $s1, $s6, 14` | yes | unreachable | **correct** |
| funcs_27.c:105140 | `audioCompandS16` | `0x800A39EC` | `0x0016C554` | `dsllv t8 s6 zero None` | `.word       0x0016C554                   # dsllv       $t8, $s6, $zero # 00000540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105152 | `audioCompandS16` | `0x800A3A04` | `0x0016E4FB` | `dsra gp s6 None 19` | `dsra        $gp, $s6, 19` | yes | unreachable | **correct** |
| funcs_27.c:105187 | `audioCompandS16` | `0x800A3A44` | `0x00173A3B` | `dsra a3 s7 None 8` | `dsra        $a3, $s7, 8` | yes | unreachable | **correct** |
| funcs_27.c:105205 | `audioCompandS16` | `0x800A3A68` | `0x00176ABB` | `dsra t5 s7 None 10` | `dsra        $t5, $s7, 10` | yes | unreachable | **correct** |
| funcs_27.c:105211 | `audioCompandS16` | `0x800A3A74` | `0x00177AFC` | `dsll32 t7 s7 None 11` | `dsll32      $t7, $s7, 11` | yes | unreachable | **correct** |
| funcs_27.c:105228 | `audioCompandS16` | `0x800A3A90` | `0x0017A114` | `dsllv s4 s7 zero None` | `.word       0x0017A114                   # dsllv       $s4, $s7, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105234 | `audioCompandS16` | `0x800A3A9C` | `0x0017B17B` | `dsra s6 s7 None 5` | `dsra        $s6, $s7, 5` | yes | unreachable | **correct** |
| funcs_27.c:105259 | `audioCompandS16` | `0x800A3AC8` | `0x0017EDFF` | `dsra32 sp s7 None 23` | `dsra32      $sp, $s7, 23` | yes | unreachable | **correct** |
| funcs_27.c:105294 | `audioCompandS16` | `0x800A3B04` | `0x0018417F` | `dsra32 t0 t8 None 5` | `dsra32      $t0, $t8, 5` | yes | unreachable | **correct** |
| funcs_27.c:105312 | `audioCompandS16` | `0x800A3B24` | `0x00186E7E` | `dsrl32 t5 t8 None 25` | `dsrl32      $t5, $t8, 25` | yes | unreachable | **correct** |
| funcs_27.c:105345 | `audioCompandS16` | `0x800A3B60` | `0x0018C3BE` | `dsrl32 t8 t8 None 14` | `dsrl32      $t8, $t8, 14` | yes | unreachable | **correct** |
| funcs_27.c:105365 | `audioCompandS16` | `0x800A3B88` | `0x0018FD38` | `dsll ra t8 None 20` | `dsll        $ra, $t8, 20` | yes | unreachable | **correct** |
| funcs_27.c:105367 | `audioCompandS16` | `0x800A3B8C` | `0x001902FF` | `dsra32 zero t9 None 11` | `dsra32      $zero, $t9, 11` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:105385 | `audioCompandS16` | `0x800A3BB0` | `0x00193738` | `dsll a2 t9 None 28` | `dsll        $a2, $t9, 28` | yes | unreachable | **correct** |
| funcs_27.c:105392 | `audioCompandS16` | `0x800A3BBC` | `0x001948B8` | `dsll t1 t9 None 2` | `dsll        $t1, $t9, 2` | yes | unreachable | **correct** |
| funcs_27.c:105402 | `audioCompandS16` | `0x800A3BD0` | `0x001965FF` | `dsra32 t4 t9 None 23` | `dsra32      $t4, $t9, 23` | yes | unreachable | **correct** |
| funcs_27.c:105406 | `audioCompandS16` | `0x800A3BD8` | `0x001971BE` | `dsrl32 t6 t9 None 6` | `dsrl32      $t6, $t9, 6` | yes | unreachable | **correct** |
| funcs_27.c:105429 | `audioCompandS16` | `0x800A3C04` | `0x0019B2BB` | `dsra s6 t9 None 10` | `dsra        $s6, $t9, 10` | yes | unreachable | **correct** |
| funcs_27.c:105465 | `audioCompandS16` | `0x800A3C4C` | `0x001A1E7C` | `dsll32 v1 k0 None 25` | `dsll32      $v1, $k0, 25` | yes | unreachable | **correct** |
| funcs_27.c:105475 | `audioCompandS16` | `0x800A3C60` | `0x001A3CBA` | `dsrl a3 k0 None 18` | `dsrl        $a3, $k0, 18` | yes | unreachable | **correct** |
| funcs_27.c:105501 | `audioCompandS16` | `0x800A3C94` | `0x001A8BFF` | `dsra32 s1 k0 None 15` | `dsra32      $s1, $k0, 15` | yes | unreachable | **correct** |
| funcs_27.c:105511 | `audioCompandS16` | `0x800A3CA8` | `0x001AAABC` | `dsll32 s5 k0 None 10` | `dsll32      $s5, $k0, 10` | yes | unreachable | **correct** |
| funcs_27.c:105517 | `audioCompandS16` | `0x800A3CB4` | `0x001ABD3E` | `dsrl32 s7 k0 None 20` | `dsrl32      $s7, $k0, 20` | yes | unreachable | **correct** |
| funcs_27.c:105560 | `audioCompandS16` | `0x800A3CF8` | `0x001B2714` | `dsllv a0 k1 zero None` | `.word       0x001B2714                   # dsllv       $a0, $k1, $zero # 00000700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105568 | `audioCompandS16` | `0x800A3D08` | `0x001B4038` | `dsll t0 k1 None 0` | `dsll        $t0, $k1, 0` | yes | unreachable | **correct** |
| funcs_27.c:105588 | `audioCompandS16` | `0x800A3D30` | `0x001B7F78` | `dsll t7 k1 None 29` | `dsll        $t7, $k1, 29` | yes | unreachable | **correct** |
| funcs_27.c:105604 | `audioCompandS16` | `0x800A3D50` | `0x001BB27A` | `dsrl s6 k1 None 9` | `dsrl        $s6, $k1, 9` | yes | unreachable | **correct** |
| funcs_27.c:105617 | `audioCompandS16` | `0x800A3D68` | `0x001BD8FB` | `dsra k1 k1 None 3` | `dsra        $k1, $k1, 3` | yes | unreachable | **correct** |
| funcs_27.c:105653 | `audioCompandS16` | `0x800A3DB0` | `0x001C4DBE` | `dsrl32 t1 gp None 22` | `dsrl32      $t1, $gp, 22` | yes | unreachable | **correct** |
| funcs_27.c:105665 | `audioCompandS16` | `0x800A3DC8` | `0x001C7516` | `dsrlv t6 gp zero None` | `.word       0x001C7516                   # dsrlv       $t6, $gp, $zero # 00000500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105669 | `audioCompandS16` | `0x800A3DD0` | `0x001C823F` | `dsra32 s0 gp None 8` | `dsra32      $s0, $gp, 8` | yes | unreachable | **correct** |
| funcs_27.c:105671 | `audioCompandS16` | `0x800A3DD4` | `0x001C88D6` | `dsrlv s1 gp zero None` | `.word       0x001C88D6                   # dsrlv       $s1, $gp, $zero # 000000C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105693 | `audioCompandS16` | `0x800A3E00` | `0x001CD1B8` | `dsll k0 gp None 6` | `dsll        $k0, $gp, 6` | yes | unreachable | **correct** |
| funcs_27.c:105704 | `audioCompandS16` | `0x800A3E14` | `0x001CF316` | `dsrlv fp gp zero None` | `.word       0x001CF316                   # dsrlv       $fp, $gp, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105708 | `audioCompandS16` | `0x800A3E1C` | `0x001D007A` | `dsrl zero sp None 1` | `dsrl        $zero, $sp, 1` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:105716 | `audioCompandS16` | `0x800A3E2C` | `0x001D1B54` | `dsllv v1 sp zero None` | `.word       0x001D1B54                   # dsllv       $v1, $sp, $zero # 00000340 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105746 | `audioCompandS16` | `0x800A3E5C` | `0x001D6C78` | `dsll t5 sp None 17` | `dsll        $t5, $sp, 17` | yes | unreachable | **correct** |
| funcs_27.c:105750 | `audioCompandS16` | `0x800A3E64` | `0x001D7A14` | `dsllv t7 sp zero None` | `.word       0x001D7A14                   # dsllv       $t7, $sp, $zero # 00000200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105770 | `audioCompandS16` | `0x800A3E8C` | `0x001DBE7E` | `dsrl32 s7 sp None 25` | `dsrl32      $s7, $sp, 25` | yes | unreachable | **correct** |
| funcs_27.c:105785 | `audioCompandS16` | `0x800A3EA4` | `0x001DE7D7` | `dsrav gp sp zero None` | `.word       0x001DE7D7                   # dsrav       $gp, $sp, $zero # 000007C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105821 | `audioCompandS16` | `0x800A3EEC` | `0x001E653A` | `dsrl t4 fp None 20` | `dsrl        $t4, $fp, 20` | yes | unreachable | **correct** |
| funcs_27.c:105833 | `audioCompandS16` | `0x800A3F04` | `0x001E8F7B` | `dsra s1 fp None 29` | `dsra        $s1, $fp, 29` | yes | unreachable | **correct** |
| funcs_27.c:105877 | `audioCompandS16` | `0x800A3F54` | `0x001F1DFB` | `dsra v1 ra None 23` | `dsra        $v1, $ra, 23` | yes | unreachable | **correct** |
| funcs_27.c:105883 | `audioCompandS16` | `0x800A3F60` | `0x001F3394` | `dsllv a2 ra zero None` | `.word       0x001F3394                   # dsllv       $a2, $ra, $zero # 00000380 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105889 | `audioCompandS16` | `0x800A3F6C` | `0x001F493C` | `dsll32 t1 ra None 4` | `dsll32      $t1, $ra, 4` | yes | unreachable | **correct** |
| funcs_27.c:105891 | `audioCompandS16` | `0x800A3F70` | `0x001F5078` | `dsll t2 ra None 1` | `dsll        $t2, $ra, 1` | yes | unreachable | **correct** |
| funcs_27.c:105901 | `audioCompandS16` | `0x800A3F84` | `0x001F74BA` | `dsrl t6 ra None 18` | `dsrl        $t6, $ra, 18` | yes | unreachable | **correct** |
| funcs_27.c:105903 | `audioCompandS16` | `0x800A3F88` | `0x001F7BFF` | `dsra32 t7 ra None 15` | `dsra32      $t7, $ra, 15` | yes | unreachable | **correct** |
| funcs_27.c:105917 | `audioCompandS16` | `0x800A3FA4` | `0x001FAF14` | `dsllv s5 ra zero None` | `.word       0x001FAF14                   # dsllv       $s5, $ra, $zero # 00000700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105921 | `audioCompandS16` | `0x800A3FAC` | `0x001FBDBC` | `dsll32 s7 ra None 22` | `dsll32      $s7, $ra, 22` | yes | unreachable | **correct** |
| funcs_27.c:105931 | `audioCompandS16` | `0x800A3FC0` | `0x001FE27C` | `dsll32 gp ra None 9` | `dsll32      $gp, $ra, 9` | yes | unreachable | **correct** |
| funcs_27.c:105935 | `audioCompandS16` | `0x800A3FC8` | `0x001FF13B` | `dsra fp ra None 4` | `dsra        $fp, $ra, 4` | yes | unreachable | **correct** |
| funcs_27.c:105980 | `audioCompandS16` | `0x800A401C` | `0x000FBDFF` | `dsra32 s7 t7 None 23` | `dsra32      $s7, $t7, 23` | yes | unreachable | **correct** |
| funcs_27.c:105984 | `audioCompandS16` | `0x800A4024` | `0x000FB6BA` | `dsrl s6 t7 None 26` | `dsrl        $s6, $t7, 26` | yes | unreachable | **correct** |
| funcs_27.c:105992 | `audioCompandS16` | `0x800A4034` | `0x000FA83B` | `dsra s5 t7 None 0` | `dsra        $s5, $t7, 0` | yes | unreachable | **correct** |
| funcs_27.c:106004 | `audioCompandS16` | `0x800A404C` | `0x000F9296` | `dsrlv s2 t7 zero None` | `.word       0x000F9296                   # dsrlv       $s2, $t7, $zero # 00000280 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106012 | `audioCompandS16` | `0x800A405C` | `0x000F8438` | `dsll s0 t7 None 16` | `dsll        $s0, $t7, 16` | yes | unreachable | **correct** |
| funcs_27.c:106018 | `audioCompandS16` | `0x800A4068` | `0x000F797A` | `dsrl t7 t7 None 5` | `dsrl        $t7, $t7, 5` | yes | unreachable | **correct** |
| funcs_27.c:106034 | `audioCompandS16` | `0x800A4088` | `0x000F5CFA` | `dsrl t3 t7 None 19` | `dsrl        $t3, $t7, 19` | yes | unreachable | **correct** |
| funcs_27.c:106066 | `audioCompandS16` | `0x800A40C8` | `0x000F2497` | `dsrav a0 t7 zero None` | `.word       0x000F2497                   # dsrav       $a0, $t7, $zero # 00000480 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106084 | `audioCompandS16` | `0x800A40EC` | `0x000F053B` | `dsra zero t7 None 20` | `dsra        $zero, $t7, 20` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:106107 | `audioCompandS16` | `0x800A4118` | `0x000EDF3E` | `dsrl32 k1 t6 None 28` | `dsrl32      $k1, $t6, 28` | yes | unreachable | **correct** |
| funcs_27.c:106131 | `audioCompandS16` | `0x800A4148` | `0x000EB63B` | `dsra s6 t6 None 24` | `dsra        $s6, $t6, 24` | yes | unreachable | **correct** |
| funcs_27.c:106133 | `audioCompandS16` | `0x800A414C` | `0x000EB2D6` | `dsrlv s6 t6 zero None` | `.word       0x000EB2D6                   # dsrlv       $s6, $t6, $zero # 000002C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106162 | `audioCompandS16` | `0x800A4184` | `0x000E8397` | `dsrav s0 t6 zero None` | `.word       0x000E8397                   # dsrav       $s0, $t6, $zero # 00000380 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106164 | `audioCompandS16` | `0x800A4188` | `0x000E803C` | `dsll32 s0 t6 None 0` | `dsll32      $s0, $t6, 0` | yes | unreachable | **correct** |
| funcs_27.c:106188 | `audioCompandS16` | `0x800A41B8` | `0x000E583F` | `dsra32 t3 t6 None 0` | `dsra32      $t3, $t6, 0` | yes | unreachable | **correct** |
| funcs_27.c:106204 | `audioCompandS16` | `0x800A41D8` | `0x000E3DD4` | `dsllv a3 t6 zero None` | `.word       0x000E3DD4                   # dsllv       $a3, $t6, $zero # 000005C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106222 | `audioCompandS16` | `0x800A41FC` | `0x000E2056` | `dsrlv a0 t6 zero None` | `.word       0x000E2056                   # dsrlv       $a0, $t6, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106240 | `audioCompandS16` | `0x800A4220` | `0x000E0314` | `dsllv zero t6 zero None` | `.word       0x000E0314                   # dsllv       $zero, $t6, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:106278 | `audioCompandS16` | `0x800A426C` | `0x000DC617` | `dsrav t8 t5 zero None` | `.word       0x000DC617                   # dsrav       $t8, $t5, $zero # 00000600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106282 | `audioCompandS16` | `0x800A4274` | `0x000DBFBB` | `dsra s7 t5 None 30` | `dsra        $s7, $t5, 30` | yes | unreachable | **correct** |
| funcs_27.c:106337 | `audioCompandS16` | `0x800A42E0` | `0x000D6AFF` | `dsra32 t5 t5 None 11` | `dsra32      $t5, $t5, 11` | yes | unreachable | **correct** |
| funcs_27.c:106365 | `audioCompandS16` | `0x800A4310` | `0x000D45FF` | `dsra32 t0 t5 None 23` | `dsra32      $t0, $t5, 23` | yes | unreachable | **correct** |
| funcs_27.c:106425 | `audioCompandS16` | `0x800A4388` | `0x000CEB3A` | `dsrl sp t4 None 12` | `dsrl        $sp, $t4, 12` | yes | unreachable | **correct** |
| funcs_27.c:106427 | `audioCompandS16` | `0x800A438C` | `0x000CE83E` | `dsrl32 sp t4 None 0` | `dsrl32      $sp, $t4, 0` | yes | unreachable | **correct** |
| funcs_27.c:106446 | `audioCompandS16` | `0x800A43AC` | `0x000CD078` | `dsll k0 t4 None 1` | `dsll        $k0, $t4, 1` | yes | unreachable | **correct** |
| funcs_27.c:106466 | `audioCompandS16` | `0x800A43D4` | `0x000CB2FF` | `dsra32 s6 t4 None 11` | `dsra32      $s6, $t4, 11` | yes | unreachable | **correct** |
| funcs_27.c:106493 | `audioCompandS16` | `0x800A4404` | `0x000C8FFA` | `dsrl s1 t4 None 31` | `dsrl        $s1, $t4, 31` | yes | unreachable | **correct** |
| funcs_27.c:106503 | `audioCompandS16` | `0x800A4418` | `0x000C817F` | `dsra32 s0 t4 None 5` | `dsra32      $s0, $t4, 5` | yes | unreachable | **correct** |
| funcs_27.c:106509 | `audioCompandS16` | `0x800A4424` | `0x000C78D7` | `dsrav t7 t4 zero None` | `.word       0x000C78D7                   # dsrav       $t7, $t4, $zero # 000000C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106523 | `audioCompandS16` | `0x800A4440` | `0x000C64BB` | `dsra t4 t4 None 18` | `dsra        $t4, $t4, 18` | yes | unreachable | **correct** |
| funcs_27.c:106556 | `audioCompandS16` | `0x800A4480` | `0x000C373E` | `dsrl32 a2 t4 None 28` | `dsrl32      $a2, $t4, 28` | yes | unreachable | **correct** |
| funcs_27.c:106573 | `audioCompandS16` | `0x800A44A0` | `0x000C20BF` | `dsra32 a0 t4 None 2` | `dsra32      $a0, $t4, 2` | yes | unreachable | **correct** |
| funcs_27.c:106585 | `audioCompandS16` | `0x800A44B8` | `0x000C0FFA` | `dsrl at t4 None 31` | `dsrl        $at, $t4, 31` | yes | unreachable | **correct** |
| funcs_27.c:106606 | `audioCompandS16` | `0x800A44DC` | `0x000BF6FF` | `dsra32 fp t3 None 27` | `dsra32      $fp, $t3, 27` | yes | unreachable | **correct** |
| funcs_27.c:106608 | `audioCompandS16` | `0x800A44E0` | `0x000BF43C` | `dsll32 fp t3 None 16` | `dsll32      $fp, $t3, 16` | yes | unreachable | **correct** |
| funcs_27.c:106624 | `audioCompandS16` | `0x800A4500` | `0x000BDE38` | `dsll k1 t3 None 24` | `dsll        $k1, $t3, 24` | yes | unreachable | **correct** |
| funcs_27.c:106626 | `audioCompandS16` | `0x800A4504` | `0x000BDB7A` | `dsrl k1 t3 None 13` | `dsrl        $k1, $t3, 13` | yes | unreachable | **correct** |
| funcs_27.c:106669 | `audioCompandS16` | `0x800A4558` | `0x000BA27C` | `dsll32 s4 t3 None 9` | `dsll32      $s4, $t3, 9` | yes | unreachable | **correct** |
| funcs_27.c:106684 | `audioCompandS16` | `0x800A4574` | `0x000B8FBA` | `dsrl s1 t3 None 30` | `dsrl        $s1, $t3, 30` | yes | unreachable | **correct** |
| funcs_27.c:106696 | `audioCompandS16` | `0x800A458C` | `0x000B7FBE` | `dsrl32 t7 t3 None 30` | `dsrl32      $t7, $t3, 30` | yes | unreachable | **correct** |
| funcs_27.c:106698 | `audioCompandS16` | `0x800A4590` | `0x000B7D16` | `dsrlv t7 t3 zero None` | `.word       0x000B7D16                   # dsrlv       $t7, $t3, $zero # 00000500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106757 | `audioCompandS16` | `0x800A45F4` | `0x000B3B78` | `dsll a3 t3 None 13` | `dsll        $a3, $t3, 13` | yes | unreachable | **correct** |
| funcs_27.c:106787 | `audioCompandS16` | `0x800A4624` | `0x000B1C7F` | `dsra32 v1 t3 None 17` | `dsra32      $v1, $t3, 17` | yes | unreachable | **correct** |
| funcs_27.c:106795 | `audioCompandS16` | `0x800A4634` | `0x000B123E` | `dsrl32 v0 t3 None 8` | `dsrl32      $v0, $t3, 8` | yes | unreachable | **correct** |
| funcs_27.c:106804 | `audioCompandS16` | `0x800A4648` | `0x000B057C` | `dsll32 zero t3 None 21` | `dsll32      $zero, $t3, 21` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:106808 | `audioCompandS16` | `0x800A4648` | `0x000B057C` | `dsll32 zero t3 None 21` | `dsll32      $zero, $t3, 21` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_27.c:106820 | `audioCompandS16` | `0x800A4660` | `0x000AF63F` | `dsra32 fp t2 None 24` | `dsra32      $fp, $t2, 24` | yes | unreachable | **correct** |
| funcs_27.c:106832 | `audioCompandS16` | `0x800A4678` | `0x000AE717` | `dsrav gp t2 zero None` | `.word       0x000AE717                   # dsrav       $gp, $t2, $zero # 00000700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106879 | `audioCompandS16` | `0x800A46D0` | `0x000AB038` | `dsll s6 t2 None 0` | `dsll        $s6, $t2, 0` | yes | unreachable | **correct** |
| funcs_27.c:106896 | `audioCompandS16` | `0x800A46EC` | `0x000A9EFC` | `dsll32 s3 t2 None 27` | `dsll32      $s3, $t2, 27` | yes | unreachable | **correct** |
| funcs_27.c:106909 | `audioCompandS16` | `0x800A4700` | `0x000A92BE` | `dsrl32 s2 t2 None 10` | `dsrl32      $s2, $t2, 10` | yes | unreachable | **correct** |
| funcs_27.c:106933 | `audioCompandS16` | `0x800A4730` | `0x000A7596` | `dsrlv t6 t2 zero None` | `.word       0x000A7596                   # dsrlv       $t6, $t2, $zero # 00000580 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106957 | `audioCompandS16` | `0x800A4760` | `0x000A58BE` | `dsrl32 t3 t2 None 2` | `dsrl32      $t3, $t2, 2` | yes | unreachable | **correct** |
| funcs_27.c:106963 | `audioCompandS16` | `0x800A476C` | `0x000A5194` | `dsllv t2 t2 zero None` | `.word       0x000A5194                   # dsllv       $t2, $t2, $zero # 00000180 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106985 | `audioCompandS16` | `0x800A4798` | `0x000A377C` | `dsll32 a2 t2 None 29` | `dsll32      $a2, $t2, 29` | yes | unreachable | **correct** |
| funcs_27.c:107005 | `audioCompandS16` | `0x800A47C0` | `0x000A1FFC` | `dsll32 v1 t2 None 31` | `dsll32      $v1, $t2, 31` | yes | unreachable | **correct** |
| funcs_27.c:107011 | `audioCompandS16` | `0x800A47CC` | `0x000A18FA` | `dsrl v1 t2 None 3` | `dsrl        $v1, $t2, 3` | yes | unreachable | **correct** |
| funcs_27.c:107021 | `audioCompandS16` | `0x800A47E0` | `0x000A0D56` | `dsrlv at t2 zero None` | `.word       0x000A0D56                   # dsrlv       $at, $t2, $zero # 00000540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107051 | `audioCompandS16` | `0x800A481C` | `0x0009EABC` | `dsll32 sp t1 None 10` | `dsll32      $sp, $t1, 10` | yes | unreachable | **correct** |
| funcs_27.c:107059 | `audioCompandS16` | `0x800A482C` | `0x0009E196` | `dsrlv gp t1 zero None` | `.word       0x0009E196                   # dsrlv       $gp, $t1, $zero # 00000180 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107065 | `audioCompandS16` | `0x800A4838` | `0x0009DABF` | `dsra32 k1 t1 None 10` | `dsra32      $k1, $t1, 10` | yes | unreachable | **correct** |
| funcs_27.c:107067 | `audioCompandS16` | `0x800A483C` | `0x0009D878` | `dsll k1 t1 None 1` | `dsll        $k1, $t1, 1` | yes | unreachable | **correct** |
| funcs_27.c:107083 | `audioCompandS16` | `0x800A485C` | `0x0009C656` | `dsrlv t8 t1 zero None` | `.word       0x0009C656                   # dsrlv       $t8, $t1, $zero # 00000640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107085 | `audioCompandS16` | `0x800A4860` | `0x0009C414` | `dsllv t8 t1 zero None` | `.word       0x0009C414                   # dsllv       $t8, $t1, $zero # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107097 | `audioCompandS16` | `0x800A4878` | `0x0009B694` | `dsllv s6 t1 zero None` | `.word       0x0009B694                   # dsllv       $s6, $t1, $zero # 00000680 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107099 | `audioCompandS16` | `0x800A487C` | `0x0009B456` | `dsrlv s6 t1 zero None` | `.word       0x0009B456                   # dsrlv       $s6, $t1, $zero # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107131 | `audioCompandS16` | `0x800A48BC` | `0x000990B8` | `dsll s2 t1 None 2` | `dsll        $s2, $t1, 2` | yes | unreachable | **correct** |
| funcs_27.c:107143 | `audioCompandS16` | `0x800A48D4` | `0x0009837E` | `dsrl32 s0 t1 None 13` | `dsrl32      $s0, $t1, 13` | yes | unreachable | **correct** |
| funcs_27.c:107156 | `audioCompandS16` | `0x800A48EC` | `0x00097657` | `dsrav t6 t1 zero None` | `.word       0x00097657                   # dsrav       $t6, $t1, $zero # 00000640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107170 | `audioCompandS16` | `0x800A4908` | `0x00096716` | `dsrlv t4 t1 zero None` | `.word       0x00096716                   # dsrlv       $t4, $t1, $zero # 00000700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107174 | `audioCompandS16` | `0x800A4910` | `0x000962BE` | `dsrl32 t4 t1 None 10` | `dsrl32      $t4, $t1, 10` | yes | unreachable | **correct** |
| funcs_27.c:107180 | `audioCompandS16` | `0x800A491C` | `0x00095C3F` | `dsra32 t3 t1 None 16` | `dsra32      $t3, $t1, 16` | yes | unreachable | **correct** |
| funcs_27.c:107182 | `audioCompandS16` | `0x800A4920` | `0x00095A16` | `dsrlv t3 t1 zero None` | `.word       0x00095A16                   # dsrlv       $t3, $t1, $zero # 00000200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107200 | `audioCompandS16` | `0x800A4944` | `0x000946B8` | `dsll t0 t1 None 26` | `dsll        $t0, $t1, 26` | yes | unreachable | **correct** |
| funcs_27.c:107241 | `audioCompandS16` | `0x800A4994` | `0x00091C3C` | `dsll32 v1 t1 None 16` | `dsll32      $v1, $t1, 16` | yes | unreachable | **correct** |
| funcs_27.c:107254 | `audioCompandS16` | `0x800A49A8` | `0x000911BC` | `dsll32 v0 t1 None 6` | `dsll32      $v0, $t1, 6` | yes | unreachable | **correct** |
| funcs_27.c:107285 | `audioCompandS16` | `0x800A49D8` | `0x0008F8BA` | `dsrl ra t0 None 2` | `dsrl        $ra, $t0, 2` | yes | unreachable | **correct** |
| funcs_27.c:107305 | `audioCompandS16` | `0x800A4A00` | `0x0008E417` | `dsrav gp t0 zero None` | `.word       0x0008E417                   # dsrav       $gp, $t0, $zero # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107309 | `audioCompandS16` | `0x800A4A08` | `0x0008DFFC` | `dsll32 k1 t0 None 31` | `dsll32      $k1, $t0, 31` | yes | unreachable | **correct** |
| funcs_27.c:107337 | `audioCompandS16` | `0x800A4A3C` | `0x0008C57C` | `dsll32 t8 t0 None 21` | `dsll32      $t8, $t0, 21` | yes | unreachable | **correct** |
| funcs_27.c:107354 | `audioCompandS16` | `0x800A4A5C` | `0x0008B554` | `dsllv s6 t0 zero None` | `.word       0x0008B554                   # dsllv       $s6, $t0, $zero # 00000540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107384 | `audioCompandS16` | `0x800A4A94` | `0x00089957` | `dsrav s3 t0 zero None` | `.word       0x00089957                   # dsrav       $s3, $t0, $zero # 00000140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107406 | `audioCompandS16` | `0x800A4AC0` | `0x00088397` | `dsrav s0 t0 zero None` | `.word       0x00088397                   # dsrav       $s0, $t0, $zero # 00000380 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107445 | `audioCompandS16` | `0x800A4B08` | `0x00086078` | `dsll t4 t0 None 1` | `dsll        $t4, $t0, 1` | yes | unreachable | **correct** |
| funcs_27.c:107453 | `audioCompandS16` | `0x800A4B18` | `0x000858BE` | `dsrl32 t3 t0 None 2` | `dsrl32      $t3, $t0, 2` | yes | unreachable | **correct** |
| funcs_27.c:107498 | `audioCompandS16` | `0x800A4B70` | `0x00082EBC` | `dsll32 a1 t0 None 26` | `dsll32      $a1, $t0, 26` | yes | unreachable | **correct** |
| funcs_27.c:107532 | `audioCompandS16` | `0x800A4BB4` | `0x00080ED7` | `dsrav at t0 zero None` | `.word       0x00080ED7                   # dsrav       $at, $t0, $zero # 000006C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107534 | `audioCompandS16` | `0x800A4BB8` | `0x00080CFA` | `dsrl at t0 None 19` | `dsrl        $at, $t0, 19` | yes | unreachable | **correct** |
| funcs_27.c:108010 | `audioCompandS16` | `0x800A4EA8` | `0x010159FC` | `dsll32 t3 at None 7` | `.word       0x010159FC                   # dsll32      $t3, $at, 7 # 01000000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:108014 | `audioCompandS16` | `0x800A4EB0` | `0x00AE5896` | `dsrlv t3 t6 a1 None` | `.word       0x00AE5896                   # dsrlv       $t3, $t6, $a1 # 00000080 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:6335 | `data_gap_800CC3D4` | `0x800CC4BC` | `0x0077FFFF` | `dsra32 ra s7 None 31` | `.word       0x0077FFFF                   # dsra32      $ra, $s7, 31 # 00600000 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_37.c:6337 | `data_gap_800CC3D4` | `0x800CC4C0` | `0x007D007E` | `dsrl32 zero sp None 1` | `.word       0x007D007E                   # dsrl32      $zero, $sp, 1 # 00600000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:6351 | `data_gap_800CC3D4` | `0x800CC4D8` | `0x0088FFFF` | `dsra32 ra t0 None 31` | `.word       0x0088FFFF                   # dsra32      $ra, $t0, 31 # 00800000 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_37.c:6361 | `data_gap_800CC3D4` | `0x800CC4E8` | `0x0085FFFF` | `dsra32 ra a1 None 31` | `.word       0x0085FFFF                   # dsra32      $ra, $a1, 31 # 00800000 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_37.c:6363 | `data_gap_800CC3D4` | `0x800CC4EC` | `0x007A007B` | `dsra zero k0 None 1` | `.word       0x007A007B                   # dsra        $zero, $k0, 1 # 00600000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:6365 | `data_gap_800CC3D4` | `0x800CC4F0` | `0x007CFFFF` | `dsra32 ra gp None 31` | `.word       0x007CFFFF                   # dsra32      $ra, $gp, 31 # 00600000 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_37.c:6844 | `data_gap_800CC3D4` | `0x800CC870` | `0x000000FF` | `dsra32 zero zero None 3` | `dsra32      $zero, $zero, 3` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:6910 | `data_gap_800CC3D4` | `0x800CC8DC` | `0x0188FFFF` | `dsra32 ra t0 None 31` | `.word       0x0188FFFF                   # dsra32      $ra, $t0, 31 # 01800000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:6940 | `data_gap_800CC3D4` | `0x800CC914` | `0x003C0054` | `dsllv zero gp at None` | `.word       0x003C0054                   # dsllv       $zero, $gp, $at # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:6949 | `data_gap_800CC3D4` | `0x800CC924` | `0x01ABFFFF` | `dsra32 ra t3 None 31` | `.word       0x01ABFFFF                   # dsra32      $ra, $t3, 31 # 01A00000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:6968 | `data_gap_800CC3D4` | `0x800CC948` | `0x0192FFFF` | `dsra32 ra s2 None 31` | `.word       0x0192FFFF                   # dsra32      $ra, $s2, 31 # 01800000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:6983 | `data_gap_800CC3D4` | `0x800CC964` | `0x00C80078` | `dsll zero t0 None 1` | `.word       0x00C80078                   # dsll        $zero, $t0, 1 # 00C00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:6987 | `data_gap_800CC3D4` | `0x800CC96C` | `0x019CFFFF` | `dsra32 ra gp None 31` | `.word       0x019CFFFF                   # dsra32      $ra, $gp, 31 # 01800000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:7033 | `data_gap_800CC3D4` | `0x800CC9C8` | `0x007A007B` | `dsra zero k0 None 1` | `.word       0x007A007B                   # dsra        $zero, $k0, 1 # 00600000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:7039 | `data_gap_800CC3D4` | `0x800CC9D4` | `0x025BFFFF` | `dsra32 ra k1 None 31` | `.word       0x025BFFFF                   # dsra32      $ra, $k1, 31 # 02400000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:7723 | `data_gap_800CC3D4` | `0x800CCF18` | `0x00000054` | `dsllv zero zero zero None` | `.word       0x00000054                   # dsllv       $zero, $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:7731 | `data_gap_800CC3D4` | `0x800CCF28` | `0x00000056` | `dsrlv zero zero zero None` | `.word       0x00000056                   # dsrlv       $zero, $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:7735 | `data_gap_800CC3D4` | `0x800CCF30` | `0x00000057` | `dsrav zero zero zero None` | `.word       0x00000057                   # dsrav       $zero, $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:7800 | `data_gap_800CC3D4` | `0x800CCFB0` | `0x00000038` | `dsll zero zero None 0` | `dsll        $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:7808 | `data_gap_800CC3D4` | `0x800CCFC0` | `0x0000003A` | `dsrl zero zero None 0` | `dsrl        $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:7812 | `data_gap_800CC3D4` | `0x800CCFC8` | `0x0000003B` | `dsra zero zero None 0` | `dsra        $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:7820 | `data_gap_800CC3D4` | `0x800CCFD8` | `0x0000003C` | `dsll32 zero zero None 0` | `dsll32      $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:7854 | `data_gap_800CC3D4` | `0x800CD01C` | `0x002E0017` | `dsrav zero t6 at None` | `dsrav       $zero, $t6, $at` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:7856 | `data_gap_800CC3D4` | `0x800CD020` | `0x002D0016` | `dsrlv zero t5 at None` | `dsrlv       $zero, $t5, $at` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:7920 | `data_gap_800CC3D4` | `0x800CD08C` | `0x002F0017` | `dsrav zero t7 at None` | `dsrav       $zero, $t7, $at` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:8043 | `data_gap_800CC3D4` | `0x800CD16C` | `0x002B0014` | `dsllv zero t3 at None` | `dsllv       $zero, $t3, $at` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:8211 | `data_gap_800CC3D4` | `0x800CD2B0` | `0x02000154` | `dsllv zero zero s0 None` | `.word       0x02000154                   # dsllv       $zero, $zero, $s0 # 00000140 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:8399 | `data_gap_800CC3D4` | `0x800CD3C4` | `0x02EE0078` | `dsll zero t6 None 1` | `.word       0x02EE0078                   # dsll        $zero, $t6, 1 # 02E00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_37.c:8449 | `data_gap_800CC3D4` | `0x800CD428` | `0x00000078` | `dsll zero zero None 1` | `dsll        $zero, $zero, 1` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_4.c:33691 | `convertMat3x4ToN64Mtx` | `0x80018D9C` | `0x0018C438` | `dsll t8 t8 None 16` | `dsll        $t8, $t8, 16` | yes | reachable | **correct** |
| funcs_4.c:33783 | `convertMat3x4ToN64Mtx` | `0x80018E18` | `0x00085C38` | `dsll t3 t0 None 16` | `dsll        $t3, $t0, 16` | yes | reachable | **correct** |
| funcs_4.c:33789 | `convertMat3x4ToN64Mtx` | `0x80018E24` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_4.c:33795 | `convertMat3x4ToN64Mtx` | `0x80018E30` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_4.c:33802 | `convertMat3x4ToN64Mtx` | `0x80018E3C` | `0x00084438` | `dsll t0 t0 None 16` | `dsll        $t0, $t0, 16` | yes | reachable | **correct** |
| funcs_4.c:33808 | `convertMat3x4ToN64Mtx` | `0x80018E48` | `0x00084438` | `dsll t0 t0 None 16` | `dsll        $t0, $t0, 16` | yes | reachable | **correct** |
| funcs_4.c:33875 | `packMtxRowFloatToFixed` | `0x80018E8C` | `0x00085C38` | `dsll t3 t0 None 16` | `dsll        $t3, $t0, 16` | yes | reachable | **correct** |
| funcs_4.c:33881 | `packMtxRowFloatToFixed` | `0x80018E98` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_4.c:33887 | `packMtxRowFloatToFixed` | `0x80018EA4` | `0x000B5C38` | `dsll t3 t3 None 16` | `dsll        $t3, $t3, 16` | yes | reachable | **correct** |
| funcs_4.c:33894 | `packMtxRowFloatToFixed` | `0x80018EB0` | `0x00084438` | `dsll t0 t0 None 16` | `dsll        $t0, $t0, 16` | yes | reachable | **correct** |
| funcs_4.c:33900 | `packMtxRowFloatToFixed` | `0x80018EBC` | `0x00084438` | `dsll t0 t0 None 16` | `dsll        $t0, $t0, 16` | yes | reachable | **correct** |
| funcs_49.c:1916 | `lvj_checkComplexObjectives` | `0x80109690` | `0x00000114` | `dsllv zero zero zero None` | `.word       0x00000114                   # dsllv       $zero, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1946 | `lvj_checkComplexObjectives` | `0x801096C4` | `0x006400FA` | `dsrl zero a0 None 3` | `.word       0x006400FA                   # dsrl        $zero, $a0, 3 # 00600000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1948 | `lvj_checkComplexObjectives` | `0x801096C8` | `0x00FA00FA` | `dsrl zero k0 None 3` | `.word       0x00FA00FA                   # dsrl        $zero, $k0, 3 # 00E00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1950 | `lvj_checkComplexObjectives` | `0x801096CC` | `0x03E800FA` | `dsrl zero t0 None 3` | `.word       0x03E800FA                   # dsrl        $zero, $t0, 3 # 03E00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1956 | `lvj_checkComplexObjectives` | `0x801096D8` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1962 | `lvj_checkComplexObjectives` | `0x801096D8` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1965 | `lvj_checkComplexObjectives` | `0x801096DC` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1967 | `lvj_checkComplexObjectives` | `0x801096E0` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1969 | `lvj_checkComplexObjectives` | `0x801096E4` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1971 | `lvj_checkComplexObjectives` | `0x801096E8` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1973 | `lvj_checkComplexObjectives` | `0x801096EC` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1981 | `lvj_checkComplexObjectives` | `0x801096FC` | `0x000A0014` | `dsllv zero t2 zero None` | `dsllv       $zero, $t2, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1983 | `lvj_checkComplexObjectives` | `0x80109700` | `0x001E0014` | `dsllv zero fp zero None` | `dsllv       $zero, $fp, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1985 | `lvj_checkComplexObjectives` | `0x80109704` | `0x003C0014` | `dsllv zero gp at None` | `dsllv       $zero, $gp, $at` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1993 | `lvj_checkComplexObjectives` | `0x80109714` | `0x001E0014` | `dsllv zero fp zero None` | `dsllv       $zero, $fp, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:1999 | `lvj_checkComplexObjectives` | `0x80109720` | `0x000A0014` | `dsllv zero t2 zero None` | `dsllv       $zero, $t2, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:2606 | `lvj_checkComplexObjectives` | `0x80109B78` | `0x002E0078` | `dsll zero t6 None 1` | `.word       0x002E0078                   # dsll        $zero, $t6, 1 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:2618 | `lvj_checkComplexObjectives` | `0x80109B90` | `0x00070078` | `dsll zero a3 None 1` | `dsll        $zero, $a3, 1` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:2654 | `lvj_checkComplexObjectives` | `0x80109BD8` | `0x000E0078` | `dsll zero t6 None 1` | `dsll        $zero, $t6, 1` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:2666 | `lvj_checkComplexObjectives` | `0x80109BF0` | `0x00110078` | `dsll zero s1 None 1` | `dsll        $zero, $s1, 1` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:2678 | `lvj_checkComplexObjectives` | `0x80109C08` | `0x000F0078` | `dsll zero t7 None 1` | `dsll        $zero, $t7, 1` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:2690 | `lvj_checkComplexObjectives` | `0x80109C20` | `0x00120078` | `dsll zero s2 None 1` | `dsll        $zero, $s2, 1` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:2702 | `lvj_checkComplexObjectives` | `0x80109C38` | `0x00130078` | `dsll zero s3 None 1` | `dsll        $zero, $s3, 1` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:2714 | `lvj_checkComplexObjectives` | `0x80109C50` | `0x002E0078` | `dsll zero t6 None 1` | `.word       0x002E0078                   # dsll        $zero, $t6, 1 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:2726 | `lvj_checkComplexObjectives` | `0x80109C68` | `0x00070078` | `dsll zero a3 None 1` | `dsll        $zero, $a3, 1` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:2750 | `lvj_checkComplexObjectives` | `0x80109C98` | `0x000E0078` | `dsll zero t6 None 1` | `dsll        $zero, $t6, 1` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:3296 | `lvj_checkComplexObjectives` | `0x80109EE4` | `0x0000FFFF` | `dsra32 ra zero None 31` | `dsra32      $ra, $zero, 31` | yes | unreachable | **correct** |
| funcs_49.c:3495 | `lvj_checkComplexObjectives` | `0x80109FF8` | `0x00000016` | `dsrlv zero zero zero None` | `dsrlv       $zero, $zero, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:5879 | `lvj_checkComplexObjectives` | `0x8010B214` | `0x00080014` | `dsllv zero t0 zero None` | `dsllv       $zero, $t0, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:5885 | `lvj_checkComplexObjectives` | `0x8010B220` | `0x00090016` | `dsrlv zero t1 zero None` | `dsrlv       $zero, $t1, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:6023 | `lvj_checkComplexObjectives` | `0x8010B30C` | `0x003C003A` | `dsrl zero gp None 0` | `.word       0x003C003A                   # dsrl        $zero, $gp, 0 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:6025 | `lvj_checkComplexObjectives` | `0x8010B310` | `0x0039003B` | `dsra zero t9 None 0` | `.word       0x0039003B                   # dsra        $zero, $t9, 0 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:6035 | `lvj_checkComplexObjectives` | `0x8010B320` | `0x00000014` | `dsllv zero zero zero None` | `dsllv       $zero, $zero, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:6039 | `lvj_checkComplexObjectives` | `0x8010B328` | `0x0000003C` | `dsll32 zero zero None 0` | `dsll32      $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:6045 | `lvj_checkComplexObjectives` | `0x8010B334` | `0x00000014` | `dsllv zero zero zero None` | `dsllv       $zero, $zero, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:6049 | `lvj_checkComplexObjectives` | `0x8010B33C` | `0x0000003C` | `dsll32 zero zero None 0` | `dsll32      $zero, $zero, 0` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:6299 | `lvj_checkComplexObjectives` | `0x8010B4EC` | `0x000EFFFF` | `dsra32 ra t6 None 31` | `dsra32      $ra, $t6, 31` | yes | unreachable | **correct** |
| funcs_49.c:8749 | `static_3_800A2558` | `0x800A25AC` | `0x00054D38` | `dsll t1 a1 None 20` | `dsll        $t1, $a1, 20` | yes | reachable | **correct** |
| funcs_49.c:8827 | `static_3_800A2558` | `0x800A2628` | `0x00058F38` | `dsll s1 a1 None 28` | `dsll        $s1, $a1, 28` | yes | reachable | **correct** |
| funcs_49.c:8829 | `static_3_800A2558` | `0x800A262C` | `0x00066A3A` | `dsrl t5 a2 None 8` | `dsrl        $t5, $a2, 8` | yes | reachable | **correct** |
| funcs_49.c:8869 | `static_3_800A2558` | `0x800A266C` | `0x00070C3B` | `dsra at a3 None 16` | `dsra        $at, $a3, 16` | yes | reachable | **correct** |
| funcs_49.c:8905 | `static_3_800A2558` | `0x800A26A4` | `0x0005B138` | `dsll s6 a1 None 4` | `dsll        $s6, $a1, 4` | yes | reachable | **correct** |
| funcs_49.c:8907 | `static_3_800A2558` | `0x800A26A8` | `0x0006BA3A` | `dsrl s7 a2 None 8` | `dsrl        $s7, $a2, 8` | yes | reachable | **correct** |
| funcs_49.c:8909 | `static_3_800A2558` | `0x800A26AC` | `0x0007C33C` | `dsll32 t8 a3 None 12` | `dsll32      $t8, $a3, 12` | yes | reachable | **correct** |
| funcs_49.c:8947 | `static_3_800A2558` | `0x800A26E8` | `0x0007663B` | `dsra t4 a3 None 24` | `dsra        $t4, $a3, 24` | yes | reachable | **correct** |
| funcs_49.c:8983 | `static_3_800A2558` | `0x800A2720` | `0x0005A238` | `dsll s4 a1 None 8` | `dsll        $s4, $a1, 8` | yes | reachable | **correct** |
| funcs_49.c:8985 | `static_3_800A2558` | `0x800A2724` | `0x0006E23A` | `dsrl gp a2 None 8` | `dsrl        $gp, $a2, 8` | yes | reachable | **correct** |
| funcs_49.c:8987 | `static_3_800A2558` | `0x800A2728` | `0x0008233C` | `dsll32 a0 t0 None 12` | `dsll32      $a0, $t0, 12` | yes | reachable | **correct** |
| funcs_49.c:8989 | `static_3_800A2558` | `0x800A272C` | `0x0009633E` | `dsrl32 t4 t1 None 12` | `dsrl32      $t4, $t1, 12` | yes | reachable | **correct** |
| funcs_49.c:9025 | `static_3_800A2558` | `0x800A2764` | `0x0007933B` | `dsra s2 a3 None 12` | `dsra        $s2, $a3, 12` | yes | reachable | **correct** |
| funcs_49.c:9029 | `static_3_800A2558` | `0x800A276C` | `0x000A543F` | `dsra32 t2 t2 None 16` | `dsra32      $t2, $t2, 16` | yes | reachable | **correct** |
| funcs_49.c:9067 | `static_3_800A2790` | `0x800A27A0` | `0x0006D23A` | `dsrl k0 a2 None 8` | `dsrl        $k0, $a2, 8` | yes | reachable | **correct** |
| funcs_49.c:9069 | `static_3_800A2790` | `0x800A27A4` | `0x0008563C` | `dsll32 t2 t0 None 24` | `dsll32      $t2, $t0, 24` | yes | reachable | **correct** |
| funcs_49.c:9071 | `static_3_800A2790` | `0x800A27A8` | `0x0009DA3E` | `dsrl32 k1 t1 None 8` | `dsrl32      $k1, $t1, 8` | yes | reachable | **correct** |
| funcs_49.c:9099 | `static_3_800A2790` | `0x800A27D0` | `0x0000D538` | `dsll k0 zero None 20` | `dsll        $k0, $zero, 20` | yes | reachable | **correct** |
| funcs_49.c:9101 | `static_3_800A2790` | `0x800A27D4` | `0x00027F38` | `dsll t7 v0 None 28` | `dsll        $t7, $v0, 28` | yes | reachable | **correct** |
| funcs_49.c:9103 | `static_3_800A2790` | `0x800A27D8` | `0x00042A38` | `dsll a1 a0 None 8` | `dsll        $a1, $a0, 8` | yes | reachable | **correct** |
| funcs_49.c:9105 | `static_3_800A2790` | `0x800A27DC` | `0x0005D438` | `dsll k0 a1 None 16` | `dsll        $k0, $a1, 16` | yes | reachable | **correct** |
| funcs_49.c:9107 | `static_3_800A2790` | `0x800A27E0` | `0x0007803B` | `dsra s0 a3 None 0` | `dsra        $s0, $a3, 0` | yes | reachable | **correct** |
| funcs_49.c:9111 | `static_3_800A2790` | `0x800A27E8` | `0x000AD53F` | `dsra32 k0 t2 None 20` | `dsra32      $k0, $t2, 20` | yes | reachable | **correct** |
| funcs_49.c:9147 | `static_3_800A2790` | `0x800A2820` | `0x0008403C` | `dsll32 t0 t0 None 0` | `dsll32      $t0, $t0, 0` | yes | reachable | **correct** |
| funcs_49.c:9149 | `static_3_800A2790` | `0x800A2824` | `0x000A153E` | `dsrl32 v0 t2 None 20` | `dsrl32      $v0, $t2, 20` | yes | reachable | **correct** |
| funcs_49.c:9179 | `static_3_800A2790` | `0x800A2850` | `0x0001023A` | `dsrl zero at None 8` | `dsrl        $zero, $at, 8` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:9181 | `static_3_800A2790` | `0x800A2854` | `0x0003063A` | `dsrl zero v1 None 24` | `dsrl        $zero, $v1, 24` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:9183 | `static_3_800A2790` | `0x800A2858` | `0x00050B3A` | `dsrl at a1 None 12` | `dsrl        $at, $a1, 12` | yes | reachable | **correct** |
| funcs_49.c:9185 | `static_3_800A2790` | `0x800A285C` | `0x00070F3A` | `dsrl at a3 None 28` | `dsrl        $at, $a3, 28` | yes | reachable | **correct** |
| funcs_49.c:9189 | `static_3_800A2790` | `0x800A2864` | `0x000B183F` | `dsra32 v1 t3 None 0` | `dsra32      $v1, $t3, 0` | yes | reachable | **correct** |
| funcs_49.c:9219 | `static_3_800A2790` | `0x800A2890` | `0x00011C3B` | `dsra v1 at None 16` | `dsra        $v1, $at, 16` | yes | reachable | **correct** |
| funcs_49.c:9221 | `static_3_800A2790` | `0x800A2894` | `0x0003543B` | `dsra t2 v1 None 16` | `dsra        $t2, $v1, 16` | yes | reachable | **correct** |
| funcs_49.c:9223 | `static_3_800A2790` | `0x800A2898` | `0x00058C3B` | `dsra s1 a1 None 16` | `dsra        $s1, $a1, 16` | yes | reachable | **correct** |
| funcs_49.c:9225 | `static_3_800A2790` | `0x800A289C` | `0x0007C43B` | `dsra t8 a3 None 16` | `dsra        $t8, $a3, 16` | yes | reachable | **correct** |
| funcs_49.c:9227 | `static_3_800A2790` | `0x800A28A0` | `0x0009FC3E` | `dsrl32 ra t1 None 16` | `dsrl32      $ra, $t1, 16` | yes | reachable | **correct** |
| funcs_49.c:9259 | `static_3_800A2790` | `0x800A28D0` | `0x0001383C` | `dsll32 a3 at None 0` | `dsll32      $a3, $at, 0` | yes | reachable | **correct** |
| funcs_49.c:9261 | `static_3_800A2790` | `0x800A28D4` | `0x0003A83C` | `dsll32 s5 v1 None 0` | `dsll32      $s5, $v1, 0` | yes | reachable | **correct** |
| funcs_49.c:9263 | `static_3_800A2790` | `0x800A28D8` | `0x0006193C` | `dsll32 v1 a2 None 4` | `dsll32      $v1, $a2, 4` | yes | reachable | **correct** |
| funcs_49.c:9265 | `static_3_800A2790` | `0x800A28DC` | `0x0008893C` | `dsll32 s1 t0 None 4` | `dsll32      $s1, $t0, 4` | yes | reachable | **correct** |
| funcs_49.c:9267 | `static_3_800A2790` | `0x800A28E0` | `0x000AFB3F` | `dsra32 ra t2 None 12` | `dsra32      $ra, $t2, 12` | yes | reachable | **correct** |
| funcs_49.c:9343 | `static_3_800A2924` | `0x800A2950` | `0x00017A3E` | `dsrl32 t7 at None 8` | `dsrl32      $t7, $at, 8` | yes | reachable | **correct** |
| funcs_49.c:9345 | `static_3_800A2924` | `0x800A2954` | `0x00046E3E` | `dsrl32 t5 a0 None 24` | `dsrl32      $t5, $a0, 24` | yes | reachable | **correct** |
| funcs_49.c:9347 | `static_3_800A2924` | `0x800A2958` | `0x0007623E` | `dsrl32 t4 a3 None 8` | `dsrl32      $t4, $a3, 8` | yes | reachable | **correct** |
| funcs_49.c:9349 | `static_3_800A2924` | `0x800A295C` | `0x000A563E` | `dsrl32 t2 t2 None 24` | `dsrl32      $t2, $t2, 24` | yes | reachable | **correct** |
| funcs_49.c:9383 | `static_3_800A2924` | `0x800A2990` | `0x00019F3F` | `dsra32 s3 at None 28` | `dsra32      $s3, $at, 28` | yes | reachable | **correct** |
| funcs_49.c:9385 | `static_3_800A2924` | `0x800A2994` | `0x0004DE3F` | `dsra32 k1 a0 None 24` | `dsra32      $k1, $a0, 24` | yes | reachable | **correct** |
| funcs_49.c:9387 | `static_3_800A2924` | `0x800A2998` | `0x00081E3F` | `dsra32 v1 t0 None 24` | `dsra32      $v1, $t0, 24` | yes | reachable | **correct** |
| funcs_49.c:9389 | `static_3_800A2924` | `0x800A299C` | `0x000B5D3F` | `dsra32 t3 t3 None 20` | `dsra32      $t3, $t3, 20` | yes | reachable | **correct** |
| funcs_49.c:9936 | `static_3_800A2BE4` | `0x800A2CAC` | `0x004C7A54` | `dsllv t7 t4 v0 None` | `.word       0x004C7A54                   # dsllv       $t7, $t4, $v0 # 00000240 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10018 | `static_3_800A2BE4` | `0x800A2D28` | `0x00503354` | `dsllv a2 s0 v0 None` | `.word       0x00503354                   # dsllv       $a2, $s0, $v0 # 00000340 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10020 | `static_3_800A2BE4` | `0x800A2D2C` | `0x005C8956` | `dsrlv s1 gp v0 None` | `.word       0x005C8956                   # dsrlv       $s1, $gp, $v0 # 00000140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10060 | `static_3_800A2BE4` | `0x800A2D6C` | `0x0065CB57` | `dsrav t9 a1 v1 None` | `.word       0x0065CB57                   # dsrav       $t9, $a1, $v1 # 00000340 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10096 | `static_3_800A2BE4` | `0x800A2DA4` | `0x00521E54` | `dsllv v1 s2 v0 None` | `.word       0x00521E54                   # dsllv       $v1, $s2, $v0 # 00000640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10098 | `static_3_800A2BE4` | `0x800A2DA8` | `0x00610C56` | `dsrlv at at v1 None` | `.word       0x00610C56                   # dsrlv       $at, $at, $v1 # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10138 | `static_3_800A2BE4` | `0x800A2DE8` | `0x006AC157` | `dsrav t8 t2 v1 None` | `.word       0x006AC157                   # dsrav       $t8, $t2, $v1 # 00000140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10174 | `static_3_800A2BE4` | `0x800A2E20` | `0x00514C54` | `dsllv t1 s1 v0 None` | `.word       0x00514C54                   # dsllv       $t1, $s1, $v0 # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10176 | `static_3_800A2BE4` | `0x800A2E24` | `0x00635D56` | `dsrlv t3 v1 v1 None` | `.word       0x00635D56                   # dsrlv       $t3, $v1, $v1 # 00000540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10216 | `static_3_800A2BE4` | `0x800A2E64` | `0x006D4C57` | `dsrav t1 t5 v1 None` | `.word       0x006D4C57                   # dsrav       $t1, $t5, $v1 # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10258 | `static_3_800A2E98` | `0x800A2EA0` | `0x00625F56` | `dsrlv t3 v0 v1 None` | `.word       0x00625F56                   # dsrlv       $t3, $v0, $v1 # 00000740 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10290 | `static_3_800A2E98` | `0x800A2ED0` | `0x000C0554` | `dsllv zero t4 zero None` | `.word       0x000C0554                   # dsllv       $zero, $t4, $zero # 00000540 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:10292 | `static_3_800A2E98` | `0x800A2ED4` | `0x00241054` | `dsllv v0 a0 at None` | `.word       0x00241054                   # dsllv       $v0, $a0, $at # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10294 | `static_3_800A2E98` | `0x800A2ED8` | `0x003C1C54` | `dsllv v1 gp at None` | `.word       0x003C1C54                   # dsllv       $v1, $gp, $at # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10296 | `static_3_800A2E98` | `0x800A2EDC` | `0x00542754` | `dsllv a0 s4 v0 None` | `.word       0x00542754                   # dsllv       $a0, $s4, $v0 # 00000740 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10298 | `static_3_800A2E98` | `0x800A2EE0` | `0x006C3457` | `dsrav a2 t4 v1 None` | `.word       0x006C3457                   # dsrav       $a2, $t4, $v1 # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10374 | `static_3_800A2F28` | `0x800A2F50` | `0x000E8C56` | `dsrlv s1 t6 zero None` | `.word       0x000E8C56                   # dsrlv       $s1, $t6, $zero # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10376 | `static_3_800A2F28` | `0x800A2F54` | `0x002BA456` | `dsrlv s4 t3 at None` | `.word       0x002BA456                   # dsrlv       $s4, $t3, $at # 00000440 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10378 | `static_3_800A2F28` | `0x800A2F58` | `0x0048BD56` | `dsrlv s7 t0 v0 None` | `.word       0x0048BD56                   # dsrlv       $s7, $t0, $v0 # 00000540 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10380 | `static_3_800A2F28` | `0x800A2F5C` | `0x0065D556` | `dsrlv k0 a1 v1 None` | `.word       0x0065D556                   # dsrlv       $k0, $a1, $v1 # 00000540 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10414 | `static_3_800A2F28` | `0x800A2F90` | `0x000FFF57` | `dsrav ra t7 zero None` | `.word       0x000FFF57                   # dsrav       $ra, $t7, $zero # 00000740 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10416 | `static_3_800A2F28` | `0x800A2F94` | `0x002FFE57` | `dsrav ra t7 at None` | `.word       0x002FFE57                   # dsrav       $ra, $t7, $at # 00000640 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10418 | `static_3_800A2F28` | `0x800A2F98` | `0x004FFE57` | `dsrav ra t7 v0 None` | `.word       0x004FFE57                   # dsrav       $ra, $t7, $v0 # 00000640 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10420 | `static_3_800A2F28` | `0x800A2F9C` | `0x006FFD57` | `dsrav ra t7 v1 None` | `.word       0x006FFD57                   # dsrav       $ra, $t7, $v1 # 00000540 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10468 | `static_3_800A2FE4` | `0x800A2FF0` | `0x001965FF` | `dsra32 t4 t9 None 23` | `dsra32      $t4, $t9, 23` | yes | reachable | **correct** |
| funcs_49.c:10474 | `static_3_800A2FE4` | `0x800A2FF8` | `0x001C823F` | `dsra32 s0 gp None 8` | `dsra32      $s0, $gp, 8` | yes | reachable | **correct** |
| funcs_49.c:10477 | `static_3_800A2FE4` | `0x800A2FFC` | `0x001E3438` | `dsll a2 fp None 16` | `dsll        $a2, $fp, 16` | yes | reachable | **correct** |
| funcs_49.c:10496 | `static_3_800A2FE4` | `0x800A3018` | `0x002D413E` | `dsrl32 t0 t5 None 4` | `.word       0x002D413E                   # dsrl32      $t0, $t5, 4 # 00200000 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10500 | `static_3_800A2FE4` | `0x800A3020` | `0x0032CBFF` | `dsra32 t9 s2 None 15` | `.word       0x0032CBFF                   # dsra32      $t9, $s2, 15 # 00200000 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10504 | `static_3_800A2FE4` | `0x800A3028` | `0x0039047E` | `dsrl32 zero t9 None 17` | `.word       0x0039047E                   # dsrl32      $zero, $t9, 17 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:10514 | `static_3_800A2FE4` | `0x800A303C` | `0x004C1BFA` | `dsrl v1 t4 None 15` | `.word       0x004C1BFA                   # dsrl        $v1, $t4, 15 # 00400000 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10520 | `static_3_800A2FE4` | `0x800A3048` | `0x005A827C` | `dsll32 s0 k0 None 9` | `.word       0x005A827C                   # dsll32      $s0, $k0, 9 # 00400000 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10524 | `static_3_800A2FE4` | `0x800A3050` | `0x006597FE` | `dsrl32 s2 a1 None 31` | `.word       0x006597FE                   # dsrl32      $s2, $a1, 31 # 00600000 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10528 | `static_3_800A2FE4` | `0x800A3058` | `0x007208FC` | `dsll32 at s2 None 3` | `.word       0x007208FC                   # dsll32      $at, $s2, 3 # 00600000 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10548 | `static_3_800A2FE4` | `0x800A3080` | `0x00CB2FFC` | `dsll32 a1 t3 None 31` | `.word       0x00CB2FFC                   # dsll32      $a1, $t3, 31 # 00C00000 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10552 | `static_3_800A2FE4` | `0x800A3088` | `0x00E411F8` | `dsll v0 a0 None 7` | `.word       0x00E411F8                   # dsll        $v0, $a0, 7 # 00E00000 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10567 | `static_3_800A2FE4` | `0x800A30A0` | `0x01428A3A` | `dsrl s1 v0 None 8` | `.word       0x01428A3A                   # dsrl        $s1, $v0, 8 # 01400000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10575 | `static_3_800A2FE4` | `0x800A30B0` | `0x01965FF8` | `dsll t3 s6 None 31` | `.word       0x01965FF8                   # dsll        $t3, $s6, 31 # 01800000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10592 | `static_3_800A2FE4` | `0x800A30CC` | `0x0260DFD4` | `dsllv k1 zero s3 None` | `.word       0x0260DFD4                   # dsllv       $k1, $zero, $s3 # 000007C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10596 | `static_3_800A2FE4` | `0x800A30D4` | `0x02AB7038` | `dsll t6 t3 None 0` | `.word       0x02AB7038                   # dsll        $t6, $t3, 0 # 02A00000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:11587 | `static_4_801096D8` | `0x801096D8` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:11589 | `static_4_801096D8` | `0x801096DC` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:11591 | `static_4_801096D8` | `0x801096E0` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:11593 | `static_4_801096D8` | `0x801096E4` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:11595 | `static_4_801096D8` | `0x801096E8` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:11597 | `static_4_801096D8` | `0x801096EC` | `0x00140014` | `dsllv zero s4 zero None` | `dsllv       $zero, $s4, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:11605 | `static_4_801096D8` | `0x801096FC` | `0x000A0014` | `dsllv zero t2 zero None` | `dsllv       $zero, $t2, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:11607 | `static_4_801096D8` | `0x80109700` | `0x001E0014` | `dsllv zero fp zero None` | `dsllv       $zero, $fp, $zero` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_49.c:11609 | `static_4_801096D8` | `0x80109704` | `0x003C0014` | `dsllv zero gp at None` | `dsllv       $zero, $gp, $at` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_7.c:2768 | `swizzleTextureRowsToTmem` | `0x800248AC` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2774 | `swizzleTextureRowsToTmem` | `0x800248B8` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2780 | `swizzleTextureRowsToTmem` | `0x800248C4` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2786 | `swizzleTextureRowsToTmem` | `0x800248D0` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2792 | `swizzleTextureRowsToTmem` | `0x800248DC` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2798 | `swizzleTextureRowsToTmem` | `0x800248E8` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2804 | `swizzleTextureRowsToTmem` | `0x800248F4` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2840 | `swizzleTextureRowsToTmem` | `0x80024928` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2846 | `swizzleTextureRowsToTmem` | `0x80024934` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2852 | `swizzleTextureRowsToTmem` | `0x80024940` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2858 | `swizzleTextureRowsToTmem` | `0x8002494C` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2864 | `swizzleTextureRowsToTmem` | `0x80024958` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2870 | `swizzleTextureRowsToTmem` | `0x80024964` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2876 | `swizzleTextureRowsToTmem` | `0x80024970` | `0x00084238` | `dsll t0 t0 None 8` | `dsll        $t0, $t0, 8` | yes | reachable | **correct** |
| funcs_7.c:2920 | `swizzleTextureRowsToTmem` | `0x800249AC` | `0x0008403C` | `dsll32 t0 t0 None 0` | `dsll32      $t0, $t0, 0` | yes | reachable | **correct** |
| funcs_7.c:2954 | `swizzleTextureRowsToTmem` | `0x800249DC` | `0x0008403C` | `dsll32 t0 t0 None 0` | `dsll32      $t0, $t0, 0` | yes | reachable | **correct** |
| funcs_8.c:11149 | `__OSGlobalIntMask` | `0x80039270` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11159 | `__OSGlobalIntMask` | `0x80039284` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11193 | `__OSGlobalIntMask` | `0x800392C0` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11203 | `__OSGlobalIntMask` | `0x800392D4` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11284 | `__OSGlobalIntMask` | `0x80039360` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11294 | `__OSGlobalIntMask` | `0x80039374` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11339 | `__OSGlobalIntMask` | `0x800393C4` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11373 | `__OSGlobalIntMask` | `0x80039400` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11383 | `__OSGlobalIntMask` | `0x80039414` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11428 | `__OSGlobalIntMask` | `0x80039464` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11467 | `__OSGlobalIntMask` | `0x800394A0` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11477 | `__OSGlobalIntMask` | `0x800394B4` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11527 | `__OSGlobalIntMask` | `0x80039504` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11566 | `__OSGlobalIntMask` | `0x80039540` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11576 | `__OSGlobalIntMask` | `0x80039554` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11626 | `__OSGlobalIntMask` | `0x800395A4` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11671 | `__OSGlobalIntMask` | `0x800395F4` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11716 | `__OSGlobalIntMask` | `0x80039644` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11761 | `__OSGlobalIntMask` | `0x80039694` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11806 | `__OSGlobalIntMask` | `0x800396E4` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11855 | `__OSGlobalIntMask` | `0x80039734` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:11904 | `__OSGlobalIntMask` | `0x80039784` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:12625 | `__OSGlobalIntMask` | `0x80039C20` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:12635 | `__OSGlobalIntMask` | `0x80039C34` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:12685 | `__OSGlobalIntMask` | `0x80039C84` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:12724 | `__OSGlobalIntMask` | `0x80039CC0` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:12734 | `__OSGlobalIntMask` | `0x80039CD4` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:12784 | `__OSGlobalIntMask` | `0x80039D24` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:12818 | `__OSGlobalIntMask` | `0x80039D60` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:12828 | `__OSGlobalIntMask` | `0x80039D74` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:12873 | `__OSGlobalIntMask` | `0x80039DC4` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:12907 | `__OSGlobalIntMask` | `0x80039E00` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:12917 | `__OSGlobalIntMask` | `0x80039E14` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:12962 | `__OSGlobalIntMask` | `0x80039E64` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:13007 | `__OSGlobalIntMask` | `0x80039EB4` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:13052 | `__OSGlobalIntMask` | `0x80039F04` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:13097 | `__OSGlobalIntMask` | `0x80039F54` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:13142 | `__OSGlobalIntMask` | `0x80039FA4` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:13187 | `__OSGlobalIntMask` | `0x80039FF4` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
| funcs_8.c:13232 | `__OSGlobalIntMask` | `0x8003A044` | `0x002501FF` | `dsra32 zero a1 None 7` | `.word       0x002501FF                   # dsra32      $zero, $a1, 7 # 00200000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable-or-zero** |
