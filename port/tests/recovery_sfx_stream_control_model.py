"""Declarative ROM-free high-bit stream control and channel shutdown model."""
def model(state,ctx,resource):
 if ctx[:2]!=bytes.fromhex('8235'):return None
 s=bytearray(state);a,x,y,p,sp=ctx[2:7];events=[]
 def nz(v):
  nonlocal p
  v&=255;p=(p&0x7d)|(v&128)|(2 if v==0 else 0);return v
 def store(at,v):s[at]=v;events.append(('ram',at,v))
 def push(v):
  nonlocal sp
  store(256+sp,v);sp=(sp-1)&255
 def pop():
  nonlocal sp
  sp=(sp+1)&255;return s[256+sp]
 def call(ret):push(ret>>8);push(ret&255)
 def rts():return ((pop()|(pop()<<8))+1)&65535
 def lsr(v):
  nonlocal p
  p=(p&254)|(v&1);return nz(v>>1)
 def asl(v):
  nonlocal p
  p=(p&254)|(v>>7);return nz(v<<1)
 def apu(at):events.append(('apu',at,a,1))
 store(0xce,y);a=nz(s[0xd7]);a=lsr(a)
 if p&1:call(0x823e);pc=0x80fb
 else:
  a=nz(0)
  for at in (0xce,0xd0,0xd1,0xd7,0xd8):store(at,a)
  a=nz(s[0xcf])
  if a:
   a=nz(a^15);store(0xcf,a);call(0x81ad)
   a=nz(s[0xcf]);push(a);x=nz(3)
   while True:
    a=nz(s[0xcf]);a=lsr(a)
    if not p&1:
     call(0x81cc);a=nz(x);a=nz(a&3);a=nz(a^3);a=asl(asl(a));y=nz(a);a=nz(0x30)
     p=(p&254)|(y>=8);nz(y-8)
     if y==8:a=nz(0)
     apu(0x4000+y);assert rts()==0x81cd
     a=nz(s[0x754+x]);a=nz(a|s[0x750+x])
     if a:a=nz(255);store(0x77c+x,a)
    store(0xcf,lsr(s[0xcf]));x=nz(x-1)
    if x&128:break
   a=nz(pop());store(0xcf,a);a=nz(8);apu(0x4001);apu(0x4005);a=nz(15);apu(0x4015);assert rts()==0x81ae
   a=nz(0);store(0xcf,a)
  pc=rts()
 return bytes(s),pc.to_bytes(2,'big')+bytes((a,x,y,p,sp,ctx[7])),events

def validation_reads(state,ctx,resource):return []
