#!/usr/bin/env python3
"""s7548 class GH census: port statics in src/main that capture a guest-derived value and use it later.

After class GG (ultramodern/librecomp retain only static guest objects) the residual is the port's own host code: a static,
atomic, function-local static, thread_local, pointer or container in src/main/*.cpp|.mm that is ASSIGNED from a guest-derived
value in one call and DEREFERENCED into guest memory in a later one.  If the guest frees/reuses the object in between, the
host reads or writes whatever now lives there (the s7545 heap-reuse hazard).

Enumerate (static analysis, comment/string blanked, brace-scoped):
  statics   integer/atomic/PTR scalars and arrays, pointers, std:: containers with static storage (namespace scope, anon
            namespace, `static`/`thread_local` locals; struct members and plain locals excluded).
  capture   an assignment / store / exchange / push_back / insert whose RHS is guest-derived: ctx->rN, task->t.*, a guest
            accessor call (TO_PTR, MEM_*, rdram_be*, rs64_rdram_u*, or any function/lambda whose body reads guest memory with
            one of its params), rdram[..], a tainted local (fixpoint over the enclosing function, seeded with its params and
            with every static already captured), or for pointers rdram/task/TO_PTR.
  deref     the static, a local derived from it (fixpoint, range-for), or a getter call returning it, inside the arguments of
            a guest accessor or an rdram-base index/offset (rdram/RDRAM/uint8_t* locals and params); pointers also *p, p[], p->.
  escape    a getter returning a captured static that is referenced outside src/main (ultramodern, librecomp, rt64 src,
            tools/fixup_*.py, tools/apply_*.py inject C into RecompiledFuncs).
Classes: H-diag (captured, never dereferenced, no escape: print/compare/cache key only; automatic),
  rule classes for dereferenced/escaping rows: H-inflight (task pointer valid for the task run, class GA), H-gated (every
  deref site's enclosing function carries a default-off env gate, verified per site), H-base (the rdram base pointer itself),
  H-host (host-allocated shadow table, never guest memory), H-refresh (re-read from live guest state before every use),
  H-static-target (captured value is a static-image address, read-only use), H-value (escape returns a scalar/count/float, not an address),
  OPEN (default-on deref of a captured heap pointer).  UNCLASSIFIED = deref/escape with no rule; DRIFT = rule proof regex
  missing from the source, gate missing at a deref site, or a rule naming a row that no longer exists.
Exit 0 iff 0 OPEN, 0 UNCLASSIFIED, 0 DRIFT.  --controls runs the planted / mutated variants listed in CONTROLS.
"""
import os
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import re,sys,glob,collections
KW={'if','for','while','switch','catch','return','sizeof','defined','else','do'}
def strip(src):
    # blank comments and string/char literals, keep offsets
    out=list(src); i=0; n=len(src)
    while i<n:
        c=src[i]
        if src.startswith('//',i):
            j=src.find('\n',i); j=n if j<0 else j
            for k in range(i,j): out[k]=' '
            i=j; continue
        if src.startswith('/*',i):
            j=src.find('*/',i+2); j=n if j<0 else j+2
            for k in range(i,j):
                if out[k]!='\n': out[k]=' '
            i=j; continue
        if c=='"' or (c=="'" and not (i>0 and (src[i-1].isalnum()))):
            q=c; j=i+1
            while j<n and src[j]!=q:
                if src[j]=='\\': j+=1
                if j<n and src[j]=='\n': break
                j+=1
            for k in range(i+1,min(j,n)): out[k]=' '
            i=j+1; continue
        i+=1
    return ''.join(out)
def functions(s):
    """top-level function bodies: (name, params, body_start, body_end) ignoring namespace/extern blocks"""
    res=[]; depth=0; cont=[]; i=0; n=len(s); fstart=None
    stack=[]
    for m in re.finditer(r'[{}]',s):
        p=m.start()
        if s[p]=='{':
            pre=s[max(0,p-200):p]
            is_cont=bool(re.search(r'(namespace\s*\w*|extern\s*"C"|extern\s+\s*)\s*$',pre)) or bool(re.search(r'extern\s+"?C?"?\s*$',pre))
            stack.append((p,is_cont))
        else:
            if not stack: continue
            st,ic=stack.pop()
            if ic: continue
            BLOCKS.append((st,p,bool(re.search(r'\b(?:struct|class|union|enum)\b[^;{}()]*$',s[max(0,st-200):st]))))
            if all(c for _,c in stack):
                pre=s[max(0,st-600):st]
                mm=re.search(r'(\w+)\s*\(([^;{}]*)\)\s*(?:const\s*)?(?:noexcept\s*)?(?:->\s*[\w:<>]+\s*)?$',pre)
                if mm and mm.group(1) not in KW:
                    res.append((mm.group(1),mm.group(2),st,p))
                else:
                    res.append(('<init>','',st,p))
    return res

T=r'(?:std::atomic<\s*(?:uint32_t|int32_t|gpr|uint64_t|u32|s32|int|unsigned|int64_t|uintptr_t)\s*>|(?:volatile\s+)?(?:uint32_t|int32_t|gpr|u32|s32|uint64_t|int64_t|uintptr_t|unsigned|int|PTR\([^)]*\)))'
DECL=re.compile(r'(?m)^([ \t]*)((?:static\s+|thread_local\s+|inline\s+|extern\s+"C"\s+)*)('+T+r')\s+((?:[^;(){}]|\{[^{};]*\}|\([^;(){}]*\))*?)\s*;')
GACC=r'(?:TO_PTR|MEM_[A-Z]+|rdram_be\d+(?:_at)?|rs64_rdram_u\d+)'
SRC=re.compile(r'ctx->r\d+|ctx->gpr|\b'+GACC+r'\s*\(|->t\.\w+|\btask->|\brdram\s*\[')
KIND={}
TMEMO={}
BLOCKS=[]
def lineof(s,p): return s.count('\n',0,p)+1
def declarators(txt):
    out=[]; depth=0; cur=''
    for c in txt:
        if c in '({[': depth+=1
        if c in ')}]': depth-=1
        if c==',' and depth==0: out.append(cur); cur=''
        else: cur+=c
    out.append(cur)
    names=[]
    for d in out:
        m=re.match(r'\s*\**\s*(\w+)',d)
        if m: names.append(m.group(1))
    return names
def stmts(body):
    return [m for m in re.finditer(r'[^;{}]+',body)]
def assigned(stmt,name):
    """rhs strings assigning to name in stmt"""
    r=[]
    for m in re.finditer(r'\b'+name+r'\b\s*(?:\[[^\]]*\])?\s*(?:[|+&^-]?=)(?!=)(.*)',stmt):
        if m.start()>0 and stmt[m.start()-1] in '.>': continue
        r.append(m.group(1))
    for m in re.finditer(r'\b'+name+r'\s*(?:\.|->)\s*(?:store|exchange|fetch_\w+|compare_exchange_\w+|push_back|emplace_back|emplace|insert|push_front|try_emplace)\s*\((.*)',stmt): r.append(m.group(1))
    return r
def idents(e): return set(re.findall(r'\b[A-Za-z_]\w*\b',e))
class File:
    def __init__(s,path,text):
        s.path=path; s.raw=text; s.s=strip(text); del BLOCKS[:]; s.F=functions(s.s); s.blocks=list(BLOCKS)
        s.fb=[(a,b,n,p) for (n,p,a,b) in s.F]
        s.fids=[set(re.findall(r'\b[A-Za-z_]\w*\b',s.s[a:b])) for (a,b,n,p) in s.fb]; s.ids=set(re.findall(r'\b[A-Za-z_]\w*\b',s.s))
    def block_at(s,p):
        best=None
        for a,b,isstruct in s.blocks:
            if a<p<b and (best is None or a>best[0]): best=(a,b,isstruct)
        return best
    def func_at(s,p):
        for a,b,n,par in s.fb:
            if a<p<b: return (a,b,n,par)
        return None
PDECL=re.compile(r'(?m)^([ \t]*)((?:static\s+|thread_local\s+|inline\s+)*)(?:const\s+)?(?:volatile\s+)?([A-Za-z_][\w:]*)\s*\*\s*(\w+)\s*(?:=[^;]*|\{[^;]*\})?;')
CDECL=re.compile(r'(?m)^([ \t]*)((?:static\s+|thread_local\s+|inline\s+)*)(std::(?:vector|array|unordered_map|unordered_set|map|set|deque)<[^;]*?>)\s+(\w+)\s*(?:\[[^\]]*\])?\s*(?:=[^;]*|\{[^;]*\})?;')
PSKIP={'FILE','char','SDL_Window','SDL_GameController','void','CONTEXT','SYMBOL_INFO','RT64'}
def scope_of(F,p,q):
    """False = not a static object; None = namespace scope; (a,b) = enclosing block of a function-local static"""
    bl=F.block_at(p)
    if bl is None:
        return ('FILE',) if re.search(r'\bstatic\b',q) or in_anon(F,p) else None
    if bl[2]: return False
    if 'static' not in q and 'thread_local' not in q: return False
    return (bl[0],bl[1])
def in_anon(F,p):
    pre=F.s[:p]
    return bool(re.search(r'namespace\s*\{',pre)) and pre.count('namespace {')>pre.count('} // namespace')
def analyze(files):
    statics=[]  # (file, name, declpos, scope(a,b) or None)
    for F in files:
        for R,kind in ((PDECL,'ptr'),(CDECL,'cont')):
            for m in R.finditer(F.s):
                q=m.group(2)
                if kind=='ptr' and m.group(3) in PSKIP: continue
                sc=scope_of(F,m.start(),q)
                if sc is False: continue
                statics.append((F,m.group(4),m.start(),sc))
                KIND[(F.path,m.group(4))]=kind
    for F in files:
        for m in DECL.finditer(F.s):
            q=m.group(2); typ=m.group(3); body=m.group(4)
            if 'const' in F.s[max(0,m.start()-1):m.start(3)] : continue
            sc=scope_of(F,m.start(),q)
            if sc is False: continue
            for nm in declarators(body):
                if nm in ('const','volatile'): continue
                statics.append((F,nm,m.start(),sc))
    return statics
def func_info(F,fn):
    a,b,name,par=fn
    body=F.s[a:b]
    # params
    params=set()
    for p in par.split(','):
        ids=re.findall(r'\b\w+\b',p)
        if ids: params.add(ids[-1])
    bases={'rdram','RDRAM'}
    for p in par.split(','):
        if re.search(r'uint8_t\s*\*',p):
            ids=re.findall(r'\b\w+\b',p); bases.add(ids[-1])
    o=F.func_at(a+1); ob=F.s[o[0]:o[1]] if o else body
    for m in re.finditer(r'uint8_t\s*\*\s*(\w+)\s*=',ob): bases.add(m.group(1))
    if o:
        for p in o[3].split(','):
            if re.search(r'uint8_t\s*\*',p): bases.add(re.findall(r'\b\w+\b',p)[-1])
    for m in re.finditer(r'\bauto\s+(\w+)\s*=\s*(?:\(\s*)?(?:const\s+)?(?:volatile\s+)?(?:uint8_t\s*\*\s*\)?)?\s*\(?\s*(?:rdram|RDRAM)\b(?!\s*\[)',body): bases.add(m.group(1))
    bases={x for x in bases if 'dmem' not in x.lower() and 'imem' not in x.lower()}
    return body,params,bases
def deref_re(bases,acc):
    B='|'.join(sorted(map(re.escape,bases)))
    A='|'.join(sorted(map(re.escape,acc)))
    return B,A
def find_accessors(files):
    """top-level functions and lambdas whose body touches guest memory with one of their params"""
    acc=set(['TO_PTR','MEM_W','MEM_WU','MEM_H','MEM_HU','MEM_B','MEM_BU','MEM_D','MEM_DU','rs64_rdram_u8','rs64_rdram_u16','rs64_rdram_u32','rdram_be32','rdram_be16','rdram_be32_at','rdram_be16_at'])
    for F in files:
        for fn in F.fb:
            a,b,name,par=fn
            if name=='<init>': continue
            body,params,bases=func_info(F,fn)
            B='|'.join(map(re.escape,bases))
            for p in params:
                if re.search(r'(?:\b(?:'+B+r')\s*(?:\[|\+)[^;\]]*\b'+p+r'\b)|\b'+GACC+r'\s*\([^;]*\b'+p+r'\b',body): acc.add(name); break
        for m in re.finditer(r'\bauto\s+(\w+)\s*=\s*\[[^\]]*\]\s*\(([^)]*)\)[^{;]*\{',F.s):
            st=m.end(); d=1; j=st
            while j<len(F.s) and d: d+= {'{':1,'}':-1}.get(F.s[j],0); j+=1
            lb=F.s[st:j]; ps=[re.findall(r'\w+',p)[-1] for p in m.group(2).split(',') if re.findall(r'\w+',p)]
            for p in ps:
                if re.search(r'(?:\b(?:rdram|RDRAM|rd|r|q|rr|p|base)\s*(?:\[|\+)[^;\]]*\b'+p+r'\b)|\b'+GACC+r'\s*\([^;]*\b'+p+r'\b|\b(?:rs64_rdram_u\d+|rdram_be\d+)\s*\([^;]*\b'+p+r'\b',lb): acc.add(m.group(1)); break
    acc.discard('<init>')
    return acc

def calls(body,names):
    if not names: return
    for m in re.finditer(r'\b('+'|'.join(map(re.escape,sorted(names)))+r')\s*\(',body):
        j=m.end(); d=1
        while j<len(body) and d:
            d+={'(':1,')':-1}.get(body[j],0); j+=1
        yield m.start(), m.group(1), body[m.end():j-1]
def base_idx(body,bases):
    B='|'.join(map(re.escape,sorted(bases)))
    for m in re.finditer(r'\b('+B+r')\s*(\[|\+)',body):
        if m.start()>0 and body[m.start()-1] in '.>': continue
        if m.group(2)=='[':
            j=m.end(); d=1
            while j<len(body) and d: d+={'[':1,']':-1}.get(body[j],0); j+=1
            yield m.start(), body[m.end():j-1]
        else:
            e=re.match(r'[^;,)]*',body[m.end():]).group(0)
            if e.strip().startswith('('):
                j=m.end()+body[m.end():].find('(')+1; d=1
                while j<len(body) and d: d+={'(':1,')':-1}.get(body[j],0); j+=1
                e=body[m.end():j]
            yield m.start(), e
def fixpoint(body,seed,extra_src=None):
    S=set(seed)
    st=[x.group(0) for x in stmts(body)]
    for _ in range(6):
        grow=False
        for t in st:
            for m in re.finditer(r'(?:\b(?:auto|uint32_t|int32_t|uint64_t|int64_t|gpr|u32|s32|unsigned|int|uintptr_t)\s+)?\b([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*=(?!=)(.*)',t):
                lhs,rhs=m.group(1),m.group(2)
                if lhs in S: continue
                if (idents(rhs)&S) or (extra_src and extra_src(rhs)):
                    S.add(lhs); grow=True
        for m in re.finditer(r'\bfor\s*\(\s*(?:const\s+)?(?:auto|[\w:]+)\s*&?\s*(?:\[\s*(\w+)\s*,\s*(\w+)\s*\]|(\w+))\s*:\s*([^)]*)\)',body):
            if idents(m.group(4))&S:
                for g in (m.group(1),m.group(2),m.group(3)):
                    if g and g not in S: S.add(g); grow=True
        if not grow: break
    return S
def shadows(G,fn,nm):
    body=G.s[fn[0]:fn[1]]
    if nm in [ (re.findall(r'\w+',p) or [''])[-1] for p in fn[3].split(',')]: return True
    return bool(re.search(r'(?:\b(?:auto|uint\d+_t|int\d+_t|gpr|u32|s32|unsigned|int|bool|float|double|size_t|uintptr_t|char)\b|\*|&)\s*'+nm+r'\s*(?:=|;|\[|\{|,|\))',body) or re.search(r'\[[^\]]*\]\s*\([^)]*\b'+nm+r'\s*\)',body))
def census(files, verbose=False):
    TMEMO.clear(); KIND.clear()
    acc=find_accessors(files)
    st=analyze(files)
    capnames=set()
    for rnd in range(4):
        rows=one_round(files,acc,st,capnames)
        nn={r['name'] for r in rows}
        if nn==capnames: break
        capnames=nn
    return finish(files,acc,rows)
def one_round(files,acc,st,capnames):
    rows=[]
    for F,nm,dp,scope in st:
        users=[]
        if scope and scope[0]!='FILE':
            fn=F.func_at(scope[0]+1) or (scope[0],scope[1],'<block>','')
            if fn[2]=='<init>': fn=(scope[0],scope[1],'<block>','')
            users=[(F,(scope[0],scope[1],fn[2],fn[3]))]
        else:
            for G in files:
                if scope and G is not F: continue
                if nm not in G.ids: continue
                for k,fn in enumerate(G.fb):
                    if fn[2]=='<init>': continue
                    if nm in G.fids[k] and not shadows(G,fn,nm): users.append((G,fn))
            if F.s[dp:].find(nm)>=0 and re.search(r'\bstatic\b',F.s[dp:dp+60]) is None:
                pass
        # capture
        caps=[]
        for G,fn in users:
            body,params,bases=func_info(G,fn)
            o=G.func_at(fn[0]+1); full=G.s[o[0]:o[1]] if o else body
            src=lambda e: bool(SRC.search(e)) or any(True for _ in calls(e,acc))
            key=(G.path,o[0] if o else fn[0],len(capnames))
            if key not in TMEMO: TMEMO[key]=fixpoint(full, params|capnames, src)
            taint=set(TMEMO[key])
            taint.discard(nm)
            for sm in stmts(body):
                for rhs in assigned(sm.group(0),nm):
                    if SRC.search(rhs) or (idents(rhs)&taint) or any(True for _ in calls(rhs,acc)) or (KIND.get((F.path,nm))=='ptr' and re.search(r'\brdram\b|\btask\b|TO_PTR',rhs)):
                        caps.append((G.path,lineof(G.s,fn[0]+sm.start())))
        if not caps: continue
        rows.append(dict(F=F,name=nm,decl=lineof(F.s,dp),scope=scope,caps=caps,users=users))
    return rows
def finish(files,acc,rows):
    # getters
    getters=collections.defaultdict(set)
    for r in rows:
        for G,fn in r['users']:
            body=G.s[fn[0]:fn[1]]
            if fn[2]!='<init>' and re.search(r'\breturn\b[^;]*\b'+r['name']+r'\b',body): getters[r['name']].add(fn[2])
    for r in rows:
        ders=[]
        gs=getters[r['name']]
        funs=list(r['users'])
        if gs:
            for G in files:
                if not (set(gs)&G.ids): continue
                for fn in G.fb:
                    if fn[2]!='<init>' and re.search(r'\b('+'|'.join(gs)+r')\s*\(',G.s[fn[0]:fn[1]]) and (G,fn) not in funs: funs.append((G,fn))
        for G,fn in funs:
            body,params,bases=func_info(G,fn)
            seed={r['name']}
            D=fixpoint(body,seed,lambda e: any(True for _ in calls(e,gs)) if gs else None)
            for p,cn,args in calls(body,acc):
                if idents(args)&D or any(True for _ in calls(args,gs)):
                    ders.append((G.path,lineof(G.s,fn[0]+p),cn))
            for p,e in base_idx(body,bases):
                if idents(e)&D: ders.append((G.path,lineof(G.s,fn[0]+p),'rdram'))
            if KIND.get((r['F'].path,r['name']))=='ptr':
                for m in re.finditer(r'(?:\*\s*|\b)('+'|'.join(map(re.escape,D))+r')\s*(?:\[|->)|\*\s*('+'|'.join(map(re.escape,D))+r')\b',body):
                    ders.append((G.path,lineof(G.s,fn[0]+m.start()),'ptr'))
        r['ders']=sorted(set(ders)); r['getters']=sorted(gs)
    return rows,acc
def load(paths=None,overrides=None):
    paths=paths or sorted(glob.glob('src/main/*.cpp')+glob.glob('src/main/*.mm'))
    out=[]
    for p in paths:
        t=(overrides or {}).get(p) or open(p,errors='replace').read()
        out.append(File(p,t))
    return out

ROOTS_EXT = ['lib/N64ModernRuntime/ultramodern/src', 'lib/N64ModernRuntime/librecomp/src', 'lib/rt64/src']
EXT_GLOBS = ['tools/fixup_*.py', 'tools/apply_*.py']

# (file basename, static) -> (class, [proof regexes that must be in that file], why).  H-gated: proof regexes are the gate
# tokens; EVERY deref site's enclosing function (or a function it calls first) must contain one of them.
RULES = {
 ('main.cpp', 's_pending_task_data_ptr'): ('H-inflight',
    [r'case M_GFXTASK:[^}]*s_pending_task_data_ptr\s*=\s*\(uint32_t\)task->t\.data_ptr;[^}]*return &factor5_gfx_runner;',
     r'case M_AUDTASK:[^}]*s_pending_task_data_ptr = \(uint32_t\)task->t\.data_ptr;'],
    'thread_local, re-set from the OSTask on every get_rsp_microcode (M_GFXTASK/M_AUDTASK) and on the direct path before '
    'factor5_gfx_runner; read only by that task\'s runner on the same thread = the in-flight task data (class GA, s7535)'),
 ('main.cpp', 's_pending_audio_task'): ('H-inflight',
    [r'case M_AUDTASK: \{\s*s_pending_audio_task = task;'],
    'host pointer to the OSTask ultramodern hands get_rsp_microcode (its by-value SpTaskAction copy, class GG), re-set per '
    'audio task, thread_local; readers are the audio ucode hooks of that task on the same thread'),
 ('main.cpp', 'ring'): ('H-gated', [r'ROGUESQ_LOG_S4457', r'rs64_s4457_on\(\)'],
    's4457 next-pointer ring (diag): rs64_s4457_list_check returns unless ROGUESQ_LOG_S4457'),
 ('main.cpp', 'g_m5_task_fault_pending_phys'): ('H-gated', [r'ROGUESQ_LOG_M5_TASK_WRITE_FAULT', r'g_m5_task_fault_pending_phys'],
    'write-fault watcher thread starts only under ROGUESQ_LOG_M5_TASK_WRITE_FAULT; phys is a fault address, read once'),
 ('main.cpp', 'g_s5229_pc'): ('H-host', [r'g_s5229_pc = \(uint32_t\*\)std::calloc'], 'host calloc shadow table indexed by guest phys (ROGUESQ_LOG_S5223_ENTRY_JOIN)'),
 ('main.cpp', 'g_s5229_val'): ('H-host', [r'g_s5229_val = \(uint8_t\*\)std::calloc'], 'host calloc shadow table'),
 ('main.cpp', 'g_s5229_w'): ('H-host', [r'g_s5229_w = \(uint8_t\*\)std::calloc'], 'host calloc shadow table'),
 ('rt64_render_context.cpp', 's_ti_w1'): ('H-gated', [r'ROGUESQ_LOG_G1D_CMD', r'if \(s_cmd_log\)'],
    'SETTIMG w1 of the RDP stream being submitted (s6230 probe), inside the s_cmd_log (ROGUESQ_LOG_G1D_CMD) block'),
 ('main.cpp', 's_s7781_lo'): ('H-gated', [r'ROGUESQ_S7779_ARENA"', r'if \(!s_s7779_on\) return;'], 's7781/s7783 FB-arena census epoch bounds (diag): s7781_escape and s7783_walk return unless ROGUESQ_S7779_ARENA=1; passed to the s7783 walk/classifier only'),
 ('main.cpp', 's_s7781_hi'): ('H-gated', [r'ROGUESQ_S7779_ARENA"', r'if \(!s_s7779_on\) return;'], 's7781/s7783 FB-arena census epoch bounds (diag): s7781_escape and s7783_walk return unless ROGUESQ_S7779_ARENA=1; passed to the s7783 walk/classifier only'),
 ('main.cpp', 's_s7781_last'): ('H-gated', [r'ROGUESQ_S7779_ARENA"', r'if \(!s_s7779_on\) return;'], 's7781/s7783 FB-arena census epoch bounds (diag): s7781_escape and s7783_walk return unless ROGUESQ_S7779_ARENA=1; passed to the s7783 walk/classifier only'),
 ('main.cpp', 's_s7781_lastext'): ('H-gated', [r'ROGUESQ_S7779_ARENA"', r'if \(!s_s7779_on\) return;'], 's7781/s7783 FB-arena census epoch bounds (diag): s7781_escape and s7783_walk return unless ROGUESQ_S7779_ARENA=1; passed to the s7783 walk/classifier only'),
 ('upstream_compat.cpp', 's_s7472_pa'): ('H-gated', [r'ROGUESQ_S7472_HEAPCHK"'],
    's7472 heap-walker planted-block control: s7472_check returns unless ROGUESQ_S7472_HEAPCHK; restore checks the plant is intact'),
 ('upstream_compat.cpp', 's_s7472_pw0'): ('H-gated', [r'ROGUESQ_S7472_HEAPCHK"'], 'as s_s7472_pa'),
 ('upstream_compat.cpp', 's7033_rd'): ('H-base', [r's7033_rd = rdram;'], 'the rdram base pointer; hm/rt are re-read from 0x80136DC0/C4 per call'),
 ('upstream_compat.cpp', 'g_s6127_rd'): ('H-base', [r'g_s6127_rd = rdram;'], 'the rdram base pointer (s6127 freelist walk)'),
 ('main.cpp', 'g_rsp_dma_shadow2_addr'): ('H-gated', [r'getenv\("ROGUESQ_SHADOW2"\)'],
    'ucode-image shadow (gfx task->t.ucode phys), only inside `if (s_sh2 && ucode_addr)` = ROGUESQ_SHADOW2 default off; '
    'read-only compare vs the first capture, <=24 logs, length clamped (s7364)'),
 ('upstream_compat.cpp', 's7031_w'): ('H-refresh', [r's7031_w = \(int\)\(uint16_t\)\(MEM_W\(0, \(int64_t\)\(int32_t\)0x80136DF8\) >> 16\); s7031_hgt',
     r'rs64_s7032_frame\(\); rs64_s7033_frame\(rdram, a0\);', r'const uint32_t hm = \(uint32_t\)MEM_W\(0, \(int64_t\)\(int32_t\)0x80136DC0\)'],
    'terrain dims re-read from the live level header 0x80136DF8 by the per-frame hook before rs64_s7033_frame/hr run; used only '
    'as clamp bounds, the heightmap/record bases hm/rt are re-read from 0x80136DC0/C4 on every call'),
 ('upstream_compat.cpp', 's7031_hgt'): ('H-refresh', [r's7031_hgt = \(int\)\(uint16_t\)MEM_W\(0, \(int64_t\)\(int32_t\)0x80136DF8\);'], 'as s7031_w'),
 # escapes: getters of captured statics referenced outside src/main
 ('upstream_compat.cpp', 's7567_keep'): ('H-value', [r's7567_keep = live && !dda; return s7567_keep;'], 's7567/s6919: 0/1 flag (CUT_LIVE live && !dda) returned to the s6919 fixup and counted by the ROGUESQ_S7567_CUTW witness; not a guest value (row added s7608)'),
 ('main.cpp', 'g_rs64_m5_pcm_callsite'): ('H-value', [r'rs64_m5_pcm_get_callsite'], 'guest PC (code address), printed by librecomp rsp.cpp'),
 ('main.cpp', 'g_rs64_audio_break_pc'): ('H-value', [r'rs64_audio_image_break_pc'], 'guest PC, printed by librecomp rsp.cpp'),
 ('main.cpp', 'g_rs64_m5_static_rs_memset_callsite'): ('H-value', [r'rs64_m5_static_rs_memset_last_callsite'], 'guest PC, printed by the s2447 fixup diag'),
 ('main.cpp', 'g_rs64_m5_static_rs_memset_ra'): ('H-value', [r'rs64_m5_static_rs_memset_last_ra'], 'guest RA, printed by the s2447 fixup diag'),
 ('main.cpp', 'lo'): ('H-value', [r'lo = \(uint32_t\)std::strtoul\(e'], 'VI window bound parsed from ROGUESQ_S6848_FORCE_OVL (getter match is `return hi > lo`)'),
 ('upstream_compat.cpp', 's6919_org'): ('H-value', [r'tools/apply_s6919_cutlive.py@@union \{ uint32_t u; float f; \} c; c\.u = org6418',
                                                   r's6919_org = org;'],
    'far-cutoff float bits latched from 0x8009DEB4 (s6418/s6919), handed back to the patched guest as a float value, never an address'),
 ('upstream_compat.cpp', 's6919_lastb'): ('H-value', [r'tools/apply_s6919_cutlive.py@@org6418 = rs64_s6919_base\(org6418, \(uint32_t\)MEM_W\(0, \(int64_t\)\(int32_t\)0x8009DEB4\)',
                                                     r'if \(cur != s6919_lastw\) s6919_lastb = cur;'],
    'the game\'s live far-cutoff float bits (cur = *0x8009DEB4), returned as a value; ROGUESQ_DD_CUT_LIVE default off'),
 ('upstream_compat.cpp', 's6893_cap'): ('H-value', [r'return count < s6893_cap \? count : s6893_cap - 1;'], 'tile slot index clamp (count)'),
}

def ext_texts(extra=None):
    out = []
    for r in ROOTS_EXT:
        for p in glob.glob(r + '/**/*', recursive=True):
            if p.endswith(('.cpp', '.c', '.h', '.hpp', '.cc')): out.append((p, open(p, errors='replace').read()))
    for g in EXT_GLOBS:
        for p in sorted(glob.glob(g)): out.append((p, open(p, errors='replace').read()))
    return out + list(extra or [])

def outer_text(G, line):
    pos = sum(len(x) + 1 for x in G.s.split('\n')[:line - 1])
    fn = G.func_at(pos)
    return G.raw[fn[0]:fn[1]] if fn else ''

def classify(files, rules=RULES, ext_extra=None):
    rows, acc = census(files)
    ext = ext_texts(ext_extra)
    byp = {F.path: F for F in files}
    res = []; seen = set()
    for r in rows:
        base = os.path.basename(r['F'].path); key = (base, r['name'])
        esc = sorted({p for g in r['getters'] for p, t in ext if re.search(r'\b' + re.escape(g) + r'\b', t)})
        r['esc'] = esc
        if not r['ders'] and not esc:
            r['cls'] = 'H-diag'; r['why'] = 'captured, no deref, no escape'; res.append(r); continue
        if key not in rules:
            r['cls'] = 'UNCLASSIFIED'; r['why'] = 'deref/escape with no rule'; res.append(r); continue
        seen.add(key)
        cls, proofs, why = rules[key]
        r['cls'] = cls; r['why'] = why
        txt = r['F'].raw
        if cls == 'H-gated':
            if not any(re.search(p, txt) for p in proofs): r['cls'] = 'DRIFT'; r['why'] = 'gate token missing from file'
            for p, l, c in r['ders']:
                ot = outer_text(byp[p], l)
                if not any(re.search(q, ot) for q in proofs) and not gated_callee(byp[p], ot, proofs):
                    r['cls'] = 'DRIFT'; r['why'] = 'deref at %s:%d not under the gate' % (os.path.basename(p), l)
        else:
            for p in proofs:
                t2 = txt
                if '@@' in p:
                    fp, p = p.split('@@', 1); t2 = open(fp, errors='replace').read() if os.path.exists(fp) else ''
                if not re.search(p, t2, re.S): r['cls'] = 'DRIFT'; r['why'] = 'proof regex missing: ' + p[:60]
        res.append(r)
    for key in rules:
        if key not in seen:
            res.append(dict(F=None, name=key[1], decl=0, caps=[], ders=[], getters=[], esc=[], cls='DRIFT',
                            why='rule row %s:%s not found as a dereferenced/escaping capture' % key))
    return res

def gated_callee(G, ot, proofs):
    """the deref function returns early through a gate helper whose body holds the gate token (e.g. if (!rs64_x_on()) return)"""
    for m in re.finditer(r'if\s*\(\s*!\s*(\w+)\s*\(\s*\)[^)]*\)\s*return', ot):
        for a, b, n, p in G.fb:
            if n == m.group(1) and any(re.search(q, G.raw[a:b]) for q in proofs): return True
    return False

PLANT = """
static uint32_t s_gh_plant = 0;
extern "C" void rs64_gh_plant_set(uint8_t* rdram, uint32_t a0) { s_gh_plant = (uint32_t)MEM_W(0, (int64_t)(int32_t)a0); }
extern "C" uint32_t rs64_gh_plant_use(uint8_t* rdram) { const uint32_t p = s_gh_plant; return (uint32_t)MEM_W(4, (int64_t)(int32_t)p); }
"""
PLANT_PTR = """
static uint8_t* s_gh_pp = nullptr;
extern "C" void rs64_gh_pp_set(uint8_t* rdram, uint32_t a0) { s_gh_pp = rdram + (a0 & 0x7FFFFFu); }
extern "C" uint32_t rs64_gh_pp_use() { return s_gh_pp[3]; }
"""
PLANT_DIAG = """
static uint32_t s_gh_diag = 0;
extern "C" void rs64_gh_diag_set(uint8_t* rdram, uint32_t a0) { s_gh_diag = (uint32_t)MEM_W(0, (int64_t)(int32_t)a0); }
extern "C" void rs64_gh_diag_print() { std::fprintf(stderr, "%08X", s_gh_diag); }
"""
PLANT_ESC = """
static std::atomic<uint32_t> s_gh_esc{0};
extern "C" void rs64_gh_esc_set(RecompContext* ctx) { s_gh_esc.store((uint32_t)ctx->r4); }
extern "C" uint32_t rs64_gh_esc_get() { return s_gh_esc.load(); }
"""
PLANT_TAINT = """
static uint32_t s_gh_t2 = 0;
extern "C" void rs64_gh_t2_set(uint8_t* rdram, uint32_t node) { uint32_t a = (uint32_t)MEM_W(0, (int64_t)(int32_t)node); uint32_t b = a + 8u; s_gh_t2 = b; }
extern "C" uint32_t rs64_gh_t2_use(uint8_t* rdram) { uint32_t q = s_gh_t2; uint32_t z = q & 0x7FFFFFu; return rdram[z ^ 3]; }
"""

def find(res, name):
    return [r for r in res if r['name'] == name]

def run_controls():
    UC = 'src/main/upstream_compat.cpp'
    base = open(UC).read()
    paths = sorted(glob.glob('src/main/*.cpp') + glob.glob('src/main/*.mm'))
    def go(over=None, rules=RULES, ext=None):
        return classify(load(paths, over), rules, ext)
    out = []
    def chk(n, ok, msg): out.append(ok); print('control %d %s: %s' % (n, 'PASS' if ok else 'FAIL', msg))
    r = go({UC: base + PLANT}); c = [x['cls'] for x in find(r, 's_gh_plant')]
    chk(1, c == ['UNCLASSIFIED'], 'planted MEM_W capture + later MEM_W deref -> %s' % c)
    r = go({UC: base + PLANT_PTR}); c = [x['cls'] for x in find(r, 's_gh_pp')]
    chk(2, c == ['UNCLASSIFIED'], 'planted rdram+guest pointer static + later p[3] -> %s' % c)
    r = go({UC: base + PLANT_DIAG}); c = [x['cls'] for x in find(r, 's_gh_diag')]
    chk(3, c == ['H-diag'], 'planted print-only capture -> %s' % c)
    r = go({UC: base + PLANT_ESC}, ext=[('tools/fake_fixup.py', 'ctx->r4 = rs64_gh_esc_get();')]); c = [(x['cls'], x['esc']) for x in find(r, 's_gh_esc')]
    chk(4, [k for k, _ in c] == ['UNCLASSIFIED'], 'planted getter used by injected C -> %s' % c)
    r = go({UC: base + PLANT_TAINT}); c = [x['cls'] for x in find(r, 's_gh_t2')]
    chk(5, c == ['UNCLASSIFIED'], 'two-hop local taint capture + derived-local rdram[] deref -> %s' % c)
    R2 = dict(RULES); del R2[('upstream_compat.cpp', 's_s7472_pa')]
    r = go(rules=R2); c = [x['cls'] for x in find(r, 's_s7472_pa')]
    chk(6, c == ['UNCLASSIFIED'], 'deleted rule s_s7472_pa -> %s' % c)
    r = go({UC: base.replace('"ROGUESQ_S7472_HEAPCHK"', '"ROGUESQ_S7472_XHEAPCHK"')}); c = [x['cls'] for x in find(r, 's_s7472_pa')]
    chk(7, c == ['DRIFT'], 'gate token renamed -> %s' % c)
    r = go({UC: base.replace('g_s6127_rd = rdram;', 'g_s6127_rd = rdram + 4;')}); c = [x['cls'] for x in find(r, 'g_s6127_rd')]
    chk(8, c == ['DRIFT'], 'H-base proof broken -> %s' % c)
    R3 = dict(RULES); R3[('main.cpp', 'no_such_static')] = ('H-value', [], 'x')
    r = go(rules=R3); c = [x['cls'] for x in find(r, 'no_such_static')]
    chk(9, c == ['DRIFT'], 'stale rule row -> %s' % c)
    r = go(); bad = [x for x in r if x['cls'] in ('OPEN', 'UNCLASSIFIED', 'DRIFT')]
    chk(10, not bad, 'real tree: %d bad rows' % len(bad))
    print('controls %d/%d' % (sum(out), len(out)))
    return 0 if all(out) else 1

def main():
    os.chdir(REPO)
    if '--controls' in sys.argv: sys.exit(run_controls())
    res = classify(load())
    cnt = collections.Counter(r['cls'] for r in res)
    kinds = collections.Counter(KIND.get((r['F'].path, r['name']), 'int') for r in res if r['F'])
    print('[s7548-gh] captured statics=%d kinds=%s classes=%s' % (len(res), dict(kinds), dict(cnt)))
    for r in res:
        if r['cls'] == 'H-diag' and '-v' not in sys.argv: continue
        f = os.path.basename(r['F'].path) if r['F'] else '-'
        print('  %-12s %s:%d %s caps=%s ders=%d esc=%s | %s' % (r['cls'], f, r['decl'], r['name'],
              [c[1] for c in r['caps']][:3], len(r['ders']), [os.path.basename(e) for e in r['esc']], r['why'][:110]))
    bad = cnt['OPEN'] + cnt['UNCLASSIFIED'] + cnt['DRIFT']
    print('[s7548-gh] rc=%d' % (1 if bad else 0))
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
