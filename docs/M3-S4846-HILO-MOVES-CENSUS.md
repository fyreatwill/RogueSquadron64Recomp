# M3 HI/LO move census

Static census only. The retail ELF supplies the independent raw word; generated C supplies the lowering and conservative CFG reachability.

- annotation rows: **989**
- classifications: `ELF/annotation mismatch`=26, `correct`=916, `data-like/unreachable`=47
- positive control `0x80003444`: raw=`0x00001012`, decode=`mflo $v0`, lowering=present

## Site table

| file:line | function | guest PC | raw word | ELF decode | annotation | lowering | CFG | classification |
|---|---|---:|---:|---|---|---|---|---|
| funcs_0.c:819 | `partitionFramebufferMemory` | `0x80000E08` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_0.c:838 | `partitionFramebufferMemory` | `0x80000E28` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_0.c:859 | `partitionFramebufferMemory` | `0x80000E48` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_0.c:6663 | `computeElapsedMillis` | `0x800026D4` | `0x00002010` | `mfhi $a0` | `mfhi        $a0` | yes | unreachable | **correct** |
| funcs_0.c:6665 | `computeElapsedMillis` | `0x800026D8` | `0x00002812` | `mflo $a1` | `mflo        $a1` | yes | unreachable | **correct** |
| funcs_1.c:285 | `rand_recomp` | `0x80003444` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_1.c:6253 | `rs_zcalloc` | `0x80005294` | `0x00008812` | `mflo $s1` | `mflo        $s1` | yes | unreachable | **correct** |
| funcs_10.c:442 | `initGridLayerFromLevelData` | `0x80045924` | `0x00005812` | `mflo $t3` | `mflo        $t3` | yes | unreachable | **correct** |
| funcs_10.c:538 | `initGridLayerFromLevelData` | `0x800459BC` | `0x00005812` | `mflo $t3` | `mflo        $t3` | yes | unreachable | **correct** |
| funcs_10.c:2040 | `selectGridCellTileVariant` | `0x80046178` | `0x00006812` | `mflo $t5` | `mflo        $t5` | yes | unreachable | **correct** |
| funcs_10.c:2218 | `buildGridCellLabel` | `0x80046290` | `0x00005812` | `mflo $t3` | `mflo        $t3` | yes | unreachable | **correct** |
| funcs_10.c:2693 | `loadGridCellTilesByDistance` | `0x8004651C` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_10.c:3015 | `parseDatItemCommon` | `0x800466D0` | `0x00006812` | `mflo $t5` | `mflo        $t5` | yes | unreachable | **correct** |
| funcs_10.c:5168 | `loadDatFile` | `0x80047028` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_10.c:5186 | `loadDatFile` | `0x80047044` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_10.c:5223 | `loadDatFile` | `0x80047078` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_10.c:6136 | `updateActiveGridCellState` | `0x800474D4` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_10.c:8521 | `allocAndInitGridCellArray` | `0x8004809C` | `0x00006810` | `mfhi $t5` | `mfhi        $t5` | yes | unreachable | **correct** |
| funcs_10.c:8658 | `loadLevelTextureCache` | `0x8004814C` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_10.c:9442 | `getGridCellValueAt` | `0x80048568` | `0x00006812` | `mflo $t5` | `mflo        $t5` | yes | unreachable | **correct** |
| funcs_10.c:9799 | `getGridCellValueAt` | `0x8004877C` | `0x00006812` | `mflo $t5` | `mflo        $t5` | yes | unreachable | **correct** |
| funcs_10.c:10301 | `clampGridCellLookup` | `0x80048A1C` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_10.c:10877 | `processGridCellByDistance` | `0x80048D64` | `0x00006812` | `mflo $t5` | `mflo        $t5` | yes | unreachable | **correct** |
| funcs_10.c:10970 | `processGridCellByDistance` | `0x80048DF4` | `0x00006812` | `mflo $t5` | `mflo        $t5` | yes | unreachable | **correct** |
| funcs_10.c:12819 | `emitGridCellTileStrip` | `0x80049854` | `0x00004812` | `mflo $t1` | `mflo        $t1` | yes | unreachable | **correct** |
| funcs_10.c:13545 | `emitGridCellTileStripAdjacent` | `0x80049BFC` | `0x00004812` | `mflo $t1` | `mflo        $t1` | yes | unreachable | **correct** |
| funcs_10.c:14354 | `emitGridCellTileStripDiagonal` | `0x80049FF8` | `0x00006012` | `mflo $t4` | `mflo        $t4` | yes | unreachable | **correct** |
| funcs_10.c:16872 | `mapCellGeometryToGridSpace` | `0x8004AAF0` | `0x00004812` | `mflo $t1` | `mflo        $t1` | yes | unreachable | **correct** |
| funcs_10.c:18524 | `scaleObjectPosToGridUnits` | `0x8004B308` | `0x0000A012` | `mflo $s4` | `mflo        $s4` | yes | unreachable | **correct** |
| funcs_10.c:22114 | `getGridCellFromWorldPos` | `0x8004C3B0` | `0x0000A012` | `mflo $s4` | `mflo        $s4` | yes | unreachable | **correct** |
| funcs_11.c:4868 | `updateMultiNodeAudioListeners` | `0x80050580` | `0x00003810` | `mfhi $a3` | `mfhi        $a3` | yes | unreachable | **correct** |
| funcs_11.c:17270 | `updateAnimatedTextureStreaming` | `0x800541AC` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_11.c:17408 | `updateAnimatedTextureStreaming` | `0x80054234` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_11.c:18134 | `randomizeListEntrySpacing` | `0x800545B8` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_11.c:18557 | `tickWrappingTimerAccumulatorList` | `0x80054748` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_11.c:18597 | `tickWrappingTimerAccumulatorList` | `0x80054774` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_11.c:18994 | `loadAssetIntoNewSlot` | `0x80054954` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_11.c:19061 | `loadAssetIntoNewSlot` | `0x800549B0` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_11.c:19570 | `getPoolEntryFrameIndex` | `0x80054C48` | `0x00001010` | `mfhi $v0` | `mfhi        $v0` | yes | unreachable | **correct** |
| funcs_11.c:20546 | `loadAssetAndIterateSubchunks` | `0x800550E0` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_12.c:327 | `loadSpriteSheetTextureFrames` | `0x80055304` | `0x0000A012` | `mflo $s4` | `mflo        $s4` | yes | unreachable | **correct** |
| funcs_12.c:499 | `loadSpriteSheetTextureFrames` | `0x800553EC` | `0x00008812` | `mflo $s1` | `mflo        $s1` | yes | unreachable | **correct** |
| funcs_12.c:2336 | `tickVoiceSubtitleDisplay` | `0x80055DD0` | `0x00005010` | `mfhi $t2` | `mfhi        $t2` | yes | unreachable | **correct** |
| funcs_12.c:2603 | `tickVoiceSubtitleDisplay` | `0x80055F48` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_12.c:3085 | `setSubtitleOverlayScreenPos` | `0x800561E4` | `0x00008012` | `mflo $s0` | `mflo        $s0` | yes | unreachable | **correct** |
| funcs_12.c:3097 | `setSubtitleOverlayScreenPos` | `0x800561FC` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_12.c:3123 | `setSubtitleOverlayScreenPos` | `0x80056224` | `0x00008812` | `mflo $s1` | `mflo        $s1` | yes | unreachable | **correct** |
| funcs_12.c:3131 | `setSubtitleOverlayScreenPos` | `0x80056234` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_12.c:3173 | `setSubtitleOverlayScreenPos` | `0x8005627C` | `0x00003810` | `mfhi $a3` | `mfhi        $a3` | yes | unreachable | **correct** |
| funcs_12.c:5127 | `load_hmt_and_hob` | `0x80056CA0` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_12.c:5339 | `isHobObjectLoaded` | `0x80056DE0` | `0x00006010` | `mfhi $t4` | `mfhi        $t4` | yes | unreachable | **correct** |
| funcs_12.c:5624 | `walkMeshdef0List` | `0x80056F18` | `0x00005010` | `mfhi $t2` | `mfhi        $t2` | yes | unreachable | **correct** |
| funcs_12.c:6384 | `instantiateNamedMeshInstance` | `0x8005738C` | `0x00006010` | `mfhi $t4` | `mfhi        $t4` | yes | unreachable | **correct** |
| funcs_12.c:6709 | `applyRgbaTintToMeshVertices` | `0x8005757C` | `0x00002010` | `mfhi $a0` | `mfhi        $a0` | yes | unreachable | **correct** |
| funcs_12.c:6729 | `applyRgbaTintToMeshVertices` | `0x800575A4` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_12.c:6743 | `applyRgbaTintToMeshVertices` | `0x800575C0` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_12.c:6759 | `applyRgbaTintToMeshVertices` | `0x800575E0` | `0x00003810` | `mfhi $a3` | `mfhi        $a3` | yes | unreachable | **correct** |
| funcs_12.c:6796 | `applyRgbaTintToMeshVertices` | `0x80057620` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6807 | `applyRgbaTintToMeshVertices` | `0x80057634` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6818 | `applyRgbaTintToMeshVertices` | `0x80057648` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6829 | `applyRgbaTintToMeshVertices` | `0x8005765C` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6852 | `applyRgbaTintToMeshVertices` | `0x80057680` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6863 | `applyRgbaTintToMeshVertices` | `0x80057694` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6874 | `applyRgbaTintToMeshVertices` | `0x800576A8` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6885 | `applyRgbaTintToMeshVertices` | `0x800576BC` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6896 | `applyRgbaTintToMeshVertices` | `0x800576D0` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6907 | `applyRgbaTintToMeshVertices` | `0x800576E4` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6918 | `applyRgbaTintToMeshVertices` | `0x800576F8` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6929 | `applyRgbaTintToMeshVertices` | `0x8005770C` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6952 | `applyRgbaTintToMeshVertices` | `0x80057730` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6963 | `applyRgbaTintToMeshVertices` | `0x80057744` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6974 | `applyRgbaTintToMeshVertices` | `0x80057758` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:6985 | `applyRgbaTintToMeshVertices` | `0x8005776C` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_12.c:7290 | `releaseMeshAsset` | `0x80057918` | `0x00003810` | `mfhi $a3` | `mfhi        $a3` | yes | unreachable | **correct** |
| funcs_12.c:7757 | `getHobObjectByName` | `0x80057B88` | `0x00006010` | `mfhi $t4` | `mfhi        $t4` | yes | unreachable | **correct** |
| funcs_13.c:2807 | `loadTopCloudsAsset` | `0x8005A2EC` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_13.c:4107 | `updateWalkerParticlePositions` | `0x8005A95C` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_13.c:6327 | `setupWalkerSpriteTileQuad` | `0x8005B570` | `0x00006010` | `mfhi $t4` | `mfhi        $t4` | yes | unreachable | **correct** |
| funcs_13.c:6363 | `setupWalkerSpriteTileQuad` | `0x8005B5A0` | `0x00006010` | `mfhi $t4` | `mfhi        $t4` | yes | unreachable | **correct** |
| funcs_13.c:7081 | `setupWalkerSpriteTileQuad` | `0x8005B8D4` | `0x00006010` | `mfhi $t4` | `mfhi        $t4` | yes | unreachable | **correct** |
| funcs_13.c:7294 | `setupWalkerSpriteTileQuad` | `0x8005B9CC` | `0x00006010` | `mfhi $t4` | `mfhi        $t4` | yes | unreachable | **correct** |
| funcs_13.c:10706 | `audioCueDispatcherNpcHandler` | `0x8005C954` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_13.c:11776 | `audioCueDispatcherNpcHandler` | `0x8005CE6C` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_13.c:25053 | `randomlyScaledColoredEffectNpcHandler` | `0x80060C88` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_14.c:1031 | `loadCharTextureSet` | `0x80061708` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_14.c:1041 | `loadCharTextureSet` | `0x8006171C` | `0x00006012` | `mflo $t4` | `mflo        $t4` | yes | unreachable | **correct** |
| funcs_14.c:1060 | `loadCharTextureSet` | `0x80061738` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_14.c:1074 | `loadCharTextureSet` | `0x80061754` | `0x00006012` | `mflo $t4` | `mflo        $t4` | yes | unreachable | **correct** |
| funcs_14.c:1183 | `loadCharTextureSet` | `0x800617E4` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_14.c:1199 | `loadCharTextureSet` | `0x80061804` | `0x00002812` | `mflo $a1` | `mflo        $a1` | yes | unreachable | **correct** |
| funcs_14.c:1632 | `loadCharTextureSet` | `0x80061A24` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_14.c:1652 | `loadCharTextureSet` | `0x80061A3C` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_14.c:3952 | `startPlayerSlotAnimationChannelExt` | `0x80062660` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_14.c:3974 | `startPlayerSlotAnimationChannelExt` | `0x80062688` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_14.c:4104 | `startPlayerSlotAnimationChannelExt` | `0x80062744` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_14.c:4124 | `startPlayerSlotAnimationChannelExt` | `0x80062768` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_14.c:4420 | `startPlayerSlotAnimationChannel` | `0x800628F8` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_14.c:4440 | `startPlayerSlotAnimationChannel` | `0x8006291C` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_14.c:4586 | `startPlayerSlotAnimationChannel` | `0x800629EC` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_14.c:4604 | `startPlayerSlotAnimationChannel` | `0x80062A0C` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_14.c:4844 | `advancePlayerAnimationPhase` | `0x80062B34` | `0x00003812` | `mflo $a3` | `mflo        $a3` | yes | unreachable | **correct** |
| funcs_14.c:5432 | `initPlayerSlotAnimationChannelFull` | `0x80062E10` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_14.c:5454 | `initPlayerSlotAnimationChannelFull` | `0x80062E38` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_14.c:5691 | `startPlayerSlotAnimationChannelFlagged` | `0x80062F80` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_14.c:5709 | `startPlayerSlotAnimationChannelFlagged` | `0x80062FA0` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_14.c:7745 | `buildPlayerCraftAssetTemplate` | `0x800639AC` | `0x00008012` | `mflo $s0` | `mflo        $s0` | yes | unreachable | **correct** |
| funcs_14.c:8464 | `setPlayerSlotAnimationFlag` | `0x80063D70` | `0x00004812` | `mflo $t1` | `mflo        $t1` | yes | unreachable | **correct** |
| funcs_14.c:8488 | `setPlayerSlotAnimationFlag` | `0x80063D9C` | `0x00004812` | `mflo $t1` | `mflo        $t1` | yes | unreachable | **correct** |
| funcs_16.c:831 | `wrapAngleToCyclicRange` | `0x80067FA4` | `0x00005812` | `mflo $t3` | `mflo        $t3` | yes | unreachable | **correct** |
| funcs_16.c:1777 | `sampleTerrainSurfaceAtWorldXz` | `0x800683B8` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_16.c:1887 | `sampleTerrainSurfaceAtWorldXz` | `0x80068464` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_16.c:1998 | `sampleTerrainSurfaceAtWorldXz` | `0x80068514` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_16.c:2120 | `sampleTerrainSurfaceAtWorldXz` | `0x800685D4` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_16.c:2234 | `sampleTerrainSurfaceAtWorldXz` | `0x80068684` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_16.c:4319 | `sampleTerrainAtNpcPosition` | `0x80068F28` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_16.c:4473 | `sampleTerrainAtNpcPosition` | `0x80068FC8` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_16.c:6950 | `isTerrainCellBlockedAtWorldXz` | `0x80069A6C` | `0x00004812` | `mflo $t1` | `mflo        $t1` | yes | unreachable | **correct** |
| funcs_16.c:19348 | `updateDestructionDebrisNpc` | `0x8006D104` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_16.c:19903 | `updateDestructionDebrisNpc` | `0x8006D3A8` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_17.c:4702 | `cycleIdleDemoId` | `0x8006F064` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_17.c:11362 | `multiEventTemplateNpcHandler` | `0x80070ED4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_18.c:1284 | `loadSfxAsset` | `0x80071E7C` | `0x00007810` | `mfhi $t7` | `mfhi        $t7` | yes | unreachable | **correct** |
| funcs_18.c:1304 | `loadSfxAsset` | `0x80071E9C` | `0x00007810` | `mfhi $t7` | `mfhi        $t7` | yes | unreachable | **correct** |
| funcs_18.c:1731 | `composeRandomRotationMatrix` | `0x800720A0` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_18.c:2035 | `composeRandomRotationMatrixVariant` | `0x80072208` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_18.c:10441 | `triggerObjectDestructionEffects` | `0x80074934` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_18.c:12556 | `buildRandomCameraFacingOrientation` | `0x800752DC` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_18.c:12951 | `buildRandomCameraFacingOrientation` | `0x800754C4` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_18.c:14763 | `buildNpcAnchoredCameraEffectTransform` | `0x80075D14` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_18.c:16617 | `npcPowerGeneratorHandleDestruction` | `0x80076544` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_19.c:2019 | `spawnNpcWithRandomRotation` | `0x80079AE4` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_19.c:2320 | `setRandomFacingDirection` | `0x80079C64` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_19.c:3348 | `sampleRgbBoxFilter2x2AtSubpixel` | `0x8007A138` | `0x00003812` | `mflo $a3` | `mflo        $a3` | yes | unreachable | **correct** |
| funcs_19.c:3392 | `sampleRgbBoxFilter2x2AtSubpixel` | `0x8007A184` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_19.c:3671 | `downscaleImageHalfResBoxFilter` | `0x8007A30C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_19.c:5051 | `transformMeshVerticesForNpc` | `0x8007AA4C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_19.c:5059 | `transformMeshVerticesForNpc` | `0x8007AA5C` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_19.c:5092 | `transformMeshVerticesForNpc` | `0x8007AA88` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_19.c:5100 | `transformMeshVerticesForNpc` | `0x8007AA98` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_19.c:5189 | `transformMeshVerticesForNpc` | `0x8007AAFC` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_19.c:5199 | `transformMeshVerticesForNpc` | `0x8007AB10` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_19.c:5209 | `transformMeshVerticesForNpc` | `0x8007AB24` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_19.c:7142 | `npcShieldUpdate` | `0x8007B3FC` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_19.c:7354 | `npcShieldUpdate` | `0x8007B518` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_19.c:18000 | `spawnWorldDevastatorVacuumDebris` | `0x8007E8A0` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_19.c:24469 | `attachedAudioVisualEmitterNpcHandler` | `0x80080760` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_19.c:27546 | `npcShieldGeneratorUpdate` | `0x8008168C` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_2.c:2683 | `initSaveData` | `0x800065B0` | `0x00005012` | `mflo $t2` | `mflo        $t2` | yes | unreachable | **correct** |
| funcs_2.c:2771 | `initSaveData` | `0x80006624` | `0x00005012` | `mflo $t2` | `mflo        $t2` | yes | unreachable | **correct** |
| funcs_2.c:3304 | `saveLoadDispatcher` | `0x800068B4` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_2.c:3504 | `loadOrSaveEepromRecord` | `0x800069B4` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_2.c:3804 | `loadOrSaveAllEepromRecords` | `0x80006B38` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_2.c:5878 | `u64DivU64` | `0x80007504` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_20.c:6731 | `unusedRand` | `0x80083C84` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_20.c:6876 | `setTrackVoiceTickBudget` | `0x80083D50` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_20.c:8952 | `evaluateVoiceModulatorRecord` | `0x80084968` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_20.c:9057 | `evaluateVoiceModulatorRecord` | `0x800849E4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_20.c:9115 | `evaluateVoiceModulatorRecord` | `0x80084A30` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_20.c:9193 | `evaluateVoiceModulatorRecord` | `0x80084A88` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_21.c:3208 | `binarySearchWithComparator` | `0x80085C64` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_21.c:3421 | `factor5BucketedTableLookupValue` | `0x80085D88` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_21.c:3617 | `factor5SortedTableLookupWidePairRecord` | `0x80085E84` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_21.c:3859 | `factor5SecondSortedTableLookupValue` | `0x80085FC0` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_21.c:4026 | `factor5SortedTableLookupValue` | `0x80086098` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_21.c:4213 | `factor5SortedTableLookupTaggedValue` | `0x80086188` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_21.c:4406 | `musyxSortedInsertByU16` | `0x80086284` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_21.c:5957 | `computeVoiceGlidePitch` | `0x80086A80` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_21.c:5965 | `computeVoiceGlidePitch` | `0x80086A90` | `0x00002812` | `mflo $a1` | `mflo        $a1` | yes | unreachable | **correct** |
| funcs_21.c:5975 | `computeVoiceGlidePitch` | `0x80086AA4` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_21.c:6369 | `findActiveVoiceByKeyPair` | `0x80086C94` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_21.c:6377 | `findActiveVoiceByKeyPair` | `0x80086CA4` | `0x00002812` | `mflo $a1` | `mflo        $a1` | yes | unreachable | **correct** |
| funcs_21.c:6387 | `findActiveVoiceByKeyPair` | `0x80086CB8` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_21.c:7878 | `applyNoteEventToGroup` | `0x80087488` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_21.c:8198 | `applyNoteEventToGroup` | `0x8008762C` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_21.c:8218 | `applyNoteEventToGroup` | `0x80087654` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_21.c:9069 | `dispatchSequencerNoteEvent` | `0x80087AA4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_21.c:9690 | `musyxNoteEventLockedDispatch` | `0x80087DF8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_21.c:9976 | `bsearchFactor5TableByU16Key` | `0x80087F70` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_21.c:10363 | `musyxSetSequenceParamLocked` | `0x80088154` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:1749 | `computeChannelTempoStepFromTable` | `0x800895AC` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:1925 | `computeChannelWaitDuration` | `0x8008968C` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_22.c:1946 | `computeChannelWaitDuration` | `0x800896AC` | `0x00002010` | `mfhi $a0` | `mfhi        $a0` | yes | unreachable | **correct** |
| funcs_22.c:2064 | `computeChannelWaitDuration` | `0x80089748` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:2593 | `soundMacroOpGosubRandomLoop` | `0x800899E4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:2916 | `soundMacroOpLoopRandomCount` | `0x80089B80` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_22.c:2937 | `soundMacroOpLoopRandomCount` | `0x80089BA0` | `0x00002010` | `mfhi $a0` | `mfhi        $a0` | yes | unreachable | **correct** |
| funcs_22.c:3505 | `soundMacroOpSetPitchBendGlide` | `0x80089E80` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:3750 | `computeChannelPitchSweepStep` | `0x80089F9C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:3760 | `computeChannelPitchSweepStep` | `0x80089FB0` | `0x00002810` | `mfhi $a1` | `mfhi        $a1` | yes | unreachable | **correct** |
| funcs_22.c:3791 | `computeChannelPitchSweepStep` | `0x80089FE0` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_22.c:3801 | `computeChannelPitchSweepStep` | `0x80089FF4` | `0x00002810` | `mfhi $a1` | `mfhi        $a1` | yes | unreachable | **correct** |
| funcs_22.c:3912 | `soundMacroOpStartNoteAbsoluteSweep` | `0x8008A088` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:3922 | `soundMacroOpStartNoteAbsoluteSweep` | `0x8008A09C` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_22.c:3953 | `soundMacroOpStartNoteAbsoluteSweep` | `0x8008A0CC` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_22.c:3963 | `soundMacroOpStartNoteAbsoluteSweep` | `0x8008A0E0` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_22.c:4132 | `soundMacroOpStartNoteRelativeSweep` | `0x8008A1C8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:4142 | `soundMacroOpStartNoteRelativeSweep` | `0x8008A1DC` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_22.c:4173 | `soundMacroOpStartNoteRelativeSweep` | `0x8008A20C` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_22.c:4183 | `soundMacroOpStartNoteRelativeSweep` | `0x8008A220` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_22.c:4330 | `soundMacroOpStartNoteTransposedSweep` | `0x8008A2E8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:4340 | `soundMacroOpStartNoteTransposedSweep` | `0x8008A2FC` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_22.c:4371 | `soundMacroOpStartNoteTransposedSweep` | `0x8008A32C` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_22.c:4381 | `soundMacroOpStartNoteTransposedSweep` | `0x8008A340` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_22.c:4522 | `soundMacroOpPlaySampleKeymap` | `0x8008A400` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:4706 | `soundMacroOpPlaySampleKeymap` | `0x8008A4F4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:4714 | `soundMacroOpPlaySampleKeymap` | `0x8008A504` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_22.c:4898 | `soundMacroOpPlaySampleKeymap` | `0x8008A5F8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:4908 | `soundMacroOpPlaySampleKeymap` | `0x8008A60C` | `0x00003810` | `mfhi $a3` | `mfhi        $a3` | yes | unreachable | **correct** |
| funcs_22.c:4937 | `soundMacroOpPlaySampleKeymap` | `0x8008A638` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_22.c:4947 | `soundMacroOpPlaySampleKeymap` | `0x8008A64C` | `0x00003810` | `mfhi $a3` | `mfhi        $a3` | yes | unreachable | **correct** |
| funcs_22.c:5201 | `soundMacroOpSetPanSweep` | `0x8008A7A4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:5507 | `musyxSetVoiceAdsrFromTable` | `0x8008A930` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:5839 | `soundMacroOpSetVolumeRamp` | `0x8008AAF4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:5883 | `soundMacroOpSetPitchRelativeToNote` | `0x8008AB2C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:6037 | `evaluateSoundMacroCurveTable` | `0x8008ABEC` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:6135 | `evaluateSoundMacroCurveTable` | `0x8008AC64` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_22.c:6255 | `soundMacroSetVoiceVolume` | `0x8008AD08` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:6347 | `soundMacroSetVoiceVolume` | `0x8008AD80` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:6445 | `soundMacroSetVoiceVolume` | `0x8008ADF8` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_22.c:6632 | `soundMacroSetupVolumeRamp` | `0x8008AEF8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:6662 | `soundMacroSetupVolumeRamp` | `0x8008AF20` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_22.c:6730 | `soundMacroSetupVolumeRamp` | `0x8008AF84` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:6832 | `soundMacroSetupVolumeRamp` | `0x8008B004` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_22.c:6890 | `soundMacroSetupVolumeRamp` | `0x8008B054` | `0x00002812` | `mflo $a1` | `mflo        $a1` | yes | unreachable | **correct** |
| funcs_22.c:7079 | `soundMacroPlayRandomKeyNote` | `0x8008B164` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_22.c:7097 | `soundMacroPlayRandomKeyNote` | `0x8008B184` | `0x00005810` | `mfhi $t3` | `mfhi        $t3` | yes | unreachable | **correct** |
| funcs_22.c:7135 | `soundMacroPlayRandomKeyNote` | `0x8008B1C8` | `0x00002812` | `mflo $a1` | `mflo        $a1` | yes | unreachable | **correct** |
| funcs_22.c:7183 | `soundMacroPlayRandomKeyNote` | `0x8008B20C` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_23.c:472 | `soundMacroPushEffectEvent` | `0x8008B324` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_23.c:655 | `seqCmdHandler40` | `0x8008B414` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_23.c:838 | `seqCmdHandler41` | `0x8008B504` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_23.c:1021 | `seqCmdHandler42` | `0x8008B5F4` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_23.c:1204 | `seqCmdHandler43` | `0x8008B6E4` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_23.c:1387 | `seqCmdHandler44` | `0x8008B7D4` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_23.c:1570 | `seqCmdHandler45` | `0x8008B8C4` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_23.c:1753 | `seqCmdHandler46` | `0x8008B9B4` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_23.c:2003 | `soundMacroSetPitchTarget` | `0x8008BAF0` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:3266 | `tickAudioChannel` | `0x8008C098` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_23.c:3289 | `tickAudioChannel` | `0x8008C0BC` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_23.c:3797 | `tickAudioChannel` | `0x8008C358` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:3958 | `tickAudioChannel` | `0x8008C420` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:4075 | `tickAudioChannel` | `0x8008C4AC` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:4740 | `tickAudioChannel` | `0x8008C7E8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:5354 | `tickAllAudioChannels` | `0x8008CA74` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_23.c:5373 | `tickAllAudioChannels` | `0x8008CA90` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_23.c:5515 | `tickAllAudioChannels` | `0x8008CB64` | `0x00001010` | `mfhi $v0` | `mfhi        $v0` | yes | unreachable | **correct** |
| funcs_23.c:5534 | `tickAllAudioChannels` | `0x8008CB80` | `0x00002812` | `mflo $a1` | `mflo        $a1` | yes | unreachable | **correct** |
| funcs_23.c:6245 | `tickAllAudioChannels` | `0x8008CF50` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:6290 | `tickAllAudioChannels` | `0x8008CF9C` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_23.c:6454 | `tickAllAudioChannels` | `0x8008D094` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_23.c:6462 | `tickAllAudioChannels` | `0x8008D0A4` | `0x00002812` | `mflo $a1` | `mflo        $a1` | yes | unreachable | **correct** |
| funcs_23.c:6472 | `tickAllAudioChannels` | `0x8008D0B8` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_23.c:6588 | `tickAllAudioChannels` | `0x8008D160` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_23.c:6614 | `tickAllAudioChannels` | `0x8008D18C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:6633 | `tickAllAudioChannels` | `0x8008D1AC` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_23.c:6659 | `tickAllAudioChannels` | `0x8008D1D8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:6772 | `tickAllAudioChannels` | `0x8008D278` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:6782 | `tickAllAudioChannels` | `0x8008D28C` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_23.c:6852 | `tickAllAudioChannels` | `0x8008D2F8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:6862 | `tickAllAudioChannels` | `0x8008D30C` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_23.c:6882 | `tickAllAudioChannels` | `0x8008D330` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:6940 | `tickAllAudioChannels` | `0x8008D384` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:6975 | `tickAllAudioChannels` | `0x8008D3B4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:7033 | `tickAllAudioChannels` | `0x8008D410` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_23.c:7089 | `tickAllAudioChannels` | `0x8008D468` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_23.c:7240 | `tickAllAudioChannels` | `0x8008D560` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_23.c:7252 | `tickAllAudioChannels` | `0x8008D578` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_23.c:7301 | `tickAllAudioChannels` | `0x8008D5D0` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_23.c:7320 | `tickAllAudioChannels` | `0x8008D5EC` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_23.c:7350 | `tickAllAudioChannels` | `0x8008D614` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_23.c:7490 | `tickAllAudioChannels` | `0x8008D6CC` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:7597 | `tickAllAudioChannels` | `0x8008D760` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_23.c:7821 | `tickAllAudioChannels` | `0x8008D898` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_23.c:8054 | `tickAudioSequencerFrame` | `0x8008D9D8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:8955 | `dispatchAudioCommand` | `0x8008DE34` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:9090 | `dispatchAudioCommand` | `0x8008DEF8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:9248 | `dispatchAudioCommand` | `0x8008DFD4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:9356 | `dispatchAudioCommand` | `0x8008E070` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:9833 | `setupAudioFaderRamp` | `0x8008E2D4` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_23.c:9949 | `setupAudioFaderRamp` | `0x8008E378` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:10070 | `setupAudioFaderRamp` | `0x8008E424` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:10170 | `setupAudioFaderRamp` | `0x8008E4B8` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_23.c:12360 | `buildSongTempoSchedule` | `0x8008EEF8` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_23.c:12368 | `buildSongTempoSchedule` | `0x8008EF08` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_23.c:12382 | `buildSongTempoSchedule` | `0x8008EF24` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_23.c:12481 | `buildSongTempoSchedule` | `0x8008EFB4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:12489 | `buildSongTempoSchedule` | `0x8008EFC4` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_23.c:13073 | `allocateSongChannelArray` | `0x8008F258` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_23.c:13342 | `setupSongRenderBuffers` | `0x8008F39C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_23.c:13350 | `setupSongRenderBuffers` | `0x8008F3AC` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_23.c:13554 | `setupSongRenderBuffers` | `0x8008F4B4` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_23.c:13612 | `advanceVolumeFadeEnvelope` | `0x8008F508` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_24.c:1290 | `fillSampleStreamRange` | `0x8008FCC0` | `0x0000C810` | `mfhi $t9` | `mfhi        $t9` | yes | unreachable | **correct** |
| funcs_24.c:2332 | `musyxRenderVoiceSamples` | `0x8008FFEC` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_24.c:4011 | `musyxRenderVoiceSamples` | `0x80090790` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_24.c:4977 | `musyxKeyOnVoice` | `0x80090B1C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_24.c:5239 | `musyxKeyOnVoice` | `0x80090C14` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_24.c:5499 | `musyxKeyOnVoice` | `0x80090D08` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_24.c:5557 | `musyxKeyOnVoice` | `0x80090D4C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_24.c:5615 | `musyxKeyOnVoice` | `0x80090D90` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_24.c:5673 | `musyxKeyOnVoice` | `0x80090DD4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_24.c:6699 | `musyxBuildVoiceCommandList` | `0x8009118C` | `0x00003810` | `mfhi $a3` | `mfhi        $a3` | yes | unreachable | **correct** |
| funcs_24.c:8423 | `initN64RspMixer` | `0x80091960` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_24.c:8431 | `initN64RspMixer` | `0x80091970` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_24.c:8450 | `initN64RspMixer` | `0x80091990` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_24.c:11712 | `resampleVoicePointTableSamples` | `0x800926F4` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:11910 | `interpolatePointTableSamplesToPackedWord` | `0x800927EC` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:11960 | `interpolatePointTableSamplesToPackedWord` | `0x80092834` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:12010 | `interpolatePointTableSamplesToPackedWord` | `0x8009287C` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:12062 | `interpolatePointTableSamplesToPackedWord` | `0x800928C8` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:12210 | `resampleVoiceLutSamples` | `0x80092998` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:12414 | `interpolateLutSamplesToPackedWord` | `0x80092A9C` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:12470 | `interpolateLutSamplesToPackedWord` | `0x80092AF0` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:12526 | `interpolateLutSamplesToPackedWord` | `0x80092B44` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:12584 | `interpolateLutSamplesToPackedWord` | `0x80092B9C` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:12872 | `interpolateConstantSamplesToPackedWord` | `0x80092D24` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:12928 | `interpolateConstantSamplesToPackedWord` | `0x80092D78` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:12984 | `interpolateConstantSamplesToPackedWord` | `0x80092DCC` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:13040 | `interpolateConstantSamplesToPackedWord` | `0x80092E20` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:13364 | `packFourLutResampledSamples` | `0x80092FE0` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:13432 | `packFourLutResampledSamples` | `0x8009304C` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:13500 | `packFourLutResampledSamples` | `0x800930B8` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_24.c:13568 | `packFourLutResampledSamples` | `0x80093124` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_25.c:303 | `musyxComputeNotePlaybackRate` | `0x80093EEC` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_25.c:305 | `musyxComputeNotePlaybackRate` | `0x80093EF0` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_25.c:347 | `divideByMixerBaseFrequency` | `0x80093F30` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_25.c:365 | `scaleFixedPointByRatioA` | `0x80093F48` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_25.c:367 | `scaleFixedPointByRatioA` | `0x80093F4C` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_25.c:389 | `scaleFixedPointByRatioB` | `0x80093F6C` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_25.c:391 | `scaleFixedPointByRatioB` | `0x80093F70` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_25.c:419 | `scaleByPitchTableA` | `0x80093F9C` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_25.c:421 | `scaleByPitchTableA` | `0x80093FA0` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_25.c:449 | `scaleByPitchTableB` | `0x80093FCC` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_25.c:451 | `scaleByPitchTableB` | `0x80093FD0` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_25.c:471 | `computeNoteRatePairFromTableA` | `0x80093FEC` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_25.c:473 | `computeNoteRatePairFromTableA` | `0x80093FF0` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_25.c:489 | `computeNoteRatePairFromTableA` | `0x80094010` | `0x00005012` | `mflo $t2` | `mflo        $t2` | yes | unreachable | **correct** |
| funcs_25.c:491 | `computeNoteRatePairFromTableA` | `0x80094014` | `0x00005810` | `mfhi $t3` | `mfhi        $t3` | yes | unreachable | **correct** |
| funcs_25.c:511 | `computeNoteRatePairFromTableA` | `0x80094038` | `0x00005012` | `mflo $t2` | `mflo        $t2` | yes | unreachable | **correct** |
| funcs_25.c:513 | `computeNoteRatePairFromTableA` | `0x8009403C` | `0x00005810` | `mfhi $t3` | `mfhi        $t3` | yes | unreachable | **correct** |
| funcs_25.c:541 | `computeNoteRatePairFromTableB` | `0x80094064` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_25.c:543 | `computeNoteRatePairFromTableB` | `0x80094068` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_25.c:559 | `computeNoteRatePairFromTableB` | `0x80094088` | `0x00005012` | `mflo $t2` | `mflo        $t2` | yes | unreachable | **correct** |
| funcs_25.c:561 | `computeNoteRatePairFromTableB` | `0x8009408C` | `0x00005810` | `mfhi $t3` | `mfhi        $t3` | yes | unreachable | **correct** |
| funcs_25.c:581 | `computeNoteRatePairFromTableB` | `0x800940B0` | `0x00005012` | `mflo $t2` | `mflo        $t2` | yes | unreachable | **correct** |
| funcs_25.c:583 | `computeNoteRatePairFromTableB` | `0x800940B4` | `0x00005810` | `mfhi $t3` | `mfhi        $t3` | yes | unreachable | **correct** |
| funcs_25.c:5460 | `updateSongTempoTickRate` | `0x80095684` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_25.c:5499 | `updateSongTempoTickRate` | `0x800956AC` | `0x00003810` | `mfhi $a3` | `mfhi        $a3` | yes | unreachable | **correct** |
| funcs_25.c:5507 | `updateSongTempoTickRate` | `0x800956BC` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_25.c:5515 | `updateSongTempoTickRate` | `0x800956CC` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_25.c:10454 | `tickAllActiveSongs` | `0x80096E5C` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_25.c:10474 | `tickAllActiveSongs` | `0x80096E84` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_25.c:10482 | `tickAllActiveSongs` | `0x80096E94` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_25.c:10490 | `tickAllActiveSongs` | `0x80096EA4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_26.c:12208 | `allocAndConfigureNewVoice` | `0x8009B160` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_26.c:12248 | `allocAndConfigureNewVoice` | `0x8009B198` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_27.c:919 | `serviceStreamingVoice` | `0x8009C0D4` | `0x00002810` | `mfhi $a1` | `mfhi        $a1` | yes | unreachable | **correct** |
| funcs_27.c:1061 | `serviceStreamingVoice` | `0x8009C19C` | `0x00002010` | `mfhi $a0` | `mfhi        $a0` | yes | unreachable | **correct** |
| funcs_27.c:4951 | `filterVoiceSampleBlock` | `0x8009D850` | `0x00006812` | `mflo $t5` | `mflo        $t5` | yes | unreachable | **correct** |
| funcs_27.c:5128 | `applyVoiceDelayFilter` | `0x8009D948` | `0x00004812` | `mflo $t1` | `mflo        $t1` | yes | unreachable | **correct** |
| funcs_27.c:5188 | `runVoiceLatticeFilter` | `0x8009D994` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5200 | `runVoiceLatticeFilter` | `0x8009D9AC` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5210 | `runVoiceLatticeFilter` | `0x8009D9C0` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5224 | `runVoiceLatticeFilter` | `0x8009D9DC` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5234 | `runVoiceLatticeFilter` | `0x8009D9F0` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5246 | `runVoiceLatticeFilter` | `0x8009DA08` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5256 | `runVoiceLatticeFilter` | `0x8009DA1C` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5270 | `runVoiceLatticeFilter` | `0x8009DA38` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5280 | `runVoiceLatticeFilter` | `0x8009DA4C` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5292 | `runVoiceLatticeFilter` | `0x8009DA64` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5302 | `runVoiceLatticeFilter` | `0x8009DA78` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5316 | `runVoiceLatticeFilter` | `0x8009DA94` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5326 | `runVoiceLatticeFilter` | `0x8009DAA8` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5338 | `runVoiceLatticeFilter` | `0x8009DAC0` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5348 | `runVoiceLatticeFilter` | `0x8009DAD4` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:5362 | `runVoiceLatticeFilter` | `0x8009DAF0` | `0x00000812` | `mflo $at` | `mflo        $at` | yes | unreachable | **correct** |
| funcs_27.c:6291 | `audioCompandS16` | `0x8009DEE8` | `0x00000050` | `mfhi $zero` | `.word       0x00000050                   # mfhi        $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:11302 | `audioCompandS16` | `0x8009FD24` | `0x00000010` | `mfhi $zero` | `mfhi        $zero` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:11306 | `audioCompandS16` | `0x8009FD2C` | `0x00000011` | `mthi $zero` | `mthi        $zero` | yes | unreachable | **correct** |
| funcs_27.c:11310 | `audioCompandS16` | `0x8009FD34` | `0x00000012` | `mflo $zero` | `mflo        $zero` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:11314 | `audioCompandS16` | `0x8009FD3C` | `0x00000013` | `mtlo $zero` | `mtlo        $zero` | yes | unreachable | **correct** |
| funcs_27.c:11566 | `audioCompandS16` | `0x8009FF24` | `0x00000050` | `mfhi $zero` | `.word       0x00000050                   # mfhi        $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:11570 | `audioCompandS16` | `0x8009FF2C` | `0x00000051` | `mthi $zero` | `.word       0x00000051                   # mthi        $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:11574 | `audioCompandS16` | `0x8009FF34` | `0x00000052` | `mflo $zero` | `.word       0x00000052                   # mflo        $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:11578 | `audioCompandS16` | `0x8009FF3C` | `0x00000053` | `mtlo $zero` | `.word       0x00000053                   # mtlo        $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:11677 | `audioCompandS16` | `0x800A0000` | `0x00000010` | `mfhi $zero` | `mfhi        $zero` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:11679 | `audioCompandS16` | `0x800A0004` | `0x00110012` | `mflo $zero` | `.word       0x00110012                   # mflo        $zero # 00110000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:11765 | `audioCompandS16` | `0x800A00A8` | `0x00500051` | `mthi $v0` | `.word       0x00500051                   # mthi        $v0 # 00100040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:11767 | `audioCompandS16` | `0x800A00AC` | `0x00000052` | `mflo $zero` | `.word       0x00000052                   # mflo        $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:11769 | `audioCompandS16` | `0x800A00B0` | `0x00000053` | `mtlo $zero` | `.word       0x00000053                   # mtlo        $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:11873 | `audioCompandS16` | `0x800A0180` | `0x00000091` | `mthi $zero` | `.word       0x00000091                   # mthi        $zero # 00000080 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:11875 | `audioCompandS16` | `0x800A0184` | `0x00920093` | `mtlo $a0` | `.word       0x00920093                   # mtlo        $a0 # 00120080 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:11953 | `audioCompandS16` | `0x800A0218` | `0x000000D0` | `mfhi $zero` | `.word       0x000000D0                   # mfhi        $zero # 000000C0 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:11955 | `audioCompandS16` | `0x800A021C` | `0x00D100D2` | `mflo $zero` | `.word       0x00D100D2                   # mflo        $zero # 00D100C0 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:12031 | `audioCompandS16` | `0x800A02AC` | `0x00000110` | `mfhi $zero` | `.word       0x00000110                   # mfhi        $zero # 00000100 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:12033 | `audioCompandS16` | `0x800A02B0` | `0x00000111` | `mthi $zero` | `.word       0x00000111                   # mthi        $zero # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12035 | `audioCompandS16` | `0x800A02B4` | `0x01120113` | `mtlo $t0` | `.word       0x01120113                   # mtlo        $t0 # 00120100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12145 | `audioCompandS16` | `0x800A0390` | `0x01500151` | `mthi $t2` | `.word       0x01500151                   # mthi        $t2 # 00100140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12243 | `audioCompandS16` | `0x800A0454` | `0x01900191` | `mthi $t4` | `.word       0x01900191                   # mthi        $t4 # 00100180 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12245 | `audioCompandS16` | `0x800A0458` | `0x01920193` | `mtlo $t4` | `.word       0x01920193                   # mtlo        $t4 # 00120180 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12323 | `audioCompandS16` | `0x800A04EC` | `0x01CF01D0` | `mfhi $zero` | `.word       0x01CF01D0                   # mfhi        $zero # 01CF01C0 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:12325 | `audioCompandS16` | `0x800A04F0` | `0x01D101D2` | `mflo $zero` | `.word       0x01D101D2                   # mflo        $zero # 01D101C0 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:12411 | `audioCompandS16` | `0x800A059C` | `0x02100211` | `mthi $s0` | `.word       0x02100211                   # mthi        $s0 # 00100200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12413 | `audioCompandS16` | `0x800A05A0` | `0x02120213` | `mtlo $s0` | `.word       0x02120213                   # mtlo        $s0 # 00120200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12837 | `audioCompandS16` | `0x800A08A4` | `0x01D60190` | `mfhi $zero` | `.word       0x01D60190                   # mfhi        $zero # 01D60180 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:13360 | `audioCompandS16` | `0x800A0C38` | `0x00000010` | `mfhi $zero` | `mfhi        $zero` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:13829 | `audioCompandS16` | `0x800A0F5C` | `0x000C0012` | `mflo $zero` | `.word       0x000C0012                   # mflo        $zero # 000C0000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:13839 | `audioCompandS16` | `0x800A0F70` | `0x004B0051` | `mthi $v0` | `.word       0x004B0051                   # mthi        $v0 # 000B0040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:13849 | `audioCompandS16` | `0x800A0F84` | `0x008A0090` | `mfhi $zero` | `.word       0x008A0090                   # mfhi        $zero # 008A0080 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:13925 | `audioCompandS16` | `0x800A1014` | `0x024C0252` | `mflo $zero` | `.word       0x024C0252                   # mflo        $zero # 024C0240 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:13935 | `audioCompandS16` | `0x800A1028` | `0x028A0290` | `mfhi $zero` | `.word       0x028A0290                   # mfhi        $zero # 028A0280 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:13978 | `audioCompandS16` | `0x800A107C` | `0x038D0393` | `mtlo $gp` | `.word       0x038D0393                   # mtlo        $gp # 000D0380 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:13988 | `audioCompandS16` | `0x800A1090` | `0x03CA03D0` | `mfhi $zero` | `.word       0x03CA03D0                   # mfhi        $zero # 03CA03C0 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:98928 | `audioCompandS16` | `0x800A1794` | `0x000B0011` | `mthi $zero` | `.word       0x000B0011                   # mthi        $zero # 000B0000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:98979 | `audioCompandS16` | `0x800A17F4` | `0x03E00412` | `mflo $zero` | `.word       0x03E00412                   # mflo        $zero # 03E00400 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:99874 | `audioCompandS16` | `0x800A1BAC` | `0x00001E10` | `mfhi $v1` | `.word       0x00001E10                   # mfhi        $v1 # 00000600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:99944 | `audioCompandS16` | `0x800A1BEC` | `0x00001F11` | `mthi $zero` | `.word       0x00001F11                   # mthi        $zero # 00001F00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:99983 | `audioCompandS16` | `0x800A1C28` | `0x00001E10` | `mfhi $v1` | `.word       0x00001E10                   # mfhi        $v1 # 00000600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:99985 | `audioCompandS16` | `0x800A1C2C` | `0x00002212` | `mflo $a0` | `.word       0x00002212                   # mflo        $a0 # 00000200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100023 | `audioCompandS16` | `0x800A1C68` | `0x00002111` | `mthi $zero` | `.word       0x00002111                   # mthi        $zero # 00002100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100025 | `audioCompandS16` | `0x800A1C6C` | `0x00002613` | `mtlo $zero` | `.word       0x00002613                   # mtlo        $zero # 00002600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100061 | `audioCompandS16` | `0x800A1CA4` | `0x00001E10` | `mfhi $v1` | `.word       0x00001E10                   # mfhi        $v1 # 00000600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100063 | `audioCompandS16` | `0x800A1CA8` | `0x00002412` | `mflo $a0` | `.word       0x00002412                   # mflo        $a0 # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100105 | `audioCompandS16` | `0x800A1CE4` | `0x00002211` | `mthi $zero` | `.word       0x00002211                   # mthi        $zero # 00002200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100107 | `audioCompandS16` | `0x800A1CE8` | `0x00002813` | `mtlo $zero` | `.word       0x00002813                   # mtlo        $zero # 00002800 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100143 | `audioCompandS16` | `0x800A1D20` | `0x00001F10` | `mfhi $v1` | `.word       0x00001F10                   # mfhi        $v1 # 00000700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100145 | `audioCompandS16` | `0x800A1D24` | `0x00002612` | `mflo $a0` | `.word       0x00002612                   # mflo        $a0 # 00000600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100183 | `audioCompandS16` | `0x800A1D60` | `0x00002211` | `mthi $zero` | `.word       0x00002211                   # mthi        $zero # 00002200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100185 | `audioCompandS16` | `0x800A1D64` | `0x00002913` | `mtlo $zero` | `.word       0x00002913                   # mtlo        $zero # 00002900 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100223 | `audioCompandS16` | `0x800A1DA0` | `0x00002612` | `mflo $a0` | `.word       0x00002612                   # mflo        $a0 # 00000600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100255 | `audioCompandS16` | `0x800A1DD0` | `0x00000410` | `mfhi $zero` | `.word       0x00000410                   # mfhi        $zero # 00000400 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:100257 | `audioCompandS16` | `0x800A1DD4` | `0x00000D10` | `mfhi $at` | `.word       0x00000D10                   # mfhi        $at # 00000500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100259 | `audioCompandS16` | `0x800A1DD8` | `0x00001610` | `mfhi $v0` | `.word       0x00001610                   # mfhi        $v0 # 00000600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100261 | `audioCompandS16` | `0x800A1DDC` | `0x00001F10` | `mfhi $v1` | `.word       0x00001F10                   # mfhi        $v1 # 00000700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100263 | `audioCompandS16` | `0x800A1DE0` | `0x00002913` | `mtlo $zero` | `.word       0x00002913                   # mtlo        $zero # 00002900 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100295 | `audioCompandS16` | `0x800A1E10` | `0x00000511` | `mthi $zero` | `.word       0x00000511                   # mthi        $zero # 00000500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100297 | `audioCompandS16` | `0x800A1E14` | `0x00000F11` | `mthi $zero` | `.word       0x00000F11                   # mthi        $zero # 00000F00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100299 | `audioCompandS16` | `0x800A1E18` | `0x00001911` | `mthi $zero` | `.word       0x00001911                   # mthi        $zero # 00001900 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100301 | `audioCompandS16` | `0x800A1E1C` | `0x00002311` | `mthi $zero` | `.word       0x00002311                   # mthi        $zero # 00002300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100335 | `audioCompandS16` | `0x800A1E50` | `0x00000512` | `mflo $zero` | `.word       0x00000512                   # mflo        $zero # 00000500 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:100337 | `audioCompandS16` | `0x800A1E54` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_27.c:100339 | `audioCompandS16` | `0x800A1E58` | `0x00001B12` | `mflo $v1` | `.word       0x00001B12                   # mflo        $v1 # 00000300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100341 | `audioCompandS16` | `0x800A1E5C` | `0x00002612` | `mflo $a0` | `.word       0x00002612                   # mflo        $a0 # 00000600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100375 | `audioCompandS16` | `0x800A1E90` | `0x00000613` | `mtlo $zero` | `.word       0x00000613                   # mtlo        $zero # 00000600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100377 | `audioCompandS16` | `0x800A1E94` | `0x00001213` | `mtlo $zero` | `.word       0x00001213                   # mtlo        $zero # 00001200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100379 | `audioCompandS16` | `0x800A1E98` | `0x00001F13` | `mtlo $zero` | `.word       0x00001F13                   # mtlo        $zero # 00001F00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100381 | `audioCompandS16` | `0x800A1E9C` | `0x00002B13` | `mtlo $zero` | `.word       0x00002B13                   # mtlo        $zero # 00002B00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102506 | `audioCompandS16` | `0x800A2BAC` | `0x00343C50` | `mfhi $a3` | `.word       0x00343C50                   # mfhi        $a3 # 00340440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102578 | `audioCompandS16` | `0x800A2BEC` | `0x00397451` | `mthi $at` | `.word       0x00397451                   # mthi        $at # 00197440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102617 | `audioCompandS16` | `0x800A2C28` | `0x0036C750` | `mfhi $t8` | `.word       0x0036C750                   # mfhi        $t8 # 00360740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102619 | `audioCompandS16` | `0x800A2C2C` | `0x003F3452` | `mflo $a2` | `.word       0x003F3452                   # mflo        $a2 # 003F0440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102659 | `audioCompandS16` | `0x800A2C68` | `0x003C4151` | `mthi $at` | `.word       0x003C4151                   # mthi        $at # 001C4140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102661 | `audioCompandS16` | `0x800A2C6C` | `0x00458653` | `mtlo $v0` | `.word       0x00458653                   # mtlo        $v0 # 00058640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102697 | `audioCompandS16` | `0x800A2CA4` | `0x00381550` | `mfhi $v0` | `.word       0x00381550                   # mfhi        $v0 # 00380540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102699 | `audioCompandS16` | `0x800A2CA8` | `0x00424852` | `mflo $t1` | `.word       0x00424852                   # mflo        $t1 # 00420040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102742 | `audioCompandS16` | `0x800A2CE4` | `0x003DB151` | `mthi $at` | `.word       0x003DB151                   # mthi        $at # 001DB140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102744 | `audioCompandS16` | `0x800A2CE8` | `0x0048E953` | `mtlo $v0` | `.word       0x0048E953                   # mtlo        $v0 # 0008E940 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102780 | `audioCompandS16` | `0x800A2D20` | `0x00378650` | `mfhi $s0` | `.word       0x00378650                   # mfhi        $s0 # 00370640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102782 | `audioCompandS16` | `0x800A2D24` | `0x0043DC52` | `mflo $k1` | `.word       0x0043DC52                   # mflo        $k1 # 00430440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102821 | `audioCompandS16` | `0x800A2D60` | `0x003D1451` | `mthi $at` | `.word       0x003D1451                   # mthi        $at # 001D1440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102823 | `audioCompandS16` | `0x800A2D64` | `0x004AA653` | `mtlo $v0` | `.word       0x004AA653                   # mtlo        $v0 # 000AA640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102861 | `audioCompandS16` | `0x800A2DA0` | `0x00433052` | `mflo $a2` | `.word       0x00433052                   # mflo        $a2 # 00430040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102893 | `audioCompandS16` | `0x800A2DD0` | `0x00083650` | `mfhi $a2` | `.word       0x00083650                   # mfhi        $a2 # 00080640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102895 | `audioCompandS16` | `0x800A2DD4` | `0x0018A250` | `mfhi $s4` | `.word       0x0018A250                   # mfhi        $s4 # 00180240 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102897 | `audioCompandS16` | `0x800A2DD8` | `0x00290F50` | `mfhi $at` | `.word       0x00290F50                   # mfhi        $at # 00290740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102899 | `audioCompandS16` | `0x800A2DDC` | `0x00397B50` | `mfhi $t7` | `.word       0x00397B50                   # mfhi        $t7 # 00390340 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102901 | `audioCompandS16` | `0x800A2DE0` | `0x0049E853` | `mtlo $v0` | `.word       0x0049E853                   # mtlo        $v0 # 0009E840 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102936 | `audioCompandS16` | `0x800A2E10` | `0x00090851` | `mthi $zero` | `.word       0x00090851                   # mthi        $zero # 00090840 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102938 | `audioCompandS16` | `0x800A2E14` | `0x001B1951` | `mthi $zero` | `.word       0x001B1951                   # mthi        $zero # 001B1940 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102940 | `audioCompandS16` | `0x800A2E18` | `0x002D2A51` | `mthi $at` | `.word       0x002D2A51                   # mthi        $at # 000D2A40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102942 | `audioCompandS16` | `0x800A2E1C` | `0x003F3B51` | `mthi $at` | `.word       0x003F3B51                   # mthi        $at # 001F3B40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102976 | `audioCompandS16` | `0x800A2E50` | `0x0009EF52` | `mflo $sp` | `.word       0x0009EF52                   # mflo        $sp # 00090740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102978 | `audioCompandS16` | `0x800A2E54` | `0x001DCE52` | `mflo $t9` | `.word       0x001DCE52                   # mflo        $t9 # 001D0640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102980 | `audioCompandS16` | `0x800A2E58` | `0x0031AE52` | `mflo $s5` | `.word       0x0031AE52                   # mflo        $s5 # 00310640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102982 | `audioCompandS16` | `0x800A2E5C` | `0x00458D52` | `mflo $s1` | `.word       0x00458D52                   # mflo        $s1 # 00450540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103016 | `audioCompandS16` | `0x800A2E90` | `0x000AEE53` | `mtlo $zero` | `.word       0x000AEE53                   # mtlo        $zero # 000AEE40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103018 | `audioCompandS16` | `0x800A2E94` | `0x0020CA53` | `mtlo $at` | `.word       0x0020CA53                   # mtlo        $at # 0000CA40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103021 | `audioCompandS16` | `0x800A2E98` | `0x0036A653` | `mtlo $at` | `.word       0x0036A653                   # mtlo        $at # 0016A640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103023 | `audioCompandS16` | `0x800A2E9C` | `0x004C8253` | `mtlo $v0` | `.word       0x004C8253                   # mtlo        $v0 # 000C8240 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103221 | `audioCompandS16` | `0x800A2FD4` | `0x0010F390` | `mfhi $fp` | `.word       0x0010F390                   # mfhi        $fp # 00100380 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103234 | `audioCompandS16` | `0x800A2FEC` | `0x0017F911` | `mthi $zero` | `.word       0x0017F911                   # mthi        $zero # 0017F900 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103347 | `audioCompandS16` | `0x800A30C0` | `0x02000010` | `mfhi $zero` | `.word       0x02000010                   # mfhi        $zero # 02000000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:103365 | `audioCompandS16` | `0x800A30E4` | `0x035D1410` | `mfhi $v0` | `.word       0x035D1410                   # mfhi        $v0 # 035D0400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104081 | `audioCompandS16` | `0x800A31DC` | `0x000D7450` | `mfhi $t6` | `.word       0x000D7450                   # mfhi        $t6 # 000D0440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104094 | `audioCompandS16` | `0x800A31F0` | `0x000A1451` | `mthi $zero` | `.word       0x000A1451                   # mthi        $zero # 000A1440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104169 | `audioCompandS16` | `0x800A3274` | `0x00017F91` | `mthi $zero` | `.word       0x00017F91                   # mthi        $zero # 00017F80 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104187 | `audioCompandS16` | `0x800A3298` | `0x0000E412` | `mflo $gp` | `.word       0x0000E412                   # mflo        $gp # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104209 | `audioCompandS16` | `0x800A32C4` | `0x000078D1` | `mthi $zero` | `.word       0x000078D1                   # mthi        $zero # 000078C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104237 | `audioCompandS16` | `0x800A32FC` | `0x000035D1` | `mthi $zero` | `.word       0x000035D1                   # mthi        $zero # 000035C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104248 | `audioCompandS16` | `0x800A3310` | `0x00002851` | `mthi $zero` | `.word       0x00002851                   # mthi        $zero # 00002840 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104293 | `audioCompandS16` | `0x800A3368` | `0x00000B50` | `mfhi $at` | `.word       0x00000B50                   # mfhi        $at # 00000340 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104333 | `audioCompandS16` | `0x800A33B8` | `0x00000390` | `mfhi $zero` | `.word       0x00000390                   # mfhi        $zero # 00000380 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:104353 | `audioCompandS16` | `0x800A33E0` | `0x00100ED0` | `mfhi $at` | `.word       0x00100ED0                   # mfhi        $at # 001006C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104425 | `audioCompandS16` | `0x800A3470` | `0x00109692` | `mflo $s2` | `.word       0x00109692                   # mflo        $s2 # 00100680 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104445 | `audioCompandS16` | `0x800A3498` | `0x0010BD12` | `mflo $s7` | `.word       0x0010BD12                   # mflo        $s7 # 00100500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104449 | `audioCompandS16` | `0x800A34A0` | `0x0010C4D0` | `mfhi $t8` | `.word       0x0010C4D0                   # mfhi        $t8 # 001004C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104453 | `audioCompandS16` | `0x800A34A8` | `0x0010CC92` | `mflo $t9` | `.word       0x0010CC92                   # mflo        $t9 # 00100480 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104467 | `audioCompandS16` | `0x800A34C4` | `0x0010E7D3` | `mtlo $zero` | `.word       0x0010E7D3                   # mtlo        $zero # 0010E7C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104479 | `audioCompandS16` | `0x800A34DC` | `0x0010FF53` | `mtlo $zero` | `.word       0x0010FF53                   # mtlo        $zero # 0010FF40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104487 | `audioCompandS16` | `0x800A34EC` | `0x00110F10` | `mfhi $at` | `.word       0x00110F10                   # mfhi        $at # 00110700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104497 | `audioCompandS16` | `0x800A3500` | `0x001122D0` | `mfhi $a0` | `.word       0x001122D0                   # mfhi        $a0 # 001102C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104600 | `audioCompandS16` | `0x800A35C8` | `0x0011ED50` | `mfhi $sp` | `.word       0x0011ED50                   # mfhi        $sp # 00110540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104610 | `audioCompandS16` | `0x800A35DC` | `0x00120211` | `mthi $zero` | `.word       0x00120211                   # mthi        $zero # 00120200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104616 | `audioCompandS16` | `0x800A35E8` | `0x00120E91` | `mthi $zero` | `.word       0x00120E91                   # mthi        $zero # 00120E80 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104632 | `audioCompandS16` | `0x800A3608` | `0x00123010` | `mfhi $a2` | `.word       0x00123010                   # mfhi        $a2 # 00120000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104646 | `audioCompandS16` | `0x800A3624` | `0x00124D93` | `mtlo $zero` | `.word       0x00124D93                   # mtlo        $zero # 00124D80 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104668 | `audioCompandS16` | `0x800A3650` | `0x00127C53` | `mtlo $zero` | `.word       0x00127C53                   # mtlo        $zero # 00127C40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104682 | `audioCompandS16` | `0x800A366C` | `0x00129A51` | `mthi $zero` | `.word       0x00129A51                   # mthi        $zero # 00129A40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104698 | `audioCompandS16` | `0x800A368C` | `0x0012BCD3` | `mtlo $zero` | `.word       0x0012BCD3                   # mtlo        $zero # 0012BCC0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104718 | `audioCompandS16` | `0x800A36B4` | `0x0012E850` | `mfhi $sp` | `.word       0x0012E850                   # mfhi        $sp # 00120040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104726 | `audioCompandS16` | `0x800A36C4` | `0x0012F9D2` | `mflo $ra` | `.word       0x0012F9D2                   # mflo        $ra # 001201C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104805 | `audioCompandS16` | `0x800A375C` | `0x0013A350` | `mfhi $s4` | `.word       0x0013A350                   # mfhi        $s4 # 00130340 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104823 | `audioCompandS16` | `0x800A3780` | `0x0013CC51` | `mthi $zero` | `.word       0x0013CC51                   # mthi        $zero # 0013CC40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104939 | `audioCompandS16` | `0x800A3860` | `0x0014D310` | `mfhi $k0` | `.word       0x0014D310                   # mfhi        $k0 # 00140300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104981 | `audioCompandS16` | `0x800A38B4` | `0x00153912` | `mflo $a3` | `.word       0x00153912                   # mflo        $a3 # 00150100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104993 | `audioCompandS16` | `0x800A38CC` | `0x00155692` | `mflo $t2` | `.word       0x00155692                   # mflo        $t2 # 00150680 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105001 | `audioCompandS16` | `0x800A38DC` | `0x00156A53` | `mtlo $zero` | `.word       0x00156A53                   # mtlo        $zero # 00156A40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105015 | `audioCompandS16` | `0x800A38F8` | `0x00158D12` | `mflo $s1` | `.word       0x00158D12                   # mflo        $s1 # 00150500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105036 | `audioCompandS16` | `0x800A391C` | `0x0015BA11` | `mthi $zero` | `.word       0x0015BA11                   # mthi        $zero # 0015BA00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105050 | `audioCompandS16` | `0x800A3938` | `0x0015DD52` | `mflo $k1` | `.word       0x0015DD52                   # mflo        $k1 # 00150540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105058 | `audioCompandS16` | `0x800A3948` | `0x0015F190` | `mfhi $fp` | `.word       0x0015F190                   # mfhi        $fp # 00150180 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105070 | `audioCompandS16` | `0x800A3960` | `0x00161011` | `mthi $zero` | `.word       0x00161011                   # mthi        $zero # 00161000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105094 | `audioCompandS16` | `0x800A3990` | `0x00164D92` | `mflo $t1` | `.word       0x00164D92                   # mflo        $t1 # 00160580 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105106 | `audioCompandS16` | `0x800A39A8` | `0x00166C92` | `mflo $t5` | `.word       0x00166C92                   # mflo        $t5 # 00160480 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105132 | `audioCompandS16` | `0x800A39DC` | `0x0016B052` | `mflo $s6` | `.word       0x0016B052                   # mflo        $s6 # 00160040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105134 | `audioCompandS16` | `0x800A39E0` | `0x0016B591` | `mthi $zero` | `.word       0x0016B591                   # mthi        $zero # 0016B580 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105136 | `audioCompandS16` | `0x800A39E4` | `0x0016BAD1` | `mthi $zero` | `.word       0x0016BAD1                   # mthi        $zero # 0016BAC0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105138 | `audioCompandS16` | `0x800A39E8` | `0x0016C012` | `mflo $t8` | `.word       0x0016C012                   # mflo        $t8 # 00160000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105156 | `audioCompandS16` | `0x800A3A0C` | `0x0016EF92` | `mflo $sp` | `.word       0x0016EF92                   # mflo        $sp # 00160780 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105203 | `audioCompandS16` | `0x800A3A64` | `0x00176552` | `mflo $t4` | `.word       0x00176552                   # mflo        $t4 # 00170540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105263 | `audioCompandS16` | `0x800A3AD0` | `0x0017F911` | `mthi $zero` | `.word       0x0017F911                   # mthi        $zero # 0017F900 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105276 | `audioCompandS16` | `0x800A3AE4` | `0x001814D3` | `mtlo $zero` | `.word       0x001814D3                   # mtlo        $zero # 001814C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105331 | `audioCompandS16` | `0x800A3B44` | `0x00189BD1` | `mthi $zero` | `.word       0x00189BD1                   # mthi        $zero # 00189BC0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105371 | `audioCompandS16` | `0x800A3B94` | `0x00190E90` | `mfhi $at` | `.word       0x00190E90                   # mfhi        $at # 00190680 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105381 | `audioCompandS16` | `0x800A3BA8` | `0x00192B93` | `mtlo $zero` | `.word       0x00192B93                   # mtlo        $zero # 00192B80 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105394 | `audioCompandS16` | `0x800A3BC0` | `0x00194E90` | `mfhi $t1` | `.word       0x00194E90                   # mfhi        $t1 # 00190680 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105435 | `audioCompandS16` | `0x800A3C10` | `0x0019C492` | `mflo $t8` | `.word       0x0019C492                   # mflo        $t8 # 00190480 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105469 | `audioCompandS16` | `0x800A3C54` | `0x001A2A90` | `mfhi $a1` | `.word       0x001A2A90                   # mfhi        $a1 # 001A0280 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105509 | `audioCompandS16` | `0x800A3CA4` | `0x001AA493` | `mtlo $zero` | `.word       0x001AA493                   # mtlo        $zero # 001AA480 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105515 | `audioCompandS16` | `0x800A3CB0` | `0x001AB711` | `mthi $zero` | `.word       0x001AB711                   # mthi        $zero # 001AB700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105535 | `audioCompandS16` | `0x800A3CD8` | `0x001AF512` | `mflo $fp` | `.word       0x001AF512                   # mflo        $fp # 001A0500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105572 | `audioCompandS16` | `0x800A3D10` | `0x001B4CD3` | `mtlo $zero` | `.word       0x001B4CD3                   # mtlo        $zero # 001B4CC0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105590 | `audioCompandS16` | `0x800A3D34` | `0x001B85D3` | `mtlo $zero` | `.word       0x001B85D3                   # mtlo        $zero # 001B85C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105691 | `audioCompandS16` | `0x800A3DFC` | `0x001CCB10` | `mfhi $t9` | `.word       0x001CCB10                   # mfhi        $t9 # 001C0300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105738 | `audioCompandS16` | `0x800A3E4C` | `0x001D5153` | `mtlo $zero` | `.word       0x001D5153                   # mtlo        $zero # 001D5140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105801 | `audioCompandS16` | `0x800A3EC4` | `0x001E1F51` | `mthi $zero` | `.word       0x001E1F51                   # mthi        $zero # 001E1F40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105827 | `audioCompandS16` | `0x800A3EF8` | `0x001E7A53` | `mtlo $zero` | `.word       0x001E7A53                   # mtlo        $zero # 001E7A40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105848 | `audioCompandS16` | `0x800A3F20` | `0x001EC110` | `mfhi $t8` | `.word       0x001EC110                   # mfhi        $t8 # 001E0100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105862 | `audioCompandS16` | `0x800A3F38` | `0x001EEBD0` | `mfhi $sp` | `.word       0x001EEBD0                   # mfhi        $sp # 001E03C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105923 | `audioCompandS16` | `0x800A3FB0` | `0x001FC512` | `mflo $t8` | `.word       0x001FC512                   # mflo        $t8 # 001F0500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105972 | `audioCompandS16` | `0x800A400C` | `0x000FCC92` | `mflo $t9` | `.word       0x000FCC92                   # mflo        $t9 # 000F0480 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106101 | `audioCompandS16` | `0x800A410C` | `0x000EE991` | `mthi $zero` | `.word       0x000EE991                   # mthi        $zero # 000EE980 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106186 | `audioCompandS16` | `0x800A41B4` | `0x000E5B90` | `mfhi $t3` | `.word       0x000E5B90                   # mfhi        $t3 # 000E0380 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106194 | `audioCompandS16` | `0x800A41C4` | `0x000E4E52` | `mflo $t1` | `.word       0x000E4E52                   # mflo        $t1 # 000E0640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106224 | `audioCompandS16` | `0x800A4200` | `0x000E1D12` | `mflo $v1` | `.word       0x000E1D12                   # mflo        $v1 # 000E0500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106226 | `audioCompandS16` | `0x800A4204` | `0x000E19D0` | `mfhi $v1` | `.word       0x000E19D0                   # mfhi        $v1 # 000E01C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106238 | `audioCompandS16` | `0x800A421C` | `0x000E0651` | `mthi $zero` | `.word       0x000E0651                   # mthi        $zero # 000E0640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106297 | `audioCompandS16` | `0x800A4290` | `0x000DA991` | `mthi $zero` | `.word       0x000DA991                   # mthi        $zero # 000DA980 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106307 | `audioCompandS16` | `0x800A42A4` | `0x000D99D1` | `mthi $zero` | `.word       0x000D99D1                   # mthi        $zero # 000D99C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106363 | `audioCompandS16` | `0x800A430C` | `0x000D4910` | `mfhi $t1` | `.word       0x000D4910                   # mfhi        $t1 # 000D0100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106468 | `audioCompandS16` | `0x800A43D8` | `0x000CB010` | `mfhi $s6` | `.word       0x000CB010                   # mfhi        $s6 # 000C0000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106495 | `audioCompandS16` | `0x800A4408` | `0x000C8D13` | `mtlo $zero` | `.word       0x000C8D13                   # mtlo        $zero # 000C8D00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106542 | `audioCompandS16` | `0x800A4464` | `0x000C4B10` | `mfhi $t1` | `.word       0x000C4B10                   # mfhi        $t1 # 000C0300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106554 | `audioCompandS16` | `0x800A447C` | `0x000C3A11` | `mthi $zero` | `.word       0x000C3A11                   # mthi        $zero # 000C3A00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106595 | `audioCompandS16` | `0x800A44CC` | `0x000C0213` | `mtlo $zero` | `.word       0x000C0213                   # mtlo        $zero # 000C0200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106653 | `audioCompandS16` | `0x800A4538` | `0x000BB812` | `mflo $s7` | `.word       0x000BB812                   # mflo        $s7 # 000B0000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106680 | `audioCompandS16` | `0x800A456C` | `0x000B9513` | `mtlo $zero` | `.word       0x000B9513                   # mtlo        $zero # 000B9500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106692 | `audioCompandS16` | `0x800A4584` | `0x000B8510` | `mfhi $s0` | `.word       0x000B8510                   # mfhi        $s0 # 000B0500 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106715 | `audioCompandS16` | `0x800A45AC` | `0x000B6A90` | `mfhi $t5` | `.word       0x000B6A90                   # mfhi        $t5 # 000B0280 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106755 | `audioCompandS16` | `0x800A45F0` | `0x000B3E11` | `mthi $zero` | `.word       0x000B3E11                   # mthi        $zero # 000B3E00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106785 | `audioCompandS16` | `0x800A4620` | `0x000B1F10` | `mfhi $v1` | `.word       0x000B1F10                   # mfhi        $v1 # 000B0700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106816 | `audioCompandS16` | `0x800A4658` | `0x000AFB51` | `mthi $zero` | `.word       0x000AFB51                   # mthi        $zero # 000AFB40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106834 | `audioCompandS16` | `0x800A467C` | `0x000AE492` | `mflo $gp` | `.word       0x000AE492                   # mflo        $gp # 000A0480 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106867 | `audioCompandS16` | `0x800A46B8` | `0x000ABF13` | `mtlo $zero` | `.word       0x000ABF13                   # mtlo        $zero # 000ABF00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106884 | `audioCompandS16` | `0x800A46DC` | `0x000AA8D1` | `mthi $zero` | `.word       0x000AA8D1                   # mthi        $zero # 000AA8C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106888 | `audioCompandS16` | `0x800A46DC` | `0x000AA8D1` | `mthi $zero` | `.word       0x000AA8D1                   # mthi        $zero # 000AA8C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106949 | `audioCompandS16` | `0x800A4750` | `0x000A6252` | `mflo $t4` | `.word       0x000A6252                   # mflo        $t4 # 000A0240 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106967 | `audioCompandS16` | `0x800A4774` | `0x000A4CD1` | `mthi $zero` | `.word       0x000A4CD1                   # mthi        $zero # 000A4CC0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106975 | `audioCompandS16` | `0x800A4784` | `0x000A4350` | `mfhi $t0` | `.word       0x000A4350                   # mfhi        $t0 # 000A0340 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106979 | `audioCompandS16` | `0x800A478C` | `0x000A3E93` | `mtlo $zero` | `.word       0x000A3E93                   # mtlo        $zero # 000A3E80 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107003 | `audioCompandS16` | `0x800A47BC` | `0x000A2253` | `mtlo $zero` | `.word       0x000A2253                   # mtlo        $zero # 000A2240 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107015 | `audioCompandS16` | `0x800A47D4` | `0x000A1450` | `mfhi $v0` | `.word       0x000A1450                   # mfhi        $v0 # 000A0440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107029 | `audioCompandS16` | `0x800A47F0` | `0x000A0410` | `mfhi $zero` | `.word       0x000A0410                   # mfhi        $zero # 000A0400 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:107037 | `audioCompandS16` | `0x800A4800` | `0x0009FAD3` | `mtlo $zero` | `.word       0x0009FAD3                   # mtlo        $zero # 0009FAC0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107047 | `audioCompandS16` | `0x800A4814` | `0x0009EF52` | `mflo $sp` | `.word       0x0009EF52                   # mflo        $sp # 00090740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107087 | `audioCompandS16` | `0x800A4864` | `0x0009C1D3` | `mtlo $zero` | `.word       0x0009C1D3                   # mtlo        $zero # 0009C1C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107089 | `audioCompandS16` | `0x800A4868` | `0x0009BF92` | `mflo $s7` | `.word       0x0009BF92                   # mflo        $s7 # 00090780 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107091 | `audioCompandS16` | `0x800A486C` | `0x0009BD52` | `mflo $s7` | `.word       0x0009BD52                   # mflo        $s7 # 00090540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107093 | `audioCompandS16` | `0x800A4870` | `0x0009BB12` | `mflo $s7` | `.word       0x0009BB12                   # mflo        $s7 # 00090300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107095 | `audioCompandS16` | `0x800A4874` | `0x0009B8D3` | `mtlo $zero` | `.word       0x0009B8D3                   # mtlo        $zero # 0009B8C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107123 | `audioCompandS16` | `0x800A48AC` | `0x00099993` | `mtlo $zero` | `.word       0x00099993                   # mtlo        $zero # 00099980 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107176 | `audioCompandS16` | `0x800A4914` | `0x00096093` | `mtlo $zero` | `.word       0x00096093                   # mtlo        $zero # 00096080 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107202 | `audioCompandS16` | `0x800A4948` | `0x00094493` | `mtlo $zero` | `.word       0x00094493                   # mtlo        $zero # 00094480 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107297 | `audioCompandS16` | `0x800A49F0` | `0x0008EC52` | `mflo $sp` | `.word       0x0008EC52                   # mflo        $sp # 00080440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107331 | `audioCompandS16` | `0x800A4A30` | `0x0008CB93` | `mtlo $zero` | `.word       0x0008CB93                   # mtlo        $zero # 0008CB80 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107356 | `audioCompandS16` | `0x800A4A60` | `0x0008B352` | `mflo $s6` | `.word       0x0008B352                   # mflo        $s6 # 00080340 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107380 | `audioCompandS16` | `0x800A4A8C` | `0x00089D51` | `mthi $zero` | `.word       0x00089D51                   # mthi        $zero # 00089D40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107382 | `audioCompandS16` | `0x800A4A90` | `0x00089B53` | `mtlo $zero` | `.word       0x00089B53                   # mtlo        $zero # 00089B40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107418 | `audioCompandS16` | `0x800A4AD8` | `0x000877D2` | `mflo $t6` | `.word       0x000877D2                   # mflo        $t6 # 000807C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107455 | `audioCompandS16` | `0x800A4B1C` | `0x000856D0` | `mfhi $t2` | `.word       0x000856D0                   # mfhi        $t2 # 000806C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107480 | `audioCompandS16` | `0x800A4B4C` | `0x00083FD1` | `mthi $zero` | `.word       0x00083FD1                   # mthi        $zero # 00083FC0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107504 | `audioCompandS16` | `0x800A4B7C` | `0x00082912` | `mflo $a1` | `.word       0x00082912                   # mflo        $a1 # 00080100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107528 | `audioCompandS16` | `0x800A4BAC` | `0x00081291` | `mthi $zero` | `.word       0x00081291                   # mthi        $zero # 00081280 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107847 | `audioCompandS16` | `0x800A4E08` | `0x00010010` | `mfhi $zero` | `.word       0x00010010                   # mfhi        $zero # 00010000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_27.c:107994 | `audioCompandS16` | `0x800A4E90` | `0x022A5DD0` | `mfhi $t3` | `.word       0x022A5DD0                   # mfhi        $t3 # 022A05C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107998 | `audioCompandS16` | `0x800A4E90` | `0x022A5DD0` | `mfhi $t3` | `.word       0x022A5DD0                   # mfhi        $t3 # 022A05C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:108006 | `audioCompandS16` | `0x800A4EA0` | `0x015B5B53` | `mtlo $t2` | `.word       0x015B5B53                   # mtlo        $t2 # 001B5B40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_28.c:23553 | `npcIncomingMissileUpdate` | `0x800ABE18` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_28.c:26331 | `buildCutsceneGradientBuffers` | `0x800AC670` | `0x00006010` | `mfhi $t4` | `mfhi        $t4` | yes | unreachable | **correct** |
| funcs_28.c:27667 | `spawnNpcBurstAlongSegment` | `0x800ACD24` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_28.c:32821 | `updateCinematicCameraStateMachine` | `0x800AD800` | `0xD4245AD0` | `—` | `mfhi        $t0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_28.c:38191 | `loadBackdropAsset` | `0x800AE0A8` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_28.c:38241 | `loadBackdropAsset` | `0x800AE0EC` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_28.c:38251 | `loadBackdropAsset` | `0x800AE100` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_28.c:38508 | `loadBackdropAsset` | `0x800AE250` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_28.c:38518 | `loadBackdropAsset` | `0x800AE264` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_28.c:38666 | `loadBackdropAsset` | `0x800AE330` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_28.c:38685 | `loadBackdropAsset` | `0x800AE34C` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_28.c:38687 | `loadBackdropAsset` | `0x800AE350` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_28.c:38695 | `loadBackdropAsset` | `0x800AE360` | `0x00008812` | `mflo $s1` | `mflo        $s1` | yes | unreachable | **correct** |
| funcs_28.c:38703 | `loadBackdropAsset` | `0x800AE370` | `0x00006012` | `mflo $t4` | `mflo        $t4` | yes | unreachable | **correct** |
| funcs_28.c:38711 | `loadBackdropAsset` | `0x800AE380` | `0x00006012` | `mflo $t4` | `mflo        $t4` | yes | unreachable | **correct** |
| funcs_28.c:38721 | `loadBackdropAsset` | `0x800AE394` | `0x00008812` | `mflo $s1` | `mflo        $s1` | yes | unreachable | **correct** |
| funcs_28.c:38736 | `loadBackdropAsset` | `0x800AE3A8` | `0x00006012` | `mflo $t4` | `mflo        $t4` | yes | unreachable | **correct** |
| funcs_28.c:38744 | `loadBackdropAsset` | `0x800AE3B8` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_28.c:38754 | `loadBackdropAsset` | `0x800AE3CC` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_28.c:38762 | `loadBackdropAsset` | `0x800AE3DC` | `0x00006012` | `mflo $t4` | `mflo        $t4` | yes | unreachable | **correct** |
| funcs_28.c:38778 | `loadBackdropAsset` | `0x800AE3FC` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_28.c:38881 | `loadBackdropAsset` | `0x800AE48C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_28.c:38906 | `loadBackdropAsset` | `0x800AE4B0` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_28.c:41056 | `initCinematicSceneAssets` | `0x800AE628` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_28.c:41108 | `initCinematicSceneAssets` | `0x800AE670` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_28.c:41128 | `initCinematicSceneAssets` | `0x800AE690` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_28.c:41202 | `initCinematicSceneAssets` | `0x800AE6E8` | `0x00005812` | `mflo $t3` | `mflo        $t3` | yes | unreachable | **correct** |
| funcs_28.c:41222 | `initCinematicSceneAssets` | `0x800AE708` | `0x00008012` | `mflo $s0` | `mflo        $s0` | yes | unreachable | **correct** |
| funcs_28.c:41348 | `initCinematicSceneAssets` | `0x800AE7AC` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_28.c:41390 | `initCinematicSceneAssets` | `0x800AE7E0` | `0x00008812` | `mflo $s1` | `mflo        $s1` | yes | unreachable | **correct** |
| funcs_29.c:15710 | `spawnSceneDebrisAndEffectCluster` | `0x800B0674` | `0x00000000` | `—` | `mfhi        $t0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_29.c:15825 | `spawnSceneDebrisAndEffectCluster` | `0x800B070C` | `0x3E800000` | `—` | `mfhi        $t0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_29.c:17320 | `runScriptedCraftCinematicEvent` | `0x800B09D0` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_29.c:18994 | `runScriptedCraftCinematicEvent` | `0x800B1178` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_30.c:13709 | `buildFormatMessageGlyphBuffer` | `0x800B278C` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_30.c:13753 | `buildFormatMessageGlyphBuffer` | `0x800B27C8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_30.c:13763 | `buildFormatMessageGlyphBuffer` | `0x800B27DC` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_30.c:13899 | `buildFormatMessageGlyphBuffer` | `0x800B2884` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_30.c:13924 | `buildFormatMessageGlyphBuffer` | `0x800B28A8` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_30.c:14196 | `buildFormatMessageGlyphBuffer` | `0x800B2A0C` | `0x00002812` | `mflo $a1` | `mflo        $a1` | yes | unreachable | **correct** |
| funcs_30.c:14204 | `buildFormatMessageGlyphBuffer` | `0x800B2A1C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_30.c:14613 | `allocFormatTextElement` | `0x800B2C1C` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_30.c:14657 | `allocFormatTextElement` | `0x800B2C58` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_30.c:14667 | `allocFormatTextElement` | `0x800B2C6C` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_30.c:14752 | `allocFormatTextElement` | `0x800B2CD0` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_30.c:14775 | `allocFormatTextElement` | `0x800B2CF0` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_30.c:15080 | `loadNamedTextureDescriptor` | `0x800B2E84` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_30.c:15130 | `loadNamedTextureDescriptor` | `0x800B2EC8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_30.c:15140 | `loadNamedTextureDescriptor` | `0x800B2EDC` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_30.c:15397 | `loadNamedTextureDescriptor` | `0x800B302C` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_30.c:15407 | `loadNamedTextureDescriptor` | `0x800B3040` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_30.c:15555 | `loadNamedTextureDescriptor` | `0x800B310C` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_30.c:15574 | `loadNamedTextureDescriptor` | `0x800B3128` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_30.c:15576 | `loadNamedTextureDescriptor` | `0x800B312C` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_30.c:15584 | `loadNamedTextureDescriptor` | `0x800B313C` | `0x00008812` | `mflo $s1` | `mflo        $s1` | yes | unreachable | **correct** |
| funcs_30.c:15592 | `loadNamedTextureDescriptor` | `0x800B314C` | `0x00006012` | `mflo $t4` | `mflo        $t4` | yes | unreachable | **correct** |
| funcs_30.c:15600 | `loadNamedTextureDescriptor` | `0x800B315C` | `0x00006012` | `mflo $t4` | `mflo        $t4` | yes | unreachable | **correct** |
| funcs_30.c:15610 | `loadNamedTextureDescriptor` | `0x800B3170` | `0x00008812` | `mflo $s1` | `mflo        $s1` | yes | unreachable | **correct** |
| funcs_30.c:15625 | `loadNamedTextureDescriptor` | `0x800B3184` | `0x00006012` | `mflo $t4` | `mflo        $t4` | yes | unreachable | **correct** |
| funcs_30.c:15633 | `loadNamedTextureDescriptor` | `0x800B3194` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_30.c:15643 | `loadNamedTextureDescriptor` | `0x800B31A8` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_30.c:15651 | `loadNamedTextureDescriptor` | `0x800B31B8` | `0x00006012` | `mflo $t4` | `mflo        $t4` | yes | unreachable | **correct** |
| funcs_30.c:15667 | `loadNamedTextureDescriptor` | `0x800B31D8` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_30.c:15770 | `loadNamedTextureDescriptor` | `0x800B3268` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_30.c:15795 | `loadNamedTextureDescriptor` | `0x800B328C` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_30.c:16077 | `allocTextRenderTarget` | `0x800B3400` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_30.c:16125 | `allocTextRenderTarget` | `0x800B3440` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_30.c:16145 | `allocTextRenderTarget` | `0x800B3460` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_30.c:16221 | `allocTextRenderTarget` | `0x800B34BC` | `0x00005812` | `mflo $t3` | `mflo        $t3` | yes | unreachable | **correct** |
| funcs_30.c:16245 | `allocTextRenderTarget` | `0x800B34DC` | `0x00008012` | `mflo $s0` | `mflo        $s0` | yes | unreachable | **correct** |
| funcs_30.c:16371 | `allocTextRenderTarget` | `0x800B3580` | `0x00008812` | `mflo $s1` | `mflo        $s1` | yes | unreachable | **correct** |
| funcs_30.c:16413 | `allocTextRenderTarget` | `0x800B35B4` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_30.c:19081 | `buildScaledFormatTextElement` | `0x800B3B9C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_30.c:19127 | `buildScaledFormatTextElement` | `0x800B3BD8` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_31.c:3525 | `menuControllerInput` | `0x800B4928` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_31.c:5537 | `menuControllerInput` | `0x800B529C` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_31.c:26837 | `buildHudAmmoReadout` | `0x800B83AC` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_31.c:26861 | `buildHudAmmoReadout` | `0x800B83D0` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_31.c:26915 | `buildHudAmmoReadout` | `0x800B8420` | `0x00005812` | `mflo $t3` | `mflo        $t3` | yes | unreachable | **correct** |
| funcs_31.c:28151 | `readAccountForSelectionScreen` | `0x800B8640` | `0x00003810` | `mfhi $a3` | `mfhi        $a3` | yes | unreachable | **correct** |
| funcs_31.c:28736 | `setMaterialTextureByName` | `0x800B8948` | `0x00003810` | `mfhi $a3` | `mfhi        $a3` | yes | unreachable | **correct** |
| funcs_31.c:32276 | `cycleAccountLabelText` | `0x800B8E54` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_31.c:32330 | `cycleAccountLabelText` | `0x800B8EB0` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_31.c:32356 | `cycleAccountLabelText` | `0x800B8EE0` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_31.c:35517 | `tickVwingEngineAudio` | `0x800B9AA8` | `0xC42C6A68` | `—` | `mfhi        $t0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_31.c:35568 | `tickVwingEngineAudio` | `0x800B9AF8` | `0x24150004` | `—` | `mfhi        $t0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_32.c:15930 | `integrateTieInterceptorPhysics` | `0x800BC530` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_32.c:16104 | `integrateTieInterceptorPhysics` | `0x800BC638` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_32.c:18162 | `playerTieInterceptorMainUpdate` | `0x800BC9D4` | `0x0000B810` | `mfhi $s7` | `mfhi        $s7` | yes | unreachable | **correct** |
| funcs_32.c:18202 | `playerTieInterceptorMainUpdate` | `0x800BCA0C` | `0x0000B812` | `mflo $s7` | `mflo        $s7` | yes | unreachable | **correct** |
| funcs_32.c:18499 | `playerTieInterceptorMainUpdate` | `0x800BCB58` | `0x0000B810` | `mfhi $s7` | `mfhi        $s7` | yes | unreachable | **correct** |
| funcs_32.c:18842 | `playerTieInterceptorMainUpdate` | `0x800BCCB8` | `0x0000B810` | `mfhi $s7` | `mfhi        $s7` | yes | unreachable | **correct** |
| funcs_32.c:19079 | `playerTieInterceptorMainUpdate` | `0x800BCDBC` | `0x0000B810` | `mfhi $s7` | `mfhi        $s7` | yes | unreachable | **correct** |
| funcs_33.c:4001 | `runMenuRandomBackdropScreen` | `0x800BF91C` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_33.c:10176 | `initHudStruct` | `0x800C123C` | `0x02002821` | `—` | `mfhi        $t0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:14624 | `postLevelStatScreen` | `0x800C0DC8` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_33.c:14668 | `postLevelStatScreen` | `0x800C0E08` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_33.c:18138 | `tickMenuSelectionEnterState` | `0x800C1E00` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_33.c:26153 | `runPauseMenuStateMachine` | `0x800C3118` | `0xA3A40020` | `—` | `mfhi        $t8` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:26192 | `runPauseMenuStateMachine` | `0x800C3150` | `0x3C02800A` | `—` | `mflo        $v0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:27084 | `runPauseMenuStateMachine` | `0x800C35D4` | `0x1049FFED` | `—` | `mfhi        $t8` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:27141 | `runPauseMenuStateMachine` | `0x800C3630` | `0x0C021FBA` | `—` | `mfhi        $t8` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:27316 | `runPauseMenuStateMachine` | `0x800C3730` | `0x0C021FBA` | `—` | `mfhi        $t8` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:34324 | `setupCraftPreviewModel` | `0x800C4484` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_33.c:34936 | `plotRadarBlipColumn` | `0x800C423C` | `0x8E46001C` | `—` | `mflo        $t9` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:35000 | `plotRadarBlipColumn` | `0x800C42B0` | `0x0803115D` | `—` | `mfhi        $a2` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:35016 | `plotRadarBlipColumn` | `0x800C42D0` | `0x3C01800A` | `—` | `mfhi        $s0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:35038 | `plotRadarBlipColumn` | `0x800C42F8` | `0x10400029` | `—` | `mfhi        $a2` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:35054 | `plotRadarBlipColumn` | `0x800C4318` | `0x46146302` | `—` | `mfhi        $s0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:35171 | `plotRadarBlipRow` | `0x800C43B8` | `0x0C01CAF8` | `—` | `mflo        $t8` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:35249 | `plotRadarBlipRow` | `0x800C4434` | `0x00000000` | `—` | `mfhi        $a2` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:35265 | `plotRadarBlipRow` | `0x800C4454` | `0xAE600014` | `—` | `mfhi        $t9` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:35287 | `plotRadarBlipRow` | `0x800C447C` | `0x306400FF` | `—` | `mfhi        $a2` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_33.c:35303 | `plotRadarBlipRow` | `0x800C449C` | `0x3C03800D` | `—` | `mfhi        $t9` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_34.c:6181 | `initMenuBackdropAndPickRandom` | `0x800C5794` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_35.c:5144 | `parseJfifSOF0Marker` | `0x800C7104` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_35.c:5171 | `parseJfifSOF0Marker` | `0x800C7128` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_35.c:5481 | `parseJfifSOF0Marker` | `0x800C72C4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_35.c:5521 | `parseJfifSOF0Marker` | `0x800C72F8` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_35.c:5564 | `parseJfifSOF0Marker` | `0x800C733C` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_35.c:5604 | `parseJfifSOF0Marker` | `0x800C7370` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_35.c:5618 | `parseJfifSOF0Marker` | `0x800C7388` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_35.c:5658 | `parseJfifSOF0Marker` | `0x800C73BC` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_35.c:7588 | `paserJfifSOSMarker` | `0x800C77A8` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_35.c:7628 | `paserJfifSOSMarker` | `0x800C77DC` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_35.c:7636 | `paserJfifSOSMarker` | `0x800C77EC` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_35.c:7676 | `paserJfifSOSMarker` | `0x800C7820` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_35.c:7729 | `paserJfifSOSMarker` | `0x800C7864` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_35.c:7748 | `paserJfifSOSMarker` | `0x800C7880` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_35.c:7764 | `paserJfifSOSMarker` | `0x800C78A0` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_35.c:7778 | `paserJfifSOSMarker` | `0x800C78BC` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_35.c:8201 | `randMod` | `0x800C7814` | `0x14C10002` | `—` | `mfhi        $v1` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_36.c:633 | `rebuildDebrisCellGeometry` | `0x800C7A58` | `0x00008812` | `mflo $s1` | `mflo        $s1` | yes | unreachable | **correct** |
| funcs_36.c:2158 | `emitDebrisCellFaces` | `0x800C7EAC` | `0x00007812` | `mflo $t7` | `mflo        $t7` | yes | unreachable | **correct** |
| funcs_36.c:3611 | `computeCellGridIndices` | `0x800C808C` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_36.c:3657 | `computeCellGridIndices` | `0x800C80CC` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_36.c:3698 | `computeCellGridIndices` | `0x800C8104` | `0x00002812` | `mflo $a1` | `mflo        $a1` | yes | unreachable | **correct** |
| funcs_36.c:3738 | `computeCellGridIndices` | `0x800C8138` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_36.c:3754 | `computeCellGridIndices` | `0x800C8154` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_36.c:3794 | `computeCellGridIndices` | `0x800C8188` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_36.c:3816 | `computeCellGridIndices` | `0x800C81A8` | `0x00002812` | `mflo $a1` | `mflo        $a1` | yes | unreachable | **correct** |
| funcs_36.c:8356 | `allocCellGeometryBuffer` | `0x800C8B60` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_36.c:8392 | `allocCellGeometryBuffer` | `0x800C8B90` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_36.c:8430 | `allocCellGeometryBuffer` | `0x800C8BC4` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_36.c:8466 | `allocCellGeometryBuffer` | `0x800C8BF4` | `0x00004012` | `mflo $t0` | `mflo        $t0` | yes | unreachable | **correct** |
| funcs_36.c:8631 | `buildDebrisMeshFromCells` | `0x800C8CCC` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_36.c:8641 | `buildDebrisMeshFromCells` | `0x800C8CE0` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_36.c:8924 | `buildDebrisMeshFromCells` | `0x800C8E70` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_36.c:9048 | `buildDebrisMeshFromCells` | `0x800C8F24` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_36.c:9197 | `buildDebrisMeshFromCells` | `0x800C9004` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_36.c:9237 | `buildDebrisMeshFromCells` | `0x800C9038` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_36.c:9245 | `buildDebrisMeshFromCells` | `0x800C9048` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_36.c:9285 | `buildDebrisMeshFromCells` | `0x800C907C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_36.c:9299 | `buildDebrisMeshFromCells` | `0x800C9098` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_36.c:9323 | `buildDebrisMeshFromCells` | `0x800C90C8` | `0x00003812` | `mflo $a3` | `mflo        $a3` | yes | unreachable | **correct** |
| funcs_36.c:9478 | `buildDebrisMeshFromCells` | `0x800C91D0` | `0x00006012` | `mflo $t4` | `mflo        $t4` | yes | unreachable | **correct** |
| funcs_36.c:9486 | `buildDebrisMeshFromCells` | `0x800C91E0` | `0x00005012` | `mflo $t2` | `mflo        $t2` | yes | unreachable | **correct** |
| funcs_36.c:9717 | `buildDebrisMeshFromCells` | `0x800C9350` | `0x0000A012` | `mflo $s4` | `mflo        $s4` | yes | unreachable | **correct** |
| funcs_36.c:9726 | `buildDebrisMeshFromCells` | `0x800C9360` | `0x00003812` | `mflo $a3` | `mflo        $a3` | yes | unreachable | **correct** |
| funcs_36.c:9766 | `buildDebrisMeshFromCells` | `0x800C9394` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_36.c:9774 | `buildDebrisMeshFromCells` | `0x800C93A4` | `0x00003812` | `mflo $a3` | `mflo        $a3` | yes | unreachable | **correct** |
| funcs_36.c:9814 | `buildDebrisMeshFromCells` | `0x800C93D8` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_36.c:9824 | `buildDebrisMeshFromCells` | `0x800C93EC` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_36.c:9840 | `buildDebrisMeshFromCells` | `0x800C940C` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_36.c:10137 | `buildDebrisMeshFromCells` | `0x800C95F8` | `0x0000F012` | `mflo $fp` | `mflo        $fp` | yes | unreachable | **correct** |
| funcs_36.c:10145 | `buildDebrisMeshFromCells` | `0x800C9608` | `0x0000B012` | `mflo $s6` | `mflo        $s6` | yes | unreachable | **correct** |
| funcs_36.c:10163 | `buildDebrisMeshFromCells` | `0x800C9628` | `0x0000A012` | `mflo $s4` | `mflo        $s4` | yes | unreachable | **correct** |
| funcs_36.c:10470 | `buildDebrisMeshFromCells` | `0x800C9824` | `0x0000B812` | `mflo $s7` | `mflo        $s7` | yes | unreachable | **correct** |
| funcs_36.c:10482 | `buildDebrisMeshFromCells` | `0x800C983C` | `0x00008812` | `mflo $s1` | `mflo        $s1` | yes | unreachable | **correct** |
| funcs_36.c:10490 | `buildDebrisMeshFromCells` | `0x800C984C` | `0x0000B012` | `mflo $s6` | `mflo        $s6` | yes | unreachable | **correct** |
| funcs_36.c:12794 | `npcTurretUpdate` | `0x800C97A8` | `0x96030002` | `—` | `mfhi        $t0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_36.c:14397 | `npcTurretUpdate` | `0x800C9F20` | `0x24080002` | `—` | `mfhi        $t0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_36.c:22385 | `npcProbeDriod` | `0x800CB17C` | `0x00108100` | `—` | `mfhi        $t0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_36.c:22711 | `npcProbeDriod` | `0x800CB320` | `0xAFB1006C` | `—` | `mfhi        $t0` | yes | unreachable | **ELF/annotation mismatch** |
| funcs_37.c:1336 | `loadModelViewerModels` | `0x800CB8FC` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_37.c:6011 | `compareStatstoMedalInfo` | `0x800CC2E4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_37.c:6167 | `calculateShotAccuracy` | `0x800CC3A8` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_37.c:6964 | `data_gap_800CC3D4` | `0x800CC940` | `0x00C80091` | `mthi $a2` | `.word       0x00C80091                   # mthi        $a2 # 00080080 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:6966 | `data_gap_800CC3D4` | `0x800CC944` | `0x01900191` | `mthi $t4` | `.word       0x01900191                   # mthi        $t4 # 00100180 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:7063 | `data_gap_800CC3D4` | `0x800CCA04` | `0x00100011` | `mthi $zero` | `.word       0x00100011                   # mthi        $zero # 00100000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:7084 | `data_gap_800CC3D4` | `0x800CCA2C` | `0x00900091` | `mthi $a0` | `.word       0x00900091                   # mthi        $a0 # 00100080 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:7127 | `data_gap_800CC3D4` | `0x800CCA7C` | `0x00000010` | `mfhi $zero` | `mfhi        $zero` | NO | unreachable | **data-like/unreachable** |
| funcs_37.c:7663 | `data_gap_800CC3D4` | `0x800CCEA0` | `0x00000011` | `mthi $zero` | `mthi        $zero` | yes | unreachable | **correct** |
| funcs_37.c:7667 | `data_gap_800CC3D4` | `0x800CCEA8` | `0x00000013` | `mtlo $zero` | `mtlo        $zero` | yes | unreachable | **correct** |
| funcs_37.c:7711 | `data_gap_800CC3D4` | `0x800CCF00` | `0x00000051` | `mthi $zero` | `.word       0x00000051                   # mthi        $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:7715 | `data_gap_800CC3D4` | `0x800CCF08` | `0x00000052` | `mflo $zero` | `.word       0x00000052                   # mflo        $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_37.c:7719 | `data_gap_800CC3D4` | `0x800CCF10` | `0x00000053` | `mtlo $zero` | `.word       0x00000053                   # mtlo        $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:7824 | `data_gap_800CC3D4` | `0x800CCFE0` | `0x00000050` | `mfhi $zero` | `.word       0x00000050                   # mfhi        $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_37.c:7895 | `data_gap_800CC3D4` | `0x800CD06C` | `0x00230010` | `mfhi $zero` | `.word       0x00230010                   # mfhi        $zero # 00230000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_37.c:7897 | `data_gap_800CC3D4` | `0x800CD070` | `0x00220010` | `mfhi $zero` | `.word       0x00220010                   # mfhi        $zero # 00220000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_37.c:7922 | `data_gap_800CC3D4` | `0x800CD090` | `0x00240011` | `mthi $at` | `.word       0x00240011                   # mthi        $at # 00040000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:8021 | `data_gap_800CC3D4` | `0x800CD140` | `0x00250012` | `mflo $zero` | `.word       0x00250012                   # mflo        $zero # 00250000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_37.c:8023 | `data_gap_800CC3D4` | `0x800CD144` | `0x00270012` | `mflo $zero` | `.word       0x00270012                   # mflo        $zero # 00270000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_37.c:8041 | `data_gap_800CC3D4` | `0x800CD168` | `0x00290013` | `mtlo $at` | `.word       0x00290013                   # mtlo        $at # 00090000 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:8258 | `data_gap_800CC3D4` | `0x800CD2E8` | `0x00100010` | `mfhi $zero` | `.word       0x00100010                   # mfhi        $zero # 00100000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_37.c:8284 | `data_gap_800CC3D4` | `0x800CD300` | `0x01C00010` | `mfhi $zero` | `.word       0x01C00010                   # mfhi        $zero # 01C00000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_37.c:8286 | `data_gap_800CC3D4` | `0x800CD304` | `0x00101110` | `mfhi $v0` | `.word       0x00101110                   # mfhi        $v0 # 00100100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:8290 | `data_gap_800CC3D4` | `0x800CD30C` | `0x000002D0` | `mfhi $zero` | `.word       0x000002D0                   # mfhi        $zero # 000002C0 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_37.c:8327 | `data_gap_800CC3D4` | `0x800CD338` | `0x00001110` | `mfhi $v0` | `.word       0x00001110                   # mfhi        $v0 # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:8353 | `data_gap_800CC3D4` | `0x800CD36C` | `0x00001110` | `mfhi $v0` | `.word       0x00001110                   # mfhi        $v0 # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:8379 | `data_gap_800CC3D4` | `0x800CD3A0` | `0x00001110` | `mfhi $v0` | `.word       0x00001110                   # mfhi        $v0 # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:8385 | `data_gap_800CC3D4` | `0x800CD3AC` | `0x00640010` | `mfhi $zero` | `.word       0x00640010                   # mfhi        $zero # 00640000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_37.c:19055 | `npcAtStHandleDestruction` | `0x800CFAD0` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_38.c:733 | `npcShuttleHandleDestruction` | `0x800D3524` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_38.c:1078 | `npcShuttleHandleDestruction` | `0x800D36BC` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_38.c:3716 | `npcShuttleUpdate` | `0x800D4310` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_38.c:7879 | `npcDebrisFieldUpdate` | `0x800D5704` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_38.c:17940 | `npcWingmanBehaviorByMode` | `0x800D8718` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_38.c:17983 | `npcWingmanBehaviorByMode` | `0x800D8760` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_38.c:18026 | `npcWingmanBehaviorByMode` | `0x800D87A8` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_38.c:18121 | `npcWingmanBehaviorByMode` | `0x800D8834` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_38.c:26146 | `npcTieVariantHandleDestruction` | `0x800DAED0` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_38.c:28503 | `npcTieVariantUpdate` | `0x800DBA3C` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_38.c:32222 | `npcRadarDishUpdate` | `0x800DCBB8` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_38.c:40479 | `npcGroundTransportUpdate` | `0x800DF3BC` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_39.c:1470 | `playAttachmentCueWithSlotIter` | `0x800E02D0` | `0x00004810` | `mfhi $t1` | `mfhi        $t1` | yes | unreachable | **correct** |
| funcs_39.c:11954 | `npcTrainCarUpdate` | `0x800E3534` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_39.c:19974 | `npcWaterCraftHandleDestruction` | `0x800E5C6C` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_39.c:20606 | `npcWaterCraftHandleDestruction` | `0x800E5F70` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_39.c:29787 | `runDestructionPhaseSequence` | `0x800E8AF8` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_39.c:37828 | `npcAtPtUpdate` | `0x800EB0DC` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_39.c:41382 | `allocObjectPoolNode` | `0x800EC1AC` | `0x00006010` | `mfhi $t4` | `mfhi        $t4` | yes | unreachable | **correct** |
| funcs_4.c:7091 | `renderFlatMeshFaceGroup` | `0x800117A0` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_4.c:7101 | `renderFlatMeshFaceGroup` | `0x800117B4` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_4.c:7187 | `renderFlatMeshFaceGroup` | `0x80011838` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_4.c:8855 | `renderUnlitMeshFaces` | `0x80011F9C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_4.c:8865 | `renderUnlitMeshFaces` | `0x80011FB0` | `0x00003012` | `mflo $a2` | `mflo        $a2` | yes | unreachable | **correct** |
| funcs_4.c:8951 | `renderUnlitMeshFaces` | `0x80012034` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_4.c:24570 | `drawSubtitleText` | `0x80016338` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_4.c:24948 | `drawSubtitleText` | `0x800164C0` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_4.c:25220 | `drawSubtitleText` | `0x800165F8` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_4.c:25228 | `drawSubtitleText` | `0x80016608` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_4.c:25508 | `drawSubtitleText` | `0x800167A0` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_4.c:25880 | `drawSubtitleText` | `0x80016920` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_4.c:26152 | `drawSubtitleText` | `0x80016A58` | `0x00001812` | `mflo $v1` | `mflo        $v1` | yes | unreachable | **correct** |
| funcs_4.c:26160 | `drawSubtitleText` | `0x80016A68` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_4.c:30419 | `buildAndRegisterDefaultMaterial` | `0x80017E40` | `0x00005810` | `mfhi $t3` | `mfhi        $t3` | yes | unreachable | **correct** |
| funcs_4.c:30752 | `buildAndRegisterDefaultMaterial` | `0x8001801C` | `0x00005810` | `mfhi $t3` | `mfhi        $t3` | yes | unreachable | **correct** |
| funcs_40.c:6544 | `processPendingSoundCueRequest` | `0x800EE270` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_40.c:7096 | `processPendingSoundCueRequest` | `0x800EE534` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_40.c:13312 | `updateNpcEventTimer` | `0x800F0330` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_40.c:13382 | `updateNpcEventTimer` | `0x800F03A8` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_41.c:4974 | `initActorMotionParams` | `0x800F291C` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_41.c:6887 | `copyRandomPipeDelimitedField` | `0x800F31AC` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_42.c:14717 | `setupMissionTransitionScreenOverlay` | `0x800FB3C8` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_49.c:1910 | `lvj_checkComplexObjectives` | `0x80109684` | `0x00000110` | `mfhi $zero` | `.word       0x00000110                   # mfhi        $zero # 00000100 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_49.c:1912 | `lvj_checkComplexObjectives` | `0x80109688` | `0x00000111` | `mthi $zero` | `.word       0x00000111                   # mthi        $zero # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:1914 | `lvj_checkComplexObjectives` | `0x8010968C` | `0x00000113` | `mtlo $zero` | `.word       0x00000113                   # mtlo        $zero # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:1940 | `lvj_checkComplexObjectives` | `0x801096C0` | `0x012C0190` | `mfhi $zero` | `.word       0x012C0190                   # mfhi        $zero # 012C0180 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_49.c:1944 | `lvj_checkComplexObjectives` | `0x801096C0` | `0x012C0190` | `mfhi $zero` | `.word       0x012C0190                   # mfhi        $zero # 012C0180 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_49.c:3157 | `lvj_checkComplexObjectives` | `0x80109DE4` | `0x00002010` | `mfhi $a0` | `mfhi        $a0` | yes | unreachable | **correct** |
| funcs_49.c:3163 | `lvj_checkComplexObjectives` | `0x80109DF0` | `0x00002010` | `mfhi $a0` | `mfhi        $a0` | yes | unreachable | **correct** |
| funcs_49.c:5867 | `lvj_checkComplexObjectives` | `0x8010B1FC` | `0x00070010` | `mfhi $zero` | `.word       0x00070010                   # mfhi        $zero # 00070000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_49.c:5873 | `lvj_checkComplexObjectives` | `0x8010B208` | `0x00080012` | `mflo $zero` | `.word       0x00080012                   # mflo        $zero # 00080000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_49.c:6041 | `lvj_checkComplexObjectives` | `0x8010B32C` | `0x00000050` | `mfhi $zero` | `.word       0x00000050                   # mfhi        $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_49.c:7833 | `static_3_80045024` | `0x800452E0` | `0x00002810` | `mfhi $a1` | `mfhi        $a1` | yes | unreachable | **correct** |
| funcs_49.c:7851 | `static_3_80045024` | `0x80045300` | `0x00006010` | `mfhi $t4` | `mfhi        $t4` | yes | unreachable | **correct** |
| funcs_49.c:7886 | `static_3_80045024` | `0x80045334` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_49.c:7904 | `static_3_80045024` | `0x80045354` | `0x00001010` | `mfhi $v0` | `mfhi        $v0` | yes | unreachable | **correct** |
| funcs_49.c:9741 | `static_3_800A2B50` | `0x800A2BAC` | `0x00343C50` | `mfhi $a3` | `.word       0x00343C50                   # mfhi        $a3 # 00340440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:9815 | `static_3_800A2BE4` | `0x800A2BEC` | `0x00397451` | `mthi $at` | `.word       0x00397451                   # mthi        $at # 00197440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:9854 | `static_3_800A2BE4` | `0x800A2C28` | `0x0036C750` | `mfhi $t8` | `.word       0x0036C750                   # mfhi        $t8 # 00360740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:9856 | `static_3_800A2BE4` | `0x800A2C2C` | `0x003F3452` | `mflo $a2` | `.word       0x003F3452                   # mflo        $a2 # 003F0440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:9894 | `static_3_800A2BE4` | `0x800A2C68` | `0x003C4151` | `mthi $at` | `.word       0x003C4151                   # mthi        $at # 001C4140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:9896 | `static_3_800A2BE4` | `0x800A2C6C` | `0x00458653` | `mtlo $v0` | `.word       0x00458653                   # mtlo        $v0 # 00058640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:9932 | `static_3_800A2BE4` | `0x800A2CA4` | `0x00381550` | `mfhi $v0` | `.word       0x00381550                   # mfhi        $v0 # 00380540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:9934 | `static_3_800A2BE4` | `0x800A2CA8` | `0x00424852` | `mflo $t1` | `.word       0x00424852                   # mflo        $t1 # 00420040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:9976 | `static_3_800A2BE4` | `0x800A2CE4` | `0x003DB151` | `mthi $at` | `.word       0x003DB151                   # mthi        $at # 001DB140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:9978 | `static_3_800A2BE4` | `0x800A2CE8` | `0x0048E953` | `mtlo $v0` | `.word       0x0048E953                   # mtlo        $v0 # 0008E940 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10014 | `static_3_800A2BE4` | `0x800A2D20` | `0x00378650` | `mfhi $s0` | `.word       0x00378650                   # mfhi        $s0 # 00370640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10016 | `static_3_800A2BE4` | `0x800A2D24` | `0x0043DC52` | `mflo $k1` | `.word       0x0043DC52                   # mflo        $k1 # 00430440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10054 | `static_3_800A2BE4` | `0x800A2D60` | `0x003D1451` | `mthi $at` | `.word       0x003D1451                   # mthi        $at # 001D1440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10056 | `static_3_800A2BE4` | `0x800A2D64` | `0x004AA653` | `mtlo $v0` | `.word       0x004AA653                   # mtlo        $v0 # 000AA640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10094 | `static_3_800A2BE4` | `0x800A2DA0` | `0x00433052` | `mflo $a2` | `.word       0x00433052                   # mflo        $a2 # 00430040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10126 | `static_3_800A2BE4` | `0x800A2DD0` | `0x00083650` | `mfhi $a2` | `.word       0x00083650                   # mfhi        $a2 # 00080640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10128 | `static_3_800A2BE4` | `0x800A2DD4` | `0x0018A250` | `mfhi $s4` | `.word       0x0018A250                   # mfhi        $s4 # 00180240 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10130 | `static_3_800A2BE4` | `0x800A2DD8` | `0x00290F50` | `mfhi $at` | `.word       0x00290F50                   # mfhi        $at # 00290740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10132 | `static_3_800A2BE4` | `0x800A2DDC` | `0x00397B50` | `mfhi $t7` | `.word       0x00397B50                   # mfhi        $t7 # 00390340 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10134 | `static_3_800A2BE4` | `0x800A2DE0` | `0x0049E853` | `mtlo $v0` | `.word       0x0049E853                   # mtlo        $v0 # 0009E840 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10166 | `static_3_800A2BE4` | `0x800A2E10` | `0x00090851` | `mthi $zero` | `.word       0x00090851                   # mthi        $zero # 00090840 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10168 | `static_3_800A2BE4` | `0x800A2E14` | `0x001B1951` | `mthi $zero` | `.word       0x001B1951                   # mthi        $zero # 001B1940 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10170 | `static_3_800A2BE4` | `0x800A2E18` | `0x002D2A51` | `mthi $at` | `.word       0x002D2A51                   # mthi        $at # 000D2A40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10172 | `static_3_800A2BE4` | `0x800A2E1C` | `0x003F3B51` | `mthi $at` | `.word       0x003F3B51                   # mthi        $at # 001F3B40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10206 | `static_3_800A2BE4` | `0x800A2E50` | `0x0009EF52` | `mflo $sp` | `.word       0x0009EF52                   # mflo        $sp # 00090740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10208 | `static_3_800A2BE4` | `0x800A2E54` | `0x001DCE52` | `mflo $t9` | `.word       0x001DCE52                   # mflo        $t9 # 001D0640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10210 | `static_3_800A2BE4` | `0x800A2E58` | `0x0031AE52` | `mflo $s5` | `.word       0x0031AE52                   # mflo        $s5 # 00310640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10212 | `static_3_800A2BE4` | `0x800A2E5C` | `0x00458D52` | `mflo $s1` | `.word       0x00458D52                   # mflo        $s1 # 00450540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10246 | `static_3_800A2BE4` | `0x800A2E90` | `0x000AEE53` | `mtlo $zero` | `.word       0x000AEE53                   # mtlo        $zero # 000AEE40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10248 | `static_3_800A2BE4` | `0x800A2E94` | `0x0020CA53` | `mtlo $at` | `.word       0x0020CA53                   # mtlo        $at # 0000CA40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10254 | `static_3_800A2E98` | `0x800A2E98` | `0x0036A653` | `mtlo $at` | `.word       0x0036A653                   # mtlo        $at # 0016A640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10256 | `static_3_800A2E98` | `0x800A2E9C` | `0x004C8253` | `mtlo $v0` | `.word       0x004C8253                   # mtlo        $v0 # 000C8240 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10465 | `static_3_800A2FE4` | `0x800A2FEC` | `0x0017F911` | `mthi $zero` | `.word       0x0017F911                   # mthi        $zero # 0017F900 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10586 | `static_3_800A2FE4` | `0x800A30C0` | `0x02000010` | `mfhi $zero` | `.word       0x02000010                   # mfhi        $zero # 02000000 <InstrIdType: CPU_SPECIAL>` | NO | unreachable | **data-like/unreachable** |
| funcs_49.c:10604 | `static_3_800A2FE4` | `0x800A30E4` | `0x035D1410` | `mfhi $v0` | `.word       0x035D1410                   # mfhi        $v0 # 035D0400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_5.c:550 | `initVideoSubsystem` | `0x8001A2B0` | `0x00008012` | `mflo $s0` | `mflo        $s0` | yes | unreachable | **correct** |
| funcs_5.c:571 | `initVideoSubsystem` | `0x8001A2D4` | `0x00008012` | `mflo $s0` | `mflo        $s0` | yes | unreachable | **correct** |
| funcs_5.c:969 | `initVideoSubsystem` | `0x8001A514` | `0x0000C810` | `mfhi $t9` | `mfhi        $t9` | yes | unreachable | **correct** |
| funcs_5.c:1340 | `initVideoSubsystem` | `0x8001A6E0` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_5.c:1436 | `initVideoSubsystem` | `0x8001A74C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_5.c:1531 | `initVideoSubsystem` | `0x8001A7BC` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_5.c:1623 | `initVideoSubsystem` | `0x8001A824` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_5.c:2002 | `initVideoSubsystem` | `0x8001AA48` | `0x0000C810` | `mfhi $t9` | `mfhi        $t9` | yes | unreachable | **correct** |
| funcs_5.c:2373 | `initVideoSubsystem` | `0x8001AC18` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_5.c:2828 | `initVideoSubsystem` | `0x8001AEB4` | `0x0000C810` | `mfhi $t9` | `mfhi        $t9` | yes | unreachable | **correct** |
| funcs_5.c:3197 | `initVideoSubsystem` | `0x8001B07C` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_5.c:3289 | `initVideoSubsystem` | `0x8001B0E4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_5.c:3384 | `initVideoSubsystem` | `0x8001B154` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_5.c:3476 | `initVideoSubsystem` | `0x8001B1BC` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_5.c:3855 | `initVideoSubsystem` | `0x8001B3E0` | `0x0000C810` | `mfhi $t9` | `mfhi        $t9` | yes | unreachable | **correct** |
| funcs_5.c:4226 | `initVideoSubsystem` | `0x8001B5B0` | `0x00002012` | `mflo $a0` | `mflo        $a0` | yes | unreachable | **correct** |
| funcs_5.c:5780 | `computeFramebufferByteSize` | `0x8001BC70` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_5.c:5799 | `computeFramebufferByteSize` | `0x8001BC90` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_6.c:8508 | `loadTextureTile` | `0x800202C4` | `0x00008812` | `mflo $s1` | `mflo        $s1` | yes | unreachable | **correct** |
| funcs_6.c:9083 | `loadTextureTile` | `0x800205E0` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_6.c:9578 | `loadTextureTile` | `0x80020894` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_6.c:10474 | `loadTextureTile` | `0x80020D24` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_6.c:10987 | `loadTextureTile` | `0x80020FF4` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_6.c:11474 | `loadTextureTile` | `0x80021298` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_6.c:11975 | `loadTextureTile` | `0x80021558` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_6.c:12472 | `loadTextureTile` | `0x80021810` | `0x00009012` | `mflo $s2` | `mflo        $s2` | yes | unreachable | **correct** |
| funcs_7.c:646 | `emitProfilerBarSegment` | `0x80023DAC` | `0x00002010` | `mfhi $a0` | `mfhi        $a0` | yes | unreachable | **correct** |
| funcs_7.c:648 | `emitProfilerBarSegment` | `0x80023DB0` | `0x00002812` | `mflo $a1` | `mflo        $a1` | yes | unreachable | **correct** |
| funcs_7.c:1865 | `flushDebugTextOverlay` | `0x800243A4` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_7.c:8372 | `adler32` | `0x80026B1C` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_7.c:8392 | `adler32` | `0x80026B44` | `0x00002010` | `mfhi $a0` | `mfhi        $a0` | yes | unreachable | **correct** |
| funcs_7.c:9356 | `inflate_recomp` | `0x80026FD0` | `0x00002010` | `mfhi $a0` | `mfhi        $a0` | yes | unreachable | **correct** |
| funcs_8.c:6857 | `_Printf` | `0x80036184` | `0x00007812` | `mflo $t7` | `mflo        $t7` | yes | unreachable | **correct** |
| funcs_8.c:6995 | `_Printf` | `0x80036230` | `0x00007812` | `mflo $t7` | `mflo        $t7` | yes | unreachable | **correct** |
| funcs_8.c:8731 | `_Genld` | `0x80036A58` | `0x00009010` | `mfhi $s2` | `mfhi        $s2` | yes | unreachable | **correct** |
| funcs_8.c:8735 | `_Genld` | `0x80036A60` | `0x0000C812` | `mflo $t9` | `mflo        $t9` | yes | unreachable | **correct** |
| funcs_8.c:8786 | `_Genld` | `0x80036AA4` | `0x00009010` | `mfhi $s2` | `mfhi        $s2` | yes | unreachable | **correct** |
| funcs_8.c:8790 | `_Genld` | `0x80036AAC` | `0x0000C812` | `mflo $t9` | `mflo        $t9` | yes | unreachable | **correct** |
| funcs_8.c:8841 | `_Genld` | `0x80036AF0` | `0x00009010` | `mfhi $s2` | `mfhi        $s2` | yes | unreachable | **correct** |
| funcs_8.c:8845 | `_Genld` | `0x80036AF8` | `0x0000C812` | `mflo $t9` | `mflo        $t9` | yes | unreachable | **correct** |
| funcs_8.c:9339 | `_Ldtob` | `0x80036D58` | `0x0000C012` | `mflo $t8` | `mflo        $t8` | yes | unreachable | **correct** |
| funcs_8.c:9347 | `_Ldtob` | `0x80036D68` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_8.c:10267 | `ldiv_recomp` | `0x800371E4` | `0x00001012` | `mflo $v0` | `mflo        $v0` | yes | unreachable | **correct** |
| funcs_8.c:10311 | `ldiv_recomp` | `0x8003721C` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_8.c:11131 | `__OSGlobalIntMask` | `0x80039254` | `0x00040C11` | `mthi $zero` | `.word       0x00040C11                   # mthi        $zero # 00040C00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:12607 | `__OSGlobalIntMask` | `0x80039C04` | `0x00040C11` | `mthi $zero` | `.word       0x00040C11                   # mthi        $zero # 00040C00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:12657 | `__OSGlobalIntMask` | `0x80039C54` | `0x00000C10` | `mfhi $at` | `.word       0x00000C10                   # mfhi        $at # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:12706 | `__OSGlobalIntMask` | `0x80039CA4` | `0x00040C11` | `mthi $zero` | `.word       0x00040C11                   # mthi        $zero # 00040C00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:12756 | `__OSGlobalIntMask` | `0x80039CF4` | `0x00000C10` | `mfhi $at` | `.word       0x00000C10                   # mfhi        $at # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:12800 | `__OSGlobalIntMask` | `0x80039D44` | `0x00040C11` | `mthi $zero` | `.word       0x00040C11                   # mthi        $zero # 00040C00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:12845 | `__OSGlobalIntMask` | `0x80039D94` | `0x00000C10` | `mfhi $at` | `.word       0x00000C10                   # mfhi        $at # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:12889 | `__OSGlobalIntMask` | `0x80039DE4` | `0x00040C11` | `mthi $zero` | `.word       0x00040C11                   # mthi        $zero # 00040C00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:12934 | `__OSGlobalIntMask` | `0x80039E34` | `0x00000C10` | `mfhi $at` | `.word       0x00000C10                   # mfhi        $at # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:12979 | `__OSGlobalIntMask` | `0x80039E84` | `0x00000C10` | `mfhi $at` | `.word       0x00000C10                   # mfhi        $at # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:13024 | `__OSGlobalIntMask` | `0x80039ED4` | `0x00000C10` | `mfhi $at` | `.word       0x00000C10                   # mfhi        $at # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:13069 | `__OSGlobalIntMask` | `0x80039F24` | `0x00000C10` | `mfhi $at` | `.word       0x00000C10                   # mfhi        $at # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:13114 | `__OSGlobalIntMask` | `0x80039F74` | `0x00000C10` | `mfhi $at` | `.word       0x00000C10                   # mfhi        $at # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:13159 | `__OSGlobalIntMask` | `0x80039FC4` | `0x00000C10` | `mfhi $at` | `.word       0x00000C10                   # mfhi        $at # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:13204 | `__OSGlobalIntMask` | `0x8003A014` | `0x00000C10` | `mfhi $at` | `.word       0x00000C10                   # mfhi        $at # 00000400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_8.c:13595 | `__OSGlobalIntMask` | `0x8003A29C` | `0x00000010` | `mfhi $zero` | `mfhi        $zero` | NO | unreachable | **data-like/unreachable** |
| funcs_8.c:13599 | `__OSGlobalIntMask` | `0x8003A29C` | `0x00000010` | `mfhi $zero` | `mfhi        $zero` | NO | unreachable | **data-like/unreachable** |
| funcs_9.c:4517 | `randomBurstNpcHandlerVariant` | `0x800405C4` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_9.c:5655 | `spawnNpcFormationWithRandomOrientation` | `0x80040B08` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_9.c:5729 | `spawnNpcFormationWithRandomOrientation` | `0x80040B80` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_9.c:5919 | `spawnNpcFormationWithRandomOrientation` | `0x80040C68` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_9.c:6029 | `spawnNpcFormationWithRandomOrientation` | `0x80040CFC` | `0x00003010` | `mfhi $a2` | `mfhi        $a2` | yes | unreachable | **correct** |
| funcs_9.c:6133 | `spawnNpcFormationWithRandomOrientation` | `0x80040D94` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_9.c:6346 | `spawnNpcFormationWithRandomOrientation` | `0x80040E90` | `0x00004010` | `mfhi $t0` | `mfhi        $t0` | yes | unreachable | **correct** |
| funcs_9.c:12729 | `streamTerrainGridCellsByDistance` | `0x80042C54` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_9.c:12757 | `streamTerrainGridCellsByDistance` | `0x80042C78` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_9.c:13723 | `streamTerrainGridCellsByDistance` | `0x80043110` | `0x00007012` | `mflo $t6` | `mflo        $t6` | yes | unreachable | **correct** |
| funcs_9.c:15994 | `markLowLodCellsInGrid` | `0x80043BA8` | `0x00005812` | `mflo $t3` | `mflo        $t3` | yes | unreachable | **correct** |
| funcs_9.c:16016 | `markLowLodCellsInGrid` | `0x80043BD0` | `0x00005812` | `mflo $t3` | `mflo        $t3` | yes | unreachable | **correct** |
| funcs_9.c:16256 | `markHighLodCellsInGrid` | `0x80043CEC` | `0x00005812` | `mflo $t3` | `mflo        $t3` | yes | unreachable | **correct** |
| funcs_9.c:16278 | `markHighLodCellsInGrid` | `0x80043D14` | `0x00005812` | `mflo $t3` | `mflo        $t3` | yes | unreachable | **correct** |
| funcs_9.c:16921 | `load_level_hmp` | `0x8004408C` | `0x0000C012` | `mflo $t8` | `mflo        $t8` | yes | unreachable | **correct** |
| funcs_9.c:16955 | `load_level_hmp` | `0x800440B8` | `0x0000C012` | `mflo $t8` | `mflo        $t8` | yes | unreachable | **correct** |
| funcs_9.c:16992 | `load_level_hmp` | `0x800440EC` | `0x0000C012` | `mflo $t8` | `mflo        $t8` | yes | unreachable | **correct** |
| funcs_9.c:17015 | `load_level_hmp` | `0x80044110` | `0x0000C012` | `mflo $t8` | `mflo        $t8` | yes | unreachable | **correct** |
| funcs_9.c:17075 | `load_level_hmp` | `0x80044170` | `0x0000C012` | `mflo $t8` | `mflo        $t8` | yes | unreachable | **correct** |
| funcs_9.c:19240 | `computeGridTileEdgeAdjacencyMasks` | `0x80044C8C` | `0x0000C012` | `mflo $t8` | `mflo        $t8` | yes | unreachable | **correct** |
| funcs_9.c:19294 | `computeGridTileEdgeAdjacencyMasks` | `0x80044CD4` | `0x0000C012` | `mflo $t8` | `mflo        $t8` | yes | unreachable | **correct** |
| funcs_9.c:19344 | `computeGridTileEdgeAdjacencyMasks` | `0x80044D14` | `0x0000C012` | `mflo $t8` | `mflo        $t8` | yes | unreachable | **correct** |
| funcs_9.c:19402 | `computeGridTileEdgeAdjacencyMasks` | `0x80044D6C` | `0x0000C012` | `mflo $t8` | `mflo        $t8` | yes | unreachable | **correct** |
| funcs_9.c:20319 | `computeGridTileEdgeAdjacencyMasks` | `0x800452E0` | `0x00002810` | `mfhi $a1` | `mfhi        $a1` | yes | unreachable | **correct** |
| funcs_9.c:20337 | `computeGridTileEdgeAdjacencyMasks` | `0x80045300` | `0x00006010` | `mfhi $t4` | `mfhi        $t4` | yes | unreachable | **correct** |
| funcs_9.c:20372 | `computeGridTileEdgeAdjacencyMasks` | `0x80045334` | `0x00001810` | `mfhi $v1` | `mfhi        $v1` | yes | unreachable | **correct** |
| funcs_9.c:20390 | `computeGridTileEdgeAdjacencyMasks` | `0x80045354` | `0x00001010` | `mfhi $v0` | `mfhi        $v0` | yes | unreachable | **correct** |
