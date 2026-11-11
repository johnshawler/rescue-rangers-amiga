#!/usr/bin/env python3
"""Complete linked-target fault regressions, including reviewed counterexamples.
Synthetic CIA clock and injected malformed state are test-only. This proves
control flow, register writes, drain duration and error retention, not real-core
fault PCM. Valid histories have separate fresh PUAE playback checks.
"""
from pathlib import Path
import argparse,json,struct,hashlib
import machine68k

def test(out):
 code=(out/'target.bin').read_bytes();symbols=json.loads((out/'target.symbols.json').read_text());BASE=0x1000
 # Locate actual guard comparisons in the runner, independently of failure stubs.
 for name,pattern in [('loop_guard', '0cae00002ee0000c'),('history_guard','0c830000007f'),('event_guard','4aae0014')]:
  blob=bytes.fromhex(pattern);assert code.count(blob)==1
  symbols[name]=code.index(blob)
 rows=[]
 cases=[('loop_budget_guard','loop_guard',0,9,0,0,-6),
        ('input_history_guard','history_guard',0,9,0,0,-7),
        ('repeated_event_guard','event_guard',0,9,0,0,-8),
        ('count_over_limit','capture_journal',33596,9,6,0,-3),
        ('helper_over_limit','capture_journal',0,72,0,0,-3),
        ('helper48_missing_sentinel','capture_journal',0,48,12,0,-3),
        ('capture_capacity','capture_journal',0,9,0,262144,-3),
        ('capture_DMA_capacity','capture_journal',0,6,298,262000,-3),
        ('failed_minus4','failed',0,9,0,0,-4),
        ('failed_minus1','failed',0,9,0,0,-1),
        ('adapter_rejection_bridge','paula_consume',1,20,6,0,-4),
        ('adapter_invalid_sentinel','paula_consume',0,9,65535,0,-4),
        ('adapter_short_header','paula_consume',0,9,1,0,-4),
        ('renderer_rejection_bridge','paula_render',0,9,0,0,-5)]
 for name,entry,count,helper,size,used,error in cases:
  m=machine68k.Machine(machine68k.CPUType.M68EC020,16384);mem,cpu=m.mem,m.cpu;mem.w_block(BASE,code)
  J,R,P,S=0x200000,0x220000,BASE+symbols['report'],0x240000
  mem.w16(J,count);mem.w16(R+6,helper);mem.w16(R+8,size);mem.w32(P+72,BASE+symbols['capture']);mem.w32(P+76,used)
  if entry=='loop_guard':mem.w32(P+12,12000)
  if entry=='history_guard':mem.w32(P+84,128);cpu.w_reg(3,128)
  if entry=='event_guard':mem.w32(P+20,1)
  if entry=='paula_consume':mem.w_block(J,bytes.fromhex('000140151001'))
  for i in range(4):mem.w16(0xdff0a8+16*i,20+i)
  mem.w16(0xdff096,0x820f);clock=[0];writes=[]
  def trace(mode,width,addr,value):
   if mode=='R' and addr==0xbfd700:
    clock[0]+=100;v=~clock[0]&0xffffffff
    for a,shift in ((0xbfd700,24),(0xbfd600,16),(0xbfd500,8),(0xbfd400,0)):mem.w8(a,(v>>shift)&255)
   if mode=='W' and 0xdff000<=addr<0xdff200:writes.append((addr,value,clock[0]))
  mem.set_trace_func(trace);cpu.w_sr(0x2700);cpu.w_sp(S);mem.w32(S,0x900)
  cpu.w_reg(0,0 if entry in ('loop_guard','history_guard','event_guard') else error&0xffffffff);cpu.w_reg(10,J);cpu.w_reg(12,R);cpu.w_reg(14,P);cpu.w_pc(BASE+symbols[entry]);mem.set_trace_mode(True)
  for _ in range(1000):
   cpu.execute(1000)
   if cpu.r_pc()==BASE+symbols['stop']:break
  else:raise AssertionError(('failed to enter permanent stop',name,hex(cpu.r_pc())))
  assert mem.r32(P+8)==error&0xffffffff,(name,mem.r32(P+8),error)
  assert all(mem.r16(0xdff0a8+16*i)==0 for i in range(4)),name
  zeros=[(a,v,t) for a,v,t in writes if a in [0xdff0a8+16*i for i in range(4)]]
  assert len(zeros)>=4 and all(v==0 for a,v,t in zeros),name
  off=[(a,v,t) for a,v,t in writes if a==0xdff096]
  assert off and all(v==15 for a,v,t in off),('DMA not disabled or re-enabled',name,off)
  assert off[0][2]-zeros[3][2]>=14188,('drain missing',name,writes)
  before=len(writes);cpu.execute(100000);mem.set_trace_mode(False)
  assert cpu.r_pc()==BASE+symbols['stop'] and len(writes)==before and mem.r32(P+8)==error&0xffffffff
  assert bytes(mem.r_block(BASE,code.index(b'CDRDIS01')))==code[:code.index(b'CDRDIS01')]
  if entry=='paula_render':assert mem.r32(BASE+symbols['startup_display_report']+8)==0xffffffff
  rows.append(dict(case=name,status='PASS',retained_error=error,zero_volume_writes=len(zeros),DMA_disable_writes=len(off),first_drain_ticks=off[0][2]-zeros[3][2],permanent_stop=True))
 result=dict(status='PASS',target_sha256=hashlib.sha256(code).hexdigest(),scope=__doc__,cases=rows)
 (out/'complete-target-rejections.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result
def compare_layout(out,baseline):
 """Prove a diagnostic-only binary patch against the preserved v6 target."""
 old=(baseline/'target.bin').read_bytes();new=(out/'target.bin').read_bytes()
 a=json.loads((baseline/'target.symbols.json').read_text());b=json.loads((out/'target.symbols.json').read_text())
 assert len(old)==len(new) and all(b[k]==v for k,v in a.items())
 assert (baseline/'adapter.bin').read_bytes()==(out/'adapter.bin').read_bytes()
 allowed=set();operands=[]
 for pattern in ('0cae00002ee0000c','0c830000007f','4aae0014'):
  blob=bytes.fromhex(pattern);assert old.count(blob)==new.count(blob)==1
  site=new.index(blob);assert old.index(blob)==site
  pos=site+len(blob)+2;allowed.update(range(pos,pos+2));operands.append([pos,pos+2])
 start=b['paula_loop_limit'];assert old[start:start+14]==bytes.fromhex('4e71')*7
 allowed.update(range(start,start+14))
 changed=[i for i,(x,y) in enumerate(zip(old,new)) if x!=y]
 assert changed and set(changed)<=allowed
 result=dict(status='PASS',payload_bytes=len(new),all_previous_symbol_addresses_equal=True,adapter_identical=True,allowed_branch_operand_ranges=operands,unreachable_padding_reused=[start,start+14],changed_offsets=changed,changed_bytes=len(changed),baseline_target_sha256=hashlib.sha256(old).hexdigest(),target_sha256=hashlib.sha256(new).hexdigest(),scope='Only three guard branch-displacement words and14 formerly unreachable padding bytes differ; no successful-path instruction size/address or frozen native/data/adapter bytes change.')
 (out/'v6-layout-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--baseline',type=Path);a=p.parse_args();test(a.output)
 if a.baseline:compare_layout(a.output,a.baseline)
