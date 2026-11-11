"""Run the default SFX stream_control proof from a source-only temporary tree."""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path
PORT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    for folder, name in (("src", "recovery_sfx_stream_control.s"),
                         ("tests", "recovery_test_sfx_stream_control.py"),
                         ("tests", "recovery_sfx_stream_control_model.py"),
                         ("tests", "recovery_test_sfx_stream_control_audit.py")):
        target = root / "port" / folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PORT / folder / name, target)
    guard = root / "guard"
    guard.mkdir()
    (guard / "sitecustomize.py").write_text('''import sys
class DenyPrivate:
 def find_spec(self, fullname, path=None, target=None):
  if fullname.startswith(('recovery_', 'verify_recovery_')) and fullname not in ('recovery_sfx_stream_control_model','recovery_test_sfx_stream_control'):
   raise ImportError('Private reference imports denied: '+fullname)
sys.meta_path.insert(0,DenyPrivate())
def audit(event,args):
 if event=='open' and isinstance(args[0],(str,bytes)):
  path=str(args[0]).lower()
  if '.nes' in path or '/input/' in path or 'private' in path:
   raise PermissionError('Private inputs denied')
sys.addaudithook(audit)
''')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env["PYTHONPATH"] = str(guard) + os.pathsep + env.get("PYTHONPATH", "")
    tests = ['recovery_test_sfx_stream_control.py', 'recovery_test_sfx_stream_control_audit.py']
    for name in tests:
        subprocess.run([sys.executable, str(root / 'port/tests' / name)], cwd=root, env=env, check=True)

print("PASS source-only isolation with ROM and private reference imports denied")
