# website-health-report 开发者说明

运行时使用说明见 `SKILL.md`（面向执行体检的智能体）；本文件面向**维护这个技能代码的人**。

## 项目结构

```
website-health-report/
├── SKILL.md              # 运行时指令（7 步流程、证据纪律、字体策略、边界）
├── brand.json            # 品牌配置（报告三处品牌位；--brand none 可整体去除）
├── scripts/
│   ├── audit.py          # 深度体检：DNS/TLS/HTTPS/页面信号 + 内页抽查 ≤10 页，输出 JSON
│   ├── gen_report.py     # 数据 JSON → 报告 HTML（参数化渲染，内部编码不上交付物）
│   └── html2pdf.py       # 报告 HTML → PDF（fpdf2，封面/色条/品牌表格，跨系统字体探测）
├── templates/
│   └── report_template.html
├── references/
│   └── 措辞与证据纪律.md   # 禁词、证据、复测纪律（SKILL.md 第 3/6 步引用）
└── tests/                # unittest 标准库，零额外依赖
```

## 跑测试

```bash
python3 -m unittest discover -s tests -v
```

- `test_gen_report.py`：CLI 端到端（渲染、占位符替换、严重度映射、摘要数字一致性、HTML 转义、品牌开关、文件名建议、坏输入必须报错）
- `test_audit.py`：纯函数单元（内页链接抽取与评分、DNS 存活），不发任何网络请求
- `test_html2pdf.py`：纯函数（标签剥离、严重度 span 剔除、字体探测）+ PDF 冒烟；无 fpdf2 或无中文字体的环境自动跳过

依赖：fpdf2（PDF 冒烟测试需要，建议独立 venv）；pypdfium2（PDF 文本抽取断言，缺则跳过对应断言）。

## 改代码流程

1. **先跑测试**确认基线全绿；
2. 改代码；**修 bug 必须先加复现该 bug 的回归测试**；
3. 再跑测试，全绿才算改完；
4. 同步三份副本：本目录 = 技能仓库 `skills/website-health-report/`（git 管理）+ SkillHub 发布暂存目录。注意：向暂存目录同步 SKILL.md 会覆盖其 SkillHub 专有 frontmatter（`slug`/`displayName`/`summary`），同步后必须补回；
5. 改了对外行为 → `SKILL.md` 与暂存 SKILL.md 的 `version` 一起 bump（严格 SemVer，如 `1.0.1`）。

## 发布（SkillHub）

```bash
skillhub publish <暂存目录> --dry-run          # 先预检
skillhub publish <暂存目录> --changelog "变更说明"
```

- slug 固定 `website-health-report`（全网唯一即占位，无需加人名/品牌后缀，命名空间自带归属）；
- 其他渠道：GitHub 仓库 `baiyigali/skills`（push 后 skills.sh / SkillsMP 自动爬取收录）；
- SkillHub 审核未过时看驳回理由，调整后同 slug 重新 publish。
