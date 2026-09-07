# M5 session 3659 — byte-store evidence correction

The reported retail-versus-port nonzero memset divergence was a measurement
error. Retail ROM offset 0x84EC contains 0xA0450000 (`sb $a1, 0($v0)` at
0x800078EC). The oracle's post-value observer reads an aligned 32-bit word;
three neighboring bytes can remain nonzero after a legitimate zero byte store.

Added `post-store-scalar` counters for SB, aligned SH, and aligned SW. The
observer masks the actual guest byte lanes and compares with the source GPR
latched before execution. Unsupported instructions remain explicitly unqualified.
The core's `device/memory/memory.c:write_with_bp_checks` reports 4-byte
transactions, so the lane comes from decoded base register plus signed immediate,
not the aligned breakpoint address. A different effective word is unsupported.

Validation: oracle built with -Wall/-Wextra; byte-lane regression tests passed
under undefined-behavior sanitizer. Tests cover every SB lane, both SH lanes,
SW, unsupported/unaligned cases, and zero byte stores inside nonzero words.
Initial sandbox launch failed SDL display initialization, with zero VIs; it is
not evidence about game behavior. Retried with desktop access. The first
capture exposed lane mismatches outside lane zero; using effective addresses
fixed them. Final 60.1-second retail capture reached 3,557 VIs, including 632
at title 0x790400/1024 and 310 at hangar 0x6AB400/512.

| Watched span | memset samples | nonzero containing words | actual zero stores | actual nonzero stores | mismatches |
|---|---:|---:|---:|---:|---:|
| 0x1797B0..0x179930 | 768 | 309 | 768 | 0 | 0 |
| 0x65FA30..0x65FA4C | 1076 | 520 | 1076 | 0 | 0 |

Whole-RDRAM control: 12,776 writes; watched spans: 1,058 and 1,718 writes.
No scalar-store PC in the final capture reported a mismatch. The sampling
gate arms on title/hangar and remains armed; these are post-gate totals, not
counts restricted exclusively to the exact hangar VI. Dynamic nonzero stores
at other PCs provide an independent positive control for nonzero detection.
Logs: `scratch/agent/s3659_scalar_store/scalar-effective.log` (final),
`scalar-desktop.log` (superseded lane calculation), `scalar.log` (display failure).

The rs_zcfree audit revealed indirect zlib consumers: inflateInit2_ installs
zcfree at stream+0x24 and zcalloc at +0x20. The direct-wrapper census alone
cannot close that lifetime class. The calloc producer at 0x800052C4 is also
part of that family. M3 is not marked Complete by this session.

Outcome: H-RetailNonzeroMemset is refuted for every sampled memset store;
H-NeighborBytes explains the old nonzero word observation. Exact DMA ordering,
audio task/source ownership, and production audio remain open. The next useful
comparison must identify the live audio task and its source object before
comparing reused physical heap addresses across retail and port.

ORIGIN: no runtime mitigation or game-state change. Corrected diagnostic
interpretation of a legitimate zero byte store.
