"""Independent declared RGB4 scanout contract; no target palette as an oracle."""
import struct
from PIL import Image,ImageChops
RGB12=(0x666,0x028,0x21a,0x40a,0x607,0x700,0x600,0x540,0x330,0x040,0x050,0x040,0x044,0,0,0,
0xaaa,0x16c,0x44f,0x83f,0xb2c,0xd25,0xc40,0xa60,0x880,0x590,0x2a0,0x0a3,0x099,0,0,0,
0xfff,0x6bf,0x99f,0xc8f,0xf7f,0xf7b,0xf96,0xdb2,0xbc0,0x8d1,0x5e5,0x4e9,0x4dd,0x444,0,0,
0xfff,0xbef,0xddf,0xedf,0xfdf,0xfde,0xfdc,0xeea,0xdea,0xcea,0xbeb,0xbed,0xbee,0xbbb,0,0)
HEADER=bytes.fromhex('01005200010200000104000001060000010c001101fc0000008e2c8100902cc100920038009400d001080000010a0000')
def expected_copper(frame_address,palette):
 assert len(palette)==32 and all(x<64 for x in palette)
 data=bytearray(HEADER)
 for p in range(5):
  address=frame_address+p*10240
  data+=struct.pack('>4H',0xe0+4*p,address>>16,0xe2+4*p,address&65535)
 for i in range(32):data+=struct.pack('>HH',0x180+2*i,RGB12[palette[i if i%4 else 0]])
 return bytes(data)+bytes.fromhex('fffffffe')
def expected_screen(frame,palette):
 assert len(frame)==51200
 colors=[RGB12[palette[i if i%4 else 0]] for i in range(32)]
 rgb=[((c>>8)*17,((c>>4)&15)*17,(c&15)*17) for c in colors]
 image=Image.new('RGB',(320,256))
 image.putdata([rgb[sum(((frame[p*10240+y*40+x//8]>>(7-x%8))&1)<<p for p in range(5))] for y in range(256) for x in range(320)])
 return image.resize((640,256),Image.Resampling.NEAREST)
def verify_scanout(chip,path,copper_address,frame_address,palette,frame):
 want=expected_copper(frame_address,palette)
 assert chip[copper_address:copper_address+220]==want,'independent Copper setup/pointers/palette/terminator'
 actual=Image.open(path).convert('RGB');assert actual.size==(720,287)
 assert ImageChops.difference(expected_screen(frame,palette),actual.crop((40,18,680,274))).getbbox() is None,'independent original-derived RGB pixels'
 return dict(status='PASS',Copper_bytes_equal=220,Copper_palette_entries_equal=32,DMA_pointers_equal=5,actual_video_dimensions=[720,287],verified_viewport=[40,18,680,274],RGB_pixels_equal=163840,RGB_source='original-verified palette/frame and fixed declared RGB12 table')
