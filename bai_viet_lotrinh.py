#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Giao diện /bai-viet/ theo chuẩn trang Lộ trình Hành nghề TVCL (30/10/2026).

Được gọi từ build_bai_viet.py. Dữ liệu: 03_tuvichualanh_80_articles_database.json
+ kb_digest.json (trích từ Core MD v3.2.0 bằng kb_extract.py).
"""
from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "_bai-viet-source"
OUT = ROOT / "bai-viet"
SITE = "https://tuvichualanh.com"
CSS_URL = "/bai-viet/assets/tvcl-bv.css?v=20261030"
LOGO_URL = "/bai-viet/assets/logo-tvcl.webp"
SLOGAN = "Tử Vi Chữa Lành: Ứng dụng Tử Vi, Tâm Lý, Đạo Học để Hiểu Mình, Cải Mệnh &amp; Chữa Lành"
TAGLINE = "Lá số là bản đồ, không phải bản án."
KCYCLE = ["k2", "k1", "k3", "k4", "k5"]
CAT_K = {"goc-nhin-moi": "k1", "luan-tri-thuc": "k2", "la-so-van-han": "k3", "tam-ly-dao-hoc": "k4", "tam-thuc-tai-chinh": "k5"}
COURSE_LINKS = [
    ("Luận Nhanh", "/khoa-hoc/luan-nhanh-tu-vi/", "Xem khóa Luận Nhanh"),
    ("Bí Kíp", "/khoa-hoc-tu-vi-bi-kip-chua-lanh/", "Xem khóa Bí Kíp Chữa Lành"),
    ("Vận Hạn", "/luan-van-han/", "Xem khóa Luận Vận Hạn"),
    ("Tình Duyên", "/tham-van-tinh-duyen/", "Tìm hiểu tham vấn Tình Duyên"),
    ("Tài Lộc", "/khoa-hoc/", "Xem các khóa học"),
    ("Tử Vi Chữa Lành", "/khoa-hoc-tu-vi-chua-lanh/", "Xem khóa Tử Vi Chữa Lành"),
]
STEP_NAMES = ["Sao · Gốc", "Duyên · Bối cảnh", "Tâm · Nhận thức", "Hành · Phương pháp", "Quả · Chuyển hóa"]


def esc(v):
    return html.escape(str(v or ""), quote=True)


def jscript(v):
    return json.dumps(v, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def url_of(a):
    return f"/bai-viet/{a['category']}/{a['id']}/"


def strip_links(text):
    return re.sub(r"\[([^\]]+)\]\(wiki:[^)]+\)", r"\1", text or "")


def short_cat(name):
    return re.sub(r"^\d+\.\s*", "", name or "")


def hero_svg():
    return (SOURCE / "hero-shanshui.svg.html").read_text(encoding="utf-8")


def head(title, description, canonical, og_type, extra=""):
    return f'''<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="Tử Vi Chữa Lành — Bộ tộc Tử Vi Chữa Lành">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{SITE}/assets/img/hero-shanshui.jpg"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{LOGO_URL}" type="image/webp">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="{CSS_URL}">
{extra}
</head>'''


def footer():
    return f'''<footer>
  <div class="wrap stack" style="gap:6px">
    <img class="logo sm" src="{LOGO_URL}" alt="" width="64" height="64" loading="lazy">
    <p class="brand">Bộ tộc Tử Vi Chữa Lành</p>
    <p>{SLOGAN}</p>
    <p>“{TAGLINE}” · <a href="https://www.facebook.com/tuvichualanh/" target="_blank" rel="noopener">Fanpage</a> · <a href="https://www.facebook.com/groups/congdongtuvichualanh" target="_blank" rel="noopener">Cộng đồng Facebook</a> · <a href="/bai-viet/">Thư viện bài viết</a> · <a href="/lo-trinh-hanh-nghe-tvcl/">Lộ trình học</a> · <a href="/">tuvichualanh.com</a></p>
  </div>
</footer>'''


def path_strip(label="Chuỗi chuyển hóa nhân quả"):
    names = ["Sao", "Duyên", "Tâm", "Hành", "Nghiệp", "Vận", "Quả", "Chuyển hóa"]
    out = []
    for i, n in enumerate(names):
        cls = "pill end k5" if i == len(names) - 1 else f"pill {['k1', 'k2', 'k3', 'k4', 'k1', 'k2', 'k3'][i]}"
        out.append(f'<span class="{cls}">{n}</span>')
    return f'<div class="path-strip" aria-label="{label}">' + '<span class="arrow">→</span>'.join(out) + "</div>"


# ───────────────────────── Bài viết ─────────────────────────

def parse_axes(text):
    plain = strip_links(text)
    rows, role = [], ""
    for m in re.finditer(r"(Bản cung|Đối cung|Tam hợp|Nhị hợp|Giáp cung|Xung chiếu)?\s*([^()↔&]+?)\s*\((\d+)\s*%\)", plain):
        name = m.group(2).strip(" ,:-–")
        pm = re.match(r"^(Bản cung|Đối cung|Tam hợp|Nhị hợp|Giáp cung|Xung chiếu)\s+(.+)$", name)
        if pm:
            role, name = pm.group(1), pm.group(2)
        elif m.group(1):
            role = m.group(1)
        rows.append((name, role or "Liên kết", int(m.group(3))))
    return rows


def axes_html(article):
    rows = parse_axes(article.get("chart3P4CAxes", ""))
    if len(rows) < 2:
        plain = strip_links(article.get("chart3P4CAxes", ""))
        nodes, last = [], 0
        for m in re.finditer(r"([^()↔←→&]+?)\s*\(([^)]+)\)", plain):
            sep = plain[last:m.start()].strip()
            name = m.group(1).strip(" ,:-–")
            if nodes or sep:
                nodes.append(f'<span class="nsep">{esc(sep[:2] if sep else "·")}</span>')
            nodes.append(f'<div class="node-card {KCYCLE[len(nodes) // 2 % 5]}"><b>{esc(name)}</b><span>{esc(m.group(2))}</span></div>')
            last = m.end()
        tail = plain[last:].strip()
        if len([x for x in nodes if "node-card" in x]) >= 2:
            cap = f'<p class="axis-cap">{esc(tail)}</p>' if tail else ""
            return f'<div class="nodes">{"".join(nodes)}</div>{cap}'
        parts = [x.strip() for x in re.split(r"\s+[·×↔→←]\s+", plain) if x.strip()]
        seps = re.findall(r"\s+([·×↔→←])\s+", plain)
        if len(parts) >= 2:
            out = []
            for i, part in enumerate(parts):
                if i:
                    out.append(f'<span class="nsep">{esc(seps[i - 1] if i - 1 < len(seps) else "·")}</span>')
                m = re.match(r"^(.*?)\s*\(([^)]+)\)\s*$", part)
                inner = f"<b>{esc(m.group(1))}</b><span>{esc(m.group(2))}</span>" if m else f"<b>{esc(part)}</b>"
                out.append(f'<div class="node-card {KCYCLE[i % 5]}">{inner}</div>')
            return f'<div class="nodes">{"".join(out)}</div>'
        return f'<div class="pass"><b>{esc(plain)}</b></div>'
    ks = ["k2", "k1", "k4", "k3", "k5", "k2"]
    return '<div class="axis">' + "".join(
        f'<div class="ax {ks[i % len(ks)]}"><span class="lbl">{esc(n)} <small>{esc(r)}</small></span>'
        f'<span class="bar"><i style="width:{min(p, 100)}%"></i></span><span class="pct">{p}%</span></div>'
        for i, (n, r, p) in enumerate(rows)) + "</div>"


def steps_html(article, md):
    steps = article.get("causalFlow5Steps", [])
    out = []
    for i, s in enumerate(steps):
        k = f"k{min(i + 1, 5)}"
        dot = "✦" if i == len(steps) - 1 else str(i + 1)
        raw = (s.get("step") or "").replace("/", "·").title()
        name = STEP_NAMES[i] if i < len(STEP_NAMES) and len(steps) == 5 else raw
        desc = md(s.get("description", "")).replace("<p>", "").replace("</p>", "")
        out.append(f'<div class="course {k}"><div class="node"><div class="dot">{dot}</div><div class="rail"></div></div>'
                   f'<div class="cbody"><h3 class="cname">{esc(name)}</h3><p class="step-sm">{desc}</p></div></div>')
    return "".join(out)


def kb_html(article, kb, wiki):
    blocks = []
    for key in article.get("tags", []):
        if key not in kb or key.startswith("_"):
            continue
        entry, w = kb[key], wiki.get(key, {})
        title = w.get("title") or entry["items"][0]["name"]
        typ = (w.get("type") or "").split("·")[0].strip().upper() or "TÀNG KINH CÁC"
        rows = []
        if w.get("summary"):
            rows.append(("Tóm lược", esc(w["summary"])))
        for it in entry["items"]:
            pre = f"<b>{esc(it['name'])}</b> · " if len(entry["items"]) > 1 else ""
            if entry["kind"] == "star":
                if it.get("image"):
                    rows.append(("Hình tượng", pre + esc(it["image"])))
                if it.get("light"):
                    rows.append(("Mặt sáng · Dụng", (pre and f"<b>{esc(it['name'])}</b>") + "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in it["light"]) + "</ul>"))
                if it.get("shadow"):
                    rows.append(("Vùng bài học", (pre and f"<b>{esc(it['name'])}</b>") + "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in it["shadow"]) + "</ul>"))
                if it.get("heal"):
                    rows.append(("Chuyển hóa", (pre and f"<b>{esc(it['name'])}</b>") + "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in it["heal"]) + "</ul>"))
            else:
                if it.get("definition"):
                    rows.append(("Định nghĩa", esc(it["definition"])))
                if it.get("remedy"):
                    rows.append(("Cải mệnh", "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in it["remedy"]) + "</ul>"))
        if w.get("healingView"):
            rows.append(("Góc nhìn TVCL", esc(w["healingView"])))
        body = "".join(f'<div class="row"><span class="k">{k}</span><span>{v}</span></div>' for k, v in rows)
        blocks.append(f'<details class="stage"><summary><span class="num">{esc(typ)}</span><span class="stitle">{esc(title)}</span><span class="chev">›</span></summary><div class="sbody">{body}</div></details>')
        if len(blocks) == 4:
            break
    return "".join(blocks)


def course_link(title):
    for needle, href, label in COURSE_LINKS:
        if needle.lower() in (title or "").lower():
            return href, label
    return "/khoa-hoc/", "Xem các khóa học"

THAM_VAN = {
    "luan": ("/dich-vu-luan-tu-vi/", "Đặt lịch luận lá số", "Muốn soi chủ đề này trên chính lá số của mình? Một buổi luận Tử Vi giúp bạn thấy rõ vùng mạnh để dụng và vùng bài học để chuyển hóa."),
    "tinh": ("/tham-van-tinh-duyen/", "Tham vấn Tình Duyên", "Đang vướng trong chuyện yêu thương, hôn nhân? Một buổi tham vấn riêng giúp bạn nhìn rõ mô thức gắn bó của mình và người thương."),
    "qt": ("/tham-van-quan-trung/", "Tham vấn cùng thầy Quán Trung", "Khi cần người đồng hành sâu hơn, bạn có thể đặt buổi tham vấn 1:1 với thầy Quán Trung, kết hợp lá số và tâm lý học chữa lành."),
}
COURSES = {
    "nhanh": ("/khoa-hoc/luan-nhanh-tu-vi/", "Luận Nhanh Tử Vi", "Cửa vào cho người mới: tự đọc lá số của mình theo 5 bước."),
    "vanhan": ("/luan-van-han/", "Luận Vận Hạn", "Đọc đại vận, tiểu vận, lưu niên để sống thuận nhịp thời."),
    "tvcl": ("/khoa-hoc-tu-vi-chua-lanh/", "Tử Vi Chữa Lành", "Hiểu Mình – Cải Mệnh – Chữa Lành trên chính lá số của bạn."),
    "bikip": ("/khoa-hoc-tu-vi-bi-kip-chua-lanh/", "Tử Vi Bí Kíp Chữa Lành", "Chuyển hóa sâu bằng CBT, ACT, IFS và Đạo học."),
    "tinh": ("https://forms.gle/5DE4WyrKZXpV24cm6", "Tử Vi Chữa Lành Tình Duyên", "Thấu hiểu mô thức gắn bó, hóa giải xung đột trong tình yêu và hôn nhân."),
    "tai": ("https://forms.gle/LA967HBgEniFXNqv7", "Tử Vi Chữa Lành Tài Lộc", "Chữa lành mối quan hệ với tiền, nuôi dưỡng khí chất Hóa Lộc."),
}
ZALO = {
    "botoc": ("https://zalo.me/g/mykxsq198", "Bộ tộc Tử Vi Chữa Lành"),
    "tailieu": ("https://zalo.me/g/aqtxsx783", "Nhận Tài liệu Tử Vi Chữa Lành miễn phí"),
    "tamly": ("https://zalo.me/g/nkjvcd698", "Tâm lý học Chữa lành"),
    "treem": ("https://zalo.me/g/ztdpej867", "Tâm lý học Trẻ em"),
    "tailoc": ("https://zalo.me/g/gzverp694", "Tử Vi Chữa Lành Tài Lộc"),
    "con": ("https://zalo.me/g/gaxmii224", "Luận Tử Vi Cho Con"),
    "tinh": ("https://zalo.me/g/smxfrt156", "Tử Vi Chữa Lành Tình Duyên"),
}


def pick_cta(article, category, rc):
    i, dom, cat, t = article.get("index", 0), article.get("lifeDomain", ""), category["id"], (rc.get("title") or "").lower()
    if dom == "tinh-duyen":
        tv, z = "tinh", "tinh"
    elif dom == "tai-chinh" or cat == "tam-thuc-tai-chinh":
        tv, z = ("qt" if i % 2 else "luan"), "tailoc"
    elif dom == "con-cai":
        tv, z = "luan", ("con" if i % 2 else "treem")
    elif dom == "van-han" or cat == "la-so-van-han":
        tv, z = "luan", ("botoc" if i % 2 else "tailieu")
    elif cat == "tam-ly-dao-hoc" or dom == "noi-tam":
        tv, z = ("qt" if i % 2 else "luan"), ("tamly" if i % 3 else "tailieu")
    else:
        tv, z = ["luan", "qt", "luan"][i % 3], ["botoc", "tailieu", "tamly"][i % 3]
    if "tình duyên" in t: c = "tinh"
    elif "tài lộc" in t: c = "tai"
    elif "vận hạn" in t: c = "vanhan"
    elif "bí kíp" in t: c = "bikip"
    elif "luận nhanh" in t: c = "nhanh"
    else: c = "tvcl"
    return tv, c, z


def cta_html(article, category, rc):
    tv, c, z = pick_cta(article, category, rc)
    th, tl, td = THAM_VAN[tv]
    ch, cn, cd = COURSES[c]
    zh, zn = ZALO[z]
    ext = lambda h: ' target="_blank" rel="noopener"' if h.startswith("http") else ""
    intro = f'<p class="lead">{esc(rc.get("desc"))} Bộ tộc luôn sẵn lòng đồng hành cùng bạn theo cách phù hợp nhất.</p>' if rc.get("desc") else ""
    return (intro + '<div class="paths">'
            f'<a class="path-card k1" href="{th}"{ext(th)}><span class="pk">Tham vấn 1:1</span><b>{esc(tl)}</b><span>{esc(td)}</span><em>Đăng ký tham vấn →</em></a>'
            f'<a class="path-card k2" href="{ch}"{ext(ch)}><span class="pk">Khóa học phù hợp</span><b>{esc(cn)}</b><span>{esc(cd)}</span><em>Xem khóa học →</em></a>'
            f'<a class="path-card k5" href="/lo-trinh-hanh-nghe-tvcl/"><span class="pk">Đi xa hơn</span><b>Lộ trình Hành nghề TVCL</b><span>4 khóa, 13 chặng để trở thành người đồng hành chữa lành bằng Tử Vi.</span><em>Xem lộ trình →</em></a>'
            '</div>'
            f'<p class="zalo">💬 Muốn cùng chiêm nghiệm thêm với những người cùng chí hướng? Mời bạn vào nhóm Zalo miễn phí <a href="{zh}" target="_blank" rel="noopener">{esc(zn)}</a> của Bộ tộc.</p>')


def render_article(article, category, data, kb, B):
    md = B.render_markdown
    base_title = article["seo"].get("metaTitle") or article["title"]
    title_tag = base_title + " | Tử Vi Chữa Lành" if len(base_title) <= 46 else base_title
    description = article["seo"].get("metaDescription") or article["subtitle"]
    canonical = article["canonicalUrl"]
    schema = jscript(B.schema_for(article, category, data))
    ck = CAT_K.get(category["id"], "k2")
    bands, n = [], 0

    def band(eyebrow, h2, inner, anchor=""):
        nonlocal n
        k = KCYCLE[n % len(KCYCLE)]
        paper = " paper" if n % 2 else ""
        n += 1
        aid = f' id="{anchor}"' if anchor else ""
        bands.append(f'<section class="band{paper}" style="--c:var(--{k})"{aid}><div class="wrap stack"><p class="eyebrow">{eyebrow}</p><h2>{h2}</h2>{inner}</div></section>')

    mv = article.get("mythVsTruth", {})
    band("Đối chiếu góc nhìn", "Điều thường nghe và điều lá số thật sự chỉ ra",
         f'<p class="lead">{esc(article["subtitle"])}</p><div class="vs" style="margin-top:12px">'
         f'<div class="side myth"><h3>Lầm tưởng thường gặp</h3><p>{esc(mv.get("myth"))}</p></div>'
         f'<div class="side truth"><h3>Góc nhìn Tử Vi Chữa Lành</h3><p>{esc(mv.get("truth"))}</p></div></div>', "doi-chieu")
    if article.get("chart3P4CAxes"):
        band("Hệ sinh thái 3P4C", "Trục liên kết trên lá số",
             '<p class="lead">TVCL luận theo hệ sinh thái, không luận đơn cung, đơn sao. Đây là trục năng lượng chính của bài, các thành phần cùng nâng đỡ và điều hòa nhau.</p>'
             f'<div style="margin-top:12px">{axes_html(article)}</div>', "3p4c")
    if article.get("causalFlow5Steps"):
        band("Chuỗi nhân quả", "5 điểm then chốt trên hành trình chuyển hóa",
             '<p class="lead" style="margin-bottom:16px">Tiến trình nhân quả đầy đủ trong Tử Vi là Sao → Duyên → Tâm → Hành → Nghiệp → Vận → Quả → Chuyển hóa. Dưới đây là 5 điểm then chốt của chủ đề này, mỗi điểm đều có chỗ để bạn chọn lại.</p>'
             + steps_html(article, md), "chuyen-hoa")
    toc = []
    for i, s in enumerate(article.get("sections", []), 1):
        heading = re.sub(r"^\d+\.\s*", "", s["heading"])
        anchor = B.slugify(s["heading"]) or f"phan-{i}"
        toc.append((anchor, heading))
        band(f"Phần {i}", esc(heading), f'<div class="prose">{md(s.get("bodyMarkdown", ""))}</div>', anchor)
    kb_blocks = kb_html(article, kb, data["wikiEntries"])
    if kb_blocks:
        band("Tàng Kinh Các", "Tra cứu nhanh các sao, cung trong bài",
             '<p class="lead" style="margin-bottom:8px">Trích từ bộ tri thức chuẩn TVCL. Mỗi sao đều có mặt sáng để dụng và vùng bài học để chuyển hóa. Bấm vào từng mục để mở.</p>'
             + f'<div class="stack" style="gap:10px">{kb_blocks}</div>', "tang-kinh-cac")
    prompts = article.get("reflectionPrompts", [])
    if prompts or article.get("microPractice"):
        crit = "".join(f'<div class="crit"><b>CÂU HỎI {i}</b>{esc(p)}</div>' for i, p in enumerate(prompts, 1))
        practice = f'<div class="pass"><b>Thực hành hôm nay:</b> {esc(article.get("microPractice"))}</div>' if article.get("microPractice") else ""
        band("Tự soi chiếu", "Câu hỏi cho bạn và thực hành hôm nay", f'<div class="criteria" style="margin-top:8px">{crit}</div>{practice}', "tu-soi-chieu")
    faqs = article.get("faq", [])
    if faqs:
        items = "".join(f'<details><summary>{esc(f["question"])}</summary><p>{esc(f["answer"])}</p></details>' for f in faqs)
        items += '<details><summary>Đọc lá số có thay được bác sĩ, nhà trị liệu hay luật sư?</summary><p>Không. Lá số giúp bạn hiểu khuynh hướng và mô thức của mình. Khi vấn đề kéo dài hoặc có tổn thương sâu, hãy tìm tới chuyên gia phù hợp. Tử Vi Chữa Lành đồng hành, không thay thế chuyên gia.</p></details>'
        band("Câu hỏi thường gặp", "Bạn còn băn khoăn?", f'<div class="faq">{items}</div>', "cau-hoi-thuong-gap")
    rc = article.get("recommendedCourse") or {}
    href, label = course_link(rc.get("title"))
    tags_by_overlap = sorted((x for x in data["articles"] if x["id"] != article["id"]),
                             key=lambda x: (-sum(t in x.get("tags", []) for t in article.get("tags", [])), x["index"]))[:4]
    related = "".join(f'<a href="{url_of(a)}"><span>{esc(short_cat(a["categoryName"]))} · {esc(a.get("readTime", ""))}</span>{esc(a["title"])}</a>' for a in tags_by_overlap)
    taglinks = "".join(f'<a class="tagchip" href="/bai-viet/?tag={html.escape(k, quote=True)}">✦ {esc(lbl)}</a>' for k, lbl in zip(article.get("tags", []), article.get("tagLabels", [])))
    arts = data["articles"]
    i = next(j for j, a in enumerate(arts) if a["id"] == article["id"])
    prev = f'<a href="{url_of(arts[i-1])}"><span>← Bài trước</span>{esc(arts[i-1]["title"])}</a>' if i else '<a href="/bai-viet/"><span>← Thư viện</span>Về thư viện bài viết</a>'
    nxt = f'<a class="nx" href="{url_of(arts[i+1])}"><span>Bài tiếp →</span>{esc(arts[i+1]["title"])}</a>' if i + 1 < len(arts) else '<a class="nx" href="/bai-viet/"><span>Thư viện →</span>Khám phá thêm bài viết</a>'
    cta = cta_html(article, category, rc)
    band("Đồng hành", esc(rc.get("title") or "Học cùng Bộ tộc Tử Vi Chữa Lành"),
         cta + f'<h3 style="margin-top:20px">Đọc tiếp</h3><div class="related">{related}</div>'
         f'<h3 style="margin-top:16px">Theo Sao, Cung và chủ đề</h3><div class="tagrow">{taglinks}</div>'
         f'<nav class="prevnext" aria-label="Bài trước và bài tiếp">{prev}{nxt}</nav>', "dong-hanh")

    toc_links = "".join(f'<a href="#{a}">{esc(h)}</a>' for a, h in toc)
    toc_html = f'<nav class="toc" aria-label="Trong bài viết"><span>Trong bài</span>{toc_links}<a href="#cau-hoi-thuong-gap">Hỏi đáp</a></nav>' if toc else ""
    wiki = jscript(data["wikiEntries"])
    return head(title_tag, description, canonical, "article", f'<script type="application/ld+json">{schema}</script>') + f'''
<body class="art">
<div class="progress" id="progress"></div>
<header class="hero">
  {hero_svg()}
  <div class="wrap">
    <a class="home-logo" href="/" aria-label="Về trang chủ Tử Vi Chữa Lành"><img class="logo" src="{LOGO_URL}" alt="Logo Tử Vi Chữa Lành" width="120" height="120"></a>
    <p class="crumb"><a href="/">Trang chủ</a> › <a href="/bai-viet/">Bài viết</a> › <a href="/bai-viet/{category["id"]}/">{esc(short_cat(category["shortName"]))}</a></p>
    <p class="eyebrow">{esc(short_cat(category["name"]))}</p>
    <h1>{esc(article["title"])}</h1>
    <p class="tribe">Bộ tộc Tử Vi Chữa Lành</p>
    <p class="slogan">{SLOGAN}</p>
    <p class="quote">“{TAGLINE}”</p>
    {path_strip()}
    <p class="byline"><span>Viết bởi <b>{esc(article.get("authorName", "Bộ tộc Tử Vi Chữa Lành"))}</b></span><span class="sep">·</span><span>{esc(article.get("readTime", ""))} đọc</span><span class="sep">·</span><a class="{ck}" href="/bai-viet/{category["id"]}/">{esc(short_cat(category["shortName"]))}</a></p>
    {toc_html}
  </div>
</header>
<main>
{"".join(bands)}
</main>
{footer()}
<div class="wiki-modal" id="wiki-modal" role="dialog" aria-modal="true" aria-labelledby="wiki-title"><div class="wiki-card"><button id="wiki-close" class="wiki-close" aria-label="Đóng">×</button><p class="eyebrow">Tàng Kinh Các</p><h3 id="wiki-title"></h3><p id="wiki-type" class="wtype"></p><p id="wiki-summary"></p><p class="eyebrow" style="margin-top:12px">Góc nhìn chuyển hóa</p><p id="wiki-healing"></p><a id="wiki-filter" href="/bai-viet/">Các bài cùng chủ đề →</a></div></div>
<script>const WIKI={wiki};const M=document.getElementById('wiki-modal');document.addEventListener('click',e=>{{const b=e.target.closest('[data-wiki-key]');if(!b)return;const x=WIKI[b.dataset.wikiKey];if(!x)return;for(const[k,f]of[['wiki-title','title'],['wiki-type','type'],['wiki-summary','summary'],['wiki-healing','healingView']])document.getElementById(k).textContent=x[f]||'';document.getElementById('wiki-filter').href='/bai-viet/?tag='+encodeURIComponent(b.dataset.wikiKey);M.classList.add('open')}});document.getElementById('wiki-close').onclick=()=>M.classList.remove('open');M.onclick=e=>{{if(e.target===M)M.classList.remove('open')}};document.addEventListener('keydown',e=>{{if(e.key==='Escape')M.classList.remove('open')}});const P=document.getElementById('progress'),t=()=>{{const m=document.documentElement.scrollHeight-innerHeight;P.style.width=(m>0?scrollY/m*100:0)+'%'}};addEventListener('scroll',t,{{passive:true}});t();</script>
</body>
</html>'''


# ───────────────────────── Thư viện ─────────────────────────

def story_card(a):
    tags = "".join(f'<span class="article-tag">{esc(l)}</span>' for l in a.get("tagLabels", [])[:3])
    return (f'<article class="story-card" data-id="{esc(a["id"])}"><div class="story-meta"><a href="/bai-viet/{esc(a["category"])}/">{esc(short_cat(a["categoryName"]))}</a><span>{esc(a.get("readTime", ""))}</span></div>'
            f'<h3><a href="{url_of(a)}">{esc(a["title"])}</a></h3><p class="story-deck">{esc(a.get("subtitle", ""))}</p><div class="story-tags">{tags}</div></article>')


def render_library(data, category, articles, title, description, canonical, is_root):
    cats = data["categories"]
    counts = {c["id"]: sum(a["category"] == c["id"] for a in data["articles"]) for c in cats}
    pills = '<a class="pill {k}{cur}" href="/bai-viet/"{ac}>Tất cả</a>'.format(k="k2", cur=" end" if is_root else "", ac=' aria-current="page"' if is_root else "")
    pills += "".join(f'<a class="pill {CAT_K.get(c["id"], "k2")}{" end" if c["id"] == category["id"] else ""}" href="/bai-viet/{c["id"]}/"{" aria-current=page" if c["id"] == category["id"] else ""}>{esc(short_cat(c["shortName"]))}</a>' for c in cats)
    lead = next((a for a in data["articles"] if a["id"] == "la-so-tu-vi-co-phai-la-ban-an-dinh-menh"), data["articles"][0])
    pool = [a for a in articles if a.get("featured")] or articles
    picks = [a for a in pool if a["id"] != lead["id"]][:3]
    if is_root:
        picks = [lead] + picks
    else:
        picks = pool[:4]
    pick_html = "".join(f'<a class="card pillar {KCYCLE[i % 5]} pick" href="{url_of(a)}"><span class="pk">{esc(short_cat(a["categoryName"]))} · {esc(a.get("readTime", ""))}</span><h3>{esc(a["title"])}</h3><p>{esc(a["subtitle"])}</p><span class="go">Đọc bài →</span></a>' for i, a in enumerate(picks))
    tag_count, tag_label = {}, {}
    for a in articles:
        for k, l in zip(a.get("tags", []), a.get("tagLabels", [])):
            tag_count[k] = tag_count.get(k, 0) + 1
            tag_label[k] = l
    popular = sorted(tag_count, key=lambda k: (-tag_count[k], k))[:6]
    sugg = "".join(f'<button type="button" class="query-chip" data-query="{esc(tag_label[k])}">{esc(tag_label[k])}</button>' for k in popular)
    cards = "".join(story_card(a) for a in articles)
    topics = "".join(f'<a class="card pillar {CAT_K.get(c["id"], "k2")} pick" href="/bai-viet/{c["id"]}/"><span class="pk">{counts[c["id"]]} bài viết</span><h3>{esc(short_cat(c["name"]))}</h3><p>{esc(c["heroDesc"])}</p><span class="go">Xem chuyên đề →</span></a>' for c in cats)
    h1 = 'Bài viết &amp; <span>Chiêm nghiệm</span> lá số' if is_root else esc(category.get("heroTitle") or category["name"])
    eyebrow = "Tàng Kinh Các · Thư viện bài viết" if is_root else "Chuyên đề · " + esc(short_cat(category["name"]))
    schema = jscript({"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": title, "description": description, "url": canonical,
         "isPartOf": {"@type": "WebSite", "name": "Tử Vi Chữa Lành", "url": SITE + "/"}},
        {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + url_of(a), "name": a["title"]} for i, a in enumerate(articles)]}]})
    pagecat = "all" if is_root else category["id"]
    domains = [("all", "Tất cả lĩnh vực"), ("noi-tam", "Nội tâm & chữa lành"), ("tai-chinh", "Tiền bạc & tài chính"), ("tinh-duyen", "Tình duyên & hôn nhân"), ("con-cai", "Cha mẹ & con cái"), ("su-nghiep", "Sự nghiệp & tự học"), ("van-han", "Vận hạn & bước ngoặt")]
    opts = "".join(f'<option value="{v}">{esc(l)}</option>' for v, l in domains)
    return head(title, description, canonical, "website",
                f'<script type="application/ld+json">{schema}</script><script defer src="/bai-viet/assets/data.js"></script><script defer src="/bai-viet/assets/library.js"></script>') + f'''
<body class="lib" data-category="{pagecat}">
<header class="hero">
  {hero_svg()}
  <div class="wrap">
    <a class="home-logo" href="/" aria-label="Về trang chủ Tử Vi Chữa Lành"><img class="logo" src="{LOGO_URL}" alt="Logo Tử Vi Chữa Lành" width="120" height="120"></a>
    <p class="crumb"><a href="/">Trang chủ</a> › {'Bài viết' if is_root else '<a href="/bai-viet/">Bài viết</a> › ' + esc(short_cat(category["shortName"]))}</p>
    <p class="eyebrow">{eyebrow}</p>
    <h1>{h1}</h1>
    <p class="tribe">Bộ tộc Tử Vi Chữa Lành</p>
    <p class="slogan">{SLOGAN}</p>
    <p class="quote">“{TAGLINE}”</p>
    <nav class="path-strip" aria-label="Chuyên đề">{pills}</nav>
  </div>
</header>
<main>
  <section class="band" style="--c:var(--k2)">
    <div class="wrap stack">
      <p class="eyebrow">Tìm bài viết</p>
      <h2>Bạn đang muốn hiểu rõ điều gì?</h2>
      <form id="search-form" class="search" role="search">
        <label for="library-search" class="sr">Tìm bài viết</label>
        <div class="search-row"><input id="library-search" type="search" autocomplete="off" placeholder="Thử: Hóa Kỵ, Phu Thê, tiền bạc, vận hạn…"><button class="cta" type="submit">Tìm</button></div>
        <p class="hint">Tìm không dấu được. Gõ tên Sao, Cung, phương pháp hoặc điều bạn đang băn khoăn.</p>
        <div class="suggestions"><span>Gợi ý:</span>{sugg}</div>
      </form>
    </div>
  </section>
  <section class="band paper" style="--c:var(--k1)">
    <div class="wrap stack">
      <p class="eyebrow">Bắt đầu từ đây</p>
      <h2>Đọc từ điều cốt lõi</h2>
      <div class="grid" style="margin-top:8px">{pick_html}</div>
    </div>
  </section>
  <section class="band" style="--c:var(--k3)" id="thu-vien">
    <div class="wrap stack">
      <p class="eyebrow">Thư viện chiêm nghiệm</p>
      <div class="res-head"><h2>{'Tất cả bài viết' if is_root else esc(short_cat(category["shortName"]))}</h2><label class="sort">Sắp xếp <select id="sort-order"><option value="curated">Thứ tự biên soạn</option><option value="az">Tiêu đề A–Z</option></select></label></div>
      <p id="result-count" class="count" aria-live="polite">{len(articles)} bài viết</p>
      <div class="lib-layout">
        <div class="lib-main"><div id="active-filters" class="active-filters" hidden></div><div id="article-results" class="story-grid">{cards}</div><button type="button" id="show-more" class="cta ghost show-more" hidden>Xem thêm bài viết</button></div>
        <aside class="lib-aside">
          <details id="filter-panel" class="filter-panel"><summary><span><b>Lọc theo Sao, Cung &amp; Phương pháp</b><small id="filter-summary">45 chủ đề</small></span><span class="chev">›</span></summary>
            <div class="filter-controls"><label for="life-domain">Lĩnh vực đời sống</label><select id="life-domain">{opts}</select><div id="filter-groups"></div><button class="clear-button" id="clear-all" type="button">Xóa tìm kiếm và bộ lọc</button></div>
          </details>
          <div class="aside-note"><p class="eyebrow">Tinh thần TVCL</p><p>Tử Vi gợi ra khuynh hướng. Nhận thức và hành động mở thêm con đường.</p><a href="/lo-trinh-hanh-nghe-tvcl/">Xem lộ trình học →</a></div>
        </aside>
      </div>
    </div>
  </section>
  <section class="band paper" style="--c:var(--k4)">
    <div class="wrap stack">
      <p class="eyebrow">5 chuyên đề</p>
      <h2>Đi sâu theo từng chủ đề</h2>
      <div class="grid topics" style="margin-top:8px">{topics}</div>
    </div>
  </section>
</main>
{footer()}
</body>
</html>'''


EXTRA_CSS = r'''
/* ══ Bổ sung cho /bai-viet/ (chuẩn Lộ trình, 30/10/2026) ══ */
.art .hero h1,.lib .hero h1{font-size:clamp(1.8rem,4.4vw,2.8rem);max-width:24ch}
.crumb{font-size:.85rem;color:var(--muted);margin-bottom:6px}.crumb a{text-decoration:none}.crumb a:hover{text-decoration:underline}
.byline{margin-top:18px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:.88rem;color:var(--muted)}.byline b{color:var(--ink)}.byline .sep{opacity:.5}.byline a{font-weight:600;color:var(--c,var(--sky-ink));text-decoration:none}
.toc{margin-top:16px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;max-width:720px}.toc span{font-size:.75rem;letter-spacing:.1em;text-transform:uppercase;font-weight:700;color:var(--muted);margin-right:4px}
.toc a{font-size:.82rem;text-decoration:none;color:var(--ink);background:color-mix(in srgb,var(--card) 80%,transparent);border:1px solid var(--line);border-radius:999px;padding:4px 11px}.toc a:hover{border-color:var(--sky);color:var(--sky-ink)}
.progress{position:fixed;top:0;left:0;height:3px;width:0;background:linear-gradient(90deg,var(--sky),var(--heal));z-index:20}
.prose{max-width:68ch;display:grid;gap:14px;font-size:1.04rem}.prose p,.prose ul,.prose ol{margin:0}.prose ul,.prose ol{padding-left:22px;display:grid;gap:6px}
.prose h3,.prose h4,.prose h5{color:var(--c);margin-top:6px}.prose strong{color:var(--ink)}.prose code{background:var(--sky-soft);border-radius:4px;padding:0 4px}
.wiki-chip{display:inline;border:0;border-bottom:1.5px dotted var(--c,var(--sky));background:transparent;color:var(--c,var(--sky-ink));font:inherit;font-weight:600;padding:0;cursor:pointer}.wiki-chip:hover{background:var(--sky-soft)}
.vs{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.vs .side{border-radius:14px;padding:20px;border:1px solid var(--line);background:var(--card);display:flex;flex-direction:column;gap:8px}
.vs .side.myth{border-top:4px solid var(--muted)}.vs .side.myth h3{color:var(--muted)}.vs .side.myth p::before{content:"✕  ";color:var(--muted)}
.vs .side.truth{border-top:4px solid var(--heal);background:color-mix(in srgb,var(--heal) 10%,var(--card))}.vs .side.truth h3{color:var(--heal)}.vs .side.truth p::before{content:"✓  ";color:var(--heal);font-weight:700}
.axis{display:grid;gap:10px}.ax{display:grid;grid-template-columns:170px 1fr 54px;gap:14px;align-items:center}
.ax .lbl{font-weight:700;color:var(--c)}.ax .lbl small{display:block;font-weight:500;color:var(--muted);font-size:.78rem}
.ax .bar{height:12px;border-radius:999px;background:var(--line);overflow:hidden}.ax .bar i{display:block;height:100%;background:var(--c);border-radius:999px}.ax .pct{font-weight:800;color:var(--c);text-align:right}
.nodes{display:flex;flex-wrap:wrap;gap:10px;align-items:stretch}.nsep{align-self:center;font-size:1.3rem;font-weight:700;color:var(--muted)}
.node-card{flex:1 1 180px;max-width:300px;background:color-mix(in srgb,var(--c) 12%,var(--card));border:1px solid color-mix(in srgb,var(--c) 30%,transparent);border-top:4px solid var(--c);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;gap:4px}
.node-card b{color:var(--c);font-size:1.05rem}.node-card span{font-size:.9rem;color:var(--ink)}.axis-cap{margin-top:10px;color:var(--muted);font-size:.9rem}
.step-sm{font-size:.95rem;color:var(--ink)}.course .cbody{padding-bottom:26px}
.sbody .row>span:last-child ul{margin:4px 0 0}.sbody b{color:var(--c)}
.faq summary{list-style:none}.faq summary::-webkit-details-marker{display:none}.faq summary::before{content:"+";display:inline-block;width:1.2em;color:var(--c);font-weight:800}.faq details[open] summary::before{content:"–"}
.offer-box{background:var(--card);border:1px solid var(--line);border-top:4px solid var(--c);border-radius:14px;padding:22px;display:grid;gap:12px;max-width:760px}
.cta{display:inline-block;background:var(--sky);color:#fff;text-decoration:none;font-weight:700;padding:11px 20px;border-radius:999px;border:0;cursor:pointer;font:inherit;font-weight:700}
.cta:hover{filter:brightness(1.06)}.cta.ghost{background:transparent;color:var(--sky-ink);border:1.5px solid var(--sky)}
.related{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.related a,.prevnext a{display:block;padding:14px 16px;border:1px solid var(--line);border-left:4px solid var(--sky);border-radius:12px;background:var(--card);text-decoration:none;font-weight:600;color:var(--ink);line-height:1.45}
.related a span,.prevnext a span{display:block;font-size:.78rem;color:var(--muted);font-weight:500;margin-bottom:2px}.related a:hover,.prevnext a:hover{border-color:var(--sky)}
.tagrow{display:flex;flex-wrap:wrap;gap:6px}.tagchip{font-size:.82rem;text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:4px 11px;color:var(--ink);background:var(--card)}.tagchip:hover{border-color:var(--sky);color:var(--sky-ink)}
.prevnext{display:grid;gap:10px;grid-template-columns:1fr 1fr;margin-top:16px}.prevnext a.nx{text-align:right;border-left:1px solid var(--line);border-right:4px solid var(--sky)}
.wiki-modal{position:fixed;inset:0;z-index:30;display:none;place-items:center;padding:16px;background:rgba(20,27,36,.55)}.wiki-modal.open{display:grid}
.wiki-card{max-width:520px;width:100%;background:var(--card);border-radius:16px;border-top:4px solid var(--sky);padding:22px;box-shadow:0 20px 60px rgba(0,0,0,.25)}.wiki-card h3{font-size:1.35rem;color:var(--sky-ink);margin:6px 40px 4px 0}
.wiki-card .wtype{font-size:.82rem;color:var(--muted)}.wiki-card p{margin:6px 0}.wiki-card>a{font-weight:600}
.wiki-close{float:right;width:36px;height:36px;border-radius:50%;border:1px solid var(--line);background:transparent;color:var(--ink);font-size:20px;cursor:pointer}
/* Thư viện */
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.lib .path-strip .pill{text-decoration:none}.lib .path-strip{gap:8px}
.search{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;display:grid;gap:10px;max-width:820px}
.search-row{display:flex;gap:8px}.search-row input{flex:1;min-width:0;border:1.5px solid var(--line);border-radius:999px;padding:11px 18px;font:inherit;background:var(--bg);color:var(--ink)}.search-row input:focus{outline:none;border-color:var(--sky)}
.hint{font-size:.85rem;color:var(--muted)}.suggestions{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:.85rem;color:var(--muted)}
.query-chip,.story-tag,.active-chip,.filter-chip{font:inherit;font-size:.82rem;border:1px solid var(--line);border-radius:999px;padding:4px 11px;background:var(--card);color:var(--ink);cursor:pointer}
.query-chip:hover,.story-tag:hover,.filter-chip:hover{border-color:var(--sky);color:var(--sky-ink)}
.card.pick{text-decoration:none;color:var(--ink)}.card.pick .pk{font-size:.75rem;letter-spacing:.06em;text-transform:uppercase;font-weight:700;color:var(--muted)}.card.pick .go{margin-top:auto;font-weight:700;color:var(--c);font-size:.9rem}.card.pick:hover{transform:translateY(-2px);transition:transform .15s}
.res-head{display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px;align-items:end}.sort{font-size:.85rem;color:var(--muted)}.sort select,.filter-controls select{font:inherit;border:1px solid var(--line);border-radius:8px;padding:6px 10px;background:var(--card);color:var(--ink)}
.count{color:var(--muted);font-size:.9rem}
.grid.topics{grid-template-columns:repeat(auto-fit,minmax(175px,1fr))}
.lib-layout{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:24px;align-items:start;margin-top:6px}
.story-grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}
.story-card{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--sky);border-radius:14px;padding:18px;display:flex;flex-direction:column;gap:8px;min-width:0}
.story-card:hover{border-color:color-mix(in srgb,var(--sky) 60%,var(--line))}
.story-meta{display:flex;justify-content:space-between;gap:8px;font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;font-weight:600}.story-meta a{text-decoration:none;color:var(--sky-ink)}
.story-card h3{font-size:1.05rem}.story-card h3 a{text-decoration:none;color:var(--ink)}.story-card h3 a:hover{color:var(--sky-ink)}
.story-deck{color:var(--muted);font-size:.92rem;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.story-tags{display:flex;flex-wrap:wrap;gap:5px;margin-top:auto}.article-tag{font-size:.75rem;background:var(--sky-soft);border-radius:6px;padding:2px 8px;color:var(--ink)}.story-tag{font-size:.75rem;padding:2px 9px}
.show-more{margin-top:16px}.empty-result{grid-column:1/-1;background:var(--paper);border-radius:14px;padding:24px;text-align:center}.empty-result .button{font:inherit;border:1.5px solid var(--sky);border-radius:999px;padding:8px 16px;background:transparent;color:var(--sky-ink);cursor:pointer}
.active-filters{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}.active-chip{background:var(--sky-soft);border-color:var(--sky)}.active-chip span{margin-left:6px}
.lib-aside{position:sticky;top:16px;display:grid;gap:14px}
.filter-panel{background:var(--card);border:1px solid var(--line);border-radius:14px}
.filter-panel>summary{cursor:pointer;list-style:none;padding:14px 16px;display:flex;justify-content:space-between;gap:10px;align-items:center}.filter-panel>summary::-webkit-details-marker{display:none}
.filter-panel>summary small{display:block;color:var(--muted);font-size:.8rem}.filter-panel[open]>summary .chev{transform:rotate(90deg)}
.filter-controls{padding:0 16px 16px;display:grid;gap:10px;font-size:.9rem}
.filter-group{border-top:1px solid var(--line);padding-top:8px}.filter-group summary{cursor:pointer;font-weight:600;display:flex;justify-content:space-between}.filter-group summary span{color:var(--muted);font-weight:500}
.filter-chip-list{display:flex;flex-wrap:wrap;gap:5px;padding:8px 0}.filter-chip small{color:var(--muted);margin-left:4px}.filter-chip.is-active{background:var(--sky);border-color:var(--sky);color:#fff}.filter-chip.is-active small{color:#fff}
.clear-button{font:inherit;font-size:.85rem;background:transparent;border:0;color:var(--sky-ink);text-decoration:underline;cursor:pointer;justify-self:start;padding:0}
.aside-note{background:var(--sky-soft);border-radius:14px;padding:16px;display:grid;gap:6px;font-size:.92rem}.aside-note a{font-weight:600}
.paths{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));margin-top:8px}
.path-card{display:flex;flex-direction:column;gap:6px;text-decoration:none;color:var(--ink);background:color-mix(in srgb,var(--c) 10%,var(--card));border:1px solid color-mix(in srgb,var(--c) 30%,transparent);border-top:4px solid var(--c);border-radius:14px;padding:18px}
.path-card .pk{font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;font-weight:700;color:var(--muted)}.path-card b{color:var(--c);font-size:1.08rem}.path-card span:not(.pk){font-size:.92rem}
.path-card em{margin-top:auto;font-style:normal;font-weight:700;color:var(--c);font-size:.9rem}.path-card:hover{transform:translateY(-2px);transition:transform .15s}
.zalo{margin-top:14px;background:var(--sky-soft);border-radius:12px;padding:14px 18px;max-width:760px}.zalo a{font-weight:700}
@media (max-width:860px){.lib-layout{grid-template-columns:1fr}.lib-aside{position:static;order:-1}}
@media (max-width:560px){.ax{grid-template-columns:1fr 46px;gap:6px 10px}.ax .lbl{grid-column:1/-1}.prevnext{grid-template-columns:1fr}.prevnext a.nx{text-align:left;border-right:1px solid var(--line);border-left:4px solid var(--sky)}.search-row{flex-direction:column}}
'''


def write_assets():
    assets = OUT / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    base = (SOURCE / "tvcl-lotrinh-base.css").read_text(encoding="utf-8")
    (assets / "tvcl-bv.css").write_text(base + "\n" + EXTRA_CSS, encoding="utf-8")
    shutil.copyfile(SOURCE / "logo-tvcl.webp", assets / "logo-tvcl.webp")


def load_kb():
    p = SOURCE / "kb_digest.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
