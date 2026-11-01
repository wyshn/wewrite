# Changelog

> 4.2.1 及更早版本来自 upstream [imraywang/wewrite](https://github.com/imraywang/wewrite)。本文件从 4.3.0 开始记录本仓库的变更。

## 4.3.1 — 2026-11-01

> 发布页：[v4.3.1](https://github.com/wyshn/wewrite/releases/tag/v4.3.1)

补全 4.3.0 的 tag 快照，并更正维护者署名。

### 文档修正

- `CHANGELOG.md` 的发布页链接、`README.md` 的更新日志链接进入 4.3.1 tag 快照。
- 维护者署名由 `Madara` 更正为 `Marcus`（README、LICENSE、NOTICE、Release 说明）。
- 4.3.0 Release 说明同步更正署名；历史 tag `v4.3.0` 快照保持不变。

### 验证

- `python3 -m pytest tests/ -q`：136 passed
- `git show v4.3.1:CHANGELOG.md` 包含 Release 链接与 Marcus 署名
- `git show v4.3.1:NOTICE` 包含 `Copyright (c) 2026 Marcus`

## 4.3.0 — 2026-11-01

> 发布页：[v4.3.0](https://github.com/wyshn/wewrite/releases/tag/v4.3.0)

本版本把 wewrite 独立为可持续维护的 fork，并补齐 CodeBuddy 安装、即梦生图通道、微信图片后处理、排版修复与产出目录校验。

### 新增

- **即梦 / Dreamina CLI 通道**：`image.provider: dreamina`，不需要 API Key，复用本机 `dreamina login` 的 OAuth 登录态；默认 `model: 5.0`、`resolution: 2k`。
- **参考图 / 图生图**：manifest 条目支持 `refs: [本地图片路径]`，单张模式支持 `--refs a.png b.png`；有参考图时自动走 `image2image`，最多 10 张。
- **`wewrite draft-delete <media_id>`**：封装微信 `draft/delete`，用于清理旧版草稿；凭据走 `config.yaml`，也支持 `--appid/--secret`。
- **`wewrite output-check`**：校验 `~/.wewrite/output` 的目录契约，检查必需文件、图片体积、相对路径、密钥文件与 `ai-daily-report` 残留。
- **CodeBuddy 安装支持**：`install.sh` 现在会把 10 个 skill 链接到 `~/.codebuddy/skills`，同时保留 `~/.claude/skills`、`~/.agents/skills`、OpenClaw 和 Codex 目录。
- **归属文件**：新增 `NOTICE`；`LICENSE` 同时保留 upstream（OpenClaw）与修改方（Marcus）版权。

### 修复

- **中文标点空格**：转换器只在中日韩汉字与拉丁字母/数字之间插空格，不再在 `，。；：、` 前后插空格。此前一篇 1,800 字的文章会出现 22 处逗号前空格、17 处句号前空格。
- **AIGC 声明**：默认文案从“作者进行了实测验证和编辑修改”改为“作者进行了编辑与校对”，避免与未实测文章自相矛盾；新增 `--no-aigc-footer`，可按文章关闭。
- **微信图片规格**：封面统一裁切/缩放为 900×383，正文图统一缩到宽 900，体积上限从 5MB 改为微信 `media/uploadimg` 的 1MB。
- **封面比例映射**：`_size_to_aspect` 增加 21:9，2.35:1 不再退化成 16:9。
- **内联代码配色**：`professional-clean` 的 `code` 从品红 `#d946ef` 改为蓝色 `#1d4ed8`，并加 `box-decoration-break: clone` 防止换行断色。
- **diagnose**：配置了 dreamina 但没有 `api_key` 时，不再误报 `skip_image_gen=true`。

### 方法 / 约定

- **产出目录契约**：
  - 过程产物：`~/.wewrite/runs/<run_id>/`
  - 交付物：`~/.wewrite/output/<slug>/`，包含 `article.md`、`article-illustrated.md`、`preview.html`、`cover.png`、`images/`、`review-report.json`
  - 仓库内不再新建 `daily/`、`pushes/`、`reports/` 等正文产出目录。
- **交付前校验**：运行 `wewrite output-check`；正文图必须 ≤1MB、≤10 张，图片必须用相对路径且不能跳出产出目录。
- **写作人格**：支持 `~/.wewrite/personas/` 自定义人格；`style.yaml` 的 `writing_persona` 一行切换，内置人格不复制、不 fork。
- **生图策略**：封面走即梦的 1920×816（后端按比例对齐），落盘后本地裁切到 900×383；正文请求 1440×810（后端可能按比例对齐），落盘后缩到宽 900。

### 仓库 / 工程

- 远程更新：`origin` 指向 `wyshn/wewrite`，`upstream` 保留 `imraywang/wewrite`；保留 upstream 完整历史并合并目标仓库初始提交。
- 仓库 URL、安装命令、`pyproject.toml` 的 `Repository` 全部切到 `wyshn/wewrite`，并新增 `Upstream` 链接。
- `install.sh` 在无 `pyproject.toml` 的 dist 场景改为从本仓库 git 安装，不再从 PyPI 安装 upstream 包。
- 移除 upstream-only 的 `release.yml`（PyPI 发布）与 `star-history.yml`（upstream 星图），只保留 `checks.yml`。
- 版本号：`4.2.1` → `4.3.0`。

### 验证

- `python3 -m pytest tests/ -q`：136 passed
- `python3 scripts/context_budget.py --budget-tokens 15500`：通过
- `bash -n install.sh`：通过
- `wewrite output-check`：现有两个产出目录 2/2 通过
- 跟踪文件无密钥、无 >5MB 大文件

### 升级提示

- 已安装旧版 skill 的机器，拉取后重跑 `bash install.sh`，会补上 `~/.codebuddy/skills` 链接。
- 旧草稿里的“实测验证”文案不会自动更新；需要重新 `wewrite publish` 生成新草稿。
- 如果之前用 `pip install wewrite` 安装的是 upstream 包，请改为 `bash install.sh` 或 `uv tool install git+https://github.com/wyshn/wewrite.git`。
