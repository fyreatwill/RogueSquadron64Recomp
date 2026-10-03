#!/usr/bin/env python3
import os
import signal
import subprocess
import time
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = root / "scratch/agent/s3823_m5_paired_route_parity"
out.mkdir(parents=True, exist_ok=True)

binary = root / "build/RogueSquadron64Recomp"
oracle = root / "tools/oracle/build/rs64_oracle"
oracle_core = root.parent / "rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib"
oracle_rom = root.parent / "rogue_squadron64/rogue_squadron.z64"
oracle_video = Path("/opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib")

required = (binary, root / "build/rogue_squadron.z64", oracle, oracle_core, oracle_rom, oracle_video)
if not all(p.exists() for p in required):
    (out / "driver.log").write_text("prerequisite failure\n" + "\n".join(str(p) for p in required if not p.exists()))
    raise SystemExit(2)

common = {
    "ROGUESQ_LLE_FORCE": "1",
    "ROGUESQ_SPIN_YIELD": "1",
    "ROGUESQ_LLE_UNGATED": "1",
    "ROGUESQ_LLE_SOLO": "1",
    "ROGUESQ_STUB_MISSING_FUNCS": "1",
    "ROGUESQ_DRAIN_INLOOP_TICK": "1",
    "ROGUESQ_LOG_PHASE": "1",
    "ROGUESQ_LOG_AUDIO_RETURN": "1",
    "ROGUESQ_LOG_PCM_BOUNDARY": "1",
    "ROGUESQ_LOG_M5_EXACT_ROUTE": "1",
    "ROGUESQ_LOG_M5_ROUTE_WRITER": "1",
    "ROGUESQ_LOG_M5_SOURCE_WRITER": "1",
    "ROGUESQ_LOG_M5_SOURCE_TRANSITION": "1",
    "ROGUESQ_LOG_M5_FAMILY_EDGE": "1",
    "ROGUESQ_LOG_M5_SOURCE_PRODUCER": "1",
    "ROGUESQ_LOG_M5_ROUTE_ORDER": "1",
    "ROGUESQ_LOG_M5_RSP_SOURCE": "1",
    "PROBE_PHASE_WIDTH": "1024",
    "PROBE_KEYS_FROM_PHASE": "1",
    "ROGUESQ_AUTOPILOT": "6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start",
    "ROGUESQ_AUTOPILOT_STOP_WIDTH": "512",
}
press = common["ROGUESQ_AUTOPILOT"]
oracle_args = [
    str(oracle), "--core", str(oracle_core), "--rom", str(oracle_rom), "--video", str(oracle_video),
    "--secs", "45", "--watch-write", "0x0:0x800000", "--watch-write", "0x1797b0:0x179a48",
    "--hit-cap", "10000", "--watch-pc", "0x80007640", "--watch-pc", "0x8001e230", "--watch-pc", "0x8001f954",
    "--pc-phase-log-width", "0x00790400:1024", "--pc-phase-log-width", "0x006ab400:512",
    "--post-value-watch", "1", "--pc-hist-phase", "0x00790400:1024", "--pc-hist-phase", "0x006ab400:512",
    "--vi-trace", "--press", press,
]

env = os.environ.copy()
env.update(common)
port_log = (out / "port_image.log").open("w")
oracle_log = (out / "retail_oracle.log").open("w")
port = subprocess.Popen([str(binary)], cwd=root, env={**env, "ROGUESQ_AUDIO_UCODE": "1"}, stdout=port_log, stderr=subprocess.STDOUT)
retail = subprocess.Popen(oracle_args, cwd=root, env=os.environ.copy(), stdout=oracle_log, stderr=subprocess.STDOUT)
try:
    time.sleep(50)
finally:
    for proc in (port, retail):
        if proc.poll() is None:
            proc.send_signal(signal.SIGKILL)
    port.wait()
    retail.wait()
    port_log.close()
    oracle_log.close()

def count(path, marker):
    return sum(marker in line for line in path.open(errors="replace"))

port_path = out / "port_image.log"
retail_path = out / "retail_oracle.log"
for label, path, markers in [
    ("port", port_path, ["[phase]", "[audtask-dispatch]", "[m5-source-range-reader]", "[m5-exact-route-poll-control]", "[m5-family-edge-control]", "[CRASH]", "[ABORT]"]),
    ("retail", retail_path, ["watch write [0x00000000,0x00800000):", "origin=0x00790400 width=1024", "origin=0x006ab400 width=512", "[oracle] done:"]),
]:
    print(f"--- {label} ---")
    for marker in markers:
        print(f"{marker}={count(path, marker)}")
    for line in path.open(errors="replace"):
        if line.startswith("[phase]") or line.startswith("[CRASH]") or line.startswith("[ABORT]") or line.startswith("[oracle] done:"):
            print(line.rstrip())
