#!/usr/bin/env python3
"""Independent bitwise full-adder proof of test-only Ricoh binary arithmetic."""
from recovery_test_startup_fade_continue import CPU
from recovery_test_gameplay_fade_entry import prove_binary_sbc

def main():
    cpu=CPU();cases=0
    for a in range(256):
        for b in range(256):
            for cin in (0,1):
                carry=cin;result=0;carry7=0
                for bit in range(8):
                    av=(a>>bit)&1;bv=(b>>bit)&1
                    if bit==7:carry7=carry
                    result|=(av^bv^carry)<<bit
                    carry=(av&bv)|(av&carry)|(bv&carry)
                flags=carry|(2 if result==0 else 0)|(result&128)|((carry7^carry)<<6)
                for d in (0,8):
                    cpu.a=a;cpu.p=0x34|d|cin;cpu.memory[0]=b
                    cpu.opADC(lambda:0)
                    assert (cpu.a,cpu.p)==(result,0x34|d|flags)
                    cases+=1
    print(f'PASS {cases} ADC and {prove_binary_sbc()} SBC binary truth-table cases, with D preserved and both carry inputs.')
if __name__=='__main__':main()
