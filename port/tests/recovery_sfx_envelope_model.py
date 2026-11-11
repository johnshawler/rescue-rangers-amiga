"""ROM-free domain model for indexed envelopes; no opcode interpretation.

The caller supplies arbitrary bounded bank3 data. The model emits semantic
resource/APU effects and all original RAM stores, including dead stack bytes.
"""
def envelope(state,ctx,resource):
 s=bytearray(state);a,x,y,p,sp=ctx[2:7];events=[]
 assert int.from_bytes(ctx[:2],'big')==0x86b2 and x in range(4)
 pointer=s[0xc5]|s[0xc6]<<8
 assert 0x8000<=pointer<=0xbff8 and s[0x704+x]&7<=4
 targets=(0x86c9,0x86de,0x8718,0x86fa,0x890d)
 assert all(resource[0x6bf+2*i]|resource[0x6c0+2*i]<<8==v for i,v in enumerate(targets))
 assert resource[0x92e]==0
 def store(addr,v):
  s[addr]=v&255;events.append(('ram',addr,v&255))
 def read(addr):
  assert 0x8000<=addr<=0xbfff
  v=resource[addr-0x8000];events.append(('resource',addr,v,0));return v
 def nz(v):
  nonlocal p
  v&=255;p=(p&0x7d)|(v&128)|(2 if v==0 else 0);return v
 def carry(v):
  nonlocal p
  p=(p&254)|bool(v)
 def adc(v,w):
  nonlocal p
  total=v+w+(p&1);r=total&255
  p=(p&0x3c)|(total>255)|(64 if (~(v^w)&(v^r)&128) else 0);return nz(r)
 def sub(v,w):
  nonlocal p
  total=v-w-(1-(p&1));r=total&255
  p=(p&0x3c)|(total>=0)|(64 if ((v^w)&(v^r)&128) else 0);return nz(r)
 def compare(v,w):
  carry(v>=w);nz((v-w)&255)
 def asl(v):carry(v&128);return nz(v<<1)
 def lsr(v):carry(v&1);return nz(v>>1)
 def rol(v):
  old=p&1;carry(v&128);return nz((v<<1)|old)
 def ror(v):
  old=p&1;carry(v&1);return nz((v>>1)|(old<<7))
 def push(v):
  nonlocal sp
  store(0x100+sp,v);sp=(sp-1)&255
 def pop():
  nonlocal sp
  sp=(sp+1)&255;return s[0x100+sp]
 def frame(ret):push(ret>>8);push(ret&255)
 def rts():return ((pop()|(pop()<<8))+1)&65535
 def mul(ret):
  nonlocal a,y
  frame(ret);a=nz(0);store(0xc2,a);y=nz(8)
  for _ in range(8):
   store(0xc2,asl(s[0xc2]));store(0xc1,rol(s[0xc1]))
   if p&1:
    carry(0);a=nz(s[0xc2]);a=adc(a,s[0xc4]);store(0xc2,a)
    a=nz(s[0xc1]);a=adc(a,0);store(0xc1,a)
   y=nz(y-1)
  assert rts()==ret+1
 def apu(ret):
  nonlocal a,y
  frame(ret);push(a);a=nz(x);a=nz(a&3);a=nz(a^3);a=asl(asl(a));store(0xc4,y)
  a=nz(a|s[0xc4]);y=nz(a);a=nz(pop());events.append(('apu',0x4000+y,a,1));assert rts()==ret+1
 def instrument(index):return read(pointer+index)
 # Envelope stage dispatch consumes the real 8023 JSR frame and leaves none.
 a=nz(s[0x710+x]);store(0xc4,a);a=nz(s[0x704+x]);a=nz(a&7);stage=a
 frame(0x86be);a=asl(a);y=nz(a);y=nz(y+1)
 a=nz(pop());store(0xc1,a);a=nz(pop());store(0xc2,a)
 base=s[0xc1]|s[0xc2]<<8;a=nz(read(base+y));push(a);y=nz(y+1)
 a=nz(read(base+y));store(0xc2,a);a=nz(pop());store(0xc1,a)
 if stage==4:
  pc=rts();return bytes(s),pc.to_bytes(2,'big')+bytes((a,x,y,p,sp,ctx[7])),events
 # Attack, decay, sustain, and release produce the next amplitude.
 update=False;advance=False
 if stage==0:
  y=nz(0);a=nz(instrument(y));y=nz(a);a=nz(s[0xc4]);carry(0);a=adc(a,read(0x890e+y))
  saturated=bool(p&1)
  if not saturated:compare(a,0xf0);saturated=bool(p&1)
  if saturated:a=nz(0xf0);advance=True
  update=True
 elif stage==1:
  y=nz(1);a=nz(instrument(y));floor=a==0
  if not floor:
   y=nz(a);a=nz(s[0xc4]);carry(1);a=sub(a,read(0x890e+y));floor=not p&1
   if not floor:y=nz(2);compare(a,instrument(y));floor=not p&1
  if floor:y=nz(2);a=nz(instrument(y));advance=True
  update=True
 elif stage==3:
  a=nz(x);a=nz(a&3);compare(a,1);silence=bool(p&2)
  if not silence:
   y=nz(3);a=nz(instrument(y))
   if a:
    y=nz(a);a=nz(s[0xc4]);carry(1);a=sub(a,read(0x890e+y));silence=not p&1;update=True
  else:update=True
  if silence:a=nz(0);advance=True;update=True
 if advance:store(0x704+x,nz(s[0x704+x]+1))
 if update:store(0x710+x,a)
 # SFX always publishes directly, independently of CF, CD and CC.
 compare(x,0x28);a=nz(x);a=nz(a&3);compare(a,1)
 if p&2:
  a=nz(s[0x710+x])
  if a:a=nz(255)
 else:
  a=nz(s[0x710+x])
  for _ in range(4):a=lsr(a)
  a=nz(a^15);store(0xc3,a);y=nz(6);a=nz(instrument(y));compare(a,5)
  clipped=False
  if p&1:
   store(0xc4,a);y=nz(s[0x708+x]);a=nz(s[0x704+x]);a=asl(asl(a));a=nz(y)
   if p&1:a=nz(a^255)
   if a:
    store(0xc1,a);mul(0x8781);a=nz(s[0xc1]);a=lsr(lsr(a));compare(a,16);clipped=bool(p&1)
    if not clipped:
     compare(a,s[0xc3])
     if p&1:store(0xc3,a)
  if not clipped:
   a=nz(16);store(0xc4,a);a=nz(s[0x70c+x]);carry(1);a=sub(a,s[0xc3])
   # BIT sets N,V from operand and Z from conjunction.
   p=(p&0x3d)|(s[0xc4]&0xc0)|(2 if not a&s[0xc4] else 0)
   clipped=bool(p&2)
  if clipped:a=nz(s[0x70c+x]);a=nz(a&240)
 y=nz(0);apu(0x87a7)
 # Pitch modulation; preserve the original zero-high-byte fallback.
 a=nz(x);a=nz(a&3);y=nz(a);a=nz(s[0x77c+y]);fallback=bool(p&128)
 if not fallback:
  y=nz(5);a=nz(instrument(y));fallback=a==0
 if not fallback:
  store(0xc4,a);y=nz(s[0x708+x]);a=nz(s[0x704+x]);a=asl(asl(a));a=nz(y)
  if p&1:a=nz(a^255)
  fallback=a==0
 if not fallback:
  store(0xc1,a);mul(0x87cc);a=nz(s[0xc1])
  for _ in range(4):a=lsr(a);store(0xc2,ror(s[0xc2]))
  y=nz(a);a=nz(a|s[0xc2]);fallback=a==0
 if not fallback:
  a=nz(s[0x704+x]);subtract=bool(p&128)
  if not subtract:
   carry(0);a=nz(s[0xc2]);a=adc(a,s[0x720+x]);store(0xc2,a);a=nz(y);a=adc(a,s[0x724+x]);subtract=a==0
  if subtract:
   carry(1);a=nz(s[0x720+x]);a=sub(a,s[0xc2]);store(0xc2,a)
   a=nz(s[0x724+x]);store(0xc1,y);a=sub(a,s[0xc1])
  y=nz(a);fallback=y==0
 if fallback:a=nz(s[0x720+x]);store(0xc2,a);y=nz(s[0x724+x])
 compare(x,0x28);a=nz(s[0xd6])
 if p&128:
  a=nz(s[0xd8])
  if a:
   store(0xc4,a);store(0xc1,y);a=nz(s[0xc2]);push(a);mul(0x8822)
   a=nz(pop());carry(0);a=adc(a,s[0xc2]);store(0xc2,a);a=nz(0);a=adc(a,s[0xc1]);y=nz(a)
 a=nz(x);a=nz(a&3)
 if not a:
  a=nz(y);a=nz(a&15);y=nz(7);a=nz(a|instrument(y));store(0xc2,a);a=nz(0);store(0xc1,a)
 else:
  a=nz(y);y=nz(8)
  while True:
   y=nz(y-1);compare(a,read(0x892e+y))
   if p&1:break
  store(0xc1,a);a=nz(y);carry(0);a=adc(a,s[0xc1]);y=nz(a);a=nz(a&7);carry(0);a=adc(a,6);store(0xc1,a)
  a=nz(y);a=nz(a&56);a=nz(a^56)
  while a:
   store(0xc1,lsr(s[0xc1]));store(0xc2,ror(s[0xc2]));carry(1);a=sub(a,8)
  y=nz(0);a=nz(s[0x714+x])
  if a:
   if p&128:y=nz(y-1)
   carry(0);a=adc(a,s[0xc2]);store(0xc2,a);a=nz(y);a=adc(a,s[0xc1]);store(0xc1,a)
 y=nz(2);a=nz(s[0xc2]);apu(0x8883);a=nz(x);a=nz(a&3);y=nz(a);a=nz(s[0xc1]);compare(a,s[0x77c+y])
 if not p&2:
  store(0x77c+y,a);a=nz(a|8);y=nz(3);apu(0x8898)
 # Glide convergence and instrument modulation phase advancement.
 a=nz(s[0x704+x]);a=nz(a&32)
 if a:
  a=nz(s[0x718+x]);clear=a==0
  if not clear:
   y=nz(0);a=asl(a);push(p|0x30)
   if p&1:a=nz(a^255);carry(0);a=adc(a,1);y=nz(y-1)
   carry(0);a=adc(a,s[0x720+x]);store(0x720+x,a);a=nz(y);a=adc(a,s[0x724+x]);store(0x724+x,a)
   a=nz(s[0x71c+x]);a=asl(a);y=nz(a);carry(1);a=nz(s[0x720+x]);a=sub(a,read(0x8934+y))
   a=nz(s[0x724+x]);a=nz(a&63);a=sub(a,read(0x8935+y));a=nz(255);a=adc(a,0)
   p=pop()|48;a=adc(a,0)
   if a==0:
    a=nz(x)
    if a:
     a=nz(read(0x8934+y));store(0x720+x,a);a=nz(read(0x8935+y));store(0x724+x,a);clear=True
  if clear:a=nz(s[0x704+x]);a=nz(a&223);store(0x704+x,a)
 y=nz(4);a=nz(instrument(y));a=nz(a&127)
 if a:
  carry(0);a=adc(a,s[0x708+x]);store(0x708+x,a)
  if p&1:a=nz(s[0x704+x]);carry(0);a=adc(a,64);store(0x704+x,a)
 pc=rts()
 return bytes(s),pc.to_bytes(2,'big')+bytes((a,x,y,p,sp,ctx[7])),events
