"""Six invented non-deferred stage-entry states, no captured game state."""
CASES=((0,2,9,0,255,0,0),(0,12,4,255,8,15,14),(1,2,3,1,72,128,1),
       (1,12,3,5,36,143,127),(1,2,12,6,8,144,254),(1,12,12,7,129,255,255))
def fixture(case):
    mode,s0,s1,sp,p,palette0,index=case
    state=bytearray((i*37+19)&255 for i in range(2048))
    state[0x50]=mode;state[0x54:0x56]=bytes((s0,s1));state[0xf6]=0;state[0x31]=index
    state[0x320:0x340]=bytes((i*17+palette0)&255 for i in range(32))
    return state,bytes((0xc6,0xb5,0x17,0x35,0x79,p,sp,0xa7))
