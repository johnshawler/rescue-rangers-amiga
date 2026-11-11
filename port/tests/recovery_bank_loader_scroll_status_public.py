"""Source-only exact wrapper routing and all raw output status bytes."""
import tempfile,subprocess,os,random
from pathlib import Path
from recovery_bank_loader_scroll_status_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME

def main():
 rng=random.Random(0x9030);cases=0
 for result,index in ((1,160),(1,68),(1,90),(1,139),(1,140),(1,150),(-1,160),(0,160)):
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/'wrapper.s';out=Path(td)/'wrapper.bin'
   src.write_text((PORT/'src/recovery_bank_loader_scroll_status_dispatch.s').read_text()+f'\nrecovery_bank_loader_envelope_dispatch:\n move.w #{index},6(a4)\n moveq #{result},d0\n rts\n'+(PORT/'src/recovery_bank_loader_canonical_status.s').read_text())
   subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True);n=Native(out.read_bytes(),bytes(131072))
   for p in range(256):
    ctx=rng.randbytes(5)+bytes((p,))+rng.randbytes(2);n.mem.w_block(RAM,rng.randbytes(2048));n.mem.w_block(CTX,ctx);n.mem.w_block(JOURNAL,rng.randbytes(134638));before=n.snapshot();got=n.run();after=n.snapshot();adapt=result==1 and index==160
    assert got==result&0xffffffff and after[0]==before[0] and after[2]==before[2]
    assert after[1]==ctx[:5]+bytes((p&239 if adapt else p,))+ctx[6:]
    assert after[3]==before[3][:6]+index.to_bytes(2,'big')+before[3][8:]
    assert n.raw_adapter_context==(ctx if adapt else None) and not n.events and not n.reads;cases+=1
   n.m.cleanup()
 print('PASS exact helper160 publication wrapper',cases,'allrawP routing cases; success160 only; failure/wait/other helpers unchanged')
if __name__=='__main__':main()
