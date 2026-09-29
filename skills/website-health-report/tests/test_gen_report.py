#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_report.py 测试：CLI 端到端（临时文件，不出网）+ 纪律断言。"""
import json, os, re, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
GEN = os.path.join(SCRIPTS, "gen_report.py")

def run_gen(data, out, *extra):
    data_file = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(data, data_file, ensure_ascii=False)
    data_file.close()
    p = subprocess.run([sys.executable, GEN, data_file.name, out, *extra],
                       capture_output=True, text=True)
    os.unlink(data_file.name)
    return p

def sample_data(**over):
    d = {
        "domain": "www.example.com", "org": "示例律所",
        "full_name": "示例律师事务所", "industry": "法律服务",
        "finding": "核心问题一句话",
        "checks_total": 24,
        "issues": [
            {"title": "问题一", "evidence": "证据 <b>一</b>", "impact": "影响一",
             "fix": "修复一", "severity": "高"},
            {"title": "问题二", "evidence": "证据二", "impact": "影响二",
             "fix": "修复二", "severity": "改善项"},
        ],
    }
    d.update(over)
    return d


class TestGenReport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.out = os.path.join(self.tmp, "report.html")

    def test_render_ok_and_no_placeholders(self):
        p = run_gen(sample_data(), self.out)
        self.assertEqual(p.returncode, 0, p.stderr)
        html = open(self.out, encoding="utf-8").read()
        self.assertNotRegex(html, r"__[A-Z_]+__")           # 占位符全部替换
        self.assertIn("示例律师事务所", html)
        self.assertIn("常见问题（FAQ）", html)
        self.assertEqual(html.count('<div class="issue"'), 2)

    def test_severity_bianhaoxiang_accepted(self):
        """回归：severity=改善项 不能再 KeyError（2026-09-29 自检时踩过）"""
        p = run_gen(sample_data(), self.out)
        self.assertEqual(p.returncode, 0, p.stderr)
        html = open(self.out, encoding="utf-8").read()
        self.assertIn("改善项", html)
        self.assertNotIn("中等", html.split("</h2>")[1])   # 无中级标签混入

    def test_summary_counts_match_issues(self):
        p = run_gen(sample_data(), self.out)
        html = open(self.out, encoding="utf-8").read()
        self.assertIn("1 项较严重问题", html)               # 摘要高项数与正文一致
        self.assertIn("1 项改善项", html)

    def test_content_is_escaped(self):
        d = sample_data()
        d["issues"][0]["evidence"] = "探测 <script>alert(1)</script>"
        p = run_gen(d, self.out)
        html = open(self.out, encoding="utf-8").read()
        self.assertNotIn("<script>alert", html)
        self.assertIn("&lt;script&gt;", html)

    def test_no_internal_codes_on_deliverable(self):
        data = sample_data()
        data["issues"][0]["title"] = "【A1】带编码的标题"
        p = run_gen(data, self.out)
        html = open(self.out, encoding="utf-8").read()
        # 生成器原样透传标题——纪律要求智能体不带编码输入，此处固化检查点
        self.assertNotRegex(html, r"data-sev=\"【")
        self.assertIn("【A1】带编码的标题", html)  # 透传行为本身：文档化而非静默清洗

    def test_brand_none_removes_brand(self):
        p = run_gen(sample_data(), self.out, "--brand", "none")
        html = open(self.out, encoding="utf-8").read()
        self.assertNotIn("Pipe CMS", html)
        self.assertNotIn('class="note about"', html)
        self.assertIn("编号：WB-", html)

    def test_brand_default_injected(self):
        p = run_gen(sample_data(), self.out)
        html = open(self.out, encoding="utf-8").read()
        self.assertIn("Pipe CMS", html)
        self.assertIn('class="note about"', html)

    def test_filename_suggest_org_priority(self):
        p = run_gen(sample_data(), self.out)
        self.assertIn("FILENAME_SUGGEST: 网站体检报告-示例律所", p.stdout)

    def test_filename_suggest_from_full_name(self):
        d = sample_data()
        del d["org"]
        p = run_gen(d, self.out)
        self.assertIn("FILENAME_SUGGEST: 网站体检报告-示例律师事务所", p.stdout)

    def test_report_id_format(self):
        run_gen(sample_data(), self.out)
        html = open(self.out, encoding="utf-8").read()
        self.assertRegex(html, r"WB-\d{8}-[A-Za-z0-9]+")

    def test_missing_severity_fails_loudly(self):
        d = sample_data()
        del d["issues"][0]["severity"]
        p = run_gen(d, self.out)
        self.assertNotEqual(p.returncode, 0)   # 坏输入必须报错，不许出半成品


if __name__ == "__main__":
    unittest.main()
