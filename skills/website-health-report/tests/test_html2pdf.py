#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""html2pdf.py 测试：纯函数 + 端到端 PDF 冒烟（依赖本机中文字体与 fpdf2，缺则跳过）。"""
import os, re, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
sys.path.insert(0, SCRIPTS)
import html2pdf  # noqa: E402

HAS_FPDF = True
try:
    import fpdf  # noqa: F401
except ImportError:
    HAS_FPDF = False


class TestStripTags(unittest.TestCase):
    def test_br_and_p_become_newlines(self):
        self.assertEqual(html2pdf.strip_tags("a<br>b</p>c"), "a\nb\nc")

    def test_tags_removed_entities_unescaped(self):
        self.assertEqual(html2pdf.strip_tags("<b>一</b>&amp;二"), "一&二")

    def test_severity_span_stripped_from_title(self):
        """回归：标题里的严重度 span 必须剔掉，不能拼进标题文本"""
        title = '1. 标题 &nbsp;<span class="sev sev-h">较严重</span>'
        cleaned = html2pdf.strip_tags(re.sub(r"<span[^>]*>.*?</span>", "", title, flags=re.S))
        self.assertEqual(cleaned, "1. 标题")
        self.assertNotIn("较严重", cleaned)


class TestFontDetection(unittest.TestCase):
    def test_first_returns_existing(self):
        a = tempfile.NamedTemporaryFile(delete=False)
        a.close()
        try:
            self.assertEqual(html2pdf._first(["/no/such/path", a.name]), a.name)
        finally:
            os.unlink(a.name)

    def test_first_returns_none_when_missing(self):
        self.assertIsNone(html2pdf._first(["/no/such/1", "/no/such/2"]))


@unittest.skipUnless(HAS_FPDF, "fpdf2 not installed")
class TestEndToEndPDF(unittest.TestCase):
    def test_build_produces_valid_pdf(self):
        gen = os.path.join(SCRIPTS, "gen_report.py")
        tmp = tempfile.mkdtemp()
        data = os.path.join(tmp, "d.json")
        html_out = os.path.join(tmp, "r.html")
        pdf_out = os.path.join(tmp, "r.pdf")
        with open(data, "w", encoding="utf-8") as f:
            f.write("""
{"domain": "www.example.com", "org": "示例律所", "full_name": "示例律师事务所",
 "industry": "法律服务", "finding": "核心问题一句话", "checks_total": 24,
 "issues": [{"title": "问题一", "evidence": "证据一", "impact": "影响一",
             "fix": "修复一", "severity": "高"},
            {"title": "问题二", "evidence": "证据二", "impact": "影响二",
             "fix": "修复二", "severity": "改善项"}]}
""")
        r1 = subprocess.run([sys.executable, gen, data, html_out], capture_output=True, text=True)
        self.assertEqual(r1.returncode, 0, r1.stderr)
        try:
            r2 = subprocess.run([sys.executable, os.path.join(SCRIPTS, "html2pdf.py"),
                                 html_out, pdf_out], capture_output=True, text=True)
            if r2.returncode != 0:
                self.assertIn("中文字体", r2.stderr)   # 无字体环境必须明确报错，不许出缺字 PDF
                self.skipTest("no CJK font on this machine")
        except SystemExit:
            self.skipTest("no CJK font on this machine")
        self.assertTrue(os.path.exists(pdf_out))
        head = open(pdf_out, "rb").read(5)
        self.assertEqual(head, b"%PDF-")
        # 文本抽取验证：标题不含严重度字样、问题标题与 FAQ 都在
        try:
            import pypdfium2 as pdfium
        except ImportError:
            self.skipTest("pypdfium2 not installed")
        pdf = pdfium.PdfDocument(pdf_out)
        self.assertGreaterEqual(len(pdf), 2)            # 封面 + 至少一页正文
        text = "".join(pdf[i].get_textpage().get_text_range() for i in range(len(pdf)))
        self.assertIn("示例律师事务所", text)
        self.assertIn("常见问题", text)
        self.assertIn("1. 问题一", text)
        self.assertNotIn("问题一 较严重", text)          # 严重度标签不得混入标题行


if __name__ == "__main__":
    unittest.main()
