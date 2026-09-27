#!/usr/bin/env python3
"""Buat animasi avatar: rotate orbit + glow breathing.
Pakai: python3 make-anim.py <nama> <r,g,b> [fps] [durasi]
Contoh: python3 make-anim.py kiro "232,200,122"
"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFilter

def make_anim(name, color, fps=20, dur=4.0):
    src = f'png/{name}-512.png'
    if not os.path.exists(src):
        print(f'❌ {src} tidak ada'); return 1
    base = Image.open(src).convert('RGBA')
    n = int(fps * dur)
    frames = []
    for i in range(n):
        t = i / n
        scale = 0.93 + 0.07 * math.sin(t * math.pi * 2)   # breathing
        angle = t * 360                                    # rotate
        f = Image.new('RGBA', (512, 512), (7, 7, 12, 255))
        r = base.resize((int(512*scale), int(512*scale)), Image.LANCZOS)
        off = (512 - r.width) // 2
        f.paste(r, (off, off), r)
        d = ImageDraw.Draw(f, 'RGBA')
        rad = int(198 * scale)
        for k in range(3):
            a = math.radians(angle + k*120)
            x, y = 256 + rad*math.cos(a), 256 + rad*math.sin(a)
            sz = 9 - k*2
            d.ellipse([x-sz, y-sz, x+sz, y+sz], fill=color + (230,))
        glow = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for k in range(3):
            a = math.radians(angle + k*120)
            x, y = 256 + rad*math.cos(a), 256 + rad*math.sin(a)
            gd.ellipse([x-20, y-20, x+20, y+20], fill=color + (90,))
        glow = glow.filter(ImageFilter.GaussianBlur(11))
        f = Image.alpha_composite(f, glow)
        frames.append(f.convert('RGB'))
    os.makedirs('anim', exist_ok=True)
    gif = f'anim/{name}.gif'
    frames[0].save(gif, save_all=True, append_images=frames[1:],
                   duration=int(1000/fps), loop=0)
    print(f'✅ {gif} ({n} frame @ {fps}fps)')
    print(f'   ffmpeg -y -i {gif} -pix_fmt yuv420p -r {fps} anim/{name}.mp4')
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    name = sys.argv[1]
    color = tuple(int(x) for x in sys.argv[2].split(','))
    fps = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    dur = float(sys.argv[4]) if len(sys.argv) > 4 else 4.0
    sys.exit(make_anim(name, color, fps, dur))
