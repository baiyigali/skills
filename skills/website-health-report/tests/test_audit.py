#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit.py 纯函数单元测试（不发任何网络请求）。"""
import os, sys, unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import audit  # noqa: E402


class TestExtractLinks(unittest.TestCase):
    BASE = "http://www.example.com/"

    def test_relative_join_and_dedup(self):
        page = '<a href="/news/a.html">x</a><a href="news/a.html">y</a><a href="/news/a.html/">z</a>'
        urls = audit.extract_links(page, self.BASE, "www.example.com")
        self.assertEqual(urls, ["http://www.example.com/news/a.html"])

    def test_non_http_scheme_dropped(self):
        page = ('<a href="javascript:void(0)">a</a><a href="mailto:a@b.com">b</a>'
                '<a href="tel:123">c</a><a href="data:x">d</a><a href="#top">e</a>')
        self.assertEqual(audit.extract_links(page, self.BASE, "www.example.com"), [])

    def test_external_domain_dropped(self):
        page = '<a href="https://other.com/news">x</a><a href="/news">y</a>'
        urls = audit.extract_links(page, self.BASE, "www.example.com")
        self.assertEqual(urls, ["http://www.example.com/news"])

    def test_static_assets_dropped(self):
        page = ('<a href="/logo.png">a</a><a href="/style.css">b</a><a href="/app.js">c</a>'
                '<a href="/doc.pdf">d</a><a href="/font.woff2">e</a><a href="/news">keep</a>')
        self.assertEqual(audit.extract_links(page, self.BASE, "www.example.com"),
                         ["http://www.example.com/news"])

    def test_scoring_news_over_about_over_shallow(self):
        page = ('<a href="/about">about</a>'
                '<a href="/news/2026/story.html">news</a>'
                '<a href="/misc">misc</a>')
        urls = audit.extract_links(page, self.BASE, "www.example.com")
        # 新闻详情页（内容分3+深度分1）> 关于页（2）> 普通页（0）
        self.assertEqual(urls[0], "http://www.example.com/news/2026/story.html")
        self.assertEqual(urls[1], "http://www.example.com/about")
        self.assertIn("http://www.example.com/misc", urls)

    def test_chinese_slug_keywords_scored(self):
        page = '<a href="/zixun/list.html">资讯</a><a href="/gywm">关于我们</a>'
        urls = audit.extract_links(page, self.BASE, "www.example.com")
        self.assertEqual(urls[0], "http://www.example.com/zixun/list.html")


class TestDnsAlive(unittest.TestCase):
    def test_alive_true(self):
        with mock.patch("socket.gethostbyname", return_value="1.2.3.4"):
            self.assertTrue(audit.dns_alive("ok.example.com"))

    def test_dead_false(self):
        with mock.patch("socket.gethostbyname", side_effect=OSError("nx")):
            self.assertFalse(audit.dns_alive("dead.example.com"))


if __name__ == "__main__":
    unittest.main()
