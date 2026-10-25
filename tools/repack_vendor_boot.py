#!/usr/bin/env python3
"""
repack_vendor_boot.py  -  put a new recovery ramdisk into your STOCK vendor_boot image.

Why: your phone keeps its recovery inside vendor_boot. That image also holds the
stock "platform" ramdisk (touch, display and storage drivers) and the device tree.
We keep all of that untouched and replace ONLY the part named "recovery".

Usage:
    python3 repack_vendor_boot.py vendor_boot_a.img  my_recovery_ramdisk  -o vendor_boot_new.img

my_recovery_ramdisk can be a raw cpio, or a gzip / xz / lz4-legacy compressed cpio.
Tip: install the lz4 tool first (WSL/Ubuntu: sudo apt install lz4) so the result is small.
Nothing is flashed by this script. It only writes a new file.
"""
import argparse, gzip, lzma, os, struct, subprocess, sys, tempfile

def al(x, p): return (x + p - 1) // p * p

# ---------- LZ4 legacy (the format Android uses for ramdisks) ----------
def lz4_block_decode(src):
    out = bytearray(); i = 0; n = len(src)
    while i < n:
        t = src[i]; i += 1
        ll = t >> 4
        if ll == 15:
            while True:
                b = src[i]; i += 1; ll += b
                if b != 255: break
        out += src[i:i + ll]; i += ll
        if i >= n: break
        off = src[i] | (src[i + 1] << 8); i += 2
        ml = t & 15
        if ml == 15:
            while True:
                b = src[i]; i += 1; ml += b
                if b != 255: break
        ml += 4
        st = len(out) - off
        if off >= ml: out += out[st:st + ml]
        else:
            for k in range(ml): out.append(out[st + k])
    return bytes(out)

def lz4_legacy_decode(data):
    i = 4; out = bytearray()
    while i < len(data):
        sz = struct.unpack('<I', data[i:i + 4])[0]; i += 4
        if sz == 0x184C2102: continue
        out += lz4_block_decode(data[i:i + sz]); i += sz
    return bytes(out)

def lz4_literal_only(raw):
    """Valid but NOT compressed LZ4 legacy stream. Only used if the lz4 tool is missing."""
    out = bytearray(b'\x02\x21\x4c\x18')
    for s in range(0, len(raw), 8 << 20):
        chunk = raw[s:s + (8 << 20)]
        n = len(chunk)
        tok = bytearray([min(n, 15) << 4])
        if n >= 15:
            r = n - 15
            while r >= 255: tok.append(255); r -= 255
            tok.append(r)
        blk = bytes(tok) + chunk
        out += struct.pack('<I', len(blk)) + blk
    return bytes(out)

def lz4_legacy_encode(raw):
    try:
        with tempfile.TemporaryDirectory() as d:
            a, b = os.path.join(d, 'in'), os.path.join(d, 'out')
            open(a, 'wb').write(raw)
            subprocess.run(['lz4', '-l', '-9', '-f', '-q', a, b], check=True)
            return open(b, 'rb').read()
    except (FileNotFoundError, subprocess.CalledProcessError):
        print('WARNING: "lz4" tool not found. Writing an uncompressed LZ4 stream (bigger).')
        print('         Install it for a smaller result: sudo apt install lz4')
        return lz4_literal_only(raw)

def to_raw_cpio(data):
    m = data[:6]
    if data[:2] == b'\x1f\x8b': return gzip.decompress(data)
    if data[:4] == b'\xfd7zX': return lzma.decompress(data)
    if data[:4] == b'\x02\x21\x4c\x18': return lz4_legacy_decode(data)
    if m == b'070701': return data
    sys.exit('ERROR: ramdisk is not a raw cpio, gzip, xz or lz4-legacy file (first bytes: %s).\n'
             'Give me a raw cpio or a gzip file.' % data[:4].hex())

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('stock'); ap.add_argument('ramdisk')
    ap.add_argument('-o', '--out', default='vendor_boot_new.img')
    ap.add_argument('--fragment', default='recovery', help='name of the fragment to replace')
    a = ap.parse_args()

    img = open(a.stock, 'rb').read()
    if img[:8] != b'VNDRBOOT': sys.exit('ERROR: not a vendor_boot image')
    hv, page, kaddr, raddr, vrsz = struct.unpack('<5I', img[8:28])
    if hv != 4: sys.exit('ERROR: only header version 4 is supported (yours is %d)' % hv)
    hsz, dtbsz = struct.unpack('<II', img[2096:2104])
    tsz, tnum, tesz, bcsz = struct.unpack('<IIII', img[2112:2128])

    rd_off  = al(hsz, page)
    dtb_off = rd_off + al(vrsz, page)
    tab_off = dtb_off + al(dtbsz, page)
    bc_off  = tab_off + al(tsz, page)
    end     = bc_off + al(bcsz, page)

    entries = []
    for i in range(tnum):
        e = bytearray(img[tab_off + i * tesz: tab_off + (i + 1) * tesz])
        sz, off, typ = struct.unpack('<III', e[:12])
        name = bytes(e[12:44]).split(b'\0')[0].decode(errors='replace')
        entries.append([e, name, typ, img[rd_off + off: rd_off + off + sz]])
    target = [x for x in entries if x[1] == a.fragment]
    if len(target) != 1: sys.exit('ERROR: fragment "%s" not found. Found: %s' % (a.fragment, [x[1] for x in entries]))

    new_cpio = to_raw_cpio(open(a.ramdisk, 'rb').read())
    target[0][3] = lz4_legacy_encode(new_cpio)
    print('new %s fragment: %d bytes (raw cpio %d bytes)' % (a.fragment, len(target[0][3]), len(new_cpio)))

    # rebuild ramdisk blob and table
    blob = b''; table = b''
    for e, name, typ, data in entries:
        struct.pack_into('<II', e, 0, len(data), len(blob))
        blob += data; table += bytes(e)

    hdr = bytearray(img[:hsz]); struct.pack_into('<I', hdr, 24, len(blob))
    pad = lambda b: b + b'\0' * (al(len(b), page) - len(b))
    body = pad(bytes(hdr)) + pad(blob) + pad(img[dtb_off:dtb_off + dtbsz]) + pad(table) + pad(img[bc_off:bc_off + bcsz])

    # AVB footer (last 64 bytes): move the small vbmeta blob behind the new content
    total = len(img)
    if img[-64:-60] == b'AVBf':
        f = bytearray(img[-64:])
        maj, mnr, orig, vb_off, vb_sz = struct.unpack('>IIQQQ', f[4:36])
        vb = img[vb_off:vb_off + vb_sz]
        struct.pack_into('>QQ', f, 12, len(body), len(body))
        out = body + vb
        if len(out) > total - 64: sys.exit('ERROR: too big for the partition (%d > %d). Use the lz4 tool or a smaller ramdisk.' % (len(out), total - 64))
        out += b'\0' * (total - 64 - len(out)) + bytes(f)
    else:
        if len(body) > total: sys.exit('ERROR: too big for the partition')
        out = body + b'\0' * (total - len(body))

    open(a.out, 'wb').write(out)
    print('wrote %s (%d bytes, same size as stock: %s)' % (a.out, len(out), len(out) == total))
    print('Stock platform ramdisk, dtb and header were kept unchanged.')

main()
