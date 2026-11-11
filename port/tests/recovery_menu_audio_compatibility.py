"""Qualify actual frame-final snapshots against the unchanged native Paula planner.
Requires a private collection made by recovery_menu_audio_events.py.
No sound is played; this is a host functional contract check.
"""
import argparse,json,struct,subprocess,hashlib,collections,os
from pathlib import Path
import machine68k
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profiles',required=True,type=Path);args=p.parse_args()
PROFILES=args.profiles.resolve();OUT=PROFILES/'planner'
if OUT.is_relative_to(ROOT) and not OUT.is_relative_to(ROOT/'port/build'):
 raise ValueError('Private outputs inside this repository must stay in ignored port/build')
collection=json.loads((PROFILES/'collection.json').read_text())
assert collection['status']=='PASS' and collection['APU_writes']==15059
assert collection['composition_sha256']=='a8a31217696f2f3d30d629adf570b9723c171d965e25f267294a55dc1534496e'
assert collection['collector_sha256']==hashlib.sha256((ROOT/'port/tests/recovery_menu_audio_events.py').read_bytes()).hexdigest()
for row in collection['cases']:
 assert hashlib.sha256((PROFILES/(row['history']+'-private-events.json')).read_bytes()).hexdigest()==row['sha256']
OUT.mkdir(exist_ok=False)
SRC=ROOT/'port/src/experimental_direct_paula.c'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='5c5be6ac34df5fc7d9b72a081343abc262c762d8b67b142c9e585e6a24080420'
cc=os.getenv('PAULA_CC','m68k-linux-gnu-gcc')
subprocess.run([cc,'-m68020','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fno-pie','-nostdlib','-Wl,-Ttext=0x1000','-Wl,-e,experimental_direct_paula_plan',str(SRC),'-o',str(OUT/'unit.elf')],check=True)
subprocess.run([cc.replace('gcc','objcopy'),'-O','binary','--only-section=.text',str(OUT/'unit.elf'),str(OUT/'unit.bin')],check=True)
code=(OUT/'unit.bin').read_bytes();m=machine68k.Machine(machine68k.CPUType.M68EC020,2048);mem,cpu=m.mem,m.cpu;mem.w_block(0x1000,code);mem.w16(0x800,0x60fe)
calls=0;rejections=0

def plan(r,en):
 reasons=[];p=[];v=[];w=[]
 if en&~15:reasons.append('enable')
 if r[1]!=8 or r[5]!=8:reasons.append('sweep')
 if r[8] not in(0,255):reasons.append('triangle_linear')
 if any(r[x]&48!=48 for x in (0,4,12)):reasons.append('envelope_length')
 if r[14] not in(7,13,129):reasons.append('noise_mode')
 for i,b in enumerate((0,4,8)):
  t=r[b+2]+256*(r[b+3]&7);period=((64 if i<2 else 32)*(t+1)+7)//15
  vol=(2*(r[b]&15) if i<2 else 24) if en&(1<<i) and t>=(8 if i<2 else 2) and (i<2 or r[8]) else 0
  if period<124:
   if vol:reasons.append('audible_period_'+str(i))
   period=124
  p.append(period);v.append(vol);w.append(r[b]>>6 if i<2 else 4)
 p.append(160);v.append(2*(r[12]&15) if en&8 else 0);w.append({7:5,13:6,129:7}.get(r[14],7))
 return reasons,p+v+w

def call(r,en):
 global calls,rejections
 reasons,expected=plan(r,en);valid=not reasons
 mem.w_block(0x10000,bytes(r));mem.w_block(0x20000,b'G'*16+b'X'*24+b'H'*16)
 sp=0x1f0000;cpu.w_sr(0x2700);cpu.w_sp(sp);mem.w32(sp,0x800)
 for i,a in enumerate((0x10000,en,0x20010)):mem.w32(sp+4+4*i,a)
 saved={x:0x51000000+x for x in list(range(2,8))+list(range(10,15))}
 for reg,val in saved.items():cpu.w_reg(reg,val)
 cpu.w_pc(0x1000)
 for _ in range(100):
  cpu.execute(1000)
  if cpu.r_pc()==0x800:break
 else:raise AssertionError('timeout')
 assert cpu.r_sp()==sp+4 and all(cpu.r_reg(k)==v for k,v in saved.items())
 assert cpu.r_reg(0)==valid,(r,en,reasons)
 assert bytes(mem.r_block(0x10000,16))==bytes(r)
 assert bytes(mem.r_block(0x20010,24))==(struct.pack('>12H',*expected) if valid else b'X'*24)
 assert bytes(mem.r_block(0x20000,16))==b'G'*16 and bytes(mem.r_block(0x20028,16))==b'H'*16
 assert bytes(mem.r_block(0x1000,len(code)))==code
 calls+=1;rejections+=not valid
 return reasons,expected

results=[];domains=collections.defaultdict(set);phases=collections.Counter();timer_ranges=[[],[],[]]
for path in sorted(PROFILES.glob('*-private-events.json')):
 d=json.loads(path.read_text());events=d['events'];raw=[0]*16;safe=[0]*16;safe[14]=7;en=0;idx=0;seen=set();rows=[];transient=collections.Counter();rawrej=collections.Counter();saferej=collections.Counter();firstnoise=None;uninitialized_noise_transients=[]
 assert d['complete'] and len(d['RTIs'])==d['logical_NMIs'] and not d['entries_without_previous_RTI']
 assert all(rt['nmi']==i+1 for i,rt in enumerate(d['RTIs']))
 assert all(e['address']==0x4017 for e in d['reads']) # reads are controller2, not APU status
 for rt in d['RTIs']:
  same=collections.Counter();change=collections.defaultdict(list)
  while idx<rt['event_count']:
   e=events[idx];a=e['address'];val=e['value'];assert e['nmi']==rt['nmi'] and e['phase']=='entry_to_RTI';domains[a].add(val);phases[e['phase']]+=1;seen.add(a);same[a]+=1;change[a].append(val)
   if a==0x4015:en=val
   else:
    assert 0x4000<=a<0x4010
    raw[a-0x4000]=safe[a-0x4000]=val
   if a==0x400e and firstnoise is None:firstnoise={'nmi':e['nmi'],'ordinal':idx,'value':val}
   if firstnoise is None and en&8 and safe[12]&15:uninitialized_noise_transients.append({'nmi':e['nmi'],'ordinal':idx,'address':a,'value':val})
   why,_=call(safe,en)
   for x in why:transient[x]+=1
   idx+=1
  if firstnoise is None:assert not(en&8 and safe[12]&15),'noise audible at RTI before first actual period'
  wr,pr=call(raw,en);ws,ps=call(safe,en)
  for x in wr:rawrej[x]+=1
  for x in ws:saferej[x]+=1
  for i,b in enumerate((0,4,8)):
   if ps[4+i]:timer_ranges[i].append(raw[b+2]+256*(raw[b+3]&7))
  rows.append({'nmi':rt['nmi'],'raw_rejection':wr,'safe_rejection':ws,'safe_plan':ps,'uninitialized':[f'{0x4000+x:04x}' for x in range(16) if 0x4000+x not in seen],'multiwrite_addresses':[f'{a:04x}' for a,n in same.items() if n>1],'changed_multiwrite_addresses':[f'{a:04x}' for a,v in change.items() if len(set(v))>1]})
 assert idx==len(events)
 row={'history':d['history'],'frames':len(rows),'writes':len(events),'reads_controller2':len(d['reads']),'raw_rejection_reasons':dict(rawrej),'safe_rejection_reasons':dict(saferej),'per_write_safe_rejection_reasons':dict(transient),'first_actual_noise_period':firstnoise,'uninitialized_noise_per_write_transients':uninitialized_noise_transients,'frames_with_multiple_same_register_writes':sum(bool(r['multiwrite_addresses']) for r in rows),'frames_with_changed_same_register_writes':sum(bool(r['changed_multiwrite_addresses']) for r in rows)}
 (OUT/(d['history']+'-private-plans.json')).write_text(json.dumps({'summary':row,'frames':rows},indent=2)+'\n');results.append(row);print(json.dumps(row),flush=True)
summary={'status':'PASS','native_calls':calls,'atomic_rejections':rejections,'histories':results,'APU_writes':sum(r['writes'] for r in results),'real_RTI_snapshots':sum(r['frames'] for r in results),'phases':dict(phases),'write_domains':{f'{a:04x}':sorted(v) for a,v in sorted(domains.items())},'audible_timer_ranges':[[min(v),max(v)] for v in timer_ranges],'backend_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'compiled_code_sha256':hashlib.sha256(code).hexdigest(),'scope':'Logical RTI snapshots and transient states only; no audio capture, cycle timing, or target speed measurement.'}
assert len(results)==14 and calls==18991 and rejections==163
assert summary['APU_writes']==15059 and summary['real_RTI_snapshots']==1966
assert summary['audible_timer_ranges']==[[166,280],[78,595],[140,595]]
assert all(h['raw_rejection_reasons']=={'noise_mode':2} and not h['safe_rejection_reasons'] for h in results)
assert summary['phases']=={'entry_to_RTI':15059}
summary['checker_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(OUT/'planner-results.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='histories'}),flush=True)
