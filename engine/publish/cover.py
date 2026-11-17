"""Covers: 600 x 800 grayscale PNGs, dithered to 16 gray levels for e-ink."""
import io
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 600, 800
SERIF = ["/System/Library/Fonts/Supplemental/Georgia.ttf", "/Library/Fonts/Georgia.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "DejaVuSerif.ttf"]
SERIF_BOLD = ["/System/Library/Fonts/Supplemental/Georgia Bold.ttf", "/Library/Fonts/Georgia Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "DejaVuSerif-Bold.ttf"]


def _font(size, bold=False):
    for p in SERIF_BOLD if bold else SERIF:
        if Path(p).exists() or "/" not in p:
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def _center(draw, y, text, font, fill=0):
    w = draw.textlength(text, font=font)
    draw.text(((W - w) / 2, y), text, font=font, fill=fill)
    return y + font.size * 1.25


def _wrapped(draw, y, text, font, width_chars, fill=0, max_lines=4):
    lines = textwrap.wrap(text, width_chars)[:max_lines]
    for line in lines:
        y = _center(draw, y, line, font, fill)
    return y


def dither16(img):
    """Quantize a grayscale image to 16 levels with Floyd-Steinberg dithering."""
    pal = Image.new("P", (1, 1))
    levels = [round(i * 255 / 15) for i in range(16)]
    pal.putpalette(sum(([v, v, v] for v in levels), []) + [0] * (768 - 48))
    q = img.convert("RGB").quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG)
    return q.convert("L")


def png_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def unit_cover(subject_title, n, total, chapter, subtitle=None, pass_no=1):
    img = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(img)
    d.rectangle([24, 24, W - 25, H - 25], outline=0, width=3)
    d.rectangle([34, 34, W - 35, H - 35], outline=96, width=1)
    y = _wrapped(d, 90, subject_title.upper(), _font(40, bold=True), 18, max_lines=2)
    d.line([(W / 2 - 80, y + 18), (W / 2 + 80, y + 18)], fill=0, width=2)
    _center(d, 250, "UNIT", _font(30), fill=64)
    big = _font(170, bold=True)
    _center(d, 290, str(n), big)
    _center(d, 500, f"of {total}", _font(34), fill=48)
    y = _wrapped(d, 580, chapter or "", _font(32), 26, max_lines=3)
    if subtitle:
        _wrapped(d, y + 6, subtitle, _font(24), 34, fill=80, max_lines=2)
    foot = "second pass" if pass_no == 2 else (f"pass {pass_no}" if pass_no > 2 else "")
    if foot:
        _center(d, H - 120, foot, _font(26), fill=64)
    _center(d, H - 80, "wikicourse", _font(22), fill=96)
    return png_bytes(dither16(img))


def course_cover(subject_title, n_units, n_entries, tagline=None):
    img = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(img)
    d.rectangle([24, 24, W - 25, H - 25], outline=0, width=3)
    d.rectangle([34, 34, W - 35, H - 35], outline=96, width=1)
    y = _wrapped(d, 150, subject_title, _font(64, bold=True), 14, max_lines=3)
    d.line([(W / 2 - 100, y + 30), (W / 2 + 100, y + 30)], fill=0, width=3)
    _center(d, y + 70, "The complete course", _font(36))
    _center(d, y + 130, f"{n_units} units · {n_entries:,} entries", _font(28), fill=64)
    if tagline:
        _wrapped(d, H - 230, tagline, _font(24), 36, fill=80, max_lines=4)
    _center(d, H - 80, "wikicourse", _font(22), fill=96)
    return png_bytes(dither16(img))
