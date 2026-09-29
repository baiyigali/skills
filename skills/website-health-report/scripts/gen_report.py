#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""技能版报告生成器：读体检数据 JSON（audit.py 输出 + 分析出的问题列表），渲染正式报告 HTML。

用法:
    python3 gen_report.py <data.json> <out.html> [--brand none | --brand-file <path>]

data.json 结构（audit.py 的输出 + issues 分析，issues 由智能体按 SKILL.md 纪律撰写）:
{
  "domain": "www.example.com", "org": "机构简称（可选，用于文件名）",
  "full_name": "机构全称", "industry": "行业",
  "date": "2026-09-29",                # 缺省取今天
  "finding": "核心问题一句话",
  "extra": "补充说明（可为空）",
  "checks_total": 24,
  "issues": [
    {"title": "问题标题（不带编号、不带恐吓词）", "evidence": "检测证据（实测原文）",
     "impact": "对您的影响（结合该机构业务场景）", "fix": "修复方向（具体可执行）",
     "severity": "高|中|低"}
  ]
}

注意：问题不写内部编号；输出 HTML 中不含任何分类代码。
"""
import json, os, re, html, argparse, time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 技能根目录

def esc(s):
    return html.escape(str(s), quote=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", help="数据 JSON 路径")
    ap.add_argument("out", help="输出 HTML 路径")
    ap.add_argument("--brand", default="auto", help="none=不出品牌块；auto=用 brand-file")
    ap.add_argument("--brand-file", default=os.path.join(BASE, "brand.json"))
    a = ap.parse_args()

    d = json.load(open(a.data, encoding="utf-8"))
    full_name = d["full_name"]
    domain = d["domain"]
    date = d.get("date") or time.strftime("%Y-%m-%d")
    industry = d.get("industry", "—")
    issues = d["issues"]
    checks_total = d.get("checks_total", 24)
    finding = d.get("finding", "")
    extra = d.get("extra", "")

    # 机构简称（文件名用）：优先 org 字段，否则取 full_name 去掉公司后缀与括注
    short = d.get("org") or re.sub(r"(股份)?有限(责任)?公司$|（[^）]*）$|\([^)]*\)$", "", full_name).strip() or full_name
    report_id = "WB-" + date.replace("-", "") + "-" + re.sub(r"[^A-Za-z0-9]", "", domain)[:24]

    n_high = sum(1 for i in issues if i["severity"] == "高")
    n_mid = sum(1 for i in issues if i["severity"] == "中")
    n_low = sum(1 for i in issues if i["severity"] == "低")

    sev_tag = {"高": ("sev-h", "较严重"), "中": ("sev-m", "中等"), "低": ("sev-l", "改善项")}
    issues_html = ""
    for i, p in enumerate(issues, 1):
        cls, label = sev_tag[p["severity"]]
        issues_html += f"""
<div class="issue" data-sev="{esc(p["severity"])}">
<h3>{i}. {esc(p["title"])} &nbsp;<span class="sev {cls}">{label}</span></h3>
<div class="ev"><b>检测证据：</b>{esc(p["evidence"])}</div>
<div class="im"><b>对您的影响：</b>{esc(p["impact"])}</div>
<div class="fx"><b>修复方向：</b>{esc(p["fix"])}</div>
</div>"""

    extra_html = f'<div class="note">{esc(extra)}</div>' if extra else ""

    faq_html = """
<h2>常见问题（FAQ）</h2>
<table class="faq">
<tr><th>问题</th><th>回答</th></tr>
<tr><td>这些问题影响网站正常使用吗？</td><td>不影响日常编辑与访问，影响的是<b>新客户第一次接触贵机构时的观感、信任与搜索排名</b>——属于慢性流失，而非急性故障。</td></tr>
<tr><td>修复要花多少钱？</td><td>视建站方式而定：证书部署类通常数百元/年成本加少量配置工时；域名跳转、描述补全等属于小改动。可先看报告，再自行询价比价，我们不强求合作。</td></tr>
<tr><td>修复需要多长时间？</td><td>证书与跳转类通常 1 个工作日内完成；涉及建站系统升级另议。</td></tr>
<tr><td>我们自己找原来的建站服务商修可以吗？</td><td>完全可以。本报告所有问题均附检测证据与修复方向，拿给任何一位技术人员都可照单处理。</td></tr>
</table>"""

    # 品牌/无品牌两套头部
    if a.brand == "none":
        brand = {"name": "", "site": "", "about": None}
        brandline = '<div class="brandline"><span>网站健康体检</span></div>'
        sub_meta = (f"检测对象：{esc(domain)} ｜ 行业：{esc(industry)} ｜ "
                    f"检测日期：{esc(date)}<br>编号：{esc(report_id)}")
        about_html = ""
    else:
        brand = json.load(open(a.brand_file, encoding="utf-8"))
        brandline = f'<div class="brandline"><span>{esc(brand["name"])}</span><span>网站健康体检</span></div>'
        sub_meta = (f"检测对象：{esc(domain)} ｜ 行业：{esc(industry)} ｜ 检测日期：{esc(date)}<br>"
                    f"出品：{esc(brand['name'])}（{esc(brand['site'])}） ｜ 编号：{esc(report_id)}")
        about_html = f'<div class="note about">{esc(brand["about"])}</div>' if brand.get("about") else ""

    tpl = open(os.path.join(BASE, "templates", "report_template.html"), encoding="utf-8").read()
    rep = (tpl
           .replace("__BRANDLINE__", brandline)
           .replace("__SUB_META__", sub_meta)
           .replace("__FULL_NAME__", esc(full_name))
           .replace("__DOMAIN__", esc(domain))
           .replace("__INDUSTRY__", esc(industry))
           .replace("__DATE__", esc(date))
           .replace("__CHECKS_TOTAL__", str(checks_total))
           .replace("__N_HIGH__", str(n_high))
           .replace("__N_MID__", str(n_mid))
           .replace("__N_LOW__", str(n_low))
           .replace("__FINDING__", esc(finding))
           .replace("__ISSUES_HTML__", issues_html)
           .replace("__EXTRA_HTML__", extra_html)
           .replace("__FAQ_HTML__", faq_html)
           .replace("__ABOUT_HTML__", about_html))

    out_dir = os.path.dirname(os.path.abspath(a.out))
    os.makedirs(out_dir, exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(rep)
    print("OK", a.out)
    print(f"FILENAME_SUGGEST: 网站体检报告-{short}")

if __name__ == "__main__":
    main()
