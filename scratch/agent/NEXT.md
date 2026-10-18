# Next work unit: split key-delivery (H2) from title->hangar regression (H1)
HYPOTHESIS-ID: m6-mission-endurance

s5415a: title reached, keys sent via winctl, hangar 0x6AB400 never appeared (nohangar-att1), modal cleared, trusted=yes.
Do in ONE run: at title, send a key and log an in-process SDL key event witness (one-line SDL_KEYDOWN log in the input path; positive control = it fires for a winctl key) AND watch whether any phase/origin changes. If SDL sees keys but no hangar -> H1 (regression; bisect via the s5374 deltas). If SDL sees nothing -> H2 (focus/keycode; try CGEventPost or osascript keystroke).
