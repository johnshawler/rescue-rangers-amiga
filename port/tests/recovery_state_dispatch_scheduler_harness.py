"""PUBLIC ROM-free harness; reuse frozen native ABI/access instrumentation."""
from recovery_state_dispatch_active_harness import *
SIZES=SIZES+(74,0,0,22,0,10,514,0)

def assemble():
 names=('recovery_state_dispatch_scheduler','recovery_state_dispatch_active',
        'recovery_state_dispatch_palette','recovery_state_dispatch_prefix')+NAMES+('recovery_general_task_scheduler','recovery_startup_fade_continue','recovery_gameplay_frame_yield','recovery_music_empty_queue_entry','recovery_music_active_control','recovery_music_duration_prepare','recovery_music_active_envelope','recovery_music_duration_progress')
 source=b'\n'.join((PORT/'src'/f'{n}.s').read_bytes() for n in names)
 with tempfile.TemporaryDirectory() as t:
  src,out=Path(t)/'dispatch.s',Path(t)/'dispatch.bin';src.write_bytes(source)
  subprocess.run([os.environ['VASM'],'-quiet','-m68020','-Fbin','-o',str(out),str(src)],check=True)
  code=out.read_bytes()
 assert CODE+len(code)<RAM-16
 return code

FrozenNative=Native
class Native(FrozenNative):
 def __init__(self,code,resource):
  super().__init__(code,resource)
  original=self.trace
  def trace(mode,width,addr,value):
   original(mode,width,addr,value)
   if mode=='W' and addr==JOURNAL and width==1 and value and self.mem.r16(CTX) in (0x8374,0x86b2):
    event=self.events[-1]
    if 0x8000<=event[1]<0xc000:self.events[-1]=('resource',*event[1:])
  self.trace=trace;self.mem.set_trace_func(trace)
