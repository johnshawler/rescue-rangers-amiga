"""Private original-ROM reference selector, isolated from native code/metadata."""
from recovery_state_dispatch_prefix_oracle import ControllerBus, SHA, select_boundary as prefix_boundary

def select_boundary(ref,bus,event):
    if event not in (0,1): return -1,None,None
    if ref.pc==0xfe8d and bus[0x18]:
        assert bus[0x80]==1
        return (1,11,0xc0bf) if event else (0,None,None)
    if ref.pc==0x8003 and ref.a==7:
        return (-1,None,None) if event else (1,12,0xc0f3)
    if ref.pc==0xc0f3 and bus[0xc9]: return -1,None,None
    return prefix_boundary(ref,bus,event)
