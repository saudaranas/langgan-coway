"""
Bina peta "Jeti Melaka" untuk Hikayat Pahlawan Rezeki (versi cubaan).
Hasil: hikayat/dunia/aset/peta-bawah.png, peta-atas.png, peta.json

Grafik: Ninja Adventure Asset Pack oleh Pixel-boy & AAA (lesen CC0).
Jalankan:  python3 tools/bina-peta.py /laluan/ke/ninja-adventure
"""
import json, random, sys, os
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/assets/na-full"
OUT = os.path.join(os.path.dirname(__file__), "..", "hikayat", "dunia", "aset")
T = 16
W, H = 34, 26
random.seed(7)

def sheet(name):
    return Image.open(os.path.join(SRC, "Backgrounds", "Tilesets", name)).convert("RGBA")

FLOOR, NAT, HOUSE, WATER, ELEM = (sheet(n) for n in
    ["TilesetFloor.png", "TilesetNature.png", "TilesetHouse.png", "TilesetWater.png", "TilesetElement.png"])

def tile(sh, c, r, w=1, h=1):
    return sh.crop((c * T, r * T, (c + w) * T, (r + h) * T))

bawah = Image.new("RGBA", (W * T, H * T))
atas = Image.new("RGBA", (W * T, H * T))
halang = [[0] * W for _ in range(H)]      # 1 = tak boleh lalu
guna = [[0] * W for _ in range(H)]        # sel sudah ada objek (untuk taburan bunga)

def put(img, x, y, layer=None):
    (layer or bawah).alpha_composite(img, (x * T, y * T))

# ---------- tanah ----------
jalan = [[0] * W for _ in range(H)]
def rect(grid, x0, y0, x1, y1, v=1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if 0 <= x < W and 0 <= y < H:
                grid[y][x] = v

rect(jalan, 2, 11, 33, 12)     # jalan utama timur-barat
rect(jalan, 15, 11, 17, 18)    # jalan ke jeti
rect(jalan, 10, 13, 19, 16)    # dataran gerai
rect(jalan, 4, 11, 5, 11)      # depan rumah Tok Malik

air = [[0] * W for _ in range(H)]
rect(air, 0, 19, W - 1, H - 1)
rect(air, 0, 17, 3, 18)        # teluk kecil di kiri
rect(air, 30, 18, 33, 18)

def nine(grid, x, y, base, oob=0):
    """Pilih kepingan 9-slice ikut jiran (n/s/e/w)."""
    g = lambda xx, yy: grid[yy][xx] if 0 <= xx < W and 0 <= yy < H else oob
    n, s, e, w = g(x, y - 1), g(x, y + 1), g(x + 1, y), g(x - 1, y)
    c0, r0 = base
    cx = 0 if not w else (2 if not e else 1)
    cy = 0 if not n else (2 if not s else 1)
    if not w and not e: cx = 1
    if not n and not s: cy = 1
    return c0 + cx, r0 + cy

for y in range(H):
    for x in range(W):
        put(tile(FLOOR, 0, 12), x, y)
        if random.random() < 0.16:
            put(tile(FLOOR, random.choice([1, 2, 3, 4]), 12), x, y)
        if jalan[y][x]:
            put(tile(FLOOR, *nine(jalan, x, y, (0, 7))), x, y)
            if random.random() < 0.06 and nine(jalan, x, y, (0, 7)) == (1, 8):
                put(tile(FLOOR, random.choice([0, 1]), 11), x, y)
        if air[y][x]:
            put(tile(WATER, *nine(air, x, y, (0, 6), oob=1)), x, y)
            halang[y][x] = 1

# ---------- jeti kayu ----------
for y in range(17, 25):
    for i, x in enumerate(range(15, 18)):
        put(tile(WATER, i, 15 if y == 24 else 13), x, y)
        halang[y][x] = 0
        guna[y][x] = 1

# perahu & layar di sebelah jeti
perahu = Image.open(os.path.join(SRC, "Backgrounds", "Vehicles", "Boat.png")).convert("RGBA")
layar = Image.open(os.path.join(SRC, "Backgrounds", "Vehicles", "Sail.png")).convert("RGBA")
bawah.alpha_composite(perahu, (18 * T + 6, 21 * T + 4))
bawah.alpha_composite(layar, (18 * T + 30, 19 * T + 2))
perahu2 = perahu.transpose(Image.FLIP_LEFT_RIGHT)
bawah.alpha_composite(perahu2, (8 * T + 4, 22 * T + 6))

# ---------- objek (cop) ----------
def cop(sh, c, r, w, h, x, y, k=1, halang_baris=None):
    """k = bilangan baris atas yang dilukis di lapisan atas (menutup pemain)."""
    img = tile(sh, c, r, w, h)
    if k:
        atas.alpha_composite(img.crop((0, 0, w * T, k * T)), (x * T, y * T))
    bawah.alpha_composite(img.crop((0, k * T, w * T, h * T)), (x * T, (y + k) * T))
    rows = halang_baris if halang_baris is not None else range(k, h)
    for yy in range(h):
        for xx in range(w):
            guna[y + yy][x + xx] = 1
    for yy in rows:
        for xx in range(w):
            halang[y + yy][x + xx] = 1

# rumah Melayu Tok Malik (bumbung tinggi)
cop(HOUSE, 25, 7, 4, 7, 3, 4, k=4, halang_baris=range(3, 7))
# rumah-rumah kampung
cop(HOUSE, 0, 0, 4, 3, 20, 6, k=1)
cop(HOUSE, 12, 0, 4, 3, 25, 6, k=1)
cop(HOUSE, 4, 0, 4, 3, 9, 6, k=1)
# gudang kayu tepi laut
cop(HOUSE, 25, 14, 4, 5, 27, 13, k=2)

# gerai Tok Malik: bakul di bawah kanopi
for i in range(3):
    put(tile(HOUSE, 16 + i, 13), 12 + i, 14)
cop(HOUSE, 16, 16, 3, 2, 12, 13, k=1)
cop(HOUSE, 19, 14, 2, 2, 10, 13, k=0)          # peti buah
put(tile(HOUSE, 16, 15), 18, 13); halang[13][18] = 1; guna[13][18] = 1
put(tile(HOUSE, 17, 15), 19, 13); halang[13][19] = 1; guna[13][19] = 1
put(tile(HOUSE, 18, 12), 18, 16); halang[16][18] = 1; guna[16][18] = 1   # tempayan

# ---------- pokok ----------
POKOK = [(0, 0), (2, 0), (16, 0), (18, 0)]
def pokok(x, y, jenis=None):
    c, r = jenis or random.choice(POKOK)
    if any(guna[y + j][x + i] or jalan[y + j][x + i] or air[y + j][x + i] for j in range(2) for i in range(2)):
        return
    cop(NAT, c, r, 2, 2, x, y, k=1)

for x in range(0, W, 2):
    pokok(x, 0); pokok(x, 2)
for y in range(4, 17, 2):
    pokok(0, y)
    if not (10 <= y <= 12):
        pokok(32, y)
rect(halang, 0, 0, W - 1, 1)
for (x, y) in [(13, 8), (24, 9), (8, 15), (21, 15), (1, 15), (30, 9), (7, 2), (26, 16), (22, 3)]:
    pokok(x, y)
pokok(23, 13, (16, 0)); pokok(24, 16, (0, 0))

# kelapa / buluh di tepi pantai
for x in (20, 23, 26):
    if not guna[17][x] and not jalan[17][x]:
        cop(NAT, 11, 8, 1, 3, x, 15, k=2, halang_baris=[2])

# taburan bunga & semak
HIASAN = [(0, 10), (1, 10), (2, 10), (3, 10), (6, 10), (0, 11), (1, 11), (2, 11), (6, 11)]
for y in range(4, 19):
    for x in range(2, 32):
        if not (guna[y][x] or jalan[y][x] or air[y][x] or halang[y][x]) and random.random() < 0.07:
            put(tile(NAT, *random.choice(HIASAN)), x, y)
            guna[y][x] = 1

# sempadan timur: pagar kecuali pintu pasar
for y in list(range(4, 11)) + list(range(13, 19)):
    halang[y][33] = 1

# ---------- simpan ----------
bawah.save(os.path.join(OUT, "peta-bawah.png"), optimize=True)
atas.save(os.path.join(OUT, "peta-atas.png"), optimize=True)
riak = [[x, y] for y in range(20, H) for x in range(W) if air[y][x] and not (15 <= x <= 17) and random.random() < 0.06]
json.dump({
    "w": W, "h": H, "tile": T,
    "halang": ["".join(str(v) for v in row) for row in halang],
    "riak": riak,
}, open(os.path.join(OUT, "peta.json"), "w"))
print("siap", W * T, H * T)
