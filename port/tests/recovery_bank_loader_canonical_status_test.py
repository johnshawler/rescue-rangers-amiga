"""Native live-status ABI adapter checks; no cartridge/oracle imports."""
import os,subprocess,tempfile,random
from pathlib import Path
from recovery_bank_loader_collision_harness import Native,PORT,RAM,CTX,JOURNAL,RUNTIME

def main():
 rng=random.Random(0xb);cases=0
 for success in (False,True):
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/'status.s';out=Path(td)/'status.bin'
   src.write_text(' moveq #'+('1' if success else '-1')+',d0\n cmpi.l #1,d0\n bne.s .done\n bsr.w recovery_bank_loader_canonical_status\n.done:\n rts\n'+(PORT/'src/recovery_bank_loader_canonical_status.s').read_text())
   subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True);n=Native(out.read_bytes(),bytes(131072))
   for p in range(256):
    ctx=rng.randbytes(5)+bytes((p,))+rng.randbytes(2);n.mem.w_block(RAM,rng.randbytes(2048));n.mem.w_block(CTX,ctx);n.mem.w_block(JOURNAL,rng.randbytes(134638));before=n.snapshot();result=n.run();after=n.snapshot()
    want=ctx[:5]+bytes((p&239,))+ctx[6:] if success else ctx
    assert n.raw_adapter_context==(ctx if success else None)
    assert result==(1 if success else 0xffffffff) and after[1]==want
    assert after[0]==before[0] and after[2:]==before[2:] and not n.events and not n.reads
    assert ((after[1][5]^p)&239)==0;cases+=1
   n.m.cleanup()
 print('PASS canonical live-status adapter',cases,'USER/native cases; onlyB changes on success, failures untouched')
if __name__=='__main__':main()
