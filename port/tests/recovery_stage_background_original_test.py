#!/usr/bin/env python3
"""Private proof against original-derived completed-NMI renderer states.
Reads an existing qualified capture's actual input history; never feeds capture
state into the original replay. No ROM, assets, or snapshots are emitted.
"""
from pathlib import Path
import argparse,hashlib,json,random,struct
from recovery_stage_target_oracle import oracle
from recovery_stage_target_pixels import expected as final_pixels
from recovery_resident_chr_fade_target_oracle import SerialMapper
from recovery_stage_background_test import Runner,assemble,world_pixels,reference

def snapshots(rom,ref):
 results,bus,_=ref;nt=bytearray(2048);mapper=SerialMapper()
 ctrl=mask=sx=sy=latch=hi=v=pos=0
 for i,result in enumerate(results):
  for e in bus.events[pos:bus.event_ends[i]]:
   if e[0]=='mapper':mapper.write(e[1],e[2]);continue
   if e[0]!='ppu':continue
   a,d=e[1:3]
   if a==0x2002:latch=0
   elif a==0x2000:ctrl=d
   elif a==0x2001:mask=d
   elif a==0x2005:
    if latch:sy=d
    else:sx=d
    latch^=1
   elif a==0x2006:
    if latch:v=(hi<<8)|d
    else:hi=d&63
    latch^=1
   elif a==0x2007:
    addr=v&0x3fff;assert addr>=0x2000
    if addr<0x3f00:
     logical=(addr&0xfff)//1024;physical=(0,1,logical&1,logical>>1)[mapper.control&3]
     nt[physical*1024+(addr&1023)]=d
    v=(v+(32 if ctrl&4 else 1))&0x7fff
  pos=bus.event_ends[i]
  if result[0] in (8,20,42) and ctrl in (0x90,0x91) and mask in (0,0x1e) and sy==0 and mapper.control==0x1e:
   bg=rom[16+131072+mapper.chr1*4096:16+131072+(mapper.chr1+1)*4096]
   yield bytes(nt),bg,(ctrl,mask,sx,sy,mapper.control)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('capture',type=Path);args=ap.parse_args()
 chip=(args.capture/'full-CHIP.bin').read_bytes();cfg=json.loads((args.capture/'build.json').read_text())
 f=struct.unpack_from('>21I',chip,chip.index(b'CDRSFX01')+8);live=struct.unpack_from('>9I',chip,chip.index(b'CDRCLIV1')+8)
 changes=[struct.unpack_from('>4I',chip,live[4]+i*16) for i in range(live[5])]
 rom=Path('input/rescue-rangers-europe.nes').read_bytes();ref=oracle(rom,changes,f[1],scene=cfg.get('scene',False))
 r=Runner();code=assemble('recovery_stage_background_draw.s');old=assemble('recovery_scroll_view_draw.s')
 rng=random.Random(734);frame=bytearray(rng.randbytes(51200));opacity=bytearray(rng.randbytes(7680))
 seen=set();admitted=0
 for nt,chrdata,params in snapshots(rom,ref):
  admitted+=1;key=hashlib.sha256(nt+chrdata+bytes(params)).digest()
  if key in seen:continue
  seen.add(key);world=world_pixels(nt,chrdata);want=reference(world,256*(params[0]&1)+params[2],frame,params[1]==0)
  for sr in (0,0x2700):
   got=r.run(code,nt,chrdata,frame,opacity,params,sr,True)
   baseline=r.run(old,nt,chrdata,frame,opacity,params,sr,True,depth=62)
   assert got==baseline==want
 # Full original-derived final stage plus unchanged sprite renderer, every byte.
 _,nt,pal,oam,chrdata,composite,op,state=final_pixels(rom,ref)
 sprites=assemble('native_sprite_blitter.s')
 for sr in (0,0x2700):
  params=[state[0],state[1],state[3],state[4],state[10]]
  bg,gotop=r.run(code,nt,chrdata[4096:],bytearray(51200),opacity,params,sr,True)
  result,retained=r.run(sprites,nt,chrdata,bg,gotop,params[:2],sr,True,True,oam)
  assert result==composite and retained==gotop==op
 r.m.cleanup()
 print(json.dumps(dict(status='PASS',actual_input_changes=changes,helper_calls=len(ref[0]),original_instructions=ref[2],admitted_completed_NMI_states=admitted,unique_background_states=len(seen),assembled_calls=r.calls,all_width_traced=True,final_original_sprite_composition=True,candidate_sha256=hashlib.sha256(code).hexdigest()),indent=2))
if __name__=='__main__':main()
