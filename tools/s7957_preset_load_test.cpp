// s7957: drives RT64 PresetLibrary<T>::load on planted preset files. Built twice by
// tools/s7957_preset_load_test.zsh: against the pre-fix header copy (control: must abort on bad json)
// and against lib/rt64/src/preset/rt64_preset.h (fix: must return false and stay alive).
#include PRESET_HDR
#include <cstdio>
namespace RT64 {
    bool PresetBase::readJson(const json &j) { enabled = j.value("enabled", true); return true; }
    bool PresetBase::writeJson(json &j) const { j["enabled"] = enabled; return true; }
    struct TP : PresetBase {};
}
int main(int argc, char **argv) {
    RT64::PresetLibrary<RT64::TP> lib;
    bool ok = lib.load(argv[1]);
    printf("RESULT ok=%d n=%zu\n", ok ? 1 : 0, lib.presetMap.size());
    return 0;
}
