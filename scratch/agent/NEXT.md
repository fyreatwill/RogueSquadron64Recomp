# NEXT (s7620)
HYPOTHESIS-ID: g6-upstream-features

G6b steps 1-2 landed (s7618 table, s7619 controls.json: src/main/rs64_bindings_json.h, rs64_bind_load in main.cpp).
Take G6b step 3: F6 ImGui Controls panel in the RT64 overlay (find how F1 opens RT64's ImGui: grep -n "F1\|ImGui" in
src/main/*.cpp and lib/rt64/src; upstream `git show origin/main:src/input/input_bindings.cpp` F6 panel = UI reference only).
Panel: list the 14 N64 buttons + stick directions with their sources (rs64_bind_source_name), "Bind" = capture the next
pad button / axis past 16000 / key press as a new source (Shift-click or a second button = add instead of replace), "Clear",
"Reset to defaults", "Save" (rs64_bind_to_json -> controls.json; skip the write under ROGUESQ_NO_SAVE_WRITE like
audio_device.txt, log instead). The live table must become mutable (s_table is a function static const now): guard with a
mutex or swap an atomic shared_ptr; the input poll thread reads it.
Hypotheses: H-equal (panel never opened -> identical, rerun tools/test_bindings.cpp + selftest mismatches=0) vs H-drift.
Proof: same-run selftest with ROGUESQ_BIND_PANEL_TEST=1 that programmatically rebinds A->pad:b via the panel's own code path
(mismatches go >0) then Reset (back to 0 in the same run). Screenshot of the panel for the owner.
Then README Controls section + OWNER-OPT-INS. Then G6c stand-ins (design doc first).
Runtime recipe: cd build; env SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_BIND_SELFTEST=1
./RogueSquadron64Recomp rogue_squadron.z64 (50 s, SIGKILL). Offline: see the build line at the top of tools/test_bindings.cpp.
Hygiene: one game at a time; never touch build/saves or clear ROGUESQ_NO_SAVE_WRITE; never launch under lldb.
