#!/usr/bin/env python3
"""PUBLIC ROM-free synthetic dispatcher contracts. No ROM/py65/oracle imports."""
from recovery_state_dispatch_active_harness import *
from recovery_test_music_indexed_contract import contract as indexed,COMMANDS,DISPATCH
from recovery_test_music_pitched_gate_contract import contract as gate
from recovery_test_music_pitched_note_contract import contract as note
from test_recovery_music_tick_fetch_contract import expected_result as tick
from recovery_test_music_channel_iteration_contract import declarative as iteration,cases as iteration_cases
from test_recovery_active_return_contract import expected as return_model

def main():
 rng=random.Random(0xad501);resource=bytearray(rng.randbytes(131072));offset=3*16384
 for table,target in DISPATCH:
  if table:resource[offset+table-0x8000:offset+table-0x8000+2]=target.to_bytes(2,'little')
 bank=bytes(resource[offset:offset+16384]);code=assemble();assert code==assemble()
 n=Native(code,resource);success=rejected=0;fixtures={}
 runtime=bytes.fromhex('1e0010030000baddf00dd501')
 def load(s,c):
  n.mem.w_block(RAM,bytes(s));n.mem.w_block(CTX,c);n.mem.w_block(JOURNAL,bytes(8754));n.mem.w_block(RUNTIME,runtime)
 def verify(s,c,index,model,reads):
  nonlocal success,rejected
  load(s,c);before=n.snapshot()
  assert model is not None,(index,c.hex())
  want_s,want_c,events,journal=model
  assert n.run()==1,(index,c.hex())
  out_s,out_c,out_j,out_r=n.snapshot()
  assert (out_s,out_c)==(want_s,want_c),(index,c.hex())
  assert out_j==journal+bytes(8754-len(journal)),index
  if events is not None:assert n.events==events,(index,n.events,events)
  assert n.reads==[offset+i for i in reads],(index,n.reads,reads)
  assert out_r[6:10]==struct.pack('>HH',index,SIZES[index])
  assert out_r[:6]==(bytes.fromhex('1e0010060000') if index==20 else runtime[:6])
  assert out_r[10:]==runtime[10:]
  success+=1;n.restore(before);fixtures.setdefault(index,before)
  for addr,value in [(RUNTIME,b'\0'),(RUNTIME+3,b'\x0b'),(RUNTIME+4,b'\1'),(RUNTIME+5,b'\1'),(RUNTIME+10,b'\0\0'),(CTX,b'\x12\x34')]:
   n.reject(addr,value);rejected+=1
  for event in (1,2,0x100,0xffffffff):n.reject(event=event);rejected+=1
  return before
 def frame(s,sp,offset,values):
  for i,v in enumerate(values):s[0x100+((sp+offset+i)&255)]=v
 # Four channels, every original stack offset, every supported command plus
 # fetch/rest and both pitched transitions. Resources are invented bytes.
 for k in range(1024):
  x=0x28+k//256;sp=k&255;s=bytearray(rng.randbytes(2048));p=(k&0xc7)|0x20
  pointer=(0x8000,0x8fff,0xbffe)[k%3];s[0x728+x]=pointer&255;s[0x72c+x]=pointer>>8
  ci=(0,1,2,3,4,5,6,7,8)[k%9];a=COMMANDS[ci] if COMMANDS[ci] is not None else (32*(1+k%7) if ci==3 else 0)
  c=bytes((0x83,0x9d if ci==8 else 0xa0,a,x,0,p,sp,0xa7))
  frame(s,sp,1,(0x84,0x80))
  model,reads=indexed(s,c,bank,ci);verify(s,c,14 if ci==8 else 16 if ci==3 else 15,model,reads)
  if ci not in (3,8):
   for ptr in (0x7fff,0xc000,0xffff):
    bad=bytearray(s);bad[0x728+x]=ptr&255;bad[0x72c+x]=ptr>>8;load(bad,c);n.reject();rejected+=1
   load(s,c)
  # Gate and note independently use declarative models, not prior native output.
  a=32*(1+k%7)+1+(k//7)%31;c=bytes((0x83,0xa0,a,x,0,p,sp,0xa7))
  model,reads=gate(s,c,bank);verify(s,c,17,model,reads)
  s[0xc5]=0x10;s[0xc6]=0x90;frame(s,sp,1,(1+k%31,0x84,0x80))
  c=bytes((0x83,0xfd,0,x,0,p,sp,0xa7));model,reads=note(s,c,bank)
  verify(s,c,18,model,reads)
  for off in (2,3):n.reject(RAM+0x100+((sp+off)&255),b'\0');rejected+=1
 # Full tick fetch across all SPs and canonical statuses.
 for sp in range(256):
  s=bytearray(rng.randbytes(2048));s[0xc0]=(sp%3)*4;s[0xc9]=1+sp%255
  s[0xd0]=s[0xd1]=s[0xcf]=s[0x763]=0;s[0xdb]=sp%8;s[0xdc+sp%8]=0x88
  pointer=0x8000 if sp&1 else 0xbfff;s[0x753]=pointer&255;s[0x757]=pointer>>8
  c=bytes.fromhex('c0f3')+bytes((0,0,0,(sp&0xc7)|0x20,sp,0xa7))
  out,ctx,journal=tick(s,c,bank)
  events=[('ram',0x100+((sp-i)&255),v) for i,v in enumerate((0xc0,0xf8))]
  events += [('ram',a,out[a]) for a in (0xc3,0xc0,0xc8,0xc7)]
  events += [('ram',0x100+((sp-i)&255),v) for i,v in enumerate((0,3,0x80,0x84,0x83,0x9f),2)]
  events += [('ram',0xc1,pointer&255),('ram',0xc2,pointer>>8),('resource',pointer,bank[pointer-0x8000],0),('ram',0x753,out[0x753])]
  if pointer&255==255:events.append(('ram',0x757,out[0x757]))
  verify(s,c,13,(out,ctx,events,journal),[pointer-0x8000])
  for addr in (0xd0,0xd1,0xcf,0x763):n.reject(RAM+addr,b'\1');rejected+=1
  for addr,value in ((0xc0,3),(0xdb,8),(0xdc+sp%8,0),(0x757,0x7f)):
   n.reject(RAM+addr,bytes((value,)));rejected+=1
  for status in (0,0x30,0x28):n.reject(CTX+5,bytes((status,)));rejected+=1
 # Outer channel and RTI, including page-one wrap and saved status variation.
 for k,(raw,c) in enumerate(iteration_cases(1024)):
  s=bytearray(raw);sp=c[6];frame(s,sp,3,(0xf8,0xc0));out,ctx,events=iteration(s,c)
  verify(s,c,19,(out,ctx,events,b''),[])
  n.reject(RAM+0x100+((sp+3)&255),b'\0');rejected+=1
 for sp in range(256):
  s=bytearray(rng.randbytes(2048));s[0xf1]=6;s[0x80]=4
  frame(s,sp,5,(sp,0x8d,0xfe));c=bytes.fromhex('c0f9')+rng.randbytes(4)+bytes((sp,0xa7))
  out,ctx,journal,status,events=return_model(s,c)
  verify(s,c,20,(out,ctx,events,journal),[])
  for addr in (0xf1,0x80,0x100+((sp+6)&255),0x100+((sp+7)&255)):
   n.reject(RAM+addr,b'\0');rejected+=1
 # Exhaustive unsupported music command bytes and indexed state selectors.
 s=bytearray(2048);s[0x753]=0;s[0x757]=0x90;c=bytes.fromhex('83a0002b0024b8a7')
 for command in range(32):
  if command not in (4,5,6,7,8,9,24):
   load(s,c[:2]+bytes((command,))+c[3:]);n.reject();rejected+=1
 for x in range(256):
  if x not in range(0x28,0x2c):
   load(s,bytes.fromhex('839d00')+bytes((x,0,0x24,0xb8,0xa7)));n.reject();rejected+=1
 # Exhaust every unsupported live PRG/control value at each new boundary.
 for index,saved in fixtures.items():
  n.restore(saved)
  for status in (() if index==20 else (0,0x30)):
   n.reject(CTX+5,bytes((status,)));rejected+=1
  for value in range(256):
   if value!=3:n.reject(RUNTIME+3,bytes((value,)));rejected+=1
   if value!=0x1e:n.reject(RUNTIME,bytes((value,)));rejected+=1
 # Instrument address overflow/outside window must reject before mutation.
 saved=fixtures[18];s=bytearray(saved[0]);c=saved[1];x=c[3];s[0x730+x]=0;s[0x71c+x]=0
 for pointer in (0,0x7ffb,0xbffc,0xfffc,0xffff):
  s[0xc5]=pointer&255;s[0xc6]=pointer>>8;load(s,c);n.reject();rejected+=1
 # Stacked note operand is validated independently of the return frame.
 n.restore(fixtures[18]);sp=n.mem.r8(CTX+6)
 for value in (0,32,255):n.reject(RAM+0x100+((sp+1)&255),bytes((value,)));rejected+=1
 # Original channel index and pending callbacks are guard failures.
 saved=fixtures[19];s=bytearray(saved[0]);c=saved[1];sp=c[6]
 for value in (4,255):
  frame(s,sp,1,(value,));load(s,c);n.reject();rejected+=1
 frame(s,sp,1,(3,));s[0xcf]=2;load(s,c);n.reject();rejected+=1
 s[0xcf]=0;s[0xc0]=0;s[0x752]=1;s[0x762]=1;load(s,c);n.reject();rejected+=1
 n.m.cleanup()
 # Malformed immutable dispatch-table bytes, checked with separate machines.
 for ci,(table,target) in enumerate(DISPATCH):
  if not table:continue
  for delta in (0,1):
   broken=bytearray(resource);broken[offset+table-0x8000+delta]^=1
   n=Native(code,broken);s=bytearray(2048);s[0x757]=0x90
   c=bytes((0x83,0xa0,COMMANDS[ci],0x2b,0,0x24,0xb8,0xa7));load(s,c);n.reject();rejected+=1
   n.m.cleanup()
 print(json.dumps(dict(status='PASS',scope='PUBLIC synthetic ROM-free',successes=success,inert_rejections=rejected,
  code_bytes=len(code),code_sha256=hashlib.sha256(code).hexdigest()),indent=2))
if __name__=='__main__':main()
