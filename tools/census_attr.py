"""Shared brace-aware function attribution for census tools (s7650 algorithm, moved here s7651).
fn_spans(lines) -> [(name, head_line, end_line)] (0-based); enclosing_braced(spans, i) -> (name, head_line) or
("UNATTRIBUTED", None). Used by s7648_mk8_census.py and s7430_file_growth.py."""
import re


# s7650: brace-aware attribution. A candidate definition head is a column-0 line naming `ident(` (return type may be on
# the previous line; one-line bodies allowed). It is a DEFINITION only if, at paren depth 0 after the head, a `{` comes
# before any `;`. Its span runs to the matching `}`. A site is attributed to the innermost span containing it; a site in
# no span (class-body inline members, unmatched heads) is UNATTRIBUTED and must be classified by hand (DIAG_SITE).
HEAD = re.compile(r'^(?:extern "C"\s+|static\s+|inline\s+|__attribute__\(\([^)]*\)\)\s+)*(?:[A-Za-z_][\w:<>\*&,\s]*?[\s\*&])?'
                  r'((?:[A-Za-z_]\w*::)*~?[A-Za-z_]\w*)\s*\(')
KW = {"if", "for", "while", "switch", "return", "sizeof", "do", "else", "case", "defined", "catch"}


def _clean(lines):
    """Blank out comments and string/char literals (keeps columns), so braces/semicolons inside them are not counted."""
    out, blk = [], False
    for l in lines:
        r, k, n = [], 0, len(l)
        while k < n:
            if blk:
                e = l.find("*/", k)
                if e < 0:
                    r.append(" " * (n - k)); k = n
                else:
                    r.append(" " * (e + 2 - k)); k = e + 2; blk = False
                continue
            c = l[k]
            if l.startswith("//", k):
                r.append(" " * (n - k)); k = n
            elif l.startswith("/*", k):
                blk = True; r.append("  "); k += 2
            elif c in "\"'":
                e = k + 1
                while e < n and l[e] != c:
                    e += 2 if l[e] == "\\" else 1
                r.append(c + " " * (min(e, n) - k - 1) + (c if e < n else "")); k = min(e + 1, n)
            else:
                r.append(c); k += 1
        out.append("".join(r))
    return out


def fn_spans(lines):
    C = _clean(lines)
    spans = []
    for j, l in enumerate(C):
        if not l or l[0].isspace() or l[0] in "#}{":
            continue
        m = HEAD.match(lines[j])  # match the raw line (cleaning blanks `extern "C"`); columns are preserved
        if not m or m.group(1).split("::")[-1] in KW:
            continue
        # find `{` before `;` at paren depth 0, starting after the head's `(`
        k, c0, par, found = j, m.end() - 1, 0, None
        while k < len(C) and k < j + 40 and found is None:
            t = C[k]
            for c in range(c0, len(t)):
                ch = t[c]
                if ch == "(":
                    par += 1
                elif ch == ")":
                    par -= 1
                elif par == 0 and ch == ";":
                    found = False; break
                elif par == 0 and ch == "{":
                    found = (k, c); break
            k, c0 = k + 1, 0
        if not found:
            continue
        k, c0, dep, end = found[0], found[1], 0, None
        while k < len(C) and end is None:
            t = C[k]
            for c in range(c0, len(t)):
                if t[c] == "{":
                    dep += 1
                elif t[c] == "}":
                    dep -= 1
                    if dep == 0:
                        end = k; break
            k, c0 = k + 1, 0
        spans.append((m.group(1).split("::")[-1], j, end if end is not None else len(C) - 1))
    return spans


def enclosing_braced(spans, i):
    best = None
    for name, a, b in spans:
        if a <= i <= b and (best is None or a >= best[1]):
            best = (name, a, b)
    return (best[0], best[1]) if best else ("UNATTRIBUTED", None)
