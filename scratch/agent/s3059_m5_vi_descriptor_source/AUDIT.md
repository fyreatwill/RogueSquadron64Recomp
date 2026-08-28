# Session 3059 audit — VI descriptor source behind `applyPendingViChanges`

## Static data flow

`applyPendingViChanges` at `0x8001B7F0` forms the four-record table base as
`0x80130000 - 0x72B0 = 0x80128D50`. Its direct callsite at `0x8001B8DC`
passes the selected record unchanged to `osViSetMode`.

The selector logic chooses one of four records at offsets `0x00`, `0x50`,
`0xA0`, and `0xF0`: `0x80128D50`, `0x80128DA0`, `0x80128DF0`, and
`0x80128E40`. The width-bearing field is offset `+8`.

Retail ground truth from session 3058 attributed the title's 1024-capable
request to `0x8001B8DC`. The mode pointer was `0x80128DA0` (table offset
`0x50`). The same-build port capture submitted `0x80128DF0` at width 640,
not the retail-selected `0x80128DA0` record.

## Writers and mapping

`initVideoSubsystem` is the writer for the four RAM records. Its loop at
`0x8001B680–0x8001B6D4` copies four 16-byte chunks per record from the local
four-record staging area into `0x80128D50 + {0x00,0x50,0xA0,0xF0}`. Its
earlier setup fills that staging area from the video-mode inputs. No direct
writer to the active record is present in `applyPendingViChanges`; it only
selects and consumes a record.

The generated function body, project symbol table, and companion symbol file
agree on `applyPendingViChanges = 0x8001B7F0`, its `0x8001B8DC` callsite, and
the four-record selection/copy structure. The port callsite passes the
selected pointer unchanged to `osViSetMode`; no host-side pointer adjustment
was found in the inspected path.

## Result

This selects **H-SourceSelection** for the current capture: the record writer
and generated mapping exist, but the port reaches a different legitimate
record before the direct call. It rejects **H-SourceWriter** and
**H-SourceAlias** at this boundary. The selector-state producer remains open;
no behavior change is justified.
