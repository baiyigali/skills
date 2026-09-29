#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""网站深度体检（技能版）：对任意域名做 DNS/TLS/HTTPS/页面信号检查 + 内页抽查（默认共 ≤10 页），输出 JSON。

用法:
    python3 audit.py <domain 或 URL> [-o out.json] [--pages 10] [--org 机构名] [--industry 行业]

输出 JSON 结构（供 gen_report.py 与人工分析使用）:
{
  "domain": ..., "org": ..., "industry": ..., "date": ...,
  "checks": { A1_https_code, A2_cert, A2_issuer, A3_notAfter, A4_http_redirect, A6_hsts,
               B1_title, B2_description, B3_h1_count, B4_viewports, B5_robots_code,
               B5_sitemap_code, B7_404_code, C1_copyright, C3_phones, C3_emails,
               D1_icp, D4_load_sec, E1_fingerprint, A5_http_assets, dns_alive, page_error },
  "pages": [ {url, status, title, h1_count, latest_year, load_sec}, ... ]
}

纪律：只读检测（GET/HEAD），不登录、不提交表单、不做任何注入测试。
"""
import subprocess, json, re, os, socket, sys, argparse, time
from urllib.parse import urlparse, urljoin

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")
T = 18

def curl(args, timeout=T + 6):
    return subprocess.run(args, capture_output=True, timeout=timeout)

def curl_page(url):
    """带 cookie 罐二跳抓取（应对 JS 设 cookie 防爬），按声明的 charset 解码"""
    jar = f"/tmp/wb_audit_jar_{abs(hash(url))}.txt"
    try:
        curl(["curl", "-sL", "--compressed", "--max-time", str(T), "-A", UA,
              "-c", jar, "-b", jar, url])
        p = curl(["curl", "-sL", "--compressed", "--max-time", str(T), "-A", UA,
                  "-c", jar, "-b", jar, url])
        raw = p.stdout
    finally:
        try: os.remove(jar)
        except OSError: pass
    if p.returncode != 0 or not raw:
        return None
    m = re.search(rb'charset=["\']?([\w-]+)', raw[:2000], re.I)
    enc = (m.group(1).decode() if m else "utf-8").lower()
    for e in (enc, "utf-8", "gb18030"):
        try:
            return raw.decode(e)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", "ignore")

def dns_alive(domain):
    try:
        socket.gethostbyname(domain)
        return True
    except OSError:
        return False

def cert_info(domain):
    """证书 subject/issuer/有效期。443 失败可能为无证书或网络阻断，输出注明。"""
    cmd = (f'echo | openssl s_client -connect {domain}:443 -servername {domain} 2>/dev/null '
           f'| openssl x509 -noout -subject -issuer -dates 2>/dev/null')
    try:
        p = curl(["bash", "-c", cmd])
        out = p.stdout.decode().strip()
        if not out:
            return "NO_TLS_RESPONSE（无证书或网络阻断，需在境内网络人工复核）", "-", "-"
        subj = re.search(r"subject=.*", out)
        issuer = re.search(r"issuer=.*", out)
        dates = re.search(r"notAfter=(.+)", out)
        return (subj.group(0)[:120] if subj else "unknown",
                issuer.group(0)[:120] if issuer else "unknown",
                dates.group(1).strip() if dates else "-")
    except Exception as e:
        return f"ERR:{e}", "-", "-"

def extract_links(page, base_url, domain):
    """抽取同域名内部链接，按内容价值打分排序"""
    seen, scored = set(), []
    for href in re.findall(r'href=["\'](.*?)["\']', page, re.I):
        href = href.strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
            continue
        url = urljoin(base_url, href).split("#")[0].rstrip("/")
        if not url or url in seen:
            continue
        pu = urlparse(url)
        if pu.scheme not in ("http", "https") or domain not in pu.netloc:
            continue
        if re.search(r"\.(jpg|jpeg|png|gif|css|js|ico|pdf|zip|rar|mp4|woff2?|ttf|svg)$", pu.path, re.I):
            continue
        seen.add(url)
        score = 0
        if re.search(r"(news|article|info|detail|view|show|content|post|blog|zixun|xinwen|gonggao|dongtai)", url, re.I):
            score += 3
        if re.search(r"(about|jianjie|gywm|intro|team|fuwu|service|product|chanpin|case|anli)", url, re.I):
            score += 2
        if pu.path.count("/") >= 2:          # 更深层路径通常是有内容的详情页
            score += 1
        scored.append((score, url))
    scored.sort(key=lambda x: -x[0])
    return [u for _, u in scored]

def sample_pages(domain, homepage_html, base_url, limit=9):
    """内页抽查：返回每页状态/标题/H1/最新年份提及/加载耗时"""
    urls = extract_links(homepage_html, base_url, domain)[:limit]
    out = []
    for u in urls:
        item = {"url": u}
        p = curl(["curl", "-s", "-o", "/dev/null", "--max-time", str(T), "-A", UA,
                  "-w", "%{http_code} %{time_total}", u])
        if p.returncode == 0:
            code, _, sec = p.stdout.decode().strip().partition(" ")
            item["status"] = code
            item["load_sec"] = sec
        else:
            item["status"] = "FAIL"
        page = curl_page(u) or ""
        if page:
            m = re.search(r"<title[^>]*>(.*?)</title>", page, re.I | re.S)
            item["title"] = re.sub(r"\s+", " ", m.group(1)).strip()[:100] if m else "MISSING"
            item["h1_count"] = len(re.findall(r"<h1[\s>]", page, re.I))
            years = re.findall(r"20\d{2}", page)
            item["latest_year"] = max(years) if years else ""
            # 内页内容更新信号：页面里提到的最新日期（如新闻日期）
            dates = re.findall(r"20\d{2}[-/年.]\d{1,2}[-/月.]\d{1,2}", page)
            item["latest_date"] = max(dates) if dates else ""
        else:
            item["title"] = "FETCH_FAILED"
        out.append(item)
        print(f"  page: {u} -> {item.get('status')} {item.get('title', '')[:40]}", file=sys.stderr)
    return out

def check_site(domain, max_pages=10):
    r = {"domain": domain, "checks": {}}
    c = r["checks"]
    c["dns_alive"] = dns_alive(domain)

    p = curl(["curl", "-sI", "--max-time", "10", f"https://{domain}/", "-o", "/dev/null",
              "-w", "%{http_code}"])
    c["A1_https_code"] = p.stdout.decode().strip() if p.returncode == 0 else "NO_TLS"

    c["A2_cert"], c["A2_issuer"], c["A3_notAfter"] = cert_info(domain)

    p = curl(["curl", "-sIL", "--max-time", str(T), "-A", UA, f"http://{domain}/",
              "-o", "/dev/null", "-w", "%{http_code} %{url_effective}"])
    c["A4_http_redirect"] = p.stdout.decode().strip() if p.returncode == 0 else "FAIL"

    p = curl(["curl", "-sI", "--max-time", "10", f"https://{domain}/"])
    c["A6_hsts"] = "yes" if b"strict-transport" in p.stdout.lower() else "no"

    page = curl_page(f"http://{domain}/") or curl_page(f"https://{domain}/") or ""
    base_url = f"http://{domain}/"
    if page:
        c["A5_http_assets"] = len(set(re.findall(
            r'(?:src|href)=["\']http://[^"\']+\.(?:css|js|jpg|png|gif)', page, re.I)))
        m = re.search(r"<title[^>]*>(.*?)</title>", page, re.I | re.S)
        c["B1_title"] = re.sub(r"\s+", " ", m.group(1)).strip()[:120] if m else "MISSING"
        m = (re.search(r'name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', page, re.I)
             or re.search(r'content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', page, re.I))
        c["B2_description"] = m.group(1).strip()[:150] if m else "MISSING"
        c["B3_h1_count"] = len(re.findall(r"<h1[\s>]", page, re.I))
        c["B4_viewports"] = re.findall(r'name=["\']viewport["\'][^>]*content=["\']([^"\']*)["\']', page, re.I)
        m = re.findall(r"(?:©|版权所有|Copyright)[^<>\n]{0,40}", page, re.I)
        c["C1_copyright"] = sorted(set(x.strip()[:60] for x in m))[:3]
        tels = sorted(set(re.findall(r"(?:1[3-9]\d{9}|0\d{2,3}-\d{7,8}|400-?\d{3,4}-?\d{3,4})", page)))[:5]
        mails = sorted(set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", page)))
        mails = [m for m in mails if not m.lower().endswith((".png", ".jpg", ".gif", ".css", ".js"))][:5]
        c["C3_phones"] = tels
        c["C3_emails"] = mails
        m = re.search(r"([京津沪渝冀晋辽吉黑苏浙皖闽赣鲁豫鄂湘粤桂琼川黔云陕甘青宁新]ICP备\s*\d+号(?:-\d+)?)", page)
        c["D1_icp"] = m.group(1) if m else "NOT_FOUND"
        p = curl(["curl", "-sL", "-o", "/dev/null", "--max-time", str(T), "-A", UA,
                  "-w", "%{time_total}", f"http://{domain}/"])
        c["D4_load_sec"] = p.stdout.decode().strip() if p.returncode == 0 else "?"
        fp = []
        if re.search(r"\.aspx?[\s\"'?]", page, re.I): fp.append("ASP/ASPX")
        if re.search(r"\.jsp[\s\"'?]", page, re.I): fp.append("JSP")
        if "col.jsp" in page: fp.append("凡科(col.jsp)")
        m = re.search(r"Powered\s*by\s*[^<\s]{1,30}", page, re.I)
        if m: fp.append(m.group(0)[:40])
        c["E1_fingerprint"] = fp

        # JS 渲染壳识别（curl 拿不到有效内容的信号，报告里需人工/浏览器复核）
        text_len = len(re.sub(r"<[^>]+>", "", re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", "", page)))
        c["render_hint"] = ("JS_RENDER_SHELL_SUSPECT（正文文本过少，需浏览器实测）"
                            if text_len < 500 else "ok")
    else:
        c["page_error"] = "PAGE_FETCH_FAILED"

    p = curl(["curl", "-s", "--max-time", "10", f"http://{domain}/robots.txt", "-o", "/dev/null", "-w", "%{http_code}"])
    c["B5_robots_code"] = p.stdout.decode().strip() if p.returncode == 0 else "?"
    p = curl(["curl", "-s", "--max-time", "10", f"http://{domain}/sitemap.xml", "-o", "/dev/null", "-w", "%{http_code}"])
    c["B5_sitemap_code"] = p.stdout.decode().strip() if p.returncode == 0 else "?"
    p = curl(["curl", "-s", "--max-time", "10", f"http://{domain}/wb-audit-nonexist-xyz/", "-o", "/dev/null", "-w", "%{http_code}"])
    c["B7_404_code"] = p.stdout.decode().strip() if p.returncode == 0 else "?"

    # 内页抽查（含首页在内共约 max_pages 页）
    if page:
        inner = sample_pages(domain, page, base_url, limit=max(1, max_pages - 1))
        r["pages"] = inner
    return r

def normalize_domain(s):
    s = s.strip()
    if "://" in s:
        s = urlparse(s).netloc or s
    return s.split("/")[0].strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="域名或 URL")
    ap.add_argument("-o", "--out", default=None, help="输出 JSON 路径（默认 stdout）")
    ap.add_argument("--pages", type=int, default=10, help="体检页面总数上限（默认 10）")
    ap.add_argument("--org", default="", help="机构名（可选）")
    ap.add_argument("--industry", default="", help="行业（可选）")
    a = ap.parse_args()

    domain = normalize_domain(a.target)
    print(f"auditing {domain} (max {a.pages} pages) ...", file=sys.stderr)
    result = check_site(domain, max_pages=a.pages)
    result["org"] = a.org
    result["industry"] = a.industry
    result["date"] = time.strftime("%Y-%m-%d")

    js = json.dumps(result, ensure_ascii=False, indent=1)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(js)
        print(f"saved {a.out}", file=sys.stderr)
    else:
        print(js)

if __name__ == "__main__":
    main()
