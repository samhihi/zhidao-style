---
name: zhidao-style
description: 按「知到 ZhiDao」设计系统产出物料——纸感编辑部风 HTML 文档、深色科技风演讲 PPT，或把这套设计语法迁移到新品牌。当用户说"知到风 / 知到风格 / 用知到的设计系统 / zhidao style"，或要做与知到 PRD / 配套分享 PPT 同款视觉的交付物时使用。
---

> 正本：本仓库（知到 DS v1.1）。规范资产随 skill 同目录分发，下表路径均相对本文件。安装：`npx zhidao-style` 一键装（自动检测两类目录），或手动把整个仓库目录拷为 `~/.claude/skills/zhidao-style/`（Claude Code）或 `~/.agents/skills/zhidao-style/`（Codex 及其他兼容 SKILL.md 开放标准的 agent）——升级即整目录覆盖（重跑 `npx zhidao-style@latest` 或 `git pull`）。

# 知到风 · 设计系统应用

## 规范资产（唯一事实源，路径相对本 skill 目录）

| 文件 | 内容 |
|---|---|
| `design-system.md` | 总纲：品牌 DNA、六原则、版式/母题/文案速查、迁移指南、设计债定版、修订记录 |
| `tokens.css` | Web token：三色彩面 + 语义层 + 交互状态最小集 + 间距/圆角刻度 + 跨面禁忌 |
| `zd-components.css` | 组件几何 + 断点 + print（从 PRD 源码抽出，只引用语义 token） |
| `tokens_deck.py` | python-pptx 常量库+函数：色板/字号/EMU 级几何 + `add_veil()`/`add_header()`/`add_conclusion_bar()`/`assert_fonts_installed()`/`set_font()` |
| `check_contrast.py` | WCAG 对比度计算——改任何色值必跑 |
| `reference/` | 五分册：color / typography / layout-components / motifs / voice-ia（精确值+证据页码+do/don't） |
| `index.html` | 导读页（浏览器打开）：设计系统的活样板——五段式骨架、组件用法、三色彩面 token 样本，做新 HTML 时可直接参考其 markup |

本 skill 派生自上表资产（知到 DS **v1.1**），数字权威分工：**对比度归 color.md，几何归 token 文件**——本页只写结论不复述数字，数值以权威册为准，不要凭印象改数。**先读总纲，再按需读分册**（做 deck 读 layout-components + motifs；写文案读 voice-ia；配色纠结读 color）。若资产文件缺失（安装不完整），如实告知用户，别凭记忆复现规范。

## 任务一：知到风 HTML 文档

1. 把 `tokens.css` + `zd-components.css` 一起拷进目标项目并 `<link>`（组件几何/断点/print 已在后者，别从分册散文重新翻译）；自写样式只引用语义层（`--text-1`/`--brand`/`--bg-1`…），不写裸 hex
2. 骨架五段式：sticky 顶栏+2px 进度条 → hero（暖黑底+双径向氛围光）→ metastrip 四格元信息带 → 双栏 shell（1160px 版心 = 236px 侧目录 + 54px gap + 正文）→ footer
3. 深色嵌入块（代码窗/SVG 示意图）挂 `data-mode="ink"`
4. 系统信息（编号/眉题/徽章/表头/元数据）走 mono 标签语法：JetBrains Mono + 大写 + 宽字距（字号越小字距越大，.04em→.22em）；列表符用菱形（6px 方块 rotate 45°）
5. 焦点环 `:focus-visible`、hover/disabled、`prefers-reduced-motion` 兜底的样板都已含在 tokens.css——直接用，别即兴发挥
6. QA 三层（无头截图实测可用，视觉核对不再纯人工）：
   - ① agent 静态自查 5 条：琥珀文字必用深档 `#7D5A0D`／`--mute` 只做 11–12px 元信息／无裸 hex、全走语义 token／深色嵌入块挂了 `data-mode`／列表符是菱形
   - ② 无头截图 + 新鲜眼睛 subagent 审图（subagent 是 Claude Code 机制；Codex 等无子代理的 agent 由主 agent 自己读图核对，或交人工）。Windows/Edge 示例（macOS/Linux 用 Chrome/Chromium 同参数）：`& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --virtual-time-budget=8000 --screenshot=out.png --window-size=1440,6400 "file:///…/页面.html"`。三个坑：布局视口有 ~461px 最小宽，直接开窄窗会得「右缘切字」假象——测真窄屏用外壳页嵌 `<iframe style="width:400px">`；不加 `--virtual-time-budget` 会撞上 150ms 过渡半程（假对比度问题）；截图只覆盖 window-size 视口，长页给足高度否则尾部「缺失」是假象。审图报的缺陷先对源制品原片核对——原片如此的是忠实还原（如 6px 菱形符看似圆点、陶土编号、弱氛围光），不是 bug
   - ③ 最终视觉把关仍是**人工**——请用户打开确认，别替用户签收

## 任务二：知到风 deck（python-pptx）

1. 把 `tokens_deck.py` 拷到生成脚本旁，`from tokens_deck import *`；画布 `SLIDE_W×SLIDE_H`（SLIDE_W=12192000，真 16:9；`SLIDE_W_LEGACY` 只在改旧片时用）；开工先跑 `assert_fonts_installed()`——缺思源黑体显式报错，绝不静默落雅黑
2. 每页三层三明治：全幅底图 → 压暗渐变纱一律调 `add_veil()`（含 alpha 的三停渐变已封装，α 随插画亮度调；别再手糊渐变）→ 原生文字层。底图按降级链走：①有生图工具→按 motifs 分册 §3.2/3.3 模板生成（2048×1152，同时产出一句 alt 文案）；②用户供图→校验 2048×1152 与暗部占比；③都没有→`BG_DEEP` 纯底 + `add_veil()` + 四角光斑，同样是合规知到风
3. 内容页页眉三件套调 `add_header(slide, title, chapter, section)`，别逐页手放；结论条（绿框体例，金框专属金句）用 `add_conclusion_bar()`
4. 版式从总纲第三节的 15 原型（L1–L15）里选，不发明新版式；要改文案的内容用 L13 原生表格，别烘焙进图；金句字号分档：框体 `SZ_QUOTE_BOX` / 裸排 `SZ_QUOTE_BARE`
5. **文字一律 `set_font()`**——latin/ea/cs 三槽齐设思源黑体，漏槽会中英文各走各的字体
6. QA：PowerPoint COM 渲染成图逐页自检（`Presentations.Open` → `.Export(dir,"PNG",1920,1080)`；需装有 PowerPoint 的 Windows，没有就如实降级为人工核对）；文字压暗有硬判据——文字框投影区在渲染图上平均亮度 L>60/255 即判失败、重调纱（PIL 可算；原片 S38 属违例勿仿）；另查金焦点是否唯一、页眉三件套是否恒定

## 任务三：迁移到新品牌（迁语法不迁颜色）

只改 `tokens.css`/`tokens_deck.py` 顶部原始色板层（主色可换任意色相、插画主体随项目换），语义层与规则不动。身份是语法不是色相：中性压场→主色立骨→暖色点睛的用量比、密度反比律、mono 标签语法、暗部 ≥60%。换色后必跑 `py check_contrast.py --audit`（在 skill 目录内；macOS/Linux 用 `python3`），不达标不上线；主色撞上现有色彩修辞（如换蓝紫系与「蓝=外部引用」冲突）时的处置见总纲第七节迁移指南。

## 硬规则速记（违反即不是知到风）

- **金色即结论**：每页一个金色焦点；亮金 `FFC000` 只留收尾强调页
- **描边语义靠颜色**（中性/品牌绿/金各司其职），粗细只是制作规格三档：中性 1.0pt / 品牌绿 1.2pt / 金句 1.4pt——观众看不出 0.1pt 差，语义别压在粗细上
- **灰阶纪律**：deck 文字灰阶只有 `E6EDF3`/`8A97A3` 两档，别自创中间档；✗/负向分治：浅面用 clay 暖红系，深面只压灰不发彩
- **跨面禁忌**：浅面松绿别上深底、深面灰别上纸底、琥珀别当浅底文字——对比度全不达标，具体比值以 color.md 为准；`#00B050` 禁用（色板漂移）
- **版式与页眉收口**：只从 15 原型（L1–L15）里选；绿竖条 39/41，完整三件套是内容页体例（约 32 页），章封面用加高竖条+章名+进度语变体，S1/S2/S41 破格——别给破格页硬挂面包屑
- **密度反比律**：字越多图越退（表格页四角光斑），字越少图越进（金句页全幅）
- **秩序与氛围不混**：编号/表格/分隔线从不发光，插画/辉光从不承载信息
