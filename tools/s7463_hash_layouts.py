"""s7463 class DS: record layouts of every struct hashed or memcmp-ed by raw bytes (rerun after an rt64 edit; padding must be routed through rs64_s7463_hash)."""
import sys,json,re,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
m=__import__('s7463_uninit_census')
cc=json.load(open(m.CC))
want={'lib/rt64/src/hle/rt64_game_frame.cpp':['CallMatchKey'],'lib/rt64/src/hle/rt64_framebuffer.cpp':['FramebufferTile'],
 'lib/rt64/src/render/rt64_shader_common.cpp':['ShaderDescription'],'lib/rt64/src/preset/rt64_preset_draw_call.cpp':['DrawCallKey'],
 'lib/rt64/src/render/rt64_render_target_manager.cpp':['RenderTargetKey','RenderFramebufferKey'],'lib/rt64/src/hle/rt64_state.cpp':['ReinterpretHashData']}
for e in cc:
    r=m.rel(e['file'])
    if r not in want: continue
    rc,out=m.run(m.base_args(e)+['-fsyntax-only','-w','-Xclang','-fdump-record-layouts-complete'],e['directory'])
    _,o2=m.run(m.base_args(e)+['-fsyntax-only','-w','-Xclang','-fdump-record-layouts-complete'],e['directory'])
    p=subprocess=None
    import subprocess
    p=subprocess.run(m.base_args(e)+['-fsyntax-only','-w','-Xclang','-fdump-record-layouts-complete'],cwd=e['directory'],capture_output=True,text=True,errors='replace')
    txt=p.stdout
    blocks=txt.split('*** Dumping AST Record Layout')
    for name in want[r]:
        for b in blocks:
            hdr=b.strip().splitlines()[0:2]
            if any(re.search(r'\b(struct|class) (\w+::)*'+name+r'\b',h) for h in hdr):
                print('==',r,name); print('\n'.join(b.strip().splitlines()[:60])); break
        want[r]=[x for x in want[r] if x!=name]
