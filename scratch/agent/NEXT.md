# NEXT: (after the Step-0 maintenance compaction CURRENT-TRUTH now triggers, 60051 B) G1d wide-width fixed-epsilon idiom audit
HYPOTHESIS-ID: g1d-wide-epsilon-audit

Why: s6844 (12-bit lr.x overflow at 1024), s6845 (HUD anchor on a full-screen sprite) and s6846 (initHudStruct
`ox <= -W/2 + 1` fixed 1 px epsilon vs a W*0.001 residual) are all one class: retail arithmetic on the screen width W that
is safe for W <= 640 and breaks at G1d W = 1024. Instead of waiting for the next owner-visible transition defect, enumerate
the class once (s282-s288 model).

Method (offline first, one build at most):
1. grep RecompiledFuncs for every read of the screen width: screen struct +0x10 via the s4 screen pointer pattern
   (`lw $v0, 0x0($s4)` / `lw ..., 0x10($v0)`), 0x8011A838 (`-0x57C8(` with lui 0x8012; 19 sites), and the viewport width
   words used by G1d (src/main/main.cpp rs64_g1d_*). For each, follow the value to a compare (c.le.s/c.lt.s/slt/sltiu) or
   a 10.2 / 12-bit pack (sll 2 + andi 0xFFF), and classify: (a) compare against W-derived +/- small constant (epsilon
   idiom, like 0x800C1A9C), (b) packed into an RDP 12-bit field (overflow idiom, like s6844), (c) safe (scales cleanly).
2. For each (a)/(b) site reachable in play, say whether W=1024 can flip it; fix via a tools/apply_s68xx_*.py with a
   =0 switch and keep W <= 640 bit-identical.
3. Runtime witness only for sites that flip: one build, 21:9 route (scratch/s6846/port_abort.sh or scratch/s6731/menus.sh),
   same-build A/B.
Expected outcomes: 0 further flipping sites -> class CLOSED with the census table; N sites -> fixes + A/B.
Budget 2 iterations, then G3c/G1d owner-judgement items or the next ladder rung.
