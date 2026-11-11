#!/usr/bin/env python3
"""Private frame-state diagnostic builder. Requires separately verified profile.
Never embeds cartridge bytes or generated trace data in source-controlled files.
"""
import argparse,hashlib,json,os,struct,subprocess
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def noise(period,short,n=2048):
    # Exact box integration at nominal integer clocks, THEN 8-bit rounding.
    # LFSR starts at1 independently per loop; looping is deliberately approximate.
    step=period*3546895; width=160*1662607; remaining=step;state=1;result=[]
    for _ in range(n):
        todo=width;area=0
        while todo:
            d=min(todo,remaining);area+=(-64 if state&1 else 64)*d
            todo-=d;remaining-=d
            if not remaining:
                state=(state>>1)|(((state^(state>>(6 if short else 1)))&1)<<14);remaining=step
        result.append(round(area/width))
    return result

def prepare(profile,b):
    p=json.loads(profile.read_text());ev=p['events'];assert len(ev)==p['APU_writes']==7136
    regs=p['registers'];assert regs['400E']['values']==[7,13,129]
    assert regs['4001']['values']==regs['4005']['values']==[8]
    assert regs['4008']['values']==[0,255] and regs['4015']['values']==[15]
    assert not any(0x4010<=e['address']<=0x4013 for e in ev)
    assert all(e['value']&48==48 for e in ev if e['address'] in (0x4000,0x4004,0x400c))
    bootstrap=[e for e in ev if e['nmi'] is None];known=[e for e in ev if e['nmi'] is not None]
    assert ev[:len(bootstrap)]==bootstrap and all(a['nmi']<=z['nmi'] for a,z in zip(known,known[1:]))
    r=[0]*16;r[14]=7;frames=[];ix=0
    def put(e):
        if e['address']!=0x4015:r[e['address']-0x4000]=e['value']
    for e in bootstrap:put(e)
    for n in range(known[-1]['nmi']+1):
        while ix<len(known) and known[ix]['nmi']==n:put(known[ix]);ix+=1
        frames.append(r.copy())
    ranges=[]
    for base in (0,4,8):
        vals=[f[base+2]+((f[base+3]&7)<<8) for f in frames if (f[base]&15 if base<8 else f[8])]
        ranges.append([min(vals),max(vals)])
    assert ranges==[[166,280],[333,595],[140,595]],ranges
    text='#define DP_FRAMES %d\n'%len(frames)
    text+='static const unsigned char dp_frames[DP_FRAMES][16]={\n'+',\n'.join('{'+','.join(map(str,f))+'}' for f in frames)+'};\n'
    text+='static const signed char dp_noise[3][2048] __attribute__((aligned(2)))={\n'+',\n'.join('{'+','.join(map(str,noise(p,s)))+'}' for p,s in [(148,0),(944,0),(8,1)])+'};\n'
    (b/'experimental_direct_paula_private.h').write_text(text)
    report={'profile_sha256':hashlib.sha256(profile.read_bytes()).hexdigest(),'writes':len(ev),'bootstrap_unknown_time_writes':len(bootstrap),'logical_frames':len(frames),'audible_frame_final_timer_ranges':ranges,'scheduling':'Bootstrap applied before replay; one final register snapshot per logical NMI at one PAL Amiga VBL. Intra-frame transients collapsed, not cycle timestamps.','noise_periods_cpu_cycles':[148,944,8],'noise_sample_bytes':6144,'frame_state_bytes':len(frames)*16}
    (b/'profile-verification.json').write_text(json.dumps(report,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('profile',type=Path);a=ap.parse_args();b=P/'build/experimental-direct-paula';b.mkdir(parents=True,exist_ok=True);prepare(a.profile,b)
    cc=os.environ.get('PAULA_CC','m68k-linux-gnu-gcc');elf=b/'probe.elf';ld=b/'probe.ld'
    ld.write_text('SECTIONS { . = 0; .text : { *(.entry) *(.text*) *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) *(COMMON) } /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) } }')
    subprocess.run([cc,'-I'+str(b),'-m68020','-mpcrel','-O2','-ffreestanding','-fno-builtin','-nostdlib','-fno-pie','-Wl,--build-id=none','-Wl,-T,'+str(ld),*[str(P/'src'/('experimental_direct_paula'+s)) for s in ['_entry.s','_probe.c','.c']],'-o',str(elf)],check=True)
    subprocess.run([cc.replace('gcc','objcopy'),'-O','binary',str(elf),str(b/'probe.bin')],check=True)
    symbols=subprocess.check_output([cc.replace('gcc','nm'),'-n',str(elf)],text=True);(b/'symbols.txt').write_text(symbols)
    size=32768;assert all(int(x.split()[0],16)<size for x in symbols.splitlines() if len(x.split())==3)
    payload=(b/'probe.bin').read_bytes();assert len(payload)<size
    subprocess.run([os.environ['VASM'],'-m68020','-Fbin','-quiet','-DPAYLOAD_BYTES='+str(size),'-o',str(b/'boot.bin'),str(P/'src/boot.s')],check=True)
    disk=bytearray(901120);boot=(b/'boot.bin').read_bytes();disk[:len(boot)]=boot;disk[1024:1024+len(payload)]=payload;checksum=0
    for i in range(0,1024,4):checksum+=struct.unpack_from('>I',disk,i)[0];checksum=(checksum&0xffffffff)+(checksum>>32)
    struct.pack_into('>I',disk,4,(~checksum)&0xffffffff);(b/'private-replay.adf').write_bytes(disk)
    (b/'build.json').write_text(json.dumps({'payload_file_bytes':len(payload),'allocated_chip_bytes':size,'adf_sha256':hashlib.sha256(disk).hexdigest(),'classification':'PRIVATE game-profile-derived approximate replay diagnostic, NOT integrated game audio'},indent=2)+'\n')
if __name__=='__main__':main()
