# s2462 slot-dispatch callback provenance audit

Date: 2026-08-26

## Scope and sources

This is a static audit of the current generated tree at
`/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs`, cross-checked
against the companion symbol files and `docs/game-architecture.md`. The
callback consumed by `slotDispatcherIter` at `0x8003E974` is the word at NPC
context `+0x00`; the context pointer is reached from the NPC slot list at
`0x80130BB0`.

The census found 144 callsites in 72 distinct generated functions. The list
below is complete; repeated PCs in a row are separate callsites in the same
caller.

## Generated caller census

| Caller | Call PCs |
|---|---|
| assignNpcTargetAndPosition | 0x80041DD0 |
| attachChildNpcByIndex | 0x80041D2C |
| attachedAudioVisualEmitterNpcHandler | 0x800812F4 |
| audioCueDispatcherNpcHandler | 0x8005CC00, 0x8005D35C, 0x8005D554 |
| broadcastSceneEventWithPayload | 0x800C404C |
| broadcastSceneShutdownAndCleanup | 0x800C4000 |
| cinematicLoopBody | 0x800A6388, 0x800A6398, 0x800A63A8, 0x800A63B8, 0x800A63C8, 0x800A63D8, 0x800A63E8 |
| cinematicSlotBatchDispatch | 0x800A7114, 0x800A7124, 0x800A7134, 0x800A7144, 0x800A7154, 0x800A7164, 0x800A7178 |
| collectNearbyNpcsForEffect | 0x8005DA94 |
| computeNpcGroupCentroidAndCull | 0x80041668 |
| cutsceneActorNpcHandler | 0x80044B9C |
| dealDamagetoDatItem | 0x800C73F8, 0x800C7450 |
| despawnEffectOnNamedDatItem | 0x800C7CD4 |
| dispatchHudInstanceWeaponEffect | 0x800FE6DC, 0x800FEA94 |
| dispatchSlotAction5IfActive | 0x800EFDC4 |
| dispatchSlotActionTwelveByGlobalId | 0x800ECDF0 |
| emitTrailPuffAndCue | 0x8005F94C, 0x8005F964 |
| executeActorType1Effect | 0x800F4250, 0x800F4310, 0x800F48C0, 0x800F4A94 |
| executeActorType4Effect | 0x800F9358, 0x800F941C |
| getDatItemHealth | 0x800C7BC0 |
| guidedEffectNpcHandler | 0x800600A0, 0x80060198 |
| heavyMechSubEffectNpcHandler | 0x8007951C, 0x800795E4 |
| npcAtAtUpdate | 0x800CDFE4 |
| npcPowerGeneratorUpdate | 0x80078894 |
| npcProbeDriod | 0x800CB8C0 |
| npcShieldGeneratorUpdate | 0x80081A30 |
| npcShuttleUpdate | 0x800D4D0C |
| npcTexturedEffectUpdateWithSlotChain | 0x8007CCE8, 0x8007CD0C |
| npcTickEffectChannelShared | 0x800D621C |
| npcTickEffectChannelWithSlotDispatch | 0x800D336C |
| npcTieVariantTickAttachmentEffect | 0x800DAB20 |
| npcTieVariantTickEffects | 0x800DA56C, 0x800DA680, 0x800DA6B0 |
| npcTieVariantUpdate | 0x800DC080 |
| npcTrainCarUpdate | 0x800E30BC, 0x800E315C, 0x800E3EB0 |
| npcVortexUpdate | 0x80081F58 |
| npcWalkerUpdate | 0x8007E29C |
| npcWingmanStateEffectShared | 0x800D7C20 |
| npcWordDevastatorUpdate | 0x8007F708, 0x8007F9C4, 0x8007FB40 |
| playAttachmentCueWithSlotIter | 0x800E039C |
| playerAtStUpdate | 0x800D2AEC |
| playerT16MainUpdate | 0x800BD3C4 |
| processAtAtSubFeatureSlot | 0x800CCC40 |
| resolveNpcContextByIndex | 0x80041EC8 |
| runInMissionFrame | 0x800FA954, 0x800FA964, 0x800FA974, 0x800FA984, 0x800FA994, 0x800FA9A4, 0x800FA9B4, 0x800FA9C4, 0x800FA9D4, 0x800FA9E4, 0x800FA9F4, 0x800FAA04, 0x800FAA14, 0x800FAA24, 0x800FAA70, 0x800FAB88, 0x800FAB98, 0x800FABA8, 0x800FABC8, 0x800FABB8, 0x800FABD8, 0x800FABE8, 0x800FABF8, 0x800FAC08, 0x800FAC18, 0x800FAC28, 0x800FAC38, 0x800FAC60 |
| sendSlotActionTwelve | 0x80072AE4 |
| setNpcForwardVectorByIndex | 0x80041E70 |
| setupNpcUpdateFunctions | 0x80065694 |
| spawnCutsceneDebrisField | 0x800AB028, 0x800AB30C, 0x800AB4D0 |
| spawnDatDrivenAudioVisualEmitters | 0x8007D388, 0x8007D44C |
| spawnDatStructureNpcByType | 0x80065770 |
| spawnEffectOnNamedDatItem | 0x800C79D0 |
| spawnInheritedNpcVariantA | 0x8003F830, 0x8003F858 |
| spawnInheritedNpcVariantB | 0x8003F9C4, 0x8003F9EC |
| spawnInheritedNpcVariantC | 0x8003FBA8, 0x8003FBD0 |
| spawnNamedTexturedEmitterNpc | 0x8007D5FC, 0x8007D630, 0x8007D7C4 |
| spawnNpcAnchoredEffectSlot | 0x800F9DE0, 0x800F9E0C |
| spawnNpcDestructionEffect | 0x800C8464, 0x800C8478 |
| spawnNpcImpactEffectVariant | 0x800C88DC, 0x800C88F0 |
| spawnNpcOfType | 0x80040110 |
| spawnNpcWithSubtype | 0x8003FFC0 |
| spawnObjectImpactEffectWithSound | 0x800E9E68 |
| spawnRandomBurstNpc | 0x80041AF4 |
| sprayEffectEmitterNpcHandler | 0x8005E0C4 |
| stepObjectOrientationTowardTarget | 0x800FF260, 0x800FFC88, 0x800FFD78 |
| tickActorTexturedSoundEffect | 0x800CC250 |
| tickCinematicEffectObject | 0x800ACAC8, 0x800ACB28, 0x800ACC90 |
| tickMissionObjectives | 0x800FBCC0 |
| triggerCueWithSlotEffect | 0x800F3078 |
| triggerPlayerVehicleSpecialSlotEffect | 0x800AD364 |
| triggerT16Effect | 0x800BD9F8 |
| tryPlaySpatialSoundWithGates | 0x800B3E24 |
| updateNpcEffectIntensity | 0x800F4070 |

## Callback-writer table

| Site | Writer and value | Classification |
|---|---|---|
| `funcs_8.c:0x8003E65C` | `allocateNpcSlot`; `sw $zero, 0x0($v0)` after selecting a free context | Zero initialization only. It is legitimate during allocation, before the handler is installed. |
| `funcs_9.c:0x800400BC` | `spawnNpcOfType`; `sw $s2, 0x0($s0)`, where `$s2` is the handler argument | Nonzero dynamic writer when the caller supplies a handler; static code does not prove the argument is nonzero for every caller. |
| `funcs_15.c:0x800653F4..0x80065654` | `setupNpcUpdateFunctions`; type-table branches load a handler address into `$a0`, then call `spawnNpcOfType` at `0x80065664` | Nonzero generated handler selection for recognized types. Unsupported/out-of-range type takes the failure path and does not install a handler. |
| `funcs_9.c:0x800400FC` | `spawnNpcOfType`; stores the newly-created context pointer into the slot-list entry at `+0x00` | Slot-list link writer, not the context callback field. Excluded from callback provenance. |

No other generated store can be proven to target the NPC context callback
field. The broad `sw ...,0x0(register)` census contains many unrelated
structures; the lifecycle chain above is the only one whose base is proven to
be an element of `gNpcContextArray` and whose field is consumed by
`slotDispatcherIter`.

## Result

The complete static census selects **H-UnresolvedWriter**, with a qualified
zero edge. `allocateNpcSlot` legitimately creates a zero-callback context,
but `spawnNpcOfType` installs the callback from a dynamic handler argument.
The generated caller table alone cannot prove that every path into
`spawnNpcOfType` supplies a nonzero argument, and the type-table failure path
can leave a newly allocated context without a handler. This audit therefore
does not select H-ZeroWriter as a reachable post-install state, nor H-ValidWriter
as a universal invariant.

This is static evidence only. It does not identify the live field writer for
the s2461 pre-target failure and authorizes no guard, dispatch change, or audio
behavior change. The next discriminating probe must capture the handler
argument at `spawnNpcOfType` and the context field immediately before each
phase-gated dispatch, with the existing indirect resolver positive control.
