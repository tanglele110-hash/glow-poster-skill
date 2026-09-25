# 图像生成 / Image generation

scripts/plan.py 的 `--layout` 决定 prompt.txt 是无字背景提示还是完整竖排海报提示。所有文案来自目录，按选择生成，不依赖已有对话或某张生肖示例。
The selected layout determines whether the prompt describes a text-free background or a complete vertical poster.

## 参考图 / References

- style-reference.png 仅用于雾面颗粒、暖米色光斑、半透明柔影。
- layout-reference.png 用于默认竖排比例和层级，不继承图内文案或物象。备用横排只读取无字风格图，依据横排布局说明排字。
- 所有参考路径由包目录解析；先查看图片，再按宿主图片工具支持的机制传入。不要假定某个工具名在所有宿主存在。

Inspect only the references listed in the plan. Reference content must not override the selected poem, palette, window or scene.
署名仅取自已确认的输入，参考图中的姓名必须移除。未决定是否署名时先按 SKILL.md 询问，不直接生图。
Use only the confirmed signature input, never reference-image names. Complete signature intake before image generation.

## 视觉约束 / Visual constraints

只画所选窗形及场景，替换参考图中的旧物象。阴影为 soft diffused shadow, semi-transparent, feathered edges，保持透光空间。窗形是光的外轮廓，不是实体窗框或剪纸。生肖识别特征取自目录；不能让其他动物或人物混入。
Keep selected subjects readable as translucent projected shadows, with a single luminous aperture.

采用目录 HEX，保持整体色相和明度。不要通过加深底色解决白字问题；可读性失败需明确处理。中央光斑约 x=20–80%、y=30–73%，文字位置按所选版式留白。
Preserve the numeric base color while allowing subtle grain and light. Keep text clear of the central scene.

## 横排 / Horizontal

生成无字背景后，检查色彩、窗形、物象；把真实背景路径写入 compose.json，用 compose.py 排字。该脚本读取真实字体，输出 PNG 与布局报告。
Generate a text-free background, then compose exact type locally and review the layout report.

## 竖排 / Vertical

直接以 prompt.txt 生成整张含字海报，以 text.json 核对原文。标题在右上，诗句在左侧由右向左分列、各列自上而下；作者与篇名在左下小字竖排，英文置外侧弱化。中文保持正立，标点采用竖排位置，篇名可用竖排书名号。
Generate the complete poster and compare all text with the manifest. Chinese glyphs stay upright; columns read from right to left, top to bottom.
有署名时在右下 x=86–93%、y=75–93% 留出小字竖排区，完整呈现 text.json 的 signature 字段；否则保持留白。有署名时「右下留白」指署名周围的呼吸空间，不能据此删去署名。
Render a confirmed signature in the lower-right reserved zone; otherwise keep it empty. When signed, lower-right negative space means space around the signature, not omission of it.

长诗句和长篇名按内容增加列数或缩小至仍可读的字号，不能剪裁、漏字、挤进光斑或默认复用短句坐标。图像模型只能参照字体风格，不等于精确字体文件排印；必须逐字目检，不将完整海报再次送入横排脚本叠字。
Adapt column count to text length. Image-model typography approximates the selected style and requires character-by-character inspection.
