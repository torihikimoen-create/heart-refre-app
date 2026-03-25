"""
ハートリフレ アイコン生成
水色グラジエント。Python標準ライブラリのみ。
"""
import struct, zlib, math, os

def make_png(path, size):
    w = h = size

    def lerp(a, b, t): return int(a + (b - a) * t)

    def pixel(x, y):
        cx, cy = w / 2, h / 2
        # Radial gradient: center=light-water, edge=deep-water
        dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        t = min(dist / (cx * 1.05), 1.0)
        t = t ** 0.8  # ease in

        # Water gradient: #c8dde8 → #5a8aa0
        r = lerp(200, 90, t)
        g = lerp(221, 138, t)
        b = lerp(232, 160, t)

        # Soft highlight (upper-left)
        hx, hy = cx - cx * 0.25, cy - cy * 0.3
        hd = math.sqrt((x - hx) ** 2 * 3.5 + (y - hy) ** 2)
        hr = w * 0.22
        if hd < hr:
            ht = (1 - hd / hr) ** 2 * 0.45
            r = lerp(r, 255, ht)
            g = lerp(g, 255, ht)
            b = lerp(b, 255, ht)

        # Pink shimmer (lower-right)
        px2, py2 = cx + cx * 0.3, cy + cy * 0.35
        pd = math.sqrt((x - px2) ** 2 + (y - py2) ** 2)
        pr = w * 0.25
        if pd < pr:
            pt = (1 - pd / pr) ** 2.5 * 0.18
            r = lerp(r, 232, pt)
            g = lerp(g, 164, pt)
            b = lerp(b, 176, pt)

        return bytes([r, g, b])

    rows = []
    for y in range(h):
        row = bytearray([0])
        for x in range(w):
            row.extend(pixel(x, y))
        rows.append(bytes(row))

    raw = b''.join(rows)
    compressed = zlib.compress(raw, 9)

    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', crc)

    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
    idat = chunk(b'IDAT', compressed)
    iend = chunk(b'IEND', b'')

    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + ihdr + idat + iend)

    print(f'Created {path} ({size}x{size})')

os.makedirs('icons', exist_ok=True)
make_png('icons/icon-192.png', 192)
make_png('icons/icon-512.png', 512)
print('Done.')
