#!/usr/bin/env python3
"""ROM-free verifier regressions. Synthetic images/PCM are not capture evidence."""
from pathlib import Path
import ast,tempfile,struct
import numpy as np
from PIL import Image
from recovery_stage_target_scanout_check import expected_copper,expected_screen,verify_scanout
P=Path(__file__).parent

def main():
 palette=bytes(range(32));frame=bytes([0x55])*51200;cop,ptr=32,4096
 chip=bytearray(1024);chip[cop:cop+220]=expected_copper(ptr,palette)
 with tempfile.TemporaryDirectory() as tmp:
  path=Path(tmp)/'screen.png';im=Image.new('RGB',(720,287));im.paste(expected_screen(frame,palette),(40,18));im.save(path)
  verify_scanout(chip,path,cop,ptr,palette,frame)
  for offset in list(range(0,48,2))+list(range(48,88,2))+list(range(88,216,2))+[216,218]:
   bad=chip.copy();bad[cop+offset]^=1
   try:verify_scanout(bad,path,cop,ptr,palette,frame)
   except AssertionError:pass
   else:raise AssertionError(('Copper corruption admitted',offset))
  # Former self-reference hole: corrupt both all target colors and screenshot.
  bad=chip.copy()
  for i in range(32):struct.pack_into('>H',bad,cop+90+i*4,0xf0f)
  im.paste(Image.new('RGB',(640,256),(255,0,255)),(40,18));im.save(path)
  try:verify_scanout(bad,path,cop,ptr,palette,frame)
  except AssertionError:pass
  else:raise AssertionError('paired Copper/screen magenta admitted')
 # Execute the production spectral functions without importing private oracles.
 ns={'np':np}
 for filename,name in [('recovery_menu_paula_verify.py','spectral'),('recovery_stage_target_verify.py','check_retained_spectral')]:
  tree=ast.parse((P/filename).read_text());node=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name)
  exec(compile(ast.Module(body=[node],type_ignores=[]),filename,'exec'),ns)
 tree=ast.parse((P/'recovery_stage_target_verify.py').read_text())
 imports=[n for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.module=='recovery_stage_target_pixels']
 assert len(imports)==1 and imports[0].names[0].asname=='expected_pixels','pixel import shadows audio list'
 step=177345;rows=[(i*step,i*step,i*step+1) for i in range(20)]
 plans=[]
 for i in range(20):
  v=[0,0,0,26] if 2<=i<7 else [20,20,0,0] if 17<=i<19 else [0,0,0,0]
  plans.append([713,1693,160,160]+v+[0,0,4,5])
 pcm=np.zeros((240000,2));at=lambda i:round(rows[i][1]*44100/709379)
 rng=np.random.default_rng(188);pcm[at(2):at(7),0]=rng.normal(0,1000,at(7)-at(2))
 for c in range(2):
  n=at(19)-at(17);pcm[at(17):at(19),c]=2000*np.sin(np.arange(n)*2*np.pi*(3546895/(plans[17][c]*8))/44100)
 expected=[(8,15,b'',p) for p in plans]
 result=ns['check_retained_spectral'](pcm,rows,expected,at(2))
 assert result['negative_PCM_checks']==['DC','swapped','wrong_tone']
 assert ns['check_retained_spectral'](pcm,rows,expected*13,at(2)) is None
 print('PASS independent Copper fields/DMA/terminator, paired magenta negative, synthetic <=256 spectral positive/three negatives and >256 branch. No new capture coverage.')
if __name__=='__main__':main()
