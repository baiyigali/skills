#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""技能版报告 HTML→PDF（fpdf2）：品牌封面页 + 严重度色条 + 品牌蓝表格，跨系统字体自动探测。

用法:
    python3 html2pdf.py <in.html> <out.pdf> [--brand-file <path>]

字体策略（不打包字体文件，运行时按系统探测，取第一个存在的）:
    macOS   正文 /Library/Fonts/Arial Unicode.ttf；标题 /System/Library/Fonts/STHeiti Medium.ttc
    Windows 正文 C:\\Windows\\Fonts\\msyh.ttc（微软雅黑）；标题 msyhbd.ttc
    Linux   Noto Sans CJK / 思源黑体（自动 glob /usr/share/fonts 与 ~/.fonts）
    找不到中文字体 → 报错退出并提示安装 Noto Sans CJK，绝不缺字硬出。

依赖: pip install fpdf2（建议装在独立 venv）
"""
import re, sys, os, glob, json, html as H, platform, argparse
from fpdf import FPDF
from fpdf.fonts import FontFace

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------- 字体探测 ----------
def _first(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None

def _linux_cjk():
    pats = ["/usr/share/fonts/**/NotoSansCJK*", "/usr/share/fonts/**/SourceHanSans*",
            "/usr/share/fonts/**/noto*cjk*", os.path.expanduser("~/.fonts/**/*CJK*"),
            "/usr/share/fonts/**/wqy-microhei*"]
    hits = []
    for pat in pats:
        hits += glob.glob(pat, recursive=True)
    # 优先 Regular/普通体
    hits.sort(key=lambda p: (("Regular" not in p), ("Bold" in p or "bold" in p)))
    return hits

def find_fonts():
    """返回 (body, bold) 字体路径；找不到中文字体时抛 SystemExit"""
    s = platform.system()
    if s == "Darwin":
        body = _first(["/Library/Fonts/Arial Unicode.ttf",
                       "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"])
        bold = _first(["/System/Library/Fonts/STHeiti Medium.ttc",
                       "/System/Library/Fonts/PingFang.ttc",
                       "/System/Library/Fonts/Hiragino Sans GB.ttc"])
    elif s == "Windows":
        body = _first([r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyh.ttf",
                       r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simsun.ttc"])
        bold = _first([r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\simhei.ttf",
                       r"C:\Windows\Fonts\msyh.ttc"])
    else:  # Linux 及其他
        cjk = _linux_cjk()
        body = cjk[0] if cjk else None
        bold = next((p for p in cjk if re.search(r"(Bold|bold)", p)), body)
    if not body:
        raise SystemExit("未找到中文字体。请安装 Noto Sans CJK（Linux: "
                         "apt install fonts-noto-cjk / macOS、Windows 自带中文字体）后重试。")
    if not bold:
        print("WARN: 未找到独立粗体字体，标题将以正文字体渲染", file=sys.stderr)
        bold = body
    return body, bold

# ---------- HTML 解析 ----------
def strip_tags(s):
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</p>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return H.unescape(s).strip()

BRAND = (44, 90, 160)

class PDF(FPDF):
    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_font("cjk", "", 8.5)
        self.set_text_color(150, 150, 150)
        label = f"{self._brand_name} · 网站健康体检 · 第 {self.page_no()} 页" if self._brand_name \
            else f"网站健康体检 · 第 {self.page_no()} 页"
        self.cell(0, 8, label, align="C")

def build(src, dst, brand_file=None):
    doc = open(src, encoding="utf-8").read()

    # 品牌信息：从 brand.json 读；无品牌块（HTML 无 about 块）时用无品牌页脚/声明
    brand = {"name": "", "disclaimer": "本报告基于公开信息层面的只读检测，不涉及任何侵入性操作。"}
    has_brand = '<div class="note about">' in doc
    if brand_file and os.path.exists(brand_file):
        brand = json.load(open(brand_file, encoding="utf-8"))

    org = strip_tags(re.search(r"<h1>(.*?)</h1>", doc, re.S).group(1))
    org = org.replace(" · 网站健康体检报告", "")
    sub = strip_tags(re.search(r'<div class="sub">(.*?)</div>', doc, re.S).group(1))
    summary = ""
    m = re.search(r'<div class="note"><b>结论摘要：</b>(.*?)</div>', doc, re.S)
    if m:
        summary = strip_tags(m.group(1))

    body_font, bold_font = find_fonts()
    pdf = PDF()
    pdf._brand_name = brand["name"] if has_brand else ""
    pdf.set_auto_page_break(True, margin=16)
    pdf.add_font("cjk", "", body_font)
    pdf.add_font("cjk", "B", bold_font)
    pdf.add_font("cjkb", "", bold_font)
    pdf.add_font("cjkb", "B", bold_font)
    pdf.set_margins(18, 16, 18)

    # ---------- 封面页 ----------
    pdf.add_page()
    w = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_fill_color(*BRAND)
    pdf.rect(pdf.l_margin, 16, w, 92, "F")
    pdf.set_xy(pdf.l_margin + 10, 24)
    pdf.set_font("cjk", "", 9.5)
    pdf.set_text_color(235, 240, 250)
    top_label = f"{brand['name']}  ｜  网 站 健 康 体 检" if has_brand else "网 站 健 康 体 检"
    pdf.cell(0, 6, top_label, align="L")
    pdf.set_xy(pdf.l_margin + 10, 42)
    pdf.set_font("cjkb", "", 22)
    pdf.set_text_color(255, 255, 255)
    pdf.multi_cell(w - 20, 10.5, org, align="L")
    pdf.set_xy(pdf.l_margin + 10, pdf.get_y() + 4)
    pdf.set_font("cjk", "", 13.5)
    pdf.set_text_color(220, 230, 248)
    pdf.cell(0, 8, "网 站 健 康 体 检 报 告", align="L")

    # 摘要框
    y = 128
    pdf.set_fill_color(247, 248, 250)
    pdf.set_draw_color(*BRAND)
    pdf.set_line_width(0.6)
    pdf.set_font("cjk", "", 11)
    pdf.set_text_color(40, 40, 40)
    lines = pdf.multi_cell(w - 18, 6.2, summary, dry_run=True, output="LINES")
    sh = len(lines) * 6.2 + 14
    pdf.rect(pdf.l_margin, y, w, sh, "DF")
    pdf.set_xy(pdf.l_margin + 9, y + 7)
    pdf.multi_cell(w - 18, 6.2, summary, align="L")

    # 元信息（按 ｜ 和换行同时切分，每条独立成行、各带圆点）
    pdf.set_y(y + sh + 14)
    for part in re.split(r"｜|\n", sub):
        part = part.strip()
        if not part:
            continue
        pdf.set_x(pdf.l_margin + 2)
        pdf.set_font("cjkb", "", 11)
        pdf.set_text_color(*BRAND)
        pdf.cell(7, 7.5, "•", align="L")
        pdf.set_x(pdf.l_margin + 9)
        pdf.set_font("cjk", "", 11)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 7.5, part, align="L")

    # 底部声明
    pdf.set_y(-48)
    pdf.set_font("cjk", "", 9)
    pdf.set_text_color(140, 140, 140)
    disclaimer = brand.get("disclaimer") if has_brand else brand.get("disclaimer_nobrand", brand["disclaimer"])
    pdf.multi_cell(0, 5.5, disclaimer, align="L")

    # ---------- 正文 ----------
    pdf.add_page()

    def note_box(txt, about=False):
        bg, border = ((240, 245, 252), BRAND) if about else ((247, 248, 250), (44, 90, 160))
        pdf.set_fill_color(*bg)
        pdf.set_draw_color(*border)
        pdf.set_line_width(0.5)
        y = pdf.get_y()
        pdf.set_font("cjk", "", 11)
        pdf.set_text_color(40, 40, 40)
        w2 = pdf.w - pdf.l_margin - pdf.r_margin
        lines = pdf.multi_cell(w2 - 10, 6, txt, dry_run=True, output="LINES")
        hgt = len(lines) * 6 + 13
        if y + hgt > pdf.h - 18:
            pdf.add_page(); y = pdf.get_y()
        pdf.rect(pdf.l_margin, y, w2, hgt, "DF")
        if about:
            pdf.set_fill_color(*BRAND)
            pdf.rect(pdf.l_margin, y, 2.6, hgt, "F")
        pdf.set_xy(pdf.l_margin + 6, y + 5.5)
        pdf.multi_cell(w2 - 12, 6, txt, align="L")
        pdf.set_y(y + hgt + 5)

    marks = [(m.start(), m.group(0)) for m in re.finditer(
        r'<h2>|<div class="note"[^>]*>|<div class="issue" data-sev="[^"]*">|<table class="faq">', doc)]
    end_of_body = doc.find("</body>") if "</body>" in doc else len(doc)
    for idx, (pos, tag) in enumerate(marks):
        nxt = marks[idx + 1][0] if idx + 1 < len(marks) else end_of_body
        seg = doc[pos:nxt]
        if tag == "<h2>":
            pdf.ln(3)
            pdf.set_x(pdf.l_margin)
            pdf.set_font("cjkb", "", 15)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 8, strip_tags(re.sub(r"</?h2>", "", seg)), align="L")
            pdf.ln(1.5)
        elif tag.startswith('<div class="note'):
            inner = re.sub(r'^<div class="note"[^>]*>|</div>\s*$', "", seg.strip())
            txt = strip_tags(inner)
            note_box(txt, about="about" in tag)
        elif tag.startswith('<div class="issue"'):
            sev = (re.search(r'data-sev="([^"]*)"', tag)).group(1)
            sev_color = {"高": (176, 58, 46), "中": (185, 119, 14), "低": (58, 125, 68)}.get(sev, (120, 120, 120))
            sev_label = {"高": "较严重", "中": "中等", "低": "改善项"}.get(sev, "")
            m = re.search(r"<h3>(.*?)</h3>", seg, re.S)
            ev = re.search(r'<div class="ev">(.*?)</div>', seg, re.S)
            im = re.search(r'<div class="im">(.*?)</div>', seg, re.S)
            fx = re.search(r'<div class="fx">(.*?)</div>', seg, re.S)
            y = pdf.get_y()
            w2 = pdf.w - pdf.l_margin - pdf.r_margin

            def nlines(txt, width, font, style, size, lh):
                pdf.set_font(font, style, size)
                return len(pdf.multi_cell(width, lh, txt, dry_run=True, output="LINES"))

            title_html = re.sub(r"<span[^>]*>.*?</span>", "", m.group(1), flags=re.S)  # 剔掉严重度标签
            title_txt = strip_tags(title_html)
            title_l = nlines(title_txt, w2 - 14, "cjkb", "", 12.5, 6.6)
            ev_l = nlines(strip_tags(ev.group(1)), w2 - 14, "cjk", "", 10.5, 5.8) if ev else 0
            im_l = nlines(strip_tags(im.group(1)), w2 - 14, "cjk", "", 11, 6) if im else 0
            fx_txt = strip_tags(fx.group(1)) if fx else ""
            fx_l = nlines(fx_txt, w2 - 20, "cjk", "", 10.5, 5.6) if fx else 0
            hgt = 5 + title_l * 6.6 + (6.5 if sev_label else 0) + (1 + ev_l * 5.8 if ev else 0) \
                + (1 + im_l * 6 if im else 0) + (2 + fx_l * 5.6 + 8 if fx else 0) + 6
            if y + hgt > pdf.h - 18:
                pdf.add_page(); y = pdf.get_y()
            pdf.set_draw_color(227, 232, 240)
            pdf.set_line_width(0.4)
            pdf.rect(pdf.l_margin, y, w2, hgt, "D")
            pdf.set_fill_color(*sev_color)
            pdf.rect(pdf.l_margin, y, 2.6, hgt, "F")
            pdf.set_xy(pdf.l_margin + 9, y + 5)
            pdf.set_font("cjkb", "", 12.5)
            pdf.set_text_color(25, 25, 25)
            pdf.multi_cell(w2 - 16, 6.6, title_txt, align="L")
            if sev_label:
                pdf.set_font("cjk", "", 9.5)
                pdf.set_text_color(*sev_color)
                pdf.set_x(pdf.l_margin + 9)
                pdf.cell(34, 5.5, "■ " + sev_label, align="L")
                pdf.ln(6.5)
            else:
                pdf.ln(1)
            if ev:
                pdf.set_font("cjk", "", 10.5)
                pdf.set_text_color(90, 90, 90)
                pdf.set_x(pdf.l_margin + 9)
                pdf.multi_cell(w2 - 16, 5.8, strip_tags(ev.group(1)), align="L")
                pdf.ln(1.5)
            if im:
                pdf.set_font("cjk", "", 11)
                pdf.set_text_color(40, 40, 40)
                pdf.set_x(pdf.l_margin + 9)
                pdf.multi_cell(w2 - 16, 6, strip_tags(im.group(1)), align="L")
                pdf.ln(1.5)
            if fx:
                pdf.set_fill_color(240, 247, 242)
                pdf.set_draw_color(26, 92, 46)
                pdf.set_line_width(0.3)
                fh = fx_l * 5.6 + 8
                fy = pdf.get_y()
                pdf.rect(pdf.l_margin + 9, fy, w2 - 16, fh, "DF")
                pdf.set_xy(pdf.l_margin + 12, fy + 4)
                pdf.set_text_color(26, 92, 46)
                pdf.multi_cell(w2 - 22, 5.6, fx_txt, align="L")
            pdf.set_y(y + hgt + 6)
        else:  # faq table
            rows = re.findall(r"<tr>(.*?)</tr>", seg, re.S)
            data = []
            for r in rows:
                cells = [strip_tags(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", r, re.S)]
                data.append(cells)
            if data:
                pdf.ln(1.5)
                pdf.set_font("cjk", "", 10.5)
                pdf.set_text_color(40, 40, 40)
                head = FontFace(family="cjkb", emphasis="BOLD", color=(255, 255, 255), fill_color=BRAND)
                with pdf.table(col_widths=(62, 118), text_align="LEFT", line_height=6,
                               borders_layout="ALL", padding=2.2,
                               headings_style=head, cell_fill_color=(246, 248, 251),
                               cell_fill_mode="ROWS") as t:
                    for i, row in enumerate(data):
                        tr = t.row()
                        for c in row:
                            if i == 0:
                                tr.cell(c, style=head)
                            else:
                                tr.cell(c)
                pdf.ln(2.5)

    pdf.output(dst)
    print("OK", dst)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--brand-file", default=os.path.join(SKILL, "brand.json"))
    a = ap.parse_args()
    build(a.src, a.dst, a.brand_file)
