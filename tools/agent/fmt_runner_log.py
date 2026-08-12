#!/usr/bin/env python3
"""Render a runner's raw output into something readable in loop.log.

stdin -> stdout. Three shapes, detected rather than configured:

  * one JSON document  (claude/deepseek `--output-format json`) -> pretty-printed
  * JSONL event stream (`codex exec --json`)                    -> one block per event
  * anything else      (crash text, CLI warnings, grok)         -> passed through

WHY THIS IS NOT IN loop.sh's CLASSIFIER PATH: loop.sh decides "is this a usage
limit?" from the RAW runner output, and must keep doing so. If the agent's own
narrative were rendered into plain text and then pattern-matched, an iteration
that merely mentions "usage limit" would put the loop to sleep for 30 minutes —
that exact bug cost a fully successful grok iteration in s68. This script is
display only. Call it when WRITING the log, never before classifying.

Lossless by construction: command output is unescaped, not truncated, and every
event type renders something. `item.started` is the one deliberate omission —
codex emits it immediately before `item.completed` for the same id, so printing
both would double every command.
"""
import json
import sys


def _nl(s):
    return str(s).replace("\r\n", "\n").replace("\r", "\n")


def _body(text, bar="  | "):
    return [bar + line for line in _nl(text).split("\n")]


def _render(ev):
    """One event -> list of display lines. `[codex]` tags only codex-shaped
    events; anything else stays generic, because a claude/deepseek result
    object reaches this path too whenever a stderr warning line precedes the
    JSON and breaks the whole-document parse."""
    t = str(ev.get("type", ""))

    if "is_error" in ev or (t == "result" and "result" in ev):
        return json.dumps(ev, indent=2).split("\n")

    if t == "item.started":
        return []                      # always followed by item.completed

    if t == "item.completed":
        item = ev.get("item") or {}
        it = str(item.get("type", ""))
        lines = []
        if it == "command_execution":
            lines.append("[codex] $ " + _nl(item.get("command", "")).strip())
            out = item.get("aggregated_output")
            if out:
                lines += _body(out)
            rc = item.get("exit_code")
            if rc not in (None, 0):
                lines.append("[codex]   exit=%s" % rc)
        elif it == "agent_message":
            lines.append("[codex] > " + _nl(item.get("text", "")).strip())
        elif it == "reasoning":
            lines.append("[codex] ~ " + _nl(item.get("text", "")).strip())
        elif it in ("file_change", "patch_apply"):
            lines.append("[codex] edit " + json.dumps(item.get("changes", item)))
        else:
            lines.append("[codex] %s %s" % (it or "item", json.dumps(item)))
        return lines

    if "error" in t or ev.get("error"):
        return ["[runner] ERROR: " + _nl(ev.get("message") or json.dumps(ev)).strip()]

    if t in ("thread.started", "turn.started"):
        return ["[codex] --- %s ---" % t.replace(".", " ")]

    if t in ("turn.completed", "turn.failed"):
        u = ev.get("usage") or {}
        if u:
            return ["[codex] %s tokens in=%s out=%s cached=%s" % (
                t.split(".")[-1], u.get("input_tokens", "?"),
                u.get("output_tokens", "?"), u.get("cached_input_tokens", 0))]
        return ["[codex] " + t]

    return ["[runner] " + json.dumps(ev)]


def main():
    raw = sys.stdin.read()

    try:
        doc = json.loads(raw)
        print(json.dumps(doc, indent=2))
        return
    except Exception:
        pass

    out = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            out.append("")
            continue
        try:
            ev = json.loads(stripped)
        except Exception:
            out.append(line)           # plain text: CLI warnings, crash output
            continue
        if isinstance(ev, dict):
            out.extend(_render(ev))
        else:
            out.append(line)
    print("\n".join(out))


if __name__ == "__main__":
    main()
