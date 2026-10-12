# M3 s4683 `MEM_H` backward-loop census

## Scope and discriminator

The required pre-build commands were run against the external generated tree
at `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs`. The
working hypothesis was that a non-self, zero-offset signed-halfword load in a
backward loop might be a pointer transition requiring a guard.

Two independent interval scans found the same 97 load sites. The first scan
grouped them into 48 `(file,function,back-edge)` groups; a second scan grouped
nested back-edges differently and reported 39 groups, but also reported 97
sites. A raw `rg` count found 160 total non-self `MEM_H(ctx->rN,0)` loads;
the remaining 63 are not enclosed by a backward `goto` interval. Thus the
“19 sites” in the prior work order is stale for this generated snapshot.

The discriminator was whether the loaded halfword is subsequently used as a
guest address/pointer, rather than whether it merely comes from a pointer-base
address. The complete table below records every backward-loop site. The
immediate-consumer review found scalar index, interpolation, animation,
geometry, text, or audio coefficient use at every site. Eight sites form an
address expression after scaling or addition, but their values are array
indices/offsets; none is loaded and then dereferenced as an unscaled guest
pointer. No named writer publishes a canonical or noncanonical pointer here.

## Complete site table

`lines` are generated source lines; each row is one function/back-edge group.

| file | function | back-edge | lines | classification |
|---|---|---|---|---|
| funcs_8.c | bcopy_recomp | L_8003405C | 4695,4700,4723 | bounded copy/index |
| funcs_11.c | trackResourceListWithMappingTables | L_800539A0 | 16913,17021 | table scalar |
| funcs_11.c | tickWrappingTimerAccumulatorList | L_800546A8 | 20051 | timer scalar |
| funcs_34.c | renderRadarSweep | L_800C5C94 | 8955,8957,9313,9350 | geometry scalar |
| funcs_30.c | layoutMenuTextRow | L_800B18AC | 4908 | text offset |
| funcs_41.c | gatherAndSortNearbyNpcViewPoints | L_800F1448/L_800F1464 | 440,478,616,631 | sort/index scalar |
| funcs_20.c | findModelAnimKeyframeByPhase | L_8008270C | 2923 | animation index |
| funcs_20.c | parseModelAnimType2Entry | L_80083588 | 5573,5595,5708,5773,5795,5908,6349,6371,6484 | bounded animation table |
| funcs_24.c | interpolatePointTableSamplesToPackedWord | L_80092760/L_80092768/L_8009276C | 11868,11918,11968 | interpolation scalar |
| funcs_24.c | interpolateLutSamplesToPackedWord | L_80092A04/L_80092A0C/L_80092A10 | 12372,12428,12484 | LUT scalar |
| funcs_24.c | interpolateConstantSamplesToPackedWord | L_80092C6C/L_80092C7C/L_80092C8C/L_80092C9C | 12814,12871,12927,12983 | constant/interpolation scalar |
| funcs_12.c | tickVoiceSubtitleDisplay | L_80055E48 | 2662 | subtitle scalar |
| funcs_33.c | findHudElementExtremes | L_800BFEFC/L_800BFF4C/L_800BFF9C/L_800BFFEC | 6005,6007,6067,6069,6129,6131,6191,6193 | HUD index scalar |
| funcs_33.c | transformSceneMeshVertices | L_800C2674 | 23926,23999 | vertex/index scalar |
| funcs_33.c | runPauseMenuStateMachine | L_800C2AAC/L_800C30C4 | 26752,27037,27290,27397,27483,27652,27740,28026,28329,28391 | menu/text index |
| funcs_29.c | runScriptedCraftCinematicEvent | L_800B11EC | 20037 | event scalar |
| funcs_27.c | updateVoiceChannelParams | L_8009C530 | 1779,1781,1798,1800 | voice coefficient |
| funcs_27.c | updateVoiceChannelParamsLarge | L_8009C870 | 2329,2331,2355,2357 | voice coefficient |
| funcs_27.c | decodeAndFillVoiceBlock | L_8009D724 | 5001,5003,5027,5029 | voice sample scalar |
| funcs_27.c | filterVoiceSampleBlock | L_8009D83C/L_8009D89C | 5192,5256 | filter coefficient |
| funcs_27.c | applyVoiceDelayFilter | L_8009D93C | 5390 | filter coefficient |
| funcs_36.c | emitDebrisCellFaces | L_800C7BD0 | 1598,1608,1681,1793 | geometry index |
| funcs_19.c | transformMeshVerticesForNpc | L_8007AA2C | 5310,5316,5446,5464 | vertex scalar |
| funcs_13.c | loadSkyHorizonHob | L_8005AC3C/L_8005ACE8 | 5024,5163,5165 | horizon index |
| funcs_17.c | multiEventTemplateNpcHandler | L_80070798 | 10355,10409 | event/table scalar |
| funcs_4.c | drawSubtitleText | L_800164A4/L_80016904 | 26421,27384 | text offset |
| funcs_32.c | controllerSettingsScreen | L_800BD540 | 23431 | menu scalar |
| funcs_43.c | applyCraftAnimationKeyframePose | L_80100384 | 13598 | animation scalar |
| funcs_28.c | transformAndNormalizeDirectionByMatrix | L_800ADCF8 | 38095,38168 | vector scalar |
| funcs_9.c | scanConvertTriangleToSpanTable | L_800425F8/L_80042740 | 12028,12030,12323,12325 | raster index |
| funcs_14.c | measurePlayerSlotTextLayout | L_80062490/L_80062548 | 3883,3981 | text offset |

## Result

The static result selects `H-MEMH-bounded` for this snapshot and rejects
`H-MEMH-invalid` as a guard candidate. It also rejects
`H-MEMH-unreached` as the useful explanation: the sites are ordinary active
game algorithms, but their values are scalar data, not linked pointers. No
build, runtime probe, guard, or mitigation was authorized. The allocator and
free-list controls remain relevant only to the separate `MEM_W` pointer-walk
class.

Evidence is single-source in the sense that both scans inspect generated
source rather than retail execution; the second scan independently confirms
the candidate count, while the consumer classification is code-reading
evidence. A future runtime probe would be required only if a new symptom names
one of these scalar sites specifically.
