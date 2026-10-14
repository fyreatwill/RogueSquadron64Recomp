# M3 generic `do_break` CPU-instruction census

This is a static census only; it changes no generated output or runtime behavior. Every row is a generated guest annotation followed by a `do_break`; the raw word comes independently from the retail ELF at that guest PC.

- generated `do_break` sites with ELF words: **5635** / 5635
- unique file/guest-PC sites: **5391**
- selected valid `sync` sites (funct 0x0F with reserved fields clear): **7**
- decoded opcode counts: `beq`=33, `break`=291, `cop0`=1219, `cop1`=42, `div`=1, `j`=307, `jalr`=69, `lui`=1, `movn`=84, `movz`=95, `opcode_0x12`=805, `opcode_0x13`=122, `opcode_0x1C`=163, `opcode_0x1D`=99, `opcode_0x1E`=45, `opcode_0x1F`=9, `opcode_0x30`=191, `opcode_0x32`=289, `opcode_0x33`=6, `opcode_0x34`=4, `opcode_0x36`=7, `opcode_0x38`=8, `opcode_0x3A`=187, `opcode_0x3B`=10, `opcode_0x3C`=10, `opcode_0x3E`=42, `regimm`=236, `special_0x01`=122, `special_0x05`=80, `special_0x0E`=97, `special_0x0F`=98, `special_0x15`=78, `special_0x28`=56, `special_0x29`=81, `special_0x30`=77, `special_0x31`=52, `special_0x32`=58, `special_0x33`=50, `special_0x34`=62, `special_0x35`=61, `special_0x36`=50, `special_0x37`=54, `special_0x39`=99, `special_0x3D`=78, `sync`=7

## Site table

| file:line | function | guest PC | raw word | independent decode | annotation |
|---|---|---:|---:|---|---|
| funcs_10.c:2669 | `loadGridCellTilesByDistance` | `0x80046500` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_10.c:2690 | `loadGridCellTilesByDistance` | `0x80046518` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_11.c:17246 | `updateAnimatedTextureStreaming` | `0x80054190` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_11.c:17267 | `updateAnimatedTextureStreaming` | `0x800541A8` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_11.c:17384 | `updateAnimatedTextureStreaming` | `0x80054218` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_11.c:17405 | `updateAnimatedTextureStreaming` | `0x80054230` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_11.c:18110 | `randomizeListEntrySpacing` | `0x8005459C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_11.c:18131 | `randomizeListEntrySpacing` | `0x800545B4` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_11.c:18553 | `tickWrappingTimerAccumulatorList` | `0x80054744` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_11.c:19567 | `getPoolEntryFrameIndex` | `0x80054C44` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_11.c:20522 | `loadAssetAndIterateSubchunks` | `0x800550C4` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_11.c:20543 | `loadAssetAndIterateSubchunks` | `0x800550DC` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_12.c:303 | `loadSpriteSheetTextureFrames` | `0x800552E8` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_12.c:324 | `loadSpriteSheetTextureFrames` | `0x80055300` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_12.c:2579 | `tickVoiceSubtitleDisplay` | `0x80055F2C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_12.c:2600 | `tickVoiceSubtitleDisplay` | `0x80055F44` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_13.c:18505 | `steerOrientationTowardTargetPreamble` | `0x8005EE64` | `0x08017B9D` | `j` | `j           L_8005EE74` |
| funcs_14.c:1028 | `loadCharTextureSet` | `0x80061704` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_14.c:1057 | `loadCharTextureSet` | `0x80061734` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_17.c:11338 | `multiEventTemplateNpcHandler` | `0x80070EB8` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_17.c:11359 | `multiEventTemplateNpcHandler` | `0x80070ED0` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_18.c:1707 | `composeRandomRotationMatrix` | `0x80072084` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_18.c:1728 | `composeRandomRotationMatrix` | `0x8007209C` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_18.c:2011 | `composeRandomRotationMatrixVariant` | `0x800721EC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_18.c:2032 | `composeRandomRotationMatrixVariant` | `0x80072204` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_18.c:12532 | `buildRandomCameraFacingOrientation` | `0x800752C0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_18.c:12553 | `buildRandomCameraFacingOrientation` | `0x800752D8` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_18.c:12927 | `buildRandomCameraFacingOrientation` | `0x800754A8` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_18.c:12948 | `buildRandomCameraFacingOrientation` | `0x800754C0` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_18.c:16593 | `npcPowerGeneratorHandleDestruction` | `0x80076528` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_18.c:16614 | `npcPowerGeneratorHandleDestruction` | `0x80076540` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_19.c:1995 | `spawnNpcWithRandomRotation` | `0x80079AC8` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_19.c:2016 | `spawnNpcWithRandomRotation` | `0x80079AE0` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_19.c:2296 | `setRandomFacingDirection` | `0x80079C48` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_19.c:2317 | `setRandomFacingDirection` | `0x80079C60` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_19.c:7118 | `npcShieldUpdate` | `0x8007B3E0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_19.c:7139 | `npcShieldUpdate` | `0x8007B3F8` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_20.c:2441 | `rspbootTextPreamble` | `0x800825D0` | `0x09000419` | `j` | `j           L_84001064` |
| funcs_20.c:2445 | `rspbootTextPreamble` | `0x800825D0` | `0x09000419` | `j` | `j           L_84001064` |
| funcs_20.c:2455 | `rspbootTextPreamble` | `0x800825E4` | `0x40870000` | `cop0` | `mtc0        $a3, Index` |
| funcs_20.c:2458 | `rspbootTextPreamble` | `0x800825E8` | `0x40820800` | `cop0` | `mtc0        $v0, Random` |
| funcs_20.c:2460 | `rspbootTextPreamble` | `0x800825EC` | `0x40831000` | `cop0` | `mtc0        $v1, EntryLo0` |
| funcs_20.c:2463 | `rspbootTextPreamble` | `0x800825F0` | `0x40043000` | `cop0` | `mfc0        $a0, Wired` |
| funcs_20.c:2482 | `rspbootTextPreamble` | `0x80082608` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_20.c:2486 | `rspbootTextPreamble` | `0x80082608` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_20.c:2489 | `rspbootTextPreamble` | `0x8008260C` | `0x40082000` | `cop0` | `mfc0        $t0, Context` |
| funcs_20.c:2502 | `rspbootTextPreamble` | `0x80082620` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_20.c:2506 | `rspbootTextPreamble` | `0x80082620` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_20.c:2510 | `rspbootTextPreamble` | `0x80082628` | `0x40882000` | `cop0` | `mtc0        $t0, Context` |
| funcs_20.c:2512 | `rspbootTextPreamble` | `0x8008262C` | `0x0000000D` | `break $zero,$zero,$zero` | `break       0` |
| funcs_20.c:2536 | `rspbootTextPreamble` | `0x8008264C` | `0x40025800` | `cop0` | `mfc0        $v0, Compare` |
| funcs_20.c:2556 | `rspbootTextPreamble` | `0x80082668` | `0x401E2800` | `cop0` | `mfc0        $fp, PageMask` |
| funcs_20.c:2566 | `rspbootTextPreamble` | `0x80082674` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_20.c:2568 | `rspbootTextPreamble` | `0x80082678` | `0x40820800` | `cop0` | `mtc0        $v0, Random` |
| funcs_20.c:2570 | `rspbootTextPreamble` | `0x8008267C` | `0x40831000` | `cop0` | `mtc0        $v1, EntryLo0` |
| funcs_20.c:2573 | `rspbootTextPreamble` | `0x80082680` | `0x40043000` | `cop0` | `mfc0        $a0, Wired` |
| funcs_20.c:2591 | `rspbootTextPreamble` | `0x80082694` | `0x09000402` | `j` | `j           L_84001008` |
| funcs_21.c:5954 | `computeVoiceGlidePitch` | `0x80086A7C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_21.c:6366 | `findActiveVoiceByKeyPair` | `0x80086C90` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_22.c:1746 | `computeChannelTempoStepFromTable` | `0x800895A8` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_22.c:1943 | `computeChannelWaitDuration` | `0x800896A8` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_22.c:2061 | `computeChannelWaitDuration` | `0x80089744` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_22.c:2934 | `soundMacroOpLoopRandomCount` | `0x80089B9C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_22.c:3502 | `soundMacroOpSetPitchBendGlide` | `0x80089E7C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_22.c:5198 | `soundMacroOpSetPanSweep` | `0x8008A7A0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_22.c:5836 | `soundMacroOpSetVolumeRamp` | `0x8008AAF0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_22.c:6629 | `soundMacroSetupVolumeRamp` | `0x8008AEF4` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_22.c:6866 | `soundMacroSetupVolumeRamp` | `0x8008B038` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_22.c:6887 | `soundMacroSetupVolumeRamp` | `0x8008B050` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_22.c:7159 | `soundMacroPlayRandomKeyNote` | `0x8008B1F0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_22.c:7180 | `soundMacroPlayRandomKeyNote` | `0x8008B208` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_23.c:2000 | `soundMacroSetPitchTarget` | `0x8008BAEC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:3286 | `tickAudioChannel` | `0x8008C0B8` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:3955 | `tickAudioChannel` | `0x8008C41C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:4737 | `tickAudioChannel` | `0x8008C7E4` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:5351 | `tickAllAudioChannels` | `0x8008CA70` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:5370 | `tickAllAudioChannels` | `0x8008CA8C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:5512 | `tickAllAudioChannels` | `0x8008CB60` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:5531 | `tickAllAudioChannels` | `0x8008CB7C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:6451 | `tickAllAudioChannels` | `0x8008D090` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:8030 | `tickAudioSequencerFrame` | `0x8008D9BC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:8051 | `tickAudioSequencerFrame` | `0x8008D9D4` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_23.c:8931 | `dispatchAudioCommand` | `0x8008DE18` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:8952 | `dispatchAudioCommand` | `0x8008DE30` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_23.c:9066 | `dispatchAudioCommand` | `0x8008DEDC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:9087 | `dispatchAudioCommand` | `0x8008DEF4` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_23.c:9224 | `dispatchAudioCommand` | `0x8008DFB8` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:9245 | `dispatchAudioCommand` | `0x8008DFD0` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_23.c:9332 | `dispatchAudioCommand` | `0x8008E054` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:9353 | `dispatchAudioCommand` | `0x8008E06C` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_23.c:9809 | `setupAudioFaderRamp` | `0x8008E2B8` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:9830 | `setupAudioFaderRamp` | `0x8008E2D0` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_23.c:9925 | `setupAudioFaderRamp` | `0x8008E35C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:9946 | `setupAudioFaderRamp` | `0x8008E374` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_23.c:10046 | `setupAudioFaderRamp` | `0x8008E408` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:10067 | `setupAudioFaderRamp` | `0x8008E420` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_23.c:10146 | `setupAudioFaderRamp` | `0x8008E49C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_23.c:10167 | `setupAudioFaderRamp` | `0x8008E4B4` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_23.c:13609 | `advanceVolumeFadeEnvelope` | `0x8008F504` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_24.c:1682 | `fillSampleStreamRange` | `0x8008FE70` | `0x000101CD` | `break $zero,$zero,$at` | `break       1, 7` |
| funcs_25.c:1121 | `data_gap_80094348` | `0x80094348` | `0x080250DC` | `j` | `j           L_80094370` |
| funcs_25.c:5436 | `updateSongTempoTickRate` | `0x80095668` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_25.c:5457 | `updateSongTempoTickRate` | `0x80095680` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_25.c:10430 | `tickAllActiveSongs` | `0x80096E40` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_25.c:10451 | `tickAllActiveSongs` | `0x80096E58` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_25.c:10983 | `data_gap_8009711C` | `0x8009711C` | `0x08025C4F` | `j` | `j           L_8009713C` |
| funcs_26.c:9345 | `data_gap_80099FDC` | `0x80099FE0` | `0x40065800` | `cop0` | `mfc0        $a2, Compare` |
| funcs_26.c:9349 | `data_gap_80099FDC` | `0x80099FE0` | `0x40065800` | `cop0` | `mfc0        $a2, Compare` |
| funcs_26.c:9371 | `data_gap_80099FDC` | `0x80099FF8` | `0x40055800` | `cop0` | `mfc0        $a1, Compare` |
| funcs_26.c:9384 | `data_gap_80099FDC` | `0x8009A008` | `0x4A00002C` | `opcode_0x12` | `.word       0x4A00002C                   # INVALID     $s0, $zero, 0x2C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:9560 | `data_gap_80099FDC` | `0x8009A0E4` | `0x09000480` | `j` | `j           L_84001200` |
| funcs_26.c:9769 | `data_gap_80099FDC` | `0x8009A1EC` | `0x0900044B` | `j` | `j           L_8400112C` |
| funcs_26.c:9860 | `data_gap_80099FDC` | `0x8009A26C` | `0x090004FA` | `j` | `j           L_840013E8` |
| funcs_26.c:9881 | `data_gap_80099FDC` | `0x8009A28C` | `0x40852000` | `cop0` | `mtc0        $a1, Context` |
| funcs_26.c:9883 | `data_gap_80099FDC` | `0x8009A290` | `0x0000000D` | `break $zero,$zero,$zero` | `break       0` |
| funcs_26.c:9926 | `data_gap_80099FDC` | `0x8009A2D4` | `0x090004FA` | `j` | `j           L_840013E8` |
| funcs_26.c:9941 | `data_gap_80099FDC` | `0x8009A2EC` | `0x09000506` | `j` | `j           L_84001418` |
| funcs_26.c:9960 | `data_gap_80099FDC` | `0x8009A308` | `0x09000506` | `j` | `j           L_84001418` |
| funcs_26.c:9965 | `data_gap_80099FDC` | `0x8009A310` | `0x40083800` | `cop0` | `mfc0        $t0, Reserved07` |
| funcs_26.c:9976 | `data_gap_80099FDC` | `0x8009A31C` | `0x40082800` | `cop0` | `mfc0        $t0, PageMask` |
| funcs_26.c:9986 | `data_gap_80099FDC` | `0x8009A328` | `0x40850000` | `cop0` | `mtc0        $a1, Index` |
| funcs_26.c:9988 | `data_gap_80099FDC` | `0x8009A32C` | `0x40860800` | `cop0` | `mtc0        $a2, Random` |
| funcs_26.c:9990 | `data_gap_80099FDC` | `0x8009A330` | `0x40871800` | `cop0` | `mtc0        $a3, EntryLo1` |
| funcs_26.c:9993 | `data_gap_80099FDC` | `0x8009A334` | `0x40053000` | `cop0` | `mfc0        $a1, Wired` |
| funcs_26.c:10004 | `data_gap_80099FDC` | `0x8009A344` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_26.c:10007 | `data_gap_80099FDC` | `0x8009A344` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_26.c:10010 | `data_gap_80099FDC` | `0x8009A348` | `0x40083800` | `cop0` | `mfc0        $t0, Reserved07` |
| funcs_26.c:10014 | `data_gap_80099FDC` | `0x8009A350` | `0x40082800` | `cop0` | `mfc0        $t0, PageMask` |
| funcs_26.c:10019 | `data_gap_80099FDC` | `0x8009A350` | `0x40082800` | `cop0` | `mfc0        $t0, PageMask` |
| funcs_26.c:10029 | `data_gap_80099FDC` | `0x8009A35C` | `0x40860000` | `cop0` | `mtc0        $a2, Index` |
| funcs_26.c:10031 | `data_gap_80099FDC` | `0x8009A360` | `0x40850800` | `cop0` | `mtc0        $a1, Random` |
| funcs_26.c:10033 | `data_gap_80099FDC` | `0x8009A364` | `0x40871000` | `cop0` | `mtc0        $a3, EntryLo0` |
| funcs_26.c:10038 | `data_gap_80099FDC` | `0x8009A36C` | `0x40073000` | `cop0` | `mfc0        $a3, Wired` |
| funcs_26.c:10042 | `data_gap_80099FDC` | `0x8009A36C` | `0x40073000` | `cop0` | `mfc0        $a3, Wired` |
| funcs_26.c:10045 | `data_gap_80099FDC` | `0x8009A374` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_26.c:10048 | `data_gap_80099FDC` | `0x8009A374` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_26.c:10051 | `data_gap_80099FDC` | `0x8009A378` | `0x40083800` | `cop0` | `mfc0        $t0, Reserved07` |
| funcs_26.c:10055 | `data_gap_80099FDC` | `0x8009A380` | `0x40082800` | `cop0` | `mfc0        $t0, PageMask` |
| funcs_26.c:10060 | `data_gap_80099FDC` | `0x8009A380` | `0x40082800` | `cop0` | `mfc0        $t0, PageMask` |
| funcs_26.c:10070 | `data_gap_80099FDC` | `0x8009A38C` | `0x40860000` | `cop0` | `mtc0        $a2, Index` |
| funcs_26.c:10072 | `data_gap_80099FDC` | `0x8009A390` | `0x40850800` | `cop0` | `mtc0        $a1, Random` |
| funcs_26.c:10075 | `data_gap_80099FDC` | `0x8009A398` | `0x40871000` | `cop0` | `mtc0        $a3, EntryLo0` |
| funcs_26.c:10078 | `data_gap_80099FDC` | `0x8009A398` | `0x40871000` | `cop0` | `mtc0        $a3, EntryLo0` |
| funcs_26.c:10081 | `data_gap_80099FDC` | `0x8009A39C` | `0x400A3000` | `cop0` | `mfc0        $t2, Wired` |
| funcs_26.c:10092 | `data_gap_80099FDC` | `0x8009A3AC` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_26.c:10095 | `data_gap_80099FDC` | `0x8009A3AC` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_26.c:10120 | `data_gap_80099FDC` | `0x8009A3CC` | `0x4B271094` | `opcode_0x12` | `.word       0x4B271094                   # INVALID     $t9, $a3, 0x1094 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10122 | `data_gap_80099FDC` | `0x8009A3D0` | `0xC9231800` | `opcode_0x32` | `lwc2        $3, 0x1800($t1)` |
| funcs_26.c:10124 | `data_gap_80099FDC` | `0x8009A3D4` | `0x4B070850` | `opcode_0x12` | `.word       0x4B070850                   # INVALID     $t8, $a3, 0x850 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10126 | `data_gap_80099FDC` | `0x8009A3D8` | `0xC9A31C00` | `opcode_0x32` | `lwc2        $3, 0x1C00($t5)` |
| funcs_26.c:10128 | `data_gap_80099FDC` | `0x8009A3DC` | `0x4B3F0ED1` | `opcode_0x12` | `.word       0x4B3F0ED1                   # INVALID     $t9, $ra, 0xED1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10130 | `data_gap_80099FDC` | `0x8009A3E0` | `0xC9441800` | `opcode_0x32` | `lwc2        $4, 0x1800($t2)` |
| funcs_26.c:10132 | `data_gap_80099FDC` | `0x8009A3E4` | `0xC9C41C00` | `opcode_0x32` | `lwc2        $4, 0x1C00($t6)` |
| funcs_26.c:10134 | `data_gap_80099FDC` | `0x8009A3E8` | `0xC9651800` | `opcode_0x32` | `lwc2        $5, 0x1800($t3)` |
| funcs_26.c:10136 | `data_gap_80099FDC` | `0x8009A3EC` | `0xC9E51C00` | `opcode_0x32` | `lwc2        $5, 0x1C00($t7)` |
| funcs_26.c:10138 | `data_gap_80099FDC` | `0x8009A3F0` | `0x4B5FDED0` | `opcode_0x12` | `.word       0x4B5FDED0                   # INVALID     $k0, $ra, -0x2130 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10140 | `data_gap_80099FDC` | `0x8009A3F4` | `0xC9861800` | `opcode_0x32` | `lwc2        $6, 0x1800($t4)` |
| funcs_26.c:10142 | `data_gap_80099FDC` | `0x8009A3F8` | `0xCA061C00` | `opcode_0x32` | `lwc2        $6, 0x1C00($s0)` |
| funcs_26.c:10144 | `data_gap_80099FDC` | `0x8009A3FC` | `0xCA391800` | `opcode_0x32` | `lwc2        $25, 0x1800($s1)` |
| funcs_26.c:10146 | `data_gap_80099FDC` | `0x8009A400` | `0x4B3F0860` | `opcode_0x12` | `.word       0x4B3F0860                   # INVALID     $t9, $ra, 0x860 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10148 | `data_gap_80099FDC` | `0x8009A404` | `0xCAB91C00` | `opcode_0x32` | `lwc2        $25, 0x1C00($s5)` |
| funcs_26.c:10150 | `data_gap_80099FDC` | `0x8009A408` | `0x4A1B0867` | `opcode_0x12` | `.word       0x4A1B0867                   # INVALID     $s0, $k1, 0x867 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10152 | `data_gap_80099FDC` | `0x8009A40C` | `0xCA581800` | `opcode_0x32` | `lwc2        $24, 0x1800($s2)` |
| funcs_26.c:10154 | `data_gap_80099FDC` | `0x8009A410` | `0xCAD81C00` | `opcode_0x32` | `lwc2        $24, 0x1C00($s6)` |
| funcs_26.c:10156 | `data_gap_80099FDC` | `0x8009A414` | `0xCA7D1800` | `opcode_0x32` | `lwc2        $29, 0x1800($s3)` |
| funcs_26.c:10158 | `data_gap_80099FDC` | `0x8009A418` | `0xCAFD1C00` | `opcode_0x32` | `lwc2        $29, 0x1C00($s7)` |
| funcs_26.c:10160 | `data_gap_80099FDC` | `0x8009A41C` | `0x4B7F0EC6` | `opcode_0x12` | `.word       0x4B7F0EC6                   # INVALID     $k1, $ra, 0xEC6 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10162 | `data_gap_80099FDC` | `0x8009A420` | `0xCA9E1800` | `opcode_0x32` | `lwc2        $30, 0x1800($s4)` |
| funcs_26.c:10164 | `data_gap_80099FDC` | `0x8009A424` | `0x4BBF1684` | `opcode_0x12` | `.word       0x4BBF1684                   # INVALID     $sp, $ra, 0x1684 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10166 | `data_gap_80099FDC` | `0x8009A428` | `0xCB1E1C00` | `opcode_0x32` | `lwc2        $30, 0x1C00($t8)` |
| funcs_26.c:10168 | `data_gap_80099FDC` | `0x8009A42C` | `0x4B9FD686` | `opcode_0x12` | `.word       0x4B9FD686                   # INVALID     $gp, $ra, -0x297A # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10170 | `data_gap_80099FDC` | `0x8009A430` | `0x4B1FE68E` | `opcode_0x12` | `.word       0x4B1FE68E                   # INVALID     $t8, $ra, -0x1972 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10172 | `data_gap_80099FDC` | `0x8009A434` | `0xE83B2000` | `opcode_0x3A` | `swc2        $27, 0x2000($at)` |
| funcs_26.c:10174 | `data_gap_80099FDC` | `0x8009A438` | `0xE83A2001` | `opcode_0x3A` | `swc2        $26, 0x2001($at)` |
| funcs_26.c:10176 | `data_gap_80099FDC` | `0x8009A43C` | `0x4A1918C0` | `opcode_0x12` | `.word       0x4A1918C0                   # INVALID     $s0, $t9, 0x18C0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10180 | `data_gap_80099FDC` | `0x8009A444` | `0x4A182100` | `opcode_0x12` | `.word       0x4A182100                   # INVALID     $s0, $t8, 0x2100 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10184 | `data_gap_80099FDC` | `0x8009A44C` | `0x4A1D2940` | `opcode_0x12` | `.word       0x4A1D2940                   # INVALID     $s0, $sp, 0x2940 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10188 | `data_gap_80099FDC` | `0x8009A454` | `0x4A1E3180` | `opcode_0x12` | `.word       0x4A1E3180                   # INVALID     $s0, $fp, 0x3180 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10192 | `data_gap_80099FDC` | `0x8009A45C` | `0x4A6318D0` | `opcode_0x12` | `.word       0x4A6318D0                   # INVALID     $s3, $v1, 0x18D0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10196 | `data_gap_80099FDC` | `0x8009A464` | `0x4A642110` | `opcode_0x12` | `.word       0x4A642110                   # INVALID     $s3, $a0, 0x2110 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10200 | `data_gap_80099FDC` | `0x8009A46C` | `0x4A652950` | `opcode_0x12` | `.word       0x4A652950                   # INVALID     $s3, $a1, 0x2950 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10204 | `data_gap_80099FDC` | `0x8009A474` | `0x4A663190` | `opcode_0x12` | `.word       0x4A663190                   # INVALID     $s3, $a2, 0x3190 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10208 | `data_gap_80099FDC` | `0x8009A47C` | `0x4AC318D0` | `opcode_0x12` | `.word       0x4AC318D0                   # INVALID     $s6, $v1, 0x18D0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10212 | `data_gap_80099FDC` | `0x8009A484` | `0x4AC42110` | `opcode_0x12` | `.word       0x4AC42110                   # INVALID     $s6, $a0, 0x2110 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10216 | `data_gap_80099FDC` | `0x8009A48C` | `0x4AC52950` | `opcode_0x12` | `.word       0x4AC52950                   # INVALID     $s6, $a1, 0x2950 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10220 | `data_gap_80099FDC` | `0x8009A494` | `0x4AC63190` | `opcode_0x12` | `.word       0x4AC63190                   # INVALID     $s6, $a2, 0x3190 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10224 | `data_gap_80099FDC` | `0x8009A49C` | `0x4A8340C6` | `opcode_0x12` | `.word       0x4A8340C6                   # INVALID     $s4, $v1, 0x40C6 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10228 | `data_gap_80099FDC` | `0x8009A4A4` | `0x4A8448CE` | `opcode_0x12` | `.word       0x4A8448CE                   # INVALID     $s4, $a0, 0x48CE # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10232 | `data_gap_80099FDC` | `0x8009A4AC` | `0x4A8550CE` | `opcode_0x12` | `.word       0x4A8550CE                   # INVALID     $s4, $a1, 0x50CE # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10236 | `data_gap_80099FDC` | `0x8009A4B4` | `0x4A8658CE` | `opcode_0x12` | `.word       0x4A8658CE                   # INVALID     $s4, $a2, 0x58CE # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10240 | `data_gap_80099FDC` | `0x8009A4BC` | `0xCB9A2000` | `opcode_0x32` | `lwc2        $26, 0x2000($gp)` |
| funcs_26.c:10242 | `data_gap_80099FDC` | `0x8009A4C0` | `0xCB7B2000` | `opcode_0x32` | `lwc2        $27, 0x2000($k1)` |
| funcs_26.c:10244 | `data_gap_80099FDC` | `0x8009A4C4` | `0x4A121980` | `opcode_0x12` | `.word       0x4A121980                   # INVALID     $s0, $s2, 0x1980 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10248 | `data_gap_80099FDC` | `0x8009A4CC` | `0x4A1CD68F` | `opcode_0x12` | `.word       0x4A1CD68F                   # INVALID     $s0, $gp, -0x2971 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10250 | `data_gap_80099FDC` | `0x8009A4D0` | `0x4A101940` | `opcode_0x12` | `.word       0x4A101940                   # INVALID     $s0, $s0, 0x1940 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10254 | `data_gap_80099FDC` | `0x8009A4D8` | `0x4A1CDECF` | `opcode_0x12` | `.word       0x4A1CDECF                   # INVALID     $s0, $gp, -0x2131 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10256 | `data_gap_80099FDC` | `0x8009A4DC` | `0xCB392000` | `opcode_0x32` | `lwc2        $25, 0x2000($t9)` |
| funcs_26.c:10258 | `data_gap_80099FDC` | `0x8009A4E0` | `0xCB582000` | `opcode_0x32` | `lwc2        $24, 0x2000($k0)` |
| funcs_26.c:10260 | `data_gap_80099FDC` | `0x8009A4E4` | `0x4A0D1900` | `opcode_0x12` | `.word       0x4A0D1900                   # INVALID     $s0, $t5, 0x1900 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10264 | `data_gap_80099FDC` | `0x8009A4EC` | `0x4A1CCE4F` | `opcode_0x12` | `.word       0x4A1CCE4F                   # INVALID     $s0, $gp, -0x31B1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10268 | `data_gap_80099FDC` | `0x8009A4F4` | `0x4A0C18C0` | `opcode_0x12` | `.word       0x4A0C18C0                   # INVALID     $s0, $t4, 0x18C0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10270 | `data_gap_80099FDC` | `0x8009A4F8` | `0x4A1CC60F` | `opcode_0x12` | `.word       0x4A1CC60F                   # INVALID     $s0, $gp, -0x39F1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10272 | `data_gap_80099FDC` | `0x8009A4FC` | `0x4B759CD0` | `opcode_0x12` | `.word       0x4B759CD0                   # INVALID     $k1, $s5, -0x6330 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10274 | `data_gap_80099FDC` | `0x8009A500` | `0x4B749494` | `opcode_0x12` | `.word       0x4B749494                   # INVALID     $k1, $s4, -0x6B6C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10276 | `data_gap_80099FDC` | `0x8009A504` | `0x4B357BD4` | `opcode_0x12` | `.word       0x4B357BD4                   # INVALID     $t9, $s5, 0x7BD4 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10278 | `data_gap_80099FDC` | `0x8009A508` | `0xEB9A207F` | `opcode_0x3A` | `swc2        $26, 0x207F($gp)` |
| funcs_26.c:10280 | `data_gap_80099FDC` | `0x8009A50C` | `0x4B346B50` | `opcode_0x12` | `.word       0x4B346B50                   # INVALID     $t9, $s4, 0x6B50 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10282 | `data_gap_80099FDC` | `0x8009A510` | `0xEB39207F` | `opcode_0x3A` | `swc2        $25, 0x207F($t9)` |
| funcs_26.c:10284 | `data_gap_80099FDC` | `0x8009A514` | `0x4B157394` | `opcode_0x12` | `.word       0x4B157394                   # INVALID     $t8, $s5, 0x7394 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10286 | `data_gap_80099FDC` | `0x8009A518` | `0xEB58207F` | `opcode_0x3A` | `swc2        $24, 0x207F($k0)` |
| funcs_26.c:10288 | `data_gap_80099FDC` | `0x8009A51C` | `0x4B146310` | `opcode_0x12` | `.word       0x4B146310                   # INVALID     $t8, $s4, 0x6310 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10290 | `data_gap_80099FDC` | `0x8009A520` | `0xEB7B207F` | `opcode_0x3A` | `swc2        $27, 0x207F($k1)` |
| funcs_26.c:10292 | `data_gap_80099FDC` | `0x8009A524` | `0x4B558C54` | `opcode_0x12` | `.word       0x4B558C54                   # INVALID     $k0, $s5, -0x73AC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10296 | `data_gap_80099FDC` | `0x8009A52C` | `0x4B548410` | `opcode_0x12` | `.word       0x4B548410                   # INVALID     $k0, $s4, -0x7BF0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10300 | `data_gap_80099FDC` | `0x8009A52C` | `0x4B548410` | `opcode_0x12` | `.word       0x4B548410                   # INVALID     $k0, $s4, -0x7BF0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10312 | `data_gap_80099FDC` | `0x8009A544` | `0xE8A30F00` | `opcode_0x3A` | `swc2        $3, 0xF00($a1)` |
| funcs_26.c:10314 | `data_gap_80099FDC` | `0x8009A548` | `0xE8A40F01` | `opcode_0x3A` | `swc2        $4, 0xF01($a1)` |
| funcs_26.c:10316 | `data_gap_80099FDC` | `0x8009A54C` | `0xE8A50F02` | `opcode_0x3A` | `swc2        $5, 0xF02($a1)` |
| funcs_26.c:10319 | `data_gap_80099FDC` | `0x8009A554` | `0xE8A60F03` | `opcode_0x3A` | `swc2        $6, 0xF03($a1)` |
| funcs_26.c:10323 | `data_gap_80099FDC` | `0x8009A554` | `0xE8A60F03` | `opcode_0x3A` | `swc2        $6, 0xF03($a1)` |
| funcs_26.c:10325 | `data_gap_80099FDC` | `0x8009A558` | `0x489FFE00` | `opcode_0x12` | `.word       0x489FFE00                   # mtc2        $ra, $31 # 00000600 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10331 | `data_gap_80099FDC` | `0x8009A564` | `0x4887F800` | `opcode_0x12` | `mtc2        $a3, $31` |
| funcs_26.c:10337 | `data_gap_80099FDC` | `0x8009A570` | `0x48863900` | `opcode_0x12` | `.word       0x48863900                   # mtc2        $a2, $7 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10341 | `data_gap_80099FDC` | `0x8009A578` | `0x48863800` | `opcode_0x12` | `mtc2        $a2, $7` |
| funcs_26.c:10373 | `data_gap_80099FDC` | `0x8009A5B0` | `0x09000597` | `j` | `j           L_8400165C` |
| funcs_26.c:10380 | `data_gap_80099FDC` | `0x8009A5BC` | `0x4886F900` | `opcode_0x12` | `.word       0x4886F900                   # mtc2        $a2, $31 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10382 | `data_gap_80099FDC` | `0x8009A5C0` | `0x4885FA00` | `opcode_0x12` | `.word       0x4885FA00                   # mtc2        $a1, $31 # 00000200 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10386 | `data_gap_80099FDC` | `0x8009A5C8` | `0x4885FB00` | `opcode_0x12` | `.word       0x4885FB00                   # mtc2        $a1, $31 # 00000300 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10390 | `data_gap_80099FDC` | `0x8009A5D0` | `0x4885FC00` | `opcode_0x12` | `.word       0x4885FC00                   # mtc2        $a1, $31 # 00000400 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10394 | `data_gap_80099FDC` | `0x8009A5D8` | `0x4885FD00` | `opcode_0x12` | `.word       0x4885FD00                   # mtc2        $a1, $31 # 00000500 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10398 | `data_gap_80099FDC` | `0x8009A5E0` | `0x4885E000` | `opcode_0x12` | `mtc2        $a1, $28` |
| funcs_26.c:10400 | `data_gap_80099FDC` | `0x8009A5E4` | `0x4B1C0710` | `opcode_0x12` | `.word       0x4B1C0710                   # INVALID     $t8, $gp, 0x710 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10420 | `data_gap_80099FDC` | `0x8009A5FC` | `0x4A001890` | `opcode_0x12` | `.word       0x4A001890                   # INVALID     $s0, $zero, 0x1890 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10422 | `data_gap_80099FDC` | `0x8009A600` | `0x4A002050` | `opcode_0x12` | `.word       0x4A002050                   # INVALID     $s0, $zero, 0x2050 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10424 | `data_gap_80099FDC` | `0x8009A604` | `0x4B3F08D1` | `opcode_0x12` | `.word       0x4B3F08D1                   # INVALID     $t9, $ra, 0x8D1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10426 | `data_gap_80099FDC` | `0x8009A608` | `0x4B5F18D0` | `opcode_0x12` | `.word       0x4B5F18D0                   # INVALID     $k0, $ra, 0x18D0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10428 | `data_gap_80099FDC` | `0x8009A60C` | `0x4B3F0860` | `opcode_0x12` | `.word       0x4B3F0860                   # INVALID     $t9, $ra, 0x860 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10430 | `data_gap_80099FDC` | `0x8009A610` | `0x4A030867` | `opcode_0x12` | `.word       0x4A030867                   # INVALID     $s0, $v1, 0x867 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10432 | `data_gap_80099FDC` | `0x8009A614` | `0x4B7F08C6` | `opcode_0x12` | `.word       0x4B7F08C6                   # INVALID     $k1, $ra, 0x8C6 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10434 | `data_gap_80099FDC` | `0x8009A618` | `0x4BBF1104` | `opcode_0x12` | `.word       0x4BBF1104                   # INVALID     $sp, $ra, 0x1104 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10436 | `data_gap_80099FDC` | `0x8009A61C` | `0x4B9F2106` | `opcode_0x12` | `.word       0x4B9F2106                   # INVALID     $gp, $ra, 0x2106 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10438 | `data_gap_80099FDC` | `0x8009A620` | `0x4B1FE10E` | `opcode_0x12` | `.word       0x4B1FE10E                   # INVALID     $t8, $ra, -0x1EF2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10442 | `data_gap_80099FDC` | `0x8009A628` | `0xE8232000` | `opcode_0x3A` | `swc2        $3, 0x2000($at)` |
| funcs_26.c:10444 | `data_gap_80099FDC` | `0x8009A62C` | `0xE8242001` | `opcode_0x3A` | `swc2        $4, 0x2001($at)` |
| funcs_26.c:10478 | `data_gap_80099FDC` | `0x8009A670` | `0x481FFE00` | `opcode_0x12` | `.word       0x481FFE00                   # mfc2        $ra, $31 # 00000600 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10494 | `data_gap_80099FDC` | `0x8009A68C` | `0x4A08422C` | `opcode_0x12` | `.word       0x4A08422C                   # INVALID     $s0, $t0, 0x422C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10496 | `data_gap_80099FDC` | `0x8009A690` | `0x48854000` | `opcode_0x12` | `mtc2        $a1, $8` |
| funcs_26.c:10498 | `data_gap_80099FDC` | `0x8009A694` | `0x48854400` | `opcode_0x12` | `.word       0x48854400                   # mtc2        $a1, $8 # 00000400 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10500 | `data_gap_80099FDC` | `0x8009A698` | `0x4A094A6C` | `opcode_0x12` | `.word       0x4A094A6C                   # INVALID     $s0, $t1, 0x4A6C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10502 | `data_gap_80099FDC` | `0x8009A69C` | `0x48854900` | `opcode_0x12` | `.word       0x48854900                   # mtc2        $a1, $9 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10504 | `data_gap_80099FDC` | `0x8009A6A0` | `0x48854D00` | `opcode_0x12` | `.word       0x48854D00                   # mtc2        $a1, $9 # 00000500 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10506 | `data_gap_80099FDC` | `0x8009A6A4` | `0x4A0A52AC` | `opcode_0x12` | `.word       0x4A0A52AC                   # INVALID     $s0, $t2, 0x52AC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10508 | `data_gap_80099FDC` | `0x8009A6A8` | `0x48855200` | `opcode_0x12` | `.word       0x48855200                   # mtc2        $a1, $10 # 00000200 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10510 | `data_gap_80099FDC` | `0x8009A6AC` | `0x48855600` | `opcode_0x12` | `.word       0x48855600                   # mtc2        $a1, $10 # 00000600 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10512 | `data_gap_80099FDC` | `0x8009A6B0` | `0x4A0B5AEC` | `opcode_0x12` | `.word       0x4A0B5AEC                   # INVALID     $s0, $t3, 0x5AEC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10514 | `data_gap_80099FDC` | `0x8009A6B4` | `0x48855B00` | `opcode_0x12` | `.word       0x48855B00                   # mtc2        $a1, $11 # 00000300 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10517 | `data_gap_80099FDC` | `0x8009A6BC` | `0x48855F00` | `opcode_0x12` | `.word       0x48855F00                   # mtc2        $a1, $11 # 00000700 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10520 | `data_gap_80099FDC` | `0x8009A6BC` | `0x48855F00` | `opcode_0x12` | `.word       0x48855F00                   # mtc2        $a1, $11 # 00000700 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10534 | `data_gap_80099FDC` | `0x8009A6D0` | `0x4A001B90` | `opcode_0x12` | `.word       0x4A001B90                   # INVALID     $s0, $zero, 0x1B90 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10536 | `data_gap_80099FDC` | `0x8009A6D4` | `0x4A002310` | `opcode_0x12` | `.word       0x4A002310                   # INVALID     $s0, $zero, 0x2310 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10540 | `data_gap_80099FDC` | `0x8009A6DC` | `0x4886A800` | `opcode_0x12` | `mtc2        $a2, $21` |
| funcs_26.c:10544 | `data_gap_80099FDC` | `0x8009A6E4` | `0x4886A000` | `opcode_0x12` | `mtc2        $a2, $20` |
| funcs_26.c:10556 | `data_gap_80099FDC` | `0x8009A6F4` | `0x4A001BD0` | `opcode_0x12` | `.word       0x4A001BD0                   # INVALID     $s0, $zero, 0x1BD0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10558 | `data_gap_80099FDC` | `0x8009A6F8` | `0x4A002350` | `opcode_0x12` | `.word       0x4A002350                   # INVALID     $s0, $zero, 0x2350 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10562 | `data_gap_80099FDC` | `0x8009A700` | `0x4886A900` | `opcode_0x12` | `.word       0x4886A900                   # mtc2        $a2, $21 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10566 | `data_gap_80099FDC` | `0x8009A708` | `0x4886A100` | `opcode_0x12` | `.word       0x4886A100                   # mtc2        $a2, $20 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10578 | `data_gap_80099FDC` | `0x8009A718` | `0x4A001C50` | `opcode_0x12` | `.word       0x4A001C50                   # INVALID     $s0, $zero, 0x1C50 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10580 | `data_gap_80099FDC` | `0x8009A71C` | `0x4A002410` | `opcode_0x12` | `.word       0x4A002410                   # INVALID     $s0, $zero, 0x2410 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10584 | `data_gap_80099FDC` | `0x8009A724` | `0x4886AA00` | `opcode_0x12` | `.word       0x4886AA00                   # mtc2        $a2, $21 # 00000200 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10588 | `data_gap_80099FDC` | `0x8009A72C` | `0x4886A200` | `opcode_0x12` | `.word       0x4886A200                   # mtc2        $a2, $20 # 00000200 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10600 | `data_gap_80099FDC` | `0x8009A73C` | `0x4A001CD0` | `opcode_0x12` | `.word       0x4A001CD0                   # INVALID     $s0, $zero, 0x1CD0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10602 | `data_gap_80099FDC` | `0x8009A740` | `0x4A002490` | `opcode_0x12` | `.word       0x4A002490                   # INVALID     $s0, $zero, 0x2490 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10606 | `data_gap_80099FDC` | `0x8009A748` | `0x4886AB00` | `opcode_0x12` | `.word       0x4886AB00                   # mtc2        $a2, $21 # 00000300 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10611 | `data_gap_80099FDC` | `0x8009A754` | `0x4886A300` | `opcode_0x12` | `.word       0x4886A300                   # mtc2        $a2, $20 # 00000300 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10615 | `data_gap_80099FDC` | `0x8009A754` | `0x4886A300` | `opcode_0x12` | `.word       0x4886A300                   # mtc2        $a2, $20 # 00000300 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10617 | `data_gap_80099FDC` | `0x8009A758` | `0x48861800` | `opcode_0x12` | `mtc2        $a2, $3` |
| funcs_26.c:10621 | `data_gap_80099FDC` | `0x8009A760` | `0x48882000` | `opcode_0x12` | `mtc2        $t0, $4` |
| funcs_26.c:10623 | `data_gap_80099FDC` | `0x8009A764` | `0xC8052001` | `opcode_0x32` | `lwc2        $5, 0x2001($zero)` |
| funcs_26.c:10625 | `data_gap_80099FDC` | `0x8009A768` | `0x4B0300D0` | `opcode_0x12` | `.word       0x4B0300D0                   # INVALID     $t8, $v1, 0xD0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10627 | `data_gap_80099FDC` | `0x8009A76C` | `0x4B040110` | `opcode_0x12` | `.word       0x4B040110                   # INVALID     $t8, $a0, 0x110 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10629 | `data_gap_80099FDC` | `0x8009A770` | `0x48853000` | `opcode_0x12` | `mtc2        $a1, $6` |
| funcs_26.c:10633 | `data_gap_80099FDC` | `0x8009A778` | `0x48883100` | `opcode_0x12` | `.word       0x48883100                   # mtc2        $t0, $6 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10635 | `data_gap_80099FDC` | `0x8009A77C` | `0x4A0518C6` | `opcode_0x12` | `.word       0x4A0518C6                   # INVALID     $s0, $a1, 0x18C6 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10637 | `data_gap_80099FDC` | `0x8009A780` | `0x4A05210F` | `opcode_0x12` | `.word       0x4A05210F                   # INVALID     $s0, $a1, 0x210F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10639 | `data_gap_80099FDC` | `0x8009A784` | `0x4B0618D4` | `opcode_0x12` | `.word       0x4B0618D4                   # INVALID     $t8, $a2, 0x18D4 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10642 | `data_gap_80099FDC` | `0x8009A78C` | `0x4B262110` | `opcode_0x12` | `.word       0x4B262110                   # INVALID     $t9, $a2, 0x2110 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10645 | `data_gap_80099FDC` | `0x8009A78C` | `0x4B262110` | `opcode_0x12` | `.word       0x4B262110                   # INVALID     $t9, $a2, 0x2110 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10651 | `data_gap_80099FDC` | `0x8009A798` | `0x48881800` | `opcode_0x12` | `mtc2        $t0, $3` |
| funcs_26.c:10721 | `data_gap_80099FDC` | `0x8009A7FC` | `0x488B1C00` | `opcode_0x12` | `.word       0x488B1C00                   # mtc2        $t3, $3 # 00000400 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10723 | `data_gap_80099FDC` | `0x8009A800` | `0x488C1D00` | `opcode_0x12` | `.word       0x488C1D00                   # mtc2        $t4, $3 # 00000500 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10725 | `data_gap_80099FDC` | `0x8009A804` | `0x4B830114` | `opcode_0x12` | `.word       0x4B830114                   # INVALID     $gp, $v1, 0x114 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10727 | `data_gap_80099FDC` | `0x8009A808` | `0x4BA30154` | `opcode_0x12` | `.word       0x4BA30154                   # INVALID     $sp, $v1, 0x154 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10732 | `data_gap_80099FDC` | `0x8009A810` | `0xC8A12000` | `opcode_0x32` | `lwc2        $1, 0x2000($a1)` |
| funcs_26.c:10734 | `data_gap_80099FDC` | `0x8009A814` | `0xC8C22000` | `opcode_0x32` | `lwc2        $2, 0x2000($a2)` |
| funcs_26.c:10740 | `data_gap_80099FDC` | `0x8009A820` | `0x4B032187` | `opcode_0x12` | `.word       0x4B032187                   # INVALID     $t8, $v1, 0x2187 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10742 | `data_gap_80099FDC` | `0x8009A824` | `0x4B03084F` | `opcode_0x12` | `.word       0x4B03084F                   # INVALID     $t8, $v1, 0x84F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10744 | `data_gap_80099FDC` | `0x8009A828` | `0x4B032987` | `opcode_0x12` | `.word       0x4B032987                   # INVALID     $t8, $v1, 0x2987 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10746 | `data_gap_80099FDC` | `0x8009A82C` | `0x4B03108F` | `opcode_0x12` | `.word       0x4B03108F                   # INVALID     $t8, $v1, 0x108F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10748 | `data_gap_80099FDC` | `0x8009A830` | `0xE8E10800` | `opcode_0x3A` | `swc2        $1, 0x800($a3)` |
| funcs_26.c:10750 | `data_gap_80099FDC` | `0x8009A834` | `0xE8E20801` | `opcode_0x3A` | `swc2        $2, 0x801($a3)` |
| funcs_26.c:10752 | `data_gap_80099FDC` | `0x8009A838` | `0xE8E10902` | `opcode_0x3A` | `swc2        $1, 0x902($a3)` |
| funcs_26.c:10754 | `data_gap_80099FDC` | `0x8009A83C` | `0xE8E20903` | `opcode_0x3A` | `swc2        $2, 0x903($a3)` |
| funcs_26.c:10756 | `data_gap_80099FDC` | `0x8009A840` | `0xE8E10A04` | `opcode_0x3A` | `swc2        $1, 0xA04($a3)` |
| funcs_26.c:10758 | `data_gap_80099FDC` | `0x8009A844` | `0xE8E20A05` | `opcode_0x3A` | `swc2        $2, 0xA05($a3)` |
| funcs_26.c:10760 | `data_gap_80099FDC` | `0x8009A848` | `0xE8E10B06` | `opcode_0x3A` | `swc2        $1, 0xB06($a3)` |
| funcs_26.c:10762 | `data_gap_80099FDC` | `0x8009A84C` | `0xE8E20B07` | `opcode_0x3A` | `swc2        $2, 0xB07($a3)` |
| funcs_26.c:10764 | `data_gap_80099FDC` | `0x8009A850` | `0xE8E10C08` | `opcode_0x3A` | `swc2        $1, 0xC08($a3)` |
| funcs_26.c:10766 | `data_gap_80099FDC` | `0x8009A854` | `0xE8E20C09` | `opcode_0x3A` | `swc2        $2, 0xC09($a3)` |
| funcs_26.c:10768 | `data_gap_80099FDC` | `0x8009A858` | `0xE8E10D0A` | `opcode_0x3A` | `swc2        $1, 0xD0A($a3)` |
| funcs_26.c:10770 | `data_gap_80099FDC` | `0x8009A85C` | `0xE8E20D0B` | `opcode_0x3A` | `swc2        $2, 0xD0B($a3)` |
| funcs_26.c:10772 | `data_gap_80099FDC` | `0x8009A860` | `0xE8E10E0C` | `opcode_0x3A` | `swc2        $1, 0xE0C($a3)` |
| funcs_26.c:10774 | `data_gap_80099FDC` | `0x8009A864` | `0xE8E20E0D` | `opcode_0x3A` | `swc2        $2, 0xE0D($a3)` |
| funcs_26.c:10776 | `data_gap_80099FDC` | `0x8009A868` | `0xE8E10F0E` | `opcode_0x3A` | `swc2        $1, 0xF0E($a3)` |
| funcs_26.c:10778 | `data_gap_80099FDC` | `0x8009A86C` | `0xE8E20F0F` | `opcode_0x3A` | `swc2        $2, 0xF0F($a3)` |
| funcs_26.c:10814 | `data_gap_80099FDC` | `0x8009A8A0` | `0x48852000` | `opcode_0x12` | `mtc2        $a1, $4` |
| funcs_26.c:10816 | `data_gap_80099FDC` | `0x8009A8A4` | `0x48862100` | `opcode_0x12` | `.word       0x48862100                   # mtc2        $a2, $4 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10820 | `data_gap_80099FDC` | `0x8009A8AC` | `0xC9A21801` | `opcode_0x32` | `lwc2        $2, 0x1801($t5)` |
| funcs_26.c:10822 | `data_gap_80099FDC` | `0x8009A8B0` | `0xC9A31800` | `opcode_0x32` | `lwc2        $3, 0x1800($t5)` |
| funcs_26.c:10824 | `data_gap_80099FDC` | `0x8009A8B4` | `0x4B041146` | `opcode_0x12` | `.word       0x4B041146                   # INVALID     $t8, $a0, 0x1146 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10826 | `data_gap_80099FDC` | `0x8009A8B8` | `0x4B04194F` | `opcode_0x12` | `.word       0x4B04194F                   # INVALID     $t8, $a0, 0x194F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10845 | `data_gap_80099FDC` | `0x8009A8D4` | `0xC9411800` | `opcode_0x32` | `lwc2        $1, 0x1800($t2)` |
| funcs_26.c:10847 | `data_gap_80099FDC` | `0x8009A8D8` | `0x4B04094D` | `opcode_0x12` | `.word       0x4B04094D                   # INVALID     $t8, $a0, 0x94D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10858 | `data_gap_80099FDC` | `0x8009A8E4` | `0x4B43289D` | `opcode_0x12` | `.word       0x4B43289D                   # INVALID     $k0, $v1, 0x289D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10860 | `data_gap_80099FDC` | `0x8009A8E8` | `0x4B2328DD` | `opcode_0x12` | `.word       0x4B2328DD                   # INVALID     $t9, $v1, 0x28DD # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10862 | `data_gap_80099FDC` | `0x8009A8EC` | `0x4B241144` | `opcode_0x12` | `.word       0x4B241144                   # INVALID     $t9, $a0, 0x1144 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10864 | `data_gap_80099FDC` | `0x8009A8F0` | `0x4B2418CD` | `opcode_0x12` | `.word       0x4B2418CD                   # INVALID     $t9, $a0, 0x18CD # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10866 | `data_gap_80099FDC` | `0x8009A8F4` | `0x4A00288E` | `opcode_0x12` | `.word       0x4A00288E                   # INVALID     $s0, $zero, 0x288E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10868 | `data_gap_80099FDC` | `0x8009A8F8` | `0xE9A31800` | `opcode_0x3A` | `swc2        $3, 0x1800($t5)` |
| funcs_26.c:10871 | `data_gap_80099FDC` | `0x8009A900` | `0xE9A21801` | `opcode_0x3A` | `swc2        $2, 0x1801($t5)` |
| funcs_26.c:10875 | `data_gap_80099FDC` | `0x8009A900` | `0xE9A21801` | `opcode_0x3A` | `swc2        $2, 0x1801($t5)` |
| funcs_26.c:10881 | `data_gap_80099FDC` | `0x8009A90C` | `0x48880800` | `opcode_0x12` | `mtc2        $t0, $1` |
| funcs_26.c:10885 | `data_gap_80099FDC` | `0x8009A914` | `0x48880900` | `opcode_0x12` | `.word       0x48880900                   # mtc2        $t0, $1 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10923 | `data_gap_80099FDC` | `0x8009A94C` | `0x488A0F00` | `opcode_0x12` | `.word       0x488A0F00                   # mtc2        $t2, $1 # 00000700 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10931 | `data_gap_80099FDC` | `0x8009A95C` | `0x4BE10194` | `opcode_0x12` | `.word       0x4BE10194                   # INVALID     $ra, $at, 0x194 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10936 | `data_gap_80099FDC` | `0x8009A964` | `0xC9822000` | `opcode_0x32` | `lwc2        $2, 0x2000($t4)` |
| funcs_26.c:10938 | `data_gap_80099FDC` | `0x8009A968` | `0x4B011147` | `opcode_0x12` | `.word       0x4B011147                   # INVALID     $t8, $at, 0x1147 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10940 | `data_gap_80099FDC` | `0x8009A96C` | `0x4B0130CF` | `opcode_0x12` | `.word       0x4B0130CF                   # INVALID     $t8, $at, 0x30CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10942 | `data_gap_80099FDC` | `0x8009A970` | `0xE9802000` | `opcode_0x3A` | `swc2        $0, 0x2000($t4)` |
| funcs_26.c:10944 | `data_gap_80099FDC` | `0x8009A974` | `0x4B211147` | `opcode_0x12` | `.word       0x4B211147                   # INVALID     $t9, $at, 0x1147 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10946 | `data_gap_80099FDC` | `0x8009A978` | `0x4B21310F` | `opcode_0x12` | `.word       0x4B21310F                   # INVALID     $t9, $at, 0x310F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10954 | `data_gap_80099FDC` | `0x8009A988` | `0xE9A3207F` | `opcode_0x3A` | `swc2        $3, 0x207F($t5)` |
| funcs_26.c:10960 | `data_gap_80099FDC` | `0x8009A994` | `0xE9C4207F` | `opcode_0x3A` | `swc2        $4, 0x207F($t6)` |
| funcs_26.c:10964 | `data_gap_80099FDC` | `0x8009A994` | `0xE9C4207F` | `opcode_0x3A` | `swc2        $4, 0x207F($t6)` |
| funcs_26.c:10995 | `data_gap_80099FDC` | `0x8009A9C4` | `0x4A01086C` | `opcode_0x12` | `.word       0x4A01086C                   # INVALID     $s0, $at, 0x86C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:10997 | `data_gap_80099FDC` | `0x8009A9C8` | `0x4A0210AC` | `opcode_0x12` | `.word       0x4A0210AC                   # INVALID     $s0, $v0, 0x10AC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11003 | `data_gap_80099FDC` | `0x8009A9D4` | `0x48859B00` | `opcode_0x12` | `.word       0x48859B00                   # mtc2        $a1, $19 # 00000300 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11005 | `data_gap_80099FDC` | `0x8009A9D8` | `0x48869C00` | `opcode_0x12` | `.word       0x48869C00                   # mtc2        $a2, $19 # 00000400 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11007 | `data_gap_80099FDC` | `0x8009A9DC` | `0xC8011800` | `opcode_0x32` | `lwc2        $1, 0x1800($zero)` |
| funcs_26.c:11009 | `data_gap_80099FDC` | `0x8009A9E0` | `0xC8021C00` | `opcode_0x32` | `lwc2        $2, 0x1C00($zero)` |
| funcs_26.c:11011 | `data_gap_80099FDC` | `0x8009A9E4` | `0xC8031801` | `opcode_0x32` | `lwc2        $3, 0x1801($zero)` |
| funcs_26.c:11013 | `data_gap_80099FDC` | `0x8009A9E8` | `0xC8031C01` | `opcode_0x32` | `lwc2        $3, 0x1C01($zero)` |
| funcs_26.c:11016 | `data_gap_80099FDC` | `0x8009A9EC` | `0x4A05296C` | `opcode_0x12` | `.word       0x4A05296C                   # INVALID     $s0, $a1, 0x296C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11018 | `data_gap_80099FDC` | `0x8009A9F0` | `0xC9541800` | `opcode_0x32` | `lwc2        $20, 0x1800($t2)` |
| funcs_26.c:11020 | `data_gap_80099FDC` | `0x8009A9F4` | `0x4A0631AC` | `opcode_0x12` | `.word       0x4A0631AC                   # INVALID     $s0, $a2, 0x31AC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11024 | `data_gap_80099FDC` | `0x8009A9FC` | `0x4A0739EC` | `opcode_0x12` | `.word       0x4A0739EC                   # INVALID     $s0, $a3, 0x39EC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11026 | `data_gap_80099FDC` | `0x8009AA00` | `0xC9731000` | `opcode_0x32` | `lwc2        $19, 0x1000($t3)` |
| funcs_26.c:11028 | `data_gap_80099FDC` | `0x8009AA04` | `0x4A08422C` | `opcode_0x12` | `.word       0x4A08422C                   # INVALID     $s0, $t0, 0x422C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11032 | `data_gap_80099FDC` | `0x8009AA0C` | `0x4A094A6C` | `opcode_0x12` | `.word       0x4A094A6C                   # INVALID     $s0, $t1, 0x4A6C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11036 | `data_gap_80099FDC` | `0x8009AA14` | `0x4A0A52AC` | `opcode_0x12` | `.word       0x4A0A52AC                   # INVALID     $s0, $t2, 0x52AC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11040 | `data_gap_80099FDC` | `0x8009AA1C` | `0x4A0B5AEC` | `opcode_0x12` | `.word       0x4A0B5AEC                   # INVALID     $s0, $t3, 0x5AEC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11042 | `data_gap_80099FDC` | `0x8009AA20` | `0x4A0C632C` | `opcode_0x12` | `.word       0x4A0C632C                   # INVALID     $s0, $t4, 0x632C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11044 | `data_gap_80099FDC` | `0x8009AA24` | `0x4A0D6B6C` | `opcode_0x12` | `.word       0x4A0D6B6C                   # INVALID     $s0, $t5, 0x6B6C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11046 | `data_gap_80099FDC` | `0x8009AA28` | `0x4B140BE8` | `opcode_0x12` | `.word       0x4B140BE8                   # INVALID     $t8, $s4, 0xBE8 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11048 | `data_gap_80099FDC` | `0x8009AA2C` | `0x4B341428` | `opcode_0x12` | `.word       0x4B341428                   # INVALID     $t9, $s4, 0x1428 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11050 | `data_gap_80099FDC` | `0x8009AA30` | `0x4B540C68` | `opcode_0x12` | `.word       0x4B540C68                   # INVALID     $k0, $s4, 0xC68 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11052 | `data_gap_80099FDC` | `0x8009AA34` | `0x4B7414A8` | `opcode_0x12` | `.word       0x4B7414A8                   # INVALID     $k1, $s4, 0x14A8 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11054 | `data_gap_80099FDC` | `0x8009AA38` | `0x4A037BC6` | `opcode_0x12` | `.word       0x4A037BC6                   # INVALID     $s0, $v1, 0x7BC6 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11056 | `data_gap_80099FDC` | `0x8009AA3C` | `0xC9541801` | `opcode_0x32` | `lwc2        $20, 0x1801($t2)` |
| funcs_26.c:11058 | `data_gap_80099FDC` | `0x8009AA40` | `0x4A0385CE` | `opcode_0x12` | `.word       0x4A0385CE                   # INVALID     $s0, $v1, -0x7A32 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11060 | `data_gap_80099FDC` | `0x8009AA44` | `0x4A038C46` | `opcode_0x12` | `.word       0x4A038C46                   # INVALID     $s0, $v1, -0x73BA # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11062 | `data_gap_80099FDC` | `0x8009AA48` | `0x4A03960E` | `opcode_0x12` | `.word       0x4A03960E                   # INVALID     $s0, $v1, -0x69F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11064 | `data_gap_80099FDC` | `0x8009AA4C` | `0x4B140BE8` | `opcode_0x12` | `.word       0x4B140BE8                   # INVALID     $t8, $s4, 0xBE8 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11068 | `data_gap_80099FDC` | `0x8009AA54` | `0x4B341428` | `opcode_0x12` | `.word       0x4B341428                   # INVALID     $t9, $s4, 0x1428 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11072 | `data_gap_80099FDC` | `0x8009AA5C` | `0x4B540C68` | `opcode_0x12` | `.word       0x4B540C68                   # INVALID     $k0, $s4, 0xC68 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11076 | `data_gap_80099FDC` | `0x8009AA64` | `0x4B7414A8` | `opcode_0x12` | `.word       0x4B7414A8                   # INVALID     $k1, $s4, 0x14A8 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11080 | `data_gap_80099FDC` | `0x8009AA6C` | `0x4A037BC6` | `opcode_0x12` | `.word       0x4A037BC6                   # INVALID     $s0, $v1, 0x7BC6 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11082 | `data_gap_80099FDC` | `0x8009AA70` | `0x48859A00` | `opcode_0x12` | `.word       0x48859A00                   # mtc2        $a1, $19 # 00000200 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11084 | `data_gap_80099FDC` | `0x8009AA74` | `0x4A03864E` | `opcode_0x12` | `.word       0x4A03864E                   # INVALID     $s0, $v1, -0x79B2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11086 | `data_gap_80099FDC` | `0x8009AA78` | `0x4A038C46` | `opcode_0x12` | `.word       0x4A038C46                   # INVALID     $s0, $v1, -0x73BA # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11090 | `data_gap_80099FDC` | `0x8009AA80` | `0x4A03968E` | `opcode_0x12` | `.word       0x4A03968E                   # INVALID     $s0, $v1, -0x6972 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11094 | `data_gap_80099FDC` | `0x8009AA80` | `0x4A03968E` | `opcode_0x12` | `.word       0x4A03968E                   # INVALID     $s0, $v1, -0x6972 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11096 | `data_gap_80099FDC` | `0x8009AA84` | `0x4B53BDC5` | `opcode_0x12` | `.word       0x4B53BDC5                   # INVALID     $k0, $s3, -0x423B # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11098 | `data_gap_80099FDC` | `0x8009AA88` | `0x4B53C605` | `opcode_0x12` | `.word       0x4B53C605                   # INVALID     $k0, $s3, -0x39FB # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11100 | `data_gap_80099FDC` | `0x8009AA8C` | `0x4B53CE45` | `opcode_0x12` | `.word       0x4B53CE45                   # INVALID     $k0, $s3, -0x31BB # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11102 | `data_gap_80099FDC` | `0x8009AA90` | `0x4B53D685` | `opcode_0x12` | `.word       0x4B53D685                   # INVALID     $k0, $s3, -0x297B # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11107 | `data_gap_80099FDC` | `0x8009AA98` | `0xC8A52801` | `opcode_0x32` | `lwc2        $5, 0x2801($a1)` |
| funcs_26.c:11109 | `data_gap_80099FDC` | `0x8009AA9C` | `0x4B934173` | `opcode_0x12` | `.word       0x4B934173                   # INVALID     $gp, $s3, 0x4173 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11111 | `data_gap_80099FDC` | `0x8009AAA0` | `0xC8A62802` | `opcode_0x32` | `lwc2        $6, 0x2802($a1)` |
| funcs_26.c:11113 | `data_gap_80099FDC` | `0x8009AAA4` | `0x4B9349B3` | `opcode_0x12` | `.word       0x4B9349B3                   # INVALID     $gp, $s3, 0x49B3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11117 | `data_gap_80099FDC` | `0x8009AAAC` | `0xC8A72802` | `opcode_0x32` | `lwc2        $7, 0x2802($a1)` |
| funcs_26.c:11119 | `data_gap_80099FDC` | `0x8009AAB0` | `0x4B9351F3` | `opcode_0x12` | `.word       0x4B9351F3                   # INVALID     $gp, $s3, 0x51F3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11123 | `data_gap_80099FDC` | `0x8009AAB8` | `0xC8A82802` | `opcode_0x32` | `lwc2        $8, 0x2802($a1)` |
| funcs_26.c:11125 | `data_gap_80099FDC` | `0x8009AABC` | `0x4B935A33` | `opcode_0x12` | `.word       0x4B935A33                   # INVALID     $gp, $s3, 0x5A33 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11129 | `data_gap_80099FDC` | `0x8009AAC4` | `0xC8A92802` | `opcode_0x32` | `lwc2        $9, 0x2802($a1)` |
| funcs_26.c:11131 | `data_gap_80099FDC` | `0x8009AAC8` | `0x4B936273` | `opcode_0x12` | `.word       0x4B936273                   # INVALID     $gp, $s3, 0x6273 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11135 | `data_gap_80099FDC` | `0x8009AAD0` | `0xC8AA2802` | `opcode_0x32` | `lwc2        $10, 0x2802($a1)` |
| funcs_26.c:11137 | `data_gap_80099FDC` | `0x8009AAD4` | `0x4B936AB3` | `opcode_0x12` | `.word       0x4B936AB3                   # INVALID     $gp, $s3, 0x6AB3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11141 | `data_gap_80099FDC` | `0x8009AADC` | `0xC8AB2802` | `opcode_0x32` | `lwc2        $11, 0x2802($a1)` |
| funcs_26.c:11143 | `data_gap_80099FDC` | `0x8009AAE0` | `0x4B9372F3` | `opcode_0x12` | `.word       0x4B9372F3                   # INVALID     $gp, $s3, 0x72F3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11145 | `data_gap_80099FDC` | `0x8009AAE4` | `0x4B937B33` | `opcode_0x12` | `.word       0x4B937B33                   # INVALID     $gp, $s3, 0x7B33 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11147 | `data_gap_80099FDC` | `0x8009AAE8` | `0x4B132BC7` | `opcode_0x12` | `.word       0x4B132BC7                   # INVALID     $t8, $s3, 0x2BC7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11151 | `data_gap_80099FDC` | `0x8009AAF0` | `0x4B3333CF` | `opcode_0x12` | `.word       0x4B3333CF                   # INVALID     $t9, $s3, 0x33CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11153 | `data_gap_80099FDC` | `0x8009AAF4` | `0xC9A52000` | `opcode_0x32` | `lwc2        $5, 0x2000($t5)` |
| funcs_26.c:11155 | `data_gap_80099FDC` | `0x8009AAF8` | `0x4B573BCF` | `opcode_0x12` | `.word       0x4B573BCF                   # INVALID     $k0, $s7, 0x3BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11157 | `data_gap_80099FDC` | `0x8009AAFC` | `0xC9A62001` | `opcode_0x32` | `lwc2        $6, 0x2001($t5)` |
| funcs_26.c:11159 | `data_gap_80099FDC` | `0x8009AB00` | `0x4B7743CF` | `opcode_0x12` | `.word       0x4B7743CF                   # INVALID     $k1, $s7, 0x43CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11161 | `data_gap_80099FDC` | `0x8009AB04` | `0xC8A72802` | `opcode_0x32` | `lwc2        $7, 0x2802($a1)` |
| funcs_26.c:11163 | `data_gap_80099FDC` | `0x8009AB08` | `0x4B974BCF` | `opcode_0x12` | `.word       0x4B974BCF                   # INVALID     $gp, $s7, 0x4BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11167 | `data_gap_80099FDC` | `0x8009AB10` | `0x4BB753CF` | `opcode_0x12` | `.word       0x4BB753CF                   # INVALID     $sp, $s7, 0x53CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11169 | `data_gap_80099FDC` | `0x8009AB14` | `0xC8A82802` | `opcode_0x32` | `lwc2        $8, 0x2802($a1)` |
| funcs_26.c:11171 | `data_gap_80099FDC` | `0x8009AB18` | `0x4BD75BCF` | `opcode_0x12` | `.word       0x4BD75BCF                   # INVALID     $fp, $s7, 0x5BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11175 | `data_gap_80099FDC` | `0x8009AB20` | `0x4BF763CF` | `opcode_0x12` | `.word       0x4BF763CF                   # INVALID     $ra, $s7, 0x63CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11177 | `data_gap_80099FDC` | `0x8009AB24` | `0xC8A92802` | `opcode_0x32` | `lwc2        $9, 0x2802($a1)` |
| funcs_26.c:11179 | `data_gap_80099FDC` | `0x8009AB28` | `0x4B357C1D` | `opcode_0x12` | `.word       0x4B357C1D                   # INVALID     $t9, $s5, 0x7C1D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11183 | `data_gap_80099FDC` | `0x8009AB30` | `0x4B157D5D` | `opcode_0x12` | `.word       0x4B157D5D                   # INVALID     $t8, $s5, 0x7D5D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11185 | `data_gap_80099FDC` | `0x8009AB34` | `0xC8AA2802` | `opcode_0x32` | `lwc2        $10, 0x2802($a1)` |
| funcs_26.c:11187 | `data_gap_80099FDC` | `0x8009AB38` | `0x4B738406` | `opcode_0x12` | `.word       0x4B738406                   # INVALID     $k1, $s3, -0x7BFA # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11191 | `data_gap_80099FDC` | `0x8009AB40` | `0x4B73AD4F` | `opcode_0x12` | `.word       0x4B73AD4F                   # INVALID     $k1, $s3, -0x52B1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11193 | `data_gap_80099FDC` | `0x8009AB44` | `0xC8AB2802` | `opcode_0x32` | `lwc2        $11, 0x2802($a1)` |
| funcs_26.c:11195 | `data_gap_80099FDC` | `0x8009AB48` | `0x4BD52BC7` | `opcode_0x12` | `.word       0x4BD52BC7                   # INVALID     $fp, $s5, 0x2BC7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11199 | `data_gap_80099FDC` | `0x8009AB50` | `0x4BF533CF` | `opcode_0x12` | `.word       0x4BF533CF                   # INVALID     $ra, $s5, 0x33CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11201 | `data_gap_80099FDC` | `0x8009AB54` | `0xC8AC2802` | `opcode_0x32` | `lwc2        $12, 0x2802($a1)` |
| funcs_26.c:11203 | `data_gap_80099FDC` | `0x8009AB58` | `0x4B183BCF` | `opcode_0x12` | `.word       0x4B183BCF                   # INVALID     $t8, $t8, 0x3BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11207 | `data_gap_80099FDC` | `0x8009AB60` | `0x4B3843CF` | `opcode_0x12` | `.word       0x4B3843CF                   # INVALID     $t9, $t8, 0x43CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11209 | `data_gap_80099FDC` | `0x8009AB64` | `0xC8AD2802` | `opcode_0x32` | `lwc2        $13, 0x2802($a1)` |
| funcs_26.c:11211 | `data_gap_80099FDC` | `0x8009AB68` | `0x4B584BCF` | `opcode_0x12` | `.word       0x4B584BCF                   # INVALID     $k0, $t8, 0x4BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11213 | `data_gap_80099FDC` | `0x8009AB6C` | `0xE9952000` | `opcode_0x3A` | `swc2        $21, 0x2000($t4)` |
| funcs_26.c:11215 | `data_gap_80099FDC` | `0x8009AB70` | `0x4B7853CF` | `opcode_0x12` | `.word       0x4B7853CF                   # INVALID     $k1, $t8, 0x53CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11217 | `data_gap_80099FDC` | `0x8009AB74` | `0x4B985BCF` | `opcode_0x12` | `.word       0x4B985BCF                   # INVALID     $gp, $t8, 0x5BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11219 | `data_gap_80099FDC` | `0x8009AB78` | `0x4BB863CF` | `opcode_0x12` | `.word       0x4BB863CF                   # INVALID     $sp, $t8, 0x63CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11221 | `data_gap_80099FDC` | `0x8009AB7C` | `0x4BD86BCF` | `opcode_0x12` | `.word       0x4BD86BCF                   # INVALID     $fp, $t8, 0x6BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11223 | `data_gap_80099FDC` | `0x8009AB80` | `0x4B93C3CF` | `opcode_0x12` | `.word       0x4B93C3CF                   # INVALID     $gp, $s3, -0x3C31 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11225 | `data_gap_80099FDC` | `0x8009AB84` | `0x4B367C1D` | `opcode_0x12` | `.word       0x4B367C1D                   # INVALID     $t9, $s6, 0x7C1D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11227 | `data_gap_80099FDC` | `0x8009AB88` | `0x4B167D9D` | `opcode_0x12` | `.word       0x4B167D9D                   # INVALID     $t8, $s6, 0x7D9D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11229 | `data_gap_80099FDC` | `0x8009AB8C` | `0x4B738406` | `opcode_0x12` | `.word       0x4B738406                   # INVALID     $k1, $s3, -0x7BFA # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11231 | `data_gap_80099FDC` | `0x8009AB90` | `0x4B73B58F` | `opcode_0x12` | `.word       0x4B73B58F                   # INVALID     $k1, $s3, -0x4A71 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11233 | `data_gap_80099FDC` | `0x8009AB94` | `0x4BD62BC7` | `opcode_0x12` | `.word       0x4BD62BC7                   # INVALID     $fp, $s6, 0x2BC7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11235 | `data_gap_80099FDC` | `0x8009AB98` | `0x4BF633CF` | `opcode_0x12` | `.word       0x4BF633CF                   # INVALID     $ra, $s6, 0x33CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11237 | `data_gap_80099FDC` | `0x8009AB9C` | `0x4B193BCF` | `opcode_0x12` | `.word       0x4B193BCF                   # INVALID     $t8, $t9, 0x3BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11239 | `data_gap_80099FDC` | `0x8009ABA0` | `0x4B3943CF` | `opcode_0x12` | `.word       0x4B3943CF                   # INVALID     $t9, $t9, 0x43CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11241 | `data_gap_80099FDC` | `0x8009ABA4` | `0xE9962001` | `opcode_0x3A` | `swc2        $22, 0x2001($t4)` |
| funcs_26.c:11243 | `data_gap_80099FDC` | `0x8009ABA8` | `0x4B594BCF` | `opcode_0x12` | `.word       0x4B594BCF                   # INVALID     $k0, $t9, 0x4BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11245 | `data_gap_80099FDC` | `0x8009ABAC` | `0x4B7953CF` | `opcode_0x12` | `.word       0x4B7953CF                   # INVALID     $k1, $t9, 0x53CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11247 | `data_gap_80099FDC` | `0x8009ABB0` | `0x4B995BCF` | `opcode_0x12` | `.word       0x4B995BCF                   # INVALID     $gp, $t9, 0x5BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11249 | `data_gap_80099FDC` | `0x8009ABB4` | `0x4BB963CF` | `opcode_0x12` | `.word       0x4BB963CF                   # INVALID     $sp, $t9, 0x63CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11251 | `data_gap_80099FDC` | `0x8009ABB8` | `0x4BD96BCF` | `opcode_0x12` | `.word       0x4BD96BCF                   # INVALID     $fp, $t9, 0x6BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11253 | `data_gap_80099FDC` | `0x8009ABBC` | `0x4B93CBCF` | `opcode_0x12` | `.word       0x4B93CBCF                   # INVALID     $gp, $s3, -0x3431 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11255 | `data_gap_80099FDC` | `0x8009ABC0` | `0x4B357C1D` | `opcode_0x12` | `.word       0x4B357C1D                   # INVALID     $t9, $s5, 0x7C1D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11257 | `data_gap_80099FDC` | `0x8009ABC4` | `0x4B157D5D` | `opcode_0x12` | `.word       0x4B157D5D                   # INVALID     $t8, $s5, 0x7D5D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11259 | `data_gap_80099FDC` | `0x8009ABC8` | `0x4B738406` | `opcode_0x12` | `.word       0x4B738406                   # INVALID     $k1, $s3, -0x7BFA # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11261 | `data_gap_80099FDC` | `0x8009ABCC` | `0x4B73AD4F` | `opcode_0x12` | `.word       0x4B73AD4F                   # INVALID     $k1, $s3, -0x52B1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11263 | `data_gap_80099FDC` | `0x8009ABD0` | `0x4BD52BC7` | `opcode_0x12` | `.word       0x4BD52BC7                   # INVALID     $fp, $s5, 0x2BC7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11265 | `data_gap_80099FDC` | `0x8009ABD4` | `0x4BF533CF` | `opcode_0x12` | `.word       0x4BF533CF                   # INVALID     $ra, $s5, 0x33CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11267 | `data_gap_80099FDC` | `0x8009ABD8` | `0x4B1A3BCF` | `opcode_0x12` | `.word       0x4B1A3BCF                   # INVALID     $t8, $k0, 0x3BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11269 | `data_gap_80099FDC` | `0x8009ABDC` | `0x4B3A43CF` | `opcode_0x12` | `.word       0x4B3A43CF                   # INVALID     $t9, $k0, 0x43CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11271 | `data_gap_80099FDC` | `0x8009ABE0` | `0xE9952002` | `opcode_0x3A` | `swc2        $21, 0x2002($t4)` |
| funcs_26.c:11273 | `data_gap_80099FDC` | `0x8009ABE4` | `0x4B5A4BCF` | `opcode_0x12` | `.word       0x4B5A4BCF                   # INVALID     $k0, $k0, 0x4BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11277 | `data_gap_80099FDC` | `0x8009ABEC` | `0x4B7A53CF` | `opcode_0x12` | `.word       0x4B7A53CF                   # INVALID     $k1, $k0, 0x53CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11279 | `data_gap_80099FDC` | `0x8009ABF0` | `0x4B9A5BCF` | `opcode_0x12` | `.word       0x4B9A5BCF                   # INVALID     $gp, $k0, 0x5BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11281 | `data_gap_80099FDC` | `0x8009ABF4` | `0x4BBA63CF` | `opcode_0x12` | `.word       0x4BBA63CF                   # INVALID     $sp, $k0, 0x63CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11283 | `data_gap_80099FDC` | `0x8009ABF8` | `0x4BDA6BCF` | `opcode_0x12` | `.word       0x4BDA6BCF                   # INVALID     $fp, $k0, 0x6BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11287 | `data_gap_80099FDC` | `0x8009AC00` | `0x4B93D3CF` | `opcode_0x12` | `.word       0x4B93D3CF                   # INVALID     $gp, $s3, -0x2C31 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11291 | `data_gap_80099FDC` | `0x8009AC00` | `0x4B93D3CF` | `opcode_0x12` | `.word       0x4B93D3CF                   # INVALID     $gp, $s3, -0x2C31 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11300 | `data_gap_80099FDC` | `0x8009AC10` | `0x4B367C1D` | `opcode_0x12` | `.word       0x4B367C1D                   # INVALID     $t9, $s6, 0x7C1D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11304 | `data_gap_80099FDC` | `0x8009AC18` | `0x4B167D9D` | `opcode_0x12` | `.word       0x4B167D9D                   # INVALID     $t8, $s6, 0x7D9D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11310 | `data_gap_80099FDC` | `0x8009AC24` | `0x4B738406` | `opcode_0x12` | `.word       0x4B738406                   # INVALID     $k1, $s3, -0x7BFA # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11312 | `data_gap_80099FDC` | `0x8009AC28` | `0x4B73B58F` | `opcode_0x12` | `.word       0x4B73B58F                   # INVALID     $k1, $s3, -0x4A71 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11316 | `data_gap_80099FDC` | `0x8009AC30` | `0xE996207F` | `opcode_0x3A` | `swc2        $22, 0x207F($t4)` |
| funcs_26.c:11320 | `data_gap_80099FDC` | `0x8009AC30` | `0xE996207F` | `opcode_0x3A` | `swc2        $22, 0x207F($t4)` |
| funcs_26.c:11366 | `data_gap_80099FDC` | `0x8009AC74` | `0x488A0800` | `opcode_0x12` | `mtc2        $t2, $1` |
| funcs_26.c:11370 | `data_gap_80099FDC` | `0x8009AC7C` | `0x4B010054` | `opcode_0x12` | `.word       0x4B010054                   # INVALID     $t8, $at, 0x54 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11375 | `data_gap_80099FDC` | `0x8009AC84` | `0xE9212000` | `opcode_0x3A` | `swc2        $1, 0x2000($t1)` |
| funcs_26.c:11377 | `data_gap_80099FDC` | `0x8009AC88` | `0xE9212001` | `opcode_0x3A` | `swc2        $1, 0x2001($t1)` |
| funcs_26.c:11398 | `data_gap_80099FDC` | `0x8009ACA4` | `0xE8A02000` | `opcode_0x3A` | `swc2        $0, 0x2000($a1)` |
| funcs_26.c:11400 | `data_gap_80099FDC` | `0x8009ACA8` | `0xE8A02001` | `opcode_0x3A` | `swc2        $0, 0x2001($a1)` |
| funcs_26.c:11402 | `data_gap_80099FDC` | `0x8009ACAC` | `0xE8A02002` | `opcode_0x3A` | `swc2        $0, 0x2002($a1)` |
| funcs_26.c:11406 | `data_gap_80099FDC` | `0x8009ACB4` | `0xE8A02003` | `opcode_0x3A` | `swc2        $0, 0x2003($a1)` |
| funcs_26.c:11428 | `data_gap_80099FDC` | `0x8009ACD4` | `0x48860800` | `opcode_0x12` | `mtc2        $a2, $1` |
| funcs_26.c:11438 | `data_gap_80099FDC` | `0x8009ACE0` | `0x48860A00` | `opcode_0x12` | `.word       0x48860A00                   # mtc2        $a2, $1 # 00000200 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11539 | `data_gap_80099FDC` | `0x8009AD74` | `0xC9610900` | `opcode_0x32` | `lwc2        $1, 0x900($t3)` |
| funcs_26.c:11565 | `data_gap_80099FDC` | `0x8009AD98` | `0xC8A10905` | `opcode_0x32` | `lwc2        $1, 0x905($a1)` |
| funcs_26.c:11600 | `data_gap_80099FDC` | `0x8009ADCC` | `0xC8E32000` | `opcode_0x32` | `lwc2        $3, 0x2000($a3)` |
| funcs_26.c:11602 | `data_gap_80099FDC` | `0x8009ADD0` | `0xC8A72000` | `opcode_0x32` | `lwc2        $7, 0x2000($a1)` |
| funcs_26.c:11604 | `data_gap_80099FDC` | `0x8009ADD4` | `0xC8CC2000` | `opcode_0x32` | `lwc2        $12, 0x2000($a2)` |
| funcs_26.c:11606 | `data_gap_80099FDC` | `0x8009ADD8` | `0x4B011887` | `opcode_0x12` | `.word       0x4B011887                   # INVALID     $t8, $at, 0x1887 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11608 | `data_gap_80099FDC` | `0x8009ADDC` | `0x4B0139CF` | `opcode_0x12` | `.word       0x4B0139CF                   # INVALID     $t8, $at, 0x39CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11610 | `data_gap_80099FDC` | `0x8009ADE0` | `0x4B011887` | `opcode_0x12` | `.word       0x4B011887                   # INVALID     $t8, $at, 0x1887 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11612 | `data_gap_80099FDC` | `0x8009ADE4` | `0x4B01630F` | `opcode_0x12` | `.word       0x4B01630F                   # INVALID     $t8, $at, 0x630F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11618 | `data_gap_80099FDC` | `0x8009ADF0` | `0xE8A7207F` | `opcode_0x3A` | `swc2        $7, 0x207F($a1)` |
| funcs_26.c:11620 | `data_gap_80099FDC` | `0x8009ADF4` | `0xE8CC207F` | `opcode_0x3A` | `swc2        $12, 0x207F($a2)` |
| funcs_26.c:11643 | `data_gap_80099FDC` | `0x8009AE10` | `0xC8C32000` | `opcode_0x32` | `lwc2        $3, 0x2000($a2)` |
| funcs_26.c:11645 | `data_gap_80099FDC` | `0x8009AE14` | `0xC8C42001` | `opcode_0x32` | `lwc2        $4, 0x2001($a2)` |
| funcs_26.c:11647 | `data_gap_80099FDC` | `0x8009AE18` | `0xC8A72000` | `opcode_0x32` | `lwc2        $7, 0x2000($a1)` |
| funcs_26.c:11649 | `data_gap_80099FDC` | `0x8009AE1C` | `0xC8AC2001` | `opcode_0x32` | `lwc2        $12, 0x2001($a1)` |
| funcs_26.c:11651 | `data_gap_80099FDC` | `0x8009AE20` | `0x4B213880` | `opcode_0x12` | `.word       0x4B213880                   # INVALID     $t9, $at, 0x3880 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11653 | `data_gap_80099FDC` | `0x8009AE24` | `0x4B0118CF` | `opcode_0x12` | `.word       0x4B0118CF                   # INVALID     $t8, $at, 0x18CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11655 | `data_gap_80099FDC` | `0x8009AE28` | `0x4B216080` | `opcode_0x12` | `.word       0x4B216080                   # INVALID     $t9, $at, 0x6080 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11657 | `data_gap_80099FDC` | `0x8009AE2C` | `0x4B01210F` | `opcode_0x12` | `.word       0x4B01210F                   # INVALID     $t8, $at, 0x210F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11659 | `data_gap_80099FDC` | `0x8009AE30` | `0xE8C32000` | `opcode_0x3A` | `swc2        $3, 0x2000($a2)` |
| funcs_26.c:11661 | `data_gap_80099FDC` | `0x8009AE34` | `0xE8C42001` | `opcode_0x3A` | `swc2        $4, 0x2001($a2)` |
| funcs_26.c:11685 | `data_gap_80099FDC` | `0x8009AE58` | `0xC8EF1808` | `opcode_0x32` | `lwc2        $15, 0x1808($a3)` |
| funcs_26.c:11687 | `data_gap_80099FDC` | `0x8009AE5C` | `0xC8EF1C08` | `opcode_0x32` | `lwc2        $15, 0x1C08($a3)` |
| funcs_26.c:11691 | `data_gap_80099FDC` | `0x8009AE64` | `0xC8E21800` | `opcode_0x32` | `lwc2        $2, 0x1800($a3)` |
| funcs_26.c:11709 | `data_gap_80099FDC` | `0x8009AE88` | `0xE8A2187F` | `opcode_0x3A` | `swc2        $2, 0x187F($a1)` |
| funcs_26.c:11713 | `data_gap_80099FDC` | `0x8009AE90` | `0xC8A71800` | `opcode_0x32` | `lwc2        $7, 0x1800($a1)` |
| funcs_26.c:11715 | `data_gap_80099FDC` | `0x8009AE94` | `0x4B217BC0` | `opcode_0x12` | `.word       0x4B217BC0                   # INVALID     $t9, $at, 0x7BC0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11725 | `data_gap_80099FDC` | `0x8009AEA0` | `0xE8E71800` | `opcode_0x3A` | `swc2        $7, 0x1800($a3)` |
| funcs_26.c:11727 | `data_gap_80099FDC` | `0x8009AEA4` | `0xCA271800` | `opcode_0x32` | `lwc2        $7, 0x1800($s1)` |
| funcs_26.c:11729 | `data_gap_80099FDC` | `0x8009AEA8` | `0xCAA71C00` | `opcode_0x32` | `lwc2        $7, 0x1C00($s5)` |
| funcs_26.c:11731 | `data_gap_80099FDC` | `0x8009AEAC` | `0xCA4C1800` | `opcode_0x32` | `lwc2        $12, 0x1800($s2)` |
| funcs_26.c:11733 | `data_gap_80099FDC` | `0x8009AEB0` | `0xCACC1C00` | `opcode_0x32` | `lwc2        $12, 0x1C00($s6)` |
| funcs_26.c:11738 | `data_gap_80099FDC` | `0x8009AEB8` | `0xCA6D1800` | `opcode_0x32` | `lwc2        $13, 0x1800($s3)` |
| funcs_26.c:11740 | `data_gap_80099FDC` | `0x8009AEBC` | `0xCAED1C00` | `opcode_0x32` | `lwc2        $13, 0x1C00($s7)` |
| funcs_26.c:11742 | `data_gap_80099FDC` | `0x8009AEC0` | `0xCA8E1800` | `opcode_0x32` | `lwc2        $14, 0x1800($s4)` |
| funcs_26.c:11744 | `data_gap_80099FDC` | `0x8009AEC4` | `0xCB0E1C00` | `opcode_0x32` | `lwc2        $14, 0x1C00($t8)` |
| funcs_26.c:11746 | `data_gap_80099FDC` | `0x8009AEC8` | `0x4A0F39C0` | `opcode_0x12` | `.word       0x4A0F39C0                   # INVALID     $s0, $t7, 0x39C0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11748 | `data_gap_80099FDC` | `0x8009AECC` | `0xC8D02000` | `opcode_0x32` | `lwc2        $16, 0x2000($a2)` |
| funcs_26.c:11750 | `data_gap_80099FDC` | `0x8009AED0` | `0x4A0F6300` | `opcode_0x12` | `.word       0x4A0F6300                   # INVALID     $s0, $t7, 0x6300 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11754 | `data_gap_80099FDC` | `0x8009AED8` | `0x4A0F6B40` | `opcode_0x12` | `.word       0x4A0F6B40                   # INVALID     $s0, $t7, 0x6B40 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11758 | `data_gap_80099FDC` | `0x8009AEE0` | `0x4A0F7380` | `opcode_0x12` | `.word       0x4A0F7380                   # INVALID     $s0, $t7, 0x7380 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11762 | `data_gap_80099FDC` | `0x8009AEE8` | `0x4A6739D0` | `opcode_0x12` | `.word       0x4A6739D0                   # INVALID     $s3, $a3, 0x39D0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11766 | `data_gap_80099FDC` | `0x8009AEF0` | `0x4A6C6310` | `opcode_0x12` | `.word       0x4A6C6310                   # INVALID     $s3, $t4, 0x6310 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11770 | `data_gap_80099FDC` | `0x8009AEF8` | `0x4A6D6B50` | `opcode_0x12` | `.word       0x4A6D6B50                   # INVALID     $s3, $t5, 0x6B50 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11774 | `data_gap_80099FDC` | `0x8009AF00` | `0x4A6E7390` | `opcode_0x12` | `.word       0x4A6E7390                   # INVALID     $s3, $t6, 0x7390 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11778 | `data_gap_80099FDC` | `0x8009AF08` | `0x4AC738D0` | `opcode_0x12` | `.word       0x4AC738D0                   # INVALID     $s6, $a3, 0x38D0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11782 | `data_gap_80099FDC` | `0x8009AF10` | `0x4ACC6110` | `opcode_0x12` | `.word       0x4ACC6110                   # INVALID     $s6, $t4, 0x6110 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11786 | `data_gap_80099FDC` | `0x8009AF18` | `0x4ACD6950` | `opcode_0x12` | `.word       0x4ACD6950                   # INVALID     $s6, $t5, 0x6950 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11788 | `data_gap_80099FDC` | `0x8009AF1C` | `0xCA271800` | `opcode_0x32` | `lwc2        $7, 0x1800($s1)` |
| funcs_26.c:11790 | `data_gap_80099FDC` | `0x8009AF20` | `0x4ACE7190` | `opcode_0x12` | `.word       0x4ACE7190                   # INVALID     $s6, $t6, 0x7190 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11792 | `data_gap_80099FDC` | `0x8009AF24` | `0x4A8340C7` | `opcode_0x12` | `.word       0x4A8340C7                   # INVALID     $s4, $v1, 0x40C7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11794 | `data_gap_80099FDC` | `0x8009AF28` | `0xCAA71C00` | `opcode_0x32` | `lwc2        $7, 0x1C00($s5)` |
| funcs_26.c:11796 | `data_gap_80099FDC` | `0x8009AF2C` | `0x4A8448CF` | `opcode_0x12` | `.word       0x4A8448CF                   # INVALID     $s4, $a0, 0x48CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11798 | `data_gap_80099FDC` | `0x8009AF30` | `0xCA4C1800` | `opcode_0x32` | `lwc2        $12, 0x1800($s2)` |
| funcs_26.c:11800 | `data_gap_80099FDC` | `0x8009AF34` | `0x4A8550CF` | `opcode_0x12` | `.word       0x4A8550CF                   # INVALID     $s4, $a1, 0x50CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11802 | `data_gap_80099FDC` | `0x8009AF38` | `0xCACC1C00` | `opcode_0x32` | `lwc2        $12, 0x1C00($s6)` |
| funcs_26.c:11804 | `data_gap_80099FDC` | `0x8009AF3C` | `0x4A8658CF` | `opcode_0x12` | `.word       0x4A8658CF                   # INVALID     $s4, $a2, 0x58CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11806 | `data_gap_80099FDC` | `0x8009AF40` | `0x4B01840F` | `opcode_0x12` | `.word       0x4B01840F                   # INVALID     $t8, $at, -0x7BF1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_26.c:11812 | `data_gap_80099FDC` | `0x8009AF4C` | `0xE8D0207F` | `opcode_0x3A` | `swc2        $16, 0x207F($a2)` |
| funcs_26.c:11816 | `data_gap_80099FDC` | `0x8009AF4C` | `0xE8D0207F` | `opcode_0x3A` | `swc2        $16, 0x207F($a2)` |
| funcs_27.c:916 | `serviceStreamingVoice` | `0x8009C0D0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_27.c:1058 | `serviceStreamingVoice` | `0x8009C198` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_27.c:5030 | `filterVoiceSampleBlock` | `0x8009D8C0` | `0xF1F3F5F7` | `opcode_0x3C` | `scd         $s3, -0xA09($t7)` |
| funcs_27.c:6026 | `audioCompandS16` | `0x8009DDF0` | `0x00100001` | `special_0x01 $zero,$zero,$s0` | `.word       0x00100001                   # INVALID     $zero, $s0, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:6073 | `audioCompandS16` | `0x8009DE14` | `0x00100001` | `special_0x01 $zero,$zero,$s0` | `.word       0x00100001                   # INVALID     $zero, $s0, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:6145 | `audioCompandS16` | `0x8009DE38` | `0x00100001` | `special_0x01 $zero,$zero,$s0` | `.word       0x00100001                   # INVALID     $zero, $s0, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:6212 | `audioCompandS16` | `0x8009DE54` | `0x40002000` | `cop0` | `mfc0        $zero, Context` |
| funcs_27.c:6216 | `audioCompandS16` | `0x8009DE5C` | `0x00100001` | `special_0x01 $zero,$zero,$s0` | `.word       0x00100001                   # INVALID     $zero, $s0, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:6226 | `audioCompandS16` | `0x8009DE70` | `0x41000000` | `cop0` | `bc0f        L_8009DE74` |
| funcs_27.c:6245 | `audioCompandS16` | `0x8009DE94` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6247 | `audioCompandS16` | `0x8009DE98` | `0x42440000` | `cop0` | `.word       0x42440000                   # INVALID     $s2, $a0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6250 | `audioCompandS16` | `0x8009DE9C` | `0x41F20000` | `cop0` | `.word       0x41F20000                   # INVALID     $t7, $s2, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6252 | `audioCompandS16` | `0x8009DEA0` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6254 | `audioCompandS16` | `0x8009DEA4` | `0x40C80000` | `cop0` | `ctc0        $t0, Index` |
| funcs_27.c:6258 | `audioCompandS16` | `0x8009DEAC` | `0x41680000` | `cop0` | `.word       0x41680000                   # INVALID     $t3, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6260 | `audioCompandS16` | `0x8009DEB0` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6289 | `audioCompandS16` | `0x8009DEE4` | `0x00000070` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 1` |
| funcs_27.c:6295 | `audioCompandS16` | `0x8009DEF0` | `0x00030001` | `special_0x01 $zero,$zero,$v1` | `.word       0x00030001                   # INVALID     $zero, $v1, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:6329 | `audioCompandS16` | `0x8009DF34` | `0x41000000` | `cop0` | `bc0f        L_8009DF38` |
| funcs_27.c:6360 | `audioCompandS16` | `0x8009DF70` | `0x40D00000` | `cop0` | `ctc0        $s0, Index` |
| funcs_27.c:6364 | `audioCompandS16` | `0x8009DF78` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6376 | `audioCompandS16` | `0x8009DF90` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6378 | `audioCompandS16` | `0x8009DF94` | `0xC0A00000` | `opcode_0x30` | `ll          $zero, 0x0($a1)` |
| funcs_27.c:6384 | `audioCompandS16` | `0x8009DFA0` | `0x41040000` | `cop0` | `.word       0x41040000                   # INVALID     $t0, $a0, 0x0 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_27.c:6390 | `audioCompandS16` | `0x8009DFAC` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:6406 | `audioCompandS16` | `0x8009DFCC` | `0xC0900000` | `opcode_0x30` | `ll          $s0, 0x0($a0)` |
| funcs_27.c:6408 | `audioCompandS16` | `0x8009DFD0` | `0xC0C00000` | `opcode_0x30` | `ll          $zero, 0x0($a2)` |
| funcs_27.c:6414 | `audioCompandS16` | `0x8009DFDC` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_27.c:6424 | `audioCompandS16` | `0x8009DFF0` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6436 | `audioCompandS16` | `0x8009E008` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6438 | `audioCompandS16` | `0x8009E00C` | `0xC1400000` | `opcode_0x30` | `ll          $zero, 0x0($t2)` |
| funcs_27.c:6450 | `audioCompandS16` | `0x8009E024` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:6452 | `audioCompandS16` | `0x8009E028` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6454 | `audioCompandS16` | `0x8009E02C` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6456 | `audioCompandS16` | `0x8009E030` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:6476 | `audioCompandS16` | `0x8009E058` | `0x00030001` | `special_0x01 $zero,$zero,$v1` | `.word       0x00030001                   # INVALID     $zero, $v1, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:6494 | `audioCompandS16` | `0x8009E07C` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6510 | `audioCompandS16` | `0x8009E09C` | `0x41000000` | `cop0` | `bc0f        L_8009E0A0` |
| funcs_27.c:6527 | `audioCompandS16` | `0x8009E0BC` | `0xC0B60000` | `opcode_0x30` | `ll          $s6, 0x0($a1)` |
| funcs_27.c:6529 | `audioCompandS16` | `0x8009E0C0` | `0xC1280000` | `opcode_0x30` | `ll          $t0, 0x0($t1)` |
| funcs_27.c:6541 | `audioCompandS16` | `0x8009E0D8` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_27.c:6545 | `audioCompandS16` | `0x8009E0E0` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6557 | `audioCompandS16` | `0x8009E0F8` | `0xC0C40000` | `opcode_0x30` | `ll          $a0, 0x0($a2)` |
| funcs_27.c:6559 | `audioCompandS16` | `0x8009E0FC` | `0xC18ECCCD` | `opcode_0x30` | `ll          $t6, -0x3333($t4)` |
| funcs_27.c:6565 | `audioCompandS16` | `0x8009E108` | `0x410C0000` | `cop0` | `.word       0x410C0000                   # INVALID     $t0, $t4, 0x0 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_27.c:6571 | `audioCompandS16` | `0x8009E114` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6587 | `audioCompandS16` | `0x8009E134` | `0xC11A0000` | `opcode_0x30` | `ll          $k0, 0x0($t0)` |
| funcs_27.c:6589 | `audioCompandS16` | `0x8009E138` | `0xC1D20000` | `opcode_0x30` | `ll          $s2, 0x0($t6)` |
| funcs_27.c:6595 | `audioCompandS16` | `0x8009E144` | `0x418C0000` | `cop0` | `.word       0x418C0000                   # INVALID     $t4, $t4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6605 | `audioCompandS16` | `0x8009E158` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6617 | `audioCompandS16` | `0x8009E170` | `0xC07C0000` | `opcode_0x30` | `ll          $gp, 0x0($v1)` |
| funcs_27.c:6631 | `audioCompandS16` | `0x8009E18C` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:6633 | `audioCompandS16` | `0x8009E190` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:6635 | `audioCompandS16` | `0x8009E194` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6637 | `audioCompandS16` | `0x8009E198` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:6657 | `audioCompandS16` | `0x8009E1C0` | `0x00030001` | `special_0x01 $zero,$zero,$v1` | `.word       0x00030001                   # INVALID     $zero, $v1, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:6691 | `audioCompandS16` | `0x8009E204` | `0x41000000` | `cop0` | `bc0f        L_8009E208` |
| funcs_27.c:6722 | `audioCompandS16` | `0x8009E240` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_27.c:6726 | `audioCompandS16` | `0x8009E248` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6738 | `audioCompandS16` | `0x8009E260` | `0xC0100000` | `opcode_0x30` | `ll          $s0, 0x0($zero)` |
| funcs_27.c:6740 | `audioCompandS16` | `0x8009E264` | `0xC04CCCCD` | `opcode_0x30` | `ll          $t4, -0x3333($v0)` |
| funcs_27.c:6746 | `audioCompandS16` | `0x8009E270` | `0x41240000` | `cop0` | `.word       0x41240000                   # INVALID     $t1, $a0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6752 | `audioCompandS16` | `0x8009E27C` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6768 | `audioCompandS16` | `0x8009E29C` | `0xC0600000` | `opcode_0x30` | `ll          $zero, 0x0($v1)` |
| funcs_27.c:6770 | `audioCompandS16` | `0x8009E2A0` | `0xC1200000` | `opcode_0x30` | `ll          $zero, 0x0($t1)` |
| funcs_27.c:6776 | `audioCompandS16` | `0x8009E2AC` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6786 | `audioCompandS16` | `0x8009E2C0` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6798 | `audioCompandS16` | `0x8009E2D8` | `0xC0100000` | `opcode_0x30` | `ll          $s0, 0x0($zero)` |
| funcs_27.c:6812 | `audioCompandS16` | `0x8009E2F4` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:6814 | `audioCompandS16` | `0x8009E2F8` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:6816 | `audioCompandS16` | `0x8009E2FC` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:6818 | `audioCompandS16` | `0x8009E300` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:6838 | `audioCompandS16` | `0x8009E328` | `0x00030001` | `special_0x01 $zero,$zero,$v1` | `.word       0x00030001                   # INVALID     $zero, $v1, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:6872 | `audioCompandS16` | `0x8009E36C` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:6902 | `audioCompandS16` | `0x8009E3A8` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:6918 | `audioCompandS16` | `0x8009E3C8` | `0xC0100000` | `opcode_0x30` | `ll          $s0, 0x0($zero)` |
| funcs_27.c:6932 | `audioCompandS16` | `0x8009E3E4` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_27.c:6948 | `audioCompandS16` | `0x8009E404` | `0xC0200000` | `opcode_0x30` | `ll          $zero, 0x0($at)` |
| funcs_27.c:6962 | `audioCompandS16` | `0x8009E420` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:6978 | `audioCompandS16` | `0x8009E440` | `0xC0100000` | `opcode_0x30` | `ll          $s0, 0x0($zero)` |
| funcs_27.c:6992 | `audioCompandS16` | `0x8009E45C` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:6994 | `audioCompandS16` | `0x8009E460` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6996 | `audioCompandS16` | `0x8009E464` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:6998 | `audioCompandS16` | `0x8009E468` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:7018 | `audioCompandS16` | `0x8009E490` | `0x00030001` | `special_0x01 $zero,$zero,$v1` | `.word       0x00030001                   # INVALID     $zero, $v1, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:7052 | `audioCompandS16` | `0x8009E4D4` | `0x41000000` | `cop0` | `bc0f        L_8009E4D8` |
| funcs_27.c:7069 | `audioCompandS16` | `0x8009E4F4` | `0xC0F00000` | `opcode_0x30` | `ll          $s0, 0x0($a3)` |
| funcs_27.c:7071 | `audioCompandS16` | `0x8009E4F8` | `0xC0E00000` | `opcode_0x30` | `ll          $zero, 0x0($a3)` |
| funcs_27.c:7075 | `audioCompandS16` | `0x8009E500` | `0xC0800000` | `opcode_0x30` | `ll          $zero, 0x0($a0)` |
| funcs_27.c:7077 | `audioCompandS16` | `0x8009E504` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:7083 | `audioCompandS16` | `0x8009E510` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_27.c:7087 | `audioCompandS16` | `0x8009E518` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7099 | `audioCompandS16` | `0x8009E530` | `0xC1400000` | `opcode_0x30` | `ll          $zero, 0x0($t2)` |
| funcs_27.c:7101 | `audioCompandS16` | `0x8009E534` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7105 | `audioCompandS16` | `0x8009E53C` | `0xC0B00000` | `opcode_0x30` | `ll          $s0, 0x0($a1)` |
| funcs_27.c:7107 | `audioCompandS16` | `0x8009E540` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:7113 | `audioCompandS16` | `0x8009E54C` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:7129 | `audioCompandS16` | `0x8009E56C` | `0xC1780000` | `opcode_0x30` | `ll          $t8, 0x0($t3)` |
| funcs_27.c:7131 | `audioCompandS16` | `0x8009E570` | `0xC1700000` | `opcode_0x30` | `ll          $s0, 0x0($t3)` |
| funcs_27.c:7137 | `audioCompandS16` | `0x8009E57C` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:7147 | `audioCompandS16` | `0x8009E590` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7159 | `audioCompandS16` | `0x8009E5A8` | `0xC0100000` | `opcode_0x30` | `ll          $s0, 0x0($zero)` |
| funcs_27.c:7173 | `audioCompandS16` | `0x8009E5C4` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:7175 | `audioCompandS16` | `0x8009E5C8` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:7177 | `audioCompandS16` | `0x8009E5CC` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:7179 | `audioCompandS16` | `0x8009E5D0` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:7199 | `audioCompandS16` | `0x8009E5F8` | `0x00030001` | `special_0x01 $zero,$zero,$v1` | `.word       0x00030001                   # INVALID     $zero, $v1, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:7233 | `audioCompandS16` | `0x8009E63C` | `0x41000000` | `cop0` | `bc0f        L_8009E640` |
| funcs_27.c:7252 | `audioCompandS16` | `0x8009E660` | `0xC0600000` | `opcode_0x30` | `ll          $zero, 0x0($v1)` |
| funcs_27.c:7264 | `audioCompandS16` | `0x8009E678` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:7268 | `audioCompandS16` | `0x8009E680` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7280 | `audioCompandS16` | `0x8009E698` | `0xC0100000` | `opcode_0x30` | `ll          $s0, 0x0($zero)` |
| funcs_27.c:7282 | `audioCompandS16` | `0x8009E69C` | `0xC0A66666` | `opcode_0x30` | `ll          $a2, 0x6666($a1)` |
| funcs_27.c:7288 | `audioCompandS16` | `0x8009E6A8` | `0x41240000` | `cop0` | `.word       0x41240000                   # INVALID     $t1, $a0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:7294 | `audioCompandS16` | `0x8009E6B4` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:7310 | `audioCompandS16` | `0x8009E6D4` | `0xC0600000` | `opcode_0x30` | `ll          $zero, 0x0($v1)` |
| funcs_27.c:7312 | `audioCompandS16` | `0x8009E6D8` | `0xC1700000` | `opcode_0x30` | `ll          $s0, 0x0($t3)` |
| funcs_27.c:7318 | `audioCompandS16` | `0x8009E6E4` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:7328 | `audioCompandS16` | `0x8009E6F8` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7340 | `audioCompandS16` | `0x8009E710` | `0xC0100000` | `opcode_0x30` | `ll          $s0, 0x0($zero)` |
| funcs_27.c:7354 | `audioCompandS16` | `0x8009E72C` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:7356 | `audioCompandS16` | `0x8009E730` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:7358 | `audioCompandS16` | `0x8009E734` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:7360 | `audioCompandS16` | `0x8009E738` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:7380 | `audioCompandS16` | `0x8009E760` | `0x00030001` | `special_0x01 $zero,$zero,$v1` | `.word       0x00030001                   # INVALID     $zero, $v1, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:7414 | `audioCompandS16` | `0x8009E7A4` | `0x41000000` | `cop0` | `bc0f        L_8009E7A8` |
| funcs_27.c:7431 | `audioCompandS16` | `0x8009E7C4` | `0xC00CCCCD` | `opcode_0x30` | `ll          $t4, -0x3333($zero)` |
| funcs_27.c:7439 | `audioCompandS16` | `0x8009E7D4` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:7445 | `audioCompandS16` | `0x8009E7E0` | `0x41080000` | `cop0` | `.word       0x41080000                   # INVALID     $t0, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_27.c:7449 | `audioCompandS16` | `0x8009E7E8` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7461 | `audioCompandS16` | `0x8009E800` | `0xC0900000` | `opcode_0x30` | `ll          $s0, 0x0($a0)` |
| funcs_27.c:7463 | `audioCompandS16` | `0x8009E804` | `0xC0C00000` | `opcode_0x30` | `ll          $zero, 0x0($a2)` |
| funcs_27.c:7469 | `audioCompandS16` | `0x8009E810` | `0x40880000` | `cop0` | `mtc0        $t0, Index` |
| funcs_27.c:7475 | `audioCompandS16` | `0x8009E81C` | `0x41000000` | `cop0` | `bc0f        L_8009E820` |
| funcs_27.c:7492 | `audioCompandS16` | `0x8009E83C` | `0xC1200000` | `opcode_0x30` | `ll          $zero, 0x0($t1)` |
| funcs_27.c:7494 | `audioCompandS16` | `0x8009E840` | `0xC1000000` | `opcode_0x30` | `ll          $zero, 0x0($t0)` |
| funcs_27.c:7500 | `audioCompandS16` | `0x8009E84C` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_27.c:7510 | `audioCompandS16` | `0x8009E860` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7522 | `audioCompandS16` | `0x8009E878` | `0xC0100000` | `opcode_0x30` | `ll          $s0, 0x0($zero)` |
| funcs_27.c:7536 | `audioCompandS16` | `0x8009E894` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:7538 | `audioCompandS16` | `0x8009E898` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:7540 | `audioCompandS16` | `0x8009E89C` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:7542 | `audioCompandS16` | `0x8009E8A0` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:7562 | `audioCompandS16` | `0x8009E8C8` | `0x00030001` | `special_0x01 $zero,$zero,$v1` | `.word       0x00030001                   # INVALID     $zero, $v1, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:7596 | `audioCompandS16` | `0x8009E90C` | `0x41000000` | `cop0` | `bc0f        L_8009E910` |
| funcs_27.c:7627 | `audioCompandS16` | `0x8009E948` | `0x40D00000` | `cop0` | `ctc0        $s0, Index` |
| funcs_27.c:7631 | `audioCompandS16` | `0x8009E950` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7643 | `audioCompandS16` | `0x8009E968` | `0xC0400000` | `opcode_0x30` | `ll          $zero, 0x0($v0)` |
| funcs_27.c:7651 | `audioCompandS16` | `0x8009E978` | `0x40880000` | `cop0` | `mtc0        $t0, Index` |
| funcs_27.c:7657 | `audioCompandS16` | `0x8009E984` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_27.c:7673 | `audioCompandS16` | `0x8009E9A4` | `0xC0700000` | `opcode_0x30` | `ll          $s0, 0x0($v1)` |
| funcs_27.c:7679 | `audioCompandS16` | `0x8009E9B0` | `0xC0300000` | `opcode_0x30` | `ll          $s0, 0x0($at)` |
| funcs_27.c:7681 | `audioCompandS16` | `0x8009E9B4` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:7691 | `audioCompandS16` | `0x8009E9C8` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7703 | `audioCompandS16` | `0x8009E9E0` | `0xC0100000` | `opcode_0x30` | `ll          $s0, 0x0($zero)` |
| funcs_27.c:7717 | `audioCompandS16` | `0x8009E9FC` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:7719 | `audioCompandS16` | `0x8009EA00` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7721 | `audioCompandS16` | `0x8009EA04` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:7723 | `audioCompandS16` | `0x8009EA08` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:7743 | `audioCompandS16` | `0x8009EA30` | `0x00030001` | `special_0x01 $zero,$zero,$v1` | `.word       0x00030001                   # INVALID     $zero, $v1, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:7777 | `audioCompandS16` | `0x8009EA74` | `0x41000000` | `cop0` | `bc0f        L_8009EA78` |
| funcs_27.c:7794 | `audioCompandS16` | `0x8009EA94` | `0xC0600000` | `opcode_0x30` | `ll          $zero, 0x0($v1)` |
| funcs_27.c:7808 | `audioCompandS16` | `0x8009EAB0` | `0x40D00000` | `cop0` | `ctc0        $s0, Index` |
| funcs_27.c:7812 | `audioCompandS16` | `0x8009EAB8` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7824 | `audioCompandS16` | `0x8009EAD0` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7832 | `audioCompandS16` | `0x8009EAE0` | `0x41040000` | `cop0` | `.word       0x41040000                   # INVALID     $t0, $a0, 0x0 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_27.c:7838 | `audioCompandS16` | `0x8009EAEC` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:7854 | `audioCompandS16` | `0x8009EB0C` | `0xC0900000` | `opcode_0x30` | `ll          $s0, 0x0($a0)` |
| funcs_27.c:7856 | `audioCompandS16` | `0x8009EB10` | `0xC0800000` | `opcode_0x30` | `ll          $zero, 0x0($a0)` |
| funcs_27.c:7862 | `audioCompandS16` | `0x8009EB1C` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_27.c:7872 | `audioCompandS16` | `0x8009EB30` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7884 | `audioCompandS16` | `0x8009EB48` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:7886 | `audioCompandS16` | `0x8009EB4C` | `0xC1400000` | `opcode_0x30` | `ll          $zero, 0x0($t2)` |
| funcs_27.c:7898 | `audioCompandS16` | `0x8009EB64` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:7900 | `audioCompandS16` | `0x8009EB68` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:7904 | `audioCompandS16` | `0x8009EB70` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:7957 | `audioCompandS16` | `0x8009EBD0` | `0x447A0000` | `cop1` | `.word       0x447A0000                   # INVALID     $v1, $k0, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_27.c:7959 | `audioCompandS16` | `0x8009EBD4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:7961 | `audioCompandS16` | `0x8009EBD8` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_27.c:7963 | `audioCompandS16` | `0x8009EBDC` | `0x43480000` | `cop0` | `.word       0x43480000                   # INVALID     $k0, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:8039 | `audioCompandS16` | `0x8009EC6C` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:8051 | `audioCompandS16` | `0x8009EC84` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:8074 | `audioCompandS16` | `0x8009ECB0` | `0x419C0000` | `cop0` | `.word       0x419C0000                   # INVALID     $t4, $gp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:8076 | `audioCompandS16` | `0x8009ECB4` | `0x42000000` | `cop0` | `.word       0x42000000                   # INVALID     $s0, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0_TLB>` |
| funcs_27.c:8078 | `audioCompandS16` | `0x8009ECB8` | `0x42C80000` | `cop0` | `.word       0x42C80000                   # INVALID     $s6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:8080 | `audioCompandS16` | `0x8009ECBC` | `0x43480000` | `cop0` | `.word       0x43480000                   # INVALID     $k0, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:8102 | `audioCompandS16` | `0x8009ECE0` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:8104 | `audioCompandS16` | `0x8009ECE4` | `0xC0A00000` | `opcode_0x30` | `ll          $zero, 0x0($a1)` |
| funcs_27.c:8106 | `audioCompandS16` | `0x8009ECE8` | `0x41A80000` | `cop0` | `.word       0x41A80000                   # INVALID     $t5, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:8108 | `audioCompandS16` | `0x8009ECEC` | `0xC1A80000` | `opcode_0x30` | `ll          $t0, 0x0($t5)` |
| funcs_27.c:8156 | `audioCompandS16` | `0x8009ED44` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:8158 | `audioCompandS16` | `0x8009ED48` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:8170 | `audioCompandS16` | `0x8009ED60` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:8190 | `audioCompandS16` | `0x8009ED88` | `0x0B202020` | `j` | `j           L_8C808080` |
| funcs_27.c:8218 | `audioCompandS16` | `0x8009EDB0` | `0x0B0C110E` | `j` | `j           L_8C304438` |
| funcs_27.c:8226 | `audioCompandS16` | `0x8009EDB0` | `0x0B0C110E` | `j` | `j           L_8C304438` |
| funcs_27.c:8230 | `audioCompandS16` | `0x8009EDB0` | `0x0B0C110E` | `j` | `j           L_8C304438` |
| funcs_27.c:8241 | `audioCompandS16` | `0x8009EDCC` | `0x0A100712` | `j` | `j           L_88401C48` |
| funcs_27.c:8262 | `audioCompandS16` | `0x8009EDCC` | `0x0A100712` | `j` | `j           L_88401C48` |
| funcs_27.c:8279 | `audioCompandS16` | `0x8009EDCC` | `0x0A100712` | `j` | `j           L_88401C48` |
| funcs_27.c:8293 | `audioCompandS16` | `0x8009EDCC` | `0x0A100712` | `j` | `j           L_88401C48` |
| funcs_27.c:8305 | `audioCompandS16` | `0x8009EDCC` | `0x0A100712` | `j` | `j           L_88401C48` |
| funcs_27.c:8313 | `audioCompandS16` | `0x8009EDCC` | `0x0A100712` | `j` | `j           L_88401C48` |
| funcs_27.c:8317 | `audioCompandS16` | `0x8009EDCC` | `0x0A100712` | `j` | `j           L_88401C48` |
| funcs_27.c:8383 | `audioCompandS16` | `0x8009EDFC` | `0xFA010101` | `opcode_0x3E` | `sdc2        $1, 0x101($s0)` |
| funcs_27.c:8514 | `audioCompandS16` | `0x8009EF00` | `0xFA010100` | `opcode_0x3E` | `sdc2        $1, 0x100($s0)` |
| funcs_27.c:8630 | `audioCompandS16` | `0x8009EFE8` | `0x09070607` | `j` | `j           L_841C181C` |
| funcs_27.c:8632 | `audioCompandS16` | `0x8009EFEC` | `0x06070707` | `regimm` | `.word       0x06070707                   # INVALID     $s0, $a3, 0x707 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8634 | `audioCompandS16` | `0x8009EFF0` | `0x05080807` | `regimm` | `tgei        $t0, 0x807` |
| funcs_27.c:8636 | `audioCompandS16` | `0x8009EFF4` | `0x09080707` | `j` | `j           L_84201C1C` |
| funcs_27.c:8638 | `audioCompandS16` | `0x8009EFF8` | `0x07070707` | `regimm` | `.word       0x07070707                   # INVALID     $t8, $a3, 0x707 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8640 | `audioCompandS16` | `0x8009EFFC` | `0x08090908` | `j` | `j           L_80242420` |
| funcs_27.c:8642 | `audioCompandS16` | `0x8009F000` | `0x08060606` | `j` | `j           L_80181818` |
| funcs_27.c:8644 | `audioCompandS16` | `0x8009F004` | `0x06070607` | `regimm` | `.word       0x06070607                   # INVALID     $s0, $a3, 0x607 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8646 | `audioCompandS16` | `0x8009F008` | `0x06060606` | `regimm` | `.word       0x06060606                   # INVALID     $s0, $a2, 0x606 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8648 | `audioCompandS16` | `0x8009F00C` | `0x03060605` | `special_0x05 $zero,$t8,$a2` | `.word       0x03060605                   # INVALID     $t8, $a2, 0x605 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:8652 | `audioCompandS16` | `0x8009F014` | `0x07060606` | `regimm` | `.word       0x07060606                   # INVALID     $t8, $a2, 0x606 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8657 | `audioCompandS16` | `0x8009F020` | `0x0038000A` | `movz $zero,$at,$t8` | `movz        $zero, $at, $t8` |
| funcs_27.c:8661 | `audioCompandS16` | `0x8009F020` | `0x0038000A` | `movz $zero,$at,$t8` | `movz        $zero, $at, $t8` |
| funcs_27.c:8663 | `audioCompandS16` | `0x8009F024` | `0x000E000E` | `special_0x0E $zero,$zero,$t6` | `.word       0x000E000E                   # INVALID     $zero, $t6, 0xE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:8675 | `audioCompandS16` | `0x8009F03C` | `0xFA010101` | `opcode_0x3E` | `sdc2        $1, 0x101($s0)` |
| funcs_27.c:8792 | `audioCompandS16` | `0x8009F124` | `0x0038000A` | `movz $zero,$at,$t8` | `movz        $zero, $at, $t8` |
| funcs_27.c:8794 | `audioCompandS16` | `0x8009F128` | `0x000E000E` | `special_0x0E $zero,$zero,$t6` | `.word       0x000E000E                   # INVALID     $zero, $t6, 0xE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:8796 | `audioCompandS16` | `0x8009F12C` | `0x00010001` | `special_0x01 $zero,$zero,$at` | `.word       0x00010001                   # INVALID     $zero, $at, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:8806 | `audioCompandS16` | `0x8009F140` | `0xFA010101` | `opcode_0x3E` | `sdc2        $1, 0x101($s0)` |
| funcs_27.c:8922 | `audioCompandS16` | `0x8009F228` | `0x05050505` | `regimm` | `.word       0x05050505                   # INVALID     $t0, $a1, 0x505 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8924 | `audioCompandS16` | `0x8009F22C` | `0x05050505` | `regimm` | `.word       0x05050505                   # INVALID     $t0, $a1, 0x505 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8926 | `audioCompandS16` | `0x8009F230` | `0x03030605` | `special_0x05 $zero,$t8,$v1` | `.word       0x03030605                   # INVALID     $t8, $v1, 0x605 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:8928 | `audioCompandS16` | `0x8009F234` | `0x07050606` | `regimm` | `.word       0x07050606                   # INVALID     $t8, $a1, 0x606 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8930 | `audioCompandS16` | `0x8009F238` | `0x06050505` | `regimm` | `.word       0x06050505                   # INVALID     $s0, $a1, 0x505 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8932 | `audioCompandS16` | `0x8009F23C` | `0x05050705` | `regimm` | `.word       0x05050705                   # INVALID     $t0, $a1, 0x705 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8934 | `audioCompandS16` | `0x8009F240` | `0x05040504` | `regimm` | `.word       0x05040504                   # INVALID     $t0, $a0, 0x504 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8936 | `audioCompandS16` | `0x8009F244` | `0x05050505` | `regimm` | `.word       0x05050505                   # INVALID     $t0, $a1, 0x505 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8938 | `audioCompandS16` | `0x8009F248` | `0x05040505` | `regimm` | `.word       0x05040505                   # INVALID     $t0, $a0, 0x505 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8948 | `audioCompandS16` | `0x8009F25C` | `0x06060600` | `regimm` | `.word       0x06060600                   # INVALID     $s0, $a2, 0x600 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:8951 | `audioCompandS16` | `0x8009F264` | `0x000F000F` | `special_0x0F $zero,$zero,$t7` | `.word       0x000F000F                   # sync # 000F0000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:8955 | `audioCompandS16` | `0x8009F264` | `0x000F000F` | `special_0x0F $zero,$zero,$t7` | `.word       0x000F000F                   # sync # 000F0000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:9084 | `audioCompandS16` | `0x8009F368` | `0x000F000F` | `special_0x0F $zero,$zero,$t7` | `.word       0x000F000F                   # sync # 000F0000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:9088 | `audioCompandS16` | `0x8009F368` | `0x000F000F` | `special_0x0F $zero,$zero,$t7` | `.word       0x000F000F                   # sync # 000F0000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:9090 | `audioCompandS16` | `0x8009F36C` | `0x00010001` | `special_0x01 $zero,$zero,$at` | `.word       0x00010001                   # INVALID     $zero, $at, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:9812 | `audioCompandS16` | `0x8009F4EC` | `0xEC010100` | `opcode_0x3B` | `.word       0xEC010100                   # INVALID     $zero, $at, 0x100 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:9928 | `audioCompandS16` | `0x8009F5D4` | `0x05050505` | `regimm` | `.word       0x05050505                   # INVALID     $t0, $a1, 0x505 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:9930 | `audioCompandS16` | `0x8009F5D8` | `0x04040505` | `regimm` | `.word       0x04040505                   # INVALID     $zero, $a0, 0x505 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:9934 | `audioCompandS16` | `0x8009F5E0` | `0x06050505` | `regimm` | `.word       0x06050505                   # INVALID     $s0, $a1, 0x505 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:9936 | `audioCompandS16` | `0x8009F5E4` | `0x05050504` | `regimm` | `.word       0x05050504                   # INVALID     $t0, $a1, 0x504 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:9938 | `audioCompandS16` | `0x8009F5E8` | `0x05050605` | `regimm` | `.word       0x05050605                   # INVALID     $t0, $a1, 0x605 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:9940 | `audioCompandS16` | `0x8009F5EC` | `0x05040503` | `regimm` | `.word       0x05040503                   # INVALID     $t0, $a0, 0x503 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:9942 | `audioCompandS16` | `0x8009F5F0` | `0x05050505` | `regimm` | `.word       0x05050505                   # INVALID     $t0, $a1, 0x505 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:9944 | `audioCompandS16` | `0x8009F5F4` | `0x05050505` | `regimm` | `.word       0x05050505                   # INVALID     $t0, $a1, 0x505 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:9950 | `audioCompandS16` | `0x8009F600` | `0x05050505` | `regimm` | `.word       0x05050505                   # INVALID     $t0, $a1, 0x505 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:9955 | `audioCompandS16` | `0x8009F600` | `0x05050505` | `regimm` | `.word       0x05050505                   # INVALID     $t0, $a1, 0x505 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:9968 | `audioCompandS16` | `0x8009F60C` | `0x000C000A` | `movz $zero,$zero,$t4` | `movz        $zero, $zero, $t4` |
| funcs_27.c:10097 | `audioCompandS16` | `0x8009F70C` | `0x0A0A0A0A` | `j` | `j           L_88282828` |
| funcs_27.c:10099 | `audioCompandS16` | `0x8009F710` | `0x08080A0A` | `j` | `j           L_80202828` |
| funcs_27.c:10101 | `audioCompandS16` | `0x8009F714` | `0x04080A08` | `regimm` | `tgei        $zero, 0xA08` |
| funcs_27.c:10104 | `audioCompandS16` | `0x8009F71C` | `0x0A0A0A08` | `j` | `j           L_88282820` |
| funcs_27.c:10108 | `audioCompandS16` | `0x8009F71C` | `0x0A0A0A08` | `j` | `j           L_88282820` |
| funcs_27.c:10111 | `audioCompandS16` | `0x8009F720` | `0x0A0A0C0A` | `j` | `j           L_88283028` |
| funcs_27.c:10113 | `audioCompandS16` | `0x8009F724` | `0x0A080A06` | `j` | `j           L_88202818` |
| funcs_27.c:10115 | `audioCompandS16` | `0x8009F728` | `0x0A0A0A0A` | `j` | `j           L_88282828` |
| funcs_27.c:10117 | `audioCompandS16` | `0x8009F72C` | `0x0A0A0A0A` | `j` | `j           L_88282828` |
| funcs_27.c:10119 | `audioCompandS16` | `0x8009F730` | `0x04080A06` | `regimm` | `tgei        $zero, 0xA06` |
| funcs_27.c:10121 | `audioCompandS16` | `0x8009F734` | `0x0A060C0C` | `j` | `j           L_88183030` |
| funcs_27.c:10123 | `audioCompandS16` | `0x8009F738` | `0x0A0A0A0A` | `j` | `j           L_88282828` |
| funcs_27.c:10125 | `audioCompandS16` | `0x8009F73C` | `0x08040A00` | `j` | `j           L_80102800` |
| funcs_27.c:10130 | `audioCompandS16` | `0x8009F744` | `0x000C000A` | `movz $zero,$zero,$t4` | `movz        $zero, $zero, $t4` |
| funcs_27.c:10259 | `audioCompandS16` | `0x8009F844` | `0x08070707` | `j` | `j           L_801C1C1C` |
| funcs_27.c:10261 | `audioCompandS16` | `0x8009F848` | `0x06060707` | `regimm` | `.word       0x06060707                   # INVALID     $s0, $a2, 0x707 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10265 | `audioCompandS16` | `0x8009F850` | `0x0A080707` | `j` | `j           L_88201C1C` |
| funcs_27.c:10267 | `audioCompandS16` | `0x8009F854` | `0x07070707` | `regimm` | `.word       0x07070707                   # INVALID     $t8, $a3, 0x707 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10269 | `audioCompandS16` | `0x8009F858` | `0x07080A08` | `regimm` | `tgei        $t8, 0xA08` |
| funcs_27.c:10271 | `audioCompandS16` | `0x8009F85C` | `0x09070507` | `j` | `j           L_841C141C` |
| funcs_27.c:10273 | `audioCompandS16` | `0x8009F860` | `0x07070807` | `regimm` | `.word       0x07070807                   # INVALID     $t8, $a3, 0x807 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10275 | `audioCompandS16` | `0x8009F864` | `0x07060707` | `regimm` | `.word       0x07060707                   # INVALID     $t8, $a2, 0x707 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10281 | `audioCompandS16` | `0x8009F870` | `0x0A0A0807` | `j` | `j           L_8828201C` |
| funcs_27.c:10286 | `audioCompandS16` | `0x8009F870` | `0x0A0A0807` | `j` | `j           L_8828201C` |
| funcs_27.c:10289 | `audioCompandS16` | `0x8009F874` | `0x07080703` | `regimm` | `tgei        $t8, 0x703` |
| funcs_27.c:10291 | `audioCompandS16` | `0x8009F878` | `0x0034000A` | `movz $zero,$at,$s4` | `movz        $zero, $at, $s4` |
| funcs_27.c:10293 | `audioCompandS16` | `0x8009F87C` | `0x0014000F` | `special_0x0F $zero,$zero,$s4` | `.word       0x0014000F                   # sync # 00140000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:10295 | `audioCompandS16` | `0x8009F880` | `0x0002FFFD` | `special_0x3D $ra,$zero,$v0` | `.word       0x0002FFFD                   # INVALID     $zero, $v0, -0x3 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:10305 | `audioCompandS16` | `0x8009F894` | `0xFA010001` | `opcode_0x3E` | `sdc2        $1, 0x1($s0)` |
| funcs_27.c:10421 | `audioCompandS16` | `0x8009F97C` | `0x07060606` | `regimm` | `.word       0x07060606                   # INVALID     $t8, $a2, 0x606 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10423 | `audioCompandS16` | `0x8009F980` | `0x05050606` | `regimm` | `.word       0x05050606                   # INVALID     $t0, $a1, 0x606 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10425 | `audioCompandS16` | `0x8009F984` | `0x03060705` | `special_0x05 $zero,$t8,$a2` | `.word       0x03060705                   # INVALID     $t8, $a2, 0x705 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:10427 | `audioCompandS16` | `0x8009F988` | `0x09060606` | `j` | `j           L_84181818` |
| funcs_27.c:10429 | `audioCompandS16` | `0x8009F98C` | `0x06060605` | `regimm` | `.word       0x06060605                   # INVALID     $s0, $a2, 0x605 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10431 | `audioCompandS16` | `0x8009F990` | `0x06060907` | `regimm` | `.word       0x06060907                   # INVALID     $s0, $a2, 0x907 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10433 | `audioCompandS16` | `0x8009F994` | `0x06060604` | `regimm` | `.word       0x06060604                   # INVALID     $s0, $a2, 0x604 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10435 | `audioCompandS16` | `0x8009F998` | `0x06060706` | `regimm` | `.word       0x06060706                   # INVALID     $s0, $a2, 0x706 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10437 | `audioCompandS16` | `0x8009F99C` | `0x06060606` | `regimm` | `.word       0x06060606                   # INVALID     $s0, $a2, 0x606 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10443 | `audioCompandS16` | `0x8009F9A8` | `0x07040405` | `regimm` | `.word       0x07040405                   # INVALID     $t8, $a0, 0x405 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10448 | `audioCompandS16` | `0x8009F9A8` | `0x07040405` | `regimm` | `.word       0x07040405                   # INVALID     $t8, $a0, 0x405 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10451 | `audioCompandS16` | `0x8009F9AC` | `0x05070707` | `regimm` | `.word       0x05070707                   # INVALID     $t0, $a3, 0x707 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:10453 | `audioCompandS16` | `0x8009F9B0` | `0x0034000A` | `movz $zero,$at,$s4` | `movz        $zero, $at, $s4` |
| funcs_27.c:10455 | `audioCompandS16` | `0x8009F9B4` | `0x0014000F` | `special_0x0F $zero,$zero,$s4` | `.word       0x0014000F                   # sync # 00140000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:10457 | `audioCompandS16` | `0x8009F9B8` | `0x0002FFFD` | `special_0x3D $ra,$zero,$v0` | `.word       0x0002FFFD                   # INVALID     $zero, $v0, -0x3 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:10467 | `audioCompandS16` | `0x8009F9CC` | `0xFA010100` | `opcode_0x3E` | `sdc2        $1, 0x100($s0)` |
| funcs_27.c:10587 | `audioCompandS16` | `0x8009FABC` | `0x090B1712` | `j` | `j           L_842C5C48` |
| funcs_27.c:10595 | `audioCompandS16` | `0x8009FABC` | `0x090B1712` | `j` | `j           L_842C5C48` |
| funcs_27.c:10599 | `audioCompandS16` | `0x8009FABC` | `0x090B1712` | `j` | `j           L_842C5C48` |
| funcs_27.c:10627 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10679 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10727 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10771 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10811 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10847 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10879 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10907 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10931 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10951 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10967 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10979 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10987 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10991 | `audioCompandS16` | `0x8009FAF4` | `0x090D070E` | `j` | `j           L_84341C38` |
| funcs_27.c:10993 | `audioCompandS16` | `0x8009FAF8` | `0x0909180A` | `j` | `j           L_84246028` |
| funcs_27.c:10995 | `audioCompandS16` | `0x8009FAFC` | `0x081A0918` | `j` | `j           L_80682460` |
| funcs_27.c:11042 | `audioCompandS16` | `0x8009FB28` | `0xEC010100` | `opcode_0x3B` | `.word       0xEC010100                   # INVALID     $zero, $at, 0x100 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:11242 | `audioCompandS16` | `0x8009FCB8` | `0x04060506` | `regimm` | `.word       0x04060506                   # INVALID     $zero, $a2, 0x506 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:11244 | `audioCompandS16` | `0x8009FCBC` | `0x05070407` | `regimm` | `.word       0x05070407                   # INVALID     $t0, $a3, 0x407 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:11248 | `audioCompandS16` | `0x8009FCC4` | `0x03070105` | `special_0x05 $zero,$t8,$a3` | `.word       0x03070105                   # INVALID     $t8, $a3, 0x105 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11273 | `audioCompandS16` | `0x8009FCEC` | `0x00000009` | `jalr $zero,$zero,$zero` | `jalr        $zero, $zero` |
| funcs_27.c:11277 | `audioCompandS16` | `0x8009FCF4` | `0x0000000A` | `movz $zero,$zero,$zero` | `movz        $zero, $zero, $zero` |
| funcs_27.c:11281 | `audioCompandS16` | `0x8009FCFC` | `0x0000000B` | `movn $zero,$zero,$zero` | `movn        $zero, $zero, $zero` |
| funcs_27.c:11290 | `audioCompandS16` | `0x8009FD0C` | `0x0000000D` | `break $zero,$zero,$zero` | `break       0` |
| funcs_27.c:11294 | `audioCompandS16` | `0x8009FD14` | `0x0000000E` | `special_0x0E $zero,$zero,$zero` | `.word       0x0000000E                   # INVALID     $zero, $zero, 0xE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11298 | `audioCompandS16` | `0x8009FD1C` | `0x0000000F` | `sync $zero,$zero,$zero` | `sync` |
| funcs_27.c:11322 | `audioCompandS16` | `0x8009FD4C` | `0x00000015` | `special_0x15 $zero,$zero,$zero` | `.word       0x00000015                   # INVALID     $zero, $zero, 0x15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11390 | `audioCompandS16` | `0x8009FDD4` | `0x00000028` | `special_0x28 $zero,$zero,$zero` | `.word       0x00000028                   # INVALID     $zero, $zero, 0x28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11394 | `audioCompandS16` | `0x8009FDDC` | `0x00000029` | `special_0x29 $zero,$zero,$zero` | `.word       0x00000029                   # INVALID     $zero, $zero, 0x29 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11416 | `audioCompandS16` | `0x8009FE04` | `0x00000030` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 0` |
| funcs_27.c:11420 | `audioCompandS16` | `0x8009FE0C` | `0x00000031` | `special_0x31 $zero,$zero,$zero` | `tgeu        $zero, $zero, 0` |
| funcs_27.c:11424 | `audioCompandS16` | `0x8009FE14` | `0x00000032` | `special_0x32 $zero,$zero,$zero` | `tlt         $zero, $zero, 0` |
| funcs_27.c:11428 | `audioCompandS16` | `0x8009FE1C` | `0x00000033` | `special_0x33 $zero,$zero,$zero` | `tltu        $zero, $zero, 0` |
| funcs_27.c:11432 | `audioCompandS16` | `0x8009FE24` | `0x00000034` | `special_0x34 $zero,$zero,$zero` | `teq         $zero, $zero, 0` |
| funcs_27.c:11449 | `audioCompandS16` | `0x8009FE44` | `0x00000035` | `special_0x35 $zero,$zero,$zero` | `.word       0x00000035                   # INVALID     $zero, $zero, 0x35 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11454 | `audioCompandS16` | `0x8009FE4C` | `0x00000036` | `special_0x36 $zero,$zero,$zero` | `tne         $zero, $zero, 0` |
| funcs_27.c:11458 | `audioCompandS16` | `0x8009FE54` | `0x00000037` | `special_0x37 $zero,$zero,$zero` | `.word       0x00000037                   # INVALID     $zero, $zero, 0x37 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11466 | `audioCompandS16` | `0x8009FE64` | `0x00000039` | `special_0x39 $zero,$zero,$zero` | `.word       0x00000039                   # INVALID     $zero, $zero, 0x39 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11486 | `audioCompandS16` | `0x8009FE8C` | `0x0000003D` | `special_0x3D $zero,$zero,$zero` | `.word       0x0000003D                   # INVALID     $zero, $zero, 0x3D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11502 | `audioCompandS16` | `0x8009FEAC` | `0x00000041` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000041                   # INVALID     $zero, $zero, 0x41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11518 | `audioCompandS16` | `0x8009FECC` | `0x00000045` | `special_0x05 $zero,$zero,$zero` | `.word       0x00000045                   # INVALID     $zero, $zero, 0x45 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11537 | `audioCompandS16` | `0x8009FEEC` | `0x00000049` | `jalr $zero,$zero,$zero` | `.word       0x00000049                   # jalr        $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11541 | `audioCompandS16` | `0x8009FEF4` | `0x0000004A` | `movz $zero,$zero,$zero` | `.word       0x0000004A                   # movz        $zero, $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11545 | `audioCompandS16` | `0x8009FEFC` | `0x0000004B` | `movn $zero,$zero,$zero` | `.word       0x0000004B                   # movn        $zero, $zero, $zero # 00000040 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11554 | `audioCompandS16` | `0x8009FF0C` | `0x0000004D` | `break $zero,$zero,$zero` | `break       0, 1` |
| funcs_27.c:11558 | `audioCompandS16` | `0x8009FF14` | `0x0000004E` | `special_0x0E $zero,$zero,$zero` | `.word       0x0000004E                   # INVALID     $zero, $zero, 0x4E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11562 | `audioCompandS16` | `0x8009FF1C` | `0x0000004F` | `sync $zero,$zero,$zero` | `.word       0x0000004F                   # sync # 00000040 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11586 | `audioCompandS16` | `0x8009FF4C` | `0x00000055` | `special_0x15 $zero,$zero,$zero` | `.word       0x00000055                   # INVALID     $zero, $zero, 0x55 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11614 | `audioCompandS16` | `0x8009FF84` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11634 | `audioCompandS16` | `0x8009FFAC` | `0x00000005` | `special_0x05 $zero,$zero,$zero` | `.word       0x00000005                   # INVALID     $zero, $zero, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11661 | `audioCompandS16` | `0x8009FFE0` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11665 | `audioCompandS16` | `0x8009FFE8` | `0x00040005` | `special_0x05 $zero,$zero,$a0` | `.word       0x00040005                   # INVALID     $zero, $a0, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11669 | `audioCompandS16` | `0x8009FFF0` | `0x00080009` | `jalr $zero,$zero,$t0` | `.word       0x00080009                   # jalr        $zero, $zero # 00080000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11671 | `audioCompandS16` | `0x8009FFF4` | `0x000A000B` | `movn $zero,$zero,$t2` | `movn        $zero, $zero, $t2` |
| funcs_27.c:11673 | `audioCompandS16` | `0x8009FFF8` | `0x000C000D` | `break $zero,$zero,$t4` | `break       12` |
| funcs_27.c:11675 | `audioCompandS16` | `0x8009FFFC` | `0x000E000F` | `special_0x0F $zero,$zero,$t6` | `.word       0x000E000F                   # sync # 000E0000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11683 | `audioCompandS16` | `0x800A000C` | `0x00140015` | `special_0x15 $zero,$zero,$s4` | `.word       0x00140015                   # INVALID     $zero, $s4, 0x15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11707 | `audioCompandS16` | `0x800A003C` | `0x00000028` | `special_0x28 $zero,$zero,$zero` | `.word       0x00000028                   # INVALID     $zero, $zero, 0x28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11717 | `audioCompandS16` | `0x800A0050` | `0x002F0030` | `special_0x30 $zero,$at,$t7` | `tge         $at, $t7, 0` |
| funcs_27.c:11719 | `audioCompandS16` | `0x800A0054` | `0x00310032` | `special_0x32 $zero,$at,$s1` | `tlt         $at, $s1, 0` |
| funcs_27.c:11725 | `audioCompandS16` | `0x800A0060` | `0x00000035` | `special_0x35 $zero,$zero,$zero` | `.word       0x00000035                   # INVALID     $zero, $zero, 0x35 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11731 | `audioCompandS16` | `0x800A006C` | `0x00000037` | `special_0x37 $zero,$zero,$zero` | `.word       0x00000037                   # INVALID     $zero, $zero, 0x37 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11733 | `audioCompandS16` | `0x800A0070` | `0x00380039` | `special_0x39 $zero,$at,$t8` | `.word       0x00380039                   # INVALID     $at, $t8, 0x39 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11737 | `audioCompandS16` | `0x800A0078` | `0x003C003D` | `special_0x3D $zero,$at,$gp` | `.word       0x003C003D                   # INVALID     $at, $gp, 0x3D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11743 | `audioCompandS16` | `0x800A0084` | `0x00000041` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000041                   # INVALID     $zero, $zero, 0x41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11752 | `audioCompandS16` | `0x800A0098` | `0x0049004A` | `movz $zero,$v0,$t1` | `.word       0x0049004A                   # movz        $zero, $v0, $t1 # 00000040 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11756 | `audioCompandS16` | `0x800A0098` | `0x0049004A` | `movz $zero,$v0,$t1` | `.word       0x0049004A                   # movz        $zero, $v0, $t1 # 00000040 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11761 | `audioCompandS16` | `0x800A00A0` | `0x0000004D` | `break $zero,$zero,$zero` | `break       0, 1` |
| funcs_27.c:11763 | `audioCompandS16` | `0x800A00A4` | `0x004E004F` | `special_0x0F $zero,$v0,$t6` | `.word       0x004E004F                   # sync # 004E0040 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11771 | `audioCompandS16` | `0x800A00B4` | `0x00540055` | `special_0x15 $zero,$v0,$s4` | `.word       0x00540055                   # INVALID     $v0, $s4, 0x55 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11791 | `audioCompandS16` | `0x800A00DC` | `0x00670068` | `special_0x28 $zero,$v1,$a3` | `.word       0x00670068                   # INVALID     $v1, $a3, 0x68 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11799 | `audioCompandS16` | `0x800A00EC` | `0x006F0070` | `special_0x30 $zero,$v1,$t7` | `tge         $v1, $t7, 1` |
| funcs_27.c:11801 | `audioCompandS16` | `0x800A00F0` | `0x00710072` | `special_0x32 $zero,$v1,$s1` | `tlt         $v1, $s1, 1` |
| funcs_27.c:11803 | `audioCompandS16` | `0x800A00F4` | `0x00730074` | `special_0x34 $zero,$v1,$s3` | `teq         $v1, $s3, 1` |
| funcs_27.c:11805 | `audioCompandS16` | `0x800A00F8` | `0x00000075` | `special_0x35 $zero,$zero,$zero` | `.word       0x00000075                   # INVALID     $zero, $zero, 0x75 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11807 | `audioCompandS16` | `0x800A00FC` | `0x00760077` | `special_0x37 $zero,$v1,$s6` | `.word       0x00760077                   # INVALID     $v1, $s6, 0x77 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11817 | `audioCompandS16` | `0x800A0110` | `0x0000007D` | `special_0x3D $zero,$zero,$zero` | `.word       0x0000007D                   # INVALID     $zero, $zero, 0x7D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11829 | `audioCompandS16` | `0x800A0128` | `0x00800081` | `special_0x01 $zero,$a0,$zero` | `.word       0x00800081                   # INVALID     $a0, $zero, 0x81 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11839 | `audioCompandS16` | `0x800A013C` | `0x00000085` | `special_0x05 $zero,$zero,$zero` | `.word       0x00000085                   # INVALID     $zero, $zero, 0x85 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11847 | `audioCompandS16` | `0x800A014C` | `0x00880089` | `jalr $zero,$a0,$t0` | `.word       0x00880089                   # jalr        $zero, $a0 # 00080080 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11851 | `audioCompandS16` | `0x800A0154` | `0x008A008B` | `movn $zero,$a0,$t2` | `.word       0x008A008B                   # movn        $zero, $a0, $t2 # 00000080 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11855 | `audioCompandS16` | `0x800A015C` | `0x0000008D` | `break $zero,$zero,$zero` | `break       0, 2` |
| funcs_27.c:11867 | `audioCompandS16` | `0x800A0174` | `0x0000008F` | `sync $zero,$zero,$zero` | `.word       0x0000008F                   # sync # 00000080 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11899 | `audioCompandS16` | `0x800A01B4` | `0x00A800A9` | `special_0x29 $zero,$a1,$t0` | `.word       0x00A800A9                   # INVALID     $a1, $t0, 0xA9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11907 | `audioCompandS16` | `0x800A01C4` | `0x00B000B1` | `special_0x31 $zero,$a1,$s0` | `tgeu        $a1, $s0, 2` |
| funcs_27.c:11909 | `audioCompandS16` | `0x800A01C8` | `0x00B200B3` | `special_0x33 $zero,$a1,$s2` | `tltu        $a1, $s2, 2` |
| funcs_27.c:11913 | `audioCompandS16` | `0x800A01D0` | `0x000000B4` | `special_0x34 $zero,$zero,$zero` | `teq         $zero, $zero, 2` |
| funcs_27.c:11917 | `audioCompandS16` | `0x800A01D8` | `0x000000B6` | `special_0x36 $zero,$zero,$zero` | `tne         $zero, $zero, 2` |
| funcs_27.c:11921 | `audioCompandS16` | `0x800A01E0` | `0x00B800B9` | `special_0x39 $zero,$a1,$t8` | `.word       0x00B800B9                   # INVALID     $a1, $t8, 0xB9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11927 | `audioCompandS16` | `0x800A01EC` | `0x000000BD` | `special_0x3D $zero,$zero,$zero` | `.word       0x000000BD                   # INVALID     $zero, $zero, 0xBD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11931 | `audioCompandS16` | `0x800A01F4` | `0x00C000C1` | `special_0x01 $zero,$a2,$zero` | `.word       0x00C000C1                   # INVALID     $a2, $zero, 0xC1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11940 | `audioCompandS16` | `0x800A0208` | `0x00C900CA` | `movz $zero,$a2,$t1` | `.word       0x00C900CA                   # movz        $zero, $a2, $t1 # 000000C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11944 | `audioCompandS16` | `0x800A0208` | `0x00C900CA` | `movz $zero,$a2,$t1` | `.word       0x00C900CA                   # movz        $zero, $a2, $t1 # 000000C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11951 | `audioCompandS16` | `0x800A0214` | `0x00CE00CF` | `special_0x0F $zero,$a2,$t6` | `.word       0x00CE00CF                   # sync # 00CE00C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11981 | `audioCompandS16` | `0x800A0250` | `0x00E800E9` | `special_0x29 $zero,$a3,$t0` | `.word       0x00E800E9                   # INVALID     $a3, $t0, 0xE9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11989 | `audioCompandS16` | `0x800A0260` | `0x00F000F1` | `special_0x31 $zero,$a3,$s0` | `tgeu        $a3, $s0, 3` |
| funcs_27.c:11991 | `audioCompandS16` | `0x800A0264` | `0x00F200F3` | `special_0x33 $zero,$a3,$s2` | `tltu        $a3, $s2, 3` |
| funcs_27.c:11993 | `audioCompandS16` | `0x800A0268` | `0x00F400F5` | `special_0x35 $zero,$a3,$s4` | `.word       0x00F400F5                   # INVALID     $a3, $s4, 0xF5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11995 | `audioCompandS16` | `0x800A026C` | `0x00F600F7` | `special_0x37 $zero,$a3,$s6` | `.word       0x00F600F7                   # INVALID     $a3, $s6, 0xF7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:11997 | `audioCompandS16` | `0x800A0270` | `0x00F800F9` | `special_0x39 $zero,$a3,$t8` | `.word       0x00F800F9                   # INVALID     $a3, $t8, 0xF9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12009 | `audioCompandS16` | `0x800A0288` | `0x00000101` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000101                   # INVALID     $zero, $zero, 0x101 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12018 | `audioCompandS16` | `0x800A029C` | `0x0109010A` | `movz $zero,$t0,$t1` | `.word       0x0109010A                   # movz        $zero, $t0, $t1 # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12022 | `audioCompandS16` | `0x800A029C` | `0x0109010A` | `movz $zero,$t0,$t1` | `.word       0x0109010A                   # movz        $zero, $t0, $t1 # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12027 | `audioCompandS16` | `0x800A02A4` | `0x0000010D` | `break $zero,$zero,$zero` | `break       0, 4` |
| funcs_27.c:12029 | `audioCompandS16` | `0x800A02A8` | `0x010E010F` | `special_0x0F $zero,$t0,$t6` | `.word       0x010E010F                   # sync # 010E0100 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12037 | `audioCompandS16` | `0x800A02B8` | `0x01140115` | `special_0x15 $zero,$t0,$s4` | `.word       0x01140115                   # INVALID     $t0, $s4, 0x115 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12057 | `audioCompandS16` | `0x800A02E0` | `0x01270128` | `special_0x28 $zero,$t1,$a3` | `.word       0x01270128                   # INVALID     $t1, $a3, 0x128 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12071 | `audioCompandS16` | `0x800A02FC` | `0x012F0130` | `special_0x30 $zero,$t1,$t7` | `tge         $t1, $t7, 4` |
| funcs_27.c:12073 | `audioCompandS16` | `0x800A0300` | `0x01310132` | `special_0x32 $zero,$t1,$s1` | `tlt         $t1, $s1, 4` |
| funcs_27.c:12083 | `audioCompandS16` | `0x800A0314` | `0x01340135` | `special_0x35 $zero,$t1,$s4` | `.word       0x01340135                   # INVALID     $t1, $s4, 0x135 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12093 | `audioCompandS16` | `0x800A0328` | `0x00000137` | `special_0x37 $zero,$zero,$zero` | `.word       0x00000137                   # INVALID     $zero, $zero, 0x137 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12095 | `audioCompandS16` | `0x800A032C` | `0x01380139` | `special_0x39 $zero,$t1,$t8` | `.word       0x01380139                   # INVALID     $t1, $t8, 0x139 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12099 | `audioCompandS16` | `0x800A0334` | `0x013C013D` | `special_0x3D $zero,$t1,$gp` | `.word       0x013C013D                   # INVALID     $t1, $gp, 0x13D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12115 | `audioCompandS16` | `0x800A0354` | `0x01440145` | `special_0x05 $zero,$t2,$a0` | `.word       0x01440145                   # INVALID     $t2, $a0, 0x145 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12137 | `audioCompandS16` | `0x800A0380` | `0x01480149` | `jalr $zero,$t2,$t0` | `.word       0x01480149                   # jalr        $zero, $t2 # 00080140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12139 | `audioCompandS16` | `0x800A0384` | `0x014A014B` | `movn $zero,$t2,$t2` | `.word       0x014A014B                   # movn        $zero, $t2, $t2 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12141 | `audioCompandS16` | `0x800A0388` | `0x014C014D` | `break $zero,$t2,$t4` | `break       332, 5` |
| funcs_27.c:12143 | `audioCompandS16` | `0x800A038C` | `0x014E014F` | `special_0x0F $zero,$t2,$t6` | `.word       0x014E014F                   # sync # 014E0140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12183 | `audioCompandS16` | `0x800A03DC` | `0x01680169` | `special_0x29 $zero,$t3,$t0` | `.word       0x01680169                   # INVALID     $t3, $t0, 0x169 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12193 | `audioCompandS16` | `0x800A03F0` | `0x016F0170` | `special_0x30 $zero,$t3,$t7` | `tge         $t3, $t7, 5` |
| funcs_27.c:12199 | `audioCompandS16` | `0x800A03FC` | `0x01720173` | `special_0x33 $zero,$t3,$s2` | `tltu        $t3, $s2, 5` |
| funcs_27.c:12201 | `audioCompandS16` | `0x800A0400` | `0x01740175` | `special_0x35 $zero,$t3,$s4` | `.word       0x01740175                   # INVALID     $t3, $s4, 0x175 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12203 | `audioCompandS16` | `0x800A0404` | `0x01760177` | `special_0x37 $zero,$t3,$s6` | `.word       0x01760177                   # INVALID     $t3, $s6, 0x177 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12207 | `audioCompandS16` | `0x800A040C` | `0x00000179` | `special_0x39 $zero,$zero,$zero` | `.word       0x00000179                   # INVALID     $zero, $zero, 0x179 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12221 | `audioCompandS16` | `0x800A0428` | `0x01800181` | `special_0x01 $zero,$t4,$zero` | `.word       0x01800181                   # INVALID     $t4, $zero, 0x181 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12235 | `audioCompandS16` | `0x800A0444` | `0x00000189` | `jalr $zero,$zero,$zero` | `.word       0x00000189                   # jalr        $zero, $zero # 00000180 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12237 | `audioCompandS16` | `0x800A0448` | `0x018A018B` | `movn $zero,$t4,$t2` | `.word       0x018A018B                   # movn        $zero, $t4, $t2 # 00000180 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12239 | `audioCompandS16` | `0x800A044C` | `0x018C018D` | `break $zero,$t4,$t4` | `break       396, 6` |
| funcs_27.c:12241 | `audioCompandS16` | `0x800A0450` | `0x018E018F` | `special_0x0F $zero,$t4,$t6` | `.word       0x018E018F                   # sync # 018E0180 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12247 | `audioCompandS16` | `0x800A045C` | `0x01940195` | `special_0x15 $zero,$t4,$s4` | `.word       0x01940195                   # INVALID     $t4, $s4, 0x195 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12273 | `audioCompandS16` | `0x800A0490` | `0x000001A8` | `special_0x28 $zero,$zero,$zero` | `.word       0x000001A8                   # INVALID     $zero, $zero, 0x1A8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12285 | `audioCompandS16` | `0x800A04A8` | `0x01AF01B0` | `special_0x30 $zero,$t5,$t7` | `tge         $t5, $t7, 6` |
| funcs_27.c:12287 | `audioCompandS16` | `0x800A04AC` | `0x01B101B2` | `special_0x32 $zero,$t5,$s1` | `tlt         $t5, $s1, 6` |
| funcs_27.c:12289 | `audioCompandS16` | `0x800A04B0` | `0x01B301B4` | `special_0x34 $zero,$t5,$s3` | `teq         $t5, $s3, 6` |
| funcs_27.c:12291 | `audioCompandS16` | `0x800A04B4` | `0x01B501B6` | `special_0x36 $zero,$t5,$s5` | `tne         $t5, $s5, 6` |
| funcs_27.c:12312 | `audioCompandS16` | `0x800A04E0` | `0x01C901CA` | `movz $zero,$t6,$t1` | `.word       0x01C901CA                   # movz        $zero, $t6, $t1 # 000001C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12316 | `audioCompandS16` | `0x800A04E0` | `0x01C901CA` | `movz $zero,$t6,$t1` | `.word       0x01C901CA                   # movz        $zero, $t6, $t1 # 000001C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12321 | `audioCompandS16` | `0x800A04E8` | `0x01CD01CE` | `special_0x0E $zero,$t6,$t5` | `.word       0x01CD01CE                   # INVALID     $t6, $t5, 0x1CE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12329 | `audioCompandS16` | `0x800A04F8` | `0x000001D5` | `special_0x15 $zero,$zero,$zero` | `.word       0x000001D5                   # INVALID     $zero, $zero, 0x1D5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12363 | `audioCompandS16` | `0x800A053C` | `0x01E701E8` | `special_0x28 $zero,$t7,$a3` | `.word       0x01E701E8                   # INVALID     $t7, $a3, 0x1E8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12379 | `audioCompandS16` | `0x800A055C` | `0x01F001F1` | `special_0x31 $zero,$t7,$s0` | `tgeu        $t7, $s0, 7` |
| funcs_27.c:12381 | `audioCompandS16` | `0x800A0560` | `0x01F201F3` | `special_0x33 $zero,$t7,$s2` | `tltu        $t7, $s2, 7` |
| funcs_27.c:12383 | `audioCompandS16` | `0x800A0564` | `0x01F401F5` | `special_0x35 $zero,$t7,$s4` | `.word       0x01F401F5                   # INVALID     $t7, $s4, 0x1F5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12385 | `audioCompandS16` | `0x800A0568` | `0x01F601F7` | `special_0x37 $zero,$t7,$s6` | `.word       0x01F601F7                   # INVALID     $t7, $s6, 0x1F7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12387 | `audioCompandS16` | `0x800A056C` | `0x01F801F9` | `special_0x39 $zero,$t7,$t8` | `.word       0x01F801F9                   # INVALID     $t7, $t8, 0x1F9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12391 | `audioCompandS16` | `0x800A0574` | `0x01FC01FD` | `special_0x3D $zero,$t7,$gp` | `.word       0x01FC01FD                   # INVALID     $t7, $gp, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12395 | `audioCompandS16` | `0x800A057C` | `0x02000201` | `special_0x01 $zero,$s0,$zero` | `.word       0x02000201                   # INVALID     $s0, $zero, 0x201 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12399 | `audioCompandS16` | `0x800A0584` | `0x02040205` | `special_0x05 $zero,$s0,$a0` | `.word       0x02040205                   # INVALID     $s0, $a0, 0x205 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12403 | `audioCompandS16` | `0x800A058C` | `0x02080209` | `jalr $zero,$s0,$t0` | `.word       0x02080209                   # jalr        $zero, $s0 # 00080200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12405 | `audioCompandS16` | `0x800A0590` | `0x020A020B` | `movn $zero,$s0,$t2` | `.word       0x020A020B                   # movn        $zero, $s0, $t2 # 00000200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12407 | `audioCompandS16` | `0x800A0594` | `0x020C020D` | `break $zero,$s0,$t4` | `break       524, 8` |
| funcs_27.c:12409 | `audioCompandS16` | `0x800A0598` | `0x020E020F` | `special_0x0F $zero,$s0,$t6` | `.word       0x020E020F                   # sync # 020E0200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12415 | `audioCompandS16` | `0x800A05A4` | `0x02140215` | `special_0x15 $zero,$s0,$s4` | `.word       0x02140215                   # INVALID     $s0, $s4, 0x215 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12458 | `audioCompandS16` | `0x800A05F0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:12460 | `audioCompandS16` | `0x800A05F4` | `0xCEC0A4FF` | `opcode_0x33` | `pref        $zero, -0x5B01($s6)` |
| funcs_27.c:12462 | `audioCompandS16` | `0x800A05F8` | `0xC8C0A0FF` | `opcode_0x32` | `lwc2        $0, -0x5F01($a2)` |
| funcs_27.c:12468 | `audioCompandS16` | `0x800A0604` | `0x01C20230` | `special_0x30 $zero,$t6,$v0` | `tge         $t6, $v0, 8` |
| funcs_27.c:12482 | `audioCompandS16` | `0x800A0620` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:12490 | `audioCompandS16` | `0x800A0630` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12505 | `audioCompandS16` | `0x800A064C` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:12507 | `audioCompandS16` | `0x800A0650` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:12509 | `audioCompandS16` | `0x800A0654` | `0x788060FF` | `opcode_0x1E` | `.word       0x788060FF                   # INVALID     $a0, $zero, 0x60FF # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:12511 | `audioCompandS16` | `0x800A0658` | `0x788060FF` | `opcode_0x1E` | `.word       0x788060FF                   # INVALID     $a0, $zero, 0x60FF # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:12515 | `audioCompandS16` | `0x800A0660` | `0x000000C1` | `special_0x01 $zero,$zero,$zero` | `.word       0x000000C1                   # INVALID     $zero, $zero, 0xC1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12531 | `audioCompandS16` | `0x800A0680` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_27.c:12551 | `audioCompandS16` | `0x800A0690` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12568 | `audioCompandS16` | `0x800A06B0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:12580 | `audioCompandS16` | `0x800A06C4` | `0x01D601F4` | `special_0x34 $zero,$t6,$s6` | `teq         $t6, $s6, 7` |
| funcs_27.c:12592 | `audioCompandS16` | `0x800A06DC` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:12594 | `audioCompandS16` | `0x800A06E0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:12596 | `audioCompandS16` | `0x800A06E4` | `0x080808FF` | `j` | `j           L_802023FC` |
| funcs_27.c:12598 | `audioCompandS16` | `0x800A06E8` | `0x080808FF` | `j` | `j           L_802023FC` |
| funcs_27.c:12626 | `audioCompandS16` | `0x800A0720` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12644 | `audioCompandS16` | `0x800A0744` | `0x4A5972FF` | `opcode_0x12` | `.word       0x4A5972FF                   # INVALID     $s2, $t9, 0x72FF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_27.c:12646 | `audioCompandS16` | `0x800A0748` | `0x485870FF` | `opcode_0x12` | `.word       0x485870FF                   # cfc2        $t8, $14 # 000000FF <InstrIdType: CPU_COP2>` |
| funcs_27.c:12650 | `audioCompandS16` | `0x800A0750` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12669 | `audioCompandS16` | `0x800A0770` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:12726 | `audioCompandS16` | `0x800A07E0` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12750 | `audioCompandS16` | `0x800A0810` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12766 | `audioCompandS16` | `0x800A0830` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:12810 | `audioCompandS16` | `0x800A0870` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12827 | `audioCompandS16` | `0x800A0890` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:12831 | `audioCompandS16` | `0x800A0898` | `0xC8D0D0FF` | `opcode_0x32` | `lwc2        $16, -0x2F01($a2)` |
| funcs_27.c:12835 | `audioCompandS16` | `0x800A08A0` | `0x00000081` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000081                   # INVALID     $zero, $zero, 0x81 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12849 | `audioCompandS16` | `0x800A08BC` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_27.c:12851 | `audioCompandS16` | `0x800A08C0` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_27.c:12861 | `audioCompandS16` | `0x800A08D4` | `0x015E01F4` | `special_0x34 $zero,$t2,$fp` | `teq         $t2, $fp, 7` |
| funcs_27.c:12875 | `audioCompandS16` | `0x800A08F0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:12877 | `audioCompandS16` | `0x800A08F4` | `0xCEC0A4FF` | `opcode_0x33` | `pref        $zero, -0x5B01($s6)` |
| funcs_27.c:12879 | `audioCompandS16` | `0x800A08F8` | `0xC8C0A0FF` | `opcode_0x32` | `lwc2        $0, -0x5F01($a2)` |
| funcs_27.c:12898 | `audioCompandS16` | `0x800A091C` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:12900 | `audioCompandS16` | `0x800A0920` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_27.c:12902 | `audioCompandS16` | `0x800A0924` | `0x080808FF` | `j` | `j           L_802023FC` |
| funcs_27.c:12904 | `audioCompandS16` | `0x800A0928` | `0x080808FF` | `j` | `j           L_802023FC` |
| funcs_27.c:12908 | `audioCompandS16` | `0x800A0930` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12910 | `audioCompandS16` | `0x800A0934` | `0x01E001F4` | `special_0x34 $zero,$t7,$zero` | `teq         $t7, $zero, 7` |
| funcs_27.c:12924 | `audioCompandS16` | `0x800A0950` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_27.c:12926 | `audioCompandS16` | `0x800A0954` | `0xD1E7F5FF` | `opcode_0x34` | `lld         $a3, -0xA01($t7)` |
| funcs_27.c:12928 | `audioCompandS16` | `0x800A0958` | `0xD0E0F0FF` | `opcode_0x34` | `lld         $zero, -0xF01($a3)` |
| funcs_27.c:12950 | `audioCompandS16` | `0x800A0984` | `0xDBDDF1FF` | `opcode_0x36` | `ldc2        $29, -0xE01($fp)` |
| funcs_27.c:12952 | `audioCompandS16` | `0x800A0988` | `0xD8E0F0FF` | `opcode_0x36` | `ldc2        $0, -0xF01($a3)` |
| funcs_27.c:12980 | `audioCompandS16` | `0x800A09C0` | `0x0000000E` | `special_0x0E $zero,$zero,$zero` | `.word       0x0000000E                   # INVALID     $zero, $zero, 0xE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:12982 | `audioCompandS16` | `0x800A09C4` | `0x0A0C9005` | `j` | `j           L_88324014` |
| funcs_27.c:12988 | `audioCompandS16` | `0x800A09D0` | `0x00040001` | `special_0x01 $zero,$zero,$a0` | `.word       0x00040001                   # INVALID     $zero, $a0, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13007 | `audioCompandS16` | `0x800A09E8` | `0x0000000E` | `special_0x0E $zero,$zero,$zero` | `.word       0x0000000E                   # INVALID     $zero, $zero, 0xE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13009 | `audioCompandS16` | `0x800A09EC` | `0x0A0C9005` | `j` | `j           L_88324014` |
| funcs_27.c:13035 | `audioCompandS16` | `0x800A0A10` | `0x0000000E` | `special_0x0E $zero,$zero,$zero` | `.word       0x0000000E                   # INVALID     $zero, $zero, 0xE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13037 | `audioCompandS16` | `0x800A0A14` | `0x0A0C9005` | `j` | `j           L_88324014` |
| funcs_27.c:13061 | `audioCompandS16` | `0x800A0A38` | `0x0000000E` | `special_0x0E $zero,$zero,$zero` | `.word       0x0000000E                   # INVALID     $zero, $zero, 0xE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13063 | `audioCompandS16` | `0x800A0A3C` | `0x0A0C9005` | `j` | `j           L_88324014` |
| funcs_27.c:13069 | `audioCompandS16` | `0x800A0A48` | `0x00080005` | `special_0x05 $zero,$zero,$t0` | `.word       0x00080005                   # INVALID     $zero, $t0, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13168 | `audioCompandS16` | `0x800A0AE8` | `0x08000C00` | `j` | `j           L_80003000` |
| funcs_27.c:13292 | `audioCompandS16` | `0x800A0BB0` | `0x41100000` | `cop0` | `.word       0x41100000                   # INVALID     $t0, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_27.c:13348 | `audioCompandS16` | `0x800A0C20` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13352 | `audioCompandS16` | `0x800A0C28` | `0x00000401` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000401                   # INVALID     $zero, $zero, 0x401 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13549 | `audioCompandS16` | `0x800A0D80` | `0x476A6000` | `cop1` | `.word       0x476A6000                   # INVALID     $k1, $t2, 0x6000 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_27.c:13551 | `audioCompandS16` | `0x800A0D84` | `0xEF5152FF` | `opcode_0x3B` | `.word       0xEF5152FF                   # INVALID     $k0, $s1, 0x52FF # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:13571 | `audioCompandS16` | `0x800A0DAC` | `0x40FFF007` | `cop0` | `.word       0x40FFF007                   # INVALID     $a3, $ra, -0xFF9 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13581 | `audioCompandS16` | `0x800A0DC0` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13583 | `audioCompandS16` | `0x800A0DC4` | `0xC3350000` | `opcode_0x30` | `ll          $s5, 0x0($t9)` |
| funcs_27.c:13585 | `audioCompandS16` | `0x800A0DC8` | `0x43350000` | `cop0` | `.word       0x43350000                   # INVALID     $t9, $s5, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13589 | `audioCompandS16` | `0x800A0DD0` | `0x42700000` | `cop0` | `.word       0x42700000                   # INVALID     $s3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13591 | `audioCompandS16` | `0x800A0DD4` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:13601 | `audioCompandS16` | `0x800A0DE8` | `0x40D447D8` | `cop0` | `.word       0x40D447D8                   # ctc0        $s4, BadVaddr # 000007D8 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13611 | `audioCompandS16` | `0x800A0DFC` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13613 | `audioCompandS16` | `0x800A0E00` | `0xC3350000` | `opcode_0x30` | `ll          $s5, 0x0($t9)` |
| funcs_27.c:13615 | `audioCompandS16` | `0x800A0E04` | `0x43350000` | `cop0` | `.word       0x43350000                   # INVALID     $t9, $s5, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13618 | `audioCompandS16` | `0x800A0E08` | `0xC1200000` | `opcode_0x30` | `ll          $zero, 0x0($t1)` |
| funcs_27.c:13620 | `audioCompandS16` | `0x800A0E0C` | `0x43350000` | `cop0` | `.word       0x43350000                   # INVALID     $t9, $s5, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13622 | `audioCompandS16` | `0x800A0E10` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:13643 | `audioCompandS16` | `0x800A0E38` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13645 | `audioCompandS16` | `0x800A0E3C` | `0xC1C80000` | `opcode_0x30` | `ll          $t0, 0x0($t6)` |
| funcs_27.c:13647 | `audioCompandS16` | `0x800A0E40` | `0x41C80000` | `cop0` | `.word       0x41C80000                   # INVALID     $t6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13649 | `audioCompandS16` | `0x800A0E44` | `0xC0E00000` | `opcode_0x30` | `ll          $zero, 0x0($a3)` |
| funcs_27.c:13651 | `audioCompandS16` | `0x800A0E48` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13653 | `audioCompandS16` | `0x800A0E4C` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:13661 | `audioCompandS16` | `0x800A0E5C` | `0xC053BB06` | `opcode_0x30` | `ll          $s3, -0x44FA($v0)` |
| funcs_27.c:13663 | `audioCompandS16` | `0x800A0E60` | `0x415AFF2E` | `cop0` | `.word       0x415AFF2E                   # INVALID     $t2, $k0, -0xD2 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13673 | `audioCompandS16` | `0x800A0E74` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13675 | `audioCompandS16` | `0x800A0E78` | `0xC3350000` | `opcode_0x30` | `ll          $s5, 0x0($t9)` |
| funcs_27.c:13677 | `audioCompandS16` | `0x800A0E7C` | `0x43350000` | `cop0` | `.word       0x43350000                   # INVALID     $t9, $s5, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13679 | `audioCompandS16` | `0x800A0E80` | `0xC1A00000` | `opcode_0x30` | `ll          $zero, 0x0($t5)` |
| funcs_27.c:13681 | `audioCompandS16` | `0x800A0E84` | `0x428C0000` | `cop0` | `.word       0x428C0000                   # INVALID     $s4, $t4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13683 | `audioCompandS16` | `0x800A0E88` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_27.c:13691 | `audioCompandS16` | `0x800A0E98` | `0xC05185C6` | `opcode_0x30` | `ll          $s1, -0x7A3A($v0)` |
| funcs_27.c:13693 | `audioCompandS16` | `0x800A0E9C` | `0x40ACCD8A` | `cop0` | `.word       0x40ACCD8A                   # dmtc0       $t4, Reserved25 # 0000058A <InstrIdType: CPU_COP0>` |
| funcs_27.c:13703 | `audioCompandS16` | `0x800A0EB0` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_27.c:13705 | `audioCompandS16` | `0x800A0EB4` | `0xC3350000` | `opcode_0x30` | `ll          $s5, 0x0($t9)` |
| funcs_27.c:13707 | `audioCompandS16` | `0x800A0EB8` | `0x43350000` | `cop0` | `.word       0x43350000                   # INVALID     $t9, $s5, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13711 | `audioCompandS16` | `0x800A0EC0` | `0x428C0000` | `cop0` | `.word       0x428C0000                   # INVALID     $s4, $t4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13733 | `audioCompandS16` | `0x800A0EE8` | `0x40C19208` | `cop0` | `.word       0x40C19208                   # ctc0        $at, WatchLo # 00000208 <InstrIdType: CPU_COP0>` |
| funcs_27.c:13735 | `audioCompandS16` | `0x800A0EEC` | `0x7DD0CC4B` | `opcode_0x1F` | `.word       0x7DD0CC4B                   # INVALID     $t6, $s0, -0x33B5 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:13741 | `audioCompandS16` | `0x800A0EF4` | `0xC9278EE5` | `opcode_0x32` | `lwc2        $7, -0x711B($t1)` |
| funcs_27.c:13745 | `audioCompandS16` | `0x800A0EFC` | `0xE8A593FA` | `opcode_0x3A` | `swc2        $5, -0x6C06($a1)` |
| funcs_27.c:13752 | `audioCompandS16` | `0x800A0F0C` | `0xCEB94078` | `opcode_0x33` | `pref        $t9, 0x4078($s5)` |
| funcs_27.c:13760 | `audioCompandS16` | `0x800A0F0C` | `0xCEB94078` | `opcode_0x33` | `pref        $t9, 0x4078($s5)` |
| funcs_27.c:13766 | `audioCompandS16` | `0x800A0F0C` | `0xCEB94078` | `opcode_0x33` | `pref        $t9, 0x4078($s5)` |
| funcs_27.c:13771 | `audioCompandS16` | `0x800A0F14` | `0xE999EC85` | `opcode_0x3A` | `swc2        $25, -0x137B($t4)` |
| funcs_27.c:13775 | `audioCompandS16` | `0x800A0F1C` | `0xD842019E` | `opcode_0x36` | `ldc2        $2, 0x19E($v0)` |
| funcs_27.c:13780 | `audioCompandS16` | `0x800A0F1C` | `0xD842019E` | `opcode_0x36` | `ldc2        $2, 0x19E($v0)` |
| funcs_27.c:13784 | `audioCompandS16` | `0x800A0F24` | `0x09B770C0` | `j` | `j           L_86DDC300` |
| funcs_27.c:13788 | `audioCompandS16` | `0x800A0F24` | `0x09B770C0` | `j` | `j           L_86DDC300` |
| funcs_27.c:13799 | `audioCompandS16` | `0x800A0F34` | `0x477AC2FB` | `cop1` | `.word       0x477AC2FB                   # INVALID     $k1, $k0, -0x3D05 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_27.c:13803 | `audioCompandS16` | `0x800A0F3C` | `0x494DAC91` | `opcode_0x12` | `.word       0x494DAC91                   # INVALID     $t2, $t5, -0x536F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_27.c:13808 | `audioCompandS16` | `0x800A0F3C` | `0x494DAC91` | `opcode_0x12` | `.word       0x494DAC91                   # INVALID     $t2, $t5, -0x536F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_27.c:13825 | `audioCompandS16` | `0x800A0F54` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13837 | `audioCompandS16` | `0x800A0F6C` | `0x003E0045` | `special_0x05 $zero,$at,$fp` | `.word       0x003E0045                   # INVALID     $at, $fp, 0x45 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13845 | `audioCompandS16` | `0x800A0F7C` | `0x00710077` | `special_0x37 $zero,$v1,$s1` | `.word       0x00710077                   # INVALID     $v1, $s1, 0x77 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13853 | `audioCompandS16` | `0x800A0F8C` | `0x00A300A9` | `special_0x29 $zero,$a1,$v1` | `.word       0x00A300A9                   # INVALID     $a1, $v1, 0xA9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13855 | `audioCompandS16` | `0x800A0F90` | `0x00AF00B6` | `special_0x36 $zero,$a1,$t7` | `tne         $a1, $t7, 2` |
| funcs_27.c:13859 | `audioCompandS16` | `0x800A0F98` | `0x00C800CF` | `special_0x0F $zero,$a2,$t0` | `.word       0x00C800CF                   # sync # 00C800C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13863 | `audioCompandS16` | `0x800A0FA0` | `0x00E200E8` | `special_0x28 $zero,$a3,$v0` | `.word       0x00E200E8                   # INVALID     $a3, $v0, 0xE8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13865 | `audioCompandS16` | `0x800A0FA4` | `0x00EE00F4` | `special_0x34 $zero,$a3,$t6` | `teq         $a3, $t6, 3` |
| funcs_27.c:13867 | `audioCompandS16` | `0x800A0FA8` | `0x00FB0101` | `special_0x01 $zero,$a3,$k1` | `.word       0x00FB0101                   # INVALID     $a3, $k1, 0x101 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13869 | `audioCompandS16` | `0x800A0FAC` | `0x0107010D` | `break $zero,$t0,$a3` | `break       263, 4` |
| funcs_27.c:13875 | `audioCompandS16` | `0x800A0FB8` | `0x012D0133` | `special_0x33 $zero,$t1,$t5` | `tltu        $t1, $t5, 4` |
| funcs_27.c:13886 | `audioCompandS16` | `0x800A0FCC` | `0x016B0172` | `special_0x32 $zero,$t3,$t3` | `tlt         $t3, $t3, 5` |
| funcs_27.c:13890 | `audioCompandS16` | `0x800A0FD4` | `0x0184018B` | `movn $zero,$t4,$a0` | `.word       0x0184018B                   # movn        $zero, $t4, $a0 # 00000180 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13896 | `audioCompandS16` | `0x800A0FE0` | `0x01AA01B0` | `special_0x30 $zero,$t5,$t2` | `tge         $t5, $t2, 6` |
| funcs_27.c:13898 | `audioCompandS16` | `0x800A0FE4` | `0x01B601BD` | `special_0x3D $zero,$t5,$s6` | `.word       0x01B601BD                   # INVALID     $t5, $s6, 0x1BD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13900 | `audioCompandS16` | `0x800A0FE8` | `0x01C301C9` | `jalr $zero,$t6,$v1` | `.word       0x01C301C9                   # jalr        $zero, $t6 # 000301C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13921 | `audioCompandS16` | `0x800A100C` | `0x02330239` | `special_0x39 $zero,$s1,$s3` | `.word       0x02330239                   # INVALID     $s1, $s3, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13939 | `audioCompandS16` | `0x800A1030` | `0x02A302A9` | `special_0x29 $zero,$s5,$v1` | `.word       0x02A302A9                   # INVALID     $s5, $v1, 0x2A9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13941 | `audioCompandS16` | `0x800A1034` | `0x02AF02B6` | `special_0x36 $zero,$s5,$t7` | `tne         $s5, $t7, 10` |
| funcs_27.c:13945 | `audioCompandS16` | `0x800A103C` | `0x02C802CE` | `special_0x0E $zero,$s6,$t0` | `.word       0x02C802CE                   # INVALID     $s6, $t0, 0x2CE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13951 | `audioCompandS16` | `0x800A1048` | `0x02ED02F3` | `special_0x33 $zero,$s7,$t5` | `tltu        $s7, $t5, 11` |
| funcs_27.c:13962 | `audioCompandS16` | `0x800A105C` | `0x032B0331` | `special_0x31 $zero,$t9,$t3` | `tgeu        $t9, $t3, 12` |
| funcs_27.c:13964 | `audioCompandS16` | `0x800A1060` | `0x0337033D` | `special_0x3D $zero,$t9,$s7` | `.word       0x0337033D                   # INVALID     $t9, $s7, 0x33D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13966 | `audioCompandS16` | `0x800A1064` | `0x0344034A` | `movz $zero,$k0,$a0` | `.word       0x0344034A                   # movz        $zero, $k0, $a0 # 00000340 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13992 | `audioCompandS16` | `0x800A1098` | `0x03E303E9` | `special_0x29 $zero,$ra,$v1` | `.word       0x03E303E9                   # INVALID     $ra, $v1, 0x3E9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13994 | `audioCompandS16` | `0x800A109C` | `0x03EF03F5` | `special_0x35 $zero,$ra,$t7` | `.word       0x03EF03F5                   # INVALID     $ra, $t7, 0x3F5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13996 | `audioCompandS16` | `0x800A10A0` | `0x03FB0401` | `special_0x01 $zero,$ra,$k1` | `.word       0x03FB0401                   # INVALID     $ra, $k1, 0x401 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:13998 | `audioCompandS16` | `0x800A10A4` | `0x0407040D` | `regimm` | `.word       0x0407040D                   # INVALID     $zero, $a3, 0x40D # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14004 | `audioCompandS16` | `0x800A10B0` | `0x042C0432` | `regimm` | `teqi        $at, 0x432` |
| funcs_27.c:14014 | `audioCompandS16` | `0x800A10B0` | `0x042C0432` | `regimm` | `teqi        $at, 0x432` |
| funcs_27.c:14020 | `audioCompandS16` | `0x800A10B0` | `0x042C0432` | `regimm` | `teqi        $at, 0x432` |
| funcs_27.c:14022 | `audioCompandS16` | `0x800A10B4` | `0x0438043E` | `regimm` | `.word       0x0438043E                   # INVALID     $at, $t8, 0x43E # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14024 | `audioCompandS16` | `0x800A10B8` | `0x0444044A` | `regimm` | `.word       0x0444044A                   # INVALID     $v0, $a0, 0x44A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14028 | `audioCompandS16` | `0x800A10C0` | `0x045C0462` | `regimm` | `.word       0x045C0462                   # INVALID     $v0, $gp, 0x462 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14033 | `audioCompandS16` | `0x800A10C0` | `0x045C0462` | `regimm` | `.word       0x045C0462                   # INVALID     $v0, $gp, 0x462 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14036 | `audioCompandS16` | `0x800A10C4` | `0x0468046E` | `regimm` | `tgei        $v1, 0x46E` |
| funcs_27.c:14038 | `audioCompandS16` | `0x800A10C8` | `0x0474047A` | `regimm` | `.word       0x0474047A                   # INVALID     $v1, $s4, 0x47A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14042 | `audioCompandS16` | `0x800A10D0` | `0x048C0492` | `regimm` | `teqi        $a0, 0x492` |
| funcs_27.c:14046 | `audioCompandS16` | `0x800A10D0` | `0x048C0492` | `regimm` | `teqi        $a0, 0x492` |
| funcs_27.c:14048 | `audioCompandS16` | `0x800A10D4` | `0x0498049E` | `regimm` | `.word       0x0498049E                   # INVALID     $a0, $t8, 0x49E # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14050 | `audioCompandS16` | `0x800A10D8` | `0x04A504AB` | `regimm` | `.word       0x04A504AB                   # INVALID     $a1, $a1, 0x4AB # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14054 | `audioCompandS16` | `0x800A10E0` | `0x04BD04C3` | `regimm` | `.word       0x04BD04C3                   # INVALID     $a1, $sp, 0x4C3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14059 | `audioCompandS16` | `0x800A10E0` | `0x04BD04C3` | `regimm` | `.word       0x04BD04C3                   # INVALID     $a1, $sp, 0x4C3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14062 | `audioCompandS16` | `0x800A10E4` | `0x04C904CF` | `regimm` | `tgeiu       $a2, 0x4CF` |
| funcs_27.c:14064 | `audioCompandS16` | `0x800A10E8` | `0x04D504DB` | `regimm` | `.word       0x04D504DB                   # INVALID     $a2, $s5, 0x4DB # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14068 | `audioCompandS16` | `0x800A10F0` | `0x04EC04F2` | `regimm` | `teqi        $a3, 0x4F2` |
| funcs_27.c:14072 | `audioCompandS16` | `0x800A10F0` | `0x04EC04F2` | `regimm` | `teqi        $a3, 0x4F2` |
| funcs_27.c:14074 | `audioCompandS16` | `0x800A10F4` | `0x04F804FE` | `regimm` | `.word       0x04F804FE                   # INVALID     $a3, $t8, 0x4FE # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14076 | `audioCompandS16` | `0x800A10F8` | `0x0504050A` | `regimm` | `.word       0x0504050A                   # INVALID     $t0, $a0, 0x50A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14080 | `audioCompandS16` | `0x800A1100` | `0x051C0522` | `regimm` | `.word       0x051C0522                   # INVALID     $t0, $gp, 0x522 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14085 | `audioCompandS16` | `0x800A1100` | `0x051C0522` | `regimm` | `.word       0x051C0522                   # INVALID     $t0, $gp, 0x522 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14088 | `audioCompandS16` | `0x800A1104` | `0x0528052E` | `regimm` | `tgei        $t1, 0x52E` |
| funcs_27.c:14090 | `audioCompandS16` | `0x800A1108` | `0x0534053A` | `regimm` | `.word       0x0534053A                   # INVALID     $t1, $s4, 0x53A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14094 | `audioCompandS16` | `0x800A1110` | `0x054C0552` | `regimm` | `teqi        $t2, 0x552` |
| funcs_27.c:14098 | `audioCompandS16` | `0x800A1110` | `0x054C0552` | `regimm` | `teqi        $t2, 0x552` |
| funcs_27.c:14100 | `audioCompandS16` | `0x800A1114` | `0x0558055D` | `regimm` | `.word       0x0558055D                   # INVALID     $t2, $t8, 0x55D # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14104 | `audioCompandS16` | `0x800A111C` | `0x056F0575` | `regimm` | `.word       0x056F0575                   # INVALID     $t3, $t7, 0x575 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14109 | `audioCompandS16` | `0x800A111C` | `0x056F0575` | `regimm` | `.word       0x056F0575                   # INVALID     $t3, $t7, 0x575 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14112 | `audioCompandS16` | `0x800A1120` | `0x057B0581` | `regimm` | `.word       0x057B0581                   # INVALID     $t3, $k1, 0x581 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14114 | `audioCompandS16` | `0x800A1124` | `0x0587058D` | `regimm` | `.word       0x0587058D                   # INVALID     $t4, $a3, 0x58D # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14118 | `audioCompandS16` | `0x800A112C` | `0x059E05A4` | `regimm` | `.word       0x059E05A4                   # INVALID     $t4, $fp, 0x5A4 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14124 | `audioCompandS16` | `0x800A112C` | `0x059E05A4` | `regimm` | `.word       0x059E05A4                   # INVALID     $t4, $fp, 0x5A4 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14128 | `audioCompandS16` | `0x800A1130` | `0x05AA05B0` | `regimm` | `tlti        $t5, 0x5B0` |
| funcs_27.c:14130 | `audioCompandS16` | `0x800A1134` | `0x05B605BC` | `regimm` | `.word       0x05B605BC                   # INVALID     $t5, $s6, 0x5BC # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14134 | `audioCompandS16` | `0x800A113C` | `0x05CD05D3` | `regimm` | `.word       0x05CD05D3                   # INVALID     $t6, $t5, 0x5D3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14139 | `audioCompandS16` | `0x800A113C` | `0x05CD05D3` | `regimm` | `.word       0x05CD05D3                   # INVALID     $t6, $t5, 0x5D3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14142 | `audioCompandS16` | `0x800A1140` | `0x05D905DF` | `regimm` | `.word       0x05D905DF                   # INVALID     $t6, $t9, 0x5DF # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14144 | `audioCompandS16` | `0x800A1144` | `0x05E505EB` | `regimm` | `.word       0x05E505EB                   # INVALID     $t7, $a1, 0x5EB # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14148 | `audioCompandS16` | `0x800A114C` | `0x05FC0602` | `regimm` | `.word       0x05FC0602                   # INVALID     $t7, $gp, 0x602 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14153 | `audioCompandS16` | `0x800A114C` | `0x05FC0602` | `regimm` | `.word       0x05FC0602                   # INVALID     $t7, $gp, 0x602 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14156 | `audioCompandS16` | `0x800A1150` | `0x0608060E` | `regimm` | `tgei        $s0, 0x60E` |
| funcs_27.c:14160 | `audioCompandS16` | `0x800A1158` | `0x061F0625` | `regimm` | `.word       0x061F0625                   # INVALID     $s0, $ra, 0x625 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14166 | `audioCompandS16` | `0x800A1158` | `0x061F0625` | `regimm` | `.word       0x061F0625                   # INVALID     $s0, $ra, 0x625 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14170 | `audioCompandS16` | `0x800A115C` | `0x062B0630` | `regimm` | `tltiu       $s1, 0x630` |
| funcs_27.c:14172 | `audioCompandS16` | `0x800A1160` | `0x0636063C` | `regimm` | `.word       0x0636063C                   # INVALID     $s1, $s6, 0x63C # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14176 | `audioCompandS16` | `0x800A1168` | `0x064D0653` | `regimm` | `.word       0x064D0653                   # INVALID     $s2, $t5, 0x653 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14181 | `audioCompandS16` | `0x800A1168` | `0x064D0653` | `regimm` | `.word       0x064D0653                   # INVALID     $s2, $t5, 0x653 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14184 | `audioCompandS16` | `0x800A116C` | `0x0659065F` | `regimm` | `.word       0x0659065F                   # INVALID     $s2, $t9, 0x65F # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14186 | `audioCompandS16` | `0x800A1170` | `0x0664066A` | `regimm` | `.word       0x0664066A                   # INVALID     $s3, $a0, 0x66A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14190 | `audioCompandS16` | `0x800A1178` | `0x067B0681` | `regimm` | `.word       0x067B0681                   # INVALID     $s3, $k1, 0x681 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14195 | `audioCompandS16` | `0x800A1178` | `0x067B0681` | `regimm` | `.word       0x067B0681                   # INVALID     $s3, $k1, 0x681 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14198 | `audioCompandS16` | `0x800A117C` | `0x0687068D` | `regimm` | `.word       0x0687068D                   # INVALID     $s4, $a3, 0x68D # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14202 | `audioCompandS16` | `0x800A1184` | `0x069E06A3` | `regimm` | `.word       0x069E06A3                   # INVALID     $s4, $fp, 0x6A3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14208 | `audioCompandS16` | `0x800A1184` | `0x069E06A3` | `regimm` | `.word       0x069E06A3                   # INVALID     $s4, $fp, 0x6A3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14212 | `audioCompandS16` | `0x800A1188` | `0x06A906AF` | `regimm` | `tgeiu       $s5, 0x6AF` |
| funcs_27.c:14214 | `audioCompandS16` | `0x800A118C` | `0x06B506BA` | `regimm` | `.word       0x06B506BA                   # INVALID     $s5, $s5, 0x6BA # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14218 | `audioCompandS16` | `0x800A1194` | `0x06CB06D1` | `regimm` | `tltiu       $s6, 0x6D1` |
| funcs_27.c:14222 | `audioCompandS16` | `0x800A1194` | `0x06CB06D1` | `regimm` | `tltiu       $s6, 0x6D1` |
| funcs_27.c:14224 | `audioCompandS16` | `0x800A1198` | `0x06D706DC` | `regimm` | `.word       0x06D706DC                   # INVALID     $s6, $s7, 0x6DC # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14228 | `audioCompandS16` | `0x800A11A0` | `0x06ED06F3` | `regimm` | `.word       0x06ED06F3                   # INVALID     $s7, $t5, 0x6F3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14233 | `audioCompandS16` | `0x800A11A0` | `0x06ED06F3` | `regimm` | `.word       0x06ED06F3                   # INVALID     $s7, $t5, 0x6F3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14236 | `audioCompandS16` | `0x800A11A4` | `0x06F906FE` | `regimm` | `.word       0x06F906FE                   # INVALID     $s7, $t9, 0x6FE # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14238 | `audioCompandS16` | `0x800A11A8` | `0x0704070A` | `regimm` | `.word       0x0704070A                   # INVALID     $t8, $a0, 0x70A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14240 | `audioCompandS16` | `0x800A11AC` | `0x070F0715` | `regimm` | `.word       0x070F0715                   # INVALID     $t8, $t7, 0x715 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14242 | `audioCompandS16` | `0x800A11B0` | `0x071B0720` | `regimm` | `.word       0x071B0720                   # INVALID     $t8, $k1, 0x720 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14244 | `audioCompandS16` | `0x800A11B4` | `0x0726072B` | `regimm` | `.word       0x0726072B                   # INVALID     $t9, $a2, 0x72B # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14248 | `audioCompandS16` | `0x800A11BC` | `0x073C0742` | `regimm` | `.word       0x073C0742                   # INVALID     $t9, $gp, 0x742 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14253 | `audioCompandS16` | `0x800A11BC` | `0x073C0742` | `regimm` | `.word       0x073C0742                   # INVALID     $t9, $gp, 0x742 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14256 | `audioCompandS16` | `0x800A11C0` | `0x0748074D` | `regimm` | `tgei        $k0, 0x74D` |
| funcs_27.c:14260 | `audioCompandS16` | `0x800A11C8` | `0x075E0763` | `regimm` | `.word       0x075E0763                   # INVALID     $k0, $fp, 0x763 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14266 | `audioCompandS16` | `0x800A11C8` | `0x075E0763` | `regimm` | `.word       0x075E0763                   # INVALID     $k0, $fp, 0x763 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14270 | `audioCompandS16` | `0x800A11CC` | `0x0769076F` | `regimm` | `tgeiu       $k1, 0x76F` |
| funcs_27.c:14272 | `audioCompandS16` | `0x800A11D0` | `0x0774077A` | `regimm` | `.word       0x0774077A                   # INVALID     $k1, $s4, 0x77A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14274 | `audioCompandS16` | `0x800A11D4` | `0x077F0785` | `regimm` | `.word       0x077F0785                   # INVALID     $k1, $ra, 0x785 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14276 | `audioCompandS16` | `0x800A11D8` | `0x078A0790` | `regimm` | `tlti        $gp, 0x790` |
| funcs_27.c:14278 | `audioCompandS16` | `0x800A11DC` | `0x0795079B` | `regimm` | `.word       0x0795079B                   # INVALID     $gp, $s5, 0x79B # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14282 | `audioCompandS16` | `0x800A11E4` | `0x07AC07B1` | `regimm` | `teqi        $sp, 0x7B1` |
| funcs_27.c:14286 | `audioCompandS16` | `0x800A11E4` | `0x07AC07B1` | `regimm` | `teqi        $sp, 0x7B1` |
| funcs_27.c:14288 | `audioCompandS16` | `0x800A11E8` | `0x07B707BC` | `regimm` | `.word       0x07B707BC                   # INVALID     $sp, $s7, 0x7BC # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14292 | `audioCompandS16` | `0x800A11F0` | `0x07CD07D2` | `regimm` | `.word       0x07CD07D2                   # INVALID     $fp, $t5, 0x7D2 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14297 | `audioCompandS16` | `0x800A11F0` | `0x07CD07D2` | `regimm` | `.word       0x07CD07D2                   # INVALID     $fp, $t5, 0x7D2 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14300 | `audioCompandS16` | `0x800A11F4` | `0x07D707DD` | `regimm` | `.word       0x07D707DD                   # INVALID     $fp, $s7, 0x7DD # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14304 | `audioCompandS16` | `0x800A11FC` | `0x07ED07F3` | `regimm` | `.word       0x07ED07F3                   # INVALID     $ra, $t5, 0x7F3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14309 | `audioCompandS16` | `0x800A11FC` | `0x07ED07F3` | `regimm` | `.word       0x07ED07F3                   # INVALID     $ra, $t5, 0x7F3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14312 | `audioCompandS16` | `0x800A1200` | `0x07F807FE` | `regimm` | `.word       0x07F807FE                   # INVALID     $ra, $t8, 0x7FE # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:14314 | `audioCompandS16` | `0x800A1204` | `0x08030809` | `j` | `j           L_800C2024` |
| funcs_27.c:14316 | `audioCompandS16` | `0x800A1208` | `0x080E0813` | `j` | `j           L_8038204C` |
| funcs_27.c:14318 | `audioCompandS16` | `0x800A120C` | `0x0819081E` | `j` | `j           L_80642078` |
| funcs_27.c:14320 | `audioCompandS16` | `0x800A1210` | `0x08240829` | `j` | `j           L_809020A4` |
| funcs_27.c:14322 | `audioCompandS16` | `0x800A1214` | `0x082E0834` | `j` | `j           L_80B820D0` |
| funcs_27.c:14324 | `audioCompandS16` | `0x800A1218` | `0x0839083F` | `j` | `j           L_80E420FC` |
| funcs_27.c:14326 | `audioCompandS16` | `0x800A121C` | `0x08440849` | `j` | `j           L_81102124` |
| funcs_27.c:14328 | `audioCompandS16` | `0x800A1220` | `0x084F0854` | `j` | `j           L_813C2150` |
| funcs_27.c:14330 | `audioCompandS16` | `0x800A1224` | `0x085A085F` | `j` | `j           L_8168217C` |
| funcs_27.c:14332 | `audioCompandS16` | `0x800A1228` | `0x0864086A` | `j` | `j           L_819021A8` |
| funcs_27.c:14334 | `audioCompandS16` | `0x800A122C` | `0x086F0874` | `j` | `j           L_81BC21D0` |
| funcs_27.c:14336 | `audioCompandS16` | `0x800A1230` | `0x087A087F` | `j` | `j           L_81E821FC` |
| funcs_27.c:14338 | `audioCompandS16` | `0x800A1234` | `0x0884088A` | `j` | `j           L_82102228` |
| funcs_27.c:14340 | `audioCompandS16` | `0x800A1238` | `0x088F0894` | `j` | `j           L_823C2250` |
| funcs_27.c:14342 | `audioCompandS16` | `0x800A123C` | `0x0899089F` | `j` | `j           L_8264227C` |
| funcs_27.c:14344 | `audioCompandS16` | `0x800A1240` | `0x08A408A9` | `j` | `j           L_829022A4` |
| funcs_27.c:14346 | `audioCompandS16` | `0x800A1244` | `0x08AF08B4` | `j` | `j           L_82BC22D0` |
| funcs_27.c:14348 | `audioCompandS16` | `0x800A1248` | `0x08B908BE` | `j` | `j           L_82E422F8` |
| funcs_27.c:14350 | `audioCompandS16` | `0x800A124C` | `0x08C408C9` | `j` | `j           L_83102324` |
| funcs_27.c:14352 | `audioCompandS16` | `0x800A1250` | `0x08CE08D3` | `j` | `j           L_8338234C` |
| funcs_27.c:14354 | `audioCompandS16` | `0x800A1254` | `0x08D908DE` | `j` | `j           L_83642378` |
| funcs_27.c:14356 | `audioCompandS16` | `0x800A1258` | `0x08E308E8` | `j` | `j           L_838C23A0` |
| funcs_27.c:14358 | `audioCompandS16` | `0x800A125C` | `0x08EE08F3` | `j` | `j           L_83B823CC` |
| funcs_27.c:14360 | `audioCompandS16` | `0x800A1260` | `0x08F808FD` | `j` | `j           L_83E023F4` |
| funcs_27.c:14362 | `audioCompandS16` | `0x800A1264` | `0x09020908` | `j` | `j           L_84082420` |
| funcs_27.c:14364 | `audioCompandS16` | `0x800A1268` | `0x090D0912` | `j` | `j           L_84342448` |
| funcs_27.c:14366 | `audioCompandS16` | `0x800A126C` | `0x0917091C` | `j` | `j           L_845C2470` |
| funcs_27.c:14368 | `audioCompandS16` | `0x800A1270` | `0x09210927` | `j` | `j           L_8484249C` |
| funcs_27.c:14370 | `audioCompandS16` | `0x800A1274` | `0x092C0931` | `j` | `j           L_84B024C4` |
| funcs_27.c:14372 | `audioCompandS16` | `0x800A1278` | `0x0936093B` | `j` | `j           L_84D824EC` |
| funcs_27.c:14374 | `audioCompandS16` | `0x800A127C` | `0x09400945` | `j` | `j           L_85002514` |
| funcs_27.c:14376 | `audioCompandS16` | `0x800A1280` | `0x094B0950` | `j` | `j           L_852C2540` |
| funcs_27.c:14378 | `audioCompandS16` | `0x800A1284` | `0x0955095A` | `j` | `j           L_85542568` |
| funcs_27.c:14380 | `audioCompandS16` | `0x800A1288` | `0x095F0964` | `j` | `j           L_857C2590` |
| funcs_27.c:14382 | `audioCompandS16` | `0x800A128C` | `0x0969096E` | `j` | `j           L_85A425B8` |
| funcs_27.c:14384 | `audioCompandS16` | `0x800A1290` | `0x09730978` | `j` | `j           L_85CC25E0` |
| funcs_27.c:14386 | `audioCompandS16` | `0x800A1294` | `0x097D0982` | `j` | `j           L_85F42608` |
| funcs_27.c:14388 | `audioCompandS16` | `0x800A1298` | `0x0987098D` | `j` | `j           L_861C2634` |
| funcs_27.c:14390 | `audioCompandS16` | `0x800A129C` | `0x09920997` | `j` | `j           L_8648265C` |
| funcs_27.c:14392 | `audioCompandS16` | `0x800A12A0` | `0x099C09A1` | `j` | `j           L_86702684` |
| funcs_27.c:14394 | `audioCompandS16` | `0x800A12A4` | `0x09A609AB` | `j` | `j           L_869826AC` |
| funcs_27.c:14396 | `audioCompandS16` | `0x800A12A8` | `0x09B009B5` | `j` | `j           L_86C026D4` |
| funcs_27.c:14398 | `audioCompandS16` | `0x800A12AC` | `0x09BA09BF` | `j` | `j           L_86E826FC` |
| funcs_27.c:14400 | `audioCompandS16` | `0x800A12B0` | `0x09C409C9` | `j` | `j           L_87102724` |
| funcs_27.c:14402 | `audioCompandS16` | `0x800A12B4` | `0x09CE09D3` | `j` | `j           L_8738274C` |
| funcs_27.c:14404 | `audioCompandS16` | `0x800A12B8` | `0x09D709DC` | `j` | `j           L_875C2770` |
| funcs_27.c:14406 | `audioCompandS16` | `0x800A12BC` | `0x09E109E6` | `j` | `j           L_87842798` |
| funcs_27.c:14408 | `audioCompandS16` | `0x800A12C0` | `0x09EB09F0` | `j` | `j           L_87AC27C0` |
| funcs_27.c:14410 | `audioCompandS16` | `0x800A12C4` | `0x09F509FA` | `j` | `j           L_87D427E8` |
| funcs_27.c:14412 | `audioCompandS16` | `0x800A12C8` | `0x09FF0A04` | `j` | `j           L_87FC2810` |
| funcs_27.c:14414 | `audioCompandS16` | `0x800A12CC` | `0x0A090A0E` | `j` | `j           L_88242838` |
| funcs_27.c:14416 | `audioCompandS16` | `0x800A12D0` | `0x0A120A17` | `j` | `j           L_8848285C` |
| funcs_27.c:14418 | `audioCompandS16` | `0x800A12D4` | `0x0A1C0A21` | `j` | `j           L_88702884` |
| funcs_27.c:14420 | `audioCompandS16` | `0x800A12D8` | `0x0A260A2B` | `j` | `j           L_889828AC` |
| funcs_27.c:14422 | `audioCompandS16` | `0x800A12DC` | `0x0A300A35` | `j` | `j           L_88C028D4` |
| funcs_27.c:14424 | `audioCompandS16` | `0x800A12E0` | `0x0A390A3E` | `j` | `j           L_88E428F8` |
| funcs_27.c:14426 | `audioCompandS16` | `0x800A12E4` | `0x0A430A48` | `j` | `j           L_890C2920` |
| funcs_27.c:14428 | `audioCompandS16` | `0x800A12E8` | `0x0A4D0A51` | `j` | `j           L_89342944` |
| funcs_27.c:14430 | `audioCompandS16` | `0x800A12EC` | `0x0A560A5B` | `j` | `j           L_8958296C` |
| funcs_27.c:14432 | `audioCompandS16` | `0x800A12F0` | `0x0A600A65` | `j` | `j           L_89802994` |
| funcs_27.c:14434 | `audioCompandS16` | `0x800A12F4` | `0x0A690A6E` | `j` | `j           L_89A429B8` |
| funcs_27.c:14436 | `audioCompandS16` | `0x800A12F8` | `0x0A730A78` | `j` | `j           L_89CC29E0` |
| funcs_27.c:14438 | `audioCompandS16` | `0x800A12FC` | `0x0A7C0A81` | `j` | `j           L_89F02A04` |
| funcs_27.c:14440 | `audioCompandS16` | `0x800A1300` | `0x0A860A8B` | `j` | `j           L_8A182A2C` |
| funcs_27.c:14442 | `audioCompandS16` | `0x800A1304` | `0x0A8F0A94` | `j` | `j           L_8A3C2A50` |
| funcs_27.c:14444 | `audioCompandS16` | `0x800A1308` | `0x0A990A9D` | `j` | `j           L_8A642A74` |
| funcs_27.c:14446 | `audioCompandS16` | `0x800A130C` | `0x0AA20AA7` | `j` | `j           L_8A882A9C` |
| funcs_27.c:14448 | `audioCompandS16` | `0x800A1310` | `0x0AAC0AB0` | `j` | `j           L_8AB02AC0` |
| funcs_27.c:14450 | `audioCompandS16` | `0x800A1314` | `0x0AB50ABA` | `j` | `j           L_8AD42AE8` |
| funcs_27.c:14452 | `audioCompandS16` | `0x800A1318` | `0x0ABE0AC3` | `j` | `j           L_8AF82B0C` |
| funcs_27.c:14454 | `audioCompandS16` | `0x800A131C` | `0x0AC80ACC` | `j` | `j           L_8B202B30` |
| funcs_27.c:14456 | `audioCompandS16` | `0x800A1320` | `0x0AD10AD5` | `j` | `j           L_8B442B54` |
| funcs_27.c:14458 | `audioCompandS16` | `0x800A1324` | `0x0ADA0ADF` | `j` | `j           L_8B682B7C` |
| funcs_27.c:14460 | `audioCompandS16` | `0x800A1328` | `0x0AE30AE8` | `j` | `j           L_8B8C2BA0` |
| funcs_27.c:14462 | `audioCompandS16` | `0x800A132C` | `0x0AEC0AF1` | `j` | `j           L_8BB02BC4` |
| funcs_27.c:14464 | `audioCompandS16` | `0x800A1330` | `0x0AF60AFA` | `j` | `j           L_8BD82BE8` |
| funcs_27.c:14466 | `audioCompandS16` | `0x800A1334` | `0x0AFF0B03` | `j` | `j           L_8BFC2C0C` |
| funcs_27.c:14468 | `audioCompandS16` | `0x800A1338` | `0x0B080B0C` | `j` | `j           L_8C202C30` |
| funcs_27.c:14470 | `audioCompandS16` | `0x800A133C` | `0x0B110B15` | `j` | `j           L_8C442C54` |
| funcs_27.c:14472 | `audioCompandS16` | `0x800A1340` | `0x0B1A0B1F` | `j` | `j           L_8C682C7C` |
| funcs_27.c:14474 | `audioCompandS16` | `0x800A1344` | `0x0B230B28` | `j` | `j           L_8C8C2CA0` |
| funcs_27.c:14476 | `audioCompandS16` | `0x800A1348` | `0x0B2C0B31` | `j` | `j           L_8CB02CC4` |
| funcs_27.c:14478 | `audioCompandS16` | `0x800A134C` | `0x0B350B3A` | `j` | `j           L_8CD42CE8` |
| funcs_27.c:14480 | `audioCompandS16` | `0x800A1350` | `0x0B3E0B42` | `j` | `j           L_8CF82D08` |
| funcs_27.c:14482 | `audioCompandS16` | `0x800A1354` | `0x0B470B4B` | `j` | `j           L_8D1C2D2C` |
| funcs_27.c:14484 | `audioCompandS16` | `0x800A1358` | `0x0B500B54` | `j` | `j           L_8D402D50` |
| funcs_27.c:14486 | `audioCompandS16` | `0x800A135C` | `0x0B590B5D` | `j` | `j           L_8D642D74` |
| funcs_27.c:14488 | `audioCompandS16` | `0x800A1360` | `0x0B620B66` | `j` | `j           L_8D882D98` |
| funcs_27.c:14490 | `audioCompandS16` | `0x800A1364` | `0x0B6A0B6F` | `j` | `j           L_8DA82DBC` |
| funcs_27.c:14492 | `audioCompandS16` | `0x800A1368` | `0x0B730B78` | `j` | `j           L_8DCC2DE0` |
| funcs_27.c:14494 | `audioCompandS16` | `0x800A136C` | `0x0B7C0B80` | `j` | `j           L_8DF02E00` |
| funcs_27.c:14496 | `audioCompandS16` | `0x800A1370` | `0x0B850B89` | `j` | `j           L_8E142E24` |
| funcs_27.c:14498 | `audioCompandS16` | `0x800A1374` | `0x0B8D0B92` | `j` | `j           L_8E342E48` |
| funcs_27.c:14500 | `audioCompandS16` | `0x800A1378` | `0x0B960B9A` | `j` | `j           L_8E582E68` |
| funcs_27.c:14502 | `audioCompandS16` | `0x800A137C` | `0x0B9F0BA3` | `j` | `j           L_8E7C2E8C` |
| funcs_27.c:14504 | `audioCompandS16` | `0x800A1380` | `0x0BA70BAC` | `j` | `j           L_8E9C2EB0` |
| funcs_27.c:14506 | `audioCompandS16` | `0x800A1384` | `0x0BB00BB4` | `j` | `j           L_8EC02ED0` |
| funcs_27.c:14508 | `audioCompandS16` | `0x800A1388` | `0x0BB80BBD` | `j` | `j           L_8EE02EF4` |
| funcs_27.c:14510 | `audioCompandS16` | `0x800A138C` | `0x0BC10BC5` | `j` | `j           L_8F042F14` |
| funcs_27.c:14512 | `audioCompandS16` | `0x800A1390` | `0x0BCA0BCE` | `j` | `j           L_8F282F38` |
| funcs_27.c:14514 | `audioCompandS16` | `0x800A1394` | `0x0BD20BD6` | `j` | `j           L_8F482F58` |
| funcs_27.c:14516 | `audioCompandS16` | `0x800A1398` | `0x0BDA0BDF` | `j` | `j           L_8F682F7C` |
| funcs_27.c:14518 | `audioCompandS16` | `0x800A139C` | `0x0BE30BE7` | `j` | `j           L_8F8C2F9C` |
| funcs_27.c:14520 | `audioCompandS16` | `0x800A13A0` | `0x0BEB0BEF` | `j` | `j           L_8FAC2FBC` |
| funcs_27.c:14522 | `audioCompandS16` | `0x800A13A4` | `0x0BF40BF8` | `j` | `j           L_8FD02FE0` |
| funcs_27.c:14524 | `audioCompandS16` | `0x800A13A8` | `0x0BFC0C00` | `j` | `j           L_8FF03000` |
| funcs_27.c:98926 | `audioCompandS16` | `0x800A1790` | `0x00000005` | `special_0x05 $zero,$zero,$zero` | `.word       0x00000005                   # INVALID     $zero, $zero, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:98934 | `audioCompandS16` | `0x800A17A0` | `0x0035003D` | `special_0x3D $zero,$at,$s5` | `.word       0x0035003D                   # INVALID     $at, $s5, 0x3D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:98936 | `audioCompandS16` | `0x800A17A4` | `0x0045004E` | `special_0x0E $zero,$v0,$a1` | `.word       0x0045004E                   # INVALID     $v0, $a1, 0x4E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:98940 | `audioCompandS16` | `0x800A17AC` | `0x006B0075` | `special_0x35 $zero,$v1,$t3` | `.word       0x006B0075                   # INVALID     $v1, $t3, 0x75 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:98942 | `audioCompandS16` | `0x800A17B0` | `0x0080008B` | `movn $zero,$a0,$zero` | `.word       0x0080008B                   # movn        $zero, $a0, $zero # 00000080 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:98961 | `audioCompandS16` | `0x800A17D8` | `0x01E201FD` | `special_0x3D $zero,$t7,$v0` | `.word       0x01E201FD                   # INVALID     $t7, $v0, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:98965 | `audioCompandS16` | `0x800A17D8` | `0x01E201FD` | `special_0x3D $zero,$t7,$v0` | `.word       0x01E201FD                   # INVALID     $t7, $v0, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:98967 | `audioCompandS16` | `0x800A17DC` | `0x021A0237` | `special_0x37 $zero,$s0,$k0` | `.word       0x021A0237                   # INVALID     $s0, $k0, 0x237 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:98969 | `audioCompandS16` | `0x800A17E0` | `0x02560276` | `special_0x36 $zero,$s2,$s6` | `tne         $s2, $s6, 9` |
| funcs_27.c:98977 | `audioCompandS16` | `0x800A17F0` | `0x038303B1` | `special_0x31 $zero,$gp,$v1` | `tgeu        $gp, $v1, 14` |
| funcs_27.c:98981 | `audioCompandS16` | `0x800A17F8` | `0x0446047C` | `regimm` | `.word       0x0446047C                   # INVALID     $v0, $a2, 0x47C # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:98983 | `audioCompandS16` | `0x800A17FC` | `0x04B404EF` | `regimm` | `.word       0x04B404EF                   # INVALID     $a1, $s4, 0x4EF # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:98985 | `audioCompandS16` | `0x800A1800` | `0x052D056D` | `regimm` | `.word       0x052D056D                   # INVALID     $t1, $t5, 0x56D # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:98991 | `audioCompandS16` | `0x800A180C` | `0x06DC0730` | `regimm` | `.word       0x06DC0730                   # INVALID     $s6, $gp, 0x730 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:99000 | `audioCompandS16` | `0x800A180C` | `0x06DC0730` | `regimm` | `.word       0x06DC0730                   # INVALID     $s6, $gp, 0x730 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:99005 | `audioCompandS16` | `0x800A180C` | `0x06DC0730` | `regimm` | `.word       0x06DC0730                   # INVALID     $s6, $gp, 0x730 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:99007 | `audioCompandS16` | `0x800A1810` | `0x078707E2` | `regimm` | `.word       0x078707E2                   # INVALID     $gp, $a3, 0x7E2 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:99009 | `audioCompandS16` | `0x800A1814` | `0x084108A4` | `j` | `j           L_81042290` |
| funcs_27.c:99011 | `audioCompandS16` | `0x800A1818` | `0x090C0978` | `j` | `j           L_843025E0` |
| funcs_27.c:99013 | `audioCompandS16` | `0x800A181C` | `0x09E90A5F` | `j` | `j           L_87A4297C` |
| funcs_27.c:99015 | `audioCompandS16` | `0x800A1820` | `0x0ADB0B5B` | `j` | `j           L_8B6C2D6C` |
| funcs_27.c:99017 | `audioCompandS16` | `0x800A1824` | `0x0BE20C6E` | `j` | `j           L_8F8831B8` |
| funcs_27.c:99324 | `audioCompandS16` | `0x800A1874` | `0x459048AA` | `cop1` | `.word       0x459048AA                   # INVALID     $t4, $s0, 0x48AA # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_27.c:99326 | `audioCompandS16` | `0x800A1878` | `0x4BE74F49` | `opcode_0x12` | `.word       0x4BE74F49                   # INVALID     $ra, $a3, 0x4F49 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_27.c:99352 | `audioCompandS16` | `0x800A188C` | `0x75557A8D` | `opcode_0x1D` | `.word       0x75557A8D                   # INVALID     $t2, $s5, 0x7A8D # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:99374 | `audioCompandS16` | `0x800A18B0` | `0xC041C2FA` | `opcode_0x30` | `ll          $at, -0x3D06($v0)` |
| funcs_27.c:99378 | `audioCompandS16` | `0x800A18B8` | `0xCA7ACCC4` | `opcode_0x32` | `lwc2        $26, -0x333C($s3)` |
| funcs_27.c:99380 | `audioCompandS16` | `0x800A18BC` | `0xCEF6D10F` | `opcode_0x33` | `pref        $s6, -0x2EF1($s7)` |
| funcs_27.c:99382 | `audioCompandS16` | `0x800A18C0` | `0xD312D4FF` | `opcode_0x34` | `lld         $s2, -0x2B01($t8)` |
| funcs_27.c:99387 | `audioCompandS16` | `0x800A18C8` | `0xDA4DDBEB` | `opcode_0x36` | `ldc2        $13, -0x2415($s2)` |
| funcs_27.c:99391 | `audioCompandS16` | `0x800A18D0` | `0xE061E1BE` | `opcode_0x38` | `sc          $at, -0x1E42($v1)` |
| funcs_27.c:99393 | `audioCompandS16` | `0x800A18D4` | `0xE30BE44B` | `opcode_0x38` | `sc          $t3, -0x1BB5($t8)` |
| funcs_27.c:99403 | `audioCompandS16` | `0x800A18E0` | `0xE9CAEAC0` | `opcode_0x3A` | `swc2        $10, -0x1540($t6)` |
| funcs_27.c:99405 | `audioCompandS16` | `0x800A18E4` | `0xEBACEC8E` | `opcode_0x3A` | `swc2        $12, -0x1372($sp)` |
| funcs_27.c:99407 | `audioCompandS16` | `0x800A18E8` | `0xED67EE36` | `opcode_0x3B` | `.word       0xED67EE36                   # INVALID     $t3, $a3, -0x11CA # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:99409 | `audioCompandS16` | `0x800A18EC` | `0xEEFDEFBB` | `opcode_0x3B` | `.word       0xEEFDEFBB                   # INVALID     $s7, $sp, -0x1045 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:99411 | `audioCompandS16` | `0x800A18F0` | `0xF071F11F` | `opcode_0x3C` | `scd         $s1, -0xEE1($v1)` |
| funcs_27.c:99413 | `audioCompandS16` | `0x800A18F4` | `0xF1C6F266` | `opcode_0x3C` | `scd         $a2, -0xD9A($t6)` |
| funcs_27.c:99415 | `audioCompandS16` | `0x800A18F8` | `0xF2FFF392` | `opcode_0x3C` | `scd         $ra, -0xC6E($s7)` |
| funcs_27.c:99436 | `audioCompandS16` | `0x800A1910` | `0xF879F8D0` | `opcode_0x3E` | `sdc2        $25, -0x730($v1)` |
| funcs_27.c:99438 | `audioCompandS16` | `0x800A1914` | `0xF924F974` | `opcode_0x3E` | `sdc2        $4, -0x68C($t1)` |
| funcs_27.c:99440 | `audioCompandS16` | `0x800A1918` | `0xF9C0FA09` | `opcode_0x3E` | `sdc2        $0, -0x5F7($t6)` |
| funcs_27.c:99442 | `audioCompandS16` | `0x800A191C` | `0xFA50FA93` | `opcode_0x3E` | `sdc2        $16, -0x56D($s2)` |
| funcs_27.c:99444 | `audioCompandS16` | `0x800A1920` | `0xFAD3FB11` | `opcode_0x3E` | `sdc2        $19, -0x4EF($s6)` |
| funcs_27.c:99446 | `audioCompandS16` | `0x800A1924` | `0xFB4CFB84` | `opcode_0x3E` | `sdc2        $12, -0x47C($k0)` |
| funcs_27.c:99448 | `audioCompandS16` | `0x800A1928` | `0xFBBAFBEE` | `opcode_0x3E` | `sdc2        $26, -0x412($sp)` |
| funcs_27.c:99577 | `audioCompandS16` | `0x800A19E4` | `0x00000B05` | `special_0x05 $at,$zero,$zero` | `.word       0x00000B05                   # INVALID     $zero, $zero, 0xB05 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99581 | `audioCompandS16` | `0x800A19EC` | `0x00000F09` | `jalr $at,$zero,$zero` | `.word       0x00000F09                   # jalr        $at, $zero # 00000700 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99607 | `audioCompandS16` | `0x800A1A10` | `0x00000101` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000101                   # INVALID     $zero, $zero, 0x101 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99609 | `audioCompandS16` | `0x800A1A14` | `0x00000301` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000301                   # INVALID     $zero, $zero, 0x301 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99611 | `audioCompandS16` | `0x800A1A18` | `0x00000501` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000501                   # INVALID     $zero, $zero, 0x501 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99613 | `audioCompandS16` | `0x800A1A1C` | `0x00000701` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000701                   # INVALID     $zero, $zero, 0x701 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99620 | `audioCompandS16` | `0x800A1A2C` | `0x0000100A` | `movz $v0,$zero,$zero` | `movz        $v0, $zero, $zero` |
| funcs_27.c:99624 | `audioCompandS16` | `0x800A1A2C` | `0x0000100A` | `movz $v0,$zero,$zero` | `movz        $v0, $zero, $zero` |
| funcs_27.c:99658 | `audioCompandS16` | `0x800A1A60` | `0x00000B05` | `special_0x05 $at,$zero,$zero` | `.word       0x00000B05                   # INVALID     $zero, $zero, 0xB05 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99662 | `audioCompandS16` | `0x800A1A68` | `0x00001009` | `jalr $v0,$zero,$zero` | `jalr        $v0, $zero` |
| funcs_27.c:99664 | `audioCompandS16` | `0x800A1A6C` | `0x0000120B` | `movn $v0,$zero,$zero` | `.word       0x0000120B                   # movn        $v0, $zero, $zero # 00000200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99701 | `audioCompandS16` | `0x800A1AA8` | `0x0000110A` | `movz $v0,$zero,$zero` | `.word       0x0000110A                   # movz        $v0, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99705 | `audioCompandS16` | `0x800A1AA8` | `0x0000110A` | `movz $v0,$zero,$zero` | `.word       0x0000110A                   # movz        $v0, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99744 | `audioCompandS16` | `0x800A1AE4` | `0x00001009` | `jalr $v0,$zero,$zero` | `jalr        $v0, $zero` |
| funcs_27.c:99746 | `audioCompandS16` | `0x800A1AE8` | `0x0000130B` | `movn $v0,$zero,$zero` | `.word       0x0000130B                   # movn        $v0, $zero, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99748 | `audioCompandS16` | `0x800A1AEC` | `0x0000160D` | `break $v0,$zero,$zero` | `break       0, 88` |
| funcs_27.c:99775 | `audioCompandS16` | `0x800A1B10` | `0x00000105` | `special_0x05 $zero,$zero,$zero` | `.word       0x00000105                   # INVALID     $zero, $zero, 0x105 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99777 | `audioCompandS16` | `0x800A1B14` | `0x00000405` | `special_0x05 $zero,$zero,$zero` | `.word       0x00000405                   # INVALID     $zero, $zero, 0x405 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99779 | `audioCompandS16` | `0x800A1B18` | `0x00000705` | `special_0x05 $zero,$zero,$zero` | `.word       0x00000705                   # INVALID     $zero, $zero, 0x705 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99781 | `audioCompandS16` | `0x800A1B1C` | `0x00000A05` | `special_0x05 $at,$zero,$zero` | `.word       0x00000A05                   # INVALID     $zero, $zero, 0xA05 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99784 | `audioCompandS16` | `0x800A1B24` | `0x0000110A` | `movz $v0,$zero,$zero` | `.word       0x0000110A                   # movz        $v0, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99788 | `audioCompandS16` | `0x800A1B24` | `0x0000110A` | `movz $v0,$zero,$zero` | `.word       0x0000110A                   # movz        $v0, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99793 | `audioCompandS16` | `0x800A1B2C` | `0x0000170E` | `special_0x0E $v0,$zero,$zero` | `.word       0x0000170E                   # INVALID     $zero, $zero, 0x170E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99827 | `audioCompandS16` | `0x800A1B60` | `0x00000F09` | `jalr $at,$zero,$zero` | `.word       0x00000F09                   # jalr        $at, $zero # 00000700 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99829 | `audioCompandS16` | `0x800A1B64` | `0x0000120B` | `movn $v0,$zero,$zero` | `.word       0x0000120B                   # movn        $v0, $zero, $zero # 00000200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99831 | `audioCompandS16` | `0x800A1B68` | `0x0000160D` | `break $v0,$zero,$zero` | `break       0, 88` |
| funcs_27.c:99833 | `audioCompandS16` | `0x800A1B6C` | `0x0000190F` | `special_0x0F $v1,$zero,$zero` | `.word       0x0000190F                   # sync # 00001900 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99867 | `audioCompandS16` | `0x800A1BA0` | `0x0000120A` | `movz $v0,$zero,$zero` | `.word       0x0000120A                   # movz        $v0, $zero, $zero # 00000200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99872 | `audioCompandS16` | `0x800A1BA8` | `0x00001A0E` | `special_0x0E $v1,$zero,$zero` | `.word       0x00001A0E                   # INVALID     $zero, $zero, 0x1A0E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99904 | `audioCompandS16` | `0x800A1BE0` | `0x0000130B` | `movn $v0,$zero,$zero` | `.word       0x0000130B                   # movn        $v0, $zero, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99917 | `audioCompandS16` | `0x800A1BE0` | `0x0000130B` | `movn $v0,$zero,$zero` | `.word       0x0000130B                   # movn        $v0, $zero, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99927 | `audioCompandS16` | `0x800A1BE0` | `0x0000130B` | `movn $v0,$zero,$zero` | `.word       0x0000130B                   # movn        $v0, $zero, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99934 | `audioCompandS16` | `0x800A1BE0` | `0x0000130B` | `movn $v0,$zero,$zero` | `.word       0x0000130B                   # movn        $v0, $zero, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99938 | `audioCompandS16` | `0x800A1BE0` | `0x0000130B` | `movn $v0,$zero,$zero` | `.word       0x0000130B                   # movn        $v0, $zero, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99940 | `audioCompandS16` | `0x800A1BE4` | `0x0000170D` | `break $v0,$zero,$zero` | `break       0, 92` |
| funcs_27.c:99942 | `audioCompandS16` | `0x800A1BE8` | `0x00001B0F` | `special_0x0F $v1,$zero,$zero` | `.word       0x00001B0F                   # sync # 00001B00 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99970 | `audioCompandS16` | `0x800A1C10` | `0x00000209` | `jalr $zero,$zero,$zero` | `.word       0x00000209                   # jalr        $zero, $zero # 00000200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99972 | `audioCompandS16` | `0x800A1C14` | `0x00000609` | `jalr $zero,$zero,$zero` | `.word       0x00000609                   # jalr        $zero, $zero # 00000600 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99974 | `audioCompandS16` | `0x800A1C18` | `0x00000B09` | `jalr $at,$zero,$zero` | `.word       0x00000B09                   # jalr        $at, $zero # 00000300 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99976 | `audioCompandS16` | `0x800A1C1C` | `0x00000F09` | `jalr $at,$zero,$zero` | `.word       0x00000F09                   # jalr        $at, $zero # 00000700 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:99981 | `audioCompandS16` | `0x800A1C24` | `0x0000190E` | `special_0x0E $v1,$zero,$zero` | `.word       0x0000190E                   # INVALID     $zero, $zero, 0x190E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100011 | `audioCompandS16` | `0x800A1C50` | `0x0000020A` | `movz $zero,$zero,$zero` | `.word       0x0000020A                   # movz        $zero, $zero, $zero # 00000200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100013 | `audioCompandS16` | `0x800A1C54` | `0x0000070A` | `movz $zero,$zero,$zero` | `.word       0x0000070A                   # movz        $zero, $zero, $zero # 00000700 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100015 | `audioCompandS16` | `0x800A1C58` | `0x00000C0A` | `movz $at,$zero,$zero` | `.word       0x00000C0A                   # movz        $at, $zero, $zero # 00000400 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100017 | `audioCompandS16` | `0x800A1C5C` | `0x0000110A` | `movz $v0,$zero,$zero` | `.word       0x0000110A                   # movz        $v0, $zero, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100019 | `audioCompandS16` | `0x800A1C60` | `0x0000170D` | `break $v0,$zero,$zero` | `break       0, 92` |
| funcs_27.c:100021 | `audioCompandS16` | `0x800A1C64` | `0x00001C0F` | `special_0x0F $v1,$zero,$zero` | `.word       0x00001C0F                   # sync # 00001C00 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100051 | `audioCompandS16` | `0x800A1C90` | `0x0000020B` | `movn $zero,$zero,$zero` | `.word       0x0000020B                   # movn        $zero, $zero, $zero # 00000200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100053 | `audioCompandS16` | `0x800A1C94` | `0x0000070B` | `movn $zero,$zero,$zero` | `.word       0x0000070B                   # movn        $zero, $zero, $zero # 00000700 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100055 | `audioCompandS16` | `0x800A1C98` | `0x00000D0B` | `movn $at,$zero,$zero` | `.word       0x00000D0B                   # movn        $at, $zero, $zero # 00000500 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100057 | `audioCompandS16` | `0x800A1C9C` | `0x0000120B` | `movn $v0,$zero,$zero` | `.word       0x0000120B                   # movn        $v0, $zero, $zero # 00000200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100059 | `audioCompandS16` | `0x800A1CA0` | `0x0000190E` | `special_0x0E $v1,$zero,$zero` | `.word       0x0000190E                   # INVALID     $zero, $zero, 0x190E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100103 | `audioCompandS16` | `0x800A1CE0` | `0x00001C0F` | `special_0x0F $v1,$zero,$zero` | `.word       0x00001C0F                   # sync # 00001C00 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100109 | `audioCompandS16` | `0x800A1CEC` | `0x00002E15` | `special_0x15 $a1,$zero,$zero` | `.word       0x00002E15                   # INVALID     $zero, $zero, 0x2E15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100135 | `audioCompandS16` | `0x800A1D10` | `0x0000030D` | `break $zero,$zero,$zero` | `break       0, 12` |
| funcs_27.c:100137 | `audioCompandS16` | `0x800A1D14` | `0x00000A0D` | `break $at,$zero,$zero` | `break       0, 40` |
| funcs_27.c:100139 | `audioCompandS16` | `0x800A1D18` | `0x0000110D` | `break $v0,$zero,$zero` | `break       0, 68` |
| funcs_27.c:100141 | `audioCompandS16` | `0x800A1D1C` | `0x0000180D` | `break $v1,$zero,$zero` | `break       0, 96` |
| funcs_27.c:100175 | `audioCompandS16` | `0x800A1D50` | `0x0000030E` | `special_0x0E $zero,$zero,$zero` | `.word       0x0000030E                   # INVALID     $zero, $zero, 0x30E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100177 | `audioCompandS16` | `0x800A1D54` | `0x00000A0E` | `special_0x0E $at,$zero,$zero` | `.word       0x00000A0E                   # INVALID     $zero, $zero, 0xA0E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100179 | `audioCompandS16` | `0x800A1D58` | `0x0000120E` | `special_0x0E $v0,$zero,$zero` | `.word       0x0000120E                   # INVALID     $zero, $zero, 0x120E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100181 | `audioCompandS16` | `0x800A1D5C` | `0x0000190E` | `special_0x0E $v1,$zero,$zero` | `.word       0x0000190E                   # INVALID     $zero, $zero, 0x190E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100187 | `audioCompandS16` | `0x800A1D68` | `0x00003115` | `special_0x15 $a2,$zero,$zero` | `.word       0x00003115                   # INVALID     $zero, $zero, 0x3115 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100215 | `audioCompandS16` | `0x800A1D90` | `0x0000040F` | `sync $zero,$zero,$zero` | `.word       0x0000040F                   # sync # 00000400 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100217 | `audioCompandS16` | `0x800A1D94` | `0x00000C0F` | `special_0x0F $at,$zero,$zero` | `.word       0x00000C0F                   # sync # 00000C00 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100219 | `audioCompandS16` | `0x800A1D98` | `0x0000150F` | `special_0x0F $v0,$zero,$zero` | `.word       0x0000150F                   # sync # 00001500 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100221 | `audioCompandS16` | `0x800A1D9C` | `0x00001D0F` | `special_0x0F $v1,$zero,$zero` | `.word       0x00001D0F                   # sync # 00001D00 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100265 | `audioCompandS16` | `0x800A1DE4` | `0x00003215` | `special_0x15 $a2,$zero,$zero` | `.word       0x00003215                   # INVALID     $zero, $zero, 0x3215 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100343 | `audioCompandS16` | `0x800A1E60` | `0x00003215` | `special_0x15 $a2,$zero,$zero` | `.word       0x00003215                   # INVALID     $zero, $zero, 0x3215 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100455 | `audioCompandS16` | `0x800A1F10` | `0x00000715` | `special_0x15 $zero,$zero,$zero` | `.word       0x00000715                   # INVALID     $zero, $zero, 0x715 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100457 | `audioCompandS16` | `0x800A1F14` | `0x00001615` | `special_0x15 $v0,$zero,$zero` | `.word       0x00001615                   # INVALID     $zero, $zero, 0x1615 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100460 | `audioCompandS16` | `0x800A1F18` | `0x00002515` | `special_0x15 $a0,$zero,$zero` | `.word       0x00002515                   # INVALID     $zero, $zero, 0x2515 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100462 | `audioCompandS16` | `0x800A1F1C` | `0x00003415` | `special_0x15 $a2,$zero,$zero` | `.word       0x00003415                   # INVALID     $zero, $zero, 0x3415 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100872 | `audioCompandS16` | `0x800A21AC` | `0x00012528` | `special_0x28 $a0,$zero,$at` | `.word       0x00012528                   # INVALID     $zero, $at, 0x2528 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100912 | `audioCompandS16` | `0x800A21EC` | `0x00014329` | `special_0x29 $t0,$zero,$at` | `.word       0x00014329                   # INVALID     $zero, $at, 0x4329 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100951 | `audioCompandS16` | `0x800A2228` | `0x00013428` | `special_0x28 $a2,$zero,$at` | `.word       0x00013428                   # INVALID     $zero, $at, 0x3428 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:100991 | `audioCompandS16` | `0x800A2268` | `0x00015329` | `special_0x29 $t2,$zero,$at` | `.word       0x00015329                   # INVALID     $zero, $at, 0x5329 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101029 | `audioCompandS16` | `0x800A22A4` | `0x00013B28` | `special_0x28 $a3,$zero,$at` | `.word       0x00013B28                   # INVALID     $zero, $at, 0x3B28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101069 | `audioCompandS16` | `0x800A22E4` | `0x00015B29` | `special_0x29 $t3,$zero,$at` | `.word       0x00015B29                   # INVALID     $zero, $at, 0x5B29 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101108 | `audioCompandS16` | `0x800A2320` | `0x00013928` | `special_0x28 $a3,$zero,$at` | `.word       0x00013928                   # INVALID     $zero, $at, 0x3928 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101148 | `audioCompandS16` | `0x800A2360` | `0x00015929` | `special_0x29 $t3,$zero,$at` | `.word       0x00015929                   # INVALID     $zero, $at, 0x5929 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101194 | `audioCompandS16` | `0x800A23AC` | `0x00027730` | `special_0x30 $t6,$zero,$v0` | `tge         $zero, $v0, 476` |
| funcs_27.c:101221 | `audioCompandS16` | `0x800A23D0` | `0x00002E28` | `special_0x28 $a1,$zero,$zero` | `.word       0x00002E28                   # INVALID     $zero, $zero, 0x2E28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101223 | `audioCompandS16` | `0x800A23D4` | `0x00008A28` | `special_0x28 $s1,$zero,$zero` | `.word       0x00008A28                   # INVALID     $zero, $zero, -0x75D8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101225 | `audioCompandS16` | `0x800A23D8` | `0x0000E728` | `special_0x28 $gp,$zero,$zero` | `.word       0x0000E728                   # INVALID     $zero, $zero, -0x18D8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101227 | `audioCompandS16` | `0x800A23DC` | `0x00014328` | `special_0x28 $t0,$zero,$at` | `.word       0x00014328                   # INVALID     $zero, $at, 0x4328 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101235 | `audioCompandS16` | `0x800A23EC` | `0x0002B631` | `special_0x31 $s6,$zero,$v0` | `tgeu        $zero, $v0, 728` |
| funcs_27.c:101261 | `audioCompandS16` | `0x800A2410` | `0x00003329` | `special_0x29 $a2,$zero,$zero` | `.word       0x00003329                   # INVALID     $zero, $zero, 0x3329 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101263 | `audioCompandS16` | `0x800A2414` | `0x00009929` | `special_0x29 $s3,$zero,$zero` | `.word       0x00009929                   # INVALID     $zero, $zero, -0x66D7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101265 | `audioCompandS16` | `0x800A2418` | `0x0000FF29` | `special_0x29 $ra,$zero,$zero` | `.word       0x0000FF29                   # INVALID     $zero, $zero, -0xD7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101267 | `audioCompandS16` | `0x800A241C` | `0x00016529` | `special_0x29 $t4,$zero,$at` | `.word       0x00016529                   # INVALID     $zero, $at, 0x6529 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101273 | `audioCompandS16` | `0x800A2428` | `0x00029730` | `special_0x30 $s2,$zero,$v0` | `tge         $zero, $v0, 604` |
| funcs_27.c:101275 | `audioCompandS16` | `0x800A242C` | `0x0002FD32` | `special_0x32 $ra,$zero,$v0` | `tlt         $zero, $v0, 1012` |
| funcs_27.c:101313 | `audioCompandS16` | `0x800A2468` | `0x0002D931` | `special_0x31 $k1,$zero,$v0` | `tgeu        $zero, $v0, 868` |
| funcs_27.c:101315 | `audioCompandS16` | `0x800A246C` | `0x00034933` | `special_0x33 $t1,$zero,$v1` | `tltu        $zero, $v1, 292` |
| funcs_27.c:101352 | `audioCompandS16` | `0x800A24A4` | `0x0002A630` | `special_0x30 $s4,$zero,$v0` | `tge         $zero, $v0, 664` |
| funcs_27.c:101354 | `audioCompandS16` | `0x800A24A8` | `0x00032232` | `special_0x32 $a0,$zero,$v1` | `tlt         $zero, $v1, 136` |
| funcs_27.c:101356 | `audioCompandS16` | `0x800A24AC` | `0x00039D34` | `special_0x34 $s3,$zero,$v1` | `teq         $zero, $v1, 628` |
| funcs_27.c:101393 | `audioCompandS16` | `0x800A24E4` | `0x0002EC31` | `special_0x31 $sp,$zero,$v0` | `tgeu        $zero, $v0, 944` |
| funcs_27.c:101395 | `audioCompandS16` | `0x800A24E8` | `0x00037433` | `special_0x33 $t6,$zero,$v1` | `tltu        $zero, $v1, 464` |
| funcs_27.c:101397 | `audioCompandS16` | `0x800A24EC` | `0x0003FC35` | `special_0x35 $ra,$zero,$v1` | `.word       0x0003FC35                   # INVALID     $zero, $v1, -0x3CB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101431 | `audioCompandS16` | `0x800A2520` | `0x0002A030` | `special_0x30 $s4,$zero,$v0` | `tge         $zero, $v0, 640` |
| funcs_27.c:101433 | `audioCompandS16` | `0x800A2524` | `0x00033532` | `special_0x32 $a2,$zero,$v1` | `tlt         $zero, $v1, 212` |
| funcs_27.c:101435 | `audioCompandS16` | `0x800A2528` | `0x0003CB34` | `special_0x34 $t9,$zero,$v1` | `teq         $zero, $v1, 812` |
| funcs_27.c:101437 | `audioCompandS16` | `0x800A252C` | `0x00046036` | `special_0x36 $t4,$zero,$a0` | `tne         $zero, $a0, 384` |
| funcs_27.c:101472 | `audioCompandS16` | `0x800A2560` | `0x0002E431` | `special_0x31 $gp,$zero,$v0` | `tgeu        $zero, $v0, 912` |
| funcs_27.c:101474 | `audioCompandS16` | `0x800A2564` | `0x00038833` | `special_0x33 $s1,$zero,$v1` | `tltu        $zero, $v1, 544` |
| funcs_27.c:101476 | `audioCompandS16` | `0x800A2568` | `0x00042D35` | `special_0x35 $a1,$zero,$a0` | `.word       0x00042D35                   # INVALID     $zero, $a0, 0x2D35 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101478 | `audioCompandS16` | `0x800A256C` | `0x0004D137` | `special_0x37 $k0,$zero,$a0` | `.word       0x0004D137                   # INVALID     $zero, $a0, -0x2EC9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101512 | `audioCompandS16` | `0x800A25A0` | `0x00032E32` | `special_0x32 $a1,$zero,$v1` | `tlt         $zero, $v1, 184` |
| funcs_27.c:101514 | `audioCompandS16` | `0x800A25A4` | `0x0003E334` | `special_0x34 $gp,$zero,$v1` | `teq         $zero, $v1, 908` |
| funcs_27.c:101516 | `audioCompandS16` | `0x800A25A8` | `0x00049836` | `special_0x36 $s3,$zero,$a0` | `tne         $zero, $a0, 608` |
| funcs_27.c:101544 | `audioCompandS16` | `0x800A25D0` | `0x00006330` | `special_0x30 $t4,$zero,$zero` | `tge         $zero, $zero, 396` |
| funcs_27.c:101546 | `audioCompandS16` | `0x800A25D4` | `0x00012A30` | `special_0x30 $a1,$zero,$at` | `tge         $zero, $at, 168` |
| funcs_27.c:101548 | `audioCompandS16` | `0x800A25D8` | `0x0001F130` | `special_0x30 $fp,$zero,$at` | `tge         $zero, $at, 964` |
| funcs_27.c:101550 | `audioCompandS16` | `0x800A25DC` | `0x0002B830` | `special_0x30 $s7,$zero,$v0` | `tge         $zero, $v0, 736` |
| funcs_27.c:101552 | `audioCompandS16` | `0x800A25E0` | `0x00037F33` | `special_0x33 $t7,$zero,$v1` | `tltu        $zero, $v1, 508` |
| funcs_27.c:101554 | `audioCompandS16` | `0x800A25E4` | `0x00044635` | `special_0x35 $t0,$zero,$a0` | `.word       0x00044635                   # INVALID     $zero, $a0, 0x4635 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101556 | `audioCompandS16` | `0x800A25E8` | `0x00050D37` | `special_0x37 $at,$zero,$a1` | `.word       0x00050D37                   # INVALID     $zero, $a1, 0xD37 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101558 | `audioCompandS16` | `0x800A25EC` | `0x0005D439` | `special_0x39 $k0,$zero,$a1` | `.word       0x0005D439                   # INVALID     $zero, $a1, -0x2BC7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101584 | `audioCompandS16` | `0x800A2610` | `0x00006D31` | `special_0x31 $t5,$zero,$zero` | `tgeu        $zero, $zero, 436` |
| funcs_27.c:101586 | `audioCompandS16` | `0x800A2614` | `0x00014831` | `special_0x31 $t1,$zero,$at` | `tgeu        $zero, $at, 288` |
| funcs_27.c:101588 | `audioCompandS16` | `0x800A2618` | `0x00022331` | `special_0x31 $a0,$zero,$v0` | `tgeu        $zero, $v0, 140` |
| funcs_27.c:101590 | `audioCompandS16` | `0x800A261C` | `0x0002FE31` | `special_0x31 $ra,$zero,$v0` | `tgeu        $zero, $v0, 1016` |
| funcs_27.c:101592 | `audioCompandS16` | `0x800A2620` | `0x0003D934` | `special_0x34 $k1,$zero,$v1` | `teq         $zero, $v1, 868` |
| funcs_27.c:101594 | `audioCompandS16` | `0x800A2624` | `0x0004B436` | `special_0x36 $s6,$zero,$a0` | `tne         $zero, $a0, 720` |
| funcs_27.c:101625 | `audioCompandS16` | `0x800A2650` | `0x00007832` | `special_0x32 $t7,$zero,$zero` | `tlt         $zero, $zero, 480` |
| funcs_27.c:101627 | `audioCompandS16` | `0x800A2654` | `0x00016832` | `special_0x32 $t5,$zero,$at` | `tlt         $zero, $at, 416` |
| funcs_27.c:101629 | `audioCompandS16` | `0x800A2658` | `0x00025932` | `special_0x32 $t3,$zero,$v0` | `tlt         $zero, $v0, 356` |
| funcs_27.c:101631 | `audioCompandS16` | `0x800A265C` | `0x00034932` | `special_0x32 $t1,$zero,$v1` | `tlt         $zero, $v1, 292` |
| funcs_27.c:101633 | `audioCompandS16` | `0x800A2660` | `0x00043B35` | `special_0x35 $a3,$zero,$a0` | `.word       0x00043B35                   # INVALID     $zero, $a0, 0x3B35 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101635 | `audioCompandS16` | `0x800A2664` | `0x00052B37` | `special_0x37 $a1,$zero,$a1` | `.word       0x00052B37                   # INVALID     $zero, $a1, 0x2B37 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101637 | `audioCompandS16` | `0x800A2668` | `0x00061C39` | `special_0x39 $v1,$zero,$a2` | `.word       0x00061C39                   # INVALID     $zero, $a2, 0x1C39 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101665 | `audioCompandS16` | `0x800A2690` | `0x00008433` | `special_0x33 $s0,$zero,$zero` | `tltu        $zero, $zero, 528` |
| funcs_27.c:101667 | `audioCompandS16` | `0x800A2694` | `0x00018D33` | `special_0x33 $s1,$zero,$at` | `tltu        $zero, $at, 564` |
| funcs_27.c:101669 | `audioCompandS16` | `0x800A2698` | `0x00029633` | `special_0x33 $s2,$zero,$v0` | `tltu        $zero, $v0, 600` |
| funcs_27.c:101671 | `audioCompandS16` | `0x800A269C` | `0x00039F33` | `special_0x33 $s3,$zero,$v1` | `tltu        $zero, $v1, 636` |
| funcs_27.c:101673 | `audioCompandS16` | `0x800A26A0` | `0x0004A836` | `special_0x36 $s5,$zero,$a0` | `tne         $zero, $a0, 672` |
| funcs_27.c:101706 | `audioCompandS16` | `0x800A26D0` | `0x00009134` | `special_0x34 $s2,$zero,$zero` | `teq         $zero, $zero, 580` |
| funcs_27.c:101708 | `audioCompandS16` | `0x800A26D4` | `0x0001B434` | `special_0x34 $s6,$zero,$at` | `teq         $zero, $at, 720` |
| funcs_27.c:101710 | `audioCompandS16` | `0x800A26D8` | `0x0002D834` | `special_0x34 $k1,$zero,$v0` | `teq         $zero, $v0, 864` |
| funcs_27.c:101712 | `audioCompandS16` | `0x800A26DC` | `0x0003FB34` | `special_0x34 $ra,$zero,$v1` | `teq         $zero, $v1, 1004` |
| funcs_27.c:101714 | `audioCompandS16` | `0x800A26E0` | `0x00051F37` | `special_0x37 $v1,$zero,$a1` | `.word       0x00051F37                   # INVALID     $zero, $a1, 0x1F37 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101716 | `audioCompandS16` | `0x800A26E4` | `0x00064239` | `special_0x39 $t0,$zero,$a2` | `.word       0x00064239                   # INVALID     $zero, $a2, 0x4239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101720 | `audioCompandS16` | `0x800A26EC` | `0x0008893D` | `special_0x3D $s1,$zero,$t0` | `.word       0x0008893D                   # INVALID     $zero, $t0, -0x76C3 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101746 | `audioCompandS16` | `0x800A2710` | `0x0000A035` | `special_0x35 $s4,$zero,$zero` | `.word       0x0000A035                   # INVALID     $zero, $zero, -0x5FCB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101748 | `audioCompandS16` | `0x800A2714` | `0x0001E035` | `special_0x35 $gp,$zero,$at` | `.word       0x0001E035                   # INVALID     $zero, $at, -0x1FCB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101750 | `audioCompandS16` | `0x800A2718` | `0x00032135` | `special_0x35 $a0,$zero,$v1` | `.word       0x00032135                   # INVALID     $zero, $v1, 0x2135 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101752 | `audioCompandS16` | `0x800A271C` | `0x00046135` | `special_0x35 $t4,$zero,$a0` | `.word       0x00046135                   # INVALID     $zero, $a0, 0x6135 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101786 | `audioCompandS16` | `0x800A2750` | `0x0000B036` | `special_0x36 $s6,$zero,$zero` | `tne         $zero, $zero, 704` |
| funcs_27.c:101788 | `audioCompandS16` | `0x800A2754` | `0x00021036` | `special_0x36 $v0,$zero,$v0` | `tne         $zero, $v0, 64` |
| funcs_27.c:101790 | `audioCompandS16` | `0x800A2758` | `0x00037136` | `special_0x36 $t6,$zero,$v1` | `tne         $zero, $v1, 452` |
| funcs_27.c:101792 | `audioCompandS16` | `0x800A275C` | `0x0004D136` | `special_0x36 $k0,$zero,$a0` | `tne         $zero, $a0, 836` |
| funcs_27.c:101794 | `audioCompandS16` | `0x800A2760` | `0x00063339` | `special_0x39 $a2,$zero,$a2` | `.word       0x00063339                   # INVALID     $zero, $a2, 0x3339 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101798 | `audioCompandS16` | `0x800A2768` | `0x0008F43D` | `special_0x3D $fp,$zero,$t0` | `.word       0x0008F43D                   # INVALID     $zero, $t0, -0xBC3 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101827 | `audioCompandS16` | `0x800A2790` | `0x0000C237` | `special_0x37 $t8,$zero,$zero` | `.word       0x0000C237                   # INVALID     $zero, $zero, -0x3DC9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101829 | `audioCompandS16` | `0x800A2794` | `0x00024637` | `special_0x37 $t0,$zero,$v0` | `.word       0x00024637                   # INVALID     $zero, $v0, 0x4637 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101831 | `audioCompandS16` | `0x800A2798` | `0x0003CA37` | `special_0x37 $t9,$zero,$v1` | `.word       0x0003CA37                   # INVALID     $zero, $v1, -0x35C9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101833 | `audioCompandS16` | `0x800A279C` | `0x00054E37` | `special_0x37 $t1,$zero,$a1` | `.word       0x00054E37                   # INVALID     $zero, $a1, 0x4E37 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101877 | `audioCompandS16` | `0x800A27E4` | `0x00092A3D` | `special_0x3D $a1,$zero,$t1` | `.word       0x00092A3D                   # INVALID     $zero, $t1, 0x2A3D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101881 | `audioCompandS16` | `0x800A27EC` | `0x000C7F41` | `special_0x01 $t7,$zero,$t4` | `.word       0x000C7F41                   # INVALID     $zero, $t4, 0x7F41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101907 | `audioCompandS16` | `0x800A2810` | `0x0000EA39` | `special_0x39 $sp,$zero,$zero` | `.word       0x0000EA39                   # INVALID     $zero, $zero, -0x15C7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101909 | `audioCompandS16` | `0x800A2814` | `0x0002BF39` | `special_0x39 $s7,$zero,$v0` | `.word       0x0002BF39                   # INVALID     $zero, $v0, -0x40C7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101911 | `audioCompandS16` | `0x800A2818` | `0x00049539` | `special_0x39 $s2,$zero,$a0` | `.word       0x00049539                   # INVALID     $zero, $a0, -0x6AC7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101913 | `audioCompandS16` | `0x800A281C` | `0x00066A39` | `special_0x39 $t5,$zero,$a2` | `.word       0x00066A39                   # INVALID     $zero, $a2, 0x6A39 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101956 | `audioCompandS16` | `0x800A2860` | `0x0009143D` | `special_0x3D $v0,$zero,$t1` | `.word       0x0009143D                   # INVALID     $zero, $t1, 0x143D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:101960 | `audioCompandS16` | `0x800A2868` | `0x000D1D41` | `special_0x01 $v1,$zero,$t5` | `.word       0x000D1D41                   # INVALID     $zero, $t5, 0x1D41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102038 | `audioCompandS16` | `0x800A28E4` | `0x000D6B41` | `special_0x01 $t5,$zero,$t5` | `.word       0x000D6B41                   # INVALID     $zero, $t5, 0x6B41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102042 | `audioCompandS16` | `0x800A28EC` | `0x00124C45` | `special_0x05 $t1,$zero,$s2` | `.word       0x00124C45                   # INVALID     $zero, $s2, 0x4C45 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102068 | `audioCompandS16` | `0x800A2910` | `0x0001573D` | `special_0x3D $t2,$zero,$at` | `.word       0x0001573D                   # INVALID     $zero, $at, 0x573D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102070 | `audioCompandS16` | `0x800A2914` | `0x0004063D` | `special_0x3D $zero,$zero,$a0` | `.word       0x0004063D                   # INVALID     $zero, $a0, 0x63D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102072 | `audioCompandS16` | `0x800A2918` | `0x0006B53D` | `special_0x3D $s6,$zero,$a2` | `.word       0x0006B53D                   # INVALID     $zero, $a2, -0x4AC3 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102074 | `audioCompandS16` | `0x800A291C` | `0x0009643D` | `special_0x3D $t4,$zero,$t1` | `.word       0x0009643D                   # INVALID     $zero, $t1, 0x643D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102117 | `audioCompandS16` | `0x800A2960` | `0x000D4A41` | `special_0x01 $t1,$zero,$t5` | `.word       0x000D4A41                   # INVALID     $zero, $t5, 0x4A41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102121 | `audioCompandS16` | `0x800A2968` | `0x00133245` | `special_0x05 $a2,$zero,$s3` | `.word       0x00133245                   # INVALID     $zero, $s3, 0x3245 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102205 | `audioCompandS16` | `0x800A29E4` | `0x0013A845` | `special_0x05 $s5,$zero,$s3` | `.word       0x0013A845                   # INVALID     $zero, $s3, -0x57BB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102209 | `audioCompandS16` | `0x800A29EC` | `0x001ACE49` | `jalr $t9,$zero,$k0` | `.word       0x001ACE49                   # jalr        $t9, $zero # 001A0640 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102236 | `audioCompandS16` | `0x800A2A10` | `0x0001F741` | `special_0x01 $fp,$zero,$at` | `.word       0x0001F741                   # INVALID     $zero, $at, -0x8BF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102238 | `audioCompandS16` | `0x800A2A14` | `0x0005E541` | `special_0x01 $gp,$zero,$a1` | `.word       0x0005E541                   # INVALID     $zero, $a1, -0x1ABF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102240 | `audioCompandS16` | `0x800A2A18` | `0x0009D441` | `special_0x01 $k0,$zero,$t1` | `.word       0x0009D441                   # INVALID     $zero, $t1, -0x2BBF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102242 | `audioCompandS16` | `0x800A2A1C` | `0x000DC241` | `special_0x01 $t8,$zero,$t5` | `.word       0x000DC241                   # INVALID     $zero, $t5, -0x3DBF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102249 | `audioCompandS16` | `0x800A2A2C` | `0x001D7C4A` | `movz $t7,$zero,$sp` | `.word       0x001D7C4A                   # movz        $t7, $zero, $sp # 00000440 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102253 | `audioCompandS16` | `0x800A2A2C` | `0x001D7C4A` | `movz $t7,$zero,$sp` | `.word       0x001D7C4A                   # movz        $t7, $zero, $sp # 00000440 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102289 | `audioCompandS16` | `0x800A2A60` | `0x00137545` | `special_0x05 $t6,$zero,$s3` | `.word       0x00137545                   # INVALID     $zero, $s3, 0x7545 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102293 | `audioCompandS16` | `0x800A2A68` | `0x001C1B49` | `jalr $v1,$zero,$gp` | `.word       0x001C1B49                   # jalr        $v1, $zero # 001C0340 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102295 | `audioCompandS16` | `0x800A2A6C` | `0x00206E4B` | `movn $t5,$at,$zero` | `.word       0x00206E4B                   # movn        $t5, $at, $zero # 00000640 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102333 | `audioCompandS16` | `0x800A2AA8` | `0x001EEA4A` | `movz $sp,$zero,$fp` | `.word       0x001EEA4A                   # movz        $sp, $zero, $fp # 00000240 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102337 | `audioCompandS16` | `0x800A2AA8` | `0x001EEA4A` | `movz $sp,$zero,$fp` | `.word       0x001EEA4A                   # movz        $sp, $zero, $fp # 00000240 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102376 | `audioCompandS16` | `0x800A2AE4` | `0x001CC649` | `jalr $t8,$zero,$gp` | `.word       0x001CC649                   # jalr        $t8, $zero # 001C0640 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102378 | `audioCompandS16` | `0x800A2AE8` | `0x0022024B` | `movn $zero,$at,$v0` | `.word       0x0022024B                   # movn        $zero, $at, $v0 # 00000240 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102380 | `audioCompandS16` | `0x800A2AEC` | `0x00273D4D` | `break $a3,$at,$a3` | `break       39, 245` |
| funcs_27.c:102406 | `audioCompandS16` | `0x800A2B10` | `0x0002E045` | `special_0x05 $gp,$zero,$v0` | `.word       0x0002E045                   # INVALID     $zero, $v0, -0x1FBB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102408 | `audioCompandS16` | `0x800A2B14` | `0x0008A145` | `special_0x05 $s4,$zero,$t0` | `.word       0x0008A145                   # INVALID     $zero, $t0, -0x5EBB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102410 | `audioCompandS16` | `0x800A2B18` | `0x000E6345` | `special_0x05 $t4,$zero,$t6` | `.word       0x000E6345                   # INVALID     $zero, $t6, 0x6345 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102412 | `audioCompandS16` | `0x800A2B1C` | `0x00142445` | `special_0x05 $a0,$zero,$s4` | `.word       0x00142445                   # INVALID     $zero, $s4, 0x2445 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102415 | `audioCompandS16` | `0x800A2B24` | `0x001FA74A` | `movz $s4,$zero,$ra` | `.word       0x001FA74A                   # movz        $s4, $zero, $ra # 00000740 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102419 | `audioCompandS16` | `0x800A2B24` | `0x001FA74A` | `movz $s4,$zero,$ra` | `.word       0x001FA74A                   # movz        $s4, $zero, $ra # 00000740 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102424 | `audioCompandS16` | `0x800A2B2C` | `0x002B2A4E` | `special_0x0E $a1,$at,$t3` | `.word       0x002B2A4E                   # INVALID     $at, $t3, 0x2A4E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102459 | `audioCompandS16` | `0x800A2B60` | `0x001C7E49` | `jalr $t7,$zero,$gp` | `.word       0x001C7E49                   # jalr        $t7, $zero # 001C0640 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102461 | `audioCompandS16` | `0x800A2B64` | `0x0022D34B` | `movn $k0,$at,$v0` | `.word       0x0022D34B                   # movn        $k0, $at, $v0 # 00000340 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102463 | `audioCompandS16` | `0x800A2B68` | `0x0029284D` | `break $a1,$at,$t1` | `break       41, 161` |
| funcs_27.c:102465 | `audioCompandS16` | `0x800A2B6C` | `0x002F7D4F` | `special_0x0F $t7,$at,$t7` | `.word       0x002F7D4F                   # sync # 002F7D40 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102499 | `audioCompandS16` | `0x800A2BA0` | `0x001F574A` | `movz $t2,$zero,$ra` | `.word       0x001F574A                   # movz        $t2, $zero, $ra # 00000740 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102504 | `audioCompandS16` | `0x800A2BA8` | `0x002D454E` | `special_0x0E $t0,$at,$t5` | `.word       0x002D454E                   # INVALID     $at, $t5, 0x454E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102536 | `audioCompandS16` | `0x800A2BE0` | `0x0022794B` | `movn $t7,$at,$v0` | `.word       0x0022794B                   # movn        $t7, $at, $v0 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102549 | `audioCompandS16` | `0x800A2BE0` | `0x0022794B` | `movn $t7,$at,$v0` | `.word       0x0022794B                   # movn        $t7, $at, $v0 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102559 | `audioCompandS16` | `0x800A2BE0` | `0x0022794B` | `movn $t7,$at,$v0` | `.word       0x0022794B                   # movn        $t7, $at, $v0 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102566 | `audioCompandS16` | `0x800A2BE0` | `0x0022794B` | `movn $t7,$at,$v0` | `.word       0x0022794B                   # movn        $t7, $at, $v0 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102571 | `audioCompandS16` | `0x800A2BE0` | `0x0022794B` | `movn $t7,$at,$v0` | `.word       0x0022794B                   # movn        $t7, $at, $v0 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102574 | `audioCompandS16` | `0x800A2BE4` | `0x002A224D` | `break $a0,$at,$t2` | `break       42, 137` |
| funcs_27.c:102576 | `audioCompandS16` | `0x800A2BE8` | `0x0031CB4F` | `special_0x0F $t9,$at,$s1` | `.word       0x0031CB4F                   # sync # 0031CB40 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102604 | `audioCompandS16` | `0x800A2C10` | `0x00043649` | `jalr $a2,$zero,$a0` | `.word       0x00043649                   # jalr        $a2, $zero # 00040640 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102606 | `audioCompandS16` | `0x800A2C14` | `0x000CA349` | `jalr $s4,$zero,$t4` | `.word       0x000CA349                   # jalr        $s4, $zero # 000C0340 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102608 | `audioCompandS16` | `0x800A2C18` | `0x00151149` | `jalr $v0,$zero,$s5` | `.word       0x00151149                   # jalr        $v0, $zero # 00150140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102610 | `audioCompandS16` | `0x800A2C1C` | `0x001D7E49` | `jalr $t7,$zero,$sp` | `.word       0x001D7E49                   # jalr        $t7, $zero # 001D0640 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102615 | `audioCompandS16` | `0x800A2C24` | `0x002E594E` | `special_0x0E $t3,$at,$t6` | `.word       0x002E594E                   # INVALID     $at, $t6, 0x594E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102645 | `audioCompandS16` | `0x800A2C50` | `0x0004A24A` | `movz $s4,$zero,$a0` | `.word       0x0004A24A                   # movz        $s4, $zero, $a0 # 00000240 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102647 | `audioCompandS16` | `0x800A2C54` | `0x000DE74A` | `movz $gp,$zero,$t5` | `.word       0x000DE74A                   # movz        $gp, $zero, $t5 # 00000740 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102649 | `audioCompandS16` | `0x800A2C58` | `0x00172C4A` | `movz $a1,$zero,$s7` | `.word       0x00172C4A                   # movz        $a1, $zero, $s7 # 00000440 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102651 | `audioCompandS16` | `0x800A2C5C` | `0x0020714A` | `movz $t6,$at,$zero` | `.word       0x0020714A                   # movz        $t6, $at, $zero # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102653 | `audioCompandS16` | `0x800A2C60` | `0x0029B74D` | `break $s6,$at,$t1` | `break       41, 733` |
| funcs_27.c:102656 | `audioCompandS16` | `0x800A2C64` | `0x0032FC4F` | `special_0x0F $ra,$at,$s2` | `.word       0x0032FC4F                   # sync # 0032FC40 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102687 | `audioCompandS16` | `0x800A2C90` | `0x0005194B` | `movn $v1,$zero,$a1` | `.word       0x0005194B                   # movn        $v1, $zero, $a1 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102689 | `audioCompandS16` | `0x800A2C94` | `0x000F4B4B` | `movn $t1,$zero,$t7` | `.word       0x000F4B4B                   # movn        $t1, $zero, $t7 # 00000340 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102691 | `audioCompandS16` | `0x800A2C98` | `0x00197E4B` | `movn $t7,$zero,$t9` | `.word       0x00197E4B                   # movn        $t7, $zero, $t9 # 00000640 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102693 | `audioCompandS16` | `0x800A2C9C` | `0x0023B04B` | `movn $s6,$at,$v1` | `.word       0x0023B04B                   # movn        $s6, $at, $v1 # 00000040 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102695 | `audioCompandS16` | `0x800A2CA0` | `0x002DE34E` | `special_0x0E $gp,$at,$t5` | `.word       0x002DE34E                   # INVALID     $at, $t5, -0x1CB2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102740 | `audioCompandS16` | `0x800A2CE0` | `0x00327A4F` | `special_0x0F $t7,$at,$s2` | `.word       0x00327A4F                   # sync # 00327A40 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102746 | `audioCompandS16` | `0x800A2CEC` | `0x00542055` | `special_0x15 $a0,$v0,$s4` | `.word       0x00542055                   # INVALID     $v0, $s4, 0x2055 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102772 | `audioCompandS16` | `0x800A2D10` | `0x00062B4D` | `break $a1,$zero,$a2` | `break       6, 173` |
| funcs_27.c:102774 | `audioCompandS16` | `0x800A2D14` | `0x0012814D` | `break $s0,$zero,$s2` | `break       18, 517` |
| funcs_27.c:102776 | `audioCompandS16` | `0x800A2D18` | `0x001ED84D` | `break $k1,$zero,$fp` | `break       30, 865` |
| funcs_27.c:102778 | `audioCompandS16` | `0x800A2D1C` | `0x002B2E4D` | `break $a1,$at,$t3` | `break       43, 185` |
| funcs_27.c:102813 | `audioCompandS16` | `0x800A2D50` | `0x0006C94E` | `special_0x0E $t9,$zero,$a2` | `.word       0x0006C94E                   # INVALID     $zero, $a2, -0x36B2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102815 | `audioCompandS16` | `0x800A2D54` | `0x00145B4E` | `special_0x0E $t3,$zero,$s4` | `.word       0x00145B4E                   # INVALID     $zero, $s4, 0x5B4E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102817 | `audioCompandS16` | `0x800A2D58` | `0x0021EE4E` | `special_0x0E $sp,$at,$at` | `.word       0x0021EE4E                   # INVALID     $at, $at, -0x11B2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102819 | `audioCompandS16` | `0x800A2D5C` | `0x002F804E` | `special_0x0E $s0,$at,$t7` | `.word       0x002F804E                   # INVALID     $at, $t7, -0x7FB2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102825 | `audioCompandS16` | `0x800A2D68` | `0x00583955` | `special_0x15 $a3,$v0,$t8` | `.word       0x00583955                   # INVALID     $v0, $t8, 0x3955 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102853 | `audioCompandS16` | `0x800A2D90` | `0x0007774F` | `special_0x0F $t6,$zero,$a3` | `.word       0x0007774F                   # sync # 00077740 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102855 | `audioCompandS16` | `0x800A2D94` | `0x0016654F` | `special_0x0F $t4,$zero,$s6` | `.word       0x0016654F                   # sync # 00166540 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102857 | `audioCompandS16` | `0x800A2D98` | `0x0025534F` | `special_0x0F $t2,$at,$a1` | `.word       0x0025534F                   # sync # 00255340 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102859 | `audioCompandS16` | `0x800A2D9C` | `0x0034414F` | `special_0x0F $t0,$at,$s4` | `.word       0x0034414F                   # sync # 00344140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102903 | `audioCompandS16` | `0x800A2DE4` | `0x005A5455` | `special_0x15 $t2,$v0,$k0` | `.word       0x005A5455                   # INVALID     $v0, $k0, 0x5455 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:102984 | `audioCompandS16` | `0x800A2E60` | `0x00596D55` | `special_0x15 $t5,$v0,$t9` | `.word       0x00596D55                   # INVALID     $v0, $t9, 0x6D55 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103097 | `audioCompandS16` | `0x800A2F10` | `0x000D3955` | `special_0x15 $a3,$zero,$t5` | `.word       0x000D3955                   # INVALID     $zero, $t5, 0x3955 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103099 | `audioCompandS16` | `0x800A2F14` | `0x0027AC55` | `special_0x15 $s5,$at,$a3` | `.word       0x0027AC55                   # INVALID     $at, $a3, -0x53AB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103101 | `audioCompandS16` | `0x800A2F18` | `0x00422055` | `special_0x15 $a0,$v0,$v0` | `.word       0x00422055                   # INVALID     $v0, $v0, 0x2055 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103103 | `audioCompandS16` | `0x800A2F1C` | `0x005C9355` | `special_0x15 $s2,$v0,$gp` | `.word       0x005C9355                   # INVALID     $v0, $gp, -0x6CAB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103230 | `audioCompandS16` | `0x800A2FE4` | `0x00155B81` | `special_0x01 $t3,$zero,$s5` | `.word       0x00155B81                   # INVALID     $zero, $s5, 0x5B81 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103244 | `audioCompandS16` | `0x800A3000` | `0x00200001` | `special_0x01 $zero,$at,$zero` | `.word       0x00200001                   # INVALID     $at, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103248 | `audioCompandS16` | `0x800A3008` | `0x0023EB36` | `special_0x36 $sp,$at,$v1` | `tne         $at, $v1, 940` |
| funcs_27.c:103250 | `audioCompandS16` | `0x800A300C` | `0x00260DFD` | `special_0x3D $at,$at,$a2` | `.word       0x00260DFD                   # INVALID     $at, $a2, 0xDFD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103262 | `audioCompandS16` | `0x800A3024` | `0x0035D141` | `special_0x01 $k0,$at,$s5` | `.word       0x0035D141                   # INVALID     $at, $s5, -0x2EBF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103266 | `audioCompandS16` | `0x800A302C` | `0x003C6871` | `special_0x31 $t5,$at,$gp` | `tgeu        $at, $gp, 417` |
| funcs_27.c:103276 | `audioCompandS16` | `0x800A3040` | `0x0050A28E` | `special_0x0E $s4,$v0,$s0` | `.word       0x0050A28E                   # INVALID     $v0, $s0, -0x5D72 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103294 | `audioCompandS16` | `0x800A3064` | `0x00879C81` | `special_0x01 $s3,$a0,$a3` | `.word       0x00879C81                   # INVALID     $a0, $a3, -0x637F # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103298 | `audioCompandS16` | `0x800A306C` | `0x009837F5` | `special_0x35 $a2,$a0,$t8` | `.word       0x009837F5                   # INVALID     $a0, $t8, 0x37F5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103302 | `audioCompandS16` | `0x800A3074` | `0x00AADC0E` | `special_0x0E $k1,$a1,$t2` | `.word       0x00AADC0E                   # INVALID     $a1, $t2, -0x23F2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103304 | `audioCompandS16` | `0x800A3078` | `0x00B504F9` | `special_0x39 $zero,$a1,$s5` | `.word       0x00B504F9                   # INVALID     $a1, $s5, 0x4F9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103307 | `audioCompandS16` | `0x800A307C` | `0x00BFC88D` | `break $t9,$a1,$ra` | `break       191, 802` |
| funcs_27.c:103324 | `audioCompandS16` | `0x800A3098` | `0x011F59B6` | `special_0x36 $t3,$t0,$ra` | `tne         $t0, $ra, 358` |
| funcs_27.c:103332 | `audioCompandS16` | `0x800A30A8` | `0x016A09F2` | `special_0x32 $at,$t3,$t2` | `tlt         $t3, $t2, 39` |
| funcs_27.c:103339 | `audioCompandS16` | `0x800A30B8` | `0x01C823F0` | `special_0x30 $a0,$t6,$t0` | `tge         $t6, $t0, 143` |
| funcs_27.c:103343 | `audioCompandS16` | `0x800A30B8` | `0x01C823F0` | `special_0x30 $a0,$t6,$t0` | `tge         $t6, $t0, 143` |
| funcs_27.c:103345 | `audioCompandS16` | `0x800A30BC` | `0x01E3438E` | `special_0x0E $t0,$t7,$v1` | `.word       0x01E3438E                   # INVALID     $t7, $v1, 0x438E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:103355 | `audioCompandS16` | `0x800A30D0` | `0x02851474` | `special_0x34 $v0,$s4,$a1` | `teq         $s4, $a1, 81` |
| funcs_27.c:103361 | `audioCompandS16` | `0x800A30DC` | `0x02FF2234` | `special_0x34 $a0,$s7,$ra` | `teq         $s7, $ra, 136` |
| funcs_27.c:103363 | `audioCompandS16` | `0x800A30E0` | `0x032CBFF0` | `special_0x30 $s7,$t9,$t4` | `tge         $t9, $t4, 767` |
| funcs_27.c:103373 | `audioCompandS16` | `0x800A30F4` | `0x043CE408` | `regimm` | `.word       0x043CE408                   # INVALID     $at, $gp, -0x1BF8 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:103377 | `audioCompandS16` | `0x800A30F4` | `0x043CE408` | `regimm` | `.word       0x043CE408                   # INVALID     $at, $gp, -0x1BF8 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:103379 | `audioCompandS16` | `0x800A30F8` | `0x047D66D8` | `regimm` | `.word       0x047D66D8                   # INVALID     $v1, $sp, 0x66D8 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:103383 | `audioCompandS16` | `0x800A3100` | `0x050A28E8` | `regimm` | `tlti        $t0, 0x28E8` |
| funcs_27.c:103387 | `audioCompandS16` | `0x800A3100` | `0x050A28E8` | `regimm` | `tlti        $t0, 0x28E8` |
| funcs_27.c:103390 | `audioCompandS16` | `0x800A3104` | `0x0556E070` | `regimm` | `.word       0x0556E070                   # INVALID     $t2, $s6, -0x1F90 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:103392 | `audioCompandS16` | `0x800A3108` | `0x05A827C8` | `regimm` | `tgei        $t5, 0x27C8` |
| funcs_27.c:103395 | `audioCompandS16` | `0x800A310C` | `0x05FE4468` | `regimm` | `.word       0x05FE4468                   # INVALID     $t7, $fp, 0x4468 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:103397 | `audioCompandS16` | `0x800A3110` | `0x06597FE0` | `regimm` | `.word       0x06597FE0                   # INVALID     $s2, $t9, 0x7FE0 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:103399 | `audioCompandS16` | `0x800A3114` | `0x06BA2820` | `regimm` | `.word       0x06BA2820                   # INVALID     $s5, $k0, 0x2820 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:103403 | `audioCompandS16` | `0x800A311C` | `0x078D0E38` | `regimm` | `.word       0x078D0E38                   # INVALID     $gp, $t5, 0xE38 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:103407 | `audioCompandS16` | `0x800A311C` | `0x078D0E38` | `regimm` | `.word       0x078D0E38                   # INVALID     $gp, $t5, 0xE38 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:103409 | `audioCompandS16` | `0x800A3120` | `0x08000040` | `j` | `j           L_80000100` |
| funcs_27.c:103411 | `audioCompandS16` | `0x800A3124` | `0x0879C810` | `j` | `j           L_81E72040` |
| funcs_27.c:103413 | `audioCompandS16` | `0x800A3128` | `0x08FACDB0` | `j` | `j           L_83EB36C0` |
| funcs_27.c:103415 | `audioCompandS16` | `0x800A312C` | `0x09837F50` | `j` | `j           L_860DFD40` |
| funcs_27.c:103417 | `audioCompandS16` | `0x800A3130` | `0x0A1451D0` | `j` | `j           L_88514740` |
| funcs_27.c:103419 | `audioCompandS16` | `0x800A3134` | `0x0AADC0E0` | `j` | `j           L_8AB70380` |
| funcs_27.c:103421 | `audioCompandS16` | `0x800A3138` | `0x0B504F90` | `j` | `j           L_8D413E40` |
| funcs_27.c:103423 | `audioCompandS16` | `0x800A313C` | `0x0BFC88D0` | `j` | `j           L_8FF22340` |
| funcs_27.c:104011 | `audioCompandS16` | `0x800A31B0` | `0x40000200` | `cop0` | `.word       0x40000200                   # mfc0        $zero, Index # 00000200 <InstrIdType: CPU_COP0>` |
| funcs_27.c:104013 | `audioCompandS16` | `0x800A31B4` | `0x43CE4080` | `cop0` | `.word       0x43CE4080                   # INVALID     $fp, $t6, 0x4080 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:104015 | `audioCompandS16` | `0x800A31B8` | `0x47D66D80` | `cop1` | `.word       0x47D66D80                   # INVALID     $fp, $s6, 0x6D80 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_27.c:104017 | `audioCompandS16` | `0x800A31BC` | `0x4C1BFA80` | `opcode_0x13` | `.word       0x4C1BFA80                   # INVALID     $zero, $k1, -0x580 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:104086 | `audioCompandS16` | `0x800A31E8` | `0x000B504F` | `special_0x0F $t2,$zero,$t3` | `.word       0x000B504F                   # sync # 000B5040 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104090 | `audioCompandS16` | `0x800A31E8` | `0x000B504F` | `special_0x0F $t2,$zero,$t3` | `.word       0x000B504F                   # sync # 000B5040 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104098 | `audioCompandS16` | `0x800A31F8` | `0x0008FACD` | `break $ra,$zero,$t0` | `break       8, 1003` |
| funcs_27.c:104108 | `audioCompandS16` | `0x800A3204` | `0x00078D0E` | `special_0x0E $s1,$zero,$a3` | `.word       0x00078D0E                   # INVALID     $zero, $a3, -0x72F2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104110 | `audioCompandS16` | `0x800A3208` | `0x0007208F` | `special_0x0F $a0,$zero,$a3` | `.word       0x0007208F                   # sync # 00072080 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104112 | `audioCompandS16` | `0x800A320C` | `0x0006BA28` | `special_0x28 $s7,$zero,$a2` | `.word       0x0006BA28                   # INVALID     $zero, $a2, -0x45D8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104122 | `audioCompandS16` | `0x800A3220` | `0x00050A29` | `special_0x29 $at,$zero,$a1` | `.word       0x00050A29                   # INVALID     $zero, $a1, 0xA29 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104149 | `audioCompandS16` | `0x800A324C` | `0x0002AB70` | `special_0x30 $s5,$zero,$v0` | `tge         $zero, $v0, 685` |
| funcs_27.c:104155 | `audioCompandS16` | `0x800A3258` | `0x00023EB3` | `special_0x33 $a3,$zero,$v0` | `tltu        $zero, $v0, 250` |
| funcs_27.c:104157 | `audioCompandS16` | `0x800A325C` | `0x00021E72` | `special_0x32 $v1,$zero,$v0` | `tlt         $zero, $v0, 121` |
| funcs_27.c:104165 | `audioCompandS16` | `0x800A326C` | `0x0001AE8A` | `movz $s5,$zero,$at` | `.word       0x0001AE8A                   # movz        $s5, $zero, $at # 00000680 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104171 | `audioCompandS16` | `0x800A3278` | `0x00016A0A` | `movz $t5,$zero,$at` | `.word       0x00016A0A                   # movz        $t5, $zero, $at # 00000200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104175 | `audioCompandS16` | `0x800A3280` | `0x0001428A` | `movz $t0,$zero,$at` | `.word       0x0001428A                   # movz        $t0, $zero, $at # 00000280 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104177 | `audioCompandS16` | `0x800A3284` | `0x00013070` | `special_0x30 $a2,$zero,$at` | `tge         $zero, $at, 193` |
| funcs_27.c:104181 | `audioCompandS16` | `0x800A328C` | `0x00010F39` | `special_0x39 $at,$zero,$at` | `.word       0x00010F39                   # INVALID     $zero, $at, 0xF39 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104189 | `audioCompandS16` | `0x800A329C` | `0x0000D745` | `special_0x05 $k0,$zero,$zero` | `.word       0x0000D745                   # INVALID     $zero, $zero, -0x28BB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104191 | `audioCompandS16` | `0x800A32A0` | `0x0000CB30` | `special_0x30 $t9,$zero,$zero` | `tge         $zero, $zero, 812` |
| funcs_27.c:104193 | `audioCompandS16` | `0x800A32A4` | `0x0000BFC9` | `jalr $s7,$zero,$zero` | `.word       0x0000BFC9                   # jalr        $s7, $zero # 000007C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104195 | `audioCompandS16` | `0x800A32A8` | `0x0000B505` | `special_0x05 $s6,$zero,$zero` | `.word       0x0000B505                   # INVALID     $zero, $zero, -0x4AFB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104199 | `audioCompandS16` | `0x800A32B0` | `0x0000A145` | `special_0x05 $s4,$zero,$zero` | `.word       0x0000A145                   # INVALID     $zero, $zero, -0x5EBB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104211 | `audioCompandS16` | `0x800A32C8` | `0x00007209` | `jalr $t6,$zero,$zero` | `.word       0x00007209                   # jalr        $t6, $zero # 00000200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104229 | `audioCompandS16` | `0x800A32EC` | `0x000043CE` | `special_0x0E $t0,$zero,$zero` | `.word       0x000043CE                   # INVALID     $zero, $zero, 0x43CE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104233 | `audioCompandS16` | `0x800A32F4` | `0x00003C68` | `special_0x28 $a3,$zero,$zero` | `.word       0x00003C68                   # INVALID     $zero, $zero, 0x3C68 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104242 | `audioCompandS16` | `0x800A3304` | `0x00002FF2` | `special_0x32 $a1,$zero,$zero` | `tlt         $zero, $zero, 191` |
| funcs_27.c:104244 | `audioCompandS16` | `0x800A3308` | `0x00002D41` | `special_0x01 $a1,$zero,$zero` | `.word       0x00002D41                   # INVALID     $zero, $zero, 0x2D41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104246 | `audioCompandS16` | `0x800A330C` | `0x00002AB7` | `special_0x37 $a1,$zero,$zero` | `.word       0x00002AB7                   # INVALID     $zero, $zero, 0x2AB7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104250 | `audioCompandS16` | `0x800A3314` | `0x0000260E` | `special_0x0E $a0,$zero,$zero` | `.word       0x0000260E                   # INVALID     $zero, $zero, 0x260E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104258 | `audioCompandS16` | `0x800A3324` | `0x00001E34` | `special_0x34 $v1,$zero,$zero` | `teq         $zero, $zero, 120` |
| funcs_27.c:104262 | `audioCompandS16` | `0x800A332C` | `0x00001AE9` | `special_0x29 $v1,$zero,$zero` | `.word       0x00001AE9                   # INVALID     $zero, $zero, 0x1AE9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104266 | `audioCompandS16` | `0x800A3334` | `0x000017F9` | `special_0x39 $v0,$zero,$zero` | `.word       0x000017F9                   # INVALID     $zero, $zero, 0x17F9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104272 | `audioCompandS16` | `0x800A3340` | `0x00001429` | `special_0x29 $v0,$zero,$zero` | `.word       0x00001429                   # INVALID     $zero, $zero, 0x1429 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104276 | `audioCompandS16` | `0x800A3348` | `0x000011F6` | `special_0x36 $v0,$zero,$zero` | `tne         $zero, $zero, 71` |
| funcs_27.c:104278 | `audioCompandS16` | `0x800A334C` | `0x000010F4` | `special_0x34 $v0,$zero,$zero` | `teq         $zero, $zero, 67` |
| funcs_27.c:104285 | `audioCompandS16` | `0x800A3358` | `0x00000E41` | `special_0x01 $at,$zero,$zero` | `.word       0x00000E41                   # INVALID     $zero, $zero, 0xE41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104287 | `audioCompandS16` | `0x800A335C` | `0x00000D74` | `special_0x34 $at,$zero,$zero` | `teq         $zero, $zero, 53` |
| funcs_27.c:104289 | `audioCompandS16` | `0x800A3360` | `0x00000CB3` | `special_0x33 $at,$zero,$zero` | `tltu        $zero, $zero, 50` |
| funcs_27.c:104291 | `audioCompandS16` | `0x800A3364` | `0x00000BFD` | `special_0x3D $at,$zero,$zero` | `.word       0x00000BFD                   # INVALID     $zero, $zero, 0xBFD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104307 | `audioCompandS16` | `0x800A3384` | `0x0000078D` | `break $zero,$zero,$zero` | `break       0, 30` |
| funcs_27.c:104317 | `audioCompandS16` | `0x800A3398` | `0x000005A8` | `special_0x28 $zero,$zero,$zero` | `.word       0x000005A8                   # INVALID     $zero, $zero, 0x5A8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104321 | `audioCompandS16` | `0x800A33A0` | `0x0000050A` | `movz $zero,$zero,$zero` | `.word       0x0000050A                   # movz        $zero, $zero, $zero # 00000500 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104325 | `audioCompandS16` | `0x800A33A8` | `0x0000047D` | `special_0x3D $zero,$zero,$zero` | `.word       0x0000047D                   # INVALID     $zero, $zero, 0x47D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104327 | `audioCompandS16` | `0x800A33AC` | `0x0000043D` | `special_0x3D $zero,$zero,$zero` | `.word       0x0000043D                   # INVALID     $zero, $zero, 0x43D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104347 | `audioCompandS16` | `0x800A33D4` | `0x001003B3` | `special_0x33 $zero,$zero,$s0` | `tltu        $zero, $s0, 14` |
| funcs_27.c:104359 | `audioCompandS16` | `0x800A33EC` | `0x001019F6` | `special_0x36 $v1,$zero,$s0` | `tne         $zero, $s0, 103` |
| funcs_27.c:104363 | `audioCompandS16` | `0x800A33F4` | `0x00102168` | `special_0x28 $a0,$zero,$s0` | `.word       0x00102168                   # INVALID     $zero, $s0, 0x2168 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104373 | `audioCompandS16` | `0x800A3408` | `0x00103415` | `special_0x15 $a2,$zero,$s0` | `.word       0x00103415                   # INVALID     $zero, $s0, 0x3415 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104379 | `audioCompandS16` | `0x800A3414` | `0x00103F55` | `special_0x15 $a3,$zero,$s0` | `.word       0x00103F55                   # INVALID     $zero, $s0, 0x3F55 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104393 | `audioCompandS16` | `0x800A3430` | `0x001059B1` | `special_0x31 $t3,$zero,$s0` | `tgeu        $zero, $s0, 358` |
| funcs_27.c:104397 | `audioCompandS16` | `0x800A3438` | `0x00106141` | `special_0x01 $t4,$zero,$s0` | `.word       0x00106141                   # INVALID     $zero, $s0, 0x6141 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104399 | `audioCompandS16` | `0x800A343C` | `0x0010650A` | `movz $t4,$zero,$s0` | `.word       0x0010650A                   # movz        $t4, $zero, $s0 # 00000500 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104409 | `audioCompandS16` | `0x800A3450` | `0x00107805` | `special_0x05 $t7,$zero,$s0` | `.word       0x00107805                   # INVALID     $zero, $s0, 0x7805 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104415 | `audioCompandS16` | `0x800A345C` | `0x00108373` | `special_0x33 $s0,$zero,$s0` | `tltu        $zero, $s0, 525` |
| funcs_27.c:104417 | `audioCompandS16` | `0x800A3460` | `0x00108745` | `special_0x05 $s0,$zero,$s0` | `.word       0x00108745                   # INVALID     $zero, $s0, -0x78BB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104427 | `audioCompandS16` | `0x800A3474` | `0x00109A68` | `special_0x28 $s3,$zero,$s0` | `.word       0x00109A68                   # INVALID     $zero, $s0, -0x6598 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104443 | `audioCompandS16` | `0x800A3494` | `0x0010B935` | `special_0x35 $s7,$zero,$s0` | `.word       0x0010B935                   # INVALID     $zero, $s0, -0x46CB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104447 | `audioCompandS16` | `0x800A349C` | `0x0010C0F1` | `special_0x31 $t8,$zero,$s0` | `tgeu        $zero, $s0, 771` |
| funcs_27.c:104451 | `audioCompandS16` | `0x800A34A4` | `0x0010C8B1` | `special_0x31 $t9,$zero,$s0` | `tgeu        $zero, $s0, 802` |
| funcs_27.c:104455 | `audioCompandS16` | `0x800A34AC` | `0x0010D074` | `special_0x34 $k0,$zero,$s0` | `teq         $zero, $s0, 833` |
| funcs_27.c:104463 | `audioCompandS16` | `0x800A34BC` | `0x0010E005` | `special_0x05 $gp,$zero,$s0` | `.word       0x0010E005                   # INVALID     $zero, $s0, -0x1FFB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104473 | `audioCompandS16` | `0x800A34D0` | `0x0010F38F` | `special_0x0F $fp,$zero,$s0` | `.word       0x0010F38F                   # sync # 0010F380 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104481 | `audioCompandS16` | `0x800A34E0` | `0x00110341` | `special_0x01 $zero,$zero,$s1` | `.word       0x00110341                   # INVALID     $zero, $s1, 0x341 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104483 | `audioCompandS16` | `0x800A34E4` | `0x00110730` | `special_0x30 $zero,$zero,$s1` | `tge         $zero, $s1, 28` |
| funcs_27.c:104489 | `audioCompandS16` | `0x800A34F0` | `0x00111301` | `special_0x01 $v0,$zero,$s1` | `.word       0x00111301                   # INVALID     $zero, $s1, 0x1301 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104491 | `audioCompandS16` | `0x800A34F4` | `0x001116F4` | `special_0x34 $v0,$zero,$s1` | `teq         $zero, $s1, 91` |
| funcs_27.c:104501 | `audioCompandS16` | `0x800A3508` | `0x00112ABD` | `special_0x3D $a1,$zero,$s1` | `.word       0x00112ABD                   # INVALID     $zero, $s1, 0x2ABD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104503 | `audioCompandS16` | `0x800A350C` | `0x00112EB5` | `special_0x35 $a1,$zero,$s1` | `.word       0x00112EB5                   # INVALID     $zero, $s1, 0x2EB5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104507 | `audioCompandS16` | `0x800A3514` | `0x001136A8` | `special_0x28 $a2,$zero,$s1` | `.word       0x001136A8                   # INVALID     $zero, $s1, 0x36A8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104519 | `audioCompandS16` | `0x800A352C` | `0x00114E95` | `special_0x15 $t1,$zero,$s1` | `.word       0x00114E95                   # INVALID     $zero, $s1, 0x4E95 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104521 | `audioCompandS16` | `0x800A3530` | `0x00115295` | `special_0x15 $t2,$zero,$s1` | `.word       0x00115295                   # INVALID     $zero, $s1, 0x5295 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104535 | `audioCompandS16` | `0x800A354C` | `0x00116EB0` | `special_0x30 $t5,$zero,$s1` | `tge         $zero, $s1, 442` |
| funcs_27.c:104539 | `audioCompandS16` | `0x800A3554` | `0x001176C1` | `special_0x01 $t6,$zero,$s1` | `.word       0x001176C1                   # INVALID     $zero, $s1, 0x76C1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104541 | `audioCompandS16` | `0x800A3558` | `0x00117ACA` | `movz $t7,$zero,$s1` | `.word       0x00117ACA                   # movz        $t7, $zero, $s1 # 000002C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104549 | `audioCompandS16` | `0x800A3568` | `0x00118AF9` | `special_0x39 $s1,$zero,$s1` | `.word       0x00118AF9                   # INVALID     $zero, $s1, -0x7507 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104557 | `audioCompandS16` | `0x800A3578` | `0x00119B37` | `special_0x37 $s3,$zero,$s1` | `.word       0x00119B37                   # INVALID     $zero, $s1, -0x64C9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104559 | `audioCompandS16` | `0x800A357C` | `0x00119F49` | `jalr $s3,$zero,$s1` | `.word       0x00119F49                   # jalr        $s3, $zero # 00110740 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104569 | `audioCompandS16` | `0x800A3590` | `0x0011B3B0` | `special_0x30 $s6,$zero,$s1` | `tge         $zero, $s1, 718` |
| funcs_27.c:104584 | `audioCompandS16` | `0x800A35A8` | `0x0011CC4B` | `movn $t9,$zero,$s1` | `.word       0x0011CC4B                   # movn        $t9, $zero, $s1 # 00000440 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104586 | `audioCompandS16` | `0x800A35AC` | `0x0011D069` | `special_0x29 $k0,$zero,$s1` | `.word       0x0011D069                   # INVALID     $zero, $s1, -0x2F97 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104596 | `audioCompandS16` | `0x800A35C0` | `0x0011E509` | `jalr $gp,$zero,$s1` | `.word       0x0011E509                   # jalr        $gp, $zero # 00110500 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104602 | `audioCompandS16` | `0x800A35CC` | `0x0011F175` | `special_0x35 $fp,$zero,$s1` | `.word       0x0011F175                   # INVALID     $zero, $s1, -0xE8B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104606 | `audioCompandS16` | `0x800A35D4` | `0x0011F9C1` | `special_0x01 $ra,$zero,$s1` | `.word       0x0011F9C1                   # INVALID     $zero, $s1, -0x63F # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104608 | `audioCompandS16` | `0x800A35D8` | `0x0011FDE9` | `special_0x29 $ra,$zero,$s1` | `.word       0x0011FDE9                   # INVALID     $zero, $s1, -0x217 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104624 | `audioCompandS16` | `0x800A35F8` | `0x00121F49` | `jalr $v1,$zero,$s2` | `.word       0x00121F49                   # jalr        $v1, $zero # 00120740 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104626 | `audioCompandS16` | `0x800A35FC` | `0x00122379` | `special_0x39 $a0,$zero,$s2` | `.word       0x00122379                   # INVALID     $zero, $s2, 0x2379 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104634 | `audioCompandS16` | `0x800A360C` | `0x00123445` | `special_0x05 $a2,$zero,$s2` | `.word       0x00123445                   # INVALID     $zero, $s2, 0x3445 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104638 | `audioCompandS16` | `0x800A3614` | `0x00123CB0` | `special_0x30 $a3,$zero,$s2` | `tge         $zero, $s2, 242` |
| funcs_27.c:104648 | `audioCompandS16` | `0x800A3628` | `0x001251CE` | `special_0x0E $t2,$zero,$s2` | `.word       0x001251CE                   # INVALID     $zero, $s2, 0x51CE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104650 | `audioCompandS16` | `0x800A362C` | `0x0012560A` | `movz $t2,$zero,$s2` | `.word       0x0012560A                   # movz        $t2, $zero, $s2 # 00000600 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104654 | `audioCompandS16` | `0x800A3634` | `0x00125E85` | `special_0x05 $t3,$zero,$s2` | `.word       0x00125E85                   # INVALID     $zero, $s2, 0x5E85 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104660 | `audioCompandS16` | `0x800A3640` | `0x00126B45` | `special_0x05 $t5,$zero,$s2` | `.word       0x00126B45                   # INVALID     $zero, $s2, 0x6B45 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104664 | `audioCompandS16` | `0x800A3648` | `0x001273CA` | `movz $t6,$zero,$s2` | `.word       0x001273CA                   # movz        $t6, $zero, $s2 # 000003C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104666 | `audioCompandS16` | `0x800A364C` | `0x0012780E` | `special_0x0E $t7,$zero,$s2` | `.word       0x0012780E                   # INVALID     $zero, $s2, 0x780E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104676 | `audioCompandS16` | `0x800A3660` | `0x00128D70` | `special_0x30 $s1,$zero,$s2` | `tge         $zero, $s2, 565` |
| funcs_27.c:104680 | `audioCompandS16` | `0x800A3668` | `0x00129605` | `special_0x05 $s2,$zero,$s2` | `.word       0x00129605                   # INVALID     $zero, $s2, -0x69FB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104690 | `audioCompandS16` | `0x800A367C` | `0x0012AB8A` | `movz $s5,$zero,$s2` | `.word       0x0012AB8A                   # movz        $s5, $zero, $s2 # 00000380 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104700 | `audioCompandS16` | `0x800A3690` | `0x0012C128` | `special_0x28 $t8,$zero,$s2` | `.word       0x0012C128                   # INVALID     $zero, $s2, -0x3ED8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104708 | `audioCompandS16` | `0x800A36A0` | `0x0012D285` | `special_0x05 $k0,$zero,$s2` | `.word       0x0012D285                   # INVALID     $zero, $s2, -0x2D7B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104714 | `audioCompandS16` | `0x800A36AC` | `0x0012DF95` | `special_0x15 $k1,$zero,$s2` | `.word       0x0012DF95                   # INVALID     $zero, $s2, -0x206B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104716 | `audioCompandS16` | `0x800A36B0` | `0x0012E3F2` | `special_0x32 $gp,$zero,$s2` | `tlt         $zero, $s2, 911` |
| funcs_27.c:104722 | `audioCompandS16` | `0x800A36BC` | `0x0012F10F` | `special_0x0F $fp,$zero,$s2` | `.word       0x0012F10F                   # sync # 0012F100 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104724 | `audioCompandS16` | `0x800A36C0` | `0x0012F570` | `special_0x30 $fp,$zero,$s2` | `tge         $zero, $s2, 981` |
| funcs_27.c:104728 | `audioCompandS16` | `0x800A36C8` | `0x0012FE35` | `special_0x35 $ra,$zero,$s2` | `.word       0x0012FE35                   # INVALID     $zero, $s2, -0x1CB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104732 | `audioCompandS16` | `0x800A36D0` | `0x001306FD` | `special_0x3D $zero,$zero,$s3` | `.word       0x001306FD                   # INVALID     $zero, $s3, 0x6FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104736 | `audioCompandS16` | `0x800A36D8` | `0x00130FCA` | `movz $at,$zero,$s3` | `.word       0x00130FCA                   # movz        $at, $zero, $s3 # 000007C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104738 | `audioCompandS16` | `0x800A36DC` | `0x00131432` | `special_0x32 $v0,$zero,$s3` | `tlt         $zero, $s3, 80` |
| funcs_27.c:104742 | `audioCompandS16` | `0x800A36E4` | `0x00131D05` | `special_0x05 $v1,$zero,$s3` | `.word       0x00131D05                   # INVALID     $zero, $s3, 0x1D05 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104744 | `audioCompandS16` | `0x800A36E8` | `0x00132170` | `special_0x30 $a0,$zero,$s3` | `tge         $zero, $s3, 133` |
| funcs_27.c:104748 | `audioCompandS16` | `0x800A36F0` | `0x00132A49` | `jalr $a1,$zero,$s3` | `.word       0x00132A49                   # jalr        $a1, $zero # 00130240 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104769 | `audioCompandS16` | `0x800A3714` | `0x0013524D` | `break $t2,$zero,$s3` | `break       19, 329` |
| funcs_27.c:104771 | `audioCompandS16` | `0x800A3718` | `0x001356C5` | `special_0x05 $t2,$zero,$s3` | `.word       0x001356C5                   # INVALID     $zero, $s3, 0x56C5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104773 | `audioCompandS16` | `0x800A371C` | `0x00135B3D` | `special_0x3D $t3,$zero,$s3` | `.word       0x00135B3D                   # INVALID     $zero, $s3, 0x5B3D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104775 | `audioCompandS16` | `0x800A3720` | `0x00135FB6` | `special_0x36 $t3,$zero,$s3` | `tne         $zero, $s3, 382` |
| funcs_27.c:104777 | `audioCompandS16` | `0x800A3724` | `0x00136431` | `special_0x31 $t4,$zero,$s3` | `tgeu        $zero, $s3, 400` |
| funcs_27.c:104781 | `audioCompandS16` | `0x800A372C` | `0x00136D29` | `special_0x29 $t5,$zero,$s3` | `.word       0x00136D29                   # INVALID     $zero, $s3, 0x6D29 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104797 | `audioCompandS16` | `0x800A374C` | `0x00139133` | `special_0x33 $s2,$zero,$s3` | `tltu        $zero, $s3, 580` |
| funcs_27.c:104811 | `audioCompandS16` | `0x800A3768` | `0x0013B0F2` | `special_0x32 $s6,$zero,$s3` | `tlt         $zero, $s3, 707` |
| funcs_27.c:104815 | `audioCompandS16` | `0x800A3770` | `0x0013BA0D` | `break $s7,$zero,$s3` | `break       19, 744` |
| funcs_27.c:104827 | `audioCompandS16` | `0x800A3788` | `0x0013D579` | `special_0x39 $k0,$zero,$s3` | `.word       0x0013D579                   # INVALID     $zero, $s3, -0x2A87 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104829 | `audioCompandS16` | `0x800A378C` | `0x0013DA0F` | `special_0x0F $k1,$zero,$s3` | `.word       0x0013DA0F                   # sync # 0013DA00 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104833 | `audioCompandS16` | `0x800A3794` | `0x0013E33D` | `special_0x3D $gp,$zero,$s3` | `.word       0x0013E33D                   # INVALID     $zero, $s3, -0x1CC3 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104837 | `audioCompandS16` | `0x800A379C` | `0x0013EC70` | `special_0x30 $sp,$zero,$s3` | `tge         $zero, $s3, 945` |
| funcs_27.c:104839 | `audioCompandS16` | `0x800A37A0` | `0x0013F10B` | `movn $fp,$zero,$s3` | `.word       0x0013F10B                   # movn        $fp, $zero, $s3 # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104855 | `audioCompandS16` | `0x800A37C0` | `0x00141609` | `jalr $v0,$zero,$s4` | `.word       0x00141609                   # jalr        $v0, $zero # 00140600 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104865 | `audioCompandS16` | `0x800A37D4` | `0x00142D4B` | `movn $a1,$zero,$s4` | `.word       0x00142D4B                   # movn        $a1, $zero, $s4 # 00000540 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104867 | `audioCompandS16` | `0x800A37D8` | `0x001431F5` | `special_0x35 $a2,$zero,$s4` | `.word       0x001431F5                   # INVALID     $zero, $s4, 0x31F5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104874 | `audioCompandS16` | `0x800A37E4` | `0x00143FF9` | `special_0x39 $a3,$zero,$s4` | `.word       0x00143FF9                   # INVALID     $zero, $s4, 0x3FF9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104876 | `audioCompandS16` | `0x800A37E8` | `0x001444A8` | `special_0x28 $t0,$zero,$s4` | `.word       0x001444A8                   # INVALID     $zero, $s4, 0x44A8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104881 | `audioCompandS16` | `0x800A37F4` | `0x001452B9` | `special_0x39 $t2,$zero,$s4` | `.word       0x001452B9                   # INVALID     $zero, $s4, 0x52B9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104885 | `audioCompandS16` | `0x800A37F4` | `0x001452B9` | `special_0x39 $t2,$zero,$s4` | `.word       0x001452B9                   # INVALID     $zero, $s4, 0x52B9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104893 | `audioCompandS16` | `0x800A3804` | `0x0014658A` | `movz $t4,$zero,$s4` | `.word       0x0014658A                   # movz        $t4, $zero, $s4 # 00000580 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104895 | `audioCompandS16` | `0x800A3808` | `0x00146A41` | `special_0x01 $t5,$zero,$s4` | `.word       0x00146A41                   # INVALID     $zero, $s4, 0x6A41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104897 | `audioCompandS16` | `0x800A380C` | `0x00146EF9` | `special_0x39 $t5,$zero,$s4` | `.word       0x00146EF9                   # INVALID     $zero, $s4, 0x6EF9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104899 | `audioCompandS16` | `0x800A3810` | `0x001473B2` | `special_0x32 $t6,$zero,$s4` | `tlt         $zero, $s4, 462` |
| funcs_27.c:104903 | `audioCompandS16` | `0x800A3818` | `0x00147D28` | `special_0x28 $t7,$zero,$s4` | `.word       0x00147D28                   # INVALID     $zero, $s4, 0x7D28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104923 | `audioCompandS16` | `0x800A3840` | `0x0014ACB6` | `special_0x36 $s5,$zero,$s4` | `tne         $zero, $s4, 690` |
| funcs_27.c:104925 | `audioCompandS16` | `0x800A3844` | `0x0014B17D` | `special_0x3D $s6,$zero,$s4` | `.word       0x0014B17D                   # INVALID     $zero, $s4, -0x4E83 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104929 | `audioCompandS16` | `0x800A384C` | `0x0014BB0F` | `special_0x0F $s7,$zero,$s4` | `.word       0x0014BB0F                   # sync # 0014BB00 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104935 | `audioCompandS16` | `0x800A3858` | `0x0014C973` | `special_0x33 $t9,$zero,$s4` | `tltu        $zero, $s4, 805` |
| funcs_27.c:104937 | `audioCompandS16` | `0x800A385C` | `0x0014CE41` | `special_0x01 $t9,$zero,$s4` | `.word       0x0014CE41                   # INVALID     $zero, $s4, -0x31BF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104943 | `audioCompandS16` | `0x800A3868` | `0x0014DCB2` | `special_0x32 $k1,$zero,$s4` | `tlt         $zero, $s4, 882` |
| funcs_27.c:104955 | `audioCompandS16` | `0x800A3880` | `0x0014F9B2` | `special_0x32 $ra,$zero,$s4` | `tlt         $zero, $s4, 998` |
| funcs_27.c:104957 | `audioCompandS16` | `0x800A3884` | `0x0014FE8B` | `movn $ra,$zero,$s4` | `.word       0x0014FE8B                   # movn        $ra, $zero, $s4 # 00000680 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104961 | `audioCompandS16` | `0x800A388C` | `0x00150841` | `special_0x01 $at,$zero,$s5` | `.word       0x00150841                   # INVALID     $zero, $s5, 0x841 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104973 | `audioCompandS16` | `0x800A38A4` | `0x0015257D` | `special_0x3D $a0,$zero,$s5` | `.word       0x0015257D                   # INVALID     $zero, $s5, 0x257D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104977 | `audioCompandS16` | `0x800A38AC` | `0x00152F45` | `special_0x05 $a1,$zero,$s5` | `.word       0x00152F45                   # INVALID     $zero, $s5, 0x2F45 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104983 | `audioCompandS16` | `0x800A38B8` | `0x00153DF9` | `special_0x39 $a3,$zero,$s5` | `.word       0x00153DF9                   # INVALID     $zero, $s5, 0x3DF9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:104987 | `audioCompandS16` | `0x800A38C0` | `0x001547CD` | `break $t0,$zero,$s5` | `break       21, 287` |
| funcs_27.c:104997 | `audioCompandS16` | `0x800A38D4` | `0x00156070` | `special_0x30 $t4,$zero,$s5` | `tge         $zero, $s5, 385` |
| funcs_27.c:105007 | `audioCompandS16` | `0x800A38E8` | `0x00157931` | `special_0x31 $t7,$zero,$s5` | `tgeu        $zero, $s5, 484` |
| funcs_27.c:105017 | `audioCompandS16` | `0x800A38FC` | `0x0015920E` | `special_0x0E $s2,$zero,$s5` | `.word       0x0015920E                   # INVALID     $zero, $s5, -0x6DF2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105019 | `audioCompandS16` | `0x800A3900` | `0x0015970A` | `movz $s2,$zero,$s5` | `.word       0x0015970A                   # movz        $s2, $zero, $s5 # 00000700 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105032 | `audioCompandS16` | `0x800A3914` | `0x0015B00A` | `movz $s6,$zero,$s5` | `movz        $s6, $zero, $s5` |
| funcs_27.c:105034 | `audioCompandS16` | `0x800A3918` | `0x0015B50D` | `break $s6,$zero,$s5` | `break       21, 724` |
| funcs_27.c:105048 | `audioCompandS16` | `0x800A3934` | `0x0015D845` | `special_0x05 $k1,$zero,$s5` | `.word       0x0015D845                   # INVALID     $zero, $s5, -0x27BB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105062 | `audioCompandS16` | `0x800A3950` | `0x0015FBB6` | `special_0x36 $ra,$zero,$s5` | `tne         $zero, $s5, 1006` |
| funcs_27.c:105064 | `audioCompandS16` | `0x800A3954` | `0x001600CB` | `movn $zero,$zero,$s6` | `.word       0x001600CB                   # movn        $zero, $zero, $s6 # 000000C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105074 | `audioCompandS16` | `0x800A3968` | `0x00161A45` | `special_0x05 $v1,$zero,$s6` | `.word       0x00161A45                   # INVALID     $zero, $s6, 0x1A45 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105096 | `audioCompandS16` | `0x800A3994` | `0x001652B9` | `special_0x39 $t2,$zero,$s6` | `.word       0x001652B9                   # INVALID     $zero, $s6, 0x52B9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105100 | `audioCompandS16` | `0x800A399C` | `0x00165D0D` | `break $t3,$zero,$s6` | `break       22, 372` |
| funcs_27.c:105108 | `audioCompandS16` | `0x800A39AC` | `0x001671C1` | `special_0x01 $t6,$zero,$s6` | `.word       0x001671C1                   # INVALID     $zero, $s6, 0x71C1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105110 | `audioCompandS16` | `0x800A39B0` | `0x001676F1` | `special_0x31 $t6,$zero,$s6` | `tgeu        $zero, $s6, 475` |
| funcs_27.c:105114 | `audioCompandS16` | `0x800A39B8` | `0x00168155` | `special_0x15 $s0,$zero,$s6` | `.word       0x00168155                   # INVALID     $zero, $s6, -0x7EAB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105116 | `audioCompandS16` | `0x800A39BC` | `0x00168689` | `jalr $s0,$zero,$s6` | `.word       0x00168689                   # jalr        $s0, $zero # 00160680 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105120 | `audioCompandS16` | `0x800A39C4` | `0x001690F4` | `special_0x34 $s2,$zero,$s6` | `teq         $zero, $s6, 579` |
| funcs_27.c:105130 | `audioCompandS16` | `0x800A39D8` | `0x0016AB15` | `special_0x15 $s5,$zero,$s6` | `.word       0x0016AB15                   # INVALID     $zero, $s6, -0x54EB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105148 | `audioCompandS16` | `0x800A39FC` | `0x0016DA69` | `special_0x29 $k1,$zero,$s6` | `.word       0x0016DA69                   # INVALID     $zero, $s6, -0x2597 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105150 | `audioCompandS16` | `0x800A3A00` | `0x0016DFB2` | `special_0x32 $k1,$zero,$s6` | `tlt         $zero, $s6, 894` |
| funcs_27.c:105162 | `audioCompandS16` | `0x800A3A18` | `0x0016FF7D` | `special_0x3D $ra,$zero,$s6` | `.word       0x0016FF7D                   # INVALID     $zero, $s6, -0x83 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105164 | `audioCompandS16` | `0x800A3A1C` | `0x001704CE` | `special_0x0E $zero,$zero,$s7` | `.word       0x001704CE                   # INVALID     $zero, $s7, 0x4CE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105168 | `audioCompandS16` | `0x800A3A24` | `0x00170F74` | `special_0x34 $at,$zero,$s7` | `teq         $zero, $s7, 61` |
| funcs_27.c:105177 | `audioCompandS16` | `0x800A3A30` | `0x00171F75` | `special_0x35 $v1,$zero,$s7` | `.word       0x00171F75                   # INVALID     $zero, $s7, 0x1F75 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105179 | `audioCompandS16` | `0x800A3A34` | `0x001724CE` | `special_0x0E $a0,$zero,$s7` | `.word       0x001724CE                   # INVALID     $zero, $s7, 0x24CE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105191 | `audioCompandS16` | `0x800A3A4C` | `0x001744F9` | `special_0x39 $t0,$zero,$s7` | `.word       0x001744F9                   # INVALID     $zero, $s7, 0x44F9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105195 | `audioCompandS16` | `0x800A3A54` | `0x00174FBD` | `special_0x3D $t1,$zero,$s7` | `.word       0x00174FBD                   # INVALID     $zero, $s7, 0x4FBD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105199 | `audioCompandS16` | `0x800A3A5C` | `0x00175A85` | `special_0x05 $t3,$zero,$s7` | `.word       0x00175A85                   # INVALID     $zero, $s7, 0x5A85 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105209 | `audioCompandS16` | `0x800A3A70` | `0x0017758F` | `special_0x0F $t6,$zero,$s7` | `.word       0x0017758F                   # sync # 00177580 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105213 | `audioCompandS16` | `0x800A3A78` | `0x00178069` | `special_0x29 $s0,$zero,$s7` | `.word       0x00178069                   # INVALID     $zero, $s7, -0x7F97 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105218 | `audioCompandS16` | `0x800A3A84` | `0x001790B9` | `special_0x39 $s2,$zero,$s7` | `.word       0x001790B9                   # INVALID     $zero, $s7, -0x6F47 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105222 | `audioCompandS16` | `0x800A3A84` | `0x001790B9` | `special_0x39 $s2,$zero,$s7` | `.word       0x001790B9                   # INVALID     $zero, $s7, -0x6F47 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105230 | `audioCompandS16` | `0x800A3A94` | `0x0017A68B` | `movn $s4,$zero,$s7` | `.word       0x0017A68B                   # movn        $s4, $zero, $s7 # 00000680 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105236 | `audioCompandS16` | `0x800A3AA0` | `0x0017B6F5` | `special_0x35 $s6,$zero,$s7` | `.word       0x0017B6F5                   # INVALID     $zero, $s7, -0x490B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105238 | `audioCompandS16` | `0x800A3AA4` | `0x0017BC70` | `special_0x30 $s7,$zero,$s7` | `tge         $zero, $s7, 753` |
| funcs_27.c:105254 | `audioCompandS16` | `0x800A3AC0` | `0x0017E2F3` | `special_0x33 $gp,$zero,$s7` | `tltu        $zero, $s7, 907` |
| funcs_27.c:105257 | `audioCompandS16` | `0x800A3AC4` | `0x0017E879` | `special_0x39 $sp,$zero,$s7` | `.word       0x0017E879                   # INVALID     $zero, $s7, -0x1787 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105271 | `audioCompandS16` | `0x800A3ADC` | `0x001809B4` | `special_0x34 $at,$zero,$t8` | `teq         $zero, $t8, 38` |
| funcs_27.c:105280 | `audioCompandS16` | `0x800A3AEC` | `0x00181FF6` | `special_0x36 $v1,$zero,$t8` | `tne         $zero, $t8, 127` |
| funcs_27.c:105282 | `audioCompandS16` | `0x800A3AF0` | `0x0018258A` | `movz $a0,$zero,$t8` | `.word       0x0018258A                   # movz        $a0, $zero, $t8 # 00000580 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105286 | `audioCompandS16` | `0x800A3AF8` | `0x001830B5` | `special_0x35 $a2,$zero,$t8` | `.word       0x001830B5                   # INVALID     $zero, $t8, 0x30B5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105298 | `audioCompandS16` | `0x800A3B0C` | `0x00184CB7` | `special_0x37 $t1,$zero,$t8` | `.word       0x00184CB7                   # INVALID     $zero, $t8, 0x4CB7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105300 | `audioCompandS16` | `0x800A3B10` | `0x00185255` | `special_0x15 $t2,$zero,$t8` | `.word       0x00185255                   # INVALID     $zero, $t8, 0x5255 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105303 | `audioCompandS16` | `0x800A3B14` | `0x001857F4` | `special_0x34 $t2,$zero,$t8` | `teq         $zero, $t8, 351` |
| funcs_27.c:105306 | `audioCompandS16` | `0x800A3B18` | `0x00185D95` | `special_0x15 $t3,$zero,$t8` | `.word       0x00185D95                   # INVALID     $zero, $t8, 0x5D95 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105308 | `audioCompandS16` | `0x800A3B1C` | `0x00186336` | `special_0x36 $t4,$zero,$t8` | `tne         $zero, $t8, 396` |
| funcs_27.c:105316 | `audioCompandS16` | `0x800A3B2C` | `0x001879CB` | `movn $t7,$zero,$t8` | `.word       0x001879CB                   # movn        $t7, $zero, $t8 # 000001C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105318 | `audioCompandS16` | `0x800A3B30` | `0x00187F73` | `special_0x33 $t7,$zero,$t8` | `tltu        $zero, $t8, 509` |
| funcs_27.c:105323 | `audioCompandS16` | `0x800A3B3C` | `0x00189074` | `special_0x34 $s2,$zero,$t8` | `teq         $zero, $t8, 577` |
| funcs_27.c:105327 | `audioCompandS16` | `0x800A3B3C` | `0x00189074` | `special_0x34 $s2,$zero,$t8` | `teq         $zero, $t8, 577` |
| funcs_27.c:105333 | `audioCompandS16` | `0x800A3B48` | `0x0018A181` | `special_0x01 $s4,$zero,$t8` | `.word       0x0018A181                   # INVALID     $zero, $t8, -0x5E7F # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105335 | `audioCompandS16` | `0x800A3B4C` | `0x0018A732` | `special_0x32 $s4,$zero,$t8` | `tlt         $zero, $t8, 668` |
| funcs_27.c:105341 | `audioCompandS16` | `0x800A3B58` | `0x0018B84F` | `special_0x0F $s7,$zero,$t8` | `.word       0x0018B84F                   # sync # 0018B840 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105347 | `audioCompandS16` | `0x800A3B64` | `0x0018C977` | `special_0x37 $t9,$zero,$t8` | `.word       0x0018C977                   # INVALID     $zero, $t8, -0x3689 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105349 | `audioCompandS16` | `0x800A3B68` | `0x0018CF32` | `special_0x32 $t9,$zero,$t8` | `tlt         $zero, $t8, 828` |
| funcs_27.c:105363 | `audioCompandS16` | `0x800A3B84` | `0x0018F773` | `special_0x33 $fp,$zero,$t8` | `tltu        $zero, $t8, 989` |
| funcs_27.c:105377 | `audioCompandS16` | `0x800A3BA0` | `0x00191FF4` | `special_0x34 $v1,$zero,$t9` | `teq         $zero, $t9, 127` |
| funcs_27.c:105398 | `audioCompandS16` | `0x800A3BC8` | `0x00195A45` | `special_0x05 $t3,$zero,$t9` | `.word       0x00195A45                   # INVALID     $zero, $t9, 0x5A45 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105414 | `audioCompandS16` | `0x800A3BE8` | `0x0019894D` | `break $s1,$zero,$t9` | `break       25, 549` |
| funcs_27.c:105416 | `audioCompandS16` | `0x800A3BEC` | `0x00198F34` | `special_0x34 $s1,$zero,$t9` | `teq         $zero, $t9, 572` |
| funcs_27.c:105422 | `audioCompandS16` | `0x800A3BF8` | `0x0019A0F1` | `special_0x31 $s4,$zero,$t9` | `tgeu        $zero, $t9, 643` |
| funcs_27.c:105439 | `audioCompandS16` | `0x800A3C18` | `0x0019D07D` | `special_0x3D $k0,$zero,$t9` | `.word       0x0019D07D                   # INVALID     $zero, $t9, -0x2F83 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105441 | `audioCompandS16` | `0x800A3C1C` | `0x0019D675` | `special_0x35 $k0,$zero,$t9` | `.word       0x0019D675                   # INVALID     $zero, $t9, -0x298B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105445 | `audioCompandS16` | `0x800A3C24` | `0x0019E268` | `special_0x28 $gp,$zero,$t9` | `.word       0x0019E268                   # INVALID     $zero, $t9, -0x1D98 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105463 | `audioCompandS16` | `0x800A3C48` | `0x001A1873` | `special_0x33 $v1,$zero,$k0` | `tltu        $zero, $k0, 97` |
| funcs_27.c:105467 | `audioCompandS16` | `0x800A3C50` | `0x001A2485` | `special_0x05 $a0,$zero,$k0` | `.word       0x001A2485                   # INVALID     $zero, $k0, 0x2485 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105477 | `audioCompandS16` | `0x800A3C64` | `0x001A42CA` | `movz $t0,$zero,$k0` | `.word       0x001A42CA                   # movz        $t0, $zero, $k0 # 000002C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105481 | `audioCompandS16` | `0x800A3C6C` | `0x001A4EF0` | `special_0x30 $t1,$zero,$k0` | `tge         $zero, $k0, 315` |
| funcs_27.c:105487 | `audioCompandS16` | `0x800A3C78` | `0x001A6132` | `special_0x32 $t4,$zero,$k0` | `tlt         $zero, $k0, 388` |
| funcs_27.c:105489 | `audioCompandS16` | `0x800A3C7C` | `0x001A674B` | `movn $t4,$zero,$k0` | `.word       0x001A674B                   # movn        $t4, $zero, $k0 # 00000740 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105493 | `audioCompandS16` | `0x800A3C84` | `0x001A7381` | `special_0x01 $t6,$zero,$k0` | `.word       0x001A7381                   # INVALID     $zero, $k0, 0x7381 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105497 | `audioCompandS16` | `0x800A3C8C` | `0x001A7FBD` | `special_0x3D $t7,$zero,$k0` | `.word       0x001A7FBD                   # INVALID     $zero, $k0, 0x7FBD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105523 | `audioCompandS16` | `0x800A3CC0` | `0x001ACFCD` | `break $t9,$zero,$k0` | `break       26, 831` |
| funcs_27.c:105527 | `audioCompandS16` | `0x800A3CC8` | `0x001ADC34` | `special_0x34 $k1,$zero,$k0` | `teq         $zero, $k0, 880` |
| funcs_27.c:105529 | `audioCompandS16` | `0x800A3CCC` | `0x001AE269` | `special_0x29 $gp,$zero,$k0` | `.word       0x001AE269                   # INVALID     $zero, $k0, -0x1D97 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105537 | `audioCompandS16` | `0x800A3CDC` | `0x001AFB4E` | `special_0x0E $ra,$zero,$k0` | `.word       0x001AFB4E                   # INVALID     $zero, $k0, -0x4B2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105539 | `audioCompandS16` | `0x800A3CE0` | `0x001B018A` | `movz $zero,$zero,$k1` | `.word       0x001B018A                   # movz        $zero, $zero, $k1 # 00000180 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105543 | `audioCompandS16` | `0x800A3CEC` | `0x001B1449` | `jalr $v0,$zero,$k1` | `.word       0x001B1449                   # jalr        $v0, $zero # 001B0440 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105550 | `audioCompandS16` | `0x800A3CEC` | `0x001B1449` | `jalr $v0,$zero,$k1` | `.word       0x001B1449                   # jalr        $v0, $zero # 001B0440 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105554 | `audioCompandS16` | `0x800A3CEC` | `0x001B1449` | `jalr $v0,$zero,$k1` | `.word       0x001B1449                   # jalr        $v0, $zero # 001B0440 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105556 | `audioCompandS16` | `0x800A3CF0` | `0x001B1A8B` | `movn $v1,$zero,$k1` | `.word       0x001B1A8B                   # movn        $v1, $zero, $k1 # 00000280 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105558 | `audioCompandS16` | `0x800A3CF4` | `0x001B20CF` | `special_0x0F $a0,$zero,$k1` | `.word       0x001B20CF                   # sync # 001B20C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105570 | `audioCompandS16` | `0x800A3D0C` | `0x001B4685` | `special_0x05 $t0,$zero,$k1` | `.word       0x001B4685                   # INVALID     $zero, $k1, 0x4685 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105576 | `audioCompandS16` | `0x800A3D18` | `0x001B5973` | `special_0x33 $t3,$zero,$k1` | `tltu        $zero, $k1, 357` |
| funcs_27.c:105592 | `audioCompandS16` | `0x800A3D38` | `0x001B8C30` | `special_0x30 $s1,$zero,$k1` | `tge         $zero, $k1, 560` |
| funcs_27.c:105594 | `audioCompandS16` | `0x800A3D3C` | `0x001B928E` | `special_0x0E $s2,$zero,$k1` | `.word       0x001B928E                   # INVALID     $zero, $k1, -0x6D72 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105598 | `audioCompandS16` | `0x800A3D44` | `0x001B9F4E` | `special_0x0E $s3,$zero,$k1` | `.word       0x001B9F4E                   # INVALID     $zero, $k1, -0x60B2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105600 | `audioCompandS16` | `0x800A3D48` | `0x001BA5B1` | `special_0x31 $s4,$zero,$k1` | `tgeu        $zero, $k1, 662` |
| funcs_27.c:105602 | `audioCompandS16` | `0x800A3D4C` | `0x001BAC15` | `special_0x15 $s5,$zero,$k1` | `.word       0x001BAC15                   # INVALID     $zero, $k1, -0x53EB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105608 | `audioCompandS16` | `0x800A3D58` | `0x001BBF4A` | `movz $s7,$zero,$k1` | `.word       0x001BBF4A                   # movz        $s7, $zero, $k1 # 00000740 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105610 | `audioCompandS16` | `0x800A3D5C` | `0x001BC5B4` | `special_0x34 $t8,$zero,$k1` | `teq         $zero, $k1, 790` |
| funcs_27.c:105623 | `audioCompandS16` | `0x800A3D74` | `0x001BEC4F` | `special_0x0F $sp,$zero,$k1` | `.word       0x001BEC4F                   # sync # 001BEC40 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105627 | `audioCompandS16` | `0x800A3D7C` | `0x001BF939` | `special_0x39 $ra,$zero,$k1` | `.word       0x001BF939                   # INVALID     $zero, $k1, -0x6C7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105629 | `audioCompandS16` | `0x800A3D80` | `0x001BFFB0` | `special_0x30 $ra,$zero,$k1` | `tge         $zero, $k1, 1022` |
| funcs_27.c:105631 | `audioCompandS16` | `0x800A3D84` | `0x001C0629` | `special_0x29 $zero,$zero,$gp` | `.word       0x001C0629                   # INVALID     $zero, $gp, 0x629 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105651 | `audioCompandS16` | `0x800A3DAC` | `0x001C4734` | `special_0x34 $t0,$zero,$gp` | `teq         $zero, $gp, 284` |
| funcs_27.c:105655 | `audioCompandS16` | `0x800A3DB4` | `0x001C5449` | `jalr $t2,$zero,$gp` | `.word       0x001C5449                   # jalr        $t2, $zero # 001C0440 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105657 | `audioCompandS16` | `0x800A3DB8` | `0x001C5AD5` | `special_0x15 $t3,$zero,$gp` | `.word       0x001C5AD5                   # INVALID     $zero, $gp, 0x5AD5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105661 | `audioCompandS16` | `0x800A3DC0` | `0x001C67F2` | `special_0x32 $t4,$zero,$gp` | `tlt         $zero, $gp, 415` |
| funcs_27.c:105675 | `audioCompandS16` | `0x800A3DDC` | `0x001C9609` | `jalr $s2,$zero,$gp` | `.word       0x001C9609                   # jalr        $s2, $zero # 001C0600 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105679 | `audioCompandS16` | `0x800A3DE4` | `0x001CA341` | `special_0x01 $s4,$zero,$gp` | `.word       0x001CA341                   # INVALID     $zero, $gp, -0x5CBF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105687 | `audioCompandS16` | `0x800A3DF4` | `0x001CBDC5` | `special_0x05 $s7,$zero,$gp` | `.word       0x001CBDC5                   # INVALID     $zero, $gp, -0x423B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105700 | `audioCompandS16` | `0x800A3E0C` | `0x001CE5B9` | `special_0x39 $gp,$zero,$gp` | `.word       0x001CE5B9                   # INVALID     $zero, $gp, -0x1A47 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105718 | `audioCompandS16` | `0x800A3E30` | `0x001D220F` | `special_0x0F $a0,$zero,$sp` | `.word       0x001D220F                   # sync # 001D2200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105720 | `audioCompandS16` | `0x800A3E34` | `0x001D28CB` | `movn $a1,$zero,$sp` | `.word       0x001D28CB                   # movn        $a1, $zero, $sp # 000000C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105730 | `audioCompandS16` | `0x800A3E44` | `0x001D43CA` | `movz $t0,$zero,$sp` | `.word       0x001D43CA                   # movz        $t0, $zero, $sp # 000003C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105734 | `audioCompandS16` | `0x800A3E44` | `0x001D43CA` | `movz $t0,$zero,$sp` | `.word       0x001D43CA                   # movz        $t0, $zero, $sp # 000003C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105736 | `audioCompandS16` | `0x800A3E48` | `0x001D4A8E` | `special_0x0E $t1,$zero,$sp` | `.word       0x001D4A8E                   # INVALID     $zero, $sp, 0x4A8E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105748 | `audioCompandS16` | `0x800A3E60` | `0x001D7345` | `special_0x05 $t6,$zero,$sp` | `.word       0x001D7345                   # INVALID     $zero, $sp, 0x7345 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105754 | `audioCompandS16` | `0x800A3E6C` | `0x001D87B6` | `special_0x36 $s0,$zero,$sp` | `tne         $zero, $sp, 542` |
| funcs_27.c:105756 | `audioCompandS16` | `0x800A3E70` | `0x001D8E8A` | `movz $s1,$zero,$sp` | `.word       0x001D8E8A                   # movz        $s1, $zero, $sp # 00000680 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105760 | `audioCompandS16` | `0x800A3E78` | `0x001D9C35` | `special_0x35 $s3,$zero,$sp` | `.word       0x001D9C35                   # INVALID     $zero, $sp, -0x63CB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105762 | `audioCompandS16` | `0x800A3E7C` | `0x001DA30E` | `special_0x0E $s4,$zero,$sp` | `.word       0x001DA30E                   # INVALID     $zero, $sp, -0x5CF2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105795 | `audioCompandS16` | `0x800A3EB8` | `0x001E0A77` | `special_0x37 $at,$zero,$fp` | `.word       0x001E0A77                   # INVALID     $zero, $fp, 0xA77 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105797 | `audioCompandS16` | `0x800A3EBC` | `0x001E1169` | `special_0x29 $v0,$zero,$fp` | `.word       0x001E1169                   # INVALID     $zero, $fp, 0x1169 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105807 | `audioCompandS16` | `0x800A3ED0` | `0x001E3439` | `special_0x39 $a2,$zero,$fp` | `.word       0x001E3439                   # INVALID     $zero, $fp, 0x3439 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105809 | `audioCompandS16` | `0x800A3ED4` | `0x001E3B35` | `special_0x35 $a3,$zero,$fp` | `.word       0x001E3B35                   # INVALID     $zero, $fp, 0x3B35 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105811 | `audioCompandS16` | `0x800A3ED8` | `0x001E4232` | `special_0x32 $t0,$zero,$fp` | `tlt         $zero, $fp, 264` |
| funcs_27.c:105813 | `audioCompandS16` | `0x800A3EDC` | `0x001E4930` | `special_0x30 $t1,$zero,$fp` | `tge         $zero, $fp, 292` |
| funcs_27.c:105815 | `audioCompandS16` | `0x800A3EE0` | `0x001E5030` | `special_0x30 $t2,$zero,$fp` | `tge         $zero, $fp, 320` |
| funcs_27.c:105817 | `audioCompandS16` | `0x800A3EE4` | `0x001E5732` | `special_0x32 $t2,$zero,$fp` | `tlt         $zero, $fp, 348` |
| funcs_27.c:105819 | `audioCompandS16` | `0x800A3EE8` | `0x001E5E35` | `special_0x35 $t3,$zero,$fp` | `.word       0x001E5E35                   # INVALID     $zero, $fp, 0x5E35 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105823 | `audioCompandS16` | `0x800A3EF0` | `0x001E6C41` | `special_0x01 $t5,$zero,$fp` | `.word       0x001E6C41                   # INVALID     $zero, $fp, 0x6C41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105825 | `audioCompandS16` | `0x800A3EF4` | `0x001E7349` | `jalr $t6,$zero,$fp` | `.word       0x001E7349                   # jalr        $t6, $zero # 001E0340 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105835 | `audioCompandS16` | `0x800A3F08` | `0x001E968B` | `movn $s2,$zero,$fp` | `.word       0x001E968B                   # movn        $s2, $zero, $fp # 00000680 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105840 | `audioCompandS16` | `0x800A3F10` | `0x001EA4B1` | `special_0x31 $s4,$zero,$fp` | `tgeu        $zero, $fp, 658` |
| funcs_27.c:105846 | `audioCompandS16` | `0x800A3F1C` | `0x001EB9F6` | `special_0x36 $s7,$zero,$fp` | `tne         $zero, $fp, 743` |
| funcs_27.c:105854 | `audioCompandS16` | `0x800A3F28` | `0x001ECF49` | `jalr $t9,$zero,$fp` | `.word       0x001ECF49                   # jalr        $t9, $zero # 001E0740 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105856 | `audioCompandS16` | `0x800A3F2C` | `0x001ED668` | `special_0x28 $k0,$zero,$fp` | `.word       0x001ED668                   # INVALID     $zero, $fp, -0x2998 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105858 | `audioCompandS16` | `0x800A3F30` | `0x001EDD89` | `jalr $k1,$zero,$fp` | `.word       0x001EDD89                   # jalr        $k1, $zero # 001E0580 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105864 | `audioCompandS16` | `0x800A3F3C` | `0x001EF2F6` | `special_0x36 $fp,$zero,$fp` | `tne         $zero, $fp, 971` |
| funcs_27.c:105870 | `audioCompandS16` | `0x800A3F48` | `0x001F0871` | `special_0x31 $at,$zero,$ra` | `tgeu        $zero, $ra, 33` |
| funcs_27.c:105875 | `audioCompandS16` | `0x800A3F50` | `0x001F16CB` | `movn $v0,$zero,$ra` | `.word       0x001F16CB                   # movn        $v0, $zero, $ra # 000006C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105885 | `audioCompandS16` | `0x800A3F64` | `0x001F3ACB` | `movn $a3,$zero,$ra` | `.word       0x001F3ACB                   # movn        $a3, $zero, $ra # 000002C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105893 | `audioCompandS16` | `0x800A3F74` | `0x001F57B5` | `special_0x35 $t2,$zero,$ra` | `.word       0x001F57B5                   # INVALID     $zero, $ra, 0x57B5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105895 | `audioCompandS16` | `0x800A3F78` | `0x001F5EF3` | `special_0x33 $t3,$zero,$ra` | `tltu        $zero, $ra, 379` |
| funcs_27.c:105897 | `audioCompandS16` | `0x800A3F7C` | `0x001F6634` | `special_0x34 $t4,$zero,$ra` | `teq         $zero, $ra, 408` |
| funcs_27.c:105899 | `audioCompandS16` | `0x800A3F80` | `0x001F6D76` | `special_0x36 $t5,$zero,$ra` | `tne         $zero, $ra, 437` |
| funcs_27.c:105907 | `audioCompandS16` | `0x800A3F90` | `0x001F8A8F` | `special_0x0F $s1,$zero,$ra` | `.word       0x001F8A8F                   # sync # 001F8A80 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105913 | `audioCompandS16` | `0x800A3F9C` | `0x001FA073` | `special_0x33 $s4,$zero,$ra` | `tltu        $zero, $ra, 641` |
| funcs_27.c:105943 | `audioCompandS16` | `0x800A3FD8` | `0x000FFC4E` | `special_0x0E $ra,$zero,$t7` | `.word       0x000FFC4E                   # INVALID     $zero, $t7, -0x3B2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105949 | `audioCompandS16` | `0x800A3FE4` | `0x000FF13D` | `special_0x3D $fp,$zero,$t7` | `.word       0x000FF13D                   # INVALID     $zero, $t7, -0xEC3 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105951 | `audioCompandS16` | `0x800A3FE8` | `0x000FED8F` | `special_0x0F $sp,$zero,$t7` | `.word       0x000FED8F                   # sync # 000FED80 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105955 | `audioCompandS16` | `0x800A3FF0` | `0x000FE634` | `special_0x34 $gp,$zero,$t7` | `teq         $zero, $t7, 920` |
| funcs_27.c:105964 | `audioCompandS16` | `0x800A3FFC` | `0x000FDB33` | `special_0x33 $k1,$zero,$t7` | `tltu        $zero, $t7, 876` |
| funcs_27.c:105966 | `audioCompandS16` | `0x800A4000` | `0x000FD789` | `jalr $k0,$zero,$t7` | `.word       0x000FD789                   # jalr        $k0, $zero # 000F0780 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105970 | `audioCompandS16` | `0x800A4008` | `0x000FD039` | `special_0x39 $k0,$zero,$t7` | `.word       0x000FD039                   # INVALID     $zero, $t7, -0x2FC7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105988 | `audioCompandS16` | `0x800A402C` | `0x000FAF79` | `special_0x39 $s5,$zero,$t7` | `.word       0x000FAF79                   # INVALID     $zero, $t7, -0x5087 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:105996 | `audioCompandS16` | `0x800A403C` | `0x000FA101` | `special_0x01 $s4,$zero,$t7` | `.word       0x000FA101                   # INVALID     $zero, $t7, -0x5EFF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106000 | `audioCompandS16` | `0x800A4044` | `0x000F99C9` | `jalr $s3,$zero,$t7` | `.word       0x000F99C9                   # jalr        $s3, $zero # 000F01C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106006 | `audioCompandS16` | `0x800A4050` | `0x000F8EFD` | `special_0x3D $s1,$zero,$t7` | `.word       0x000F8EFD                   # INVALID     $zero, $t7, -0x7103 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106010 | `audioCompandS16` | `0x800A4058` | `0x000F87CE` | `special_0x0E $s0,$zero,$t7` | `.word       0x000F87CE                   # INVALID     $zero, $t7, -0x7832 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106016 | `audioCompandS16` | `0x800A4064` | `0x000F7D0E` | `special_0x0E $t7,$zero,$t7` | `.word       0x000F7D0E                   # INVALID     $zero, $t7, 0x7D0E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106022 | `audioCompandS16` | `0x800A4070` | `0x000F7255` | `special_0x15 $t6,$zero,$t7` | `.word       0x000F7255                   # INVALID     $zero, $t7, 0x7255 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106026 | `audioCompandS16` | `0x800A4078` | `0x000F6B34` | `special_0x34 $t5,$zero,$t7` | `teq         $zero, $t7, 428` |
| funcs_27.c:106030 | `audioCompandS16` | `0x800A4080` | `0x000F6415` | `special_0x15 $t4,$zero,$t7` | `.word       0x000F6415                   # INVALID     $zero, $t7, 0x6415 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106042 | `audioCompandS16` | `0x800A4098` | `0x000F4ECE` | `special_0x0E $t1,$zero,$t7` | `.word       0x000F4ECE                   # INVALID     $zero, $t7, 0x4ECE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106044 | `audioCompandS16` | `0x800A409C` | `0x000F4B45` | `special_0x05 $t1,$zero,$t7` | `.word       0x000F4B45                   # INVALID     $zero, $t7, 0x4B45 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106046 | `audioCompandS16` | `0x800A40A0` | `0x000F47BD` | `special_0x3D $t0,$zero,$t7` | `.word       0x000F47BD                   # INVALID     $zero, $t7, 0x47BD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106048 | `audioCompandS16` | `0x800A40A4` | `0x000F4435` | `special_0x35 $t0,$zero,$t7` | `.word       0x000F4435                   # INVALID     $zero, $t7, 0x4435 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106052 | `audioCompandS16` | `0x800A40AC` | `0x000F3D29` | `special_0x29 $a3,$zero,$t7` | `.word       0x000F3D29                   # INVALID     $zero, $t7, 0x3D29 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106078 | `audioCompandS16` | `0x800A40E0` | `0x000F0FA8` | `special_0x28 $at,$zero,$t7` | `.word       0x000F0FA8                   # INVALID     $zero, $t7, 0xFA8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106082 | `audioCompandS16` | `0x800A40E8` | `0x000F08B4` | `special_0x34 $at,$zero,$t7` | `teq         $zero, $t7, 34` |
| funcs_27.c:106091 | `audioCompandS16` | `0x800A40F8` | `0x000EFAD5` | `special_0x15 $ra,$zero,$t6` | `.word       0x000EFAD5                   # INVALID     $zero, $t6, -0x52B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106097 | `audioCompandS16` | `0x800A4104` | `0x000EF077` | `special_0x37 $fp,$zero,$t6` | `.word       0x000EF077                   # INVALID     $zero, $t6, -0xF89 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106109 | `audioCompandS16` | `0x800A411C` | `0x000EDBCF` | `special_0x0F $k1,$zero,$t6` | `.word       0x000EDBCF                   # sync # 000EDBC0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106113 | `audioCompandS16` | `0x800A4124` | `0x000ED4F3` | `special_0x33 $k0,$zero,$t6` | `tltu        $zero, $t6, 851` |
| funcs_27.c:106125 | `audioCompandS16` | `0x800A413C` | `0x000EC072` | `special_0x32 $t8,$zero,$t6` | `tlt         $zero, $t6, 769` |
| funcs_27.c:106127 | `audioCompandS16` | `0x800A4140` | `0x000EBD09` | `jalr $s7,$zero,$t6` | `.word       0x000EBD09                   # jalr        $s7, $zero # 000E0500 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106135 | `audioCompandS16` | `0x800A4150` | `0x000EAF71` | `special_0x31 $s5,$zero,$t6` | `tgeu        $zero, $t6, 701` |
| funcs_27.c:106140 | `audioCompandS16` | `0x800A4158` | `0x000EA8A9` | `special_0x29 $s5,$zero,$t6` | `.word       0x000EA8A9                   # INVALID     $zero, $t6, -0x5757 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106156 | `audioCompandS16` | `0x800A4178` | `0x000E8DA9` | `special_0x29 $s1,$zero,$t6` | `.word       0x000E8DA9                   # INVALID     $zero, $t6, -0x7257 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106158 | `audioCompandS16` | `0x800A417C` | `0x000E8A4D` | `break $s1,$zero,$t6` | `break       14, 553` |
| funcs_27.c:106160 | `audioCompandS16` | `0x800A4180` | `0x000E86F1` | `special_0x31 $s0,$zero,$t6` | `tgeu        $zero, $t6, 539` |
| funcs_27.c:106168 | `audioCompandS16` | `0x800A4190` | `0x000E798B` | `movn $t7,$zero,$t6` | `.word       0x000E798B                   # movn        $t7, $zero, $t6 # 00000180 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106170 | `audioCompandS16` | `0x800A4194` | `0x000E7633` | `special_0x33 $t6,$zero,$t6` | `tltu        $zero, $t6, 472` |
| funcs_27.c:106176 | `audioCompandS16` | `0x800A41A0` | `0x000E6C30` | `special_0x30 $t5,$zero,$t6` | `tge         $zero, $t6, 432` |
| funcs_27.c:106182 | `audioCompandS16` | `0x800A41AC` | `0x000E6234` | `special_0x34 $t4,$zero,$t6` | `teq         $zero, $t6, 392` |
| funcs_27.c:106198 | `audioCompandS16` | `0x800A41CC` | `0x000E47B7` | `special_0x37 $t0,$zero,$t6` | `.word       0x000E47B7                   # INVALID     $zero, $t6, 0x47B7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106206 | `audioCompandS16` | `0x800A41DC` | `0x000E3A8A` | `movz $a3,$zero,$t6` | `.word       0x000E3A8A                   # movz        $a3, $zero, $t6 # 00000280 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106208 | `audioCompandS16` | `0x800A41E0` | `0x000E3741` | `special_0x01 $a2,$zero,$t6` | `.word       0x000E3741                   # INVALID     $zero, $t6, 0x3741 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106210 | `audioCompandS16` | `0x800A41E4` | `0x000E33F9` | `special_0x39 $a2,$zero,$t6` | `.word       0x000E33F9                   # INVALID     $zero, $t6, 0x33F9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106212 | `audioCompandS16` | `0x800A41E8` | `0x000E30B1` | `special_0x31 $a2,$zero,$t6` | `tgeu        $zero, $t6, 194` |
| funcs_27.c:106228 | `audioCompandS16` | `0x800A4208` | `0x000E168E` | `special_0x0E $v0,$zero,$t6` | `.word       0x000E168E                   # INVALID     $zero, $t6, 0x168E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106230 | `audioCompandS16` | `0x800A420C` | `0x000E134D` | `break $v0,$zero,$t6` | `break       14, 77` |
| funcs_27.c:106232 | `audioCompandS16` | `0x800A4210` | `0x000E100D` | `break $v0,$zero,$t6` | `break       14, 64` |
| funcs_27.c:106234 | `audioCompandS16` | `0x800A4214` | `0x000E0CCE` | `special_0x0E $at,$zero,$t6` | `.word       0x000E0CCE                   # INVALID     $zero, $t6, 0xCCE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106236 | `audioCompandS16` | `0x800A4218` | `0x000E098F` | `special_0x0F $at,$zero,$t6` | `.word       0x000E098F                   # sync # 000E0980 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106252 | `audioCompandS16` | `0x800A4238` | `0x000DEFB5` | `special_0x35 $sp,$zero,$t5` | `.word       0x000DEFB5                   # INVALID     $zero, $t5, -0x104B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106254 | `audioCompandS16` | `0x800A423C` | `0x000DEC7D` | `special_0x3D $sp,$zero,$t5` | `.word       0x000DEC7D                   # INVALID     $zero, $t5, -0x1383 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106256 | `audioCompandS16` | `0x800A4240` | `0x000DE945` | `special_0x05 $sp,$zero,$t5` | `.word       0x000DE945                   # INVALID     $zero, $t5, -0x16BB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106258 | `audioCompandS16` | `0x800A4244` | `0x000DE60F` | `special_0x0F $gp,$zero,$t5` | `.word       0x000DE60F                   # sync # 000DE600 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106264 | `audioCompandS16` | `0x800A4250` | `0x000DDC70` | `special_0x30 $k1,$zero,$t5` | `tge         $zero, $t5, 881` |
| funcs_27.c:106266 | `audioCompandS16` | `0x800A4254` | `0x000DD93D` | `special_0x3D $k1,$zero,$t5` | `.word       0x000DD93D                   # INVALID     $zero, $t5, -0x26C3 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106268 | `audioCompandS16` | `0x800A4258` | `0x000DD60A` | `movz $k0,$zero,$t5` | `.word       0x000DD60A                   # movz        $k0, $zero, $t5 # 00000600 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106274 | `audioCompandS16` | `0x800A4264` | `0x000DCC76` | `special_0x36 $t9,$zero,$t5` | `tne         $zero, $t5, 817` |
| funcs_27.c:106280 | `audioCompandS16` | `0x800A4270` | `0x000DC2E9` | `special_0x29 $t8,$zero,$t5` | `.word       0x000DC2E9                   # INVALID     $zero, $t5, -0x3D17 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106284 | `audioCompandS16` | `0x800A4278` | `0x000DBC8E` | `special_0x0E $s7,$zero,$t5` | `.word       0x000DBC8E                   # INVALID     $zero, $t5, -0x4372 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106288 | `audioCompandS16` | `0x800A4280` | `0x000DB637` | `special_0x37 $s6,$zero,$t5` | `.word       0x000DB637                   # INVALID     $zero, $t5, -0x49C9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106295 | `audioCompandS16` | `0x800A428C` | `0x000DACB9` | `special_0x39 $s5,$zero,$t5` | `.word       0x000DACB9                   # INVALID     $zero, $t5, -0x5347 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106299 | `audioCompandS16` | `0x800A4294` | `0x000DA669` | `special_0x29 $s4,$zero,$t5` | `.word       0x000DA669                   # INVALID     $zero, $t5, -0x5997 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106305 | `audioCompandS16` | `0x800A42A0` | `0x000D9CF6` | `special_0x36 $s3,$zero,$t5` | `tne         $zero, $t5, 627` |
| funcs_27.c:106311 | `audioCompandS16` | `0x800A42AC` | `0x000D938A` | `movz $s2,$zero,$t5` | `.word       0x000D938A                   # movz        $s2, $zero, $t5 # 00000380 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106315 | `audioCompandS16` | `0x800A42B4` | `0x000D8D45` | `special_0x05 $s1,$zero,$t5` | `.word       0x000D8D45                   # INVALID     $zero, $t5, -0x72BB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106327 | `audioCompandS16` | `0x800A42CC` | `0x000D7A89` | `jalr $t7,$zero,$t5` | `.word       0x000D7A89                   # jalr        $t7, $zero # 000D0280 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106331 | `audioCompandS16` | `0x800A42D4` | `0x000D744F` | `special_0x0F $t6,$zero,$t5` | `.word       0x000D744F                   # sync # 000D7440 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106333 | `audioCompandS16` | `0x800A42D8` | `0x000D7134` | `special_0x34 $t6,$zero,$t5` | `teq         $zero, $t5, 452` |
| funcs_27.c:106341 | `audioCompandS16` | `0x800A42E8` | `0x000D64CD` | `break $t4,$zero,$t5` | `break       13, 403` |
| funcs_27.c:106343 | `audioCompandS16` | `0x800A42EC` | `0x000D61B6` | `special_0x36 $t4,$zero,$t5` | `tne         $zero, $t5, 390` |
| funcs_27.c:106348 | `audioCompandS16` | `0x800A42F8` | `0x000D5872` | `special_0x32 $t3,$zero,$t5` | `tlt         $zero, $t5, 353` |
| funcs_27.c:106352 | `audioCompandS16` | `0x800A42F8` | `0x000D5872` | `special_0x32 $t3,$zero,$t5` | `tlt         $zero, $t5, 353` |
| funcs_27.c:106357 | `audioCompandS16` | `0x800A4300` | `0x000D5249` | `jalr $t2,$zero,$t5` | `.word       0x000D5249                   # jalr        $t2, $zero # 000D0240 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106359 | `audioCompandS16` | `0x800A4304` | `0x000D4F35` | `special_0x35 $t1,$zero,$t5` | `.word       0x000D4F35                   # INVALID     $zero, $t5, 0x4F35 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106371 | `audioCompandS16` | `0x800A431C` | `0x000D3CCF` | `special_0x0F $a3,$zero,$t5` | `.word       0x000D3CCF                   # sync # 000D3CC0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106375 | `audioCompandS16` | `0x800A4324` | `0x000D36B2` | `special_0x32 $a2,$zero,$t5` | `tlt         $zero, $t5, 218` |
| funcs_27.c:106381 | `audioCompandS16` | `0x800A4330` | `0x000D2D8D` | `break $a1,$zero,$t5` | `break       13, 182` |
| funcs_27.c:106385 | `audioCompandS16` | `0x800A4338` | `0x000D2777` | `special_0x37 $a0,$zero,$t5` | `.word       0x000D2777                   # INVALID     $zero, $t5, 0x2777 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106393 | `audioCompandS16` | `0x800A4348` | `0x000D1B55` | `special_0x15 $v1,$zero,$t5` | `.word       0x000D1B55                   # INVALID     $zero, $t5, 0x1B55 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106395 | `audioCompandS16` | `0x800A434C` | `0x000D184E` | `special_0x0E $v1,$zero,$t5` | `.word       0x000D184E                   # INVALID     $zero, $t5, 0x184E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106401 | `audioCompandS16` | `0x800A4358` | `0x000D0F3D` | `special_0x3D $at,$zero,$t5` | `.word       0x000D0F3D                   # INVALID     $zero, $t5, 0xF3D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106403 | `audioCompandS16` | `0x800A435C` | `0x000D0C39` | `special_0x39 $at,$zero,$t5` | `.word       0x000D0C39                   # INVALID     $zero, $t5, 0xC39 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106405 | `audioCompandS16` | `0x800A4360` | `0x000D0936` | `special_0x36 $at,$zero,$t5` | `tne         $zero, $t5, 36` |
| funcs_27.c:106407 | `audioCompandS16` | `0x800A4364` | `0x000D0633` | `special_0x33 $zero,$zero,$t5` | `tltu        $zero, $t5, 24` |
| funcs_27.c:106409 | `audioCompandS16` | `0x800A4368` | `0x000D0331` | `special_0x31 $zero,$zero,$t5` | `tgeu        $zero, $t5, 12` |
| funcs_27.c:106411 | `audioCompandS16` | `0x800A436C` | `0x000D0030` | `special_0x30 $zero,$zero,$t5` | `tge         $zero, $t5, 0` |
| funcs_27.c:106417 | `audioCompandS16` | `0x800A4378` | `0x000CF730` | `special_0x30 $fp,$zero,$t4` | `tge         $zero, $t4, 988` |
| funcs_27.c:106419 | `audioCompandS16` | `0x800A437C` | `0x000CF431` | `special_0x31 $fp,$zero,$t4` | `tgeu        $zero, $t4, 976` |
| funcs_27.c:106421 | `audioCompandS16` | `0x800A4380` | `0x000CF133` | `special_0x33 $fp,$zero,$t4` | `tltu        $zero, $t4, 964` |
| funcs_27.c:106423 | `audioCompandS16` | `0x800A4384` | `0x000CEE36` | `special_0x36 $sp,$zero,$t4` | `tne         $zero, $t4, 952` |
| funcs_27.c:106432 | `audioCompandS16` | `0x800A4398` | `0x000CDF4F` | `special_0x0F $k1,$zero,$t4` | `.word       0x000CDF4F                   # sync # 000CDF40 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106436 | `audioCompandS16` | `0x800A4398` | `0x000CDF4F` | `special_0x0F $k1,$zero,$t4` | `.word       0x000CDF4F                   # sync # 000CDF40 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106438 | `audioCompandS16` | `0x800A439C` | `0x000CDC55` | `special_0x15 $k1,$zero,$t4` | `.word       0x000CDC55                   # INVALID     $zero, $t4, -0x23AB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106450 | `audioCompandS16` | `0x800A43B4` | `0x000CCA8E` | `special_0x0E $t9,$zero,$t4` | `.word       0x000CCA8E                   # INVALID     $zero, $t4, -0x3572 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106456 | `audioCompandS16` | `0x800A43C0` | `0x000CC1B3` | `special_0x33 $t8,$zero,$t4` | `tltu        $zero, $t4, 774` |
| funcs_27.c:106458 | `audioCompandS16` | `0x800A43C4` | `0x000CBEC1` | `special_0x01 $s7,$zero,$t4` | `.word       0x000CBEC1                   # INVALID     $zero, $t4, -0x413F # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106460 | `audioCompandS16` | `0x800A43C8` | `0x000CBBCF` | `special_0x0F $s7,$zero,$t4` | `.word       0x000CBBCF                   # sync # 000CBBC0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106472 | `audioCompandS16` | `0x800A43E0` | `0x000CAA34` | `special_0x34 $s5,$zero,$t4` | `teq         $zero, $t4, 680` |
| funcs_27.c:106481 | `audioCompandS16` | `0x800A43EC` | `0x000CA170` | `special_0x30 $s4,$zero,$t4` | `tge         $zero, $t4, 645` |
| funcs_27.c:106483 | `audioCompandS16` | `0x800A43F0` | `0x000C9E85` | `special_0x05 $s3,$zero,$t4` | `.word       0x000C9E85                   # INVALID     $zero, $t4, -0x617B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106487 | `audioCompandS16` | `0x800A43F8` | `0x000C98B2` | `special_0x32 $s3,$zero,$t4` | `tlt         $zero, $t4, 610` |
| funcs_27.c:106489 | `audioCompandS16` | `0x800A43FC` | `0x000C95C9` | `jalr $s2,$zero,$t4` | `.word       0x000C95C9                   # jalr        $s2, $zero # 000C05C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106507 | `audioCompandS16` | `0x800A4420` | `0x000C7BB9` | `special_0x39 $t7,$zero,$t4` | `.word       0x000C7BB9                   # INVALID     $zero, $t4, 0x7BB9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106511 | `audioCompandS16` | `0x800A4428` | `0x000C75F5` | `special_0x35 $t6,$zero,$t4` | `.word       0x000C75F5                   # INVALID     $zero, $t4, 0x75F5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106513 | `audioCompandS16` | `0x800A442C` | `0x000C7315` | `special_0x15 $t6,$zero,$t4` | `.word       0x000C7315                   # INVALID     $zero, $t4, 0x7315 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106515 | `audioCompandS16` | `0x800A4430` | `0x000C7034` | `special_0x34 $t6,$zero,$t4` | `teq         $zero, $t4, 448` |
| funcs_27.c:106517 | `audioCompandS16` | `0x800A4434` | `0x000C6D55` | `special_0x15 $t5,$zero,$t4` | `.word       0x000C6D55                   # INVALID     $zero, $t4, 0x6D55 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106519 | `audioCompandS16` | `0x800A4438` | `0x000C6A76` | `special_0x36 $t5,$zero,$t4` | `tne         $zero, $t4, 425` |
| funcs_27.c:106534 | `audioCompandS16` | `0x800A4454` | `0x000C5672` | `special_0x32 $t2,$zero,$t4` | `tlt         $zero, $t4, 345` |
| funcs_27.c:106540 | `audioCompandS16` | `0x800A4460` | `0x000C4DE8` | `special_0x28 $t1,$zero,$t4` | `.word       0x000C4DE8                   # INVALID     $zero, $t4, 0x4DE8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106544 | `audioCompandS16` | `0x800A4468` | `0x000C4839` | `special_0x39 $t1,$zero,$t4` | `.word       0x000C4839                   # INVALID     $zero, $t4, 0x4839 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106548 | `audioCompandS16` | `0x800A4470` | `0x000C428E` | `special_0x0E $t0,$zero,$t4` | `.word       0x000C428E                   # INVALID     $zero, $t4, 0x428E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106550 | `audioCompandS16` | `0x800A4474` | `0x000C3FB9` | `special_0x39 $a3,$zero,$t4` | `.word       0x000C3FB9                   # INVALID     $zero, $t4, 0x3FB9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106562 | `audioCompandS16` | `0x800A448C` | `0x000C2ECA` | `movz $a1,$zero,$t4` | `.word       0x000C2ECA                   # movz        $a1, $zero, $t4 # 000006C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106564 | `audioCompandS16` | `0x800A4490` | `0x000C2BF9` | `special_0x39 $a1,$zero,$t4` | `.word       0x000C2BF9                   # INVALID     $zero, $t4, 0x2BF9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106575 | `audioCompandS16` | `0x800A44A4` | `0x000C1DF2` | `special_0x32 $v1,$zero,$t4` | `tlt         $zero, $t4, 119` |
| funcs_27.c:106581 | `audioCompandS16` | `0x800A44B0` | `0x000C158F` | `special_0x0F $v0,$zero,$t4` | `.word       0x000C158F                   # sync # 000C1580 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106587 | `audioCompandS16` | `0x800A44BC` | `0x000C0D31` | `special_0x31 $at,$zero,$t4` | `tgeu        $zero, $t4, 52` |
| funcs_27.c:106589 | `audioCompandS16` | `0x800A44C0` | `0x000C0A69` | `special_0x29 $at,$zero,$t4` | `.word       0x000C0A69                   # INVALID     $zero, $t4, 0xA69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106597 | `audioCompandS16` | `0x800A44D0` | `0x000BFF4D` | `break $ra,$zero,$t3` | `break       11, 1021` |
| funcs_27.c:106610 | `audioCompandS16` | `0x800A44E4` | `0x000BF179` | `special_0x39 $fp,$zero,$t3` | `.word       0x000BF179                   # INVALID     $zero, $t3, -0xE87 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106612 | `audioCompandS16` | `0x800A44E8` | `0x000BEEB7` | `special_0x37 $sp,$zero,$t3` | `.word       0x000BEEB7                   # INVALID     $zero, $t3, -0x1149 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106614 | `audioCompandS16` | `0x800A44EC` | `0x000BEBF5` | `special_0x35 $sp,$zero,$t3` | `.word       0x000BEBF5                   # INVALID     $zero, $t3, -0x140B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106616 | `audioCompandS16` | `0x800A44F0` | `0x000BE935` | `special_0x35 $sp,$zero,$t3` | `.word       0x000BE935                   # INVALID     $zero, $t3, -0x16CB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106618 | `audioCompandS16` | `0x800A44F4` | `0x000BE674` | `special_0x34 $gp,$zero,$t3` | `teq         $zero, $t3, 921` |
| funcs_27.c:106620 | `audioCompandS16` | `0x800A44F8` | `0x000BE3B5` | `special_0x35 $gp,$zero,$t3` | `.word       0x000BE3B5                   # INVALID     $zero, $t3, -0x1C4B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106622 | `audioCompandS16` | `0x800A44FC` | `0x000BE0F6` | `special_0x36 $gp,$zero,$t3` | `tne         $zero, $t3, 899` |
| funcs_27.c:106628 | `audioCompandS16` | `0x800A4508` | `0x000BD8BD` | `special_0x3D $k1,$zero,$t3` | `.word       0x000BD8BD                   # INVALID     $zero, $t3, -0x2743 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106632 | `audioCompandS16` | `0x800A4510` | `0x000BD345` | `special_0x05 $k0,$zero,$t3` | `.word       0x000BD345                   # INVALID     $zero, $t3, -0x2CBB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106634 | `audioCompandS16` | `0x800A4514` | `0x000BD08A` | `movz $k0,$zero,$t3` | `.word       0x000BD08A                   # movz        $k0, $zero, $t3 # 00000080 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106636 | `audioCompandS16` | `0x800A4518` | `0x000BCDCF` | `special_0x0F $t9,$zero,$t3` | `.word       0x000BCDCF                   # sync # 000BCDC0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106638 | `audioCompandS16` | `0x800A451C` | `0x000BCB15` | `special_0x15 $t9,$zero,$t3` | `.word       0x000BCB15                   # INVALID     $zero, $t3, -0x34EB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106647 | `audioCompandS16` | `0x800A452C` | `0x000BC034` | `special_0x34 $t8,$zero,$t3` | `teq         $zero, $t3, 768` |
| funcs_27.c:106649 | `audioCompandS16` | `0x800A4530` | `0x000BBD7D` | `special_0x3D $s7,$zero,$t3` | `.word       0x000BBD7D                   # INVALID     $zero, $t3, -0x4283 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106657 | `audioCompandS16` | `0x800A4540` | `0x000BB2A8` | `special_0x28 $s6,$zero,$t3` | `.word       0x000BB2A8                   # INVALID     $zero, $t3, -0x4D58 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106659 | `audioCompandS16` | `0x800A4544` | `0x000BAFF5` | `special_0x35 $s5,$zero,$t3` | `.word       0x000BAFF5                   # INVALID     $zero, $t3, -0x500B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106663 | `audioCompandS16` | `0x800A454C` | `0x000BAA8F` | `special_0x0F $s5,$zero,$t3` | `.word       0x000BAA8F                   # sync # 000BAA80 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106686 | `audioCompandS16` | `0x800A4578` | `0x000B8D0F` | `special_0x0F $s1,$zero,$t3` | `.word       0x000B8D0F                   # sync # 000B8D00 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106690 | `audioCompandS16` | `0x800A4580` | `0x000B87B9` | `special_0x39 $s0,$zero,$t3` | `.word       0x000B87B9                   # INVALID     $zero, $t3, -0x7847 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106709 | `audioCompandS16` | `0x800A45A0` | `0x000B727D` | `special_0x3D $t6,$zero,$t3` | `.word       0x000B727D                   # INVALID     $zero, $t3, 0x727D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106713 | `audioCompandS16` | `0x800A45A8` | `0x000B6D34` | `special_0x34 $t5,$zero,$t3` | `teq         $zero, $t3, 436` |
| funcs_27.c:106719 | `audioCompandS16` | `0x800A45B4` | `0x000B654B` | `movn $t4,$zero,$t3` | `.word       0x000B654B                   # movn        $t4, $zero, $t3 # 00000540 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106721 | `audioCompandS16` | `0x800A45B8` | `0x000B62A9` | `special_0x29 $t4,$zero,$t3` | `.word       0x000B62A9                   # INVALID     $zero, $t3, 0x62A9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106724 | `audioCompandS16` | `0x800A45C0` | `0x000B5D68` | `special_0x28 $t3,$zero,$t3` | `.word       0x000B5D68                   # INVALID     $zero, $t3, 0x5D68 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106728 | `audioCompandS16` | `0x800A45C0` | `0x000B5D68` | `special_0x28 $t3,$zero,$t3` | `.word       0x000B5D68                   # INVALID     $zero, $t3, 0x5D68 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106731 | `audioCompandS16` | `0x800A45C8` | `0x000B5829` | `special_0x29 $t3,$zero,$t3` | `.word       0x000B5829                   # INVALID     $zero, $t3, 0x5829 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106735 | `audioCompandS16` | `0x800A45C8` | `0x000B5829` | `special_0x29 $t3,$zero,$t3` | `.word       0x000B5829                   # INVALID     $zero, $t3, 0x5829 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106737 | `audioCompandS16` | `0x800A45CC` | `0x000B558A` | `movz $t2,$zero,$t3` | `.word       0x000B558A                   # movz        $t2, $zero, $t3 # 00000580 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106741 | `audioCompandS16` | `0x800A45D4` | `0x000B504E` | `special_0x0E $t2,$zero,$t3` | `.word       0x000B504E                   # INVALID     $zero, $t3, 0x504E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106743 | `audioCompandS16` | `0x800A45D8` | `0x000B4DB1` | `special_0x31 $t1,$zero,$t3` | `tgeu        $zero, $t3, 310` |
| funcs_27.c:106745 | `audioCompandS16` | `0x800A45DC` | `0x000B4B15` | `special_0x15 $t1,$zero,$t3` | `.word       0x000B4B15                   # INVALID     $zero, $t3, 0x4B15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106747 | `audioCompandS16` | `0x800A45E0` | `0x000B4879` | `special_0x39 $t1,$zero,$t3` | `.word       0x000B4879                   # INVALID     $zero, $t3, 0x4879 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106762 | `audioCompandS16` | `0x800A4600` | `0x000B33B2` | `special_0x32 $a2,$zero,$t3` | `tlt         $zero, $t3, 206` |
| funcs_27.c:106766 | `audioCompandS16` | `0x800A4600` | `0x000B33B2` | `special_0x32 $a2,$zero,$t3` | `tlt         $zero, $t3, 206` |
| funcs_27.c:106772 | `audioCompandS16` | `0x800A460C` | `0x000B2BF1` | `special_0x31 $a1,$zero,$t3` | `tgeu        $zero, $t3, 175` |
| funcs_27.c:106777 | `audioCompandS16` | `0x800A4618` | `0x000B2435` | `special_0x35 $a0,$zero,$t3` | `.word       0x000B2435                   # INVALID     $zero, $t3, 0x2435 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106781 | `audioCompandS16` | `0x800A4618` | `0x000B2435` | `special_0x35 $a0,$zero,$t3` | `.word       0x000B2435                   # INVALID     $zero, $t3, 0x2435 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106793 | `audioCompandS16` | `0x800A4630` | `0x000B14CE` | `special_0x0E $v0,$zero,$t3` | `.word       0x000B14CE                   # INVALID     $zero, $t3, 0x14CE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106797 | `audioCompandS16` | `0x800A4638` | `0x000B0FB0` | `special_0x30 $at,$zero,$t3` | `tge         $zero, $t3, 62` |
| funcs_27.c:106801 | `audioCompandS16` | `0x800A4640` | `0x000B0A95` | `special_0x15 $at,$zero,$t3` | `.word       0x000B0A95                   # INVALID     $zero, $t3, 0xA95 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106810 | `audioCompandS16` | `0x800A464C` | `0x000B02F0` | `special_0x30 $zero,$zero,$t3` | `tge         $zero, $t3, 11` |
| funcs_27.c:106822 | `audioCompandS16` | `0x800A4664` | `0x000AF3B7` | `special_0x37 $fp,$zero,$t2` | `.word       0x000AF3B7                   # INVALID     $zero, $t2, -0xC49 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106826 | `audioCompandS16` | `0x800A466C` | `0x000AEEA8` | `special_0x28 $sp,$zero,$t2` | `.word       0x000AEEA8                   # INVALID     $zero, $t2, -0x1158 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106836 | `audioCompandS16` | `0x800A4680` | `0x000AE20E` | `special_0x0E $gp,$zero,$t2` | `.word       0x000AE20E                   # INVALID     $zero, $t2, -0x1DF2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106838 | `audioCompandS16` | `0x800A4684` | `0x000ADF8B` | `movn $k1,$zero,$t2` | `.word       0x000ADF8B                   # movn        $k1, $zero, $t2 # 00000780 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106861 | `audioCompandS16` | `0x800A46AC` | `0x000AC689` | `jalr $t8,$zero,$t2` | `.word       0x000AC689                   # jalr        $t8, $zero # 000A0680 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106863 | `audioCompandS16` | `0x800A46B0` | `0x000AC40B` | `movn $t8,$zero,$t2` | `.word       0x000AC40B                   # movn        $t8, $zero, $t2 # 00000400 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106865 | `audioCompandS16` | `0x800A46B4` | `0x000AC18F` | `special_0x0F $t8,$zero,$t2` | `.word       0x000AC18F                   # sync # 000AC180 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106875 | `audioCompandS16` | `0x800A46C8` | `0x000AB529` | `special_0x29 $s6,$zero,$t2` | `.word       0x000AB529                   # INVALID     $zero, $t2, -0x4AD7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106877 | `audioCompandS16` | `0x800A46CC` | `0x000AB2B0` | `special_0x30 $s6,$zero,$t2` | `tge         $zero, $t2, 714` |
| funcs_27.c:106894 | `audioCompandS16` | `0x800A46E8` | `0x000AA171` | `special_0x31 $s4,$zero,$t2` | `tgeu        $zero, $t2, 645` |
| funcs_27.c:106899 | `audioCompandS16` | `0x800A46F4` | `0x000A9A15` | `special_0x15 $s3,$zero,$t2` | `.word       0x000A9A15                   # INVALID     $zero, $t2, -0x65EB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106903 | `audioCompandS16` | `0x800A46F4` | `0x000A9A15` | `special_0x15 $s3,$zero,$t2` | `.word       0x000A9A15                   # INVALID     $zero, $t2, -0x65EB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106907 | `audioCompandS16` | `0x800A46FC` | `0x000A9530` | `special_0x30 $s2,$zero,$t2` | `tge         $zero, $t2, 596` |
| funcs_27.c:106911 | `audioCompandS16` | `0x800A4704` | `0x000A904D` | `break $s2,$zero,$t2` | `break       10, 577` |
| funcs_27.c:106917 | `audioCompandS16` | `0x800A4710` | `0x000A88FD` | `special_0x3D $s1,$zero,$t2` | `.word       0x000A88FD                   # INVALID     $zero, $t2, -0x7703 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106919 | `audioCompandS16` | `0x800A4714` | `0x000A868E` | `special_0x0E $s0,$zero,$t2` | `.word       0x000A868E                   # INVALID     $zero, $t2, -0x7972 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106923 | `audioCompandS16` | `0x800A471C` | `0x000A81B2` | `special_0x32 $s0,$zero,$t2` | `tlt         $zero, $t2, 518` |
| funcs_27.c:106925 | `audioCompandS16` | `0x800A4720` | `0x000A7F45` | `special_0x05 $t7,$zero,$t2` | `.word       0x000A7F45                   # INVALID     $zero, $t2, 0x7F45 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106931 | `audioCompandS16` | `0x800A472C` | `0x000A7801` | `special_0x01 $t7,$zero,$t2` | `.word       0x000A7801                   # INVALID     $zero, $t2, 0x7801 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106937 | `audioCompandS16` | `0x800A4738` | `0x000A70C1` | `special_0x01 $t6,$zero,$t2` | `.word       0x000A70C1                   # INVALID     $zero, $t2, 0x70C1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106941 | `audioCompandS16` | `0x800A4740` | `0x000A6BF0` | `special_0x30 $t5,$zero,$t2` | `tge         $zero, $t2, 431` |
| funcs_27.c:106947 | `audioCompandS16` | `0x800A474C` | `0x000A64B9` | `special_0x39 $t4,$zero,$t2` | `.word       0x000A64B9                   # INVALID     $zero, $t2, 0x64B9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106961 | `audioCompandS16` | `0x800A4768` | `0x000A53F7` | `special_0x37 $t2,$zero,$t2` | `.word       0x000A53F7                   # INVALID     $zero, $t2, 0x53F7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106965 | `audioCompandS16` | `0x800A4770` | `0x000A4F32` | `special_0x32 $t1,$zero,$t2` | `tlt         $zero, $t2, 316` |
| funcs_27.c:106969 | `audioCompandS16` | `0x800A4778` | `0x000A4A70` | `special_0x30 $t1,$zero,$t2` | `tge         $zero, $t2, 297` |
| funcs_27.c:106971 | `audioCompandS16` | `0x800A477C` | `0x000A480F` | `special_0x0F $t1,$zero,$t2` | `.word       0x000A480F                   # sync # 000A4800 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106973 | `audioCompandS16` | `0x800A4780` | `0x000A45B0` | `special_0x30 $t0,$zero,$t2` | `tge         $zero, $t2, 278` |
| funcs_27.c:106977 | `audioCompandS16` | `0x800A4788` | `0x000A40F2` | `special_0x32 $t0,$zero,$t2` | `tlt         $zero, $t2, 259` |
| funcs_27.c:106981 | `audioCompandS16` | `0x800A4790` | `0x000A3C36` | `special_0x36 $a3,$zero,$t2` | `tne         $zero, $t2, 240` |
| funcs_27.c:106991 | `audioCompandS16` | `0x800A47A4` | `0x000A3069` | `special_0x29 $a2,$zero,$t2` | `.word       0x000A3069                   # INVALID     $zero, $t2, 0x3069 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106993 | `audioCompandS16` | `0x800A47A8` | `0x000A2E0F` | `special_0x0F $a1,$zero,$t2` | `.word       0x000A2E0F                   # sync # 000A2E00 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:106995 | `audioCompandS16` | `0x800A47AC` | `0x000A2BB5` | `special_0x35 $a1,$zero,$t2` | `.word       0x000A2BB5                   # INVALID     $zero, $t2, 0x2BB5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107009 | `audioCompandS16` | `0x800A47C8` | `0x000A1B4F` | `special_0x0F $v1,$zero,$t2` | `.word       0x000A1B4F                   # sync # 000A1B40 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107017 | `audioCompandS16` | `0x800A47D8` | `0x000A11FD` | `special_0x3D $v0,$zero,$t2` | `.word       0x000A11FD                   # INVALID     $zero, $t2, 0x11FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107019 | `audioCompandS16` | `0x800A47DC` | `0x000A0FA9` | `special_0x29 $at,$zero,$t2` | `.word       0x000A0FA9                   # INVALID     $zero, $t2, 0xFA9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107025 | `audioCompandS16` | `0x800A47E8` | `0x000A08B2` | `special_0x32 $at,$zero,$t2` | `tlt         $zero, $t2, 34` |
| funcs_27.c:107033 | `audioCompandS16` | `0x800A47F8` | `0x0009FF71` | `special_0x31 $ra,$zero,$t1` | `tgeu        $zero, $t1, 1021` |
| funcs_27.c:107039 | `audioCompandS16` | `0x800A4804` | `0x0009F885` | `special_0x05 $ra,$zero,$t1` | `.word       0x0009F885                   # INVALID     $zero, $t1, -0x77B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107041 | `audioCompandS16` | `0x800A4808` | `0x0009F637` | `special_0x37 $fp,$zero,$t1` | `.word       0x0009F637                   # INVALID     $zero, $t1, -0x9C9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107053 | `audioCompandS16` | `0x800A4820` | `0x0009E872` | `special_0x32 $sp,$zero,$t1` | `tlt         $zero, $t1, 929` |
| funcs_27.c:107055 | `audioCompandS16` | `0x800A4824` | `0x0009E628` | `special_0x28 $gp,$zero,$t1` | `.word       0x0009E628                   # INVALID     $zero, $t1, -0x19D8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107061 | `audioCompandS16` | `0x800A4830` | `0x0009DF4E` | `special_0x0E $k1,$zero,$t1` | `.word       0x0009DF4E                   # INVALID     $zero, $t1, -0x20B2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107069 | `audioCompandS16` | `0x800A4840` | `0x0009D632` | `special_0x32 $k0,$zero,$t1` | `tlt         $zero, $t1, 856` |
| funcs_27.c:107073 | `audioCompandS16` | `0x800A4848` | `0x0009D1A8` | `special_0x28 $k0,$zero,$t1` | `.word       0x0009D1A8                   # INVALID     $zero, $t1, -0x2E58 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107113 | `audioCompandS16` | `0x800A4898` | `0x0009A4B0` | `special_0x30 $s4,$zero,$t1` | `tge         $zero, $t1, 658` |
| funcs_27.c:107115 | `audioCompandS16` | `0x800A489C` | `0x0009A276` | `special_0x36 $s4,$zero,$t1` | `tne         $zero, $t1, 649` |
| funcs_27.c:107117 | `audioCompandS16` | `0x800A48A0` | `0x0009A03D` | `special_0x3D $s4,$zero,$t1` | `.word       0x0009A03D                   # INVALID     $zero, $t1, -0x5FC3 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107121 | `audioCompandS16` | `0x800A48A8` | `0x00099BCB` | `movn $s3,$zero,$t1` | `.word       0x00099BCB                   # movn        $s3, $zero, $t1 # 000003C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107135 | `audioCompandS16` | `0x800A48C4` | `0x00098C4D` | `break $s1,$zero,$t1` | `break       9, 561` |
| funcs_27.c:107141 | `audioCompandS16` | `0x800A48D0` | `0x000985B1` | `special_0x31 $s0,$zero,$t1` | `tgeu        $zero, $t1, 534` |
| funcs_27.c:107150 | `audioCompandS16` | `0x800A48E0` | `0x00097CE8` | `special_0x28 $t7,$zero,$t1` | `.word       0x00097CE8                   # INVALID     $zero, $t1, 0x7CE8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107152 | `audioCompandS16` | `0x800A48E4` | `0x00097AB7` | `special_0x37 $t7,$zero,$t1` | `.word       0x00097AB7                   # INVALID     $zero, $t1, 0x7AB7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107158 | `audioCompandS16` | `0x800A48F0` | `0x00097428` | `special_0x28 $t6,$zero,$t1` | `.word       0x00097428                   # INVALID     $zero, $t1, 0x7428 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107160 | `audioCompandS16` | `0x800A48F4` | `0x000971F9` | `special_0x39 $t6,$zero,$t1` | `.word       0x000971F9                   # INVALID     $zero, $t1, 0x71F9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107162 | `audioCompandS16` | `0x800A48F8` | `0x00096FCA` | `movz $t5,$zero,$t1` | `.word       0x00096FCA                   # movz        $t5, $zero, $t1 # 000007C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107178 | `audioCompandS16` | `0x800A4918` | `0x00095E69` | `special_0x29 $t3,$zero,$t1` | `.word       0x00095E69                   # INVALID     $zero, $t1, 0x5E69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107186 | `audioCompandS16` | `0x800A4928` | `0x000955C5` | `special_0x05 $t2,$zero,$t1` | `.word       0x000955C5                   # INVALID     $zero, $t1, 0x55C5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107190 | `audioCompandS16` | `0x800A4930` | `0x00095175` | `special_0x35 $t2,$zero,$t1` | `.word       0x00095175                   # INVALID     $zero, $t1, 0x5175 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107192 | `audioCompandS16` | `0x800A4934` | `0x00094F4E` | `special_0x0E $t1,$zero,$t1` | `.word       0x00094F4E                   # INVALID     $zero, $t1, 0x4F4E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107194 | `audioCompandS16` | `0x800A4938` | `0x00094D28` | `special_0x28 $t1,$zero,$t1` | `.word       0x00094D28                   # INVALID     $zero, $t1, 0x4D28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107209 | `audioCompandS16` | `0x800A4954` | `0x00093E29` | `special_0x29 $a3,$zero,$t1` | `.word       0x00093E29                   # INVALID     $zero, $t1, 0x3E29 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107219 | `audioCompandS16` | `0x800A4968` | `0x00093381` | `special_0x01 $a2,$zero,$t1` | `.word       0x00093381                   # INVALID     $zero, $t1, 0x3381 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107231 | `audioCompandS16` | `0x800A4980` | `0x000926C9` | `jalr $a0,$zero,$t1` | `.word       0x000926C9                   # jalr        $a0, $zero # 000906C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107235 | `audioCompandS16` | `0x800A4988` | `0x0009228F` | `special_0x0F $a0,$zero,$t1` | `.word       0x0009228F                   # sync # 00092280 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107237 | `audioCompandS16` | `0x800A498C` | `0x00092073` | `special_0x33 $a0,$zero,$t1` | `tltu        $zero, $t1, 129` |
| funcs_27.c:107252 | `audioCompandS16` | `0x800A49A4` | `0x000913D5` | `special_0x15 $v0,$zero,$t1` | `.word       0x000913D5                   # INVALID     $zero, $t1, 0x13D5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107261 | `audioCompandS16` | `0x800A49B4` | `0x00090B75` | `special_0x35 $at,$zero,$t1` | `.word       0x00090B75                   # INVALID     $zero, $t1, 0xB75 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107266 | `audioCompandS16` | `0x800A49C0` | `0x00090532` | `special_0x32 $zero,$zero,$t1` | `tlt         $zero, $t1, 20` |
| funcs_27.c:107270 | `audioCompandS16` | `0x800A49C0` | `0x00090532` | `special_0x32 $zero,$zero,$t1` | `tlt         $zero, $t1, 20` |
| funcs_27.c:107275 | `audioCompandS16` | `0x800A49CC` | `0x0008FEF4` | `special_0x34 $ra,$zero,$t0` | `teq         $zero, $t0, 1019` |
| funcs_27.c:107279 | `audioCompandS16` | `0x800A49CC` | `0x0008FEF4` | `special_0x34 $ra,$zero,$t0` | `teq         $zero, $t0, 1019` |
| funcs_27.c:107283 | `audioCompandS16` | `0x800A49D4` | `0x0008FACD` | `break $ra,$zero,$t0` | `break       8, 1003` |
| funcs_27.c:107289 | `audioCompandS16` | `0x800A49E0` | `0x0008F495` | `special_0x15 $fp,$zero,$t0` | `.word       0x0008F495                   # INVALID     $zero, $t0, -0xB6B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107293 | `audioCompandS16` | `0x800A49E8` | `0x0008F073` | `special_0x33 $fp,$zero,$t0` | `tltu        $zero, $t0, 961` |
| funcs_27.c:107301 | `audioCompandS16` | `0x800A49F8` | `0x0008E834` | `special_0x34 $sp,$zero,$t0` | `teq         $zero, $t0, 928` |
| funcs_27.c:107307 | `audioCompandS16` | `0x800A4A04` | `0x0008E209` | `jalr $gp,$zero,$t0` | `.word       0x0008E209                   # jalr        $gp, $zero # 00080200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107311 | `audioCompandS16` | `0x800A4A0C` | `0x0008DDF0` | `special_0x30 $k1,$zero,$t0` | `tge         $zero, $t0, 887` |
| funcs_27.c:107320 | `audioCompandS16` | `0x800A4A1C` | `0x0008D5C1` | `special_0x01 $k0,$zero,$t0` | `.word       0x0008D5C1                   # INVALID     $zero, $t0, -0x2A3F # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107322 | `audioCompandS16` | `0x800A4A20` | `0x0008D3B7` | `special_0x37 $k0,$zero,$t0` | `.word       0x0008D3B7                   # INVALID     $zero, $t0, -0x2C49 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107333 | `audioCompandS16` | `0x800A4A34` | `0x0008C98B` | `movn $t9,$zero,$t0` | `.word       0x0008C98B                   # movn        $t9, $zero, $t0 # 00000180 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107339 | `audioCompandS16` | `0x800A4A40` | `0x0008C375` | `special_0x35 $t8,$zero,$t0` | `.word       0x0008C375                   # INVALID     $zero, $t0, -0x3C8B # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107358 | `audioCompandS16` | `0x800A4A64` | `0x0008B14F` | `special_0x0F $s6,$zero,$t0` | `.word       0x0008B14F                   # sync # 0008B140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107360 | `audioCompandS16` | `0x800A4A68` | `0x0008AF4D` | `break $s5,$zero,$t0` | `break       8, 701` |
| funcs_27.c:107365 | `audioCompandS16` | `0x800A4A70` | `0x0008AB4B` | `movn $s5,$zero,$t0` | `.word       0x0008AB4B                   # movn        $s5, $zero, $t0 # 00000340 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107367 | `audioCompandS16` | `0x800A4A74` | `0x0008A94A` | `movz $s5,$zero,$t0` | `.word       0x0008A94A                   # movz        $s5, $zero, $t0 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107369 | `audioCompandS16` | `0x800A4A78` | `0x0008A74A` | `movz $s4,$zero,$t0` | `.word       0x0008A74A                   # movz        $s4, $zero, $t0 # 00000740 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107371 | `audioCompandS16` | `0x800A4A7C` | `0x0008A54B` | `movn $s4,$zero,$t0` | `.word       0x0008A54B                   # movn        $s4, $zero, $t0 # 00000540 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107373 | `audioCompandS16` | `0x800A4A80` | `0x0008A34B` | `movn $s4,$zero,$t0` | `.word       0x0008A34B                   # movn        $s4, $zero, $t0 # 00000340 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107375 | `audioCompandS16` | `0x800A4A84` | `0x0008A14D` | `break $s4,$zero,$t0` | `break       8, 645` |
| funcs_27.c:107378 | `audioCompandS16` | `0x800A4A88` | `0x00089F4E` | `special_0x0E $s3,$zero,$t0` | `.word       0x00089F4E                   # INVALID     $zero, $t0, -0x60B2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107392 | `audioCompandS16` | `0x800A4AA4` | `0x00089168` | `special_0x28 $s2,$zero,$t0` | `.word       0x00089168                   # INVALID     $zero, $t0, -0x6E98 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107396 | `audioCompandS16` | `0x800A4AAC` | `0x00088D73` | `special_0x33 $s1,$zero,$t0` | `tltu        $zero, $t0, 565` |
| funcs_27.c:107398 | `audioCompandS16` | `0x800A4AB0` | `0x00088B79` | `special_0x39 $s1,$zero,$t0` | `.word       0x00088B79                   # INVALID     $zero, $t0, -0x7487 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107404 | `audioCompandS16` | `0x800A4ABC` | `0x0008858F` | `special_0x0F $s0,$zero,$t0` | `.word       0x0008858F                   # sync # 00088580 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107410 | `audioCompandS16` | `0x800A4AC8` | `0x00087FA9` | `special_0x29 $t7,$zero,$t0` | `.word       0x00087FA9                   # INVALID     $zero, $t0, 0x7FA9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107412 | `audioCompandS16` | `0x800A4ACC` | `0x00087DB3` | `special_0x33 $t7,$zero,$t0` | `tltu        $zero, $t0, 502` |
| funcs_27.c:107414 | `audioCompandS16` | `0x800A4AD0` | `0x00087BBD` | `special_0x3D $t7,$zero,$t0` | `.word       0x00087BBD                   # INVALID     $zero, $t0, 0x7BBD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107422 | `audioCompandS16` | `0x800A4AE0` | `0x000873E9` | `special_0x29 $t6,$zero,$t0` | `.word       0x000873E9                   # INVALID     $zero, $t0, 0x73E9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107424 | `audioCompandS16` | `0x800A4AE4` | `0x000871F5` | `special_0x35 $t6,$zero,$t0` | `.word       0x000871F5                   # INVALID     $zero, $t0, 0x71F5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107428 | `audioCompandS16` | `0x800A4AEC` | `0x00086E0F` | `special_0x0F $t5,$zero,$t0` | `.word       0x00086E0F                   # sync # 00086E00 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107434 | `audioCompandS16` | `0x800A4AF8` | `0x00086839` | `special_0x39 $t5,$zero,$t0` | `.word       0x00086839                   # INVALID     $zero, $t0, 0x6839 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107443 | `audioCompandS16` | `0x800A4B04` | `0x00086268` | `special_0x28 $t4,$zero,$t0` | `.word       0x00086268                   # INVALID     $zero, $t0, 0x6268 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107447 | `audioCompandS16` | `0x800A4B0C` | `0x00085E89` | `jalr $t3,$zero,$t0` | `.word       0x00085E89                   # jalr        $t3, $zero # 00080680 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107459 | `audioCompandS16` | `0x800A4B24` | `0x000852F7` | `special_0x37 $t2,$zero,$t0` | `.word       0x000852F7                   # INVALID     $zero, $t0, 0x52F7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107461 | `audioCompandS16` | `0x800A4B28` | `0x0008510A` | `movz $t2,$zero,$t0` | `.word       0x0008510A                   # movz        $t2, $zero, $t0 # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107465 | `audioCompandS16` | `0x800A4B30` | `0x00084D33` | `special_0x33 $t1,$zero,$t0` | `tltu        $zero, $t0, 308` |
| funcs_27.c:107467 | `audioCompandS16` | `0x800A4B34` | `0x00084B49` | `jalr $t1,$zero,$t0` | `.word       0x00084B49                   # jalr        $t1, $zero # 00080340 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107472 | `audioCompandS16` | `0x800A4B3C` | `0x00084774` | `special_0x34 $t0,$zero,$t0` | `teq         $zero, $t0, 285` |
| funcs_27.c:107474 | `audioCompandS16` | `0x800A4B40` | `0x0008458B` | `movn $t0,$zero,$t0` | `.word       0x0008458B                   # movn        $t0, $zero, $t0 # 00000580 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107478 | `audioCompandS16` | `0x800A4B48` | `0x000841B9` | `special_0x39 $t0,$zero,$t0` | `.word       0x000841B9                   # INVALID     $zero, $t0, 0x41B9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107482 | `audioCompandS16` | `0x800A4B50` | `0x00083DE9` | `special_0x29 $a3,$zero,$t0` | `.word       0x00083DE9                   # INVALID     $zero, $t0, 0x3DE9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107488 | `audioCompandS16` | `0x800A4B5C` | `0x00083835` | `special_0x35 $a3,$zero,$t0` | `.word       0x00083835                   # INVALID     $zero, $t0, 0x3835 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107490 | `audioCompandS16` | `0x800A4B60` | `0x0008364F` | `special_0x0F $a2,$zero,$t0` | `.word       0x0008364F                   # sync # 00083640 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107492 | `audioCompandS16` | `0x800A4B64` | `0x00083469` | `special_0x29 $a2,$zero,$t0` | `.word       0x00083469                   # INVALID     $zero, $t0, 0x3469 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107502 | `audioCompandS16` | `0x800A4B78` | `0x00082AF5` | `special_0x35 $a1,$zero,$t0` | `.word       0x00082AF5                   # INVALID     $zero, $t0, 0x2AF5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107508 | `audioCompandS16` | `0x800A4B84` | `0x0008254D` | `break $a0,$zero,$t0` | `break       8, 149` |
| funcs_27.c:107512 | `audioCompandS16` | `0x800A4B8C` | `0x0008218B` | `movn $a0,$zero,$t0` | `.word       0x0008218B                   # movn        $a0, $zero, $t0 # 00000180 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107516 | `audioCompandS16` | `0x800A4B94` | `0x00081DC9` | `jalr $v1,$zero,$t0` | `.word       0x00081DC9                   # jalr        $v1, $zero # 000805C0 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107520 | `audioCompandS16` | `0x800A4B9C` | `0x00081A0A` | `movz $v1,$zero,$t0` | `.word       0x00081A0A                   # movz        $v1, $zero, $t0 # 00000200 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107524 | `audioCompandS16` | `0x800A4BA4` | `0x0008164D` | `break $v0,$zero,$t0` | `break       8, 89` |
| funcs_27.c:107530 | `audioCompandS16` | `0x800A4BB0` | `0x000810B4` | `special_0x34 $v0,$zero,$t0` | `teq         $zero, $t0, 66` |
| funcs_27.c:107540 | `audioCompandS16` | `0x800A4BC4` | `0x00080768` | `special_0x28 $zero,$zero,$t0` | `.word       0x00080768                   # INVALID     $zero, $t0, 0x768 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107542 | `audioCompandS16` | `0x800A4BC8` | `0x0008058D` | `break $zero,$zero,$t0` | `break       8, 22` |
| funcs_27.c:107544 | `audioCompandS16` | `0x800A4BCC` | `0x000803B3` | `special_0x33 $zero,$zero,$t0` | `tltu        $zero, $t0, 14` |
| funcs_27.c:107825 | `audioCompandS16` | `0x800A4DE0` | `0x46FFFE00` | `cop1` | `.word       0x46FFFE00                   # INVALID     $s7, $ra, -0x200 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_27.c:107843 | `audioCompandS16` | `0x800A4E00` | `0xF0000F00` | `opcode_0x3C` | `scd         $zero, 0xF00($zero)` |
| funcs_27.c:107845 | `audioCompandS16` | `0x800A4E04` | `0x00F0000F` | `special_0x0F $zero,$a3,$s0` | `.word       0x00F0000F                   # sync # 00F00000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107851 | `audioCompandS16` | `0x800A4E10` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107855 | `audioCompandS16` | `0x800A4E18` | `0x00040005` | `special_0x05 $zero,$zero,$a0` | `.word       0x00040005                   # INVALID     $zero, $a0, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107862 | `audioCompandS16` | `0x800A4E28` | `0x0B396696` | `j` | `j           L_8CE59A58` |
| funcs_27.c:107869 | `audioCompandS16` | `0x800A4E28` | `0x0B396696` | `j` | `j           L_8CE59A58` |
| funcs_27.c:107874 | `audioCompandS16` | `0x800A4E28` | `0x0B396696` | `j` | `j           L_8CE59A58` |
| funcs_27.c:107878 | `audioCompandS16` | `0x800A4E30` | `0x0A446669` | `j` | `j           L_891199A4` |
| funcs_27.c:107882 | `audioCompandS16` | `0x800A4E30` | `0x0A446669` | `j` | `j           L_891199A4` |
| funcs_27.c:107886 | `audioCompandS16` | `0x800A4E38` | `0x095A6626` | `j` | `j           L_85699898` |
| funcs_27.c:107890 | `audioCompandS16` | `0x800A4E38` | `0x095A6626` | `j` | `j           L_85699898` |
| funcs_27.c:107895 | `audioCompandS16` | `0x800A4E40` | `0x087D65CD` | `j` | `j           L_81F59734` |
| funcs_27.c:107899 | `audioCompandS16` | `0x800A4E40` | `0x087D65CD` | `j` | `j           L_81F59734` |
| funcs_27.c:107903 | `audioCompandS16` | `0x800A4E48` | `0x07AB655E` | `regimm` | `tltiu       $sp, 0x655E` |
| funcs_27.c:107907 | `audioCompandS16` | `0x800A4E48` | `0x07AB655E` | `regimm` | `tltiu       $sp, 0x655E` |
| funcs_27.c:107911 | `audioCompandS16` | `0x800A4E50` | `0x06E464D9` | `regimm` | `.word       0x06E464D9                   # INVALID     $s7, $a0, 0x64D9 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:107915 | `audioCompandS16` | `0x800A4E50` | `0x06E464D9` | `regimm` | `.word       0x06E464D9                   # INVALID     $s7, $a0, 0x64D9 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:107919 | `audioCompandS16` | `0x800A4E58` | `0x0628643F` | `regimm` | `tgei        $s1, 0x643F` |
| funcs_27.c:107923 | `audioCompandS16` | `0x800A4E58` | `0x0628643F` | `regimm` | `tgei        $s1, 0x643F` |
| funcs_27.c:107927 | `audioCompandS16` | `0x800A4E60` | `0x0577638F` | `regimm` | `.word       0x0577638F                   # INVALID     $t3, $s7, 0x638F # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:107931 | `audioCompandS16` | `0x800A4E60` | `0x0577638F` | `regimm` | `.word       0x0577638F                   # INVALID     $t3, $s7, 0x638F # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:107939 | `audioCompandS16` | `0x800A4E70` | `0x043561F3` | `regimm` | `.word       0x043561F3                   # INVALID     $at, $s5, 0x61F3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:107952 | `audioCompandS16` | `0x800A4E70` | `0x043561F3` | `regimm` | `.word       0x043561F3                   # INVALID     $at, $s5, 0x61F3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:107961 | `audioCompandS16` | `0x800A4E70` | `0x043561F3` | `regimm` | `.word       0x043561F3                   # INVALID     $at, $s5, 0x61F3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:107966 | `audioCompandS16` | `0x800A4E70` | `0x043561F3` | `regimm` | `.word       0x043561F3                   # INVALID     $at, $s5, 0x61F3 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:107986 | `audioCompandS16` | `0x800A4E88` | `0x029F5EF5` | `special_0x35 $t3,$s4,$ra` | `.word       0x029F5EF5                   # INVALID     $s4, $ra, 0x5EF5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:107990 | `audioCompandS16` | `0x800A4E88` | `0x029F5EF5` | `special_0x35 $t3,$s4,$ra` | `.word       0x029F5EF5                   # INVALID     $s4, $ra, 0x5EF5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:108082 | `audioCompandS16` | `0x800A4F1C` | `0x4060FEAF` | `cop0` | `.word       0x4060FEAF                   # INVALID     $v1, $zero, -0x151 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:108087 | `audioCompandS16` | `0x800A4F24` | `0x424AFEB6` | `cop0` | `.word       0x424AFEB6                   # INVALID     $s2, $t2, -0x14A # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_27.c:108104 | `audioCompandS16` | `0x800A4F3C` | `0x47EDFEDF` | `cop1` | `.word       0x47EDFEDF                   # INVALID     $ra, $t5, -0x121 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_27.c:108110 | `audioCompandS16` | `0x800A4F44` | `0x49C2FEF5` | `opcode_0x12` | `.word       0x49C2FEF5                   # INVALID     $t6, $v0, -0x10B # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_27.c:108115 | `audioCompandS16` | `0x800A4F4C` | `0x4B91FF0F` | `opcode_0x12` | `.word       0x4B91FF0F                   # INVALID     $gp, $s1, -0xF1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_27.c:108120 | `audioCompandS16` | `0x800A4F54` | `0x4D57FF2E` | `opcode_0x13` | `.word       0x4D57FF2E                   # INVALID     $t2, $s7, -0xD2 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:108125 | `audioCompandS16` | `0x800A4F5C` | `0x4F14FF53` | `opcode_0x13` | `.word       0x4F14FF53                   # INVALID     $t8, $s4, -0xAD # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:108353 | `audioCompandS16` | `0x800A5058` | `0x002E0015` | `special_0x15 $zero,$at,$t6` | `.word       0x002E0015                   # INVALID     $at, $t6, 0x15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_27.c:108367 | `audioCompandS16` | `0x800A5074` | `0x0697062E` | `regimm` | `.word       0x0697062E                   # INVALID     $s4, $s7, 0x62E # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:108371 | `audioCompandS16` | `0x800A5074` | `0x0697062E` | `regimm` | `.word       0x0697062E                   # INVALID     $s4, $s7, 0x62E # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:108373 | `audioCompandS16` | `0x800A5078` | `0x05CB056E` | `regimm` | `tltiu       $t6, 0x56E` |
| funcs_27.c:108375 | `audioCompandS16` | `0x800A507C` | `0x051704C6` | `regimm` | `.word       0x051704C6                   # INVALID     $t0, $s7, 0x4C6 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_27.c:108380 | `audioCompandS16` | `0x800A5084` | `0xFA2EFA39` | `opcode_0x3E` | `sdc2        $14, -0x5C7($s1)` |
| funcs_27.c:108382 | `audioCompandS16` | `0x800A5088` | `0xFA83FAE8` | `opcode_0x3E` | `sdc2        $3, -0x518($s4)` |
| funcs_27.c:108384 | `audioCompandS16` | `0x800A508C` | `0xFB54FBBF` | `opcode_0x3E` | `sdc2        $20, -0x441($k0)` |
| funcs_27.c:108386 | `audioCompandS16` | `0x800A5090` | `0x0B600C6C` | `j` | `j           L_8D8031B0` |
| funcs_27.c:108389 | `audioCompandS16` | `0x800A5098` | `0x0ADF09F8` | `j` | `j           L_8B7C27E0` |
| funcs_27.c:108393 | `audioCompandS16` | `0x800A5098` | `0x0ADF09F8` | `j` | `j           L_8B7C27E0` |
| funcs_27.c:108396 | `audioCompandS16` | `0x800A509C` | `0x0914083C` | `j` | `j           L_845020F0` |
| funcs_27.c:108398 | `audioCompandS16` | `0x800A50A0` | `0xF880F1B4` | `opcode_0x3E` | `sdc2        $0, -0xE4C($a0)` |
| funcs_27.c:108400 | `audioCompandS16` | `0x800A50A4` | `0xEBC8E6DB` | `opcode_0x3A` | `swc2        $8, -0x1925($fp)` |
| funcs_27.c:108402 | `audioCompandS16` | `0x800A50A8` | `0xE307E058` | `opcode_0x38` | `sc          $a3, -0x1FA8($t8)` |
| funcs_27.c:108426 | `audioCompandS16` | `0x800A50C0` | `0xF900F30A` | `opcode_0x3E` | `sdc2        $0, -0xCF6($t0)` |
| funcs_27.c:108428 | `audioCompandS16` | `0x800A50C4` | `0xEE21EA40` | `opcode_0x3B` | `.word       0xEE21EA40                   # INVALID     $s1, $at, -0x15C0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_27.c:108446 | `audioCompandS16` | `0x800A50E0` | `0xF980F452` | `opcode_0x3E` | `sdc2        $0, -0xBAE($t4)` |
| funcs_27.c:108462 | `audioCompandS16` | `0x800A50E0` | `0xF980F452` | `opcode_0x3E` | `sdc2        $0, -0xBAE($t4)` |
| funcs_27.c:108475 | `audioCompandS16` | `0x800A50E0` | `0xF980F452` | `opcode_0x3E` | `sdc2        $0, -0xBAE($t4)` |
| funcs_27.c:108483 | `audioCompandS16` | `0x800A50E0` | `0xF980F452` | `opcode_0x3E` | `sdc2        $0, -0xBAE($t4)` |
| funcs_27.c:108487 | `audioCompandS16` | `0x800A50E0` | `0xF980F452` | `opcode_0x3E` | `sdc2        $0, -0xBAE($t4)` |
| funcs_27.c:108490 | `audioCompandS16` | `0x800A50E4` | `0xF04CED45` | `opcode_0x3C` | `scd         $t4, -0x12BB($v0)` |
| funcs_27.c:108492 | `audioCompandS16` | `0x800A50E8` | `0xEB1BE9AC` | `opcode_0x3A` | `swc2        $27, -0x1654($t8)` |
| funcs_27.c:108494 | `audioCompandS16` | `0x800A50EC` | `0xE8DBE88E` | `opcode_0x3A` | `swc2        $27, -0x1772($a2)` |
| funcs_27.c:108504 | `audioCompandS16` | `0x800A5100` | `0xF800F000` | `opcode_0x3E` | `sdc2        $0, -0x1000($zero)` |
| funcs_27.c:108520 | `audioCompandS16` | `0x800A5100` | `0xF800F000` | `opcode_0x3E` | `sdc2        $0, -0x1000($zero)` |
| funcs_27.c:108533 | `audioCompandS16` | `0x800A5100` | `0xF800F000` | `opcode_0x3E` | `sdc2        $0, -0x1000($zero)` |
| funcs_27.c:108541 | `audioCompandS16` | `0x800A5100` | `0xF800F000` | `opcode_0x3E` | `sdc2        $0, -0x1000($zero)` |
| funcs_27.c:108545 | `audioCompandS16` | `0x800A5100` | `0xF800F000` | `opcode_0x3E` | `sdc2        $0, -0x1000($zero)` |
| funcs_27.c:108547 | `audioCompandS16` | `0x800A5104` | `0xE800E000` | `opcode_0x3A` | `swc2        $0, -0x2000($zero)` |
| funcs_27.c:108549 | `audioCompandS16` | `0x800A5108` | `0xD800D000` | `opcode_0x36` | `ldc2        $0, -0x3000($zero)` |
| funcs_27.c:108551 | `audioCompandS16` | `0x800A510C` | `0xC800C000` | `opcode_0x32` | `lwc2        $0, -0x4000($zero)` |
| funcs_27.c:108553 | `audioCompandS16` | `0x800A5110` | `0x10001800` | `beq` | `b           L_800AB114` |
| funcs_27.c:108560 | `audioCompandS16` | `0x800A511C` | `0x40004800` | `cop0` | `mfc0        $zero, Count` |
| funcs_28.c:23529 | `npcIncomingMissileUpdate` | `0x800ABDFC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_28.c:23550 | `npcIncomingMissileUpdate` | `0x800ABE14` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_28.c:38167 | `loadBackdropAsset` | `0x800AE08C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_28.c:38188 | `loadBackdropAsset` | `0x800AE0A4` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_28.c:38217 | `loadBackdropAsset` | `0x800AE0D0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_28.c:38238 | `loadBackdropAsset` | `0x800AE0E8` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_28.c:38663 | `loadBackdropAsset` | `0x800AE32C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_28.c:38682 | `loadBackdropAsset` | `0x800AE348` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_28.c:38878 | `loadBackdropAsset` | `0x800AE488` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_28.c:38903 | `loadBackdropAsset` | `0x800AE4AC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_28.c:41032 | `initCinematicSceneAssets` | `0x800AE60C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_28.c:41053 | `initCinematicSceneAssets` | `0x800AE624` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_28.c:41084 | `initCinematicSceneAssets` | `0x800AE654` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_28.c:41105 | `initCinematicSceneAssets` | `0x800AE66C` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_28.c:41324 | `initCinematicSceneAssets` | `0x800AE790` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_28.c:41345 | `initCinematicSceneAssets` | `0x800AE7A8` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_28.c:41366 | `initCinematicSceneAssets` | `0x800AE7C4` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_28.c:41387 | `initCinematicSceneAssets` | `0x800AE7DC` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_30.c:13685 | `buildFormatMessageGlyphBuffer` | `0x800B2770` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:13706 | `buildFormatMessageGlyphBuffer` | `0x800B2788` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_30.c:13729 | `buildFormatMessageGlyphBuffer` | `0x800B27AC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:13750 | `buildFormatMessageGlyphBuffer` | `0x800B27C4` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_30.c:13896 | `buildFormatMessageGlyphBuffer` | `0x800B2880` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:13921 | `buildFormatMessageGlyphBuffer` | `0x800B28A4` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:14589 | `allocFormatTextElement` | `0x800B2C00` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:14610 | `allocFormatTextElement` | `0x800B2C18` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_30.c:14633 | `allocFormatTextElement` | `0x800B2C3C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:14654 | `allocFormatTextElement` | `0x800B2C54` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_30.c:14749 | `allocFormatTextElement` | `0x800B2CCC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:14772 | `allocFormatTextElement` | `0x800B2CEC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:15056 | `loadNamedTextureDescriptor` | `0x800B2E68` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:15077 | `loadNamedTextureDescriptor` | `0x800B2E80` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_30.c:15106 | `loadNamedTextureDescriptor` | `0x800B2EAC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:15127 | `loadNamedTextureDescriptor` | `0x800B2EC4` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_30.c:15552 | `loadNamedTextureDescriptor` | `0x800B3108` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:15571 | `loadNamedTextureDescriptor` | `0x800B3124` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:15767 | `loadNamedTextureDescriptor` | `0x800B3264` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:15792 | `loadNamedTextureDescriptor` | `0x800B3288` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:16053 | `allocTextRenderTarget` | `0x800B33E4` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:16074 | `allocTextRenderTarget` | `0x800B33FC` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_30.c:16101 | `allocTextRenderTarget` | `0x800B3424` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:16122 | `allocTextRenderTarget` | `0x800B343C` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_30.c:16347 | `allocTextRenderTarget` | `0x800B3564` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:16368 | `allocTextRenderTarget` | `0x800B357C` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_30.c:16389 | `allocTextRenderTarget` | `0x800B3598` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:16410 | `allocTextRenderTarget` | `0x800B35B0` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_30.c:19057 | `buildScaledFormatTextElement` | `0x800B3B80` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:19078 | `buildScaledFormatTextElement` | `0x800B3B98` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_30.c:19103 | `buildScaledFormatTextElement` | `0x800B3BBC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_30.c:19124 | `buildScaledFormatTextElement` | `0x800B3BD4` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_35.c:5141 | `parseJfifSOF0Marker` | `0x800C7100` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_35.c:5168 | `parseJfifSOF0Marker` | `0x800C7124` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_35.c:5457 | `parseJfifSOF0Marker` | `0x800C72A8` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_35.c:5478 | `parseJfifSOF0Marker` | `0x800C72C0` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_35.c:5497 | `parseJfifSOF0Marker` | `0x800C72DC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_35.c:5518 | `parseJfifSOF0Marker` | `0x800C72F4` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_35.c:5580 | `parseJfifSOF0Marker` | `0x800C7354` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_35.c:5601 | `parseJfifSOF0Marker` | `0x800C736C` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_35.c:5634 | `parseJfifSOF0Marker` | `0x800C73A0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_35.c:5655 | `parseJfifSOF0Marker` | `0x800C73B8` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_35.c:7604 | `paserJfifSOSMarker` | `0x800C77C0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_35.c:7625 | `paserJfifSOSMarker` | `0x800C77D8` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_35.c:7652 | `paserJfifSOSMarker` | `0x800C7804` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_35.c:7673 | `paserJfifSOSMarker` | `0x800C781C` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_35.c:7705 | `paserJfifSOSMarker` | `0x800C7848` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_35.c:7726 | `paserJfifSOSMarker` | `0x800C7860` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_35.c:7745 | `paserJfifSOSMarker` | `0x800C787C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_35.c:8177 | `randMod` | `0x800C77F8` | `0x00C2001A` | `div $zero,$a2,$v0` | `break       7` |
| funcs_35.c:8198 | `randMod` | `0x800C7810` | `0x3C018000` | `lui` | `break       6` |
| funcs_36.c:3587 | `computeCellGridIndices` | `0x800C8070` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_36.c:3608 | `computeCellGridIndices` | `0x800C8088` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_36.c:3633 | `computeCellGridIndices` | `0x800C80B0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_36.c:3654 | `computeCellGridIndices` | `0x800C80C8` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_36.c:3714 | `computeCellGridIndices` | `0x800C811C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_36.c:3735 | `computeCellGridIndices` | `0x800C8134` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_36.c:3770 | `computeCellGridIndices` | `0x800C816C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_36.c:3791 | `computeCellGridIndices` | `0x800C8184` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_36.c:9213 | `buildDebrisMeshFromCells` | `0x800C901C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_36.c:9234 | `buildDebrisMeshFromCells` | `0x800C9034` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_36.c:9261 | `buildDebrisMeshFromCells` | `0x800C9060` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_36.c:9282 | `buildDebrisMeshFromCells` | `0x800C9078` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_36.c:9742 | `buildDebrisMeshFromCells` | `0x800C9378` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_36.c:9763 | `buildDebrisMeshFromCells` | `0x800C9390` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_36.c:9790 | `buildDebrisMeshFromCells` | `0x800C93BC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_36.c:9811 | `buildDebrisMeshFromCells` | `0x800C93D4` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_37.c:6008 | `compareStatstoMedalInfo` | `0x800CC2E0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_37.c:6164 | `calculateShotAccuracy` | `0x800CC3A4` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_37.c:6216 | `data_gap_800CC3D4` | `0x800CC3E0` | `0x42C80000` | `cop0` | `.word       0x42C80000                   # INVALID     $s6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6224 | `data_gap_800CC3D4` | `0x800CC3F0` | `0xC1D80000` | `opcode_0x30` | `ll          $t8, 0x0($t6)` |
| funcs_37.c:6232 | `data_gap_800CC3D4` | `0x800CC400` | `0x08000000` | `j` | `j           L_80000000` |
| funcs_37.c:6238 | `data_gap_800CC3D4` | `0x800CC40C` | `0x00080301` | `special_0x01 $zero,$zero,$t0` | `.word       0x00080301                   # INVALID     $zero, $t0, 0x301 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6242 | `data_gap_800CC3D4` | `0x800CC40C` | `0x00080301` | `special_0x01 $zero,$zero,$t0` | `.word       0x00080301                   # INVALID     $zero, $t0, 0x301 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6244 | `data_gap_800CC3D4` | `0x800CC410` | `0x05040206` | `regimm` | `.word       0x05040206                   # INVALID     $t0, $a0, 0x206 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_37.c:6301 | `data_gap_800CC3D4` | `0x800CC478` | `0x05DC0000` | `regimm` | `.word       0x05DC0000                   # INVALID     $t6, $gp, 0x0 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_37.c:6307 | `data_gap_800CC3D4` | `0x800CC484` | `0x7A000000` | `opcode_0x1E` | `.word       0x7A000000                   # INVALID     $s0, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_37.c:6333 | `data_gap_800CC3D4` | `0x800CC4B8` | `0x00750076` | `special_0x36 $zero,$v1,$s5` | `tne         $v1, $s5, 1` |
| funcs_37.c:6353 | `data_gap_800CC3D4` | `0x800CC4DC` | `0x00780079` | `special_0x39 $zero,$v1,$t8` | `.word       0x00780079                   # INVALID     $v1, $t8, 0x79 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6395 | `data_gap_800CC3D4` | `0x800CC524` | `0x03010509` | `jalr $zero,$t8,$at` | `.word       0x03010509                   # jalr        $zero, $t8 # 00010500 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6397 | `data_gap_800CC3D4` | `0x800CC528` | `0x08000000` | `j` | `j           L_80000000` |
| funcs_37.c:6399 | `data_gap_800CC3D4` | `0x800CC52C` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6403 | `data_gap_800CC3D4` | `0x800CC534` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6405 | `data_gap_800CC3D4` | `0x800CC538` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_37.c:6409 | `data_gap_800CC3D4` | `0x800CC540` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_37.c:6411 | `data_gap_800CC3D4` | `0x800CC544` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_37.c:6415 | `data_gap_800CC3D4` | `0x800CC54C` | `0x40D00000` | `cop0` | `ctc0        $s0, Index` |
| funcs_37.c:6417 | `data_gap_800CC3D4` | `0x800CC550` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_37.c:6421 | `data_gap_800CC3D4` | `0x800CC558` | `0x41000000` | `cop0` | `bc0f        L_800CC55C` |
| funcs_37.c:6424 | `data_gap_800CC3D4` | `0x800CC55C` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6428 | `data_gap_800CC3D4` | `0x800CC564` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6430 | `data_gap_800CC3D4` | `0x800CC568` | `0x41840000` | `cop0` | `.word       0x41840000                   # INVALID     $t4, $a0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6434 | `data_gap_800CC3D4` | `0x800CC570` | `0x41680000` | `cop0` | `.word       0x41680000                   # INVALID     $t3, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6436 | `data_gap_800CC3D4` | `0x800CC574` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6440 | `data_gap_800CC3D4` | `0x800CC57C` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6442 | `data_gap_800CC3D4` | `0x800CC580` | `0x4099999A` | `cop0` | `.word       0x4099999A                   # mtc0        $t9, WatchHi # 0000019A <InstrIdType: CPU_COP0>` |
| funcs_37.c:6446 | `data_gap_800CC3D4` | `0x800CC588` | `0x40D00000` | `cop0` | `ctc0        $s0, Index` |
| funcs_37.c:6450 | `data_gap_800CC3D4` | `0x800CC590` | `0xE1AF00FF` | `opcode_0x38` | `sc          $t7, 0xFF($t5)` |
| funcs_37.c:6496 | `data_gap_800CC3D4` | `0x800CC5E8` | `0x00010001` | `special_0x01 $zero,$zero,$at` | `.word       0x00010001                   # INVALID     $zero, $at, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6498 | `data_gap_800CC3D4` | `0x800CC5EC` | `0x00010001` | `special_0x01 $zero,$zero,$at` | `.word       0x00010001                   # INVALID     $zero, $at, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6500 | `data_gap_800CC3D4` | `0x800CC5F0` | `0x00010101` | `special_0x01 $zero,$zero,$at` | `.word       0x00010101                   # INVALID     $zero, $at, 0x101 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6502 | `data_gap_800CC3D4` | `0x800CC5F4` | `0x00010001` | `special_0x01 $zero,$zero,$at` | `.word       0x00010001                   # INVALID     $zero, $at, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6506 | `data_gap_800CC3D4` | `0x800CC5FC` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6508 | `data_gap_800CC3D4` | `0x800CC600` | `0x40B9999A` | `cop0` | `.word       0x40B9999A                   # dmtc0       $t9, WatchHi # 0000019A <InstrIdType: CPU_COP0>` |
| funcs_37.c:6510 | `data_gap_800CC3D4` | `0x800CC604` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6512 | `data_gap_800CC3D4` | `0x800CC608` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_37.c:6514 | `data_gap_800CC3D4` | `0x800CC60C` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_37.c:6516 | `data_gap_800CC3D4` | `0x800CC610` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6518 | `data_gap_800CC3D4` | `0x800CC614` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6520 | `data_gap_800CC3D4` | `0x800CC618` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_37.c:6522 | `data_gap_800CC3D4` | `0x800CC61C` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_37.c:6524 | `data_gap_800CC3D4` | `0x800CC620` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_37.c:6526 | `data_gap_800CC3D4` | `0x800CC624` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6528 | `data_gap_800CC3D4` | `0x800CC628` | `0x40C66666` | `cop0` | `.word       0x40C66666                   # ctc0        $a2, Status # 00000666 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6530 | `data_gap_800CC3D4` | `0x800CC62C` | `0x40B00000` | `cop0` | `dmtc0       $s0, Index` |
| funcs_37.c:6532 | `data_gap_800CC3D4` | `0x800CC630` | `0x40F00000` | `cop0` | `.word       0x40F00000                   # INVALID     $a3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6534 | `data_gap_800CC3D4` | `0x800CC634` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6536 | `data_gap_800CC3D4` | `0x800CC638` | `0x41600000` | `cop0` | `.word       0x41600000                   # INVALID     $t3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:6540 | `data_gap_800CC3D4` | `0x800CC640` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_37.c:6544 | `data_gap_800CC3D4` | `0x800CC648` | `0x0000008E` | `special_0x0E $zero,$zero,$zero` | `.word       0x0000008E                   # INVALID     $zero, $zero, 0x8E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6546 | `data_gap_800CC3D4` | `0x800CC64C` | `0x0A0C9005` | `j` | `j           L_88324014` |
| funcs_37.c:6552 | `data_gap_800CC3D4` | `0x800CC658` | `0x00040001` | `special_0x01 $zero,$zero,$a0` | `.word       0x00040001                   # INVALID     $zero, $a0, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6558 | `data_gap_800CC3D4` | `0x800CC664` | `0x10000800` | `beq` | `b           L_800CE668` |
| funcs_37.c:6567 | `data_gap_800CC3D4` | `0x800CC670` | `0x0000008E` | `special_0x0E $zero,$zero,$zero` | `.word       0x0000008E                   # INVALID     $zero, $zero, 0x8E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6569 | `data_gap_800CC3D4` | `0x800CC674` | `0x0A0C9005` | `j` | `j           L_88324014` |
| funcs_37.c:6578 | `data_gap_800CC3D4` | `0x800CC688` | `0x10000800` | `beq` | `b           L_800CE68C` |
| funcs_37.c:6582 | `data_gap_800CC3D4` | `0x800CC688` | `0x10000800` | `beq` | `b           L_800CE68C` |
| funcs_37.c:6590 | `data_gap_800CC3D4` | `0x800CC698` | `0x0000008E` | `special_0x0E $zero,$zero,$zero` | `.word       0x0000008E                   # INVALID     $zero, $zero, 0x8E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6592 | `data_gap_800CC3D4` | `0x800CC69C` | `0x0A0C9005` | `j` | `j           L_88324014` |
| funcs_37.c:6604 | `data_gap_800CC3D4` | `0x800CC6B4` | `0x10001000` | `beq` | `b           L_800D06B8` |
| funcs_37.c:6606 | `data_gap_800CC3D4` | `0x800CC6B8` | `0x10000800` | `beq` | `b           L_800CE6BC` |
| funcs_37.c:6610 | `data_gap_800CC3D4` | `0x800CC6C0` | `0x0000008E` | `special_0x0E $zero,$zero,$zero` | `.word       0x0000008E                   # INVALID     $zero, $zero, 0x8E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6612 | `data_gap_800CC3D4` | `0x800CC6C4` | `0x0A0C9005` | `j` | `j           L_88324014` |
| funcs_37.c:6618 | `data_gap_800CC3D4` | `0x800CC6D0` | `0x00080005` | `special_0x05 $zero,$zero,$t0` | `.word       0x00080005                   # INVALID     $zero, $t0, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6620 | `data_gap_800CC3D4` | `0x800CC6D4` | `0x10000800` | `beq` | `b           L_800CE6D8` |
| funcs_37.c:6622 | `data_gap_800CC3D4` | `0x800CC6D8` | `0x10001000` | `beq` | `b           L_800D06DC` |
| funcs_37.c:6630 | `data_gap_800CC3D4` | `0x800CC6E8` | `0x00C20028` | `special_0x28 $zero,$a2,$v0` | `.word       0x00C20028                   # INVALID     $a2, $v0, 0x28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6634 | `data_gap_800CC3D4` | `0x800CC6F0` | `0xE1AF00FF` | `opcode_0x38` | `sc          $t7, 0xFF($t5)` |
| funcs_37.c:6683 | `data_gap_800CC3D4` | `0x800CC74C` | `0x0000FFF0` | `special_0x30 $ra,$zero,$zero` | `tge         $zero, $zero, 1023` |
| funcs_37.c:6829 | `data_gap_800CC3D4` | `0x800CC854` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6846 | `data_gap_800CC3D4` | `0x800CC874` | `0xEBE1D7FF` | `opcode_0x3A` | `swc2        $1, -0x2801($ra)` |
| funcs_37.c:6851 | `data_gap_800CC3D4` | `0x800CC87C` | `0xE1AF00FF` | `opcode_0x38` | `sc          $t7, 0xFF($t5)` |
| funcs_37.c:6857 | `data_gap_800CC3D4` | `0x800CC884` | `0x7AB2FFFF` | `opcode_0x1E` | `.word       0x7AB2FFFF                   # INVALID     $s5, $s2, -0x1 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_37.c:6861 | `data_gap_800CC3D4` | `0x800CC88C` | `0x4FD926FF` | `opcode_0x13` | `.word       0x4FD926FF                   # INVALID     $fp, $t9, 0x26FF # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_37.c:6865 | `data_gap_800CC3D4` | `0x800CC88C` | `0x4FD926FF` | `opcode_0x13` | `.word       0x4FD926FF                   # INVALID     $fp, $t9, 0x26FF # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_37.c:6890 | `data_gap_800CC3D4` | `0x800CC8B8` | `0x01A701A8` | `special_0x28 $zero,$t5,$a3` | `.word       0x01A701A8                   # INVALID     $t5, $a3, 0x1A8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6901 | `data_gap_800CC3D4` | `0x800CC8CC` | `0x00320032` | `special_0x32 $zero,$at,$s2` | `tlt         $at, $s2, 0` |
| funcs_37.c:6906 | `data_gap_800CC3D4` | `0x800CC8D4` | `0x00C80069` | `special_0x29 $zero,$a2,$t0` | `.word       0x00C80069                   # INVALID     $a2, $t0, 0x69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6927 | `data_gap_800CC3D4` | `0x800CC8FC` | `0x018C018D` | `break $zero,$t4,$t4` | `break       396, 6` |
| funcs_37.c:6929 | `data_gap_800CC3D4` | `0x800CC900` | `0x018E018F` | `special_0x0F $zero,$t4,$t6` | `.word       0x018E018F                   # sync # 018E0180 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6959 | `data_gap_800CC3D4` | `0x800CC938` | `0x0032004B` | `movn $zero,$at,$s2` | `.word       0x0032004B                   # movn        $zero, $at, $s2 # 00000040 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6978 | `data_gap_800CC3D4` | `0x800CC95C` | `0x00320037` | `special_0x37 $zero,$at,$s2` | `.word       0x00320037                   # INVALID     $at, $s2, 0x37 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6993 | `data_gap_800CC3D4` | `0x800CC978` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:6997 | `data_gap_800CC3D4` | `0x800CC980` | `0x00680069` | `special_0x29 $zero,$v1,$t0` | `.word       0x00680069                   # INVALID     $v1, $t0, 0x69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7005 | `data_gap_800CC3D4` | `0x800CC990` | `0x00000005` | `special_0x05 $zero,$zero,$zero` | `.word       0x00000005                   # INVALID     $zero, $zero, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7021 | `data_gap_800CC3D4` | `0x800CC9B0` | `0x00780079` | `special_0x39 $zero,$v1,$t8` | `.word       0x00780079                   # INVALID     $v1, $t8, 0x79 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7027 | `data_gap_800CC3D4` | `0x800CC9BC` | `0x00740075` | `special_0x35 $zero,$v1,$s4` | `.word       0x00740075                   # INVALID     $v1, $s4, 0x75 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7035 | `data_gap_800CC3D4` | `0x800CC9CC` | `0x007C007D` | `special_0x3D $zero,$v1,$gp` | `.word       0x007C007D                   # INVALID     $v1, $gp, 0x7D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7049 | `data_gap_800CC3D4` | `0x800CC9E8` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7053 | `data_gap_800CC3D4` | `0x800CC9F0` | `0x00040005` | `special_0x05 $zero,$zero,$a0` | `.word       0x00040005                   # INVALID     $zero, $a0, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7055 | `data_gap_800CC3D4` | `0x800CC9F4` | `0x00060009` | `jalr $zero,$zero,$a2` | `.word       0x00060009                   # jalr        $zero, $zero # 00060000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7057 | `data_gap_800CC3D4` | `0x800CC9F8` | `0x000A000B` | `movn $zero,$zero,$t2` | `movn        $zero, $zero, $t2` |
| funcs_37.c:7059 | `data_gap_800CC3D4` | `0x800CC9FC` | `0x000C000D` | `break $zero,$zero,$t4` | `break       12` |
| funcs_37.c:7061 | `data_gap_800CC3D4` | `0x800CCA00` | `0x000E000F` | `special_0x0F $zero,$zero,$t6` | `.word       0x000E000F                   # sync # 000E0000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7068 | `data_gap_800CC3D4` | `0x800CCA0C` | `0x00840085` | `special_0x05 $zero,$a0,$a0` | `.word       0x00840085                   # INVALID     $a0, $a0, 0x85 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7072 | `data_gap_800CC3D4` | `0x800CCA14` | `0x00880089` | `jalr $zero,$a0,$t0` | `.word       0x00880089                   # jalr        $zero, $a0 # 00080080 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7076 | `data_gap_800CC3D4` | `0x800CCA1C` | `0x0000008B` | `movn $zero,$zero,$zero` | `.word       0x0000008B                   # movn        $zero, $zero, $zero # 00000080 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7078 | `data_gap_800CC3D4` | `0x800CCA20` | `0x008B008B` | `movn $zero,$a0,$t3` | `.word       0x008B008B                   # movn        $zero, $a0, $t3 # 00000080 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7080 | `data_gap_800CC3D4` | `0x800CCA24` | `0x008C008D` | `break $zero,$a0,$t4` | `break       140, 2` |
| funcs_37.c:7082 | `data_gap_800CC3D4` | `0x800CCA28` | `0x008E008F` | `special_0x0F $zero,$a0,$t6` | `.word       0x008E008F                   # sync # 008E0080 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7090 | `data_gap_800CC3D4` | `0x800CCA38` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7106 | `data_gap_800CC3D4` | `0x800CCA58` | `0x00000005` | `special_0x05 $zero,$zero,$zero` | `.word       0x00000005                   # INVALID     $zero, $zero, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7125 | `data_gap_800CC3D4` | `0x800CCA78` | `0x00000009` | `jalr $zero,$zero,$zero` | `jalr        $zero, $zero` |
| funcs_37.c:7129 | `data_gap_800CC3D4` | `0x800CCA80` | `0x0000000A` | `movz $zero,$zero,$zero` | `movz        $zero, $zero, $zero` |
| funcs_37.c:7132 | `data_gap_800CC3D4` | `0x800CCA88` | `0x0000000B` | `movn $zero,$zero,$zero` | `movn        $zero, $zero, $zero` |
| funcs_37.c:7136 | `data_gap_800CC3D4` | `0x800CCA88` | `0x0000000B` | `movn $zero,$zero,$zero` | `movn        $zero, $zero, $zero` |
| funcs_37.c:7145 | `data_gap_800CC3D4` | `0x800CCA98` | `0x0000000D` | `break $zero,$zero,$zero` | `break       0` |
| funcs_37.c:7147 | `data_gap_800CC3D4` | `0x800CCA9C` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7149 | `data_gap_800CC3D4` | `0x800CCAA0` | `0x43000000` | `cop0` | `.word       0x43000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7151 | `data_gap_800CC3D4` | `0x800CCAA4` | `0x437A0000` | `cop0` | `.word       0x437A0000                   # INVALID     $k1, $k0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7161 | `data_gap_800CC3D4` | `0x800CCAB8` | `0x42C00000` | `cop0` | `.word       0x42C00000                   # INVALID     $s6, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7163 | `data_gap_800CC3D4` | `0x800CCABC` | `0x43960000` | `cop0` | `.word       0x43960000                   # INVALID     $gp, $s6, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7173 | `data_gap_800CC3D4` | `0x800CCAD0` | `0xC3360000` | `opcode_0x30` | `ll          $s6, 0x0($t9)` |
| funcs_37.c:7175 | `data_gap_800CC3D4` | `0x800CCAD4` | `0x43960000` | `cop0` | `.word       0x43960000                   # INVALID     $gp, $s6, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7185 | `data_gap_800CC3D4` | `0x800CCAE8` | `0xC3560000` | `opcode_0x30` | `ll          $s6, 0x0($k0)` |
| funcs_37.c:7187 | `data_gap_800CC3D4` | `0x800CCAEC` | `0x437A0000` | `cop0` | `.word       0x437A0000                   # INVALID     $k1, $k0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7197 | `data_gap_800CC3D4` | `0x800CCB00` | `0xC3560000` | `opcode_0x30` | `ll          $s6, 0x0($k0)` |
| funcs_37.c:7199 | `data_gap_800CC3D4` | `0x800CCB04` | `0x425C0000` | `cop0` | `.word       0x425C0000                   # INVALID     $s2, $gp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7207 | `data_gap_800CC3D4` | `0x800CCB14` | `0xC0180000` | `opcode_0x30` | `ll          $t8, 0x0($zero)` |
| funcs_37.c:7209 | `data_gap_800CC3D4` | `0x800CCB18` | `0xC3560000` | `opcode_0x30` | `ll          $s6, 0x0($k0)` |
| funcs_37.c:7211 | `data_gap_800CC3D4` | `0x800CCB1C` | `0x43110000` | `cop0` | `.word       0x43110000                   # INVALID     $t8, $s1, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7221 | `data_gap_800CC3D4` | `0x800CCB30` | `0xC3560000` | `opcode_0x30` | `ll          $s6, 0x0($k0)` |
| funcs_37.c:7223 | `data_gap_800CC3D4` | `0x800CCB34` | `0x42A00000` | `cop0` | `.word       0x42A00000                   # INVALID     $s5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7233 | `data_gap_800CC3D4` | `0x800CCB48` | `0xC3560000` | `opcode_0x30` | `ll          $s6, 0x0($k0)` |
| funcs_37.c:7235 | `data_gap_800CC3D4` | `0x800CCB4C` | `0x42F00000` | `cop0` | `.word       0x42F00000                   # INVALID     $s7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7245 | `data_gap_800CC3D4` | `0x800CCB60` | `0xC3360000` | `opcode_0x30` | `ll          $s6, 0x0($t9)` |
| funcs_37.c:7255 | `data_gap_800CC3D4` | `0x800CCB74` | `0xC0700000` | `opcode_0x30` | `ll          $s0, 0x0($v1)` |
| funcs_37.c:7257 | `data_gap_800CC3D4` | `0x800CCB78` | `0x42C00000` | `cop0` | `.word       0x42C00000                   # INVALID     $s6, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7267 | `data_gap_800CC3D4` | `0x800CCB8C` | `0xC0700000` | `opcode_0x30` | `ll          $s0, 0x0($v1)` |
| funcs_37.c:7269 | `data_gap_800CC3D4` | `0x800CCB90` | `0x43000000` | `cop0` | `.word       0x43000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7271 | `data_gap_800CC3D4` | `0x800CCB94` | `0x42480000` | `cop0` | `.word       0x42480000                   # INVALID     $s2, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7279 | `data_gap_800CC3D4` | `0x800CCBA4` | `0xC02B851F` | `opcode_0x30` | `ll          $t3, -0x7AE1($at)` |
| funcs_37.c:7281 | `data_gap_800CC3D4` | `0x800CCBA8` | `0x43000000` | `cop0` | `.word       0x43000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7283 | `data_gap_800CC3D4` | `0x800CCBAC` | `0x430C0000` | `cop0` | `.word       0x430C0000                   # INVALID     $t8, $t4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7293 | `data_gap_800CC3D4` | `0x800CCBC0` | `0x43000000` | `cop0` | `.word       0x43000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7295 | `data_gap_800CC3D4` | `0x800CCBC4` | `0x42960000` | `cop0` | `.word       0x42960000                   # INVALID     $s4, $s6, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7303 | `data_gap_800CC3D4` | `0x800CCBD4` | `0xC00404EA` | `opcode_0x30` | `ll          $a0, 0x4EA($zero)` |
| funcs_37.c:7305 | `data_gap_800CC3D4` | `0x800CCBD8` | `0x43000000` | `cop0` | `.word       0x43000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7307 | `data_gap_800CC3D4` | `0x800CCBDC` | `0x42E60000` | `cop0` | `.word       0x42E60000                   # INVALID     $s7, $a2, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:7315 | `data_gap_800CC3D4` | `0x800CCBEC` | `0xC00404EA` | `opcode_0x30` | `ll          $a0, 0x4EA($zero)` |
| funcs_37.c:7429 | `data_gap_800CC3D4` | `0x800CCCD0` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_37.c:7521 | `data_gap_800CC3D4` | `0x800CCD88` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_37.c:7523 | `data_gap_800CC3D4` | `0x800CCD8C` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_37.c:7598 | `data_gap_800CC3D4` | `0x800CCE20` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7610 | `data_gap_800CC3D4` | `0x800CCE38` | `0x00000005` | `special_0x05 $zero,$zero,$zero` | `.word       0x00000005                   # INVALID     $zero, $zero, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7626 | `data_gap_800CC3D4` | `0x800CCE58` | `0x00000009` | `jalr $zero,$zero,$zero` | `jalr        $zero, $zero` |
| funcs_37.c:7647 | `data_gap_800CC3D4` | `0x800CCE80` | `0x0000000D` | `break $zero,$zero,$zero` | `break       0` |
| funcs_37.c:7651 | `data_gap_800CC3D4` | `0x800CCE88` | `0x0000000E` | `special_0x0E $zero,$zero,$zero` | `.word       0x0000000E                   # INVALID     $zero, $zero, 0xE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7655 | `data_gap_800CC3D4` | `0x800CCE90` | `0x0000000F` | `sync $zero,$zero,$zero` | `sync` |
| funcs_37.c:7671 | `data_gap_800CC3D4` | `0x800CCEB0` | `0x00000015` | `special_0x15 $zero,$zero,$zero` | `.word       0x00000015                   # INVALID     $zero, $zero, 0x15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7675 | `data_gap_800CC3D4` | `0x800CCEB8` | `0x00000030` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 0` |
| funcs_37.c:7687 | `data_gap_800CC3D4` | `0x800CCED0` | `0x00000033` | `special_0x33 $zero,$zero,$zero` | `tltu        $zero, $zero, 0` |
| funcs_37.c:7695 | `data_gap_800CC3D4` | `0x800CCEE0` | `0x00000031` | `special_0x31 $zero,$zero,$zero` | `tgeu        $zero, $zero, 0` |
| funcs_37.c:7727 | `data_gap_800CC3D4` | `0x800CCF20` | `0x00000055` | `special_0x15 $zero,$zero,$zero` | `.word       0x00000055                   # INVALID     $zero, $zero, 0x55 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7747 | `data_gap_800CC3D4` | `0x800CCF48` | `0x00000034` | `special_0x34 $zero,$zero,$zero` | `teq         $zero, $zero, 0` |
| funcs_37.c:7751 | `data_gap_800CC3D4` | `0x800CCF50` | `0x0000000B` | `movn $zero,$zero,$zero` | `movn        $zero, $zero, $zero` |
| funcs_37.c:7772 | `data_gap_800CC3D4` | `0x800CCF78` | `0x00000032` | `special_0x32 $zero,$zero,$zero` | `tlt         $zero, $zero, 0` |
| funcs_37.c:7776 | `data_gap_800CC3D4` | `0x800CCF80` | `0x00000029` | `special_0x29 $zero,$zero,$zero` | `.word       0x00000029                   # INVALID     $zero, $zero, 0x29 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7784 | `data_gap_800CC3D4` | `0x800CCF90` | `0x00000034` | `special_0x34 $zero,$zero,$zero` | `teq         $zero, $zero, 0` |
| funcs_37.c:7788 | `data_gap_800CC3D4` | `0x800CCF98` | `0x00000035` | `special_0x35 $zero,$zero,$zero` | `.word       0x00000035                   # INVALID     $zero, $zero, 0x35 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7792 | `data_gap_800CC3D4` | `0x800CCFA0` | `0x00000036` | `special_0x36 $zero,$zero,$zero` | `tne         $zero, $zero, 0` |
| funcs_37.c:7796 | `data_gap_800CC3D4` | `0x800CCFA8` | `0x00000037` | `special_0x37 $zero,$zero,$zero` | `.word       0x00000037                   # INVALID     $zero, $zero, 0x37 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7804 | `data_gap_800CC3D4` | `0x800CCFB8` | `0x00000039` | `special_0x39 $zero,$zero,$zero` | `.word       0x00000039                   # INVALID     $zero, $zero, 0x39 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7858 | `data_gap_800CC3D4` | `0x800CD024` | `0x002C0015` | `special_0x15 $zero,$at,$t4` | `.word       0x002C0015                   # INVALID     $at, $t4, 0x15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7861 | `data_gap_800CC3D4` | `0x800CD028` | `0x0021000F` | `special_0x0F $zero,$at,$at` | `.word       0x0021000F                   # sync # 00210000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7863 | `data_gap_800CC3D4` | `0x800CD02C` | `0x0020000F` | `special_0x0F $zero,$at,$zero` | `.word       0x0020000F                   # sync # 00200000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7865 | `data_gap_800CC3D4` | `0x800CD030` | `0x0019000A` | `movz $zero,$zero,$t9` | `movz        $zero, $zero, $t9` |
| funcs_37.c:7867 | `data_gap_800CC3D4` | `0x800CD034` | `0x0018000A` | `movz $zero,$zero,$t8` | `movz        $zero, $zero, $t8` |
| funcs_37.c:7869 | `data_gap_800CC3D4` | `0x800CD038` | `0x00160009` | `jalr $zero,$zero,$s6` | `.word       0x00160009                   # jalr        $zero, $zero # 00160000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7871 | `data_gap_800CC3D4` | `0x800CD03C` | `0x00150009` | `jalr $zero,$zero,$s5` | `.word       0x00150009                   # jalr        $zero, $zero # 00150000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7877 | `data_gap_800CC3D4` | `0x800CD048` | `0x000C0005` | `special_0x05 $zero,$zero,$t4` | `.word       0x000C0005                   # INVALID     $zero, $t4, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:7879 | `data_gap_800CC3D4` | `0x800CD04C` | `0x000B0005` | `special_0x05 $zero,$zero,$t3` | `.word       0x000B0005                   # INVALID     $zero, $t3, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:8019 | `data_gap_800CC3D4` | `0x800CD13C` | `0x001E000D` | `break $zero,$zero,$fp` | `break       30` |
| funcs_37.c:8025 | `data_gap_800CC3D4` | `0x800CD148` | `0x00010001` | `special_0x01 $zero,$zero,$at` | `.word       0x00010001                   # INVALID     $zero, $at, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:8035 | `data_gap_800CC3D4` | `0x800CD15C` | `0x001A000B` | `movn $zero,$zero,$k0` | `movn        $zero, $zero, $k0` |
| funcs_37.c:8037 | `data_gap_800CC3D4` | `0x800CD160` | `0x001B000B` | `movn $zero,$zero,$k1` | `movn        $zero, $zero, $k1` |
| funcs_37.c:8039 | `data_gap_800CC3D4` | `0x800CD164` | `0x001F000E` | `special_0x0E $zero,$zero,$ra` | `.word       0x001F000E                   # INVALID     $zero, $ra, 0xE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:8242 | `data_gap_800CC3D4` | `0x800CD2D0` | `0x0046120E` | `special_0x0E $v0,$v0,$a2` | `.word       0x0046120E                   # INVALID     $v0, $a2, 0x120E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:8246 | `data_gap_800CC3D4` | `0x800CD2D8` | `0x0000014A` | `movz $zero,$zero,$zero` | `.word       0x0000014A                   # movz        $zero, $zero, $zero # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:8250 | `data_gap_800CC3D4` | `0x800CD2D8` | `0x0000014A` | `movz $zero,$zero,$zero` | `.word       0x0000014A                   # movz        $zero, $zero, $zero # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:8263 | `data_gap_800CC3D4` | `0x800CD2F4` | `0x041A012C` | `regimm` | `.word       0x041A012C                   # INVALID     $zero, $k0, 0x12C # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_37.c:8271 | `data_gap_800CC3D4` | `0x800CD2F4` | `0x041A012C` | `regimm` | `.word       0x041A012C                   # INVALID     $zero, $k0, 0x12C # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_37.c:8277 | `data_gap_800CC3D4` | `0x800CD2F4` | `0x041A012C` | `regimm` | `.word       0x041A012C                   # INVALID     $zero, $k0, 0x12C # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_37.c:8296 | `data_gap_800CC3D4` | `0x800CD318` | `0x014000F0` | `special_0x30 $zero,$t2,$zero` | `tge         $t2, $zero, 3` |
| funcs_37.c:8343 | `data_gap_800CC3D4` | `0x800CD358` | `0x7D0000A0` | `opcode_0x1F` | `.word       0x7D0000A0                   # INVALID     $t0, $zero, 0xA0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_37.c:8369 | `data_gap_800CC3D4` | `0x800CD38C` | `0x7D0000A0` | `opcode_0x1F` | `.word       0x7D0000A0                   # INVALID     $t0, $zero, 0xA0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_37.c:8431 | `data_gap_800CC3D4` | `0x800CD404` | `0x0005070A` | `movz $zero,$zero,$a1` | `.word       0x0005070A                   # movz        $zero, $zero, $a1 # 00000700 <InstrIdType: CPU_SPECIAL>` |
| funcs_37.c:8433 | `data_gap_800CC3D4` | `0x800CD408` | `0x0B110000` | `j` | `j           L_8C440000` |
| funcs_37.c:8445 | `data_gap_800CC3D4` | `0x800CD420` | `0x000000F0` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 3` |
| funcs_37.c:8451 | `data_gap_800CC3D4` | `0x800CD42C` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:8455 | `data_gap_800CC3D4` | `0x800CD434` | `0x42BB8000` | `cop0` | `.word       0x42BB8000                   # INVALID     $s5, $k1, -0x8000 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_37.c:8557 | `data_gap_800CC3D4` | `0x800CD4F8` | `0xEBCD69FF` | `opcode_0x3A` | `swc2        $13, 0x69FF($fp)` |
| funcs_37.c:8559 | `data_gap_800CC3D4` | `0x800CD4FC` | `0x46FA0000` | `cop1` | `.word       0x46FA0000                   # INVALID     $s7, $k0, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_37.c:8561 | `data_gap_800CC3D4` | `0x800CD500` | `0x46FA0000` | `cop1` | `.word       0x46FA0000                   # INVALID     $s7, $k0, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_37.c:8563 | `data_gap_800CC3D4` | `0x800CD504` | `0x46FA0000` | `cop1` | `.word       0x46FA0000                   # INVALID     $s7, $k0, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_39.c:41255 | `data_gap_800EC10C` | `0x800EC10C` | `0x4A652950` | `opcode_0x12` | `.word       0x4A652950                   # INVALID     $s3, $a1, 0x2950 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_4.c:7163 | `renderFlatMeshFaceGroup` | `0x8001181C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_4.c:7184 | `renderFlatMeshFaceGroup` | `0x80011834` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_4.c:8927 | `renderUnlitMeshFaces` | `0x80012018` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_4.c:8948 | `renderUnlitMeshFaces` | `0x80012030` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_4.c:32151 | `data_gap_800186D8` | `0x800186E8` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_4.c:32153 | `data_gap_800186D8` | `0x800186EC` | `0x47800000` | `cop1` | `.word       0x47800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_4.c:32155 | `data_gap_800186D8` | `0x800186F0` | `0x4B800000` | `opcode_0x12` | `.word       0x4B800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_4.c:32163 | `data_gap_800186D8` | `0x80018700` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_4.c:32165 | `data_gap_800186D8` | `0x80018704` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_4.c:32167 | `data_gap_800186D8` | `0x80018708` | `0xC2FA0000` | `opcode_0x30` | `ll          $k0, 0x0($s7)` |
| funcs_4.c:32169 | `data_gap_800186D8` | `0x8001870C` | `0x42FA0000` | `cop0` | `.word       0x42FA0000                   # INVALID     $s7, $k0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_40.c:910 | `data_gap_800EC6EC` | `0x800EC6EC` | `0x4B140BE8` | `opcode_0x12` | `.word       0x4B140BE8                   # INVALID     $t8, $s4, 0xBE8 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_40.c:6520 | `processPendingSoundCueRequest` | `0x800EE254` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_40.c:6541 | `processPendingSoundCueRequest` | `0x800EE26C` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_40.c:7072 | `processPendingSoundCueRequest` | `0x800EE518` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_40.c:7093 | `processPendingSoundCueRequest` | `0x800EE530` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_41.c:6863 | `copyRandomPipeDelimitedField` | `0x800F3190` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_41.c:6884 | `copyRandomPipeDelimitedField` | `0x800F31A8` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_42.c:16831 | `data_gap_800FBE14` | `0x800FBE14` | `0x73742021` | `opcode_0x1C` | `.word       0x73742021                   # INVALID     $k1, $s4, 0x2021 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_42.c:16835 | `data_gap_800FBE14` | `0x800FBE1C` | `0x4C4C0000` | `opcode_0x13` | `.word       0x4C4C0000                   # INVALID     $v0, $t4, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:1903 | `lvj_checkComplexObjectives` | `0x80109680` | `0x0000010F` | `sync $zero,$zero,$zero` | `.word       0x0000010F                   # sync # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:1907 | `lvj_checkComplexObjectives` | `0x80109680` | `0x0000010F` | `sync $zero,$zero,$zero` | `.word       0x0000010F                   # sync # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:1918 | `lvj_checkComplexObjectives` | `0x80109694` | `0x00000115` | `special_0x15 $zero,$zero,$zero` | `.word       0x00000115                   # INVALID     $zero, $zero, 0x115 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:1922 | `lvj_checkComplexObjectives` | `0x8010969C` | `0x000001F7` | `special_0x37 $zero,$zero,$zero` | `.word       0x000001F7                   # INVALID     $zero, $zero, 0x1F7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:1924 | `lvj_checkComplexObjectives` | `0x801096A0` | `0x000001E8` | `special_0x28 $zero,$zero,$zero` | `.word       0x000001E8                   # INVALID     $zero, $zero, 0x1E8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:1977 | `lvj_checkComplexObjectives` | `0x801096F4` | `0x001E000A` | `movz $zero,$zero,$fp` | `movz        $zero, $zero, $fp` |
| funcs_49.c:1991 | `lvj_checkComplexObjectives` | `0x80109710` | `0x00140028` | `special_0x28 $zero,$zero,$s4` | `.word       0x00140028                   # INVALID     $zero, $s4, 0x28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:1997 | `lvj_checkComplexObjectives` | `0x8010971C` | `0x00140028` | `special_0x28 $zero,$zero,$s4` | `.word       0x00140028                   # INVALID     $zero, $s4, 0x28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:2003 | `lvj_checkComplexObjectives` | `0x80109728` | `0x001496A8` | `special_0x28 $s2,$zero,$s4` | `.word       0x001496A8                   # INVALID     $zero, $s4, -0x6958 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:2011 | `lvj_checkComplexObjectives` | `0x80109730` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:2013 | `lvj_checkComplexObjectives` | `0x80109734` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:2015 | `lvj_checkComplexObjectives` | `0x80109738` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2053 | `lvj_checkComplexObjectives` | `0x80109784` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2061 | `lvj_checkComplexObjectives` | `0x80109794` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2069 | `lvj_checkComplexObjectives` | `0x801097A4` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2077 | `lvj_checkComplexObjectives` | `0x801097B4` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2081 | `lvj_checkComplexObjectives` | `0x801097BC` | `0x08000000` | `j` | `j           L_80000000` |
| funcs_49.c:2126 | `lvj_checkComplexObjectives` | `0x80109808` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:2164 | `lvj_checkComplexObjectives` | `0x80109854` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2172 | `lvj_checkComplexObjectives` | `0x80109864` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2185 | `lvj_checkComplexObjectives` | `0x80109874` | `0x001F0005` | `special_0x05 $zero,$zero,$ra` | `.word       0x001F0005                   # INVALID     $zero, $ra, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:2226 | `lvj_checkComplexObjectives` | `0x801098C4` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_49.c:2234 | `lvj_checkComplexObjectives` | `0x801098D4` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_49.c:2280 | `lvj_checkComplexObjectives` | `0x80109928` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:2302 | `lvj_checkComplexObjectives` | `0x80109954` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2310 | `lvj_checkComplexObjectives` | `0x80109964` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2349 | `lvj_checkComplexObjectives` | `0x801099A0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:2351 | `lvj_checkComplexObjectives` | `0x801099A4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:2353 | `lvj_checkComplexObjectives` | `0x801099A8` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2357 | `lvj_checkComplexObjectives` | `0x801099B0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:2359 | `lvj_checkComplexObjectives` | `0x801099B4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:2361 | `lvj_checkComplexObjectives` | `0x801099B8` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2429 | `lvj_checkComplexObjectives` | `0x80109A38` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2456 | `lvj_checkComplexObjectives` | `0x80109A60` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:2460 | `lvj_checkComplexObjectives` | `0x80109A60` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:2462 | `lvj_checkComplexObjectives` | `0x80109A64` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:2464 | `lvj_checkComplexObjectives` | `0x80109A68` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2486 | `lvj_checkComplexObjectives` | `0x80109A94` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2494 | `lvj_checkComplexObjectives` | `0x80109AA4` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:2550 | `lvj_checkComplexObjectives` | `0x80109B08` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2554 | `lvj_checkComplexObjectives` | `0x80109B10` | `0x40700000` | `cop0` | `.word       0x40700000                   # INVALID     $v1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2556 | `lvj_checkComplexObjectives` | `0x80109B14` | `0x10001000` | `beq` | `b           L_8010DB18` |
| funcs_49.c:2562 | `lvj_checkComplexObjectives` | `0x80109B20` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2564 | `lvj_checkComplexObjectives` | `0x80109B24` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_49.c:2566 | `lvj_checkComplexObjectives` | `0x80109B28` | `0x40580000` | `cop0` | `cfc0        $t8, Index` |
| funcs_49.c:2568 | `lvj_checkComplexObjectives` | `0x80109B2C` | `0x10001000` | `beq` | `b           L_8010DB30` |
| funcs_49.c:2574 | `lvj_checkComplexObjectives` | `0x80109B38` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2576 | `lvj_checkComplexObjectives` | `0x80109B3C` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_49.c:2578 | `lvj_checkComplexObjectives` | `0x80109B40` | `0x40B40000` | `cop0` | `dmtc0       $s4, Index` |
| funcs_49.c:2580 | `lvj_checkComplexObjectives` | `0x80109B44` | `0x10001000` | `beq` | `b           L_8010DB48` |
| funcs_49.c:2586 | `lvj_checkComplexObjectives` | `0x80109B50` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2588 | `lvj_checkComplexObjectives` | `0x80109B54` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_49.c:2590 | `lvj_checkComplexObjectives` | `0x80109B58` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_49.c:2592 | `lvj_checkComplexObjectives` | `0x80109B5C` | `0x10001000` | `beq` | `b           L_8010DB60` |
| funcs_49.c:2598 | `lvj_checkComplexObjectives` | `0x80109B68` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2600 | `lvj_checkComplexObjectives` | `0x80109B6C` | `0x40280000` | `cop0` | `dmfc0       $t0, Index` |
| funcs_49.c:2602 | `lvj_checkComplexObjectives` | `0x80109B70` | `0x40640000` | `cop0` | `.word       0x40640000                   # INVALID     $v1, $a0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2604 | `lvj_checkComplexObjectives` | `0x80109B74` | `0x10001000` | `beq` | `b           L_8010DB78` |
| funcs_49.c:2610 | `lvj_checkComplexObjectives` | `0x80109B80` | `0x41900000` | `cop0` | `.word       0x41900000                   # INVALID     $t4, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2614 | `lvj_checkComplexObjectives` | `0x80109B88` | `0x40700000` | `cop0` | `.word       0x40700000                   # INVALID     $v1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2616 | `lvj_checkComplexObjectives` | `0x80109B8C` | `0x10001000` | `beq` | `b           L_8010DB90` |
| funcs_49.c:2622 | `lvj_checkComplexObjectives` | `0x80109B98` | `0x41600000` | `cop0` | `.word       0x41600000                   # INVALID     $t3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2624 | `lvj_checkComplexObjectives` | `0x80109B9C` | `0x40280000` | `cop0` | `dmfc0       $t0, Index` |
| funcs_49.c:2626 | `lvj_checkComplexObjectives` | `0x80109BA0` | `0x40700000` | `cop0` | `.word       0x40700000                   # INVALID     $v1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2634 | `lvj_checkComplexObjectives` | `0x80109BB0` | `0x41600000` | `cop0` | `.word       0x41600000                   # INVALID     $t3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2638 | `lvj_checkComplexObjectives` | `0x80109BB8` | `0x40700000` | `cop0` | `.word       0x40700000                   # INVALID     $v1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2640 | `lvj_checkComplexObjectives` | `0x80109BBC` | `0x10001000` | `beq` | `b           L_8010DBC0` |
| funcs_49.c:2646 | `lvj_checkComplexObjectives` | `0x80109BC8` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2650 | `lvj_checkComplexObjectives` | `0x80109BD0` | `0x40700000` | `cop0` | `.word       0x40700000                   # INVALID     $v1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2652 | `lvj_checkComplexObjectives` | `0x80109BD4` | `0x10001000` | `beq` | `b           L_8010DBD8` |
| funcs_49.c:2658 | `lvj_checkComplexObjectives` | `0x80109BE0` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2662 | `lvj_checkComplexObjectives` | `0x80109BE8` | `0x40700000` | `cop0` | `.word       0x40700000                   # INVALID     $v1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2664 | `lvj_checkComplexObjectives` | `0x80109BEC` | `0x10001000` | `beq` | `b           L_8010DBF0` |
| funcs_49.c:2670 | `lvj_checkComplexObjectives` | `0x80109BF8` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2672 | `lvj_checkComplexObjectives` | `0x80109BFC` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_49.c:2674 | `lvj_checkComplexObjectives` | `0x80109C00` | `0x40580000` | `cop0` | `cfc0        $t8, Index` |
| funcs_49.c:2676 | `lvj_checkComplexObjectives` | `0x80109C04` | `0x10001000` | `beq` | `b           L_8010DC08` |
| funcs_49.c:2682 | `lvj_checkComplexObjectives` | `0x80109C10` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2684 | `lvj_checkComplexObjectives` | `0x80109C14` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_49.c:2686 | `lvj_checkComplexObjectives` | `0x80109C18` | `0x40B40000` | `cop0` | `dmtc0       $s4, Index` |
| funcs_49.c:2688 | `lvj_checkComplexObjectives` | `0x80109C1C` | `0x10001000` | `beq` | `b           L_8010DC20` |
| funcs_49.c:2694 | `lvj_checkComplexObjectives` | `0x80109C28` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2696 | `lvj_checkComplexObjectives` | `0x80109C2C` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_49.c:2698 | `lvj_checkComplexObjectives` | `0x80109C30` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_49.c:2700 | `lvj_checkComplexObjectives` | `0x80109C34` | `0x10001000` | `beq` | `b           L_8010DC38` |
| funcs_49.c:2706 | `lvj_checkComplexObjectives` | `0x80109C40` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2708 | `lvj_checkComplexObjectives` | `0x80109C44` | `0x40280000` | `cop0` | `dmfc0       $t0, Index` |
| funcs_49.c:2710 | `lvj_checkComplexObjectives` | `0x80109C48` | `0x40640000` | `cop0` | `.word       0x40640000                   # INVALID     $v1, $a0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2712 | `lvj_checkComplexObjectives` | `0x80109C4C` | `0x10001000` | `beq` | `b           L_8010DC50` |
| funcs_49.c:2718 | `lvj_checkComplexObjectives` | `0x80109C58` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2722 | `lvj_checkComplexObjectives` | `0x80109C60` | `0x40700000` | `cop0` | `.word       0x40700000                   # INVALID     $v1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2724 | `lvj_checkComplexObjectives` | `0x80109C64` | `0x10001000` | `beq` | `b           L_8010DC68` |
| funcs_49.c:2730 | `lvj_checkComplexObjectives` | `0x80109C70` | `0x41900000` | `cop0` | `.word       0x41900000                   # INVALID     $t4, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2732 | `lvj_checkComplexObjectives` | `0x80109C74` | `0x40280000` | `cop0` | `dmfc0       $t0, Index` |
| funcs_49.c:2734 | `lvj_checkComplexObjectives` | `0x80109C78` | `0x40700000` | `cop0` | `.word       0x40700000                   # INVALID     $v1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2736 | `lvj_checkComplexObjectives` | `0x80109C7C` | `0x10000800` | `beq` | `b           L_8010BC80` |
| funcs_49.c:2742 | `lvj_checkComplexObjectives` | `0x80109C88` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2746 | `lvj_checkComplexObjectives` | `0x80109C90` | `0x40700000` | `cop0` | `.word       0x40700000                   # INVALID     $v1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2748 | `lvj_checkComplexObjectives` | `0x80109C94` | `0x10001000` | `beq` | `b           L_8010DC98` |
| funcs_49.c:2754 | `lvj_checkComplexObjectives` | `0x80109CA0` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2758 | `lvj_checkComplexObjectives` | `0x80109CA8` | `0x40700000` | `cop0` | `.word       0x40700000                   # INVALID     $v1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2760 | `lvj_checkComplexObjectives` | `0x80109CAC` | `0x10001000` | `beq` | `b           L_8010DCB0` |
| funcs_49.c:2790 | `lvj_checkComplexObjectives` | `0x80109CE8` | `0xD1B807FF` | `opcode_0x34` | `lld         $t8, 0x7FF($t5)` |
| funcs_49.c:2792 | `lvj_checkComplexObjectives` | `0x80109CEC` | `0xF32001FF` | `opcode_0x3C` | `scd         $zero, 0x1FF($t9)` |
| funcs_49.c:2806 | `lvj_checkComplexObjectives` | `0x80109D04` | `0x4FD926FF` | `opcode_0x13` | `.word       0x4FD926FF                   # INVALID     $fp, $t9, 0x26FF # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:2815 | `lvj_checkComplexObjectives` | `0x80109D04` | `0x4FD926FF` | `opcode_0x13` | `.word       0x4FD926FF                   # INVALID     $fp, $t9, 0x26FF # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:2821 | `lvj_checkComplexObjectives` | `0x80109D04` | `0x4FD926FF` | `opcode_0x13` | `.word       0x4FD926FF                   # INVALID     $fp, $t9, 0x26FF # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:2824 | `lvj_checkComplexObjectives` | `0x80109D08` | `0x4FD926FF` | `opcode_0x13` | `.word       0x4FD926FF                   # INVALID     $fp, $t9, 0x26FF # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:2829 | `lvj_checkComplexObjectives` | `0x80109D10` | `0x4FD926FF` | `opcode_0x13` | `.word       0x4FD926FF                   # INVALID     $fp, $t9, 0x26FF # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:2837 | `lvj_checkComplexObjectives` | `0x80109D1C` | `0xEA0000FF` | `opcode_0x3A` | `swc2        $0, 0xFF($s0)` |
| funcs_49.c:2842 | `lvj_checkComplexObjectives` | `0x80109D24` | `0xEA0000FF` | `opcode_0x3A` | `swc2        $0, 0xFF($s0)` |
| funcs_49.c:2844 | `lvj_checkComplexObjectives` | `0x80109D28` | `0xEA0000FF` | `opcode_0x3A` | `swc2        $0, 0xFF($s0)` |
| funcs_49.c:2846 | `lvj_checkComplexObjectives` | `0x80109D2C` | `0x43444546` | `cop0` | `.word       0x43444546                   # INVALID     $k0, $a0, 0x4546 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:2848 | `lvj_checkComplexObjectives` | `0x80109D30` | `0x47000000` | `cop1` | `.word       0x47000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_49.c:2850 | `lvj_checkComplexObjectives` | `0x80109D34` | `0x48490000` | `opcode_0x12` | `cfc2        $t1, $0` |
| funcs_49.c:2852 | `lvj_checkComplexObjectives` | `0x80109D38` | `0x4A4B4C4D` | `opcode_0x12` | `.word       0x4A4B4C4D                   # INVALID     $s2, $t3, 0x4C4D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_49.c:2854 | `lvj_checkComplexObjectives` | `0x80109D3C` | `0x4E4F5000` | `opcode_0x13` | `.word       0x4E4F5000                   # INVALID     $s2, $t7, 0x5000 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:2981 | `lvj_checkComplexObjectives` | `0x80109D74` | `0x72737400` | `opcode_0x1C` | `.word       0x72737400                   # INVALID     $s3, $s3, 0x7400 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:2989 | `lvj_checkComplexObjectives` | `0x80109D84` | `0x04FFFFFF` | `regimm` | `.word       0x04FFFFFF                   # INVALID     $a3, $ra, -0x1 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_49.c:2991 | `lvj_checkComplexObjectives` | `0x80109D88` | `0x0506FFFF` | `regimm` | `.word       0x0506FFFF                   # INVALID     $t0, $a2, -0x1 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_49.c:2993 | `lvj_checkComplexObjectives` | `0x80109D8C` | `0x0708090A` | `regimm` | `tgei        $t8, 0x90A` |
| funcs_49.c:2995 | `lvj_checkComplexObjectives` | `0x80109D90` | `0x0B0C0DFF` | `j` | `j           L_8C3037FC` |
| funcs_49.c:3173 | `lvj_checkComplexObjectives` | `0x80109E04` | `0x40410021` | `cop0` | `.word       0x40410021                   # cfc0        $at, Index # 00000021 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3179 | `lvj_checkComplexObjectives` | `0x80109E10` | `0x4021002E` | `cop0` | `.word       0x4021002E                   # dmfc0       $at, Index # 0000002E <InstrIdType: CPU_COP0>` |
| funcs_49.c:3196 | `lvj_checkComplexObjectives` | `0x80109E30` | `0x40050025` | `cop0` | `.word       0x40050025                   # mfc0        $a1, Index # 00000025 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3198 | `lvj_checkComplexObjectives` | `0x80109E34` | `0x00014005` | `special_0x05 $t0,$zero,$at` | `.word       0x00014005                   # INVALID     $zero, $at, 0x4005 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:3202 | `lvj_checkComplexObjectives` | `0x80109E3C` | `0x41050028` | `cop0` | `.word       0x41050028                   # INVALID     $t0, $a1, 0x28 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_49.c:3204 | `lvj_checkComplexObjectives` | `0x80109E40` | `0x00054005` | `special_0x05 $t0,$zero,$a1` | `.word       0x00054005                   # INVALID     $zero, $a1, 0x4005 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:3208 | `lvj_checkComplexObjectives` | `0x80109E48` | `0x4005002B` | `cop0` | `.word       0x4005002B                   # mfc0        $a1, Index # 0000002B <InstrIdType: CPU_COP0>` |
| funcs_49.c:3210 | `lvj_checkComplexObjectives` | `0x80109E4C` | `0x00034005` | `special_0x05 $t0,$zero,$v1` | `.word       0x00034005                   # INVALID     $zero, $v1, 0x4005 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:3234 | `lvj_checkComplexObjectives` | `0x80109E74` | `0x42010033` | `cop0` | `.word       0x42010033                   # INVALID     $s0, $at, 0x33 # 00000000 <InstrIdType: CPU_COP0_TLB>` |
| funcs_49.c:3240 | `lvj_checkComplexObjectives` | `0x80109E80` | `0x48000000` | `opcode_0x12` | `mfc2        $zero, $0` |
| funcs_49.c:3244 | `lvj_checkComplexObjectives` | `0x80109E88` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:3247 | `lvj_checkComplexObjectives` | `0x80109E90` | `0x00004201` | `special_0x01 $t0,$zero,$zero` | `.word       0x00004201                   # INVALID     $zero, $zero, 0x4201 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:3250 | `lvj_checkComplexObjectives` | `0x80109E90` | `0x00004201` | `special_0x01 $t0,$zero,$zero` | `.word       0x00004201                   # INVALID     $zero, $zero, 0x4201 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:3253 | `lvj_checkComplexObjectives` | `0x80109E94` | `0x00340001` | `special_0x01 $zero,$at,$s4` | `.word       0x00340001                   # INVALID     $at, $s4, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:3261 | `lvj_checkComplexObjectives` | `0x80109EA4` | `0x48000001` | `opcode_0x12` | `.word       0x48000001                   # mfc2        $zero, $0 # 00000001 <InstrIdType: CPU_COP2>` |
| funcs_49.c:3267 | `lvj_checkComplexObjectives` | `0x80109EB0` | `0x42010035` | `cop0` | `.word       0x42010035                   # INVALID     $s0, $at, 0x35 # 00000000 <InstrIdType: CPU_COP0_TLB>` |
| funcs_49.c:3273 | `lvj_checkComplexObjectives` | `0x80109EBC` | `0x48000002` | `opcode_0x12` | `.word       0x48000002                   # mfc2        $zero, $0 # 00000002 <InstrIdType: CPU_COP2>` |
| funcs_49.c:3277 | `lvj_checkComplexObjectives` | `0x80109EC4` | `0x00020001` | `special_0x01 $zero,$zero,$v0` | `.word       0x00020001                   # INVALID     $zero, $v0, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:3280 | `lvj_checkComplexObjectives` | `0x80109ECC` | `0x00004109` | `jalr $t0,$zero,$zero` | `.word       0x00004109                   # jalr        $t0, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:3283 | `lvj_checkComplexObjectives` | `0x80109ECC` | `0x00004109` | `jalr $t0,$zero,$zero` | `.word       0x00004109                   # jalr        $t0, $zero # 00000100 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:3288 | `lvj_checkComplexObjectives` | `0x80109ED4` | `0x41090038` | `cop0` | `.word       0x41090038                   # INVALID     $t0, $t1, 0x38 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_49.c:3294 | `lvj_checkComplexObjectives` | `0x80109EE0` | `0x40210039` | `cop0` | `.word       0x40210039                   # dmfc0       $at, Index # 00000039 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3317 | `lvj_checkComplexObjectives` | `0x80109F08` | `0x00004081` | `special_0x01 $t0,$zero,$zero` | `.word       0x00004081                   # INVALID     $zero, $zero, 0x4081 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:3320 | `lvj_checkComplexObjectives` | `0x80109F08` | `0x00004081` | `special_0x01 $t0,$zero,$zero` | `.word       0x00004081                   # INVALID     $zero, $zero, 0x4081 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:3400 | `lvj_checkComplexObjectives` | `0x80109F9C` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:3408 | `lvj_checkComplexObjectives` | `0x80109FAC` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3515 | `lvj_checkComplexObjectives` | `0x8010A00C` | `0x7F949494` | `opcode_0x1F` | `.word       0x7F949494                   # INVALID     $gp, $s4, -0x6B6C # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:3533 | `lvj_checkComplexObjectives` | `0x8010A028` | `0xE9E9E9D4` | `opcode_0x3A` | `swc2        $9, -0x162C($t7)` |
| funcs_49.c:3542 | `lvj_checkComplexObjectives` | `0x8010A038` | `0x7F7F6A6A` | `opcode_0x1F` | `.word       0x7F7F6A6A                   # INVALID     $k1, $ra, 0x6A6A # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:3567 | `lvj_checkComplexObjectives` | `0x8010A058` | `0xE9E9E9E9` | `opcode_0x3A` | `swc2        $9, -0x1617($t7)` |
| funcs_49.c:3569 | `lvj_checkComplexObjectives` | `0x8010A05C` | `0xE9E9BFBF` | `opcode_0x3A` | `swc2        $9, -0x4041($t7)` |
| funcs_49.c:3575 | `lvj_checkComplexObjectives` | `0x8010A068` | `0x7F7F6A6A` | `opcode_0x1F` | `.word       0x7F7F6A6A                   # INVALID     $k1, $ra, 0x6A6A # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:3602 | `lvj_checkComplexObjectives` | `0x8010A094` | `0x40C7AE14` | `cop0` | `.word       0x40C7AE14                   # ctc0        $a3, Reserved21 # 00000614 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3604 | `lvj_checkComplexObjectives` | `0x8010A098` | `0x40FCCCCD` | `cop0` | `.word       0x40FCCCCD                   # INVALID     $a3, $gp, -0x3333 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3610 | `lvj_checkComplexObjectives` | `0x8010A0A4` | `0x4079999A` | `cop0` | `.word       0x4079999A                   # INVALID     $v1, $t9, -0x6666 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3616 | `lvj_checkComplexObjectives` | `0x8010A0B0` | `0x40733333` | `cop0` | `.word       0x40733333                   # INVALID     $v1, $s3, 0x3333 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3622 | `lvj_checkComplexObjectives` | `0x8010A0BC` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_49.c:3628 | `lvj_checkComplexObjectives` | `0x8010A0C8` | `0x401E147B` | `cop0` | `.word       0x401E147B                   # mfc0        $fp, EntryLo0 # 0000047B <InstrIdType: CPU_COP0>` |
| funcs_49.c:3630 | `lvj_checkComplexObjectives` | `0x8010A0CC` | `0x41540000` | `cop0` | `.word       0x41540000                   # INVALID     $t2, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3644 | `lvj_checkComplexObjectives` | `0x8010A0E8` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3650 | `lvj_checkComplexObjectives` | `0x8010A0F4` | `0x40D051EC` | `cop0` | `.word       0x40D051EC                   # ctc0        $s0, EntryHi # 000001EC <InstrIdType: CPU_COP0>` |
| funcs_49.c:3652 | `lvj_checkComplexObjectives` | `0x8010A0F8` | `0x410CCCCD` | `cop0` | `.word       0x410CCCCD                   # INVALID     $t0, $t4, -0x3333 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_49.c:3690 | `lvj_checkComplexObjectives` | `0x8010A144` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3692 | `lvj_checkComplexObjectives` | `0x8010A148` | `0xC2200000` | `opcode_0x30` | `ll          $zero, 0x0($s1)` |
| funcs_49.c:3694 | `lvj_checkComplexObjectives` | `0x8010A14C` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_49.c:3696 | `lvj_checkComplexObjectives` | `0x8010A150` | `0x423C0000` | `cop0` | `.word       0x423C0000                   # INVALID     $s1, $gp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3698 | `lvj_checkComplexObjectives` | `0x8010A154` | `0xC1D80000` | `opcode_0x30` | `ll          $t8, 0x0($t6)` |
| funcs_49.c:3700 | `lvj_checkComplexObjectives` | `0x8010A158` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3702 | `lvj_checkComplexObjectives` | `0x8010A15C` | `0x42700000` | `cop0` | `.word       0x42700000                   # INVALID     $s3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3704 | `lvj_checkComplexObjectives` | `0x8010A160` | `0xC2340000` | `opcode_0x30` | `ll          $s4, 0x0($s1)` |
| funcs_49.c:3706 | `lvj_checkComplexObjectives` | `0x8010A164` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3708 | `lvj_checkComplexObjectives` | `0x8010A168` | `0x42700000` | `cop0` | `.word       0x42700000                   # INVALID     $s3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3710 | `lvj_checkComplexObjectives` | `0x8010A16C` | `0xC1000000` | `opcode_0x30` | `ll          $zero, 0x0($t0)` |
| funcs_49.c:3712 | `lvj_checkComplexObjectives` | `0x8010A170` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3714 | `lvj_checkComplexObjectives` | `0x8010A174` | `0x42480000` | `cop0` | `.word       0x42480000                   # INVALID     $s2, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3716 | `lvj_checkComplexObjectives` | `0x8010A178` | `0xC1C80000` | `opcode_0x30` | `ll          $t0, 0x0($t6)` |
| funcs_49.c:3718 | `lvj_checkComplexObjectives` | `0x8010A17C` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3720 | `lvj_checkComplexObjectives` | `0x8010A180` | `0x426C0000` | `cop0` | `.word       0x426C0000                   # INVALID     $s3, $t4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3722 | `lvj_checkComplexObjectives` | `0x8010A184` | `0xC2340000` | `opcode_0x30` | `ll          $s4, 0x0($s1)` |
| funcs_49.c:3724 | `lvj_checkComplexObjectives` | `0x8010A188` | `0x41000000` | `cop0` | `bc0f        L_8010A18C` |
| funcs_49.c:3727 | `lvj_checkComplexObjectives` | `0x8010A18C` | `0x41C80000` | `cop0` | `.word       0x41C80000                   # INVALID     $t6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3729 | `lvj_checkComplexObjectives` | `0x8010A190` | `0xC1E00000` | `opcode_0x30` | `ll          $zero, 0x0($t7)` |
| funcs_49.c:3731 | `lvj_checkComplexObjectives` | `0x8010A194` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3733 | `lvj_checkComplexObjectives` | `0x8010A198` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3735 | `lvj_checkComplexObjectives` | `0x8010A19C` | `0xC1A00000` | `opcode_0x30` | `ll          $zero, 0x0($t5)` |
| funcs_49.c:3737 | `lvj_checkComplexObjectives` | `0x8010A1A0` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3739 | `lvj_checkComplexObjectives` | `0x8010A1A4` | `0x42700000` | `cop0` | `.word       0x42700000                   # INVALID     $s3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3741 | `lvj_checkComplexObjectives` | `0x8010A1A8` | `0xC2340000` | `opcode_0x30` | `ll          $s4, 0x0($s1)` |
| funcs_49.c:3743 | `lvj_checkComplexObjectives` | `0x8010A1AC` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3763 | `lvj_checkComplexObjectives` | `0x8010A1D4` | `0x421C4000` | `cop0` | `.word       0x421C4000                   # INVALID     $s0, $gp, 0x4000 # 00000000 <InstrIdType: CPU_COP0_TLB>` |
| funcs_49.c:3765 | `lvj_checkComplexObjectives` | `0x8010A1D8` | `0x41DAC000` | `cop0` | `.word       0x41DAC000                   # INVALID     $t6, $k0, -0x4000 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3767 | `lvj_checkComplexObjectives` | `0x8010A1DC` | `0x41DAC000` | `cop0` | `.word       0x41DAC000                   # INVALID     $t6, $k0, -0x4000 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3769 | `lvj_checkComplexObjectives` | `0x8010A1E0` | `0x41DAC000` | `cop0` | `.word       0x41DAC000                   # INVALID     $t6, $k0, -0x4000 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3771 | `lvj_checkComplexObjectives` | `0x8010A1E4` | `0x41FA0000` | `cop0` | `.word       0x41FA0000                   # INVALID     $t7, $k0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3773 | `lvj_checkComplexObjectives` | `0x8010A1E8` | `0x41FA0000` | `cop0` | `.word       0x41FA0000                   # INVALID     $t7, $k0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3775 | `lvj_checkComplexObjectives` | `0x8010A1EC` | `0x420CA000` | `cop0` | `.word       0x420CA000                   # INVALID     $s0, $t4, -0x6000 # 00000000 <InstrIdType: CPU_COP0_TLB>` |
| funcs_49.c:3777 | `lvj_checkComplexObjectives` | `0x8010A1F0` | `0x41DAC000` | `cop0` | `.word       0x41DAC000                   # INVALID     $t6, $k0, -0x4000 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:3779 | `lvj_checkComplexObjectives` | `0x8010A1F4` | `0x420CA000` | `cop0` | `.word       0x420CA000                   # INVALID     $s0, $t4, -0x6000 # 00000000 <InstrIdType: CPU_COP0_TLB>` |
| funcs_49.c:3783 | `lvj_checkComplexObjectives` | `0x8010A1FC` | `0x42BB8000` | `cop0` | `.word       0x42BB8000                   # INVALID     $s5, $k1, -0x8000 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4259 | `lvj_checkComplexObjectives` | `0x8010A5AC` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4261 | `lvj_checkComplexObjectives` | `0x8010A5B0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4263 | `lvj_checkComplexObjectives` | `0x8010A5B4` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:4265 | `lvj_checkComplexObjectives` | `0x8010A5B8` | `0x41900000` | `cop0` | `.word       0x41900000                   # INVALID     $t4, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4267 | `lvj_checkComplexObjectives` | `0x8010A5BC` | `0x41933E0E` | `cop0` | `.word       0x41933E0E                   # INVALID     $t4, $s3, 0x3E0E # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4269 | `lvj_checkComplexObjectives` | `0x8010A5C0` | `0x41A40000` | `cop0` | `.word       0x41A40000                   # INVALID     $t5, $a0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4271 | `lvj_checkComplexObjectives` | `0x8010A5C4` | `0x41980000` | `cop0` | `.word       0x41980000                   # INVALID     $t4, $t8, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4273 | `lvj_checkComplexObjectives` | `0x8010A5C8` | `0x41B00000` | `cop0` | `.word       0x41B00000                   # INVALID     $t5, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4275 | `lvj_checkComplexObjectives` | `0x8010A5CC` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4279 | `lvj_checkComplexObjectives` | `0x8010A5D4` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4283 | `lvj_checkComplexObjectives` | `0x8010A5DC` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4285 | `lvj_checkComplexObjectives` | `0x8010A5E0` | `0xC1A00000` | `opcode_0x30` | `ll          $zero, 0x0($t5)` |
| funcs_49.c:4287 | `lvj_checkComplexObjectives` | `0x8010A5E4` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_49.c:4289 | `lvj_checkComplexObjectives` | `0x8010A5E8` | `0xC0A00000` | `opcode_0x30` | `ll          $zero, 0x0($a1)` |
| funcs_49.c:4291 | `lvj_checkComplexObjectives` | `0x8010A5EC` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4293 | `lvj_checkComplexObjectives` | `0x8010A5F0` | `0xC2340000` | `opcode_0x30` | `ll          $s4, 0x0($s1)` |
| funcs_49.c:4301 | `lvj_checkComplexObjectives` | `0x8010A600` | `0x40ACCCCD` | `cop0` | `.word       0x40ACCCCD                   # dmtc0       $t4, Reserved25 # 000004CD <InstrIdType: CPU_COP0>` |
| funcs_49.c:4309 | `lvj_checkComplexObjectives` | `0x8010A610` | `0x41B00000` | `cop0` | `.word       0x41B00000                   # INVALID     $t5, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4311 | `lvj_checkComplexObjectives` | `0x8010A614` | `0x41B00000` | `cop0` | `.word       0x41B00000                   # INVALID     $t5, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4319 | `lvj_checkComplexObjectives` | `0x8010A624` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_49.c:4321 | `lvj_checkComplexObjectives` | `0x8010A628` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_49.c:4323 | `lvj_checkComplexObjectives` | `0x8010A62C` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_49.c:4341 | `lvj_checkComplexObjectives` | `0x8010A650` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4343 | `lvj_checkComplexObjectives` | `0x8010A654` | `0x00010001` | `special_0x01 $zero,$zero,$at` | `.word       0x00010001                   # INVALID     $zero, $at, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:4345 | `lvj_checkComplexObjectives` | `0x8010A658` | `0x00010001` | `special_0x01 $zero,$zero,$at` | `.word       0x00010001                   # INVALID     $zero, $at, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:4365 | `lvj_checkComplexObjectives` | `0x8010A680` | `0x41000000` | `cop0` | `bc0f        L_8010A684` |
| funcs_49.c:4368 | `lvj_checkComplexObjectives` | `0x8010A684` | `0x41B00000` | `cop0` | `.word       0x41B00000                   # INVALID     $t5, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4370 | `lvj_checkComplexObjectives` | `0x8010A688` | `0x41B00000` | `cop0` | `.word       0x41B00000                   # INVALID     $t5, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4392 | `lvj_checkComplexObjectives` | `0x8010A6B4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4394 | `lvj_checkComplexObjectives` | `0x8010A6B8` | `0x00010001` | `special_0x01 $zero,$zero,$at` | `.word       0x00010001                   # INVALID     $zero, $at, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:4398 | `lvj_checkComplexObjectives` | `0x8010A6C0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4408 | `lvj_checkComplexObjectives` | `0x8010A6D4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4412 | `lvj_checkComplexObjectives` | `0x8010A6DC` | `0x00030001` | `special_0x01 $zero,$zero,$v1` | `.word       0x00030001                   # INVALID     $zero, $v1, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:4446 | `lvj_checkComplexObjectives` | `0x8010A720` | `0x41000000` | `cop0` | `bc0f        L_8010A724` |
| funcs_49.c:4461 | `lvj_checkComplexObjectives` | `0x8010A73C` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4463 | `lvj_checkComplexObjectives` | `0x8010A740` | `0xC1700000` | `opcode_0x30` | `ll          $s0, 0x0($t3)` |
| funcs_49.c:4465 | `lvj_checkComplexObjectives` | `0x8010A744` | `0xC1F00000` | `opcode_0x30` | `ll          $s0, 0x0($t7)` |
| funcs_49.c:4467 | `lvj_checkComplexObjectives` | `0x8010A748` | `0xC1200000` | `opcode_0x30` | `ll          $zero, 0x0($t1)` |
| funcs_49.c:4477 | `lvj_checkComplexObjectives` | `0x8010A75C` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_49.c:4481 | `lvj_checkComplexObjectives` | `0x8010A764` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_49.c:4493 | `lvj_checkComplexObjectives` | `0x8010A77C` | `0xC1B00000` | `opcode_0x30` | `ll          $s0, 0x0($t5)` |
| funcs_49.c:4495 | `lvj_checkComplexObjectives` | `0x8010A780` | `0xC1B00000` | `opcode_0x30` | `ll          $s0, 0x0($t5)` |
| funcs_49.c:4499 | `lvj_checkComplexObjectives` | `0x8010A788` | `0xC1000000` | `opcode_0x30` | `ll          $zero, 0x0($t0)` |
| funcs_49.c:4501 | `lvj_checkComplexObjectives` | `0x8010A78C` | `0x41300000` | `cop0` | `.word       0x41300000                   # INVALID     $t1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4507 | `lvj_checkComplexObjectives` | `0x8010A798` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4511 | `lvj_checkComplexObjectives` | `0x8010A7A0` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_49.c:4523 | `lvj_checkComplexObjectives` | `0x8010A7B8` | `0xC1E00000` | `opcode_0x30` | `ll          $zero, 0x0($t7)` |
| funcs_49.c:4525 | `lvj_checkComplexObjectives` | `0x8010A7BC` | `0xC1E00000` | `opcode_0x30` | `ll          $zero, 0x0($t7)` |
| funcs_49.c:4529 | `lvj_checkComplexObjectives` | `0x8010A7C4` | `0xC1400000` | `opcode_0x30` | `ll          $zero, 0x0($t2)` |
| funcs_49.c:4531 | `lvj_checkComplexObjectives` | `0x8010A7C8` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4541 | `lvj_checkComplexObjectives` | `0x8010A7DC` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_49.c:4553 | `lvj_checkComplexObjectives` | `0x8010A7F4` | `0xC1F00000` | `opcode_0x30` | `ll          $s0, 0x0($t7)` |
| funcs_49.c:4555 | `lvj_checkComplexObjectives` | `0x8010A7F8` | `0xC2340000` | `opcode_0x30` | `ll          $s4, 0x0($s1)` |
| funcs_49.c:4559 | `lvj_checkComplexObjectives` | `0x8010A800` | `0xC1A00000` | `opcode_0x30` | `ll          $zero, 0x0($t5)` |
| funcs_49.c:4561 | `lvj_checkComplexObjectives` | `0x8010A804` | `0x41A00000` | `cop0` | `.word       0x41A00000                   # INVALID     $t5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4567 | `lvj_checkComplexObjectives` | `0x8010A810` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:4569 | `lvj_checkComplexObjectives` | `0x8010A814` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4571 | `lvj_checkComplexObjectives` | `0x8010A818` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4573 | `lvj_checkComplexObjectives` | `0x8010A81C` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_49.c:4621 | `lvj_checkComplexObjectives` | `0x8010A874` | `0x41000000` | `cop0` | `bc0f        L_8010A878` |
| funcs_49.c:4624 | `lvj_checkComplexObjectives` | `0x8010A878` | `0x41600000` | `cop0` | `.word       0x41600000                   # INVALID     $t3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4630 | `lvj_checkComplexObjectives` | `0x8010A880` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4654 | `lvj_checkComplexObjectives` | `0x8010A8B0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4656 | `lvj_checkComplexObjectives` | `0x8010A8B4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4658 | `lvj_checkComplexObjectives` | `0x8010A8B8` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:4664 | `lvj_checkComplexObjectives` | `0x8010A8C4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4666 | `lvj_checkComplexObjectives` | `0x8010A8C8` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4668 | `lvj_checkComplexObjectives` | `0x8010A8CC` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4670 | `lvj_checkComplexObjectives` | `0x8010A8D0` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:4672 | `lvj_checkComplexObjectives` | `0x8010A8D4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4674 | `lvj_checkComplexObjectives` | `0x8010A8D8` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4676 | `lvj_checkComplexObjectives` | `0x8010A8DC` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:4678 | `lvj_checkComplexObjectives` | `0x8010A8E0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4680 | `lvj_checkComplexObjectives` | `0x8010A8E4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4682 | `lvj_checkComplexObjectives` | `0x8010A8E8` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:4684 | `lvj_checkComplexObjectives` | `0x8010A8EC` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4686 | `lvj_checkComplexObjectives` | `0x8010A8F0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4688 | `lvj_checkComplexObjectives` | `0x8010A8F4` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:4690 | `lvj_checkComplexObjectives` | `0x8010A8F8` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4692 | `lvj_checkComplexObjectives` | `0x8010A8FC` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4694 | `lvj_checkComplexObjectives` | `0x8010A900` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:4696 | `lvj_checkComplexObjectives` | `0x8010A904` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4698 | `lvj_checkComplexObjectives` | `0x8010A908` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4700 | `lvj_checkComplexObjectives` | `0x8010A90C` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_49.c:4702 | `lvj_checkComplexObjectives` | `0x8010A910` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4704 | `lvj_checkComplexObjectives` | `0x8010A914` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4706 | `lvj_checkComplexObjectives` | `0x8010A918` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4708 | `lvj_checkComplexObjectives` | `0x8010A91C` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4710 | `lvj_checkComplexObjectives` | `0x8010A920` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4712 | `lvj_checkComplexObjectives` | `0x8010A924` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4714 | `lvj_checkComplexObjectives` | `0x8010A928` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4716 | `lvj_checkComplexObjectives` | `0x8010A92C` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4718 | `lvj_checkComplexObjectives` | `0x8010A930` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:4720 | `lvj_checkComplexObjectives` | `0x8010A934` | `0x41000000` | `cop0` | `bc0f        L_8010A938` |
| funcs_49.c:4747 | `lvj_checkComplexObjectives` | `0x8010A960` | `0x41980000` | `cop0` | `.word       0x41980000                   # INVALID     $t4, $t8, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4759 | `lvj_checkComplexObjectives` | `0x8010A978` | `0x42280000` | `cop0` | `.word       0x42280000                   # INVALID     $s1, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4761 | `lvj_checkComplexObjectives` | `0x8010A97C` | `0x41000000` | `cop0` | `bc0f        L_8010A980` |
| funcs_49.c:4768 | `lvj_checkComplexObjectives` | `0x8010A988` | `0x0000000A` | `movz $zero,$zero,$zero` | `movz        $zero, $zero, $zero` |
| funcs_49.c:4774 | `lvj_checkComplexObjectives` | `0x8010A994` | `0x42280000` | `cop0` | `.word       0x42280000                   # INVALID     $s1, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4776 | `lvj_checkComplexObjectives` | `0x8010A998` | `0x41000000` | `cop0` | `bc0f        L_8010A99C` |
| funcs_49.c:4783 | `lvj_checkComplexObjectives` | `0x8010A9A4` | `0x0000000A` | `movz $zero,$zero,$zero` | `movz        $zero, $zero, $zero` |
| funcs_49.c:4789 | `lvj_checkComplexObjectives` | `0x8010A9B0` | `0x41900000` | `cop0` | `.word       0x41900000                   # INVALID     $t4, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4791 | `lvj_checkComplexObjectives` | `0x8010A9B4` | `0x41000000` | `cop0` | `bc0f        L_8010A9B8` |
| funcs_49.c:4798 | `lvj_checkComplexObjectives` | `0x8010A9C0` | `0x0000000B` | `movn $zero,$zero,$zero` | `movn        $zero, $zero, $zero` |
| funcs_49.c:4806 | `lvj_checkComplexObjectives` | `0x8010A9D0` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4814 | `lvj_checkComplexObjectives` | `0x8010A9E0` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4822 | `lvj_checkComplexObjectives` | `0x8010A9F0` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4830 | `lvj_checkComplexObjectives` | `0x8010AA00` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4842 | `lvj_checkComplexObjectives` | `0x8010AA18` | `0x4102221F` | `cop0` | `bc0fl       L_80113298` |
| funcs_49.c:4852 | `lvj_checkComplexObjectives` | `0x8010AA2C` | `0x43350000` | `cop0` | `.word       0x43350000                   # INVALID     $t9, $s5, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4856 | `lvj_checkComplexObjectives` | `0x8010AA34` | `0xC3350000` | `opcode_0x30` | `ll          $s5, 0x0($t9)` |
| funcs_49.c:4860 | `lvj_checkComplexObjectives` | `0x8010AA3C` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4882 | `lvj_checkComplexObjectives` | `0x8010AA68` | `0x4102221F` | `cop0` | `bc0fl       L_801132E8` |
| funcs_49.c:4892 | `lvj_checkComplexObjectives` | `0x8010AA7C` | `0x43350000` | `cop0` | `.word       0x43350000                   # INVALID     $t9, $s5, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4896 | `lvj_checkComplexObjectives` | `0x8010AA84` | `0xC3350000` | `opcode_0x30` | `ll          $s5, 0x0($t9)` |
| funcs_49.c:4900 | `lvj_checkComplexObjectives` | `0x8010AA8C` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4922 | `lvj_checkComplexObjectives` | `0x8010AAB8` | `0x40F6147B` | `cop0` | `.word       0x40F6147B                   # INVALID     $a3, $s6, 0x147B # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4928 | `lvj_checkComplexObjectives` | `0x8010AAC4` | `0x41428F5C` | `cop0` | `.word       0x41428F5C                   # INVALID     $t2, $v0, -0x70A4 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4932 | `lvj_checkComplexObjectives` | `0x8010AACC` | `0x42C80000` | `cop0` | `.word       0x42C80000                   # INVALID     $s6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4934 | `lvj_checkComplexObjectives` | `0x8010AAD0` | `0x43350000` | `cop0` | `.word       0x43350000                   # INVALID     $t9, $s5, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4936 | `lvj_checkComplexObjectives` | `0x8010AAD4` | `0xC2C80000` | `opcode_0x30` | `ll          $t0, 0x0($s6)` |
| funcs_49.c:4938 | `lvj_checkComplexObjectives` | `0x8010AAD8` | `0xC3350000` | `opcode_0x30` | `ll          $s5, 0x0($t9)` |
| funcs_49.c:4940 | `lvj_checkComplexObjectives` | `0x8010AADC` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4942 | `lvj_checkComplexObjectives` | `0x8010AAE0` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4958 | `lvj_checkComplexObjectives` | `0x8010AB00` | `0x41000000` | `cop0` | `bc0f        L_8010AB04` |
| funcs_49.c:4961 | `lvj_checkComplexObjectives` | `0x8010AB04` | `0x41A00000` | `cop0` | `.word       0x41A00000                   # INVALID     $t5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4969 | `lvj_checkComplexObjectives` | `0x8010AB14` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4973 | `lvj_checkComplexObjectives` | `0x8010AB1C` | `0x41033333` | `cop0` | `bc0tl       L_801177EC` |
| funcs_49.c:4975 | `lvj_checkComplexObjectives` | `0x8010AB20` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_49.c:4981 | `lvj_checkComplexObjectives` | `0x8010AB2C` | `0x0000000B` | `movn $zero,$zero,$zero` | `movn        $zero, $zero, $zero` |
| funcs_49.c:4983 | `lvj_checkComplexObjectives` | `0x8010AB30` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:4987 | `lvj_checkComplexObjectives` | `0x8010AB38` | `0x41033333` | `cop0` | `bc0tl       L_80117808` |
| funcs_49.c:4989 | `lvj_checkComplexObjectives` | `0x8010AB3C` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_49.c:4995 | `lvj_checkComplexObjectives` | `0x8010AB48` | `0x0000000B` | `movn $zero,$zero,$zero` | `movn        $zero, $zero, $zero` |
| funcs_49.c:4997 | `lvj_checkComplexObjectives` | `0x8010AB4C` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5001 | `lvj_checkComplexObjectives` | `0x8010AB54` | `0x41033333` | `cop0` | `bc0tl       L_80117824` |
| funcs_49.c:5003 | `lvj_checkComplexObjectives` | `0x8010AB58` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_49.c:5009 | `lvj_checkComplexObjectives` | `0x8010AB64` | `0x0000000B` | `movn $zero,$zero,$zero` | `movn        $zero, $zero, $zero` |
| funcs_49.c:5011 | `lvj_checkComplexObjectives` | `0x8010AB68` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5015 | `lvj_checkComplexObjectives` | `0x8010AB70` | `0x41033333` | `cop0` | `bc0tl       L_80117840` |
| funcs_49.c:5017 | `lvj_checkComplexObjectives` | `0x8010AB74` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_49.c:5023 | `lvj_checkComplexObjectives` | `0x8010AB80` | `0x0000000B` | `movn $zero,$zero,$zero` | `movn        $zero, $zero, $zero` |
| funcs_49.c:5025 | `lvj_checkComplexObjectives` | `0x8010AB84` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5029 | `lvj_checkComplexObjectives` | `0x8010AB8C` | `0x41033333` | `cop0` | `bc0tl       L_8011785C` |
| funcs_49.c:5031 | `lvj_checkComplexObjectives` | `0x8010AB90` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_49.c:5037 | `lvj_checkComplexObjectives` | `0x8010AB9C` | `0x0000000B` | `movn $zero,$zero,$zero` | `movn        $zero, $zero, $zero` |
| funcs_49.c:5057 | `lvj_checkComplexObjectives` | `0x8010ABC4` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5059 | `lvj_checkComplexObjectives` | `0x8010ABC8` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5061 | `lvj_checkComplexObjectives` | `0x8010ABCC` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_49.c:5081 | `lvj_checkComplexObjectives` | `0x8010ABF4` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5083 | `lvj_checkComplexObjectives` | `0x8010ABF8` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5085 | `lvj_checkComplexObjectives` | `0x8010ABFC` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5179 | `lvj_checkComplexObjectives` | `0x8010ACB8` | `0x400CCCCD` | `cop0` | `.word       0x400CCCCD                   # mfc0        $t4, Reserved25 # 000004CD <InstrIdType: CPU_COP0>` |
| funcs_49.c:5213 | `lvj_checkComplexObjectives` | `0x8010ACFC` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5215 | `lvj_checkComplexObjectives` | `0x8010AD00` | `0x41A00000` | `cop0` | `.word       0x41A00000                   # INVALID     $t5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5221 | `lvj_checkComplexObjectives` | `0x8010AD0C` | `0xC1200000` | `opcode_0x30` | `ll          $zero, 0x0($t1)` |
| funcs_49.c:5251 | `lvj_checkComplexObjectives` | `0x8010AD48` | `0x40366666` | `cop0` | `.word       0x40366666                   # dmfc0       $s6, Status # 00000666 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5253 | `lvj_checkComplexObjectives` | `0x8010AD4C` | `0xC09126E9` | `opcode_0x30` | `ll          $s1, 0x26E9($a0)` |
| funcs_49.c:5257 | `lvj_checkComplexObjectives` | `0x8010AD54` | `0x40366666` | `cop0` | `.word       0x40366666                   # dmfc0       $s6, Status # 00000666 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5259 | `lvj_checkComplexObjectives` | `0x8010AD58` | `0x409126E9` | `cop0` | `.word       0x409126E9                   # mtc0        $s1, Context # 000006E9 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5263 | `lvj_checkComplexObjectives` | `0x8010AD60` | `0x40733333` | `cop0` | `.word       0x40733333                   # INVALID     $v1, $s3, 0x3333 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5269 | `lvj_checkComplexObjectives` | `0x8010AD6C` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5271 | `lvj_checkComplexObjectives` | `0x8010AD70` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5273 | `lvj_checkComplexObjectives` | `0x8010AD74` | `0x42F00000` | `cop0` | `.word       0x42F00000                   # INVALID     $s7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5275 | `lvj_checkComplexObjectives` | `0x8010AD78` | `0x42F00000` | `cop0` | `.word       0x42F00000                   # INVALID     $s7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5277 | `lvj_checkComplexObjectives` | `0x8010AD7C` | `0x43350000` | `cop0` | `.word       0x43350000                   # INVALID     $t9, $s5, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5279 | `lvj_checkComplexObjectives` | `0x8010AD80` | `0xC2F00000` | `opcode_0x30` | `ll          $s0, 0x0($s7)` |
| funcs_49.c:5281 | `lvj_checkComplexObjectives` | `0x8010AD84` | `0xC2F00000` | `opcode_0x30` | `ll          $s0, 0x0($s7)` |
| funcs_49.c:5283 | `lvj_checkComplexObjectives` | `0x8010AD88` | `0xC3350000` | `opcode_0x30` | `ll          $s5, 0x0($t9)` |
| funcs_49.c:5285 | `lvj_checkComplexObjectives` | `0x8010AD8C` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5287 | `lvj_checkComplexObjectives` | `0x8010AD90` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5289 | `lvj_checkComplexObjectives` | `0x8010AD94` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5519 | `lvj_checkComplexObjectives` | `0x8010AF60` | `0x41000000` | `cop0` | `bc0f        L_8010AF64` |
| funcs_49.c:5522 | `lvj_checkComplexObjectives` | `0x8010AF64` | `0x41000000` | `cop0` | `bc0f        L_8010AF68` |
| funcs_49.c:5525 | `lvj_checkComplexObjectives` | `0x8010AF68` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5573 | `lvj_checkComplexObjectives` | `0x8010AFC8` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5575 | `lvj_checkComplexObjectives` | `0x8010AFCC` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5589 | `lvj_checkComplexObjectives` | `0x8010AFE8` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5591 | `lvj_checkComplexObjectives` | `0x8010AFEC` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5607 | `lvj_checkComplexObjectives` | `0x8010B00C` | `0x40A9BCBE` | `cop0` | `.word       0x40A9BCBE                   # dmtc0       $t1, Reserved23 # 000004BE <InstrIdType: CPU_COP0>` |
| funcs_49.c:5609 | `lvj_checkComplexObjectives` | `0x8010B010` | `0xC101B036` | `opcode_0x30` | `ll          $at, -0x4FCA($t0)` |
| funcs_49.c:5613 | `lvj_checkComplexObjectives` | `0x8010B018` | `0x40A0EF89` | `cop0` | `.word       0x40A0EF89                   # dmtc0       $zero, TagHi # 00000789 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5615 | `lvj_checkComplexObjectives` | `0x8010B01C` | `0x410A1D34` | `cop0` | `.word       0x410A1D34                   # INVALID     $t0, $t2, 0x1D34 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_49.c:5619 | `lvj_checkComplexObjectives` | `0x8010B024` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5623 | `lvj_checkComplexObjectives` | `0x8010B02C` | `0x43070000` | `cop0` | `.word       0x43070000                   # INVALID     $t8, $a3, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5627 | `lvj_checkComplexObjectives` | `0x8010B034` | `0xC3070000` | `opcode_0x30` | `ll          $a3, 0x0($t8)` |
| funcs_49.c:5629 | `lvj_checkComplexObjectives` | `0x8010B038` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5631 | `lvj_checkComplexObjectives` | `0x8010B03C` | `0x42700000` | `cop0` | `.word       0x42700000                   # INVALID     $s3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5653 | `lvj_checkComplexObjectives` | `0x8010B068` | `0x40D8A5F8` | `cop0` | `.word       0x40D8A5F8                   # ctc0        $t8, XContext # 000005F8 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5655 | `lvj_checkComplexObjectives` | `0x8010B06C` | `0x41DCB81D` | `cop0` | `.word       0x41DCB81D                   # INVALID     $t6, $gp, -0x47E3 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5657 | `lvj_checkComplexObjectives` | `0x8010B070` | `0x416DEDFA` | `cop0` | `.word       0x416DEDFA                   # INVALID     $t3, $t5, -0x1206 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5659 | `lvj_checkComplexObjectives` | `0x8010B074` | `0xC0D8A5F8` | `opcode_0x30` | `ll          $t8, -0x5A08($a2)` |
| funcs_49.c:5661 | `lvj_checkComplexObjectives` | `0x8010B078` | `0x41DCB81D` | `cop0` | `.word       0x41DCB81D                   # INVALID     $t6, $gp, -0x47E3 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5663 | `lvj_checkComplexObjectives` | `0x8010B07C` | `0x416DEDFA` | `cop0` | `.word       0x416DEDFA                   # INVALID     $t3, $t5, -0x1206 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5677 | `lvj_checkComplexObjectives` | `0x8010B098` | `0x41A00000` | `cop0` | `.word       0x41A00000                   # INVALID     $t5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5679 | `lvj_checkComplexObjectives` | `0x8010B09C` | `0x41A00000` | `cop0` | `.word       0x41A00000                   # INVALID     $t5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5681 | `lvj_checkComplexObjectives` | `0x8010B0A0` | `0xC28C0000` | `opcode_0x30` | `ll          $t4, 0x0($s4)` |
| funcs_49.c:5683 | `lvj_checkComplexObjectives` | `0x8010B0A4` | `0xC28C0000` | `opcode_0x30` | `ll          $t4, 0x0($s4)` |
| funcs_49.c:5685 | `lvj_checkComplexObjectives` | `0x8010B0A8` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:5687 | `lvj_checkComplexObjectives` | `0x8010B0AC` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:5721 | `lvj_checkComplexObjectives` | `0x8010B0E8` | `0x0000000A` | `movz $zero,$zero,$zero` | `movz        $zero, $zero, $zero` |
| funcs_49.c:5764 | `lvj_checkComplexObjectives` | `0x8010B13C` | `0x0000000A` | `movz $zero,$zero,$zero` | `movz        $zero, $zero, $zero` |
| funcs_49.c:5782 | `lvj_checkComplexObjectives` | `0x8010B160` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_49.c:5784 | `lvj_checkComplexObjectives` | `0x8010B164` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5786 | `lvj_checkComplexObjectives` | `0x8010B168` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:5794 | `lvj_checkComplexObjectives` | `0x8010B178` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:5796 | `lvj_checkComplexObjectives` | `0x8010B17C` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:5798 | `lvj_checkComplexObjectives` | `0x8010B180` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:5808 | `lvj_checkComplexObjectives` | `0x8010B194` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:5810 | `lvj_checkComplexObjectives` | `0x8010B198` | `0x00010001` | `special_0x01 $zero,$zero,$at` | `.word       0x00010001                   # INVALID     $zero, $at, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:5818 | `lvj_checkComplexObjectives` | `0x8010B1A8` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:5824 | `lvj_checkComplexObjectives` | `0x8010B1B4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:5834 | `lvj_checkComplexObjectives` | `0x8010B1C4` | `0x78000004` | `opcode_0x1E` | `.word       0x78000004                   # INVALID     $zero, $zero, 0x4 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5839 | `lvj_checkComplexObjectives` | `0x8010B1D0` | `0x78000004` | `opcode_0x1E` | `.word       0x78000004                   # INVALID     $zero, $zero, 0x4 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5843 | `lvj_checkComplexObjectives` | `0x8010B1D0` | `0x78000004` | `opcode_0x1E` | `.word       0x78000004                   # INVALID     $zero, $zero, 0x4 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5848 | `lvj_checkComplexObjectives` | `0x8010B1D8` | `0x0004000A` | `movz $zero,$zero,$a0` | `movz        $zero, $zero, $a0` |
| funcs_49.c:5850 | `lvj_checkComplexObjectives` | `0x8010B1DC` | `0x78000005` | `opcode_0x1E` | `.word       0x78000005                   # INVALID     $zero, $zero, 0x5 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5857 | `lvj_checkComplexObjectives` | `0x8010B1E8` | `0x76000006` | `opcode_0x1D` | `.word       0x76000006                   # INVALID     $s0, $zero, 0x6 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5861 | `lvj_checkComplexObjectives` | `0x8010B1F0` | `0x0006000E` | `special_0x0E $zero,$zero,$a2` | `.word       0x0006000E                   # INVALID     $zero, $a2, 0xE # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:5863 | `lvj_checkComplexObjectives` | `0x8010B1F4` | `0x78000007` | `opcode_0x1E` | `.word       0x78000007                   # INVALID     $zero, $zero, 0x7 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5869 | `lvj_checkComplexObjectives` | `0x8010B200` | `0x78000008` | `opcode_0x1E` | `.word       0x78000008                   # INVALID     $zero, $zero, 0x8 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5875 | `lvj_checkComplexObjectives` | `0x8010B20C` | `0x78000008` | `opcode_0x1E` | `.word       0x78000008                   # INVALID     $zero, $zero, 0x8 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5881 | `lvj_checkComplexObjectives` | `0x8010B218` | `0x78000009` | `opcode_0x1E` | `.word       0x78000009                   # INVALID     $zero, $zero, 0x9 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5887 | `lvj_checkComplexObjectives` | `0x8010B224` | `0x7800000A` | `opcode_0x1E` | `.word       0x7800000A                   # INVALID     $zero, $zero, 0xA # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5893 | `lvj_checkComplexObjectives` | `0x8010B230` | `0x7800000B` | `opcode_0x1E` | `.word       0x7800000B                   # INVALID     $zero, $zero, 0xB # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5899 | `lvj_checkComplexObjectives` | `0x8010B23C` | `0x7800000C` | `opcode_0x1E` | `.word       0x7800000C                   # INVALID     $zero, $zero, 0xC # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5905 | `lvj_checkComplexObjectives` | `0x8010B248` | `0x7800000D` | `opcode_0x1E` | `.word       0x7800000D                   # INVALID     $zero, $zero, 0xD # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5911 | `lvj_checkComplexObjectives` | `0x8010B254` | `0x7800000F` | `opcode_0x1E` | `.word       0x7800000F                   # INVALID     $zero, $zero, 0xF # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5917 | `lvj_checkComplexObjectives` | `0x8010B260` | `0x78000010` | `opcode_0x1E` | `.word       0x78000010                   # INVALID     $zero, $zero, 0x10 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5923 | `lvj_checkComplexObjectives` | `0x8010B26C` | `0x78000011` | `opcode_0x1E` | `.word       0x78000011                   # INVALID     $zero, $zero, 0x11 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5929 | `lvj_checkComplexObjectives` | `0x8010B278` | `0x78000012` | `opcode_0x1E` | `.word       0x78000012                   # INVALID     $zero, $zero, 0x12 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5935 | `lvj_checkComplexObjectives` | `0x8010B284` | `0x78000012` | `opcode_0x1E` | `.word       0x78000012                   # INVALID     $zero, $zero, 0x12 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5939 | `lvj_checkComplexObjectives` | `0x8010B28C` | `0x00130029` | `special_0x29 $zero,$zero,$s3` | `.word       0x00130029                   # INVALID     $zero, $s3, 0x29 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:5941 | `lvj_checkComplexObjectives` | `0x8010B290` | `0x78000013` | `opcode_0x1E` | `.word       0x78000013                   # INVALID     $zero, $zero, 0x13 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5947 | `lvj_checkComplexObjectives` | `0x8010B29C` | `0x78000015` | `opcode_0x1E` | `.word       0x78000015                   # INVALID     $zero, $zero, 0x15 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5953 | `lvj_checkComplexObjectives` | `0x8010B2A8` | `0x78000017` | `opcode_0x1E` | `.word       0x78000017                   # INVALID     $zero, $zero, 0x17 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5963 | `lvj_checkComplexObjectives` | `0x8010B2BC` | `0x00190031` | `special_0x31 $zero,$zero,$t9` | `tgeu        $zero, $t9, 0` |
| funcs_49.c:5965 | `lvj_checkComplexObjectives` | `0x8010B2C0` | `0x7800001A` | `opcode_0x1E` | `.word       0x7800001A                   # INVALID     $zero, $zero, 0x1A # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5969 | `lvj_checkComplexObjectives` | `0x8010B2C8` | `0x001B0033` | `special_0x33 $zero,$zero,$k1` | `tltu        $zero, $k1, 0` |
| funcs_49.c:5971 | `lvj_checkComplexObjectives` | `0x8010B2CC` | `0x7800001C` | `opcode_0x1E` | `.word       0x7800001C                   # INVALID     $zero, $zero, 0x1C # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5977 | `lvj_checkComplexObjectives` | `0x8010B2D8` | `0x78000021` | `opcode_0x1E` | `.word       0x78000021                   # INVALID     $zero, $zero, 0x21 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5983 | `lvj_checkComplexObjectives` | `0x8010B2E4` | `0x7800FFFF` | `opcode_0x1E` | `.word       0x7800FFFF                   # INVALID     $zero, $zero, -0x1 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:5988 | `lvj_checkComplexObjectives` | `0x8010B2EC` | `0x060C0D0F` | `regimm` | `teqi        $s0, 0xD0F` |
| funcs_49.c:5990 | `lvj_checkComplexObjectives` | `0x8010B2F0` | `0x0615181A` | `regimm` | `.word       0x0615181A                   # INVALID     $s0, $s5, 0x181A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_49.c:6012 | `lvj_checkComplexObjectives` | `0x8010B304` | `0x00350036` | `special_0x36 $zero,$at,$s5` | `tne         $at, $s5, 0` |
| funcs_49.c:6018 | `lvj_checkComplexObjectives` | `0x8010B304` | `0x00350036` | `special_0x36 $zero,$at,$s5` | `tne         $at, $s5, 0` |
| funcs_49.c:6037 | `lvj_checkComplexObjectives` | `0x8010B324` | `0x00000028` | `special_0x28 $zero,$zero,$zero` | `.word       0x00000028                   # INVALID     $zero, $zero, 0x28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:6047 | `lvj_checkComplexObjectives` | `0x8010B338` | `0x00000028` | `special_0x28 $zero,$zero,$zero` | `.word       0x00000028                   # INVALID     $zero, $zero, 0x28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:6051 | `lvj_checkComplexObjectives` | `0x8010B340` | `0x00010101` | `special_0x01 $zero,$zero,$at` | `.word       0x00010101                   # INVALID     $zero, $at, 0x101 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:6057 | `lvj_checkComplexObjectives` | `0x8010B34C` | `0x0901FF01` | `j` | `j           L_8407FC04` |
| funcs_49.c:6065 | `lvj_checkComplexObjectives` | `0x8010B34C` | `0x0901FF01` | `j` | `j           L_8407FC04` |
| funcs_49.c:6069 | `lvj_checkComplexObjectives` | `0x8010B34C` | `0x0901FF01` | `j` | `j           L_8407FC04` |
| funcs_49.c:6123 | `lvj_checkComplexObjectives` | `0x8010B390` | `0x08000000` | `j` | `j           L_80000000` |
| funcs_49.c:6172 | `lvj_checkComplexObjectives` | `0x8010B3F0` | `0x0A0A0507` | `j` | `j           L_8828141C` |
| funcs_49.c:6174 | `lvj_checkComplexObjectives` | `0x8010B3F4` | `0x0B070805` | `j` | `j           L_8C1C2014` |
| funcs_49.c:6176 | `lvj_checkComplexObjectives` | `0x8010B3F8` | `0x08050000` | `j` | `j           L_80140000` |
| funcs_49.c:6182 | `lvj_checkComplexObjectives` | `0x8010B404` | `0xC0B00000` | `opcode_0x30` | `ll          $s0, 0x0($a1)` |
| funcs_49.c:6186 | `lvj_checkComplexObjectives` | `0x8010B40C` | `0x40B00000` | `cop0` | `dmtc0       $s0, Index` |
| funcs_49.c:6192 | `lvj_checkComplexObjectives` | `0x8010B418` | `0xC0B00000` | `opcode_0x30` | `ll          $s0, 0x0($a1)` |
| funcs_49.c:6196 | `lvj_checkComplexObjectives` | `0x8010B420` | `0x40B00000` | `cop0` | `dmtc0       $s0, Index` |
| funcs_49.c:6218 | `lvj_checkComplexObjectives` | `0x8010B44C` | `0x41100000` | `cop0` | `.word       0x41100000                   # INVALID     $t0, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_49.c:6220 | `lvj_checkComplexObjectives` | `0x8010B450` | `0x41300000` | `cop0` | `.word       0x41300000                   # INVALID     $t1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6226 | `lvj_checkComplexObjectives` | `0x8010B45C` | `0x41100000` | `cop0` | `.word       0x41100000                   # INVALID     $t0, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_49.c:6228 | `lvj_checkComplexObjectives` | `0x8010B460` | `0x41300000` | `cop0` | `.word       0x41300000                   # INVALID     $t1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6234 | `lvj_checkComplexObjectives` | `0x8010B46C` | `0x41100000` | `cop0` | `.word       0x41100000                   # INVALID     $t0, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_49.c:6236 | `lvj_checkComplexObjectives` | `0x8010B470` | `0x41300000` | `cop0` | `.word       0x41300000                   # INVALID     $t1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6238 | `lvj_checkComplexObjectives` | `0x8010B474` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6240 | `lvj_checkComplexObjectives` | `0x8010B478` | `0x41300000` | `cop0` | `.word       0x41300000                   # INVALID     $t1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6246 | `lvj_checkComplexObjectives` | `0x8010B484` | `0x40F00000` | `cop0` | `.word       0x40F00000                   # INVALID     $a3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6248 | `lvj_checkComplexObjectives` | `0x8010B488` | `0x41180000` | `cop0` | `.word       0x41180000                   # INVALID     $t0, $t8, 0x0 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_49.c:6250 | `lvj_checkComplexObjectives` | `0x8010B48C` | `0x41100000` | `cop0` | `.word       0x41100000                   # INVALID     $t0, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_49.c:6252 | `lvj_checkComplexObjectives` | `0x8010B490` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6256 | `lvj_checkComplexObjectives` | `0x8010B498` | `0x400CCCCD` | `cop0` | `.word       0x400CCCCD                   # mfc0        $t4, Reserved25 # 000004CD <InstrIdType: CPU_COP0>` |
| funcs_49.c:6258 | `lvj_checkComplexObjectives` | `0x8010B49C` | `0x41100000` | `cop0` | `.word       0x41100000                   # INVALID     $t0, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_49.c:6260 | `lvj_checkComplexObjectives` | `0x8010B4A0` | `0x41300000` | `cop0` | `.word       0x41300000                   # INVALID     $t1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6270 | `lvj_checkComplexObjectives` | `0x8010B4B4` | `0x001F0005` | `special_0x05 $zero,$zero,$ra` | `.word       0x001F0005                   # INVALID     $zero, $ra, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:6326 | `lvj_checkComplexObjectives` | `0x8010B51C` | `0x00BEFF55` | `special_0x15 $ra,$a1,$fp` | `.word       0x00BEFF55                   # INVALID     $a1, $fp, -0xAB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:6342 | `lvj_checkComplexObjectives` | `0x8010B534` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_49.c:6344 | `lvj_checkComplexObjectives` | `0x8010B538` | `0x40700000` | `cop0` | `.word       0x40700000                   # INVALID     $v1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6354 | `lvj_checkComplexObjectives` | `0x8010B54C` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:6358 | `lvj_checkComplexObjectives` | `0x8010B554` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6362 | `lvj_checkComplexObjectives` | `0x8010B55C` | `0x40580000` | `cop0` | `cfc0        $t8, Index` |
| funcs_49.c:6368 | `lvj_checkComplexObjectives` | `0x8010B568` | `0x40266666` | `cop0` | `.word       0x40266666                   # dmfc0       $a2, Status # 00000666 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6372 | `lvj_checkComplexObjectives` | `0x8010B570` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:6376 | `lvj_checkComplexObjectives` | `0x8010B578` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6378 | `lvj_checkComplexObjectives` | `0x8010B57C` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_49.c:6380 | `lvj_checkComplexObjectives` | `0x8010B580` | `0x40B40000` | `cop0` | `dmtc0       $s4, Index` |
| funcs_49.c:6390 | `lvj_checkComplexObjectives` | `0x8010B594` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:6394 | `lvj_checkComplexObjectives` | `0x8010B59C` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6396 | `lvj_checkComplexObjectives` | `0x8010B5A0` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_49.c:6398 | `lvj_checkComplexObjectives` | `0x8010B5A4` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_49.c:6408 | `lvj_checkComplexObjectives` | `0x8010B5B8` | `0x41C80000` | `cop0` | `.word       0x41C80000                   # INVALID     $t6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6412 | `lvj_checkComplexObjectives` | `0x8010B5C0` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6432 | `lvj_checkComplexObjectives` | `0x8010B5E8` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_49.c:6434 | `lvj_checkComplexObjectives` | `0x8010B5EC` | `0x40B40000` | `cop0` | `dmtc0       $s4, Index` |
| funcs_49.c:6444 | `lvj_checkComplexObjectives` | `0x8010B600` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:6448 | `lvj_checkComplexObjectives` | `0x8010B608` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:6470 | `lvj_checkComplexObjectives` | `0x8010B634` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_49.c:6480 | `lvj_checkComplexObjectives` | `0x8010B648` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_49.c:6484 | `lvj_checkComplexObjectives` | `0x8010B650` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:7983 | `static_3_8009D8BC` | `0x8009D8C0` | `0xF1F3F5F7` | `opcode_0x3C` | `scd         $s3, -0xA09($t7)` |
| funcs_49.c:8097 | `static_3_800A2114` | `0x800A21AC` | `0x00012528` | `special_0x28 $a0,$zero,$at` | `.word       0x00012528                   # INVALID     $zero, $at, 0x2528 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8137 | `static_3_800A2114` | `0x800A21EC` | `0x00014329` | `special_0x29 $t0,$zero,$at` | `.word       0x00014329                   # INVALID     $zero, $at, 0x4329 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8179 | `static_3_800A2218` | `0x800A2228` | `0x00013428` | `special_0x28 $a2,$zero,$at` | `.word       0x00013428                   # INVALID     $zero, $at, 0x3428 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8219 | `static_3_800A2218` | `0x800A2268` | `0x00015329` | `special_0x29 $t2,$zero,$at` | `.word       0x00015329                   # INVALID     $zero, $at, 0x5329 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8257 | `static_3_800A2218` | `0x800A22A4` | `0x00013B28` | `special_0x28 $a3,$zero,$at` | `.word       0x00013B28                   # INVALID     $zero, $at, 0x3B28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8297 | `static_3_800A2218` | `0x800A22E4` | `0x00015B29` | `special_0x29 $t3,$zero,$at` | `.word       0x00015B29                   # INVALID     $zero, $at, 0x5B29 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8335 | `static_3_800A2218` | `0x800A2320` | `0x00013928` | `special_0x28 $a3,$zero,$at` | `.word       0x00013928                   # INVALID     $zero, $at, 0x3928 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8375 | `static_3_800A2218` | `0x800A2360` | `0x00015929` | `special_0x29 $t3,$zero,$at` | `.word       0x00015929                   # INVALID     $zero, $at, 0x5929 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8421 | `static_3_800A2218` | `0x800A23AC` | `0x00027730` | `special_0x30 $t6,$zero,$v0` | `tge         $zero, $v0, 476` |
| funcs_49.c:8451 | `static_3_800A23BC` | `0x800A23D0` | `0x00002E28` | `special_0x28 $a1,$zero,$zero` | `.word       0x00002E28                   # INVALID     $zero, $zero, 0x2E28 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8453 | `static_3_800A23BC` | `0x800A23D4` | `0x00008A28` | `special_0x28 $s1,$zero,$zero` | `.word       0x00008A28                   # INVALID     $zero, $zero, -0x75D8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8455 | `static_3_800A23BC` | `0x800A23D8` | `0x0000E728` | `special_0x28 $gp,$zero,$zero` | `.word       0x0000E728                   # INVALID     $zero, $zero, -0x18D8 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8457 | `static_3_800A23BC` | `0x800A23DC` | `0x00014328` | `special_0x28 $t0,$zero,$at` | `.word       0x00014328                   # INVALID     $zero, $at, 0x4328 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8465 | `static_3_800A23BC` | `0x800A23EC` | `0x0002B631` | `special_0x31 $s6,$zero,$v0` | `tgeu        $zero, $v0, 728` |
| funcs_49.c:8491 | `static_3_800A23BC` | `0x800A2410` | `0x00003329` | `special_0x29 $a2,$zero,$zero` | `.word       0x00003329                   # INVALID     $zero, $zero, 0x3329 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8493 | `static_3_800A23BC` | `0x800A2414` | `0x00009929` | `special_0x29 $s3,$zero,$zero` | `.word       0x00009929                   # INVALID     $zero, $zero, -0x66D7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8495 | `static_3_800A23BC` | `0x800A2418` | `0x0000FF29` | `special_0x29 $ra,$zero,$zero` | `.word       0x0000FF29                   # INVALID     $zero, $zero, -0xD7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8497 | `static_3_800A23BC` | `0x800A241C` | `0x00016529` | `special_0x29 $t4,$zero,$at` | `.word       0x00016529                   # INVALID     $zero, $at, 0x6529 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8503 | `static_3_800A23BC` | `0x800A2428` | `0x00029730` | `special_0x30 $s2,$zero,$v0` | `tge         $zero, $v0, 604` |
| funcs_49.c:8505 | `static_3_800A23BC` | `0x800A242C` | `0x0002FD32` | `special_0x32 $ra,$zero,$v0` | `tlt         $zero, $v0, 1012` |
| funcs_49.c:8543 | `static_3_800A23BC` | `0x800A2468` | `0x0002D931` | `special_0x31 $k1,$zero,$v0` | `tgeu        $zero, $v0, 868` |
| funcs_49.c:8545 | `static_3_800A23BC` | `0x800A246C` | `0x00034933` | `special_0x33 $t1,$zero,$v1` | `tltu        $zero, $v1, 292` |
| funcs_49.c:8581 | `static_3_800A23BC` | `0x800A24A4` | `0x0002A630` | `special_0x30 $s4,$zero,$v0` | `tge         $zero, $v0, 664` |
| funcs_49.c:8583 | `static_3_800A23BC` | `0x800A24A8` | `0x00032232` | `special_0x32 $a0,$zero,$v1` | `tlt         $zero, $v1, 136` |
| funcs_49.c:8585 | `static_3_800A23BC` | `0x800A24AC` | `0x00039D34` | `special_0x34 $s3,$zero,$v1` | `teq         $zero, $v1, 628` |
| funcs_49.c:8621 | `static_3_800A23BC` | `0x800A24E4` | `0x0002EC31` | `special_0x31 $sp,$zero,$v0` | `tgeu        $zero, $v0, 944` |
| funcs_49.c:8623 | `static_3_800A23BC` | `0x800A24E8` | `0x00037433` | `special_0x33 $t6,$zero,$v1` | `tltu        $zero, $v1, 464` |
| funcs_49.c:8625 | `static_3_800A23BC` | `0x800A24EC` | `0x0003FC35` | `special_0x35 $ra,$zero,$v1` | `.word       0x0003FC35                   # INVALID     $zero, $v1, -0x3CB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8659 | `static_3_800A23BC` | `0x800A2520` | `0x0002A030` | `special_0x30 $s4,$zero,$v0` | `tge         $zero, $v0, 640` |
| funcs_49.c:8661 | `static_3_800A23BC` | `0x800A2524` | `0x00033532` | `special_0x32 $a2,$zero,$v1` | `tlt         $zero, $v1, 212` |
| funcs_49.c:8663 | `static_3_800A23BC` | `0x800A2528` | `0x0003CB34` | `special_0x34 $t9,$zero,$v1` | `teq         $zero, $v1, 812` |
| funcs_49.c:8665 | `static_3_800A23BC` | `0x800A252C` | `0x00046036` | `special_0x36 $t4,$zero,$a0` | `tne         $zero, $a0, 384` |
| funcs_49.c:8703 | `static_3_800A2558` | `0x800A2560` | `0x0002E431` | `special_0x31 $gp,$zero,$v0` | `tgeu        $zero, $v0, 912` |
| funcs_49.c:8705 | `static_3_800A2558` | `0x800A2564` | `0x00038833` | `special_0x33 $s1,$zero,$v1` | `tltu        $zero, $v1, 544` |
| funcs_49.c:8707 | `static_3_800A2558` | `0x800A2568` | `0x00042D35` | `special_0x35 $a1,$zero,$a0` | `.word       0x00042D35                   # INVALID     $zero, $a0, 0x2D35 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8709 | `static_3_800A2558` | `0x800A256C` | `0x0004D137` | `special_0x37 $k0,$zero,$a0` | `.word       0x0004D137                   # INVALID     $zero, $a0, -0x2EC9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8743 | `static_3_800A2558` | `0x800A25A0` | `0x00032E32` | `special_0x32 $a1,$zero,$v1` | `tlt         $zero, $v1, 184` |
| funcs_49.c:8745 | `static_3_800A2558` | `0x800A25A4` | `0x0003E334` | `special_0x34 $gp,$zero,$v1` | `teq         $zero, $v1, 908` |
| funcs_49.c:8747 | `static_3_800A2558` | `0x800A25A8` | `0x00049836` | `special_0x36 $s3,$zero,$a0` | `tne         $zero, $a0, 608` |
| funcs_49.c:8775 | `static_3_800A2558` | `0x800A25D0` | `0x00006330` | `special_0x30 $t4,$zero,$zero` | `tge         $zero, $zero, 396` |
| funcs_49.c:8777 | `static_3_800A2558` | `0x800A25D4` | `0x00012A30` | `special_0x30 $a1,$zero,$at` | `tge         $zero, $at, 168` |
| funcs_49.c:8779 | `static_3_800A2558` | `0x800A25D8` | `0x0001F130` | `special_0x30 $fp,$zero,$at` | `tge         $zero, $at, 964` |
| funcs_49.c:8781 | `static_3_800A2558` | `0x800A25DC` | `0x0002B830` | `special_0x30 $s7,$zero,$v0` | `tge         $zero, $v0, 736` |
| funcs_49.c:8783 | `static_3_800A2558` | `0x800A25E0` | `0x00037F33` | `special_0x33 $t7,$zero,$v1` | `tltu        $zero, $v1, 508` |
| funcs_49.c:8785 | `static_3_800A2558` | `0x800A25E4` | `0x00044635` | `special_0x35 $t0,$zero,$a0` | `.word       0x00044635                   # INVALID     $zero, $a0, 0x4635 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8787 | `static_3_800A2558` | `0x800A25E8` | `0x00050D37` | `special_0x37 $at,$zero,$a1` | `.word       0x00050D37                   # INVALID     $zero, $a1, 0xD37 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8789 | `static_3_800A2558` | `0x800A25EC` | `0x0005D439` | `special_0x39 $k0,$zero,$a1` | `.word       0x0005D439                   # INVALID     $zero, $a1, -0x2BC7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8815 | `static_3_800A2558` | `0x800A2610` | `0x00006D31` | `special_0x31 $t5,$zero,$zero` | `tgeu        $zero, $zero, 436` |
| funcs_49.c:8817 | `static_3_800A2558` | `0x800A2614` | `0x00014831` | `special_0x31 $t1,$zero,$at` | `tgeu        $zero, $at, 288` |
| funcs_49.c:8819 | `static_3_800A2558` | `0x800A2618` | `0x00022331` | `special_0x31 $a0,$zero,$v0` | `tgeu        $zero, $v0, 140` |
| funcs_49.c:8821 | `static_3_800A2558` | `0x800A261C` | `0x0002FE31` | `special_0x31 $ra,$zero,$v0` | `tgeu        $zero, $v0, 1016` |
| funcs_49.c:8823 | `static_3_800A2558` | `0x800A2620` | `0x0003D934` | `special_0x34 $k1,$zero,$v1` | `teq         $zero, $v1, 868` |
| funcs_49.c:8825 | `static_3_800A2558` | `0x800A2624` | `0x0004B436` | `special_0x36 $s6,$zero,$a0` | `tne         $zero, $a0, 720` |
| funcs_49.c:8855 | `static_3_800A2558` | `0x800A2650` | `0x00007832` | `special_0x32 $t7,$zero,$zero` | `tlt         $zero, $zero, 480` |
| funcs_49.c:8857 | `static_3_800A2558` | `0x800A2654` | `0x00016832` | `special_0x32 $t5,$zero,$at` | `tlt         $zero, $at, 416` |
| funcs_49.c:8859 | `static_3_800A2558` | `0x800A2658` | `0x00025932` | `special_0x32 $t3,$zero,$v0` | `tlt         $zero, $v0, 356` |
| funcs_49.c:8861 | `static_3_800A2558` | `0x800A265C` | `0x00034932` | `special_0x32 $t1,$zero,$v1` | `tlt         $zero, $v1, 292` |
| funcs_49.c:8863 | `static_3_800A2558` | `0x800A2660` | `0x00043B35` | `special_0x35 $a3,$zero,$a0` | `.word       0x00043B35                   # INVALID     $zero, $a0, 0x3B35 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8865 | `static_3_800A2558` | `0x800A2664` | `0x00052B37` | `special_0x37 $a1,$zero,$a1` | `.word       0x00052B37                   # INVALID     $zero, $a1, 0x2B37 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8867 | `static_3_800A2558` | `0x800A2668` | `0x00061C39` | `special_0x39 $v1,$zero,$a2` | `.word       0x00061C39                   # INVALID     $zero, $a2, 0x1C39 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8895 | `static_3_800A2558` | `0x800A2690` | `0x00008433` | `special_0x33 $s0,$zero,$zero` | `tltu        $zero, $zero, 528` |
| funcs_49.c:8897 | `static_3_800A2558` | `0x800A2694` | `0x00018D33` | `special_0x33 $s1,$zero,$at` | `tltu        $zero, $at, 564` |
| funcs_49.c:8899 | `static_3_800A2558` | `0x800A2698` | `0x00029633` | `special_0x33 $s2,$zero,$v0` | `tltu        $zero, $v0, 600` |
| funcs_49.c:8901 | `static_3_800A2558` | `0x800A269C` | `0x00039F33` | `special_0x33 $s3,$zero,$v1` | `tltu        $zero, $v1, 636` |
| funcs_49.c:8903 | `static_3_800A2558` | `0x800A26A0` | `0x0004A836` | `special_0x36 $s5,$zero,$a0` | `tne         $zero, $a0, 672` |
| funcs_49.c:8935 | `static_3_800A2558` | `0x800A26D0` | `0x00009134` | `special_0x34 $s2,$zero,$zero` | `teq         $zero, $zero, 580` |
| funcs_49.c:8937 | `static_3_800A2558` | `0x800A26D4` | `0x0001B434` | `special_0x34 $s6,$zero,$at` | `teq         $zero, $at, 720` |
| funcs_49.c:8939 | `static_3_800A2558` | `0x800A26D8` | `0x0002D834` | `special_0x34 $k1,$zero,$v0` | `teq         $zero, $v0, 864` |
| funcs_49.c:8941 | `static_3_800A2558` | `0x800A26DC` | `0x0003FB34` | `special_0x34 $ra,$zero,$v1` | `teq         $zero, $v1, 1004` |
| funcs_49.c:8943 | `static_3_800A2558` | `0x800A26E0` | `0x00051F37` | `special_0x37 $v1,$zero,$a1` | `.word       0x00051F37                   # INVALID     $zero, $a1, 0x1F37 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8945 | `static_3_800A2558` | `0x800A26E4` | `0x00064239` | `special_0x39 $t0,$zero,$a2` | `.word       0x00064239                   # INVALID     $zero, $a2, 0x4239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8949 | `static_3_800A2558` | `0x800A26EC` | `0x0008893D` | `special_0x3D $s1,$zero,$t0` | `.word       0x0008893D                   # INVALID     $zero, $t0, -0x76C3 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8975 | `static_3_800A2558` | `0x800A2710` | `0x0000A035` | `special_0x35 $s4,$zero,$zero` | `.word       0x0000A035                   # INVALID     $zero, $zero, -0x5FCB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8977 | `static_3_800A2558` | `0x800A2714` | `0x0001E035` | `special_0x35 $gp,$zero,$at` | `.word       0x0001E035                   # INVALID     $zero, $at, -0x1FCB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8979 | `static_3_800A2558` | `0x800A2718` | `0x00032135` | `special_0x35 $a0,$zero,$v1` | `.word       0x00032135                   # INVALID     $zero, $v1, 0x2135 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:8981 | `static_3_800A2558` | `0x800A271C` | `0x00046135` | `special_0x35 $t4,$zero,$a0` | `.word       0x00046135                   # INVALID     $zero, $a0, 0x6135 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9015 | `static_3_800A2558` | `0x800A2750` | `0x0000B036` | `special_0x36 $s6,$zero,$zero` | `tne         $zero, $zero, 704` |
| funcs_49.c:9017 | `static_3_800A2558` | `0x800A2754` | `0x00021036` | `special_0x36 $v0,$zero,$v0` | `tne         $zero, $v0, 64` |
| funcs_49.c:9019 | `static_3_800A2558` | `0x800A2758` | `0x00037136` | `special_0x36 $t6,$zero,$v1` | `tne         $zero, $v1, 452` |
| funcs_49.c:9021 | `static_3_800A2558` | `0x800A275C` | `0x0004D136` | `special_0x36 $k0,$zero,$a0` | `tne         $zero, $a0, 836` |
| funcs_49.c:9023 | `static_3_800A2558` | `0x800A2760` | `0x00063339` | `special_0x39 $a2,$zero,$a2` | `.word       0x00063339                   # INVALID     $zero, $a2, 0x3339 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9027 | `static_3_800A2558` | `0x800A2768` | `0x0008F43D` | `special_0x3D $fp,$zero,$t0` | `.word       0x0008F43D                   # INVALID     $zero, $t0, -0xBC3 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9059 | `static_3_800A2790` | `0x800A2790` | `0x0000C237` | `special_0x37 $t8,$zero,$zero` | `.word       0x0000C237                   # INVALID     $zero, $zero, -0x3DC9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9061 | `static_3_800A2790` | `0x800A2794` | `0x00024637` | `special_0x37 $t0,$zero,$v0` | `.word       0x00024637                   # INVALID     $zero, $v0, 0x4637 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9063 | `static_3_800A2790` | `0x800A2798` | `0x0003CA37` | `special_0x37 $t9,$zero,$v1` | `.word       0x0003CA37                   # INVALID     $zero, $v1, -0x35C9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9065 | `static_3_800A2790` | `0x800A279C` | `0x00054E37` | `special_0x37 $t1,$zero,$a1` | `.word       0x00054E37                   # INVALID     $zero, $a1, 0x4E37 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9109 | `static_3_800A2790` | `0x800A27E4` | `0x00092A3D` | `special_0x3D $a1,$zero,$t1` | `.word       0x00092A3D                   # INVALID     $zero, $t1, 0x2A3D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9113 | `static_3_800A2790` | `0x800A27EC` | `0x000C7F41` | `special_0x01 $t7,$zero,$t4` | `.word       0x000C7F41                   # INVALID     $zero, $t4, 0x7F41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9139 | `static_3_800A2790` | `0x800A2810` | `0x0000EA39` | `special_0x39 $sp,$zero,$zero` | `.word       0x0000EA39                   # INVALID     $zero, $zero, -0x15C7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9141 | `static_3_800A2790` | `0x800A2814` | `0x0002BF39` | `special_0x39 $s7,$zero,$v0` | `.word       0x0002BF39                   # INVALID     $zero, $v0, -0x40C7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9143 | `static_3_800A2790` | `0x800A2818` | `0x00049539` | `special_0x39 $s2,$zero,$a0` | `.word       0x00049539                   # INVALID     $zero, $a0, -0x6AC7 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9145 | `static_3_800A2790` | `0x800A281C` | `0x00066A39` | `special_0x39 $t5,$zero,$a2` | `.word       0x00066A39                   # INVALID     $zero, $a2, 0x6A39 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9187 | `static_3_800A2790` | `0x800A2860` | `0x0009143D` | `special_0x3D $v0,$zero,$t1` | `.word       0x0009143D                   # INVALID     $zero, $t1, 0x143D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9191 | `static_3_800A2790` | `0x800A2868` | `0x000D1D41` | `special_0x01 $v1,$zero,$t5` | `.word       0x000D1D41                   # INVALID     $zero, $t5, 0x1D41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9269 | `static_3_800A2790` | `0x800A28E4` | `0x000D6B41` | `special_0x01 $t5,$zero,$t5` | `.word       0x000D6B41                   # INVALID     $zero, $t5, 0x6B41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9273 | `static_3_800A2790` | `0x800A28EC` | `0x00124C45` | `special_0x05 $t1,$zero,$s2` | `.word       0x00124C45                   # INVALID     $zero, $s2, 0x4C45 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9299 | `static_3_800A2790` | `0x800A2910` | `0x0001573D` | `special_0x3D $t2,$zero,$at` | `.word       0x0001573D                   # INVALID     $zero, $at, 0x573D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9301 | `static_3_800A2790` | `0x800A2914` | `0x0004063D` | `special_0x3D $zero,$zero,$a0` | `.word       0x0004063D                   # INVALID     $zero, $a0, 0x63D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9303 | `static_3_800A2790` | `0x800A2918` | `0x0006B53D` | `special_0x3D $s6,$zero,$a2` | `.word       0x0006B53D                   # INVALID     $zero, $a2, -0x4AC3 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9305 | `static_3_800A2790` | `0x800A291C` | `0x0009643D` | `special_0x3D $t4,$zero,$t1` | `.word       0x0009643D                   # INVALID     $zero, $t1, 0x643D # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9351 | `static_3_800A2924` | `0x800A2960` | `0x000D4A41` | `special_0x01 $t1,$zero,$t5` | `.word       0x000D4A41                   # INVALID     $zero, $t5, 0x4A41 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9355 | `static_3_800A2924` | `0x800A2968` | `0x00133245` | `special_0x05 $a2,$zero,$s3` | `.word       0x00133245                   # INVALID     $zero, $s3, 0x3245 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9441 | `static_3_800A29BC` | `0x800A29E4` | `0x0013A845` | `special_0x05 $s5,$zero,$s3` | `.word       0x0013A845                   # INVALID     $zero, $s3, -0x57BB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9445 | `static_3_800A29BC` | `0x800A29EC` | `0x001ACE49` | `jalr $t9,$zero,$k0` | `.word       0x001ACE49                   # jalr        $t9, $zero # 001A0640 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9471 | `static_3_800A29BC` | `0x800A2A10` | `0x0001F741` | `special_0x01 $fp,$zero,$at` | `.word       0x0001F741                   # INVALID     $zero, $at, -0x8BF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9473 | `static_3_800A29BC` | `0x800A2A14` | `0x0005E541` | `special_0x01 $gp,$zero,$a1` | `.word       0x0005E541                   # INVALID     $zero, $a1, -0x1ABF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9475 | `static_3_800A29BC` | `0x800A2A18` | `0x0009D441` | `special_0x01 $k0,$zero,$t1` | `.word       0x0009D441                   # INVALID     $zero, $t1, -0x2BBF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9477 | `static_3_800A29BC` | `0x800A2A1C` | `0x000DC241` | `special_0x01 $t8,$zero,$t5` | `.word       0x000DC241                   # INVALID     $zero, $t5, -0x3DBF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9484 | `static_3_800A29BC` | `0x800A2A2C` | `0x001D7C4A` | `movz $t7,$zero,$sp` | `.word       0x001D7C4A                   # movz        $t7, $zero, $sp # 00000440 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9488 | `static_3_800A29BC` | `0x800A2A2C` | `0x001D7C4A` | `movz $t7,$zero,$sp` | `.word       0x001D7C4A                   # movz        $t7, $zero, $sp # 00000440 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9522 | `static_3_800A29BC` | `0x800A2A60` | `0x00137545` | `special_0x05 $t6,$zero,$s3` | `.word       0x00137545                   # INVALID     $zero, $s3, 0x7545 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9526 | `static_3_800A29BC` | `0x800A2A68` | `0x001C1B49` | `jalr $v1,$zero,$gp` | `.word       0x001C1B49                   # jalr        $v1, $zero # 001C0340 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9528 | `static_3_800A29BC` | `0x800A2A6C` | `0x00206E4B` | `movn $t5,$at,$zero` | `.word       0x00206E4B                   # movn        $t5, $at, $zero # 00000640 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9565 | `static_3_800A29BC` | `0x800A2AA8` | `0x001EEA4A` | `movz $sp,$zero,$fp` | `.word       0x001EEA4A                   # movz        $sp, $zero, $fp # 00000240 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9569 | `static_3_800A29BC` | `0x800A2AA8` | `0x001EEA4A` | `movz $sp,$zero,$fp` | `.word       0x001EEA4A                   # movz        $sp, $zero, $fp # 00000240 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9608 | `static_3_800A29BC` | `0x800A2AE4` | `0x001CC649` | `jalr $t8,$zero,$gp` | `.word       0x001CC649                   # jalr        $t8, $zero # 001C0640 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9610 | `static_3_800A29BC` | `0x800A2AE8` | `0x0022024B` | `movn $zero,$at,$v0` | `.word       0x0022024B                   # movn        $zero, $at, $v0 # 00000240 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9612 | `static_3_800A29BC` | `0x800A2AEC` | `0x00273D4D` | `break $a3,$at,$a3` | `break       39, 245` |
| funcs_49.c:9638 | `static_3_800A29BC` | `0x800A2B10` | `0x0002E045` | `special_0x05 $gp,$zero,$v0` | `.word       0x0002E045                   # INVALID     $zero, $v0, -0x1FBB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9640 | `static_3_800A29BC` | `0x800A2B14` | `0x0008A145` | `special_0x05 $s4,$zero,$t0` | `.word       0x0008A145                   # INVALID     $zero, $t0, -0x5EBB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9642 | `static_3_800A29BC` | `0x800A2B18` | `0x000E6345` | `special_0x05 $t4,$zero,$t6` | `.word       0x000E6345                   # INVALID     $zero, $t6, 0x6345 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9644 | `static_3_800A29BC` | `0x800A2B1C` | `0x00142445` | `special_0x05 $a0,$zero,$s4` | `.word       0x00142445                   # INVALID     $zero, $s4, 0x2445 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9647 | `static_3_800A29BC` | `0x800A2B24` | `0x001FA74A` | `movz $s4,$zero,$ra` | `.word       0x001FA74A                   # movz        $s4, $zero, $ra # 00000740 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9651 | `static_3_800A29BC` | `0x800A2B24` | `0x001FA74A` | `movz $s4,$zero,$ra` | `.word       0x001FA74A                   # movz        $s4, $zero, $ra # 00000740 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9656 | `static_3_800A29BC` | `0x800A2B2C` | `0x002B2A4E` | `special_0x0E $a1,$at,$t3` | `.word       0x002B2A4E                   # INVALID     $at, $t3, 0x2A4E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9694 | `static_3_800A2B50` | `0x800A2B60` | `0x001C7E49` | `jalr $t7,$zero,$gp` | `.word       0x001C7E49                   # jalr        $t7, $zero # 001C0640 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9696 | `static_3_800A2B50` | `0x800A2B64` | `0x0022D34B` | `movn $k0,$at,$v0` | `.word       0x0022D34B                   # movn        $k0, $at, $v0 # 00000340 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9698 | `static_3_800A2B50` | `0x800A2B68` | `0x0029284D` | `break $a1,$at,$t1` | `break       41, 161` |
| funcs_49.c:9700 | `static_3_800A2B50` | `0x800A2B6C` | `0x002F7D4F` | `special_0x0F $t7,$at,$t7` | `.word       0x002F7D4F                   # sync # 002F7D40 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9734 | `static_3_800A2B50` | `0x800A2BA0` | `0x001F574A` | `movz $t2,$zero,$ra` | `.word       0x001F574A                   # movz        $t2, $zero, $ra # 00000740 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9739 | `static_3_800A2B50` | `0x800A2BA8` | `0x002D454E` | `special_0x0E $t0,$at,$t5` | `.word       0x002D454E                   # INVALID     $at, $t5, 0x454E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9771 | `static_3_800A2B50` | `0x800A2BE0` | `0x0022794B` | `movn $t7,$at,$v0` | `.word       0x0022794B                   # movn        $t7, $at, $v0 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9784 | `static_3_800A2B50` | `0x800A2BE0` | `0x0022794B` | `movn $t7,$at,$v0` | `.word       0x0022794B                   # movn        $t7, $at, $v0 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9794 | `static_3_800A2B50` | `0x800A2BE0` | `0x0022794B` | `movn $t7,$at,$v0` | `.word       0x0022794B                   # movn        $t7, $at, $v0 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9801 | `static_3_800A2B50` | `0x800A2BE0` | `0x0022794B` | `movn $t7,$at,$v0` | `.word       0x0022794B                   # movn        $t7, $at, $v0 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9805 | `static_3_800A2B50` | `0x800A2BE0` | `0x0022794B` | `movn $t7,$at,$v0` | `.word       0x0022794B                   # movn        $t7, $at, $v0 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9811 | `static_3_800A2BE4` | `0x800A2BE4` | `0x002A224D` | `break $a0,$at,$t2` | `break       42, 137` |
| funcs_49.c:9813 | `static_3_800A2BE4` | `0x800A2BE8` | `0x0031CB4F` | `special_0x0F $t9,$at,$s1` | `.word       0x0031CB4F                   # sync # 0031CB40 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9841 | `static_3_800A2BE4` | `0x800A2C10` | `0x00043649` | `jalr $a2,$zero,$a0` | `.word       0x00043649                   # jalr        $a2, $zero # 00040640 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9843 | `static_3_800A2BE4` | `0x800A2C14` | `0x000CA349` | `jalr $s4,$zero,$t4` | `.word       0x000CA349                   # jalr        $s4, $zero # 000C0340 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9845 | `static_3_800A2BE4` | `0x800A2C18` | `0x00151149` | `jalr $v0,$zero,$s5` | `.word       0x00151149                   # jalr        $v0, $zero # 00150140 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9847 | `static_3_800A2BE4` | `0x800A2C1C` | `0x001D7E49` | `jalr $t7,$zero,$sp` | `.word       0x001D7E49                   # jalr        $t7, $zero # 001D0640 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9852 | `static_3_800A2BE4` | `0x800A2C24` | `0x002E594E` | `special_0x0E $t3,$at,$t6` | `.word       0x002E594E                   # INVALID     $at, $t6, 0x594E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9882 | `static_3_800A2BE4` | `0x800A2C50` | `0x0004A24A` | `movz $s4,$zero,$a0` | `.word       0x0004A24A                   # movz        $s4, $zero, $a0 # 00000240 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9884 | `static_3_800A2BE4` | `0x800A2C54` | `0x000DE74A` | `movz $gp,$zero,$t5` | `.word       0x000DE74A                   # movz        $gp, $zero, $t5 # 00000740 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9886 | `static_3_800A2BE4` | `0x800A2C58` | `0x00172C4A` | `movz $a1,$zero,$s7` | `.word       0x00172C4A                   # movz        $a1, $zero, $s7 # 00000440 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9888 | `static_3_800A2BE4` | `0x800A2C5C` | `0x0020714A` | `movz $t6,$at,$zero` | `.word       0x0020714A                   # movz        $t6, $at, $zero # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9890 | `static_3_800A2BE4` | `0x800A2C60` | `0x0029B74D` | `break $s6,$at,$t1` | `break       41, 733` |
| funcs_49.c:9892 | `static_3_800A2BE4` | `0x800A2C64` | `0x0032FC4F` | `special_0x0F $ra,$at,$s2` | `.word       0x0032FC4F                   # sync # 0032FC40 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9922 | `static_3_800A2BE4` | `0x800A2C90` | `0x0005194B` | `movn $v1,$zero,$a1` | `.word       0x0005194B                   # movn        $v1, $zero, $a1 # 00000140 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9924 | `static_3_800A2BE4` | `0x800A2C94` | `0x000F4B4B` | `movn $t1,$zero,$t7` | `.word       0x000F4B4B                   # movn        $t1, $zero, $t7 # 00000340 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9926 | `static_3_800A2BE4` | `0x800A2C98` | `0x00197E4B` | `movn $t7,$zero,$t9` | `.word       0x00197E4B                   # movn        $t7, $zero, $t9 # 00000640 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9928 | `static_3_800A2BE4` | `0x800A2C9C` | `0x0023B04B` | `movn $s6,$at,$v1` | `.word       0x0023B04B                   # movn        $s6, $at, $v1 # 00000040 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9930 | `static_3_800A2BE4` | `0x800A2CA0` | `0x002DE34E` | `special_0x0E $gp,$at,$t5` | `.word       0x002DE34E                   # INVALID     $at, $t5, -0x1CB2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9974 | `static_3_800A2BE4` | `0x800A2CE0` | `0x00327A4F` | `special_0x0F $t7,$at,$s2` | `.word       0x00327A4F                   # sync # 00327A40 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:9980 | `static_3_800A2BE4` | `0x800A2CEC` | `0x00542055` | `special_0x15 $a0,$v0,$s4` | `.word       0x00542055                   # INVALID     $v0, $s4, 0x2055 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10006 | `static_3_800A2BE4` | `0x800A2D10` | `0x00062B4D` | `break $a1,$zero,$a2` | `break       6, 173` |
| funcs_49.c:10008 | `static_3_800A2BE4` | `0x800A2D14` | `0x0012814D` | `break $s0,$zero,$s2` | `break       18, 517` |
| funcs_49.c:10010 | `static_3_800A2BE4` | `0x800A2D18` | `0x001ED84D` | `break $k1,$zero,$fp` | `break       30, 865` |
| funcs_49.c:10012 | `static_3_800A2BE4` | `0x800A2D1C` | `0x002B2E4D` | `break $a1,$at,$t3` | `break       43, 185` |
| funcs_49.c:10046 | `static_3_800A2BE4` | `0x800A2D50` | `0x0006C94E` | `special_0x0E $t9,$zero,$a2` | `.word       0x0006C94E                   # INVALID     $zero, $a2, -0x36B2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10048 | `static_3_800A2BE4` | `0x800A2D54` | `0x00145B4E` | `special_0x0E $t3,$zero,$s4` | `.word       0x00145B4E                   # INVALID     $zero, $s4, 0x5B4E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10050 | `static_3_800A2BE4` | `0x800A2D58` | `0x0021EE4E` | `special_0x0E $sp,$at,$at` | `.word       0x0021EE4E                   # INVALID     $at, $at, -0x11B2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10052 | `static_3_800A2BE4` | `0x800A2D5C` | `0x002F804E` | `special_0x0E $s0,$at,$t7` | `.word       0x002F804E                   # INVALID     $at, $t7, -0x7FB2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10058 | `static_3_800A2BE4` | `0x800A2D68` | `0x00583955` | `special_0x15 $a3,$v0,$t8` | `.word       0x00583955                   # INVALID     $v0, $t8, 0x3955 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10086 | `static_3_800A2BE4` | `0x800A2D90` | `0x0007774F` | `special_0x0F $t6,$zero,$a3` | `.word       0x0007774F                   # sync # 00077740 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10088 | `static_3_800A2BE4` | `0x800A2D94` | `0x0016654F` | `special_0x0F $t4,$zero,$s6` | `.word       0x0016654F                   # sync # 00166540 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10090 | `static_3_800A2BE4` | `0x800A2D98` | `0x0025534F` | `special_0x0F $t2,$at,$a1` | `.word       0x0025534F                   # sync # 00255340 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10092 | `static_3_800A2BE4` | `0x800A2D9C` | `0x0034414F` | `special_0x0F $t0,$at,$s4` | `.word       0x0034414F                   # sync # 00344140 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10136 | `static_3_800A2BE4` | `0x800A2DE4` | `0x005A5455` | `special_0x15 $t2,$v0,$k0` | `.word       0x005A5455                   # INVALID     $v0, $k0, 0x5455 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10214 | `static_3_800A2BE4` | `0x800A2E60` | `0x00596D55` | `special_0x15 $t5,$v0,$t9` | `.word       0x00596D55                   # INVALID     $v0, $t9, 0x6D55 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10330 | `static_3_800A2E98` | `0x800A2F10` | `0x000D3955` | `special_0x15 $a3,$zero,$t5` | `.word       0x000D3955                   # INVALID     $zero, $t5, 0x3955 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10332 | `static_3_800A2E98` | `0x800A2F14` | `0x0027AC55` | `special_0x15 $s5,$at,$a3` | `.word       0x0027AC55                   # INVALID     $at, $a3, -0x53AB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10334 | `static_3_800A2E98` | `0x800A2F18` | `0x00422055` | `special_0x15 $a0,$v0,$v0` | `.word       0x00422055                   # INVALID     $v0, $v0, 0x2055 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10336 | `static_3_800A2E98` | `0x800A2F1C` | `0x005C9355` | `special_0x15 $s2,$v0,$gp` | `.word       0x005C9355                   # INVALID     $v0, $gp, -0x6CAB # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10459 | `static_3_800A2FE4` | `0x800A2FE4` | `0x00155B81` | `special_0x01 $t3,$zero,$s5` | `.word       0x00155B81                   # INVALID     $zero, $s5, 0x5B81 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10480 | `static_3_800A2FE4` | `0x800A3000` | `0x00200001` | `special_0x01 $zero,$at,$zero` | `.word       0x00200001                   # INVALID     $at, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10486 | `static_3_800A2FE4` | `0x800A3008` | `0x0023EB36` | `special_0x36 $sp,$at,$v1` | `tne         $at, $v1, 940` |
| funcs_49.c:10489 | `static_3_800A2FE4` | `0x800A300C` | `0x00260DFD` | `special_0x3D $at,$at,$a2` | `.word       0x00260DFD                   # INVALID     $at, $a2, 0xDFD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10502 | `static_3_800A2FE4` | `0x800A3024` | `0x0035D141` | `special_0x01 $k0,$at,$s5` | `.word       0x0035D141                   # INVALID     $at, $s5, -0x2EBF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10506 | `static_3_800A2FE4` | `0x800A302C` | `0x003C6871` | `special_0x31 $t5,$at,$gp` | `tgeu        $at, $gp, 417` |
| funcs_49.c:10516 | `static_3_800A2FE4` | `0x800A3040` | `0x0050A28E` | `special_0x0E $s4,$v0,$s0` | `.word       0x0050A28E                   # INVALID     $v0, $s0, -0x5D72 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10534 | `static_3_800A2FE4` | `0x800A3064` | `0x00879C81` | `special_0x01 $s3,$a0,$a3` | `.word       0x00879C81                   # INVALID     $a0, $a3, -0x637F # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10538 | `static_3_800A2FE4` | `0x800A306C` | `0x009837F5` | `special_0x35 $a2,$a0,$t8` | `.word       0x009837F5                   # INVALID     $a0, $t8, 0x37F5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10542 | `static_3_800A2FE4` | `0x800A3074` | `0x00AADC0E` | `special_0x0E $k1,$a1,$t2` | `.word       0x00AADC0E                   # INVALID     $a1, $t2, -0x23F2 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10544 | `static_3_800A2FE4` | `0x800A3078` | `0x00B504F9` | `special_0x39 $zero,$a1,$s5` | `.word       0x00B504F9                   # INVALID     $a1, $s5, 0x4F9 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10546 | `static_3_800A2FE4` | `0x800A307C` | `0x00BFC88D` | `break $t9,$a1,$ra` | `break       191, 802` |
| funcs_49.c:10563 | `static_3_800A2FE4` | `0x800A3098` | `0x011F59B6` | `special_0x36 $t3,$t0,$ra` | `tne         $t0, $ra, 358` |
| funcs_49.c:10571 | `static_3_800A2FE4` | `0x800A30A8` | `0x016A09F2` | `special_0x32 $at,$t3,$t2` | `tlt         $t3, $t2, 39` |
| funcs_49.c:10578 | `static_3_800A2FE4` | `0x800A30B8` | `0x01C823F0` | `special_0x30 $a0,$t6,$t0` | `tge         $t6, $t0, 143` |
| funcs_49.c:10582 | `static_3_800A2FE4` | `0x800A30B8` | `0x01C823F0` | `special_0x30 $a0,$t6,$t0` | `tge         $t6, $t0, 143` |
| funcs_49.c:10584 | `static_3_800A2FE4` | `0x800A30BC` | `0x01E3438E` | `special_0x0E $t0,$t7,$v1` | `.word       0x01E3438E                   # INVALID     $t7, $v1, 0x438E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_49.c:10594 | `static_3_800A2FE4` | `0x800A30D0` | `0x02851474` | `special_0x34 $v0,$s4,$a1` | `teq         $s4, $a1, 81` |
| funcs_49.c:10600 | `static_3_800A2FE4` | `0x800A30DC` | `0x02FF2234` | `special_0x34 $a0,$s7,$ra` | `teq         $s7, $ra, 136` |
| funcs_49.c:10602 | `static_3_800A2FE4` | `0x800A30E0` | `0x032CBFF0` | `special_0x30 $s7,$t9,$t4` | `tge         $t9, $t4, 767` |
| funcs_49.c:10612 | `static_3_800A2FE4` | `0x800A30F4` | `0x043CE408` | `regimm` | `.word       0x043CE408                   # INVALID     $at, $gp, -0x1BF8 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_49.c:10616 | `static_3_800A2FE4` | `0x800A30F4` | `0x043CE408` | `regimm` | `.word       0x043CE408                   # INVALID     $at, $gp, -0x1BF8 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_49.c:10618 | `static_3_800A2FE4` | `0x800A30F8` | `0x047D66D8` | `regimm` | `.word       0x047D66D8                   # INVALID     $v1, $sp, 0x66D8 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_49.c:10622 | `static_3_800A2FE4` | `0x800A3100` | `0x050A28E8` | `regimm` | `tlti        $t0, 0x28E8` |
| funcs_49.c:10626 | `static_3_800A2FE4` | `0x800A3100` | `0x050A28E8` | `regimm` | `tlti        $t0, 0x28E8` |
| funcs_49.c:10628 | `static_3_800A2FE4` | `0x800A3104` | `0x0556E070` | `regimm` | `.word       0x0556E070                   # INVALID     $t2, $s6, -0x1F90 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_49.c:10630 | `static_3_800A2FE4` | `0x800A3108` | `0x05A827C8` | `regimm` | `tgei        $t5, 0x27C8` |
| funcs_49.c:10632 | `static_3_800A2FE4` | `0x800A310C` | `0x05FE4468` | `regimm` | `.word       0x05FE4468                   # INVALID     $t7, $fp, 0x4468 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_49.c:10634 | `static_3_800A2FE4` | `0x800A3110` | `0x06597FE0` | `regimm` | `.word       0x06597FE0                   # INVALID     $s2, $t9, 0x7FE0 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_49.c:10636 | `static_3_800A2FE4` | `0x800A3114` | `0x06BA2820` | `regimm` | `.word       0x06BA2820                   # INVALID     $s5, $k0, 0x2820 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_49.c:10640 | `static_3_800A2FE4` | `0x800A311C` | `0x078D0E38` | `regimm` | `.word       0x078D0E38                   # INVALID     $gp, $t5, 0xE38 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_49.c:10644 | `static_3_800A2FE4` | `0x800A311C` | `0x078D0E38` | `regimm` | `.word       0x078D0E38                   # INVALID     $gp, $t5, 0xE38 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_49.c:10646 | `static_3_800A2FE4` | `0x800A3120` | `0x08000040` | `j` | `j           L_80000100` |
| funcs_49.c:10648 | `static_3_800A2FE4` | `0x800A3124` | `0x0879C810` | `j` | `j           L_81E72040` |
| funcs_49.c:10650 | `static_3_800A2FE4` | `0x800A3128` | `0x08FACDB0` | `j` | `j           L_83EB36C0` |
| funcs_49.c:10652 | `static_3_800A2FE4` | `0x800A312C` | `0x09837F50` | `j` | `j           L_860DFD40` |
| funcs_49.c:10654 | `static_3_800A2FE4` | `0x800A3130` | `0x0A1451D0` | `j` | `j           L_88514740` |
| funcs_49.c:10656 | `static_3_800A2FE4` | `0x800A3134` | `0x0AADC0E0` | `j` | `j           L_8AB70380` |
| funcs_49.c:10658 | `static_3_800A2FE4` | `0x800A3138` | `0x0B504F90` | `j` | `j           L_8D413E40` |
| funcs_49.c:10660 | `static_3_800A2FE4` | `0x800A313C` | `0x0BFC88D0` | `j` | `j           L_8FF22340` |
| funcs_49.c:10666 | `static_3_800A2FE4` | `0x800A3150` | `0x10000080` | `beq` | `b           L_800A3354` |
| funcs_49.c:10679 | `static_3_800A2FE4` | `0x800A3150` | `0x10000080` | `beq` | `b           L_800A3354` |
| funcs_49.c:10690 | `static_3_800A2FE4` | `0x800A3150` | `0x10000080` | `beq` | `b           L_800A3354` |
| funcs_49.c:10698 | `static_3_800A2FE4` | `0x800A3150` | `0x10000080` | `beq` | `b           L_800A3354` |
| funcs_49.c:10703 | `static_3_800A2FE4` | `0x800A3150` | `0x10000080` | `beq` | `b           L_800A3354` |
| funcs_49.c:11017 | `static_3_800A2FE4` | `0x800A31B0` | `0x40000200` | `cop0` | `.word       0x40000200                   # mfc0        $zero, Index # 00000200 <InstrIdType: CPU_COP0>` |
| funcs_49.c:11019 | `static_3_800A2FE4` | `0x800A31B4` | `0x43CE4080` | `cop0` | `.word       0x43CE4080                   # INVALID     $fp, $t6, 0x4080 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_49.c:11021 | `static_3_800A2FE4` | `0x800A31B8` | `0x47D66D80` | `cop1` | `.word       0x47D66D80                   # INVALID     $fp, $s6, 0x6D80 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_49.c:11023 | `static_3_800A2FE4` | `0x800A31BC` | `0x4C1BFA80` | `opcode_0x13` | `.word       0x4C1BFA80                   # INVALID     $zero, $k1, -0x580 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:11097 | `static_3_800A50AC` | `0x800A50C0` | `0xF900F30A` | `opcode_0x3E` | `sdc2        $0, -0xCF6($t0)` |
| funcs_49.c:11099 | `static_3_800A50AC` | `0x800A50C4` | `0xEE21EA40` | `opcode_0x3B` | `.word       0xEE21EA40                   # INVALID     $s1, $at, -0x15C0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_49.c:11116 | `static_3_800A50AC` | `0x800A50E0` | `0xF980F452` | `opcode_0x3E` | `sdc2        $0, -0xBAE($t4)` |
| funcs_49.c:11132 | `static_3_800A50AC` | `0x800A50E0` | `0xF980F452` | `opcode_0x3E` | `sdc2        $0, -0xBAE($t4)` |
| funcs_49.c:11145 | `static_3_800A50AC` | `0x800A50E0` | `0xF980F452` | `opcode_0x3E` | `sdc2        $0, -0xBAE($t4)` |
| funcs_49.c:11153 | `static_3_800A50AC` | `0x800A50E0` | `0xF980F452` | `opcode_0x3E` | `sdc2        $0, -0xBAE($t4)` |
| funcs_49.c:11157 | `static_3_800A50AC` | `0x800A50E0` | `0xF980F452` | `opcode_0x3E` | `sdc2        $0, -0xBAE($t4)` |
| funcs_49.c:11159 | `static_3_800A50AC` | `0x800A50E4` | `0xF04CED45` | `opcode_0x3C` | `scd         $t4, -0x12BB($v0)` |
| funcs_49.c:11161 | `static_3_800A50AC` | `0x800A50E8` | `0xEB1BE9AC` | `opcode_0x3A` | `swc2        $27, -0x1654($t8)` |
| funcs_49.c:11163 | `static_3_800A50AC` | `0x800A50EC` | `0xE8DBE88E` | `opcode_0x3A` | `swc2        $27, -0x1772($a2)` |
| funcs_49.c:11172 | `static_3_800A50AC` | `0x800A5100` | `0xF800F000` | `opcode_0x3E` | `sdc2        $0, -0x1000($zero)` |
| funcs_49.c:11188 | `static_3_800A50AC` | `0x800A5100` | `0xF800F000` | `opcode_0x3E` | `sdc2        $0, -0x1000($zero)` |
| funcs_49.c:11201 | `static_3_800A50AC` | `0x800A5100` | `0xF800F000` | `opcode_0x3E` | `sdc2        $0, -0x1000($zero)` |
| funcs_49.c:11209 | `static_3_800A50AC` | `0x800A5100` | `0xF800F000` | `opcode_0x3E` | `sdc2        $0, -0x1000($zero)` |
| funcs_49.c:11213 | `static_3_800A50AC` | `0x800A5100` | `0xF800F000` | `opcode_0x3E` | `sdc2        $0, -0x1000($zero)` |
| funcs_49.c:11215 | `static_3_800A50AC` | `0x800A5104` | `0xE800E000` | `opcode_0x3A` | `swc2        $0, -0x2000($zero)` |
| funcs_49.c:11217 | `static_3_800A50AC` | `0x800A5108` | `0xD800D000` | `opcode_0x36` | `ldc2        $0, -0x3000($zero)` |
| funcs_49.c:11219 | `static_3_800A50AC` | `0x800A510C` | `0xC800C000` | `opcode_0x32` | `lwc2        $0, -0x4000($zero)` |
| funcs_49.c:11221 | `static_3_800A50AC` | `0x800A5110` | `0x10001800` | `beq` | `b           L_800AB114` |
| funcs_49.c:11227 | `static_3_800A50AC` | `0x800A511C` | `0x40004800` | `cop0` | `mfc0        $zero, Count` |
| funcs_49.c:11601 | `static_4_801096D8` | `0x801096F4` | `0x001E000A` | `movz $zero,$zero,$fp` | `movz        $zero, $zero, $fp` |
| funcs_5.c:1316 | `initVideoSubsystem` | `0x8001A6C4` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_5.c:1337 | `initVideoSubsystem` | `0x8001A6DC` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_5.c:1412 | `initVideoSubsystem` | `0x8001A730` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_5.c:1433 | `initVideoSubsystem` | `0x8001A748` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_5.c:1507 | `initVideoSubsystem` | `0x8001A7A0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_5.c:1528 | `initVideoSubsystem` | `0x8001A7B8` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_5.c:1599 | `initVideoSubsystem` | `0x8001A808` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_5.c:1620 | `initVideoSubsystem` | `0x8001A820` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_5.c:2349 | `initVideoSubsystem` | `0x8001ABFC` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_5.c:2370 | `initVideoSubsystem` | `0x8001AC14` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_5.c:3173 | `initVideoSubsystem` | `0x8001B060` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_5.c:3194 | `initVideoSubsystem` | `0x8001B078` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_5.c:3265 | `initVideoSubsystem` | `0x8001B0C8` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_5.c:3286 | `initVideoSubsystem` | `0x8001B0E0` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_5.c:3360 | `initVideoSubsystem` | `0x8001B138` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_5.c:3381 | `initVideoSubsystem` | `0x8001B150` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_5.c:3452 | `initVideoSubsystem` | `0x8001B1A0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_5.c:3473 | `initVideoSubsystem` | `0x8001B1B8` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_5.c:4202 | `initVideoSubsystem` | `0x8001B594` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_5.c:4223 | `initVideoSubsystem` | `0x8001B5AC` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_7.c:3015 | `data_gap_80024A0C` | `0x80024A20` | `0x40022000` | `cop0` | `mfc0        $v0, Context` |
| funcs_7.c:3081 | `data_gap_80024A0C` | `0x80024A74` | `0x0900046C` | `j` | `j           L_840011B0` |
| funcs_7.c:3086 | `data_gap_80024A0C` | `0x80024A7C` | `0x40822000` | `cop0` | `mtc0        $v0, Context` |
| funcs_7.c:3088 | `data_gap_80024A0C` | `0x80024A80` | `0x0000000D` | `break $zero,$zero,$zero` | `break       0` |
| funcs_7.c:3111 | `data_gap_80024A0C` | `0x80024A98` | `0x0900044A` | `j` | `j           L_84001128` |
| funcs_7.c:3154 | `data_gap_80024A0C` | `0x80024ADC` | `0x400B5800` | `cop0` | `mfc0        $t3, Compare` |
| funcs_7.c:3159 | `data_gap_80024A0C` | `0x80024ADC` | `0x400B5800` | `cop0` | `mfc0        $t3, Compare` |
| funcs_7.c:3172 | `data_gap_80024A0C` | `0x80024AEC` | `0x40105000` | `cop0` | `mfc0        $s0, EntryHi` |
| funcs_7.c:3182 | `data_gap_80024A0C` | `0x80024AF8` | `0x40884000` | `cop0` | `mtc0        $t0, BadVaddr` |
| funcs_7.c:3185 | `data_gap_80024A0C` | `0x80024AFC` | `0x40105000` | `cop0` | `mfc0        $s0, EntryHi` |
| funcs_7.c:3224 | `data_gap_80024A0C` | `0x80024B2C` | `0x40904800` | `cop0` | `mtc0        $s0, Count` |
| funcs_7.c:3235 | `data_gap_80024A0C` | `0x80024B38` | `0x0900049A` | `j` | `j           L_84001268` |
| funcs_7.c:3242 | `data_gap_80024A0C` | `0x80024B44` | `0x40043800` | `cop0` | `mfc0        $a0, Reserved07` |
| funcs_7.c:3253 | `data_gap_80024A0C` | `0x80024B50` | `0x40042800` | `cop0` | `mfc0        $a0, PageMask` |
| funcs_7.c:3263 | `data_gap_80024A0C` | `0x80024B5C` | `0x40910000` | `cop0` | `mtc0        $s1, Index` |
| funcs_7.c:3265 | `data_gap_80024A0C` | `0x80024B60` | `0x40820800` | `cop0` | `mtc0        $v0, Random` |
| funcs_7.c:3267 | `data_gap_80024A0C` | `0x80024B64` | `0x40831000` | `cop0` | `mtc0        $v1, EntryLo0` |
| funcs_7.c:3280 | `data_gap_80024A0C` | `0x80024B74` | `0x40043000` | `cop0` | `mfc0        $a0, Wired` |
| funcs_7.c:3290 | `data_gap_80024A0C` | `0x80024B80` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_7.c:3303 | `data_gap_80024A0C` | `0x80024B8C` | `0x40053800` | `cop0` | `mfc0        $a1, Reserved07` |
| funcs_7.c:3307 | `data_gap_80024A0C` | `0x80024B94` | `0x40052800` | `cop0` | `mfc0        $a1, PageMask` |
| funcs_7.c:3312 | `data_gap_80024A0C` | `0x80024B94` | `0x40052800` | `cop0` | `mfc0        $a1, PageMask` |
| funcs_7.c:3322 | `data_gap_80024A0C` | `0x80024BA0` | `0x40820000` | `cop0` | `mtc0        $v0, Index` |
| funcs_7.c:3324 | `data_gap_80024A0C` | `0x80024BA4` | `0x40830800` | `cop0` | `mtc0        $v1, Random` |
| funcs_7.c:3326 | `data_gap_80024A0C` | `0x80024BA8` | `0x40841800` | `cop0` | `mtc0        $a0, EntryLo1` |
| funcs_7.c:3331 | `data_gap_80024A0C` | `0x80024BB0` | `0x40043000` | `cop0` | `mfc0        $a0, Wired` |
| funcs_7.c:3335 | `data_gap_80024A0C` | `0x80024BB0` | `0x40043000` | `cop0` | `mfc0        $a0, Wired` |
| funcs_7.c:3338 | `data_gap_80024A0C` | `0x80024BB8` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_7.c:3341 | `data_gap_80024A0C` | `0x80024BB8` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_7.c:3344 | `data_gap_80024A0C` | `0x80024BBC` | `0x40053800` | `cop0` | `mfc0        $a1, Reserved07` |
| funcs_7.c:3348 | `data_gap_80024A0C` | `0x80024BC4` | `0x40052800` | `cop0` | `mfc0        $a1, PageMask` |
| funcs_7.c:3353 | `data_gap_80024A0C` | `0x80024BC4` | `0x40052800` | `cop0` | `mfc0        $a1, PageMask` |
| funcs_7.c:3363 | `data_gap_80024A0C` | `0x80024BD0` | `0x40830000` | `cop0` | `mtc0        $v1, Index` |
| funcs_7.c:3365 | `data_gap_80024A0C` | `0x80024BD4` | `0x40820800` | `cop0` | `mtc0        $v0, Random` |
| funcs_7.c:3367 | `data_gap_80024A0C` | `0x80024BD8` | `0x40841000` | `cop0` | `mtc0        $a0, EntryLo0` |
| funcs_7.c:3372 | `data_gap_80024A0C` | `0x80024BE0` | `0x40043000` | `cop0` | `mfc0        $a0, Wired` |
| funcs_7.c:3376 | `data_gap_80024A0C` | `0x80024BE0` | `0x40043000` | `cop0` | `mfc0        $a0, Wired` |
| funcs_7.c:3379 | `data_gap_80024A0C` | `0x80024BE8` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_7.c:3382 | `data_gap_80024A0C` | `0x80024BE8` | `0x40803800` | `cop0` | `mtc0        $zero, Reserved07` |
| funcs_7.c:3386 | `data_gap_80024A0C` | `0x80024BF0` | `0x0900049E` | `j` | `j           L_84001278` |
| funcs_7.c:3450 | `data_gap_80024A0C` | `0x80024C4C` | `0x0900046D` | `j` | `j           L_840011B4` |
| funcs_7.c:3478 | `data_gap_80024A0C` | `0x80024C6C` | `0x09000422` | `j` | `j           L_84001088` |
| funcs_7.c:3482 | `data_gap_80024A0C` | `0x80024C74` | `0x090004BC` | `j` | `j           L_840012F0` |
| funcs_7.c:3490 | `data_gap_80024A0C` | `0x80024C84` | `0x090004C9` | `j` | `j           L_84001324` |
| funcs_7.c:3494 | `data_gap_80024A0C` | `0x80024C8C` | `0x090004C2` | `j` | `j           L_84001308` |
| funcs_7.c:3538 | `data_gap_80024A0C` | `0x80024CD8` | `0x0900044B` | `j` | `j           L_8400112C` |
| funcs_7.c:3544 | `data_gap_80024A0C` | `0x80024CE4` | `0x090004DA` | `j` | `j           L_84001368` |
| funcs_7.c:3554 | `data_gap_80024A0C` | `0x80024CF8` | `0x09000436` | `j` | `j           L_840010D8` |
| funcs_7.c:3574 | `data_gap_80024A0C` | `0x80024D18` | `0x09000436` | `j` | `j           L_840010D8` |
| funcs_7.c:3588 | `data_gap_80024A0C` | `0x80024D30` | `0x09000436` | `j` | `j           L_840010D8` |
| funcs_7.c:3691 | `data_gap_80024A0C` | `0x80024DC4` | `0xCA221800` | `opcode_0x32` | `lwc2        $2, 0x1800($s1)` |
| funcs_7.c:3693 | `data_gap_80024A0C` | `0x80024DC8` | `0xCA221C01` | `opcode_0x32` | `lwc2        $2, 0x1C01($s1)` |
| funcs_7.c:3695 | `data_gap_80024A0C` | `0x80024DCC` | `0xCA401809` | `opcode_0x32` | `lwc2        $0, 0x1809($s2)` |
| funcs_7.c:3697 | `data_gap_80024A0C` | `0x80024DD0` | `0xCA401C09` | `opcode_0x32` | `lwc2        $0, 0x1C09($s2)` |
| funcs_7.c:3699 | `data_gap_80024A0C` | `0x80024DD4` | `0xCA411808` | `opcode_0x32` | `lwc2        $1, 0x1808($s2)` |
| funcs_7.c:3701 | `data_gap_80024A0C` | `0x80024DD8` | `0xCA411C08` | `opcode_0x32` | `lwc2        $1, 0x1C08($s2)` |
| funcs_7.c:3703 | `data_gap_80024A0C` | `0x80024DDC` | `0x4A0200C6` | `opcode_0x12` | `.word       0x4A0200C6                   # INVALID     $s0, $v0, 0xC6 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:3705 | `data_gap_80024A0C` | `0x80024DE0` | `0x4A02088F` | `opcode_0x12` | `.word       0x4A02088F                   # INVALID     $s0, $v0, 0x88F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:3709 | `data_gap_80024A0C` | `0x80024DE8` | `0xE9621005` | `opcode_0x3A` | `swc2        $2, 0x1005($t3)` |
| funcs_7.c:3711 | `data_gap_80024A0C` | `0x80024DEC` | `0xE9821205` | `opcode_0x3A` | `swc2        $2, 0x1205($t4)` |
| funcs_7.c:3713 | `data_gap_80024A0C` | `0x80024DF0` | `0xE9A21405` | `opcode_0x3A` | `swc2        $2, 0x1405($t5)` |
| funcs_7.c:3742 | `data_gap_80024A0C` | `0x80024E0C` | `0x0900044B` | `j` | `j           L_8400112C` |
| funcs_7.c:3762 | `data_gap_80024A0C` | `0x80024E28` | `0xE9E21605` | `opcode_0x3A` | `swc2        $2, 0x1605($t7)` |
| funcs_7.c:3806 | `data_gap_80024A0C` | `0x80024E5C` | `0x0900044B` | `j` | `j           L_8400112C` |
| funcs_7.c:3812 | `data_gap_80024A0C` | `0x80024E68` | `0xCA201800` | `opcode_0x32` | `lwc2        $0, 0x1800($s1)` |
| funcs_7.c:3814 | `data_gap_80024A0C` | `0x80024E6C` | `0xCA201C01` | `opcode_0x32` | `lwc2        $0, 0x1C01($s1)` |
| funcs_7.c:3820 | `data_gap_80024A0C` | `0x80024E78` | `0x09000436` | `j` | `j           L_840010D8` |
| funcs_7.c:3822 | `data_gap_80024A0C` | `0x80024E7C` | `0xE8402000` | `opcode_0x3A` | `swc2        $0, 0x2000($v0)` |
| funcs_7.c:3830 | `data_gap_80024A0C` | `0x80024E8C` | `0x0900048B` | `j` | `j           L_8400122C` |
| funcs_7.c:3873 | `data_gap_80024A0C` | `0x80024EC8` | `0x09000550` | `j` | `j           L_84001540` |
| funcs_7.c:3880 | `data_gap_80024A0C` | `0x80024ED4` | `0x4B1EF147` | `opcode_0x12` | `.word       0x4B1EF147                   # INVALID     $t8, $fp, -0xEB9 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:3885 | `data_gap_80024A0C` | `0x80024EDC` | `0xC9231800` | `opcode_0x32` | `lwc2        $3, 0x1800($t1)` |
| funcs_7.c:3887 | `data_gap_80024A0C` | `0x80024EE0` | `0xC9241804` | `opcode_0x32` | `lwc2        $4, 0x1804($t1)` |
| funcs_7.c:3889 | `data_gap_80024A0C` | `0x80024EE4` | `0xC9012000` | `opcode_0x32` | `lwc2        $1, 0x2000($t0)` |
| funcs_7.c:3891 | `data_gap_80024A0C` | `0x80024EE8` | `0xC9022002` | `opcode_0x32` | `lwc2        $2, 0x2002($t0)` |
| funcs_7.c:3893 | `data_gap_80024A0C` | `0x80024EEC` | `0xC9231C00` | `opcode_0x32` | `lwc2        $3, 0x1C00($t1)` |
| funcs_7.c:3895 | `data_gap_80024A0C` | `0x80024EF0` | `0xC9241C04` | `opcode_0x32` | `lwc2        $4, 0x1C04($t1)` |
| funcs_7.c:3897 | `data_gap_80024A0C` | `0x80024EF4` | `0x4A82218C` | `opcode_0x12` | `.word       0x4A82218C                   # INVALID     $s4, $v0, 0x218C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:3901 | `data_gap_80024A0C` | `0x80024EFC` | `0x4A82198D` | `opcode_0x12` | `.word       0x4A82198D                   # INVALID     $s4, $v0, 0x198D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:3905 | `data_gap_80024A0C` | `0x80024F04` | `0x4A81218E` | `opcode_0x12` | `.word       0x4A81218E                   # INVALID     $s4, $at, 0x218E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:3907 | `data_gap_80024A0C` | `0x80024F08` | `0x4A81194F` | `opcode_0x12` | `.word       0x4A81194F                   # INVALID     $s4, $at, 0x194F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:3911 | `data_gap_80024A0C` | `0x80024F10` | `0x4B1EF18E` | `opcode_0x12` | `.word       0x4B1EF18E                   # INVALID     $t8, $fp, -0xE72 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:3915 | `data_gap_80024A0C` | `0x80024F10` | `0x4B1EF18E` | `opcode_0x12` | `.word       0x4B1EF18E                   # INVALID     $t8, $fp, -0xE72 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:3921 | `data_gap_80024A0C` | `0x80024F1C` | `0xE9452000` | `opcode_0x3A` | `swc2        $5, 0x2000($t2)` |
| funcs_7.c:3923 | `data_gap_80024A0C` | `0x80024F20` | `0xE9462002` | `opcode_0x3A` | `swc2        $6, 0x2002($t2)` |
| funcs_7.c:3939 | `data_gap_80024A0C` | `0x80024F34` | `0x0900049A` | `j` | `j           L_84001268` |
| funcs_7.c:3943 | `data_gap_80024A0C` | `0x80024F3C` | `0x0900049A` | `j` | `j           L_84001268` |
| funcs_7.c:3973 | `data_gap_80024A0C` | `0x80024F68` | `0xC8481800` | `opcode_0x32` | `lwc2        $8, 0x1800($v0)` |
| funcs_7.c:3975 | `data_gap_80024A0C` | `0x80024F6C` | `0xC8491801` | `opcode_0x32` | `lwc2        $9, 0x1801($v0)` |
| funcs_7.c:3977 | `data_gap_80024A0C` | `0x80024F70` | `0xC84A1802` | `opcode_0x32` | `lwc2        $10, 0x1802($v0)` |
| funcs_7.c:3979 | `data_gap_80024A0C` | `0x80024F74` | `0xC84B1803` | `opcode_0x32` | `lwc2        $11, 0x1803($v0)` |
| funcs_7.c:3981 | `data_gap_80024A0C` | `0x80024F78` | `0xC84C1804` | `opcode_0x32` | `lwc2        $12, 0x1804($v0)` |
| funcs_7.c:3983 | `data_gap_80024A0C` | `0x80024F7C` | `0xC84D1805` | `opcode_0x32` | `lwc2        $13, 0x1805($v0)` |
| funcs_7.c:3985 | `data_gap_80024A0C` | `0x80024F80` | `0xC84E1806` | `opcode_0x32` | `lwc2        $14, 0x1806($v0)` |
| funcs_7.c:3987 | `data_gap_80024A0C` | `0x80024F84` | `0xC84F1807` | `opcode_0x32` | `lwc2        $15, 0x1807($v0)` |
| funcs_7.c:3989 | `data_gap_80024A0C` | `0x80024F88` | `0xC8481C00` | `opcode_0x32` | `lwc2        $8, 0x1C00($v0)` |
| funcs_7.c:3991 | `data_gap_80024A0C` | `0x80024F8C` | `0xC8491C01` | `opcode_0x32` | `lwc2        $9, 0x1C01($v0)` |
| funcs_7.c:3993 | `data_gap_80024A0C` | `0x80024F90` | `0xC84A1C02` | `opcode_0x32` | `lwc2        $10, 0x1C02($v0)` |
| funcs_7.c:3995 | `data_gap_80024A0C` | `0x80024F94` | `0xC84B1C03` | `opcode_0x32` | `lwc2        $11, 0x1C03($v0)` |
| funcs_7.c:3997 | `data_gap_80024A0C` | `0x80024F98` | `0xC84C1C04` | `opcode_0x32` | `lwc2        $12, 0x1C04($v0)` |
| funcs_7.c:3999 | `data_gap_80024A0C` | `0x80024F9C` | `0xC84D1C05` | `opcode_0x32` | `lwc2        $13, 0x1C05($v0)` |
| funcs_7.c:4001 | `data_gap_80024A0C` | `0x80024FA0` | `0xC84E1C06` | `opcode_0x32` | `lwc2        $14, 0x1C06($v0)` |
| funcs_7.c:4003 | `data_gap_80024A0C` | `0x80024FA4` | `0xC84F1C07` | `opcode_0x32` | `lwc2        $15, 0x1C07($v0)` |
| funcs_7.c:4011 | `data_gap_80024A0C` | `0x80024FB4` | `0xC9A22000` | `opcode_0x32` | `lwc2        $2, 0x2000($t5)` |
| funcs_7.c:4016 | `data_gap_80024A0C` | `0x80024FBC` | `0x4A826706` | `opcode_0x12` | `.word       0x4A826706                   # INVALID     $s4, $v0, 0x6706 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4020 | `data_gap_80024A0C` | `0x80024FC4` | `0x4A82470F` | `opcode_0x12` | `.word       0x4A82470F                   # INVALID     $s4, $v0, 0x470F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4022 | `data_gap_80024A0C` | `0x80024FC8` | `0x4AA26F0E` | `opcode_0x12` | `.word       0x4AA26F0E                   # INVALID     $s5, $v0, 0x6F0E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4024 | `data_gap_80024A0C` | `0x80024FCC` | `0x4AA24F0F` | `opcode_0x12` | `.word       0x4AA24F0F                   # INVALID     $s5, $v0, 0x4F0F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4026 | `data_gap_80024A0C` | `0x80024FD0` | `0x4AC2770E` | `opcode_0x12` | `.word       0x4AC2770E                   # INVALID     $s6, $v0, 0x770E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4028 | `data_gap_80024A0C` | `0x80024FD4` | `0x4AC2570F` | `opcode_0x12` | `.word       0x4AC2570F                   # INVALID     $s6, $v0, 0x570F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4030 | `data_gap_80024A0C` | `0x80024FD8` | `0x4B3E7F0E` | `opcode_0x12` | `.word       0x4B3E7F0E                   # INVALID     $t9, $fp, 0x7F0E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4032 | `data_gap_80024A0C` | `0x80024FDC` | `0x4B3E5F4F` | `opcode_0x12` | `.word       0x4B3E5F4F                   # INVALID     $t9, $fp, 0x5F4F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4034 | `data_gap_80024A0C` | `0x80024FE0` | `0xC8150803` | `opcode_0x32` | `lwc2        $21, 0x803($zero)` |
| funcs_7.c:4036 | `data_gap_80024A0C` | `0x80024FE4` | `0x4B15E506` | `opcode_0x12` | `.word       0x4B15E506                   # INVALID     $t8, $s5, -0x1AFA # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4038 | `data_gap_80024A0C` | `0x80024FE8` | `0x4B15ED4F` | `opcode_0x12` | `.word       0x4B15ED4F                   # INVALID     $t8, $s5, -0x12B1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4040 | `data_gap_80024A0C` | `0x80024FEC` | `0x4AFDE8E5` | `opcode_0x12` | `.word       0x4AFDE8E5                   # INVALID     $s7, $sp, -0x171B # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4042 | `data_gap_80024A0C` | `0x80024FF0` | `0x4AFCE0E4` | `opcode_0x12` | `.word       0x4AFCE0E4                   # INVALID     $s7, $gp, -0x1F1C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4044 | `data_gap_80024A0C` | `0x80024FF4` | `0x484B0800` | `opcode_0x12` | `cfc2        $t3, $1` |
| funcs_7.c:4046 | `data_gap_80024A0C` | `0x80024FF8` | `0x4AF5E8E5` | `opcode_0x12` | `.word       0x4AF5E8E5                   # INVALID     $s7, $s5, -0x171B # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4048 | `data_gap_80024A0C` | `0x80024FFC` | `0x4AF4E0E4` | `opcode_0x12` | `.word       0x4AF4E0E4                   # INVALID     $s7, $s4, -0x1F1C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4060 | `data_gap_80024A0C` | `0x80025014` | `0x484C0800` | `opcode_0x12` | `cfc2        $t4, $1` |
| funcs_7.c:4062 | `data_gap_80024A0C` | `0x80025018` | `0x4B1EED50` | `opcode_0x12` | `.word       0x4B1EED50                   # INVALID     $t8, $fp, -0x12B0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4068 | `data_gap_80024A0C` | `0x80025024` | `0x4B1EE510` | `opcode_0x12` | `.word       0x4B1EE510                   # INVALID     $t8, $fp, -0x1AF0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4072 | `data_gap_80024A0C` | `0x8002502C` | `0x4B13E704` | `opcode_0x12` | `.word       0x4B13E704                   # INVALID     $t8, $s3, -0x18FC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4076 | `data_gap_80024A0C` | `0x80025034` | `0x4B13EF4D` | `opcode_0x12` | `.word       0x4B13EF4D                   # INVALID     $t8, $s3, -0x10B3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4080 | `data_gap_80024A0C` | `0x8002503C` | `0x4B1EF70E` | `opcode_0x12` | `.word       0x4B1EF70E                   # INVALID     $t8, $fp, -0x8F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4094 | `data_gap_80024A0C` | `0x80025048` | `0x4B1ED9A3` | `opcode_0x12` | `.word       0x4B1ED9A3                   # INVALID     $t8, $fp, -0x265D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4096 | `data_gap_80024A0C` | `0x8002504C` | `0x4B1FD9A7` | `opcode_0x12` | `.word       0x4B1FD9A7                   # INVALID     $t8, $ra, -0x2659 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4098 | `data_gap_80024A0C` | `0x80025050` | `0xE9351800` | `opcode_0x3A` | `swc2        $21, 0x1800($t1)` |
| funcs_7.c:4100 | `data_gap_80024A0C` | `0x80025054` | `0xE9341801` | `opcode_0x3A` | `swc2        $20, 0x1801($t1)` |
| funcs_7.c:4102 | `data_gap_80024A0C` | `0x80025058` | `0x4AFAA144` | `opcode_0x12` | `.word       0x4AFAA144                   # INVALID     $s7, $k0, -0x5EBC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4104 | `data_gap_80024A0C` | `0x8002505C` | `0x4AFAA94D` | `opcode_0x12` | `.word       0x4AFAA94D                   # INVALID     $s7, $k0, -0x56B3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4106 | `data_gap_80024A0C` | `0x80025060` | `0x4AE6A14E` | `opcode_0x12` | `.word       0x4AE6A14E                   # INVALID     $s7, $a2, -0x5EB2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4108 | `data_gap_80024A0C` | `0x80025064` | `0x4AE6A90F` | `opcode_0x12` | `.word       0x4AE6A90F                   # INVALID     $s7, $a2, -0x56F1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4112 | `data_gap_80024A0C` | `0x8002506C` | `0x4B132944` | `opcode_0x12` | `.word       0x4B132944                   # INVALID     $t8, $s3, 0x2944 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4114 | `data_gap_80024A0C` | `0x80025070` | `0x4B13210D` | `opcode_0x12` | `.word       0x4B13210D                   # INVALID     $t8, $s3, 0x210D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4116 | `data_gap_80024A0C` | `0x80025074` | `0x4B1EF14E` | `opcode_0x12` | `.word       0x4B1EF14E                   # INVALID     $t8, $fp, -0xEB2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4118 | `data_gap_80024A0C` | `0x80025078` | `0x4B3E09C7` | `opcode_0x12` | `.word       0x4B3E09C7                   # INVALID     $t9, $fp, 0x9C7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4120 | `data_gap_80024A0C` | `0x8002507C` | `0xC9A22000` | `opcode_0x32` | `lwc2        $2, 0x2000($t5)` |
| funcs_7.c:4122 | `data_gap_80024A0C` | `0x80025080` | `0x4A0029CE` | `opcode_0x12` | `.word       0x4A0029CE                   # INVALID     $s0, $zero, 0x29CE # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4124 | `data_gap_80024A0C` | `0x80025084` | `0xC81D180C` | `opcode_0x32` | `lwc2        $29, 0x180C($zero)` |
| funcs_7.c:4126 | `data_gap_80024A0C` | `0x80025088` | `0x4A00218F` | `opcode_0x12` | `.word       0x4A00218F                   # INVALID     $s0, $zero, 0x218F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4128 | `data_gap_80024A0C` | `0x8002508C` | `0xC81D1C0C` | `opcode_0x32` | `lwc2        $29, 0x1C0C($zero)` |
| funcs_7.c:4130 | `data_gap_80024A0C` | `0x80025090` | `0x4B1EF1CE` | `opcode_0x12` | `.word       0x4B1EF1CE                   # INVALID     $t8, $fp, -0xE32 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4134 | `data_gap_80024A0C` | `0x80025098` | `0x4A7D31A3` | `opcode_0x12` | `.word       0x4A7D31A3                   # INVALID     $s3, $sp, 0x31A3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4138 | `data_gap_80024A0C` | `0x80025098` | `0x4A7D31A3` | `opcode_0x12` | `.word       0x4A7D31A3                   # INVALID     $s3, $sp, 0x31A3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4140 | `data_gap_80024A0C` | `0x8002509C` | `0xC8032016` | `opcode_0x32` | `lwc2        $3, 0x2016($zero)` |
| funcs_7.c:4142 | `data_gap_80024A0C` | `0x800250A0` | `0x4B232C04` | `opcode_0x12` | `.word       0x4B232C04                   # INVALID     $t9, $v1, 0x2C04 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4144 | `data_gap_80024A0C` | `0x800250A4` | `0x4B23240D` | `opcode_0x12` | `.word       0x4B23240D                   # INVALID     $t9, $v1, 0x240D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4146 | `data_gap_80024A0C` | `0x800250A8` | `0x4B03294E` | `opcode_0x12` | `.word       0x4B03294E                   # INVALID     $t8, $v1, 0x294E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4148 | `data_gap_80024A0C` | `0x800250AC` | `0x4B03210F` | `opcode_0x12` | `.word       0x4B03210F                   # INVALID     $t8, $v1, 0x210F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4150 | `data_gap_80024A0C` | `0x800250B0` | `0x4B632954` | `opcode_0x12` | `.word       0x4B632954                   # INVALID     $k1, $v1, 0x2954 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4152 | `data_gap_80024A0C` | `0x800250B4` | `0x4B432110` | `opcode_0x12` | `.word       0x4B432110                   # INVALID     $k0, $v1, 0x2110 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4154 | `data_gap_80024A0C` | `0x800250B8` | `0x4B832946` | `opcode_0x12` | `.word       0x4B832946                   # INVALID     $gp, $v1, 0x2946 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4156 | `data_gap_80024A0C` | `0x800250BC` | `0x4B83210F` | `opcode_0x12` | `.word       0x4B83210F                   # INVALID     $gp, $v1, 0x210F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4158 | `data_gap_80024A0C` | `0x800250C0` | `0x4B1E2123` | `opcode_0x12` | `.word       0x4B1E2123                   # INVALID     $t8, $fp, 0x2123 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4160 | `data_gap_80024A0C` | `0x800250C4` | `0x4B832120` | `opcode_0x12` | `.word       0x4B832120                   # INVALID     $gp, $v1, 0x2120 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4162 | `data_gap_80024A0C` | `0x800250C8` | `0xE9240293` | `opcode_0x3A` | `swc2        $4, 0x293($t1)` |
| funcs_7.c:4164 | `data_gap_80024A0C` | `0x800250CC` | `0xE92406BB` | `opcode_0x3A` | `swc2        $4, 0x6BB($t1)` |
| funcs_7.c:4167 | `data_gap_80024A0C` | `0x800250D0` | `0xE9261803` | `opcode_0x3A` | `swc2        $6, 0x1803($t1)` |
| funcs_7.c:4169 | `data_gap_80024A0C` | `0x800250D4` | `0xE9270A0F` | `opcode_0x3A` | `swc2        $7, 0xA0F($t1)` |
| funcs_7.c:4171 | `data_gap_80024A0C` | `0x800250D8` | `0xE93B0B10` | `opcode_0x3A` | `swc2        $27, 0xB10($t1)` |
| funcs_7.c:4175 | `data_gap_80024A0C` | `0x800250E0` | `0xE93A0B11` | `opcode_0x3A` | `swc2        $26, 0xB11($t1)` |
| funcs_7.c:4179 | `data_gap_80024A0C` | `0x800250E0` | `0xE93A0B11` | `opcode_0x3A` | `swc2        $26, 0xB11($t1)` |
| funcs_7.c:4181 | `data_gap_80024A0C` | `0x800250E4` | `0xE9351C05` | `opcode_0x3A` | `swc2        $21, 0x1C05($t1)` |
| funcs_7.c:4183 | `data_gap_80024A0C` | `0x800250E8` | `0xE9341C06` | `opcode_0x3A` | `swc2        $20, 0x1C06($t1)` |
| funcs_7.c:4185 | `data_gap_80024A0C` | `0x800250EC` | `0xE9261C08` | `opcode_0x3A` | `swc2        $6, 0x1C08($t1)` |
| funcs_7.c:4191 | `data_gap_80024A0C` | `0x800250F4` | `0xE9270E23` | `opcode_0x3A` | `swc2        $7, 0xE23($t1)` |
| funcs_7.c:4193 | `data_gap_80024A0C` | `0x800250F8` | `0xE93B0F24` | `opcode_0x3A` | `swc2        $27, 0xF24($t1)` |
| funcs_7.c:4195 | `data_gap_80024A0C` | `0x800250FC` | `0xE93A0F25` | `opcode_0x3A` | `swc2        $26, 0xF25($t1)` |
| funcs_7.c:4213 | `data_gap_80024A0C` | `0x80025110` | `0xCA401804` | `opcode_0x32` | `lwc2        $0, 0x1804($s2)` |
| funcs_7.c:4215 | `data_gap_80024A0C` | `0x80025114` | `0xCA411805` | `opcode_0x32` | `lwc2        $1, 0x1805($s2)` |
| funcs_7.c:4217 | `data_gap_80024A0C` | `0x80025118` | `0xCA401C04` | `opcode_0x32` | `lwc2        $0, 0x1C04($s2)` |
| funcs_7.c:4219 | `data_gap_80024A0C` | `0x8002511C` | `0xCA411C05` | `opcode_0x32` | `lwc2        $1, 0x1C05($s2)` |
| funcs_7.c:4221 | `data_gap_80024A0C` | `0x80025120` | `0xCA53081F` | `opcode_0x32` | `lwc2        $19, 0x81F($s2)` |
| funcs_7.c:4229 | `data_gap_80024A0C` | `0x8002512C` | `0x4B7D5EF2` | `opcode_0x12` | `.word       0x4B7D5EF2                   # INVALID     $k1, $sp, 0x5EF2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4231 | `data_gap_80024A0C` | `0x80025130` | `0x4B7C5EB1` | `opcode_0x12` | `.word       0x4B7C5EB1                   # INVALID     $k1, $gp, 0x5EB1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4233 | `data_gap_80024A0C` | `0x80025134` | `0x4BFD5EF2` | `opcode_0x12` | `.word       0x4BFD5EF2                   # INVALID     $ra, $sp, 0x5EF2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4235 | `data_gap_80024A0C` | `0x80025138` | `0x4BFC7EB1` | `opcode_0x12` | `.word       0x4BFC7EB1                   # INVALID     $ra, $gp, 0x7EB1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4237 | `data_gap_80024A0C` | `0x8002513C` | `0x4B1E7EF2` | `opcode_0x12` | `.word       0x4B1E7EF2                   # INVALID     $t8, $fp, 0x7EF2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4239 | `data_gap_80024A0C` | `0x80025140` | `0x4B5ED686` | `opcode_0x12` | `.word       0x4B5ED686                   # INVALID     $k0, $fp, -0x297A # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4241 | `data_gap_80024A0C` | `0x80025144` | `0x4B5EDECF` | `opcode_0x12` | `.word       0x4B5EDECF                   # INVALID     $k0, $fp, -0x2131 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4243 | `data_gap_80024A0C` | `0x80025148` | `0x4B1EF68E` | `opcode_0x12` | `.word       0x4B1EF68E                   # INVALID     $t8, $fp, -0x972 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4245 | `data_gap_80024A0C` | `0x8002514C` | `0xC8172005` | `opcode_0x32` | `lwc2        $23, 0x2005($zero)` |
| funcs_7.c:4247 | `data_gap_80024A0C` | `0x80025150` | `0x4A1EF5AC` | `opcode_0x12` | `.word       0x4A1EF5AC                   # INVALID     $s0, $fp, -0xA54 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4249 | `data_gap_80024A0C` | `0x80025154` | `0x4A1CD604` | `opcode_0x12` | `.word       0x4A1CD604                   # INVALID     $s0, $gp, -0x29FC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4251 | `data_gap_80024A0C` | `0x80025158` | `0x4A1CDE0D` | `opcode_0x12` | `.word       0x4A1CDE0D                   # INVALID     $s0, $gp, -0x21F3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4253 | `data_gap_80024A0C` | `0x8002515C` | `0x4A1DD60E` | `opcode_0x12` | `.word       0x4A1DD60E                   # INVALID     $s0, $sp, -0x29F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4255 | `data_gap_80024A0C` | `0x80025160` | `0x4A1DDE4F` | `opcode_0x12` | `.word       0x4A1DDE4F                   # INVALID     $s0, $sp, -0x21B1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4257 | `data_gap_80024A0C` | `0x80025164` | `0x4A18B615` | `opcode_0x12` | `.word       0x4A18B615                   # INVALID     $s0, $t8, -0x49EB # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4259 | `data_gap_80024A0C` | `0x80025168` | `0x4A19BE51` | `opcode_0x12` | `.word       0x4A19BE51                   # INVALID     $s0, $t9, -0x41AF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4261 | `data_gap_80024A0C` | `0x8002516C` | `0x4A18D584` | `opcode_0x12` | `.word       0x4A18D584                   # INVALID     $s0, $t8, -0x2A7C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4263 | `data_gap_80024A0C` | `0x80025170` | `0x4A18DDCD` | `opcode_0x12` | `.word       0x4A18DDCD                   # INVALID     $s0, $t8, -0x2233 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4265 | `data_gap_80024A0C` | `0x80025174` | `0x4A19D68E` | `opcode_0x12` | `.word       0x4A19D68E                   # INVALID     $s0, $t9, -0x2972 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4268 | `data_gap_80024A0C` | `0x8002517C` | `0x4A19DECF` | `opcode_0x12` | `.word       0x4A19DECF                   # INVALID     $s0, $t9, -0x2131 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4271 | `data_gap_80024A0C` | `0x8002517C` | `0x4A19DECF` | `opcode_0x12` | `.word       0x4A19DECF                   # INVALID     $s0, $t9, -0x2131 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4305 | `data_gap_80024A0C` | `0x800251B0` | `0x0900049A` | `j` | `j           L_84001268` |
| funcs_7.c:4312 | `data_gap_80024A0C` | `0x800251BC` | `0xC96D1006` | `opcode_0x32` | `lwc2        $13, 0x1006($t3)` |
| funcs_7.c:4314 | `data_gap_80024A0C` | `0x800251C0` | `0xC98E1006` | `opcode_0x32` | `lwc2        $14, 0x1006($t4)` |
| funcs_7.c:4316 | `data_gap_80024A0C` | `0x800251C4` | `0xC9AF1006` | `opcode_0x32` | `lwc2        $15, 0x1006($t5)` |
| funcs_7.c:4322 | `data_gap_80024A0C` | `0x800251D0` | `0xCA55081F` | `opcode_0x32` | `lwc2        $21, 0x81F($s2)` |
| funcs_7.c:4324 | `data_gap_80024A0C` | `0x800251D4` | `0xC9650803` | `opcode_0x32` | `lwc2        $5, 0x803($t3)` |
| funcs_7.c:4326 | `data_gap_80024A0C` | `0x800251D8` | `0x4A0D7291` | `opcode_0x12` | `.word       0x4A0D7291                   # INVALID     $s0, $t5, 0x7291 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4328 | `data_gap_80024A0C` | `0x800251DC` | `0xC9660807` | `opcode_0x32` | `lwc2        $6, 0x807($t3)` |
| funcs_7.c:4330 | `data_gap_80024A0C` | `0x800251E0` | `0x4A0D7A51` | `opcode_0x12` | `.word       0x4A0D7A51                   # INVALID     $s0, $t5, 0x7A51 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4332 | `data_gap_80024A0C` | `0x800251E4` | `0xC9850903` | `opcode_0x32` | `lwc2        $5, 0x903($t4)` |
| funcs_7.c:4334 | `data_gap_80024A0C` | `0x800251E8` | `0x4A0E6B11` | `opcode_0x12` | `.word       0x4A0E6B11                   # INVALID     $s0, $t6, 0x6B11 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4336 | `data_gap_80024A0C` | `0x800251EC` | `0xC9860907` | `opcode_0x32` | `lwc2        $6, 0x907($t4)` |
| funcs_7.c:4338 | `data_gap_80024A0C` | `0x800251F0` | `0xC9A50A03` | `opcode_0x32` | `lwc2        $5, 0xA03($t5)` |
| funcs_7.c:4340 | `data_gap_80024A0C` | `0x800251F4` | `0xC9A60A07` | `opcode_0x32` | `lwc2        $6, 0xA07($t5)` |
| funcs_7.c:4342 | `data_gap_80024A0C` | `0x800251F8` | `0x4B2A4C07` | `opcode_0x12` | `.word       0x4B2A4C07                   # INVALID     $t9, $t2, 0x4C07 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4346 | `data_gap_80024A0C` | `0x80025200` | `0x4B29640F` | `opcode_0x12` | `.word       0x4B29640F                   # INVALID     $t9, $t1, 0x640F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4350 | `data_gap_80024A0C` | `0x80025208` | `0x4B3CE71D` | `opcode_0x12` | `.word       0x4B3CE71D                   # INVALID     $t9, $gp, -0x18E3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4354 | `data_gap_80024A0C` | `0x80025210` | `0x4B1DEF5D` | `opcode_0x12` | `.word       0x4B1DEF5D                   # INVALID     $t8, $sp, -0x10A3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4358 | `data_gap_80024A0C` | `0x80025218` | `0x48048000` | `opcode_0x12` | `mfc2        $a0, $16` |
| funcs_7.c:4402 | `data_gap_80024A0C` | `0x80025268` | `0xC9AF1006` | `opcode_0x32` | `lwc2        $15, 0x1006($t5)` |
| funcs_7.c:4404 | `data_gap_80024A0C` | `0x8002526C` | `0xC98E1006` | `opcode_0x32` | `lwc2        $14, 0x1006($t4)` |
| funcs_7.c:4408 | `data_gap_80024A0C` | `0x80025274` | `0xC96D1006` | `opcode_0x32` | `lwc2        $13, 0x1006($t3)` |
| funcs_7.c:4412 | `data_gap_80024A0C` | `0x80025274` | `0xC96D1006` | `opcode_0x32` | `lwc2        $13, 0x1006($t3)` |
| funcs_7.c:4414 | `data_gap_80024A0C` | `0x80025278` | `0x4A1CF715` | `opcode_0x12` | `.word       0x4A1CF715                   # INVALID     $s0, $gp, -0x8EB # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4416 | `data_gap_80024A0C` | `0x8002527C` | `0x4A1DF751` | `opcode_0x12` | `.word       0x4A1DF751                   # INVALID     $s0, $sp, -0x8AF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4421 | `data_gap_80024A0C` | `0x80025284` | `0x4A0E7911` | `opcode_0x12` | `.word       0x4A0E7911                   # INVALID     $s0, $t6, 0x7911 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4425 | `data_gap_80024A0C` | `0x80025284` | `0x4A0E7911` | `opcode_0x12` | `.word       0x4A0E7911                   # INVALID     $s0, $t6, 0x7911 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4427 | `data_gap_80024A0C` | `0x80025288` | `0x4A0D7291` | `opcode_0x12` | `.word       0x4A0D7291                   # INVALID     $s0, $t5, 0x7291 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4429 | `data_gap_80024A0C` | `0x8002528C` | `0x4A0D7A51` | `opcode_0x12` | `.word       0x4A0D7A51                   # INVALID     $s0, $t5, 0x7A51 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4431 | `data_gap_80024A0C` | `0x80025290` | `0x4B1D5F73` | `opcode_0x12` | `.word       0x4B1D5F73                   # INVALID     $t8, $sp, 0x5F73 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4433 | `data_gap_80024A0C` | `0x80025294` | `0x4B1C5F33` | `opcode_0x12` | `.word       0x4B1C5F33                   # INVALID     $t8, $gp, 0x5F33 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4435 | `data_gap_80024A0C` | `0x80025298` | `0xEA0F0901` | `opcode_0x3A` | `swc2        $15, 0x901($s0)` |
| funcs_7.c:4437 | `data_gap_80024A0C` | `0x8002529C` | `0x4B0A5133` | `opcode_0x12` | `.word       0x4B0A5133                   # INVALID     $t8, $t2, 0x5133 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4439 | `data_gap_80024A0C` | `0x800252A0` | `0xEA0E0902` | `opcode_0x3A` | `swc2        $14, 0x902($s0)` |
| funcs_7.c:4441 | `data_gap_80024A0C` | `0x800252A4` | `0x4B2A5933` | `opcode_0x12` | `.word       0x4B2A5933                   # INVALID     $t9, $t2, 0x5933 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4443 | `data_gap_80024A0C` | `0x800252A8` | `0xEA0D0903` | `opcode_0x3A` | `swc2        $13, 0x903($s0)` |
| funcs_7.c:4445 | `data_gap_80024A0C` | `0x800252AC` | `0x4B096133` | `opcode_0x12` | `.word       0x4B096133                   # INVALID     $t8, $t1, 0x6133 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4447 | `data_gap_80024A0C` | `0x800252B0` | `0x480EEA80` | `opcode_0x12` | `.word       0x480EEA80                   # mfc2        $t6, $29 # 00000280 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4449 | `data_gap_80024A0C` | `0x800252B4` | `0x4B296933` | `opcode_0x12` | `.word       0x4B296933                   # INVALID     $t9, $t1, 0x6933 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4452 | `data_gap_80024A0C` | `0x800252BC` | `0x4B9E6886` | `opcode_0x12` | `.word       0x4B9E6886                   # INVALID     $gp, $fp, 0x6886 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4456 | `data_gap_80024A0C` | `0x800252BC` | `0x4B9E6886` | `opcode_0x12` | `.word       0x4B9E6886                   # INVALID     $gp, $fp, 0x6886 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4461 | `data_gap_80024A0C` | `0x800252C4` | `0x4B9E2245` | `opcode_0x12` | `.word       0x4B9E2245                   # INVALID     $gp, $fp, 0x2245 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4463 | `data_gap_80024A0C` | `0x800252C8` | `0x4B1EF28E` | `opcode_0x12` | `.word       0x4B1EF28E                   # INVALID     $t8, $fp, -0xD72 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4467 | `data_gap_80024A0C` | `0x800252D0` | `0x4B244A30` | `opcode_0x12` | `.word       0x4B244A30                   # INVALID     $t9, $a0, 0x4A30 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4471 | `data_gap_80024A0C` | `0x800252D8` | `0x4B1E49F2` | `opcode_0x12` | `.word       0x4B1E49F2                   # INVALID     $t8, $fp, 0x49F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4475 | `data_gap_80024A0C` | `0x800252E0` | `0x4B645A30` | `opcode_0x12` | `.word       0x4B645A30                   # INVALID     $k1, $a0, 0x5A30 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4477 | `data_gap_80024A0C` | `0x800252E4` | `0x4B1E59F2` | `opcode_0x12` | `.word       0x4B1E59F2                   # INVALID     $t8, $fp, 0x59F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4479 | `data_gap_80024A0C` | `0x800252E8` | `0x4BA46A30` | `opcode_0x12` | `.word       0x4BA46A30                   # INVALID     $sp, $a0, 0x6A30 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4481 | `data_gap_80024A0C` | `0x800252EC` | `0x4B1E69F2` | `opcode_0x12` | `.word       0x4B1E69F2                   # INVALID     $t8, $fp, 0x69F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4485 | `data_gap_80024A0C` | `0x800252F4` | `0x4B9F4204` | `opcode_0x12` | `.word       0x4B9F4204                   # INVALID     $gp, $ra, 0x4204 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4491 | `data_gap_80024A0C` | `0x800252FC` | `0x4B9F39CD` | `opcode_0x12` | `.word       0x4B9F39CD                   # INVALID     $gp, $ra, 0x39CD # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4497 | `data_gap_80024A0C` | `0x80025304` | `0x4B1EF20E` | `opcode_0x12` | `.word       0x4B1EF20E                   # INVALID     $t8, $fp, -0xDF2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4499 | `data_gap_80024A0C` | `0x80025308` | `0x4BBE2107` | `opcode_0x12` | `.word       0x4BBE2107                   # INVALID     $sp, $fp, 0x2107 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4501 | `data_gap_80024A0C` | `0x8002530C` | `0xC98C080C` | `opcode_0x32` | `lwc2        $12, 0x80C($t4)` |
| funcs_7.c:4503 | `data_gap_80024A0C` | `0x80025310` | `0x4B153184` | `opcode_0x12` | `.word       0x4B153184                   # INVALID     $t8, $s5, 0x3184 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4505 | `data_gap_80024A0C` | `0x80025314` | `0xC96C0A0C` | `opcode_0x32` | `lwc2        $12, 0xA0C($t3)` |
| funcs_7.c:4507 | `data_gap_80024A0C` | `0x80025318` | `0x4B15294D` | `opcode_0x12` | `.word       0x4B15294D                   # INVALID     $t8, $s5, 0x294D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4509 | `data_gap_80024A0C` | `0x8002531C` | `0xC96C0C0C` | `opcode_0x32` | `lwc2        $12, 0xC0C($t3)` |
| funcs_7.c:4511 | `data_gap_80024A0C` | `0x80025320` | `0x4B1EF18E` | `opcode_0x12` | `.word       0x4B1EF18E                   # INVALID     $t8, $fp, -0xE72 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4513 | `data_gap_80024A0C` | `0x80025324` | `0x4A4A4044` | `opcode_0x12` | `.word       0x4A4A4044                   # INVALID     $s2, $t2, 0x4044 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4515 | `data_gap_80024A0C` | `0x80025328` | `0x4A4A384D` | `opcode_0x12` | `.word       0x4A4A384D                   # INVALID     $s2, $t2, 0x384D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4517 | `data_gap_80024A0C` | `0x8002532C` | `0x4A49404E` | `opcode_0x12` | `.word       0x4A49404E                   # INVALID     $s2, $t1, 0x404E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4519 | `data_gap_80024A0C` | `0x80025330` | `0x4A49380F` | `opcode_0x12` | `.word       0x4A49380F                   # INVALID     $s2, $t1, 0x380F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4521 | `data_gap_80024A0C` | `0x80025334` | `0x4B1EF04E` | `opcode_0x12` | `.word       0x4B1EF04E                   # INVALID     $t8, $fp, -0xFB2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4523 | `data_gap_80024A0C` | `0x80025338` | `0x4B9E4204` | `opcode_0x12` | `.word       0x4B9E4204                   # INVALID     $gp, $fp, 0x4204 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4525 | `data_gap_80024A0C` | `0x8002533C` | `0x4B9E39CD` | `opcode_0x12` | `.word       0x4B9E39CD                   # INVALID     $gp, $fp, 0x39CD # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4527 | `data_gap_80024A0C` | `0x80025340` | `0x4B1EF20E` | `opcode_0x12` | `.word       0x4B1EF20E                   # INVALID     $t8, $fp, -0xDF2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4529 | `data_gap_80024A0C` | `0x80025344` | `0x4B9E0844` | `opcode_0x12` | `.word       0x4B9E0844                   # INVALID     $gp, $fp, 0x844 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4531 | `data_gap_80024A0C` | `0x80025348` | `0x4B9E000D` | `opcode_0x12` | `.word       0x4B9E000D                   # INVALID     $gp, $fp, 0xD # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4533 | `data_gap_80024A0C` | `0x8002534C` | `0x4B1EF04E` | `opcode_0x12` | `.word       0x4B1EF04E                   # INVALID     $t8, $fp, -0xFB2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4535 | `data_gap_80024A0C` | `0x80025350` | `0x4B3F0C28` | `opcode_0x12` | `.word       0x4B3F0C28                   # INVALID     $t9, $ra, 0xC28 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4537 | `data_gap_80024A0C` | `0x80025354` | `0x4B9E6305` | `opcode_0x12` | `.word       0x4B9E6305                   # INVALID     $gp, $fp, 0x6305 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4539 | `data_gap_80024A0C` | `0x80025358` | `0x4B1EF34E` | `opcode_0x12` | `.word       0x4B1EF34E                   # INVALID     $t8, $fp, -0xCB2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4541 | `data_gap_80024A0C` | `0x8002535C` | `0x4BDF0026` | `opcode_0x12` | `.word       0x4BDF0026                   # INVALID     $fp, $ra, 0x26 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4543 | `data_gap_80024A0C` | `0x80025360` | `0xEA0C0804` | `opcode_0x3A` | `swc2        $12, 0x804($s0)` |
| funcs_7.c:4545 | `data_gap_80024A0C` | `0x80025364` | `0x4B2282C4` | `opcode_0x12` | `.word       0x4B2282C4                   # INVALID     $t9, $v0, -0x7D3C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4547 | `data_gap_80024A0C` | `0x80025368` | `0xEA0D0805` | `opcode_0x3A` | `swc2        $13, 0x805($s0)` |
| funcs_7.c:4549 | `data_gap_80024A0C` | `0x8002536C` | `0x4B22028D` | `opcode_0x12` | `.word       0x4B22028D                   # INVALID     $t9, $v0, 0x28D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4551 | `data_gap_80024A0C` | `0x80025370` | `0xEA000906` | `opcode_0x3A` | `swc2        $0, 0x906($s0)` |
| funcs_7.c:4553 | `data_gap_80024A0C` | `0x80025374` | `0x4B1EF2CE` | `opcode_0x12` | `.word       0x4B1EF2CE                   # INVALID     $t8, $fp, -0xD32 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4555 | `data_gap_80024A0C` | `0x80025378` | `0xEA010907` | `opcode_0x3A` | `swc2        $1, 0x907($s0)` |
| funcs_7.c:4561 | `data_gap_80024A0C` | `0x80025384` | `0x4A6B68D5` | `opcode_0x12` | `.word       0x4A6B68D5                   # INVALID     $s3, $t3, 0x68D5 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4563 | `data_gap_80024A0C` | `0x80025388` | `0xEA000D0A` | `opcode_0x3A` | `swc2        $0, 0xD0A($s0)` |
| funcs_7.c:4565 | `data_gap_80024A0C` | `0x8002538C` | `0x4A6A6251` | `opcode_0x12` | `.word       0x4A6A6251                   # INVALID     $s3, $t2, 0x6251 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4567 | `data_gap_80024A0C` | `0x80025390` | `0xEA010D0B` | `opcode_0x3A` | `swc2        $1, 0xD0B($s0)` |
| funcs_7.c:4569 | `data_gap_80024A0C` | `0x80025394` | `0x4B263555` | `opcode_0x12` | `.word       0x4B263555                   # INVALID     $t9, $a2, 0x3555 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4571 | `data_gap_80024A0C` | `0x80025398` | `0xEA000B0E` | `opcode_0x3A` | `swc2        $0, 0xB0E($s0)` |
| funcs_7.c:4573 | `data_gap_80024A0C` | `0x8002539C` | `0x4B252CE0` | `opcode_0x12` | `.word       0x4B252CE0                   # INVALID     $t9, $a1, 0x2CE0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4575 | `data_gap_80024A0C` | `0x800253A0` | `0xEA010B0F` | `opcode_0x3A` | `swc2        $1, 0xB0F($s0)` |
| funcs_7.c:4577 | `data_gap_80024A0C` | `0x800253A4` | `0x4B263527` | `opcode_0x12` | `.word       0x4B263527                   # INVALID     $t9, $a2, 0x3527 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4579 | `data_gap_80024A0C` | `0x800253A8` | `0xEA090C08` | `opcode_0x3A` | `swc2        $9, 0xC08($s0)` |
| funcs_7.c:4581 | `data_gap_80024A0C` | `0x800253AC` | `0x4B46A555` | `opcode_0x12` | `.word       0x4B46A555                   # INVALID     $k0, $a2, -0x5AAB # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4583 | `data_gap_80024A0C` | `0x800253B0` | `0xEA030C09` | `opcode_0x3A` | `swc2        $3, 0xC09($s0)` |
| funcs_7.c:4585 | `data_gap_80024A0C` | `0x800253B4` | `0x4B459CE0` | `opcode_0x12` | `.word       0x4B459CE0                   # INVALID     $k0, $a1, -0x6320 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4587 | `data_gap_80024A0C` | `0x800253B8` | `0xEA090A0C` | `opcode_0x3A` | `swc2        $9, 0xA0C($s0)` |
| funcs_7.c:4589 | `data_gap_80024A0C` | `0x800253BC` | `0x4B46A527` | `opcode_0x12` | `.word       0x4B46A527                   # INVALID     $k0, $a2, -0x5AD9 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4591 | `data_gap_80024A0C` | `0x800253C0` | `0xEA030A0D` | `opcode_0x3A` | `swc2        $3, 0xA0D($s0)` |
| funcs_7.c:4597 | `data_gap_80024A0C` | `0x800253CC` | `0xC9691005` | `opcode_0x32` | `lwc2        $9, 0x1005($t3)` |
| funcs_7.c:4601 | `data_gap_80024A0C` | `0x800253CC` | `0xC9691005` | `opcode_0x32` | `lwc2        $9, 0x1005($t3)` |
| funcs_7.c:4603 | `data_gap_80024A0C` | `0x800253D0` | `0xC9891405` | `opcode_0x32` | `lwc2        $9, 0x1405($t4)` |
| funcs_7.c:4605 | `data_gap_80024A0C` | `0x800253D4` | `0xC9B61005` | `opcode_0x32` | `lwc2        $22, 0x1005($t5)` |
| funcs_7.c:4611 | `data_gap_80024A0C` | `0x800253E0` | `0x4BBFA504` | `opcode_0x12` | `.word       0x4BBFA504                   # INVALID     $sp, $ra, -0x5AFC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4615 | `data_gap_80024A0C` | `0x800253E0` | `0x4BBFA504` | `opcode_0x12` | `.word       0x4BBFA504                   # INVALID     $sp, $ra, -0x5AFC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4617 | `data_gap_80024A0C` | `0x800253E4` | `0x4BBF9CCD` | `opcode_0x12` | `.word       0x4BBF9CCD                   # INVALID     $sp, $ra, -0x6333 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4619 | `data_gap_80024A0C` | `0x800253E8` | `0x4B1EF50E` | `opcode_0x12` | `.word       0x4B1EF50E                   # INVALID     $t8, $fp, -0xAF2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4621 | `data_gap_80024A0C` | `0x800253EC` | `0xC96B0811` | `opcode_0x32` | `lwc2        $11, 0x811($t3)` |
| funcs_7.c:4623 | `data_gap_80024A0C` | `0x800253F0` | `0xC96C0810` | `opcode_0x32` | `lwc2        $12, 0x810($t3)` |
| funcs_7.c:4625 | `data_gap_80024A0C` | `0x800253F4` | `0xC98B0C11` | `opcode_0x32` | `lwc2        $11, 0xC11($t4)` |
| funcs_7.c:4627 | `data_gap_80024A0C` | `0x800253F8` | `0x4B1F5273` | `opcode_0x12` | `.word       0x4B1F5273                   # INVALID     $t8, $ra, 0x5273 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4629 | `data_gap_80024A0C` | `0x800253FC` | `0xC98C0C10` | `opcode_0x32` | `lwc2        $12, 0xC10($t4)` |
| funcs_7.c:4631 | `data_gap_80024A0C` | `0x80025400` | `0x4B1F7273` | `opcode_0x12` | `.word       0x4B1F7273                   # INVALID     $t8, $ra, 0x7273 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4633 | `data_gap_80024A0C` | `0x80025404` | `0xC9B80811` | `opcode_0x32` | `lwc2        $24, 0x811($t5)` |
| funcs_7.c:4635 | `data_gap_80024A0C` | `0x80025408` | `0x4B1F55B3` | `opcode_0x12` | `.word       0x4B1F55B3                   # INVALID     $t8, $ra, 0x55B3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4637 | `data_gap_80024A0C` | `0x8002540C` | `0xC9B90810` | `opcode_0x32` | `lwc2        $25, 0x810($t5)` |
| funcs_7.c:4639 | `data_gap_80024A0C` | `0x80025410` | `0x4B145984` | `opcode_0x12` | `.word       0x4B145984                   # INVALID     $t8, $s4, 0x5984 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4641 | `data_gap_80024A0C` | `0x80025414` | `0x4B14618D` | `opcode_0x12` | `.word       0x4B14618D                   # INVALID     $t8, $s4, 0x618D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4643 | `data_gap_80024A0C` | `0x80025418` | `0xEB130822` | `opcode_0x3A` | `swc2        $19, 0x822($t8)` |
| funcs_7.c:4645 | `data_gap_80024A0C` | `0x8002541C` | `0x4B13598E` | `opcode_0x12` | `.word       0x4B13598E                   # INVALID     $t8, $s3, 0x598E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4647 | `data_gap_80024A0C` | `0x80025420` | `0xEB140826` | `opcode_0x3A` | `swc2        $20, 0x826($t8)` |
| funcs_7.c:4649 | `data_gap_80024A0C` | `0x80025424` | `0x4B13614F` | `opcode_0x12` | `.word       0x4B13614F                   # INVALID     $t8, $s3, 0x614F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4651 | `data_gap_80024A0C` | `0x80025428` | `0x4B14C404` | `opcode_0x12` | `.word       0x4B14C404                   # INVALID     $t8, $s4, -0x3BFC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4653 | `data_gap_80024A0C` | `0x8002542C` | `0x4B14CC0D` | `opcode_0x12` | `.word       0x4B14CC0D                   # INVALID     $t8, $s4, -0x33F3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4655 | `data_gap_80024A0C` | `0x80025430` | `0x4B13C50E` | `opcode_0x12` | `.word       0x4B13C50E                   # INVALID     $t8, $s3, -0x3AF2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4657 | `data_gap_80024A0C` | `0x80025434` | `0x4B13CCCF` | `opcode_0x12` | `.word       0x4B13CCCF                   # INVALID     $t8, $s3, -0x3331 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4659 | `data_gap_80024A0C` | `0x80025438` | `0x4A864C05` | `opcode_0x12` | `.word       0x4A864C05                   # INVALID     $s4, $a2, 0x4C05 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4661 | `data_gap_80024A0C` | `0x8002543C` | `0x4A854A4F` | `opcode_0x12` | `.word       0x4A854A4F                   # INVALID     $s4, $a1, 0x4A4F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4663 | `data_gap_80024A0C` | `0x80025440` | `0x4B1EF28E` | `opcode_0x12` | `.word       0x4B1EF28E                   # INVALID     $t8, $fp, -0xD72 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4665 | `data_gap_80024A0C` | `0x80025444` | `0x4B14B405` | `opcode_0x12` | `.word       0x4B14B405                   # INVALID     $t8, $s4, -0x4BFB # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4667 | `data_gap_80024A0C` | `0x80025448` | `0x4B13B58F` | `opcode_0x12` | `.word       0x4B13B58F                   # INVALID     $t8, $s3, -0x4A71 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4669 | `data_gap_80024A0C` | `0x8002544C` | `0x4B1EF5CE` | `opcode_0x12` | `.word       0x4B1EF5CE                   # INVALID     $t8, $fp, -0xA32 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4672 | `data_gap_80024A0C` | `0x80025450` | `0xEBA91C02` | `opcode_0x3A` | `swc2        $9, 0x1C02($sp)` |
| funcs_7.c:4674 | `data_gap_80024A0C` | `0x80025454` | `0xEBAA1C03` | `opcode_0x3A` | `swc2        $10, 0x1C03($sp)` |
| funcs_7.c:4676 | `data_gap_80024A0C` | `0x80025458` | `0xEBA91800` | `opcode_0x3A` | `swc2        $9, 0x1800($sp)` |
| funcs_7.c:4678 | `data_gap_80024A0C` | `0x8002545C` | `0xEBAA1801` | `opcode_0x3A` | `swc2        $10, 0x1801($sp)` |
| funcs_7.c:4680 | `data_gap_80024A0C` | `0x80025460` | `0xEBB61804` | `opcode_0x3A` | `swc2        $22, 0x1804($sp)` |
| funcs_7.c:4682 | `data_gap_80024A0C` | `0x80025464` | `0xEBB71805` | `opcode_0x3A` | `swc2        $23, 0x1805($sp)` |
| funcs_7.c:4684 | `data_gap_80024A0C` | `0x80025468` | `0x4A094A53` | `opcode_0x12` | `.word       0x4A094A53                   # INVALID     $s0, $t1, 0x4A53 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4686 | `data_gap_80024A0C` | `0x8002546C` | `0xCBB31004` | `opcode_0x32` | `lwc2        $19, 0x1004($sp)` |
| funcs_7.c:4688 | `data_gap_80024A0C` | `0x80025470` | `0x4A16B593` | `opcode_0x12` | `.word       0x4A16B593                   # INVALID     $s0, $s6, -0x4A6D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4690 | `data_gap_80024A0C` | `0x80025474` | `0xCBB41006` | `opcode_0x32` | `lwc2        $20, 0x1006($sp)` |
| funcs_7.c:4692 | `data_gap_80024A0C` | `0x80025478` | `0x4A139CD3` | `opcode_0x12` | `.word       0x4A139CD3                   # INVALID     $s0, $s3, -0x632D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4694 | `data_gap_80024A0C` | `0x8002547C` | `0x4A164C63` | `opcode_0x12` | `.word       0x4A164C63                   # INVALID     $s0, $s6, 0x4C63 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4696 | `data_gap_80024A0C` | `0x80025480` | `0x4A1754A7` | `opcode_0x12` | `.word       0x4A1754A7                   # INVALID     $s0, $s7, 0x54A7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4698 | `data_gap_80024A0C` | `0x80025484` | `0x4A138C63` | `opcode_0x12` | `.word       0x4A138C63                   # INVALID     $s0, $s3, -0x739D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4700 | `data_gap_80024A0C` | `0x80025488` | `0x4A1494A7` | `opcode_0x12` | `.word       0x4A1494A7                   # INVALID     $s0, $s4, -0x6B59 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4703 | `data_gap_80024A0C` | `0x8002548C` | `0xEB111010` | `opcode_0x3A` | `swc2        $17, 0x1010($t8)` |
| funcs_7.c:4705 | `data_gap_80024A0C` | `0x80025490` | `0xEB121012` | `opcode_0x3A` | `swc2        $18, 0x1012($t8)` |
| funcs_7.c:4707 | `data_gap_80024A0C` | `0x80025494` | `0x4A1EF4AC` | `opcode_0x12` | `.word       0x4A1EF4AC                   # INVALID     $s0, $fp, -0xB54 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4709 | `data_gap_80024A0C` | `0x80025498` | `0xC9B93802` | `opcode_0x32` | `lwc2        $25, 0x3802($t5)` |
| funcs_7.c:4711 | `data_gap_80024A0C` | `0x8002549C` | `0x4BBF9410` | `opcode_0x12` | `.word       0x4BBF9410                   # INVALID     $sp, $ra, -0x6BF0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4713 | `data_gap_80024A0C` | `0x800254A0` | `0xC96F3802` | `opcode_0x32` | `lwc2        $15, 0x3802($t3)` |
| funcs_7.c:4715 | `data_gap_80024A0C` | `0x800254A4` | `0x4BBF9610` | `opcode_0x12` | `.word       0x4BBF9610                   # INVALID     $sp, $ra, -0x69F0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4719 | `data_gap_80024A0C` | `0x800254AC` | `0x4BBF9150` | `opcode_0x12` | `.word       0x4BBF9150                   # INVALID     $sp, $ra, -0x6EB0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4723 | `data_gap_80024A0C` | `0x800254B4` | `0xC9973802` | `opcode_0x32` | `lwc2        $23, 0x3802($t4)` |
| funcs_7.c:4727 | `data_gap_80024A0C` | `0x800254B4` | `0xC9973802` | `opcode_0x32` | `lwc2        $23, 0x3802($t4)` |
| funcs_7.c:4729 | `data_gap_80024A0C` | `0x800254B8` | `0xC9F93802` | `opcode_0x32` | `lwc2        $25, 0x3802($t7)` |
| funcs_7.c:4731 | `data_gap_80024A0C` | `0x800254BC` | `0xC9EF3802` | `opcode_0x32` | `lwc2        $15, 0x3802($t7)` |
| funcs_7.c:4733 | `data_gap_80024A0C` | `0x800254C0` | `0xC9F73802` | `opcode_0x32` | `lwc2        $23, 0x3802($t7)` |
| funcs_7.c:4736 | `data_gap_80024A0C` | `0x800254C4` | `0x4BFECE45` | `opcode_0x12` | `.word       0x4BFECE45                   # INVALID     $ra, $fp, -0x31BB # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4738 | `data_gap_80024A0C` | `0x800254C8` | `0x4BFE7BC5` | `opcode_0x12` | `.word       0x4BFE7BC5                   # INVALID     $ra, $fp, 0x7BC5 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4740 | `data_gap_80024A0C` | `0x800254CC` | `0x4BFEBDC5` | `opcode_0x12` | `.word       0x4BFEBDC5                   # INVALID     $ra, $fp, -0x423B # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4742 | `data_gap_80024A0C` | `0x800254D0` | `0xCB101C03` | `opcode_0x32` | `lwc2        $16, 0x1C03($t8)` |
| funcs_7.c:4744 | `data_gap_80024A0C` | `0x800254D4` | `0xCB0F1C02` | `opcode_0x32` | `lwc2        $15, 0x1C02($t8)` |
| funcs_7.c:4746 | `data_gap_80024A0C` | `0x800254D8` | `0xCB181C05` | `opcode_0x32` | `lwc2        $24, 0x1C05($t8)` |
| funcs_7.c:4748 | `data_gap_80024A0C` | `0x800254DC` | `0xCB171C04` | `opcode_0x32` | `lwc2        $23, 0x1C04($t8)` |
| funcs_7.c:4750 | `data_gap_80024A0C` | `0x800254E0` | `0xCB051C07` | `opcode_0x32` | `lwc2        $5, 0x1C07($t8)` |
| funcs_7.c:4752 | `data_gap_80024A0C` | `0x800254E4` | `0xCB191C06` | `opcode_0x32` | `lwc2        $25, 0x1C06($t8)` |
| funcs_7.c:4754 | `data_gap_80024A0C` | `0x800254E8` | `0xC9700F0F` | `opcode_0x32` | `lwc2        $16, 0xF0F($t3)` |
| funcs_7.c:4756 | `data_gap_80024A0C` | `0x800254EC` | `0xC96F0F0E` | `opcode_0x32` | `lwc2        $15, 0xF0E($t3)` |
| funcs_7.c:4758 | `data_gap_80024A0C` | `0x800254F0` | `0xC9980F0F` | `opcode_0x32` | `lwc2        $24, 0xF0F($t4)` |
| funcs_7.c:4760 | `data_gap_80024A0C` | `0x800254F4` | `0xC9970F0E` | `opcode_0x32` | `lwc2        $23, 0xF0E($t4)` |
| funcs_7.c:4762 | `data_gap_80024A0C` | `0x800254F8` | `0xC9A50F0F` | `opcode_0x32` | `lwc2        $5, 0xF0F($t5)` |
| funcs_7.c:4764 | `data_gap_80024A0C` | `0x800254FC` | `0xC9B90F0E` | `opcode_0x32` | `lwc2        $25, 0xF0E($t5)` |
| funcs_7.c:4766 | `data_gap_80024A0C` | `0x80025500` | `0x4A10C315` | `opcode_0x12` | `.word       0x4A10C315                   # INVALID     $s0, $s0, -0x3CEB # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4768 | `data_gap_80024A0C` | `0x80025504` | `0x4A0FBAD1` | `opcode_0x12` | `.word       0x4A0FBAD1                   # INVALID     $s0, $t7, -0x452F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4770 | `data_gap_80024A0C` | `0x80025508` | `0x4A058515` | `opcode_0x12` | `.word       0x4A058515                   # INVALID     $s0, $a1, -0x7AEB # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4772 | `data_gap_80024A0C` | `0x8002550C` | `0x4A197CD1` | `opcode_0x12` | `.word       0x4A197CD1                   # INVALID     $s0, $t9, 0x7CD1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4774 | `data_gap_80024A0C` | `0x80025510` | `0x4A102A95` | `opcode_0x12` | `.word       0x4A102A95                   # INVALID     $s0, $s0, 0x2A95 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4776 | `data_gap_80024A0C` | `0x80025514` | `0x4A0FCA51` | `opcode_0x12` | `.word       0x4A0FCA51                   # INVALID     $s0, $t7, -0x35AF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4778 | `data_gap_80024A0C` | `0x80025518` | `0x4A188595` | `opcode_0x12` | `.word       0x4A188595                   # INVALID     $s0, $t8, -0x7A6B # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4780 | `data_gap_80024A0C` | `0x8002551C` | `0x4A177D51` | `opcode_0x12` | `.word       0x4A177D51                   # INVALID     $s0, $s7, 0x7D51 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4782 | `data_gap_80024A0C` | `0x80025520` | `0x4B645186` | `opcode_0x12` | `.word       0x4B645186                   # INVALID     $k1, $a0, 0x5186 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4784 | `data_gap_80024A0C` | `0x80025524` | `0x4B64498F` | `opcode_0x12` | `.word       0x4B64498F                   # INVALID     $k1, $a0, 0x498F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4786 | `data_gap_80024A0C` | `0x80025528` | `0x4BA4B18E` | `opcode_0x12` | `.word       0x4BA4B18E                   # INVALID     $sp, $a0, -0x4E72 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4788 | `data_gap_80024A0C` | `0x8002552C` | `0x4BA4A98F` | `opcode_0x12` | `.word       0x4BA4A98F                   # INVALID     $sp, $a0, -0x5671 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4790 | `data_gap_80024A0C` | `0x80025530` | `0x4B094A5D` | `opcode_0x12` | `.word       0x4B094A5D                   # INVALID     $t8, $t1, 0x4A5D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4792 | `data_gap_80024A0C` | `0x80025534` | `0x4B2A529D` | `opcode_0x12` | `.word       0x4B2A529D                   # INVALID     $t9, $t2, 0x529D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4794 | `data_gap_80024A0C` | `0x80025538` | `0x4B846186` | `opcode_0x12` | `.word       0x4B846186                   # INVALID     $gp, $a0, 0x6186 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4796 | `data_gap_80024A0C` | `0x8002553C` | `0x4B84598F` | `opcode_0x12` | `.word       0x4B84598F                   # INVALID     $gp, $a0, 0x598F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4798 | `data_gap_80024A0C` | `0x80025540` | `0x4B44A18E` | `opcode_0x12` | `.word       0x4B44A18E                   # INVALID     $k0, $a0, -0x5E72 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4800 | `data_gap_80024A0C` | `0x80025544` | `0x4B44998F` | `opcode_0x12` | `.word       0x4B44998F                   # INVALID     $k0, $a0, -0x6671 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4802 | `data_gap_80024A0C` | `0x80025548` | `0x4B0B5ADD` | `opcode_0x12` | `.word       0x4B0B5ADD                   # INVALID     $t8, $t3, 0x5ADD # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4804 | `data_gap_80024A0C` | `0x8002554C` | `0x4B2C631D` | `opcode_0x12` | `.word       0x4B2C631D                   # INVALID     $t9, $t4, 0x631D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4806 | `data_gap_80024A0C` | `0x80025550` | `0x4B7A5184` | `opcode_0x12` | `.word       0x4B7A5184                   # INVALID     $k1, $k0, 0x5184 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4808 | `data_gap_80024A0C` | `0x80025554` | `0x4B7A498D` | `opcode_0x12` | `.word       0x4B7A498D                   # INVALID     $k1, $k0, 0x498D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4810 | `data_gap_80024A0C` | `0x80025558` | `0x4B7B528E` | `opcode_0x12` | `.word       0x4B7B528E                   # INVALID     $k1, $k1, 0x528E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4812 | `data_gap_80024A0C` | `0x8002555C` | `0x4B7B4A4F` | `opcode_0x12` | `.word       0x4B7B4A4F                   # INVALID     $k1, $k1, 0x4A4F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4814 | `data_gap_80024A0C` | `0x80025560` | `0x4B7A6184` | `opcode_0x12` | `.word       0x4B7A6184                   # INVALID     $k1, $k0, 0x6184 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4816 | `data_gap_80024A0C` | `0x80025564` | `0x4B7A598D` | `opcode_0x12` | `.word       0x4B7A598D                   # INVALID     $k1, $k0, 0x598D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4818 | `data_gap_80024A0C` | `0x80025568` | `0x4B7B630E` | `opcode_0x12` | `.word       0x4B7B630E                   # INVALID     $k1, $k1, 0x630E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4820 | `data_gap_80024A0C` | `0x8002556C` | `0xEA091801` | `opcode_0x3A` | `swc2        $9, 0x1801($s0)` |
| funcs_7.c:4822 | `data_gap_80024A0C` | `0x80025570` | `0x4B7B5ACF` | `opcode_0x12` | `.word       0x4B7B5ACF                   # INVALID     $k1, $k1, 0x5ACF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4824 | `data_gap_80024A0C` | `0x80025574` | `0xEA0A1803` | `opcode_0x3A` | `swc2        $10, 0x1803($s0)` |
| funcs_7.c:4826 | `data_gap_80024A0C` | `0x80025578` | `0x4B3E6186` | `opcode_0x12` | `.word       0x4B3E6186                   # INVALID     $t9, $fp, 0x6186 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4828 | `data_gap_80024A0C` | `0x8002557C` | `0x4B3E598F` | `opcode_0x12` | `.word       0x4B3E598F                   # INVALID     $t9, $fp, 0x598F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4830 | `data_gap_80024A0C` | `0x80025580` | `0x4BA1518C` | `opcode_0x12` | `.word       0x4BA1518C                   # INVALID     $sp, $at, 0x518C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4832 | `data_gap_80024A0C` | `0x80025584` | `0x4BA1498D` | `opcode_0x12` | `.word       0x4BA1498D                   # INVALID     $sp, $at, 0x498D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4834 | `data_gap_80024A0C` | `0x80025588` | `0x4BA0538E` | `opcode_0x12` | `.word       0x4BA0538E                   # INVALID     $sp, $zero, 0x538E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4836 | `data_gap_80024A0C` | `0x8002558C` | `0xEA0B1805` | `opcode_0x3A` | `swc2        $11, 0x1805($s0)` |
| funcs_7.c:4838 | `data_gap_80024A0C` | `0x80025590` | `0x4BA04B4F` | `opcode_0x12` | `.word       0x4BA04B4F                   # INVALID     $sp, $zero, 0x4B4F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4840 | `data_gap_80024A0C` | `0x80025594` | `0xEA0C1807` | `opcode_0x3A` | `swc2        $12, 0x1807($s0)` |
| funcs_7.c:4842 | `data_gap_80024A0C` | `0x80025598` | `0x4B227704` | `opcode_0x12` | `.word       0x4B227704                   # INVALID     $t9, $v0, 0x7704 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4844 | `data_gap_80024A0C` | `0x8002559C` | `0xEA0D1804` | `opcode_0x3A` | `swc2        $13, 0x1804($s0)` |
| funcs_7.c:4846 | `data_gap_80024A0C` | `0x800255A0` | `0x4B22698D` | `opcode_0x12` | `.word       0x4B22698D                   # INVALID     $t9, $v0, 0x698D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4848 | `data_gap_80024A0C` | `0x800255A4` | `0xEA0E1806` | `opcode_0x3A` | `swc2        $14, 0x1806($s0)` |
| funcs_7.c:4850 | `data_gap_80024A0C` | `0x800255A8` | `0x4B1EF70E` | `opcode_0x12` | `.word       0x4B1EF70E                   # INVALID     $t8, $fp, -0x8F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4852 | `data_gap_80024A0C` | `0x800255AC` | `0x4A1C8495` | `opcode_0x12` | `.word       0x4A1C8495                   # INVALID     $s0, $gp, -0x7B6B # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4854 | `data_gap_80024A0C` | `0x800255B0` | `0x4A067C51` | `opcode_0x12` | `.word       0x4A067C51                   # INVALID     $s0, $a2, 0x7C51 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4868 | `data_gap_80024A0C` | `0x800255C4` | `0xEA111878` | `opcode_0x3A` | `swc2        $17, 0x1878($s0)` |
| funcs_7.c:4870 | `data_gap_80024A0C` | `0x800255C8` | `0xEA12187A` | `opcode_0x3A` | `swc2        $18, 0x187A($s0)` |
| funcs_7.c:4883 | `data_gap_80024A0C` | `0x800255D8` | `0x48839800` | `opcode_0x12` | `mtc2        $v1, $19` |
| funcs_7.c:4885 | `data_gap_80024A0C` | `0x800255DC` | `0x4A094E13` | `opcode_0x12` | `.word       0x4A094E13                   # INVALID     $s0, $t1, 0x4E13 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4887 | `data_gap_80024A0C` | `0x800255E0` | `0xCB141C08` | `opcode_0x32` | `lwc2        $20, 0x1C08($t8)` |
| funcs_7.c:4889 | `data_gap_80024A0C` | `0x800255E4` | `0x4A0B5E53` | `opcode_0x12` | `.word       0x4A0B5E53                   # INVALID     $s0, $t3, 0x5E53 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4891 | `data_gap_80024A0C` | `0x800255E8` | `0xCB151C09` | `opcode_0x32` | `lwc2        $21, 0x1C09($t8)` |
| funcs_7.c:4893 | `data_gap_80024A0C` | `0x800255EC` | `0x4B13C605` | `opcode_0x12` | `.word       0x4B13C605                   # INVALID     $t8, $s3, -0x39FB # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4895 | `data_gap_80024A0C` | `0x800255F0` | `0x4B1EF68E` | `opcode_0x12` | `.word       0x4B1EF68E                   # INVALID     $t8, $fp, -0x972 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4897 | `data_gap_80024A0C` | `0x800255F4` | `0x4B13CE45` | `opcode_0x12` | `.word       0x4B13CE45                   # INVALID     $t8, $s3, -0x31BB # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4899 | `data_gap_80024A0C` | `0x800255F8` | `0x4B1EF6CE` | `opcode_0x12` | `.word       0x4B1EF6CE                   # INVALID     $t8, $fp, -0x932 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4901 | `data_gap_80024A0C` | `0x800255FC` | `0x4B13AD44` | `opcode_0x12` | `.word       0x4B13AD44                   # INVALID     $t8, $s3, -0x52BC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4903 | `data_gap_80024A0C` | `0x80025600` | `0x4B13A50D` | `opcode_0x12` | `.word       0x4B13A50D                   # INVALID     $t8, $s3, -0x5AF3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4905 | `data_gap_80024A0C` | `0x80025604` | `0x4B1EF54E` | `opcode_0x12` | `.word       0x4B1EF54E                   # INVALID     $t8, $fp, -0xAB2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4907 | `data_gap_80024A0C` | `0x80025608` | `0x4B5ED686` | `opcode_0x12` | `.word       0x4B5ED686                   # INVALID     $k0, $fp, -0x297A # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4909 | `data_gap_80024A0C` | `0x8002560C` | `0x4B5EC60F` | `opcode_0x12` | `.word       0x4B5EC60F                   # INVALID     $k0, $fp, -0x39F1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4911 | `data_gap_80024A0C` | `0x80025610` | `0x4B1EF68E` | `opcode_0x12` | `.word       0x4B1EF68E                   # INVALID     $t8, $fp, -0x972 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4913 | `data_gap_80024A0C` | `0x80025614` | `0x4B3EDDCE` | `opcode_0x12` | `.word       0x4B3EDDCE                   # INVALID     $t9, $fp, -0x2232 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4915 | `data_gap_80024A0C` | `0x80025618` | `0x4B3ECD8F` | `opcode_0x12` | `.word       0x4B3ECD8F                   # INVALID     $t9, $fp, -0x3271 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4917 | `data_gap_80024A0C` | `0x8002561C` | `0x4B3EA98E` | `opcode_0x12` | `.word       0x4B3EA98E                   # INVALID     $t9, $fp, -0x5672 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4919 | `data_gap_80024A0C` | `0x80025620` | `0x4B3EA14F` | `opcode_0x12` | `.word       0x4B3EA14F                   # INVALID     $t9, $fp, -0x5EB1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4921 | `data_gap_80024A0C` | `0x80025624` | `0x4BA635D5` | `opcode_0x12` | `.word       0x4BA635D5                   # INVALID     $sp, $a2, 0x35D5 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4923 | `data_gap_80024A0C` | `0x80025628` | `0x4BA52963` | `opcode_0x12` | `.word       0x4BA52963                   # INVALID     $sp, $a1, 0x2963 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4925 | `data_gap_80024A0C` | `0x8002562C` | `0x4BA631A7` | `opcode_0x12` | `.word       0x4BA631A7                   # INVALID     $sp, $a2, 0x31A7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4927 | `data_gap_80024A0C` | `0x80025630` | `0x4BC635D5` | `opcode_0x12` | `.word       0x4BC635D5                   # INVALID     $fp, $a2, 0x35D5 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4929 | `data_gap_80024A0C` | `0x80025634` | `0x4BC52963` | `opcode_0x12` | `.word       0x4BC52963                   # INVALID     $fp, $a1, 0x2963 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4931 | `data_gap_80024A0C` | `0x80025638` | `0x4BC631A7` | `opcode_0x12` | `.word       0x4BC631A7                   # INVALID     $fp, $a2, 0x31A7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4933 | `data_gap_80024A0C` | `0x8002563C` | `0x4B7F3184` | `opcode_0x12` | `.word       0x4B7F3184                   # INVALID     $k1, $ra, 0x3184 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4935 | `data_gap_80024A0C` | `0x80025640` | `0x4B7F294D` | `opcode_0x12` | `.word       0x4B7F294D                   # INVALID     $k1, $ra, 0x294D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4937 | `data_gap_80024A0C` | `0x80025644` | `0x4B1EF18E` | `opcode_0x12` | `.word       0x4B1EF18E                   # INVALID     $t8, $fp, -0xE72 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4939 | `data_gap_80024A0C` | `0x80025648` | `0x4B8545F2` | `opcode_0x12` | `.word       0x4B8545F2                   # INVALID     $gp, $a1, 0x45F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4941 | `data_gap_80024A0C` | `0x8002564C` | `0x4B8641B1` | `opcode_0x12` | `.word       0x4B8641B1                   # INVALID     $gp, $a2, 0x41B1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4943 | `data_gap_80024A0C` | `0x80025650` | `0x4B1E4172` | `opcode_0x12` | `.word       0x4B1E4172                   # INVALID     $t8, $fp, 0x4172 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4945 | `data_gap_80024A0C` | `0x80025654` | `0x4B5E3186` | `opcode_0x12` | `.word       0x4B5E3186                   # INVALID     $k0, $fp, 0x3186 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4947 | `data_gap_80024A0C` | `0x80025658` | `0x4B5E294F` | `opcode_0x12` | `.word       0x4B5E294F                   # INVALID     $k0, $fp, 0x294F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4949 | `data_gap_80024A0C` | `0x8002565C` | `0x4B3E2960` | `opcode_0x12` | `.word       0x4B3E2960                   # INVALID     $t9, $fp, 0x2960 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4951 | `data_gap_80024A0C` | `0x80025660` | `0x4B1E31A7` | `opcode_0x12` | `.word       0x4B1E31A7                   # INVALID     $t8, $fp, 0x31A7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4953 | `data_gap_80024A0C` | `0x80025664` | `0x4B069504` | `opcode_0x12` | `.word       0x4B069504                   # INVALID     $t8, $a2, -0x6AFC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4955 | `data_gap_80024A0C` | `0x80025668` | `0x4B068D0D` | `opcode_0x12` | `.word       0x4B068D0D                   # INVALID     $t8, $a2, -0x72F3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4957 | `data_gap_80024A0C` | `0x8002566C` | `0x4B05950E` | `opcode_0x12` | `.word       0x4B05950E                   # INVALID     $t8, $a1, -0x6AF2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4959 | `data_gap_80024A0C` | `0x80025670` | `0x4B058CCF` | `opcode_0x12` | `.word       0x4B058CCF                   # INVALID     $t8, $a1, -0x7331 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4961 | `data_gap_80024A0C` | `0x80025674` | `0x4B065584` | `opcode_0x12` | `.word       0x4B065584                   # INVALID     $t8, $a2, 0x5584 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4963 | `data_gap_80024A0C` | `0x80025678` | `0x4B064D8D` | `opcode_0x12` | `.word       0x4B064D8D                   # INVALID     $t8, $a2, 0x4D8D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4965 | `data_gap_80024A0C` | `0x8002567C` | `0x4B05558E` | `opcode_0x12` | `.word       0x4B05558E                   # INVALID     $t8, $a1, 0x558E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4967 | `data_gap_80024A0C` | `0x80025680` | `0xEA131C00` | `opcode_0x3A` | `swc2        $19, 0x1C00($s0)` |
| funcs_7.c:4969 | `data_gap_80024A0C` | `0x80025684` | `0x4B054D4F` | `opcode_0x12` | `.word       0x4B054D4F                   # INVALID     $t8, $a1, 0x4D4F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4971 | `data_gap_80024A0C` | `0x80025688` | `0xEA141C02` | `opcode_0x3A` | `swc2        $20, 0x1C02($s0)` |
| funcs_7.c:4973 | `data_gap_80024A0C` | `0x8002568C` | `0x4B066604` | `opcode_0x12` | `.word       0x4B066604                   # INVALID     $t8, $a2, 0x6604 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4975 | `data_gap_80024A0C` | `0x80025690` | `0x4B065E0D` | `opcode_0x12` | `.word       0x4B065E0D                   # INVALID     $t8, $a2, 0x5E0D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4977 | `data_gap_80024A0C` | `0x80025694` | `0x4B05660E` | `opcode_0x12` | `.word       0x4B05660E                   # INVALID     $t8, $a1, 0x660E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4979 | `data_gap_80024A0C` | `0x80025698` | `0xEA151C01` | `opcode_0x3A` | `swc2        $21, 0x1C01($s0)` |
| funcs_7.c:4981 | `data_gap_80024A0C` | `0x8002569C` | `0x4B055DCF` | `opcode_0x12` | `.word       0x4B055DCF                   # INVALID     $t8, $a1, 0x5DCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4983 | `data_gap_80024A0C` | `0x800256A0` | `0xEA161C03` | `opcode_0x3A` | `swc2        $22, 0x1C03($s0)` |
| funcs_7.c:4985 | `data_gap_80024A0C` | `0x800256A4` | `0x4B067684` | `opcode_0x12` | `.word       0x4B067684                   # INVALID     $t8, $a2, 0x7684 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4987 | `data_gap_80024A0C` | `0x800256A8` | `0x4B066E8D` | `opcode_0x12` | `.word       0x4B066E8D                   # INVALID     $t8, $a2, 0x6E8D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4989 | `data_gap_80024A0C` | `0x800256AC` | `0x4B05768E` | `opcode_0x12` | `.word       0x4B05768E                   # INVALID     $t8, $a1, 0x768E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4991 | `data_gap_80024A0C` | `0x800256B0` | `0xEA171C05` | `opcode_0x3A` | `swc2        $23, 0x1C05($s0)` |
| funcs_7.c:4993 | `data_gap_80024A0C` | `0x800256B4` | `0x4B056E4F` | `opcode_0x12` | `.word       0x4B056E4F                   # INVALID     $t8, $a1, 0x6E4F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:4995 | `data_gap_80024A0C` | `0x800256B8` | `0xEA181C07` | `opcode_0x3A` | `swc2        $24, 0x1C07($s0)` |
| funcs_7.c:4999 | `data_gap_80024A0C` | `0x800256C0` | `0xEA191C7C` | `opcode_0x3A` | `swc2        $25, 0x1C7C($s0)` |
| funcs_7.c:5001 | `data_gap_80024A0C` | `0x800256C4` | `0xEA1A1C7E` | `opcode_0x3A` | `swc2        $26, 0x1C7E($s0)` |
| funcs_7.c:5006 | `data_gap_80024A0C` | `0x800256CC` | `0x4B9F7386` | `opcode_0x12` | `.word       0x4B9F7386                   # INVALID     $gp, $ra, 0x7386 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5010 | `data_gap_80024A0C` | `0x800256CC` | `0x4B9F7386` | `opcode_0x12` | `.word       0x4B9F7386                   # INVALID     $gp, $ra, 0x7386 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5012 | `data_gap_80024A0C` | `0x800256D0` | `0x4B9F6B4F` | `opcode_0x12` | `.word       0x4B9F6B4F                   # INVALID     $gp, $ra, 0x6B4F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5014 | `data_gap_80024A0C` | `0x800256D4` | `0x4B1EF38E` | `opcode_0x12` | `.word       0x4B1EF38E                   # INVALID     $t8, $fp, -0xC72 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5016 | `data_gap_80024A0C` | `0x800256D8` | `0x4B9F8406` | `opcode_0x12` | `.word       0x4B9F8406                   # INVALID     $gp, $ra, -0x7BFA # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5018 | `data_gap_80024A0C` | `0x800256DC` | `0x4B9F7BCF` | `opcode_0x12` | `.word       0x4B9F7BCF                   # INVALID     $gp, $ra, 0x7BCF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5020 | `data_gap_80024A0C` | `0x800256E0` | `0x4B1EF40E` | `opcode_0x12` | `.word       0x4B1EF40E                   # INVALID     $t8, $fp, -0xBF2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5022 | `data_gap_80024A0C` | `0x800256E4` | `0xEA0D0F04` | `opcode_0x3A` | `swc2        $13, 0xF04($s0)` |
| funcs_7.c:5024 | `data_gap_80024A0C` | `0x800256E8` | `0x4B9F5286` | `opcode_0x12` | `.word       0x4B9F5286                   # INVALID     $gp, $ra, 0x5286 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5026 | `data_gap_80024A0C` | `0x800256EC` | `0xEA0E0F05` | `opcode_0x3A` | `swc2        $14, 0xF05($s0)` |
| funcs_7.c:5028 | `data_gap_80024A0C` | `0x800256F0` | `0x4B9F4A4F` | `opcode_0x12` | `.word       0x4B9F4A4F                   # INVALID     $gp, $ra, 0x4A4F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5030 | `data_gap_80024A0C` | `0x800256F4` | `0x4B1EF28E` | `opcode_0x12` | `.word       0x4B1EF28E                   # INVALID     $t8, $fp, -0xD72 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5032 | `data_gap_80024A0C` | `0x800256F8` | `0x4B9F6306` | `opcode_0x12` | `.word       0x4B9F6306                   # INVALID     $gp, $ra, 0x6306 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5034 | `data_gap_80024A0C` | `0x800256FC` | `0x4B9F5ACF` | `opcode_0x12` | `.word       0x4B9F5ACF                   # INVALID     $gp, $ra, 0x5ACF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5036 | `data_gap_80024A0C` | `0x80025700` | `0x4B1EF30E` | `opcode_0x12` | `.word       0x4B1EF30E                   # INVALID     $t8, $fp, -0xCF2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5038 | `data_gap_80024A0C` | `0x80025704` | `0xEA090F02` | `opcode_0x3A` | `swc2        $9, 0xF02($s0)` |
| funcs_7.c:5040 | `data_gap_80024A0C` | `0x80025708` | `0x4B227704` | `opcode_0x12` | `.word       0x4B227704                   # INVALID     $t9, $v0, 0x7704 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5042 | `data_gap_80024A0C` | `0x8002570C` | `0xEA0A0F03` | `opcode_0x3A` | `swc2        $10, 0xF03($s0)` |
| funcs_7.c:5044 | `data_gap_80024A0C` | `0x80025710` | `0x4B22698D` | `opcode_0x12` | `.word       0x4B22698D                   # INVALID     $t9, $v0, 0x698D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5046 | `data_gap_80024A0C` | `0x80025714` | `0xEA0B0F06` | `opcode_0x3A` | `swc2        $11, 0xF06($s0)` |
| funcs_7.c:5048 | `data_gap_80024A0C` | `0x80025718` | `0x4B1EF70E` | `opcode_0x12` | `.word       0x4B1EF70E                   # INVALID     $t8, $fp, -0x8F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5050 | `data_gap_80024A0C` | `0x8002571C` | `0xEA0C0F07` | `opcode_0x3A` | `swc2        $12, 0xF07($s0)` |
| funcs_7.c:5052 | `data_gap_80024A0C` | `0x80025720` | `0x4A1C8495` | `opcode_0x12` | `.word       0x4A1C8495                   # INVALID     $s0, $gp, -0x7B6B # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5054 | `data_gap_80024A0C` | `0x80025724` | `0x4A067C51` | `opcode_0x12` | `.word       0x4A067C51                   # INVALID     $s0, $a2, 0x7C51 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5058 | `data_gap_80024A0C` | `0x8002572C` | `0xEA110F78` | `opcode_0x3A` | `swc2        $17, 0xF78($s0)` |
| funcs_7.c:5060 | `data_gap_80024A0C` | `0x80025730` | `0xEA120F79` | `opcode_0x3A` | `swc2        $18, 0xF79($s0)` |
| funcs_7.c:5084 | `data_gap_80024A0C` | `0x80025754` | `0x40822000` | `cop0` | `mtc0        $v0, Context` |
| funcs_7.c:5114 | `data_gap_80024A0C` | `0x8002577C` | `0xC81E2003` | `opcode_0x32` | `lwc2        $30, 0x2003($zero)` |
| funcs_7.c:5116 | `data_gap_80024A0C` | `0x80025780` | `0xC81F2004` | `opcode_0x32` | `lwc2        $31, 0x2004($zero)` |
| funcs_7.c:5146 | `data_gap_80024A0C` | `0x800257A4` | `0x40025800` | `cop0` | `mfc0        $v0, Compare` |
| funcs_7.c:5152 | `data_gap_80024A0C` | `0x800257B0` | `0x40024800` | `cop0` | `mfc0        $v0, Count` |
| funcs_7.c:5156 | `data_gap_80024A0C` | `0x800257B0` | `0x40024800` | `cop0` | `mfc0        $v0, Count` |
| funcs_7.c:5162 | `data_gap_80024A0C` | `0x800257BC` | `0x40035000` | `cop0` | `mfc0        $v1, EntryHi` |
| funcs_7.c:5166 | `data_gap_80024A0C` | `0x800257BC` | `0x40035000` | `cop0` | `mfc0        $v1, EntryHi` |
| funcs_7.c:5184 | `data_gap_80024A0C` | `0x800257D0` | `0x09000797` | `j` | `j           L_84001E5C` |
| funcs_7.c:5189 | `data_gap_80024A0C` | `0x800257D8` | `0x40025800` | `cop0` | `mfc0        $v0, Compare` |
| funcs_7.c:5201 | `data_gap_80024A0C` | `0x800257E8` | `0x40825800` | `cop0` | `mtc0        $v0, Compare` |
| funcs_7.c:5203 | `data_gap_80024A0C` | `0x800257EC` | `0x40844000` | `cop0` | `mtc0        $a0, BadVaddr` |
| funcs_7.c:5205 | `data_gap_80024A0C` | `0x800257F0` | `0x40844800` | `cop0` | `mtc0        $a0, Count` |
| funcs_7.c:5211 | `data_gap_80024A0C` | `0x800257F8` | `0x0900046C` | `j` | `j           L_840011B0` |
| funcs_7.c:5230 | `data_gap_80024A0C` | `0x80025814` | `0x09000424` | `j` | `j           L_84001090` |
| funcs_7.c:5279 | `data_gap_80024A0C` | `0x80025860` | `0x0900079B` | `j` | `j           L_84001E6C` |
| funcs_7.c:5345 | `data_gap_80024A0C` | `0x800258B0` | `0x0900044B` | `j` | `j           L_8400112C` |
| funcs_7.c:5366 | `data_gap_80024A0C` | `0x800258D0` | `0x481D6800` | `opcode_0x12` | `mfc2        $sp, $13` |
| funcs_7.c:5368 | `data_gap_80024A0C` | `0x800258D4` | `0x48076900` | `opcode_0x12` | `.word       0x48076900                   # mfc2        $a3, $13 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5421 | `data_gap_80024A0C` | `0x80025910` | `0x489D6800` | `opcode_0x12` | `mtc2        $sp, $13` |
| funcs_7.c:5423 | `data_gap_80024A0C` | `0x80025914` | `0x48876900` | `opcode_0x12` | `.word       0x48876900                   # mtc2        $a3, $13 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5438 | `data_gap_80024A0C` | `0x80025928` | `0xCBA41800` | `opcode_0x32` | `lwc2        $4, 0x1800($sp)` |
| funcs_7.c:5440 | `data_gap_80024A0C` | `0x8002592C` | `0xCBA51801` | `opcode_0x32` | `lwc2        $5, 0x1801($sp)` |
| funcs_7.c:5442 | `data_gap_80024A0C` | `0x80025930` | `0xC8E91800` | `opcode_0x32` | `lwc2        $9, 0x1800($a3)` |
| funcs_7.c:5444 | `data_gap_80024A0C` | `0x80025934` | `0xC8EA1801` | `opcode_0x32` | `lwc2        $10, 0x1801($a3)` |
| funcs_7.c:5448 | `data_gap_80024A0C` | `0x8002593C` | `0xC8411800` | `opcode_0x32` | `lwc2        $1, 0x1800($v0)` |
| funcs_7.c:5450 | `data_gap_80024A0C` | `0x80025940` | `0x4B7E0807` | `opcode_0x12` | `.word       0x4B7E0807                   # INVALID     $k1, $fp, 0x807 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5452 | `data_gap_80024A0C` | `0x80025944` | `0x4A012B06` | `opcode_0x12` | `.word       0x4A012B06                   # INVALID     $s0, $at, 0x2B06 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5454 | `data_gap_80024A0C` | `0x80025948` | `0x4A0122CF` | `opcode_0x12` | `.word       0x4A0122CF                   # INVALID     $s0, $at, 0x22CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5456 | `data_gap_80024A0C` | `0x8002594C` | `0x4B1EF30E` | `opcode_0x12` | `.word       0x4B1EF30E                   # INVALID     $t8, $fp, -0xCF2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5458 | `data_gap_80024A0C` | `0x80025950` | `0x4A00570E` | `opcode_0x12` | `.word       0x4A00570E                   # INVALID     $s0, $zero, 0x570E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5460 | `data_gap_80024A0C` | `0x80025954` | `0x4A004F4F` | `opcode_0x12` | `.word       0x4A004F4F                   # INVALID     $s0, $zero, 0x4F4F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5462 | `data_gap_80024A0C` | `0x80025958` | `0x4B1EF70E` | `opcode_0x12` | `.word       0x4B1EF70E                   # INVALID     $t8, $fp, -0x8F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5464 | `data_gap_80024A0C` | `0x8002595C` | `0x4A5CE694` | `opcode_0x12` | `.word       0x4A5CE694                   # INVALID     $s2, $gp, -0x196C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5466 | `data_gap_80024A0C` | `0x80025960` | `0x4A5DEED0` | `opcode_0x12` | `.word       0x4A5DEED0                   # INVALID     $s2, $sp, -0x1130 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5468 | `data_gap_80024A0C` | `0x80025964` | `0x4ABAD714` | `opcode_0x12` | `.word       0x4ABAD714                   # INVALID     $s5, $k0, -0x28EC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5470 | `data_gap_80024A0C` | `0x80025968` | `0x4ABBDF50` | `opcode_0x12` | `.word       0x4ABBDF50                   # INVALID     $s5, $k1, -0x20B0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5472 | `data_gap_80024A0C` | `0x8002596C` | `0x4802EB00` | `opcode_0x12` | `.word       0x4802EB00                   # mfc2        $v0, $29 # 00000300 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5474 | `data_gap_80024A0C` | `0x80025970` | `0x4B7D59F2` | `opcode_0x12` | `.word       0x4B7D59F2                   # INVALID     $k1, $sp, 0x59F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5476 | `data_gap_80024A0C` | `0x80025974` | `0x4B7C58F1` | `opcode_0x12` | `.word       0x4B7C58F1                   # INVALID     $k1, $gp, 0x58F1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5478 | `data_gap_80024A0C` | `0x80025978` | `0x4B1E59F2` | `opcode_0x12` | `.word       0x4B1E59F2                   # INVALID     $t8, $fp, 0x59F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5480 | `data_gap_80024A0C` | `0x8002597C` | `0x4B5E18C6` | `opcode_0x12` | `.word       0x4B5E18C6                   # INVALID     $k0, $fp, 0x18C6 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5484 | `data_gap_80024A0C` | `0x80025984` | `0x4B5E39CF` | `opcode_0x12` | `.word       0x4B5E39CF                   # INVALID     $k0, $fp, 0x39CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5488 | `data_gap_80024A0C` | `0x80025984` | `0x4B5E39CF` | `opcode_0x12` | `.word       0x4B5E39CF                   # INVALID     $k0, $fp, 0x39CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5490 | `data_gap_80024A0C` | `0x80025988` | `0x4B7E18C6` | `opcode_0x12` | `.word       0x4B7E18C6                   # INVALID     $k1, $fp, 0x18C6 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5492 | `data_gap_80024A0C` | `0x8002598C` | `0x4B7E39CF` | `opcode_0x12` | `.word       0x4B7E39CF                   # INVALID     $k1, $fp, 0x39CF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5495 | `data_gap_80024A0C` | `0x80025990` | `0x4B1E39E1` | `opcode_0x12` | `.word       0x4B1E39E1                   # INVALID     $t8, $fp, 0x39E1 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5497 | `data_gap_80024A0C` | `0x80025994` | `0x4B7E18E7` | `opcode_0x12` | `.word       0x4B7E18E7                   # INVALID     $k1, $fp, 0x18E7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5499 | `data_gap_80024A0C` | `0x80025998` | `0x4B63E704` | `opcode_0x12` | `.word       0x4B63E704                   # INVALID     $k1, $v1, -0x18FC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5501 | `data_gap_80024A0C` | `0x8002599C` | `0x4B63EF4D` | `opcode_0x12` | `.word       0x4B63EF4D                   # INVALID     $k1, $v1, -0x10B3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5504 | `data_gap_80024A0C` | `0x800259A4` | `0x4B1EF70E` | `opcode_0x12` | `.word       0x4B1EF70E                   # INVALID     $t8, $fp, -0x8F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5508 | `data_gap_80024A0C` | `0x800259A4` | `0x4B1EF70E` | `opcode_0x12` | `.word       0x4B1EF70E                   # INVALID     $t8, $fp, -0x8F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5511 | `data_gap_80024A0C` | `0x800259A8` | `0x4A4C6714` | `opcode_0x12` | `.word       0x4A4C6714                   # INVALID     $s2, $t4, 0x6714 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5513 | `data_gap_80024A0C` | `0x800259AC` | `0x4A4B5F50` | `opcode_0x12` | `.word       0x4A4B5F50                   # INVALID     $s2, $t3, 0x5F50 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5515 | `data_gap_80024A0C` | `0x800259B0` | `0x4ABCE314` | `opcode_0x12` | `.word       0x4ABCE314                   # INVALID     $s5, $gp, -0x1CEC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5517 | `data_gap_80024A0C` | `0x800259B4` | `0x4ABDEAD0` | `opcode_0x12` | `.word       0x4ABDEAD0                   # INVALID     $s5, $sp, -0x1530 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5519 | `data_gap_80024A0C` | `0x800259B8` | `0x4A1A63C4` | `opcode_0x12` | `.word       0x4A1A63C4                   # INVALID     $s0, $k0, 0x63C4 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5521 | `data_gap_80024A0C` | `0x800259BC` | `0x4A1A5BCD` | `opcode_0x12` | `.word       0x4A1A5BCD                   # INVALID     $s0, $k0, 0x5BCD # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5523 | `data_gap_80024A0C` | `0x800259C0` | `0x4A1B63CE` | `opcode_0x12` | `.word       0x4A1B63CE                   # INVALID     $s0, $k1, 0x63CE # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5525 | `data_gap_80024A0C` | `0x800259C4` | `0x4A1B5A0F` | `opcode_0x12` | `.word       0x4A1B5A0F                   # INVALID     $s0, $k1, 0x5A0F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5527 | `data_gap_80024A0C` | `0x800259C8` | `0x4BBEF704` | `opcode_0x12` | `.word       0x4BBEF704                   # INVALID     $sp, $fp, -0x8FC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5529 | `data_gap_80024A0C` | `0x800259CC` | `0x4B637BCC` | `opcode_0x12` | `.word       0x4B637BCC                   # INVALID     $k1, $v1, 0x7BCC # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5531 | `data_gap_80024A0C` | `0x800259D0` | `0x4B63420D` | `opcode_0x12` | `.word       0x4B63420D                   # INVALID     $k1, $v1, 0x420D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5533 | `data_gap_80024A0C` | `0x800259D4` | `0x4B1EF3CE` | `opcode_0x12` | `.word       0x4B1EF3CE                   # INVALID     $t8, $fp, -0xC32 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5535 | `data_gap_80024A0C` | `0x800259D8` | `0x4B1E4221` | `opcode_0x12` | `.word       0x4B1E4221                   # INVALID     $t8, $fp, 0x4221 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5537 | `data_gap_80024A0C` | `0x800259DC` | `0x4B7E7BE7` | `opcode_0x12` | `.word       0x4B7E7BE7                   # INVALID     $k1, $fp, 0x7BE7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5539 | `data_gap_80024A0C` | `0x800259E0` | `0x4B1E7BE2` | `opcode_0x12` | `.word       0x4B1E7BE2                   # INVALID     $t8, $fp, 0x7BE2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5541 | `data_gap_80024A0C` | `0x800259E4` | `0x4B3E7BE7` | `opcode_0x12` | `.word       0x4B3E7BE7                   # INVALID     $t9, $fp, 0x7BE7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5543 | `data_gap_80024A0C` | `0x800259E8` | `0x4B1E7A2D` | `opcode_0x12` | `.word       0x4B1E7A2D                   # INVALID     $t8, $fp, 0x7A2D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5545 | `data_gap_80024A0C` | `0x800259EC` | `0x4B3E4214` | `opcode_0x12` | `.word       0x4B3E4214                   # INVALID     $t9, $fp, 0x4214 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5547 | `data_gap_80024A0C` | `0x800259F0` | `0x4A1DEF50` | `opcode_0x12` | `.word       0x4A1DEF50                   # INVALID     $s0, $sp, -0x10B0 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5549 | `data_gap_80024A0C` | `0x800259F4` | `0x4AE82F04` | `opcode_0x12` | `.word       0x4AE82F04                   # INVALID     $s7, $t0, 0x2F04 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5551 | `data_gap_80024A0C` | `0x800259F8` | `0x4AE8274D` | `opcode_0x12` | `.word       0x4AE8274D                   # INVALID     $s7, $t0, 0x274D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5553 | `data_gap_80024A0C` | `0x800259FC` | `0x4AEF570C` | `opcode_0x12` | `.word       0x4AEF570C                   # INVALID     $s7, $t7, 0x570C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5555 | `data_gap_80024A0C` | `0x80025A00` | `0x4AEF4F4D` | `opcode_0x12` | `.word       0x4AEF4F4D                   # INVALID     $s7, $t7, 0x4F4D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5557 | `data_gap_80024A0C` | `0x80025A04` | `0x4B1EF70E` | `opcode_0x12` | `.word       0x4B1EF70E                   # INVALID     $t8, $fp, -0x8F2 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5559 | `data_gap_80024A0C` | `0x80025A08` | `0xCBAC3802` | `opcode_0x32` | `lwc2        $12, 0x3802($sp)` |
| funcs_7.c:5561 | `data_gap_80024A0C` | `0x80025A0C` | `0xC8EB3802` | `opcode_0x32` | `lwc2        $11, 0x3802($a3)` |
| funcs_7.c:5563 | `data_gap_80024A0C` | `0x80025A10` | `0xCBAC1405` | `opcode_0x32` | `lwc2        $12, 0x1405($sp)` |
| funcs_7.c:5565 | `data_gap_80024A0C` | `0x80025A14` | `0xC8EB1405` | `opcode_0x32` | `lwc2        $11, 0x1405($a3)` |
| funcs_7.c:5567 | `data_gap_80024A0C` | `0x80025A18` | `0x4B686485` | `opcode_0x12` | `.word       0x4B686485                   # INVALID     $k1, $t0, 0x6485 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5569 | `data_gap_80024A0C` | `0x80025A1C` | `0x4B6F5C8D` | `opcode_0x12` | `.word       0x4B6F5C8D                   # INVALID     $k1, $t7, 0x5C8D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5571 | `data_gap_80024A0C` | `0x80025A20` | `0xE9323802` | `opcode_0x3A` | `swc2        $18, 0x3802($t1)` |
| funcs_7.c:5574 | `data_gap_80024A0C` | `0x80025A28` | `0xE9321405` | `opcode_0x3A` | `swc2        $18, 0x1405($t1)` |
| funcs_7.c:5578 | `data_gap_80024A0C` | `0x80025A28` | `0xE9321405` | `opcode_0x3A` | `swc2        $18, 0x1405($t1)` |
| funcs_7.c:5587 | `data_gap_80024A0C` | `0x80025A38` | `0x09000594` | `j` | `j           L_84001650` |
| funcs_7.c:5615 | `data_gap_80024A0C` | `0x80025A60` | `0x40822000` | `cop0` | `mtc0        $v0, Context` |
| funcs_7.c:5617 | `data_gap_80024A0C` | `0x80025A64` | `0x0000000D` | `break $zero,$zero,$zero` | `break       0` |
| funcs_7.c:5682 | `data_gap_80024A0C` | `0x80025ACC` | `0x4A000015` | `opcode_0x12` | `.word       0x4A000015                   # INVALID     $s0, $zero, 0x15 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5684 | `data_gap_80024A0C` | `0x80025AD0` | `0x4A010855` | `opcode_0x12` | `.word       0x4A010855                   # INVALID     $s0, $at, 0x855 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5708 | `data_gap_80024A0C` | `0x80025B00` | `0x489A1800` | `opcode_0x12` | `mtc2        $k0, $3` |
| funcs_7.c:5738 | `data_gap_80024A0C` | `0x80025B34` | `0x090007A2` | `j` | `j           L_84001E88` |
| funcs_7.c:5756 | `data_gap_80024A0C` | `0x80025B54` | `0x48981000` | `opcode_0x12` | `mtc2        $t8, $2` |
| funcs_7.c:5758 | `data_gap_80024A0C` | `0x80025B58` | `0x4B031087` | `opcode_0x12` | `.word       0x4B031087                   # INVALID     $t8, $v1, 0x1087 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5760 | `data_gap_80024A0C` | `0x80025B5C` | `0x48181000` | `opcode_0x12` | `mfc2        $t8, $2` |
| funcs_7.c:5805 | `data_gap_80024A0C` | `0x80025B98` | `0xC8800080` | `opcode_0x32` | `lwc2        $0, 0x80($a0)` |
| funcs_7.c:5807 | `data_gap_80024A0C` | `0x80025B9C` | `0xC8800181` | `opcode_0x32` | `lwc2        $0, 0x181($a0)` |
| funcs_7.c:5809 | `data_gap_80024A0C` | `0x80025BA0` | `0xC8800282` | `opcode_0x32` | `lwc2        $0, 0x282($a0)` |
| funcs_7.c:5811 | `data_gap_80024A0C` | `0x80025BA4` | `0xC8800383` | `opcode_0x32` | `lwc2        $0, 0x383($a0)` |
| funcs_7.c:5815 | `data_gap_80024A0C` | `0x80025BAC` | `0xC8610080` | `opcode_0x32` | `lwc2        $1, 0x80($v1)` |
| funcs_7.c:5817 | `data_gap_80024A0C` | `0x80025BB0` | `0xC8610181` | `opcode_0x32` | `lwc2        $1, 0x181($v1)` |
| funcs_7.c:5819 | `data_gap_80024A0C` | `0x80025BB4` | `0xC8610282` | `opcode_0x32` | `lwc2        $1, 0x282($v1)` |
| funcs_7.c:5821 | `data_gap_80024A0C` | `0x80025BB8` | `0xC8610383` | `opcode_0x32` | `lwc2        $1, 0x383($v1)` |
| funcs_7.c:5823 | `data_gap_80024A0C` | `0x80025BBC` | `0x4A010094` | `opcode_0x12` | `.word       0x4A010094                   # INVALID     $s0, $at, 0x94 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5825 | `data_gap_80024A0C` | `0x80025BC0` | `0x4BBF1085` | `opcode_0x12` | `.word       0x4BBF1085                   # INVALID     $sp, $ra, 0x1085 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5829 | `data_gap_80024A0C` | `0x80025BC8` | `0xE8420080` | `opcode_0x3A` | `swc2        $2, 0x80($v0)` |
| funcs_7.c:5831 | `data_gap_80024A0C` | `0x80025BCC` | `0xE8420181` | `opcode_0x3A` | `swc2        $2, 0x181($v0)` |
| funcs_7.c:5833 | `data_gap_80024A0C` | `0x80025BD0` | `0xE8420282` | `opcode_0x3A` | `swc2        $2, 0x282($v0)` |
| funcs_7.c:5835 | `data_gap_80024A0C` | `0x80025BD4` | `0xE8420383` | `opcode_0x3A` | `swc2        $2, 0x383($v0)` |
| funcs_7.c:5837 | `data_gap_80024A0C` | `0x80025BD8` | `0x090007CA` | `j` | `j           L_84001F28` |
| funcs_7.c:5884 | `data_gap_80024A0C` | `0x80025C1C` | `0x0900049A` | `j` | `j           L_84001268` |
| funcs_7.c:5893 | `data_gap_80024A0C` | `0x80025C2C` | `0xCA20080C` | `opcode_0x32` | `lwc2        $0, 0x80C($s1)` |
| funcs_7.c:5895 | `data_gap_80024A0C` | `0x80025C30` | `0xCA200A0E` | `opcode_0x32` | `lwc2        $0, 0xA0E($s1)` |
| funcs_7.c:5899 | `data_gap_80024A0C` | `0x80025C38` | `0x48830100` | `opcode_0x12` | `.word       0x48830100                   # mtc2        $v1, $0 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5901 | `data_gap_80024A0C` | `0x80025C3C` | `0x4A021095` | `opcode_0x12` | `.word       0x4A021095                   # INVALID     $s0, $v0, 0x1095 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5903 | `data_gap_80024A0C` | `0x80025C40` | `0x48821000` | `opcode_0x12` | `mtc2        $v0, $2` |
| funcs_7.c:5905 | `data_gap_80024A0C` | `0x80025C44` | `0x4A0318D5` | `opcode_0x12` | `.word       0x4A0318D5                   # INVALID     $s0, $v1, 0x18D5 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5907 | `data_gap_80024A0C` | `0x80025C48` | `0x48821A00` | `opcode_0x12` | `.word       0x48821A00                   # mtc2        $v0, $3 # 00000200 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5909 | `data_gap_80024A0C` | `0x80025C4C` | `0x4A010855` | `opcode_0x12` | `.word       0x4A010855                   # INVALID     $s0, $at, 0x855 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5911 | `data_gap_80024A0C` | `0x80025C50` | `0xCA21097E` | `opcode_0x32` | `lwc2        $1, 0x97E($s1)` |
| funcs_7.c:5921 | `data_gap_80024A0C` | `0x80025C5C` | `0x4B1E1054` | `opcode_0x12` | `.word       0x4B1E1054                   # INVALID     $t8, $fp, 0x1054 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5923 | `data_gap_80024A0C` | `0x80025C60` | `0xCA21097F` | `opcode_0x32` | `lwc2        $1, 0x97F($s1)` |
| funcs_7.c:5933 | `data_gap_80024A0C` | `0x80025C6C` | `0x4B1E1854` | `opcode_0x12` | `.word       0x4B1E1854                   # INVALID     $t8, $fp, 0x1854 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5935 | `data_gap_80024A0C` | `0x80025C70` | `0xCA210900` | `opcode_0x32` | `lwc2        $1, 0x900($s1)` |
| funcs_7.c:5945 | `data_gap_80024A0C` | `0x80025C7C` | `0x4A031054` | `opcode_0x12` | `.word       0x4A031054                   # INVALID     $s0, $v1, 0x1054 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5947 | `data_gap_80024A0C` | `0x80025C80` | `0xCA210901` | `opcode_0x32` | `lwc2        $1, 0x901($s1)` |
| funcs_7.c:5957 | `data_gap_80024A0C` | `0x80025C8C` | `0x0900049A` | `j` | `j           L_84001268` |
| funcs_7.c:5961 | `data_gap_80024A0C` | `0x80025C94` | `0x4A000854` | `opcode_0x12` | `.word       0x4A000854                   # INVALID     $s0, $zero, 0x854 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5964 | `data_gap_80024A0C` | `0x80025C9C` | `0xE8611800` | `opcode_0x3A` | `swc2        $1, 0x1800($v1)` |
| funcs_7.c:5967 | `data_gap_80024A0C` | `0x80025C9C` | `0xE8611800` | `opcode_0x3A` | `swc2        $1, 0x1800($v1)` |
| funcs_7.c:5989 | `data_gap_80024A0C` | `0x80025CB8` | `0x4A000015` | `opcode_0x12` | `.word       0x4A000015                   # INVALID     $s0, $zero, 0x15 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5991 | `data_gap_80024A0C` | `0x80025CBC` | `0x4A010855` | `opcode_0x12` | `.word       0x4A010855                   # INVALID     $s0, $at, 0x855 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:5993 | `data_gap_80024A0C` | `0x80025CC0` | `0x4A021095` | `opcode_0x12` | `.word       0x4A021095                   # INVALID     $s0, $v0, 0x1095 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6001 | `data_gap_80024A0C` | `0x80025CD0` | `0x48861800` | `opcode_0x12` | `mtc2        $a2, $3` |
| funcs_7.c:6003 | `data_gap_80024A0C` | `0x80025CD4` | `0x48821900` | `opcode_0x12` | `.word       0x48821900                   # mtc2        $v0, $3 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6058 | `data_gap_80024A0C` | `0x80025D2C` | `0xC9C00800` | `opcode_0x32` | `lwc2        $0, 0x800($t6)` |
| funcs_7.c:6060 | `data_gap_80024A0C` | `0x80025D30` | `0xCB200180` | `opcode_0x32` | `lwc2        $0, 0x180($t9)` |
| funcs_7.c:6062 | `data_gap_80024A0C` | `0x80025D34` | `0xCB200281` | `opcode_0x32` | `lwc2        $0, 0x281($t9)` |
| funcs_7.c:6064 | `data_gap_80024A0C` | `0x80025D38` | `0xCB200382` | `opcode_0x32` | `lwc2        $0, 0x382($t9)` |
| funcs_7.c:6066 | `data_gap_80024A0C` | `0x80025D3C` | `0xCB200483` | `opcode_0x32` | `lwc2        $0, 0x483($t9)` |
| funcs_7.c:6068 | `data_gap_80024A0C` | `0x80025D40` | `0xC9E10800` | `opcode_0x32` | `lwc2        $1, 0x800($t7)` |
| funcs_7.c:6070 | `data_gap_80024A0C` | `0x80025D44` | `0xCB410180` | `opcode_0x32` | `lwc2        $1, 0x180($k0)` |
| funcs_7.c:6072 | `data_gap_80024A0C` | `0x80025D48` | `0xCB410281` | `opcode_0x32` | `lwc2        $1, 0x281($k0)` |
| funcs_7.c:6074 | `data_gap_80024A0C` | `0x80025D4C` | `0xCB410382` | `opcode_0x32` | `lwc2        $1, 0x382($k0)` |
| funcs_7.c:6076 | `data_gap_80024A0C` | `0x80025D50` | `0xCB410483` | `opcode_0x32` | `lwc2        $1, 0x483($k0)` |
| funcs_7.c:6078 | `data_gap_80024A0C` | `0x80025D54` | `0xC9A20800` | `opcode_0x32` | `lwc2        $2, 0x800($t5)` |
| funcs_7.c:6080 | `data_gap_80024A0C` | `0x80025D58` | `0xCB020180` | `opcode_0x32` | `lwc2        $2, 0x180($t8)` |
| funcs_7.c:6082 | `data_gap_80024A0C` | `0x80025D5C` | `0xCB020281` | `opcode_0x32` | `lwc2        $2, 0x281($t8)` |
| funcs_7.c:6084 | `data_gap_80024A0C` | `0x80025D60` | `0xCB020382` | `opcode_0x32` | `lwc2        $2, 0x382($t8)` |
| funcs_7.c:6086 | `data_gap_80024A0C` | `0x80025D64` | `0xCB020483` | `opcode_0x32` | `lwc2        $2, 0x483($t8)` |
| funcs_7.c:6088 | `data_gap_80024A0C` | `0x80025D68` | `0x4A010114` | `opcode_0x12` | `.word       0x4A010114                   # INVALID     $s0, $at, 0x114 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6090 | `data_gap_80024A0C` | `0x80025D6C` | `0x4B032105` | `opcode_0x12` | `.word       0x4B032105                   # INVALID     $t8, $v1, 0x2105 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6092 | `data_gap_80024A0C` | `0x80025D70` | `0x4B23110D` | `opcode_0x12` | `.word       0x4B23110D                   # INVALID     $t9, $v1, 0x110D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6094 | `data_gap_80024A0C` | `0x80025D74` | `0xE9A40800` | `opcode_0x3A` | `swc2        $4, 0x800($t5)` |
| funcs_7.c:6096 | `data_gap_80024A0C` | `0x80025D78` | `0xEB040180` | `opcode_0x3A` | `swc2        $4, 0x180($t8)` |
| funcs_7.c:6098 | `data_gap_80024A0C` | `0x80025D7C` | `0xEB040281` | `opcode_0x3A` | `swc2        $4, 0x281($t8)` |
| funcs_7.c:6100 | `data_gap_80024A0C` | `0x80025D80` | `0xEB040382` | `opcode_0x3A` | `swc2        $4, 0x382($t8)` |
| funcs_7.c:6102 | `data_gap_80024A0C` | `0x80025D84` | `0xEB040483` | `opcode_0x3A` | `swc2        $4, 0x483($t8)` |
| funcs_7.c:6130 | `data_gap_80024A0C` | `0x80025DA8` | `0xCA20080C` | `opcode_0x32` | `lwc2        $0, 0x80C($s1)` |
| funcs_7.c:6132 | `data_gap_80024A0C` | `0x80025DAC` | `0xCA200A0E` | `opcode_0x32` | `lwc2        $0, 0xA0E($s1)` |
| funcs_7.c:6136 | `data_gap_80024A0C` | `0x80025DB4` | `0x48830100` | `opcode_0x12` | `.word       0x48830100                   # mtc2        $v1, $0 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6138 | `data_gap_80024A0C` | `0x80025DB8` | `0x4A021095` | `opcode_0x12` | `.word       0x4A021095                   # INVALID     $s0, $v0, 0x1095 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6140 | `data_gap_80024A0C` | `0x80025DBC` | `0x48821000` | `opcode_0x12` | `mtc2        $v0, $2` |
| funcs_7.c:6142 | `data_gap_80024A0C` | `0x80025DC0` | `0x4A0318D5` | `opcode_0x12` | `.word       0x4A0318D5                   # INVALID     $s0, $v1, 0x18D5 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6144 | `data_gap_80024A0C` | `0x80025DC4` | `0x48821A00` | `opcode_0x12` | `.word       0x48821A00                   # mtc2        $v0, $3 # 00000200 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6146 | `data_gap_80024A0C` | `0x80025DC8` | `0x4B1E4073` | `opcode_0x12` | `.word       0x4B1E4073                   # INVALID     $t8, $fp, 0x4073 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6159 | `data_gap_80024A0C` | `0x80025DE0` | `0x4B1E5073` | `opcode_0x12` | `.word       0x4B1E5073                   # INVALID     $t8, $fp, 0x5073 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6166 | `data_gap_80024A0C` | `0x80025DEC` | `0xCB210900` | `opcode_0x32` | `lwc2        $1, 0x900($t9)` |
| funcs_7.c:6172 | `data_gap_80024A0C` | `0x80025DF8` | `0x4A000914` | `opcode_0x12` | `.word       0x4A000914                   # INVALID     $s0, $zero, 0x914 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6174 | `data_gap_80024A0C` | `0x80025DFC` | `0xE9A41800` | `opcode_0x3A` | `swc2        $4, 0x1800($t5)` |
| funcs_7.c:6176 | `data_gap_80024A0C` | `0x80025E00` | `0x4A030854` | `opcode_0x12` | `.word       0x4A030854                   # INVALID     $s0, $v1, 0x854 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6188 | `data_gap_80024A0C` | `0x80025E10` | `0x4A020854` | `opcode_0x12` | `.word       0x4A020854                   # INVALID     $s0, $v0, 0x854 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6206 | `data_gap_80024A0C` | `0x80025E28` | `0x09000574` | `j` | `j           L_840015D0` |
| funcs_7.c:6220 | `data_gap_80024A0C` | `0x80025E44` | `0x48821000` | `opcode_0x12` | `mtc2        $v0, $2` |
| funcs_7.c:6222 | `data_gap_80024A0C` | `0x80025E48` | `0x48801100` | `opcode_0x12` | `.word       0x48801100                   # mtc2        $zero, $2 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6224 | `data_gap_80024A0C` | `0x80025E4C` | `0x48801800` | `opcode_0x12` | `mtc2        $zero, $3` |
| funcs_7.c:6226 | `data_gap_80024A0C` | `0x80025E50` | `0x48821900` | `opcode_0x12` | `.word       0x48821900                   # mtc2        $v0, $3 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6230 | `data_gap_80024A0C` | `0x80025E58` | `0x48822000` | `opcode_0x12` | `mtc2        $v0, $4` |
| funcs_7.c:6232 | `data_gap_80024A0C` | `0x80025E5C` | `0x4B041107` | `opcode_0x12` | `.word       0x4B041107                   # INVALID     $t8, $a0, 0x1107 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6234 | `data_gap_80024A0C` | `0x80025E60` | `0x4B1E4073` | `opcode_0x12` | `.word       0x4B1E4073                   # INVALID     $t8, $fp, 0x4073 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6239 | `data_gap_80024A0C` | `0x80025E68` | `0x4B044873` | `opcode_0x12` | `.word       0x4B044873                   # INVALID     $t8, $a0, 0x4873 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6250 | `data_gap_80024A0C` | `0x80025E7C` | `0xE9A11005` | `opcode_0x3A` | `swc2        $1, 0x1005($t5)` |
| funcs_7.c:6252 | `data_gap_80024A0C` | `0x80025E80` | `0x4A030855` | `opcode_0x12` | `.word       0x4A030855                   # INVALID     $s0, $v1, 0x855 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6274 | `data_gap_80024A0C` | `0x80025E9C` | `0x4A020854` | `opcode_0x12` | `.word       0x4A020854                   # INVALID     $s0, $v0, 0x854 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6286 | `data_gap_80024A0C` | `0x80025EAC` | `0x0900049A` | `j` | `j           L_84001268` |
| funcs_7.c:6292 | `data_gap_80024A0C` | `0x80025EB8` | `0x4A052955` | `opcode_0x12` | `.word       0x4A052955                   # INVALID     $s0, $a1, 0x2955 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6294 | `data_gap_80024A0C` | `0x80025EBC` | `0x4A063195` | `opcode_0x12` | `.word       0x4A063195                   # INVALID     $s0, $a2, 0x3195 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6296 | `data_gap_80024A0C` | `0x80025EC0` | `0x4A0739D5` | `opcode_0x12` | `.word       0x4A0739D5                   # INVALID     $s0, $a3, 0x39D5 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6300 | `data_gap_80024A0C` | `0x80025EC8` | `0x48821800` | `opcode_0x12` | `mtc2        $v0, $3` |
| funcs_7.c:6302 | `data_gap_80024A0C` | `0x80025ECC` | `0x488A1900` | `opcode_0x12` | `.word       0x488A1900                   # mtc2        $t2, $3 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6304 | `data_gap_80024A0C` | `0x80025ED0` | `0x4B2318C7` | `opcode_0x12` | `.word       0x4B2318C7                   # INVALID     $t9, $v1, 0x18C7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6306 | `data_gap_80024A0C` | `0x80025ED4` | `0x48081800` | `opcode_0x12` | `mfc2        $t0, $3` |
| funcs_7.c:6380 | `data_gap_80024A0C` | `0x80025F44` | `0x48861800` | `opcode_0x12` | `mtc2        $a2, $3` |
| funcs_7.c:6382 | `data_gap_80024A0C` | `0x80025F48` | `0x48821900` | `opcode_0x12` | `.word       0x48821900                   # mtc2        $v0, $3 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6401 | `data_gap_80024A0C` | `0x80025F64` | `0x48831A00` | `opcode_0x12` | `.word       0x48831A00                   # mtc2        $v1, $3 # 00000200 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6403 | `data_gap_80024A0C` | `0x80025F68` | `0x48821B00` | `opcode_0x12` | `.word       0x48821B00                   # mtc2        $v0, $3 # 00000300 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6444 | `data_gap_80024A0C` | `0x80025FA8` | `0x090007BE` | `j` | `j           L_84001EF8` |
| funcs_7.c:6451 | `data_gap_80024A0C` | `0x80025FB4` | `0x4BBF50F3` | `opcode_0x12` | `.word       0x4BBF50F3                   # INVALID     $sp, $ra, 0x50F3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6455 | `data_gap_80024A0C` | `0x80025FB4` | `0x4BBF50F3` | `opcode_0x12` | `.word       0x4BBF50F3                   # INVALID     $sp, $ra, 0x50F3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6457 | `data_gap_80024A0C` | `0x80025FB8` | `0x4BBF58F3` | `opcode_0x12` | `.word       0x4BBF58F3                   # INVALID     $sp, $ra, 0x58F3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6463 | `data_gap_80024A0C` | `0x80025FC4` | `0x48861800` | `opcode_0x12` | `mtc2        $a2, $3` |
| funcs_7.c:6465 | `data_gap_80024A0C` | `0x80025FC8` | `0x48821900` | `opcode_0x12` | `.word       0x48821900                   # mtc2        $v0, $3 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6517 | `data_gap_80024A0C` | `0x80026014` | `0x0900049A` | `j` | `j           L_84001268` |
| funcs_7.c:6521 | `data_gap_80024A0C` | `0x8002601C` | `0xC9C50800` | `opcode_0x32` | `lwc2        $5, 0x800($t6)` |
| funcs_7.c:6523 | `data_gap_80024A0C` | `0x80026020` | `0xCB250180` | `opcode_0x32` | `lwc2        $5, 0x180($t9)` |
| funcs_7.c:6525 | `data_gap_80024A0C` | `0x80026024` | `0xCB250281` | `opcode_0x32` | `lwc2        $5, 0x281($t9)` |
| funcs_7.c:6527 | `data_gap_80024A0C` | `0x80026028` | `0xCB250382` | `opcode_0x32` | `lwc2        $5, 0x382($t9)` |
| funcs_7.c:6529 | `data_gap_80024A0C` | `0x8002602C` | `0xCB250483` | `opcode_0x32` | `lwc2        $5, 0x483($t9)` |
| funcs_7.c:6531 | `data_gap_80024A0C` | `0x80026030` | `0xC9E60800` | `opcode_0x32` | `lwc2        $6, 0x800($t7)` |
| funcs_7.c:6533 | `data_gap_80024A0C` | `0x80026034` | `0xCB460180` | `opcode_0x32` | `lwc2        $6, 0x180($k0)` |
| funcs_7.c:6535 | `data_gap_80024A0C` | `0x80026038` | `0xCB460281` | `opcode_0x32` | `lwc2        $6, 0x281($k0)` |
| funcs_7.c:6537 | `data_gap_80024A0C` | `0x8002603C` | `0xCB460382` | `opcode_0x32` | `lwc2        $6, 0x382($k0)` |
| funcs_7.c:6539 | `data_gap_80024A0C` | `0x80026040` | `0xCB460483` | `opcode_0x32` | `lwc2        $6, 0x483($k0)` |
| funcs_7.c:6541 | `data_gap_80024A0C` | `0x80026044` | `0x4A062814` | `opcode_0x12` | `.word       0x4A062814                   # INVALID     $s0, $a2, 0x2814 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6543 | `data_gap_80024A0C` | `0x80026048` | `0x4BBF0005` | `opcode_0x12` | `.word       0x4BBF0005                   # INVALID     $sp, $ra, 0x5 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6545 | `data_gap_80024A0C` | `0x8002604C` | `0xE9A00800` | `opcode_0x3A` | `swc2        $0, 0x800($t5)` |
| funcs_7.c:6547 | `data_gap_80024A0C` | `0x80026050` | `0xEB000180` | `opcode_0x3A` | `swc2        $0, 0x180($t8)` |
| funcs_7.c:6549 | `data_gap_80024A0C` | `0x80026054` | `0xEB000281` | `opcode_0x3A` | `swc2        $0, 0x281($t8)` |
| funcs_7.c:6551 | `data_gap_80024A0C` | `0x80026058` | `0xEB000382` | `opcode_0x3A` | `swc2        $0, 0x382($t8)` |
| funcs_7.c:6553 | `data_gap_80024A0C` | `0x8002605C` | `0xEB000483` | `opcode_0x3A` | `swc2        $0, 0x483($t8)` |
| funcs_7.c:6561 | `data_gap_80024A0C` | `0x80026068` | `0xC9C50800` | `opcode_0x32` | `lwc2        $5, 0x800($t6)` |
| funcs_7.c:6563 | `data_gap_80024A0C` | `0x8002606C` | `0xCB250180` | `opcode_0x32` | `lwc2        $5, 0x180($t9)` |
| funcs_7.c:6565 | `data_gap_80024A0C` | `0x80026070` | `0xCB250281` | `opcode_0x32` | `lwc2        $5, 0x281($t9)` |
| funcs_7.c:6567 | `data_gap_80024A0C` | `0x80026074` | `0xCB250382` | `opcode_0x32` | `lwc2        $5, 0x382($t9)` |
| funcs_7.c:6569 | `data_gap_80024A0C` | `0x80026078` | `0xCB250483` | `opcode_0x32` | `lwc2        $5, 0x483($t9)` |
| funcs_7.c:6571 | `data_gap_80024A0C` | `0x8002607C` | `0xC9E60800` | `opcode_0x32` | `lwc2        $6, 0x800($t7)` |
| funcs_7.c:6573 | `data_gap_80024A0C` | `0x80026080` | `0xCB460180` | `opcode_0x32` | `lwc2        $6, 0x180($k0)` |
| funcs_7.c:6575 | `data_gap_80024A0C` | `0x80026084` | `0xCB460281` | `opcode_0x32` | `lwc2        $6, 0x281($k0)` |
| funcs_7.c:6577 | `data_gap_80024A0C` | `0x80026088` | `0xCB460382` | `opcode_0x32` | `lwc2        $6, 0x382($k0)` |
| funcs_7.c:6579 | `data_gap_80024A0C` | `0x8002608C` | `0xCB460483` | `opcode_0x32` | `lwc2        $6, 0x483($k0)` |
| funcs_7.c:6581 | `data_gap_80024A0C` | `0x80026090` | `0xC9A70800` | `opcode_0x32` | `lwc2        $7, 0x800($t5)` |
| funcs_7.c:6583 | `data_gap_80024A0C` | `0x80026094` | `0xCB070180` | `opcode_0x32` | `lwc2        $7, 0x180($t8)` |
| funcs_7.c:6585 | `data_gap_80024A0C` | `0x80026098` | `0xCB070281` | `opcode_0x32` | `lwc2        $7, 0x281($t8)` |
| funcs_7.c:6587 | `data_gap_80024A0C` | `0x8002609C` | `0xCB070382` | `opcode_0x32` | `lwc2        $7, 0x382($t8)` |
| funcs_7.c:6589 | `data_gap_80024A0C` | `0x800260A0` | `0xCB070483` | `opcode_0x32` | `lwc2        $7, 0x483($t8)` |
| funcs_7.c:6591 | `data_gap_80024A0C` | `0x800260A4` | `0x4B432805` | `opcode_0x12` | `.word       0x4B432805                   # INVALID     $k0, $v1, 0x2805 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6593 | `data_gap_80024A0C` | `0x800260A8` | `0x4B63304D` | `opcode_0x12` | `.word       0x4B63304D                   # INVALID     $k1, $v1, 0x304D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6595 | `data_gap_80024A0C` | `0x800260AC` | `0x4B40001D` | `opcode_0x12` | `.word       0x4B40001D                   # INVALID     $k0, $zero, 0x1D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6597 | `data_gap_80024A0C` | `0x800260B0` | `0x4B030104` | `opcode_0x12` | `.word       0x4B030104                   # INVALID     $t8, $v1, 0x104 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6599 | `data_gap_80024A0C` | `0x800260B4` | `0x4B03090D` | `opcode_0x12` | `.word       0x4B03090D                   # INVALID     $t8, $v1, 0x90D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6601 | `data_gap_80024A0C` | `0x800260B8` | `0x4B23384D` | `opcode_0x12` | `.word       0x4B23384D                   # INVALID     $t9, $v1, 0x384D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6603 | `data_gap_80024A0C` | `0x800260BC` | `0xE9A10800` | `opcode_0x3A` | `swc2        $1, 0x800($t5)` |
| funcs_7.c:6605 | `data_gap_80024A0C` | `0x800260C0` | `0xEB010180` | `opcode_0x3A` | `swc2        $1, 0x180($t8)` |
| funcs_7.c:6607 | `data_gap_80024A0C` | `0x800260C4` | `0xEB010281` | `opcode_0x3A` | `swc2        $1, 0x281($t8)` |
| funcs_7.c:6609 | `data_gap_80024A0C` | `0x800260C8` | `0xEB010382` | `opcode_0x3A` | `swc2        $1, 0x382($t8)` |
| funcs_7.c:6611 | `data_gap_80024A0C` | `0x800260CC` | `0xEB010483` | `opcode_0x3A` | `swc2        $1, 0x483($t8)` |
| funcs_7.c:6619 | `data_gap_80024A0C` | `0x800260D8` | `0x488A4000` | `opcode_0x12` | `mtc2        $t2, $8` |
| funcs_7.c:6621 | `data_gap_80024A0C` | `0x800260DC` | `0x4A084207` | `opcode_0x12` | `.word       0x4A084207                   # INVALID     $s0, $t0, 0x4207 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6633 | `data_gap_80024A0C` | `0x800260F4` | `0x48174000` | `opcode_0x12` | `mfc2        $s7, $8` |
| funcs_7.c:6679 | `data_gap_80024A0C` | `0x80026144` | `0xC9C50800` | `opcode_0x32` | `lwc2        $5, 0x800($t6)` |
| funcs_7.c:6681 | `data_gap_80024A0C` | `0x80026148` | `0xCB250180` | `opcode_0x32` | `lwc2        $5, 0x180($t9)` |
| funcs_7.c:6683 | `data_gap_80024A0C` | `0x8002614C` | `0xCB250281` | `opcode_0x32` | `lwc2        $5, 0x281($t9)` |
| funcs_7.c:6685 | `data_gap_80024A0C` | `0x80026150` | `0xCB250382` | `opcode_0x32` | `lwc2        $5, 0x382($t9)` |
| funcs_7.c:6687 | `data_gap_80024A0C` | `0x80026154` | `0xCB250483` | `opcode_0x32` | `lwc2        $5, 0x483($t9)` |
| funcs_7.c:6689 | `data_gap_80024A0C` | `0x80026158` | `0xC9E60800` | `opcode_0x32` | `lwc2        $6, 0x800($t7)` |
| funcs_7.c:6691 | `data_gap_80024A0C` | `0x8002615C` | `0xCB460180` | `opcode_0x32` | `lwc2        $6, 0x180($k0)` |
| funcs_7.c:6693 | `data_gap_80024A0C` | `0x80026160` | `0xCB460281` | `opcode_0x32` | `lwc2        $6, 0x281($k0)` |
| funcs_7.c:6695 | `data_gap_80024A0C` | `0x80026164` | `0xCB460382` | `opcode_0x32` | `lwc2        $6, 0x382($k0)` |
| funcs_7.c:6697 | `data_gap_80024A0C` | `0x80026168` | `0xCB460483` | `opcode_0x32` | `lwc2        $6, 0x483($k0)` |
| funcs_7.c:6699 | `data_gap_80024A0C` | `0x8002616C` | `0x4A062814` | `opcode_0x12` | `.word       0x4A062814                   # INVALID     $s0, $a2, 0x2814 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6701 | `data_gap_80024A0C` | `0x80026170` | `0x4BBF0005` | `opcode_0x12` | `.word       0x4BBF0005                   # INVALID     $sp, $ra, 0x5 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6703 | `data_gap_80024A0C` | `0x80026174` | `0xE9A00800` | `opcode_0x3A` | `swc2        $0, 0x800($t5)` |
| funcs_7.c:6705 | `data_gap_80024A0C` | `0x80026178` | `0xEB000180` | `opcode_0x3A` | `swc2        $0, 0x180($t8)` |
| funcs_7.c:6707 | `data_gap_80024A0C` | `0x8002617C` | `0xEB000281` | `opcode_0x3A` | `swc2        $0, 0x281($t8)` |
| funcs_7.c:6709 | `data_gap_80024A0C` | `0x80026180` | `0xEB000382` | `opcode_0x3A` | `swc2        $0, 0x382($t8)` |
| funcs_7.c:6711 | `data_gap_80024A0C` | `0x80026184` | `0xEB000483` | `opcode_0x3A` | `swc2        $0, 0x483($t8)` |
| funcs_7.c:6731 | `data_gap_80024A0C` | `0x8002619C` | `0x48861800` | `opcode_0x12` | `mtc2        $a2, $3` |
| funcs_7.c:6733 | `data_gap_80024A0C` | `0x800261A0` | `0x48821900` | `opcode_0x12` | `.word       0x48821900                   # mtc2        $v0, $3 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6735 | `data_gap_80024A0C` | `0x800261A4` | `0x488B4000` | `opcode_0x12` | `mtc2        $t3, $8` |
| funcs_7.c:6737 | `data_gap_80024A0C` | `0x800261A8` | `0x489E4100` | `opcode_0x12` | `.word       0x489E4100                   # mtc2        $fp, $8 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6758 | `data_gap_80024A0C` | `0x800261C8` | `0x48831A00` | `opcode_0x12` | `.word       0x48831A00                   # mtc2        $v1, $3 # 00000200 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6760 | `data_gap_80024A0C` | `0x800261CC` | `0x48821B00` | `opcode_0x12` | `.word       0x48821B00                   # mtc2        $v0, $3 # 00000300 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6764 | `data_gap_80024A0C` | `0x800261D4` | `0x48822000` | `opcode_0x12` | `mtc2        $v0, $4` |
| funcs_7.c:6766 | `data_gap_80024A0C` | `0x800261D8` | `0x48822100` | `opcode_0x12` | `.word       0x48822100                   # mtc2        $v0, $4 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6768 | `data_gap_80024A0C` | `0x800261DC` | `0x4A082107` | `opcode_0x12` | `.word       0x4A082107                   # INVALID     $s0, $t0, 0x2107 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6770 | `data_gap_80024A0C` | `0x800261E0` | `0x480E2000` | `opcode_0x12` | `mfc2        $t6, $4` |
| funcs_7.c:6772 | `data_gap_80024A0C` | `0x800261E4` | `0x48192100` | `opcode_0x12` | `.word       0x48192100                   # mfc2        $t9, $4 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6811 | `data_gap_80024A0C` | `0x80026220` | `0x090007D2` | `j` | `j           L_84001F48` |
| funcs_7.c:6818 | `data_gap_80024A0C` | `0x8002622C` | `0x4BBF50F3` | `opcode_0x12` | `.word       0x4BBF50F3                   # INVALID     $sp, $ra, 0x50F3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6822 | `data_gap_80024A0C` | `0x8002622C` | `0x4BBF50F3` | `opcode_0x12` | `.word       0x4BBF50F3                   # INVALID     $sp, $ra, 0x50F3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6824 | `data_gap_80024A0C` | `0x80026230` | `0x4BBF58F3` | `opcode_0x12` | `.word       0x4BBF58F3                   # INVALID     $sp, $ra, 0x58F3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6828 | `data_gap_80024A0C` | `0x80026238` | `0x48861800` | `opcode_0x12` | `mtc2        $a2, $3` |
| funcs_7.c:6830 | `data_gap_80024A0C` | `0x8002623C` | `0x48821900` | `opcode_0x12` | `.word       0x48821900                   # mtc2        $v0, $3 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6880 | `data_gap_80024A0C` | `0x80026284` | `0x0900049A` | `j` | `j           L_84001268` |
| funcs_7.c:6884 | `data_gap_80024A0C` | `0x8002628C` | `0xC9C50800` | `opcode_0x32` | `lwc2        $5, 0x800($t6)` |
| funcs_7.c:6886 | `data_gap_80024A0C` | `0x80026290` | `0xCB250180` | `opcode_0x32` | `lwc2        $5, 0x180($t9)` |
| funcs_7.c:6888 | `data_gap_80024A0C` | `0x80026294` | `0xCB250281` | `opcode_0x32` | `lwc2        $5, 0x281($t9)` |
| funcs_7.c:6890 | `data_gap_80024A0C` | `0x80026298` | `0xCB250382` | `opcode_0x32` | `lwc2        $5, 0x382($t9)` |
| funcs_7.c:6892 | `data_gap_80024A0C` | `0x8002629C` | `0xCB250483` | `opcode_0x32` | `lwc2        $5, 0x483($t9)` |
| funcs_7.c:6894 | `data_gap_80024A0C` | `0x800262A0` | `0xC9E60800` | `opcode_0x32` | `lwc2        $6, 0x800($t7)` |
| funcs_7.c:6896 | `data_gap_80024A0C` | `0x800262A4` | `0xCB460180` | `opcode_0x32` | `lwc2        $6, 0x180($k0)` |
| funcs_7.c:6898 | `data_gap_80024A0C` | `0x800262A8` | `0xCB460281` | `opcode_0x32` | `lwc2        $6, 0x281($k0)` |
| funcs_7.c:6900 | `data_gap_80024A0C` | `0x800262AC` | `0xCB460382` | `opcode_0x32` | `lwc2        $6, 0x382($k0)` |
| funcs_7.c:6902 | `data_gap_80024A0C` | `0x800262B0` | `0xCB460483` | `opcode_0x32` | `lwc2        $6, 0x483($k0)` |
| funcs_7.c:6904 | `data_gap_80024A0C` | `0x800262B4` | `0xC9A70800` | `opcode_0x32` | `lwc2        $7, 0x800($t5)` |
| funcs_7.c:6906 | `data_gap_80024A0C` | `0x800262B8` | `0xCB070180` | `opcode_0x32` | `lwc2        $7, 0x180($t8)` |
| funcs_7.c:6908 | `data_gap_80024A0C` | `0x800262BC` | `0xCB070281` | `opcode_0x32` | `lwc2        $7, 0x281($t8)` |
| funcs_7.c:6910 | `data_gap_80024A0C` | `0x800262C0` | `0xCB070382` | `opcode_0x32` | `lwc2        $7, 0x382($t8)` |
| funcs_7.c:6912 | `data_gap_80024A0C` | `0x800262C4` | `0xCB070483` | `opcode_0x32` | `lwc2        $7, 0x483($t8)` |
| funcs_7.c:6914 | `data_gap_80024A0C` | `0x800262C8` | `0x4B432805` | `opcode_0x12` | `.word       0x4B432805                   # INVALID     $k0, $v1, 0x2805 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6916 | `data_gap_80024A0C` | `0x800262CC` | `0x4B63304D` | `opcode_0x12` | `.word       0x4B63304D                   # INVALID     $k1, $v1, 0x304D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6918 | `data_gap_80024A0C` | `0x800262D0` | `0x4B40001D` | `opcode_0x12` | `.word       0x4B40001D                   # INVALID     $k0, $zero, 0x1D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6920 | `data_gap_80024A0C` | `0x800262D4` | `0x4B030104` | `opcode_0x12` | `.word       0x4B030104                   # INVALID     $t8, $v1, 0x104 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6922 | `data_gap_80024A0C` | `0x800262D8` | `0x4B03090D` | `opcode_0x12` | `.word       0x4B03090D                   # INVALID     $t8, $v1, 0x90D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6924 | `data_gap_80024A0C` | `0x800262DC` | `0x4B23384D` | `opcode_0x12` | `.word       0x4B23384D                   # INVALID     $t9, $v1, 0x384D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6926 | `data_gap_80024A0C` | `0x800262E0` | `0xE9A10800` | `opcode_0x3A` | `swc2        $1, 0x800($t5)` |
| funcs_7.c:6928 | `data_gap_80024A0C` | `0x800262E4` | `0xEB010180` | `opcode_0x3A` | `swc2        $1, 0x180($t8)` |
| funcs_7.c:6930 | `data_gap_80024A0C` | `0x800262E8` | `0xEB010281` | `opcode_0x3A` | `swc2        $1, 0x281($t8)` |
| funcs_7.c:6932 | `data_gap_80024A0C` | `0x800262EC` | `0xEB010382` | `opcode_0x3A` | `swc2        $1, 0x382($t8)` |
| funcs_7.c:6935 | `data_gap_80024A0C` | `0x800262F4` | `0xEB010483` | `opcode_0x3A` | `swc2        $1, 0x483($t8)` |
| funcs_7.c:6938 | `data_gap_80024A0C` | `0x800262F4` | `0xEB010483` | `opcode_0x3A` | `swc2        $1, 0x483($t8)` |
| funcs_7.c:6942 | `data_gap_80024A0C` | `0x800262FC` | `0xC805083A` | `opcode_0x32` | `lwc2        $5, 0x83A($zero)` |
| funcs_7.c:6972 | `data_gap_80024A0C` | `0x80026334` | `0xC9A6080E` | `opcode_0x32` | `lwc2        $6, 0x80E($t5)` |
| funcs_7.c:6974 | `data_gap_80024A0C` | `0x80026338` | `0xC868080E` | `opcode_0x32` | `lwc2        $8, 0x80E($v1)` |
| funcs_7.c:6976 | `data_gap_80024A0C` | `0x8002633C` | `0x4B0641F3` | `opcode_0x12` | `.word       0x4B0641F3                   # INVALID     $t8, $a2, 0x41F3 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6978 | `data_gap_80024A0C` | `0x80026340` | `0xC889080E` | `opcode_0x32` | `lwc2        $9, 0x80E($a0)` |
| funcs_7.c:6980 | `data_gap_80024A0C` | `0x80026344` | `0xC8AA080E` | `opcode_0x32` | `lwc2        $10, 0x80E($a1)` |
| funcs_7.c:6982 | `data_gap_80024A0C` | `0x80026348` | `0x4B053185` | `opcode_0x12` | `.word       0x4B053185                   # INVALID     $t8, $a1, 0x3185 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6984 | `data_gap_80024A0C` | `0x8002634C` | `0x4B05418D` | `opcode_0x12` | `.word       0x4B05418D                   # INVALID     $t8, $a1, 0x418D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6986 | `data_gap_80024A0C` | `0x80026350` | `0x4B05498D` | `opcode_0x12` | `.word       0x4B05498D                   # INVALID     $t8, $a1, 0x498D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:6998 | `data_gap_80024A0C` | `0x80026360` | `0x4B053985` | `opcode_0x12` | `.word       0x4B053985                   # INVALID     $t8, $a1, 0x3985 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7000 | `data_gap_80024A0C` | `0x80026364` | `0x4B05498D` | `opcode_0x12` | `.word       0x4B05498D                   # INVALID     $t8, $a1, 0x498D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7002 | `data_gap_80024A0C` | `0x80026368` | `0x4B05518D` | `opcode_0x12` | `.word       0x4B05518D                   # INVALID     $t8, $a1, 0x518D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7064 | `data_gap_80024A0C` | `0x800263B4` | `0x090007A3` | `j` | `j           L_84001E8C` |
| funcs_7.c:7116 | `data_gap_80024A0C` | `0x800263F0` | `0x090007B3` | `j` | `j           L_84001ECC` |
| funcs_7.c:7144 | `data_gap_80024A0C` | `0x80026414` | `0x0900049A` | `j` | `j           L_84001268` |
| funcs_7.c:7148 | `data_gap_80024A0C` | `0x8002641C` | `0xC846080E` | `opcode_0x32` | `lwc2        $6, 0x80E($v0)` |
| funcs_7.c:7152 | `data_gap_80024A0C` | `0x80026424` | `0xC868080E` | `opcode_0x32` | `lwc2        $8, 0x80E($v1)` |
| funcs_7.c:7154 | `data_gap_80024A0C` | `0x80026428` | `0xC889080E` | `opcode_0x32` | `lwc2        $9, 0x80E($a0)` |
| funcs_7.c:7168 | `data_gap_80024A0C` | `0x80026438` | `0x4B053185` | `opcode_0x12` | `.word       0x4B053185                   # INVALID     $t8, $a1, 0x3185 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7170 | `data_gap_80024A0C` | `0x8002643C` | `0x4B05418D` | `opcode_0x12` | `.word       0x4B05418D                   # INVALID     $t8, $a1, 0x418D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7172 | `data_gap_80024A0C` | `0x80026440` | `0x4B05498D` | `opcode_0x12` | `.word       0x4B05498D                   # INVALID     $t8, $a1, 0x498D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7191 | `data_gap_80024A0C` | `0x80026458` | `0x48033000` | `opcode_0x12` | `mfc2        $v1, $6` |
| funcs_7.c:7195 | `data_gap_80024A0C` | `0x80026458` | `0x48033000` | `opcode_0x12` | `mfc2        $v1, $6` |
| funcs_7.c:7253 | `data_gap_80024A0C` | `0x8002649C` | `0x090007E7` | `j` | `j           L_84001F9C` |
| funcs_7.c:7260 | `data_gap_80024A0C` | `0x800264A4` | `0x090007E7` | `j` | `j           L_84001F9C` |
| funcs_7.c:7334 | `data_gap_80024A0C` | `0x800264FC` | `0x090007E7` | `j` | `j           L_84001F9C` |
| funcs_7.c:7368 | `data_gap_80024A0C` | `0x80026524` | `0x090004B7` | `j` | `j           L_840012DC` |
| funcs_7.c:7422 | `data_gap_80024A0C` | `0x80026564` | `0x090004C8` | `j` | `j           L_84001320` |
| funcs_7.c:7458 | `data_gap_80024A0C` | `0x80026598` | `0x48870800` | `opcode_0x12` | `mtc2        $a3, $1` |
| funcs_7.c:7460 | `data_gap_80024A0C` | `0x8002659C` | `0x48820900` | `opcode_0x12` | `.word       0x48820900                   # mtc2        $v0, $1 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7474 | `data_gap_80024A0C` | `0x800265B0` | `0x48820100` | `opcode_0x12` | `.word       0x48820100                   # mtc2        $v0, $0 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7480 | `data_gap_80024A0C` | `0x800265BC` | `0x48820000` | `opcode_0x12` | `mtc2        $v0, $0` |
| funcs_7.c:7482 | `data_gap_80024A0C` | `0x800265C0` | `0x4A010007` | `opcode_0x12` | `.word       0x4A010007                   # INVALID     $s0, $at, 0x7 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7490 | `data_gap_80024A0C` | `0x800265D0` | `0x480B0000` | `opcode_0x12` | `mfc2        $t3, $0` |
| funcs_7.c:7494 | `data_gap_80024A0C` | `0x800265D0` | `0x480B0000` | `opcode_0x12` | `mfc2        $t3, $0` |
| funcs_7.c:7496 | `data_gap_80024A0C` | `0x800265D4` | `0x48020100` | `opcode_0x12` | `.word       0x48020100                   # mfc2        $v0, $0 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7514 | `data_gap_80024A0C` | `0x800265F0` | `0x090004E7` | `j` | `j           L_8400139C` |
| funcs_7.c:7539 | `data_gap_80024A0C` | `0x80026614` | `0xE8411002` | `opcode_0x3A` | `swc2        $1, 0x1002($v0)` |
| funcs_7.c:7563 | `data_gap_80024A0C` | `0x80026634` | `0xC8411002` | `opcode_0x32` | `lwc2        $1, 0x1002($v0)` |
| funcs_7.c:7565 | `data_gap_80024A0C` | `0x80026638` | `0x090004CF` | `j` | `j           L_8400133C` |
| funcs_7.c:7578 | `data_gap_80024A0C` | `0x80026650` | `0x090004E7` | `j` | `j           L_8400139C` |
| funcs_7.c:7583 | `data_gap_80024A0C` | `0x80026658` | `0x0900049A` | `j` | `j           L_84001268` |
| funcs_7.c:7589 | `data_gap_80024A0C` | `0x80026664` | `0x09000574` | `j` | `j           L_840015D0` |
| funcs_7.c:7593 | `data_gap_80024A0C` | `0x8002666C` | `0xCA21080B` | `opcode_0x32` | `lwc2        $1, 0x80B($s1)` |
| funcs_7.c:7595 | `data_gap_80024A0C` | `0x80026670` | `0x4A042115` | `opcode_0x12` | `.word       0x4A042115                   # INVALID     $s0, $a0, 0x2115 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7607 | `data_gap_80024A0C` | `0x80026680` | `0x4B014133` | `opcode_0x12` | `.word       0x4B014133                   # INVALID     $t8, $at, 0x4133 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7619 | `data_gap_80024A0C` | `0x80026690` | `0x4B1E4133` | `opcode_0x12` | `.word       0x4B1E4133                   # INVALID     $t8, $fp, 0x4133 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7621 | `data_gap_80024A0C` | `0x80026694` | `0x4B014933` | `opcode_0x12` | `.word       0x4B014933                   # INVALID     $t8, $at, 0x4933 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7633 | `data_gap_80024A0C` | `0x800266A4` | `0x4B014133` | `opcode_0x12` | `.word       0x4B014133                   # INVALID     $t8, $at, 0x4133 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7687 | `data_gap_80024A0C` | `0x800266F0` | `0x0900049A` | `j` | `j           L_84001268` |
| funcs_7.c:7708 | `data_gap_80024A0C` | `0x80026710` | `0x090004D6` | `j` | `j           L_84001358` |
| funcs_7.c:7722 | `data_gap_80024A0C` | `0x80026724` | `0x0900044B` | `j` | `j           L_8400112C` |
| funcs_7.c:7730 | `data_gap_80024A0C` | `0x80026734` | `0xE8C41005` | `opcode_0x3A` | `swc2        $4, 0x1005($a2)` |
| funcs_7.c:7758 | `data_gap_80024A0C` | `0x8002675C` | `0x0900048B` | `j` | `j           L_8400122C` |
| funcs_7.c:7784 | `data_gap_80024A0C` | `0x80026788` | `0xC84F0800` | `opcode_0x32` | `lwc2        $15, 0x800($v0)` |
| funcs_7.c:7786 | `data_gap_80024A0C` | `0x8002678C` | `0xC84F0905` | `opcode_0x32` | `lwc2        $15, 0x905($v0)` |
| funcs_7.c:7788 | `data_gap_80024A0C` | `0x80026790` | `0xC8500810` | `opcode_0x32` | `lwc2        $16, 0x810($v0)` |
| funcs_7.c:7790 | `data_gap_80024A0C` | `0x80026794` | `0xC8500915` | `opcode_0x32` | `lwc2        $16, 0x915($v0)` |
| funcs_7.c:7794 | `data_gap_80024A0C` | `0x8002679C` | `0x48821A00` | `opcode_0x12` | `.word       0x48821A00                   # mtc2        $v0, $3 # 00000200 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7796 | `data_gap_80024A0C` | `0x800267A0` | `0xC8C20810` | `opcode_0x32` | `lwc2        $2, 0x810($a2)` |
| funcs_7.c:7798 | `data_gap_80024A0C` | `0x800267A4` | `0xC8C30811` | `opcode_0x32` | `lwc2        $3, 0x811($a2)` |
| funcs_7.c:7800 | `data_gap_80024A0C` | `0x800267A8` | `0xCA4A081F` | `opcode_0x32` | `lwc2        $10, 0x81F($s2)` |
| funcs_7.c:7802 | `data_gap_80024A0C` | `0x800267AC` | `0xCA4E1008` | `opcode_0x32` | `lwc2        $14, 0x1008($s2)` |
| funcs_7.c:7804 | `data_gap_80024A0C` | `0x800267B0` | `0xC8CD1006` | `opcode_0x32` | `lwc2        $13, 0x1006($a2)` |
| funcs_7.c:7806 | `data_gap_80024A0C` | `0x800267B4` | `0xCA28107D` | `opcode_0x32` | `lwc2        $8, 0x107D($s1)` |
| funcs_7.c:7808 | `data_gap_80024A0C` | `0x800267B8` | `0x4BBF7385` | `opcode_0x12` | `.word       0x4BBF7385                   # INVALID     $sp, $ra, 0x7385 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7814 | `data_gap_80024A0C` | `0x800267C4` | `0x4B084133` | `opcode_0x12` | `.word       0x4B084133                   # INVALID     $t8, $t0, 0x4133 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7818 | `data_gap_80024A0C` | `0x800267C4` | `0x4B084133` | `opcode_0x12` | `.word       0x4B084133                   # INVALID     $t8, $t0, 0x4133 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7820 | `data_gap_80024A0C` | `0x800267C8` | `0x4B284233` | `opcode_0x12` | `.word       0x4B284233                   # INVALID     $t9, $t0, 0x4233 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7822 | `data_gap_80024A0C` | `0x800267CC` | `0x4B044A33` | `opcode_0x12` | `.word       0x4B044A33                   # INVALID     $t8, $a0, 0x4A33 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7825 | `data_gap_80024A0C` | `0x800267D0` | `0x4B034245` | `opcode_0x12` | `.word       0x4B034245                   # INVALID     $t8, $v1, 0x4245 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7827 | `data_gap_80024A0C` | `0x800267D4` | `0x4B02420F` | `opcode_0x12` | `.word       0x4B02420F                   # INVALID     $t8, $v0, 0x420F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7829 | `data_gap_80024A0C` | `0x800267D8` | `0x4B0A4A44` | `opcode_0x12` | `.word       0x4B0A4A44                   # INVALID     $t8, $t2, 0x4A44 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7831 | `data_gap_80024A0C` | `0x800267DC` | `0x4B0A420D` | `opcode_0x12` | `.word       0x4B0A420D                   # INVALID     $t8, $t2, 0x420D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7833 | `data_gap_80024A0C` | `0x800267E0` | `0x4B1E4A4E` | `opcode_0x12` | `.word       0x4B1E4A4E                   # INVALID     $t8, $fp, 0x4A4E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7835 | `data_gap_80024A0C` | `0x800267E4` | `0x4A0E4A46` | `opcode_0x12` | `.word       0x4A0E4A46                   # INVALID     $s0, $t6, 0x4A46 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7837 | `data_gap_80024A0C` | `0x800267E8` | `0x4A0E420F` | `opcode_0x12` | `.word       0x4A0E420F                   # INVALID     $s0, $t6, 0x420F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7839 | `data_gap_80024A0C` | `0x800267EC` | `0x4A104A44` | `opcode_0x12` | `.word       0x4A104A44                   # INVALID     $s0, $s0, 0x4A44 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7841 | `data_gap_80024A0C` | `0x800267F0` | `0x4A10424D` | `opcode_0x12` | `.word       0x4A10424D                   # INVALID     $s0, $s0, 0x424D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7843 | `data_gap_80024A0C` | `0x800267F4` | `0x4A0F4A4E` | `opcode_0x12` | `.word       0x4A0F4A4E                   # INVALID     $s0, $t7, 0x4A4E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7845 | `data_gap_80024A0C` | `0x800267F8` | `0x4A0F420F` | `opcode_0x12` | `.word       0x4A0F420F                   # INVALID     $s0, $t7, 0x420F # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7847 | `data_gap_80024A0C` | `0x800267FC` | `0x4A086815` | `opcode_0x12` | `.word       0x4A086815                   # INVALID     $s0, $t0, 0x6815 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7849 | `data_gap_80024A0C` | `0x80026800` | `0x4A086854` | `opcode_0x12` | `.word       0x4A086854                   # INVALID     $s0, $t0, 0x6854 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7851 | `data_gap_80024A0C` | `0x80026804` | `0xCA2B107E` | `opcode_0x32` | `lwc2        $11, 0x107E($s1)` |
| funcs_7.c:7857 | `data_gap_80024A0C` | `0x80026810` | `0x4B084133` | `opcode_0x12` | `.word       0x4B084133                   # INVALID     $t8, $t0, 0x4133 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7861 | `data_gap_80024A0C` | `0x80026810` | `0x4B084133` | `opcode_0x12` | `.word       0x4B084133                   # INVALID     $t8, $t0, 0x4133 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7863 | `data_gap_80024A0C` | `0x80026814` | `0x4B284233` | `opcode_0x12` | `.word       0x4B284233                   # INVALID     $t9, $t0, 0x4233 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7865 | `data_gap_80024A0C` | `0x80026818` | `0x4B044A33` | `opcode_0x12` | `.word       0x4B044A33                   # INVALID     $t8, $a0, 0x4A33 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7868 | `data_gap_80024A0C` | `0x8002681C` | `0x4B084270` | `opcode_0x12` | `.word       0x4B084270                   # INVALID     $t8, $t0, 0x4270 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7870 | `data_gap_80024A0C` | `0x80026820` | `0x4B084232` | `opcode_0x12` | `.word       0x4B084232                   # INVALID     $t8, $t0, 0x4232 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7872 | `data_gap_80024A0C` | `0x80026824` | `0x4B284A70` | `opcode_0x12` | `.word       0x4B284A70                   # INVALID     $t9, $t0, 0x4A70 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7874 | `data_gap_80024A0C` | `0x80026828` | `0x4B284A32` | `opcode_0x12` | `.word       0x4B284A32                   # INVALID     $t9, $t0, 0x4A32 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7876 | `data_gap_80024A0C` | `0x8002682C` | `0x4B434A44` | `opcode_0x12` | `.word       0x4B434A44                   # INVALID     $k0, $v1, 0x4A44 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7878 | `data_gap_80024A0C` | `0x80026830` | `0x4B43420D` | `opcode_0x12` | `.word       0x4B43420D                   # INVALID     $k0, $v1, 0x420D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7880 | `data_gap_80024A0C` | `0x80026834` | `0x4B1E4A4E` | `opcode_0x12` | `.word       0x4B1E4A4E                   # INVALID     $t8, $fp, 0x4A4E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7882 | `data_gap_80024A0C` | `0x80026838` | `0x4A096304` | `opcode_0x12` | `.word       0x4A096304                   # INVALID     $s0, $t1, 0x6304 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7884 | `data_gap_80024A0C` | `0x8002683C` | `0x4A095B0D` | `opcode_0x12` | `.word       0x4A095B0D                   # INVALID     $s0, $t1, 0x5B0D # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7886 | `data_gap_80024A0C` | `0x80026840` | `0x4A08630E` | `opcode_0x12` | `.word       0x4A08630E                   # INVALID     $s0, $t0, 0x630E # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7888 | `data_gap_80024A0C` | `0x80026844` | `0x4A085ACF` | `opcode_0x12` | `.word       0x4A085ACF                   # INVALID     $s0, $t0, 0x5ACF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7890 | `data_gap_80024A0C` | `0x80026848` | `0x480B5800` | `opcode_0x12` | `mfc2        $t3, $11` |
| funcs_7.c:7892 | `data_gap_80024A0C` | `0x8002684C` | `0x480C5900` | `opcode_0x12` | `.word       0x480C5900                   # mfc2        $t4, $11 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7932 | `data_gap_80024A0C` | `0x80026888` | `0x48826000` | `opcode_0x12` | `mtc2        $v0, $12` |
| funcs_7.c:7934 | `data_gap_80024A0C` | `0x8002688C` | `0x48836100` | `opcode_0x12` | `.word       0x48836100                   # mtc2        $v1, $12 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:7940 | `data_gap_80024A0C` | `0x80026898` | `0x48825800` | `opcode_0x12` | `mtc2        $v0, $11` |
| funcs_7.c:7942 | `data_gap_80024A0C` | `0x8002689C` | `0x48835900` | `opcode_0x12` | `.word       0x48835900                   # mtc2        $v1, $11 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8005 | `data_gap_80024A0C` | `0x800268F0` | `0x4B1E0120` | `opcode_0x12` | `.word       0x4B1E0120                   # INVALID     $t8, $fp, 0x120 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8007 | `data_gap_80024A0C` | `0x800268F4` | `0x4B1E0023` | `opcode_0x12` | `.word       0x4B1E0023                   # INVALID     $t8, $fp, 0x23 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8009 | `data_gap_80024A0C` | `0x800268F8` | `0x4B1E0863` | `opcode_0x12` | `.word       0x4B1E0863                   # INVALID     $t8, $fp, 0x863 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8015 | `data_gap_80024A0C` | `0x80026904` | `0x4B045133` | `opcode_0x12` | `.word       0x4B045133                   # INVALID     $t8, $a0, 0x5133 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8019 | `data_gap_80024A0C` | `0x80026904` | `0x4B045133` | `opcode_0x12` | `.word       0x4B045133                   # INVALID     $t8, $a0, 0x5133 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8021 | `data_gap_80024A0C` | `0x80026908` | `0x4B244133` | `opcode_0x12` | `.word       0x4B244133                   # INVALID     $t9, $a0, 0x4133 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8023 | `data_gap_80024A0C` | `0x8002690C` | `0x4B444933` | `opcode_0x12` | `.word       0x4B444933                   # INVALID     $k0, $a0, 0x4933 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8026 | `data_gap_80024A0C` | `0x80026910` | `0x4A046306` | `opcode_0x12` | `.word       0x4A046306                   # INVALID     $s0, $a0, 0x6306 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8028 | `data_gap_80024A0C` | `0x80026914` | `0x4A045ACF` | `opcode_0x12` | `.word       0x4A045ACF                   # INVALID     $s0, $a0, 0x5ACF # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8030 | `data_gap_80024A0C` | `0x80026918` | `0x48025800` | `opcode_0x12` | `mfc2        $v0, $11` |
| funcs_7.c:8032 | `data_gap_80024A0C` | `0x8002691C` | `0x48035900` | `opcode_0x12` | `.word       0x48035900                   # mfc2        $v1, $11 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8042 | `data_gap_80024A0C` | `0x80026930` | `0x48070000` | `opcode_0x12` | `mfc2        $a3, $0` |
| funcs_7.c:8044 | `data_gap_80024A0C` | `0x80026934` | `0x48080100` | `opcode_0x12` | `.word       0x48080100                   # mfc2        $t0, $0 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8046 | `data_gap_80024A0C` | `0x80026938` | `0x48090800` | `opcode_0x12` | `mfc2        $t1, $1` |
| funcs_7.c:8048 | `data_gap_80024A0C` | `0x8002693C` | `0x480A0900` | `opcode_0x12` | `.word       0x480A0900                   # mfc2        $t2, $1 # 00000100 <InstrIdType: CPU_COP2>` |
| funcs_7.c:8123 | `data_gap_80024A0C` | `0x800269A0` | `0x0900044B` | `j` | `j           L_8400112C` |
| funcs_8.c:8707 | `_Genld` | `0x80036A3C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_8.c:8728 | `_Genld` | `0x80036A54` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_8.c:8762 | `_Genld` | `0x80036A88` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_8.c:8783 | `_Genld` | `0x80036AA0` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_8.c:8817 | `_Genld` | `0x80036AD4` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_8.c:8838 | `_Genld` | `0x80036AEC` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_8.c:10279 | `ldiv_recomp` | `0x800371F4` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_8.c:10300 | `ldiv_recomp` | `0x8003720C` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_8.c:10962 | `__OSGlobalIntMask` | `0x80039110` | `0x003FFF01` | `special_0x01 $ra,$at,$ra` | `.word       0x003FFF01                   # INVALID     $at, $ra, -0xFF # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11127 | `__OSGlobalIntMask` | `0x8003924C` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:11129 | `__OSGlobalIntMask` | `0x80039250` | `0x0000020D` | `break $zero,$zero,$zero` | `break       0, 8` |
| funcs_8.c:11171 | `__OSGlobalIntMask` | `0x8003929C` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11173 | `__OSGlobalIntMask` | `0x800392A0` | `0x0000020D` | `break $zero,$zero,$zero` | `break       0, 8` |
| funcs_8.c:11175 | `__OSGlobalIntMask` | `0x800392A4` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11218 | `__OSGlobalIntMask` | `0x800392EC` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:11220 | `__OSGlobalIntMask` | `0x800392F0` | `0x00000271` | `special_0x31 $zero,$zero,$zero` | `tgeu        $zero, $zero, 9` |
| funcs_8.c:11222 | `__OSGlobalIntMask` | `0x800392F4` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11240 | `__OSGlobalIntMask` | `0x80039310` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11250 | `__OSGlobalIntMask` | `0x80039324` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11258 | `__OSGlobalIntMask` | `0x80039334` | `0x0000320E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000320E                   # INVALID     $zero, $zero, 0x320E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11262 | `__OSGlobalIntMask` | `0x8003933C` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11264 | `__OSGlobalIntMask` | `0x80039340` | `0x0000020D` | `break $zero,$zero,$zero` | `break       0, 8` |
| funcs_8.c:11266 | `__OSGlobalIntMask` | `0x80039344` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11302 | `__OSGlobalIntMask` | `0x80039384` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11306 | `__OSGlobalIntMask` | `0x8003938C` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11311 | `__OSGlobalIntMask` | `0x80039394` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11329 | `__OSGlobalIntMask` | `0x800393B0` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11351 | `__OSGlobalIntMask` | `0x800393DC` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11353 | `__OSGlobalIntMask` | `0x800393E0` | `0x0000020D` | `break $zero,$zero,$zero` | `break       0, 8` |
| funcs_8.c:11355 | `__OSGlobalIntMask` | `0x800393E4` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11395 | `__OSGlobalIntMask` | `0x8003942C` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11400 | `__OSGlobalIntMask` | `0x80039434` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11418 | `__OSGlobalIntMask` | `0x80039450` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11436 | `__OSGlobalIntMask` | `0x80039474` | `0x0000330F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000330F                   # sync # 00003300 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11441 | `__OSGlobalIntMask` | `0x80039474` | `0x0000330F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000330F                   # sync # 00003300 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11445 | `__OSGlobalIntMask` | `0x8003947C` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11447 | `__OSGlobalIntMask` | `0x80039480` | `0x0000020D` | `break $zero,$zero,$zero` | `break       0, 8` |
| funcs_8.c:11449 | `__OSGlobalIntMask` | `0x80039484` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11485 | `__OSGlobalIntMask` | `0x800394C4` | `0x0000324F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000324F                   # sync # 00003240 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11490 | `__OSGlobalIntMask` | `0x800394C4` | `0x0000324F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000324F                   # sync # 00003240 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11494 | `__OSGlobalIntMask` | `0x800394CC` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11499 | `__OSGlobalIntMask` | `0x800394D4` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11517 | `__OSGlobalIntMask` | `0x800394F0` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11544 | `__OSGlobalIntMask` | `0x8003951C` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11546 | `__OSGlobalIntMask` | `0x80039520` | `0x0000020D` | `break $zero,$zero,$zero` | `break       0, 8` |
| funcs_8.c:11548 | `__OSGlobalIntMask` | `0x80039524` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11593 | `__OSGlobalIntMask` | `0x8003956C` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11598 | `__OSGlobalIntMask` | `0x80039574` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11616 | `__OSGlobalIntMask` | `0x80039590` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11632 | `__OSGlobalIntMask` | `0x800395B0` | `0x08000000` | `j` | `j           L_80000000` |
| funcs_8.c:11634 | `__OSGlobalIntMask` | `0x800395B4` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11638 | `__OSGlobalIntMask` | `0x800395BC` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11643 | `__OSGlobalIntMask` | `0x800395C4` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11661 | `__OSGlobalIntMask` | `0x800395E0` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11677 | `__OSGlobalIntMask` | `0x80039600` | `0x09000000` | `j` | `j           L_84000000` |
| funcs_8.c:11679 | `__OSGlobalIntMask` | `0x80039604` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11683 | `__OSGlobalIntMask` | `0x8003960C` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11688 | `__OSGlobalIntMask` | `0x80039614` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11706 | `__OSGlobalIntMask` | `0x80039630` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11722 | `__OSGlobalIntMask` | `0x80039650` | `0x0A000000` | `j` | `j           L_88000000` |
| funcs_8.c:11728 | `__OSGlobalIntMask` | `0x8003965C` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11733 | `__OSGlobalIntMask` | `0x80039664` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11751 | `__OSGlobalIntMask` | `0x80039680` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11767 | `__OSGlobalIntMask` | `0x800396A0` | `0x0B000000` | `j` | `j           L_8C000000` |
| funcs_8.c:11773 | `__OSGlobalIntMask` | `0x800396AC` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11778 | `__OSGlobalIntMask` | `0x800396B4` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11796 | `__OSGlobalIntMask` | `0x800396D0` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11813 | `__OSGlobalIntMask` | `0x800396F4` | `0x0000334F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000334F                   # sync # 00003340 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11817 | `__OSGlobalIntMask` | `0x800396F4` | `0x0000334F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000334F                   # sync # 00003340 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11822 | `__OSGlobalIntMask` | `0x800396FC` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11827 | `__OSGlobalIntMask` | `0x80039704` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11845 | `__OSGlobalIntMask` | `0x80039720` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11862 | `__OSGlobalIntMask` | `0x80039744` | `0x0000324F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000324F                   # sync # 00003240 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11866 | `__OSGlobalIntMask` | `0x80039744` | `0x0000324F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000324F                   # sync # 00003240 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11871 | `__OSGlobalIntMask` | `0x8003974C` | `0x03E52239` | `special_0x39 $a0,$ra,$a1` | `.word       0x03E52239                   # INVALID     $ra, $a1, 0x2239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11876 | `__OSGlobalIntMask` | `0x80039754` | `0x00000C15` | `special_0x15 $at,$zero,$zero` | `.word       0x00000C15                   # INVALID     $zero, $zero, 0xC15 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11894 | `__OSGlobalIntMask` | `0x80039770` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11911 | `__OSGlobalIntMask` | `0x80039794` | `0x0000320E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000320E                   # INVALID     $zero, $zero, 0x320E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11915 | `__OSGlobalIntMask` | `0x80039794` | `0x0000320E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000320E                   # INVALID     $zero, $zero, 0x320E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11920 | `__OSGlobalIntMask` | `0x8003979C` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:11922 | `__OSGlobalIntMask` | `0x800397A0` | `0x00000271` | `special_0x31 $zero,$zero,$zero` | `tgeu        $zero, $zero, 9` |
| funcs_8.c:11924 | `__OSGlobalIntMask` | `0x800397A4` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11942 | `__OSGlobalIntMask` | `0x800397C0` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11952 | `__OSGlobalIntMask` | `0x800397D4` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11959 | `__OSGlobalIntMask` | `0x800397E4` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11963 | `__OSGlobalIntMask` | `0x800397E4` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11968 | `__OSGlobalIntMask` | `0x800397EC` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:11970 | `__OSGlobalIntMask` | `0x800397F0` | `0x00000270` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 9` |
| funcs_8.c:11972 | `__OSGlobalIntMask` | `0x800397F4` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:11990 | `__OSGlobalIntMask` | `0x80039810` | `0x005D0237` | `special_0x37 $zero,$v0,$sp` | `.word       0x005D0237                   # INVALID     $v0, $sp, 0x237 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12000 | `__OSGlobalIntMask` | `0x80039824` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12002 | `__OSGlobalIntMask` | `0x80039828` | `0x000D0269` | `special_0x29 $zero,$zero,$t5` | `.word       0x000D0269                   # INVALID     $zero, $t5, 0x269 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12015 | `__OSGlobalIntMask` | `0x8003983C` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12017 | `__OSGlobalIntMask` | `0x80039840` | `0x00000271` | `special_0x31 $zero,$zero,$zero` | `tgeu        $zero, $zero, 9` |
| funcs_8.c:12019 | `__OSGlobalIntMask` | `0x80039844` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12037 | `__OSGlobalIntMask` | `0x80039860` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12047 | `__OSGlobalIntMask` | `0x80039874` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12064 | `__OSGlobalIntMask` | `0x8003988C` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12066 | `__OSGlobalIntMask` | `0x80039890` | `0x00000270` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 9` |
| funcs_8.c:12068 | `__OSGlobalIntMask` | `0x80039894` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12086 | `__OSGlobalIntMask` | `0x800398B0` | `0x005D0237` | `special_0x37 $zero,$v0,$sp` | `.word       0x005D0237                   # INVALID     $v0, $sp, 0x237 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12096 | `__OSGlobalIntMask` | `0x800398C4` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12098 | `__OSGlobalIntMask` | `0x800398C8` | `0x000D0269` | `special_0x29 $zero,$zero,$t5` | `.word       0x000D0269                   # INVALID     $zero, $t5, 0x269 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12104 | `__OSGlobalIntMask` | `0x800398D4` | `0x0000330F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000330F                   # sync # 00003300 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12109 | `__OSGlobalIntMask` | `0x800398D4` | `0x0000330F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000330F                   # sync # 00003300 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12113 | `__OSGlobalIntMask` | `0x800398DC` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12115 | `__OSGlobalIntMask` | `0x800398E0` | `0x00000271` | `special_0x31 $zero,$zero,$zero` | `tgeu        $zero, $zero, 9` |
| funcs_8.c:12117 | `__OSGlobalIntMask` | `0x800398E4` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12135 | `__OSGlobalIntMask` | `0x80039900` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12145 | `__OSGlobalIntMask` | `0x80039914` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12153 | `__OSGlobalIntMask` | `0x80039924` | `0x0000324F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000324F                   # sync # 00003240 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12158 | `__OSGlobalIntMask` | `0x80039924` | `0x0000324F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000324F                   # sync # 00003240 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12162 | `__OSGlobalIntMask` | `0x8003992C` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12164 | `__OSGlobalIntMask` | `0x80039930` | `0x00000270` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 9` |
| funcs_8.c:12166 | `__OSGlobalIntMask` | `0x80039934` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12184 | `__OSGlobalIntMask` | `0x80039950` | `0x005D0237` | `special_0x37 $zero,$v0,$sp` | `.word       0x005D0237                   # INVALID     $v0, $sp, 0x237 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12194 | `__OSGlobalIntMask` | `0x80039964` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12196 | `__OSGlobalIntMask` | `0x80039968` | `0x000D0269` | `special_0x29 $zero,$zero,$t5` | `.word       0x000D0269                   # INVALID     $zero, $t5, 0x269 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12211 | `__OSGlobalIntMask` | `0x8003997C` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12213 | `__OSGlobalIntMask` | `0x80039980` | `0x00000271` | `special_0x31 $zero,$zero,$zero` | `tgeu        $zero, $zero, 9` |
| funcs_8.c:12215 | `__OSGlobalIntMask` | `0x80039984` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12233 | `__OSGlobalIntMask` | `0x800399A0` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12243 | `__OSGlobalIntMask` | `0x800399B4` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12260 | `__OSGlobalIntMask` | `0x800399CC` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12262 | `__OSGlobalIntMask` | `0x800399D0` | `0x00000270` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 9` |
| funcs_8.c:12264 | `__OSGlobalIntMask` | `0x800399D4` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12282 | `__OSGlobalIntMask` | `0x800399F0` | `0x005D0237` | `special_0x37 $zero,$v0,$sp` | `.word       0x005D0237                   # INVALID     $v0, $sp, 0x237 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12292 | `__OSGlobalIntMask` | `0x80039A04` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12294 | `__OSGlobalIntMask` | `0x80039A08` | `0x000D0269` | `special_0x29 $zero,$zero,$t5` | `.word       0x000D0269                   # INVALID     $zero, $t5, 0x269 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12300 | `__OSGlobalIntMask` | `0x80039A14` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12305 | `__OSGlobalIntMask` | `0x80039A14` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12309 | `__OSGlobalIntMask` | `0x80039A1C` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12311 | `__OSGlobalIntMask` | `0x80039A20` | `0x00000270` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 9` |
| funcs_8.c:12313 | `__OSGlobalIntMask` | `0x80039A24` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12331 | `__OSGlobalIntMask` | `0x80039A40` | `0x005D0237` | `special_0x37 $zero,$v0,$sp` | `.word       0x005D0237                   # INVALID     $v0, $sp, 0x237 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12341 | `__OSGlobalIntMask` | `0x80039A54` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12343 | `__OSGlobalIntMask` | `0x80039A58` | `0x000D0269` | `special_0x29 $zero,$zero,$t5` | `.word       0x000D0269                   # INVALID     $zero, $t5, 0x269 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12349 | `__OSGlobalIntMask` | `0x80039A64` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12354 | `__OSGlobalIntMask` | `0x80039A64` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12358 | `__OSGlobalIntMask` | `0x80039A6C` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12360 | `__OSGlobalIntMask` | `0x80039A70` | `0x00000270` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 9` |
| funcs_8.c:12362 | `__OSGlobalIntMask` | `0x80039A74` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12380 | `__OSGlobalIntMask` | `0x80039A90` | `0x005D0237` | `special_0x37 $zero,$v0,$sp` | `.word       0x005D0237                   # INVALID     $v0, $sp, 0x237 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12390 | `__OSGlobalIntMask` | `0x80039AA4` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12392 | `__OSGlobalIntMask` | `0x80039AA8` | `0x000D0269` | `special_0x29 $zero,$zero,$t5` | `.word       0x000D0269                   # INVALID     $zero, $t5, 0x269 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12407 | `__OSGlobalIntMask` | `0x80039ABC` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12409 | `__OSGlobalIntMask` | `0x80039AC0` | `0x00000270` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 9` |
| funcs_8.c:12411 | `__OSGlobalIntMask` | `0x80039AC4` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12429 | `__OSGlobalIntMask` | `0x80039AE0` | `0x005D0237` | `special_0x37 $zero,$v0,$sp` | `.word       0x005D0237                   # INVALID     $v0, $sp, 0x237 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12439 | `__OSGlobalIntMask` | `0x80039AF4` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12441 | `__OSGlobalIntMask` | `0x80039AF8` | `0x000D0269` | `special_0x29 $zero,$zero,$t5` | `.word       0x000D0269                   # INVALID     $zero, $t5, 0x269 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12456 | `__OSGlobalIntMask` | `0x80039B0C` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12458 | `__OSGlobalIntMask` | `0x80039B10` | `0x00000270` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 9` |
| funcs_8.c:12460 | `__OSGlobalIntMask` | `0x80039B14` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12478 | `__OSGlobalIntMask` | `0x80039B30` | `0x005D0237` | `special_0x37 $zero,$v0,$sp` | `.word       0x005D0237                   # INVALID     $v0, $sp, 0x237 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12488 | `__OSGlobalIntMask` | `0x80039B44` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12490 | `__OSGlobalIntMask` | `0x80039B48` | `0x000D0269` | `special_0x29 $zero,$zero,$t5` | `.word       0x000D0269                   # INVALID     $zero, $t5, 0x269 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12496 | `__OSGlobalIntMask` | `0x80039B54` | `0x0000334F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000334F                   # sync # 00003340 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12501 | `__OSGlobalIntMask` | `0x80039B54` | `0x0000334F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000334F                   # sync # 00003340 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12505 | `__OSGlobalIntMask` | `0x80039B5C` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12507 | `__OSGlobalIntMask` | `0x80039B60` | `0x00000270` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 9` |
| funcs_8.c:12509 | `__OSGlobalIntMask` | `0x80039B64` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12527 | `__OSGlobalIntMask` | `0x80039B80` | `0x005D0237` | `special_0x37 $zero,$v0,$sp` | `.word       0x005D0237                   # INVALID     $v0, $sp, 0x237 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12537 | `__OSGlobalIntMask` | `0x80039B94` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12539 | `__OSGlobalIntMask` | `0x80039B98` | `0x000D0269` | `special_0x29 $zero,$zero,$t5` | `.word       0x000D0269                   # INVALID     $zero, $t5, 0x269 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12545 | `__OSGlobalIntMask` | `0x80039BA4` | `0x0000324F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000324F                   # sync # 00003240 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12550 | `__OSGlobalIntMask` | `0x80039BA4` | `0x0000324F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000324F                   # sync # 00003240 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12554 | `__OSGlobalIntMask` | `0x80039BAC` | `0x04541E3A` | `regimm` | `.word       0x04541E3A                   # INVALID     $v0, $s4, 0x1E3A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12556 | `__OSGlobalIntMask` | `0x80039BB0` | `0x00000270` | `special_0x30 $zero,$zero,$zero` | `tge         $zero, $zero, 9` |
| funcs_8.c:12558 | `__OSGlobalIntMask` | `0x80039BB4` | `0x00170C69` | `special_0x29 $at,$zero,$s7` | `.word       0x00170C69                   # INVALID     $zero, $s7, 0xC69 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12576 | `__OSGlobalIntMask` | `0x80039BD0` | `0x005D0237` | `special_0x37 $zero,$v0,$sp` | `.word       0x005D0237                   # INVALID     $v0, $sp, 0x237 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12586 | `__OSGlobalIntMask` | `0x80039BE4` | `0x005F0239` | `special_0x39 $zero,$v0,$ra` | `.word       0x005F0239                   # INVALID     $v0, $ra, 0x239 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12588 | `__OSGlobalIntMask` | `0x80039BE8` | `0x000D0269` | `special_0x29 $zero,$zero,$t5` | `.word       0x000D0269                   # INVALID     $zero, $t5, 0x269 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12594 | `__OSGlobalIntMask` | `0x80039BF4` | `0x0000320E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000320E                   # INVALID     $zero, $zero, 0x320E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12599 | `__OSGlobalIntMask` | `0x80039BF4` | `0x0000320E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000320E                   # INVALID     $zero, $zero, 0x320E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12603 | `__OSGlobalIntMask` | `0x80039BFC` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12605 | `__OSGlobalIntMask` | `0x80039C00` | `0x0000020D` | `break $zero,$zero,$zero` | `break       0, 8` |
| funcs_8.c:12643 | `__OSGlobalIntMask` | `0x80039C44` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12648 | `__OSGlobalIntMask` | `0x80039C44` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12652 | `__OSGlobalIntMask` | `0x80039C4C` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12675 | `__OSGlobalIntMask` | `0x80039C70` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12702 | `__OSGlobalIntMask` | `0x80039C9C` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12704 | `__OSGlobalIntMask` | `0x80039CA0` | `0x0000020D` | `break $zero,$zero,$zero` | `break       0, 8` |
| funcs_8.c:12751 | `__OSGlobalIntMask` | `0x80039CEC` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12774 | `__OSGlobalIntMask` | `0x80039D10` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12792 | `__OSGlobalIntMask` | `0x80039D34` | `0x0000330F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000330F                   # sync # 00003300 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12796 | `__OSGlobalIntMask` | `0x80039D3C` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12798 | `__OSGlobalIntMask` | `0x80039D40` | `0x0000020D` | `break $zero,$zero,$zero` | `break       0, 8` |
| funcs_8.c:12836 | `__OSGlobalIntMask` | `0x80039D84` | `0x0000324F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000324F                   # sync # 00003240 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12840 | `__OSGlobalIntMask` | `0x80039D8C` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12863 | `__OSGlobalIntMask` | `0x80039DB0` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12885 | `__OSGlobalIntMask` | `0x80039DDC` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12887 | `__OSGlobalIntMask` | `0x80039DE0` | `0x0000020D` | `break $zero,$zero,$zero` | `break       0, 8` |
| funcs_8.c:12929 | `__OSGlobalIntMask` | `0x80039E2C` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12952 | `__OSGlobalIntMask` | `0x80039E50` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12970 | `__OSGlobalIntMask` | `0x80039E74` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:12974 | `__OSGlobalIntMask` | `0x80039E7C` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:12997 | `__OSGlobalIntMask` | `0x80039EA0` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:13015 | `__OSGlobalIntMask` | `0x80039EC4` | `0x0000324E` | `special_0x0E $a2,$zero,$zero` | `.word       0x0000324E                   # INVALID     $zero, $zero, 0x324E # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:13019 | `__OSGlobalIntMask` | `0x80039ECC` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13042 | `__OSGlobalIntMask` | `0x80039EF0` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:13064 | `__OSGlobalIntMask` | `0x80039F1C` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13087 | `__OSGlobalIntMask` | `0x80039F40` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:13109 | `__OSGlobalIntMask` | `0x80039F6C` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13132 | `__OSGlobalIntMask` | `0x80039F90` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:13150 | `__OSGlobalIntMask` | `0x80039FB4` | `0x0000334F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000334F                   # sync # 00003340 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:13154 | `__OSGlobalIntMask` | `0x80039FBC` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13177 | `__OSGlobalIntMask` | `0x80039FE0` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:13195 | `__OSGlobalIntMask` | `0x8003A004` | `0x0000324F` | `special_0x0F $a2,$zero,$zero` | `.word       0x0000324F                   # sync # 00003240 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:13199 | `__OSGlobalIntMask` | `0x8003A00C` | `0x04651E39` | `regimm` | `.word       0x04651E39                   # INVALID     $v1, $a1, 0x1E39 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13222 | `__OSGlobalIntMask` | `0x8003A030` | `0x002301FD` | `special_0x3D $zero,$at,$v1` | `.word       0x002301FD                   # INVALID     $at, $v1, 0x1FD # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:13294 | `__OSGlobalIntMask` | `0x8003A0C0` | `0x43444546` | `cop0` | `.word       0x43444546                   # INVALID     $k0, $a0, 0x4546 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13316 | `__OSGlobalIntMask` | `0x8003A0EC` | `0xEEA56814` | `opcode_0x3B` | `.word       0xEEA56814                   # INVALID     $s5, $a1, 0x6814 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13330 | `__OSGlobalIntMask` | `0x8003A100` | `0x400921FB` | `cop0` | `.word       0x400921FB                   # mfc0        $t1, Context # 000001FB <InstrIdType: CPU_COP0>` |
| funcs_8.c:13435 | `__OSGlobalIntMask` | `0x8003A170` | `0x7F810000` | `opcode_0x1F` | `.word       0x7F810000                   # INVALID     $gp, $at, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13467 | `__OSGlobalIntMask` | `0x8003A1B0` | `0x05550556` | `regimm` | `.word       0x05550556                   # INVALID     $t2, $s5, 0x556 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13469 | `__OSGlobalIntMask` | `0x8003A1B4` | `0x0559055A` | `regimm` | `.word       0x0559055A                   # INVALID     $t2, $t9, 0x55A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13471 | `__OSGlobalIntMask` | `0x8003A1B8` | `0x05650566` | `regimm` | `.word       0x05650566                   # INVALID     $t3, $a1, 0x566 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13473 | `__OSGlobalIntMask` | `0x8003A1BC` | `0x0569056A` | `regimm` | `tgeiu       $t3, 0x56A` |
| funcs_8.c:13475 | `__OSGlobalIntMask` | `0x8003A1C0` | `0x05950596` | `regimm` | `.word       0x05950596                   # INVALID     $t4, $s5, 0x596 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13477 | `__OSGlobalIntMask` | `0x8003A1C4` | `0x0599059A` | `regimm` | `.word       0x0599059A                   # INVALID     $t4, $t9, 0x59A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13479 | `__OSGlobalIntMask` | `0x8003A1C8` | `0x05A505A6` | `regimm` | `.word       0x05A505A6                   # INVALID     $t5, $a1, 0x5A6 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13481 | `__OSGlobalIntMask` | `0x8003A1CC` | `0x05A905AA` | `regimm` | `tgeiu       $t5, 0x5AA` |
| funcs_8.c:13483 | `__OSGlobalIntMask` | `0x8003A1D0` | `0x06550656` | `regimm` | `.word       0x06550656                   # INVALID     $s2, $s5, 0x656 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13485 | `__OSGlobalIntMask` | `0x8003A1D4` | `0x0659065A` | `regimm` | `.word       0x0659065A                   # INVALID     $s2, $t9, 0x65A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13487 | `__OSGlobalIntMask` | `0x8003A1D8` | `0x06650666` | `regimm` | `.word       0x06650666                   # INVALID     $s3, $a1, 0x666 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13489 | `__OSGlobalIntMask` | `0x8003A1DC` | `0x0669066A` | `regimm` | `tgeiu       $s3, 0x66A` |
| funcs_8.c:13491 | `__OSGlobalIntMask` | `0x8003A1E0` | `0x06950696` | `regimm` | `.word       0x06950696                   # INVALID     $s4, $s5, 0x696 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13493 | `__OSGlobalIntMask` | `0x8003A1E4` | `0x0699069A` | `regimm` | `.word       0x0699069A                   # INVALID     $s4, $t9, 0x69A # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13495 | `__OSGlobalIntMask` | `0x8003A1E8` | `0x06A506A6` | `regimm` | `.word       0x06A506A6                   # INVALID     $s5, $a1, 0x6A6 # 00000000 <InstrIdType: CPU_REGIMM>` |
| funcs_8.c:13497 | `__OSGlobalIntMask` | `0x8003A1EC` | `0x06A906AA` | `regimm` | `tgeiu       $s5, 0x6AA` |
| funcs_8.c:13499 | `__OSGlobalIntMask` | `0x8003A1F0` | `0x09550956` | `j` | `j           L_85542558` |
| funcs_8.c:13501 | `__OSGlobalIntMask` | `0x8003A1F4` | `0x0959095A` | `j` | `j           L_85642568` |
| funcs_8.c:13503 | `__OSGlobalIntMask` | `0x8003A1F8` | `0x09650966` | `j` | `j           L_85942598` |
| funcs_8.c:13505 | `__OSGlobalIntMask` | `0x8003A1FC` | `0x0969096A` | `j` | `j           L_85A425A8` |
| funcs_8.c:13507 | `__OSGlobalIntMask` | `0x8003A200` | `0x09950996` | `j` | `j           L_86542658` |
| funcs_8.c:13509 | `__OSGlobalIntMask` | `0x8003A204` | `0x0999099A` | `j` | `j           L_86642668` |
| funcs_8.c:13511 | `__OSGlobalIntMask` | `0x8003A208` | `0x09A509A6` | `j` | `j           L_86942698` |
| funcs_8.c:13513 | `__OSGlobalIntMask` | `0x8003A20C` | `0x09A909AA` | `j` | `j           L_86A426A8` |
| funcs_8.c:13515 | `__OSGlobalIntMask` | `0x8003A210` | `0x0A550A56` | `j` | `j           L_89542958` |
| funcs_8.c:13517 | `__OSGlobalIntMask` | `0x8003A214` | `0x0A590A5A` | `j` | `j           L_89642968` |
| funcs_8.c:13519 | `__OSGlobalIntMask` | `0x8003A218` | `0x0A650A66` | `j` | `j           L_89942998` |
| funcs_8.c:13521 | `__OSGlobalIntMask` | `0x8003A21C` | `0x0A690A6A` | `j` | `j           L_89A429A8` |
| funcs_8.c:13523 | `__OSGlobalIntMask` | `0x8003A220` | `0x0A950A96` | `j` | `j           L_8A542A58` |
| funcs_8.c:13525 | `__OSGlobalIntMask` | `0x8003A224` | `0x0A990A9A` | `j` | `j           L_8A642A68` |
| funcs_8.c:13527 | `__OSGlobalIntMask` | `0x8003A228` | `0x0AA50AA6` | `j` | `j           L_8A942A98` |
| funcs_8.c:13529 | `__OSGlobalIntMask` | `0x8003A22C` | `0x0AA90AAA` | `j` | `j           L_8AA42AA8` |
| funcs_8.c:13545 | `__OSGlobalIntMask` | `0x8003A24C` | `0xEEA56814` | `opcode_0x3B` | `.word       0xEEA56814                   # INVALID     $s5, $a1, 0x6814 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13559 | `__OSGlobalIntMask` | `0x8003A260` | `0x400921FB` | `cop0` | `.word       0x400921FB                   # mfc0        $t1, Context # 000001FB <InstrIdType: CPU_COP0>` |
| funcs_8.c:13588 | `__OSGlobalIntMask` | `0x8003A28C` | `0x00000001` | `special_0x01 $zero,$zero,$zero` | `.word       0x00000001                   # INVALID     $zero, $zero, 0x1 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:13713 | `__OSGlobalIntMask` | `0x8003A380` | `0x40240000` | `cop0` | `dmfc0       $a0, Index` |
| funcs_8.c:13717 | `__OSGlobalIntMask` | `0x8003A388` | `0x40590000` | `cop0` | `cfc0        $t9, Index` |
| funcs_8.c:13721 | `__OSGlobalIntMask` | `0x8003A390` | `0x40C38800` | `cop0` | `ctc0        $v1, LLAddr` |
| funcs_8.c:13725 | `__OSGlobalIntMask` | `0x8003A398` | `0x4197D784` | `cop0` | `.word       0x4197D784                   # INVALID     $t4, $s7, -0x287C # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13729 | `__OSGlobalIntMask` | `0x8003A3A0` | `0x4341C379` | `cop0` | `.word       0x4341C379                   # INVALID     $k0, $at, -0x3C87 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13733 | `__OSGlobalIntMask` | `0x8003A3A8` | `0x4693B8B5` | `cop1` | `.word       0x4693B8B5                   # INVALID     $s4, $s3, -0x474B # 00000000 <InstrIdType: CPU_COP1_FPUW>` |
| funcs_8.c:13737 | `__OSGlobalIntMask` | `0x8003A3B0` | `0x4D384F03` | `opcode_0x13` | `.word       0x4D384F03                   # INVALID     $t1, $t8, 0x4F03 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13739 | `__OSGlobalIntMask` | `0x8003A3B4` | `0xE93FF9F5` | `opcode_0x3A` | `swc2        $31, -0x60B($t1)` |
| funcs_8.c:13743 | `__OSGlobalIntMask` | `0x8003A3BC` | `0xF9301D32` | `opcode_0x3E` | `sdc2        $16, 0x1D32($t1)` |
| funcs_8.c:13748 | `__OSGlobalIntMask` | `0x8003A3BC` | `0xF9301D32` | `opcode_0x3E` | `sdc2        $16, 0x1D32($t1)` |
| funcs_8.c:13751 | `__OSGlobalIntMask` | `0x8003A3C0` | `0x75154FDD` | `opcode_0x1D` | `.word       0x75154FDD                   # INVALID     $t0, $s5, 0x4FDD # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13753 | `__OSGlobalIntMask` | `0x8003A3C4` | `0x7F73BF3C` | `opcode_0x1F` | `.word       0x7F73BF3C                   # INVALID     $k1, $s3, -0x40C4 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13755 | `__OSGlobalIntMask` | `0x8003A3C8` | `0x4E614E00` | `opcode_0x13` | `.word       0x4E614E00                   # INVALID     $s3, $at, 0x4E00 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13757 | `__OSGlobalIntMask` | `0x8003A3CC` | `0x496E6600` | `opcode_0x12` | `.word       0x496E6600                   # INVALID     $t3, $t6, 0x6600 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:13763 | `__OSGlobalIntMask` | `0x8003A3D8` | `0x4197D784` | `cop0` | `.word       0x4197D784                   # INVALID     $t4, $s7, -0x287C # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13791 | `__OSGlobalIntMask` | `0x8003A410` | `0x70617274` | `opcode_0x1C` | `.word       0x70617274                   # INVALID     $v1, $at, 0x7274 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13803 | `__OSGlobalIntMask` | `0x8003A41C` | `0x70617274` | `opcode_0x1C` | `.word       0x70617274                   # INVALID     $v1, $at, 0x7274 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13815 | `__OSGlobalIntMask` | `0x8003A428` | `0x42C80000` | `cop0` | `.word       0x42C80000                   # INVALID     $s6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13829 | `__OSGlobalIntMask` | `0x8003A444` | `0x42C80000` | `cop0` | `.word       0x42C80000                   # INVALID     $s6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13833 | `__OSGlobalIntMask` | `0x8003A44C` | `0x42C80000` | `cop0` | `.word       0x42C80000                   # INVALID     $s6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13837 | `__OSGlobalIntMask` | `0x8003A454` | `0x42C80000` | `cop0` | `.word       0x42C80000                   # INVALID     $s6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13839 | `__OSGlobalIntMask` | `0x8003A458` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13841 | `__OSGlobalIntMask` | `0x8003A45C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13843 | `__OSGlobalIntMask` | `0x8003A460` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13849 | `__OSGlobalIntMask` | `0x8003A46C` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13851 | `__OSGlobalIntMask` | `0x8003A470` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:13853 | `__OSGlobalIntMask` | `0x8003A474` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13855 | `__OSGlobalIntMask` | `0x8003A478` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13857 | `__OSGlobalIntMask` | `0x8003A47C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13859 | `__OSGlobalIntMask` | `0x8003A480` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13865 | `__OSGlobalIntMask` | `0x8003A48C` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13867 | `__OSGlobalIntMask` | `0x8003A490` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:13873 | `__OSGlobalIntMask` | `0x8003A49C` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:13877 | `__OSGlobalIntMask` | `0x8003A4A4` | `0x42E20000` | `cop0` | `.word       0x42E20000                   # INVALID     $s7, $v0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13879 | `__OSGlobalIntMask` | `0x8003A4A8` | `0x42E60000` | `cop0` | `.word       0x42E60000                   # INVALID     $s7, $a2, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13881 | `__OSGlobalIntMask` | `0x8003A4AC` | `0x43000000` | `cop0` | `.word       0x43000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13885 | `__OSGlobalIntMask` | `0x8003A4B4` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13887 | `__OSGlobalIntMask` | `0x8003A4B8` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:13893 | `__OSGlobalIntMask` | `0x8003A4C4` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:13907 | `__OSGlobalIntMask` | `0x8003A4E0` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13909 | `__OSGlobalIntMask` | `0x8003A4E4` | `0xC1200000` | `opcode_0x30` | `ll          $zero, 0x0($t1)` |
| funcs_8.c:13911 | `__OSGlobalIntMask` | `0x8003A4E8` | `0x42FE0000` | `cop0` | `.word       0x42FE0000                   # INVALID     $s7, $fp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13913 | `__OSGlobalIntMask` | `0x8003A4EC` | `0xC3000000` | `opcode_0x30` | `ll          $zero, 0x0($t8)` |
| funcs_8.c:13915 | `__OSGlobalIntMask` | `0x8003A4F0` | `0x42FE0000` | `cop0` | `.word       0x42FE0000                   # INVALID     $s7, $fp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13917 | `__OSGlobalIntMask` | `0x8003A4F4` | `0xC3000000` | `opcode_0x30` | `ll          $zero, 0x0($t8)` |
| funcs_8.c:13931 | `__OSGlobalIntMask` | `0x8003A510` | `0x477FFF00` | `cop1` | `.word       0x477FFF00                   # INVALID     $k1, $ra, -0x100 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:13933 | `__OSGlobalIntMask` | `0x8003A514` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:13937 | `__OSGlobalIntMask` | `0x8003A51C` | `0xC0800000` | `opcode_0x30` | `ll          $zero, 0x0($a0)` |
| funcs_8.c:13939 | `__OSGlobalIntMask` | `0x8003A520` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:13941 | `__OSGlobalIntMask` | `0x8003A524` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:13943 | `__OSGlobalIntMask` | `0x8003A528` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13945 | `__OSGlobalIntMask` | `0x8003A52C` | `0xC0400000` | `opcode_0x30` | `ll          $zero, 0x0($v0)` |
| funcs_8.c:13947 | `__OSGlobalIntMask` | `0x8003A530` | `0x42B40000` | `cop0` | `.word       0x42B40000                   # INVALID     $s5, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13949 | `__OSGlobalIntMask` | `0x8003A534` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:13963 | `__OSGlobalIntMask` | `0x8003A550` | `0x45580000` | `cop1` | `.word       0x45580000                   # INVALID     $t2, $t8, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:13965 | `__OSGlobalIntMask` | `0x8003A554` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13967 | `__OSGlobalIntMask` | `0x8003A558` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13969 | `__OSGlobalIntMask` | `0x8003A55C` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13977 | `__OSGlobalIntMask` | `0x8003A56C` | `0x41B00000` | `cop0` | `.word       0x41B00000                   # INVALID     $t5, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:13979 | `__OSGlobalIntMask` | `0x8003A570` | `0x42000000` | `cop0` | `.word       0x42000000                   # INVALID     $s0, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0_TLB>` |
| funcs_8.c:14003 | `__OSGlobalIntMask` | `0x8003A594` | `0x4D000000` | `opcode_0x13` | `.word       0x4D000000                   # INVALID     $t0, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14009 | `__OSGlobalIntMask` | `0x8003A5A0` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:14011 | `__OSGlobalIntMask` | `0x8003A5A4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:14013 | `__OSGlobalIntMask` | `0x8003A5A8` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14015 | `__OSGlobalIntMask` | `0x8003A5AC` | `0x41C00000` | `cop0` | `.word       0x41C00000                   # INVALID     $t6, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14017 | `__OSGlobalIntMask` | `0x8003A5B0` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_8.c:14019 | `__OSGlobalIntMask` | `0x8003A5B4` | `0xC1000000` | `opcode_0x30` | `ll          $zero, 0x0($t0)` |
| funcs_8.c:14021 | `__OSGlobalIntMask` | `0x8003A5B8` | `0xC1A00000` | `opcode_0x30` | `ll          $zero, 0x0($t5)` |
| funcs_8.c:14025 | `__OSGlobalIntMask` | `0x8003A5C0` | `0x41B00000` | `cop0` | `.word       0x41B00000                   # INVALID     $t5, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14033 | `__OSGlobalIntMask` | `0x8003A5D0` | `0x706C6179` | `opcode_0x1C` | `.word       0x706C6179                   # INVALID     $v1, $t4, 0x6179 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14037 | `__OSGlobalIntMask` | `0x8003A5D8` | `0x74617274` | `opcode_0x1D` | `.word       0x74617274                   # INVALID     $v1, $at, 0x7274 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14041 | `__OSGlobalIntMask` | `0x8003A5E0` | `0x74696F6E` | `opcode_0x1D` | `.word       0x74696F6E                   # INVALID     $v1, $t1, 0x6F6E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14046 | `__OSGlobalIntMask` | `0x8003A5E0` | `0x74696F6E` | `opcode_0x1D` | `.word       0x74696F6E                   # INVALID     $v1, $t1, 0x6F6E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14053 | `__OSGlobalIntMask` | `0x8003A5EC` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:14061 | `__OSGlobalIntMask` | `0x8003A5FC` | `0x41000000` | `cop0` | `bc0f        L_8003A600` |
| funcs_8.c:14066 | `__OSGlobalIntMask` | `0x8003A604` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:14086 | `__OSGlobalIntMask` | `0x8003A624` | `0x706B6700` | `opcode_0x1C` | `.word       0x706B6700                   # INVALID     $v1, $t3, 0x6700 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14090 | `__OSGlobalIntMask` | `0x8003A62C` | `0x706B6732` | `opcode_0x1C` | `.word       0x706B6732                   # INVALID     $v1, $t3, 0x6732 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14096 | `__OSGlobalIntMask` | `0x8003A638` | `0x705F6869` | `opcode_0x1C` | `.word       0x705F6869                   # INVALID     $v0, $ra, 0x6869 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14269 | `__OSGlobalIntMask` | `0x8003A790` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:14271 | `__OSGlobalIntMask` | `0x8003A794` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:14273 | `__OSGlobalIntMask` | `0x8003A798` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:14275 | `__OSGlobalIntMask` | `0x8003A79C` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:14277 | `__OSGlobalIntMask` | `0x8003A7A0` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:14279 | `__OSGlobalIntMask` | `0x8003A7A4` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:14281 | `__OSGlobalIntMask` | `0x8003A7A8` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:14283 | `__OSGlobalIntMask` | `0x8003A7AC` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:14291 | `__OSGlobalIntMask` | `0x8003A7BC` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14305 | `__OSGlobalIntMask` | `0x8003A7D8` | `0x43100000` | `cop0` | `.word       0x43100000                   # INVALID     $t8, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14327 | `__OSGlobalIntMask` | `0x8003A7F8` | `0x78000000` | `opcode_0x1E` | `.word       0x78000000                   # INVALID     $zero, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14353 | `__OSGlobalIntMask` | `0x8003A820` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14355 | `__OSGlobalIntMask` | `0x8003A824` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14357 | `__OSGlobalIntMask` | `0x8003A828` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14365 | `__OSGlobalIntMask` | `0x8003A838` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14367 | `__OSGlobalIntMask` | `0x8003A83C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14369 | `__OSGlobalIntMask` | `0x8003A840` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14371 | `__OSGlobalIntMask` | `0x8003A844` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14373 | `__OSGlobalIntMask` | `0x8003A848` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14375 | `__OSGlobalIntMask` | `0x8003A84C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14399 | `__OSGlobalIntMask` | `0x8003A87C` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14401 | `__OSGlobalIntMask` | `0x8003A880` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14403 | `__OSGlobalIntMask` | `0x8003A884` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14405 | `__OSGlobalIntMask` | `0x8003A888` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14407 | `__OSGlobalIntMask` | `0x8003A88C` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14409 | `__OSGlobalIntMask` | `0x8003A890` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14460 | `__OSGlobalIntMask` | `0x8003A8D8` | `0x406E0000` | `cop0` | `.word       0x406E0000                   # INVALID     $v1, $t6, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14464 | `__OSGlobalIntMask` | `0x8003A8E0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:14468 | `__OSGlobalIntMask` | `0x8003A8E8` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:14470 | `__OSGlobalIntMask` | `0x8003A8EC` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14472 | `__OSGlobalIntMask` | `0x8003A8F0` | `0x42F00000` | `cop0` | `.word       0x42F00000                   # INVALID     $s7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14476 | `__OSGlobalIntMask` | `0x8003A8F8` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14502 | `__OSGlobalIntMask` | `0x8003A92C` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_8.c:14504 | `__OSGlobalIntMask` | `0x8003A930` | `0x410C0000` | `cop0` | `.word       0x410C0000                   # INVALID     $t0, $t4, 0x0 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_8.c:14512 | `__OSGlobalIntMask` | `0x8003A940` | `0xC2B40000` | `opcode_0x30` | `ll          $s4, 0x0($s5)` |
| funcs_8.c:14514 | `__OSGlobalIntMask` | `0x8003A944` | `0x42B40000` | `cop0` | `.word       0x42B40000                   # INVALID     $s5, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14518 | `__OSGlobalIntMask` | `0x8003A94C` | `0xC2B40000` | `opcode_0x30` | `ll          $s4, 0x0($s5)` |
| funcs_8.c:14524 | `__OSGlobalIntMask` | `0x8003A958` | `0x40040000` | `cop0` | `mfc0        $a0, Index` |
| funcs_8.c:14528 | `__OSGlobalIntMask` | `0x8003A960` | `0xC2B40000` | `opcode_0x30` | `ll          $s4, 0x0($s5)` |
| funcs_8.c:14530 | `__OSGlobalIntMask` | `0x8003A964` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14532 | `__OSGlobalIntMask` | `0x8003A968` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14542 | `__OSGlobalIntMask` | `0x8003A97C` | `0x447A0000` | `cop1` | `.word       0x447A0000                   # INVALID     $v1, $k0, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:14544 | `__OSGlobalIntMask` | `0x8003A980` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14546 | `__OSGlobalIntMask` | `0x8003A984` | `0x42B40000` | `cop0` | `.word       0x42B40000                   # INVALID     $s5, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14556 | `__OSGlobalIntMask` | `0x8003A998` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14564 | `__OSGlobalIntMask` | `0x8003A9A8` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14570 | `__OSGlobalIntMask` | `0x8003A9B4` | `0x42A00000` | `cop0` | `.word       0x42A00000                   # INVALID     $s5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14572 | `__OSGlobalIntMask` | `0x8003A9B8` | `0xC2340000` | `opcode_0x30` | `ll          $s4, 0x0($s1)` |
| funcs_8.c:14574 | `__OSGlobalIntMask` | `0x8003A9BC` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14576 | `__OSGlobalIntMask` | `0x8003A9C0` | `0x42B40000` | `cop0` | `.word       0x42B40000                   # INVALID     $s5, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14578 | `__OSGlobalIntMask` | `0x8003A9C4` | `0x42B40000` | `cop0` | `.word       0x42B40000                   # INVALID     $s5, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14580 | `__OSGlobalIntMask` | `0x8003A9C8` | `0x42B40000` | `cop0` | `.word       0x42B40000                   # INVALID     $s5, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14582 | `__OSGlobalIntMask` | `0x8003A9CC` | `0x42B40000` | `cop0` | `.word       0x42B40000                   # INVALID     $s5, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14584 | `__OSGlobalIntMask` | `0x8003A9D0` | `0x42B40000` | `cop0` | `.word       0x42B40000                   # INVALID     $s5, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14586 | `__OSGlobalIntMask` | `0x8003A9D4` | `0x42B40000` | `cop0` | `.word       0x42B40000                   # INVALID     $s5, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14588 | `__OSGlobalIntMask` | `0x8003A9D8` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14590 | `__OSGlobalIntMask` | `0x8003A9DC` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:14596 | `__OSGlobalIntMask` | `0x8003A9E8` | `0x42820000` | `cop0` | `.word       0x42820000                   # INVALID     $s4, $v0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14600 | `__OSGlobalIntMask` | `0x8003A9F0` | `0x42BB8000` | `cop0` | `.word       0x42BB8000                   # INVALID     $s5, $k1, -0x8000 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14612 | `__OSGlobalIntMask` | `0x8003AA08` | `0x42A00000` | `cop0` | `.word       0x42A00000                   # INVALID     $s5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14614 | `__OSGlobalIntMask` | `0x8003AA0C` | `0xC2340000` | `opcode_0x30` | `ll          $s4, 0x0($s1)` |
| funcs_8.c:14616 | `__OSGlobalIntMask` | `0x8003AA10` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14622 | `__OSGlobalIntMask` | `0x8003AA1C` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14628 | `__OSGlobalIntMask` | `0x8003AA28` | `0x42A00000` | `cop0` | `.word       0x42A00000                   # INVALID     $s5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14630 | `__OSGlobalIntMask` | `0x8003AA2C` | `0xC2340000` | `opcode_0x30` | `ll          $s4, 0x0($s1)` |
| funcs_8.c:14632 | `__OSGlobalIntMask` | `0x8003AA30` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14638 | `__OSGlobalIntMask` | `0x8003AA3C` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14644 | `__OSGlobalIntMask` | `0x8003AA48` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:14654 | `__OSGlobalIntMask` | `0x8003AA5C` | `0x42A00000` | `cop0` | `.word       0x42A00000                   # INVALID     $s5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14656 | `__OSGlobalIntMask` | `0x8003AA60` | `0xC2340000` | `opcode_0x30` | `ll          $s4, 0x0($s1)` |
| funcs_8.c:14658 | `__OSGlobalIntMask` | `0x8003AA64` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14664 | `__OSGlobalIntMask` | `0x8003AA70` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14670 | `__OSGlobalIntMask` | `0x8003AA7C` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14672 | `__OSGlobalIntMask` | `0x8003AA80` | `0x40CCCCCD` | `cop0` | `.word       0x40CCCCCD                   # ctc0        $t4, Reserved25 # 000004CD <InstrIdType: CPU_COP0>` |
| funcs_8.c:14682 | `__OSGlobalIntMask` | `0x8003AA94` | `0x42A00000` | `cop0` | `.word       0x42A00000                   # INVALID     $s5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14684 | `__OSGlobalIntMask` | `0x8003AA98` | `0xC2340000` | `opcode_0x30` | `ll          $s4, 0x0($s1)` |
| funcs_8.c:14686 | `__OSGlobalIntMask` | `0x8003AA9C` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14692 | `__OSGlobalIntMask` | `0x8003AAA8` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14698 | `__OSGlobalIntMask` | `0x8003AAB4` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14706 | `__OSGlobalIntMask` | `0x8003AAC4` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14708 | `__OSGlobalIntMask` | `0x8003AAC8` | `0x40CCCCCD` | `cop0` | `.word       0x40CCCCCD                   # ctc0        $t4, Reserved25 # 000004CD <InstrIdType: CPU_COP0>` |
| funcs_8.c:14720 | `__OSGlobalIntMask` | `0x8003AAE0` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14722 | `__OSGlobalIntMask` | `0x8003AAE4` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:14724 | `__OSGlobalIntMask` | `0x8003AAE8` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14726 | `__OSGlobalIntMask` | `0x8003AAEC` | `0x40CCCCCD` | `cop0` | `.word       0x40CCCCCD                   # ctc0        $t4, Reserved25 # 000004CD <InstrIdType: CPU_COP0>` |
| funcs_8.c:14738 | `__OSGlobalIntMask` | `0x8003AB04` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_8.c:14742 | `__OSGlobalIntMask` | `0x8003AB0C` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14746 | `__OSGlobalIntMask` | `0x8003AB14` | `0x41AAAAAB` | `cop0` | `.word       0x41AAAAAB                   # INVALID     $t5, $t2, -0x5555 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14764 | `__OSGlobalIntMask` | `0x8003AB38` | `0x42A00000` | `cop0` | `.word       0x42A00000                   # INVALID     $s5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14766 | `__OSGlobalIntMask` | `0x8003AB3C` | `0xC2340000` | `opcode_0x30` | `ll          $s4, 0x0($s1)` |
| funcs_8.c:14768 | `__OSGlobalIntMask` | `0x8003AB40` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14774 | `__OSGlobalIntMask` | `0x8003AB4C` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14778 | `__OSGlobalIntMask` | `0x8003AB54` | `0xC0F00000` | `opcode_0x30` | `ll          $s0, 0x0($a3)` |
| funcs_8.c:14782 | `__OSGlobalIntMask` | `0x8003AB5C` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14786 | `__OSGlobalIntMask` | `0x8003AB64` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14788 | `__OSGlobalIntMask` | `0x8003AB68` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14794 | `__OSGlobalIntMask` | `0x8003AB74` | `0x42160000` | `cop0` | `.word       0x42160000                   # INVALID     $s0, $s6, 0x0 # 00000000 <InstrIdType: CPU_COP0_TLB>` |
| funcs_8.c:14796 | `__OSGlobalIntMask` | `0x8003AB78` | `0xC2160000` | `opcode_0x30` | `ll          $s6, 0x0($s0)` |
| funcs_8.c:14798 | `__OSGlobalIntMask` | `0x8003AB7C` | `0xC2C80000` | `opcode_0x30` | `ll          $t0, 0x0($s6)` |
| funcs_8.c:14800 | `__OSGlobalIntMask` | `0x8003AB80` | `0x43160000` | `cop0` | `.word       0x43160000                   # INVALID     $t8, $s6, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14802 | `__OSGlobalIntMask` | `0x8003AB84` | `0x42480000` | `cop0` | `.word       0x42480000                   # INVALID     $s2, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14804 | `__OSGlobalIntMask` | `0x8003AB88` | `0xC2480000` | `opcode_0x30` | `ll          $t0, 0x0($s2)` |
| funcs_8.c:14806 | `__OSGlobalIntMask` | `0x8003AB8C` | `0x42E10000` | `cop0` | `.word       0x42E10000                   # INVALID     $s7, $at, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14808 | `__OSGlobalIntMask` | `0x8003AB90` | `0xC1480000` | `opcode_0x30` | `ll          $t0, 0x0($t2)` |
| funcs_8.c:14810 | `__OSGlobalIntMask` | `0x8003AB94` | `0x42480000` | `cop0` | `.word       0x42480000                   # INVALID     $s2, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14814 | `__OSGlobalIntMask` | `0x8003AB9C` | `0x42A00000` | `cop0` | `.word       0x42A00000                   # INVALID     $s5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14816 | `__OSGlobalIntMask` | `0x8003ABA0` | `0xC2340000` | `opcode_0x30` | `ll          $s4, 0x0($s1)` |
| funcs_8.c:14818 | `__OSGlobalIntMask` | `0x8003ABA4` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14824 | `__OSGlobalIntMask` | `0x8003ABB0` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14832 | `__OSGlobalIntMask` | `0x8003ABC0` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14840 | `__OSGlobalIntMask` | `0x8003ABD0` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14852 | `__OSGlobalIntMask` | `0x8003ABE8` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14854 | `__OSGlobalIntMask` | `0x8003ABEC` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:14856 | `__OSGlobalIntMask` | `0x8003ABF0` | `0x45800000` | `cop1` | `.word       0x45800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:14858 | `__OSGlobalIntMask` | `0x8003ABF4` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:14860 | `__OSGlobalIntMask` | `0x8003ABF8` | `0x45800000` | `cop1` | `.word       0x45800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:14866 | `__OSGlobalIntMask` | `0x8003AC04` | `0x7677696E` | `opcode_0x1D` | `.word       0x7677696E                   # INVALID     $s3, $s7, 0x696E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14870 | `__OSGlobalIntMask` | `0x8003AC0C` | `0x7877696E` | `opcode_0x1E` | `.word       0x7877696E                   # INVALID     $v1, $s7, 0x696E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14874 | `__OSGlobalIntMask` | `0x8003AC14` | `0x7977696E` | `opcode_0x1E` | `.word       0x7977696E                   # INVALID     $t3, $s7, 0x696E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14878 | `__OSGlobalIntMask` | `0x8003AC1C` | `0x736E6F77` | `opcode_0x1C` | `.word       0x736E6F77                   # INVALID     $k1, $t6, 0x6F77 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14880 | `__OSGlobalIntMask` | `0x8003AC20` | `0x73706565` | `opcode_0x1C` | `.word       0x73706565                   # INVALID     $k1, $s0, 0x6565 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14888 | `__OSGlobalIntMask` | `0x8003AC30` | `0x7469655F` | `opcode_0x1D` | `.word       0x7469655F                   # INVALID     $v1, $t1, 0x655F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14892 | `__OSGlobalIntMask` | `0x8003AC38` | `0x72000000` | `opcode_0x1C` | `.word       0x72000000                   # INVALID     $s0, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14896 | `__OSGlobalIntMask` | `0x8003AC40` | `0x73636800` | `opcode_0x1C` | `.word       0x73636800                   # INVALID     $k1, $v1, 0x6800 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14898 | `__OSGlobalIntMask` | `0x8003AC44` | `0x74313600` | `opcode_0x1D` | `.word       0x74313600                   # INVALID     $at, $s1, 0x3600 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14900 | `__OSGlobalIntMask` | `0x8003AC48` | `0x776E645F` | `opcode_0x1D` | `.word       0x776E645F                   # INVALID     $k1, $t6, 0x645F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14934 | `__OSGlobalIntMask` | `0x8003AC8C` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:14936 | `__OSGlobalIntMask` | `0x8003AC90` | `0x40B40000` | `cop0` | `dmtc0       $s4, Index` |
| funcs_8.c:14938 | `__OSGlobalIntMask` | `0x8003AC94` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:14940 | `__OSGlobalIntMask` | `0x8003AC98` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_8.c:14944 | `__OSGlobalIntMask` | `0x8003ACA0` | `0x40700000` | `cop0` | `.word       0x40700000                   # INVALID     $v1, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14946 | `__OSGlobalIntMask` | `0x8003ACA4` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_8.c:14948 | `__OSGlobalIntMask` | `0x8003ACA8` | `0x40580000` | `cop0` | `cfc0        $t8, Index` |
| funcs_8.c:14950 | `__OSGlobalIntMask` | `0x8003ACAC` | `0x40280000` | `cop0` | `dmfc0       $t0, Index` |
| funcs_8.c:14952 | `__OSGlobalIntMask` | `0x8003ACB0` | `0x40640000` | `cop0` | `.word       0x40640000                   # INVALID     $v1, $a0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14954 | `__OSGlobalIntMask` | `0x8003ACB4` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_8.c:14956 | `__OSGlobalIntMask` | `0x8003ACB8` | `0x40B40000` | `cop0` | `dmtc0       $s4, Index` |
| funcs_8.c:14958 | `__OSGlobalIntMask` | `0x8003ACBC` | `0x40280000` | `cop0` | `dmfc0       $t0, Index` |
| funcs_8.c:14960 | `__OSGlobalIntMask` | `0x8003ACC0` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_8.c:14962 | `__OSGlobalIntMask` | `0x8003ACC4` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_8.c:14964 | `__OSGlobalIntMask` | `0x8003ACC8` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_8.c:14976 | `__OSGlobalIntMask` | `0x8003ACE0` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14984 | `__OSGlobalIntMask` | `0x8003ACF0` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14988 | `__OSGlobalIntMask` | `0x8003ACF8` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14990 | `__OSGlobalIntMask` | `0x8003ACFC` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14992 | `__OSGlobalIntMask` | `0x8003AD00` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14994 | `__OSGlobalIntMask` | `0x8003AD04` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:14996 | `__OSGlobalIntMask` | `0x8003AD08` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:14998 | `__OSGlobalIntMask` | `0x8003AD0C` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15000 | `__OSGlobalIntMask` | `0x8003AD10` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15002 | `__OSGlobalIntMask` | `0x8003AD14` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15040 | `__OSGlobalIntMask` | `0x8003AD60` | `0xE1AF00FF` | `opcode_0x38` | `sc          $t7, 0xFF($t5)` |
| funcs_8.c:15042 | `__OSGlobalIntMask` | `0x8003AD64` | `0x766F6963` | `opcode_0x1D` | `.word       0x766F6963                   # INVALID     $s3, $t7, 0x6963 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15048 | `__OSGlobalIntMask` | `0x8003AD70` | `0x410A4100` | `cop0` | `.word       0x410A4100                   # INVALID     $t0, $t2, 0x4100 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_8.c:15054 | `__OSGlobalIntMask` | `0x8003AD70` | `0x410A4100` | `cop0` | `.word       0x410A4100                   # INVALID     $t0, $t2, 0x4100 # 00000000 <InstrIdType: CPU_COP0_BC0>` |
| funcs_8.c:15059 | `__OSGlobalIntMask` | `0x8003AD78` | `0x49F42400` | `opcode_0x12` | `.word       0x49F42400                   # INVALID     $t7, $s4, 0x2400 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:15065 | `__OSGlobalIntMask` | `0x8003AD84` | `0x4D540000` | `opcode_0x13` | `.word       0x4D540000                   # INVALID     $t2, $s4, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15067 | `__OSGlobalIntMask` | `0x8003AD88` | `0x706C5F63` | `opcode_0x1C` | `.word       0x706C5F63                   # INVALID     $v1, $t4, 0x5F63 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15069 | `__OSGlobalIntMask` | `0x8003AD8C` | `0x72616674` | `opcode_0x1C` | `.word       0x72616674                   # INVALID     $s3, $at, 0x6674 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15071 | `__OSGlobalIntMask` | `0x8003AD90` | `0x732F6B6F` | `opcode_0x1C` | `.word       0x732F6B6F                   # INVALID     $t9, $t7, 0x6B6F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15079 | `__OSGlobalIntMask` | `0x8003ADA0` | `0x4F420000` | `opcode_0x13` | `.word       0x4F420000                   # INVALID     $k0, $v0, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15083 | `__OSGlobalIntMask` | `0x8003ADA8` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15085 | `__OSGlobalIntMask` | `0x8003ADAC` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15087 | `__OSGlobalIntMask` | `0x8003ADB0` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15089 | `__OSGlobalIntMask` | `0x8003ADB4` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15115 | `__OSGlobalIntMask` | `0x8003ADD8` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15117 | `__OSGlobalIntMask` | `0x8003ADDC` | `0xC1700000` | `opcode_0x30` | `ll          $s0, 0x0($t3)` |
| funcs_8.c:15119 | `__OSGlobalIntMask` | `0x8003ADE0` | `0xC0A00000` | `opcode_0x30` | `ll          $zero, 0x0($a1)` |
| funcs_8.c:15121 | `__OSGlobalIntMask` | `0x8003ADE4` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:15127 | `__OSGlobalIntMask` | `0x8003ADF0` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15137 | `__OSGlobalIntMask` | `0x8003AE04` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:15139 | `__OSGlobalIntMask` | `0x8003AE08` | `0xC1F00000` | `opcode_0x30` | `ll          $s0, 0x0($t7)` |
| funcs_8.c:15141 | `__OSGlobalIntMask` | `0x8003AE0C` | `0xC1F00000` | `opcode_0x30` | `ll          $s0, 0x0($t7)` |
| funcs_8.c:15143 | `__OSGlobalIntMask` | `0x8003AE10` | `0x736B7900` | `opcode_0x1C` | `.word       0x736B7900                   # INVALID     $k1, $t3, 0x7900 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15145 | `__OSGlobalIntMask` | `0x8003AE14` | `0x736B795F` | `opcode_0x1C` | `.word       0x736B795F                   # INVALID     $k1, $t3, 0x795F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15149 | `__OSGlobalIntMask` | `0x8003AE1C` | `0x7A6F6E00` | `opcode_0x1E` | `.word       0x7A6F6E00                   # INVALID     $s3, $t7, 0x6E00 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15165 | `__OSGlobalIntMask` | `0x8003AE3C` | `0x41C80000` | `cop0` | `.word       0x41C80000                   # INVALID     $t6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15167 | `__OSGlobalIntMask` | `0x8003AE40` | `0xC1C80000` | `opcode_0x30` | `ll          $t0, 0x0($t6)` |
| funcs_8.c:15175 | `__OSGlobalIntMask` | `0x8003AE50` | `0x795F2563` | `opcode_0x1E` | `.word       0x795F2563                   # INVALID     $t2, $ra, 0x2563 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15241 | `__OSGlobalIntMask` | `0x8003AEA4` | `0x756E0000` | `opcode_0x1D` | `.word       0x756E0000                   # INVALID     $t3, $t6, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15243 | `__OSGlobalIntMask` | `0x8003AEA8` | `0x7461745F` | `opcode_0x1D` | `.word       0x7461745F                   # INVALID     $v1, $at, 0x745F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15245 | `__OSGlobalIntMask` | `0x8003AEAC` | `0x73756E00` | `opcode_0x1C` | `.word       0x73756E00                   # INVALID     $k1, $s5, 0x6E00 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15247 | `__OSGlobalIntMask` | `0x8003AEB0` | `0x7461745F` | `opcode_0x1D` | `.word       0x7461745F                   # INVALID     $v1, $at, 0x745F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15249 | `__OSGlobalIntMask` | `0x8003AEB4` | `0x73756E32` | `opcode_0x1C` | `.word       0x73756E32                   # INVALID     $k1, $s5, 0x6E32 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15275 | `__OSGlobalIntMask` | `0x8003AEDC` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15279 | `__OSGlobalIntMask` | `0x8003AEE4` | `0x41900000` | `cop0` | `.word       0x41900000                   # INVALID     $t4, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15315 | `__OSGlobalIntMask` | `0x8003AF2C` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:15337 | `__OSGlobalIntMask` | `0x8003AF58` | `0x41900000` | `cop0` | `.word       0x41900000                   # INVALID     $t4, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15341 | `__OSGlobalIntMask` | `0x8003AF60` | `0x70685F74` | `opcode_0x1C` | `.word       0x70685F74                   # INVALID     $v1, $t0, 0x5F74 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15349 | `__OSGlobalIntMask` | `0x8003AF70` | `0x72000000` | `opcode_0x1C` | `.word       0x72000000                   # INVALID     $s0, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15353 | `__OSGlobalIntMask` | `0x8003AF78` | `0x7373696C` | `opcode_0x1C` | `.word       0x7373696C                   # INVALID     $k1, $s3, 0x696C # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15361 | `__OSGlobalIntMask` | `0x8003AF88` | `0x73657200` | `opcode_0x1C` | `.word       0x73657200                   # INVALID     $k1, $a1, 0x7200 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15363 | `__OSGlobalIntMask` | `0x8003AF8C` | `0x7265645F` | `opcode_0x1C` | `.word       0x7265645F                   # INVALID     $s3, $a1, 0x645F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15367 | `__OSGlobalIntMask` | `0x8003AF94` | `0x72000000` | `opcode_0x1C` | `.word       0x72000000                   # INVALID     $s0, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15371 | `__OSGlobalIntMask` | `0x8003AF9C` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15373 | `__OSGlobalIntMask` | `0x8003AFA0` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15399 | `__OSGlobalIntMask` | `0x8003AFD4` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15421 | `__OSGlobalIntMask` | `0x8003B000` | `0x42700000` | `cop0` | `.word       0x42700000                   # INVALID     $s3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15425 | `__OSGlobalIntMask` | `0x8003B008` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15429 | `__OSGlobalIntMask` | `0x8003B010` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:15435 | `__OSGlobalIntMask` | `0x8003B01C` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15439 | `__OSGlobalIntMask` | `0x8003B024` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:15445 | `__OSGlobalIntMask` | `0x8003B030` | `0x40600000` | `cop0` | `.word       0x40600000                   # INVALID     $v1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15449 | `__OSGlobalIntMask` | `0x8003B038` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:15461 | `__OSGlobalIntMask` | `0x8003B050` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_8.c:15463 | `__OSGlobalIntMask` | `0x8003B054` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_8.c:15467 | `__OSGlobalIntMask` | `0x8003B05C` | `0x477FFF00` | `cop1` | `.word       0x477FFF00                   # INVALID     $k1, $ra, -0x100 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:15469 | `__OSGlobalIntMask` | `0x8003B060` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15473 | `__OSGlobalIntMask` | `0x8003B068` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15499 | `__OSGlobalIntMask` | `0x8003B09C` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15505 | `__OSGlobalIntMask` | `0x8003B0A8` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_8.c:15513 | `__OSGlobalIntMask` | `0x8003B0B8` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15517 | `__OSGlobalIntMask` | `0x8003B0C0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:15519 | `__OSGlobalIntMask` | `0x8003B0C4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:15523 | `__OSGlobalIntMask` | `0x8003B0CC` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15525 | `__OSGlobalIntMask` | `0x8003B0D0` | `0x477FFF00` | `cop1` | `.word       0x477FFF00                   # INVALID     $k1, $ra, -0x100 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:15527 | `__OSGlobalIntMask` | `0x8003B0D4` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15569 | `__OSGlobalIntMask` | `0x8003B128` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15601 | `__OSGlobalIntMask` | `0x8003B168` | `0x77656170` | `opcode_0x1D` | `.word       0x77656170                   # INVALID     $k1, $a1, 0x6170 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15605 | `__OSGlobalIntMask` | `0x8003B170` | `0x70722F74` | `opcode_0x1C` | `.word       0x70722F74                   # INVALID     $v1, $s2, 0x2F74 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15611 | `__OSGlobalIntMask` | `0x8003B17C` | `0x77656170` | `opcode_0x1D` | `.word       0x77656170                   # INVALID     $k1, $a1, 0x6170 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15617 | `__OSGlobalIntMask` | `0x8003B188` | `0x74735F50` | `opcode_0x1D` | `.word       0x74735F50                   # INVALID     $v1, $s3, 0x5F50 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15619 | `__OSGlobalIntMask` | `0x8003B18C` | `0x414C0000` | `cop0` | `.word       0x414C0000                   # INVALID     $t2, $t4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15621 | `__OSGlobalIntMask` | `0x8003B190` | `0x77656170` | `opcode_0x1D` | `.word       0x77656170                   # INVALID     $k1, $a1, 0x6170 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15629 | `__OSGlobalIntMask` | `0x8003B1A0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:15633 | `__OSGlobalIntMask` | `0x8003B1A8` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_8.c:15635 | `__OSGlobalIntMask` | `0x8003B1AC` | `0x41A00000` | `cop0` | `.word       0x41A00000                   # INVALID     $t5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15639 | `__OSGlobalIntMask` | `0x8003B1B4` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_8.c:15641 | `__OSGlobalIntMask` | `0x8003B1B8` | `0x41A00000` | `cop0` | `.word       0x41A00000                   # INVALID     $t5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15645 | `__OSGlobalIntMask` | `0x8003B1C0` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_8.c:15647 | `__OSGlobalIntMask` | `0x8003B1C4` | `0x41C80000` | `cop0` | `.word       0x41C80000                   # INVALID     $t6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15653 | `__OSGlobalIntMask` | `0x8003B1D0` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:15657 | `__OSGlobalIntMask` | `0x8003B1D8` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15659 | `__OSGlobalIntMask` | `0x8003B1DC` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15661 | `__OSGlobalIntMask` | `0x8003B1E0` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15665 | `__OSGlobalIntMask` | `0x8003B1E8` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:15667 | `__OSGlobalIntMask` | `0x8003B1EC` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15671 | `__OSGlobalIntMask` | `0x8003B1F4` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:15673 | `__OSGlobalIntMask` | `0x8003B1F8` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15677 | `__OSGlobalIntMask` | `0x8003B200` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:15681 | `__OSGlobalIntMask` | `0x8003B208` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:15683 | `__OSGlobalIntMask` | `0x8003B20C` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15689 | `__OSGlobalIntMask` | `0x8003B218` | `0xC1700000` | `opcode_0x30` | `ll          $s0, 0x0($t3)` |
| funcs_8.c:15691 | `__OSGlobalIntMask` | `0x8003B21C` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15701 | `__OSGlobalIntMask` | `0x8003B230` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15707 | `__OSGlobalIntMask` | `0x8003B23C` | `0xC1700000` | `opcode_0x30` | `ll          $s0, 0x0($t3)` |
| funcs_8.c:15709 | `__OSGlobalIntMask` | `0x8003B240` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15723 | `__OSGlobalIntMask` | `0x8003B250` | `0x420C0000` | `cop0` | `.word       0x420C0000                   # INVALID     $s0, $t4, 0x0 # 00000000 <InstrIdType: CPU_COP0_TLB>` |
| funcs_8.c:15725 | `__OSGlobalIntMask` | `0x8003B254` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15727 | `__OSGlobalIntMask` | `0x8003B258` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15729 | `__OSGlobalIntMask` | `0x8003B25C` | `0x40F00000` | `cop0` | `.word       0x40F00000                   # INVALID     $a3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15731 | `__OSGlobalIntMask` | `0x8003B260` | `0x42700000` | `cop0` | `.word       0x42700000                   # INVALID     $s3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15757 | `__OSGlobalIntMask` | `0x8003B294` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15761 | `__OSGlobalIntMask` | `0x8003B29C` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:15765 | `__OSGlobalIntMask` | `0x8003B2A4` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:15769 | `__OSGlobalIntMask` | `0x8003B2AC` | `0x42700000` | `cop0` | `.word       0x42700000                   # INVALID     $s3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15779 | `__OSGlobalIntMask` | `0x8003B2C0` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_8.c:15781 | `__OSGlobalIntMask` | `0x8003B2C4` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_8.c:15799 | `__OSGlobalIntMask` | `0x8003B2E8` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15801 | `__OSGlobalIntMask` | `0x8003B2EC` | `0x477FFF00` | `cop1` | `.word       0x477FFF00                   # INVALID     $k1, $ra, -0x100 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:15803 | `__OSGlobalIntMask` | `0x8003B2F0` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15813 | `__OSGlobalIntMask` | `0x8003B304` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15815 | `__OSGlobalIntMask` | `0x8003B308` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_8.c:15817 | `__OSGlobalIntMask` | `0x8003B30C` | `0x41A00000` | `cop0` | `.word       0x41A00000                   # INVALID     $t5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15821 | `__OSGlobalIntMask` | `0x8003B314` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15823 | `__OSGlobalIntMask` | `0x8003B318` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15825 | `__OSGlobalIntMask` | `0x8003B31C` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15833 | `__OSGlobalIntMask` | `0x8003B32C` | `0x41A00000` | `cop0` | `.word       0x41A00000                   # INVALID     $t5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15839 | `__OSGlobalIntMask` | `0x8003B338` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15841 | `__OSGlobalIntMask` | `0x8003B33C` | `0x41000000` | `cop0` | `bc0f        L_8003B340` |
| funcs_8.c:15844 | `__OSGlobalIntMask` | `0x8003B340` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15848 | `__OSGlobalIntMask` | `0x8003B348` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15850 | `__OSGlobalIntMask` | `0x8003B34C` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15852 | `__OSGlobalIntMask` | `0x8003B350` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15856 | `__OSGlobalIntMask` | `0x8003B358` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15858 | `__OSGlobalIntMask` | `0x8003B35C` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_8.c:15864 | `__OSGlobalIntMask` | `0x8003B368` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15866 | `__OSGlobalIntMask` | `0x8003B36C` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15872 | `__OSGlobalIntMask` | `0x8003B378` | `0x4D475300` | `opcode_0x13` | `.word       0x4D475300                   # INVALID     $t2, $a3, 0x5300 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15878 | `__OSGlobalIntMask` | `0x8003B384` | `0x78000000` | `opcode_0x1E` | `.word       0x78000000                   # INVALID     $zero, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15909 | `__OSGlobalIntMask` | `0x8003B3A0` | `0x78000000` | `opcode_0x1E` | `.word       0x78000000                   # INVALID     $zero, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15913 | `__OSGlobalIntMask` | `0x8003B3A8` | `0x78705F49` | `opcode_0x1E` | `.word       0x78705F49                   # INVALID     $v1, $s0, 0x5F49 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15915 | `__OSGlobalIntMask` | `0x8003B3AC` | `0x4D475300` | `opcode_0x13` | `.word       0x4D475300                   # INVALID     $t2, $a3, 0x5300 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15921 | `__OSGlobalIntMask` | `0x8003B3B8` | `0x78000000` | `opcode_0x1E` | `.word       0x78000000                   # INVALID     $zero, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15925 | `__OSGlobalIntMask` | `0x8003B3C0` | `0x78325F49` | `opcode_0x1E` | `.word       0x78325F49                   # INVALID     $at, $s2, 0x5F49 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15927 | `__OSGlobalIntMask` | `0x8003B3C4` | `0x4D475300` | `opcode_0x13` | `.word       0x4D475300                   # INVALID     $t2, $a3, 0x5300 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15933 | `__OSGlobalIntMask` | `0x8003B3D0` | `0x78000000` | `opcode_0x1E` | `.word       0x78000000                   # INVALID     $zero, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15935 | `__OSGlobalIntMask` | `0x8003B3D4` | `0x736D6B65` | `opcode_0x1C` | `.word       0x736D6B65                   # INVALID     $k1, $t5, 0x6B65 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15937 | `__OSGlobalIntMask` | `0x8003B3D8` | `0x78705F49` | `opcode_0x1E` | `.word       0x78705F49                   # INVALID     $v1, $s0, 0x5F49 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15939 | `__OSGlobalIntMask` | `0x8003B3DC` | `0x4D475300` | `opcode_0x13` | `.word       0x4D475300                   # INVALID     $t2, $a3, 0x5300 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15941 | `__OSGlobalIntMask` | `0x8003B3E0` | `0x73657870` | `opcode_0x1C` | `.word       0x73657870                   # INVALID     $k1, $a1, 0x7870 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15945 | `__OSGlobalIntMask` | `0x8003B3E8` | `0x78000000` | `opcode_0x1E` | `.word       0x78000000                   # INVALID     $zero, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15947 | `__OSGlobalIntMask` | `0x8003B3EC` | `0x736D6B65` | `opcode_0x1C` | `.word       0x736D6B65                   # INVALID     $k1, $t5, 0x6B65 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15949 | `__OSGlobalIntMask` | `0x8003B3F0` | `0x78705F50` | `opcode_0x1E` | `.word       0x78705F50                   # INVALID     $v1, $s0, 0x5F50 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15951 | `__OSGlobalIntMask` | `0x8003B3F4` | `0x414C0000` | `cop0` | `.word       0x414C0000                   # INVALID     $t2, $t4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15961 | `__OSGlobalIntMask` | `0x8003B408` | `0x78000000` | `opcode_0x1E` | `.word       0x78000000                   # INVALID     $zero, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15963 | `__OSGlobalIntMask` | `0x8003B40C` | `0x736D6B65` | `opcode_0x1C` | `.word       0x736D6B65                   # INVALID     $k1, $t5, 0x6B65 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15965 | `__OSGlobalIntMask` | `0x8003B410` | `0x72000000` | `opcode_0x1C` | `.word       0x72000000                   # INVALID     $s0, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15967 | `__OSGlobalIntMask` | `0x8003B414` | `0x746D0000` | `opcode_0x1D` | `.word       0x746D0000                   # INVALID     $v1, $t5, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15985 | `__OSGlobalIntMask` | `0x8003B438` | `0x79656C6C` | `opcode_0x1E` | `.word       0x79656C6C                   # INVALID     $t3, $a1, 0x6C6C # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:15997 | `__OSGlobalIntMask` | `0x8003B450` | `0x41424344` | `cop0` | `.word       0x41424344                   # INVALID     $t2, $v0, 0x4344 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:15999 | `__OSGlobalIntMask` | `0x8003B454` | `0x45464748` | `cop1` | `.word       0x45464748                   # INVALID     $t2, $a2, 0x4748 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:16001 | `__OSGlobalIntMask` | `0x8003B458` | `0x494A4B4C` | `opcode_0x12` | `.word       0x494A4B4C                   # INVALID     $t2, $t2, 0x4B4C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:16003 | `__OSGlobalIntMask` | `0x8003B45C` | `0x4D4E4F50` | `opcode_0x13` | `.word       0x4D4E4F50                   # INVALID     $t2, $t6, 0x4F50 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16062 | `__OSGlobalIntMask` | `0x8003B494` | `0x41424344` | `cop0` | `.word       0x41424344                   # INVALID     $t2, $v0, 0x4344 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16064 | `__OSGlobalIntMask` | `0x8003B498` | `0x45464748` | `cop1` | `.word       0x45464748                   # INVALID     $t2, $a2, 0x4748 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:16066 | `__OSGlobalIntMask` | `0x8003B49C` | `0x494A4B4C` | `opcode_0x12` | `.word       0x494A4B4C                   # INVALID     $t2, $t2, 0x4B4C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:16068 | `__OSGlobalIntMask` | `0x8003B4A0` | `0x4D4E4F50` | `opcode_0x13` | `.word       0x4D4E4F50                   # INVALID     $t2, $t6, 0x4F50 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16128 | `__OSGlobalIntMask` | `0x8003B4DC` | `0x41424344` | `cop0` | `.word       0x41424344                   # INVALID     $t2, $v0, 0x4344 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16130 | `__OSGlobalIntMask` | `0x8003B4E0` | `0x45464748` | `cop1` | `.word       0x45464748                   # INVALID     $t2, $a2, 0x4748 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:16132 | `__OSGlobalIntMask` | `0x8003B4E4` | `0x494A4B4C` | `opcode_0x12` | `.word       0x494A4B4C                   # INVALID     $t2, $t2, 0x4B4C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:16134 | `__OSGlobalIntMask` | `0x8003B4E8` | `0x4D4E4F50` | `opcode_0x13` | `.word       0x4D4E4F50                   # INVALID     $t2, $t6, 0x4F50 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16186 | `__OSGlobalIntMask` | `0x8003B514` | `0x73746172` | `opcode_0x1C` | `.word       0x73746172                   # INVALID     $k1, $s4, 0x6172 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16188 | `__OSGlobalIntMask` | `0x8003B518` | `0x77617273` | `opcode_0x1D` | `.word       0x77617273                   # INVALID     $k1, $at, 0x7273 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16192 | `__OSGlobalIntMask` | `0x8003B520` | `0x41424344` | `cop0` | `.word       0x41424344                   # INVALID     $t2, $v0, 0x4344 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16194 | `__OSGlobalIntMask` | `0x8003B524` | `0x45464748` | `cop1` | `.word       0x45464748                   # INVALID     $t2, $a2, 0x4748 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:16196 | `__OSGlobalIntMask` | `0x8003B528` | `0x494A4B4C` | `opcode_0x12` | `.word       0x494A4B4C                   # INVALID     $t2, $t2, 0x4B4C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:16198 | `__OSGlobalIntMask` | `0x8003B52C` | `0x4D4E4F50` | `opcode_0x13` | `.word       0x4D4E4F50                   # INVALID     $t2, $t6, 0x4F50 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16244 | `__OSGlobalIntMask` | `0x8003B54C` | `0x73747576` | `opcode_0x1C` | `.word       0x73747576                   # INVALID     $k1, $s4, 0x7576 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16246 | `__OSGlobalIntMask` | `0x8003B550` | `0x7778797A` | `opcode_0x1D` | `.word       0x7778797A                   # INVALID     $k1, $t8, 0x797A # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16273 | `__OSGlobalIntMask` | `0x8003B574` | `0xE1E8E9EC` | `opcode_0x38` | `sc          $t0, -0x1614($t7)` |
| funcs_8.c:16275 | `__OSGlobalIntMask` | `0x8003B578` | `0xEDEEEFEB` | `opcode_0x3B` | `.word       0xEDEEEFEB                   # INVALID     $t7, $t6, -0x1015 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16277 | `__OSGlobalIntMask` | `0x8003B57C` | `0xEAF3F4FA` | `opcode_0x3A` | `swc2        $19, -0xB06($s7)` |
| funcs_8.c:16279 | `__OSGlobalIntMask` | `0x8003B580` | `0xFBA1BFC7` | `opcode_0x3E` | `sdc2        $1, -0x4039($sp)` |
| funcs_8.c:16285 | `__OSGlobalIntMask` | `0x8003B588` | `0x73756274` | `opcode_0x1C` | `.word       0x73756274                   # INVALID     $k1, $s5, 0x6274 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16291 | `__OSGlobalIntMask` | `0x8003B594` | `0x41424344` | `cop0` | `.word       0x41424344                   # INVALID     $t2, $v0, 0x4344 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16293 | `__OSGlobalIntMask` | `0x8003B598` | `0x45464748` | `cop1` | `.word       0x45464748                   # INVALID     $t2, $a2, 0x4748 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:16295 | `__OSGlobalIntMask` | `0x8003B59C` | `0x494A4B4C` | `opcode_0x12` | `.word       0x494A4B4C                   # INVALID     $t2, $t2, 0x4B4C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:16297 | `__OSGlobalIntMask` | `0x8003B5A0` | `0x4D4E4F50` | `opcode_0x13` | `.word       0x4D4E4F50                   # INVALID     $t2, $t6, 0x4F50 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16347 | `__OSGlobalIntMask` | `0x8003B5C8` | `0x73756274` | `opcode_0x1C` | `.word       0x73756274                   # INVALID     $k1, $s5, 0x6274 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16353 | `__OSGlobalIntMask` | `0x8003B5D4` | `0x73756274` | `opcode_0x1C` | `.word       0x73756274                   # INVALID     $k1, $s5, 0x6274 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16359 | `__OSGlobalIntMask` | `0x8003B5E0` | `0x41424344` | `cop0` | `.word       0x41424344                   # INVALID     $t2, $v0, 0x4344 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16361 | `__OSGlobalIntMask` | `0x8003B5E4` | `0x45464748` | `cop1` | `.word       0x45464748                   # INVALID     $t2, $a2, 0x4748 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:16363 | `__OSGlobalIntMask` | `0x8003B5E8` | `0x494A4B4C` | `opcode_0x12` | `.word       0x494A4B4C                   # INVALID     $t2, $t2, 0x4B4C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:16365 | `__OSGlobalIntMask` | `0x8003B5EC` | `0x4D4E4F50` | `opcode_0x13` | `.word       0x4D4E4F50                   # INVALID     $t2, $t6, 0x4F50 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16423 | `__OSGlobalIntMask` | `0x8003B624` | `0x41424344` | `cop0` | `.word       0x41424344                   # INVALID     $t2, $v0, 0x4344 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16425 | `__OSGlobalIntMask` | `0x8003B628` | `0x45464748` | `cop1` | `.word       0x45464748                   # INVALID     $t2, $a2, 0x4748 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:16427 | `__OSGlobalIntMask` | `0x8003B62C` | `0x494A4B4C` | `opcode_0x12` | `.word       0x494A4B4C                   # INVALID     $t2, $t2, 0x4B4C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:16429 | `__OSGlobalIntMask` | `0x8003B630` | `0x4D4E4F50` | `opcode_0x13` | `.word       0x4D4E4F50                   # INVALID     $t2, $t6, 0x4F50 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16485 | `__OSGlobalIntMask` | `0x8003B664` | `0x41424344` | `cop0` | `.word       0x41424344                   # INVALID     $t2, $v0, 0x4344 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16487 | `__OSGlobalIntMask` | `0x8003B668` | `0x45464748` | `cop1` | `.word       0x45464748                   # INVALID     $t2, $a2, 0x4748 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:16489 | `__OSGlobalIntMask` | `0x8003B66C` | `0x494A4B4C` | `opcode_0x12` | `.word       0x494A4B4C                   # INVALID     $t2, $t2, 0x4B4C # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:16491 | `__OSGlobalIntMask` | `0x8003B670` | `0x4D4E4F50` | `opcode_0x13` | `.word       0x4D4E4F50                   # INVALID     $t2, $t6, 0x4F50 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16537 | `__OSGlobalIntMask` | `0x8003B690` | `0x73747576` | `opcode_0x1C` | `.word       0x73747576                   # INVALID     $k1, $s4, 0x7576 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16539 | `__OSGlobalIntMask` | `0x8003B694` | `0x7778797A` | `opcode_0x1D` | `.word       0x7778797A                   # INVALID     $k1, $t8, 0x797A # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16557 | `__OSGlobalIntMask` | `0x8003B6B8` | `0xE9000000` | `opcode_0x3A` | `swc2        $0, 0x0($t0)` |
| funcs_8.c:16629 | `__OSGlobalIntMask` | `0x8003B724` | `0x732F2573` | `opcode_0x1C` | `.word       0x732F2573                   # INVALID     $t9, $t7, 0x2573 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16637 | `__OSGlobalIntMask` | `0x8003B734` | `0x732F2573` | `opcode_0x1C` | `.word       0x732F2573                   # INVALID     $t9, $t7, 0x2573 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16645 | `__OSGlobalIntMask` | `0x8003B744` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16647 | `__OSGlobalIntMask` | `0x8003B748` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16649 | `__OSGlobalIntMask` | `0x8003B74C` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16651 | `__OSGlobalIntMask` | `0x8003B750` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16653 | `__OSGlobalIntMask` | `0x8003B754` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16655 | `__OSGlobalIntMask` | `0x8003B758` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16657 | `__OSGlobalIntMask` | `0x8003B75C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16659 | `__OSGlobalIntMask` | `0x8003B760` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16667 | `__OSGlobalIntMask` | `0x8003B770` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16675 | `__OSGlobalIntMask` | `0x8003B780` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16677 | `__OSGlobalIntMask` | `0x8003B784` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16681 | `__OSGlobalIntMask` | `0x8003B78C` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16683 | `__OSGlobalIntMask` | `0x8003B790` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16687 | `__OSGlobalIntMask` | `0x8003B798` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16689 | `__OSGlobalIntMask` | `0x8003B79C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16693 | `__OSGlobalIntMask` | `0x8003B7A4` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16695 | `__OSGlobalIntMask` | `0x8003B7A8` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16699 | `__OSGlobalIntMask` | `0x8003B7B0` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16701 | `__OSGlobalIntMask` | `0x8003B7B4` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16705 | `__OSGlobalIntMask` | `0x8003B7BC` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:16707 | `__OSGlobalIntMask` | `0x8003B7C0` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16767 | `__OSGlobalIntMask` | `0x8003B820` | `0x01000005` | `special_0x05 $zero,$t0,$zero` | `.word       0x01000005                   # INVALID     $t0, $zero, 0x5 # 00000000 <InstrIdType: CPU_SPECIAL>` |
| funcs_8.c:16783 | `__OSGlobalIntMask` | `0x8003B838` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16787 | `__OSGlobalIntMask` | `0x8003B840` | `0x74696566` | `opcode_0x1D` | `.word       0x74696566                   # INVALID     $v1, $t1, 0x6566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16793 | `__OSGlobalIntMask` | `0x8003B84C` | `0x74696569` | `opcode_0x1D` | `.word       0x74696569                   # INVALID     $v1, $t1, 0x6569 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16799 | `__OSGlobalIntMask` | `0x8003B858` | `0x74696562` | `opcode_0x1D` | `.word       0x74696562                   # INVALID     $v1, $t1, 0x6562 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16803 | `__OSGlobalIntMask` | `0x8003B860` | `0x72000000` | `opcode_0x1C` | `.word       0x72000000                   # INVALID     $s0, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16805 | `__OSGlobalIntMask` | `0x8003B864` | `0x7469655F` | `opcode_0x1D` | `.word       0x7469655F                   # INVALID     $v1, $t1, 0x655F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16809 | `__OSGlobalIntMask` | `0x8003B86C` | `0x7469655F` | `opcode_0x1D` | `.word       0x7469655F                   # INVALID     $v1, $t1, 0x655F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16815 | `__OSGlobalIntMask` | `0x8003B878` | `0x74757272` | `opcode_0x1D` | `.word       0x74757272                   # INVALID     $v1, $s5, 0x7272 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16821 | `__OSGlobalIntMask` | `0x8003B884` | `0x74757272` | `opcode_0x1D` | `.word       0x74757272                   # INVALID     $v1, $s5, 0x7272 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16826 | `__OSGlobalIntMask` | `0x8003B88C` | `0x70726264` | `opcode_0x1C` | `.word       0x70726264                   # INVALID     $v1, $s2, 0x6264 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16828 | `__OSGlobalIntMask` | `0x8003B890` | `0x726F6964` | `opcode_0x1C` | `.word       0x726F6964                   # INVALID     $s3, $t7, 0x6964 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16834 | `__OSGlobalIntMask` | `0x8003B89C` | `0x74757272` | `opcode_0x1D` | `.word       0x74757272                   # INVALID     $v1, $s5, 0x7272 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16840 | `__OSGlobalIntMask` | `0x8003B8A8` | `0x74757272` | `opcode_0x1D` | `.word       0x74757272                   # INVALID     $v1, $s5, 0x7272 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16862 | `__OSGlobalIntMask` | `0x8003B8C8` | `0x72616461` | `opcode_0x1C` | `.word       0x72616461                   # INVALID     $s3, $at, 0x6461 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16864 | `__OSGlobalIntMask` | `0x8003B8CC` | `0x72646973` | `opcode_0x1C` | `.word       0x72646973                   # INVALID     $s3, $a0, 0x6973 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16868 | `__OSGlobalIntMask` | `0x8003B8D4` | `0x73687574` | `opcode_0x1C` | `.word       0x73687574                   # INVALID     $k1, $t0, 0x7574 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16870 | `__OSGlobalIntMask` | `0x8003B8D8` | `0x746C6500` | `opcode_0x1D` | `.word       0x746C6500                   # INVALID     $v1, $t4, 0x6500 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16872 | `__OSGlobalIntMask` | `0x8003B8DC` | `0x74616E6B` | `opcode_0x1D` | `.word       0x74616E6B                   # INVALID     $v1, $at, 0x6E6B # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16878 | `__OSGlobalIntMask` | `0x8003B8E8` | `0x7265625F` | `opcode_0x1C` | `.word       0x7265625F                   # INVALID     $s3, $a1, 0x625F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16880 | `__OSGlobalIntMask` | `0x8003B8EC` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16884 | `__OSGlobalIntMask` | `0x8003B8F4` | `0x725F7472` | `opcode_0x1C` | `.word       0x725F7472                   # INVALID     $s2, $ra, 0x7472 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16898 | `__OSGlobalIntMask` | `0x8003B910` | `0x77736B69` | `opcode_0x1D` | `.word       0x77736B69                   # INVALID     $k1, $s3, 0x6B69 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16904 | `__OSGlobalIntMask` | `0x8003B91C` | `0x725F636F` | `opcode_0x1C` | `.word       0x725F636F                   # INVALID     $s2, $ra, 0x636F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16910 | `__OSGlobalIntMask` | `0x8003B928` | `0x73686965` | `opcode_0x1C` | `.word       0x73686965                   # INVALID     $k1, $t0, 0x6965 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16916 | `__OSGlobalIntMask` | `0x8003B934` | `0x73686965` | `opcode_0x1C` | `.word       0x73686965                   # INVALID     $k1, $t0, 0x6965 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16922 | `__OSGlobalIntMask` | `0x8003B940` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16928 | `__OSGlobalIntMask` | `0x8003B94C` | `0x76667800` | `opcode_0x1D` | `.word       0x76667800                   # INVALID     $s3, $a2, 0x7800 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16930 | `__OSGlobalIntMask` | `0x8003B950` | `0x77726C64` | `opcode_0x1D` | `.word       0x77726C64                   # INVALID     $k1, $s2, 0x6C64 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16934 | `__OSGlobalIntMask` | `0x8003B958` | `0x74720000` | `opcode_0x1D` | `.word       0x74720000                   # INVALID     $v1, $s2, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16939 | `__OSGlobalIntMask` | `0x8003B958` | `0x74720000` | `opcode_0x1D` | `.word       0x74720000                   # INVALID     $v1, $s2, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16942 | `__OSGlobalIntMask` | `0x8003B95C` | `0x74726F6F` | `opcode_0x1D` | `.word       0x74726F6F                   # INVALID     $v1, $s2, 0x6F6F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16944 | `__OSGlobalIntMask` | `0x8003B960` | `0x70657200` | `opcode_0x1C` | `.word       0x70657200                   # INVALID     $v1, $a1, 0x7200 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16952 | `__OSGlobalIntMask` | `0x8003B970` | `0x725F7069` | `opcode_0x1C` | `.word       0x725F7069                   # INVALID     $s2, $ra, 0x7069 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16962 | `__OSGlobalIntMask` | `0x8003B984` | `0x725F7475` | `opcode_0x1C` | `.word       0x725F7475                   # INVALID     $s2, $ra, 0x7475 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16964 | `__OSGlobalIntMask` | `0x8003B988` | `0x72726574` | `opcode_0x1C` | `.word       0x72726574                   # INVALID     $s3, $s2, 0x6574 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16968 | `__OSGlobalIntMask` | `0x8003B990` | `0x74616C5F` | `opcode_0x1D` | `.word       0x74616C5F                   # INVALID     $v1, $at, 0x6C5F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16970 | `__OSGlobalIntMask` | `0x8003B994` | `0x74757272` | `opcode_0x1D` | `.word       0x74757272                   # INVALID     $v1, $s5, 0x7272 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16982 | `__OSGlobalIntMask` | `0x8003B9AC` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:16994 | `__OSGlobalIntMask` | `0x8003B9C4` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17002 | `__OSGlobalIntMask` | `0x8003B9D4` | `0x70777267` | `opcode_0x1C` | `.word       0x70777267                   # INVALID     $v1, $s7, 0x7267 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17006 | `__OSGlobalIntMask` | `0x8003B9DC` | `0x706F7765` | `opcode_0x1C` | `.word       0x706F7765                   # INVALID     $v1, $t7, 0x7765 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17008 | `__OSGlobalIntMask` | `0x8003B9E0` | `0x72757000` | `opcode_0x1C` | `.word       0x72757000                   # INVALID     $s3, $s5, 0x7000 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17010 | `__OSGlobalIntMask` | `0x8003B9E4` | `0x72617074` | `opcode_0x1C` | `.word       0x72617074                   # INVALID     $s3, $at, 0x7074 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17038 | `__OSGlobalIntMask` | `0x8003BA10` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17048 | `__OSGlobalIntMask` | `0x8003BA24` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17072 | `__OSGlobalIntMask` | `0x8003BA48` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17076 | `__OSGlobalIntMask` | `0x8003BA50` | `0x73745F77` | `opcode_0x1C` | `.word       0x73745F77                   # INVALID     $k1, $s4, 0x5F77 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17082 | `__OSGlobalIntMask` | `0x8003BA5C` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17086 | `__OSGlobalIntMask` | `0x8003BA64` | `0x73745F73` | `opcode_0x1C` | `.word       0x73745F73                   # INVALID     $k1, $s4, 0x5F73 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17088 | `__OSGlobalIntMask` | `0x8003BA68` | `0x74617274` | `opcode_0x1D` | `.word       0x74617274                   # INVALID     $v1, $at, 0x7274 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17094 | `__OSGlobalIntMask` | `0x8003BA74` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17098 | `__OSGlobalIntMask` | `0x8003BA7C` | `0x73745F73` | `opcode_0x1C` | `.word       0x73745F73                   # INVALID     $k1, $s4, 0x5F73 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17100 | `__OSGlobalIntMask` | `0x8003BA80` | `0x746F7000` | `opcode_0x1D` | `.word       0x746F7000                   # INVALID     $v1, $t7, 0x7000 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17118 | `__OSGlobalIntMask` | `0x8003BA98` | `0x7265625F` | `opcode_0x1C` | `.word       0x7265625F                   # INVALID     $s3, $a1, 0x625F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17124 | `__OSGlobalIntMask` | `0x8003BA98` | `0x7265625F` | `opcode_0x1C` | `.word       0x7265625F                   # INVALID     $s3, $a1, 0x625F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17127 | `__OSGlobalIntMask` | `0x8003BA9C` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17131 | `__OSGlobalIntMask` | `0x8003BAA4` | `0x70745F77` | `opcode_0x1C` | `.word       0x70745F77                   # INVALID     $v1, $s4, 0x5F77 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17135 | `__OSGlobalIntMask` | `0x8003BAAC` | `0x7265625F` | `opcode_0x1C` | `.word       0x7265625F                   # INVALID     $s3, $a1, 0x625F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17137 | `__OSGlobalIntMask` | `0x8003BAB0` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17141 | `__OSGlobalIntMask` | `0x8003BAB8` | `0x70745F73` | `opcode_0x1C` | `.word       0x70745F73                   # INVALID     $v1, $s4, 0x5F73 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17143 | `__OSGlobalIntMask` | `0x8003BABC` | `0x74617274` | `opcode_0x1D` | `.word       0x74617274                   # INVALID     $v1, $at, 0x7274 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17147 | `__OSGlobalIntMask` | `0x8003BAC4` | `0x7265625F` | `opcode_0x1C` | `.word       0x7265625F                   # INVALID     $s3, $a1, 0x625F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17149 | `__OSGlobalIntMask` | `0x8003BAC8` | `0x73747566` | `opcode_0x1C` | `.word       0x73747566                   # INVALID     $k1, $s4, 0x7566 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17153 | `__OSGlobalIntMask` | `0x8003BAD0` | `0x70745F73` | `opcode_0x1C` | `.word       0x70745F73                   # INVALID     $v1, $s4, 0x5F73 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17155 | `__OSGlobalIntMask` | `0x8003BAD4` | `0x746F7000` | `opcode_0x1D` | `.word       0x746F7000                   # INVALID     $v1, $t7, 0x7000 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17159 | `__OSGlobalIntMask` | `0x8003BADC` | `0x72726574` | `opcode_0x1C` | `.word       0x72726574                   # INVALID     $s3, $s2, 0x6574 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17165 | `__OSGlobalIntMask` | `0x8003BAE8` | `0x72726574` | `opcode_0x1C` | `.word       0x72726574                   # INVALID     $s3, $s2, 0x6574 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17171 | `__OSGlobalIntMask` | `0x8003BAF4` | `0x74757272` | `opcode_0x1D` | `.word       0x74757272                   # INVALID     $v1, $s5, 0x7272 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17175 | `__OSGlobalIntMask` | `0x8003BAFC` | `0x74726169` | `opcode_0x1D` | `.word       0x74726169                   # INVALID     $v1, $s2, 0x6169 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17179 | `__OSGlobalIntMask` | `0x8003BB04` | `0x74726169` | `opcode_0x1D` | `.word       0x74726169                   # INVALID     $v1, $s2, 0x6169 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17185 | `__OSGlobalIntMask` | `0x8003BB10` | `0x725F7472` | `opcode_0x1C` | `.word       0x725F7472                   # INVALID     $s2, $ra, 0x7472 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17189 | `__OSGlobalIntMask` | `0x8003BB18` | `0x725F7472` | `opcode_0x1C` | `.word       0x725F7472                   # INVALID     $s2, $ra, 0x7472 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17201 | `__OSGlobalIntMask` | `0x8003BB24` | `0x776D7877` | `opcode_0x1D` | `.word       0x776D7877                   # INVALID     $k1, $t5, 0x7877 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17205 | `__OSGlobalIntMask` | `0x8003BB2C` | `0x776D7977` | `opcode_0x1D` | `.word       0x776D7977                   # INVALID     $k1, $t5, 0x7977 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17209 | `__OSGlobalIntMask` | `0x8003BB34` | `0x776D6177` | `opcode_0x1D` | `.word       0x776D6177                   # INVALID     $k1, $t5, 0x6177 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17213 | `__OSGlobalIntMask` | `0x8003BB3C` | `0x776D7677` | `opcode_0x1D` | `.word       0x776D7677                   # INVALID     $k1, $t5, 0x7677 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17217 | `__OSGlobalIntMask` | `0x8003BB44` | `0x776D7370` | `opcode_0x1D` | `.word       0x776D7370                   # INVALID     $k1, $t5, 0x7370 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17221 | `__OSGlobalIntMask` | `0x8003BB4C` | `0x776D6661` | `opcode_0x1D` | `.word       0x776D6661                   # INVALID     $k1, $t5, 0x6661 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17225 | `__OSGlobalIntMask` | `0x8003BB54` | `0x74696500` | `opcode_0x1D` | `.word       0x74696500                   # INVALID     $v1, $t1, 0x6500 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17227 | `__OSGlobalIntMask` | `0x8003BB58` | `0x74313600` | `opcode_0x1D` | `.word       0x74313600                   # INVALID     $at, $s1, 0x3600 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17229 | `__OSGlobalIntMask` | `0x8003BB5C` | `0x706C5F63` | `opcode_0x1C` | `.word       0x706C5F63                   # INVALID     $v1, $t4, 0x5F63 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17231 | `__OSGlobalIntMask` | `0x8003BB60` | `0x72616674` | `opcode_0x1C` | `.word       0x72616674                   # INVALID     $s3, $at, 0x6674 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17233 | `__OSGlobalIntMask` | `0x8003BB64` | `0x732F2573` | `opcode_0x1C` | `.word       0x732F2573                   # INVALID     $t9, $t7, 0x2573 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17259 | `__OSGlobalIntMask` | `0x8003BB8C` | `0x705F616E` | `opcode_0x1C` | `.word       0x705F616E                   # INVALID     $v0, $ra, 0x616E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17265 | `__OSGlobalIntMask` | `0x8003BB98` | `0x73745F72` | `opcode_0x1C` | `.word       0x73745F72                   # INVALID     $k1, $s4, 0x5F72 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17267 | `__OSGlobalIntMask` | `0x8003BB9C` | `0x756E0000` | `opcode_0x1D` | `.word       0x756E0000                   # INVALID     $t3, $t6, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17271 | `__OSGlobalIntMask` | `0x8003BBA4` | `0x705F616E` | `opcode_0x1C` | `.word       0x705F616E                   # INVALID     $v0, $ra, 0x616E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17275 | `__OSGlobalIntMask` | `0x8003BBAC` | `0x74000000` | `opcode_0x1D` | `.word       0x74000000                   # INVALID     $zero, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17277 | `__OSGlobalIntMask` | `0x8003BBB0` | `0x73745F73` | `opcode_0x1C` | `.word       0x73745F73                   # INVALID     $k1, $s4, 0x5F73 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17283 | `__OSGlobalIntMask` | `0x8003BBBC` | `0x705F616E` | `opcode_0x1C` | `.word       0x705F616E                   # INVALID     $v0, $ra, 0x616E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17293 | `__OSGlobalIntMask` | `0x8003BBD0` | `0x70696C6F` | `opcode_0x1C` | `.word       0x70696C6F                   # INVALID     $v1, $t1, 0x6C6F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17295 | `__OSGlobalIntMask` | `0x8003BBD4` | `0x745F616E` | `opcode_0x1D` | `.word       0x745F616E                   # INVALID     $v0, $ra, 0x616E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17299 | `__OSGlobalIntMask` | `0x8003BBDC` | `0x72705F72` | `opcode_0x1C` | `.word       0x72705F72                   # INVALID     $s3, $s0, 0x5F72 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17301 | `__OSGlobalIntMask` | `0x8003BBE0` | `0x756E0000` | `opcode_0x1D` | `.word       0x756E0000                   # INVALID     $t3, $t6, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17305 | `__OSGlobalIntMask` | `0x8003BBE8` | `0x70696C6F` | `opcode_0x1C` | `.word       0x70696C6F                   # INVALID     $v1, $t1, 0x6C6F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17307 | `__OSGlobalIntMask` | `0x8003BBEC` | `0x745F616E` | `opcode_0x1D` | `.word       0x745F616E                   # INVALID     $v0, $ra, 0x616E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17315 | `__OSGlobalIntMask` | `0x8003BBFC` | `0x765F616E` | `opcode_0x1D` | `.word       0x765F616E                   # INVALID     $s2, $ra, 0x616E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17323 | `__OSGlobalIntMask` | `0x8003BC0C` | `0x72756E00` | `opcode_0x1C` | `.word       0x72756E00                   # INVALID     $s3, $s5, 0x6E00 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17327 | `__OSGlobalIntMask` | `0x8003BC14` | `0x765F616E` | `opcode_0x1D` | `.word       0x765F616E                   # INVALID     $s2, $ra, 0x616E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17345 | `__OSGlobalIntMask` | `0x8003BC38` | `0x72756E00` | `opcode_0x1C` | `.word       0x72756E00                   # INVALID     $s3, $s5, 0x6E00 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:17533 | `__OSGlobalIntMask` | `0x8003BDB0` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18139 | `__OSGlobalIntMask` | `0x8003C26C` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18141 | `__OSGlobalIntMask` | `0x8003C270` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18143 | `__OSGlobalIntMask` | `0x8003C274` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18145 | `__OSGlobalIntMask` | `0x8003C278` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18147 | `__OSGlobalIntMask` | `0x8003C27C` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18149 | `__OSGlobalIntMask` | `0x8003C280` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18151 | `__OSGlobalIntMask` | `0x8003C284` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18153 | `__OSGlobalIntMask` | `0x8003C288` | `0x43870000` | `cop0` | `.word       0x43870000                   # INVALID     $gp, $a3, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18155 | `__OSGlobalIntMask` | `0x8003C28C` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18157 | `__OSGlobalIntMask` | `0x8003C290` | `0x42B40000` | `cop0` | `.word       0x42B40000                   # INVALID     $s5, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18159 | `__OSGlobalIntMask` | `0x8003C294` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18161 | `__OSGlobalIntMask` | `0x8003C298` | `0x43870000` | `cop0` | `.word       0x43870000                   # INVALID     $gp, $a3, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18163 | `__OSGlobalIntMask` | `0x8003C29C` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18165 | `__OSGlobalIntMask` | `0x8003C2A0` | `0x42B40000` | `cop0` | `.word       0x42B40000                   # INVALID     $s5, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18167 | `__OSGlobalIntMask` | `0x8003C2A4` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18169 | `__OSGlobalIntMask` | `0x8003C2A8` | `0x43B40000` | `cop0` | `.word       0x43B40000                   # INVALID     $sp, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18171 | `__OSGlobalIntMask` | `0x8003C2AC` | `0xC3340000` | `opcode_0x30` | `ll          $s4, 0x0($t9)` |
| funcs_8.c:18173 | `__OSGlobalIntMask` | `0x8003C2B0` | `0x43B40000` | `cop0` | `.word       0x43B40000                   # INVALID     $sp, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:18235 | `__OSGlobalIntMask` | `0x8003C318` | `0x7469746C` | `opcode_0x1D` | `.word       0x7469746C                   # INVALID     $v1, $t1, 0x746C # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18241 | `__OSGlobalIntMask` | `0x8003C324` | `0x7269616C` | `opcode_0x1C` | `.word       0x7269616C                   # INVALID     $s3, $t1, 0x616C # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18245 | `__OSGlobalIntMask` | `0x8003C32C` | `0x726F6775` | `opcode_0x1C` | `.word       0x726F6775                   # INVALID     $s3, $t7, 0x6775 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18251 | `__OSGlobalIntMask` | `0x8003C338` | `0x726F6775` | `opcode_0x1C` | `.word       0x726F6775                   # INVALID     $s3, $t7, 0x6775 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18271 | `__OSGlobalIntMask` | `0x8003C360` | `0x73657138` | `opcode_0x1C` | `.word       0x73657138                   # INVALID     $k1, $a1, 0x7138 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18277 | `__OSGlobalIntMask` | `0x8003C36C` | `0x73657137` | `opcode_0x1C` | `.word       0x73657137                   # INVALID     $k1, $a1, 0x7137 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18283 | `__OSGlobalIntMask` | `0x8003C378` | `0x73657136` | `opcode_0x1C` | `.word       0x73657136                   # INVALID     $k1, $a1, 0x7136 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18289 | `__OSGlobalIntMask` | `0x8003C384` | `0x73657135` | `opcode_0x1C` | `.word       0x73657135                   # INVALID     $k1, $a1, 0x7135 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18295 | `__OSGlobalIntMask` | `0x8003C390` | `0x73657134` | `opcode_0x1C` | `.word       0x73657134                   # INVALID     $k1, $a1, 0x7134 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18301 | `__OSGlobalIntMask` | `0x8003C39C` | `0x73657133` | `opcode_0x1C` | `.word       0x73657133                   # INVALID     $k1, $a1, 0x7133 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18307 | `__OSGlobalIntMask` | `0x8003C3A8` | `0x73657132` | `opcode_0x1C` | `.word       0x73657132                   # INVALID     $k1, $a1, 0x7132 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18313 | `__OSGlobalIntMask` | `0x8003C3B4` | `0x73657131` | `opcode_0x1C` | `.word       0x73657131                   # INVALID     $k1, $a1, 0x7131 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18559 | `__OSGlobalIntMask` | `0x8003C4B0` | `0x79000000` | `opcode_0x1E` | `.word       0x79000000                   # INVALID     $t0, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18613 | `__OSGlobalIntMask` | `0x8003C51C` | `0x73696C65` | `opcode_0x1C` | `.word       0x73696C65                   # INVALID     $k1, $t1, 0x6C65 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18619 | `__OSGlobalIntMask` | `0x8003C528` | `0x73696C65` | `opcode_0x1C` | `.word       0x73696C65                   # INVALID     $k1, $t1, 0x6C65 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18740 | `__OSGlobalIntMask` | `0x8003C5CC` | `0x72740000` | `opcode_0x1C` | `.word       0x72740000                   # INVALID     $s3, $s4, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:18745 | `__OSGlobalIntMask` | `0x8003C5CC` | `0x72740000` | `opcode_0x1C` | `.word       0x72740000                   # INVALID     $s3, $s4, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19096 | `__OSGlobalIntMask` | `0x8003C72C` | `0x736F756E` | `opcode_0x1C` | `.word       0x736F756E                   # INVALID     $k1, $t7, 0x756E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19102 | `__OSGlobalIntMask` | `0x8003C738` | `0x4E440000` | `opcode_0x13` | `.word       0x4E440000                   # INVALID     $s2, $a0, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19104 | `__OSGlobalIntMask` | `0x8003C73C` | `0x736F756E` | `opcode_0x1C` | `.word       0x736F756E                   # INVALID     $k1, $t7, 0x756E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19110 | `__OSGlobalIntMask` | `0x8003C748` | `0x4E440000` | `opcode_0x13` | `.word       0x4E440000                   # INVALID     $s2, $a0, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19112 | `__OSGlobalIntMask` | `0x8003C74C` | `0x736F756E` | `opcode_0x1C` | `.word       0x736F756E                   # INVALID     $k1, $t7, 0x756E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19118 | `__OSGlobalIntMask` | `0x8003C758` | `0x4E440000` | `opcode_0x13` | `.word       0x4E440000                   # INVALID     $s2, $a0, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19120 | `__OSGlobalIntMask` | `0x8003C75C` | `0x736F756E` | `opcode_0x1C` | `.word       0x736F756E                   # INVALID     $k1, $t7, 0x756E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19126 | `__OSGlobalIntMask` | `0x8003C768` | `0x4E440000` | `opcode_0x13` | `.word       0x4E440000                   # INVALID     $s2, $a0, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19128 | `__OSGlobalIntMask` | `0x8003C76C` | `0x42480000` | `cop0` | `.word       0x42480000                   # INVALID     $s2, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19130 | `__OSGlobalIntMask` | `0x8003C770` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:19132 | `__OSGlobalIntMask` | `0x8003C774` | `0x736F756E` | `opcode_0x1C` | `.word       0x736F756E                   # INVALID     $k1, $t7, 0x756E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19146 | `__OSGlobalIntMask` | `0x8003C784` | `0x42160000` | `cop0` | `.word       0x42160000                   # INVALID     $s0, $s6, 0x0 # 00000000 <InstrIdType: CPU_COP0_TLB>` |
| funcs_8.c:19150 | `__OSGlobalIntMask` | `0x8003C78C` | `0x42480000` | `cop0` | `.word       0x42480000                   # INVALID     $s2, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19152 | `__OSGlobalIntMask` | `0x8003C790` | `0x73706565` | `opcode_0x1C` | `.word       0x73706565                   # INVALID     $k1, $s0, 0x6565 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19156 | `__OSGlobalIntMask` | `0x8003C798` | `0x42FE0000` | `cop0` | `.word       0x42FE0000                   # INVALID     $s7, $fp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19160 | `__OSGlobalIntMask` | `0x8003C7A0` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19162 | `__OSGlobalIntMask` | `0x8003C7A4` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19172 | `__OSGlobalIntMask` | `0x8003C7B8` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19178 | `__OSGlobalIntMask` | `0x8003C7C4` | `0x42FE0000` | `cop0` | `.word       0x42FE0000                   # INVALID     $s7, $fp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19186 | `__OSGlobalIntMask` | `0x8003C7D4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:19192 | `__OSGlobalIntMask` | `0x8003C7E0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:19206 | `__OSGlobalIntMask` | `0x8003C7FC` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19210 | `__OSGlobalIntMask` | `0x8003C804` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:19216 | `__OSGlobalIntMask` | `0x8003C810` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:19230 | `__OSGlobalIntMask` | `0x8003C82C` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:19232 | `__OSGlobalIntMask` | `0x8003C830` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:19242 | `__OSGlobalIntMask` | `0x8003C844` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19244 | `__OSGlobalIntMask` | `0x8003C848` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:19298 | `__OSGlobalIntMask` | `0x8003C8B4` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:19304 | `__OSGlobalIntMask` | `0x8003C8C0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:19333 | `__OSGlobalIntMask` | `0x8003C8E8` | `0x447A0000` | `cop1` | `.word       0x447A0000                   # INVALID     $v1, $k0, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:19335 | `__OSGlobalIntMask` | `0x8003C8EC` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:19337 | `__OSGlobalIntMask` | `0x8003C8F0` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:19339 | `__OSGlobalIntMask` | `0x8003C8F4` | `0x40860A92` | `cop0` | `.word       0x40860A92                   # mtc0        $a2, Random # 00000292 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19405 | `__OSGlobalIntMask` | `0x8003C960` | `0x706C5F63` | `opcode_0x1C` | `.word       0x706C5F63                   # INVALID     $v1, $t4, 0x5F63 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19407 | `__OSGlobalIntMask` | `0x8003C964` | `0x72616674` | `opcode_0x1C` | `.word       0x72616674                   # INVALID     $s3, $at, 0x6674 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19409 | `__OSGlobalIntMask` | `0x8003C968` | `0x732F7368` | `opcode_0x1C` | `.word       0x732F7368                   # INVALID     $t9, $t7, 0x7368 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19413 | `__OSGlobalIntMask` | `0x8003C970` | `0x735F544D` | `opcode_0x1C` | `.word       0x735F544D                   # INVALID     $k0, $ra, 0x544D # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19419 | `__OSGlobalIntMask` | `0x8003C97C` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:19425 | `__OSGlobalIntMask` | `0x8003C988` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19427 | `__OSGlobalIntMask` | `0x8003C98C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19431 | `__OSGlobalIntMask` | `0x8003C994` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19433 | `__OSGlobalIntMask` | `0x8003C998` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19437 | `__OSGlobalIntMask` | `0x8003C9A0` | `0x42C80000` | `cop0` | `.word       0x42C80000                   # INVALID     $s6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19441 | `__OSGlobalIntMask` | `0x8003C9A8` | `0x42C80000` | `cop0` | `.word       0x42C80000                   # INVALID     $s6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19445 | `__OSGlobalIntMask` | `0x8003C9B0` | `0x706C5F63` | `opcode_0x1C` | `.word       0x706C5F63                   # INVALID     $v1, $t4, 0x5F63 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19447 | `__OSGlobalIntMask` | `0x8003C9B4` | `0x72616674` | `opcode_0x1C` | `.word       0x72616674                   # INVALID     $s3, $at, 0x6674 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19449 | `__OSGlobalIntMask` | `0x8003C9B8` | `0x732F6B6F` | `opcode_0x1C` | `.word       0x732F6B6F                   # INVALID     $t9, $t7, 0x6B6F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19479 | `__OSGlobalIntMask` | `0x8003C9D8` | `0x74000000` | `opcode_0x1D` | `.word       0x74000000                   # INVALID     $zero, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19486 | `__OSGlobalIntMask` | `0x8003C9E4` | `0x74000000` | `opcode_0x1D` | `.word       0x74000000                   # INVALID     $zero, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19492 | `__OSGlobalIntMask` | `0x8003C9F0` | `0x74000000` | `opcode_0x1D` | `.word       0x74000000                   # INVALID     $zero, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19496 | `__OSGlobalIntMask` | `0x8003C9F8` | `0x746E6B5F` | `opcode_0x1D` | `.word       0x746E6B5F                   # INVALID     $v1, $t6, 0x6B5F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19557 | `__OSGlobalIntMask` | `0x8003CA70` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19559 | `__OSGlobalIntMask` | `0x8003CA74` | `0x414CCCCD` | `cop0` | `.word       0x414CCCCD                   # INVALID     $t2, $t4, -0x3333 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19561 | `__OSGlobalIntMask` | `0x8003CA78` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19567 | `__OSGlobalIntMask` | `0x8003CA84` | `0x43A00000` | `cop0` | `.word       0x43A00000                   # INVALID     $sp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19575 | `__OSGlobalIntMask` | `0x8003CA94` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:19581 | `__OSGlobalIntMask` | `0x8003CAA0` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_8.c:19589 | `__OSGlobalIntMask` | `0x8003CAB0` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19593 | `__OSGlobalIntMask` | `0x8003CAB8` | `0x414CCCCD` | `cop0` | `.word       0x414CCCCD                   # INVALID     $t2, $t4, -0x3333 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19595 | `__OSGlobalIntMask` | `0x8003CABC` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19599 | `__OSGlobalIntMask` | `0x8003CAC4` | `0x43A00000` | `cop0` | `.word       0x43A00000                   # INVALID     $sp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19603 | `__OSGlobalIntMask` | `0x8003CACC` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_8.c:19607 | `__OSGlobalIntMask` | `0x8003CAD4` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:19609 | `__OSGlobalIntMask` | `0x8003CAD8` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19627 | `__OSGlobalIntMask` | `0x8003CAFC` | `0x73617665` | `opcode_0x1C` | `.word       0x73617665                   # INVALID     $k1, $at, 0x7665 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19631 | `__OSGlobalIntMask` | `0x8003CB04` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19635 | `__OSGlobalIntMask` | `0x8003CB0C` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19637 | `__OSGlobalIntMask` | `0x8003CB10` | `0x43485200` | `cop0` | `.word       0x43485200                   # INVALID     $k0, $t0, 0x5200 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19641 | `__OSGlobalIntMask` | `0x8003CB18` | `0x42535400` | `cop0` | `.word       0x42535400                   # INVALID     $s2, $s3, 0x5400 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19646 | `__OSGlobalIntMask` | `0x8003CB18` | `0x42535400` | `cop0` | `.word       0x42535400                   # INVALID     $s2, $s3, 0x5400 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19649 | `__OSGlobalIntMask` | `0x8003CB1C` | `0x4D415200` | `opcode_0x13` | `.word       0x4D415200                   # INVALID     $t2, $at, 0x5200 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19655 | `__OSGlobalIntMask` | `0x8003CB28` | `0x4A554500` | `opcode_0x12` | `.word       0x4A554500                   # INVALID     $s2, $s5, 0x4500 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:19664 | `__OSGlobalIntMask` | `0x8003CB28` | `0x4A554500` | `opcode_0x12` | `.word       0x4A554500                   # INVALID     $s2, $s5, 0x4500 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:19670 | `__OSGlobalIntMask` | `0x8003CB28` | `0x4A554500` | `opcode_0x12` | `.word       0x4A554500                   # INVALID     $s2, $s5, 0x4500 # 00000000 <InstrIdType: CPU_COP2>` |
| funcs_8.c:19675 | `__OSGlobalIntMask` | `0x8003CB30` | `0x484F4C00` | `opcode_0x12` | `.word       0x484F4C00                   # cfc2        $t7, $9 # 00000400 <InstrIdType: CPU_COP2>` |
| funcs_8.c:19680 | `__OSGlobalIntMask` | `0x8003CB30` | `0x484F4C00` | `opcode_0x12` | `.word       0x484F4C00                   # cfc2        $t7, $9 # 00000400 <InstrIdType: CPU_COP2>` |
| funcs_8.c:19683 | `__OSGlobalIntMask` | `0x8003CB34` | `0x464C4F00` | `cop1` | `.word       0x464C4F00                   # INVALID     $s2, $t4, 0x4F00 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:19687 | `__OSGlobalIntMask` | `0x8003CB3C` | `0x73257300` | `opcode_0x1C` | `.word       0x73257300                   # INVALID     $t9, $a1, 0x7300 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19691 | `__OSGlobalIntMask` | `0x8003CB44` | `0x73000000` | `opcode_0x1C` | `.word       0x73000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19715 | `__OSGlobalIntMask` | `0x8003CB74` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19717 | `__OSGlobalIntMask` | `0x8003CB78` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19719 | `__OSGlobalIntMask` | `0x8003CB7C` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_8.c:19721 | `__OSGlobalIntMask` | `0x8003CB80` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19723 | `__OSGlobalIntMask` | `0x8003CB84` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19735 | `__OSGlobalIntMask` | `0x8003CB9C` | `0x43B40000` | `cop0` | `.word       0x43B40000                   # INVALID     $sp, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19737 | `__OSGlobalIntMask` | `0x8003CBA0` | `0x43B40000` | `cop0` | `.word       0x43B40000                   # INVALID     $sp, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19741 | `__OSGlobalIntMask` | `0x8003CBA8` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:19745 | `__OSGlobalIntMask` | `0x8003CBB0` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:19759 | `__OSGlobalIntMask` | `0x8003CBCC` | `0x73686F63` | `opcode_0x1C` | `.word       0x73686F63                   # INVALID     $k1, $t0, 0x6F63 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19765 | `__OSGlobalIntMask` | `0x8003CBD8` | `0x73686F63` | `opcode_0x1C` | `.word       0x73686F63                   # INVALID     $k1, $t0, 0x6F63 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19771 | `__OSGlobalIntMask` | `0x8003CBE4` | `0x73686F63` | `opcode_0x1C` | `.word       0x73686F63                   # INVALID     $k1, $t0, 0x6F63 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19781 | `__OSGlobalIntMask` | `0x8003CBF8` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19783 | `__OSGlobalIntMask` | `0x8003CBFC` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19787 | `__OSGlobalIntMask` | `0x8003CC04` | `0x41A00000` | `cop0` | `.word       0x41A00000                   # INVALID     $t5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19791 | `__OSGlobalIntMask` | `0x8003CC0C` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_8.c:19795 | `__OSGlobalIntMask` | `0x8003CC14` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:19803 | `__OSGlobalIntMask` | `0x8003CC24` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:19807 | `__OSGlobalIntMask` | `0x8003CC2C` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:19833 | `__OSGlobalIntMask` | `0x8003CC60` | `0x43520000` | `cop0` | `.word       0x43520000                   # INVALID     $k0, $s2, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19835 | `__OSGlobalIntMask` | `0x8003CC64` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19837 | `__OSGlobalIntMask` | `0x8003CC68` | `0x45800000` | `cop1` | `.word       0x45800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:19839 | `__OSGlobalIntMask` | `0x8003CC6C` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19841 | `__OSGlobalIntMask` | `0x8003CC70` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19845 | `__OSGlobalIntMask` | `0x8003CC78` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19849 | `__OSGlobalIntMask` | `0x8003CC80` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19855 | `__OSGlobalIntMask` | `0x8003CC8C` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19885 | `__OSGlobalIntMask` | `0x8003CCC8` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19887 | `__OSGlobalIntMask` | `0x8003CCCC` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19889 | `__OSGlobalIntMask` | `0x8003CCD0` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:19891 | `__OSGlobalIntMask` | `0x8003CCD4` | `0x765F7961` | `opcode_0x1D` | `.word       0x765F7961                   # INVALID     $s2, $ra, 0x7961 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19897 | `__OSGlobalIntMask` | `0x8003CCE0` | `0x765F7961` | `opcode_0x1D` | `.word       0x765F7961                   # INVALID     $s2, $ra, 0x7961 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19903 | `__OSGlobalIntMask` | `0x8003CCEC` | `0x70726F62` | `opcode_0x1C` | `.word       0x70726F62                   # INVALID     $v1, $s2, 0x6F62 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19909 | `__OSGlobalIntMask` | `0x8003CCF8` | `0x765F6372` | `opcode_0x1D` | `.word       0x765F6372                   # INVALID     $s2, $ra, 0x6372 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19911 | `__OSGlobalIntMask` | `0x8003CCFC` | `0x735F6869` | `opcode_0x1C` | `.word       0x735F6869                   # INVALID     $k0, $ra, 0x6869 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19915 | `__OSGlobalIntMask` | `0x8003CD04` | `0x725F7472` | `opcode_0x1C` | `.word       0x725F7472                   # INVALID     $s2, $ra, 0x7472 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19933 | `__OSGlobalIntMask` | `0x8003CD1C` | `0x725F626C` | `opcode_0x1C` | `.word       0x725F626C                   # INVALID     $s2, $ra, 0x626C # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19941 | `__OSGlobalIntMask` | `0x8003CD2C` | `0x705F6869` | `opcode_0x1C` | `.word       0x705F6869                   # INVALID     $v0, $ra, 0x6869 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19947 | `__OSGlobalIntMask` | `0x8003CD38` | `0x705F6869` | `opcode_0x1C` | `.word       0x705F6869                   # INVALID     $v0, $ra, 0x6869 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19951 | `__OSGlobalIntMask` | `0x8003CD40` | `0x72617074` | `opcode_0x1C` | `.word       0x72617074                   # INVALID     $s3, $at, 0x7074 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19955 | `__OSGlobalIntMask` | `0x8003CD48` | `0x7265625F` | `opcode_0x1C` | `.word       0x7265625F                   # INVALID     $s3, $a1, 0x625F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19957 | `__OSGlobalIntMask` | `0x8003CD4C` | `0x7472616E` | `opcode_0x1D` | `.word       0x7472616E                   # INVALID     $v1, $s2, 0x616E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19959 | `__OSGlobalIntMask` | `0x8003CD50` | `0x73706F72` | `opcode_0x1C` | `.word       0x73706F72                   # INVALID     $k1, $s0, 0x6F72 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19961 | `__OSGlobalIntMask` | `0x8003CD54` | `0x74000000` | `opcode_0x1D` | `.word       0x74000000                   # INVALID     $zero, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19963 | `__OSGlobalIntMask` | `0x8003CD58` | `0x77726C64` | `opcode_0x1D` | `.word       0x77726C64                   # INVALID     $k1, $s2, 0x6C64 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19967 | `__OSGlobalIntMask` | `0x8003CD60` | `0x74720000` | `opcode_0x1D` | `.word       0x74720000                   # INVALID     $v1, $s2, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19972 | `__OSGlobalIntMask` | `0x8003CD60` | `0x74720000` | `opcode_0x1D` | `.word       0x74720000                   # INVALID     $v1, $s2, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19975 | `__OSGlobalIntMask` | `0x8003CD64` | `0x765F686C` | `opcode_0x1D` | `.word       0x765F686C                   # INVALID     $s2, $ra, 0x686C # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19977 | `__OSGlobalIntMask` | `0x8003CD68` | `0x735F6869` | `opcode_0x1C` | `.word       0x735F6869                   # INVALID     $k0, $ra, 0x6869 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19981 | `__OSGlobalIntMask` | `0x8003CD70` | `0x77617665` | `opcode_0x1D` | `.word       0x77617665                   # INVALID     $k1, $at, 0x7665 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19983 | `__OSGlobalIntMask` | `0x8003CD74` | `0x736B696D` | `opcode_0x1C` | `.word       0x736B696D                   # INVALID     $k1, $t3, 0x696D # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:19989 | `__OSGlobalIntMask` | `0x8003CD80` | `0x72747261` | `opcode_0x1C` | `.word       0x72747261                   # INVALID     $s3, $s4, 0x7261 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20087 | `__OSGlobalIntMask` | `0x8003CE38` | `0x73625F68` | `opcode_0x1C` | `.word       0x73625F68                   # INVALID     $k1, $v0, 0x5F68 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20129 | `__OSGlobalIntMask` | `0x8003CE8C` | `0x73700000` | `opcode_0x1C` | `.word       0x73700000                   # INVALID     $k1, $s0, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20133 | `__OSGlobalIntMask` | `0x8003CE94` | `0x73687574` | `opcode_0x1C` | `.word       0x73687574                   # INVALID     $k1, $t0, 0x7574 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20135 | `__OSGlobalIntMask` | `0x8003CE98` | `0x746C6500` | `opcode_0x1D` | `.word       0x746C6500                   # INVALID     $v1, $t4, 0x6500 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20145 | `__OSGlobalIntMask` | `0x8003CEAC` | `0x7372635F` | `opcode_0x1C` | `.word       0x7372635F                   # INVALID     $k1, $s2, 0x635F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20163 | `__OSGlobalIntMask` | `0x8003CEC4` | `0x457FF000` | `cop1` | `.word       0x457FF000                   # INVALID     $t3, $ra, -0x1000 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:20201 | `__OSGlobalIntMask` | `0x8003CEFC` | `0x74727370` | `opcode_0x1D` | `.word       0x74727370                   # INVALID     $v1, $s2, 0x7370 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20203 | `__OSGlobalIntMask` | `0x8003CF00` | `0x72617900` | `opcode_0x1C` | `.word       0x72617900                   # INVALID     $s3, $at, 0x7900 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20205 | `__OSGlobalIntMask` | `0x8003CF04` | `0x77747273` | `opcode_0x1D` | `.word       0x77747273                   # INVALID     $k1, $s4, 0x7273 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20207 | `__OSGlobalIntMask` | `0x8003CF08` | `0x70726179` | `opcode_0x1C` | `.word       0x70726179                   # INVALID     $v1, $s2, 0x6179 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20211 | `__OSGlobalIntMask` | `0x8003CF10` | `0x77617465` | `opcode_0x1D` | `.word       0x77617465                   # INVALID     $k1, $at, 0x7465 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20213 | `__OSGlobalIntMask` | `0x8003CF14` | `0x72776869` | `opcode_0x1C` | `.word       0x72776869                   # INVALID     $s3, $s7, 0x6869 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20215 | `__OSGlobalIntMask` | `0x8003CF18` | `0x74655F31` | `opcode_0x1D` | `.word       0x74655F31                   # INVALID     $v1, $a1, 0x5F31 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20231 | `__OSGlobalIntMask` | `0x8003CF2C` | `0x74727370` | `opcode_0x1D` | `.word       0x74727370                   # INVALID     $v1, $s2, 0x7370 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20233 | `__OSGlobalIntMask` | `0x8003CF30` | `0x7261795F` | `opcode_0x1C` | `.word       0x7261795F                   # INVALID     $s3, $at, 0x795F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20235 | `__OSGlobalIntMask` | `0x8003CF34` | `0x414E4D00` | `cop0` | `.word       0x414E4D00                   # INVALID     $t2, $t6, 0x4D00 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20237 | `__OSGlobalIntMask` | `0x8003CF38` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:20245 | `__OSGlobalIntMask` | `0x8003CF48` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20253 | `__OSGlobalIntMask` | `0x8003CF58` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:20261 | `__OSGlobalIntMask` | `0x8003CF68` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:20269 | `__OSGlobalIntMask` | `0x8003CF78` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20271 | `__OSGlobalIntMask` | `0x8003CF7C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20283 | `__OSGlobalIntMask` | `0x8003CF94` | `0x400CCCCD` | `cop0` | `.word       0x400CCCCD                   # mfc0        $t4, Reserved25 # 000004CD <InstrIdType: CPU_COP0>` |
| funcs_8.c:20285 | `__OSGlobalIntMask` | `0x8003CF98` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:20295 | `__OSGlobalIntMask` | `0x8003CFAC` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:20299 | `__OSGlobalIntMask` | `0x8003CFB4` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20301 | `__OSGlobalIntMask` | `0x8003CFB8` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:20303 | `__OSGlobalIntMask` | `0x8003CFBC` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20305 | `__OSGlobalIntMask` | `0x8003CFC0` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20309 | `__OSGlobalIntMask` | `0x8003CFC8` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20311 | `__OSGlobalIntMask` | `0x8003CFCC` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20313 | `__OSGlobalIntMask` | `0x8003CFD0` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_8.c:20319 | `__OSGlobalIntMask` | `0x8003CFDC` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:20325 | `__OSGlobalIntMask` | `0x8003CFE8` | `0x42700000` | `cop0` | `.word       0x42700000                   # INVALID     $s3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20327 | `__OSGlobalIntMask` | `0x8003CFEC` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:20329 | `__OSGlobalIntMask` | `0x8003CFF0` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20333 | `__OSGlobalIntMask` | `0x8003CFF8` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20335 | `__OSGlobalIntMask` | `0x8003CFFC` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20339 | `__OSGlobalIntMask` | `0x8003D004` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20343 | `__OSGlobalIntMask` | `0x8003D00C` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:20347 | `__OSGlobalIntMask` | `0x8003D014` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:20359 | `__OSGlobalIntMask` | `0x8003D02C` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:20361 | `__OSGlobalIntMask` | `0x8003D030` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20363 | `__OSGlobalIntMask` | `0x8003D034` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20365 | `__OSGlobalIntMask` | `0x8003D038` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20369 | `__OSGlobalIntMask` | `0x8003D040` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20371 | `__OSGlobalIntMask` | `0x8003D044` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20375 | `__OSGlobalIntMask` | `0x8003D04C` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_8.c:20377 | `__OSGlobalIntMask` | `0x8003D050` | `0x42F00000` | `cop0` | `.word       0x42F00000                   # INVALID     $s7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20379 | `__OSGlobalIntMask` | `0x8003D054` | `0x40900000` | `cop0` | `mtc0        $s0, Index` |
| funcs_8.c:20383 | `__OSGlobalIntMask` | `0x8003D05C` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:20385 | `__OSGlobalIntMask` | `0x8003D060` | `0x42F00000` | `cop0` | `.word       0x42F00000                   # INVALID     $s7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20389 | `__OSGlobalIntMask` | `0x8003D068` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:20393 | `__OSGlobalIntMask` | `0x8003D070` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20397 | `__OSGlobalIntMask` | `0x8003D078` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20399 | `__OSGlobalIntMask` | `0x8003D07C` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20403 | `__OSGlobalIntMask` | `0x8003D084` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20413 | `__OSGlobalIntMask` | `0x8003D098` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:20415 | `__OSGlobalIntMask` | `0x8003D09C` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20417 | `__OSGlobalIntMask` | `0x8003D0A0` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20419 | `__OSGlobalIntMask` | `0x8003D0A4` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20421 | `__OSGlobalIntMask` | `0x8003D0A8` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20423 | `__OSGlobalIntMask` | `0x8003D0AC` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:20429 | `__OSGlobalIntMask` | `0x8003D0B8` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:20435 | `__OSGlobalIntMask` | `0x8003D0C4` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20439 | `__OSGlobalIntMask` | `0x8003D0CC` | `0x7C2206FF` | `opcode_0x1F` | `.word       0x7C2206FF                   # INVALID     $at, $v0, 0x6FF # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20441 | `__OSGlobalIntMask` | `0x8003D0D0` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_8.c:20443 | `__OSGlobalIntMask` | `0x8003D0D4` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20445 | `__OSGlobalIntMask` | `0x8003D0D8` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20469 | `__OSGlobalIntMask` | `0x8003D108` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20475 | `__OSGlobalIntMask` | `0x8003D114` | `0x40555555` | `cop0` | `.word       0x40555555                   # cfc0        $s5, EntryHi # 00000555 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20481 | `__OSGlobalIntMask` | `0x8003D120` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20483 | `__OSGlobalIntMask` | `0x8003D124` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20491 | `__OSGlobalIntMask` | `0x8003D134` | `0xC2C80000` | `opcode_0x30` | `ll          $t0, 0x0($s6)` |
| funcs_8.c:20493 | `__OSGlobalIntMask` | `0x8003D138` | `0x43200000` | `cop0` | `.word       0x43200000                   # INVALID     $t9, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20495 | `__OSGlobalIntMask` | `0x8003D13C` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20497 | `__OSGlobalIntMask` | `0x8003D140` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20499 | `__OSGlobalIntMask` | `0x8003D144` | `0x41800000` | `cop0` | `.word       0x41800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20503 | `__OSGlobalIntMask` | `0x8003D14C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20505 | `__OSGlobalIntMask` | `0x8003D150` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20519 | `__OSGlobalIntMask` | `0x8003D16C` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20537 | `__OSGlobalIntMask` | `0x8003D18C` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:20539 | `__OSGlobalIntMask` | `0x8003D190` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:20541 | `__OSGlobalIntMask` | `0x8003D194` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20551 | `__OSGlobalIntMask` | `0x8003D1A8` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:20555 | `__OSGlobalIntMask` | `0x8003D1B0` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:20561 | `__OSGlobalIntMask` | `0x8003D1BC` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20563 | `__OSGlobalIntMask` | `0x8003D1C0` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20565 | `__OSGlobalIntMask` | `0x8003D1C4` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20569 | `__OSGlobalIntMask` | `0x8003D1CC` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20575 | `__OSGlobalIntMask` | `0x8003D1D8` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20581 | `__OSGlobalIntMask` | `0x8003D1E4` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20590 | `__OSGlobalIntMask` | `0x8003D1F4` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20612 | `__OSGlobalIntMask` | `0x8003D220` | `0xF29090FF` | `opcode_0x3C` | `scd         $s0, -0x6F01($s4)` |
| funcs_8.c:20618 | `__OSGlobalIntMask` | `0x8003D228` | `0x44610000` | `cop1` | `.word       0x44610000                   # INVALID     $v1, $at, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:20622 | `__OSGlobalIntMask` | `0x8003D230` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:20624 | `__OSGlobalIntMask` | `0x8003D234` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_8.c:20626 | `__OSGlobalIntMask` | `0x8003D238` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20628 | `__OSGlobalIntMask` | `0x8003D23C` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20630 | `__OSGlobalIntMask` | `0x8003D240` | `0x42D55555` | `cop0` | `.word       0x42D55555                   # INVALID     $s6, $s5, 0x5555 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20644 | `__OSGlobalIntMask` | `0x8003D25C` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20648 | `__OSGlobalIntMask` | `0x8003D264` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:20650 | `__OSGlobalIntMask` | `0x8003D268` | `0x43A00000` | `cop0` | `.word       0x43A00000                   # INVALID     $sp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20654 | `__OSGlobalIntMask` | `0x8003D270` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20658 | `__OSGlobalIntMask` | `0x8003D278` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:20660 | `__OSGlobalIntMask` | `0x8003D27C` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:20668 | `__OSGlobalIntMask` | `0x8003D28C` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20672 | `__OSGlobalIntMask` | `0x8003D294` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:20674 | `__OSGlobalIntMask` | `0x8003D298` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20678 | `__OSGlobalIntMask` | `0x8003D2A0` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20680 | `__OSGlobalIntMask` | `0x8003D2A4` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20684 | `__OSGlobalIntMask` | `0x8003D2AC` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20686 | `__OSGlobalIntMask` | `0x8003D2B0` | `0x77616B65` | `opcode_0x1D` | `.word       0x77616B65                   # INVALID     $k1, $at, 0x6B65 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20690 | `__OSGlobalIntMask` | `0x8003D2B8` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20698 | `__OSGlobalIntMask` | `0x8003D2C8` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20700 | `__OSGlobalIntMask` | `0x8003D2CC` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20714 | `__OSGlobalIntMask` | `0x8003D2E8` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_8.c:20718 | `__OSGlobalIntMask` | `0x8003D2F0` | `0x40E00000` | `cop0` | `.word       0x40E00000                   # INVALID     $a3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20720 | `__OSGlobalIntMask` | `0x8003D2F4` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20732 | `__OSGlobalIntMask` | `0x8003D30C` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:20750 | `__OSGlobalIntMask` | `0x8003D330` | `0x400CCCCD` | `cop0` | `.word       0x400CCCCD                   # mfc0        $t4, Reserved25 # 000004CD <InstrIdType: CPU_COP0>` |
| funcs_8.c:20770 | `__OSGlobalIntMask` | `0x8003D358` | `0x74726E73` | `opcode_0x1D` | `.word       0x74726E73                   # INVALID     $v1, $s2, 0x6E73 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20774 | `__OSGlobalIntMask` | `0x8003D360` | `0x746F705F` | `opcode_0x1D` | `.word       0x746F705F                   # INVALID     $v1, $t7, 0x705F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20776 | `__OSGlobalIntMask` | `0x8003D364` | `0x746F7000` | `opcode_0x1D` | `.word       0x746F7000                   # INVALID     $v1, $t7, 0x7000 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20780 | `__OSGlobalIntMask` | `0x8003D36C` | `0x726E7331` | `opcode_0x1C` | `.word       0x726E7331                   # INVALID     $s3, $t6, 0x7331 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20790 | `__OSGlobalIntMask` | `0x8003D380` | `0x726E7325` | `opcode_0x1C` | `.word       0x726E7325                   # INVALID     $s3, $t6, 0x7325 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:20832 | `__OSGlobalIntMask` | `0x8003D3D4` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20834 | `__OSGlobalIntMask` | `0x8003D3D8` | `0x43B40000` | `cop0` | `.word       0x43B40000                   # INVALID     $sp, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20840 | `__OSGlobalIntMask` | `0x8003D3E4` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20842 | `__OSGlobalIntMask` | `0x8003D3E8` | `0x43B40000` | `cop0` | `.word       0x43B40000                   # INVALID     $sp, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20844 | `__OSGlobalIntMask` | `0x8003D3EC` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_8.c:20848 | `__OSGlobalIntMask` | `0x8003D3F4` | `0x41C00000` | `cop0` | `.word       0x41C00000                   # INVALID     $t6, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20866 | `__OSGlobalIntMask` | `0x8003D418` | `0x400CCCCD` | `cop0` | `.word       0x400CCCCD                   # mfc0        $t4, Reserved25 # 000004CD <InstrIdType: CPU_COP0>` |
| funcs_8.c:20870 | `__OSGlobalIntMask` | `0x8003D420` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:20874 | `__OSGlobalIntMask` | `0x8003D428` | `0xC0333333` | `opcode_0x30` | `ll          $s3, 0x3333($at)` |
| funcs_8.c:20876 | `__OSGlobalIntMask` | `0x8003D42C` | `0x4019999A` | `cop0` | `.word       0x4019999A                   # mfc0        $t9, WatchHi # 0000019A <InstrIdType: CPU_COP0>` |
| funcs_8.c:20878 | `__OSGlobalIntMask` | `0x8003D430` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:20880 | `__OSGlobalIntMask` | `0x8003D434` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_8.c:20884 | `__OSGlobalIntMask` | `0x8003D43C` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20886 | `__OSGlobalIntMask` | `0x8003D440` | `0x4059999A` | `cop0` | `.word       0x4059999A                   # cfc0        $t9, WatchHi # 0000019A <InstrIdType: CPU_COP0>` |
| funcs_8.c:20901 | `__OSGlobalIntMask` | `0x8003D45C` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20903 | `__OSGlobalIntMask` | `0x8003D460` | `0x414CCCCD` | `cop0` | `.word       0x414CCCCD                   # INVALID     $t2, $t4, -0x3333 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20905 | `__OSGlobalIntMask` | `0x8003D464` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20911 | `__OSGlobalIntMask` | `0x8003D470` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:20913 | `__OSGlobalIntMask` | `0x8003D474` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_8.c:20915 | `__OSGlobalIntMask` | `0x8003D478` | `0x43A00000` | `cop0` | `.word       0x43A00000                   # INVALID     $sp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20921 | `__OSGlobalIntMask` | `0x8003D484` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20925 | `__OSGlobalIntMask` | `0x8003D48C` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20927 | `__OSGlobalIntMask` | `0x8003D490` | `0x41600000` | `cop0` | `.word       0x41600000                   # INVALID     $t3, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20929 | `__OSGlobalIntMask` | `0x8003D494` | `0x41500000` | `cop0` | `.word       0x41500000                   # INVALID     $t2, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20947 | `__OSGlobalIntMask` | `0x8003D4B8` | `0x41000000` | `cop0` | `bc0f        L_8003D4BC` |
| funcs_8.c:20950 | `__OSGlobalIntMask` | `0x8003D4BC` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:20952 | `__OSGlobalIntMask` | `0x8003D4C0` | `0x43B40000` | `cop0` | `.word       0x43B40000                   # INVALID     $sp, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20956 | `__OSGlobalIntMask` | `0x8003D4C8` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_8.c:20984 | `__OSGlobalIntMask` | `0x8003D500` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20986 | `__OSGlobalIntMask` | `0x8003D504` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:20988 | `__OSGlobalIntMask` | `0x8003D508` | `0x47800000` | `cop1` | `.word       0x47800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:20994 | `__OSGlobalIntMask` | `0x8003D514` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:20996 | `__OSGlobalIntMask` | `0x8003D518` | `0x73686965` | `opcode_0x1C` | `.word       0x73686965                   # INVALID     $k1, $t0, 0x6965 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21012 | `__OSGlobalIntMask` | `0x8003D538` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21018 | `__OSGlobalIntMask` | `0x8003D544` | `0x471C4000` | `cop1` | `.word       0x471C4000                   # INVALID     $t8, $gp, 0x4000 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:21020 | `__OSGlobalIntMask` | `0x8003D548` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21022 | `__OSGlobalIntMask` | `0x8003D54C` | `0x43340000` | `cop0` | `.word       0x43340000                   # INVALID     $t9, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21024 | `__OSGlobalIntMask` | `0x8003D550` | `0x43000000` | `cop0` | `.word       0x43000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21026 | `__OSGlobalIntMask` | `0x8003D554` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21028 | `__OSGlobalIntMask` | `0x8003D558` | `0x471C4000` | `cop1` | `.word       0x471C4000                   # INVALID     $t8, $gp, 0x4000 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:21030 | `__OSGlobalIntMask` | `0x8003D55C` | `0x43000000` | `cop0` | `.word       0x43000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21032 | `__OSGlobalIntMask` | `0x8003D560` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21036 | `__OSGlobalIntMask` | `0x8003D568` | `0x42B40000` | `cop0` | `.word       0x42B40000                   # INVALID     $s5, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21038 | `__OSGlobalIntMask` | `0x8003D56C` | `0xC2B40000` | `opcode_0x30` | `ll          $s4, 0x0($s5)` |
| funcs_8.c:21040 | `__OSGlobalIntMask` | `0x8003D570` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21046 | `__OSGlobalIntMask` | `0x8003D57C` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21048 | `__OSGlobalIntMask` | `0x8003D580` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21054 | `__OSGlobalIntMask` | `0x8003D58C` | `0x43000000` | `cop0` | `.word       0x43000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21056 | `__OSGlobalIntMask` | `0x8003D590` | `0x47435000` | `cop1` | `.word       0x47435000                   # INVALID     $k0, $v1, 0x5000 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:21058 | `__OSGlobalIntMask` | `0x8003D594` | `0x47435000` | `cop1` | `.word       0x47435000                   # INVALID     $k0, $v1, 0x5000 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:21080 | `__OSGlobalIntMask` | `0x8003D5C0` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21082 | `__OSGlobalIntMask` | `0x8003D5C4` | `0x43000000` | `cop0` | `.word       0x43000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21084 | `__OSGlobalIntMask` | `0x8003D5C8` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21086 | `__OSGlobalIntMask` | `0x8003D5CC` | `0xC3800000` | `opcode_0x30` | `ll          $zero, 0x0($gp)` |
| funcs_8.c:21120 | `__OSGlobalIntMask` | `0x8003D610` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21122 | `__OSGlobalIntMask` | `0x8003D614` | `0x43000000` | `cop0` | `.word       0x43000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21124 | `__OSGlobalIntMask` | `0x8003D618` | `0x437F0000` | `cop0` | `.word       0x437F0000                   # INVALID     $k1, $ra, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21126 | `__OSGlobalIntMask` | `0x8003D61C` | `0xC3800000` | `opcode_0x30` | `ll          $zero, 0x0($gp)` |
| funcs_8.c:21130 | `__OSGlobalIntMask` | `0x8003D624` | `0x73686965` | `opcode_0x1C` | `.word       0x73686965                   # INVALID     $k1, $t0, 0x6965 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21134 | `__OSGlobalIntMask` | `0x8003D62C` | `0x414C0030` | `cop0` | `.word       0x414C0030                   # INVALID     $t2, $t4, 0x30 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21136 | `__OSGlobalIntMask` | `0x8003D630` | `0x7261726D` | `opcode_0x1C` | `.word       0x7261726D                   # INVALID     $s3, $at, 0x726D # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21160 | `__OSGlobalIntMask` | `0x8003D648` | `0x726F6872` | `opcode_0x1C` | `.word       0x726F6872                   # INVALID     $s3, $t7, 0x6872 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21178 | `__OSGlobalIntMask` | `0x8003D660` | `0x746F705F` | `opcode_0x1D` | `.word       0x746F705F                   # INVALID     $v1, $t7, 0x705F # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21180 | `__OSGlobalIntMask` | `0x8003D664` | `0x7472616E` | `opcode_0x1D` | `.word       0x7472616E                   # INVALID     $v1, $s2, 0x616E # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21184 | `__OSGlobalIntMask` | `0x8003D66C` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21188 | `__OSGlobalIntMask` | `0x8003D674` | `0x42480000` | `cop0` | `.word       0x42480000                   # INVALID     $s2, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21190 | `__OSGlobalIntMask` | `0x8003D678` | `0x428C0000` | `cop0` | `.word       0x428C0000                   # INVALID     $s4, $t4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21204 | `__OSGlobalIntMask` | `0x8003D694` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21206 | `__OSGlobalIntMask` | `0x8003D698` | `0x42480000` | `cop0` | `.word       0x42480000                   # INVALID     $s2, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21236 | `__OSGlobalIntMask` | `0x8003D6D4` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21240 | `__OSGlobalIntMask` | `0x8003D6DC` | `0x73686C64` | `opcode_0x1C` | `.word       0x73686C64                   # INVALID     $k1, $t0, 0x6C64 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21246 | `__OSGlobalIntMask` | `0x8003D6E8` | `0x7773686C` | `opcode_0x1D` | `.word       0x7773686C                   # INVALID     $k1, $s3, 0x686C # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21252 | `__OSGlobalIntMask` | `0x8003D6F4` | `0x42C80000` | `cop0` | `.word       0x42C80000                   # INVALID     $s6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21254 | `__OSGlobalIntMask` | `0x8003D6F8` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:21256 | `__OSGlobalIntMask` | `0x8003D6FC` | `0x42C80000` | `cop0` | `.word       0x42C80000                   # INVALID     $s6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21262 | `__OSGlobalIntMask` | `0x8003D708` | `0x76616375` | `opcode_0x1D` | `.word       0x76616375                   # INVALID     $s3, $at, 0x6375 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21278 | `__OSGlobalIntMask` | `0x8003D728` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:21304 | `__OSGlobalIntMask` | `0x8003D75C` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:21306 | `__OSGlobalIntMask` | `0x8003D760` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:21312 | `__OSGlobalIntMask` | `0x8003D76C` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:21316 | `__OSGlobalIntMask` | `0x8003D774` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:21318 | `__OSGlobalIntMask` | `0x8003D778` | `0xC0400000` | `opcode_0x30` | `ll          $zero, 0x0($v0)` |
| funcs_8.c:21324 | `__OSGlobalIntMask` | `0x8003D784` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:21326 | `__OSGlobalIntMask` | `0x8003D788` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:21330 | `__OSGlobalIntMask` | `0x8003D790` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21332 | `__OSGlobalIntMask` | `0x8003D794` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21334 | `__OSGlobalIntMask` | `0x8003D798` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21336 | `__OSGlobalIntMask` | `0x8003D79C` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21338 | `__OSGlobalIntMask` | `0x8003D7A0` | `0x41700000` | `cop0` | `.word       0x41700000                   # INVALID     $t3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21340 | `__OSGlobalIntMask` | `0x8003D7A4` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21342 | `__OSGlobalIntMask` | `0x8003D7A8` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:21346 | `__OSGlobalIntMask` | `0x8003D7B0` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:21364 | `__OSGlobalIntMask` | `0x8003D7D4` | `0x42652EE1` | `cop0` | `.word       0x42652EE1                   # INVALID     $s3, $a1, 0x2EE1 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21366 | `__OSGlobalIntMask` | `0x8003D7D8` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:21380 | `__OSGlobalIntMask` | `0x8003D7F4` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21384 | `__OSGlobalIntMask` | `0x8003D7FC` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21392 | `__OSGlobalIntMask` | `0x8003D80C` | `0x40C00000` | `cop0` | `ctc0        $zero, Index` |
| funcs_8.c:21394 | `__OSGlobalIntMask` | `0x8003D810` | `0x43100000` | `cop0` | `.word       0x43100000                   # INVALID     $t8, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21396 | `__OSGlobalIntMask` | `0x8003D814` | `0x42700000` | `cop0` | `.word       0x42700000                   # INVALID     $s3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21398 | `__OSGlobalIntMask` | `0x8003D818` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:21400 | `__OSGlobalIntMask` | `0x8003D81C` | `0xC1C00000` | `opcode_0x30` | `ll          $zero, 0x0($t6)` |
| funcs_8.c:21402 | `__OSGlobalIntMask` | `0x8003D820` | `0x43200000` | `cop0` | `.word       0x43200000                   # INVALID     $t9, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21404 | `__OSGlobalIntMask` | `0x8003D824` | `0x42A00000` | `cop0` | `.word       0x42A00000                   # INVALID     $s5, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21406 | `__OSGlobalIntMask` | `0x8003D828` | `0xC20C0000` | `opcode_0x30` | `ll          $t4, 0x0($s0)` |
| funcs_8.c:21408 | `__OSGlobalIntMask` | `0x8003D82C` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21410 | `__OSGlobalIntMask` | `0x8003D830` | `0x422AAAAB` | `cop0` | `.word       0x422AAAAB                   # INVALID     $s1, $t2, -0x5555 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21416 | `__OSGlobalIntMask` | `0x8003D83C` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:21418 | `__OSGlobalIntMask` | `0x8003D840` | `0xC0000000` | `opcode_0x30` | `ll          $zero, 0x0($zero)` |
| funcs_8.c:21422 | `__OSGlobalIntMask` | `0x8003D848` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:21424 | `__OSGlobalIntMask` | `0x8003D84C` | `0x41200000` | `cop0` | `.word       0x41200000                   # INVALID     $t1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21432 | `__OSGlobalIntMask` | `0x8003D85C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21434 | `__OSGlobalIntMask` | `0x8003D860` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21436 | `__OSGlobalIntMask` | `0x8003D864` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21438 | `__OSGlobalIntMask` | `0x8003D868` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21440 | `__OSGlobalIntMask` | `0x8003D86C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21442 | `__OSGlobalIntMask` | `0x8003D870` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21448 | `__OSGlobalIntMask` | `0x8003D87C` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:21456 | `__OSGlobalIntMask` | `0x8003D88C` | `0x42200000` | `cop0` | `.word       0x42200000                   # INVALID     $s1, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21462 | `__OSGlobalIntMask` | `0x8003D898` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21464 | `__OSGlobalIntMask` | `0x8003D89C` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21466 | `__OSGlobalIntMask` | `0x8003D8A0` | `0x43800000` | `cop0` | `.word       0x43800000                   # INVALID     $gp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21468 | `__OSGlobalIntMask` | `0x8003D8A4` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21470 | `__OSGlobalIntMask` | `0x8003D8A8` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21472 | `__OSGlobalIntMask` | `0x8003D8AC` | `0x77726C64` | `opcode_0x1D` | `.word       0x77726C64                   # INVALID     $k1, $s2, 0x6C64 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21476 | `__OSGlobalIntMask` | `0x8003D8B4` | `0x74720000` | `opcode_0x1D` | `.word       0x74720000                   # INVALID     $v1, $s2, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21481 | `__OSGlobalIntMask` | `0x8003D8B4` | `0x74720000` | `opcode_0x1D` | `.word       0x74720000                   # INVALID     $v1, $s2, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21484 | `__OSGlobalIntMask` | `0x8003D8B8` | `0x76616375` | `opcode_0x1D` | `.word       0x76616375                   # INVALID     $s3, $at, 0x6375 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21486 | `__OSGlobalIntMask` | `0x8003D8BC` | `0x756D0000` | `opcode_0x1D` | `.word       0x756D0000                   # INVALID     $t3, $t5, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21523 | `__OSGlobalIntMask` | `0x8003D904` | `0x41C80000` | `cop0` | `.word       0x41C80000                   # INVALID     $t6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21545 | `__OSGlobalIntMask` | `0x8003D930` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:21547 | `__OSGlobalIntMask` | `0x8003D934` | `0x40490FDB` | `cop0` | `.word       0x40490FDB                   # cfc0        $t1, Random # 000007DB <InstrIdType: CPU_COP0>` |
| funcs_8.c:21551 | `__OSGlobalIntMask` | `0x8003D93C` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:21567 | `__OSGlobalIntMask` | `0x8003D95C` | `0x42340000` | `cop0` | `.word       0x42340000                   # INVALID     $s1, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21569 | `__OSGlobalIntMask` | `0x8003D960` | `0x40100000` | `cop0` | `mfc0        $s0, Index` |
| funcs_8.c:21573 | `__OSGlobalIntMask` | `0x8003D968` | `0x40333333` | `cop0` | `.word       0x40333333                   # dmfc0       $s3, Wired # 00000333 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21575 | `__OSGlobalIntMask` | `0x8003D96C` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21577 | `__OSGlobalIntMask` | `0x8003D970` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:21581 | `__OSGlobalIntMask` | `0x8003D978` | `0x40666667` | `cop0` | `.word       0x40666667                   # INVALID     $v1, $a2, 0x6667 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21585 | `__OSGlobalIntMask` | `0x8003D980` | `0x40B66666` | `cop0` | `.word       0x40B66666                   # dmtc0       $s6, Status # 00000666 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21587 | `__OSGlobalIntMask` | `0x8003D984` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:21591 | `__OSGlobalIntMask` | `0x8003D98C` | `0x414CCCCD` | `cop0` | `.word       0x414CCCCD                   # INVALID     $t2, $t4, -0x3333 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21593 | `__OSGlobalIntMask` | `0x8003D990` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21595 | `__OSGlobalIntMask` | `0x8003D994` | `0x41CCCCCD` | `cop0` | `.word       0x41CCCCCD                   # INVALID     $t6, $t4, -0x3333 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21597 | `__OSGlobalIntMask` | `0x8003D998` | `0x43A00000` | `cop0` | `.word       0x43A00000                   # INVALID     $sp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21601 | `__OSGlobalIntMask` | `0x8003D9A0` | `0x74707400` | `opcode_0x1D` | `.word       0x74707400                   # INVALID     $v1, $s0, 0x7400 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21605 | `__OSGlobalIntMask` | `0x8003D9A8` | `0x73646800` | `opcode_0x1C` | `.word       0x73646800                   # INVALID     $k1, $a0, 0x6800 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21607 | `__OSGlobalIntMask` | `0x8003D9AC` | `0x73707400` | `opcode_0x1C` | `.word       0x73707400                   # INVALID     $k1, $s0, 0x7400 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21643 | `__OSGlobalIntMask` | `0x8003D9F4` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:21647 | `__OSGlobalIntMask` | `0x8003D9FC` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:21651 | `__OSGlobalIntMask` | `0x8003DA04` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:21655 | `__OSGlobalIntMask` | `0x8003DA0C` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:21659 | `__OSGlobalIntMask` | `0x8003DA14` | `0x40A00000` | `cop0` | `dmtc0       $zero, Index` |
| funcs_8.c:21669 | `__OSGlobalIntMask` | `0x8003DA28` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21673 | `__OSGlobalIntMask` | `0x8003DA30` | `0x73686C64` | `opcode_0x1C` | `.word       0x73686C64                   # INVALID     $k1, $t0, 0x6C64 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21695 | `__OSGlobalIntMask` | `0x8003DA5C` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:21699 | `__OSGlobalIntMask` | `0x8003DA64` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21701 | `__OSGlobalIntMask` | `0x8003DA68` | `0x414CCCCD` | `cop0` | `.word       0x414CCCCD                   # INVALID     $t2, $t4, -0x3333 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21703 | `__OSGlobalIntMask` | `0x8003DA6C` | `0x41400000` | `cop0` | `.word       0x41400000                   # INVALID     $t2, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21707 | `__OSGlobalIntMask` | `0x8003DA74` | `0x43A00000` | `cop0` | `.word       0x43A00000                   # INVALID     $sp, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21711 | `__OSGlobalIntMask` | `0x8003DA7C` | `0x41C80000` | `cop0` | `.word       0x41C80000                   # INVALID     $t6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21713 | `__OSGlobalIntMask` | `0x8003DA80` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21717 | `__OSGlobalIntMask` | `0x8003DA88` | `0x41B00000` | `cop0` | `.word       0x41B00000                   # INVALID     $t5, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21719 | `__OSGlobalIntMask` | `0x8003DA8C` | `0x42080000` | `cop0` | `.word       0x42080000                   # INVALID     $s0, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0_TLB>` |
| funcs_8.c:21723 | `__OSGlobalIntMask` | `0x8003DA94` | `0x40800000` | `cop0` | `mtc0        $zero, Index` |
| funcs_8.c:21729 | `__OSGlobalIntMask` | `0x8003DAA0` | `0x766F7274` | `opcode_0x1D` | `.word       0x766F7274                   # INVALID     $s3, $t7, 0x7274 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:21751 | `__OSGlobalIntMask` | `0x8003DACC` | `0x42C80000` | `cop0` | `.word       0x42C80000                   # INVALID     $s6, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21757 | `__OSGlobalIntMask` | `0x8003DAD8` | `0x40000000` | `cop0` | `mfc0        $zero, Index` |
| funcs_8.c:21759 | `__OSGlobalIntMask` | `0x8003DADC` | `0x43B40000` | `cop0` | `.word       0x43B40000                   # INVALID     $sp, $s4, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21763 | `__OSGlobalIntMask` | `0x8003DAE4` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:21767 | `__OSGlobalIntMask` | `0x8003DAEC` | `0x40200000` | `cop0` | `dmfc0       $zero, Index` |
| funcs_8.c:21771 | `__OSGlobalIntMask` | `0x8003DAF4` | `0x40400000` | `cop0` | `cfc0        $zero, Index` |
| funcs_8.c:21775 | `__OSGlobalIntMask` | `0x8003DAFC` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21777 | `__OSGlobalIntMask` | `0x8003DB00` | `0x428020CD` | `cop0` | `.word       0x428020CD                   # INVALID     $s4, $zero, 0x20CD # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:21787 | `__OSGlobalIntMask` | `0x8003DB14` | `0x45800000` | `cop1` | `.word       0x45800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:22073 | `__OSGlobalIntMask` | `0x8003DD50` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22077 | `__OSGlobalIntMask` | `0x8003DD58` | `0x42480000` | `cop0` | `.word       0x42480000                   # INVALID     $s2, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22079 | `__OSGlobalIntMask` | `0x8003DD5C` | `0x43400000` | `cop0` | `.word       0x43400000                   # INVALID     $k0, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22083 | `__OSGlobalIntMask` | `0x8003DD64` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:22085 | `__OSGlobalIntMask` | `0x8003DD68` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22089 | `__OSGlobalIntMask` | `0x8003DD70` | `0x42480000` | `cop0` | `.word       0x42480000                   # INVALID     $s2, $t0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22093 | `__OSGlobalIntMask` | `0x8003DD78` | `0x43400000` | `cop0` | `.word       0x43400000                   # INVALID     $k0, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22095 | `__OSGlobalIntMask` | `0x8003DD7C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:22097 | `__OSGlobalIntMask` | `0x8003DD80` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22103 | `__OSGlobalIntMask` | `0x8003DD8C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:22109 | `__OSGlobalIntMask` | `0x8003DD98` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22117 | `__OSGlobalIntMask` | `0x8003DDA8` | `0x41E00000` | `cop0` | `.word       0x41E00000                   # INVALID     $t7, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22121 | `__OSGlobalIntMask` | `0x8003DDB0` | `0x40B00000` | `cop0` | `dmtc0       $s0, Index` |
| funcs_8.c:22125 | `__OSGlobalIntMask` | `0x8003DDB8` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22129 | `__OSGlobalIntMask` | `0x8003DDC0` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22133 | `__OSGlobalIntMask` | `0x8003DDC8` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22137 | `__OSGlobalIntMask` | `0x8003DDD0` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22141 | `__OSGlobalIntMask` | `0x8003DDD8` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22145 | `__OSGlobalIntMask` | `0x8003DDE0` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22149 | `__OSGlobalIntMask` | `0x8003DDE8` | `0x40F00000` | `cop0` | `.word       0x40F00000                   # INVALID     $a3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22153 | `__OSGlobalIntMask` | `0x8003DDF0` | `0x41E00000` | `cop0` | `.word       0x41E00000                   # INVALID     $t7, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22157 | `__OSGlobalIntMask` | `0x8003DDF8` | `0x40F00000` | `cop0` | `.word       0x40F00000                   # INVALID     $a3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22161 | `__OSGlobalIntMask` | `0x8003DE00` | `0x41E00000` | `cop0` | `.word       0x41E00000                   # INVALID     $t7, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22165 | `__OSGlobalIntMask` | `0x8003DE08` | `0x41E00000` | `cop0` | `.word       0x41E00000                   # INVALID     $t7, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22169 | `__OSGlobalIntMask` | `0x8003DE10` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22175 | `__OSGlobalIntMask` | `0x8003DE1C` | `0x4E363420` | `opcode_0x13` | `.word       0x4E363420                   # INVALID     $s1, $s6, 0x3420 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:22187 | `__OSGlobalIntMask` | `0x8003DE28` | `0x72205631` | `opcode_0x1C` | `.word       0x72205631                   # INVALID     $s1, $zero, 0x5631 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:22191 | `__OSGlobalIntMask` | `0x8003DE30` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22195 | `__OSGlobalIntMask` | `0x8003DE38` | `0x42700000` | `cop0` | `.word       0x42700000                   # INVALID     $s3, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22197 | `__OSGlobalIntMask` | `0x8003DE3C` | `0x43400000` | `cop0` | `.word       0x43400000                   # INVALID     $k0, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22201 | `__OSGlobalIntMask` | `0x8003DE44` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:22207 | `__OSGlobalIntMask` | `0x8003DE50` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22211 | `__OSGlobalIntMask` | `0x8003DE58` | `0x40B00000` | `cop0` | `dmtc0       $s0, Index` |
| funcs_8.c:22223 | `__OSGlobalIntMask` | `0x8003DE70` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22227 | `__OSGlobalIntMask` | `0x8003DE78` | `0x45800000` | `cop1` | `.word       0x45800000                   # INVALID     $t4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP1>` |
| funcs_8.c:22229 | `__OSGlobalIntMask` | `0x8003DE7C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:22239 | `__OSGlobalIntMask` | `0x8003DE90` | `0x42FE0000` | `cop0` | `.word       0x42FE0000                   # INVALID     $s7, $fp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22241 | `__OSGlobalIntMask` | `0x8003DE94` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:22243 | `__OSGlobalIntMask` | `0x8003DE98` | `0x42FE0000` | `cop0` | `.word       0x42FE0000                   # INVALID     $s7, $fp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22245 | `__OSGlobalIntMask` | `0x8003DE9C` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:22249 | `__OSGlobalIntMask` | `0x8003DEA4` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22251 | `__OSGlobalIntMask` | `0x8003DEA8` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:22255 | `__OSGlobalIntMask` | `0x8003DEB0` | `0x42800000` | `cop0` | `.word       0x42800000                   # INVALID     $s4, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22257 | `__OSGlobalIntMask` | `0x8003DEB4` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:22265 | `__OSGlobalIntMask` | `0x8003DEBC` | `0x4F000000` | `opcode_0x13` | `.word       0x4F000000                   # INVALID     $t8, $zero, 0x0 # 00000000 <InstrIdType: CPU_NORMAL>` |
| funcs_8.c:22267 | `__OSGlobalIntMask` | `0x8003DEC0` | `0x42FE0000` | `cop0` | `.word       0x42FE0000                   # INVALID     $s7, $fp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22269 | `__OSGlobalIntMask` | `0x8003DEC4` | `0x42FE0000` | `cop0` | `.word       0x42FE0000                   # INVALID     $s7, $fp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22271 | `__OSGlobalIntMask` | `0x8003DEC8` | `0x42FE0000` | `cop0` | `.word       0x42FE0000                   # INVALID     $s7, $fp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22273 | `__OSGlobalIntMask` | `0x8003DECC` | `0x42FE0000` | `cop0` | `.word       0x42FE0000                   # INVALID     $s7, $fp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22275 | `__OSGlobalIntMask` | `0x8003DED0` | `0x42FE0000` | `cop0` | `.word       0x42FE0000                   # INVALID     $s7, $fp, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22299 | `__OSGlobalIntMask` | `0x8003DF00` | `0x43200000` | `cop0` | `.word       0x43200000                   # INVALID     $t9, $zero, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22303 | `__OSGlobalIntMask` | `0x8003DF08` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22307 | `__OSGlobalIntMask` | `0x8003DF10` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:22311 | `__OSGlobalIntMask` | `0x8003DF18` | `0x41F00000` | `cop0` | `.word       0x41F00000                   # INVALID     $t7, $s0, 0x0 # 00000000 <InstrIdType: CPU_COP0>` |
| funcs_8.c:23763 | `data_gap_8003E55C` | `0x8003E55C` | `0x10000021` | `beq` | `b           L_8003E5E4` |
| funcs_9.c:3914 | `data_gap_80040304` | `0x8004030C` | `0x1000010D` | `beq` | `b           L_80040744` |
| funcs_9.c:5895 | `spawnNpcFormationWithRandomOrientation` | `0x80040C4C` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_9.c:5916 | `spawnNpcFormationWithRandomOrientation` | `0x80040C64` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
| funcs_9.c:6005 | `spawnNpcFormationWithRandomOrientation` | `0x80040CE0` | `0x0007000D` | `break $zero,$zero,$a3` | `break       7` |
| funcs_9.c:6026 | `spawnNpcFormationWithRandomOrientation` | `0x80040CF8` | `0x0006000D` | `break $zero,$zero,$a2` | `break       6` |
