#!/usr/bin/env python3
"""THE WORLD IN ONE IMAGE - Tuesday 17 November 2026.
Procedural front page, standard library only. Deterministic PNG output.
Draws everything with hand-made shapes and a hand-written 5x7 bitmap font.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---- colours ----
PAPER = (247, 243, 232)
NAVY = (16, 36, 62)
NAVY2 = (24, 52, 88)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
INK = (28, 32, 40)
GOLD = (212, 175, 55)
RED = (180, 35, 24)
BLUE = (29, 78, 216)
TEAL = (14, 116, 144)
PURPLE = (124, 58, 237)
ORANGE = (194, 65, 12)
GREEN = (21, 128, 61)
LIGHT_RED = (253, 236, 234)
LIGHT_BLUE = (219, 234, 254)
LIGHT_TEAL = (207, 250, 254)
LIGHT_PURPLE = (237, 233, 254)
LIGHT_ORANGE = (255, 237, 213)
LIGHT_GREEN = (220, 252, 231)
SEA = (30, 90, 140)
YELLOW = (250, 204, 21)
GREY = (100, 116, 139)

# ---- hand-written 5x7 bitmap font: '#' = on, '.' = off ----
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "11111", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", "01100", "01100"),
    ',': (".....", ".....", ".....", ".....", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", ".....", ".....", ".....", "....."),
    ':': (".....", "01100", "01100", ".....", "01100", "01100", "....."),
    '!': ("00100", "00100", "00100", "00100", "00100", ".....", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '+': (".....", "00100", "00100", "11111", "00100", "00100", "....."),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
}

# ---- canvas ----
buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i] = c[0]
        buf[i + 1] = c[1]
        buf[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, c)


def ring(cx, cy, r, t, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
            if (r - t) * (r - t) <= d <= r * r:
                px(xx, yy, c)


def tri(x1, y1, x2, y2, x3, y3, c):
    minx, maxx = min(x1, x2, x3), max(x1, x2, x3)
    miny, maxy = min(y1, y2, y3), max(y1, y2, y3)
    d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    if d == 0:
        return
    for yy in range(miny, maxy + 1):
        for xx in range(minx, maxx + 1):
            a = ((y2 - y3) * (xx - x3) + (x3 - x2) * (yy - y3)) / d
            b = ((y3 - y1) * (xx - x3) + (x1 - x3) * (yy - y3)) / d
            cc = 1 - a - b
            if a >= 0 and b >= 0 and cc >= 0:
                px(xx, yy, c)


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == '1':
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
        cx += 6 * scale


def draw_text_c(cx, y, s, scale, c):
    draw_text(cx - text_w(s, scale) // 2, y, s, scale, c)


# ---- pictograms, each in a 132 x 168 box at (bx, by) ----
def pic_strike(bx, by):
    rect(bx, by, 132, 168, LIGHT_RED)
    # sky + sea
    rect(bx, by + 118, 132, 50, SEA)
    rect(bx, by + 118, 132, 4, WHITE)
    # island
    tri(bx + 18, by + 118, bx + 114, by + 118, bx + 66, by + 82, (120, 90, 60))
    # ship hull on sea
    rect(bx + 14, by + 128, 104, 16, (40, 40, 44))
    rect(bx + 52, by + 112, 28, 16, (40, 40, 44))
    # flames above ship
    tri(bx + 52, by + 112, bx + 66, by + 112, bx + 59, by + 78, (249, 115, 22))
    tri(bx + 70, by + 112, bx + 84, by + 112, bx + 77, by + 84, (220, 38, 38))
    tri(bx + 38, by + 112, bx + 50, by + 112, bx + 44, by + 90, (250, 204, 21))
    # warplane top right: fuselage + nose + wing + tail
    rect(bx + 78, by + 28, 34, 10, (30, 30, 34))
    tri(bx + 112, by + 28, bx + 126, by + 33, bx + 112, by + 38, (30, 30, 34))
    tri(bx + 88, by + 38, bx + 102, by + 38, bx + 92, by + 54, GREY)
    rect(bx + 78, by + 18, 6, 12, (30, 30, 34))
    # explosion star on island
    disc(bx + 66, by + 72, 10, YELLOW)
    disc(bx + 66, by + 72, 5, RED)


def pic_summit(bx, by):
    rect(bx, by, 132, 168, LIGHT_BLUE)
    # globe
    disc(bx + 66, by + 84, 52, SEA)
    rect(bx + 22, by + 78, 88, 10, (34, 139, 80))
    rect(bx + 40, by + 40, 26, 22, (34, 139, 80))
    rect(bx + 76, by + 108, 30, 22, (34, 139, 80))
    ring(bx + 66, by + 84, 52, 4, WHITE)
    # three leaders: three circles below globe
    disc(bx + 30, by + 148, 14, (220, 38, 38))
    disc(bx + 66, by + 148, 14, (29, 78, 216))
    disc(bx + 102, by + 148, 14, (250, 204, 21))
    disc(bx + 30, by + 148, 5, WHITE)
    disc(bx + 66, by + 148, 5, WHITE)
    disc(bx + 102, by + 148, 5, BLACK)


def pic_bridge(bx, by):
    rect(bx, by, 132, 168, LIGHT_TEAL)
    # water
    rect(bx, by + 128, 132, 40, SEA)
    # bridge deck + two towers + cables to centre
    rect(bx + 6, by + 96, 120, 10, (60, 60, 66))
    rect(bx + 28, by + 52, 8, 44, (60, 60, 66))
    rect(bx + 96, by + 52, 8, 44, (60, 60, 66))
    tri(bx + 32, by + 54, bx + 36, by + 54, bx + 66, by + 94, (90, 90, 96))
    tri(bx + 100, by + 54, bx + 96, by + 54, bx + 66, by + 94, (90, 90, 96))
    rect(bx + 6, by + 96, 120, 4, WHITE)
    # pillars
    rect(bx + 24, by + 106, 8, 22, (60, 60, 66))
    rect(bx + 100, by + 106, 8, 22, (60, 60, 66))
    # explosion at centre
    disc(bx + 66, by + 44, 16, YELLOW)
    disc(bx + 66, by + 44, 9, (249, 115, 22))
    disc(bx + 66, by + 44, 4, RED)
    # sparks
    rect(bx + 40, by + 26, 6, 6, YELLOW)
    rect(bx + 88, by + 30, 6, 6, YELLOW)
    rect(bx + 66, by + 14, 6, 6, (249, 115, 22))


def pic_measles(bx, by):
    rect(bx, by, 132, 168, LIGHT_PURPLE)
    # virus ball with spikes
    disc(bx + 66, by + 78, 38, PURPLE)
    for dx, dy in ((-38, 0), (38, 0), (0, -38), (0, 38), (-27, -27), (27, -27), (-27, 27), (27, 27)):
        disc(bx + 66 + dx, by + 78 + dy, 7, PURPLE)
    disc(bx + 52, by + 66, 7, (200, 170, 255))
    disc(bx + 80, by + 88, 7, (200, 170, 255))
    # big red X over it: two thin diagonal bars
    tri(bx + 28, by + 34, bx + 38, by + 28, bx + 106, by + 122, RED)
    tri(bx + 104, by + 34, bx + 94, by + 28, bx + 26, by + 122, RED)
    # shield outline bottom
    rect(bx + 46, by + 140, 40, 6, NAVY)


def pic_outage(bx, by):
    rect(bx, by, 132, 168, LIGHT_ORANGE)
    # dark screen with X
    rect(bx + 16, by + 16, 100, 62, (30, 30, 34))
    rect(bx + 22, by + 22, 88, 50, (10, 40, 70))
    draw_text(bx + 34, by + 36, "NO", 3, (250, 204, 21))
    # bank columns
    rect(bx + 14, by + 96, 104, 6, NAVY)
    for cx in (24, 50, 76, 102):
        rect(bx + cx, by + 102, 8, 34, NAVY)
    rect(bx + 14, by + 136, 104, 8, NAVY)
    # lightning bolt
    tri(bx + 66, by + 84, bx + 82, by + 84, bx + 70, by + 108, YELLOW)
    tri(bx + 58, by + 108, bx + 74, by + 108, bx + 62, by + 132, YELLOW)


def pic_gaza(bx, by):
    rect(bx, by, 132, 168, LIGHT_GREEN)
    # rain clouds
    disc(bx + 40, by + 36, 18, (100, 116, 139))
    disc(bx + 62, by + 30, 20, (100, 116, 139))
    disc(bx + 84, by + 36, 18, (100, 116, 139))
    rect(bx + 24, by + 34, 78, 14, (100, 116, 139))
    # rain drops
    for dx in (30, 52, 74, 96):
        tri(bx + dx, by + 66, bx + dx + 8, by + 66, bx + dx + 4, by + 84, SEA)
    # tents / shelters flooded
    tri(bx + 14, by + 148, bx + 62, by + 148, bx + 38, by + 108, (245, 158, 11))
    tri(bx + 70, by + 148, bx + 118, by + 148, bx + 94, by + 108, (21, 128, 61))
    rect(bx, by + 148, 132, 20, SEA)
    rect(bx, by + 148, 132, 4, WHITE)


# ---- panels ----
# (band colour, headline, pictogram fn, body lines, pictogram bg handled inside fn)
PANELS = [
    (RED, "US STRIKES IRAN", pic_strike,
     ["Warplanes hit", "Qeshm missile", "site. 24 crew", "rescued."]),
    (BLUE, "SUMMIT IN SHENZHEN", pic_summit,
     ["Trump, Xi and", "Putin meet", "for first time", "in China."]),
    (TEAL, "CRIMEAN BRIDGE HIT", pic_bridge,
     ["Ukraine struck", "bridge overnight.", "Russia hit Kyiv", "bridges in reply."]),
    (PURPLE, "MEASLES STATUS LOST", pic_measles,
     ["US loses its", "elimination", "status. First", "time since 2000."]),
    (ORANGE, "ONE WEEK OF OUTAGES", pic_outage,
     ["Airports, banks,", "Apple, Microsoft", "and NSA network", "down. Hack denied."]),
    (GREEN, "GAZA: OPEN CROSSINGS", pic_gaza,
     ["UK, Australia,", "Canada, Italy", "urge crossings", "open. Rain floods."]),
]


def draw_panel(x, y, w, h, band, headline, picfn, lines):
    rect(x, y, w, h, WHITE)
    # border
    rect(x, y, w, 3, NAVY)
    rect(x, y + h - 3, w, 3, NAVY)
    rect(x, y, 3, h, NAVY)
    rect(x + w - 3, y, 3, h, NAVY)
    # band
    rect(x + 3, y + 3, w - 6, 52, band)
    draw_text_c(x + w // 2, y + 16, headline, 3, WHITE)
    # pictogram
    picfn(x + 14, y + 68)
    # body text to the right of pictogram
    tx = x + 162
    ty = y + 76
    for ln in lines:
        draw_text(tx, ty, ln, 3, INK)
        ty += 34
    # gold rule under body area
    rect(tx, y + h - 22, w - 162 - 14, 3, GOLD)


def main():
    rect(0, 0, W, H, PAPER)
    # masthead
    rect(0, 0, W, 168, NAVY)
    rect(0, 164, W, 4, GOLD)
    draw_text_c(W // 2, 16, "THE WORLD IN ONE IMAGE", 4, GOLD)
    draw_text_c(W // 2, 62, "TUESDAY 17 NOVEMBER 2026", 5, WHITE)
    draw_text_c(W // 2, 122, "SIX STORIES FROM AROUND THE WORLD", 2, (200, 210, 225))
    # panels 2 x 3
    xs = (12, 518)
    ys = (180, 440, 700)
    for i, (band, headline, picfn, lines) in enumerate(PANELS):
        draw_panel(xs[i % 2], ys[i // 2], 494, 252, band, headline, picfn, lines)
    # footer
    rect(0, 964, W, 60, NAVY)
    rect(0, 964, W, 4, GOLD)
    draw_text_c(W // 2, 984, "17 NOVEMBER 2026 - WORLD NEWS IN ONE IMAGE", 3, WHITE)
    # PNG encode
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw.extend(buf[yy * W * 3:(yy + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b"")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
