#!/usr/bin/env python3
"""Public structural proof: source-only imports, assembly and displacement bounds."""
import importlib.abc,sys,json,hashlib
class PublicOnly(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname=='py65' or fullname.startswith('py65.') or fullname.endswith(('_rom','_oracle')) or 'resident' in fullname:
   raise AssertionError('private import in public proof: '+fullname)
sys.meta_path.insert(0,PublicOnly())
from recovery_state_menu_sfx_harness import *
from recovery_state_menu_sfx_models import MODELS

def main():
 code=assemble();assert code==assemble();n=Native(code,bytes(131072));at=CODE;starts=set();targets=[];pc_targets=[];long_pc=0
 while at<CODE+len(code):
  starts.add(at);size,op=n.cpu.disassemble(at);offset=at-CODE;w=int.from_bytes(code[offset:offset+2],'big')
  assert size>0 and size%2==0
  if w&0xf000==0x6000:
   b=w&255
   displacement=int.from_bytes(code[offset+2:offset+6],'big',signed=True) if b==255 else int.from_bytes(code[offset+2:offset+4],'big',signed=True) if b==0 else b-256 if b>=128 else b
   targets.append((at+2+displacement,displacement))
  elif w&0xf0f8==0x50c8:
   displacement=int.from_bytes(code[offset+2:offset+4],'big',signed=True);targets.append((at+2+displacement,displacement))
  if w&0xf1ff==0x41fa:
   displacement=int.from_bytes(code[offset+2:offset+4],'big',signed=True);pc_targets.append((at+2+displacement,displacement))
  elif w&0xf1ff==0x41fb:
   ext=int.from_bytes(code[offset+2:offset+4],'big')
   assert ext==0x0170,('unexpected PC full format',hex(at),hex(ext))
   displacement=int.from_bytes(code[offset+4:offset+8],'big',signed=True);pc_targets.append((at+2+displacement,displacement));long_pc+=1
  at+=size
 assert at==CODE+len(code)
 assert all(t in starts for t,d in targets+pc_targets)
 assert len(code)+CODE<RAM-16
 assert JOURNAL+134638+16<RUNTIME-16 and RUNTIME+12+16<RESOURCE-16
 # Exercise the access callback itself, including journal guard and ownership.
 for mode in ('R','W'):
  for address in (RAM-1,RAM+2047,CTX+7,JOURNAL+134637,RUNTIME+11,RESOURCE-1,STACK-1025):
   try:n.trace(mode,2,address,0)
   except AssertionError:pass
   else:raise AssertionError(('out-of-bounds trace admitted',mode,address))
 try:n.trace('W',0,RESOURCE,0)
 except AssertionError:pass
 else:raise AssertionError('writable immutable resource')
 n.m.cleanup()
 print(json.dumps(dict(status='PASS',instructions=len(starts),branches=len(targets),max_branch_displacement=max(abs(d) for _,d in targets),pc_references=len(pc_targets),max_pc_displacement=max(abs(d) for _,d in pc_targets),full_format_68020_pc_references=long_pc,code_bytes=len(code),code_sha256=hashlib.sha256(code).hexdigest(),journal_capacity=134638,source_only_models=len(MODELS))))
if __name__=='__main__':main()
