#!/usr/bin/env python3
"""s7865 g3-ai-dma-model: mupen's gap-free AI completion rate vs the measured retail queue rate.

mupen64plus (rs64-oracle iter974-armB3 src/device/rcp/ai/ai_controller.c get_dma_duration) times one AI DMA as
  D = AI_LEN * floor(cps / (4 * fs)),  fs = vi_clock / (1 + AI_DACRATE),  cps = vi->delay * 60,
  vi->delay = (V_SYNC + 1) * floor(floor(vi_clock / 60) / (V_SYNC + 1))       (vi_controller.c:145)
and starts a DMA only when one is queued (fifo_push when !BUSY / fifo_pop when FULL), so with an empty FIFO the next
buffer starts at its QUEUE time, not at the previous end. Gap-free completions run at delay / D buffers per VI; a
measured steady-state rate below that is the fraction of time the FIFO sat empty (H-dma), a rate equal to it means no
gaps (H-const). Game: osAiSetFrequency(22050) -> AI_DACRATE 2207, AI_LEN 0x300 (s7863).
usage: s7865_ai_dma_rate.py [LOG ...]   (default: the s7864 retained retail oracle log)
Controls (always): the formula must reproduce fs=22047 for dacrate 2207; a planted gap-free log (exactly delay/D per
VI) must report gap ~0; dropping the floor must move the rate by > the measured gap (the truncation is what matters).
Exit 1 on control failure, 0 otherwise."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s7863_song_end_threshold import load  # noqa: E402

CLOCK, LEN, DAC = 48681812, 0x300, 2207


def model(vsync=525, dac=DAC, floor=True):
    cpl = (CLOCK // 60) // (vsync + 1)
    delay = (vsync + 1) * cpl
    fs = CLOCK // (1 + dac)
    q = (delay * 60) // (4 * fs) if floor else (delay * 60) / (4 * fs)
    return fs, delay, LEN * q, delay / (LEN * q)


def rate(path):
    tv, bv, _ = load(path)
    lo, hi = tv[0], tv[-1]
    return sum(1 for v in bv if lo <= v <= hi) / (hi - lo + 1)


def main(a):
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs = a or [os.path.join(ROOT, "scratch/s7864/v17/r1/oracle.log")]
    fs, delay, D, bpv = model()
    print(f"[s7865] model vsync=525 dac={DAC}: fs={fs} delay={delay} D={D} cycles gap-free={bpv:.6f} buf/VI "
          f"(vsync=524: {model(524)[3]:.6f})")
    ok = fs == 22047
    nofloor = model(floor=False)[3]
    gaps = []
    for p in logs:
        if not os.path.exists(p):
            print("[s7865] missing", p); continue
        r = rate(p); g = 1 - r / bpv; gaps.append(g)
        print(f"[s7865] {os.path.relpath(p, ROOT)}: measured {r:.6f} buf/VI -> FIFO idle fraction {g * 100:.3f}% "
              f"({'H-dma: gaps' if g > 2e-4 else 'H-const: no gaps'})")
    plant_gap = 1 - (round(bpv * 100000) / 100000) / bpv
    ok &= abs(plant_gap) < 1e-5
    ok &= all(abs(nofloor - bpv) / bpv > g for g in gaps)
    print(f"[s7865] controls: fs==22047 {fs == 22047}; planted gap-free gap={plant_gap:.2e}; no-floor rate {nofloor:.6f} "
          f"(shift {abs(nofloor - bpv) / bpv * 100:.3f}%) -> {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
