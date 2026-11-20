#!/usr/bin/env python3
"""s7587 class OW: metal-cpp ownership census of plume_metal.cpp (no ARC in that TU).

Enumerates every acquisition and every release/retain, pairs them by the owning variable, and classifies each acquisition:
  +1  alloc()->init() / ->new*() / Copy* / Create* / *_create   -> OK if released somewhere, else LEAK
  +0  factory / getter (NS::String::string, commandBuffer*, *CommandEncoder(), renderPassDescriptor(), nextDrawable)
      -> OVERRELEASE if the variable is released and never retained, NEEDS-POOL if no AutoreleasePool is live in the function
         (the RT64 threads have none: the object sits in the implicit pool until the thread exits), else OK.
A site whose retain/release is gated on rs64MtlOwn() / Rs64OwnPool (the s7587 fix) gets two verdicts: OLD = ROGUESQ_MTL_OWN=0
(upstream), NEW = default. Exit 1 if any NEW verdict is LEAK or OVERRELEASE, or any row is unclassified.
usage: python3 tools/s7587_ownership_census.py [plume_metal.cpp] [--all]
"""
import re, sys

path = next((a for a in sys.argv[1:] if not a.startswith('--')), 'lib/rt64/src/contrib/plume/plume_metal.cpp')
show_all = '--all' in sys.argv
L = open(path).read().split('\n')

FN = re.compile(r'^    (?:[A-Za-z][\w:<>,\s*&]*?[\s*&])?(\w+::~?\w+)\(.*\)\s*(const\s*)?(:.*)?\{\s*$')
PLUS1 = re.compile(r'(::alloc\(\)->init\(|->new[A-Z]\w*\(|\bMTL::Copy\w+\(|\bMTL::Create\w+\(|\bdispatch_\w+_create\(|\bCF\w+Create\()')
# s7725: any class convenience constructor / shared getter `MTL|NS|CA::Class::lowerName(` (not alloc) is +0 too; the s7587 list
# named only a few and missed MTL::TextureDescriptor::textureBufferDescriptor (released by plume -> over-release, s7725 zombies).
PLUS0 = re.compile(r'(NS::String::string\(|->commandBuffer\w*\(|->(blit|compute|render)CommandEncoder\(|::renderPassDescriptor\(\)|->nextDrawable\(\)|\b(?:MTL|NS|CA)::[A-Z]\w+::(?!alloc\b)[a-z]\w*\()')
LHS = re.compile(r'(?:^|[\s(*&])([A-Za-z_][\w.\[\]>-]*?)\s*=\s*[^=]')
DECL = re.compile(r'^\s*(const\s+)?[\w:]+\s*\*\s*\w+\s*=')

def owner(line):
    m = LHS.search(line.split('//')[0])
    if not m: return None
    v = m.group(1)
    v = re.sub(r'^this->', '', v)
    return v.split('.')[-1].split('->')[-1]

# function spans
fns, cur = [], None
for i, l in enumerate(L):
    m = FN.match(l)
    if m:
        if cur: fns.append((cur[0], i, cur[1]))
        cur = (i, m.group(1))
if cur: fns.append((cur[0], len(L), cur[1]))
def fn_of(i):
    for a, b, n in fns:
        if a <= i < b: return a, b, n
    return 0, len(L), '?'

def pooled_before(i, a):
    """Upstream pool live at line i (allocated earlier in the same function, not yet released)."""
    live = False
    for j in range(a, i):
        if 'AutoreleasePool::alloc()->init()' in L[j] and 'rs64MtlOwn' not in L[j] and 'rs64WaitPool' not in L[j] and 'Rs64OwnPool' not in L[j]: live = True
        if re.search(r'\b(releasePool|pool)->release\(\)', L[j]): live = False
    return live

def new_pool(i, a):
    return any(('Rs64OwnPool' in L[j] or ('rs64Pool' in L[j] and 'AutoreleasePool::alloc' in L[j])) for j in range(max(a, i - 6), i + 1))

def gated(j):
    if 'rs64MtlOwn()' in L[j] or 'rs64Pool.p' in L[j]: return True
    for k in range(j - 1, max(-1, j - 7), -1):      # inside an open `if (rs64MtlOwn()) {` block
        if '}' in L[k]: return False
        if 'if (rs64MtlOwn()) {' in L[k]: return True
    return False

def refs(var, pat, scope):
    out = []
    rx = re.compile(r'\b' + re.escape(var) + r'\b[^;]*?' + pat) if pat != 'dr' else re.compile(r'dispatch_release\(\s*' + re.escape(var) + r'\b')
    for j, l in enumerate(L):
        code = l.split('//')[0]
        if rx.search(code) and scope(j): out.append(j)
    return out

# Ownership hand-offs the pairing cannot follow (verified by reading the code, s7587). key = (function, substring of the line).
TRANSFER = {
    ('MetalDescriptorSetLayout::MetalDescriptorSetLayout', 'ArgumentDescriptor::alloc'): 'pushed to argumentDescriptors, released in ~MetalDescriptorSetLayout',
    ('MetalShader::createFunction', 'newFunction('): 'returned +1; callers release (compute/graphics pipeline ctors)',
    ('MetalDescriptorSet::MetalDescriptorSet', '.mtl = device->mtl->newBuffer'): 'argumentBuffer.mtl, released in ~MetalDescriptorSet',
    ('MetalCommandList::getBarrierStageFence', 'newFence()'): 'fences[stage] vector, released in ~MetalCommandList',
    ('MetalDevice::MetalDevice', 'CreateSystemDefaultDevice'): 'member mtl, released in ~MetalDevice (ternary hides the owner)',
    ('MetalDevice::getOrCreateClearRenderPipelineState', 'newRenderPipelineState'): 'clearRenderPipelineStates map, released in ~MetalDevice',
    ('MetalShader::MetalShader', 'NS::String::string(entryPointName'): 'functionName: +0, retained under rs64MtlOwn (OLD = OVERRELEASE)',
}
FIXED_LEAK = {  # +1 never released upstream; s7587 releases or owns them under rs64MtlOwn (OLD = LEAK)
    ('MetalCommandList::clearColor', 'newDepthStencilState'), ('MetalDevice::createClearShaderLibrary', 'clearDepthState ='),
    ('MetalDevice::createClearShaderLibrary', 'clearDepthStencilState ='), ('MetalDevice::createClearShaderLibrary', 'clearStencilState ='),
}
rows = []
for i, l in enumerate(L):
    code = l.split('//')[0]
    if 'AutoreleasePool::alloc' in code: continue
    k = '+1' if PLUS1.search(code) else ('+0' if PLUS0.search(code) else None)
    if not k: continue
    a, b, fname = fn_of(i)
    var = owner(code)
    # +0 objects consumed in-expression (setLabel(NS::String::string(...)), isEqualToString(...)) have no owner
    inline = var is None or not re.search(r'=\s*(\([^)]*\)\s*)?[\w:>.-]*?(' + PLUS0.pattern + '|' + PLUS1.pattern + ')', code)
    cls = fname.split('::')[0]
    if DECL.match(code): scope = lambda j: a <= j < b                     # local: same function
    else: scope = lambda j: fn_of(j)[2].split('::')[0] == cls             # member: any method of the same class
    rel = [] if inline else [j for j in refs(var, r'->release\(\)', scope) + refs(var, 'dr', scope) if j != i]
    ret = [] if inline else [j for j in refs(var, r'->retain\(\)', scope)]
    if '->retain()' in code: ret.append(i)
    # s7725: `if (!rs64MtlOwn()) x->release()` runs only under OLD (upstream); gated() alone read it as NEW-only.
    old_only = lambda j: '!rs64MtlOwn()' in L[j]
    rel_old = [j for j in rel if old_only(j) or not gated(j)]
    rel_new = [j for j in rel if not old_only(j)]
    ret_old = [j for j in ret if old_only(j) or not gated(j)]
    ret_new = [j for j in ret if not old_only(j)]
    def verdict(rels, rets, newp):
        if k == '+1':
            if '->retain()' in code: return 'OK'
            if inline: return 'LEAK'
            return 'OK' if rels else 'LEAK'
        if rels and not rets: return 'OVERRELEASE'
        if pooled_before(i, a) or newp: return 'OK'
        return 'NEEDS-POOL'
    vo = verdict(rel_old, ret_old, False)
    vn = verdict(rel_new, ret_new, new_pool(i, a))
    key = next((t for t in TRANSFER if t[0] == fname and t[1] in code), None)
    if key and 'NS::String::string(entryPointName' in key[1]: vo, vn = 'OVERRELEASE', ('OK' if new_pool(i, a) else 'NEEDS-POOL')
    elif key: vo = vn = 'OK'
    if any(t[0] == fname and t[1] in code for t in FIXED_LEAK): vo, vn = 'LEAK', 'OK'
    if 'rs64WaitPool' in ' '.join(L[a:i]) and k == '+0': vn = 'OK'   # s7585 per-call pool (vo stays: OLD build had no pool)
    rows.append((i + 1, k, fname, var if not inline else '(inline)', vo, vn, len(rel_new), len(ret_new), l.strip()[:90]))

from collections import Counter
co, cn = Counter(r[4] for r in rows), Counter(r[5] for r in rows)
print(f"# {path}: {len(rows)} acquisition sites, {len(fns)} functions")
print("line kind function owner OLD NEW nrel nret | source")
for r in rows:
    if show_all or r[4] != 'OK' or r[5] != 'OK':
        print(f"{r[0]:5d} {r[1]} {r[2]:48s} {r[3]:28s} {r[4]:11s} {r[5]:11s} {r[6]} {r[7]} | {r[8]}")
print("OLD (ROGUESQ_MTL_OWN=0):", dict(co))
print("NEW (default):          ", dict(cn))
bad = [r for r in rows if r[5] in ('LEAK', 'OVERRELEASE')]
sys.exit(1 if bad else 0)
