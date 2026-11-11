#!/usr/bin/env python3
"""Additive CIA segmentation of the frozen native menu diagnostic. Private output."""
from pathlib import Path
import argparse,hashlib,json,re
P=Path(__file__).resolve().parents[1]
NAMES=('dispatch','capture','device','chr','background','sprites','empty')
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
def surround(s,call,i):return once(s,call,f' bsr.l recovery_profile_start_{i}\n'+call+f'\n bsr.l recovery_profile_end_{i}')
def instrumentation():
 s='\n cnop 0,4\n'
 for i in range(len(NAMES)):
  for kind in ('start','end'):
   s+=f'recovery_profile_{kind}_{i}:\n move.w ccr,-(sp)\n movem.l d0-d4/a0,-(sp)\n bsr.l llb_amiga_clock_read\n lea recovery_profile_data+{8+16*i}(pc),a0\n'
   if kind=='start':s+=' move.l d0,(a0)\n'
   else:s+=' sub.l (a0),d0\n add.l d0,4(a0)\n addq.l #1,8(a0)\n cmp.l 12(a0),d0\n bls.s .done\n move.l d0,12(a0)\n.done:\n'
   s+=' movem.l (sp)+,d0-d4/a0\n move.w (sp)+,ccr\n rts\n'
 s+=' cnop 0,4\nrecovery_profile_data:\n dc.b "CDRPRO01"\n dcb.l 28,0\n'
 return s

def prepare(s,out):
 # Instrument call sites, leaving the entire native dispatcher byte-identical.
 s=surround(s,' bsr.l recovery_state_menu_sfx',0)
 s=surround(s,' bsr.w capture_journal',1)
 s=surround(s,' bsr.l startup_consume',2)
 # Empty probe exercises the same timestamp/save/aggregate route on every completed call.
 s=once(s,' bsr.l paula_consume',' bsr.l paula_consume\n bsr.l recovery_profile_start_6\n bsr.l recovery_profile_end_6')
 # Widen runner branches whose diagnostic expansion can exceed signed byte range.
 pos=s.index(' include ');s=s[:pos].replace('beq.s','beq.w').replace('bne.s','bne.w').replace('bra.s','bra.w')+s[pos:]
 d=(P/'src/recovery_state_menu_display_device.s').read_text()
 d=once(d,' ; Select both immutable CHR banks',' bsr.l recovery_profile_start_3\n ; Select both immutable CHR banks')
 d=once(d,' lea startup_nt(pc),a0\n lea startup_chr+4096',' bsr.l recovery_profile_end_3\n lea startup_nt(pc),a0\n lea startup_chr+4096')
 d=surround(d,' bsr nes_draw_background',4);d=surround(d,' bsr nes_draw_sprites_8x8',5)
 (out/'recovery_profile_device.s').write_text(d)
 s=once(s,' include "recovery_state_menu_display_device.s"',f' include "{out}/recovery_profile_device.s"')
 return s+instrumentation()

def adapter(out):
 s=(P/'src/recovery_menu_paula_adapter.c').read_text()
 s=once(s,'int recovery_menu_paula_consume(','''volatile struct {char magic[8];U32 total[4],count[4],maximum[4];} recovery_profile_audio={"CDRPROA1",{0},{0},{0}};
static void profile_add(unsigned i,U32 t){U32 d=ticks()-t;recovery_profile_audio.total[i]+=d;recovery_profile_audio.count[i]++;if(d>recovery_profile_audio.maximum[i])recovery_profile_audio.maximum[i]=d;}
int recovery_menu_paula_consume(''')
 s=once(s,'U32 now,work;','U32 now,work; U32 prof=ticks();')
 s=once(s,' if(helper!=8&&helper!=20&&helper!=42)return 1;',' profile_add(0,prof);\n if(helper!=8&&helper!=20&&helper!=42)return 1;')
 s=once(s,' if(!experimental_direct_paula_plan',' prof=ticks();\n if(!experimental_direct_paula_plan')
 s=once(s,' /* Minimum 20ms',' profile_add(1,prof);\n /* Minimum 20ms')
 s=once(s,' now=ticks();if(now-mp.last',' prof=ticks(); now=ticks();if(now-mp.last')
 s=once(s,' r->published=now;apply(&r->plan);r->end=ticks();',' profile_add(2,prof);\n r->published=now;prof=ticks();apply(&r->plan);r->end=ticks();profile_add(3,prof);')
 (out/'recovery_profile_adapter.c').write_text(s)

def build(out,history,display,enabled):
 path=P/'tools/recovery_menu_paula_build.py';src=path.read_text()
 assert hashlib.sha256(path.read_bytes()).hexdigest()=='fd58f026a867cb3ae467a1115e9341bdfc6c011fed290a928a44e047f025f521'
 if enabled:
  src=once(src,"out.mkdir(parents=True,exist_ok=False)","out.mkdir(parents=True,exist_ok=False)\n adapter(out)")
  src=once(src,"str(P/'src'/n)","str(out/'recovery_profile_adapter.c') if n=='recovery_menu_paula_adapter.c' else str(P/'src'/n)")
  # Preserve header lookup from generated C location.
  src=once(src,"[cc,'-I'+str(out)","[cc,'-I'+str(out),'-I'+str(P/'src')")
  src=once(src,"(out/'recovery_menu_paula_target.s').write_text(s)","s=prepare(s,out)\n (out/'recovery_menu_paula_target.s').write_text(s)")
  src=once(src,"assert len(device)==1750 and hashlib.sha256(device).hexdigest()=='85b142d8ac84d53f4f5bb6f5143b28d1a07183989b71f2aeeeacaa0a3f920bad'","assert len(device)>1750 # Call-site instrumentation; native dispatcher remains frozen above.")
 ns={'__file__':str(path),'__name__':'recovery_profile_frozen_build','adapter':adapter,'prepare':prepare}
 exec(compile(src,str(path),'exec'),ns);ns['build'](out,history,display)
 meta=json.loads((out/'build.json').read_text());meta['profiling']=bool(enabled);meta['segments']=NAMES if enabled else [];(out/'build.json').write_text(json.dumps(meta,indent=2)+'\n')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);a.add_argument('--history',choices=('default','right_hold','move_back'),default='default');a.add_argument('--display',type=int,choices=(0,1),default=1);a.add_argument('--enabled',type=int,choices=(0,1),default=1);v=a.parse_args();build(v.output.resolve(),v.history,v.display,v.enabled)
