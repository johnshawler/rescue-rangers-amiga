#!/usr/bin/env python3
"""Rebuild determinism and proof that reference state bytes are not target inputs."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
PORT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PORT/'tools'))
from build_recovery_startup_display import OUT,source,oracle,SHA

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rom=(PORT.parent/'input/rescue-rangers-europe.nes').read_bytes();assert hashlib.sha256(rom).hexdigest()==SHA
 results,_,_=oracle(rom)
 poisoned=[(i,status,bytes([0x69])*len(ctx),bytes([0x96])*len(ram),bytes([0x5c])*len(journal),bytes([0xc5])*len(raw)) for i,status,ctx,ram,journal,raw in results]
 assert source(results,0)==source(poisoned,0),'Reference state leaked into target'
 files=['startup-display.s','startup-display.bin','startup-display-boot.s','startup-display-boot.bin','startup-display.adf','startup-display-private-chr.bin','recovery-resident-chr-fade-private-bank2.bin','recovery-resident-chr-fade-private-bank3.bin','build.json']
 before={f:sha(OUT/f) for f in files}
 for _ in range(2):
  subprocess.run([sys.executable,str(PORT/'tools/build_recovery_startup_display.py')],check=True,stdout=subprocess.DEVNULL)
  assert {f:sha(OUT/f) for f in files}==before,'Non-deterministic build'
 report={'status':'PASS','rebuilds_equal':2,'reference_RAM_context_journal_raw_bytes_poisoned_without_changing_target':True,'artifacts':before}
 (OUT/'build-test.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS deterministic rebuilds; poisoned reference state has no effect on target source')
if __name__=='__main__':main()
