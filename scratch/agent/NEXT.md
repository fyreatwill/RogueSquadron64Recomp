# NEXT (s7357): idiom-class audit - class AH, unchecked I/O lengths
HYPOTHESIS-ID: host-unchecked-io-length
Context: s7356 closed class AG (unchecked alloc/open results; census tools/s7356_unchecked_census.py, runtime arm
tools/s7356_failalloc.c + tools/s7356_arms.zsh; fixed init_overlays calloc).
Idiom (class AH): in host C++ we own (src/, lib/N64ModernRuntime/{librecomp,ultramodern}/src, our lib/rt64 '+' lines), a
fread/read/pread/fseek/ftell/fgets/fwrite/write result ignored or used unchecked, so a short read (truncated ROM, partial
save file, a pipe) leaves a partly-filled buffer treated as full data, or ftell's -1 becomes a huge size.
Highest value first: ROM load (librecomp recomp.cpp / files.cpp), save/EEPROM/flash/pak read+write (eep.cpp, flash.cpp, pak.cpp,
files.cpp — the owner's real save lives in build/saves; NEVER write it: ROGUESQ_NO_SAVE_WRITE stays set; test on a COPY in a
scratch working folder), mod_manifest zip, symtab popen(nm) reader.
Hypotheses: H-safe (every default-on site checks the length), H-diag (only env-gated dumps ignore it), H-short (a default-on
reader uses a short read as full data: fix with a named error, or zero-fill + warn where retail would see 0xFF/0 for missing).
Method: tools/s7357_iolen_census.py: enumerate the call set; classify CHECKED (result compared to the requested length / <0 /
!= 1) / D / G / B / ?; reuse s7356's guard logic and MANUAL-table pattern. Controls: planted unchecked fread (B), checked twin,
gated twin. Second line: for each B, a runtime arm forcing a short read (DYLD interpose of fread/read like s7356_failalloc.c, or
a truncated COPY of the input file in a scratch dir), pre-fix vs post-fix. Then 260 s dd8 smoke:
`env SECS=260 zsh scratch/s7326/run.zsh s7357_dd8 ''`.
Exit: PORTING-STATE s7357, CURRENT-TRUTH item 27v -> closed, commit.
