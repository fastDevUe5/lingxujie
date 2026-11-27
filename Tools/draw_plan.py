"""Draw the P0 zone plan (gate -> village -> training ground) as a scaled top-down sketch.

    python Tools/draw_plan.py Saved/plan_p0.png

Coordinates are Unreal units (cm), Y up on the sheet, matching the level so the numbers can be
copied straight into build_level.py.
"""

import sys

from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "Saved/plan_p0.png"

W, H = 1500, 1780
MARGIN = 90
WORLD_MIN, WORLD_MAX = -9000.0, 9000.0     # 180 m of world across the sheet
SCALE = (W - 2 * MARGIN) / (WORLD_MAX - WORLD_MIN)
FONT = "C:/Windows/Fonts/msyh.ttc"


def font(size, bold=False):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def to_px(x, y):
    px = MARGIN + (x - WORLD_MIN) * SCALE
    py = H - MARGIN - (y - WORLD_MIN) * SCALE
    return px, py


def zone(draw, cx, cy, width, height, fill, outline, label, sub):
    x0, y0 = to_px(cx - width / 2, cy + height / 2)
    x1, y1 = to_px(cx + width / 2, cy - height / 2)
    draw.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=3)
    draw.text((x0 + 14, y0 + 10), label, font=font(30), fill=(255, 250, 240))
    draw.text((x0 + 14, y0 + 48), sub, font=font(20), fill=(220, 220, 210))


def road(draw, points, width_px=16):
    draw.line([to_px(x, y) for x, y in points], fill=(196, 176, 140), width=width_px, joint="curve")


sheet = Image.new("RGB", (W, H), (28, 30, 34))
draw = ImageDraw.Draw(sheet)

# title
draw.text((MARGIN, 34), "灵虚界 P0 关卡动线：山门 → 落霞村 → 听雨坪", font=font(40), fill=(240, 236, 226))
draw.text((MARGIN, 86), "比例 1 格 = 10 m，坐标单位 cm，与 build_level.py 一致", font=font(20), fill=(170, 172, 176))

# grid
for step in range(-9000, 9001, 1000):
    x0, _ = to_px(step, 0)
    _, y0 = to_px(0, step)
    draw.line([(x0, MARGIN), (x0, H - MARGIN)], fill=(46, 48, 54), width=1)
    draw.line([(MARGIN, y0), (W - MARGIN, y0)], fill=(46, 48, 54), width=1)

# the road first, so the zones sit on top of it
road(draw, [(0, -7900), (0, -4600), (0, -700)])

# zones (drawn south = bottom to north = top)
zone(draw, 0, -7900, 3200, 3200, (44, 62, 58), (120, 200, 170),
     "山门 · 青云隘", "32 × 32 m · 出生点 / 教学")
zone(draw, 0, -4600, 5000, 5000, (52, 58, 44), (170, 200, 120),
     "村落 · 落霞村", "50 × 50 m · NPC / 商店 / 水塘")
zone(draw, 0, -700, 3000, 3000, (58, 46, 44), (220, 150, 120),
     "后山 · 听雨坪", "30 × 30 m · 打怪 / Boss")

# POIs
POINTS = [
    (0, -8200, "城楼（城门包）"),
    (0, -7800, "出生点 PlayerStart"),
    (-900, -7700, "引导 NPC"),
    (150, -4650, "水塘园林（洗然亭）"),
    (-1600, -4900, "民居群 3–5 栋"),
    (1600, -4600, "杂货商 / 任务 NPC"),
    (0, -700, "Boss 石台"),
    (900, -500, "小怪群 6–8"),
]
for x, y, label in POINTS:
    px, py = to_px(x, y)
    draw.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(255, 226, 150), outline=(40, 40, 40))
    draw.text((px + 14, py - 12), label, font=font(20), fill=(246, 244, 236))

# legend + notes
notes = [
    "动线：一条主路从南到北，不做岔路（P0 只验闭环）",
    "村口到道场步行约 45–60 s，来回一次构成一个任务环",
    "水面已在 (150, -4350)，碗形地形归 build_level._terrain_height",
    "城楼现位于 (0, -1500)，需改到 (0, -6600) 作为山门入口",
]
for index, line in enumerate(notes):
    draw.text((MARGIN, H - MARGIN - 120 + index * 28), "· " + line, font=font(20), fill=(200, 200, 196))

sheet.save(OUT)
print("plan written:", OUT)
