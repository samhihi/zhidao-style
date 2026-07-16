# -*- coding: utf-8 -*-
"""知到 DS v1.1 · 2026-07-14 · 修订记录见 design-system.md

WCAG 2.1 对比度计算器(评审 #6/#14 的再生程序:换任何色值,先跑这里再上屏)。

用法:
  py check_contrast.py "#前景" "#背景"    # 输出比值与 AA/AAA 判定
  py check_contrast.py --audit           # 跑内置色板全部关键配对(三色彩面)

阈值口径(与总纲/SKILL 一致):正文 4.5 / 大字·图形 3.0 / 深底强调建议 7.0。
WCAG 大字线只认 ≥24px regular / ≥18.66px bold——11–12px 元信息没有豁免。
对比度数字的权威所在册是 reference/color.md;本脚本负责算,color.md 负责记账。
"""
import sys

# ---------------------------------------------------------------- 计算核心

def _hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError("色值须为 #RGB 或 #RRGGBB: %r" % h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _linear(c8):
    c = c8 / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexcolor):
    """WCAG 2.1 相对亮度。"""
    r, g, b = (_linear(c) for c in _hex_to_rgb(hexcolor))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    """WCAG 2.1 对比度 (L1+0.05)/(L2+0.05),与前景/背景顺序无关。"""
    l1, l2 = luminance(fg), luminance(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


# ---------------------------------------------------------------- 单对模式

def report_pair(fg, bg):
    r = contrast(fg, bg)
    print("前景 %s on 背景 %s" % (fg, bg))
    print("对比度 = %.2f:1" % r)
    print("  AA  正文(4.5) : %s" % ("PASS ✓" if r >= 4.5 else "FAIL ✗"))
    print("  AA  大字(3.0) : %s" % ("PASS ✓" if r >= 3.0 else "FAIL ✗"))
    print("  AAA 正文(7.0) : %s" % ("PASS ✓" if r >= 7.0 else "FAIL ✗"))
    print("  AAA 大字(4.5) : %s" % ("PASS ✓" if r >= 4.5 else "FAIL ✗"))
    return 0 if r >= 4.5 else 1


# ---------------------------------------------------------------- 审计模式
# 角色 → 阈值。「大字」兼图形/描边(WCAG 1.4.11 同为 3.0)。
ROLES = {"正文": 4.5, "大字": 3.0, "深底强调": 7.0}

# 色板(与 tokens.css v1.1 同步;改 token 必改这里)
PAPER = "#F5F3EC"; SURFACE = "#FBFAF5"; INK = "#181A1F"
DEEP_ABYSS = "#03070E"; DEEP_BG = "#06111A"; DEEP_PANEL = "#142028"; DEEP_PANEL2 = "#1B2735"

# (面, 前景hex, 背景hex, 角色, 说明)
MUST_PASS = [
    # ---- ① 纸感浅色面(基准 paper #F5F3EC,最不利面) ----
    ("纸", "#181A1F", PAPER, "正文", "ink 主文字"),
    ("纸", "#565851", PAPER, "正文", "graphite 次级文字"),
    ("纸", "#6E706A", PAPER, "正文", "mute 弱化字 v1.1 定版(11-12px 元信息)"),
    ("纸", "#1E5A44", PAPER, "正文", "pine 品牌绿作字"),
    ("纸", "#3E7A5C", PAPER, "正文", "moss 次级绿作字(压线,别再调亮)"),
    ("纸", "#B5532F", PAPER, "大字", "clay 负向(正文 4.46 差 0.04,限加粗/大字)"),
    ("纸", "#7D5A0D", PAPER, "正文", "amber-text 琥珀文字档 v1.1 定版"),
    ("纸", "#7D5A0D", "#F6ECCF", "正文", "amber-text on amber-soft(chip 场景)"),
    ("纸", "#FFFFFF", "#1E5A44", "正文", "on-solid 反白 / pine 实底"),
    ("纸", "#FFFFFF", "#3E7A5C", "正文", "on-solid 反白 / moss 实底(P1)"),
    ("纸", "#FFFFFF", "#B5532F", "正文", "on-solid 反白 / clay 实底(P0)"),
    # ---- ② 暖深面 ink(HTML 深色嵌入块,底 #181A1F) ----
    ("暖深", "#EFEDE6", INK, "正文", "text-1 暖白"),
    ("暖深", "#C7C9C0", INK, "正文", "text-2 导语"),
    ("暖深", "#9A9D95", INK, "正文", "text-3 元信息"),
    ("暖深", "#7E8479", INK, "正文", "comment 注释灰绿(压线设计)"),
    ("暖深", "#6FBF95", INK, "深底强调", "brand 薄荷绿"),
    ("暖深", "#C9A86A", INK, "深底强调", "warm-text 沙金 v1.1 补覆写"),
    ("暖深", "#7FB7E8", INK, "深底强调", "info 代码键名蓝"),
    ("暖深", "#E2A4A4", INK, "深底强调", "negative 玫瑰"),
    ("暖深", "#C8932E", INK, "正文", "amber 原档直用(eyebrow/回环)"),
    ("暖深", "#BFE3CF", "#1E5A44", "正文", "brand-2 雾绿 / pine 核心节点"),
    # ---- ③ 冷深面 deep(演讲/深色科技风) ----
    ("冷深", "#E6EDF3", DEEP_ABYSS, "正文", "text-1 / 渐变最深端"),
    ("冷深", "#E6EDF3", DEEP_BG, "正文", "text-1 / 页底"),
    ("冷深", "#E6EDF3", DEEP_PANEL, "正文", "text-1 / 面板"),
    ("冷深", "#8A97A3", DEEP_BG, "正文", "text-2 压灰 / 页底"),
    ("冷深", "#8A97A3", DEEP_PANEL, "正文", "text-2 压灰 / 面板"),
    ("冷深", "#16C79A", DEEP_ABYSS, "深底强调", "brand 青绿 / 渐变最深端"),
    ("冷深", "#16C79A", DEEP_PANEL, "深底强调", "brand 青绿 / 面板"),
    ("冷深", "#16C79A", DEEP_PANEL2, "正文", "brand 青绿 / 高亮行(6.97,不足 7 建议档)"),
    ("冷深", "#E0B84A", DEEP_ABYSS, "深底强调", "warm 暖金 / 渐变最深端"),
    ("冷深", "#E0B84A", DEEP_PANEL, "深底强调", "warm 暖金 / 面板"),
    ("冷深", "#FFC000", DEEP_PANEL, "深底强调", "warm-hot 亮金(临门一脚)"),
    ("冷深", "#E2A4A4", DEEP_ABYSS, "深底强调", "negative 玫瑰 v1.1 定版 / 最深端"),
    ("冷深", "#E2A4A4", DEEP_PANEL, "深底强调", "negative 玫瑰 v1.1 定版 / 面板"),
    ("冷深", "#0C1418", "#16C79A", "正文", "on-solid 反深字 / 青绿表头"),
    ("冷深", "#0C1418", "#E0B84A", "正文", "on-solid 反深字 / 暖金表头"),
    ("冷深", "#FF5F56", DEEP_PANEL, "大字", "dot-red 终端红点(组件色,非文字)"),
]

# 跨面禁忌与考古值:应当不达标,证明「为什么禁」(color.md §4.4;失败不计入退出码)
EXPECT_FAIL = [
    ("跨面", "#1E5A44", DEEP_ABYSS, "正文", "浅面 pine 上冷深底(2.50) → 换 #16C79A/#6FBF95"),
    ("跨面", "#16C79A", PAPER, "正文", "冷深 brand 上纸底(1.96 归此对) → 换 pine"),
    ("跨面", "#E0B84A", PAPER, "正文", "冷深 warm 上纸底 → 换 --amber-text"),
    ("跨面", "#8A97A3", PAPER, "正文", "冷深 text-2 上纸底(2.69) → 换 graphite"),
    ("跨面", "#C8932E", PAPER, "正文", "amber 原档上纸底作字(2.47;卡底 surface 2.62) → 换 --amber-text"),
    ("考古", "#8A8C82", PAPER, "正文", "v1.0 mute 原值(3.07) → v1.1 加深为 #6E706A"),
    ("考古", "#946A10", PAPER, "正文", "v1.0 amber-text 原值(4.37) → v1.1 定版 #7D5A0D"),
    ("漂移", "#00B050", "#16C79A", "大字", "Office 标准绿混入,与品牌青绿几乎不可辨 → 禁用"),
]


def _fmt_row(face, fg, bg, role, ratio, ok, note):
    mark = "✓" if ok else "✗"
    return "%-4s %-9s on %-9s %-6s ≥%.1f  %6.2f:1  %s  %s" % (
        face, fg, bg, role, ROLES[role], ratio, mark, note)


def audit():
    fails = 0
    print("知到色板对比度审计(WCAG 2.1;阈值 正文 4.5 / 大字·图形 3.0 / 深底强调 7.0)")
    print("=" * 86)
    print("一、须达标配对(任何一行 ✗ = 有 token 违规,退出码 1)")
    print("-" * 86)
    for face, fg, bg, role, note in MUST_PASS:
        r = contrast(fg, bg)
        ok = r >= ROLES[role]
        if not ok:
            fails += 1
        print(_fmt_row(face, fg, bg, role, r, ok, note))
    print("-" * 86)
    print("二、跨面禁忌 / 考古值(应当 ✗——这就是禁用它们的理由,不计入退出码)")
    print("-" * 86)
    for face, fg, bg, role, note in EXPECT_FAIL:
        r = contrast(fg, bg)
        ok = r >= ROLES[role]
        print(_fmt_row(face, fg, bg, role, r, ok, note))
    print("=" * 86)
    if fails:
        print("结果:%d 对须达标配对不达标 ✗ —— 调色值,别调阈值。" % fails)
        return 1
    print("结果:须达标配对全部通过 ✓")
    return 0


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # Windows 控制台防乱码
    except Exception:
        pass
    if len(argv) == 2 and argv[1] == "--audit":
        return audit()
    if len(argv) == 3:
        return report_pair(argv[1], argv[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
