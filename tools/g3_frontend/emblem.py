# s6780: rebel-emblem presence per frame in the SELECT GAME left/right panels (512x448 coords): count of reddish pixels.
import struct, re, glob, sys
from PIL import Image
def red(im, box):
    c=0
    for r,g,b in im.crop(box).get_flattened_data():
        if r>60 and r>g+25 and r>b+25: c+=1
    return c
L=(70,325,135,390); R=(375,325,445,390)
for S in sys.argv[1:]:
    out=[]
    for m in re.finditer(r'\[fb-dump\] t=\s*([\d.]+)s vi=(\d+) width=1024 .*?-> (\S+)', open(S+'/retail/oracle.log').read()):
        raw=open(m[3],'rb').read(); px=struct.unpack_from('>%dH'%(512*448),raw,0x190000); b=bytearray()
        for v in px: b+=bytes(((v>>11&31)<<3,(v>>6&31)<<3,(v>>1&31)<<3))
        im=Image.frombytes('RGB',(512,448),bytes(b)); out.append(('R'+m[1],red(im,L),red(im,R)))
    for f in sorted(glob.glob(S+'/port/w_*.png')):
        im=Image.open(f).convert('RGB').crop((85,64,1191,1024)).resize((512,448)); out.append(('P'+f[-12:-4],red(im,L),red(im,R)))
    print(S,' '.join('%s:%d/%d'%x for x in out if x[1]+x[2]>0))
