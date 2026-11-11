#!/usr/bin/env python3
"""Synthetic machine68k tests of the exact new counted-journal capture routine."""
import hashlib,json,os,random,struct,subprocess,tempfile
from pathlib import Path
import machine68k
PORT=Path(__file__).resolve().parents[1];OUT=PORT/'build/recovery_menu_sfx_target'
def main():
 source=(PORT/'src/recovery_menu_sfx_target.s').read_text().split('capture_journal:\n',1)[1].split('; Preserve the predecessor',1)[0]
 source='capture_journal:\n'+source+'\nstop: bra.s stop\n'
 with tempfile.TemporaryDirectory() as tmp:
  s,b=Path(tmp)/'adapter.s',Path(tmp)/'adapter.bin';s.write_text(source)
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(b),str(s)],check=True);code=b.read_bytes()
 # No rewriting of the adapter under test. Its exact bytes also occur in target.
 payload=(OUT/'default/recovery_menu_sfx_target.bin').read_bytes()
 # Last error branch targets the runner's earlier stop label, so its displacement
 # differs in isolation. All other instruction bytes must be unchanged.
 assert payload.count(code[:-6])==1
 cases=[(0,0,0,0,True),(1,0,65535,0,True),(7,22,5,0,True),(48,65535,32768,0,True),(48,65535,33339,0,True),(48,65535,33595,0,True),(48,65535,33596,0,False),(48,74,10,0,False),(72,0,0,0,False),(7,22,5,262140,False)]
 reports=[]
 for helper,size,count,used,ok in cases:
  m=machine68k.Machine(machine68k.CPUType.M68EC020,16384);mem,cpu=m.mem,m.cpu
  C,J,R,P,A,S,STOP=0x1000,0x30000,0x20000,0x21000,0x80000,0x1f0000,0x800
  mem.w_block(C,code);mem.w16(STOP,0x60fe);mem.w32(S,STOP)
  journal=bytearray([0x69]*134638);struct.pack_into('>H',journal,0,count)
  for i in range(min(count,33595)):struct.pack_into('>HBB',journal,2+i*4,i&65535,i&255,(i>>8)&255)
  dma=bytes((i*37)&255 for i in range(256));journal[134382:134638]=dma
  mem.w_block(J,bytes(journal));mem.w16(R+6,helper);mem.w16(R+8,size);mem.w32(P+72,A);mem.w32(P+76,used)
  mem.w_block(A-16,b'Z'*16+bytes(262144)+b'Z'*16)
  rng=random.Random(17);regs=[rng.getrandbits(32) for _ in range(15)];regs[10]=J;regs[12]=R;regs[14]=P
  for i,v in enumerate(regs):cpu.w_reg(i,v)
  cpu.w_sr(0x2700);cpu.w_sp(S);cpu.w_pc(C);reads=[]
  def trace(mode,width,address,value):
   if mode=='R' and J<=address<J+len(journal):reads.extend(range(address-J,address-J+(1<<width)))
  mem.set_trace_func(trace);mem.set_trace_mode(True)
  terminal=STOP if ok else C+len(code)-2
  for _ in range(10000):
   cpu.execute(10000)
   if cpu.r_pc()==terminal:break
  else:raise AssertionError('Adapter timeout')
  mem.set_trace_mode(False)
  if ok:
   assert cpu.r_sp()==S+4 and [cpu.r_reg(i) for i in range(15)]==regs
   actual_count=count if size else 0
   want=struct.pack('>HH',helper,actual_count)+journal[2:2+actual_count*4]
   if helper==48:want+=dma
   assert mem.r32(P+76)==used+len(want)
   assert bytes(mem.r_block(A+used,len(want)))==want
   allowed=set(range(2+actual_count*4)) if size else set()
   if helper==48:allowed.update(range(134382,134638))
   assert set(reads)<=allowed,'stale padding consumed'
  else:assert mem.r32(P+8)==0xfffffffd
  assert bytes(mem.r_block(A-16,16))==b'Z'*16 and bytes(mem.r_block(A+262144,16))==b'Z'*16
  assert bytes(mem.r_block(J,len(journal)))==journal and bytes(mem.r_block(C,len(code)))==code
  m.cleanup();reports.append(dict(helper=helper,size=size,count=count,accepted=ok,journal_bytes_read=len(reads)))
 result=dict(status='PASS',cases=reports,adapter_branch_relocation_only=True,ABI_and_stack_preserved_for_success=True,stale_padding_not_read=True)
 (OUT/'adapter-test.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
