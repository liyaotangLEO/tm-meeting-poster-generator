# 头马例会海报生成器 (tm-meeting-poster-generator)

头马俱乐部例会宣传海报生成器，符合头马品牌规范（5O法则），支持常规例会和大咖工作坊两种模式，默认 3:4 竖版。

## 功能特性

- ✅ **品牌合规**：严格遵循头马 5O 法则（颜色/Logo/字体/图片/信息）
- ✅ **双模式支持**：常规例会 + 大咖工作坊（人像可选）
- ✅ **视觉元素主题驱动**：不使用固定模板元素，每期根据主题设计
- ✅ **版面结构预览**：生图前输出 ASCII 示意图跟用户确认
- ✅ **PIL 精确合成**：logo、二维码、底部文字像素级精确控制
- ✅ **品牌自动检查**：自动检查主色调、强调色、二维码可扫性
- ✅ **内置头马 logo**：官方彩色 logo 已内置，无需额外提供

## 环境依赖

| 依赖 | 说明 |
|------|------|
| Python 3.7+ | 运行合成脚本 |
| Pillow (PIL) | 图像处理库，`pip install Pillow` |
| pyzbar（可选） | 二维码自动解码检查，`pip install pyzbar` |

> 豆包工作环境默认已安装 Python 和 Pillow，可直接运行。

## 安装方法

### 方法一：一键安装（推荐，复制粘贴即可）

在 GitHub 仓库页面选中下面的指令并复制，然后粘贴到豆包工作 Agent 对话框中发送，Agent 会自动完成安装：

```
请安装 tm-meeting-poster-generator Skill：从 https://github.com/liyaotangLEO/tm-meeting-poster-generator 克隆到 ~/.agents/skills/ 目录，安装完成后告诉我。
```

Agent 收到后会自动执行：创建目录 → 克隆仓库 → 确认安装结果，全程无需手动操作。

### 方法二：下载 ZIP（适合新手）

1. 点击仓库右上角 **Code** → **Download ZIP**
2. 解压到本地 skill 目录：
   - Windows: `C:\Users\你的用户名\.agents\skills\`
   - macOS/Linux: `~/.agents/skills/`
3. 解压后目录结构：`~/.agents/skills/tm-meeting-poster-generator/`

### 方法三：Git Clone

```bash
git clone https://github.com/liyaotangLEO/tm-meeting-poster-generator.git ~/.agents/skills/tm-meeting-poster-generator
```

## 使用流程

### 6 步工作流

1. **需求收集与确认** — 收集例会信息，询问是否大咖工作坊、是否提供人像
2. **品牌规范预检** — 确认颜色/字体/logo规范
3. **视觉元素 + 版面结构方案确认** — 输出 2-3 套视觉方案 + ASCII 版面示意图，跟用户确认
4. **AI 生成背景主视觉** — 常规→image_gen；大咖+人像→image_edit；大咖+无人像→image_gen
5. **PIL 精确合成** — 贴 logo + 底部左右分栏排版 + 文字精确重写
6. **验证与交付** — 品牌合规检查 + 文字准确性 + 二维码可扫性

### 合成脚本使用

```bash
python scripts/compose_poster.py \
  --bg 背景图.png \
  --qr 二维码.png \
  --time "2026年8月26日 周二 19:30-21:30" \
  --address "深圳市南山区 金地威新中心A座4F·太湖会议室" \
  --output 最终海报.png
```

### 品牌检查脚本使用

```bash
python scripts/verify_brand.py --poster 最终海报.png
```

## 品牌规范

### 颜色

| 角色 | 颜色 | HEX |
|------|------|-----|
| 主色 | 栗红 | `#772432` |
| 主色 | 忠诚蓝 | `#004165` |
| 强调色 | 快乐黄 | `#F2DF74`（仅点缀，不宜大面积） |
| 中性色 | 白/黑/冷灰 | `#FFFFFF` / `#000000` / `#A9B2B1` |

> 栗红和忠诚蓝都是主色，不分主次，每期可选择其一或搭配使用。

### 字体

- 思源黑体 Noto Sans SC（免费商用）
- 中文推荐黑体、宋体、等线

### Logo

- 彩色原版，最小 72px（2cm）
- 周边留白 = 字标高度
- 禁止变形、特效、放在非标准色背景

## 目录结构

```
tm-meeting-poster-generator/
├── SKILL.md                          # 主入口
├── README.md                         # 本文件
├── .gitignore
├── references/
│   ├── brand-guidelines.md           # 头马品牌规范（5O法则）
│   ├── layout-spec.md                # 海报版式规范
│   ├── prompt-templates.md           # AI生图Prompt模板库
│   └── troubleshooting.md            # 常见问题与避坑指南
├── scripts/
│   ├── compose_poster.py             # PIL合成脚本
│   └── verify_brand.py               # 品牌合规检查脚本
├── assets/
│   ├── logo/
│   │   └── toastmasters-logo-color.png  # 内置头马官方彩色logo
│   └── README.md                     # 素材说明
└── examples/
    ├── talktime-444/                 # 第一期示例（常规例会）
    │   ├── final.png
    │   └── info.md
    └── mingyuan-388/                 # 第二期示例（大咖工作坊）
        ├── final.png
        └── info.md
```

## 用户需自行提供的素材

1. **VPM 微信二维码**（必填）— 清晰可扫，建议 ≥500×500px
2. **大咖人像素材**（可选）— 大咖工作坊模式下用户自选，不提供时用抽象视觉元素

## 示例海报

| 期数 | 俱乐部 | 主题 | 模式 |
|------|--------|------|------|
| 第444期 | Talktime头马国际演讲会 | 听见心底的声音 | 常规例会 |
| 第388期 | 明源云 AI Lab 头马演讲俱乐部 | 表达即思考 | 大咖工作坊（含人像） |

## 常见问题

**Q: 没有 Python 环境能用吗？**
A: 可以用 AI 直接生成完整海报（在 prompt 中详细描述 logo、二维码、底部排版），但 logo 和二维码可能不精确，建议后期手动贴二维码。

**Q: 大咖一定要提供人像吗？**
A: 不一定。用户可选择不提供，此时用抽象/象征性视觉元素（讲台、聚光灯、演讲稿等）代表大咖。

**Q: 可以用忠诚蓝作为主色吗？**
A: 可以。栗红和忠诚蓝都是头马主色，不分主次，根据主题和视觉方案选择。

## License

MIT

## 作者

Created by 耀棠 (Leo) — 头马 118 大区