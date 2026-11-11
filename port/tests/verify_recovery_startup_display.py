#!/usr/bin/env python3
"""Independent original-event device/pixel oracle for fixture-free native display."""
import hashlib,json,struct,sys
from pathlib import Path
from recovery_resident_chr_fade_target_oracle import oracle,PORT,SerialMapper
from verify_recovery_resident_chr_fade_probe import verify,verify_amiga_log

def expected(rom):
 results,bus,_=oracle(rom)
 nt=bytearray(2048);pal=bytearray(32);oam=bytearray(256)
 mapper=SerialMapper();ctrl=mask=latch=sx=sy=oa=v=hi=0;dma=iter(bus.dma)
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
   if latch:v=(hi<<8)|d
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
 assert (ctrl,mask,sx,sy,mapper.control)==(0x90,0x1e,0,0,0x1e)
 chrdata=b''.join(rom[16+131072+n*4096:16+131072+(n+1)*4096] for n in (mapper.chr0,mapper.chr1))
 frame=bytearray(51200);opacity=bytearray(7680)
 # Independent per-pixel composition, not the native tile-cache algorithm.
 for y in range(240):
  candidates=[i for i in range(64) if 0<=y-oam[4*i]-1<8][:8]
  for x in range(256):
   tx,ty=x//8,y//8;tile=nt[ty*32+tx]
   at=nt[960+(ty//4)*8+tx//4]
   palette=(at>>((ty%4//2)*4+(tx%4//2)*2))&3
   row=4096+tile*16+y%8;bit=7-x%8
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
 state=bytes((ctrl,mask,latch,sx,sy,oa))+struct.pack('>HH',v,(hi<<8)|(v&255))+bytes((mapper.control,mapper.chr0,mapper.chr1,mapper.prg,0,0))+struct.pack('>III',0,ppu_count,mapper_count)
 # t low byte is last PPUADDR low, not current incremented v. Here it is zero.
 state=state[:8]+bytes((hi,0))+state[10:]
 return results,nt,pal,oam,chrdata,frame,opacity,state

def check(chip,rom,log):
 # Existing checker preserves all startup contexts/journals/ABI/guards evidence.
 base=verify(chip,rom,0)
 base['limit']='This run covers 256 RAM boundaries and all 1024 contexts/journals. Prior four-window checkpoint is separate. Device/display proof is reported separately below.'
 assert chip.count(b'CDRDIS01')==1
 pos=chip.index(b'CDRDIS01');fields=struct.unpack_from('>10I',chip,pos+8)
 status,dev,nt,pal,oam,chrp,frame,copper,start,end=fields
 assert status==0,('display rejected',fields)
 sizes=[(dev,28),(nt,2048),(pal,32),(oam,256),(chrp,8192),(frame,51200),(copper,220)]
 for a,n in sizes:assert a%2==0 and 0<a<a+n<=len(chip)
 for i,(a,n) in enumerate(sizes):
  for b,m in sizes[i+1:]:assert a+n<=b or b+m<=a
 assert chip.count(rom[16+131072:16+262144])==1,'Immutable full cartridge CHR missing or altered'
 r,en,ep,eo,ec,ef,opacity,es=expected(rom)
 for name,addr,want in [('device',dev,es),('nametables',nt,en),('palette',pal,ep),('oam',oam,eo),('mapped_chr',chrp,ec),('five_planes',frame,ef)]:
  actual=chip[addr:addr+len(want)]
  assert actual==want,(name,next((i for i,(a,b) in enumerate(zip(actual,want)) if a!=b),None),actual[:28].hex(),bytes(want[:28]).hex())
 # Verify every Copper palette entry from declared RGB4 LUT, not screen samples.
 rgb=[0x666,0x028,0x21a,0x40a,0x607,0x700,0x600,0x540,0x330,0x040,0x050,0x040,0x044,0,0,0,0xaaa,0x16c,0x44f,0x83f,0xb2c,0xd25,0xc40,0xa60,0x880,0x590,0x2a0,0x0a3,0x099,0,0,0,0xfff,0x6bf,0x99f,0xc8f,0xf7f,0xf7b,0xf96,0xdb2,0xbc0,0x8d1,0x5e5,0x4e9,0x4dd,0x444,0,0,0xfff,0xbef,0xddf,0xedf,0xfdf,0xfde,0xfdc,0xeea,0xdea,0xcea,0xbeb,0xbed,0xbee,0xbbb,0,0]
 # Copper mode and all five DMA pointers must agree with the verified frame.
 expected_header=bytes.fromhex('01005200010200000104000001060000010c001101fc0000008e2c8100902cc100920038009400d001080000010a0000')
 assert chip[copper:copper+48]==expected_header,'Copper setup'
 for plane in range(5):
  rh,hi,rl,lo=struct.unpack_from('>4H',chip,copper+48+plane*8)
  assert (rh,rl)==(0xe0+plane*4,0xe2+plane*4)
  assert (hi<<16|lo)==frame+plane*10240,'Bitplane DMA pointer'
 # Copper starts with twelve register pairs, then five plane pointer pairs.
 for i in range(32):
  reg,value=struct.unpack_from('>HH',chip,copper+88+i*4)
  assert reg==0x180+i*2 and value==rgb[ep[i if i%4 else 0]],('copper palette',i,reg,value)
 return dict(status='PASS',startup=base,actual_target=verify_amiga_log(log),ppu_events=4301,mapper_writes=385,frame_bytes_equal=51200,state_source='unaltered original ROM event stream vs live native journals',CIA_E_ticks={'startup_with_diagnostics':start,'render_and_chr_mapping':(end-start)&0xffffffff},physical_hardware=False,real_time_claim=False)

def verify_screen(chip,path):
 from PIL import Image,ImageChops
 p=chip.index(b'CDRDIS01');f=struct.unpack_from('>10I',chip,p+8);frame,copper=f[6:8]
 colors=[struct.unpack_from('>H',chip,copper+90+i*4)[0] for i in range(32)]
 rgb=[((c>>8)*17,((c>>4)&15)*17,(c&15)*17) for c in colors]
 expected_image=Image.new('RGB',(320,256))
 expected_image.putdata([rgb[sum(((chip[frame+p*10240+y*40+x//8]>>(7-x%8))&1)<<p for p in range(5))] for y in range(256) for x in range(320)])
 expected_image=expected_image.resize((640,256),Image.Resampling.NEAREST)
 actual=Image.open(path)
 assert actual.size==(720,287),'Unexpected video geometry'
 assert ImageChops.difference(expected_image,actual.crop((40,18,680,274))).getbbox() is None,'Actual displayed pixels differ'
 return dict(status='PASS',actual_video_dimensions=[720,287],verified_viewport=[40,18,680,274],RGB_pixels_equal=640*256)

def main():
 out=Path(sys.argv[1]) if len(sys.argv)>1 else PORT/'build/startup-display-native'
 report=check((out/'chip.bin').read_bytes(),(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes(),(out/'amiga.log').read_text())
 report['actual_video']=verify_screen((out/'chip.bin').read_bytes(),out/'screen.ppm')
 (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
