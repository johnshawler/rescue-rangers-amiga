#!/usr/bin/env python3
"""ROM-free exhaustive invalid-PC and bounded indexed parser rejection tests."""
from recovery_test_music_indexed_contract import make_checker,contract,COMMANDS,DISPATCH

def main():
    check,cleanup=make_checker();count=0
    resource=bytearray(16384)
    for address,target in DISPATCH:
        if address:resource[address-0x8000:address-0x8000+2]=bytes((target&255,target>>8))
    resource=bytes(resource)
    def reject(state,context,r,index):
        nonlocal count
        expected,_=contract(state,context,r,index)
        assert expected is None
        assert check(state,context,r,index)==(state,context,[])
        count+=1
    for index in (0,3,8):
        state=bytearray(2048);state[0x757]=0x80;state=bytes(state)
        context=bytearray((0x83,0x9d if index==8 else 0xa0,8 if index==0 else 0x80,0x2b,0,0x24,0xab,0))
        entry=int.from_bytes(context[:2],'big')
        for pc in range(65536):
            if pc==entry:continue
            context[:2]=pc.to_bytes(2,'big');reject(state,bytes(context),resource,index)
    for index in range(9):
        for x in range(0x28,0x2c):
            state=bytearray(2048);state[0x72c+x]=0x80
            context=bytearray((0x83,0x9d if index==8 else 0xa0,COMMANDS[index] if index not in (3,8) else 0x80,x,0,0x24,0xab,0))
            for invalid in range(256):
                if (index==0 and invalid not in (4,5,6,7,8,9,24)) or (index==3 and invalid not in range(32,256,32)):
                    c=context.copy();c[2]=invalid;reject(bytes(state),bytes(c),resource,index)
                if not 0x28<=invalid<=0x2b:
                    c=context.copy();c[3]=invalid;reject(bytes(state),bytes(c),resource,index)
                if invalid&(0x38 if index in (0,3) else 0x30)!=0x20:
                    c=context.copy();c[5]=invalid;reject(bytes(state),bytes(c),resource,index)
                if index!=3 and not 0x80<=invalid<=0xbf:
                    s=state.copy();s[0x72c+x]=invalid;reject(bytes(s),bytes(context),resource,index)
                if index not in (3,8):
                    for offset in (0,1):
                        r=bytearray(resource);address=DISPATCH[index][0]-0x8000+offset
                        if invalid==r[address]:continue
                        r[address]=invalid;reject(bytes(state),bytes(context),bytes(r),index)
            if index==5:
                s=state.copy();s[0x728+x]=255;s[0x72c+x]=0xbf;reject(bytes(s),bytes(context),resource,index)
    cleanup();print(f'PASS {count} inert rejection comparisons: every wrong PC, every invalid X/P and pointer high byte, every malformed dispatch byte, all channel indexes, and command05 end-of-window bound.')
if __name__=='__main__':main()
