#!/usr/bin/env python3
"""Inject the s2879 route-source census into generated funcs_17.c."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT.parent / "N64Recomp" / "RecompiledFuncs" / "funcs_17.c"
MARK = "/* fixup: s2879 M5 route-source probe */"

HELPER = r'''
static void rs64_s2879_route_source(uint8_t* rdram, uint32_t pc,
                                    uint32_t a0, uint32_t a1,
                                    uint32_t ra) {
    static int enabled = -1;
    static unsigned long lifetime = 0;
    static unsigned long target = 0;
    if (enabled < 0) {
        const char* e = getenv("ROGUESQ_LOG_M5_ROUTE_SOURCE");
        enabled = (e && e[0] && e[0] != '0') ? 1 : 0;
    }
    if (!enabled) return;
    extern uint32_t rs64_vi_committed_width(void);
    extern uint32_t rs64_vi_committed_origin(void);
    uint32_t width = rs64_vi_committed_width();
    uint32_t origin = rs64_vi_committed_origin();
    if (lifetime < 16ul || (width == 1024u && origin == 0x00790400u) ||
        (width == 512u && origin == 0x006AB400u)) {
        if (width == 1024u && origin == 0x00790400u) ++target;
        if (width == 512u && origin == 0x006AB400u) ++target;
        fprintf(stderr, "[m5-route-source] life=%lu target=%lu pc=0x%08X "
                "width=%u origin=0x%06X a0=0x%08X a1=0x%08X ra=0x%08X\n",
                lifetime, target, pc, width, origin, a0, a1, ra);
        fflush(stderr);
    }
    ++lifetime;
}
'''

text = GEN.read_text()
if MARK in text:
    raise SystemExit("s2879 probe already present; regenerate before reapplying")

anchor = '#include "funcs.h"\n'
if text.count(anchor) != 1:
    raise SystemExit(f"include anchor count={text.count(anchor)}")
text = text.replace(anchor, anchor + HELPER + "\n", 1)

entries = {
    "runIdleFramesAndLoadSaveData": 0x8006D900,
    "applySaveSlotToMissionState": 0x8006DB2C,
    "loadDefaultHighScores": 0x8006DCCC,
    "highScoreBubbleSort": 0x8006DD50,
    "applyAccountUnlocksToSettings": 0x8006E018,
    "serializeSettingsToSaveAndPersist": 0x8006E1BC,
    "setUnlockBitAndPersist": 0x8006E360,
    "applyVolumeSettingsToMixer": 0x8006E468,
    "resetGameSettingsAndMissionStats": 0x8006E53C,
    "generateUnlockString": 0x8006E638,
    "getActiveAccountsBitmask": 0x8006E8AC,
    "getAccountUnk51": 0x8006E8BC,
    "createAccountProfile": 0x8006E8CC,
    "initPlayerMissionStateFromSettings": 0x8006E9E4,
    "initializeNumLives": 0x8006EA78,
    "loadAccountDataIntoStruct": 0x8006EAAC,
    "parseAccountDataBytes": 0x8006EB48,
    "packAccountProgressBits": 0x8006EB94,
    "getSaveScratchBufferPtr": 0x8006EC10,
    "findUnusedAccountId": 0x8006EC1C,
    "resetSettingsClearSaveAndReload": 0x8006EC8C,
    "initIdleDemoTimersAndSave": 0x8006ECD4,
    "resetMixerVolumesAndFlags": 0x8006ED50,
    "isUnlockBitSet": 0x8006ED90,
    "gatherActiveUnlockFlags": 0x8006EDB8,
    "syncMissionUnlockBitsToSettings": 0x8006EDD8,
    "unlockMissleUpgradeOnLevelCompletion": 0x8006EE14,
    "getAccountDataPtr": 0x8006EE5C,
    "copyAccountRecordAndMarkActive": 0x8006EE94,
    "clearAccountRecordAndMarkInactive": 0x8006EF2C,
    "registerSaveService": 0x8006EF98,
    "stopSaveServiceWorker": 0x8006EFDC,
    "isViModeTypePal": 0x8006F01C,
    "cycleIdleDemoId": 0x8006F044,
    "classifySaveStateFromInput": 0x8006F0B8,
    "loadSaveDataIfNotLoaded": 0x8006F10C,
    "persistSaveDataBody": 0x8006F1A8,
    "triggerSaveMessage": 0x8006F274,
    "saveServiceWorker": 0x8006F2CC,
    "isSaveStateNotPending": 0x8006F388,
    "setAccountHighscore": 0x8006F39C,
    "getAccountHighscore": 0x8006F3E8,
    "getSecondaryWeaponCount": 0x8006F43C,
}

for name, pc in entries.items():
    needle = f'RECOMP_FUNC void {name}(uint8_t* rdram, recomp_context* ctx) {{\n'
    if text.count(needle) != 1:
        raise SystemExit(f"entry anchor count for {name}={text.count(needle)}")
    call = (f'    rs64_s2879_route_source(rdram, 0x{pc:08X}u, U32(ctx->r4), '
            f'U32(ctx->r5), U32(ctx->r31)); {MARK}\n')
    text = text.replace(needle, needle + call, 1)

GEN.write_text(text)
print(f"patched {GEN} ({len(entries)} entries)")
