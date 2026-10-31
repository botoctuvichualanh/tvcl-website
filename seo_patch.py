#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vá SEO Phương án A lên HTML đầu ra (dùng chung dữ liệu seo_meta.py).
- /docs/*: cùng giá trị build.py sẽ sinh ra (để không phải rebuild toàn KB).
- /docs/sao-*, trang chủ, khóa học: trang không có generator → vá trực tiếp.
- Schema + og:image cho trang khóa học/dịch vụ/sự kiện.
Chạy lại nhiều lần an toàn (idempotent)."""
import re, html, json, os, sys
import seo_meta as M
ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://tuvichualanh.com"
OG_DEFAULT = f"{SITE}/assets/img/hero-shanshui.jpg"
ORG = {"@type": "Organization", "name": "Bộ Tộc Tử Vi Chữa Lành", "url": SITE}
QT = {"@type": "Person", "name": "Quán Trung", "jobTitle": "Tộc trưởng Bộ Tộc Tử Vi Chữa Lành"}

def rd(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()
def wr(p, s): open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)

def set_meta(path, title=None, desc=None, headline=None):
    s = rd(path); head, sep, body = s.partition("</head>")
    if title:
        head = re.sub(r"<title>.*?</title>", lambda m: f"<title>{html.escape(title, quote=False)}</title>", head, count=1, flags=re.S)
        head = re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*', lambda m: m.group(1) + html.escape(title), head)
    if headline:
        head = re.sub(r'("headline":\s*)"(?:[^"\\]|\\.)*"', lambda m: m.group(1) + json.dumps(headline, ensure_ascii=False), head)
    if desc:
        old = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', head).group(1))
        def meta_rep(m):
            return m.group(1) + html.escape(desc) if html.unescape(m.group(2)) == old else m.group(0)
        head = re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")([^"]*)', meta_rep, head)
        def ld_rep(m):
            return m.group(1) + json.dumps(desc, ensure_ascii=False) if json.loads(m.group(2)) == old else m.group(0)
        head = re.sub(r'("description":\s*)("(?:[^"\\]|\\.)*")', ld_rep, head)
    wr(path, head + sep + body)

def demote_h1(path):
    s = rd(path); n = [0]
    def rep(m):
        n[0] += 1
        return m.group(0) if n[0] == 1 else f"<h2{m.group(1) or ''}>{m.group(2)}</h2>"
    s2 = re.sub(r"<h1(\s[^>]*)?>([\s\S]*?)</h1>", rep, s)
    if s2 != s: wr(path, s2)

def add_head(path, snippet, marker):
    s = rd(path)
    if marker in s: return
    s = s.replace("</head>", snippet + "\n</head>", 1); wr(path, s)

def ldjson(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>"

def main():
    # 1) docs từ build.py
    for slug, m in M.DOCS_META.items():
        p = f"docs/{slug}.html"
        if not os.path.exists(os.path.join(ROOT, p)): print("skip", p); continue
        t = m.get("title")
        set_meta(p, title=(t + M.SUFFIX) if t else None, desc=m["desc"], headline=t)
    for p in ["docs/th1-tinh-hoa-tvcl.html", "docs/06-14-chinh-tinh.html"]:
        demote_h1(p)
    # 2) 26 trang sao
    for slug in M.STARS:
        t, d = M.star_meta(slug)
        set_meta(f"docs/{slug}.html", title=t, desc=d, headline=t[:-len(M.SUFFIX)])
    # 3) trang chủ + khóa học
    set_meta("index.html", desc=M.HOME_DESC)
    for p, d in M.PAGE_DESC.items(): set_meta(p, desc=d)
    # 4) schema + og
    add_head("khoa-hoc/luan-nhanh-tu-vi/index.html", ldjson({"@context": "https://schema.org", "@type": "Course",
        "name": "Luận Nhanh Lá Số Tử Vi", "url": f"{SITE}/khoa-hoc/luan-nhanh-tu-vi",
        "description": "Khóa học đơn giản, dễ hiểu, hướng dẫn từng bước để tự lập, đọc và hiểu lá số Tử Vi của chính mình.",
        "inLanguage": "vi", "image": f"{SITE}/assets/img/luan-nhanh-og.png", "provider": ORG}), '"@type": "Course"')
    add_head("luan-van-han/index.html", '<meta name="twitter:card" content="summary_large_image">\n' + ldjson({"@context": "https://schema.org", "@type": "Course",
        "name": "Luận Vận Hạn Tử Vi", "url": f"{SITE}/luan-van-han/",
        "description": "Khóa học dành cho người đã biết Tử Vi: hơn 80 video, 5 module thực hành, luận vận hạn trên chính lá số dưới góc nhìn chữa lành.",
        "inLanguage": "vi", "image": f"{SITE}/luan-van-han/assets/cong-dong.jpg", "provider": ORG, "instructor": QT}), '"@type": "Course"')
    add_head("tham-van-tinh-duyen/index.html", "\n".join([
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="Tham vấn Tình yêu &amp; Hôn nhân | Tử Vi Chữa Lành">',
        '<meta property="og:description" content="Lộ trình 3 buổi tham vấn 1:1 cùng Tộc trưởng Quán Trung: Tử Vi, Tâm lý học Tình yêu &amp; Đạo học. Hiểu mình, Thấy người, Chọn thời điểm.">',
        f'<meta property="og:url" content="{SITE}/tham-van-tinh-duyen/">',
        f'<meta property="og:image" content="{OG_DEFAULT}">',
        '<meta name="twitter:card" content="summary_large_image">',
        ldjson({"@context": "https://schema.org", "@type": "Service", "name": "Tham vấn Tình yêu & Hôn nhân",
            "serviceType": "Tham vấn Tử Vi Chữa Lành về tình duyên", "url": f"{SITE}/tham-van-tinh-duyen/",
            "description": "Lộ trình 3 buổi tham vấn 1:1 (90 phút) và 1 tháng đồng hành, kết hợp Tử Vi, Tâm lý học Tình yêu và Đạo học.",
            "provider": {**QT, "worksFor": ORG}, "areaServed": "VN", "availableChannel": {"@type": "ServiceChannel", "servicePhone": "+84856941341"}})]), 'og:image')
    add_head("su-kien-ban-do-nhan-qua-trong-tu-vi/index.html", ldjson({"@context": "https://schema.org", "@type": "Event",
        "name": "Bản Đồ Nhân Quả Trong Tử Vi", "url": f"{SITE}/su-kien-ban-do-nhan-qua-trong-tu-vi/",
        "description": "Sự kiện trực tuyến cùng Thầy Quán Trung: khám phá nguồn lực, mô thức và bài học cuộc đời qua cung Mệnh.",
        "startDate": "2026-10-01T19:30:00+07:00", "endDate": "2026-10-01T22:30:00+07:00",
        "eventAttendanceMode": "https://schema.org/OnlineEventAttendanceMode", "eventStatus": "https://schema.org/EventScheduled",
        "location": {"@type": "VirtualLocation", "url": f"{SITE}/su-kien-ban-do-nhan-qua-trong-tu-vi/"},
        "image": f"{SITE}/su-kien-ban-do-nhan-qua-trong-tu-vi/assets/preview-ban-do-nhan-qua.png",
        "organizer": ORG, "performer": QT,
        "offers": {"@type": "Offer", "price": "199000", "priceCurrency": "VND", "url": f"{SITE}/su-kien-ban-do-nhan-qua-trong-tu-vi/"}}), '"@type": "Event"')
    add_head("chinh-sach-bao-mat/index.html", "\n".join([
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="Chính sách bảo mật | Tử Vi Chữa Lành">',
        f'<meta property="og:url" content="{SITE}/chinh-sach-bao-mat/">',
        f'<meta property="og:image" content="{OG_DEFAULT}">']), 'og:image')
    print("done")

if __name__ == "__main__":
    main()
