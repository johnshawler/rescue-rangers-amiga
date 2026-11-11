#!/usr/bin/env python3
"""Source-only adversarial/baseline comparisons. No host timing as target evidence."""
import random
from recovery_stage_background_test import Runner, assemble, world_pixels, reference

def main():
 r=Runner();candidate=assemble('recovery_stage_background_draw.s');baseline=assemble('recovery_scroll_view_draw.s')
 rng=random.Random(3308);frame=bytearray(rng.randbytes(51200));op=bytearray(rng.randbytes(7680))
 for case in range(3):
  nt=bytearray([255]*2048);chrdata=bytearray(4096)
  if case==0:nt[1024:1984]=bytes(960);chrdata[4080:4096]=b'\xff'*16
  elif case==1:
   nt[960:1024]=b'\x1b'*64;nt[1984:]=b'\xe4'*64
   chrdata[:]=bytes([0x81,0x7e,0xaa,0x55]*1024)
  else:
   nt[:]=rng.randbytes(2048);chrdata[:]=rng.randbytes(4096)
  world=world_pixels(nt,chrdata)
  for origin in (*range(248,256),*range(504,512)):
   expected=reference(world,origin,frame)
   for sr in (0,0x2700):
    params=[0x90+origin//256,0x1e,origin%256,0,0x1e]
    got=r.run(candidate,nt,chrdata,frame,op,params,sr,True)
    # 33 tile IDs + 33 attributes, 30 groups; 33*2 pattern bytes, 240 rows.
    assert r.read_counts=={'NT':1980,'CHR':15840},r.read_counts
    old=r.run(baseline,nt,chrdata,frame,op,params,sr,True,depth=62)
    assert got==old==expected,(case,origin,sr)
 for sr in (0,0x2700):
  for field in range(5):
   for high in (0x10000,0x1000000,0x80000000,0xffff0000):
    for mask in (0,0x1e):
     params=[0x90,mask,255,0,0x1e];params[field]|=high
     assert r.run(candidate,nt,chrdata,frame,op,params,sr,True)==(frame,op)
     assert r.read_counts=={'NT':0,'CHR':0}
  # Software blanking is independent of previous viewport/sprite content.
  for ctrl in (0x90,0x91):
   assert r.run(candidate,nt,chrdata,frame,op,[ctrl,0,255,0,0x1e],sr,True)==reference(world,0,frame,True)
   assert r.read_counts=={'NT':0,'CHR':0}
 r.m.cleanup();print(f'PASS {r.calls} adversarial calls, all width-aware traced; exact baseline/oracle, bounded reads, high-word rejects and blank scratch preservation.')
if __name__=='__main__':main()
