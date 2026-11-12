# s7189: SETSCISSOR / SETCOLORIMAGE / FILLRECT histograms over an RDP bin: oracle rdplog (RS64_RDP_BIN, 20-B headers, arg2=1) or port RS64_RDP_BIN_PORT (16-B, arg2=0); .zst ok
# usage: s7189_bin_scissor.py BIN[.zst] RETAIL(1|0)
import struct,sys,collections,subprocess
path,retail=sys.argv[1],sys.argv[2]=='1'
raw=subprocess.run(['zstd','-dc',path],capture_output=True).stdout if path.endswith('.zst') else open(path,'rb').read()
H=20 if retail else 16; o=0; parts=[]
while o+H<=len(raw):
    ln=struct.unpack_from('<I',raw,o+(12 if retail else 8))[0]; o+=H; parts.append(raw[o:o+ln]); o+=ln
cat=b''.join(parts); a=0; sc=collections.Counter(); ci=collections.Counter(); fr=collections.Counter()
while a+8<=len(cat):
    w0,w1=struct.unpack_from('<II',cat,a); op=(w0>>24)&0x3F; n=8
    if 8<=op<=15: n=32+(64 if op&4 else 0)+(64 if op&2 else 0)+(16 if op&1 else 0)
    elif op in(0x24,0x25): n=16
    elif op==0x2D: sc[((w0>>12)&0xFFF)/4,(w0&0xFFF)/4,((w1>>12)&0xFFF)/4,(w1&0xFFF)/4]+=1
    elif op==0x3F: ci[(w0&0x3FF)+1]+=1
    elif op==0x36: fr[((w0>>12)&0xFFF)/4,(w0&0xFFF)/4]+=1
    a+=n
print('scissor',sc.most_common(6)); print('cimg',ci.most_common(4)); print('fill lr',fr.most_common(4))
