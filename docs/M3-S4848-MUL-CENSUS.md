# M3 generated 32-bit multiplication census

Static census only. The retail ELF supplies the independent raw word; generated C supplies the signedness lowering and conservative CFG reachability. The generated tree contains `mult`/`multu` annotations, not integer `mul` annotations, so this is the applicable 32-bit multiplication class.

- annotation rows: **670**; unique file/guest-PC sites: **669**
- raw ELF decodes: **643/670**; generated lowerings present: **643/670**; conservative CFG reachable: **543**
- classifications: `ELF/annotation mismatch`=27, `correct`=643
- positive control: `funcs_0.c:817` PC `0x80000E04`, raw=`0x00620018`, decode=`('mult', 'v1', 'v0')`, lowering=present; **PASS**

## Interpretation

The raw ELF and generated annotations disagree at one or more sites; provenance review is required before closure.

## Complete site table

| file:line | function | guest PC | raw word | ELF decode | annotation | lowering | CFG | classification |
|---|---|---:|---:|---|---|---|---|---|
| funcs_0.c:817 | `partitionFramebufferMemory` | `0x80000E04` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_0.c:836 | `partitionFramebufferMemory` | `0x80000E24` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_0.c:857 | `partitionFramebufferMemory` | `0x80000E44` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_0.c:6647 | `computeElapsedMillis` | `0x800026B8` | `0x02040019` | `multu s0 a0` | `multu       $s0, $a0` | yes | reachable | **correct** |
| funcs_1.c:283 | `rand_recomp` | `0x80003440` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_1.c:6237 | `rs_zcalloc` | `0x80005280` | `0x00850018` | `mult a0 a1` | `mult        $a0, $a1` | yes | reachable | **correct** |
| funcs_10.c:436 | `initGridLayerFromLevelData` | `0x80045918` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_10.c:534 | `initGridLayerFromLevelData` | `0x800459B4` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_10.c:2030 | `selectGridCellTileVariant` | `0x80046164` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_10.c:2208 | `buildGridCellLabel` | `0x8004627C` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_10.c:3005 | `parseDatItemCommon` | `0x800466BC` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_10.c:5164 | `loadDatFile` | `0x80047020` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_10.c:5182 | `loadDatFile` | `0x8004703C` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_10.c:5219 | `loadDatFile` | `0x80047070` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_10.c:6132 | `updateActiveGridCellState` | `0x800474CC` | `0x03C20018` | `mult fp v0` | `mult        $fp, $v0` | yes | reachable | **correct** |
| funcs_10.c:8505 | `allocAndInitGridCellArray` | `0x80048080` | `0x02220018` | `mult s1 v0` | `mult        $s1, $v0` | yes | reachable | **correct** |
| funcs_10.c:8650 | `loadLevelTextureCache` | `0x8004813C` | `0x00430019` | `multu v0 v1` | `multu       $v0, $v1` | yes | reachable | **correct** |
| funcs_10.c:9411 | `getGridCellValueAt` | `0x80048544` | `0x01830018` | `mult t4 v1` | `mult        $t4, $v1` | yes | reachable | **correct** |
| funcs_10.c:9791 | `getGridCellValueAt` | `0x8004876C` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_10.c:10297 | `clampGridCellLookup` | `0x80048A14` | `0x02220018` | `mult s1 v0` | `mult        $s1, $v0` | yes | reachable | **correct** |
| funcs_10.c:10855 | `processGridCellByDistance` | `0x80048D3C` | `0x00A40018` | `mult a1 a0` | `mult        $a1, $a0` | yes | reachable | **correct** |
| funcs_10.c:10960 | `processGridCellByDistance` | `0x80048DE4` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_10.c:12811 | `emitGridCellTileStrip` | `0x80049844` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_10.c:13537 | `emitGridCellTileStripAdjacent` | `0x80049BEC` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_10.c:14346 | `emitGridCellTileStripDiagonal` | `0x80049FE8` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_10.c:16868 | `mapCellGeometryToGridSpace` | `0x8004AAE8` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_10.c:18520 | `scaleObjectPosToGridUnits` | `0x8004B300` | `0x01C20018` | `mult t6 v0` | `mult        $t6, $v0` | yes | reachable | **correct** |
| funcs_10.c:22086 | `getGridCellFromWorldPos` | `0x8004C38C` | `0x01E60018` | `mult t7 a2` | `mult        $t7, $a2` | yes | reachable | **correct** |
| funcs_11.c:4856 | `updateMultiNodeAudioListeners` | `0x80050568` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_11.c:18594 | `tickWrappingTimerAccumulatorList` | `0x80054770` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_11.c:18988 | `loadAssetIntoNewSlot` | `0x80054948` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_11.c:19051 | `loadAssetIntoNewSlot` | `0x8005499C` | `0x00510018` | `mult v0 s1` | `mult        $v0, $s1` | yes | reachable | **correct** |
| funcs_12.c:464 | `loadSpriteSheetTextureFrames` | `0x800553B0` | `0x02230018` | `mult s1 v1` | `mult        $s1, $v1` | yes | reachable | **correct** |
| funcs_12.c:2325 | `tickVoiceSubtitleDisplay` | `0x80055DBC` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_12.c:3083 | `setSubtitleOverlayScreenPos` | `0x800561E0` | `0x02020018` | `mult s0 v0` | `mult        $s0, $v0` | yes | reachable | **correct** |
| funcs_12.c:3091 | `setSubtitleOverlayScreenPos` | `0x800561F0` | `0x02130018` | `mult s0 s3` | `mult        $s0, $s3` | yes | reachable | **correct** |
| funcs_12.c:3121 | `setSubtitleOverlayScreenPos` | `0x80056220` | `0x02220018` | `mult s1 v0` | `mult        $s1, $v0` | yes | reachable | **correct** |
| funcs_12.c:3129 | `setSubtitleOverlayScreenPos` | `0x80056230` | `0x02220018` | `mult s1 v0` | `mult        $s1, $v0` | yes | reachable | **correct** |
| funcs_12.c:3165 | `setSubtitleOverlayScreenPos` | `0x8005626C` | `0x00730018` | `mult v1 s3` | `mult        $v1, $s3` | yes | reachable | **correct** |
| funcs_12.c:5119 | `load_hmt_and_hob` | `0x80056C90` | `0x02820018` | `mult s4 v0` | `mult        $s4, $v0` | yes | reachable | **correct** |
| funcs_12.c:5331 | `isHobObjectLoaded` | `0x80056DD0` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_12.c:5616 | `walkMeshdef0List` | `0x80056F08` | `0x02220018` | `mult s1 v0` | `mult        $s1, $v0` | yes | reachable | **correct** |
| funcs_12.c:6376 | `instantiateNamedMeshInstance` | `0x8005737C` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_12.c:6695 | `applyRgbaTintToMeshVertices` | `0x80057560` | `0x00670018` | `mult v1 a3` | `mult        $v1, $a3` | yes | reachable | **correct** |
| funcs_12.c:6715 | `applyRgbaTintToMeshVertices` | `0x80057588` | `0x00C70018` | `mult a2 a3` | `mult        $a2, $a3` | yes | reachable | **correct** |
| funcs_12.c:6735 | `applyRgbaTintToMeshVertices` | `0x800575B0` | `0x00870018` | `mult a0 a3` | `mult        $a0, $a3` | yes | reachable | **correct** |
| funcs_12.c:6749 | `applyRgbaTintToMeshVertices` | `0x800575CC` | `0x00670018` | `mult v1 a3` | `mult        $v1, $a3` | yes | reachable | **correct** |
| funcs_12.c:6792 | `applyRgbaTintToMeshVertices` | `0x80057618` | `0x004B0018` | `mult v0 t3` | `mult        $v0, $t3` | yes | reachable | **correct** |
| funcs_12.c:6805 | `applyRgbaTintToMeshVertices` | `0x80057630` | `0x004A0018` | `mult v0 t2` | `mult        $v0, $t2` | yes | reachable | **correct** |
| funcs_12.c:6816 | `applyRgbaTintToMeshVertices` | `0x80057644` | `0x00460018` | `mult v0 a2` | `mult        $v0, $a2` | yes | reachable | **correct** |
| funcs_12.c:6827 | `applyRgbaTintToMeshVertices` | `0x80057658` | `0x00450018` | `mult v0 a1` | `mult        $v0, $a1` | yes | reachable | **correct** |
| funcs_12.c:6850 | `applyRgbaTintToMeshVertices` | `0x8005767C` | `0x004B0018` | `mult v0 t3` | `mult        $v0, $t3` | yes | reachable | **correct** |
| funcs_12.c:6861 | `applyRgbaTintToMeshVertices` | `0x80057690` | `0x004A0018` | `mult v0 t2` | `mult        $v0, $t2` | yes | reachable | **correct** |
| funcs_12.c:6872 | `applyRgbaTintToMeshVertices` | `0x800576A4` | `0x00460018` | `mult v0 a2` | `mult        $v0, $a2` | yes | reachable | **correct** |
| funcs_12.c:6883 | `applyRgbaTintToMeshVertices` | `0x800576B8` | `0x00450018` | `mult v0 a1` | `mult        $v0, $a1` | yes | reachable | **correct** |
| funcs_12.c:6894 | `applyRgbaTintToMeshVertices` | `0x800576CC` | `0x004B0018` | `mult v0 t3` | `mult        $v0, $t3` | yes | reachable | **correct** |
| funcs_12.c:6905 | `applyRgbaTintToMeshVertices` | `0x800576E0` | `0x004A0018` | `mult v0 t2` | `mult        $v0, $t2` | yes | reachable | **correct** |
| funcs_12.c:6916 | `applyRgbaTintToMeshVertices` | `0x800576F4` | `0x00460018` | `mult v0 a2` | `mult        $v0, $a2` | yes | reachable | **correct** |
| funcs_12.c:6927 | `applyRgbaTintToMeshVertices` | `0x80057708` | `0x00450018` | `mult v0 a1` | `mult        $v0, $a1` | yes | reachable | **correct** |
| funcs_12.c:6950 | `applyRgbaTintToMeshVertices` | `0x8005772C` | `0x004B0018` | `mult v0 t3` | `mult        $v0, $t3` | yes | reachable | **correct** |
| funcs_12.c:6961 | `applyRgbaTintToMeshVertices` | `0x80057740` | `0x004A0018` | `mult v0 t2` | `mult        $v0, $t2` | yes | reachable | **correct** |
| funcs_12.c:6972 | `applyRgbaTintToMeshVertices` | `0x80057754` | `0x00460018` | `mult v0 a2` | `mult        $v0, $a2` | yes | reachable | **correct** |
| funcs_12.c:6983 | `applyRgbaTintToMeshVertices` | `0x80057768` | `0x00450018` | `mult v0 a1` | `mult        $v0, $a1` | yes | reachable | **correct** |
| funcs_12.c:7275 | `releaseMeshAsset` | `0x800578FC` | `0x00460019` | `multu v0 a2` | `multu       $v0, $a2` | yes | reachable | **correct** |
| funcs_12.c:7749 | `getHobObjectByName` | `0x80057B78` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_13.c:2767 | `loadTopCloudsAsset` | `0x8005A2B4` | `0x02440018` | `mult s2 a0` | `mult        $s2, $a0` | yes | reachable | **correct** |
| funcs_13.c:4103 | `updateWalkerParticlePositions` | `0x8005A954` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_13.c:6325 | `setupWalkerSpriteTileQuad` | `0x8005B56C` | `0x00430019` | `multu v0 v1` | `multu       $v0, $v1` | yes | reachable | **correct** |
| funcs_13.c:6345 | `setupWalkerSpriteTileQuad` | `0x8005B58C` | `0x00430019` | `multu v0 v1` | `multu       $v0, $v1` | yes | reachable | **correct** |
| funcs_13.c:7077 | `setupWalkerSpriteTileQuad` | `0x8005B8CC` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_13.c:7290 | `setupWalkerSpriteTileQuad` | `0x8005B9C4` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_13.c:10694 | `audioCueDispatcherNpcHandler` | `0x8005C940` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_13.c:11774 | `audioCueDispatcherNpcHandler` | `0x8005CE68` | `0x00620019` | `multu v1 v0` | `multu       $v1, $v0` | yes | reachable | **correct** |
| funcs_13.c:25045 | `randomlyScaledColoredEffectNpcHandler` | `0x80060C78` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_14.c:1039 | `loadCharTextureSet` | `0x80061718` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_14.c:1066 | `loadCharTextureSet` | `0x80061744` | `0x00720018` | `mult v1 s2` | `mult        $v1, $s2` | yes | reachable | **correct** |
| funcs_14.c:1177 | `loadCharTextureSet` | `0x800617D8` | `0x00B30018` | `mult a1 s3` | `mult        $a1, $s3` | yes | reachable | **correct** |
| funcs_14.c:1189 | `loadCharTextureSet` | `0x800617F0` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_14.c:1618 | `loadCharTextureSet` | `0x80061A10` | `0x02240018` | `mult s1 a0` | `mult        $s1, $a0` | yes | reachable | **correct** |
| funcs_14.c:1648 | `loadCharTextureSet` | `0x80061A34` | `0x02300018` | `mult s1 s0` | `mult        $s1, $s0` | yes | reachable | **correct** |
| funcs_14.c:3942 | `startPlayerSlotAnimationChannelExt` | `0x8006264C` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_14.c:3964 | `startPlayerSlotAnimationChannelExt` | `0x80062674` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_14.c:4094 | `startPlayerSlotAnimationChannelExt` | `0x80062730` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_14.c:4116 | `startPlayerSlotAnimationChannelExt` | `0x80062758` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_14.c:4410 | `startPlayerSlotAnimationChannel` | `0x800628E4` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_14.c:4432 | `startPlayerSlotAnimationChannel` | `0x8006290C` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_14.c:4576 | `startPlayerSlotAnimationChannel` | `0x800629D8` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_14.c:4598 | `startPlayerSlotAnimationChannel` | `0x80062A00` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_14.c:4842 | `advancePlayerAnimationPhase` | `0x80062B30` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_14.c:5422 | `initPlayerSlotAnimationChannelFull` | `0x80062DFC` | `0x00450018` | `mult v0 a1` | `mult        $v0, $a1` | yes | reachable | **correct** |
| funcs_14.c:5444 | `initPlayerSlotAnimationChannelFull` | `0x80062E24` | `0x00450018` | `mult v0 a1` | `mult        $v0, $a1` | yes | reachable | **correct** |
| funcs_14.c:5681 | `startPlayerSlotAnimationChannelFlagged` | `0x80062F6C` | `0x00450018` | `mult v0 a1` | `mult        $v0, $a1` | yes | reachable | **correct** |
| funcs_14.c:5703 | `startPlayerSlotAnimationChannelFlagged` | `0x80062F94` | `0x00450018` | `mult v0 a1` | `mult        $v0, $a1` | yes | reachable | **correct** |
| funcs_14.c:7733 | `buildPlayerCraftAssetTemplate` | `0x8006399C` | `0x02020018` | `mult s0 v0` | `mult        $s0, $v0` | yes | reachable | **correct** |
| funcs_14.c:8454 | `setPlayerSlotAnimationFlag` | `0x80063D5C` | `0x00460018` | `mult v0 a2` | `mult        $v0, $a2` | yes | reachable | **correct** |
| funcs_14.c:8478 | `setPlayerSlotAnimationFlag` | `0x80063D88` | `0x00460018` | `mult v0 a2` | `mult        $v0, $a2` | yes | reachable | **correct** |
| funcs_16.c:752 | `wrapAngleToCyclicRange` | `0x80067F48` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_16.c:1714 | `sampleTerrainSurfaceAtWorldXz` | `0x8006836C` | `0x01030018` | `mult t0 v1` | `mult        $t0, $v1` | yes | reachable | **correct** |
| funcs_16.c:1885 | `sampleTerrainSurfaceAtWorldXz` | `0x80068460` | `0x01020018` | `mult t0 v0` | `mult        $t0, $v0` | yes | reachable | **correct** |
| funcs_16.c:1986 | `sampleTerrainSurfaceAtWorldXz` | `0x80068504` | `0x01030018` | `mult t0 v1` | `mult        $t0, $v1` | yes | reachable | **correct** |
| funcs_16.c:2116 | `sampleTerrainSurfaceAtWorldXz` | `0x800685CC` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_16.c:2230 | `sampleTerrainSurfaceAtWorldXz` | `0x8006867C` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_16.c:4315 | `sampleTerrainAtNpcPosition` | `0x80068F20` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_16.c:4399 | `sampleTerrainAtNpcPosition` | `0x80068F88` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_16.c:4470 | `sampleTerrainAtNpcPosition` | `0x80068FC4` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_16.c:6946 | `isTerrainCellBlockedAtWorldXz` | `0x80069A64` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_16.c:19344 | `updateDestructionDebrisNpc` | `0x8006D0FC` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_16.c:19899 | `updateDestructionDebrisNpc` | `0x8006D3A0` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_17.c:4698 | `cycleIdleDemoId` | `0x8006F05C` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_18.c:1194 | `loadSfxAsset` | `0x80071E20` | `0x00680018` | `mult v1 t0` | `mult        $v1, $t0` | yes | reachable | **correct** |
| funcs_18.c:1290 | `loadSfxAsset` | `0x80071E88` | `0x00880018` | `mult a0 t0` | `mult        $a0, $t0` | yes | reachable | **correct** |
| funcs_18.c:10437 | `triggerObjectDestructionEffects` | `0x8007492C` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_18.c:14759 | `buildNpcAnchoredCameraEffectTransform` | `0x80075D0C` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_19.c:3312 | `sampleRgbBoxFilter2x2AtSubpixel` | `0x8007A10C` | `0x00E60018` | `mult a3 a2` | `mult        $a3, $a2` | yes | reachable | **correct** |
| funcs_19.c:3368 | `sampleRgbBoxFilter2x2AtSubpixel` | `0x8007A15C` | `0x01060018` | `mult t0 a2` | `mult        $t0, $a2` | yes | reachable | **correct** |
| funcs_19.c:3659 | `downscaleImageHalfResBoxFilter` | `0x8007A2F8` | `0x02680018` | `mult s3 t0` | `mult        $s3, $t0` | yes | reachable | **correct** |
| funcs_19.c:5049 | `transformMeshVerticesForNpc` | `0x8007AA48` | `0x00630018` | `mult v1 v1` | `mult        $v1, $v1` | yes | reachable | **correct** |
| funcs_19.c:5057 | `transformMeshVerticesForNpc` | `0x8007AA58` | `0x00840018` | `mult a0 a0` | `mult        $a0, $a0` | yes | reachable | **correct** |
| funcs_19.c:5090 | `transformMeshVerticesForNpc` | `0x8007AA84` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_19.c:5098 | `transformMeshVerticesForNpc` | `0x8007AA94` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_19.c:5185 | `transformMeshVerticesForNpc` | `0x8007AAF4` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_19.c:5195 | `transformMeshVerticesForNpc` | `0x8007AB08` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_19.c:5205 | `transformMeshVerticesForNpc` | `0x8007AB1C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_19.c:7350 | `npcShieldUpdate` | `0x8007B510` | `0x00A30018` | `mult a1 v1` | `mult        $a1, $v1` | yes | reachable | **correct** |
| funcs_19.c:17996 | `spawnWorldDevastatorVacuumDebris` | `0x8007E898` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_19.c:24457 | `attachedAudioVisualEmitterNpcHandler` | `0x80080748` | `0x00A30018` | `mult a1 v1` | `mult        $a1, $v1` | yes | reachable | **correct** |
| funcs_19.c:27542 | `npcShieldGeneratorUpdate` | `0x80081684` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_2.c:2679 | `initSaveData` | `0x800065A8` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_2.c:2763 | `initSaveData` | `0x80006614` | `0x02220018` | `mult s1 v0` | `mult        $s1, $v0` | yes | reachable | **correct** |
| funcs_2.c:3292 | `saveLoadDispatcher` | `0x800068A0` | `0x03C70018` | `mult fp a3` | `mult        $fp, $a3` | yes | reachable | **correct** |
| funcs_2.c:3494 | `loadOrSaveEepromRecord` | `0x800069A0` | `0x02670018` | `mult s3 a3` | `mult        $s3, $a3` | yes | reachable | **correct** |
| funcs_2.c:3796 | `loadOrSaveAllEepromRecords` | `0x80006B28` | `0x02620018` | `mult s3 v0` | `mult        $s3, $v0` | yes | reachable | **correct** |
| funcs_20.c:6729 | `unusedRand` | `0x80083C80` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_20.c:6870 | `setTrackVoiceTickBudget` | `0x80083D44` | `0x00430019` | `multu v0 v1` | `multu       $v0, $v1` | yes | reachable | **correct** |
| funcs_20.c:8950 | `evaluateVoiceModulatorRecord` | `0x80084964` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_20.c:9055 | `evaluateVoiceModulatorRecord` | `0x800849E0` | `0x02030018` | `mult s0 v1` | `mult        $s0, $v1` | yes | reachable | **correct** |
| funcs_20.c:9113 | `evaluateVoiceModulatorRecord` | `0x80084A2C` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_20.c:9191 | `evaluateVoiceModulatorRecord` | `0x80084A84` | `0x02030018` | `mult s0 v1` | `mult        $s0, $v1` | yes | reachable | **correct** |
| funcs_21.c:3206 | `binarySearchWithComparator` | `0x80085C60` | `0x02F10018` | `mult s7 s1` | `mult        $s7, $s1` | yes | reachable | **correct** |
| funcs_21.c:3419 | `factor5BucketedTableLookupValue` | `0x80085D84` | `0x02D10018` | `mult s6 s1` | `mult        $s6, $s1` | yes | reachable | **correct** |
| funcs_21.c:3615 | `factor5SortedTableLookupWidePairRecord` | `0x80085E80` | `0x02D10018` | `mult s6 s1` | `mult        $s6, $s1` | yes | reachable | **correct** |
| funcs_21.c:3857 | `factor5SecondSortedTableLookupValue` | `0x80085FBC` | `0x02B10018` | `mult s5 s1` | `mult        $s5, $s1` | yes | reachable | **correct** |
| funcs_21.c:4024 | `factor5SortedTableLookupValue` | `0x80086094` | `0x02B10018` | `mult s5 s1` | `mult        $s5, $s1` | yes | reachable | **correct** |
| funcs_21.c:4211 | `factor5SortedTableLookupTaggedValue` | `0x80086184` | `0x02B10018` | `mult s5 s1` | `mult        $s5, $s1` | yes | reachable | **correct** |
| funcs_21.c:4404 | `musyxSortedInsertByU16` | `0x80086280` | `0x02B10018` | `mult s5 s1` | `mult        $s5, $s1` | yes | reachable | **correct** |
| funcs_21.c:5963 | `computeVoiceGlidePitch` | `0x80086A8C` | `0x00850018` | `mult a0 a1` | `mult        $a0, $a1` | yes | reachable | **correct** |
| funcs_21.c:5973 | `computeVoiceGlidePitch` | `0x80086AA0` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_21.c:6375 | `findActiveVoiceByKeyPair` | `0x80086CA0` | `0x00850018` | `mult a0 a1` | `mult        $a0, $a1` | yes | reachable | **correct** |
| funcs_21.c:6385 | `findActiveVoiceByKeyPair` | `0x80086CB4` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_21.c:7876 | `applyNoteEventToGroup` | `0x80087484` | `0x02F10018` | `mult s7 s1` | `mult        $s7, $s1` | yes | reachable | **correct** |
| funcs_21.c:8196 | `applyNoteEventToGroup` | `0x80087628` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_21.c:8204 | `applyNoteEventToGroup` | `0x80087638` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_21.c:9067 | `dispatchSequencerNoteEvent` | `0x80087AA0` | `0x01110018` | `mult t0 s1` | `mult        $t0, $s1` | yes | reachable | **correct** |
| funcs_21.c:9688 | `musyxNoteEventLockedDispatch` | `0x80087DF4` | `0x03D10018` | `mult fp s1` | `mult        $fp, $s1` | yes | reachable | **correct** |
| funcs_21.c:9974 | `bsearchFactor5TableByU16Key` | `0x80087F6C` | `0x03D10018` | `mult fp s1` | `mult        $fp, $s1` | yes | reachable | **correct** |
| funcs_21.c:10361 | `musyxSetSequenceParamLocked` | `0x80088150` | `0x02D10018` | `mult s6 s1` | `mult        $s6, $s1` | yes | reachable | **correct** |
| funcs_22.c:1923 | `computeChannelWaitDuration` | `0x80089688` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_22.c:2591 | `soundMacroOpGosubRandomLoop` | `0x800899E0` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_22.c:2914 | `soundMacroOpLoopRandomCount` | `0x80089B7C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_22.c:3748 | `computeChannelPitchSweepStep` | `0x80089F98` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_22.c:3756 | `computeChannelPitchSweepStep` | `0x80089FA8` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_22.c:3789 | `computeChannelPitchSweepStep` | `0x80089FDC` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_22.c:3797 | `computeChannelPitchSweepStep` | `0x80089FEC` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_22.c:3910 | `soundMacroOpStartNoteAbsoluteSweep` | `0x8008A084` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_22.c:3918 | `soundMacroOpStartNoteAbsoluteSweep` | `0x8008A094` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_22.c:3951 | `soundMacroOpStartNoteAbsoluteSweep` | `0x8008A0C8` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_22.c:3959 | `soundMacroOpStartNoteAbsoluteSweep` | `0x8008A0D8` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_22.c:4130 | `soundMacroOpStartNoteRelativeSweep` | `0x8008A1C4` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_22.c:4138 | `soundMacroOpStartNoteRelativeSweep` | `0x8008A1D4` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_22.c:4171 | `soundMacroOpStartNoteRelativeSweep` | `0x8008A208` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_22.c:4179 | `soundMacroOpStartNoteRelativeSweep` | `0x8008A218` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_22.c:4328 | `soundMacroOpStartNoteTransposedSweep` | `0x8008A2E4` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_22.c:4336 | `soundMacroOpStartNoteTransposedSweep` | `0x8008A2F4` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_22.c:4369 | `soundMacroOpStartNoteTransposedSweep` | `0x8008A328` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_22.c:4377 | `soundMacroOpStartNoteTransposedSweep` | `0x8008A338` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_22.c:4520 | `soundMacroOpPlaySampleKeymap` | `0x8008A3FC` | `0x02F10018` | `mult s7 s1` | `mult        $s7, $s1` | yes | reachable | **correct** |
| funcs_22.c:4704 | `soundMacroOpPlaySampleKeymap` | `0x8008A4F0` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_22.c:4712 | `soundMacroOpPlaySampleKeymap` | `0x8008A500` | `0x00430019` | `multu v0 v1` | `multu       $v0, $v1` | yes | reachable | **correct** |
| funcs_22.c:4896 | `soundMacroOpPlaySampleKeymap` | `0x8008A5F4` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_22.c:4904 | `soundMacroOpPlaySampleKeymap` | `0x8008A604` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_22.c:4935 | `soundMacroOpPlaySampleKeymap` | `0x8008A634` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_22.c:4943 | `soundMacroOpPlaySampleKeymap` | `0x8008A644` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_22.c:5505 | `musyxSetVoiceAdsrFromTable` | `0x8008A92C` | `0x02D10018` | `mult s6 s1` | `mult        $s6, $s1` | yes | reachable | **correct** |
| funcs_22.c:5881 | `soundMacroOpSetPitchRelativeToNote` | `0x8008AB28` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_22.c:6035 | `evaluateSoundMacroCurveTable` | `0x8008ABE8` | `0x02D10018` | `mult s6 s1` | `mult        $s6, $s1` | yes | reachable | **correct** |
| funcs_22.c:6133 | `evaluateSoundMacroCurveTable` | `0x8008AC60` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_22.c:6253 | `soundMacroSetVoiceVolume` | `0x8008AD04` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_22.c:6345 | `soundMacroSetVoiceVolume` | `0x8008AD7C` | `0x02F10018` | `mult s7 s1` | `mult        $s7, $s1` | yes | reachable | **correct** |
| funcs_22.c:6443 | `soundMacroSetVoiceVolume` | `0x8008ADF4` | `0x00650018` | `mult v1 a1` | `mult        $v1, $a1` | yes | reachable | **correct** |
| funcs_22.c:6660 | `soundMacroSetupVolumeRamp` | `0x8008AF1C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_22.c:6728 | `soundMacroSetupVolumeRamp` | `0x8008AF80` | `0x03D10018` | `mult fp s1` | `mult        $fp, $s1` | yes | reachable | **correct** |
| funcs_22.c:6830 | `soundMacroSetupVolumeRamp` | `0x8008B000` | `0x00650018` | `mult v1 a1` | `mult        $v1, $a1` | yes | reachable | **correct** |
| funcs_22.c:7077 | `soundMacroPlayRandomKeyNote` | `0x8008B160` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_22.c:7089 | `soundMacroPlayRandomKeyNote` | `0x8008B178` | `0x00830019` | `multu a0 v1` | `multu       $a0, $v1` | yes | reachable | **correct** |
| funcs_22.c:7133 | `soundMacroPlayRandomKeyNote` | `0x8008B1C4` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_23.c:468 | `soundMacroPushEffectEvent` | `0x8008B31C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:651 | `seqCmdHandler40` | `0x8008B40C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:834 | `seqCmdHandler41` | `0x8008B4FC` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:1017 | `seqCmdHandler42` | `0x8008B5EC` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:1200 | `seqCmdHandler43` | `0x8008B6DC` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:1383 | `seqCmdHandler44` | `0x8008B7CC` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:1566 | `seqCmdHandler45` | `0x8008B8BC` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:1749 | `seqCmdHandler46` | `0x8008B9AC` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:3264 | `tickAudioChannel` | `0x8008C094` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_23.c:3795 | `tickAudioChannel` | `0x8008C354` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:4073 | `tickAudioChannel` | `0x8008C4A8` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_23.c:6243 | `tickAllAudioChannels` | `0x8008CF4C` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_23.c:6288 | `tickAllAudioChannels` | `0x8008CF98` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:6460 | `tickAllAudioChannels` | `0x8008D0A0` | `0x00850018` | `mult a0 a1` | `mult        $a0, $a1` | yes | reachable | **correct** |
| funcs_23.c:6470 | `tickAllAudioChannels` | `0x8008D0B4` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:6586 | `tickAllAudioChannels` | `0x8008D15C` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_23.c:6612 | `tickAllAudioChannels` | `0x8008D188` | `0x00500018` | `mult v0 s0` | `mult        $v0, $s0` | yes | reachable | **correct** |
| funcs_23.c:6631 | `tickAllAudioChannels` | `0x8008D1A8` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_23.c:6657 | `tickAllAudioChannels` | `0x8008D1D4` | `0x00500018` | `mult v0 s0` | `mult        $v0, $s0` | yes | reachable | **correct** |
| funcs_23.c:6770 | `tickAllAudioChannels` | `0x8008D274` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_23.c:6778 | `tickAllAudioChannels` | `0x8008D284` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_23.c:6850 | `tickAllAudioChannels` | `0x8008D2F4` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_23.c:6858 | `tickAllAudioChannels` | `0x8008D304` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_23.c:6880 | `tickAllAudioChannels` | `0x8008D32C` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_23.c:6938 | `tickAllAudioChannels` | `0x8008D380` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_23.c:6973 | `tickAllAudioChannels` | `0x8008D3B0` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_23.c:7031 | `tickAllAudioChannels` | `0x8008D40C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:7087 | `tickAllAudioChannels` | `0x8008D464` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:7238 | `tickAllAudioChannels` | `0x8008D55C` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_23.c:7250 | `tickAllAudioChannels` | `0x8008D574` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_23.c:7299 | `tickAllAudioChannels` | `0x8008D5CC` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:7318 | `tickAllAudioChannels` | `0x8008D5E8` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_23.c:7348 | `tickAllAudioChannels` | `0x8008D610` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:7488 | `tickAllAudioChannels` | `0x8008D6C8` | `0x00520018` | `mult v0 s2` | `mult        $v0, $s2` | yes | reachable | **correct** |
| funcs_23.c:7595 | `tickAllAudioChannels` | `0x8008D75C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:7819 | `tickAllAudioChannels` | `0x8008D894` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:12358 | `buildSongTempoSchedule` | `0x8008EEF4` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:12366 | `buildSongTempoSchedule` | `0x8008EF04` | `0x00620019` | `multu v1 v0` | `multu       $v1, $v0` | yes | reachable | **correct** |
| funcs_23.c:12376 | `buildSongTempoSchedule` | `0x8008EF18` | `0x02220019` | `multu s1 v0` | `multu       $s1, $v0` | yes | reachable | **correct** |
| funcs_23.c:12479 | `buildSongTempoSchedule` | `0x8008EFB0` | `0x01020018` | `mult t0 v0` | `mult        $t0, $v0` | yes | reachable | **correct** |
| funcs_23.c:12487 | `buildSongTempoSchedule` | `0x8008EFC0` | `0x00470019` | `multu v0 a3` | `multu       $v0, $a3` | yes | reachable | **correct** |
| funcs_23.c:13071 | `allocateSongChannelArray` | `0x8008F254` | `0x00C30018` | `mult a2 v1` | `mult        $a2, $v1` | yes | reachable | **correct** |
| funcs_23.c:13340 | `setupSongRenderBuffers` | `0x8008F398` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_23.c:13348 | `setupSongRenderBuffers` | `0x8008F3A8` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_23.c:13552 | `setupSongRenderBuffers` | `0x8008F4B0` | `0x00900018` | `mult a0 s0` | `mult        $a0, $s0` | yes | reachable | **correct** |
| funcs_24.c:1284 | `fillSampleStreamRange` | `0x8008FCB4` | `0x00620019` | `multu v1 v0` | `multu       $v1, $v0` | yes | reachable | **correct** |
| funcs_24.c:2330 | `musyxRenderVoiceSamples` | `0x8008FFE8` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_24.c:4009 | `musyxRenderVoiceSamples` | `0x8009078C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_24.c:4975 | `musyxKeyOnVoice` | `0x80090B18` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_24.c:5237 | `musyxKeyOnVoice` | `0x80090C10` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_24.c:6695 | `musyxBuildVoiceCommandList` | `0x80091184` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_24.c:8421 | `initN64RspMixer` | `0x8009195C` | `0x00660018` | `mult v1 a2` | `mult        $v1, $a2` | yes | reachable | **correct** |
| funcs_24.c:8429 | `initN64RspMixer` | `0x8009196C` | `0x00620019` | `multu v1 v0` | `multu       $v1, $v0` | yes | reachable | **correct** |
| funcs_24.c:8439 | `initN64RspMixer` | `0x80091980` | `0x00620019` | `multu v1 v0` | `multu       $v1, $v0` | yes | reachable | **correct** |
| funcs_24.c:11708 | `resampleVoicePointTableSamples` | `0x800926EC` | `0x01C20018` | `mult t6 v0` | `mult        $t6, $v0` | yes | reachable | **correct** |
| funcs_24.c:11904 | `interpolatePointTableSamplesToPackedWord` | `0x800927E0` | `0x01C20018` | `mult t6 v0` | `mult        $t6, $v0` | yes | reachable | **correct** |
| funcs_24.c:11954 | `interpolatePointTableSamplesToPackedWord` | `0x80092828` | `0x01C20018` | `mult t6 v0` | `mult        $t6, $v0` | yes | reachable | **correct** |
| funcs_24.c:12004 | `interpolatePointTableSamplesToPackedWord` | `0x80092870` | `0x01C20018` | `mult t6 v0` | `mult        $t6, $v0` | yes | reachable | **correct** |
| funcs_24.c:12056 | `interpolatePointTableSamplesToPackedWord` | `0x800928BC` | `0x01C20018` | `mult t6 v0` | `mult        $t6, $v0` | yes | reachable | **correct** |
| funcs_24.c:12206 | `resampleVoiceLutSamples` | `0x80092990` | `0x01C20018` | `mult t6 v0` | `mult        $t6, $v0` | yes | reachable | **correct** |
| funcs_24.c:12408 | `interpolateLutSamplesToPackedWord` | `0x80092A90` | `0x01C20018` | `mult t6 v0` | `mult        $t6, $v0` | yes | reachable | **correct** |
| funcs_24.c:12464 | `interpolateLutSamplesToPackedWord` | `0x80092AE4` | `0x01C20018` | `mult t6 v0` | `mult        $t6, $v0` | yes | reachable | **correct** |
| funcs_24.c:12520 | `interpolateLutSamplesToPackedWord` | `0x80092B38` | `0x01C20018` | `mult t6 v0` | `mult        $t6, $v0` | yes | reachable | **correct** |
| funcs_24.c:12578 | `interpolateLutSamplesToPackedWord` | `0x80092B90` | `0x01C20018` | `mult t6 v0` | `mult        $t6, $v0` | yes | reachable | **correct** |
| funcs_24.c:12864 | `interpolateConstantSamplesToPackedWord` | `0x80092D14` | `0x01C80018` | `mult t6 t0` | `mult        $t6, $t0` | yes | reachable | **correct** |
| funcs_24.c:12920 | `interpolateConstantSamplesToPackedWord` | `0x80092D68` | `0x01C80018` | `mult t6 t0` | `mult        $t6, $t0` | yes | reachable | **correct** |
| funcs_24.c:12976 | `interpolateConstantSamplesToPackedWord` | `0x80092DBC` | `0x01C80018` | `mult t6 t0` | `mult        $t6, $t0` | yes | reachable | **correct** |
| funcs_24.c:13032 | `interpolateConstantSamplesToPackedWord` | `0x80092E10` | `0x01C80018` | `mult t6 t0` | `mult        $t6, $t0` | yes | reachable | **correct** |
| funcs_24.c:13356 | `packFourLutResampledSamples` | `0x80092FD0` | `0x01C80018` | `mult t6 t0` | `mult        $t6, $t0` | yes | reachable | **correct** |
| funcs_24.c:13424 | `packFourLutResampledSamples` | `0x8009303C` | `0x01C80018` | `mult t6 t0` | `mult        $t6, $t0` | yes | reachable | **correct** |
| funcs_24.c:13492 | `packFourLutResampledSamples` | `0x800930A8` | `0x01C80018` | `mult t6 t0` | `mult        $t6, $t0` | yes | reachable | **correct** |
| funcs_24.c:13560 | `packFourLutResampledSamples` | `0x80093114` | `0x01C80018` | `mult t6 t0` | `mult        $t6, $t0` | yes | reachable | **correct** |
| funcs_25.c:301 | `musyxComputeNotePlaybackRate` | `0x80093EE8` | `0x01090019` | `multu t0 t1` | `multu       $t0, $t1` | yes | reachable | **correct** |
| funcs_25.c:363 | `scaleFixedPointByRatioA` | `0x80093F44` | `0x00880019` | `multu a0 t0` | `multu       $a0, $t0` | yes | reachable | **correct** |
| funcs_25.c:387 | `scaleFixedPointByRatioB` | `0x80093F68` | `0x00880019` | `multu a0 t0` | `multu       $a0, $t0` | yes | reachable | **correct** |
| funcs_25.c:417 | `scaleByPitchTableA` | `0x80093F98` | `0x00880019` | `multu a0 t0` | `multu       $a0, $t0` | yes | reachable | **correct** |
| funcs_25.c:447 | `scaleByPitchTableB` | `0x80093FC8` | `0x00880019` | `multu a0 t0` | `multu       $a0, $t0` | yes | reachable | **correct** |
| funcs_25.c:487 | `computeNoteRatePairFromTableA` | `0x8009400C` | `0x00E10019` | `multu a3 at` | `multu       $a3, $at` | yes | reachable | **correct** |
| funcs_25.c:509 | `computeNoteRatePairFromTableA` | `0x80094034` | `0x00E10019` | `multu a3 at` | `multu       $a3, $at` | yes | reachable | **correct** |
| funcs_25.c:557 | `computeNoteRatePairFromTableB` | `0x80094084` | `0x00E10019` | `multu a3 at` | `multu       $a3, $at` | yes | reachable | **correct** |
| funcs_25.c:579 | `computeNoteRatePairFromTableB` | `0x800940AC` | `0x00E10019` | `multu a3 at` | `multu       $a3, $at` | yes | reachable | **correct** |
| funcs_25.c:5497 | `updateSongTempoTickRate` | `0x800956A8` | `0x00430019` | `multu v0 v1` | `multu       $v0, $v1` | yes | unreachable | **correct** |
| funcs_25.c:5505 | `updateSongTempoTickRate` | `0x800956B8` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | unreachable | **correct** |
| funcs_25.c:5513 | `updateSongTempoTickRate` | `0x800956C8` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | unreachable | **correct** |
| funcs_25.c:10472 | `tickAllActiveSongs` | `0x80096E80` | `0x00430019` | `multu v0 v1` | `multu       $v0, $v1` | yes | reachable | **correct** |
| funcs_25.c:10480 | `tickAllActiveSongs` | `0x80096E90` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_25.c:10488 | `tickAllActiveSongs` | `0x80096EA0` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_26.c:12194 | `allocAndConfigureNewVoice` | `0x8009B148` | `0x00620019` | `multu v1 v0` | `multu       $v1, $v0` | yes | reachable | **correct** |
| funcs_26.c:12214 | `allocAndConfigureNewVoice` | `0x8009B16C` | `0x00430019` | `multu v0 v1` | `multu       $v0, $v1` | yes | reachable | **correct** |
| funcs_27.c:4949 | `filterVoiceSampleBlock` | `0x8009D84C` | `0x01AC0018` | `mult t5 t4` | `mult        $t5, $t4` | yes | reachable | **correct** |
| funcs_27.c:5126 | `applyVoiceDelayFilter` | `0x8009D944` | `0x01280018` | `mult t1 t0` | `mult        $t1, $t0` | yes | reachable | **correct** |
| funcs_27.c:5186 | `runVoiceLatticeFilter` | `0x8009D990` | `0x02ED0018` | `mult s7 t5` | `mult        $s7, $t5` | yes | reachable | **correct** |
| funcs_27.c:5198 | `runVoiceLatticeFilter` | `0x8009D9A8` | `0x02CD0018` | `mult s6 t5` | `mult        $s6, $t5` | yes | reachable | **correct** |
| funcs_27.c:5208 | `runVoiceLatticeFilter` | `0x8009D9BC` | `0x01AA0018` | `mult t5 t2` | `mult        $t5, $t2` | yes | reachable | **correct** |
| funcs_27.c:5222 | `runVoiceLatticeFilter` | `0x8009D9D8` | `0x02AD0018` | `mult s5 t5` | `mult        $s5, $t5` | yes | reachable | **correct** |
| funcs_27.c:5232 | `runVoiceLatticeFilter` | `0x8009D9EC` | `0x01AA0018` | `mult t5 t2` | `mult        $t5, $t2` | yes | reachable | **correct** |
| funcs_27.c:5244 | `runVoiceLatticeFilter` | `0x8009DA04` | `0x028D0018` | `mult s4 t5` | `mult        $s4, $t5` | yes | reachable | **correct** |
| funcs_27.c:5254 | `runVoiceLatticeFilter` | `0x8009DA18` | `0x01AA0018` | `mult t5 t2` | `mult        $t5, $t2` | yes | reachable | **correct** |
| funcs_27.c:5268 | `runVoiceLatticeFilter` | `0x8009DA34` | `0x026D0018` | `mult s3 t5` | `mult        $s3, $t5` | yes | reachable | **correct** |
| funcs_27.c:5278 | `runVoiceLatticeFilter` | `0x8009DA48` | `0x01AA0018` | `mult t5 t2` | `mult        $t5, $t2` | yes | reachable | **correct** |
| funcs_27.c:5290 | `runVoiceLatticeFilter` | `0x8009DA60` | `0x024D0018` | `mult s2 t5` | `mult        $s2, $t5` | yes | reachable | **correct** |
| funcs_27.c:5300 | `runVoiceLatticeFilter` | `0x8009DA74` | `0x01AA0018` | `mult t5 t2` | `mult        $t5, $t2` | yes | reachable | **correct** |
| funcs_27.c:5314 | `runVoiceLatticeFilter` | `0x8009DA90` | `0x022D0018` | `mult s1 t5` | `mult        $s1, $t5` | yes | reachable | **correct** |
| funcs_27.c:5324 | `runVoiceLatticeFilter` | `0x8009DAA4` | `0x01AA0018` | `mult t5 t2` | `mult        $t5, $t2` | yes | reachable | **correct** |
| funcs_27.c:5336 | `runVoiceLatticeFilter` | `0x8009DABC` | `0x020D0018` | `mult s0 t5` | `mult        $s0, $t5` | yes | reachable | **correct** |
| funcs_27.c:5346 | `runVoiceLatticeFilter` | `0x8009DAD0` | `0x01AA0018` | `mult t5 t2` | `mult        $t5, $t2` | yes | reachable | **correct** |
| funcs_27.c:5360 | `runVoiceLatticeFilter` | `0x8009DAEC` | `0x00270018` | `mult at a3` | `mult        $at, $a3` | yes | reachable | **correct** |
| funcs_27.c:11330 | `audioCompandS16` | `0x8009FD5C` | `0x00000018` | `mult zero zero` | `mult        $zero, $zero` | yes | unreachable | **correct** |
| funcs_27.c:11334 | `audioCompandS16` | `0x8009FD64` | `0x00000019` | `multu zero zero` | `multu       $zero, $zero` | yes | unreachable | **correct** |
| funcs_27.c:11598 | `audioCompandS16` | `0x8009FF64` | `0x00000058` | `mult zero zero` | `.word       0x00000058                   # mult        $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:11602 | `audioCompandS16` | `0x8009FF6C` | `0x00000059` | `multu zero zero` | `.word       0x00000059                   # multu       $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:11687 | `audioCompandS16` | `0x800A0014` | `0x00180019` | `multu zero t8` | `multu       $zero, $t8` | yes | unreachable | **correct** |
| funcs_27.c:11775 | `audioCompandS16` | `0x800A00BC` | `0x00580059` | `multu v0 t8` | `.word       0x00580059                   # multu       $v0, $t8 # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:11881 | `audioCompandS16` | `0x800A0190` | `0x00970098` | `mult a0 s7` | `.word       0x00970098                   # mult        $a0, $s7 # 00000080 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:11883 | `audioCompandS16` | `0x800A0194` | `0x00000099` | `multu zero zero` | `.word       0x00000099                   # multu       $zero, $zero # 00000080 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:11963 | `audioCompandS16` | `0x800A022C` | `0x00D700D8` | `mult a2 s7` | `.word       0x00D700D8                   # mult        $a2, $s7 # 000000C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12041 | `audioCompandS16` | `0x800A02C0` | `0x01180119` | `multu t0 t8` | `.word       0x01180119                   # multu       $t0, $t8 # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12251 | `audioCompandS16` | `0x800A0464` | `0x01970198` | `mult t4 s7` | `.word       0x01970198                   # mult        $t4, $s7 # 00000180 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12341 | `audioCompandS16` | `0x800A0510` | `0x000001D8` | `mult zero zero` | `.word       0x000001D8                   # mult        $zero, $zero # 000001C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12343 | `audioCompandS16` | `0x800A0514` | `0x000001D9` | `multu zero zero` | `.word       0x000001D9                   # multu       $zero, $zero # 000001C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12419 | `audioCompandS16` | `0x800A05AC` | `0x02180219` | `multu s0 t8` | `.word       0x02180219                   # multu       $s0, $t8 # 00000200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12602 | `audioCompandS16` | `0x800A06F0` | `0x00000019` | `multu zero zero` | `multu       $zero, $zero` | yes | unreachable | **correct** |
| funcs_27.c:12677 | `audioCompandS16` | `0x800A0780` | `0x00000019` | `multu zero zero` | `multu       $zero, $zero` | yes | unreachable | **correct** |
| funcs_27.c:12774 | `audioCompandS16` | `0x800A0840` | `0x00000099` | `multu zero zero` | `.word       0x00000099                   # multu       $zero, $zero # 00000080 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:12934 | `audioCompandS16` | `0x800A0964` | `0x02260258` | `mult s1 a2` | `.word       0x02260258                   # mult        $s1, $a2 # 00000240 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:13882 | `audioCompandS16` | `0x800A0FC4` | `0x01520159` | `multu t2 s2` | `.word       0x01520159                   # multu       $t2, $s2 # 00000140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:13958 | `audioCompandS16` | `0x800A1054` | `0x03120318` | `mult t8 s2` | `.word       0x03120318                   # mult        $t8, $s2 # 00000300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:98958 | `audioCompandS16` | `0x800A17D0` | `0x01810198` | `mult t4 at` | `.word       0x01810198                   # mult        $t4, $at # 00000180 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100229 | `audioCompandS16` | `0x800A1DAC` | `0x00003F18` | `mult zero zero` | `.word       0x00003F18                   # mult        $zero, $zero # 00003F00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100269 | `audioCompandS16` | `0x800A1DEC` | `0x00004419` | `multu zero zero` | `.word       0x00004419                   # multu       $zero, $zero # 00004400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100307 | `audioCompandS16` | `0x800A1E28` | `0x00004218` | `mult zero zero` | `.word       0x00004218                   # mult        $zero, $zero # 00004200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100347 | `audioCompandS16` | `0x800A1E68` | `0x00004819` | `multu zero zero` | `.word       0x00004819                   # multu       $zero, $zero # 00004800 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100385 | `audioCompandS16` | `0x800A1EA4` | `0x00004418` | `mult zero zero` | `.word       0x00004418                   # mult        $zero, $zero # 00004400 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100425 | `audioCompandS16` | `0x800A1EE4` | `0x00004A19` | `multu zero zero` | `.word       0x00004A19                   # multu       $zero, $zero # 00004A00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100464 | `audioCompandS16` | `0x800A1F20` | `0x00004318` | `mult zero zero` | `.word       0x00004318                   # mult        $zero, $zero # 00004300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100504 | `audioCompandS16` | `0x800A1F60` | `0x00004A19` | `multu zero zero` | `.word       0x00004A19                   # multu       $zero, $zero # 00004A00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100576 | `audioCompandS16` | `0x800A1FD0` | `0x00000A18` | `mult zero zero` | `.word       0x00000A18                   # mult        $zero, $zero # 00000A00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100578 | `audioCompandS16` | `0x800A1FD4` | `0x00001E18` | `mult zero zero` | `.word       0x00001E18                   # mult        $zero, $zero # 00001E00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100580 | `audioCompandS16` | `0x800A1FD8` | `0x00003218` | `mult zero zero` | `.word       0x00003218                   # mult        $zero, $zero # 00003200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100582 | `audioCompandS16` | `0x800A1FDC` | `0x00004618` | `mult zero zero` | `.word       0x00004618                   # mult        $zero, $zero # 00004600 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100616 | `audioCompandS16` | `0x800A2010` | `0x00000B19` | `multu zero zero` | `.word       0x00000B19                   # multu       $zero, $zero # 00000B00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100618 | `audioCompandS16` | `0x800A2014` | `0x00002119` | `multu zero zero` | `.word       0x00002119                   # multu       $zero, $zero # 00002100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100620 | `audioCompandS16` | `0x800A2018` | `0x00003719` | `multu zero zero` | `.word       0x00003719                   # multu       $zero, $zero # 00003700 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:100622 | `audioCompandS16` | `0x800A201C` | `0x00004D19` | `multu zero zero` | `.word       0x00004D19                   # multu       $zero, $zero # 00004D00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102867 | `audioCompandS16` | `0x800A2DAC` | `0x006FFA58` | `mult v1 t7` | `.word       0x006FFA58                   # mult        $v1, $t7 # 0000FA40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102907 | `audioCompandS16` | `0x800A2DEC` | `0x007B2D58` | `mult v1 k1` | `.word       0x007B2D58                   # mult        $v1, $k1 # 00002D40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102948 | `audioCompandS16` | `0x800A2E28` | `0x00756E58` | `mult v1 s5` | `.word       0x00756E58                   # mult        $v1, $s5 # 00006E40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102950 | `audioCompandS16` | `0x800A2E2C` | `0x00877F58` | `mult a0 a3` | `.word       0x00877F58                   # mult        $a0, $a3 # 00007F40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102988 | `audioCompandS16` | `0x800A2E68` | `0x00812C58` | `mult a0 at` | `.word       0x00812C58                   # mult        $a0, $at # 00002C40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:102990 | `audioCompandS16` | `0x800A2E6C` | `0x00950B58` | `mult a0 s5` | `.word       0x00950B58                   # mult        $a0, $s5 # 00000B40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103027 | `audioCompandS16` | `0x800A2EA4` | `0x00783B58` | `mult v1 t8` | `.word       0x00783B58                   # mult        $v1, $t8 # 00003B40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103029 | `audioCompandS16` | `0x800A2EA8` | `0x008E1758` | `mult a0 t6` | `.word       0x008E1758                   # mult        $a0, $t6 # 00001740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103031 | `audioCompandS16` | `0x800A2EAC` | `0x00A3F358` | `mult a1 v1` | `.word       0x00A3F358                   # mult        $a1, $v1 # 0000F340 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103067 | `audioCompandS16` | `0x800A2EE4` | `0x00843F58` | `mult a0 a0` | `.word       0x00843F58                   # mult        $a0, $a0 # 00003F40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103069 | `audioCompandS16` | `0x800A2EE8` | `0x009C4B58` | `mult a0 gp` | `.word       0x009C4B58                   # mult        $a0, $gp # 00004B40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103071 | `audioCompandS16` | `0x800A2EEC` | `0x00B45658` | `mult a1 s4` | `.word       0x00B45658                   # mult        $a1, $s4 # 00005640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103105 | `audioCompandS16` | `0x800A2F20` | `0x00770758` | `mult v1 s7` | `.word       0x00770758                   # mult        $v1, $s7 # 00000740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103107 | `audioCompandS16` | `0x800A2F24` | `0x00917A58` | `mult a0 s1` | `.word       0x00917A58                   # mult        $a0, $s1 # 00007A40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103110 | `audioCompandS16` | `0x800A2F28` | `0x00ABEE58` | `mult a1 t3` | `.word       0x00ABEE58                   # mult        $a1, $t3 # 0000EE40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103112 | `audioCompandS16` | `0x800A2F2C` | `0x00C66158` | `mult a2 a2` | `.word       0x00C66158                   # mult        $a2, $a2 # 00006140 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103146 | `audioCompandS16` | `0x800A2F60` | `0x0082EE58` | `mult a0 v0` | `.word       0x0082EE58                   # mult        $a0, $v0 # 0000EE40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103148 | `audioCompandS16` | `0x800A2F64` | `0x00A00658` | `mult a1 zero` | `.word       0x00A00658                   # mult        $a1, $zero # 00000640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103150 | `audioCompandS16` | `0x800A2F68` | `0x00BD1F58` | `mult a1 sp` | `.word       0x00BD1F58                   # mult        $a1, $sp # 00001F40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103152 | `audioCompandS16` | `0x800A2F6C` | `0x00DA3758` | `mult a2 k0` | `.word       0x00DA3758                   # mult        $a2, $k0 # 00003740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103187 | `audioCompandS16` | `0x800A2FA0` | `0x008FFE58` | `mult a0 t7` | `.word       0x008FFE58                   # mult        $a0, $t7 # 0000FE40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103189 | `audioCompandS16` | `0x800A2FA4` | `0x00AFFD58` | `mult a1 t7` | `.word       0x00AFFD58                   # mult        $a1, $t7 # 0000FD40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103191 | `audioCompandS16` | `0x800A2FA8` | `0x00CFFD58` | `mult a2 t7` | `.word       0x00CFFD58                   # mult        $a2, $t7 # 0000FD40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:103193 | `audioCompandS16` | `0x800A2FAC` | `0x00EFFC58` | `mult a3 t7` | `.word       0x00EFFC58                   # mult        $a3, $t7 # 0000FC40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104215 | `audioCompandS16` | `0x800A32D0` | `0x00006598` | `mult zero zero` | `.word       0x00006598                   # mult        $zero, $zero # 00006580 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104313 | `audioCompandS16` | `0x800A3390` | `0x00000659` | `multu zero zero` | `.word       0x00000659                   # multu       $zero, $zero # 00000640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104383 | `audioCompandS16` | `0x800A341C` | `0x001046D8` | `mult zero s0` | `.word       0x001046D8                   # mult        $zero, $s0 # 000046C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104441 | `audioCompandS16` | `0x800A3490` | `0x0010B558` | `mult zero s0` | `.word       0x0010B558                   # mult        $zero, $s0 # 0000B540 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104515 | `audioCompandS16` | `0x800A3524` | `0x00114698` | `mult zero s1` | `.word       0x00114698                   # mult        $zero, $s1 # 00004680 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104525 | `audioCompandS16` | `0x800A3538` | `0x00115A99` | `multu zero s1` | `.word       0x00115A99                   # multu       $zero, $s1 # 00005A80 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104644 | `audioCompandS16` | `0x800A3620` | `0x00124959` | `multu zero s2` | `.word       0x00124959                   # multu       $zero, $s2 # 00004940 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104670 | `audioCompandS16` | `0x800A3654` | `0x00128098` | `mult zero s2` | `.word       0x00128098                   # mult        $zero, $s2 # 00008080 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104730 | `audioCompandS16` | `0x800A36CC` | `0x00130298` | `mult zero s3` | `.word       0x00130298                   # mult        $zero, $s3 # 00000280 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104947 | `audioCompandS16` | `0x800A3870` | `0x0014E658` | `mult zero s4` | `.word       0x0014E658                   # mult        $zero, $s4 # 0000E640 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:104953 | `audioCompandS16` | `0x800A387C` | `0x0014F4D9` | `multu zero s4` | `.word       0x0014F4D9                   # multu       $zero, $s4 # 0000F4C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105013 | `audioCompandS16` | `0x800A38F4` | `0x00158818` | `mult zero s5` | `.word       0x00158818                   # mult        $zero, $s5 # 00008800 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105128 | `audioCompandS16` | `0x800A39D4` | `0x0016A5D9` | `multu zero s6` | `.word       0x0016A5D9                   # multu       $zero, $s6 # 0000A5C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105142 | `audioCompandS16` | `0x800A39F0` | `0x0016CA98` | `mult zero s6` | `.word       0x0016CA98                   # mult        $zero, $s6 # 0000CA80 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105215 | `audioCompandS16` | `0x800A3A7C` | `0x001785D8` | `mult zero s7` | `.word       0x001785D8                   # mult        $zero, $s7 # 000085C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105339 | `audioCompandS16` | `0x800A3B54` | `0x0018B299` | `multu zero t8` | `.word       0x0018B299                   # multu       $zero, $t8 # 0000B280 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105533 | `audioCompandS16` | `0x800A3CD4` | `0x001AEED9` | `multu zero k0` | `.word       0x001AEED9                   # multu       $zero, $k0 # 0000EEC0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105791 | `audioCompandS16` | `0x800A3EB0` | `0x001DFC99` | `multu zero sp` | `.word       0x001DFC99                   # multu       $zero, $sp # 0000FC80 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105909 | `audioCompandS16` | `0x800A3F94` | `0x001F91D9` | `multu zero ra` | `.word       0x001F91D9                   # multu       $zero, $ra # 000091C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:105986 | `audioCompandS16` | `0x800A4028` | `0x000FB319` | `multu zero t7` | `.word       0x000FB319                   # multu       $zero, $t7 # 0000B300 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106040 | `audioCompandS16` | `0x800A4094` | `0x000F5258` | `mult zero t7` | `.word       0x000F5258                   # mult        $zero, $t7 # 00005240 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106062 | `audioCompandS16` | `0x800A40C0` | `0x000F2B98` | `mult zero t7` | `.word       0x000F2B98                   # mult        $zero, $t7 # 00002B80 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106064 | `audioCompandS16` | `0x800A40C4` | `0x000F2818` | `mult zero t7` | `.word       0x000F2818                   # mult        $zero, $t7 # 00002800 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106068 | `audioCompandS16` | `0x800A40CC` | `0x000F2118` | `mult zero t7` | `.word       0x000F2118                   # mult        $zero, $t7 # 00002100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106242 | `audioCompandS16` | `0x800A4224` | `0x000DFFD8` | `mult zero t5` | `.word       0x000DFFD8                   # mult        $zero, $t5 # 0000FFC0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106260 | `audioCompandS16` | `0x800A4248` | `0x000DE2D9` | `multu zero t5` | `.word       0x000DE2D9                   # multu       $zero, $t5 # 0000E2C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106270 | `audioCompandS16` | `0x800A425C` | `0x000DD2D8` | `mult zero t5` | `.word       0x000DD2D8                   # mult        $zero, $t5 # 0000D2C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106335 | `audioCompandS16` | `0x800A42DC` | `0x000D6E19` | `multu zero t5` | `.word       0x000D6E19                   # multu       $zero, $t5 # 00006E00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106379 | `audioCompandS16` | `0x800A432C` | `0x000D3098` | `mult zero t5` | `.word       0x000D3098                   # mult        $zero, $t5 # 00003080 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106452 | `audioCompandS16` | `0x800A43B8` | `0x000CC799` | `multu zero t4` | `.word       0x000CC799                   # multu       $zero, $t4 # 0000C780 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106521 | `audioCompandS16` | `0x800A443C` | `0x000C6798` | `mult zero t4` | `.word       0x000C6798                   # mult        $zero, $t4 # 00006780 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106536 | `audioCompandS16` | `0x800A4458` | `0x000C5399` | `multu zero t4` | `.word       0x000C5399                   # multu       $zero, $t4 # 00005380 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106711 | `audioCompandS16` | `0x800A45A4` | `0x000B6FD8` | `mult zero t3` | `.word       0x000B6FD8                   # mult        $zero, $t3 # 00006FC0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106869 | `audioCompandS16` | `0x800A46BC` | `0x000ABC98` | `mult zero t2` | `.word       0x000ABC98                   # mult        $zero, $t2 # 0000BC80 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106927 | `audioCompandS16` | `0x800A4724` | `0x000A7CD8` | `mult zero t2` | `.word       0x000A7CD8                   # mult        $zero, $t2 # 00007CC0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106939 | `audioCompandS16` | `0x800A473C` | `0x000A6E58` | `mult zero t2` | `.word       0x000A6E58                   # mult        $zero, $t2 # 00006E40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:106983 | `audioCompandS16` | `0x800A4794` | `0x000A39D9` | `multu zero t2` | `.word       0x000A39D9                   # multu       $zero, $t2 # 000039C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107081 | `audioCompandS16` | `0x800A4858` | `0x0009C899` | `multu zero t1` | `.word       0x0009C899                   # multu       $zero, $t1 # 0000C880 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107101 | `audioCompandS16` | `0x800A4880` | `0x0009B218` | `mult zero t1` | `.word       0x0009B218                   # mult        $zero, $t1 # 0000B200 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107137 | `audioCompandS16` | `0x800A48C8` | `0x00098A19` | `multu zero t1` | `.word       0x00098A19                   # multu       $zero, $t1 # 00008A00 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107239 | `audioCompandS16` | `0x800A4990` | `0x00091E58` | `mult zero t1` | `.word       0x00091E58                   # mult        $zero, $t1 # 00001E40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107315 | `audioCompandS16` | `0x800A4A14` | `0x0008D9D8` | `mult zero t0` | `.word       0x0008D9D8                   # mult        $zero, $t0 # 0000D9C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107352 | `audioCompandS16` | `0x800A4A58` | `0x0008B758` | `mult zero t0` | `.word       0x0008B758                   # mult        $zero, $t0 # 0000B740 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107437 | `audioCompandS16` | `0x800A4B00` | `0x00086458` | `mult zero t0` | `.word       0x00086458                   # mult        $zero, $t0 # 00006440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107441 | `audioCompandS16` | `0x800A4B00` | `0x00086458` | `mult zero t0` | `.word       0x00086458                   # mult        $zero, $t0 # 00006440 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107500 | `audioCompandS16` | `0x800A4B74` | `0x00082CD8` | `mult zero t0` | `.word       0x00082CD8                   # mult        $zero, $t0 # 00002CC0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_27.c:107546 | `audioCompandS16` | `0x800A4BD0` | `0x000801D9` | `multu zero t0` | `.word       0x000801D9                   # multu       $zero, $t0 # 000001C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_28.c:26329 | `buildCutsceneGradientBuffers` | `0x800AC66C` | `0x00530019` | `multu v0 s3` | `multu       $v0, $s3` | yes | reachable | **correct** |
| funcs_28.c:27649 | `spawnNpcBurstAlongSegment` | `0x800ACD00` | `0x00A30018` | `mult a1 v1` | `mult        $a1, $v1` | yes | reachable | **correct** |
| funcs_28.c:32817 | `updateCinematicCameraStateMachine` | `0x800AD7F8` | `0x46220001` | `—` | `mult        $a0, $v0` | NO | reachable | **ELF/annotation mismatch** |
| funcs_28.c:38247 | `loadBackdropAsset` | `0x800AE0F8` | `0x00C20018` | `mult a2 v0` | `mult        $a2, $v0` | yes | reachable | **correct** |
| funcs_28.c:38506 | `loadBackdropAsset` | `0x800AE24C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_28.c:38514 | `loadBackdropAsset` | `0x800AE25C` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_28.c:38693 | `loadBackdropAsset` | `0x800AE35C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_28.c:38701 | `loadBackdropAsset` | `0x800AE36C` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_28.c:38709 | `loadBackdropAsset` | `0x800AE37C` | `0x01850018` | `mult t4 a1` | `mult        $t4, $a1` | yes | reachable | **correct** |
| funcs_28.c:38717 | `loadBackdropAsset` | `0x800AE38C` | `0x02220018` | `mult s1 v0` | `mult        $s1, $v0` | yes | reachable | **correct** |
| funcs_28.c:38734 | `loadBackdropAsset` | `0x800AE3A4` | `0x02060018` | `mult s0 a2` | `mult        $s0, $a2` | yes | reachable | **correct** |
| funcs_28.c:38742 | `loadBackdropAsset` | `0x800AE3B4` | `0x01830018` | `mult t4 v1` | `mult        $t4, $v1` | yes | reachable | **correct** |
| funcs_28.c:38750 | `loadBackdropAsset` | `0x800AE3C4` | `0x00C30018` | `mult a2 v1` | `mult        $a2, $v1` | yes | reachable | **correct** |
| funcs_28.c:38760 | `loadBackdropAsset` | `0x800AE3D8` | `0x02020018` | `mult s0 v0` | `mult        $s0, $v0` | yes | reachable | **correct** |
| funcs_28.c:38768 | `loadBackdropAsset` | `0x800AE3E8` | `0x01830018` | `mult t4 v1` | `mult        $t4, $v1` | yes | reachable | **correct** |
| funcs_28.c:41114 | `initCinematicSceneAssets` | `0x800AE67C` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_28.c:41200 | `initCinematicSceneAssets` | `0x800AE6E4` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_28.c:41208 | `initCinematicSceneAssets` | `0x800AE6F4` | `0x01700018` | `mult t3 s0` | `mult        $t3, $s0` | yes | reachable | **correct** |
| funcs_29.c:15706 | `spawnSceneDebrisAndEffectCluster` | `0x800B066C` | `0x400CCCCD` | `—` | `mult        $a0, $v1` | NO | reachable | **ELF/annotation mismatch** |
| funcs_29.c:15821 | `spawnSceneDebrisAndEffectCluster` | `0x800B0704` | `0x0000000A` | `—` | `mult        $a0, $v1` | NO | reachable | **ELF/annotation mismatch** |
| funcs_29.c:17312 | `runScriptedCraftCinematicEvent` | `0x800B09C0` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_29.c:18988 | `runScriptedCraftCinematicEvent` | `0x800B116C` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_30.c:13759 | `buildFormatMessageGlyphBuffer` | `0x800B27D4` | `0x00C20018` | `mult a2 v0` | `mult        $a2, $v0` | yes | reachable | **correct** |
| funcs_30.c:14194 | `buildFormatMessageGlyphBuffer` | `0x800B2A08` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_30.c:14202 | `buildFormatMessageGlyphBuffer` | `0x800B2A18` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_30.c:14663 | `allocFormatTextElement` | `0x800B2C64` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_30.c:15136 | `loadNamedTextureDescriptor` | `0x800B2ED4` | `0x00C20018` | `mult a2 v0` | `mult        $a2, $v0` | yes | reachable | **correct** |
| funcs_30.c:15395 | `loadNamedTextureDescriptor` | `0x800B3028` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_30.c:15403 | `loadNamedTextureDescriptor` | `0x800B3038` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_30.c:15582 | `loadNamedTextureDescriptor` | `0x800B3138` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_30.c:15590 | `loadNamedTextureDescriptor` | `0x800B3148` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_30.c:15598 | `loadNamedTextureDescriptor` | `0x800B3158` | `0x01850018` | `mult t4 a1` | `mult        $t4, $a1` | yes | reachable | **correct** |
| funcs_30.c:15606 | `loadNamedTextureDescriptor` | `0x800B3168` | `0x02220018` | `mult s1 v0` | `mult        $s1, $v0` | yes | reachable | **correct** |
| funcs_30.c:15623 | `loadNamedTextureDescriptor` | `0x800B3180` | `0x02060018` | `mult s0 a2` | `mult        $s0, $a2` | yes | reachable | **correct** |
| funcs_30.c:15631 | `loadNamedTextureDescriptor` | `0x800B3190` | `0x01830018` | `mult t4 v1` | `mult        $t4, $v1` | yes | reachable | **correct** |
| funcs_30.c:15639 | `loadNamedTextureDescriptor` | `0x800B31A0` | `0x00C30018` | `mult a2 v1` | `mult        $a2, $v1` | yes | reachable | **correct** |
| funcs_30.c:15649 | `loadNamedTextureDescriptor` | `0x800B31B4` | `0x02020018` | `mult s0 v0` | `mult        $s0, $v0` | yes | reachable | **correct** |
| funcs_30.c:15657 | `loadNamedTextureDescriptor` | `0x800B31C4` | `0x01830018` | `mult t4 v1` | `mult        $t4, $v1` | yes | reachable | **correct** |
| funcs_30.c:16131 | `allocTextRenderTarget` | `0x800B344C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_30.c:16217 | `allocTextRenderTarget` | `0x800B34B4` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_30.c:16229 | `allocTextRenderTarget` | `0x800B34C8` | `0x01700018` | `mult t3 s0` | `mult        $t3, $s0` | yes | reachable | **correct** |
| funcs_31.c:3515 | `menuControllerInput` | `0x800B4914` | `0x01030018` | `mult t0 v1` | `mult        $t0, $v1` | yes | reachable | **correct** |
| funcs_31.c:5533 | `menuControllerInput` | `0x800B5294` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_31.c:26835 | `buildHudAmmoReadout` | `0x800B83A8` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_31.c:26857 | `buildHudAmmoReadout` | `0x800B83C8` | `0x00660018` | `mult v1 a2` | `mult        $v1, $a2` | yes | reachable | **correct** |
| funcs_31.c:26906 | `buildHudAmmoReadout` | `0x800B8410` | `0x01050018` | `mult t0 a1` | `mult        $t0, $a1` | yes | reachable | **correct** |
| funcs_31.c:26935 | `buildHudAmmoReadout` | `0x800B8444` | `0x01050018` | `mult t0 a1` | `mult        $t0, $a1` | yes | reachable | **correct** |
| funcs_31.c:28139 | `readAccountForSelectionScreen` | `0x800B862C` | `0x00850018` | `mult a0 a1` | `mult        $a0, $a1` | yes | reachable | **correct** |
| funcs_31.c:28732 | `setMaterialTextureByName` | `0x800B8940` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_31.c:32260 | `cycleAccountLabelText` | `0x800B8E40` | `0x00B30018` | `mult a1 s3` | `mult        $a1, $s3` | yes | reachable | **correct** |
| funcs_31.c:32320 | `cycleAccountLabelText` | `0x800B8EA0` | `0x00930018` | `mult a0 s3` | `mult        $a0, $s3` | yes | reachable | **correct** |
| funcs_31.c:32344 | `cycleAccountLabelText` | `0x800B8ECC` | `0x02130018` | `mult s0 s3` | `mult        $s0, $s3` | yes | reachable | **correct** |
| funcs_31.c:35505 | `tickVwingEngineAudio` | `0x800B9A94` | `0x46020000` | `—` | `multu       $a3, $s0` | NO | reachable | **ELF/annotation mismatch** |
| funcs_31.c:35549 | `tickVwingEngineAudio` | `0x800B9ADC` | `0x44050000` | `—` | `multu       $a3, $s0` | NO | reachable | **ELF/annotation mismatch** |
| funcs_32.c:15918 | `integrateTieInterceptorPhysics` | `0x800BC518` | `0x00510018` | `mult v0 s1` | `mult        $v0, $s1` | yes | reachable | **correct** |
| funcs_32.c:16092 | `integrateTieInterceptorPhysics` | `0x800BC620` | `0x00510018` | `mult v0 s1` | `mult        $v0, $s1` | yes | reachable | **correct** |
| funcs_32.c:18158 | `playerTieInterceptorMainUpdate` | `0x800BC9CC` | `0x01340019` | `multu t1 s4` | `multu       $t1, $s4` | yes | reachable | **correct** |
| funcs_32.c:18200 | `playerTieInterceptorMainUpdate` | `0x800BCA08` | `0x00C30018` | `mult a2 v1` | `mult        $a2, $v1` | yes | reachable | **correct** |
| funcs_32.c:18378 | `playerTieInterceptorMainUpdate` | `0x800BCAD8` | `0x01340019` | `multu t1 s4` | `multu       $t1, $s4` | yes | reachable | **correct** |
| funcs_32.c:18473 | `playerTieInterceptorMainUpdate` | `0x800BCB38` | `0x01340019` | `multu t1 s4` | `multu       $t1, $s4` | yes | reachable | **correct** |
| funcs_32.c:18496 | `playerTieInterceptorMainUpdate` | `0x800BCB54` | `0x01340019` | `multu t1 s4` | `multu       $t1, $s4` | yes | reachable | **correct** |
| funcs_32.c:18529 | `playerTieInterceptorMainUpdate` | `0x800BCB7C` | `0x01340019` | `multu t1 s4` | `multu       $t1, $s4` | yes | reachable | **correct** |
| funcs_32.c:18816 | `playerTieInterceptorMainUpdate` | `0x800BCC98` | `0x01340019` | `multu t1 s4` | `multu       $t1, $s4` | yes | reachable | **correct** |
| funcs_32.c:18839 | `playerTieInterceptorMainUpdate` | `0x800BCCB4` | `0x01340019` | `multu t1 s4` | `multu       $t1, $s4` | yes | reachable | **correct** |
| funcs_32.c:18872 | `playerTieInterceptorMainUpdate` | `0x800BCCDC` | `0x01340019` | `multu t1 s4` | `multu       $t1, $s4` | yes | reachable | **correct** |
| funcs_32.c:19076 | `playerTieInterceptorMainUpdate` | `0x800BCDB8` | `0x01340019` | `multu t1 s4` | `multu       $t1, $s4` | yes | reachable | **correct** |
| funcs_33.c:3979 | `runMenuRandomBackdropScreen` | `0x800BF8FC` | `0x00C30018` | `mult a2 v1` | `mult        $a2, $v1` | yes | reachable | **correct** |
| funcs_33.c:10172 | `initHudStruct` | `0x800C1234` | `0x24040005` | `—` | `mult        $s3, $v0` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:14618 | `postLevelStatScreen` | `0x800C0DBC` | `0x00F70019` | `multu a3 s7` | `multu       $a3, $s7` | yes | reachable | **correct** |
| funcs_33.c:14662 | `postLevelStatScreen` | `0x800C0DFC` | `0x00F70019` | `multu a3 s7` | `multu       $a3, $s7` | yes | reachable | **correct** |
| funcs_33.c:18136 | `tickMenuSelectionEnterState` | `0x800C1DFC` | `0x02020018` | `mult s0 v0` | `mult        $s0, $v0` | yes | reachable | **correct** |
| funcs_33.c:26141 | `runPauseMenuStateMachine` | `0x800C3104` | `0xF7BC0098` | `—` | `mult        $t8, $a0` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:26180 | `runPauseMenuStateMachine` | `0x800C313C` | `0x10400004` | `—` | `mult        $v0, $t8` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:27080 | `runPauseMenuStateMachine` | `0x800C35CC` | `0x1040FFEF` | `—` | `mult        $v1, $a0` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:27127 | `runPauseMenuStateMachine` | `0x800C3614` | `0x30424000` | `—` | `mult        $v1, $a0` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:27306 | `runPauseMenuStateMachine` | `0x800C371C` | `0x24150003` | `—` | `mult        $v1, $a0` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:34322 | `setupCraftPreviewModel` | `0x800C4480` | `0x00850019` | `multu a0 a1` | `multu       $a0, $a1` | yes | reachable | **correct** |
| funcs_33.c:34922 | `plotRadarBlipColumn` | `0x800C4228` | `0x0C016746` | `—` | `mult        $a3, $v0` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:34933 | `plotRadarBlipColumn` | `0x800C4238` | `0x8E450018` | `—` | `mult        $t2, $v0` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:34990 | `plotRadarBlipColumn` | `0x800C429C` | `0x28620002` | `—` | `mult        $v1, $t1` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:35006 | `plotRadarBlipColumn` | `0x800C42BC` | `0x00000000` | `—` | `multu       $v0, $t3` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:35032 | `plotRadarBlipColumn` | `0x800C42EC` | `0x0803115D` | `—` | `mult        $v1, $t1` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:35044 | `plotRadarBlipColumn` | `0x800C4304` | `0x3C01800A` | `—` | `multu       $v0, $t3` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:35154 | `plotRadarBlipRow` | `0x800C43A0` | `0x92630018` | `—` | `mult        $a2, $a1` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:35166 | `plotRadarBlipRow` | `0x800C43B0` | `0x8E650010` | `—` | `mult        $v0, $a1` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:35241 | `plotRadarBlipRow` | `0x800C4424` | `0x45000053` | `—` | `mult        $v1, $t1` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:35255 | `plotRadarBlipRow` | `0x800C4440` | `0x8E640014` | `—` | `multu       $v0, $t3` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:35281 | `plotRadarBlipRow` | `0x800C4470` | `0x34A58E39` | `—` | `mult        $v1, $t1` | NO | reachable | **ELF/annotation mismatch** |
| funcs_33.c:35293 | `plotRadarBlipRow` | `0x800C4488` | `0x00081882` | `—` | `multu       $v0, $t3` | NO | reachable | **ELF/annotation mismatch** |
| funcs_34.c:6165 | `initMenuBackdropAndPickRandom` | `0x800C5780` | `0x00A40018` | `mult a1 a0` | `mult        $a1, $a0` | yes | reachable | **correct** |
| funcs_35.c:5560 | `parseJfifSOF0Marker` | `0x800C7334` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_35.c:5614 | `parseJfifSOF0Marker` | `0x800C7380` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_35.c:7586 | `paserJfifSOSMarker` | `0x800C77A4` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_35.c:7634 | `paserJfifSOSMarker` | `0x800C77E8` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_35.c:7756 | `paserJfifSOSMarker` | `0x800C7890` | `0x00450018` | `mult v0 a1` | `mult        $v0, $a1` | yes | reachable | **correct** |
| funcs_35.c:7774 | `paserJfifSOSMarker` | `0x800C78B4` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_36.c:629 | `rebuildDebrisCellGeometry` | `0x800C7A50` | `0x01220018` | `mult t1 v0` | `mult        $t1, $v0` | yes | reachable | **correct** |
| funcs_36.c:2046 | `emitDebrisCellFaces` | `0x800C7E44` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_36.c:3692 | `computeCellGridIndices` | `0x800C80F8` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_36.c:3748 | `computeCellGridIndices` | `0x800C8148` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_36.c:3800 | `computeCellGridIndices` | `0x800C8194` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_36.c:8348 | `allocCellGeometryBuffer` | `0x800C8B50` | `0x00460018` | `mult v0 a2` | `mult        $v0, $a2` | yes | reachable | **correct** |
| funcs_36.c:8386 | `allocCellGeometryBuffer` | `0x800C8B84` | `0x00460018` | `mult v0 a2` | `mult        $v0, $a2` | yes | reachable | **correct** |
| funcs_36.c:8424 | `allocCellGeometryBuffer` | `0x800C8BB8` | `0x00460018` | `mult v0 a2` | `mult        $v0, $a2` | yes | reachable | **correct** |
| funcs_36.c:8458 | `allocCellGeometryBuffer` | `0x800C8BE4` | `0x00460018` | `mult v0 a2` | `mult        $v0, $a2` | yes | reachable | **correct** |
| funcs_36.c:8629 | `buildDebrisMeshFromCells` | `0x800C8CC8` | `0x00C30018` | `mult a2 v1` | `mult        $a2, $v1` | yes | reachable | **correct** |
| funcs_36.c:8637 | `buildDebrisMeshFromCells` | `0x800C8CD8` | `0x02460018` | `mult s2 a2` | `mult        $s2, $a2` | yes | reachable | **correct** |
| funcs_36.c:8922 | `buildDebrisMeshFromCells` | `0x800C8E6C` | `0x00550018` | `mult v0 s5` | `mult        $v0, $s5` | yes | reachable | **correct** |
| funcs_36.c:9046 | `buildDebrisMeshFromCells` | `0x800C8F20` | `0x00550018` | `mult v0 s5` | `mult        $v0, $s5` | yes | reachable | **correct** |
| funcs_36.c:9195 | `buildDebrisMeshFromCells` | `0x800C9000` | `0x01220018` | `mult t1 v0` | `mult        $t1, $v0` | yes | reachable | **correct** |
| funcs_36.c:9243 | `buildDebrisMeshFromCells` | `0x800C9044` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_36.c:9291 | `buildDebrisMeshFromCells` | `0x800C9088` | `0x00950018` | `mult a0 s5` | `mult        $a0, $s5` | yes | reachable | **correct** |
| funcs_36.c:9305 | `buildDebrisMeshFromCells` | `0x800C90A4` | `0x00930018` | `mult a0 s3` | `mult        $a0, $s3` | yes | reachable | **correct** |
| funcs_36.c:9472 | `buildDebrisMeshFromCells` | `0x800C91C4` | `0x00750018` | `mult v1 s5` | `mult        $v1, $s5` | yes | reachable | **correct** |
| funcs_36.c:9484 | `buildDebrisMeshFromCells` | `0x800C91DC` | `0x00730018` | `mult v1 s3` | `mult        $v1, $s3` | yes | reachable | **correct** |
| funcs_36.c:9715 | `buildDebrisMeshFromCells` | `0x800C934C` | `0x00530018` | `mult v0 s3` | `mult        $v0, $s3` | yes | reachable | **correct** |
| funcs_36.c:9724 | `buildDebrisMeshFromCells` | `0x800C935C` | `0x02C20018` | `mult s6 v0` | `mult        $s6, $v0` | yes | reachable | **correct** |
| funcs_36.c:9772 | `buildDebrisMeshFromCells` | `0x800C93A0` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_36.c:9820 | `buildDebrisMeshFromCells` | `0x800C93E4` | `0x00530018` | `mult v0 s3` | `mult        $v0, $s3` | yes | reachable | **correct** |
| funcs_36.c:9830 | `buildDebrisMeshFromCells` | `0x800C93F8` | `0x00750018` | `mult v1 s5` | `mult        $v1, $s5` | yes | reachable | **correct** |
| funcs_36.c:10133 | `buildDebrisMeshFromCells` | `0x800C95F0` | `0x00550018` | `mult v0 s5` | `mult        $v0, $s5` | yes | reachable | **correct** |
| funcs_36.c:10143 | `buildDebrisMeshFromCells` | `0x800C9604` | `0x00530018` | `mult v0 s3` | `mult        $v0, $s3` | yes | reachable | **correct** |
| funcs_36.c:10161 | `buildDebrisMeshFromCells` | `0x800C9624` | `0x00530018` | `mult v0 s3` | `mult        $v0, $s3` | yes | reachable | **correct** |
| funcs_36.c:10468 | `buildDebrisMeshFromCells` | `0x800C9820` | `0x00550018` | `mult v0 s5` | `mult        $v0, $s5` | yes | reachable | **correct** |
| funcs_36.c:10476 | `buildDebrisMeshFromCells` | `0x800C9830` | `0x00530018` | `mult v0 s3` | `mult        $v0, $s3` | yes | reachable | **correct** |
| funcs_36.c:10488 | `buildDebrisMeshFromCells` | `0x800C9848` | `0x00530018` | `mult v0 s3` | `mult        $v0, $s3` | yes | reachable | **correct** |
| funcs_36.c:12790 | `npcTurretUpdate` | `0x800C97A0` | `0x26310002` | `—` | `mult        $a0, $v1` | NO | reachable | **ELF/annotation mismatch** |
| funcs_36.c:14393 | `npcTurretUpdate` | `0x800C9F18` | `0x3C01800A` | `—` | `mult        $a0, $v1` | NO | reachable | **ELF/annotation mismatch** |
| funcs_36.c:22381 | `npcProbeDriod` | `0x800CB174` | `0x000280C0` | `—` | `mult        $a0, $v1` | NO | reachable | **ELF/annotation mismatch** |
| funcs_36.c:22707 | `npcProbeDriod` | `0x800CB318` | `0xF7B60090` | `—` | `mult        $a0, $v1` | NO | reachable | **ELF/annotation mismatch** |
| funcs_37.c:1324 | `loadModelViewerModels` | `0x800CB8E8` | `0x02030019` | `multu s0 v1` | `multu       $s0, $v1` | yes | reachable | **correct** |
| funcs_37.c:7549 | `data_gap_800CC3D4` | `0x800CCDC0` | `0x00D900D8` | `mult a2 t9` | `.word       0x00D900D8                   # mult        $a2, $t9 # 000000C0 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:7683 | `data_gap_800CC3D4` | `0x800CCEC8` | `0x00000018` | `mult zero zero` | `mult        $zero, $zero` | yes | unreachable | **correct** |
| funcs_37.c:7739 | `data_gap_800CC3D4` | `0x800CCF38` | `0x00000058` | `mult zero zero` | `.word       0x00000058                   # mult        $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:7816 | `data_gap_800CC3D4` | `0x800CCFD0` | `0x00000059` | `multu zero zero` | `.word       0x00000059                   # multu       $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:7852 | `data_gap_800CC3D4` | `0x800CD018` | `0x00300018` | `mult at s0` | `mult        $at, $s0` | yes | unreachable | **correct** |
| funcs_37.c:8033 | `data_gap_800CC3D4` | `0x800CD158` | `0x00310019` | `multu at s1` | `multu       $at, $s1` | yes | unreachable | **correct** |
| funcs_37.c:8345 | `data_gap_800CC3D4` | `0x800CD35C` | `0x023A0118` | `mult s1 k0` | `.word       0x023A0118                   # mult        $s1, $k0 # 00000100 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_37.c:19051 | `npcAtStHandleDestruction` | `0x800CFAC8` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_38.c:729 | `npcShuttleHandleDestruction` | `0x800D351C` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_38.c:1074 | `npcShuttleHandleDestruction` | `0x800D36B4` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_38.c:3712 | `npcShuttleUpdate` | `0x800D4308` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_38.c:7875 | `npcDebrisFieldUpdate` | `0x800D56FC` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_38.c:17936 | `npcWingmanBehaviorByMode` | `0x800D8710` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_38.c:17979 | `npcWingmanBehaviorByMode` | `0x800D8758` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_38.c:18022 | `npcWingmanBehaviorByMode` | `0x800D87A0` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_38.c:18117 | `npcWingmanBehaviorByMode` | `0x800D882C` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_38.c:26142 | `npcTieVariantHandleDestruction` | `0x800DAEC8` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_38.c:28499 | `npcTieVariantUpdate` | `0x800DBA34` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_38.c:32218 | `npcRadarDishUpdate` | `0x800DCBB0` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_38.c:40475 | `npcGroundTransportUpdate` | `0x800DF3B4` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_39.c:1460 | `playAttachmentCueWithSlotIter` | `0x800E02BC` | `0x01020018` | `mult t0 v0` | `mult        $t0, $v0` | yes | reachable | **correct** |
| funcs_39.c:11950 | `npcTrainCarUpdate` | `0x800E352C` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_39.c:19970 | `npcWaterCraftHandleDestruction` | `0x800E5C64` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_39.c:20602 | `npcWaterCraftHandleDestruction` | `0x800E5F68` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_39.c:29783 | `runDestructionPhaseSequence` | `0x800E8AF0` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_39.c:37824 | `npcAtPtUpdate` | `0x800EB0D4` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_39.c:41374 | `allocObjectPoolNode` | `0x800EC19C` | `0x00430019` | `multu v0 v1` | `multu       $v0, $v1` | yes | reachable | **correct** |
| funcs_4.c:7089 | `renderFlatMeshFaceGroup` | `0x8001179C` | `0x00420018` | `mult v0 v0` | `mult        $v0, $v0` | yes | reachable | **correct** |
| funcs_4.c:7099 | `renderFlatMeshFaceGroup` | `0x800117B0` | `0x00C60018` | `mult a2 a2` | `mult        $a2, $a2` | yes | reachable | **correct** |
| funcs_4.c:8853 | `renderUnlitMeshFaces` | `0x80011F98` | `0x00420018` | `mult v0 v0` | `mult        $v0, $v0` | yes | reachable | **correct** |
| funcs_4.c:8863 | `renderUnlitMeshFaces` | `0x80011FAC` | `0x00C60018` | `mult a2 a2` | `mult        $a2, $a2` | yes | reachable | **correct** |
| funcs_4.c:24568 | `drawSubtitleText` | `0x80016334` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_4.c:24946 | `drawSubtitleText` | `0x800164BC` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_4.c:25218 | `drawSubtitleText` | `0x800165F4` | `0x03C30018` | `mult fp v1` | `mult        $fp, $v1` | yes | reachable | **correct** |
| funcs_4.c:25226 | `drawSubtitleText` | `0x80016604` | `0x02C20018` | `mult s6 v0` | `mult        $s6, $v0` | yes | reachable | **correct** |
| funcs_4.c:25506 | `drawSubtitleText` | `0x8001679C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_4.c:25878 | `drawSubtitleText` | `0x8001691C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_4.c:26150 | `drawSubtitleText` | `0x80016A54` | `0x03C30018` | `mult fp v1` | `mult        $fp, $v1` | yes | reachable | **correct** |
| funcs_4.c:26158 | `drawSubtitleText` | `0x80016A64` | `0x02C20018` | `mult s6 v0` | `mult        $s6, $v0` | yes | reachable | **correct** |
| funcs_4.c:30409 | `buildAndRegisterDefaultMaterial` | `0x80017E30` | `0x00620019` | `multu v1 v0` | `multu       $v1, $v0` | yes | reachable | **correct** |
| funcs_4.c:30748 | `buildAndRegisterDefaultMaterial` | `0x80018014` | `0x02E20019` | `multu s7 v0` | `multu       $s7, $v0` | yes | reachable | **correct** |
| funcs_40.c:2459 | `data_gap_800ECE04` | `0x800ECE0C` | `0x00430019` | `multu v0 v1` | `multu       $v0, $v1` | yes | reachable | **correct** |
| funcs_40.c:13308 | `updateNpcEventTimer` | `0x800F0328` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_40.c:13378 | `updateNpcEventTimer` | `0x800F03A0` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_41.c:4966 | `initActorMotionParams` | `0x800F290C` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_42.c:14715 | `setupMissionTransitionScreenOverlay` | `0x800FB3C4` | `0x00640018` | `mult v1 a0` | `mult        $v1, $a0` | yes | reachable | **correct** |
| funcs_49.c:5891 | `lvj_checkComplexObjectives` | `0x8010B22C` | `0x000A0019` | `multu zero t2` | `multu       $zero, $t2` | yes | unreachable | **correct** |
| funcs_49.c:6021 | `lvj_checkComplexObjectives` | `0x8010B308` | `0x00370059` | `multu at s7` | `.word       0x00370059                   # multu       $at, $s7 # 00000040 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:7801 | `static_3_80045024` | `0x800452A4` | `0x00CB0018` | `mult a2 t3` | `mult        $a2, $t3` | yes | reachable | **correct** |
| funcs_49.c:7839 | `static_3_80045024` | `0x800452EC` | `0x004B0018` | `mult v0 t3` | `mult        $v0, $t3` | yes | reachable | **correct** |
| funcs_49.c:7878 | `static_3_80045024` | `0x80045324` | `0x00CB0018` | `mult a2 t3` | `mult        $a2, $t3` | yes | reachable | **correct** |
| funcs_49.c:7892 | `static_3_80045024` | `0x80045340` | `0x008B0018` | `mult a0 t3` | `mult        $a0, $t3` | yes | reachable | **correct** |
| funcs_49.c:10100 | `static_3_800A2BE4` | `0x800A2DAC` | `0x006FFA58` | `mult v1 t7` | `.word       0x006FFA58                   # mult        $v1, $t7 # 0000FA40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10140 | `static_3_800A2BE4` | `0x800A2DEC` | `0x007B2D58` | `mult v1 k1` | `.word       0x007B2D58                   # mult        $v1, $k1 # 00002D40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10178 | `static_3_800A2BE4` | `0x800A2E28` | `0x00756E58` | `mult v1 s5` | `.word       0x00756E58                   # mult        $v1, $s5 # 00006E40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10180 | `static_3_800A2BE4` | `0x800A2E2C` | `0x00877F58` | `mult a0 a3` | `.word       0x00877F58                   # mult        $a0, $a3 # 00007F40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10218 | `static_3_800A2BE4` | `0x800A2E68` | `0x00812C58` | `mult a0 at` | `.word       0x00812C58                   # mult        $a0, $at # 00002C40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10220 | `static_3_800A2BE4` | `0x800A2E6C` | `0x00950B58` | `mult a0 s5` | `.word       0x00950B58                   # mult        $a0, $s5 # 00000B40 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_49.c:10260 | `static_3_800A2E98` | `0x800A2EA4` | `0x00783B58` | `mult v1 t8` | `.word       0x00783B58                   # mult        $v1, $t8 # 00003B40 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10262 | `static_3_800A2E98` | `0x800A2EA8` | `0x008E1758` | `mult a0 t6` | `.word       0x008E1758                   # mult        $a0, $t6 # 00001740 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10264 | `static_3_800A2E98` | `0x800A2EAC` | `0x00A3F358` | `mult a1 v1` | `.word       0x00A3F358                   # mult        $a1, $v1 # 0000F340 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10300 | `static_3_800A2E98` | `0x800A2EE4` | `0x00843F58` | `mult a0 a0` | `.word       0x00843F58                   # mult        $a0, $a0 # 00003F40 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10302 | `static_3_800A2E98` | `0x800A2EE8` | `0x009C4B58` | `mult a0 gp` | `.word       0x009C4B58                   # mult        $a0, $gp # 00004B40 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10304 | `static_3_800A2E98` | `0x800A2EEC` | `0x00B45658` | `mult a1 s4` | `.word       0x00B45658                   # mult        $a1, $s4 # 00005640 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10338 | `static_3_800A2E98` | `0x800A2F20` | `0x00770758` | `mult v1 s7` | `.word       0x00770758                   # mult        $v1, $s7 # 00000740 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10340 | `static_3_800A2E98` | `0x800A2F24` | `0x00917A58` | `mult a0 s1` | `.word       0x00917A58                   # mult        $a0, $s1 # 00007A40 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10346 | `static_3_800A2F28` | `0x800A2F28` | `0x00ABEE58` | `mult a1 t3` | `.word       0x00ABEE58                   # mult        $a1, $t3 # 0000EE40 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10348 | `static_3_800A2F28` | `0x800A2F2C` | `0x00C66158` | `mult a2 a2` | `.word       0x00C66158                   # mult        $a2, $a2 # 00006140 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10382 | `static_3_800A2F28` | `0x800A2F60` | `0x0082EE58` | `mult a0 v0` | `.word       0x0082EE58                   # mult        $a0, $v0 # 0000EE40 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10384 | `static_3_800A2F28` | `0x800A2F64` | `0x00A00658` | `mult a1 zero` | `.word       0x00A00658                   # mult        $a1, $zero # 00000640 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10386 | `static_3_800A2F28` | `0x800A2F68` | `0x00BD1F58` | `mult a1 sp` | `.word       0x00BD1F58                   # mult        $a1, $sp # 00001F40 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10388 | `static_3_800A2F28` | `0x800A2F6C` | `0x00DA3758` | `mult a2 k0` | `.word       0x00DA3758                   # mult        $a2, $k0 # 00003740 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10422 | `static_3_800A2F28` | `0x800A2FA0` | `0x008FFE58` | `mult a0 t7` | `.word       0x008FFE58                   # mult        $a0, $t7 # 0000FE40 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10424 | `static_3_800A2F28` | `0x800A2FA4` | `0x00AFFD58` | `mult a1 t7` | `.word       0x00AFFD58                   # mult        $a1, $t7 # 0000FD40 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10426 | `static_3_800A2F28` | `0x800A2FA8` | `0x00CFFD58` | `mult a2 t7` | `.word       0x00CFFD58                   # mult        $a2, $t7 # 0000FD40 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_49.c:10428 | `static_3_800A2F28` | `0x800A2FAC` | `0x00EFFC58` | `mult a3 t7` | `.word       0x00EFFC58                   # mult        $a3, $t7 # 0000FC40 <InstrIdType: CPU_SPECIAL>` | yes | reachable | **correct** |
| funcs_5.c:548 | `initVideoSubsystem` | `0x8001A2AC` | `0x02020018` | `mult s0 v0` | `mult        $s0, $v0` | yes | reachable | **correct** |
| funcs_5.c:569 | `initVideoSubsystem` | `0x8001A2D0` | `0x02020018` | `mult s0 v0` | `mult        $s0, $v0` | yes | reachable | **correct** |
| funcs_5.c:941 | `initVideoSubsystem` | `0x8001A4E8` | `0x00A30018` | `mult a1 v1` | `mult        $a1, $v1` | yes | reachable | **correct** |
| funcs_5.c:1972 | `initVideoSubsystem` | `0x8001AA18` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_5.c:2800 | `initVideoSubsystem` | `0x8001AE88` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_5.c:3825 | `initVideoSubsystem` | `0x8001B3B0` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_5.c:5778 | `computeFramebufferByteSize` | `0x8001BC6C` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_5.c:5797 | `computeFramebufferByteSize` | `0x8001BC8C` | `0x00430018` | `mult v0 v1` | `mult        $v0, $v1` | yes | reachable | **correct** |
| funcs_6.c:8506 | `loadTextureTile` | `0x800202C0` | `0x02540018` | `mult s2 s4` | `mult        $s2, $s4` | yes | reachable | **correct** |
| funcs_6.c:9081 | `loadTextureTile` | `0x800205DC` | `0x02330018` | `mult s1 s3` | `mult        $s1, $s3` | yes | reachable | **correct** |
| funcs_6.c:9576 | `loadTextureTile` | `0x80020890` | `0x02340018` | `mult s1 s4` | `mult        $s1, $s4` | yes | reachable | **correct** |
| funcs_6.c:10472 | `loadTextureTile` | `0x80020D20` | `0x02330018` | `mult s1 s3` | `mult        $s1, $s3` | yes | reachable | **correct** |
| funcs_6.c:10985 | `loadTextureTile` | `0x80020FF0` | `0x02330018` | `mult s1 s3` | `mult        $s1, $s3` | yes | reachable | **correct** |
| funcs_6.c:11472 | `loadTextureTile` | `0x80021294` | `0x02330018` | `mult s1 s3` | `mult        $s1, $s3` | yes | reachable | **correct** |
| funcs_6.c:11973 | `loadTextureTile` | `0x80021554` | `0x02330018` | `mult s1 s3` | `mult        $s1, $s3` | yes | reachable | **correct** |
| funcs_6.c:12470 | `loadTextureTile` | `0x8002180C` | `0x02330018` | `mult s1 s3` | `mult        $s1, $s3` | yes | reachable | **correct** |
| funcs_7.c:636 | `emitProfilerBarSegment` | `0x80023D98` | `0x00A20019` | `multu a1 v0` | `multu       $a1, $v0` | yes | reachable | **correct** |
| funcs_7.c:1863 | `flushDebugTextOverlay` | `0x800243A0` | `0x00830019` | `multu a0 v1` | `multu       $a0, $v1` | yes | reachable | **correct** |
| funcs_7.c:8342 | `adler32` | `0x80026AF4` | `0x03160019` | `multu t8 s6` | `multu       $t8, $s6` | yes | reachable | **correct** |
| funcs_7.c:8369 | `adler32` | `0x80026B18` | `0x03160019` | `multu t8 s6` | `multu       $t8, $s6` | yes | reachable | **correct** |
| funcs_7.c:8378 | `adler32` | `0x80026B28` | `0x03360019` | `multu t9 s6` | `multu       $t9, $s6` | yes | reachable | **correct** |
| funcs_7.c:9354 | `inflate_recomp` | `0x80026FCC` | `0x00640019` | `multu v1 a0` | `multu       $v1, $a0` | yes | reachable | **correct** |
| funcs_8.c:6855 | `_Printf` | `0x80036180` | `0x031E0019` | `multu t8 fp` | `multu       $t8, $fp` | yes | reachable | **correct** |
| funcs_8.c:6993 | `_Printf` | `0x8003622C` | `0x033E0019` | `multu t9 fp` | `multu       $t9, $fp` | yes | reachable | **correct** |
| funcs_8.c:9331 | `_Ldtob` | `0x80036D48` | `0x03210019` | `multu t9 at` | `multu       $t9, $at` | yes | reachable | **correct** |
| funcs_8.c:10303 | `ldiv_recomp` | `0x80037210` | `0x00C20019` | `multu a2 v0` | `multu       $a2, $v0` | yes | reachable | **correct** |
| funcs_8.c:13353 | `__OSGlobalIntMask` | `0x8003A120` | `0x00141818` | `mult zero s4` | `.word       0x00141818                   # mult        $zero, $s4 # 00001800 <InstrIdType: CPU_SPECIAL>` | yes | unreachable | **correct** |
| funcs_9.c:4511 | `randomBurstNpcHandlerVariant` | `0x800405B8` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_9.c:5647 | `spawnNpcFormationWithRandomOrientation` | `0x80040AF8` | `0x00E30018` | `mult a3 v1` | `mult        $a3, $v1` | yes | reachable | **correct** |
| funcs_9.c:5723 | `spawnNpcFormationWithRandomOrientation` | `0x80040B74` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_9.c:6127 | `spawnNpcFormationWithRandomOrientation` | `0x80040D88` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_9.c:6340 | `spawnNpcFormationWithRandomOrientation` | `0x80040E84` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_9.c:12725 | `streamTerrainGridCellsByDistance` | `0x80042C4C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_9.c:12755 | `streamTerrainGridCellsByDistance` | `0x80042C74` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_9.c:13699 | `streamTerrainGridCellsByDistance` | `0x800430F4` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_9.c:13720 | `streamTerrainGridCellsByDistance` | `0x8004310C` | `0x00440018` | `mult v0 a0` | `mult        $v0, $a0` | yes | reachable | **correct** |
| funcs_9.c:15990 | `markLowLodCellsInGrid` | `0x80043BA0` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_9.c:16012 | `markLowLodCellsInGrid` | `0x80043BC8` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_9.c:16252 | `markHighLodCellsInGrid` | `0x80043CE4` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_9.c:16274 | `markHighLodCellsInGrid` | `0x80043D0C` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_9.c:16901 | `load_level_hmp` | `0x80044070` | `0x00820018` | `mult a0 v0` | `mult        $a0, $v0` | yes | reachable | **correct** |
| funcs_9.c:16951 | `load_level_hmp` | `0x800440B0` | `0x00830018` | `mult a0 v1` | `mult        $a0, $v1` | yes | reachable | **correct** |
| funcs_9.c:16988 | `load_level_hmp` | `0x800440E4` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_9.c:17013 | `load_level_hmp` | `0x8004410C` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_9.c:17071 | `load_level_hmp` | `0x80044168` | `0x00620018` | `mult v1 v0` | `mult        $v1, $v0` | yes | reachable | **correct** |
| funcs_9.c:19236 | `computeGridTileEdgeAdjacencyMasks` | `0x80044C84` | `0x00A20018` | `mult a1 v0` | `mult        $a1, $v0` | yes | reachable | **correct** |
| funcs_9.c:19282 | `computeGridTileEdgeAdjacencyMasks` | `0x80044CC4` | `0x00A30018` | `mult a1 v1` | `mult        $a1, $v1` | yes | reachable | **correct** |
| funcs_9.c:19340 | `computeGridTileEdgeAdjacencyMasks` | `0x80044D0C` | `0x01620018` | `mult t3 v0` | `mult        $t3, $v0` | yes | reachable | **correct** |
| funcs_9.c:19398 | `computeGridTileEdgeAdjacencyMasks` | `0x80044D64` | `0x01420018` | `mult t2 v0` | `mult        $t2, $v0` | yes | reachable | **correct** |
| funcs_9.c:20287 | `computeGridTileEdgeAdjacencyMasks` | `0x800452A4` | `0x00CB0018` | `mult a2 t3` | `mult        $a2, $t3` | yes | reachable | **correct** |
| funcs_9.c:20325 | `computeGridTileEdgeAdjacencyMasks` | `0x800452EC` | `0x004B0018` | `mult v0 t3` | `mult        $v0, $t3` | yes | reachable | **correct** |
| funcs_9.c:20364 | `computeGridTileEdgeAdjacencyMasks` | `0x80045324` | `0x00CB0018` | `mult a2 t3` | `mult        $a2, $t3` | yes | reachable | **correct** |
| funcs_9.c:20378 | `computeGridTileEdgeAdjacencyMasks` | `0x80045340` | `0x008B0018` | `mult a0 t3` | `mult        $a0, $t3` | yes | reachable | **correct** |
