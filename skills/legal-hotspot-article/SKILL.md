---
name: legal-hotspot-article
description: >-
  Watch real-time trending lists (Baidu realtime, Weibo hot search, Douyin hot)
  and turn today's genuine trending livelihood/legal events into publish-ready
  Chinese popular-law (普法) Markdown articles with a cinematic text-free cover
  PNG. Strict pipeline: (1) open the live hot lists themselves and pick events
  by what is actually ranking — never preset a domain or search by a guessed
  keyword; (2) dedup against existing .md in the output dir, avoid political /
  unjudged / minor-victim / gory / living-figure-privacy topics; (3) fixed
  template — title / intro / event recap / civil-administrative-criminal
  three-layer breakdown / bust 3 misconceptions / practical steps / closing +
  hashtags; (4) desensitize every company/brand/agency/person name by replacing
  one character with 某; (5) cinematic photorealistic cover with East Asian
  faces and zero on-image text, downloaded and sips-converted to a same-named
  real PNG. Produces only the .md, .png and .md-prompt files. Chinese trigger words:
  法律热点 / 普法文章 / 追热点写普法 / 民生法律热点.
license: MIT
metadata:
  author: baiyigali
  display-name: 法律普法公众号
  version: "1.0"
  repository: https://github.com/baiyigali/skills
tags:
  - content-automation
  - legal-writing
  - hot-topics
  - pufa
---

# 法律热点普法公众号文章（选题 + 写作）

## Overview

法律公众号专职撰稿人，全自动内容流水线：**① 打开实时热榜看今天真实在热的事件 → ② 法律适配筛选 + 去重 + 脱敏 → ③ 固定模板写普法文 → ④ 落盘 .md**。默认一轮 2 篇，两篇选题互不相同。本技能只负责写作，产出可直接使用的本地文件；发布等后续环节由调用方另行指定。

## Workflow

### 1. 启动：确认交付目录 + 盘点去重基线

- **交付目录**：第 1 次运行时向用户确认文章保存到哪里；用户未指定时，默认 `~/Desktop/articles/法律热点/`（不存在则创建）。同一会话后续沿用，不反复问。下文 `<输出目录>` 即指这个目录，不要写死带用户名的绝对路径。
- 先 `ls <输出目录>/*.md`，记下已有主名清单。同一事件、同一法律点不重复写；本轮新选题不得与清单重名或重法律点。

### 2. 阶段①：打开实时热榜本身选题（最关键纪律）

**严禁先入为主地带话题关键词去搜索"找"选题。** 不预设领域、不带目的，直接打开下面这些实时热榜，看今天排名上真实在热什么，再判断哪个有法律切入角度和大众认知误区：

- **首选**：百度实时榜 `https://top.baidu.com/board?tab=realtime`，用 Browser Use（`plane="bu"`）打开，`bu.read_all("div.category-wrap_iQLoo", fields=["text"], limit=55)` 逐条读榜单文本。
- **补充**：微博热搜 `https://weibo.com/hot/search`（读页面文本即可，完整榜单需登录时只取可见的 Top 10）、抖音热点 `https://www.douyin.com/hot`。

已知做不通、不要再试：微博 JSON 接口 `https://weibo.com/ajax/side/hotSearch`（Forbidden）；今日头条 hot-board 页 read_all/get_page_text 返回空或 parameter err。

从榜单里挑民生法律事件（劳动、消费维权、邻里、个保、婚姻家事、物业、网络侵权、交通安全等优先）。外交/政治/亚运体育/纯娱乐/明星私德条目直接跳过。

### 3. 阶段②：法律筛选 + 事实核实

对候选事件用 general_search 多源核实事实（央媒/权威媒体为准），再判断：热度够、有法律切入、有大众认知误区。**敏感红线（拿不准就换下一个）**：政治外交、未宣判案件（只讲官方通报、不预判结果）、未成年人可识别细节、恶性刑案猎奇细节、在世公众人物私德、民族宗教地区话题。

选好题后，1-3 句报告选题与法律点方向，直接继续不等确认。

### 4. 阶段③：固定模板写正文（每篇严格遵守）

输出 `.md`，结构固定：

- **标题**：抓人，突出「事件 + 法律观点/后果」，不标题党。
- **引言**：简述事件 → 抛大众认知误区 → 引出法律问题。
- **一、事件复盘**：客观陈述，不情绪化站队。
- **二、法律核心拆解**：分 **民事 / 行政 / 刑事** 三层讲清各方行为定性、核心争议、法条（《民法典》《治安管理处罚法》《刑法》《个保法》等规范表述）。
- **三、破除 3 个法律误区**（文章重点）。
- **四、普通人实操指引**：可落地的维权/应对步骤。
- **五、结尾**：普法价值 + 引导转发，文末跟话题标签。
- **六、参考文章**：结尾话题标签之前，列一条"**参考文章**"小标题，下面用项目符号列出本轮事实核实用到的权威报道来源（媒体名 + 报道标题），**只写文字、不放超链接**，3-6 条即可，宁缺毋滥，不用编造来源。

硬性规则：

- 通俗接地气，法条准确，客观中立不煽动；禁止虚构案号、官方未发布判决，事实忠于公开报道，存疑处标注。
- **脱敏**：企业/品牌/APP/机构/人名一律从原名挑一个字换成"某"，其余保留（读着自然为准）；讲规则本身不必点名。
- **加粗片段结尾不带标点**（禁止 `**：` `**。` 这类收尾）。
- 只输出文章正文到 md，不加多余头尾；md 格式，不出 docx。

### 5. 输出落盘

- 目录：第 1 步确认的 `<输出目录>`，**平铺不建子文件夹**。
- 主名＝事件简短概括（如 `黑芝麻糊霉菌超标.md`）。
- 收尾报告：每篇标题、主名，以及本轮目录下生成的 `.md` 文件清单。

## FAQ

| 现象 | 处理 |
| --- | --- |
| 百度榜全是体育外交/娱乐 | 切微博、抖音实时榜补选，不要硬凑 |
| 候选事件已写过 / 法律点重复 | 回到榜单换下一候选 |
| 事实多源冲突 | 以官方通报/央媒为准，冲突处文中标注 |
