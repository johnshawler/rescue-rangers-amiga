"""Private original-only diagnostic from genuine reset, no state repairs."""
import sys,json,hashlib
from pathlib import Path
from recovery_bank_loader_player_status_oracle import ControllerBus,SHA,select_boundary,REGIONS,RETURNS
from recovery_test_active_command0e_rom import Ricoh
PORT=Path(__file__).resolve().parents[1]
def run(path,press=5,stop=90):
 path.mkdir();rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA;b=ControllerBus(rom);b.inputs=(0,0);b.pos=[0,0];b[:2048]=[0xa5]*2048;b.events.clear();m=Ricoh(memory=b);m.pc,m.a,m.x,m.y,m.p,m.sp=0xfe24,23,51,0,36,253
 count=nmis=game=menu=chars=0;event=0;dialogue=False;rows=[];polls=[];unknown=[];last=[]
 def row(pc):
  x=m.x;return dict(frame=max(0,game-1),nmi=nmis,pc=hex(pc),x=x,bank=b.mapper.bank,p=m.p,sp=m.sp,ram={hex(a):b[a] for a in (0x10,0x14,0x15,0x16,0x17,0x54,0x55,0x6c,0x6d,0x400,0x401,0x410,0x420,0x430,0x4d0,0x4d1,0x4f0,0x500,0x510,0x520,0x550,0x560,0x348)})
 for loop in range(3000000):
  if m.pc==0xa025:menu+=1
  if m.pc==0xa06c:chars+=1
  value=(16 if chars<3 else 0 if chars<5 else 16) if chars else 16 if menu else 0
  if m.pc==0x911c:dialogue=True
  if dialogue:value=16 if nmis>300 and nmis%120<30 else 0
  if game:value=129 if press<=game-1<press+6 else 1
  status,index,target=select_boundary(m,b,event)
  if status==0:event=1;continue
  if status<0:
   index=None;unknown.append(dict(pc=hex(m.pc),bank=b.mapper.bank,frame=max(0,game-1)))
  elif event:m.nmi();nmis+=1
  if index in (9,21,31,50,77,87,94,97,114,133,138):b.inputs=(value,0);b.pos=[0,0];polls.append(dict(frame=max(0,game-1),helper=index,pad=value,nmi=nmis))
  for _ in range(50000 if status>0 else 1):
   pc=m.pc;op=b[pc] if index in REGIONS else 0
   if game and (pc in (0xc77b,0xc879,0xc8d8,0xc940,0xc952,0xc96b,0xc971,0xc9a9,0xc9ba,0xca05,0xcc9f,0xc848,0xfecd)):
    rows.append(row(pc))
   m.step()
   if index==135 and pc==0xc85e:break
   if index in REGIONS:
    if op==0x6c or op==0x60 and m.pc not in RETURNS[index] or not any(a<=m.pc<z for a,z in REGIONS[index]):break
   elif target is not None and m.pc in target:break
  else:
   if status>0:raise AssertionError(('original step limit',hex(m.pc)))
  if m.pc==0xc77b:
   game+=1
   if game>=stop+1:rows.append(row(0xc77b));break
  event=0;count+=1;b.events.clear();b.dma.clear()
 else:raise AssertionError('outer limit')
 result=dict(press=press,frames=game-1,nmis=nmis,helpers=count,rows=rows,polls=polls,unknown=unknown);(path/'result.json').write_text(json.dumps(result));print('Original probe',path,'frames',game-1,'rows',len(rows),'unknown',len(unknown),flush=True)
if __name__=='__main__':run(Path(sys.argv[1]),int(sys.argv[2]) if len(sys.argv)>2 else 5,int(sys.argv[3]) if len(sys.argv)>3 else 90)
