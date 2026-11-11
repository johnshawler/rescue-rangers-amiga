"""Read-only original input-history research; not native or visual control proof.
No captured state is consumed and no game RAM is patched after bootstrapping.
"""
import hashlib,collections
from pathlib import Path
from recovery_stage_map_test import genuine_entry,SHA
ROOT=Path(__file__).resolve().parents[2]
def run(rom,mode):
 m,b,nmi=genuine_entry(rom);frames=0;targets=collections.Counter();pad_changes=[];last=None
 for step in range(3000000):
  if m.pc in (0xfe8d,0xfe90) and not any(b[0x80+4*i] in (4,8) for i in range(4)):
   m.nmi();nmi+=1;continue
  if m.pc==0xfecd:
   buttons={'B_pulse':64 if frames%30<15 else 0,
            'B_hold_release':64 if frames<121 else 0,
            'A_hold_release':128 if frames<61 or 121<=frames<181 else 0}[mode]
   pad=(1|buttons) if frames else 0
   b.inputs=(pad,0);b.pos=[0,0]
   if pad!=last:pad_changes.append((frames,nmi,pad));last=pad
  if m.pc==0xc77b:
   frames+=1
   if frames==241:break
  if b.mapper.bank==6 and m.pc==0x801c:targets[(b[0]+256*b[1],b[0x4e0+m.x])]+=1
  m.step();b.events.clear();b.dma.clear()
 else:raise AssertionError('original control route bound')
 return dict(mode=mode,frame_entries=frames,nmi=nmi,targets=[(hex(a),hex(t),n) for (a,t),n in targets.items()],pad_changes=pad_changes)
if __name__=='__main__':
 rom=(ROOT/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 for mode in ('B_pulse','B_hold_release','A_hold_release'):print(run(rom,mode),flush=True)
