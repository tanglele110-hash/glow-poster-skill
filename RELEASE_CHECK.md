# 发布前检查 / Release check

检查日期：2026-09-25。此记录针对首次公开发布的包文件，不表示所有参数组合均已生图或人工验收。

## 已完成

| 项目 | 结果与范围 |
|---|---|
| Skill 结构 | frontmatter 与入口验证通过；提供 Python 版本、依赖、注册和命令行说明 |
| 随机规划 | 4,800 个经典模式组合、57,600 个生肖模式组合的本地规划检查通过；指定选项固定 |
| 竖排文案 | 20 组诗句的规划文案与出处保留检查通过；实际模型字形仍需逐张目检 |
| 横排排字 | 20 组诗句真实字体排字通过，另有画布尺寸和署名排字检查 |
| 输入及失败边界 | 20 项拒绝检查通过，含未知选项、错误布局、缺字、署名过长、碰撞相关保护、拒绝覆盖和画布比例 |
| 署名 | 未作选择时 CLI 拒绝生成正式计划；有署名、不署名两条 CLI 路径通过 |
| 字体授权 | 三份随包 OFL 与各自上游公开许可证归一化比对一致；未分发操作系统字体 |
| 字体来源 | 三个 TTF 均与上游文件逐字节哈希一致，见下表 |
| 素材范围 | 仅两张无个人署名的 AI 参考图；原始截图、用户海报、日志、账号配置均未收入发布包 |
| 图像元数据 | 两张参考 PNG 未含附加元数据字段 |
| 来源边界 | 古诗保留出处，不包含现代译注；数字色值、窗形描述与摄影图片区分说明 |
| 文档修正 | 诗卷意象的“诗句只在下方”已改为按所选版式文字区排入 |

## 字体复核依据

| 文件 | 上游定位 | SHA-256 |
|---|---|---|
| qiji.ttf | LingDong-/qiji-font，正式 release 0.0.4 中的 qiji.ttf | `2ee30738d37b102bfa90e56cd04fde2620ccef012b44390b77b0703cf995cf5b` |
| ChienChia-F.ttf | Tsao-Tung/Chienchia，tree `89f871180ca9d904875bcd917a0c06d483c7440f`，fonts/ChienChia-F.ttf | `86fb6854d649c0fc3648b3a9bd92b7b25947f38ef0f67cb0d2307ba77374ad03` |
| Iansui-Regular.ttf | ButTaiwan/iansui，tree `9d9a8e68bf1e138dd91e562eeff28d95bca33196`，fonts/ttf/Iansui-Regular.ttf | `7f1aa62e9dcbf40d0ce41a5d3f1e5ea602e66c295778ac6fefb6b84d8ed08bd5` |

## 保留的能力边界

- 本次包检查在 Windows 与现有 Python 环境完成，未宣称实测所有操作系统或图片服务。
- 竖排为完整图片生成流程，无法承诺模型精确加载字体或逐像素色准。每张成图仍须检查文字、画布、形态、留白和可读性。
- 浅色底的白字可能触发低对比度拦截；这是明确失败，不通过自动改色掩盖。
- 参考图的原始材料发布权由提供者确认；版权审查为公开来源及包内容检查，不是对所有下游使用的法律保证。
- 新诗句、新字体、新参考图或许可证更新需要重新核对来源；本次字体在线比对不代表所有目录引用网页均在该日重新抓取。

Code and font checks are evidence for this package, not a claim that every generated poster or downstream use is automatically correct or rights-cleared.
