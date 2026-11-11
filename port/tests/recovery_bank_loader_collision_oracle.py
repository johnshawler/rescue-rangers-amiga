"""Private static-region boundary bookkeeping; original executes first."""
from recovery_bank_loader_action_oracle import ControllerBus,SHA,validation_reads,select_boundary as old,log_resource as old_log,RETURN_SITES
E151=(60047, 60064, 60167, 60172, 60175, 60176, 60219, 60730, 60737, 60763, 60770, 60794, 60825, 60917, 60963, 61440, 61447, 61454, 61500, 61503, 61524, 61533, 61542, 61549, 61556, 61609, 61612, 61633, 61642, 61651, 61658, 61661, 61670, 61671, 61678, 61681, 61690, 61691, 61713, 61720, 61757, 61763, 61766, 61786, 61789, 61801, 61808, 61847, 61853, 61856, 61865, 61868, 61870, 61890, 61899, 61902, 61911, 61930, 61933, 61937, 61944, 61947, 61950, 61968, 61971, 61975, 61982, 62012, 62042, 62079, 62114, 62149, 62186, 62194, 62200, 62203, 62237, 62886, 62908, 62923, 63020, 63021, 63056, 63063, 63126, 63196, 63265, 63294, 63308, 63318, 63340, 63362, 63411, 63432, 63442, 63460)
E140=(32768, 32799, 32809, 32819, 32848, 36373, 36376, 36378, 36402, 33212, 35784, 35798, 35874, 36664, 36684, 36732, 36739, 36754, 36762)
REGIONS={140:((32768, 32935), (33212, 33228), (35784, 35875), (36373, 36481), (36664, 36806)),150:((51520, 52130), (52140, 52383), (54543, 54780), (54788, 54871)),151:((60047, 60410), (60730, 61099), (61440, 62248), (62886, 63486))}
RETURNS={140:(32799, 32809, 32819, 32848, 35798, 35874, 36376, 36402, 36684, 36732, 36739, 36754, 36762),150:RETURN_SITES,151:(60064, 60167, 60172, 60175, 60737, 60770, 61447, 61454, 61500, 61524, 61533, 61549, 61556, 61609, 61633, 61642, 61658, 61661, 61670, 61678, 61681, 61690, 61713, 61720, 61757, 61763, 61766, 61786, 61789, 61801, 61808, 61847, 61853, 61856, 61865, 61868, 61890, 61899, 61902, 61911, 61930, 61933, 61944, 61947, 61950, 61968, 61971, 62194, 62200, 62908, 62923, 63056, 63063, 63294, 63318, 63340, 63411, 63442, 63460)}
def select_boundary(ref,bus,event):
 if ref.pc==0xd40b:return (-1,None,None)
 idx=151 if ref.pc in E151 else 140 if bus.mapper.bank==6 and ref.pc in E140 else None
 if idx is not None:return (-1,None,None) if event else (1,idx,())
 return old(ref,bus,event)
def log_resource(ref,bus,index):return old_log(ref,bus,135 if index in (140,151) else index)

def raw_module_result(before,rom,index):
 """Separate original-first raw-module oracle; never changes persistent reference/native."""
 from recovery_test_active_command0e_rom import Ricoh
 import struct
 b=ControllerBus(rom);b.map_bank(before[3][3]);b[:2048]=before[0];b.events.clear()
 c=before[1];m=Ricoh(memory=b);m.pc=int.from_bytes(c[:2],'big');m.a,m.x,m.y,m.p,m.sp=c[2:7]
 for _ in range(200000):
  opcode=b[m.pc];log_resource(m,b,index);m.step()
  if opcode==0x6c or opcode==0x60 and m.pc not in RETURNS[index] or not any(a<=m.pc<z for a,z in REGIONS[index]):break
 else:raise AssertionError('raw module original budget')
 return bytes(b[:2048]),struct.pack('>H6B',m.pc,m.a,m.x,m.y,m.p,m.sp,c[7]),b.events
