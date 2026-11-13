# 发布与部署交接

> 状态：维护中 · 更新：2026-11-13 · 适用：维护者
> 会过期的环境事实只放本文件；`AGENTS.md` 只留指针。本文件不写密钥、账号和出口 IP。

## 发布链路

本地 → 阿里云 → 公众号草稿箱。不要在本地直接 `wewrite publish`：微信 IP 白名单绑定阿里云出口，换机或换出口后要同步微信后台。

## 一键脚本

入口：`wewrite-aliyun-push`（即 `scripts/aliyun-push.sh`，脚本头注释是用法与布局的单一事实源）。

```bash
wewrite-aliyun-push article output/文章.md --cover output/cover.png --theme professional-clean
wewrite-aliyun-push image poster.png -t "标题" -c "正文"
wewrite-aliyun-push sync
wewrite-aliyun-push article output/文章.md --cover output/cover.png --dry-run
```

`--dry-run` 或 `WEWRITE_PUSH_DRY_RUN=1` 只打印计划，不实际上传和推送。真发前必须有用户明确授权。

## 远端固定布局

| 路径 | 用途 |
|---|---|
| `/home/ecs-user/wewrite` | 仓库 + `.venv` |
| `/home/ecs-user/wewrite/state` | `WEWRITE_HOME`：config/style/history/output |
| `/home/ecs-user/wewrite/assets` | 每次推送的素材暂存（按 run-id 分目录） |
| `/home/ecs-user/wewrite/bin/wewrite` | 远端入口，自动设置 `WEWRITE_HOME` |

SSH 主机别名默认 `aliyun`；可用 `WEWRITE_ALIYUN_HOST`、`WEWRITE_ALIYUN_ROOT`、`WEWRITE_ALIYUN_STATE` 覆盖。

## 本地配置与状态

- 本地配置：`~/.wewrite/config.yaml`（由 `WEWRITE_LOCAL_CONFIG` 覆盖）。
- 推送时同步到远端 `state/config.yaml`；AppID/Secret 只存在用户状态目录，不入库。
- 本地状态目录：`wewrite home`（默认 `~/.wewrite`），不要提交。

## 验证

```bash
wewrite-aliyun-push --help
wewrite-aliyun-push article output/文章.md --cover output/cover.png --dry-run
ssh aliyun 'test -x /home/ecs-user/wewrite/bin/wewrite'
```
