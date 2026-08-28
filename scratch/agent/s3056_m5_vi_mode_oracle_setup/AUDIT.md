# Session 3056 — M5 VI-mode discriminator

Date: 2026-08-28

Rebuilt the debugger-enabled mupen64plus core and oracle frontend. Retail and
port arms ran together under a 120-second watchdog. Retail used Rice, the
whole-RDRAM positive control, and the VI-register watch. The port used the
qualified LLE-only AUTOPILOT environment.

Captures: `/tmp/retail_osvisetmode_s3056_run2.log` and
`/tmp/port_osvisetmode_s3056_run2.log`.

| runtime | whole-RDRAM control | title/hangar phase | VI mode evidence |
|---|---:|---|---|
| retail | 10,000 callbacks; 15,349 total watch hits | 1024 at 17.3s; 512 at 38.4s | VI write watch attributed 640→1024 transition to `pc=0x80035798` |
| port | route controls live | no title/hangar; remained origin `0x0066A500` at width 640 | exactly four `osViSetMode` calls: 320, 2, 640, 640; zero width-1024 calls |

This selects `H-TitleOsViNotCalled` at the current port route: retail reaches
and writes the 1024 mode, while the port makes no width-1024 call. The retail
PC is a register-writer boundary, not yet a named caller; map it before
changing behavior. No behavior or mitigation changed.
