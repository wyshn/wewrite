# WeWrite 产品说明

> 状态：维护中 · 更新：2026-11-13 · 适用：维护者与 Agent

## 一句话

给 AI Agent 的微信公众号内容 skill 包 + 确定性 CLI 工具层：一句话完成选题、素材、写作、审稿；配图、排版、发布按需追加。

## 用户路径

选题 → 文章任务书（brief）→ 主张与来源清单（claims）→ 初稿（draft）→ 编辑审稿（review）→ 成稿（article）

后续动作（可选）：配图 → 排版预览 → 草稿箱发布

## 三种模式

| 模式 | 用户说法 | 默认行为 |
|---|---|---|
| `draft` | “写一篇” | 只交付审过的本地成稿；不生图、不发布 |
| `complete` | “完整制作” | 先完成正文；封存后再独立配图和本地预览 |
| `publish` | “推到草稿箱” | 需用户明确授权；仍不自动生图 |

## 成功标准

- 审稿决定为 `pass`，且 `review-report.json` 的 `publishable=true`；
- `brief.yaml`、`claims.yaml`、`draft.md`、`article.md`、`review-report.json` 齐全；
- 核心事实有来源；不虚构作者经历；结论不超出证据；
- 成稿在事实、判断和读者收益上可直接使用，不以“像人”为目标。

质量口径见 `docs/content-quality-rubric.md`；回归用例见 `docs/evals.json`。

## 非目标

- 不用工具分数替代编辑判断：语言风险分只提示套话、碎句和节奏问题，不决定 `publishable`。
- 不把模型记忆标为 `verified`，不“合理重建”作者经历。
- 不在排版或发布时自动调用配图。
- 不在用户未授权时推送草稿箱。
