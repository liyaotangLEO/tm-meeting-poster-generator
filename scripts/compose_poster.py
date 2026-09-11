# -*- coding: utf-8 -*-
"""
头马例会海报 PIL 合成脚本
功能：在 AI 生成的背景主视觉上，精确合成头马 logo、底部时间地址和二维码。

用法：
    python compose_poster.py --bg <背景图路径> --qr <二维码路径> --time "<时间文本>" --address "<地址文本>" --output <输出路径>

可选参数：
    --logo      logo路径（默认使用Skill内置logo）
    --logo-size logo宽度（默认210px）
    --logo-pos  logo位置，格式"x,y"（默认"70,65"）
    --qr-size   二维码尺寸（默认275px）
    --time-size 时间字号（默认58px）
    --addr-size 地址字号（默认42px）
"""

from PIL import Image, ImageDraw, ImageFont
import os
import argparse

# ========== 默认配置 ==========

# Skill 根目录（脚本位于 scripts/ 下，上级为 Skill 根目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

# 内置 logo 路径
DEFAULT_LOGO_PATH = os.path.join(SKILL_DIR, "assets", "logo", "toastmasters-logo-color.png")

# 字体路径（思源黑体，免费商用）
FONT_PATH = r"C:\Windows\Fonts\Noto Sans SC (TrueType).otf"
FONT_PATH_BOLD = r"C:\Windows\Fonts\Noto Sans SC Bold (TrueType).otf"

# 品牌色
COLOR_MAROON = (119, 36, 50)       # 栗红 #772432
COLOR_HAPPY_YELLOW = (242, 223, 116)  # 快乐黄 #F2DF74
COLOR_WHITE = (255, 255, 255)
COLOR_LIGHT_GRAY = (220, 220, 220)


def draw_rounded_rect(draw, xy, radius, fill):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
    draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)


def compose_poster(
    bg_path,
    qr_path,
    time_text,
    address_text,
    output_path,
    logo_path=None,
    logo_size=210,
    logo_pos=(70, 65),
    qr_size=275,
    time_size=58,
    addr_size=42,
):
    """
    合成海报

    参数:
        bg_path: 背景图路径（AI生成的主视觉）
        qr_path: 二维码路径
        time_text: 时间文本，如"2026年8月26日 周二 19:30-21:30"
        address_text: 地址文本，如"深圳市南山区 金地威新中心A座4F·太湖会议室"
        output_path: 输出路径
        logo_path: logo路径，默认使用Skill内置logo
        logo_size: logo宽度，默认210px
        logo_pos: logo位置(x,y)，默认(70,65)
        qr_size: 二维码尺寸，默认275px
        time_size: 时间字号，默认58px
        addr_size: 地址字号，默认42px

    返回:
        输出文件路径
    """
    if logo_path is None:
        logo_path = DEFAULT_LOGO_PATH

    # 打开背景图
    poster = Image.open(bg_path).convert("RGBA")
    W, H = poster.size
    print(f"海报尺寸: {W}x{H}")

    draw = ImageDraw.Draw(poster)

    # ========== 1. 贴头马 LOGO（左上角，规范留白） ==========
    logo = Image.open(logo_path).convert("RGBA")
    logo_w, logo_h = logo.size
    target_logo_w = logo_size
    target_logo_h = int(logo_h * target_logo_w / logo_w)
    logo_resized = logo.resize((target_logo_w, target_logo_h), Image.LANCZOS)

    logo_x, logo_y = logo_pos
    poster.paste(logo_resized, (logo_x, logo_y), logo_resized)
    print(f"LOGO已贴到 ({logo_x}, {logo_y})，尺寸 {target_logo_w}x{target_logo_h}")

    # ========== 2. 底部重新排版 ==========
    # 覆盖原底部文字区域（从底部约17%开始）
    cover_y_start = int(H * 0.83)
    top_cover_color = poster.getpixel((W // 2, cover_y_start))
    bottom_cover_color = poster.getpixel((W // 2, H - 20))

    cover_layer = Image.new("RGBA", (W, H - cover_y_start), (0, 0, 0, 0))
    cover_draw = ImageDraw.Draw(cover_layer)
    for y in range(H - cover_y_start):
        ratio = y / (H - cover_y_start)
        r = int(top_cover_color[0] * (1 - ratio) + bottom_cover_color[0] * ratio)
        g = int(top_cover_color[1] * (1 - ratio) + bottom_cover_color[1] * ratio)
        b = int(top_cover_color[2] * (1 - ratio) + bottom_cover_color[2] * ratio)
        cover_draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
    poster.paste(cover_layer, (0, cover_y_start), cover_layer)
    draw = ImageDraw.Draw(poster)

    # ========== 右侧：微信二维码 ==========
    left_x = int(W * 0.046)  # 约70px (1536*0.046≈70)
    qr_bg_y = cover_y_start + 8
    pad = 18
    bg_w = qr_size + pad * 2
    bg_h = qr_size + pad * 2
    qr_bg_x = W - bg_w - int(W * 0.033)  # 约50px右边距
    qr_center_y = qr_bg_y + bg_h // 2

    # 白色圆角底衬
    draw_rounded_rect(draw, [qr_bg_x, qr_bg_y, qr_bg_x + bg_w, qr_bg_y + bg_h], 16, (255, 255, 255, 255))

    # 贴二维码
    qr = Image.open(qr_path).convert("RGBA")
    qr_resized = qr.resize((qr_size, qr_size), Image.LANCZOS)
    qr_x = qr_bg_x + pad
    qr_y = qr_bg_y + pad
    poster.paste(qr_resized, (qr_x, qr_y), qr_resized)

    # 二维码左侧竖排标签（避免下方标签跑出画面）
    label_font = ImageFont.truetype(FONT_PATH, 22)
    label_text = "扫码加入我们"
    label_color = COLOR_LIGHT_GRAY

    # 竖排：每个字单独绘制，从上到下
    char_spacing = 8
    label_total_h = len(label_text) * (22 + char_spacing) - char_spacing
    label_x = qr_bg_x - 35  # 二维码左侧，留5px间距
    label_start_y = qr_bg_y + (bg_h - label_total_h) // 2  # 垂直居中

    for i, char in enumerate(label_text):
        char_y = label_start_y + i * (22 + char_spacing)
        draw.text((label_x, char_y), char, font=label_font, fill=label_color)

    print(f"二维码已贴到 ({qr_x}, {qr_y})，尺寸 {qr_size}x{qr_size}")
    print(f"竖排标签位于二维码左侧 x={label_x}, y={label_start_y}-{label_start_y+label_total_h}")

    # ========== 左侧：时间 + 地址 ==========
    time_font = ImageFont.truetype(FONT_PATH_BOLD, time_size)
    addr_font = ImageFont.truetype(FONT_PATH, addr_size)

    # 检查地址宽度，过长时自动缩小
    max_text_width = qr_bg_x - left_x - 40
    addr_bbox = draw.textbbox((0, 0), address_text, font=addr_font)
    addr_w_actual = addr_bbox[2] - addr_bbox[0]

    if addr_w_actual > max_text_width:
        scale = max_text_width / addr_w_actual
        new_addr_size = int(addr_size * scale)
        addr_font = ImageFont.truetype(FONT_PATH, new_addr_size)
        addr_bbox = draw.textbbox((0, 0), address_text, font=addr_font)
        print(f"地址自动缩小到字号 {new_addr_size}")

    time_bbox = draw.textbbox((0, 0), time_text, font=time_font)
    time_h = time_bbox[3] - time_bbox[1]
    addr_h = addr_bbox[3] - addr_bbox[1]
    line_gap = 48
    total_text_h = time_h + line_gap + addr_h
    text_start_y = qr_center_y - total_text_h // 2
    time_y = text_start_y
    addr_y = time_y + time_h + line_gap

    draw.text((left_x, time_y), time_text, font=time_font, fill=COLOR_HAPPY_YELLOW)
    draw.text((left_x, addr_y), address_text, font=addr_font, fill=COLOR_WHITE)
    print(f"时间 (y={time_y}): {time_text}")
    print(f"地址 (y={addr_y}): {address_text}")

    # ========== 保存 ==========
    poster_rgb = poster.convert("RGB")
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    poster_rgb.save(output_path, "PNG", quality=95)
    print(f"\n最终海报已保存: {output_path}")
    print(f"最终尺寸: {poster_rgb.size}")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="头马例会海报 PIL 合成脚本")
    parser.add_argument("--bg", required=True, help="背景图路径（AI生成的主视觉）")
    parser.add_argument("--qr", required=True, help="二维码路径")
    parser.add_argument("--time", required=True, help="时间文本")
    parser.add_argument("--address", required=True, help="地址文本")
    parser.add_argument("--output", required=True, help="输出路径")
    parser.add_argument("--logo", default=None, help="logo路径（默认使用Skill内置logo）")
    parser.add_argument("--logo-size", type=int, default=210, help="logo宽度（默认210px）")
    parser.add_argument("--logo-pos", default="70,65", help="logo位置，格式'x,y'（默认'70,65'）")
    parser.add_argument("--qr-size", type=int, default=275, help="二维码尺寸（默认275px）")
    parser.add_argument("--time-size", type=int, default=58, help="时间字号（默认58px）")
    parser.add_argument("--addr-size", type=int, default=42, help="地址字号（默认42px）")

    args = parser.parse_args()

    # 解析 logo 位置
    logo_pos = tuple(map(int, args.logo_pos.split(",")))

    compose_poster(
        bg_path=args.bg,
        qr_path=args.qr,
        time_text=args.time,
        address_text=args.address,
        output_path=args.output,
        logo_path=args.logo,
        logo_size=args.logo_size,
        logo_pos=logo_pos,
        qr_size=args.qr_size,
        time_size=args.time_size,
        addr_size=args.addr_size,
    )


if __name__ == "__main__":
    main()