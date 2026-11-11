"""Private initial fixed-action composition selector."""
from recovery_bank_loader_frame_oracle import ControllerBus,SHA,validation_reads,select_boundary as old,log_resource as old_log
ENTRIES=(51520, 51526, 51532, 51563, 51664, 51743, 51761, 51790, 51874, 51910, 51930, 51940, 52080, 52083, 52088, 52110, 52127, 52140, 52147, 52172, 52185, 52233, 52248, 52257, 52320, 52333, 54543, 54544, 54617, 54650, 54659, 54664, 54682, 54693, 54704, 54712, 54723, 54734, 54738, 54788, 54831)
RETURN_SITES=(0xc946,0xc94c,0xc96b,0xc9d0,0xca1f,0xca31,0xca4e,0xcada,0xcae4,0xcb70,0xcb73,0xcb78,0xcb8e,0xcb9f,0xcbb3,0xcbcc,0xcbd9,0xcc09,0xcc18,0xcc21,0xcc60,0xcc6d,0xd57a,0xd583,0xd588,0xd5a5,0xd5b0,0xd5b8,0xd5c3,0xd5ce,0xd62f)
EXITS=(0xcf08,0xcf31,0xd3e7,0xd40b,0xd460,0xe01b,0xe06b,0xe817,0xea8f,0xed7a,0xf000,0xf066,0xf0fb,0xf31d,0xf379,0xff53,0xcc9f,0xcd50,0xd05e)
def select_boundary(ref,bus,event):
 if ref.pc in ENTRIES:
  ret=((bus[256+((ref.sp+1)&255)]|bus[256+((ref.sp+2)&255)]<<8)+1)&65535
  return (-1,None,None) if event else (1,150,EXITS+(() if ret in RETURN_SITES else (ret,)))
 return old(ref,bus,event)
def log_resource(ref,bus,index):return old_log(ref,bus,135 if index==150 else index)
