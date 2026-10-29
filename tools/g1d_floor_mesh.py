"""Compare emitted RasterVS vertices with RDP screen-space coefficient planes.

Independent semantics: https://www.libretro.com/index.php/parallel-rdp-how-the-upscaled-rendering-works/
RGBA is affine in screen coordinates, STW is affine before ST/W. This
floating-point comparison is not a fixed-point hardware replay.
"""
import json
import math
import pathlib
import sys
import os
import g1d_floor_inputs as base

ROOT = pathlib.Path.cwd() / 'scratch/agent/s6621_mesh'


def bary(v, x, y):
    a, b, c = v
    den = (b[1]-c[1])*(a[0]-c[0]) + (c[0]-b[0])*(a[1]-c[1])
    if abs(den) < 1e-12:
        return None
    p = ((b[1]-c[1])*(x-c[0]) + (c[0]-b[0])*(y-c[1]))/den
    q = ((c[1]-a[1])*(x-c[0]) + (a[0]-c[0])*(y-c[1]))/den
    return p, q, 1-p-q


def interpolate(v, weights, perspective=True):
    if perspective:
        ws = [b/a[3] for a, b in zip(v, weights)]
        den = sum(ws)
        if abs(den) < 1e-20:
            return None
        ws = [a/den for a in ws]
    else:
        ws = weights
    return [sum(a[k]*b for a,b in zip(v, ws)) for k in range(4,10)]


def plane_at(t, x, y):
    e, p = t['edge'], t['plane']
    dy = y - e[0]
    dx = x - (e[2] + e[3]*dy)
    vals = [p[k] + p[k+1]*dy + p[k+2]*dx for k in range(0,21,3)]
    if abs(vals[2]) < 1e-20:
        return None
    return [vals[0]/vals[2]*1024, vals[1]/vals[2]*1024] + vals[3:]


def shade_luma(vals, wrap=False):
    c = vals[2:5]
    if wrap:
        c = [a % 256 for a in c]
    return sum(a*b for a,b in zip(c,(.2126,.7152,.0722)))


def as_units(values):
    return values[:2] + [x*255 for x in values[2:]]


def boundary_distance(v, weights):
    i=min(range(3),key=lambda i:weights[i])
    j,k=(i+1)%3,(i+2)%3
    area=abs((v[1][0]-v[0][0])*(v[2][1]-v[0][1])-(v[2][0]-v[0][0])*(v[1][1]-v[0][1]))
    length=math.dist(v[j][:2],v[k][:2])
    return max(0.,-weights[i])*area/length if length else float('inf')


def selftest():
    base.selftest()
    v = [[0,0,0,1,0,0,.2,.4,.6,1], [4,0,0,1,4,0,.2,.4,.6,1], [0,4,0,1,0,4,.2,.4,.6,1]]
    for i in range(3):
        got = interpolate(v,bary(v,*v[i][:2]))
        assert max(abs(a-b) for a,b in zip(got,v[i][4:])) < 1e-10
    assert boundary_distance(v,bary(v,-1,1)) > .125
    assert boundary_distance(v,bary(v,-.01,1)) < .125
    ref = interpolate(v,bary(v,1,1))
    assert abs(ref[0]-1) < 1e-10 and abs(ref[1]-1) < 1e-10
    v[2][3] = 4
    v[2][4] = 40
    pert = interpolate(v,bary(v,1,1))
    assert abs(ref[0]-pert[0]) > 2
    smooth = [interpolate(v,bary(v,1,y/10))[0] for y in range(1,20)]
    altered = []
    for i in range(19):
        row = [r[:] for r in v]
        if i%2:
            row[2][3] = .25
            row[2][4] = 400
        altered.append(interpolate(row,bary(row,1,(i+1)/10))[0])
    step = lambda a: sum(abs(x-y) for x,y in zip(a,a[1:]))/(len(a)-1)
    assert step(altered) > 10*step(smooth)
    print(json.dumps(dict(mesh_selftest='passed', vertex_uv_w_control=pert[0],
                         smooth_step=step(smooth), injected_step=step(altered))), flush=True)


def score(path, sample_offset=0.0):
    frames = {}
    with path.open(errors='replace') as f:
        for line in f:
            if line.startswith('[floor-mesh] '):
                t = json.loads(line[len('[floor-mesh] '):])
                frames.setdefault(t['frame'], []).append(t)
    results=[]
    # A later frame closes the preceding command sequence.
    for frame, tris in sorted(frames.items())[:-1]:
        coeff, mesh, affine = {}, {}, {}
        vertex_error=0
        for t in tris:
            v=[t['v'][i:i+10] for i in (0,10,20)]
            e=t['edge']; w=t['w']
            for vi in v:
                expected=plane_at(t,*vi[:2])
                if expected:
                    vertex_error=max(vertex_error,max(abs(a-b) for a,b in zip(expected,as_units(vi[4:]))))
            for row in range(180,251):
                y=row+sample_offset
                if not (e[8] <= y <= e[9] and e[11] <= y <= e[13]):
                    continue
                major=e[2]+e[3]*(y-e[0])
                minor=e[4]+e[5]*(y-e[0]) if y <= e[1] else e[6]+e[7]*(y-e[1])
                lo,hi=sorted((major,minor))
                for col,x in enumerate((16.,w-17.)):
                    if not e[10] <= x <= e[12]:
                        continue
                    key=(row,col)
                    if lo <= x <= hi:
                        coeff[key]=plane_at(t,x,y)
                    b=bary(v,x,y)
                    if b is not None and min(b) >= -1e-7:
                        m=interpolate(v,b, bool(t['flags'][18]))
                        if m is not None:
                            mesh[key]=as_units(m)
                            affine[key]=as_units(interpolate(v,b,False))
        missing=[]
        for key in sorted(set(coeff)^set(mesh)):
            row,col=key; x=(16.,tris[0]['w']-17.)[col]; y=row+sample_offset
            near=[]
            for t in tris:
                v=[t['v'][i:i+10] for i in (0,10,20)]
                b=bary(v,x,y)
                if b is not None:
                    near.append(dict(ordinal=t['ordinal'],min_bary=min(b),distance=boundary_distance(v,b),vxy=[a[:2] for a in v],edge=t['edge']))
            missing.append(dict(row=row,col=col,coefficient=key in coeff,mesh=key in mesh,
                                nearest=sorted(near,key=lambda t:-t['min_bary'])[:1]))
        common=set(coeff)&set(mesh)
        if not common:
            continue
        pairs=[(k,(k[0]+1,k[1])) for k in common if (k[0]+1,k[1]) in common]
        def avg(xs):
            return sum(xs)/len(xs) if xs else None
        def steps(table, channel):
            return avg([abs(channel(table[a])-channel(table[b])) for a,b in pairs])
        results.append(dict(frame=frame,w=tris[0]['w'],origin=tris[0]['origin'],tris=len(tris),
            ncoeff=len(coeff),nmesh=len(mesh),common=len(common),pairs=len(pairs),
            vertex_error=vertex_error,missing=missing,
            uv_error=avg([max(abs(coeff[k][i]-mesh[k][i]) for i in (0,1)) for k in common]),
            shade_error=avg([abs(shade_luma(coeff[k])-shade_luma(mesh[k])) for k in common]),
            affine_error=avg([abs(shade_luma(coeff[k])-shade_luma(affine[k])) for k in common]),
            coeff_S=steps(coeff,lambda a:a[0]),mesh_S=steps(mesh,lambda a:a[0]),
            coeff_T=steps(coeff,lambda a:a[1]),mesh_T=steps(mesh,lambda a:a[1]),
            coeff_L=steps(coeff,shade_luma),mesh_L=steps(mesh,shade_luma),
            coeff_wrap=steps(coeff,lambda a:shade_luma(a,True)),
            mesh_wrap=steps(mesh,lambda a:shade_luma(a,True))))
    keys=('vertex_error','uv_error','shade_error','affine_error','coeff_S','mesh_S','coeff_T','mesh_T','coeff_L','mesh_L','coeff_wrap','mesh_wrap')
    pool={k:sum(r[k] for r in results)/len(results) for k in keys} if results else {}
    out=dict(frames=len(results), samples=sum(r['common'] for r in results),
             min_common=min((r['common'] for r in results),default=0),
             coverage_mismatch=sum(abs(r['ncoeff']-r['nmesh']) for r in results),pool=pool,per_frame=results)
    path.with_name('mesh_summary.json' if sample_offset == 0 else 'mesh_legacy_summary.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='per_frame'}),flush=True)
    return out


def main():
    selftest()
    if '--selftest' in sys.argv:
        return
    ROOT.mkdir(parents=True,exist_ok=True)
    arms=[]
    for aspect,tag,width in [('16:9','wide16',796),('21:9','wide21',1024)]:
        if '--analyze' not in sys.argv:
            os.environ['ROGUESQ_LOG_FLOOR_MESH']='1'
            base.run_arm(aspect,tag,width,ROOT)
        arms.append(dict(actual=score(ROOT/tag/'run.log'), legacy=score(ROOT/tag/'run.log', .5)))
    (ROOT/'comparison.json').write_text(json.dumps(arms,indent=2)+'\n')
    failures=[]
    for tag,arm in zip(('wide16','wide21'),arms):
        old=json.loads((ROOT/tag/'summary.json').read_text())
        failures += [tag+':'+x for x in old['fail']]
        if old['alpha_fill_control'] != 1 or old['crashlines']:
            failures.append(tag+':alpha-fill-or-crash')
        for mode in ('actual','legacy'):
            a=arm[mode]
            # Keep every disagreement in the output. RDP edges quantize at 1/8
            # pixel; reconstructed mesh boundaries can differ within that bin.
            edge_only=all(m['nearest'] and m['nearest'][0]['distance'] <= .125
                          for f in a['per_frame'] for m in f['missing'])
            if a['frames'] < 50 or a['min_common'] < 141 or not edge_only:
                failures.append(tag+':'+mode+':coverage')
    agreement = not failures and all(
        base.agrees(a[mode]['pool']['coeff_'+key],a[mode]['pool']['mesh_'+key])
        for a in arms for mode in ('actual','legacy') for key in ('S','T','L','wrap'))
    mesh_only = not failures and any(
        arms[1]['actual']['pool']['mesh_'+k] > 2*arms[0]['actual']['pool']['mesh_'+k]
        and arms[1]['actual']['pool']['coeff_'+k] <= 2*arms[0]['actual']['pool']['coeff_'+k]
        for k in ('S','T','L','wrap'))
    verdict=dict(verdict='H-witness' if failures else 'H-mesh' if mesh_only else 'H-pipe' if agreement else 'unresolved',
        failures=failures,agreement=agreement,single_source=True,
        limitation='CPU replay of emitted vertices; no independent GPU or hardware replay')
    (ROOT/'verdict.json').write_text(json.dumps(verdict,indent=2)+'\n')
    print(json.dumps(verdict),flush=True)



if __name__ == '__main__':
    main()
