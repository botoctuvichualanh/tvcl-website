from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageChops


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "img" / "og" / "toan-thu"
W, H, SCALE = 1200, 630, 2

STARS = [
    ("tu-vi", "Tử Vi", "#247F85"),
    ("thien-co", "Thiên Cơ", "#477FC2"),
    ("thai-duong", "Thái Dương", "#B0822A"),
    ("vu-khuc", "Vũ Khúc", "#527B56"),
    ("thien-dong", "Thiên Đồng", "#CB735C"),
    ("liem-trinh", "Liêm Trinh", "#B6536D"),
    ("thien-phu", "Thiên Phủ", "#8B704D"),
    ("thai-am", "Thái Âm", "#5D78A5"),
    ("tham-lang", "Tham Lang", "#8A6696"),
    ("cu-mon", "Cự Môn", "#A05770"),
    ("thien-tuong", "Thiên Tướng", "#3C8A78"),
    ("thien-luong", "Thiên Lương", "#718C4A"),
    ("that-sat", "Thất Sát", "#A35445"),
    ("pha-quan", "Phá Quân", "#6F68A8"),
]

FONT_REG = Path("C:/Windows/Fonts/segoeui.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/segoeuib.ttf")
LOGO = ROOT / "assets" / "img" / "tvcl-logo-6.png"
LANDSCAPE = ROOT / "assets" / "img" / "hero-shanshui.jpg"
HUB_IMAGE = "tu-vi-dau-so-toan-thu-1200x630.png"
_logo_rgb = Image.open(LOGO).convert("RGB").crop((115, 110, 1070, 1060))
_logo_r, _logo_g, _logo_b = _logo_rgb.split()
_logo_alpha = ImageChops.invert(ImageChops.darker(ImageChops.darker(_logo_r, _logo_g), _logo_b))
_logo = _logo_rgb.convert("RGBA")
_logo.putalpha(_logo_alpha)
_logo.thumbnail((330 * SCALE, 330 * SCALE), Image.Resampling.LANCZOS)


def rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def tint(color: tuple[int, int, int], background: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(foreground * amount + base * (1 - amount)) for foreground, base in zip(color, background))


def f(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REG), size * SCALE)


def fitted_font(text: str, max_size: int, max_width: int) -> ImageFont.FreeTypeFont:
    for size in range(max_size, 67, -1):
        font = f(size, True)
        if font.getlength(text) / SCALE <= max_width:
            return font
    return f(67, True)


def make_image(title: str, accent_hex: str, hub: bool = False) -> Image.Image:
    width, height = W * SCALE, H * SCALE
    accent = rgb(accent_hex)
    paper = (247, 245, 240)
    ink = (36, 52, 71)
    muted = (91, 107, 125)

    base = Image.new("RGBA", (width, height), (*paper, 255))

    # Reuse the site's own shanshui artwork as a softly faded, right-side texture.
    source = Image.open(LANDSCAPE).convert("RGB")
    landscape = source.crop((595, 0, 1190, 590)).resize((width, height), Image.Resampling.LANCZOS)
    landscape = Image.blend(landscape, Image.new("RGB", landscape.size, paper), 0.42).convert("RGBA")
    fade = Image.new("L", (width, height), 0)
    fade_draw = ImageDraw.Draw(fade)
    for x in range(width):
        opacity = int(190 * max(0, min(1, (x - 820) / 930)))
        fade_draw.line((x, 0, x, height), fill=opacity)
    landscape.putalpha(fade)
    base.alpha_composite(landscape)

    draw = ImageDraw.Draw(base, "RGBA")
    # Thin frame, house palette, and accent stripe.
    draw.rounded_rectangle((28 * SCALE, 28 * SCALE, (W - 28) * SCALE, (H - 28) * SCALE), radius=28 * SCALE, outline=(227, 230, 234, 230), width=2 * SCALE)
    draw.rounded_rectangle((58 * SCALE, 76 * SCALE, 65 * SCALE, 160 * SCALE), radius=4 * SCALE, fill=(*accent, 255))

    # Use the official TVCL roundel alone in the former orbit area.
    base.alpha_composite(_logo, (823 * SCALE, 148 * SCALE))
    draw = ImageDraw.Draw(base, "RGBA")

    draw.text((87 * SCALE, 86 * SCALE), "TÀNG KINH CÁC  ·  TỬ VI ĐẨU SỐ TOÀN THƯ", font=f(16, True), fill=(*accent, 255))

    if hub:
        draw.text((84 * SCALE, 185 * SCALE), "Tử Vi Đẩu Số", font=f(74, True), fill=(*ink, 255))
        draw.text((84 * SCALE, 272 * SCALE), "Toàn Thư", font=f(74, True), fill=(*ink, 255))
        draw.rounded_rectangle((87 * SCALE, 370 * SCALE, 466 * SCALE, 413 * SCALE), radius=21 * SCALE, fill=(*tint((30, 154, 163), paper, .09), 255), outline=(*tint((30, 154, 163), paper, .34), 255), width=1 * SCALE)
        draw.text((107 * SCALE, 379 * SCALE), "TRA CỨU 14 CHÍNH TINH", font=f(18, True), fill=(30, 121, 129, 255))
    else:
        heading = "Sao " + title
        draw.text((84 * SCALE, 176 * SCALE), heading, font=fitted_font(heading, 82, 680), fill=(*ink, 255))
        draw.text((89 * SCALE, 286 * SCALE), "TRONG TỬ VI ĐẨU SỐ", font=f(38, True), fill=(*accent, 255))
        draw.text((89 * SCALE, 342 * SCALE), "TOÀN THƯ", font=f(38, True), fill=(*accent, 255))

    return base.convert("RGB").resize((W, H), Image.Resampling.LANCZOS)


def write_metadata(file_name: str, page: Path, url: str, alt: str) -> None:
    content = page.read_text(encoding="utf-8")
    image_url = f"https://tuvichualanh.com/assets/img/og/toan-thu/{file_name}"
    og_pattern = re.compile(r'<meta property="og:image" content="[^"]*">')
    if not og_pattern.search(content):
        raise ValueError(f"Missing og:image tag in {page}")
    content = re.sub(r'\n<meta property="og:image:(?:width|height|type|alt)" content="[^"]*">', "", content)
    content = og_pattern.sub(
        f'<meta property="og:image" content="{image_url}">\n'
        f'<meta property="og:image:width" content="1200">\n'
        f'<meta property="og:image:height" content="630">\n'
        f'<meta property="og:image:type" content="image/png">\n'
        f'<meta property="og:image:alt" content="{alt}">',
        content,
        count=1,
    )
    if re.search(r'<meta name="twitter:image"', content):
        content = re.sub(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{image_url}">', content, count=1)
    else:
        content = content.replace('<meta name="twitter:card" content="summary_large_image">', f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:image" content="{image_url}">', 1)
    page.write_text(content, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hub = make_image("", "#1E9AA3", hub=True)
    hub.save(OUT / HUB_IMAGE, format="PNG", optimize=True)
    write_metadata(
        HUB_IMAGE,
        ROOT / "tu-vi-dau-so-toan-thu" / "index.html",
        "https://tuvichualanh.com/tu-vi-dau-so-toan-thu/",
        "Tử Vi Đẩu Số Toàn Thư — tra cứu 14 chính tinh, Tử Vi Chữa Lành",
    )

    for slug, name, color in STARS:
        file_name = f"sao-{slug}-tu-vi-dau-so-toan-thu-1200x630.png"
        make_image(name, color).save(OUT / file_name, format="PNG", optimize=True)
        write_metadata(
            file_name,
            ROOT / f"sao-{slug}-tu-vi-dau-so-toan-thu" / "index.html",
            f"https://tuvichualanh.com/sao-{slug}-tu-vi-dau-so-toan-thu/",
            f"Sao {name} trong Tử Vi Đẩu Số Toàn Thư — Tử Vi Chữa Lành",
        )


if __name__ == "__main__":
    main()
