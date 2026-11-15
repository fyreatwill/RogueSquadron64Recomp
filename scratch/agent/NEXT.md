# NEXT (s7368): 0x8000E29C material NULL on the fixed TSan arm (allocateDisplayListBuffer <- allocOrEvictMaterialNode)
HYPOTHESIS-ID: tsan-arm-material-crash
Context (s7367): the guest video-ack deadlock is FIXED (ROGUESQ_CF0_DUPDROP default on). The TSan arm now gets past fs=39 and at
fs~331 / t~65 s (dd8 21:9 FPS60, scratch/s7367/fix_ab.zsh arm fix) SIGBUSes in allocateDisplayListBuffer+4792 <- allocOrEvictMaterialNode
<- findOrCreateMaterial <- emitMaterialTexturedDL, far = rdram_base + 0x80000000 (guest NULL pointer), last guest PC 0x8000E29C - the
"material noise" family filed 2x in s605-s607 (PORTING-STATE ~48000) and never chased. Single occurrence so far.
First fold soaks s7367_bootload_old / s7367_bootload_fix (SOAK-RESULTS): old FROZEN under load = owner-visible freeze confirmed fixed.
Hypotheses: H-tsan-timing (only the slowed TSan schedule reaches it: a material node freed/evicted by another guest thread between
lookup and use), H-retail (a real game NULL in the material cache eviction, reachable at retail speed only rarely), H-ours (our heap
/ spill / dd8 sizing leaves a material slot or list link NULL: check dd1 4:3 retail-settings TSan arm too).
Discriminator (one TSan build, no rebuild needed): 3 runs `env ARMS="fix:360:" zsh scratch/s7367/fix_ab.zsh` + 2 runs with
RECIPE="ROGUESQ_FPS60=0" (retail settings). Recurrence rate per arm and the guest state at the fault: disassemble funcs around
allocateDisplayListBuffer+4792 (which guest load yields NULL: list head, node->next, material table slot), then a ROGUESQ_* write watch
on that slot naming its last writer (rule 11) in the next run. Retail settings crash too -> H-ours via dd8 refuted.
Then: TSan route hangar -> mission -> abort (scratch/s7326 AP), tools/s7354_tsan_report.py (exit 1 on ? / B).
Side question still carried from s7364: what did the stale tile DRAW? WLRESET=0 vs default presented frames, phase-gated.
Exit: PORTING-STATE s7368, CURRENT-TRUTH 27zg, commit; any lib/ edit -> ./submodule-patches/export.sh first.
