"""Native-only ABI/global access checks for C0F9 return; no ROM/model."""
from recovery_general_scheduler_harness import Native as Base,PORT,RAM,CTX,JOURNAL
class Native(Base):
    def __init__(self):
        self.ram_reads=[]
        super().__init__('recovery_active_nmi_return.s',22)
    def run(self,state,ctx,rng,**kwargs):
        self.ram_reads.clear()
        result=super().run(state,ctx,rng,**kwargs)
        reads=[]
        if ctx[:2]==bytes.fromhex('c0f9'):
            reads = [0xf1]+[0xf5]*5+[0x100+((ctx[6]+i)&255) for i in range(1,8)]
        assert self.ram_reads==reads,(self.ram_reads,reads)
        return result
    def trace(self,mode,width,address,value):
        size=1<<width
        assert mode in ('R','W')
        assert any(b<=address and address+size<=b+n for b,n in (self.reads if mode=='R' else self.writes)),(mode,width,hex(address))
        if mode=='R' and RAM<=address<RAM+2048:
            assert width==0
            self.ram_reads.append(address-RAM)
        if mode=='W' and RAM<=address<RAM+2048:
            raise AssertionError('C0F9 must not write original RAM')
        if mode=='W' and address==JOURNAL and value:
            assert width==1 and 1<=value<=5
            at=JOURNAL+2+4*(value-1)
            self.effects.append(('mapper',self.mem.r16(at),self.mem.r8(at+2),self.mem.r8(at+3)))
