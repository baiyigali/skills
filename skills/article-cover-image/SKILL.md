---
name: article-cover-image
description: >-
  Generate a cinematic, text-free cover image for a FINISHED Markdown article
  and wire it back into the .md by local relative path. MUST be invoked only
  after the article .md has been written to disk — never from a bare title or
  outline. Pipeline: verify the article is complete (scripts/gate.py, hard fail
  if not) → read the full text and distill one scene unique to this piece →
  write two long English prompt variants to <name>-prompts.md → generate →
  convert to a real PNG → save as <name>.png beside the .md → insert
  ![封面](<name>.png) under the H1 → append the scene description to
  .cover-log.md for cross-issue dedup. Zero on-image text, East Asian faces
  when people appear, no generic stock imagery, distinct from the last 3 issues.
  Chinese trigger words: 生成封面 / 配图 / 封面图 / 文章配图 / 补封面.
license: MIT
metadata:
  author: baiyigali
  display-name: 程序员白大力（微信公众号）
  version: "1.0"
  repository: https://github.com/baiyigali/skills
compatibility: >-
  Requires an image generation tool (ImageGen or the host agent's equivalent)
  and a format conversion tool to land a real PNG. scripts/gate.py requires
  Python 3.9+.
tags:
  - cover-image
  - content-automation
  - wechat
---

# 文章封面图生成

## Overview

为一个**已经写完并落盘**的 Markdown 文章生成封面图，并把本地相对路径引用写回 md。
这是所有写作类技能共用的收尾环节，全局只维护这一份规则。

**唯一入口纪律**：本技能只在文章 .md 落盘之后被调用。写作技能不得在动笔前调用它；用户只给标题、文章尚未成稿时，先说明需要成稿后再执行。

## 硬性前置条件（不可跳过）

调用后第一步必须运行闸门脚本；任何一项不通过就**停止执行并向用户报告**，不得继续出图：

```bash
python3 scripts/gate.py "文章路径.md" --min-chars 800
```

脚本位于本技能目录下（`scripts/gate.py`）；若当前工作目录不在技能目录，改用绝对路径。

校验五项：文件存在 → 首行是 H1 → 正文达到字数下限 → 文末有话题标签 → 文中无 `placeholder` 假链接。全部通过才返回 exit 0。

- `--min-chars` 默认 800。长报告（竞品分析等）无需调整；短篇技术文可下调到 400–600。
- 脚本缺失或不可执行时，手工完成同样五项检查，并在回复中写明检查结果。

## Workflow

### 1. 校验

见上。不通过就停下，不允许"先出图再说"。

### 2. 提炼本期画面

通读全文，提炼**本期独有的具体画面**：

- 画面必须能从本期内容推断出来，选最有代表性的场景／物件／瞬间
- 禁止通用套图：机器人+电路板、城市天际线+网络、抽象科技光效、握手开会
- 与最近 3 期明显区分：先读同目录 `.cover-log.md`（不存在则跳过），避免构图与主体重复

### 3. 拟提示词并落盘

写 **2 个不同版本**的专业长英文提示词（采用版 + 备选版），写入同目录 `<主名>-prompts.md`：

- 电影镜头质感、高画质、写实主义
- 若画面中出现人物，用中国人／亚洲人
- **画面绝对无任何文字**（含门牌号、价格牌、指示牌、数字、logo）
- 涉及具体品牌的题材，不出现可识别车标／前脸／logo

提示词不写进文章正文。

### 4. 出图与落盘

- 用出图工具按采用版提示词生成。**默认 2.35:1**（公众号封面比例），需要其它比例时传 `--aspect`
- **尺寸与额度**：日常默认用 `1024x448`（同为 2.35:1，出图额度约为一半）；对画质有特殊要求（海报、置顶大图）才用 `1536x640`
- 保存为**真实 PNG**（不是改后缀）：下载后转格式，并用 `file` 确认类型
- 文件名与 md **同名**，放同级目录

### 5. 回写引用

在 md 标题（H1）下方插入：

```markdown
![封面](<主名>.png)
```

**只写本地相对路径**，不写任何云 URL／图床地址。媒体资产跟随目标平台：发布到公众号时由 `wechat-article-publish` 自动上传转存到微信 CDN 并替换地址（需 wechat-publish ≥ 1.0.1）。

### 6. 记录与呈现

- 同目录 `.cover-log.md` 追加一行：`- <主名>.png — <一句话画面描述>`，供跨期查重
- 用 present_files 呈现 md 与 png

## 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| 文章 md 路径 | 必填 | 唯一必需输入 |
| `--aspect` | `2.35:1` | 公众号封面推荐比例；可选 3:2、16:9、1:1 |
| 尺寸 | `1024x448` | 2.35:1 省额度档；`1536x640` 为高清档 |
| `--no-people` | 关闭 | 强制纯场景空镜，不出人物 |
| `--alt-prompt` | 关闭 | 改用备选版提示词出图 |

## 常见问题

| 现象 | 处理 |
|---|---|
| 闸门脚本报错 | 停止，先补完文章再调用本技能 |
| 出图带文字／水印 | 换提示词重生成，不手动裁切蒙混 |
| 生成失败或额度不足 | 如实报告并标注「封面待补」，不跳过环节假装完成 |
| 旧文缺封面 | 直接传入该 md 补封面，本技能不区分新旧 |

## 依赖关系

本技能**独立、可选**：写作技能（competitor-analysis-report / it-hotspot-article / legal-hotspot-article / policy-interpretation-article）只产出 .md，不感知也不调用本技能，没有封面也一样能成文。

任何**已落盘的 md 文章**都可以单独、事后调用本技能补封面，新旧不限。典型组合用法：

```text
写作技能 ──▶ .md ──▶（可选）article-cover-image ──▶（可选）wechat-article-publish
```
