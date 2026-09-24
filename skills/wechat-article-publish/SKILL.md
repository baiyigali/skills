---
name: wechat-article-publish
description: >-
  Render a finished Markdown article into WeChat Official Account styling and
  push it to the account's draft box via the open-source wechat-auto-publish
  CLI. Inputs: article .md, cover .png, appid & secret (optional author name).
  Output: draft media_id or a faithful error report (e.g. 40164 = IP not
  whitelisted). Pairs well with competitor-analysis-report for an end-to-end
  "write then publish" pipeline. Chinese trigger words: 发布到公众号 /
  推到草稿箱 / 发公众号草稿.
license: MIT
metadata:
  author: baiyigali
  display-name: 程序员白大力（微信公众号）
  version: "1.1"
  repository: https://github.com/baiyigali/skills
tags:
  - wechat
  - publishing
  - content-marketing
---

# WeChat Official Article Publisher / 文章发布到公众号

## Overview

把一篇写好的文章渲染成公众号样式，推送到微信公众号草稿箱。底层依赖 `wechat-auto-publish` 命令行工具（PyPI 包，或源码安装 https://github.com/baiyigali/wechat-auto-publish.git ）。

## Workflow

### 1. 准备工具与环境

- 先检查 `wechat-auto-publish` 是否已可用（如 `command -v wechat-auto-publish`）。已可用则跳过安装。
- 未安装时，优先安装到隔离的 Python venv（避免污染全局环境）：

```bash
python3 -m venv <venv-dir>
<venv-dir>/bin/pip install wechat-auto-publish
```

- PyPI 不可用或需要源码安装时：`git clone https://github.com/baiyigali/wechat-auto-publish.git && cd wechat-auto-publish && <venv-dir>/bin/pip install -e .`

### 2. 收集输入

发布前确认以下四类输入齐全，缺什么向用户要什么，不要猜：

- **文章 Markdown**：一个 `.md` 文件路径。
- **封面 PNG**：一个 `.png` 文件路径（如由竞品分析等技能生成，通常与文章同名）。
- **凭据**：`appid`、`secret`（微信公众号后台获取）。凭据仅在本次命令行调用中使用，**绝不写入文件、日志或回复正文**。
- **作者名 `author`**：可选。

### 3. 提取文章标题

- 读取 `.md` 文件第一行，确认是否为 H1（`# ` 开头）。
- **只去掉行首的 `# `，其余内容原样作为文章标题**——不要删任何后缀、系列名、书名号或其他标记。
- 若首行不是 H1，向用户确认标题，不要自行截取。

### 4. 运行发布

```bash
wechat-auto-publish draft "文章.md" "封面.png" "文章标题" \
  --appid 用户的AppID --secret 用户的AppSecret --author 作者名
```

- 摘要可选，不传时微信会自动生成。
- 命令行参数中包含 secret，执行后不要把含 secret 的完整命令原样回显给用户。

### 5. 结果交付

- **成功**：报告文章标题与草稿 `media_id`。
- **失败**：如实报告错误信息，不编造。常见错误 `40164` = 出口 IP 未加白名单，需用户到公众号后台把当前出口 IP 加入 IP 白名单后重试。
- 最后提醒用户：草稿不会自动发表，需到公众号后台「草稿箱」中点击「发表」。

## FAQ

| 现象 | 处理 |
| --- | --- |
| 报错 40164 | 出口 IP 未加白，提示用户到公众号后台配置 IP 白名单 |
| 凭据缺失 | 向用户索要 appid/secret，不猜测、不使用占位值执行 |
| 封面缺失 | 向用户索要 png，或询问是否需要先生成封面 |
| 命令不存在 | 按 Workflow 第 1 步在 venv 中安装 |

## About the Author

Maintained by **程序员白大力** (GitHub: [baiyigali](https://github.com/baiyigali)) — WeChat Official Account: 程序员白大力. The underlying CLI is open source at [wechat-auto-publish](https://github.com/baiyigali/wechat-auto-publish).
