#!/usr/bin/env python3
"""Read a runner's limit message on stdin; print the epoch second the limit
reopens, or nothing when the text states no (sane) reset time.

Formats measured in scratch/agent/loop.log:
  claude: "You've hit your session limit · resets 6pm (America/Los_Angeles)"
          "... resets 3:10pm (America/Los_Angeles)"   (next occurrence, given tz)
  codex:  "... or try again at Sep 3rd, 2026 9:24 AM."  (absolute, local tz)
"""
import re, sys, time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

text = sys.stdin.read()
now = datetime.now().astimezone()
best = None

m = re.search(r'resets?\s+(\d{1,2})(?::(\d{2}))?\s*([ap]m)(?:\s*\(([A-Za-z_/+-]+)\))?', text, re.I)
if m:
    h, mi, ap, tzname = int(m[1]), int(m[2] or 0), m[3].lower(), m[4]
    h = h % 12 + (12 if ap == 'pm' else 0)
    try:
        tz = ZoneInfo(tzname) if tzname else now.tzinfo
    except Exception:
        tz = now.tzinfo
    t = datetime.now(tz).replace(hour=h, minute=mi, second=0, microsecond=0)
    if t <= datetime.now(tz):
        t += timedelta(days=1)
    best = t

m = re.search(r'try again at\s+([A-Za-z]{3,9})\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\s+(\d{1,2}):(\d{2})\s*([AP]M)', text, re.I)
if m and best is None:
    try:
        t = datetime.strptime(f"{m[1][:3].title()} {m[2]} {m[3]} {m[4]}:{m[5]} {m[6].upper()}", "%b %d %Y %I:%M %p")
        best = t.astimezone()  # naive -> local tz
    except Exception:
        pass

if best is not None:
    secs = best.timestamp() - time.time()
    if 0 < secs <= 8 * 86400:       # past or absurdly far = not trustworthy
        print(int(best.timestamp()))
