# M5 Session 3710 — selector input writer parity

The one-build paired port run reached title VI 1024 and hangar VI 512 in both
the real-audio and silent arms. The phase-gated source witness recorded
`0x80091CC8` writing `0x561F` to `0x80165ED0`; the `0x8009192C` load then read
`0x561F`, and the `0x80091934` caller passed that value unchanged. Source,
input, caller, and RSP positive controls all fired.

Independent retail evidence identifies the same source PC and records
`v0=0x561F` at the setup stores (`scratch/agent/s3519_selector_callsite_oracle`
and `scratch/agent/s3530_selector_input_source_oracle`). The current paired
port result therefore selects `H-SelectorInputWriterParity`, refutes
`H-SelectorInputWriterDivergence`, and refutes a stale-load explanation at
this boundary. The next boundary is the internal AI-frequency call/return
contract that supplies the setup value before `0x80091CC8`.

ORIGIN: diagnostic-only source-store, load, and caller observations. No
selector, audio, task, clear, or payload state was changed.

Evidence: `scratch/agent/s3710_m5_selector_input_writer/{real,silent}.log`,
`scratch/agent/s3530_selector_input_source_oracle/run.log`, and
`scratch/agent/s3519_selector_callsite_oracle/run.log`.
