# s4899 retrace / audio-done / synth cadence join

Instrument: `tools/apply_s4899_cadence_join.py` + `rs64_s4899_ev/vi` (src/main/upstream_compat.cpp), gate `ROGUESQ_LOG_S4899=1`. Recipe: `scratch/agent/run_s4899_cadence_join.sh` (analysis `analyze_s4899.py`). Kinds: R=recv1 (retrace q 0x80114388) return, T=recv2 (0x80128D10) return, W=audio-loop recv enter, A=audio-done q 0x80149670 return (msg byte 1), S=musyxSynthFrame entry.

```
controls: title(w1024 phase line)=1 hangar(w512)=1 pcm=10888 crash=0 abort=0
sp_enter=1263 sp_return=1263
phase pre: VIs=1  sumR=0 sumT=0 sumW=0 sumA=0 suma=0 sumS=0
   per-VI R dist: {0: 1}
   per-VI W dist: {0: 1}
   per-VI A dist: {0: 1}
   per-VI S dist: {0: 1}
   top order patterns: [('', 1)]
phase w0: VIs=1  sumR=0 sumT=0 sumW=0 sumA=0 suma=0 sumS=0
   per-VI R dist: {0: 1}
   per-VI W dist: {0: 1}
   per-VI A dist: {0: 1}
   per-VI S dist: {0: 1}
   top order patterns: [('', 1)]
phase w320: VIs=182  sumR=86 sumT=86 sumW=89 sumA=88 suma=0 sumS=84
   per-VI R dist: {0: 98, 1: 83, 3: 1}
   per-VI W dist: {0: 99, 1: 82, 7: 1}
   per-VI A dist: {0: 99, 1: 82, 6: 1}
   per-VI S dist: {0: 99, 1: 82, 2: 1}
   top order patterns: [('', 98), ('RAWTS', 81), ('RT', 1), ('RTWAWAWAWAWRAWTSRAWTS', 1), ('AWRTS', 1)]
phase w640: VIs=710  sumR=675 sumT=675 sumW=681 sumA=681 suma=0 sumS=667
   per-VI R dist: {0: 271, 1: 224, 2: 207, 3: 3, 5: 2, 6: 3}
   per-VI W dist: {0: 269, 1: 226, 2: 205, 3: 3, 4: 2, 5: 2, 6: 3}
   per-VI A dist: {0: 271, 1: 222, 2: 207, 3: 3, 4: 2, 5: 2, 6: 3}
   per-VI S dist: {0: 277, 1: 220, 2: 205, 3: 3, 5: 2, 6: 3}
   top order patterns: [('', 267), ('RAWTSRAWTS', 201), ('RAWTS', 200), ('AWRTS', 9), ('RAWT', 7), ('RAWTSR', 3)]
phase w1024: VIs=556  sumR=530 sumT=530 sumW=540 sumA=540 suma=0 sumS=526
   per-VI R dist: {0: 121, 1: 341, 2: 93, 3: 1}
   per-VI W dist: {0: 110, 1: 361, 2: 81, 3: 1, 4: 2, 6: 1}
   per-VI A dist: {0: 115, 1: 351, 2: 86, 3: 1, 4: 2, 6: 1}
   per-VI S dist: {0: 110, 1: 367, 2: 78, 3: 1}
   top order patterns: [('RAWTS', 314), ('', 104), ('RAWTSRAWTS', 74), ('AWRTS', 17), ('AWTS', 8), ('RAWTSR', 7)]
phase w512: VIs=9237  sumR=9217 sumT=9217 sumW=9224 sumA=9224 suma=0 sumS=9216
   per-VI R dist: {0: 4341, 1: 590, 2: 4294, 3: 9, 4: 3}
   per-VI W dist: {0: 4363, 1: 542, 2: 4320, 3: 7, 4: 4, 5: 1}
   per-VI A dist: {0: 4367, 1: 534, 2: 4324, 3: 7, 4: 4, 5: 1}
   per-VI S dist: {0: 4340, 1: 592, 2: 4294, 3: 8, 4: 3}
   top order patterns: [('', 4295), ('RAWTSRAWTS', 4249), ('RAWTS', 482), ('R', 38), ('AWTSRAWTS', 34), ('S', 22)]
```
