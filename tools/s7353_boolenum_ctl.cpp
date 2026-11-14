// s7353 class AD UBSan control: proves the census class rules with the compiler's own checker.
// Build: clang++ -std=c++17 -O1 -fsanitize=bool,enum tools/s7353_boolenum_ctl.cpp -o /tmp/s7353_ctl && /tmp/s7353_ctl 2>&1
// Expected: exactly two runtime errors (the planted unscoped-unfixed cast "planted" and the guest byte memcpy'd into a bool),
// none for the enum class / fixed-type / masked (RC, copied verbatim from rt64_blender.h decodeInputP) / bool-conversion twins.
#include <cstdint>
#include <cstdio>
#include <cstring>
enum Mode { MODE_A, MODE_B };                       // unscoped, no fixed type: range 0..1
enum class ModeC { A, B };                          // scoped: fixed int
enum ModeF : uint32_t { F_A, F_B };                 // unscoped, fixed
struct Blender { enum InputPM { PM_CC_OR_BLENDER = 0, PM_FRAMEBUFFER_COLOR = 1, PM_BLEND_COLOR = 2, PM_FOG_COLOR = 3 };
    static InputPM decodeInputP(unsigned blenderInputs, bool secondCycle) {
        return secondCycle ? (InputPM)((blenderInputs >> 12) & 0x3) : (InputPM)((blenderInputs >> 14) & 0x3); } };
volatile uint32_t g_guest = 0xFFFFFFFFu;            // worst-case guest word
volatile uint8_t g_byte = 0x5A;                     // guest byte, not 0/1
__attribute__((noinline)) static int use_mode(Mode* m) { return *m; }
__attribute__((noinline)) static int use_bool(bool* b) { return *b ? 7 : 3; }
int main() {
    uint32_t g = g_guest; int sink = 0;
    { Mode m = static_cast<Mode>(g); sink += use_mode(&m); }                       // planted: UB (reported)
    { ModeC m = static_cast<ModeC>(g); sink += (int)m; }                            // FIXED: no report
    { ModeF m = static_cast<ModeF>(g); sink += (int)m; }                            // FIXED: no report
    { Mode m = static_cast<Mode>(g & 1); sink += use_mode(&m); }                    // RC: no report
    for (int c = 0; c < 2; c++) { Blender::InputPM p = Blender::decodeInputP(g, c); sink += p; }  // RC (real rt64 shape): no report
    { bool b = g; sink += use_bool(&b); }                                           // conversion: no report
    { bool b; uint8_t by = g_byte; std::memcpy(&b, &by, 1); sink += use_bool(&b); } // guest byte into bool: UB (reported)
    std::printf("[s7353_ctl] done sink=%d\n", sink);
    return 0;
}
