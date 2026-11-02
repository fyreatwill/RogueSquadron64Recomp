# NEXT: passcode Concert Hall (screen 10) RDP compare + song-worker runtime (G3)
HYPOTHESIS-ID: g3-concert-hall

Done s6785: ENTER NAME 235/236 exact; native 4:3 hangar H-match via tools/g3_rdp_phase.py (static 53/53, tris ratio 1.003).
Last undriven front-end screen: screen 10, the MAESTRO passcode "Concert Hall" (s6784: the only screen that runs the
song-load worker; its H-disjoint verdict is single-source static + runtime null).
Unit (no build):
1. Route: title START/OPTIONS (17:down,19:a) -> OPTIONS -> PASSCODES (map in PORTING-STATE s6783 "Menu map"), then type
   MAESTRO on the letter wheel (d-pad left/right + a per letter; find the wheel order from the ENTER NAME capture
   scratch/s6785/name/port/w_0079.94.png, then ENTER). Port first with window captures (tools/g3_port_capture.sh, AP
   schedule) to confirm the route, then the pair run with OFF tuned so the retail presses land on the same letters.
2. Arm the s6784 marks on both arms (song 800C3B38/800C5880/800C3B4C/800C3B54 + image 800B380C/800B3FA0/800B4004 as
   the positive control; spec in the s6784 entry) and RDP-dump both.
3. Score with tools/g3_rdp_frame_match.py, plus tools/g3_rdp_phase.py (3D scene, expect animation phase).
Hypotheses: H-match (same static set, tri distribution within a few %) vs H-diff (name the writer); song marks fire in
both arms with no image job in flight (confirms H-disjoint at runtime) vs an image mark interleaves (reopens s6784).
If the passcode cannot be typed in by schedule after 2 tries, close the front-end and take the next ladder rung.
