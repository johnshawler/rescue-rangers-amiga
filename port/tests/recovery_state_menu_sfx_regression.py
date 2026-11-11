#!/usr/bin/env python3
"""Run frozen public adapter specifications against the new composite binary."""
import argparse,importlib
import recovery_state_menu_sfx_harness as harness

def main():
 p=argparse.ArgumentParser();p.add_argument('suite',choices=('menu','music','long'));args=p.parse_args()
 module=importlib.import_module({'menu':'recovery_state_dispatch_menu_contract','music':'recovery_state_dispatch_menu_music_contract','long':'recovery_state_dispatch_menu_long_contract'}[args.suite])
 for name in ('Native','assemble','SIZES','RESOURCE','CODE','STOP','RAM','CTX','JOURNAL','RUNTIME','STACK'):
  if hasattr(module,name):setattr(module,name,getattr(harness,name))
 module.main()
if __name__=='__main__':main()
