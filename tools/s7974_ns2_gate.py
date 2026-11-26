#!/usr/bin/env python3
"""s7974 class NS-2: fresh install on a full data volume. select_rom validated rogue_squadron.z64, failed to store the copy
(ENOSPC), and the only notion of "ROM valid" / "load ROM" in librecomp was the stored copy, so main printed "Place your ROM
named 'rogue_squadron.z64'" next to that file and never booted. Fix (lib/N64ModernRuntime librecomp/src/recomp.cpp): keep
the validated bytes in memory for the session (unstored_game_roms), count them valid, load from them when the stored copy
is missing, remove any partial copy, and say why once. ROGUESQ_S7974_NOMEM=1 is the mutant restoring the old drop.
Checks: STATIC (the four code points), E2E (scratch/s7974/summary.txt from tools/s7974_ns2_e2e.zsh: ctl not full boots and
stores; full boots from memory with no prompt and no partial copy; mut and old reproduce the prompt with no boot), CONTROL
(the scorer rejects a planted summary whose full arm did not boot)."""
import os, re, subprocess
# zst-ok: reads only scratch/s7974/summary.txt (raw, small) and source files
root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
ok_all = True
def say(tag, body, ok):
    global ok_all
    ok_all &= ok; print(f"{tag} {body} {'PASS' if ok else 'FAIL'}")
def rd(p):
    try: return open(os.path.join(root, p), encoding="latin-1").read()
    except OSError: return ""
r = rd("lib/N64ModernRuntime/librecomp/src/recomp.cpp")
chk = {"mem_map": "unstored_game_roms" in r,
       "valid_from_mem": "else if (unstored_game_roms.contains(cur_rom_entry.first))" in r,
       "load_from_mem": "loading the ROM from memory" in r and "std::vector<uint8_t>(mem_it->second)" in r,
       "store_keeps": "unstored_game_roms[game_id] = std::move(rom_data);" in r,
       "partial_removed": "std::filesystem::remove(config_path / game_entry.stored_filename(), rm_ec);" in r,
       "mutant": "ROGUESQ_S7974_NOMEM" in r}
say("STATIC", " ".join(f"{k}={int(v)}" for k, v in chk.items()), all(chk.values()))
def kv(line): return dict(re.findall(r"(\w+)=(\S+)", line))
def score(text):
    arms = {}
    for ln in text.splitlines():
        m = re.match(r"(ctl|full|mut|old): (.*)", ln)
        if m: arms[m.group(1)] = kv(m.group(2))
    if set(arms) != {"ctl", "full", "mut", "old"}: return False, "arms=" + ",".join(sorted(arms))
    def i(a, k):
        try: return int(arms[a].get(k, "-1"))
        except ValueError: return -1
    base = all(arms[a].get("alive") == "alive" and i(a, "crashlines") == 0 and i(a, "imported") == 1 for a in arms)
    ctl = i("ctl", "boot_lines") > 0 and i("ctl", "place_prompt") == 0 and i("ctl", "stored_rom_size") > 0
    full = (i("full", "boot_lines") > 0 and i("full", "place_prompt") == 0 and i("full", "store_failed") == 1
            and i("full", "ns2_memload") >= 1 and arms["full"].get("stored_rom_size") == "none")
    mut = i("mut", "boot_lines") == 0 and i("mut", "place_prompt") == 1 and i("mut", "ns2_mut") == 1
    old = i("old", "boot_lines") == 0 and i("old", "place_prompt") == 1 and i("old", "ns2_store") == 0
    crash = "new_crash_reports=0" in text
    return base and ctl and full and mut and old and crash, (f"base={int(base)} ctl={int(ctl)} full_boot_mem={int(full)} "
            f"mut_prompt={int(mut)} old_prompt={int(old)} full_boot_lines={arms['full'].get('boot_lines')} ctl_boot_lines={arms['ctl'].get('boot_lines')}")
summ = rd("scratch/s7974/summary.txt")
ok, why = score(summ); say("E2E", why, ok)
plant = re.sub(r"^(full: .*?)boot_lines=\d+", r"\1boot_lines=0", summ, flags=re.M).replace("place_prompt=0 store_failed=1", "place_prompt=1 store_failed=1")
pok, pwhy = score(plant); say("CONTROL", f"planted_rejected={int(not pok)} ({pwhy})", bool(summ) and not pok)
print(f"VERDICT {'CLOSED' if ok_all else 'OPEN'}")
raise SystemExit(0 if ok_all else 1)
