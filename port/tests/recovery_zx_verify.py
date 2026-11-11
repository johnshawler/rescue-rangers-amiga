#!/usr/bin/env python3
"""Verify private stock capture, callback log, and precise input-only evidence."""
import struct,json,hashlib,argparse
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
P=Path(__file__).resolve().parents[1];B=parser.parse_args().output.resolve()
b=(B/'chip.bin').read_bytes();log=(B/'run.log').read_text()
for line in ('cpu_model=68020','chipmem_size=4','fastmem_size=0','chipset=aga','ntsc=false','cpu_cycle_exact=true','cpu_memory_cycle_exact=true','PASS runs=1000'):
 assert line in log,line
positions=[i for i in range(len(b)-40) if b[i:i+8]==b'CDRCLIV1' and 0<struct.unpack_from('>I',b,i+20)[0]<len(b)]
assert len(positions)==1
p=positions[0];version,error,tick,state,records,count,_,_=struct.unpack_from('>8I',b,p+8)
assert version==65536 and error==0 and tick>200 and count==20
expected=[(10,0x31,64),(20,0x32,192),(30,0xb1,128),(40,0xb2,0),(50,0x44,16),(60,0xc4,0),(70,0x42,32),(80,0xc2,0),(90,0x4e,1),(100,0xce,0),(110,0x4f,2),(120,0xcf,0),(130,0x4d,4),(140,0xcd,0),(150,0x4c,8),(160,0xcc,0),(170,0x40,0),(180,0xc0,0),(190,0x64,0),(200,0xe4,0)]
observed=[]
for i,(wanttick,wantraw,wantheld) in enumerate(expected):
 t,held,raw,serial,cra,elapsed,event=struct.unpack_from('>I4BII',b,records+16*i)
 assert (t,raw,held,event)==(wanttick,wantraw,wantheld,i+1)
 assert raw==((((~serial)&255)>>1)|(((~serial)&1)<<7))
 assert cra==8 and 64<=elapsed<128
 observed.append(dict(tick=t,held=held,raw=raw,serial=serial,cra=cra,ack_ticks=elapsed))
assert b[records+16*count:records+2048]==bytes(2048-16*count)
assert b[state]==0 and struct.unpack_from('>I',b,state+8)[0]==20
payload=(B/'probe.bin').read_bytes();prefix=payload[:payload.index(b'CDRCLIV1')]
assert b.count(prefix)==1,'code changed'
assert log.count('KEY logical_tick=')==20
out={'classification':'Input-only real stock CIA serial evidence; not game integration or performance evidence','events':observed,'final_tick':tick,'capture_sha256':hashlib.sha256(b).hexdigest()}
(B/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS 20 real serial transitions, overlap/release, exact controls/no aliases, >=64-tick handshake, no overflow and unchanged code')
