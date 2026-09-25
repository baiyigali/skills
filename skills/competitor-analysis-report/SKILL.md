---
name: competitor-analysis-report
description: >-
  Generate professional, publication-ready competitive analysis reports in
  Markdown. Input a TOPIC (a single product or a whole product category) and the
  skill runs a strict three-phase workflow — web research, structured analysis,
  formal writing — covering market landscape, competitor tiers, head-to-head
  benchmarking (features, pricing, scenarios, channels, reputation), per-player
  SWOT, market gaps, and actionable strategy recommendations. Outputs an
  11-chapter report with references and hashtags, plus a generated cover image.
  Chinese trigger words: 竞品分析 / 竞品对标 / 竞争格局分析 / 竞品报告.
license: MIT
metadata:
  author: baiyigali
  display-name: 程序员白大力（微信公众号）
  version: "1.1"
  repository: https://github.com/baiyigali/skills
tags:
  - competitive-analysis
  - market-research
  - product-strategy
---

# Competitive Analysis Report Generator / 竞品分析报告生成器

## Overview

针对用户传入的 TOPIC（具体单品或产品品类），依托公开网络信息完成一份专业、完整、落地性强的竞品分析报告。严格遵循三阶段执行流程，不跳过步骤、不编造数据。详细执行规范与报告模板见 `references/report-template.md`（撰写报告正文前必须完整阅读该文件）。

## Workflow

### 1. 确认 TOPIC 与交付目录（输入收集阶段，一次问齐）

- 从用户请求中提取 TOPIC 参数。若用户未明确给出，先询问用户要分析的具体产品或产品品类，不要自行猜测。
- **同时询问一次交付目录**（只问一次，不反复确认）：本次报告的 .md 要保存到哪里。若用户没有指定，保存到当前工作区。**不得写死带用户名或工具专属的绝对路径。**
- **文件命名约定**：默认命名 `竞品分析报告_NN_主题.md`（NN 为两位递增序号，主题取自 TOPIC，不含空格）。若交付目录中已存在同系列文件，取现有最大序号 +1 作为本次 NN。
- 判断输入类型并确定分析模式：
  - **具体单品**（如：剪映PC版、Sora）：以该产品为核心对标主体，全网检索同赛道直接竞品、间接竞品、潜在竞品，做定向对标分析。
  - **产品品类**（如：AI视频生成产品、在线思维导图工具）：自动筛选赛道 TOP 主流头部竞品与梯队玩家，做品类全景竞品格局分析。

### 2. 阶段1：信息检索与竞品原始资料收集

- 按模板要求生成多组差异化搜索关键词，覆盖竞品清单、梯队划分、核心功能、定价、盈利模式、渠道、目标用户、技术壁垒、口碑、市场份额、迭代动态、痛点差评等全部调研维度（完整维度清单见 references/report-template.md）。
- 使用 WebSearch 广泛检索公开网络信息，来源覆盖产品官网、权威测评平台、行业白皮书、券商研报、科技媒体、用户社区、行业论坛。
- 信息分层标记：区分客观事实、行业测评观点、用户口碑、网络传闻，标注时效性，优先采用近 2-3 年数据。
- 完整留存原始素材，不提前加工润色。

### 3. 阶段2：信息清洗与结构化整理

- 去重提纯、数据校验（识别多来源冲突数据并标注口径差异）、按报告框架分层归类（竞争全景、梯队划分、头部拆解、横向对标、SWOT、口碑差异、打法策略、缺口机会）。
- 萃取关键对标数据与核心结论，搭建分析素材库。

### 4. 阶段3：撰写正式报告

- 完整阅读 `references/report-template.md`，严格遵循其中的固定 12 节目录、统一写作硬性要求与输出格式要求。
- **专业调性是底线**（适用于标题与全文）：
  - 文章标题准确描述分析对象，可点出核心结论，但不得使用耸动式副标题、噱头式反问或渲染对立的表述。
  - 正文以数据和事实为据，观点克制，结论跟着证据走，不过度渲染；话题性只能来自选题本身的含金量，不得靠刻意制造反差叙事博眼球。
  - 流量目标是参考，专业严谨是底线：宁可选题稳一点，也不为流量牺牲报告可信度。
- 输出为单个 .md 文件（禁止 doc/docx），按第 1 步约定的文件名保存到交付目录（目录不存在时先创建）。
- 仅输出完整报告成品，不在正文中暴露中间检索、整理、思考过程。

### 5. 收尾

- 文末在参考资料之后另起一行附适合公众号的话题标签。
- 话题标签之后**不附加任何署名、推广或引导关注行**——报告以话题标签收尾即止，账号引导由用户自行处理。

- 用可用的文件呈现方式将 .md 报告交付给用户。

## Resources

- `references/report-template.md` — 完整的固定报告目录、三阶段执行细则、写作硬性要求与输出格式。执行本技能任何阶段前先完整阅读。

## About the Author

Maintained by **程序员白大力** (GitHub: [baiyigali](https://github.com/baiyigali)) — WeChat Official Account: 程序员白大力. A series of AI product analysis reports is published on the account.
