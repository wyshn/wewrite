# AGENTS

## Context

- 仓库：`wewrite`，公众号内容全流程 CLI：选题 → 素材 → 写作 → 审稿 → 排版 → 发布。
- 栈：Python ≥3.11；`src/wewrite/` 是 CLI 与 toolkit，`skills/` 是 10 个可独立调用的 skill。
- 分发：`pip install -e .` 后得到 `wewrite` 命令；MIT 许可，公开仓库。
- 配置：`config.example.yaml` 为模板，实际配置在用户目录，不入库。

## Commands

| 目的 | 命令 |
|---|---|
| 安装（可编辑） | `pip install -e .` |
| 查子命令 | `wewrite --help` |
| 测试 | `python3 -m pytest tests/ -q` |
| 上下文预算守卫 | `python3 scripts/context_budget.py --budget-tokens 15500` |

## Structure

- `src/wewrite/cli.py` 是调度器：只做「子命令名 → 模块」映射并透传参数。
- `skills/`：`wewrite`、`wewrite-learn`、`wewrite-publish`、`wewrite-review`、`wewrite-rewrite`、`wewrite-stats` 等。
- `config.example.yaml` 是唯一配置口径来源。

## Boundaries

- ✅ **总是**：改 CLI 或 skill 跑 `pytest tests/ -q` 与 `context_budget.py`；新增配置项同步 `config.example.yaml` 与 README。
- ⚠️ **先问**：新增子命令或 skill；改 `cli.py` 的分发映射；改版本号（`VERSION` 文件）。
- 🚫 **绝不**：让单个 skill 的上下文超过 15500 tokens 预算；在每个命令模块里重复定义 argparse 参数；把用户配置、token、cookie 提交进仓库。

## Rules

- 各命令模块保持独立 `argparse`（历史上是独立脚本），调度器不重复定义参数——这是设计约束，不是风格偏好。
- skill 与 CLI 分离：skill 是可被 agent 读取的指令包，CLI 是可执行入口，两边不要互相内嵌。
- 版本号只在 `VERSION` 文件维护；`pyproject.toml` 动态读取它。

## Verification

- `python3 -m pytest tests/ -q` 全绿。
- `python3 scripts/context_budget.py --budget-tokens 15500` 通过。
- 手动跑一次主流程：`wewrite --help` 能列出全部子命令。

## Commit

- `feat(skill): …` / `fix(cli): …` / `docs: …`，subject 用中文。
