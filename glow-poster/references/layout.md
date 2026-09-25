# 版式与配置 / Layout and configuration

默认环绕竖排，参考 assets/layout-reference.png；横排可显式选择。默认输出目标 1376×1824（43:57），可用 1440×1920 实现精确 3:4。参考图自身尺寸不作为最终输出尺寸。

## 环绕竖排 / Surrounding vertical layout

`--layout vertical` 生成完整海报提示与 text.json；compose.py 仅支持横排。

| 区域 | 建议位置与排法 |
|---|---|
| 主标题 | x=84–90%，y=9–43%；一列正立汉字，自上而下 |
| 英文 | x=92–95%；沿标题外侧转为竖向，字号弱于中文 |
| 诗句 | x=6–18%，y=39–66%；短句两列，由右向左 |
| 作者与篇名 | 左下 y=68–91%；另起小字竖列，保留完整出处 |
| 可选署名 | 右下 x=86–93%，y=75–93%；「名称＋遙祝」一列正立小字，自上而下，底部约 y=91% |
| 主体 | x=20–80%，y=30–73%；所有文字避让光斑 |

坐标是起始建议，须按实际字数和图像检查；长句可增加列数、调整起点与字距。默认繁体标题与诗句，保留所有字；不为填满画面增添无关内容。字号按可见字形与最终输出尺寸检查。
These are starting zones, not fixed coordinates for every poem. Adapt columns to content, preserving readable type and scene clearance.

署名小于诗句，用同系柔白楷体，避让光斑、标题与安全边界；无署名时留白。长名称按可读性调整字号或列数，不能删字；署名不替换诗词作者。参考图里的姓名不属于模板固定文字。
Optional signatures use smaller ivory-white calligraphy at lower right. Preserve the complete name and suffix, adapt long names without truncation, and never replace the poem attribution or copy names from references.

## 备用横排 / Optional horizontal layout

| 元素 | 可见字形位置／大小 |
|---|---|
| 中秋佳節标题 | 顶缘 0.080H；首选字号 0.105W |
| 英文副标题 | 顶缘 0.186H；首选字号 0.036W，字距约 0.014W |
| 窗影 | 光斑约 x=0.20–0.80W，y=0.30–0.73H |
| 诗句 | 顶缘 max(0.783H, 光斑下缘+0.038H)；首选字号 0.055W |
| 出处 | 诗句末行可见字形下缘+0.020H；首选字号 0.030W |

字号以真实字形包围框计算。文字最大宽 0.86W，底部可见字形不超过 0.925H。最长诗题可以在 0.030W–0.022W 范围缩排；正文可在 0.055W–0.042W 范围缩排，仍不合适时报错。诗句保留 1–2 行，不自动删字或省略出处。

### 横排光斑检测

背景缩略到 240 像素宽并轻度降噪。每一行左右边缘的亮度中位数作为该行背景基准，以高于基准 18 的连通亮区估计光斑，忽略孤立颗粒，并对边界增加羽化余量。没有可靠光斑、光斑进入文字区均报错。方法不能判断物象内容，仍需目检。

检测不可靠时，允许把目视实测的 `scene_bbox: [left, top, right, bottom]`（0–1）写入配置；它仍经过留白校验，报告明确标记 manual_measured。不得用任意小框规避实际碰撞。

### 横排配置

```json
{
  "layout": "horizontal",
  "background": "background.png",
  "output": "poster.png",
  "canvas": [1376, 1824],
  "title": "中秋佳節",
  "title_font": "qiji",
  "subtitle": "MID-AUTUMN FESTIVAL",
  "greeting": ["好時節，願得年年，", "常見中秋月。"],
  "attribution": "—— 明 · 徐有貞《中秋月·中秋月》"
}
```

相对路径以 config.json 所在目录为基准。输出必须位于 Skill 包外，默认拒绝覆盖已有图片，需覆盖时明确设置 `overwrite: true`。旧版 background/output/font/title/subtitle/greeting/attribution 字段仍支持。

可选 `font` 替换主字体；`fonts` 对象可分别指定 title/subtitle/greeting/attribution 的字体；`fallback_fonts` 数组可明确设置备用字体，空数组会禁用默认备用字体并在缺字时报错。默认标题字体为齐伋体；`title_font: "kaiti"` 可选运行环境中的楷体。标题以外主字体为蒹葭楷，缺字备用为芫荽。`fonts.title` 的显式路径优先于标题预设。缺字时逐字使用备用字体并记录字与字体，文字内容不变。简体请求应传完整覆盖简体的字体文件；不得把缺字方框当作正常输出。

输出包括 poster.png 和 poster.layout.json，后者记录像素尺寸、字形位置、字号、备用字体使用、光斑包围框与白字对比度。对比度下限仅为自动拦截严重不可读图片，不能代替正常观看尺寸的目检。背景已有文字或选错物象需在生图阶段返工。

可选 `signature` 是已拼好的完整署名（如「樂樂遙祝」），空字符串表示不署名；CLI `--signature` 只传名称，由 planner 追加后缀。横排海报仍将署名置于右下竖排，收窄底部诗句及出处宽度以避让；`fonts.signature` 可指定字体，缺字、过长或碰撞会明确报错，不省略署名。
The composition config accepts complete signature text; the CLI accepts the name only. Horizontal posters also place it vertically at lower right, with font coverage, fit and collision checks.

## 标题字体 / Title fonts

- `qiji`：齐伋体 0.0.4，随包提供，默认选项。默认使用繁体标题「中秋佳節」，直接使用 U+7BC0「節」。
- `kaiti`：可选本地楷体，Windows 从 Fonts/simkai.ttf 读取；字体不随包分发。其他平台可用 `fonts.title` 指定已安装的楷体。
- 只切换标题字体；英文、诗句、出处和背景使用现有设置。
Qiji is bundled as the default title face. KaiTi is a selectable local alternative; explicit fonts.title paths override presets. Glyph coverage and layout are measured for the selected font.


