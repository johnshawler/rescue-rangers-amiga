#!/usr/bin/env python3
"""Additive background-only candidate, no instrumentation. PRIVATE outputs."""
from pathlib import Path
import argparse,hashlib,json
P=Path(__file__).resolve().parents[1]
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
def prepare(s,out):
 d=(P/'src/recovery_state_menu_display_device.s').read_text()
 d=once(d,' include "native_background.s"',' include "recovery_background_single_read.s"')
 (out/'recovery_background_device.s').write_text(d)
 return once(s,' include "recovery_state_menu_display_device.s"',f' include "{out}/recovery_background_device.s"')
def build(out,history,display):
 path=P/'tools/recovery_menu_paula_build.py';src=path.read_text()
 assert hashlib.sha256(path.read_bytes()).hexdigest()=='fd58f026a867cb3ae467a1115e9341bdfc6c011fed290a928a44e047f025f521'
 src=once(src,"(out/'recovery_menu_paula_target.s').write_text(s)","s=prepare(s,out)\n (out/'recovery_menu_paula_target.s').write_text(s)")
 # Device contains the renderer. Preserve all surrounding bytes relative to labels.
 src=once(src,"assert len(device)==1750 and hashlib.sha256(device).hexdigest()=='85b142d8ac84d53f4f5bb6f5143b28d1a07183989b71f2aeeeacaa0a3f920bad'","assert len(device)==1782 # Background grows 32 bytes; dispatcher/planner still pinned.")
 # Assemble a same-layout frozen reference with padding instead of new code.
 # Byte comparison then covers every byte outside the background routine,
 # including relocated device/runner references, sprites, clocks and adapter.
 src=once(src,"data=(out/'target.bin').read_bytes()", """data=(out/'target.bin').read_bytes()
 ref_device=(P/'src/recovery_state_menu_display_device.s').read_text()
 assert ref_device.count(' include "native_background.s"')==1
 ref_device=ref_device.replace(' include "native_background.s"',' include "native_background.s"\\n dcb.b 32,0')
 (out/'recovery_background_isolation_device.s').write_text(ref_device)
 ref_source=s.replace(str(out/'recovery_background_device.s'),str(out/'recovery_background_isolation_device.s'))
 assert ref_source!=s
 (out/'recovery_background_isolation_target.s').write_text(ref_source)
 asm(out/'recovery_background_isolation_target.s',out/'isolation-reference.bin')
 ref=(out/'isolation-reference.bin').read_bytes()
 lo,hi=symbols['nes_draw_background'],symbols['nes_draw_sprites_8x8']
 assert hi-lo==236 and len(ref)==len(data)
 assert data[:lo]==ref[:lo] and data[hi:]==ref[hi:], 'non-background linked bytes changed'""")
 ns={'__file__':str(path),'__name__':'recovery_background_frozen_build','prepare':prepare}
 exec(compile(src,str(path),'exec'),ns);ns['build'](out,history,display)
 meta=json.loads((out/'build.json').read_text());meta['background_variant']='compact-paired-single-read';meta['profiling']=False;(out/'build.json').write_text(json.dumps(meta,indent=2)+'\n')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);a.add_argument('--history',choices=('default','right_hold','move_back'),default='default');a.add_argument('--display',type=int,choices=(0,1),default=1);v=a.parse_args();build(v.output.resolve(),v.history,v.display)
