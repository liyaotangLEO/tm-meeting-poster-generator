# -*- coding: utf-8 -*-
"""
头马海报品牌合规检查脚本
功能：自动检查海报是否符合头马品牌规范（5O法则）。

检查项：
1. 主色调检查（采样主区域像素，对比栗红 #772432 或 忠诚蓝 #004165）
2. 强调色检查（采样点缀区域，对比快乐黄 #F2DF74）
3. Logo 尺寸检查（如果提供 logo 区域）
4. 二维码可扫性验证（需要 pyzbar 库，未安装则提示手动检查）
5. 文字清晰度提示

用法：
    python verify_brand.py --poster <海报路径>

可选参数：
    --logo-region logo区域，格式"x1,y1,x2,y2"（用于检查logo尺寸）
    --qr-region   二维码区域，格式"x1,y1,x2,y2"（用于二维码解码）
    --output      检查报告输出路径（默认打印到控制台）
"""

from PIL import Image
import os
import argparse
import json

# ========== 品牌色标准 ==========
BRAND_COLORS = {
    "maroon": {"name": "栗红 True Maroon", "hex": "#772432", "rgb": (119, 36, 50), "role": "主色"},
    "happy_yellow": {"name": "快乐黄 Happy Yellow", "hex": "#F2DF74", "rgb": (242, 223, 116), "role": "强调色"},
    "loyal_blue": {"name": "忠诚蓝 Loyal Blue", "hex": "#004165", "rgb": (0, 65, 101), "role": "主色"},
    "cool_gray": {"name": "冷灰 Cool Gray", "hex": "#A9B2B1", "rgb": (169, 178, 177), "role": "中性色"},
}

# 颜色容差（RGB各通道差值）
COLOR_TOLERANCE = 40

# Logo 最小尺寸（像素）
MIN_LOGO_SIZE = 72


def color_distance(c1, c2):
    """计算两个RGB颜色的欧氏距离"""
    return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5


def is_similar_color(c1, c2, tolerance=COLOR_TOLERANCE):
    """判断两个颜色是否相似"""
    return color_distance(c1, c2) <= tolerance


def sample_region(img, region, sample_count=100):
    """
    采样指定区域的颜色

    参数:
        img: PIL Image
        region: (x1, y1, x2, y2)
        sample_count: 采样点数

    返回:
        平均颜色 (r, g, b)
    """
    x1, y1, x2, y2 = region
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(img.width, x2), min(img.height, y2)

    if x2 <= x1 or y2 <= y1:
        return None

    import random
    random.seed(42)  # 固定种子，结果可复现

    r_total, g_total, b_total = 0, 0, 0
    count = 0

    for _ in range(sample_count):
        x = random.randint(x1, x2 - 1)
        y = random.randint(y1, y2 - 1)
        pixel = img.getpixel((x, y))
        r_total += pixel[0]
        g_total += pixel[1]
        b_total += pixel[2]
        count += 1

    if count == 0:
        return None

    return (r_total // count, g_total // count, b_total // count)


def check_main_color(img):
    """
    检查主色调是否为栗红或忠诚蓝（两者都是头马主色，不分主次）

    采样画面中部大面积区域（排除顶部品牌区和底部落款区）
    """
    W, H = img.size
    # 采样画面中部 60% 区域
    region = (int(W * 0.1), int(H * 0.2), int(W * 0.9), int(H * 0.75))
    avg_color = sample_region(img, region, sample_count=200)

    if avg_color is None:
        return {"status": "error", "message": "无法采样主色调区域"}

    maroon = BRAND_COLORS["maroon"]["rgb"]
    loyal_blue = BRAND_COLORS["loyal_blue"]["rgb"]

    distance_maroon = color_distance(avg_color, maroon)
    distance_blue = color_distance(avg_color, loyal_blue)

    # 取较近的颜色作为主色调判断
    if distance_maroon <= distance_blue:
        main_color_name = "栗红"
        main_color_rgb = maroon
        distance = distance_maroon
    else:
        main_color_name = "忠诚蓝"
        main_color_rgb = loyal_blue
        distance = distance_blue

    # 主色调可以是主色的深色/浅色变体，容差放宽
    if distance <= 80:
        status = "pass"
        message = f"主色调为{main_color_name}系（平均色 RGB{avg_color}，与标准{main_color_name}距离 {distance:.1f}）"
    elif distance <= 120:
        status = "warning"
        message = f"主色调偏{main_color_name}但有偏差（平均色 RGB{avg_color}，与标准{main_color_name}距离 {distance:.1f}），建议检查是否为非标准色"
    else:
        status = "fail"
        message = f"主色调不符合头马主色标准（平均色 RGB{avg_color}，与栗红距离 {distance_maroon:.1f}，与忠诚蓝距离 {distance_blue:.1f}），标准主色：栗红 RGB{maroon} 或 忠诚蓝 RGB{loyal_blue}"

    return {
        "check": "主色调检查",
        "status": status,
        "message": message,
        "avg_color": avg_color,
        "main_color": main_color_name,
        "distance": round(distance, 1),
    }


def check_accent_color(img):
    """
    检查是否有快乐黄作为强调色

    在整个画面中搜索快乐黄像素
    """
    W, H = img.size
    happy_yellow = BRAND_COLORS["happy_yellow"]["rgb"]

    yellow_pixels = 0
    total_pixels = 0

    # 采样整个画面（步长为5，提高效率）
    for y in range(0, H, 5):
        for x in range(0, W, 5):
            pixel = img.getpixel((x, y))
            total_pixels += 1
            if is_similar_color(pixel[:3], happy_yellow, tolerance=50):
                yellow_pixels += 1

    ratio = yellow_pixels / total_pixels if total_pixels > 0 else 0

    if ratio > 0.005:  # 超过0.5%像素为快乐黄
        status = "pass"
        message = f"检测到快乐黄强调色（占比 {ratio*100:.2f}%）"
    elif ratio > 0.001:
        status = "warning"
        message = f"快乐黄强调色较少（占比 {ratio*100:.2f}%），建议适当增加点缀"
    else:
        status = "fail"
        message = "未检测到快乐黄强调色，建议添加快乐黄点缀（时间文字、装饰线等）"

    return {
        "check": "强调色检查",
        "status": status,
        "message": message,
        "yellow_ratio": round(ratio * 100, 2),
    }


def check_logo_size(logo_region):
    """
    检查 logo 尺寸是否达标（最小72px）

    参数:
        logo_region: (x1, y1, x2, y2)
    """
    if logo_region is None:
        return {
            "check": "Logo尺寸检查",
            "status": "skip",
            "message": "未提供logo区域，跳过自动检查。请手动确认logo尺寸≥72px，周边留白=字标高度。",
        }

    x1, y1, x2, y2 = logo_region
    width = x2 - x1
    height = y2 - y1
    min_dim = min(width, height)

    if min_dim >= MIN_LOGO_SIZE:
        status = "pass"
        message = f"Logo尺寸达标（{width}x{height}px，最小边 {min_dim}px ≥ {MIN_LOGO_SIZE}px）"
    else:
        status = "fail"
        message = f"Logo尺寸过小（{width}x{height}px，最小边 {min_dim}px < {MIN_LOGO_SIZE}px），请放大至≥{MIN_LOGO_SIZE}px"

    return {
        "check": "Logo尺寸检查",
        "status": status,
        "message": message,
        "width": width,
        "height": height,
    }


def check_qr_readable(img, qr_region=None):
    """
    检查二维码是否可扫

    需要 pyzbar 库，如果未安装则提示手动检查
    """
    try:
        from pyzbar.pyzbar import decode
    except ImportError:
        return {
            "check": "二维码可扫性检查",
            "status": "skip",
            "message": "未安装 pyzbar 库，跳过自动检查。请用手机手动扫描二维码确认可扫。安装命令：pip install pyzbar",
        }

    if qr_region:
        x1, y1, x2, y2 = qr_region
        crop = img.crop((x1, y1, x2, y2))
    else:
        crop = img

    results = decode(crop)

    if len(results) > 0:
        status = "pass"
        message = f"二维码可扫（检测到 {len(results)} 个码）"
        data = [r.data.decode("utf-8", errors="replace") for r in results]
    else:
        status = "fail"
        message = "二维码无法识别，请检查二维码是否清晰、是否有遮挡、尺寸是否足够"
        data = []

    return {
        "check": "二维码可扫性检查",
        "status": status,
        "message": message,
        "qr_data": data,
    }


def check_text_clarity(img):
    """
    文字清晰度提示（无法自动检查文字内容，给出提示）
    """
    return {
        "check": "文字准确性提示",
        "status": "info",
        "message": "请手动确认：1) 俱乐部名称、期数、主题、时间、地址完全正确；2) 工作坊题目和讲师身份无误；3) 无错别字、无乱码、无重复生成文字。",
    }


def verify_brand(poster_path, logo_region=None, qr_region=None, output_path=None):
    """
    执行品牌合规检查

    参数:
        poster_path: 海报路径
        logo_region: logo区域 (x1,y1,x2,y2)，可选
        qr_region: 二维码区域 (x1,y1,x2,y2)，可选
        output_path: 检查报告输出路径，可选

    返回:
        检查结果字典
    """
    if not os.path.exists(poster_path):
        return {"error": f"文件不存在: {poster_path}"}

    img = Image.open(poster_path).convert("RGB")
    W, H = img.size

    results = {
        "poster": poster_path,
        "size": f"{W}x{H}",
        "checks": [],
        "summary": {"pass": 0, "warning": 0, "fail": 0, "skip": 0, "info": 0},
    }

    # 执行各项检查
    checks = [
        check_main_color(img),
        check_accent_color(img),
        check_logo_size(logo_region),
        check_qr_readable(img, qr_region),
        check_text_clarity(img),
    ]

    for check in checks:
        results["checks"].append(check)
        status = check["status"]
        if status in results["summary"]:
            results["summary"][status] += 1

    # 总体结论
    if results["summary"]["fail"] > 0:
        results["overall"] = "fail"
        results["overall_message"] = "存在未通过项，请修复后重新检查"
    elif results["summary"]["warning"] > 0:
        results["overall"] = "warning"
        results["overall_message"] = "基本合规，但有警告项，建议优化"
    else:
        results["overall"] = "pass"
        results["overall_message"] = "品牌合规检查通过"

    # 输出报告
    report = format_report(results)

    if output_path:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"检查报告已保存: {output_path}")

    print(report)

    return results


def format_report(results):
    """格式化检查报告为可读文本"""
    lines = []
    lines.append("=" * 60)
    lines.append("头马海报品牌合规检查报告")
    lines.append("=" * 60)
    lines.append(f"海报: {results['poster']}")
    lines.append(f"尺寸: {results['size']}")
    lines.append("")

    status_icon = {
        "pass": "✅",
        "warning": "⚠️",
        "fail": "❌",
        "skip": "⏭️",
        "info": "ℹ️",
    }

    for check in results["checks"]:
        icon = status_icon.get(check["status"], "?")
        lines.append(f"{icon} {check['check']}")
        lines.append(f"   {check['message']}")
        lines.append("")

    lines.append("-" * 60)
    lines.append(f"统计: ✅通过 {results['summary']['pass']} | ⚠️警告 {results['summary']['warning']} | ❌失败 {results['summary']['fail']} | ⏭️跳过 {results['summary']['skip']} | ℹ️提示 {results['summary']['info']}")
    lines.append("")

    overall_icon = status_icon.get(results["overall"], "?")
    lines.append(f"{overall_icon} 总体结论: {results['overall_message']}")
    lines.append("=" * 60)

    return "\n".join(lines)


def parse_region(s):
    """解析区域字符串 'x1,y1,x2,y2' 为元组"""
    if s is None:
        return None
    parts = list(map(int, s.split(",")))
    if len(parts) != 4:
        raise ValueError("区域格式应为 'x1,y1,x2,y2'")
    return tuple(parts)


def main():
    parser = argparse.ArgumentParser(description="头马海报品牌合规检查脚本")
    parser.add_argument("--poster", required=True, help="海报路径")
    parser.add_argument("--logo-region", default=None, help="logo区域，格式'x1,y1,x2,y2'")
    parser.add_argument("--qr-region", default=None, help="二维码区域，格式'x1,y1,x2,y2'")
    parser.add_argument("--output", default=None, help="检查报告输出路径")

    args = parser.parse_args()

    logo_region = parse_region(args.logo_region)
    qr_region = parse_region(args.qr_region)

    verify_brand(
        poster_path=args.poster,
        logo_region=logo_region,
        qr_region=qr_region,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()