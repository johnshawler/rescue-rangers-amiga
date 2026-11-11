"""Bounded native execution for explicit NMI; no cartridge or expected states."""
from recovery_general_scheduler_harness import Native as Base,PORT,RAM,CTX,JOURNAL,STACK,STOP,CODE
class Native(Base):
    def __init__(self):super().__init__('recovery_idle_nmi_prefix.s',454)
    def trace(self,mode,width,address,value):
        size=1<<width
        assert mode in ('R','W')
        assert any(b<=address and address+size<=b+n for b,n in (self.reads if mode=='R' else self.writes)),(mode,width,hex(address))
        if mode=='W' and RAM<=address<RAM+2048:
            assert width==0;self.stores.append((address-RAM,value));self.effects.append(('ram',address-RAM,value))
        elif mode=='W' and address==JOURNAL and value:
            assert width==1 and 1<=value<=49
            at=JOURNAL+2+4*(value-1);a,v,k=self.mem.r16(at),self.mem.r8(at+2),self.mem.r8(at+3)
            if a==0x4014:assert bytes(self.mem.r_block(JOURNAL+198,256))==bytes(self.mem.r_block(RAM+512,256))
            self.effects.append(('ppu',a,v,k))
