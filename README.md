# baiyigali/skills · AI Agent Skills by 程序员白大力

Production-ready [Agent Skills](https://agentskills.io) (SKILL.md format) for AI coding agents — Claude Code, Cursor, Codex, Gemini CLI, WorkBuddy, and 60+ other SKILL.md-compatible agents.

一组可直接安装的 AI Agent 技能（SKILL.md 标准格式），由公众号「**程序员白大力**」维护，主打 AI 产品分析与内容自动化流水线。

## Skills / 技能清单

### 1. `competitor-analysis-report` — 竞品分析报告生成器

Generate a professional competitive analysis report from a single TOPIC (product or category): three-phase workflow (research → structured analysis → writing), fixed 11-chapter structure with references and hashtags, auto-generated cover image, ready to publish.

输入一个 TOPIC（具体单品或产品品类），自动完成「检索收集 → 清洗结构化 → 撰写成稿」三阶段流程，产出 11 章正文 + 参考资料 + 话题标签的公众号风格 Markdown 报告，并自动生成封面图。

```bash
npx skills add baiyigali/skills --skill competitor-analysis-report
```

### 2. `wechat-article-publish` — 文章发布到公众号

Render a finished Markdown article into WeChat Official Account styling and push it to the draft box via the open-source [wechat-auto-publish](https://github.com/baiyigali/wechat-auto-publish) CLI. One command from local Markdown to WeChat draft.

把写好的 Markdown 文章渲染成公众号样式，一键推送到公众号草稿箱（底层为开源工具 wechat-auto-publish）。

```bash
npx skills add baiyigali/skills --skill wechat-article-publish
```

### 3. `it-hotspot-article` — IT 热点追热点写文

Chase real-time domestic IT/internet trending events and turn them into a publish-ready tech-explainer: three-phase pipeline (72-hour hotspot monitoring → IT-relevance filtering → fixed-template writing), cinematic cover image generated locally, professional tone with zero clickbait.

实时检索国内 IT/互联网热点（72 小时窗口、多源交叉验证），自动筛选最适合技术科普的事件，按固定模板产出事件复盘、技术拆解、常见误区、实操指引的公众号技术文，并生成电影感写实封面图。专业调性优先，不做标题党。

```bash
npx skills add baiyigali/skills --skill it-hotspot-article
```

### Pipeline / 组合用法

The skills chain into an end-to-end pipeline: **chase a hot topic (or analyze a market) → generate the article/report → publish to WeChat in one step.**

三个技能可以串联成完整流水线：**追热点出稿（或竞品分析出稿）→ 一键发布公众号草稿箱**。

```text
it-hotspot-article ─────────▶ .md + .png ──┐
                                           ├──▶ wechat-article-publish ──▶ 草稿箱
competitor-analysis-report ──▶ .md + .png ─┘
```

## Install / 安装说明

- Prerequisites: Node.js (for `npx`), or copy the skill folder manually into your agent's skills directory (e.g. `~/.claude/skills/`, `~/.workbuddy/skills/`).
- Each skill folder contains a `SKILL.md` following the open [Agent Skills specification](https://agentskills.io). You can also install by cloning this repo and copying any `skills/<name>/` folder.

## Repository Layout / 目录结构

```text
skills/
├── competitor-analysis-report/
│   ├── SKILL.md
│   └── references/
│       └── report-template.md   # 12-section report template & hard rules
├── wechat-article-publish/
│   └── SKILL.md
├── it-hotspot-article/
│   └── SKILL.md
└── assets/                      # images (WeChat QR code, etc.)
```

## Author / 作者

**程序员白大力** · GitHub: [baiyigali](https://github.com/baiyigali)

Focus: AI product analysis, agent engineering, content automation. Publishing a regular series of competitive analysis reports on AI products & tracks (AI Agent, humanoid robots, AI coding tools, and more).

专注 AI 产品分析与智能体工程，公众号持续更新「竞品分析报告」系列（已覆盖 AI Agent、人形机器人、AI 编程助手、AI 视频等赛道）。

<p align="center">
  <img src="assets/wechat-qrcode.png" alt="微信公众号：程序员白大力" width="180">
</p>
<p align="center"><sub>WeChat Official Account / 微信公众号：程序员白大力 — scan for the full report series / 扫码获取完整报告系列</sub></p>

## License

MIT
