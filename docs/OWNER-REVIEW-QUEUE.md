# Owner review queue (one sitting)

Every item below is finished on the engineering side and waits only for your hands, eyes or decision (s7762).
Run each command from the repo root; `cd build` first so the ROM sits beside the game. Base recipe for most rows:
`--preset tv` (16:9 fullscreen, FPS60, dd4) or `--preset ultrawide` (same at 21:9). Your real save is opened
read-only by the test harness only; a plain launch like these uses it normally. Full setting text: docs/OWNER-OPT-INS.md.
Paths and setting names here are checked by `python3 tools/s7762_owner_doc_check.py --controls` (rc 0 = all exist and
every setting is read by the game).

| # | What to judge | Command (from `build/`) | Before / after sheet | Your answer decides |
|---|---|---|---|---|
| 1 | **Rumble** on a PS4/PS5 pad: fire, take hits, crash | `./RogueSquadron64Recomp --preset tv` (on by default; `ROGUESQ_RUMBLE=0` off, `ROGUESQ_RUMBLE_SCALE=0.5` softer) | none (feel only) | close G6a, or report too weak / too strong |
| 2 | **F6 Controls panel** and `controls.json` | same, press **F6**; `ROGUESQ_CONTROLS_DUMP=1` prints the current map (s7765: dump, file load, round-trip and broken-file fallback verified at launch) | none | close G6b |
| 3 | **Far stand-ins** (buildings/turrets drawn early instead of popping) | `env ROGUESQ_STANDINS=1 ./RogueSquadron64Recomp --preset tv` | docs/owner_sheet_s7691_standins_on_off.jpg, docs/owner_sheet_s7748_l12_standins.jpg | close G6c; default-on at dd>1 or not |
| 4 | **Hangar lens after abort** (G5i): first entry vs re-entry after aborting a mission, scroll ships | `./RogueSquadron64Recomp --preset tv` | docs/owner_sheet_s6995_g5i_reentry.png, docs/owner_sheet_s6999_g5i_219.png, docs/owner_sheet_s6907_hangar_aim.png | close G5i / G5g |
| 5 | **Liberation of Gerrard V past half way** (G5a crash, twice before) | `./RogueSquadron64Recomp --preset tv` | none (fly it) | close G5a, or a crash report (tools/crash_reports.py picks it up) |
| 6 | **Terrain drops / far terrain** at dd2 and dd4 (G5b) | `--preset tv`, and `env ROGUESQ_DRAW_DISTANCE=2 ./RogueSquadron64Recomp --preset tv` | docs/owner_sheet_s6901_fwdwin_same_run.png, docs/owner_sheet_s7000_fwdwin_l7_same_run.png | close G5b; which dd you keep |
| 7 | **Fog on far terrain** (G5e): more haze at dd8 | `env ROGUESQ_DRAW_DISTANCE=8 ROGUESQ_DD_UNSAFE=1 ROGUESQ_DD_FOG_ALT=1,3,1 ./RogueSquadron64Recomp --preset tv` | docs/owner_sheet_s7303_l1k3_fog_tog.jpg, docs/owner_sheet_s7306_l1k3_219_fog_tog.jpg, docs/owner_sheet_s7308_dd8_horizon.jpg | DD_FOG_ALT default or not; more haze at 21:9? |
| 8 | **Knife lines** on stable frames (G5f) | `--preset tv` (fix on; `ROGUESQ_W_CLAMP=0` shows the old lines) | docs/owner_sheet_s7005_g5f.png, docs/owner_sheet_s7006_g5f_219.png, docs/owner_sheet_s6906_knife_clamp_on_off.png | close G5f |
| 9 | **Cutscene background** at dd2/dd4 (G5h) | `--preset tv`, watch mission intros and AT THE MOVIES | docs/owner_sheet_s7700_movies_dd2.jpg, docs/owner_sheet_s7701_movies_219_dd2.jpg, docs/owner_sheet_s6908_cutscene_ground.png | close G5h |
| 10 | **Factor 5 logo frames** at startup (G5d) | `--preset tv` | docs/owner_sheet_s6903_logo.png, docs/owner_sheet_s7145_logo_219.png | close G5d |
| 11 | **21:9 left-edge sliver** gone at dd>1 | `./RogueSquadron64Recomp --preset ultrawide` (`ROGUESQ_DD_FARMAX=0` = old) | docs/owner_sheet_s7310_farmax.jpg, docs/owner_sheet_s7312_farmax_l5_l12.jpg | close |
| 12 | **L15 at 21:9** re-flight (s6992) | `env ROGUESQ_FORCE_UNLOCK=1 ROGUESQ_NO_SAVE_WRITE=1 ./RogueSquadron64Recomp --preset ultrawide`, pick level index 15 (NO_SAVE_WRITE keeps the unlock out of your save) | none (fly it) | close L15 21:9 |
| 13 | **Menus / hangar at wide aspect** (G1d) | `--preset ultrawide`, walk title -> SELECT LEVEL -> hangar | scratch/s6731/sheet_menus_owner.png, docs/owner_sheet_s7144_menus_219.png | close G1d |
| 14 | **Rock-wall flashes** (opt-in near-lift) | `env ROGUESQ_S7115_NEARLIFT=1 ROGUESQ_S7115_NEARK=1.6 ./RogueSquadron64Recomp --preset tv` | docs/owner_sheet_s7116_nearlift_off.png, docs/owner_sheet_s7119_nearlift_hop.png | keep / drop / default |
| 15 | **21:9 holes in banked dives, L4 cutscene sky fill** | `--preset ultrawide` (on by default; `ROGUESQ_HORIZON_SKYFILL=0` old) | docs/owner_sheet_s7132_219_clear_holes.png, docs/owner_sheet_s7140_L4_L15_skyfill_219.png, docs/owner_sheet_s7166_L4_219_cutscene_fix.png | close |
| 16 | **Sharp picture on Retina / 4K** | `env ROGUESQ_RETINA=1 ./RogueSquadron64Recomp --preset tv` | docs/owner_sheet_s7205_retina.png | RETINA default or not |
| 17 | **Smoother under load** (all five QoS settings) | `env ROGUESQ_QOS_ALL=1 ./RogueSquadron64Recomp --preset tv` | none (feel) | QOS_ALL default or not |
| 18 | **Skip RT64's copy-back render** (~2.5 ms/frame) | `env ROGUESQ_RENDER_TO_RAM=0 ./RogueSquadron64Recomp --preset tv` | none (nothing should look different) | RENDER_TO_RAM=0 default or not |
| 19 | **Accuracy-only switches** (nothing visible): retail task addresses, late SP done, audio byte | `env ROGUESQ_S7524_V2P=1 ROGUESQ_SP_LATE=1 ROGUESQ_M5_B40_VALUE=1 ./RogueSquadron64Recomp --preset tv` | none | default or not, each |
| 20 | **FPS60 feel, turning shake, stick feel** | `--preset tv` (`ROGUESQ_STICK_GATE=0` old stick) | none (feel). Measured s7766: stick to screen 58 ms with FPS60, 75-86 ms without, 54 ms with `ROGUESQ_VI_LOCK=1` | close FPS60 / G3c / stick gate |

Not on this list on purpose: objective/win progression (your playtest, PARKED G1(d)), and anything the agent can still
measure. A crash or stall in any row: the game writes a report that `python3 tools/crash_reports.py` lists, and it
outranks all other work.
