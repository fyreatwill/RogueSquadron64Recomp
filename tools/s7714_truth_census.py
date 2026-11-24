#!/usr/bin/env python3
"""s7714 truth census: one ROGUESQ_X read at several sites that disagree on what a value MEANS as on/off.

s7713 closed the numeric-clamp half of the multi-reader class. This closes the boolean half, statically:
  (a) UNSET   one site is default-on  `!(e && *e == '0')`, another default-off `e && *e != '0'`;
  (b) VALUE   sites disagree on which set values are truthy: `*e == '1'` vs `*e != '0'` (=2 / =yes / =t split),
              `atoi(e)` vs `*e != '0'` (=yes / =t split), strcmp(e, "1") vs `*e != '0'`, ...
Per reader site (tools/s7711_optval_census.py finder + its helper readers) the C around the getenv is tokenised and
parsed (a small C expression parser); the expression that decides on the variable is isolated: the lowest AST node
holding every use of the variable, climbed through ! && || compares casts derefs and string/number parsers, NOT through
an operand on another variable (s7713's 16 heuristic false flags were exactly that). Conjuncts/disjuncts on other
variables evaluate to the neutral element (&& -> true, || -> false), so `f && *f != '0' && !(d && *d == '0')` is
judged on f alone. A receiving variable (`const char* e = getenv(..)`) is followed through the next statements of its
block, including `if (C) return X;` early-return chains. The isolated expression is evaluated for the variable unset
and set to "0", "1", "2", "t", "yes" with C semantics (short-circuit, atoi/strtol/atof prefix parse, strcmp family).
A value the site cannot decide (a foreign operand decides it, an opaque call) is '?', never a disagreement.
SPLIT = two modelled sites of one name give different on/off for some value. REVIEWED = hand-read, deliberate.
s7728 LOG_ALL pass: the catch-all ROGUESQ_LOG_ALL is a foreign operand above (neutral), so a name whose host readers
disagree on it (env_flag / a `getenv("ROGUESQ_LOG_ALL")` within 5 lines before .. 3 after the site honours it; the rest
do not) was invisible: LOG_ALL=1 lit half a probe. Host readers only (src/, lib/): generated-code probes come from
fixup/apply strings and read only their own flag unless stated (docs/debug-trace-env-vars.md).

s7733: a reader site inside an apply/fixup script whose C text is not in the compiled tree (../N64Recomp/RecompiledFuncs,
build/factor5_ucode, RecompiledPatches, src, include) is DEAD: a replace anchor, or a step whose anchor matches nothing
now. It is dropped before modelling; --dead lists them. 3 REVIEWED splits (OVL2C_DROP, M5_B40_VALUE, S4562_PAUSE) were
dead text only.
Exit 0 = no unreviewed SPLIT; 1 = splits; 2 = control failure.
--controls: (1) planted default-on vs default-off pair must SPLIT on unset; (2) planted `*e == '1'` vs `*e != '0'`
pair must SPLIT on "2"; (3) FPS60's real readers must AGREE with >= 4 modelled sites; (4) the pre-s7714 vendored
AUDIO_UCODE m5 label text (`audio && audio[0] && audio[0] != '0'` -> audio_on, i.e. unset = audio_stub) planted back
must SPLIT against main.cpp/rsp.cpp (unset = real ucode); (5) a site guarded by another variable (`x && e && *e`)
must evaluate on e alone (unset off, "1" on); (6) a C++17 `if (const char* e = getenv(X); e && ..)` site is modelled.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import s7711_optval_census as c7711

ROOT = c7711.ROOT
VALUES = (None, "0", "1", "2", "t", "yes", "false", "no", "", "off", "on", "true", " 1", "1 ")  # s7731: + off/on/true/whitespace; s7728: + false/no; s7730: + "" (empty shell value)
VNAME = {None: "unset", "": "empty"}

# name -> reason. Each entry read by hand at s7714.
REVIEWED = {
    "ROGUESQ_BIND_PANEL_TEST": "=2 is the save-bound round-trip variant of the test (s7666); rs64_bind_flag reads 2 as on too",
    "ROGUESQ_DD_WIDEWIN": "deliberate mode word: upstream_compat.cpp:399 recognises only 'tog3' (3-way toggle); every reader "
                          "reads tog3 as on (s6919-style mode letters)",
    "ROGUESQ_DRAIN_INLOOP_TICK": "main.cpp rs64_m5_apply_drain_tick_policy tests presence only to write the default '0' when "
                                 "unset (auto-default guard, s7711 PRESENCE class); the one reader is `*e == '1'`",
    "ROGUESQ_G1D_SPRITE_DIAG": "level digits: dpc_bridge.cpp:5821 logs the extra detail only at =1/=2; =t/=yes arm the base diag",
    "ROGUESQ_LOG_G1D_RECT": "level digits: =1 rect log, =2 rect + pointer dump (dpc_bridge.cpp:5614/5705); base gate is non-'0'",
    "ROGUESQ_RETAIL_SNAP": "level digits (s7891/s7892): any non-0 arms the =1 EL/VD pin (apply_s7839_snaplog.py:14); =2/=3 alone select the sub-VI variants at :28, t/yes/on read as =1",
    "ROGUESQ_S7524_V2P": "mode word: =alt (s7526) is on at main.cpp (non-'0') and selects the twin digest in s7526_v2p_twin.cpp",
    "ROGUESQ_PRESENT_EARLY_FORCE": "three gates of one fix: only the fb-upload gate (rt64_state.cpp:3828) defaults ON (session 21 "
                                   "comment: the 1024-wide phase must present); history-push and consumer gates stay opt-in; "
                                   "=1 arms all three, =0 the default one off. Owner default, never flip",
    "ROGUESQ_VI_EXTENT_PROBE": "rt64_state.cpp:3729 `e[0] == '2'` (dedupe mode) runs only inside `if (s_viext ...)`, the "
                               "presence gate on the line above: guarded deref, =2 is a mode",
    "ROGUESQ_HLE_TRI_AB": "RT64 HLE F3DFactor5 op map (rt64_gbi_f3dfactor5.cpp:1195 presence) is never reached: the port runs "
                          "the gfx ucode LLE; diag, no documented =0",
    "ROGUESQ_LOG_S4298": "diag log only (pi.cpp presence vs rt64 non-'0'); no documented =0",
    "ROGUESQ_LOG_MTM": "diag watches injected by s577x apply scripts (presence `e && e[0]`) vs non-'0'; no documented =0",
    "ROGUESQ_DD_OFFMAPCULL": "numeric radius R (upstream_compat.cpp:241: 't' = tog3 mode, else atoi(o); =-1 off) and main.cpp "
                             "14418 is the presence guard of the s7037 auto-default (`!getenv` -> setenv 2): not an on/off pair",
    "ROGUESQ_PLAYER_DUMP": "diag: main.cpp levels '1'/'2'; s5866/s5867 apply-script watches arm on any value",
}

# s7729: every unmodelled reader site, read by hand and classed (none disagrees with its name's other readers):
#   STRING   value is a path / number / mode string handed on (fopen, atof, strcmp table), not a truth test
#   REWRITER Python text that is a search anchor or replacement inside an apply/fixup script, not a live reader;
#            the reader it produces is modelled where it lands
#   MULTI    one gate over several env names (LOG_ALL || own, TRIM=0 || own, K override, dd>1 && own);
#            each name's own term was read and matches that name's other readers
#   GUARD    an early-return presence/non-'0' gate (`if (!e || !*e) return;`) the parser does not take as a decision;
#            it reads the same as the name's other readers on every census value
# key: (name, rel, fragment that must occur on the site's line). A site matching none is UNCLASSIFIED and fails.
UNMODELLED_CLASS = {
    "STRING": "path / number / mode string handed on, not a truth test",
    "REWRITER": "apply/fixup script anchor text, not a live reader",
    "MULTI": "multi-name gate; own term read by hand, agrees",
    "GUARD": "early-return gate the parser misses; agrees by hand",
}
S, R, M, G = "STRING", "REWRITER", "MULTI", "GUARD"
UNMODELLED_T = [
("ROGUESQ_ASPECT","src/main/main.cpp","as = std::getenv(\"ROGUESQ_ASPECT\");",S),
("ROGUESQ_ASPECT","src/main/rt64_render_context.cpp","vi_shape ? nullptr",S),
("ROGUESQ_ASPECT","src/main/rs64_settings.cpp","const char* a = std::getenv(\"ROGUESQ_ASPECT\");",S),  # s7732 launch validator
("ROGUESQ_ASPECT","tools/apply_s6031_far.py","const char* as = getenv",S),
("ROGUESQ_ASPECT_SCALE","src/rsp/dpc_bridge.cpp","ROGUESQ_G1D_PAUSE_DIM",S),
("ROGUESQ_ASPECT_SCALE","tools/apply_s6144_fpx.py","kx6144",S),
("ROGUESQ_ASPECT_SCALE","tools/apply_s6294_edgewriter.py","const char* a = getenv",S),
("ROGUESQ_CONTROLS","src/main/main.cpp","e && *e) return e;",S),
("ROGUESQ_DD_FOGCULL","src/main/upstream_compat.cpp","g_rs64_s7030 = [",M),
("ROGUESQ_DD_OFFMAPCULL","src/main/upstream_compat.cpp","g_rs64_s7030 = [",M),
("ROGUESQ_DD_WIDEWIN_CAP","src/main/upstream_compat.cpp","static const Cfg cfg",S),
("ROGUESQ_DRAW_DISTANCE","src/main/main.cpp","num(e, v) && v > 4.0",S),
("ROGUESQ_DRAW_DISTANCE","src/main/upstream_compat.cpp","ROGUESQ_G5E_FOGP",S),
("ROGUESQ_DRAW_DISTANCE","src/rsp/dpc_bridge.cpp","ROGUESQ_DD_SKYZ",M),
("ROGUESQ_FB_WIDTH","src/main/main.cpp","ROGUESQ_DD_PX8_AUTO",S),
("ROGUESQ_FLOOR_DEPTH_DIR","lib/rt64/src/render/rt64_framebuffer_renderer.cpp","const char *d = std::getenv",S),
("ROGUESQ_FLOOR_PIPE_DIR","lib/rt64/src/render/rt64_native_target.cpp","floorDir = std::getenv",S),
("ROGUESQ_FLOOR_PIPE_DIR","lib/rt64/src/render/rt64_native_target.cpp","std::string(std::getenv(\"ROGUESQ_FLOOR_PIPE_DIR\"))",S),
("ROGUESQ_FLOOR_SHADER_DIR","lib/rt64/src/render/rt64_framebuffer_renderer.cpp","floorDir = std::getenv",S),
("ROGUESQ_FL_ZERO_ADDR","src/main/main.cpp","getenv(\"ROGUESQ_FL_ZERO_ADDR\") ?",S),
("ROGUESQ_FS_SLOT_ADDR","src/main/main.cpp","getenv(\"ROGUESQ_FS_SLOT_ADDR\") ?",S),
("ROGUESQ_FORFACE_LOG","tools/apply_s6518_ret_summary.py","ROGUESQ_FORFACE_LOG",R),
("ROGUESQ_G1D_PAUSE_DIM","src/rsp/dpc_bridge.cpp","ROGUESQ_G1D_PAUSE_DIM",M),
("ROGUESQ_G1D_RECT_WRAP","src/rsp/dpc_bridge.cpp","ROGUESQ_G1D_RECT_WRAP",M),
("ROGUESQ_G1E_CDIAG","src/rsp/dpc_bridge.cpp","s_cdiag_tally",M),
("ROGUESQ_G1E_TRIM","src/main/upstream_compat.cpp","s7446_log",M),
("ROGUESQ_G1E_TRIM","src/rsp/dpc_bridge.cpp","s_cdiag_tally",M),
("ROGUESQ_G1E_TRIM","tools/apply_s5835_sphere_probe.py","rs7441_on",M),
("ROGUESQ_G1E_TRIM","tools/apply_s5908_callers.py","static int on = -1",M),
("ROGUESQ_G1E_TRIM","tools/apply_s7445_burst_latch.py","on_ = -1",M),
("ROGUESQ_G5H_BAND","src/rsp/dpc_bridge.cpp","s_bd = [",S),
("ROGUESQ_HUDPTRWATCH","tools/apply_s6595_hudptrread.py","const char* e = getenv",G),
("ROGUESQ_LOG_ALL","src/main/main.cpp","const char* all = std::getenv",M),
("ROGUESQ_LOG_ALL","src/main/upstream_compat.cpp","const char* all = std::getenv",M),
("ROGUESQ_LOG_ALL","src/rsp/dpc_bridge.cpp","const char* all = std::getenv",M),
("ROGUESQ_LOG_ALL","tools/apply_s4159_m5_preclear_span_census.py","ROGUESQ_LOG_M5_PRECLEAR_SPAN",M),
("ROGUESQ_LOG_F5_STORE_SHADOW","src/rsp/dpc_bridge.cpp","const char* e = std::getenv",M),
("ROGUESQ_LOG_HITS","tools/apply_s5834_seg_dump.py","e[0] == '1')) return;",G),
("ROGUESQ_LOG_HITS","tools/apply_s5835_sphere_probe.py","rs7441_on",M),
("ROGUESQ_LOG_HITS","tools/apply_s5908_callers.py","static int on = -1",M),
("ROGUESQ_LOG_M5_EXACT_ROUTE","src/main/main.cpp","const char* own = std::getenv",M),
("ROGUESQ_LOG_M5_ROUTE_STATE","src/main/upstream_compat.cpp","const char* own = std::getenv",M),
("ROGUESQ_LOG_S4299","tools/apply_s4569_nodecopy_watch.py","rs64_s4299_store_watch",R),
("ROGUESQ_LOG_S4526","tools/apply_s4527_holder_poll.py","ROGUESQ_LOG_S4526",R),
("ROGUESQ_LOG_SLOT_DISPATCH","tools/apply_s6942_envcache.py","ROGUESQ_LOG_SLOT_DISPATCH",R),
("ROGUESQ_M5_B40_VALUE","src/main/upstream_compat.cpp","const char* b40 = std::getenv",S),
("ROGUESQ_M5_B40_VALUE","tools/fixup_live_replay.py","getenv(\"ROGUESQ_M5_B40_VALUE\")[0]",R),
("ROGUESQ_M5_C88_VALUE","src/main/upstream_compat.cpp","const char* c88 = std::getenv",S),
("ROGUESQ_PANEL_TEST_WINDOW","src/main/main.cpp","static const char* e = std::getenv",G),
("ROGUESQ_PRESENT_QOS","src/main/main.cpp","ROGUESQ_UPLOAD_QOS",S),
("ROGUESQ_RUMBLE_TEST","src/main/main.cpp","const char* e = getenv",G),
("ROGUESQ_S7064","src/main/upstream_compat.cpp","fopen(getenv(\"ROGUESQ_S7064\")",S),
("ROGUESQ_S7103_CAMFIX","tools/apply_s7111_camfixk.py","ROGUESQ_S7103_CAMFIX",R),
("ROGUESQ_S7106_RSPTRI","src/rsp/s7106_rsptri.cpp","const char* e = getenv",S),
("ROGUESQ_S7317_ALLOCMAP","src/rsp/s7324_rcp_spill.cpp","getenv(\"ROGUESQ_S7317_ALLOCMAP\") ?",S),
("ROGUESQ_S7317_ALLOCMAP","src/rsp/s7331_reset_writer.cpp","getenv(\"ROGUESQ_S7317_ALLOCMAP\") ?",S),
("ROGUESQ_S7872_SNAP_WIN","tools/apply_s7872_snapwin.py","w7872 = 0;",S),  # s7875: lo:hi:el window list for sscanf, not a truth test
("ROGUESQ_S7324_RCPREF","src/rsp/s7331_reset_writer.cpp","getenv(\"ROGUESQ_S7324_RCPREF\") ?",S),
("ROGUESQ_S7523_SLOWRDP","src/rsp/s7523_slow_rdp.cpp","const char* e = getenv",S),
("ROGUESQ_SLOT_DISPATCH_PHASE_MIN","tools/apply_s6942_envcache.py","ROGUESQ_SLOT_DISPATCH_PHASE_MIN",R),
("ROGUESQ_TBLNULL_LOG","tools/apply_s6037_ddclamp.py","dl = getenv(\"ROGUESQ_TBLNULL_LOG\") ? 1 : 0",G),
("ROGUESQ_TELE_BOLT","tools/apply_s5835_sphere_probe.py","rs7441_on",M),
("ROGUESQ_UPLOAD_QOS","src/main/main.cpp","ROGUESQ_UPLOAD_QOS",S),
("ROGUESQ_WL_QOS","src/main/main.cpp","ROGUESQ_UPLOAD_QOS",S),
]


def classify_unmodelled(name, site, texts=None):
    rel, ln = site.rsplit(":", 1)
    lines = (texts or {}).get(rel) or open(os.path.join(ROOT, rel), errors="replace").read().split("\n")
    line = lines[int(ln) - 1] if 0 < int(ln) <= len(lines) else ""
    for i, (n, r, frag, cls) in enumerate(UNMODELLED_T):
        if n == name and r == rel and frag in line:
            return i, cls
    return None, None


# ---------------------------------------------------------------- tokenizer
TOK = re.compile(r"""
 (?P<ws>\s+|//[^\n]*|/\*.*?\*/)
|(?P<str>"(?:\\.|[^"\\\n])*")
|(?P<chr>'(?:\\.|[^'\\\n])+')
|(?P<num>0[xX][0-9a-fA-F]+[uUlL]*|(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?[fFuUlL]*)
|(?P<id>(?:::)?[A-Za-z_]\w*(?:::[A-Za-z_]\w*)*)
|(?P<op><<=|>>=|->|\+\+|--|<=|>=|==|!=|&&|\|\||<<|>>|\+=|-=|\*=|/=|\|=|&=|\^=|%=|[-+*/%<>=!~&|^?:;,.(){}\[\]#@\\`$])
""", re.X | re.S)


def tokenize(s):
    out, i = [], 0
    while i < len(s):
        m = TOK.match(s, i)
        if not m:
            out.append(("op", s[i])); i += 1; continue
        i = m.end()
        k = m.lastgroup
        if k != "ws":
            out.append((k, m.group(k)))
    return out


PYESC = {"n": "\n", "t": "\t", "r": "", "0": ""}
TQ2, TQ1 = '"' * 3, "'" * 3
PYTOK = re.compile(r"#|([rRbBuUfF]{0,2})(" + TQ2 + "|" + TQ1 + r"""|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')""")


def py_unescape(body, raw):
    if raw:
        return body
    return re.sub(r"\\(.)", lambda m: PYESC.get(m.group(1), m.group(1)), body)


def py_c_text(lines):
    """C embedded in Python source (s7715): per line, the concatenated bodies of EVERY Python string literal on it
    (assignment prefixes, mid-line `text.replace(OLD, ("..."` calls, `'..' + MARK + '..'` all count), unescaped once
    (\\" -> ", \\' -> ', \\n -> newline, \\\\ -> \\). Inside a triple-quoted block the block text is the C.
    s7714 only stripped a quote that STARTED the line, so 93 multi-reader sites read as "no call".
    Call it on the WHOLE file: triple-quote state carries across lines, and one line may toggle it several times
    (`rep(<TQ>a<TQ>, <TQ>b` with TQ a triple quote). Python code and `#` comments outside strings are dropped; one output line per input line."""
    out, tri, raw = [], None, False
    for l in lines:
        pos, pieces = 0, []
        while pos < len(l):
            if tri:
                k = l.find(tri, pos)
                pieces.append(py_unescape(l[pos:] if k < 0 else l[pos:k], raw))
                if k < 0:
                    break
                pos, tri = k + 3, None
                continue
            m = PYTOK.search(l, pos)
            if not m or m.group(0) == "#":
                break
            pre, q = (m.group(1) or "").lower(), m.group(2)
            if q in (TQ2, TQ1):
                tri, raw, pos = q, "r" in pre, m.end()
            else:
                pieces.append(py_unescape(q[1:-1], "r" in pre))
                pos = m.end()
        out.append(" ".join(pieces))
    return out


# ---------------------------------------------------------------- parser
class PErr(Exception):
    pass


BIN = {"||": 4, "&&": 5, "|": 6, "^": 7, "&": 8, "==": 9, "!=": 9, "<": 10, ">": 10, "<=": 10, ">=": 10,
       "<<": 11, ">>": 11, "+": 12, "-": 12, "*": 13, "/": 13, "%": 13}
ASSIGN = {"=", "+=", "-=", "*=", "/=", "|=", "&=", "^=", "%=", "<<=", ">>="}
TYPEW = {"const", "unsigned", "signed", "char", "int", "bool", "double", "float", "long", "short", "size_t", "void",
         "uint8_t", "uint16_t", "uint32_t", "uint64_t", "int8_t", "int16_t", "int32_t", "int64_t", "volatile", "auto",
         "static", "uintptr_t", "intptr_t"}
HELPERS = {"rs64_env_int", "s6919_mode", "rs64_bind_flag", "env_on", "env_flag", "rs64_s7355_env_is"}


class P:
    def __init__(self, toks, name, gv=None):
        self.t, self.i, self.name, self.gv = toks, 0, name, gv

    def peek(self, k=0):
        j = self.i + k
        return self.t[j] if j < len(self.t) else ("eof", "")

    def take(self, v=None):
        tk = self.peek()
        if v is not None and tk[1] != v:
            raise PErr(f"want {v} got {tk}")
        self.i += 1
        return tk

    def expr(self, minp=0, comma=False):
        a = self.unary()
        while True:
            k, v = self.peek()
            if k != "op":
                return a
            if v == "?" and minp <= 3:
                self.take()
                b = self.expr(0)
                self.take(":")
                c = self.expr(3)
                a = ("tern", a, b, c)
                continue
            if v in ASSIGN and minp <= 2:
                self.take()
                a = ("asg", v, a, self.expr(2))
                continue
            if v == "," and comma and minp <= 1:
                self.take()
                a = ("comma", a, self.expr(2, comma=True))
                continue
            p = BIN.get(v)
            if p is None or p < minp or p <= minp - 1:
                return a
            if p < max(minp, 1):
                return a
            self.take()
            a = ("bin", v, a, self.expr(p + 1))

    def is_cast(self):
        j, words = self.i + 1, 0
        while j < len(self.t) and (self.t[j][1] in TYPEW or self.t[j][1] == "*" or
                                   (self.t[j][0] == "id" and self.t[j][1].endswith("_t"))):
            words += self.t[j][1] != "*"
            j += 1
        return words > 0 and j < len(self.t) and self.t[j][1] == ")", j

    def unary(self):
        k, v = self.peek()
        if k == "op" and v in ("!", "-", "+", "~", "*", "&"):
            self.take()
            return ("un", v, self.unary())
        if k == "op" and v in ("++", "--"):
            self.take()
            return ("un", v, self.unary())
        if k == "id" and v == "sizeof":
            self.take()
            return ("num", 8, self.unary())[:2]
        if k == "op" and v == "(":
            ok, j = self.is_cast()
            if ok:
                self.i = j + 1
                return ("cast", self.unary())
        return self.postfix(self.primary())

    def primary(self):
        k, v = self.take()
        if k == "E":
            return ("E",)
        if k == "num":
            s = v.rstrip("uUlLfF") if not v.lower().startswith("0x") else v.rstrip("uUlL")
            try:
                return ("num", int(s, 0) if re.fullmatch(r"0[xX][0-9a-fA-F]+|[0-9]+", s) else float(s))
            except ValueError:
                return ("num", float(s.rstrip("fF")))
        if k == "str":
            s = v[1:-1]
            while self.peek()[0] == "str":  # adjacent literal concatenation
                s += self.take()[1][1:-1]
            return ("str", bytes(s, "utf-8").decode("unicode_escape"))
        if k == "chr":
            return ("num", ord(bytes(v[1:-1], "utf-8").decode("unicode_escape")[0]))
        if k == "id":
            if v in ("std::getenv", "getenv", "::getenv") and self.peek()[1] == "(" and self.peek(1)[0] == "str" \
                    and self.peek(1)[1] == f'"{self.name}"' and self.peek(2)[1] == ")":
                self.i += 3
                return ("E",)
            if v in HELPERS and self.peek()[1] == "(" and self.peek(1)[1] == f'"{self.name}"':
                self.take("(")
                self.take()
                args = []
                while self.peek()[1] == ",":
                    self.take()
                    args.append(self.expr(2))
                self.take(")")
                return ("helper", v, args)
            if v == self.gv:
                return ("E",)
            if v in ("NULL", "nullptr", "false"):
                return ("num", 0)
            if v == "true":
                return ("num", 1)
            return ("id", v)
        if k == "op" and v == "(":
            e = self.expr(0, comma=True)
            self.take(")")
            return e
        if k == "op" and v == "[":  # lambda: [..](..){..} -> opaque
            raise PErr("lambda")
        raise PErr(f"primary {k} {v}")

    def postfix(self, a):
        while True:
            k, v = self.peek()
            if v == "(" and k == "op":
                self.take()
                args = []
                if self.peek()[1] != ")":
                    args.append(self.expr(2))
                    while self.peek()[1] == ",":
                        self.take()
                        args.append(self.expr(2))
                self.take(")")
                a = ("call", a, args)
            elif v == "[" and k == "op":
                self.take()
                ix = self.expr(0)
                self.take("]")
                a = ("idx", a, ix)
            elif v in (".", "->") and k == "op":
                self.take()
                a = ("mem", a, self.take()[1])
            elif v in ("++", "--") and k == "op":
                self.take()
                a = ("post", a)
            else:
                return a


# ---------------------------------------------------------------- evaluator
class Null(Exception):
    pass


FOREIGN, OPAQUE = "FOREIGN", "OPAQUE"
INTF = {"atoi", "atol", "atoll", "strtol", "strtoul", "strtoll", "strtoull", "std::atoi", "std::atol", "std::strtol",
        "std::strtoul", "std::strtoll", "std::strtoull", "std::atoll"}
FLTF = {"atof", "strtod", "strtof", "std::atof", "std::strtod", "std::strtof"}
STRF = {"strcmp", "strcasecmp", "strncmp", "strncasecmp", "strstr", "strchr", "std::strcmp", "std::strncmp",
        "std::strstr", "std::strchr", "std::strcasecmp"}


def has_e(n):
    if isinstance(n, tuple):
        if n[0] in ("E", "helper"):
            return True
        return any(has_e(x) for x in n[1:])
    if isinstance(n, list):
        return any(has_e(x) for x in n)
    return False


def c_int(s, base=10):
    m = re.match(r"\s*([-+]?)(0[xX][0-9a-fA-F]+|[0-9]+)" if base in (0, 16) else r"\s*([-+]?)([0-9]+)", s)
    if not m:
        return 0
    d = m.group(2)
    v = int(d, 16) if d.lower().startswith("0x") else (int(d, 8) if base == 0 and len(d) > 1 and d[0] == "0" else int(d))
    return -v if m.group(1) == "-" else v


def c_flt(s):
    m = re.match(r"\s*[-+]?(?:[0-9]+\.?[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?", s)
    return float(m.group(0)) if m else 0.0


def truth(v):
    if v in (FOREIGN, OPAQUE):
        return v
    if isinstance(v, tuple):  # ('ptr', s)
        return v[1] is not None
    if isinstance(v, str):
        return True
    return v != 0


def ev(n, s):
    t = n[0]
    if t == "E":
        return ("ptr", s)
    if t == "num":
        return n[1]
    if t == "str":
        return n[1]
    if t == "id":
        return FOREIGN
    if t == "cast":
        return ev(n[1], s)
    if t == "helper":
        f, args = n[1], n[2]
        if f in ("rs64_env_int", "s6919_mode"):
            if s is None or s == "":
                return ev(args[0], s) if args else OPAQUE
            if f == "rs64_env_int":
                return c_int(s)
            return 2 if s[0] == "t" else int(s[0] != "0")
        if f in ("rs64_bind_flag", "env_on"):
            return int(bool(s) and s[0] != "0")
        if f == "env_flag":  # ROGUESQ_LOG_ALL ignored (foreign)
            return int(bool(s) and s[0] != "0")  # s7728: debug_logs.h dropped its false/no special case
        if f == "rs64_s7355_env_is":
            v = ev(args[0], s) if args else OPAQUE
            return OPAQUE if not isinstance(v, str) else int(s is not None and s == v)
    if t == "un":
        op = n[1]
        if op == "*":
            return deref(ev(n[2], s), 0)
        v = ev(n[2], s)
        if v in (FOREIGN, OPAQUE):
            return v
        if op == "!":
            return int(not truth(v))
        if op == "-":
            return -v if isinstance(v, (int, float)) else OPAQUE
        if op == "~":
            return ~v if isinstance(v, int) else OPAQUE
        if op == "+":
            return v
        return OPAQUE
    if t == "idx":
        ix = ev(n[2], s)
        if not isinstance(ix, int):
            return OPAQUE
        return deref(ev(n[1], s), ix)
    if t == "bin":
        op = n[1]
        if op in ("&&", "||"):
            a = ev(n[2], s)
            if a == OPAQUE:
                return OPAQUE
            if a == FOREIGN:
                b = ev(n[3], s)
                return b if b in (FOREIGN, OPAQUE) else int(truth(b))
            ta = truth(a)
            if op == "&&" and not ta:
                return 0
            if op == "||" and ta:
                return 1
            b = ev(n[3], s)
            if b == OPAQUE:
                return OPAQUE
            if b == FOREIGN:
                return int(ta)
            return int(truth(b))
        a, b = ev(n[2], s), ev(n[3], s)
        if OPAQUE in (a, b):
            return OPAQUE
        if FOREIGN in (a, b):
            return FOREIGN
        if isinstance(a, tuple) or isinstance(b, tuple):  # pointer vs NULL
            if op in ("==", "!=") and (b == 0 or a == 0):
                p = a if isinstance(a, tuple) else b
                r = p[1] is None
                return int(r if op == "==" else not r)
            return OPAQUE
        if isinstance(a, str) or isinstance(b, str):
            return OPAQUE
        try:
            return int({"==": a == b, "!=": a != b, "<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]) \
                if op in ("==", "!=", "<", ">", "<=", ">=") else \
                {"+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b, "/": lambda: a / b if b else 0,
                 "%": lambda: a % b if b else 0, "&": lambda: int(a) & int(b), "|": lambda: int(a) | int(b),
                 "^": lambda: int(a) ^ int(b), "<<": lambda: int(a) << int(b), ">>": lambda: int(a) >> int(b)}[op]()
        except (KeyError, TypeError, ValueError):
            return OPAQUE
    if t == "tern":
        c = ev(n[1], s)
        if c in (FOREIGN, OPAQUE):
            return OPAQUE
        return ev(n[2] if truth(c) else n[3], s)
    if t == "call":
        f = n[1][1] if n[1][0] == "id" else None
        args = n[2]
        if not has_e(args):
            return FOREIGN if not has_e(n[1]) else OPAQUE
        if f in INTF or f in FLTF:
            p = ev(args[0], s)
            if not isinstance(p, tuple):
                return OPAQUE
            if p[1] is None:
                raise Null(f)
            if f in FLTF:
                return c_flt(p[1])
            base = ev(args[2], s) if len(args) > 2 else 10
            return c_int(p[1], base if isinstance(base, int) else 10)
        if f in STRF:
            a = [ev(x, s) for x in args]
            if not isinstance(a[0], tuple) or len(a) < 2:
                return OPAQUE
            if a[0][1] is None:
                raise Null(f)
            x = a[0][1]
            base_f = f.split("::")[-1]
            if base_f in ("strstr",):
                return ("ptr", "x") if isinstance(a[1], str) and a[1] in x else 0
            if base_f == "strchr":
                return ("ptr", "x") if isinstance(a[1], int) and chr(a[1]) in x else 0
            if not isinstance(a[1], str):
                return OPAQUE
            y = a[1]
            if "case" in base_f:
                x, y = x.lower(), y.lower()
            if base_f.startswith("strn"):
                k = a[2] if len(a) > 2 and isinstance(a[2], int) else None
                if k is None:
                    return OPAQUE
                x, y = x[:k], y[:k]
            return (x > y) - (x < y)
        return OPAQUE
    return OPAQUE


def deref(p, k):
    if p in (FOREIGN, OPAQUE):
        return p
    if isinstance(p, tuple):
        if p[1] is None:
            raise Null("deref")
        return ord(p[1][k]) if k < len(p[1]) else 0
    if isinstance(p, str):
        return ord(p[k]) if k < len(p) else 0
    return OPAQUE


def signature(node):
    out = []
    for v in VALUES:
        try:
            r = truth(ev(node, v))
        except Null:
            r = "NULL"
        except RecursionError:
            r = OPAQUE
        out.append({True: 1, False: 0}.get(r, "?") if r != "NULL" else "NULL")
    return tuple(out)


# ---------------------------------------------------------------- isolate the deciding node
CLIMB_BIN = {"&&", "||", "==", "!=", "<", ">", "<=", ">=", "&", "|", "+", "-", "*", "/", "%", "^", "<<", ">>"}


def const_expr(n):
    return not has_e(n) and not any(isinstance(x, tuple) and x[0] in ("id", "call", "mem")
                                    for x in walk(n))


def walk(n):
    if isinstance(n, tuple):
        yield n
        for x in n[1:]:
            yield from walk(x)
    elif isinstance(n, list):
        for x in n:
            yield from walk(x)


def paths(n, pre=()):
    if isinstance(n, tuple):
        if n[0] in ("E", "helper"):
            yield pre
            return
        for i, x in enumerate(n[1:], 1):
            yield from paths(x, pre + (i,))
    elif isinstance(n, list):
        for i, x in enumerate(n):
            yield from paths(x, pre + (i,))


def at(n, p):
    for i in p:
        n = n[i]
    return n


def isolate(root):
    ps = list(paths(root))
    if not ps:
        return None
    lca = ps[0]
    for p in ps[1:]:
        k = 0
        while k < min(len(lca), len(p)) and lca[k] == p[k]:
            k += 1
        lca = lca[:k]
    p = lca
    while True:  # lists (call args) are not nodes: an LCA inside one means "this call"
        if p and isinstance(at(root, p), list):
            p = p[:-1]
            continue
        break
    while p:
        par_p = p[:-1]
        if par_p and isinstance(at(root, par_p), list):  # p is an argument of a call
            call_p = par_p[:-1]
            call = at(root, call_p)
            f = call[1][1] if call[1][0] == "id" else None
            if f in INTF or f in FLTF or f in STRF:
                p = call_p
                continue
            break
        par = at(root, par_p)
        k = p[-1]
        t = par[0]
        if t in ("cast",) or (t == "un" and par[1] in ("!", "*", "-", "~", "+")) or (t == "idx" and k == 1):
            p = par_p
            continue
        if t == "bin" and par[1] in CLIMB_BIN:
            other = par[3] if k == 2 else par[2]
            if par[1] in ("&&", "||") or has_e(other) or const_expr(other):
                p = par_p
                continue
            break
        if t == "tern" and k == 1 and all(strip_cast(b)[0] == "num" and strip_cast(b)[1] in (0, 1) for b in par[2:4]):
            p = par_p
            continue
        break  # tern (cond or branch), call, asg, comma, mem: stop
    if p and at(root, p) == ("E",):
        return None  # the bare pointer handed to a call / assignment / branch: not decided here
    return at(root, p)


# ---------------------------------------------------------------- statement scan from a site
def split_after(toks, i, limit=12):
    """Statements from token i: list of (kind, payload, next_i) with kind in if/ifret/ret/stmt/end."""
    out, n = [], len(toks)
    while i < n and len(out) < limit:
        k, v = toks[i]
        if v == "}":
            out.append(("end", [], i))
            break
        if v in ("{", ";"):
            i += 1
            continue
        if v == "if" or (v == "else" and i + 1 < n and toks[i + 1][1] == "if"):
            if v == "else":
                i += 1
            j, d = i + 1, 0
            while j < n:
                d += toks[j][1] == "("
                d -= toks[j][1] == ")"
                j += 1
                if d == 0:
                    break
            cond = toks[i + 2:j - 1]
            if j < n and toks[j][1] == "return":
                e = j + 1
                d = 0
                while e < n and not (toks[e][1] == ";" and d == 0):
                    d += toks[e][1] in "([{"
                    d -= toks[e][1] in ")]}"
                    e += 1
                out.append(("ifret", (cond, toks[j + 1:e]), e + 1))
                i = e + 1
                continue
            out.append(("if", cond, j))
            break
        if v in ("else", "for", "while", "switch", "do", "case", "default"):
            out.append(("end", [], i))
            break
        j, d = i, 0
        while j < n and not (toks[j][1] in (";", "{") and d == 0):
            d += toks[j][1] in "(["
            d -= toks[j][1] in ")]"
            if d < 0:
                break
            j += 1
        if v == "return":
            out.append(("ret", toks[i + 1:j], j + 1))
            break
        out.append(("stmt", toks[i:j], j + 1))
        i = j + 1
    return out


def strip_decl(toks):
    """Drop a leading declaration / assignment: `[type] x = RHS` -> RHS tokens and x."""
    d = 0
    for j, (k, v) in enumerate(toks):
        d += v in "(["
        d -= v in ")]"
        if d == 0 and v in ASSIGN:
            lhs = [t for t in toks[:j] if t[1] not in TYPEW and t[1] != "*"]
            return toks[j + 1:], (lhs[-1] if lhs else None)
    return toks, None


def mark_e(toks, name, gv):
    out, i = [], 0
    while i < len(toks):
        k, v = toks[i]
        if v in ("std::getenv", "getenv", "::getenv") and i + 3 < len(toks) and toks[i + 1] == ("op", "(") \
                and toks[i + 2] == ("str", f'"{name}"') and toks[i + 3] == ("op", ")"):
            out.append(("E", "E"))
            i += 4
            continue
        out.append(("E", "E") if gv and k == "id" and v == gv else toks[i])
        i += 1
    return out


def parse_tokens(toks, name):
    p = P(toks, name)
    n = p.expr(0, comma=True)
    if p.i != len(toks):
        raise PErr(f"trailing {toks[p.i]}")
    return n


def has_et(t):
    return any(x[0] == "E" or x[1] in HELPERS for x in t)


PRESENCE = (0, 1, 1, 1, 1, 1)


def ret_value(node):
    """A decision whose value IS the string (e ? e : "x") passes the string on: not an on/off reading."""
    return node is not None and node[0] == "tern" and any(x in (("E",),) or (isinstance(x, tuple) and x[0] == "str")
                                                         for x in (node[2], node[3]))


def cond_gv(t):
    semi = [q for q, x in enumerate(t) if x[1] == ";"]
    rhs, lhs = strip_decl(t[:semi[0]] if semi else t)
    return lhs[1] if lhs is not None and lhs[0] != "E" and rhs == [("E", "E")] else None


def if_init(t, toks, j, name):
    """C++17 `if (const char* e = getenv(X); e && *e)` -> the tail with e marked; `if (const char* e = getenv(X))` -> presence."""
    gv = cond_gv(t)
    if gv is None:
        return t, toks
    semi = [q for q, x in enumerate(t) if x[1] == ";"]
    tail = mark_e(t[semi[0] + 1:], name, gv) if semi else [("E", "E")]
    return tail, toks[:j] + mark_e(toks[j:], name, gv)


def decide(toks, i, name, depth=0):
    """Walk statements from i (tokens already E-marked) to the first decision on E -> (sig, node) | (None, why)."""
    if depth > 3:
        return None, "depth"
    chain, foreign_after, final = [], False, None
    for k, t, j in split_after(toks, i):
        if k == "ifret":
            cond, rv = t
            cond, toks = if_init(cond, toks, j, name)
            rv = mark_e(rv, name, cond_gv(t[0]))
            if not has_et(cond):
                foreign_after |= bool(chain)
                continue
            chain.append((isolate(parse_tokens(cond, name)), parse_tokens(rv, name) if rv else ("id", "void")))
            continue
        if k == "ret":
            final = parse_tokens(t, name) if t else ("id", "void")
            break
        if k == "if":
            t, toks = if_init(t, toks, j, name)
            if not has_et(t):
                return None, "foreign if-block"
            node = isolate(parse_tokens(t, name))
            if node is not None and signature(node) == PRESENCE:  # a guard: the decision may be inside its body
                inner = decide(toks, j + 1 if j < len(toks) and toks[j][1] == "{" else j, name, depth + 1) \
                    if j < len(toks) else (None, "")
                if inner[0] and inner[1] is not None and inner[0] != PRESENCE:
                    node = ("bin", "&&", node, inner[1])
            return finish(chain, node, foreign_after)
        if k == "stmt":
            if not has_et(t):
                continue
            rhs, lhs = strip_decl(t)
            if lhs is not None and lhs[0] == "E":
                return None, "reassigned"
            if lhs is not None and rhs == [("E", "E")]:  # const char* gv = getenv(name): follow gv
                rest = toks[:j] + mark_e(toks[j:], name, lhs[1])
                return decide(rest, j, name, depth + 1)
            node = isolate(parse_tokens(rhs, name))
            return finish(chain, node, foreign_after)
        break
    if final is None:
        return None, "no decision"
    if foreign_after:
        final = ("id", "__foreign")
    if not chain:
        return finish([], isolate(final) if has_e(final) else None, False)
    root = final
    for c, x in reversed(chain):
        root = ("tern", c, x, root)
    return finish([], root, False)


def finish(chain, node, foreign_after):
    if node is None:
        return None, "passed on / no E"
    if ret_value(node):
        return None, "string passed on"
    if chain:
        rest = ("id", "__foreign") if foreign_after else node
        for c, x in reversed(chain):
            rest = ("tern", c, x, rest)
        node = rest
    return signature(node), node


PYC_CACHE = {}


def model_site(lines, lineno, name, is_py):
    """-> (signature, node) or (None, reason)."""
    lo = lineno - 1
    if is_py:  # s7715: triple-quote state is file-wide, so convert the whole file once and window into it
        key = id(lines)
        if PYC_CACHE.get(key, (None,))[0] is not lines:
            PYC_CACHE[key] = (lines, py_c_text(lines))
        lines = PYC_CACHE[key][1]
    window = lines[max(0, lo - 3):lo + 16]
    toks = tokenize("\n".join(window))
    pos = None
    for i, (k, v) in enumerate(toks):
        if k == "str" and v == f'"{name}"' and i >= 2 and toks[i - 1][1] == "(" and \
                (toks[i - 2][1] in ("getenv", "std::getenv", "::getenv") or toks[i - 2][1] in HELPERS):
            pos = i - 2
            break
    if pos is None:
        return None, "no call"
    s, d = pos - 1, 0
    while s >= 0:
        v = toks[s][1]
        if v in (")", "]"):
            d += 1
        elif v in ("(", "["):
            d -= 1
        elif v in (";", "{", "}") and d <= 0:
            break
        s -= 1
    s += 1
    toks = toks[:s] + mark_e(toks[s:], name, None)
    try:
        return decide(toks, s, name)
    except PErr as e:
        return None, f"parse: {e}"
    except (IndexError, RecursionError) as e:
        return None, f"parse: {type(e).__name__}"


def fmt(node):
    t = node[0] if isinstance(node, tuple) else None
    if t == "E": return "e"
    if t == "num": return repr(node[1]) if not (isinstance(node[1], int) and 32 < node[1] < 127) else f"{node[1]}/'{chr(node[1])}'"
    if t == "str": return '"' + node[1] + '"'
    if t == "id": return node[1]
    if t == "un": return node[1] + fmt(node[2])
    if t == "bin": return f"({fmt(node[2])} {node[1]} {fmt(node[3])})"
    if t == "tern": return f"({fmt(node[1])} ? {fmt(node[2])} : {fmt(node[3])})"
    if t == "call": return fmt(node[1]) + "(" + ", ".join(fmt(a) for a in node[2]) + ")"
    if t == "idx": return f"{fmt(node[1])}[{fmt(node[2])}]"
    if t == "cast": return fmt(node[1])
    if t == "helper": return node[1] + "(e" + "".join(", " + fmt(a) for a in node[2]) + ")"
    if t == "mem": return fmt(node[1]) + "." + node[2]
    return str(t)


# ---------------------------------------------------------------- s7733 dead reader texts
GEN_GLOBS = ("../N64Recomp/RecompiledFuncs/*.c", "build/factor5_ucode/*.c", "RecompiledPatches/*", "src/**/*", "include/**/*")
_GEN = {}
DEAD = []  # (name, site, C text) of the last load_sites() call


def gen_corpus():
    """Whitespace- and backslash-stripped text of every tree a fixup/apply script writes into (the compiled code).
    Backslashes go because a re.sub template's `\\\\n` lands as `\\n`. None when the generated tree is absent."""
    if "c" not in _GEN:
        import glob
        if not glob.glob(os.path.join(ROOT, GEN_GLOBS[0])):
            _GEN["c"] = None
        else:
            fs = [f for g in GEN_GLOBS for f in glob.glob(os.path.join(ROOT, g), recursive=True) if os.path.isfile(f)]
            _GEN["c"] = "".join(re.sub(r"[\s\\]+", "", open(f, errors="replace").read()) for f in fs)
    return _GEN["c"]


def py_text_live(cline, corpus):
    """s7733: is this Python-embedded reader text present in the compiled tree? Comments, f-string/format holes
    ({x}, %s), braces and regex backrefs split the text; every remaining piece of >= 8 chars must occur. A replace
    ANCHOR (the old side) or a fixup step (// and /* */ comments are holes too) whose anchor no longer matches carries text the tree does not hold: DEAD."""
    nd = re.sub(r"/\*.*?\*/|//.*", "\x00", re.sub(r"\s+", "", re.sub(r"//[^\n]*", "\x00", cline)))
    nd = re.sub(r"\\[0-9]", "\x00", nd).replace("\\", "")
    pieces = [x for x in re.split(r"[{}\x00]|%[0-9.l]*[sdxXfiu]", nd) if len(x) >= 8]
    return bool(pieces) and all(x in corpus for x in pieces)


# ---------------------------------------------------------------- census
def load_sites(overrides=None, corpus=False):
    """corpus: False = the real generated tree (s7733 DEAD filter), None = no filter, str = a planted tree."""
    corpus = gen_corpus() if corpus is False else corpus
    DEAD.clear()
    pyc = {}
    pairs, site_map, _co, _dt = c7711.load()
    texts = {}
    out = {}
    for name, sl in site_map.items():
        if len(sl) < 2:
            continue
        seen = {}
        for site, _w in sl:
            rel, ln = site.rsplit(":", 1)
            if rel not in texts:
                texts[rel] = (overrides or {}).get(rel) or open(os.path.join(ROOT, rel), errors="replace").read().split("\n")
            if rel.endswith(".py") and corpus is not None:
                if rel not in pyc:
                    pyc[rel] = py_c_text(texts[rel])
                cl = pyc[rel][int(ln) - 1] if 0 < int(ln) <= len(pyc[rel]) else ""
                if not py_text_live(cl, corpus):
                    DEAD.append((name, site, cl.strip()))
                    continue
            sig, node = model_site(texts[rel], int(ln), name, rel.endswith(".py"))
            key = (rel, fmt(node) if sig else site)
            if key in seen:
                continue
            seen[key] = 1
            out.setdefault(name, []).append((site, sig, node))
    return out, set(n for n, _ in pairs)


def strip_cast(n):
    while isinstance(n, tuple) and n[0] == "cast":
        n = n[1]
    return n


def is_num(node):
    """A site whose decision is a parsed NUMBER (e ? atof(e) : 1.0, rs64_env_int): a value, not an on/off reading;
    `atof(e) > 1.0` too: the numeric half of the multi-reader class is s7713's (clamp vs raw threshold)."""
    for x in walk(node):
        if x[0] == "helper" and x[1] == "rs64_env_int":
            return True
        if x[0] == "call" and x[1][0] == "id" and (x[1][1] in INTF or x[1][1] in FLTF) and has_e(x[2]):
            return True
    return False


def judge(sites):
    """-> list of (value, (siteA, vA), (siteB, vB)) disagreements between modelled on/off sites."""
    ms = [x for x in sites if x[1] and not is_num(x[2])]
    # a site testing the opposite of the same reading (`if (!e) save()`, census = trim off) is the same reading inverted
    flip = {0: 1, 1: 0}
    if ms:
        ref = ms[0][1]
        for i, x in enumerate(ms):
            if any(a in (0, 1) and b in (0, 1) for a, b in zip(x[1], ref)) and \
                    all(a not in (0, 1) or b not in (0, 1) or a == flip[b] for a, b in zip(x[1], ref)) and \
                    not any(a in (0, 1) and b in (0, 1) and a == b for a, b in zip(x[1], ref)):
                ms[i] = (x[0], tuple(flip.get(a, a) for a in x[1]), x[2])
    bad = []
    for vi, v in enumerate(VALUES):
        known = [(x[0], x[1][vi]) for x in ms if x[1][vi] in (0, 1, "NULL")]
        vals = set(k for _, k in known)
        if len(vals) > 1:
            a = next(x for x in known if x[1] == sorted(vals, key=str)[0])
            b = next(x for x in known if x[1] != a[1])
            bad.append((v, a, b))
    return bad


def census(models, owner, quiet=False):
    bad, split_names = [], []
    n_mod = n_un = 0
    for name in sorted(models):
        ss = models[name]
        n_mod += sum(1 for x in ss if x[1])
        n_un += sum(1 for x in ss if not x[1])
        n_num = sum(1 for x in ss if x[1] and is_num(x[2]))
        if sum(1 for x in ss if x[1]) - n_num < 2:
            continue
        w = judge(ss)
        if not w:
            continue
        verdict = "REVIEWED" if name in REVIEWED else "SPLIT"
        kind = "UNSET" if any(x[0] is None for x in w) else "VALUE"
        if not quiet:
            vals = ",".join(VNAME.get(x[0], x[0]) for x in w)
            print(f"{verdict:8s} {kind:5s} {name}{' (owner)' if name in owner else ''} differs on {vals}")
            for site, sig, node in ss:
                if sig and not is_num(node):
                    print(f"         {''.join(str(c) if c != 'NULL' else 'N' for c in sig)}  {site}  {fmt(node)[:110]}")
            if verdict == "REVIEWED":
                print(f"         reviewed: {REVIEWED[name]}")
        if verdict == "SPLIT":
            bad.append(name)
        else:
            census.reviewed_hit.add(name)
    return bad, n_mod, n_un


census.reviewed_hit = set()


def honours_all(site, node, texts=None):
    """s7728: does this reader site also switch on under ROGUESQ_LOG_ALL?"""
    if any(x[0] == "helper" and x[1] == "env_flag" for x in walk(node)):
        return True
    rel, ln = site.rsplit(":", 1)
    ln = int(ln)
    t = (texts or {}).get(rel)
    if t is None:
        t = open(os.path.join(ROOT, rel), errors="replace").read().split("\n")
    return any('getenv("ROGUESQ_LOG_ALL")' in l for l in t[max(0, ln - 6):ln + 3])


def all_census(models, quiet=False, texts=None):
    """-> names whose host reader sites disagree on honouring ROGUESQ_LOG_ALL."""
    bad = []
    for name in sorted(models):
        ss = [x for x in models[name] if x[1] and not is_num(x[2]) and x[0].startswith(("src/", "lib/"))]
        if len(ss) < 2 or name == "ROGUESQ_LOG_ALL":
            continue
        h = [(x[0], honours_all(x[0], x[2], texts)) for x in ss]
        if len(set(b for _, b in h)) < 2:
            continue
        bad.append(name)
        if not quiet:
            print(f"SPLIT    LOGALL {name}: " + ", ".join(f"{s}={'all' if b else 'own'}" for s, b in h))
    return bad


def plant(lines_a, lines_b, name="ROGUESQ_PLANT"):
    a = model_site(lines_a, 1, name, False)
    b = model_site(lines_b, 1, name, False)
    return a, b, judge([("P:a", a[0], a[1]), ("P:b", b[0], b[1])])


OLD_LABEL = "const char* arm = (audio && audio[0] && audio[0] != '0') ?"


def main():
    ok = True
    if "--controls" in sys.argv:
        a, b, w = plant(['const char* e = getenv("ROGUESQ_PLANT"); return !(e && *e == \'0\');'],
                        ['const char* e = getenv("ROGUESQ_PLANT"); return e && *e != \'0\';'])
        g = any(x[0] is None for x in w)
        print(f"control default-on vs default-off sigs={a[0]},{b[0]} want SPLIT on unset {'PASS' if g else 'FAIL'}")
        ok &= g
        a, b, w = plant(['const char* e = getenv("ROGUESQ_PLANT");', "if (e && *e == '1') go();"],
                        ['static const bool on = [] { const char* f = std::getenv("ROGUESQ_PLANT"); return f && *f != \'0\'; }();'])
        g = any(x[0] == "2" for x in w)
        print(f"control '1'-only vs non-'0' sigs={a[0]},{b[0]} want SPLIT on \"2\" {'PASS' if g else 'FAIL'}")
        ok &= g
        models, owner = load_sites()
        fps = models.get("ROGUESQ_FPS60", [])
        nm = sum(1 for x in fps if x[1])
        g = nm >= 4 and not judge(fps)
        print(f"control FPS60 readers modelled={nm}/{len(fps)} want AGREE got {'SPLIT' if judge(fps) else 'AGREE'} {'PASS' if g else 'FAIL'}")
        ok &= g
        vend = "tools/fixup_game_funcs_vendored.py"
        vl = open(os.path.join(ROOT, vend), errors="replace").read()
        idx = [i for i, l in enumerate(vl.split("\n")) if "audio_on" in l and "audio_stub" in l or "arm = " in l and "audio" in l]
        cur = vl
        new_label = "const char* arm = !(audio && audio[0] == '0') ?"
        if new_label in cur:
            cur = cur.replace(new_label, OLD_LABEL)
        m2, _ = load_sites({vend: cur.split("\n")})
        au = m2.get("ROGUESQ_AUDIO_UCODE", [])
        g = any(x[0] is None for x in judge(au))
        print(f"control pre-s7714 AUDIO_UCODE label want SPLIT on unset got {'SPLIT' if judge(au) else 'AGREE'} {'PASS' if g else 'FAIL'}")
        ok &= g
        r6 = model_site(['if (const char* e = std::getenv("ROGUESQ_PLANT"); e && *e != \'0\') go();'], 1, "ROGUESQ_PLANT", False)
        g = bool(r6[0]) and r6[0][:3] == (0, 0, 1)
        print(f"control C++17 if-init site sig={r6[0]} want unset0 '0'->0 '1'->1 {'PASS' if g else 'FAIL'}")
        ok &= g
        r = model_site(['if (s_other && getenv("ROGUESQ_PLANT") && *getenv("ROGUESQ_PLANT") != \'0\') go();'], 1,
                       "ROGUESQ_PLANT", False)
        g = bool(r[0]) and r[0][0] == 0 and r[0][2] == 1 and r[0][1] == 0
        print(f"control foreign conjunct isolated sig={r[0]} want unset0 '0'->0 '1'->1 {'PASS' if g else 'FAIL'}")
        ok &= g
        pyl = ["X = ('    { const char* e = getenv(\\\"ROGUESQ_PLANT\\\"); if (e && *e != \\'0\\') go(); }\\n')"]
        r7 = model_site(pyl, 1, "ROGUESQ_PLANT", True)
        g = bool(r7[0]) and r7[0][:3] == (0, 0, 1)
        print(f"control Python-embedded escaped-quote site sig={r7[0]} want unset0 '0'->0 '1'->1 {'PASS' if g else 'FAIL'}")
        ok &= g
        r8 = model_site(["H = r\'\'\'", "int x;", 'const char* e = getenv("ROGUESQ_PLANT");', "if (e && *e == '1') go();",
                         "\'\'\'"], 3, "ROGUESQ_PLANT", True)
        g = bool(r8[0]) and r8[0][:4] == (0, 0, 1, 0)
        print(f"control Python triple-quoted block site sig={r8[0]} want unset0 '0'->0 '1'->1 '2'->0 {'PASS' if g else 'FAIL'}")
        ok &= g
        # s7728 controls: the old env_flag (false/no read as off) vs a `*e != '0'` reader must SPLIT on "false";
        # a planted LOG_ALL-honouring host site vs an own-only host site must LOGALL-SPLIT; both honouring must agree.
        a, b, w = plant(['const char* e = getenv("ROGUESQ_PLANT"); if (e && *e && *e != \'0\' && strcmp(e, "false") && strcmp(e, "no")) go();'],
                        ['const char* e = getenv("ROGUESQ_PLANT"); if (e && *e && *e != \'0\') go();'])
        g = any(x[0] == "false" for x in w) and any(x[0] == "no" for x in w)
        print(f"control pre-s7728 env_flag false/no vs non-'0' sigs={a[0]},{b[0]} want SPLIT on false,no {'PASS' if g else 'FAIL'}")
        ok &= g
        a, b, w = plant(['const char* e = getenv("ROGUESQ_PLANT"); if (e) go();'],
                        ['const char* e = getenv("ROGUESQ_PLANT"); if (e && *e) go();'])
        g = [x[0] for x in w] == [""]
        print(f"control pre-s7730 presence vs e&&*e sigs={a[0]},{b[0]} want SPLIT on empty only {'PASS' if g else 'FAIL'}")
        ok &= g
        la = ['static const bool v = [] {', '    const char* all = getenv("ROGUESQ_LOG_ALL");',
              '    const char* e = getenv("ROGUESQ_PLANT");', "    return (all && *all != '0') || (e && *e != '0');", '}();']
        lo = ['static const bool v = [] {', '    const char* e = getenv("ROGUESQ_PLANT");', "    return e && *e != '0';", '}();']
        ra, rb = model_site(la, 3, "ROGUESQ_PLANT", False), model_site(lo, 2, "ROGUESQ_PLANT", False)
        tx = {"src/plant_a.cpp": la, "src/plant_b.cpp": lo, "src/plant_c.cpp": la}
        g1 = all_census({"ROGUESQ_PLANT": [("src/plant_a.cpp:3", ra[0], ra[1]), ("src/plant_b.cpp:2", rb[0], rb[1])]}, True, tx)
        g2 = all_census({"ROGUESQ_PLANT": [("src/plant_a.cpp:3", ra[0], ra[1]), ("src/plant_c.cpp:3", ra[0], ra[1])]}, True, tx)
        g3 = all_census({"ROGUESQ_PLANT": [("src/plant_a.cpp:3", ra[0], ra[1]), ("tools/plant_b.py:2", rb[0], rb[1])]}, True, tx)
        g = g1 == ["ROGUESQ_PLANT"] and not g2 and not g3
        print(f"control LOG_ALL all-vs-own host SPLIT={bool(g1)} all-vs-all={bool(g2)} host-vs-generated={bool(g3)} "
              f"want True/False/False {'PASS' if g else 'FAIL'}")
        ok &= g
        # s7729: a planted reader the parser cannot decide must come back UNCLASSIFIED; a classed real site must not.
        pl = ['const char* e = getenv("ROGUESQ_PLANT");', 'use(e);']
        rp = model_site(pl, 1, "ROGUESQ_PLANT", False)
        _, cp = classify_unmodelled("ROGUESQ_PLANT", "src/plant_u.cpp:1", {"src/plant_u.cpp": pl})
        _, cr = classify_unmodelled("ROGUESQ_S7064", "src/main/upstream_compat.cpp:1",
                                    {"src/main/upstream_compat.cpp": ['x->fo = fopen(getenv("ROGUESQ_S7064"), "w");']})
        g = rp[0] is None and cp is None and cr == "STRING"
        print(f"control planted undecidable site modelled={rp[0] is not None} class={cp} real S7064 class={cr} "
              f"want False/None/STRING {'PASS' if g else 'FAIL'}")
        ok &= g
        # s7731: the intent gate must fire when the normaliser is missing, and pass on the real source
        models, owner = load_sites()
        m0 = intent_check(models, quiet=True, src="")
        m1 = intent_check(models, quiet=True)
        g = set(m0) >= {"off", "false", "no"} and not m1
        print(f"control s7731 intent gate no-normaliser unmapped={m0} real={m1} want off/false/no vs [] {'PASS' if g else 'FAIL'}")
        ok &= g
        l0 = letter_scan(quiet=True, keep=set())
        l1 = letter_scan(quiet=True)
        g = "ROGUESQ_DD_OFFMAPCULL_H" in l0 and not l1
        print(f"control s7731 letter scan empty-keep unkept={l0} real={l1} want OFFMAPCULL_H in first, [] {'PASS' if g else 'FAIL'}")
        ok &= g
        # s7732: a planted owner-documented presence reader must be flagged; the real tree must pass
        pz = ("ROGUESQ_PLANTZ", [("src/plant_z.cpp:1", None)], ['if (const char* e = getenv("ROGUESQ_PLANTZ"); e && *e) go();'])
        z0 = zero_on_check(quiet=True, docs="ROGUESQ_PLANTZ=16:9", extra=[pz], reviewed={})
        z1 = zero_on_check(quiet=True)
        g = "ROGUESQ_PLANTZ" in z0 and not z1
        print(f"control s7732 zero-on planted={'ROGUESQ_PLANTZ' in z0} real={z1} want True, [] {'PASS' if g else 'FAIL'}")
        ok &= g
        # s7733: Python reader text absent from the compiled tree is DEAD (does not vote). A planted anchor that cannot
        # be in the tree must be DEAD; the re.sub-template UCODE_CAP fixup text (backslash escapes) must be LIVE; the
        # vendored s4701 B40 form that fixup_live_replay rewrites must be DEAD; with the filter off, the pre-s7733
        # OVL2C_DROP split (dead default-drop fixup text) must come back.
        corp = gen_corpus()
        if corp is None:
            print("control s7733 generated tree absent: FAIL"); ok = False
        else:
            pd = py_text_live('{ const char* e = getenv("ROGUESQ_PLANT"); s7733_never_in_any_tree_q9(e); }', corp)
            fx = open(os.path.join(ROOT, "tools/fixup_factor5_ucode.py"), errors="replace").read().split("\n")
            uc = [l for l in py_c_text(fx) if 'getenv("ROGUESQ_UCODE_CAP")' in l]
            ul = bool(uc) and all(py_text_live(l, corp) for l in uc)
            models, owner = load_sites()
            b40 = any(n == "ROGUESQ_M5_B40_VALUE" and "vendored" in st for n, st, _ in DEAD)
            m0, _ = load_sites(corpus=None)
            ovl = bool(judge(m0.get("ROGUESQ_OVL2C_DROP", []))) and not judge(models.get("ROGUESQ_OVL2C_DROP", []))
            load_sites()
            g = not pd and ul and b40 and ovl
            print(f"control s7733 dead text planted_live={pd} ucode_cap_live={ul} b40_vendored_dead={b40} "
                  f"ovl2c_split_only_unfiltered={ovl} want False/True/True/True {'PASS' if g else 'FAIL'}")
            ok &= g
        if not ok:
            return 2
    else:
        models, owner = load_sites()
    if gen_corpus() is None:
        print("s7733: generated tree ../N64Recomp/RecompiledFuncs absent: DEAD filter OFF (every Python text votes)")
    else:
        print(f"s7733: {len(DEAD)} Python reader texts absent from the compiled tree (DEAD: anchors / no-op steps, not voting)"
              f" over {len(set(n for n, _, _ in DEAD))} names")
    if "--dead" in sys.argv:
        for n, st, cl in DEAD:
            print(f"  DEAD {n} {st}: {cl[:100]}")
    census.reviewed_hit = set()
    bad, n_mod, n_un = census(models, owner)
    for n in sorted(set(REVIEWED) - census.reviewed_hit):
        print(f"  stale REVIEWED entry {n} (its readers no longer split)")
    bad_all = all_census(models)
    print(f"s7714: {len(models)} names with >=2 reader sites, {n_mod} sites modelled, {n_un} unmodelled, "
          f"{len(bad)} unreviewed SPLIT, {len(bad_all)} LOG_ALL SPLIT (host readers)")
    bad = bad + bad_all
    uncls, used, by = [], set(), {}
    for name in sorted(models):
        for site, sig, why in models[name]:
            if sig:
                continue
            i, cls = classify_unmodelled(name, site)
            if cls is None:
                uncls.append((name, site, why))
            else:
                used.add(i); by[cls] = by.get(cls, 0) + 1
            if "--unmodelled" in sys.argv:
                print(f"  unmodelled {name} {site}: {why} -> {cls or 'UNCLASSIFIED'}")
    stale = [UNMODELLED_T[i][:3] for i in range(len(UNMODELLED_T)) if i not in used]
    print(f"s7729: unmodelled {n_un} = " + " ".join(f"{k}={by.get(k, 0)}" for k in UNMODELLED_CLASS)
          + f" UNCLASSIFIED={len(uncls)}; stale table entries {len(stale)}")
    for name, site, why in uncls:
        print(f"  UNCLASSIFIED {name} {site}: {why} (read it; model it or add it to UNMODELLED_T)")
    for st in stale:
        print(f"  stale UNMODELLED_T entry {st} (site gone or line changed)")
    miss = intent_check(models)
    lbad = letter_scan()
    zbad = zero_on_check()
    return 1 if bad or uncls or miss or lbad or zbad else 0


def keep_words(src=None):
    if src is None:
        src = open(os.path.join(ROOT, "src/main/rs64_settings.cpp"), errors="replace").read()
    m = re.search(r"kKeepWords\[\] = \{(.*?)\};", src, re.S)
    return set(re.findall(r'"(ROGUESQ_\w+)"', m.group(1))) if m else set()


LETTER_RE = re.compile(r"""(?:([A-Za-z_]\w*)\s*\[0\]|\*\s*([A-Za-z_]\w*)|\(\s*\*\s*([A-Za-z_]\w*)\s*\))\s*[!=]=\s*'([ofnyOFNY])'""")


def letter_scan(quiet=False, keep=None, extra=None):
    """s7731: a reader testing the first letter of an on/off word ('o' off/on, 'f' false, 'n' no, 'y' yes) gives the
    word a meaning the launch normaliser would erase. Every such name must be in kKeepWords. Scans each reader site's
    line and the 2 after it. -> names testing a word letter that are not kept (gate: must be empty)."""
    _p, site_map, _c, _d = c7711.load()
    keep = keep_words() if keep is None else keep
    texts, hits = {}, {}
    for name, sl in list(site_map.items()) + list((extra or {}).items()):
        for site, _w in sl:
            rel, ln = site.rsplit(":", 1)
            if rel not in texts:
                texts[rel] = (extra or {}).get("@" + rel) or open(os.path.join(ROOT, rel), errors="replace").read().split("\n")
            win = " ".join(texts[rel][int(ln) - 1:int(ln) + 2])
            # only the variable this name's getenv was stored in (`cl[0]=='y'` beside getenv("ROGUESQ_HUD_MARKPC") is not it)
            vs = set(re.findall(r'(\w+)\s*=\s*(?:std::)?getenv\(\s*"%s"\s*\)' % re.escape(name), win))
            for m in LETTER_RE.finditer(win):
                v = m.group(1) or m.group(2) or m.group(3)
                if not vs or v in vs:
                    hits.setdefault(name, set()).add((site, m.group(4)))
    bad = sorted(n for n in hits if n not in keep)
    if not quiet:
        print(f"s7731: readers testing an on/off word letter: {len(hits)} names "
              + " ".join(f"{n}({','.join(sorted(set(l for _, l in hits[n])))})" for n in sorted(hits))
              + f"; kept at launch {len(keep)}; unkept {len(bad)} {bad if bad else ''}")
        for n in bad:
            for site, l in sorted(hits[n]):
                print(f"  UNKEPT {n} {site} tests '{l}': add it to kKeepWords or stop testing the letter")
    stale = sorted(keep - set(hits)) if extra is None else []
    for n in stale:
        if not quiet:
            print(f"  stale kKeepWords entry {n} (no reader tests a word letter any more)")
    return bad + stale


WORDS = {"off": "0", "false": "0", "no": "0", "on": "1", "true": "1", "yes": "1"}


def intent_check(models, quiet=False, src=None):
    """s7731: a reader that reads an on/off word unlike its digit ("off" != "0") reads against intent, unless the launch
    normaliser (rs64_settings_bool_word, src/main/rs64_settings.cpp) maps that word first. -> words left unmapped that
    some reader reads against intent (gate: must be empty)."""
    if src is None:
        src = open(os.path.join(ROOT, "src/main/rs64_settings.cpp"), errors="replace").read()
    m = re.search(r'rs64_settings_bool_word\(const char\* v\) \{(.*?)\n\}', src, re.S)
    body = m.group(1) if m else ""
    mapped = {}
    for arr, d in (("off", "0"), ("on", "1")):
        a = re.search(r"\b%s\[\] = \{([^}]*)\}" % arr, body)
        for w in re.findall(r'"(\w+)"', a.group(1) if a else ""):
            mapped[w] = d if f'return "{d}"' in body else None
    idx = {v: i for i, v in enumerate(VALUES)}
    against = {}
    for name in models:
        for site, sig, node in models[name]:
            if not sig:
                continue
            for w, d in WORDS.items():
                if w in idx and d in idx and sig[idx[w]] in (0, 1) and sig[idx[d]] in (0, 1) and sig[idx[w]] != sig[idx[d]]:
                    against.setdefault(w, set()).add(name)
    miss = sorted(w for w in against if mapped.get(w) != WORDS[w])
    if not quiet:
        print("s7731: on/off words read against their digit (pre-normalisation): "
              + " ".join(f"{w}={len(against.get(w, ()))}" for w in WORDS)
              + f"; mapped at launch {len(mapped)}/{len(WORDS)}; unmapped-against {len(miss)} {miss if miss else ''}")
    return miss


# s7732: owner-documented names with a reader where "0" and "1" both read ON and unset reads OFF (a presence reader): `NAME=0`
# (or =off, which s7731 maps to "0") turns it on there. Each must be reviewed: a value name where 0 means nothing, a reader the
# isolation over-reads (outer `if (e)`, inner digit test), or fixed. A new one fails the gate.
ZERO_ON_REVIEWED = {
    "ROGUESQ_ASPECT": "FIXED s7732: launch unsets any value that is not auto/expand/W:H (KEEP control reopened the window)",
    "ROGUESQ_AUDIO_DEVICE": "value: device name substring",
    "ROGUESQ_DD_OFFMAPCULL": "value: mode/margin (t, -1, n)",
    "ROGUESQ_DD_OFFMAPCULL_K": "value: number",
    "ROGUESQ_DD_OFFMAPCULL_KEDGE": "value: number",
    "ROGUESQ_DD_OFFMAPCULL_KLEVEL": "value: level list",
    "ROGUESQ_DD_WIDEWIN_CAPLEVEL": "value: level list",
    "ROGUESQ_DD_WIDEWIN_MERGE_E": "value: number",
    "ROGUESQ_DD_WIDEWIN_RLEVEL": "value: level list",
    "ROGUESQ_DRAW_DISTANCE": "value: number (s7358 validator; 0 -> retail)",
    "ROGUESQ_G1E_FAST": "over-read: outer presence, returns *e != '0'",
    "ROGUESQ_G5G_AIM": "over-read: outer presence, atoi(e) != 0",
    "ROGUESQ_HANGAR_FOV_CAM": "value: hex address",
    "ROGUESQ_NO_SAVE_WRITE": "presence safety switch: =0 still blocks writes (errs toward the owner save; runner exports =1)",
    "ROGUESQ_OSMEM_MB": "value: MB (s7713 normaliser)",
    "ROGUESQ_RENDER_TO_RAM": "over-read: outer presence, inner v[0] == '0' turns it off",
    "ROGUESQ_SP_LATE": "value: mode (0 = early/upstream, distinct from unset = auto)",
    "ROGUESQ_WIN_DISPLAY": "value: display index or mouse",
}


def zero_on_check(quiet=False, docs=None, extra=None, reviewed=None):
    """-> owner-documented names with an unreviewed presence reader (unset off, "0" and "1" on), plus stale table entries."""
    reviewed = ZERO_ON_REVIEWED if reviewed is None else reviewed
    if docs is None:
        docs = "".join(open(os.path.join(ROOT, d), errors="replace").read() for d in ("docs/OWNER-OPT-INS.md", "README.md"))
    _p, site_map, _c, _d = c7711.load()
    iu, i0, i1 = VALUES.index(None), VALUES.index("0"), VALUES.index("1")
    texts, hits = {}, {}
    items = [(n, sl, None) for n, sl in site_map.items()] + list(extra or [])
    for name, sl, lines in items:
        if not re.search(re.escape(name) + r"\b", docs):
            continue
        for site, _w in sl:
            rel, ln = site.rsplit(":", 1)
            t = lines if lines is not None else texts.setdefault(
                rel, open(os.path.join(ROOT, rel), errors="replace").read().split("\n"))
            sig, node = model_site(t, int(ln), name, rel.endswith(".py"))
            if sig and not is_num(node) and sig[iu] == 0 and sig[i0] == 1 and sig[i1] == 1:
                hits.setdefault(name, []).append(site)
    bad = sorted(n for n in hits if n not in reviewed)
    stale = sorted(n for n in reviewed if n not in hits)
    if not quiet:
        print(f"s7732: owner-documented names whose reader takes =0 as ON (presence): {len(hits)}, "
              f"reviewed {len(hits) - len(bad)}, UNREVIEWED {len(bad)}, stale table entries {len(stale)}")
        for n in bad:
            print(f"  UNREVIEWED {n} {hits[n][:2]}: =0 reads ON here; fix the reader or the launch value, or review it")
        for n in stale:
            print(f"  stale ZERO_ON_REVIEWED entry {n} (no such reader any more)")
    return bad + stale


if __name__ == "__main__":
    sys.exit(main())
