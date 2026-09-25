# 来源与授权 / Sources and licenses

诗句与窗形的来源 URL 保存在 catalog.json。目录核对日期用于标识资料版本，不作为运行条件。古典诗句摘录公版原文，不包含现代赏析。
Quotation and window references live in the catalog; its verification date identifies the research snapshot.

## 字体 / Fonts

- 齐伋体 Qiji 0.0.4，标题默认字体。[仓库](https://github.com/LingDong-/qiji-font)、[发行版](https://github.com/LingDong-/qiji-font/releases/tag/0.0.4)。采用未修改的核心字形 qiji.ttf，授权见 assets/OFL-Qiji.txt。SHA-256：`2ee30738d37b102bfa90e56cd04fde2620ccef012b44390b77b0703cf995cf5b`。
- 蒹葭楷 ChienChia F，内嵌版本 0.900，Tsao Tung / The Klee Project Authors。[仓库](https://github.com/Tsao-Tung/Chienchia)，授权见 assets/OFL-ChienChia.txt。
- 芫荽 Iansui，蒹葭楷缺字备用。[仓库](https://github.com/ButTaiwan/iansui)，授权见 assets/OFL-Iansui.txt。缺字通过字形覆盖检查选择字体，不替换 Unicode 字符。
- 以上随包字体遵循 SIL OFL 1.1。楷体可从运行环境的已安装字体选择，不随包分发系统字体；`fonts.title` 可指定任意可用且有使用许可的标题字体。

Bundled fonts retain their original licenses. Qiji covers the default traditional title. Its simplified and traditional forms may share glyphs, so explicit simplified requests require visual verification. KaiTi is an optional locally supplied font.

## 图像 / Images

- assets/style-reference.png：AI 生成的无字龙与桂枝示例，用于纸感、光斑与柔影；具体物象由场景参数替换。
- assets/layout-reference.png：AI 生成的竖排龙海报示例，仅作文字层级与空间比例参考。示例字形来自图像模型，不是精确字体文件排印。具体文案、色相和物象按参数替换。

Reference images define treatment and spatial hierarchy; the selected catalog values define each poster's content.

原始参考材料的公开发布权由提供者确认；原始截图不随包分发。两张 AI 参考图在贡献者有权许可的范围内按项目 MIT 条款使用，不承诺纯 AI 输出在所有法域均享有排他版权，也不替代任何第三方权利。具体下游用途仍需检查其输入与输出。
The contributor confirms permission for the source references. The original screenshots are not bundled. Reference images are permitted under the project MIT terms to the extent of the contributor's rights; no universal exclusive copyright or third-party rights clearance is asserted.

## 颜色、形态与意象 / Palette and imagery

六色是固定数字设计色，以 catalog.json 的 HEX / RGB 为准；色名不代表唯一历史色标。局部光影与颗粒不等于修改基色。
The palette is a set of numeric design colors, not a claim of historical color standards.

五种花窗是传统园林窗洞的设计提炼，来源见目录；不是文物测绘。生肖、配景及其组合属于当代海报设计，不作历史图像制度或命理主张。「莲瓣瓜」指瓜果切瓣摆成莲花状供盘。
Window outlines draw on documented garden forms. Zodiac scenes and still-life combinations are contemporary design choices.

## 项目许可 / Project license

原创脚本和说明采用随包 LICENSE 中的 MIT 许可；字体继续使用各自 OFL，古典诗句原文不因收录而产生新的排他权利。许可与版权核对日期为 2026-09-25；上游许可证发生变化时应重新核验。不得将「有许可证」扩大解释为所有生成图像、所有输入或所有商用场景均无风险。
Original scripts and documentation use the bundled MIT license. Font licenses remain separate. The review date is 2026-09-25; recheck upstream terms when updating assets.
