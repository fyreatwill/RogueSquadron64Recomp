# M5 Session 4076 — 0x80094648 witness fix

The session-4075 retail oracle result remains valid: `0x80094648` stores
nonzero indexed channel bytes into the watched `0x141AD0..0x141AF0` span.
The paired port result did not establish that the port skipped this store.

The current generated `funcs_25.c` contains the expected sequence:

```text
0x80094640: build 0x80140000 + s1
0x80094648: sb $a2, 0x1AD8($at)
```

but it had no `rs64_s2609_m5_channel_store` call after the `MEM_B` operation.
The companion `fixup_game_funcs.py` already declared the helper, but placed
its insertion inside the broad `s2586` entry-patch guard. Once the s2586 entry
marker existed, that whole block was skipped and the indexed-store witness was
silently omitted on regeneration.

The fix adds an independent, unique-anchor insertion for the s2609 call. It is
diagnostic-only: it does not change the guest store or any audio gate. The next
qualified run must rebuild through the normal regeneration order and require
the s2609 positive control plus the existing retail whole-RDRAM/title/hangar
controls before interpreting a port null.

ORIGIN: the legitimate writer is the guest `sb` at `0x80094648`; the added
host call only observes its effective address and byte value.
