# NEXT (s5691): who sets bool 7 in retail? (G1/G2 voice path)
Writers of the objective-bool array are enumerated (s5690). None set id 7 in our run. Work unit: static-grep RecompiledFuncs for callers/inlined sb with immediate id 7 (offset -0x7760+7 or setObjectiveBoolean(7)), list call sites and their gating conditions; discriminator = whether the site is reached in our run (use boolstore hook plus fn-entry log on the candidates) vs unreachable because of an upstream gate.
HYPOTHESIS-ID: g1-bool7-voice-path
