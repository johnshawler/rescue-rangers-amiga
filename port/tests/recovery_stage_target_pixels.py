"""Independent original-device per-pixel reference, including horizontal wrap."""
import struct
from recovery_resident_chr_fade_target_oracle import SerialMapper
def expected(rom,reference):
 results,bus,_=reference
 nt=bytearray(2048);pal=bytearray(32);oam=bytearray(256)
 mapper=SerialMapper();ctrl=mask=latch=sx=sy=oa=v=hi=lastlo=0;dma=iter(bus.dma)
 ppu_count=mapper_count=0
 for e in bus.events:
  if e[0]=='mapper':mapper.write(e[1],e[2]);mapper_count+=1;continue
  if e[0]!='ppu':continue
  ppu_count+=1;a,d=e[1:3]
  if a==0x2002:latch=0
  elif a==0x2000:ctrl=d
  elif a==0x2001:mask=d
  elif a==0x2003:oa=d
  elif a==0x2005:
   if latch:sy=d
   else:sx=d
   latch^=1
  elif a==0x2006:
   if latch:v=(hi<<8)|d;lastlo=d
   else:hi=d&63
   latch^=1
  elif a==0x2007:
   addr=v&0x3fff
   assert addr>=0x2000
   if addr>=0x3f00:
    p=addr&31
    if p in (16,20,24,28):p-=16
    pal[p]=d&63
   else:
    logical=(addr&0xfff)//1024;mode=mapper.control&3
    physical=(0,1,logical&1,logical>>1)[mode]
    nt[physical*1024+(addr&1023)]=d
   v=(v+(32 if ctrl&4 else 1))&0x7fff
  elif a==0x4014:
   assert d==2
   values=next(dma)
   for i,value in enumerate(values):oam[(oa+i)&255]=value
  else:raise AssertionError(hex(a))
 assert ctrl in (0x90,0x91) and mask==0x1e and sy==0 and mapper.control==0x1e
 chrdata=b''.join(rom[16+131072+n*4096:16+131072+(n+1)*4096] for n in (mapper.chr0,mapper.chr1))
 frame=bytearray(51200);opacity=bytearray(7680)
 # Independent per-pixel composition, not the native tile-cache algorithm.
 for y in range(240):
  candidates=[i for i in range(64) if 0<=y-oam[4*i]-1<8][:8]
  for x in range(256):
   world=(x+sx+256*(ctrl&1))%512
   tx,ty=(world%256)//8,y//8;base=(world//256)*1024
   tile=nt[base+ty*32+tx]
   at=nt[base+960+(ty//4)*8+tx//4]
   palette=(at>>((ty%4//2)*4+(tx%4//2)*2))&3
   row=4096+tile*16+y%8;bit=7-world%8
   bg=((chrdata[row]>>bit)&1)|(((chrdata[row+8]>>bit)&1)<<1)
   color=palette*4+bg
   if bg:opacity[y*32+x//8]|=128>>(x%8)
   for i in candidates:
    yy,t,attr,xx=oam[4*i:4*i+4]
    if not xx<=x<xx+8:continue
    dy,dx=y-yy-1,x-xx
    if attr&128:dy=7-dy
    if attr&64:dx=7-dx
    row=t*16+dy
    pixel=((chrdata[row]>>(7-dx))&1)|(((chrdata[row+8]>>(7-dx))&1)<<1)
    if not pixel:continue
    if not (attr&32 and bg):color=16+4*(attr&3)+pixel
    break
   for p in range(5):
    if color&(1<<p):frame[p*10240+(y+8)*40+(x+32)//8]|=128>>(x%8)
 state=bytes((ctrl,mask,latch,sx,sy,oa))+struct.pack('>HH',v,(hi<<8)|lastlo)+bytes((mapper.control,mapper.chr0,mapper.chr1,mapper.prg,0,0))+struct.pack('>III',0,ppu_count,mapper_count)
 # Preserve the actual last PPUADDR low byte independently of incremented v.
 return results,nt,pal,oam,chrdata,frame,opacity,state
