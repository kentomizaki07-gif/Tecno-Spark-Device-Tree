#!/usr/bin/env python3
"""
extract_recovery_fragment.py - take the "recovery" ramdisk part out of a vendor_boot.img
(for example the one your GitHub build made) and save it as a file you can flash with:

    fastboot flash vendor_boot:recovery recovery.cpio.lz4

Usage:  python3 extract_recovery_fragment.py vendor_boot.img recovery.cpio.lz4
"""
import struct, sys

def al(x, p): return (x + p - 1) // p * p

img = open(sys.argv[1], 'rb').read()
if img[:8] != b'VNDRBOOT': sys.exit('ERROR: not a vendor_boot image')
hv, page, ka, ra, vrsz = struct.unpack('<5I', img[8:28])
if hv != 4: sys.exit('ERROR: header version %d, expected 4' % hv)
hsz, dtbsz = struct.unpack('<II', img[2096:2104])
tsz, tnum, tesz, bcsz = struct.unpack('<IIII', img[2112:2128])
rd = al(hsz, page); tab = rd + al(vrsz, page) + al(dtbsz, page)
frags = []
for i in range(tnum):
    e = img[tab + i * tesz: tab + (i + 1) * tesz]
    sz, off, typ = struct.unpack('<III', e[:12])
    name = e[12:44].split(b'\0')[0].decode(errors='replace')
    frags.append((name, typ, img[rd + off: rd + off + sz]))
print('fragments found:', [(n, t, len(d)) for n, t, d in frags])
rec = [f for f in frags if f[0] == 'recovery' or f[1] == 2]
if len(rec) != 1:
    sys.exit('ERROR: expected exactly one recovery fragment, found %d.\n'
             'The build may have put everything into one platform ramdisk. Send me the list above.' % len(rec))
data = rec[0][2]
kind = {b'\x02\x21\x4c\x18': 'lz4-legacy', b'\x1f\x8b': 'gzip', b'07070': 'raw cpio'}
k = next((v for m, v in kind.items() if data.startswith(m)), 'unknown')
open(sys.argv[2], 'wb').write(data)
print('wrote %s (%d bytes, %s)' % (sys.argv[2], len(data), k))
if k != 'lz4-legacy':
    print('NOTE: your stock ramdisks are lz4-legacy. Check BOARD_RAMDISK_USE_LZ4 in BoardConfig.mk.')
