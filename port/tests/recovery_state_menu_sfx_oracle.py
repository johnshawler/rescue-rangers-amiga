"""Private boundary selection from original state only; original instructions run first."""
from recovery_state_dispatch_menu_oracle import ControllerBus,SHA,select_boundary as previous,log_resource as previous_log
from recovery_state_menu_sfx_models import MODELS
PCS={0xa07b:56,0xf379:56,0xa086:56,0x8003:57,0x810d:58,0x8151:59,0x8224:60,0x8006:61,0x8298:61,0x81a3:62,0x8060:63,0x807a:63,0x82b0:64,0x82c0:64,0x82dc:65,0x830b:66,0x831b:66,0x8052:67,0x8235:69}
def select_boundary(ref,bus,event):
 if ref.pc in (0xa055,0x80fb,0x8249,0x8152,0xc5f8):return -1,None,None
 if ref.pc==0xc0bf and bus.mapper.bank==2 and bus[0xdb]<8 and bus[0xdc+bus[0xdb]]!=0x88:return (-1,None,None) if event else (1,70,(0x8003,))
 index=PCS.get(ref.pc)
 if ref.pc==0x8151 and bus[0xc0]!=1:index=71
 if ref.pc==0x8003 and ref.a!=0x27:index=None
 if ref.pc==0x86b2 and ref.x<4:index=68
 if ref.pc in (0x8085,0xc0f6) and (bus[0xcf] or bus[0xd0] or bus[0xd1]):index=63 if ref.pc==0x8085 else 67
 if index is None:return previous(ref,bus,event)
 if event:return -1,None,None
 c=ref.pc.to_bytes(2,'big')+bytes((ref.a,ref.x,ref.y,(ref.p&0xef)|0x20,ref.sp,0xa7))
 # A declarative endpoint is only an oracle endpoint, never native input.
 r=bytes(bus[0x8000:0xc000]);predicted=MODELS[index](bytes(bus[:2048]),c,r)
 if predicted is None:return -1,None,None
 return 1,index,(int.from_bytes(predicted[1][:2],'big'),)
def log_resource(ref,bus,index):
 if index<56:return previous_log(ref,bus,index)
 pc=ref.pc;a=None
 if index==56 and pc==0xa07b:a=0xa0e1+ref.y
 if index==57 and pc in (0x80f0,0x80fd,0x8102):a={0x80f0:0x8a00,0x80fd:0x8a04+ref.x,0x8102:0x8a03+ref.x}[pc]
 if index==58 and pc==0x810d:a=bus[0xc1]+256*bus[0xc2]
 if index in (60,61,65) and pc==0x835a:a=bus[0xd0]+256*bus[0xd1]
 if index in (64,65) and pc in (0x868c,0x8693):a=0x8a02 if pc==0x868c else 0x8a01
 if index==65 and pc in (0x802c,0x8030):a=(bus[0xc1]+256*bus[0xc2]+ref.y)&65535
 if index==66:
  if pc in (0x8626,0x862b):a=(0x8934 if pc==0x8626 else 0x8935)+ref.y
  if pc==0x8638:a=(bus[0xc5]+256*bus[0xc6]+ref.y)&65535
 if index==68:
  if pc in (0x802c,0x8030,0x86cb,0x86e0,0x86ef,0x86f5,0x8703,0x8766,0x87b3,0x8838,0x88f5):
   ptr=0xc1 if pc in (0x802c,0x8030) else 0xc5;a=(bus[ptr]+256*bus[ptr+1]+ref.y)&65535
  elif pc in (0x86d1,0x86e8,0x870b,0x8846,0x88c8,0x88d0,0x88df,0x88e5):a=({0x86d1:0x890e,0x86e8:0x890e,0x870b:0x890e,0x8846:0x892e,0x88c8:0x8934,0x88d0:0x8935,0x88df:0x8934,0x88e5:0x8935}[pc]+ref.y)&65535
 if a is not None:bus.events.append(('resource',a,bus[a],0))
