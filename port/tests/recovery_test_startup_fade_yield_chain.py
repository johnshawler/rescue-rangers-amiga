#!/usr/bin/env python3
"""Live-buffer fade+frame-yield native pairs from a continuous reset ROM run.
All intervening original active audio executes only in the independent oracle;
this proof does not claim native repeated-NMI/audio integration.
"""
from recovery_test_startup_fade_continue import *

def main():
    rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()
    assert hashlib.sha256(rom).hexdigest()==SHA
    results,base,steps=oracle(rom);raw=results[-1][5]
    live=RecordBus(base);ref=CPU(memory=live)
    ref.pc=int.from_bytes(raw[:2],'big');ref.a,ref.x,ref.y,ref.p,ref.sp=raw[2:7]
    native=Native('recovery_startup_fade_continue.s')
    native.install('recovery_gameplay_frame_yield.s',0x4000)
    rng=random.Random(0xc594);pairs=0;slices=0;nmis=0
    for _ in range(1000000):
        if ref.pc in (0xc2a8,0xc594):
            state=bytes(live[:2048]);ctx=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,0xa7))
            live.events=[];advance(ref)
            first=compare(native,state,ctx,ref,live,rng);slices+=1
            if ref.pc in (0xc2a5,0xff04):
                first_events=live.events.copy();live.events=[]
                for _ in range(100):
                    ref.step()
                    if ref.pc==0xfe8d:break
                else:raise AssertionError('frame yield timeout')
                got=native.run(first[0],first[1],rng,entry=0x4000,resume=True)
                expected=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,ref.p,ref.sp,ctx[7]))
                journal=b''.join(struct.pack('>HBB',a,v,0) for a,v in live.events)
                assert got==(bytes(live[:2048]),expected,journal+b'\xb6'*(512-len(journal)),len(live.events),live.events)
                assert first[4]+got[4]==first_events+live.events
                pairs+=1;slices+=1
            continue
        if ref.pc==0xc597:break
        pc=ref.pc;ref.step()
        if pc==0xfea3 and ref.pc==0xfe90:ref.nmi();nmis+=1
    else:raise AssertionError('lifecycle timeout')
    assert (pairs,slices,nmis,ref.pc,ref.sp)==(16,33,16,0xc597,0xbf)
    assert base.bank==6 and base.mapper.control==0x1e and not base.mapper.bits
    assert hashlib.sha256((PORT.parent/'input/rescue-rangers-europe.nes').read_bytes()).hexdigest()==SHA
    print('PASS 16 live-native-buffer fade+yield pairs (33 native calls), full ordered RAM/context/journal checks; continuous reset oracle reaches C597 after all real audio and 16 further NMIs. No snapshot injected into reference and no reference status normalization. Repeated NMI/audio itself is still reference-only.')
    native.close()
if __name__=='__main__':main()
