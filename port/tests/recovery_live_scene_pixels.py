"""Independent end-device and retained-last-frame check for rendering-disabled stop."""
import inspect,copy
import recovery_state_menu_display_pixels as pixels

def expected(reference,rom):
 # Reuse independent event/device implementation exactly up to its old
 # enabled-mode assertion, then return current state without drawing a fake view.
 source=inspect.getsource(pixels.expected)
 prefix,rest=source.split(' assert (ctrl,mask,sx,sy,mapper.control)==',1)
 assert prefix.startswith('def expected(rom):')
 source=prefix+''' state=bytes((ctrl,mask,latch,sx,sy,oa))+struct.pack('>HH',v,(hi<<8)|lastlo)+bytes((mapper.control,mapper.chr0,mapper.chr1,mapper.prg,0,0))+struct.pack('>III',0,ppu_count,mapper_count)
 return nt,pal,oam,state
'''
 ns=dict(pixels.__dict__);ns['oracle']=lambda _:reference;exec(source,ns)
 nt,pal,oam,state=ns['expected'](rom)
 # Plane storage deliberately retains the last genuinely rendered RTI view.
 results,bus,instructions=reference
 last=max(i for i,result in enumerate(results) if result[0] in (8,20,42))
 limited=copy.copy(bus);limited.events=bus.events[:bus.event_ends[last]]
 old=pixels.oracle
 try:
  pixels.oracle=lambda _:(results[:last+1],limited,instructions)
  _,_,_,_,chrdata,frame,_,_=pixels.expected(rom)
 finally:pixels.oracle=old
 return nt,pal,oam,chrdata,frame,state

def verify_screen(chip,path,device,palette,copper):
 import struct
 from PIL import Image
 assert chip[device+1]==0,'original rendering disabled'
 # This actual scene endpoint has original universal backdrop $0F, which the
 # existing declared RGB4 palette maps to black. Do not generalize all blanks.
 assert chip[palette]==15 and struct.unpack_from('>H',chip,copper+90)[0]==0
 im=Image.open(path).convert('RGB')
 assert im.size==(720,287)
 viewport=im.crop((40,18,680,274))
 assert viewport.getbbox() is None,'disabled original backdrop must be actual black pixels'
 return dict(status='PASS',disabled_rendering=True,original_backdrop_index=15,declared_RGB4=0,black_viewport_pixels=640*256,retained_planes_are_previous_frame=True)
