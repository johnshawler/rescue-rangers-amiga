"""Private analysis hook around the immutable complete title/native comparison.
Records original APU writes while the existing test checks matching native effects.
No production files or generated playable artifacts are changed.
"""
import sys, json, inspect, collections, hashlib, os
from pathlib import Path
root=Path(os.environ['RR_SOURCE_ROOT']).resolve()
sys.path.insert(0,str(root/'port/tests'))
import recovery_test_resident_command0f_loop as t
records=[]
original=t.CompleteBus.__setitem__
def watched(self,address,value):
    if isinstance(address,int) and (0x4000 <= address <= 0x4013 or address==0x4015):
        f=inspect.currentframe().f_back
        logical_nmi=None
        while f:
            if f.f_code is t.main.__code__:
                n=f.f_locals.get('nmis')
                logical_nmi=None if n is None else n+2
                break
            f=f.f_back
        records.append({'nmi':logical_nmi,'address':address,'value':value,'bus':id(self)})
    return original(self,address,value)
t.CompleteBus.__setitem__=watched
for key in ('MENU_INPUT','MENU_CYCLES'):
    assert key not in os.environ,key
t.main()
assert len(records)==7136,len(records)
assert len({r['bus'] for r in records})==1
for r in records: r.pop('bus')
registers={f'{a:04X}':{'writes':sum(r['address']==a for r in records),'values':sorted({r['value'] for r in records if r['address']==a})} for a in sorted({r['address'] for r in records})}
results={'scope':'Verified native/original full 900-countdown title path only; not gameplay or all sounds','original_source_test_sha256':hashlib.sha256(Path(t.__file__).read_bytes()).hexdigest(),'APU_writes':len(records),'registers':registers,'limitations':['NMI labels before the bootstrap boundary are unknown','Logical NMI labels do not provide exact APU CPU-cycle timestamps','Original APU effects do not prove audible Amiga behavior'],'events':records}
out=Path(os.environ['RR_PROFILE_OUT']);out.write_text(json.dumps(results,indent=2)+'\n')
print('APU_PROFILE',json.dumps({k:v for k,v in results.items() if k!='events'},indent=2))
