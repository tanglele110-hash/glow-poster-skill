---
name: glow-poster
description: 制作新中式中秋祝福、问候光影海报。直接说「生成一张中秋祝福海报」即可，生肖可选；支持经典中秋意象、十二生肖、诗句、配色、花窗及环绕竖排自由组合。Create Mid-Autumn greeting posters from a simple request, with optional zodiac subjects, classic festival motifs, poems, colors, window shapes and surrounding vertical typography.
---

# 中秋光影问候海报 / Mid-Autumn Glow Poster

以雾面纸感、暖色花窗光斑和半透明投影构成主体。标题默认「中秋佳節」，文案采用繁体诗句及完整出处。配色、诗句、窗形和场景可独立选择。
Build a matte-paper poster around a warm luminous aperture and translucent shadows. Default to traditional Chinese copy and preserve the complete attribution.

## 请求入口 / Request routing

- 「生成一张中秋祝福海报」「做一张中秋问候海报」即为完整的制作请求，生肖不是必填项。没有指定生肖时进入经典中秋意象模式，不追问生肖、不随机推定用户生肖，也不自动沿用上一张的生肖。
  A plain Mid-Autumn greeting poster request is sufficient. Without an explicit zodiac, use classic festival motifs; do not ask for, infer, or inherit a zodiac from a previous poster.
- 经典模式从八组窗影意象随机选择：玉兔・桂枝、嫦娥・桂树、蟾蜍・月轮、月饼・茶盏、灯笼・桂影、桂酒壶・桂花瓣、莲瓣瓜・供盘、诗卷・月光。玉兔、蟾蜍在此是节日意象，不代表用户生肖。未指定的诗句、传统色、窗形也独立随机抽取；不设固定组合。
  Randomly choose a classic festival motif and independently sample each unspecified poem, palette and aperture. A rabbit or toad in classic mode is festival imagery, not the user's zodiac.
- 只有明确提供生肖，或明确要求沿用同一生肖时，才进入生肖模式。指定某种经典意象则固定该意象，其余未指定选项继续随机。两种模式共用署名询问、繁体文案和竖排版式规则。
  Use zodiac mode only for an explicit zodiac or an explicit request to reuse it. Preserve a requested classic motif while randomizing other unspecified axes. Both modes share signature intake and typography rules.

## 开始前询问署名 / Signature intake

每次开始新的海报制作任务，若本任务尚未提供署名名称或明确选择不署名，先问：「这张海报要加署名吗？提供名称即可，右下角会竖排『名称＋遙祝』；也可以不署名。」等待明确选择后再生图；等待时可读取目录、准备随机组合。用户已给名称或已明确不署名，直接沿用该选择；同一任务的改图、换生肖和批量变体不重复问。
At the start of a new poster task, ask whether a signature is wanted unless the user has already supplied a name or declined it. Wait for that choice before generation; catalog reading and random planning may continue. Reuse an explicit choice within the same task.

- 名称由用户提供，不随机、不从参考图、示例或历史产物里推定；「乐乐」是示例，不是默认名称。遵循本任务简繁选择，默认繁体显示例为「樂樂遙祝」；用户要求保留名称原字形时优先原样保留。脚本只接收最终显示名称，原样保留名称并追加「遙祝」，不猜测专名的繁简转换。
  Never infer a name from examples or reference images. Honor the chosen script and any explicit name spelling. Pass the final display name to the planner; it appends 遙祝 without converting proper names.
- 署名在右下角小字竖排，自上而下；不加印章、额外祝词或把署名混入诗词出处。选择不署名时保留该处留白。
  Use a small upright lower-right column, separate from the poem attribution. Leave it empty when declined.

## 素材选择 / Content selection

阅读 [素材目录](references/catalog.md)；[catalog.json](references/catalog.json) 是内容数据源，包含 20 组诗句、6 色、5 窗形、8 组经典意象、十二生肖及 8 组生肖配景。
Read the catalog for stable IDs, quotations, sources and visual descriptions.

- 不设默认内容组合。每次对未指定的诗句、配色、窗形、经典意象或生肖配景随机抽取，一次一张；明确指定的选项固定。生肖只根据输入选择，不随机改变身份。推荐配对不用于自动锁定其他轴。
  Preserve explicit selections and randomize every unspecified content axis on each run. There is no default content preset.
- 输入生肖时使用 `--zodiac`（中文、繁体、英文或 z01–z12），配景用 `--accent`；未指定生肖时省略 `--zodiac` 和 `--accent`，经典意象会随机选择，仅在用户指定意象时传 `--motif`。生肖是窗内唯一动物主角，不混入参考图里的其他动物。
  Zodiac mode uses one chosen animal with an accompaniment; classic motif mode remains separate.
- 新增诗句须核对字句、作者、篇名并记录来源。保持同一版本；区分中秋诗与借用的咏月、秋景诗。
  Verify new quotations and do not combine textual variants or mislabel their subject.

## 版式选择 / Layout selection

- `horizontal`：顶部标题与英文、中央窗影、底部诗句与出处；可用本地脚本精确排字。
  Horizontal layout supports deterministic typesetting with bundled fonts.
- `vertical`：右上竖排标题、左侧诗句由右向左分列、左下小字出处，英文沿外侧弱化；为主体留出完整透光区域。详见 [版式说明](references/layout.md)。
  Vertical layout surrounds the central artwork with upright Chinese columns and a subordinate English line.
- 按请求选择版式；未指定时使用 vertical 默认值；horizontal 为备用版式。竖排目前采用完整图像生成流程，字体是视觉参考；需要精确字体文件排印时应明确说明能力边界，不能声称图片模型已嵌入指定字体。
  Vertical mode currently uses full-image generation. Do not claim exact font-file rendering from an image model.

## 规划与制作 / Planning and production

1. 使用 Python 3.10 或更新版本。仅运行 plan.py 不需要第三方包；运行横排排字或 verify.py 时检查 `PIL`、`numpy`、`fontTools`，缺包时在包外隔离环境按 requirements.txt 安装。脚本路径基于实际 Skill 目录，生成物放在包外。
   Resolve package paths independently of the working directory; keep outputs outside the Skill.
2. 创建计划，指定所需组合与版式：

   ```text
   python scripts/plan.py --no-signature --out-dir <output-dir>
   python scripts/plan.py --signature "樂樂" --out-dir <output-dir>
   python scripts/plan.py --zodiac 龙 --signature "樂樂" --layout vertical --out-dir <output-dir>
   python scripts/plan.py --zodiac 鼠 --no-signature --out-dir <output-dir>
   python scripts/plan.py --poem p07 --color c01 --window w02 --motif m01 --no-signature --layout horizontal --out-dir <output-dir>
   python scripts/plan.py --poem p01 --no-signature --count 4 --seed 42 --out-dir <batch-output-dir>
   ```

   未指定种子时每次产生新随机种子，并写入 plan.json；`--seed` 可复现同样选择，只影响未指定的内容轴。单个随机结果可能重复，批量结果去重；不要把随机说成永不重复。`--title-font kaiti` 选择楷体备用。脚本只规划，不调用图像服务。
   Planning preserves explicit choices, records a reproducible random seed and does not itself generate images.

   正式生成计划必须传入 `--signature "最终显示名称"` 或 `--no-signature`，不能用缺省参数代替询问。只传名称、不重复写「遙祝」。署名与选择状态写入 plan.json，完整署名进入 prompt.txt 和 text.json／compose.json；署名不改变随机种子和内容组合。
   Supply either the confirmed display name or an explicit no-signature choice. The plan and text manifest record it without changing random content selection.
3. 读取 [图像生成说明](references/background-prompts.md)，查看所需参考图，使用宿主实际开放的图片工具。只要求选单或优化 Skill 时不生成图片。
   Use the host's available image tool only when image production is requested.
4. 横排：生成无字背景，检查物象后把真实背景路径写入 compose.json，再运行 `python assets/compose.py <output-dir>/compose.json`。竖排：prompt.txt 已包含完整文案和竖排要求，配合 text.json 核对整张生成图；不要调用横排脚本。
   Horizontal plans produce a background prompt and composition config. Vertical plans produce a complete-poster prompt and text manifest.
5. 交付真实 PNG 并核对字句、作者、尺寸、物象、窗形、留白与可读性。横排同时检查 .layout.json；图片模型文字须逐字目检。记录实际尺寸，不把近似比例标作精确比例。
   Inspect actual output rather than treating a prompt, plan or automatic pass as a finished poster.
   有署名时另核对姓名、完整「遙祝」、右下竖排、字号与主体避让；无署名时检查未从参考图带入他人姓名。Confirm exact signature copy and lower-right placement, or its complete absence when declined.

## 字体与色彩 / Type and color

- 标题默认随包齐伋体 `qiji.ttf`；诗句、出处及英文默认蒹葭楷，缺字由芫荽补足。楷体为可选标题预设；可用 `fonts.title` 指定本地字体路径。尊重明确的简繁体与字体选择，缺字不擅自改写。
  Qiji is the default title face; ChienChia and Iansui cover other text. Honor explicit script and font choices.
- 六色以 catalog.json 的 HEX / RGB 为准，`poster_hex = hex`；色名只是描述性标签。不自动加深或换色；局部光影与颗粒可产生自然明暗。图像模型不保证逐像素色准。
  Numeric color values are authoritative. Lighting may vary locally without changing the selected base color.

## 光影与检查 / Light and verification

默认画布 1376×1824（43:57）；`--canvas 1440 1920` 可选精确 3:4。中央光斑约 x=20–80%、y=30–73%；横排保留上下文字区，竖排保留两侧文字区。花窗只取柔光外轮廓，窗内物象为半透明柔影（soft diffused shadow），避免实体窗框、剪纸式黑影及写实摆件。
Use a single luminous aperture, softly diffused shadows and layout-specific text margins.

保持完整文案及出处，不增加无关标签、宣传语或装饰小字。保留缺字、越界、文字碰撞与对比度检查；失败时修正受影响的配置或图像。配色不可为通过检查而擅自改变。
Keep the full copy and enforce glyph, boundary, collision and readability checks without silently changing the selected palette.

维护脚本后运行 `python scripts/verify.py --out-dir <verification-dir>`。计划覆盖、排版测试和实际图像目检是不同证据；不得由参数组合数量推称所有海报已生成或验收。字体授权与素材出处见 [sources.md](references/sources.md)。
Run the package verifier after code changes and distinguish plan checks from visual validation. See sources for font licenses and content provenance.
