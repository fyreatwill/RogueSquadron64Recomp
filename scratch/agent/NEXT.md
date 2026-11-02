# NEXT: G3 SELECT YOUR CRAFT (hangar craft-select) retail match at RDP level, native 4:3
HYPOTHESIS-ID: g3-craftsel-rdp

State: s6785 matched ENTER NAME and the native 4:3 hangar SELECT LEVEL at RDP level (tools/g3_menu_pair.sh +
tools/g3_rdp_frame_match.py / the phase-free compare tool for animated screens). s6791 closed the craft-select camera
"fish-eye" as retail camera motion (camera words only). The craft-select screen's RDP stream (craft model, hangar
backdrop, text, cursor) has never been compared. s6800: runners use --save-dir (private EEPROM copy); no user-wide save edit.

Hypotheses: H-match (per-frame texrect/tri multisets within the same-run cross-screen control once the camera settles);
H-diff-static (a port-only/retail-only texrect or tri group on the settled screen -> name it by PRIM/coords);
H-diff-motion (differences only during the pan = camera phase, as s6791).
Discriminator: tools/g3_menu_pair.sh with VIDEO=rdplog RENV/XE RDP bins (see s6785 entry for the exact env), schedule
from s6785's SELECT LEVEL recipe plus one more Start to reach craft select (retail ~64 s, port ~42 s as s6772), settle
>=5 s, then one d-pad RIGHT pan and settle again. Score settled frames and pan frames separately; positive control =
SELECT LEVEL frames from the same run must match (s6785), cross-screen control (SELECT LEVEL vs craft-select) 0 matches.
