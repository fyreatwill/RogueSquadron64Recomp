# NEXT (s7343): idiom-class audit - class T, host fixed buffers filled with a guest-derived length
HYPOTHESIS-ID: host-fixed-buffer-guest-length
Context: s7342 closed class S (tools/s7342_addr_index_census.py: 0 default-on address-indexed tables) and with it the spill-pointer
campaign (host R M N O P S, game A-F). A different host-safety shape remains unaudited: a fixed host buffer (stack `uint8_t buf[N]`,
static array, std::array) written by memcpy / memmove / a copy loop whose length or end comes from guest data (rdram word, OSTask
field such as data_size/ucode_size/output_buff_size, DL word, SP DMA length). A larger-than-retail length (dd>1 scenes, spill-sized
DLs, a garbage word) overflows the host buffer instead of being rejected.
Hypotheses: H-capped (every such copy clamps the length to sizeof(buf) first), H-diag (uncapped copies are all in gated probes),
H-ovf (a default-on copy takes an uncapped guest length: real defect, fix with a std::min(len, sizeof buf) clamp and a log line).
Method: new tools/s7343_buffer_copy_census.py on the s7342 scope (m.HOST + EXTRA, gates via tools/s7338_mask_census.py sites()).
Enumerate fixed buffers (reuse s7342 tables(path, 1) for sizes, plus std::array<T, N>) and, per buffer, every write sink:
memcpy/memmove/memset/fread/snprintf-length/`buf[i] =` in a loop. For each, find the length expression and classify:
K constant <= size, C clamp (std::min / `if (n > sizeof) n =` / `< N` loop bound within the function), G/D/P/C as s7338,
B default-on with a length that traces to rdram / OSTask / DL (say which), ? otherwise. Controls: plant a default-on
`uint8_t b[64]; memcpy(b, rdram + a, task->data_size);` ('?'), the clamped twin ('C'), a gated twin ('G').
Runtime only if a B site exists: build the clamp, then `env SECS=260 zsh scratch/s7326/run.zsh s7343_dd8 ''` dd8 21:9 L4 and
check the clamp's log line (positive control: arm it with ROGUESQ_S7343_SELFTEST forcing len = sizeof+1 once).
Exit: PORTING-STATE s7343, CURRENT-TRUTH item 27h -> closed/fixed, commit.
