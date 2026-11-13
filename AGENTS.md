# AGENTS

## Read first
- 产品边界与三种模式：`docs/PRODUCT.md`
- 运行时行为：`skills/wewrite/SKILL.md`（默认只交付本地稿：不生图、不发布；发布需显式授权）
- 内容质量口径：`docs/content-quality-rubric.md`；回归用例：`docs/evals.json`
- 发布/部署环境：`docs/handover/DEPLOYMENT.md`（会过期的事实只放这里）

## Context
- 双身份：`skills/` 是分发给 Agent 的指令包（产品）；`src/wewrite/` 是确定性工具层（CLI + toolkit）。用户可感知的行为改 skills，确定性能力改 src，不要把流程塞进 CLI。
- 10 个 skill = 主入口 `wewrite` + 9 个 `wewrite-*`；`install.sh` 只链接 `skills/wewrite*`。
- 用户状态统一在 `wewrite home`（默认 `~/.wewrite`）：config/style/history/output/runs 等都在这里，仓库内不落用户状态。
- 仓库 `wyshn/wewrite` fork 自 `imraywang/wewrite`；保留 `LICENSE`、`NOTICE` 与上游署名。

## Commands
| 目的 | 命令 |
|---|---|
| 安装/修复 | `bash install.sh` |
| 全量测试 | `.venv/bin/python -m pytest tests/ -q` |
| 单个契约测试 | `.venv/bin/python -m pytest tests/test_skill_contracts.py -q` |
| 上下文预算 | `.venv/bin/python scripts/context_budget.py --budget-tokens 15500` |
| CLI 自检 | `wewrite diagnose --json` |

若 `python3` 没有 pytest，用 `.venv/bin/python`；CI 用 3.11。

## Structure
- `src/wewrite/cli.py` 只做「子命令名 → 模块」映射并透传参数；各命令模块保持独立 `argparse`，调度器不重复定义参数。
- `skills/` 每个模块是独立指令包，只通过 `{home}` / `{skill_dir}` 解析路径，不写死本机路径。
- `config.example.yaml` 是配置模板与唯一口径；真实配置在 `$WEWRITE_HOME/config.yaml`。

## Boundaries
- **总是**：改 CLI 跑全量测试；改 skill 跑 `test_skill_contracts.py` + 预算；新增配置同步 `config.example.yaml` 与 README。
- **先问**：新增/删除 skill 或子命令；改 `.claude-plugin/plugin.json` 的 skills 列表；改版本；改发布链路；加核心依赖。
- **绝不**：提交用户配置、token、cookie、`~/.wewrite` 内容；让完整流程静态上下文超过 15500 tokens；重写 skill 里的契约句而不改测试；恢复 v4 已退役文件；删 NOTICE 或上游署名。

## Rules
- 版本真源是 `VERSION`；`pyproject.toml` 动态读取。改版本必须同步 `.claude-plugin/plugin.json`、README 当前版本、`CHANGELOG.md`（`test_plugin_manifest_matches_release_and_skills` 会卡）。
- 新增子命令必须同步 README（`test_readme_sync` 会卡）；新增主题同步 README 主题清单；退役文件清单见 `test_retired_v4_files_stay_removed`，不要复活。
- `context_budget.py` 量的是「主入口 + 5 个流程模块 + 引用 + 默认人格」的完整流程静态文档（当前约 6.4k），不是单个 skill；纯开发参考登记在 `AUXILIARY`。
- skill 文案里的硬约束（默认不发布、排版/发布不自动生图、原始正文不被覆盖、不得把模型记忆标为 verified）是字符串契约，改措辞先看 `tests/test_skill_contracts.py`。

## Verification
- 自动化：全量 pytest 通过；预算通过（当前约 6.4k < 15.5k）。
- 实际做一遍（按改动选一条，记录观察而非打勾）：
  - 写作/审稿：用 `docs/evals.json` 任一用例跑完整流程，确认 `publishable=true`，记 run_id。
  - 排版/主题：`wewrite preview docs/demo-article.md --theme <name>`，打开长图看一遍。
  - 发布：`wewrite-aliyun-push ... --dry-run` 先看计划；真发需用户明确授权。
  - CLI：`wewrite diagnose --json` + 改动的子命令跑一条真实输入。
- 交付写三段：改了什么 / 怎么验证 / 哪些没验证。

## Commit
- scope 用 `skill` / `cli` / `docs` 等领域名；其余遵循父级 `~/Documents/Auto_Lab/AGENTS.md`（Conventional Commits、中文 subject）。
