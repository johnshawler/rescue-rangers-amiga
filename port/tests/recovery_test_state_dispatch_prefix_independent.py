#!/usr/bin/env python3
"""Durable independent reference-selected and exhaustive prefix regression.
Adapted from the separate private review harness; no production edits.
"""
import sys,os,json,hashlib,struct
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'port/tests'))
import recovery_test_state_dispatch_prefix as t
rom=(root/'input/rescue-rangers-europe.nes').read_bytes();code=t.assemble()
assert hashlib.sha256(code).hexdigest()=='834ab65a90c73b38a2b35ff2c13fff495970d844d2c2d235cfeb72a97218a5a5'
# Reference-only driver: external logical NMI is offered at the original
# startup wait. Independent selection occurs before either machine advances.
def select(ref,bus):
 event = int(ref.pc==0xfe8d and bus[0x18]==0 and bus[0x80]==1)
 status,idx,target=t.select_boundary(ref,bus,event)
 if status==-1:return None
 assert status==1
 return idx,target,event
checkpoints=[];completions=0
for pads in [(0,0),(16,0),(1,0),(2,0),(4,8),(255,255),(128,64)]:
 n=t.Native(code);b=t.ControllerBus(rom);b.inputs=pads;b.pos=[0,0];b[:2048]=[0xa5]*2048;b.events.clear()
 r=t.MPU(memory=b);r.pc,r.a,r.x,r.y,r.p,r.sp=0xfe24,0x17,0x33,0,0x24,0xfd
 while True:
  chosen=select(r,b)
  if pads==(0,0):checkpoints.append((n.snapshot(),chosen))
  if chosen is None:
   saved=n.snapshot()
   assert n.run(0,pads)==0xffffffff and n.snapshot()==saved
   assert n.run(1,pads)==0xffffffff and n.snapshot()==saved
   break
  idx,target,event=chosen
  if event:
   saved=n.snapshot()
   for _ in range(13):assert n.run(0,pads)==0 and n.snapshot()==saved
  start=len(b.events);dma=len(b.dma)
  if event:r.nmi()
  for _ in range(50000):
   r.step()
   if r.pc==target:break
  else:raise AssertionError('reference timeout')
  n.mem.w_block(t.JOURNAL,bytes(8754));n.mem.w_block(t.RUNTIME+6,os.urandom(4))
  assert n.run(event,pads)==1
  ram,ctx,journal,runtime=n.snapshot()
  assert n.mem.r16(t.RUNTIME+6)==idx
  assert ram==bytes(b[:2048]) and ctx==t.context(r)
  assert n.events==b.events[start:]
  assert tuple(runtime[:4])==b.mapper.snapshot()[:4] and runtime[4:6]==b'\0\0' and not b.mapper.bits
  kind='mapper' if idx in (2,7,8) else 'apu' if idx==0 else 'controller' if idx==9 else 'ppu'
  effects=[e for e in b.events[start:] if e[0]==kind];size=t.SIZES[idx]
  expected=b''
  if size:
   expected=struct.pack('>H',len(effects))+b''.join(struct.pack('>HBB',*e[1:]) for e in effects)
   if idx==6:assert len(b.dma)==dma+1;expected+=b.dma[-1]
   expected+=bytes(size-len(expected))
  assert journal==expected+bytes(8754-size)
  completions+=1
 n.m.cleanup()
counts={}
def count(k):counts[k]=counts.get(k,0)+1
for saved,choice in checkpoints:
 n=t.Native(code);n.restore(saved);pc=n.mem.r16(t.CTX);event=choice[2] if choice else 0
 # Invalid event values and unexpected NMI at every non-admitted boundary.
 for v in [2,3,255,256,65535,65536,0x7fffffff,0x80000000,0xffffffff]:n.reject(event=v);count('event')
 if not event:n.reject(event=1);count('unexpected_nmi')
 # Exhaustive unsupported bank/control and nonempty serial latch bytes.
 for off in [0,3,4,5]:
  for v in range(256):
   if v==saved[3][off]:continue
   n.reject(t.RUNTIME+off,bytes([v]),event=event);count('mapper_latch')
 # Invalid PCs: sweep both bytes and all neighboring supported-entry PCs.
 supported={0xfe24,0xfe43,0xfe67,0xfe7c,0xc574,0xfe8d,0xc0bf,0x8003,0xc0f3,0xc584}
 badpcs={v<<8 | (pc&255) for v in range(256)}|{(pc&0xff00)|v for v in range(256)}|{(p+d)&65535 for p in supported for d in [-1,1]}
 for p in sorted(badpcs-supported):n.reject(t.CTX,struct.pack('>H',p),event=event);count('wrong_pc')
 # Exact exhaustive guarded P domains; all 256 variants restore same boundary.
 if choice and choice[0] in (6,8,9,10):
  idx=choice[0]
  for p in range(256):
   n.restore(saved);n.mem.w8(t.CTX+5,p);before=n.snapshot()
   allowed= ((p&0x30)==0x20 if idx==6 else p==0x26 if idx==8 else (p&0xf3)==0xa0 if idx==9 else (p&0xfa)==0xa0)
   result=n.run(event)
   assert result==(1 if allowed else 0xffffffff),(idx,p,result)
   if not allowed:assert n.snapshot()==before and not n.events
   count('status_all_values')
  n.restore(saved)
 # At first NMI every pending queue byte rejects, all nonzero byte values.
 if choice and choice[0]==6:
  for a in [0xf0,0x9a,0x18,0x19,0x1a,0x1b,0x1c,0x1d]:
   for v in range(1,256):n.reject(t.RAM+a,bytes([v]),event=1);count('pending_queues')
 n.m.cleanup()
# Check immutable predecessors without coupling results to this test's manifest.
fpath=root/'port/analysis/recovery_character_confirmation_target_manifest.json'
assert hashlib.sha256(fpath.read_bytes()).hexdigest()=='9c3203ed72bc3cb6fa152865081b070f7a1ff63afac4792e18214d39987db320'
f=json.loads(fpath.read_text())
verified=0
for path,sha in f['build']['source_sha256'].items():
 assert hashlib.sha256((root/'port'/path).read_bytes()).hexdigest()==sha,path
 verified+=1
assert verified==59
status_comparisons=0
for saved,choice in checkpoints:
 if not choice or choice[0] not in (6,8,9,10):continue
 idx,target,event=choice
 for p in range(256):
  allowed= ((p&0x30)==0x20 if idx==6 else p==0x26 if idx==8 else (p&0xf3)==0xa0 if idx==9 else (p&0xfa)==0xa0)
  if not allowed:continue
  n=t.Native(code);n.restore(saved);n.mem.w8(t.CTX+5,p);n.mem.w_block(t.JOURNAL,bytes(8754))
  b=t.ControllerBus(rom);b[:2048]=saved[0];b.events.clear();b.inputs=(0,0);b.pos=[0,0]
  b.mapper.control,b.mapper.chr0,b.mapper.chr1,b.mapper.prg=saved[3][:4];b.map_bank(b.mapper.bank)
  r=t.MPU(memory=b);r.pc,r.a,r.x,r.y,_,r.sp,_=struct.unpack('>H6B',saved[1]);r.p=p
  if event:r.nmi()
  for _ in range(50000):
   r.step()
   if r.pc==target:break
  else:raise AssertionError('status reference timeout')
  assert n.run(event)==1
  assert n.snapshot()[0]==bytes(b[:2048]) and n.snapshot()[1]==t.context(r),(idx,p)
  assert n.events==b.events
  n.m.cleanup();status_comparisons+=1
print(json.dumps(dict(status='PASS',continuous_reference_selected_completions=completions,
 boundary_probes=counts,extra_original_status_comparisons=status_comparisons,
 frozen_dependencies_verified=verified,composite_bytes=len(code),
 composite_sha256=hashlib.sha256(code).hexdigest(),
 mapper_bit7_reset='Static review only; not emitted by admitted prefix helpers'),indent=2))
