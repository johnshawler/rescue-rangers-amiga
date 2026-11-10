#!/usr/bin/env python3
"""Synthetic-only safety tests for private-input restoration."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,tempfile,unittest,zipfile
PATH=Path(__file__).resolve().parents[2]/'tools/restore_private_inputs.py'
spec=importlib.util.spec_from_file_location('restore_private_inputs',PATH);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
class RestoreTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.base=Path(self.temp.name);self.root=self.base/'repo';(self.root/'tools').mkdir(parents=True);r.ROOT=self.root
  self.data=b'private fixture';self.manifest=[{'path':'port/assets/title-snapshot.bin','bytes':len(self.data),'sha256':hashlib.sha256(self.data).hexdigest()}]
  self.save_manifest();self.bundle=self.base/'fixture.zip'
  with zipfile.ZipFile(self.bundle,'w') as z:z.writestr('title-source/port/assets/title-snapshot.bin',self.data)
  self.args=argparse.Namespace(bundle=self.bundle,rom=None,kickstart=None,check_only=False)
 def save_manifest(self):(self.root/'tools/private-fixture-manifest.json').write_text(json.dumps(self.manifest))
 def test_valid_and_idempotent(self):
  self.assertEqual(r.prepare(self.args),['port/assets/title-snapshot.bin']);self.assertEqual(r.prepare(self.args),['port/assets/title-snapshot.bin']);self.assertEqual((self.root/'port/assets/title-snapshot.bin').read_bytes(),self.data)
 def test_check_only(self):
  self.args.check_only=True;r.prepare(self.args);self.assertFalse((self.root/'port').exists())
 def test_wrong_fixture(self):
  self.manifest[0]['sha256']='0'*64;self.save_manifest()
  with self.assertRaises(ValueError):r.prepare(self.args)
  self.assertFalse((self.root/'port').exists())
 def test_existing_mismatch(self):
  target=self.root/'port/assets/title-snapshot.bin';target.parent.mkdir(parents=True);target.write_bytes(b'untouched')
  with self.assertRaises(ValueError):r.prepare(self.args)
  self.assertEqual(target.read_bytes(),b'untouched')
 def test_symlink_refused(self):
  target=self.base/'outside';target.mkdir();(self.root/'port').symlink_to(target,target_is_directory=True)
  with self.assertRaises(ValueError):r.prepare(self.args)
  self.assertEqual(list(target.iterdir()),[])
 def test_manifest_path_escape(self):
  self.manifest[0]['path']='../escape';self.save_manifest()
  with self.assertRaises(AssertionError):r.prepare(self.args)
  self.assertFalse((self.base/'escape').exists())
 def test_bad_rom_prevents_fixture_write(self):
  bad=self.base/'bad.nes';bad.write_bytes(b'not original');self.args.rom=bad
  with self.assertRaises(ValueError):r.prepare(self.args)
  self.assertFalse((self.root/'port').exists())
 def test_missing_bundle_member(self):
  with zipfile.ZipFile(self.bundle,'w') as z:z.writestr('other',b'irrelevant')
  with self.assertRaises(KeyError):r.prepare(self.args)
  self.assertFalse((self.root/'port').exists())
if __name__=='__main__':unittest.main()
