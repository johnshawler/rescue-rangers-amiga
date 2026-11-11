"""ROM-free declarative effects models, independent of generated native code."""
def resource_model(s,c,r):
 if c[:2]!=bytes.fromhex('8000'):return None
 # Independent bounded declarative stream parsing, no original opcode decoder.
 ptr=r[0x3d+c[3]]+256*r[0x47+c[3]];pos=ptr;commands=[]
 while True:
  if not 0x8000<=pos<0xc000 or pos-ptr>=4094:return None
  high=r[pos-0x8000];pos+=1
  if high==0:break
  if pos+1>=0xc000:return None
  low,count=r[pos-0x8000:pos-0x8000+2];pos+=2
  n=count+1 if count<=128 else 1
  if pos+n>=0xc000 or pos+n-ptr>=4094:return None
  commands.append((high,low,count,bytes(r[pos-0x8000:pos-0x8000+n])));pos+=n
 ram=bytearray(s);cc=bytearray(c);events=[];y=0
 def w(a,v):ram[a]=v;events.append(('ram',a,v))
 def resource(a):
  v=r[a-0x8000];events.append(('resource',a,v,0));return v
 def stream():return resource(ram[0]+256*ram[1]+y)
 def p(a,v,k=1):events.append(('ppu',a,v,k))
 def advance(low):
  nonlocal y
  w(0x100+c[6],0x80);w(0x100+((c[6]-1)&255),low)
  y=(y+1)&255
  if y==0:w(1,(ram[1]+1)&255)
 w(0,resource(0x803d+c[3]));w(1,resource(0x8047+c[3]))
 for high,low,count,data in commands:
  p(0x2002,0,0);p(0x2006,stream());advance(0x18)
  p(0x2006,stream());advance(0x20)
  w(2,stream());advance(0x27)
  for value in data:
   p(0x2007,stream());advance(0x2f);w(2,(ram[2]-1)&255)
 p(0x2002,0,0);assert stream()==0
 target=((ram[256+((c[6]+1)&255)]|ram[256+((c[6]+2)&255)]<<8)+1)&65535
 cc[:2]=target.to_bytes(2,'big');cc[2]=0;cc[4]=y;cc[5]=(cc[5]&0x7d)|2;cc[6]=(c[6]+2)&255
 return bytes(ram),bytes(cc),events

def model(s,c,r):
 pc=int.from_bytes(c[:2],'big')
 if pc==0x8000:return resource_model(s,c,r)
 if pc not in (0xff53,0x9003,0x9034,0x9039,0x9041,0xf3e5,0xf3f1,0x910c):return None
 if pc==0xff53 and s[0xf6]:return None
 if pc==0x9003 and c[6]<43:return None
 if pc in (0x9039,0x9041,0x910c) and s[0x31]!=11:return None
 ram=bytearray(s);q=bytearray(c);ev=[];sp=c[6];p=c[5];a,x,y=c[2:5]
 def w(at,v):ram[at]=v;ev.append(('ram',at,v))
 def push(v):
  nonlocal sp
  w(256+sp,v);sp=(sp-1)&255
 def pop():
  nonlocal sp
  sp=(sp+1)&255;return ram[256+sp]
 def jsr(ret):push(ret>>8);push(ret&255)
 def resource(at):v=r[at-0x8000];ev.append(('resource',at,v,0));return v
 if pc==0xff53:
  w(0xf1,a);w(0xf4,a);w(0xf5,(ram[0xf5]+1)&255)
  for i in range(5):ev.append(('mapper',0xfff0,a>>i,ram[0xf5]))
  w(0xf5,0);p=(p&124)|2|((a>>3)&1);a=0;lo=pop();pc=((pop()<<8|lo)+1)&65535
 elif pc==0x9003:
  push(ram[0x4d0]);push(ram[0x4d1]);jsr(0x900d)
  for i in reversed(range(40)):w(256+i,ram[512+i])
  lo=pop();assert (pop()<<8|lo)==0x900d
  w(512,248);w(516,248)
  for at in (0x4d0,0x4d1,250,252,251,253):w(at,0)
  a=y=(ram[49]*4)&255;push(a);x=resource(0x91f3+y)
  p=(p&124)|((ram[49]>>6)&1)|(x&128)
  ret=0x9033 if x else 0x9040
  if not x:x=9
  jsr(ret);pc=0x8000
 elif pc==0x9034:
  x=8;p&=125;jsr(0x9038);pc=0x8000
 elif pc in (0x9039,0x9041):
  y=pop();w(27,resource(0x91f4+y)|128);v=resource(0x91f3+y)
  if v:
   result=(v-4)&255;p=(p&191)|(64 if ((v^result)&(v^4)&128) else 0);v=result
  y=(v*16)&255
  for i in range(16):w(0x320+i,resource(0x922f+y));y=(y+1)&255
  for i in reversed(range(4)):w(512+i,resource(0x922b+i))
  w(26,0x8d)
  for i in range(16):w(0x330+i,resource(0x928f+i))
  a,x,y=11,16,112;p=(p&124)|1;jsr(0x910b);pc=0xf3e5
 elif pc==0xf3e5:
  push(ram[0xf1]);jsr(0xf3ea);w(240,(ram[240]-1)&255);a=30;w(254,a);ev.append(('ppu',0x2001,a,1))
  pop();pop();jsr(0xf3ed);p&=125;pc=0xff04
 elif pc==0xf3f1:
  a=pop();p=(p&125)|(a&128)|(2 if not a else 0);pc=0xff53
 elif pc==0x910c:
  a=8;w(0x97,8);jsr(0x911b);p=(p&124)|1;pc=0xf392
 q[:2]=pc.to_bytes(2,'big');q[2:7]=bytes((a,x,y,p,sp))
 return bytes(ram),bytes(q),ev

def validation_reads(r,x):
 reads=[0x47+x,0x3d+x];pos=r[0x3d+x]+256*r[0x47+x]-0x8000;used=0
 while 0<=pos<16384:
  used+=1
  if used>4094:return reads
  reads.append(pos);v=r[pos];pos+=1
  if v==0:return reads
  if not 0<=pos+1<16384:return reads
  reads.append(pos+1);n=r[pos+1];n=n+1 if n<=128 else 1
  used+=2+n;pos+=2+n
  if used>4094:return reads
 return reads
