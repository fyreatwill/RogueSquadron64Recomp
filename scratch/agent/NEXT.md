# NEXT (s7388)
HYPOTHESIS-ID: render-to-rdram-double-pass

s7387: stripe at abort -> MISSION FAILED is repeatable at r2r=0 (off 3/3, on 0/3). Mechanism (content log, single-source): RT64's
screen-fb hash check uploads stale RDRAM at fb 0xA40000 (nz 171 per mille, 135/240 zero rows). Fix landed (r2r=0 only; CPUUP=1 = old)
but the image A/B failed its control: CPUUP=1 arms 0/3 at the lower burst capture rate.

Work unit: second line for the fix, ONE build (current), interleaved arms, NO ROGUESQ_S7387_LOG (it coincided with the lower rate).
- Hypotheses: H-fix (stale upload is the sole source: CPUUP=1 shows stripes, fix 0), H-other-source (fix arm also shows stripes ->
  another path presents RDRAM, e.g. present.storage copy for screenFb==nullptr), H-rate (control arm still 0 at full rate -> the
  instrument cannot see the frame; then add an in-process present-content check at the VI that scans 0xA40800 instead of window caps).
- Run 6 arms one at a time, cpu/skip alternating: AP=<abort route as in scratch/s7387/run3.zsh>
  `env AP=$AP SECS=190 CAP0=150 BURST=153,162 RDIR=scratch/s7388 zsh tools/s7386_route_ab.zsh cpuN "ROGUESQ_LOG_VI_STALE=1 ROGUESQ_RENDER_TO_RAM=0 ROGUESQ_R2R_CPUUP=1"`
  and skipN without CPUUP. Score: python3 tools/s7387_stripe_detect.py scratch/s7388/<arm> 140 175. Check burst caps >= 230 per arm.
- Positive control: >=2/3 cpu arms STRIPE. If 0/3 again -> H-rate: build the in-process check (log nz/zrows of the texture RT64
  presents when VI origin enters an fb that last saw a hash change) and decide from that.
- Then queue a soak (L1/L4/L12 300 s, r2r=0 + fix) and update OWNER-OPT-INS. Owner save read-only. Default unchanged.
