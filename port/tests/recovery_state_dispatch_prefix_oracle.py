"""Test-only cartridge bus adapter. No native/model/schedule imports.
Hardware bus classes retained from the reviewed original-ROM test adapters.
"""
SHA = '051ea9bda7e1ae771f4c196e5bd4b35ec8db2b305dd3b1d26ad250f379d06411'

class OriginalBus(list):
    def __init__(self, rom):
        super().__init__([0]*65536)
        self[0xc000:] = rom[16+7*16384:16+8*16384]
        self.events = []
        self.status = 0
    def __getitem__(self, address):
        if address == 0x2002:
            self.events.append(('ppu', 0x2002, 0, 0))
            return self.status  # Value unused; read still resets the PPU address latch.
        return super().__getitem__(address)
    def __setitem__(self, address, value):
        if isinstance(address, int):
            if address in (0xfff0, 0x9fff, 0xbfff, 0xdfff):
                self.events.append(('mapper', address, value, self[0xf5]))
                return
            if address in (0x2000,0x2006,0x2007):
                self.events.append(('ppu', address, value, 1))
                return
            assert 0 <= address < 2048, ('unsupported write', hex(address))
            self.events.append(('ram', address, value))
        super().__setitem__(address, value)

class SerialMapper:
    """Independent MMC1 logical write model, not a 6502 instruction interpreter.
    Explicit initial obligation: empty latch, 16KiB switch-low/fixed-last mode.
    """
    def __init__(self):
        self.bits=[]; self.control=0x0c; self.chr0=0; self.chr1=0; self.prg=3
    def write(self,address,value):
        if value&128:
            self.bits.clear(); self.control|=12; return
        self.bits.append(value&1)
        if len(self.bits)==5:
            data=sum(bit<<i for i,bit in enumerate(self.bits))
            field=('control','chr0','chr1','prg')[(address>>13)&3]
            setattr(self,field,data); self.bits.clear()
    def snapshot(self):
        return self.control,self.chr0,self.chr1,self.prg,tuple(self.bits)
    @property
    def bank(self):
        assert (self.control>>2)&3==3, ('unsupported mapper mapping mode',self.snapshot())
        return self.prg&7

class AudioBus(OriginalBus):
    def __init__(self,rom):
        super().__init__(rom)
        self.rom=rom
        self.dma=[]
        self.mapper=SerialMapper()
        self.bits=self.mapper.bits
        self.bank=3
        self.map_bank(3)
    def map_bank(self,bank):
        assert 0<=bank<8
        self.bank=bank
        list.__setitem__(self,slice(0x8000,0xc000),self.rom[16+bank*16384:16+(bank+1)*16384])
    def __setitem__(self,address,value):
        if address in (0x4000,0x4004,0x4008,0x400c,0x4001,0x4005,0x4015):
            self.events.append(('apu',address,value,1));return
        if address in (0x2001,0x2003,0x2005,0x4014):
            self.events.append(('ppu',address,value,1))
            if address==0x4014:
                assert value==2
                self.dma.append(bytes(self[0x200:0x300]))
            return
        super().__setitem__(address,value)
        if address in (0xfff0,0x9fff,0xbfff,0xdfff):
            self.mapper.write(address,value)
            self.map_bank(self.mapper.bank)

class ControllerBus(AudioBus):
    inputs=(0,0)
    pos=[0,0]
    def __getitem__(self,address):
        if isinstance(address,int) and address in (0x4016,0x4017):
            port=address-0x4016; bit=self.pos[port]
            assert bit<8
            value=(self.inputs[port]>>(7-bit))&1
            self.pos[port]+=1
            self.events.append(('controller',address,value,0))
            return value
        return super().__getitem__(address)
    def __setitem__(self,address,value):
        if address==0x4016:
            self.events.append(('controller',address,value,1))
            self.pos=[0,0]
            return
        return super().__setitem__(address,value)


def select_boundary(ref, bus, event):
    """Choose test reference flow only from original state and external event.

    Return (result, helper ID, target PC). Selection happens BEFORE native
    execution; no native metadata, snapshots or helper statuses are inputs.
    Unsupported paths are outside this bounded reference comparison.
    """
    pc = ref.pc
    if event not in (0, 1):
        return (-1, None, None)
    if pc == 0xfe8d:
        if bus[0x18]:
            return (-1, None, None)
        if bus[0x80] == 1:
            return (1, 6, 0xc0bf) if event else (0, None, None)
        if bus[0x80] == 4:
            return (-1, None, None) if event else (1, 9, 0xc584)
        raise AssertionError('unknown original scheduler state')
    if event:
        return (-1, None, None)
    helper, target = {
        0xfe24: (1, 0xfe43), 0xfe43: (2, 0xfe67),
        0xfe67: (3, 0xfe7c), 0xfe7c: (4, 0xc574),
        0xc574: (5, 0xfe8d), 0xc0bf: (7, 0x8003),
        0x8003: (0, 0xc0f3), 0xc0f3: (8, 0xfe8d),
        0xc584: (10, 0xfe8d),
    }[pc]
    return (1, helper, target)
