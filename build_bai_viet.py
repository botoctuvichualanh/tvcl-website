#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the static Bài viết & Chiêm nghiệm section from its source bundle."""
from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

import bai_viet_lotrinh as LT  # giao diện chuẩn Lộ trình (30/10/2026)


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "_bai-viet-source"
DATA_FILE = SOURCE / "03_tuvichualanh_80_articles_database.json"
TEMPLATE_FILE = SOURCE / "02_tuvichualanh_clean_ui_template.html"
OUT = ROOT / "bai-viet"
SITE = "https://tuvichualanh.com"


def esc(value):
    return html.escape(str(value or ""), quote=True)


def json_script(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def slugify(value):
    value = re.sub(r"[^\w\- ]", "", value.lower(), flags=re.UNICODE)
    return re.sub(r"[\s_]+", "-", value).strip("-")


def article_url(article):
    return f"/bai-viet/{article['category']}/{article['id']}/"


def render_hubs(data):
    all_category = {
        "id": "all", "name": "Tất cả chuyên đề", "shortName": "Tất cả",
        "slug": "tuvichualanh.com/bai-viet/",
        "heroTitle": "Thư Viện Bài Viết & Chiêm Nghiệm Lá Số Thực Tế",
        "heroDesc": "Tử Vi, Tâm lý học và Đạo học cùng soi chiếu những điều đang diễn ra trong đời sống. Lá số là bản đồ để hiểu mình, không phải bản án định sẵn."
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    (OUT / "assets" / "data.js").write_text("window.TVCL_DATA=" + json_script({k: data[k] for k in ("categories", "personas", "courses", "tagGroups", "wikiEntries", "articles")}) + ";\n", encoding="utf-8")
    (OUT / "assets" / "library.js").write_text(library_js(), encoding="utf-8")
    (OUT / "assets" / "newsroom.css").write_text(newsroom_css(), encoding="utf-8")
    LT.write_assets()

    for category in [all_category] + data["categories"]:
        is_root = category["id"] == "all"
        rel = "index.html" if is_root else f"{category['id']}/index.html"
        out_file = OUT / rel
        out_file.parent.mkdir(parents=True, exist_ok=True)
        canonical = f"{SITE}/bai-viet/" if is_root else f"{SITE}/bai-viet/{category['id']}/"
        title = "Bài viết & Chiêm nghiệm lá số | Tử Vi Chữa Lành" if is_root else f"{category['name']} | Bài viết Tử Vi Chữa Lành"
        description = category["heroDesc"]
        static_articles = [a for a in data["articles"] if is_root or a["category"] == category["id"]]
        html_doc = LT.render_library(data, category, static_articles, title, description, canonical, is_root)
        out_file.write_text(html_doc, encoding="utf-8")


def library_js():
    return r'''(()=>{
const D=window.TVCL_DATA,A=D.articles,C=D.categories,groups=D.tagGroups;
const page=document.body.dataset.category||'all',params=new URLSearchParams(location.search);
const selected=new Set(params.getAll('tag')),input=document.getElementById('library-search');
const domain=document.getElementById('life-domain'),sort=document.getElementById('sort-order');
const cards=document.getElementById('article-results'),active=document.getElementById('active-filters');
const count=document.getElementById('result-count'),more=document.getElementById('show-more');
let query=params.get('q')||'',limit=12;
const norm=s=>(s||'').toString().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[đĐ]/g,'d').toLowerCase();
const esc=s=>(s||'').toString().replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const urlFor=a=>`/bai-viet/${a.category}/${a.id}/`;
const categories=page==='all'?A:A.filter(a=>a.category===page);
const searchCache=new Map(A.map(a=>[a.id,norm([a.title,a.subtitle,a.categoryName,...a.tagLabels,...a.sections.map(s=>s.bodyMarkdown)].join(' '))]));
function updateURL(){const p=new URLSearchParams();if(query)p.set('q',query);selected.forEach(t=>p.append('tag',t));if(domain.value!=='all')p.set('domain',domain.value);const s=p.toString();history.replaceState({},'',location.pathname+(s?'?'+s:''))}
function tagLabel(key){for(const g of groups)for(const t of g.items)if(t.key===key)return t.label;return key}
function drawTags(){const host=document.getElementById('filter-groups'),opened=new Set([...host.querySelectorAll('details[open]')].map(x=>x.dataset.group));host.innerHTML=groups.map((g,i)=>{
 const items=g.items.map(t=>{const n=categories.filter(a=>a.tags.includes(t.key)).length,yes=selected.has(t.key);return `<button type="button" class="filter-chip${yes?' is-active':''}" data-filter-tag="${esc(t.key)}" aria-pressed="${yes}"><span>${esc(t.label)}</span><small>${n}</small></button>`}).join('');
 const open=opened.has(g.id)||[...selected].some(k=>g.items.some(t=>t.key===k));
 return `<details class="filter-group" data-group="${esc(g.id)}" ${open?'open':''}><summary>${esc(g.title.replace(/^[^\p{L}\p{N}]+/u,''))}<span>${g.items.length}</span></summary><div class="filter-chip-list">${items}</div></details>`
}).join('')}
function drawActive(){const tags=[...selected].map(k=>`<button type="button" class="active-chip" data-remove-tag="${esc(k)}">${esc(tagLabel(k))}<span aria-hidden="true">×</span></button>`).join('');const q=query?`<button type="button" class="active-chip" data-clear-query>Tìm: “${esc(query)}”<span aria-hidden="true">×</span></button>`:'';active.innerHTML=tags+q;active.hidden=!tags&&!q}
function articleCard(a){const c=C.find(x=>x.id===a.category),tagButtons=a.tagLabels.slice(0,3).map((label,i)=>`<button type="button" class="story-tag" data-filter-tag="${esc(a.tags[i])}" aria-label="Lọc theo ${esc(label)}">${esc(label)}</button>`).join('');return `<article class="story-card category-${esc(a.category)}"><div class="story-meta"><a href="/bai-viet/${a.category}/">${esc(c?.shortName||a.categoryName)}</a><span>${esc(a.readTime||'')}</span></div><h3><a href="${urlFor(a)}">${esc(a.title)}</a></h3><p class="story-deck">${esc(a.subtitle)}</p><div class="story-tags">${tagButtons}</div></article>`}
function matches(a){if(page!=='all'&&a.category!==page)return false;if(domain.value!=='all'&&a.lifeDomain!==domain.value)return false;if([...selected].some(t=>!a.tags.includes(t)))return false;if(query){const corpus=searchCache.get(a.id),words=norm(query).split(/\s+/).filter(Boolean);if(!words.every(w=>corpus.includes(w)))return false}return true}
function render(){drawTags();drawActive();let result=categories.filter(matches);if(sort.value==='az')result.sort((a,b)=>a.title.localeCompare(b.title,'vi'));else result.sort((a,b)=>a.index-b.index);count.textContent=`${result.length} bài viết${query?' phù hợp':' trong thư viện'}`;cards.innerHTML=result.slice(0,limit).map(articleCard).join('')||`<div class="empty-result"><h3>Chưa tìm thấy bài phù hợp</h3><p>Thử từ khóa khác hoặc bỏ bớt điều kiện lọc.</p><button type="button" class="button button-outline" data-clear-all>Xóa bộ lọc</button></div>`;more.hidden=result.length<=limit;more.textContent=`Xem thêm ${Math.min(12,result.length-limit)} bài`;document.getElementById('filter-summary').textContent=selected.size?`${selected.size} chủ đề đã chọn`:'45 chủ đề';updateURL()}
input.value=query;if(params.has('domain'))domain.value=params.get('domain');
input.addEventListener('input',()=>{query=input.value.trim();limit=12;render()});domain.addEventListener('change',()=>{limit=12;render()});sort.addEventListener('change',()=>{limit=12;render()});
document.getElementById('search-form').addEventListener('submit',e=>{e.preventDefault();query=input.value.trim();limit=12;render();cards.scrollIntoView({behavior:'smooth',block:'start'})});
document.addEventListener('click',e=>{const tag=e.target.closest('[data-filter-tag]');if(tag){const k=tag.dataset.filterTag;selected.has(k)?selected.delete(k):selected.add(k);limit=12;document.getElementById('filter-panel').open=true;render();return}const remove=e.target.closest('[data-remove-tag]');if(remove){selected.delete(remove.dataset.removeTag);render();return}if(e.target.closest('[data-clear-query]')){query='';input.value='';render();input.focus();return}if(e.target.closest('[data-clear-all]')){selected.clear();query='';input.value='';domain.value='all';render();return}const moreBtn=e.target.closest('#show-more');if(moreBtn){limit+=12;render();return}const suggestion=e.target.closest('[data-query]');if(suggestion){query=suggestion.dataset.query;input.value=query;limit=12;render();document.getElementById('library-search').scrollIntoView({behavior:'smooth',block:'center'})}});
document.getElementById('clear-all').addEventListener('click',()=>{selected.clear();query='';input.value='';domain.value='all';render()});render();
})();'''


def render_library_page(data, category, articles, title, description, canonical, is_root):
    lead = next((a for a in data["articles"] if a["id"] == "la-so-tu-vi-co-phai-la-ban-an-dinh-menh"), data["articles"][0])
    picks = [a for a in data["articles"] if a.get("featured") and a["id"] != lead["id"]][:4]
    cats = [{"id": "all", "name": "Tất cả bài viết", "shortName": "Tất cả"}] + data["categories"]
    cat_links = "".join(f'<a class="category-link{" current" if c["id"] == category["id"] else ""}" href="/bai-viet/{"" if c["id"] == "all" else c["id"] + "/"}"{f" aria-current=page" if c["id"] == category["id"] else ""}>{esc(c["shortName"])}</a>' for c in cats)
    cards = "".join(card(a) for a in articles)
    featured = "".join(f'<a class="pick-link" href="{article_url(a)}"><span>{esc(next(c["shortName"] for c in data["categories"] if c["id"]==a["category"]))} · {esc(a.get("readTime",""))}</span><strong>{esc(a["title"])}</strong></a>' for a in picks)
    schema = json_script({"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "description": description, "url": canonical,
                          "isPartOf": {"@type": "WebSite", "name": "Tử Vi Chữa Lành", "url": SITE + "/"}})
    popular = []
    tag_count = {}
    tag_label = {}
    for a in articles:
        for k, label in zip(a.get("tags", []), a.get("tagLabels", [])):
            tag_count[k] = tag_count.get(k, 0) + 1
            tag_label[k] = label
    popular = sorted(tag_count, key=lambda k: (-tag_count[k], k))[:6]
    suggestions = "".join(f'<button type="button" class="query-chip" data-query="{esc(tag_label[k])}">{esc(tag_label[k])}</button>' for k in popular)
    pagecat = "all" if is_root else category["id"]
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="index, follow, max-image-preview:large"><link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Tử Vi Chữa Lành — Bộ Tộc Tử Vi Chữa Lành"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(canonical)}"><meta property="og:image" content="{SITE}/assets/img/hero-shanshui.jpg">
<script type="application/ld+json">{schema}</script><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&family=Cormorant+Garamond:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css"><link rel="stylesheet" href="/assets/css/homepage-nav.css"><link rel="stylesheet" href="/bai-viet/assets/newsroom.css"><script defer src="/bai-viet/assets/data.js"></script><script defer src="/bai-viet/assets/library.js"></script></head>
<body data-category="{pagecat}"><a class="skip-link" href="#main">Bỏ qua điều hướng</a><header class="site-header"><div class="site-header-inner"><a href="/" class="brand-lockup"><span class="logo-mark" role="img" aria-label="Logo Tử Vi Chữa Lành"></span><span class="titles"><span class="main-title">Tử Vi Chữa Lành</span><span class="sub-title">Bộ Tộc Tử Vi Chữa Lành</span></span></a><nav class="main-nav" aria-label="Điều hướng chính"><a class="nav-home" href="/">Trang chủ</a><a class="active" aria-current="page" href="/bai-viet/">Bài viết &amp; Chiêm nghiệm</a><a href="/khoa-hoc-tu-vi-chua-lanh/">Khóa học</a></nav></div></header><script src="/assets/js/homepage-nav.js" defer></script>
<main id="main" class="page-shell"><div class="crumb"><a href="/">Trang chủ</a><span>/</span><span>Bài viết & Chiêm nghiệm</span>{'' if is_root else f'<span>/</span><span>{esc(category["shortName"])}</span>'}</div>
<section class="masthead"><div class="masthead-copy"><p class="kicker">TÀNG KINH CÁC · BÀI VIẾT & CHIÊM NGHIỆM</p><h1>{esc(category["heroTitle"] if not is_root else "Lá số là bản đồ, không phải bản án")}</h1><p>{esc(description)}</p></div><div class="masthead-mark" aria-hidden="true"><span>SAO</span><i>→</i><span>DUYÊN</span><i>→</i><span>TÂM</span><i>→</i><span>HÀNH</span><i>→</i><span>QUẢ</span></div></section>
<section class="search-block" aria-label="Tìm bài viết"><form id="search-form" role="search"><label for="library-search">Anh đang muốn hiểu rõ điều gì?</label><div class="search-row"><span class="search-symbol" aria-hidden="true">⌕</span><input id="library-search" type="search" autocomplete="off" placeholder="Thử: Hóa Kỵ, Phu Thê, tiền bạc, vận hạn…" aria-describedby="search-hint"><button class="button button-primary" type="submit">Tìm bài viết</button></div><p id="search-hint">Tìm không dấu được. Có thể tìm tên Sao, Cung, phương pháp hoặc một điều đang băn khoăn.</p><div class="suggestions"><span>Gợi ý tìm nhanh</span>{suggestions}</div></form></section>
<nav class="category-nav" aria-label="Chuyên đề">{cat_links}</nav>
<section class="editors-picks"><div class="section-heading"><div><p class="kicker">BẮT ĐẦU TỪ ĐÂY</p><h2>Đọc từ điều cốt lõi</h2></div><a href="{article_url(lead)}">Bài nền tảng <span aria-hidden="true">→</span></a></div><div class="picks-grid"><article class="lead-story"><div class="lead-art"><img src="/assets/img/bai-viet-ban-do-la-so.svg" alt="Minh họa con đường qua núi và bản đồ sao: mỗi người tự chọn hướng đi của mình" width="960" height="800" fetchpriority="high"></div><div class="lead-copy"><p class="story-kicker">TUYÊN NGÔN TỬ VI CHỮA LÀNH · {esc(lead.get("readTime",""))}</p><h3><a href="{article_url(lead)}">{esc(lead["title"])}</a></h3><p>{esc(lead["subtitle"])}</p><a class="text-link" href="{article_url(lead)}">Đọc bài viết <span aria-hidden="true">→</span></a></div></article><div class="pick-list">{featured}</div></div></section>
<section class="library-area"><div class="library-main"><div class="section-heading results-heading"><div><p class="kicker">THƯ VIỆN CHIÊM NGHIỆM</p><h2>{'Tất cả bài viết' if is_root else esc(category['shortName'])}</h2><p id="result-count" class="result-count" aria-live="polite">{len(articles)} bài viết</p></div><label class="sort-label">Sắp xếp<select id="sort-order"><option value="curated">Thứ tự biên soạn</option><option value="az">Tiêu đề A–Z</option></select></label></div>
<div id="active-filters" class="active-filters" hidden></div><div id="article-results" class="story-grid">{cards}</div><button type="button" id="show-more" class="button button-outline show-more" hidden>Xem thêm bài viết</button></div>
<aside class="library-aside"><details id="filter-panel" class="filter-panel"><summary><span><strong>Lọc theo Sao, Cung & Phương pháp</strong><small id="filter-summary">45 chủ đề</small></span><b aria-hidden="true">＋</b></summary><div class="filter-controls"><label for="life-domain">Lĩnh vực đời sống</label><select id="life-domain"><option value="all">Tất cả lĩnh vực</option><option value="noi-tam">Nội tâm & chữa lành</option><option value="tai-chinh">Tiền bạc & tài chính</option><option value="tinh-duyen">Tình duyên & hôn nhân</option><option value="con-cai">Cha mẹ & con cái</option><option value="su-nghiep">Sự nghiệp & tự học</option><option value="van-han">Vận hạn & bước ngoặt</option></select><div id="filter-groups"></div><button class="clear-button" id="clear-all" type="button">Xóa tìm kiếm và bộ lọc</button></div></details>
<div class="aside-note"><p class="kicker">TINH THẦN TVCL</p><p>Tử Vi gợi ra khuynh hướng. Nhận thức và hành động mở thêm con đường.</p><a href="/">Tìm hiểu Tử Vi Chữa Lành →</a></div><a class="course-note" href="/khoa-hoc-tu-vi-chua-lanh/"><span>LỘ TRÌNH HỌC</span><strong>Từ hiểu mình đến tự đọc lá số</strong><span class="text-link">Xem các khóa học →</span></a></aside></section></main>
<footer class="site-footer"><div><strong>Tử Vi Chữa Lành</strong><span>Lá số là bản đồ, không phải bản án.</span></div><a href="/">Về trang chủ</a></footer></body></html>'''


def card(article):
    tags = "".join(f'<span class="article-tag">{esc(label)}</span>' for label in article.get("tagLabels", [])[:3])
    return f'''<article class="story-card" data-id="{esc(article['id'])}">
  <div class="story-meta"><a href="/bai-viet/{esc(article['category'])}/">{esc(article['categoryName'])}</a><span>{esc(article.get('readTime',''))}</span></div>
  <h3><a href="{article_url(article)}">{esc(article['title'])}</a></h3>
  <p class="story-deck">{esc(article.get('subtitle',''))}</p><div class="story-tags">{tags}</div>
</article>'''


def newsroom_css():
    return r'''
:root{--paper:var(--white,#F7F1E5);--surface:#FBF8F0;--ink:#20302B;--ink-soft:#40564E;--muted:#68766F;--forest:var(--blue,#0D3B32);--jade:var(--green-deep,#3F7A5E);--amber:var(--gold,#C29A4F);--clay:var(--gold-deep,#B07E2E);--line:rgba(13,59,50,.16);--line-dark:rgba(13,59,50,.3);--serif:'Be Vietnam Pro',Arial,sans-serif;--display:'Cormorant Garamond','Be Vietnam Pro',Arial,sans-serif;--sans:'Be Vietnam Pro',Arial,sans-serif;--measure:1180px}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.65 var(--serif)}a{color:inherit}button,input,select{font:inherit}button,a,select{touch-action:manipulation}.skip-link{position:absolute;left:-10000px;top:1rem;z-index:100;background:white;padding:.7rem 1rem}.skip-link:focus{left:1rem}.site-header{border-bottom:1px solid var(--line);background:var(--paper)}.site-header-inner{max-width:var(--measure);margin:0 auto;padding:12px 24px;display:flex;flex-direction:column;align-items:flex-start;gap:10px}.brand-lockup{text-decoration:none}.main-nav a{font-family:'Noto Serif',Georgia,serif!important}.main-nav a.active{color:var(--blue)!important;opacity:1!important;font-weight:700!important;text-decoration:underline!important;text-decoration-color:var(--gold)!important;text-underline-offset:7px}.page-shell{max-width:var(--measure);padding:0 28px 80px;margin:auto}.crumb{display:flex;gap:10px;align-items:center;margin:22px 0 20px;font:12px var(--sans);color:var(--muted)}.crumb a{text-decoration:none}.crumb a:hover{text-decoration:underline}.masthead{position:relative;overflow:hidden;min-height:240px;padding:40px clamp(25px,5vw,68px) 30px;background:#e9e5d9;border-top:1px solid var(--line-dark);border-bottom:1px solid var(--line-dark);display:flex;justify-content:space-between;gap:48px;align-items:center}.masthead:before{content:"";position:absolute;right:-3%;top:-55%;width:400px;height:400px;border:1px solid #c2b99f;border-radius:50%;box-shadow:0 0 0 24px #e9e5d9,0 0 0 25px #c2b99f,0 0 0 52px #e9e5d9,0 0 0 53px #c2b99f;opacity:.44}.masthead-copy{max-width:780px;position:relative;z-index:1}.kicker{font:700 10px/1.4 var(--sans);letter-spacing:.16em;color:var(--clay);margin:0 0 9px}.masthead h1{font:600 clamp(38px,5.3vw,66px)/.99 var(--display);letter-spacing:-.025em;margin:0 0 13px;max-width:800px}.masthead-copy>p:last-child{font:18px/1.55 var(--serif);color:#405b51;max-width:760px;margin:0}.masthead-mark{position:relative;z-index:1;max-width:285px;display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-end;gap:8px;color:var(--forest);font:700 9px var(--sans);letter-spacing:.09em}.masthead-mark i{font-style:normal;color:var(--amber)}.search-block{margin:24px 0 0;padding:21px 24px 18px;background:var(--surface);border:1px solid var(--line)}.search-block form>label{display:block;font:600 22px var(--display);margin-bottom:10px}.search-row{display:flex;align-items:center;gap:10px;position:relative}.search-symbol{position:absolute;left:16px;font:28px/1 var(--sans);color:var(--forest);pointer-events:none}.search-row input{min-width:0;flex:1;height:52px;padding:0 14px 0 48px;border:1px solid var(--line-dark);border-radius:3px;background:#fff;color:var(--ink);font:15px var(--sans)}.search-row input::placeholder{color:#7e8980}.button{min-height:46px;border:1px solid transparent;border-radius:3px;padding:0 18px;font:600 12px var(--sans);cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;transition:background .18s,border-color .18s,color .18s}.button-primary{background:var(--forest);color:white}.button-primary:hover{background:#12473d}.button-outline{background:transparent;border-color:var(--line-dark);color:var(--forest)}.button-outline:hover{background:#eee9dc}.search-block #search-hint{font:12px/1.5 var(--sans);color:var(--muted);margin:8px 0}.suggestions{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-top:10px}.suggestions>span{font:600 10px var(--sans);color:var(--muted);margin-right:3px}.query-chip{border:0;background:transparent;color:var(--forest);padding:3px 6px;font:500 11px var(--sans);text-decoration:underline;text-decoration-color:#b7c3b8;text-underline-offset:3px;cursor:pointer}.query-chip:hover{color:var(--clay)}.category-nav{display:flex;gap:7px;overflow-x:auto;padding:16px 0 17px;border-bottom:1px solid var(--line);scrollbar-width:thin}.category-link{flex:0 0 auto;padding:8px 12px;border:1px solid transparent;border-radius:2px;text-decoration:none;color:var(--ink-soft);font:600 11px var(--sans);transition:all .18s}.category-link:hover{border-color:var(--line-dark)}.category-link.current{background:var(--forest);color:white}.editors-picks{padding:30px 0 34px;border-bottom:1px solid var(--line)}.section-heading{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:16px}.section-heading h2{margin:0;font:600 30px/1.1 var(--display);letter-spacing:-.01em}.section-heading .kicker{margin-bottom:5px}.section-heading>a{font:600 11px var(--sans);text-decoration:none;color:var(--forest);white-space:nowrap}.section-heading>a:hover{text-decoration:underline}.picks-grid{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(250px,.8fr);gap:22px}.lead-story{min-height:255px;position:relative;display:grid;grid-template-columns:.9fr 1.1fr;border:1px solid var(--line);background:var(--surface)}.lead-art{min-height:230px;position:relative;overflow:hidden;background:#e9e5d9}.lead-art img{display:block;width:100%;height:100%;min-height:230px;object-fit:cover;object-position:50% 48%}.lead-art:after{content:"✦";position:absolute;left:18px;bottom:13px;color:#f3dfb5;font:28px var(--display)}.lead-copy{padding:21px 23px;align-self:center}.story-kicker{font:700 9px/1.5 var(--sans);letter-spacing:.12em;color:var(--clay);margin:0 0 9px}.lead-copy h3{font:600 clamp(25px,3vw,35px)/1.08 var(--display);margin:0 0 9px}.lead-copy h3 a{text-decoration:none}.lead-copy>p:not(.story-kicker){margin:0;color:var(--muted);font:14px/1.55 var(--serif);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.text-link{display:inline-block;margin-top:13px;color:var(--forest);font:700 10px var(--sans);text-decoration:none}.text-link:hover{text-decoration:underline}.pick-list{display:flex;flex-direction:column;border-top:1px solid var(--line-dark)}.pick-link{flex:1;display:flex;flex-direction:column;justify-content:center;gap:6px;padding:12px 7px;border-bottom:1px solid var(--line);text-decoration:none}.pick-link>span{font:700 9px var(--sans);letter-spacing:.06em;text-transform:uppercase;color:var(--clay)}.pick-link strong{font:600 19px/1.18 var(--display)}.pick-link:hover strong{color:var(--forest);text-decoration:underline;text-decoration-color:var(--amber);text-underline-offset:3px}.library-area{display:grid;grid-template-columns:minmax(0,1fr) 285px;gap:34px;padding-top:34px;align-items:start}.results-heading{align-items:center;margin-bottom:12px}.result-count{margin:3px 0 0;color:var(--muted);font:12px var(--sans)}.sort-label{display:flex;align-items:center;gap:8px;font:11px var(--sans);color:var(--muted)}.sort-label select,.filter-controls select{height:38px;max-width:190px;padding:0 28px 0 9px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:11px var(--sans)}.story-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));border-top:1px solid var(--line-dark);border-left:1px solid var(--line)}.story-card{min-width:0;min-height:220px;display:flex;flex-direction:column;padding:18px 18px 14px;background:var(--surface);border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.story-meta{display:flex;justify-content:space-between;gap:12px;font:700 9px var(--sans);letter-spacing:.04em;color:var(--muted);text-transform:uppercase}.story-meta a{color:var(--forest);text-decoration:none}.story-meta a:hover{text-decoration:underline}.story-card h3{font:600 24px/1.08 var(--display);letter-spacing:-.01em;margin:12px 0 7px}.story-card h3 a{text-decoration:none}.story-card h3 a:hover{color:var(--forest);text-decoration:underline;text-decoration-color:var(--amber);text-underline-offset:4px}.story-deck{font:13px/1.55 var(--serif);color:var(--muted);margin:0 0 13px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.story-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:auto}.article-tag,.story-tag{border:0;background:#efede5;color:#435b50;border-radius:2px;padding:4px 7px;font:500 9px/1.3 var(--sans)}.story-tag{cursor:pointer;min-height:28px}.story-tag:hover{background:#e2e8dc;color:var(--forest)}.show-more{display:flex;margin:18px auto 0}.library-aside{position:sticky;top:12px}.filter-panel{background:var(--surface);border:1px solid var(--line)}.filter-panel>summary{list-style:none;cursor:pointer;min-height:71px;display:flex;justify-content:space-between;align-items:center;padding:14px 16px}.filter-panel>summary::-webkit-details-marker,.filter-group>summary::-webkit-details-marker{display:none}.filter-panel>summary>span strong,.filter-panel>summary>span small{display:block}.filter-panel>summary strong{font:600 17px var(--display)}.filter-panel>summary small{font:10px var(--sans);color:var(--muted);margin-top:3px}.filter-panel>summary>b{font:300 21px var(--sans);color:var(--forest)}.filter-panel[open]>summary{border-bottom:1px solid var(--line)}.filter-panel[open]>summary>b{transform:rotate(45deg)}.filter-controls{padding:14px}.filter-controls>label{display:block;margin-bottom:6px;font:600 10px var(--sans);color:var(--ink-soft)}.filter-controls>select{width:100%;max-width:none;margin-bottom:13px}.filter-group{border-top:1px solid var(--line)}.filter-group>summary{list-style:none;display:flex;justify-content:space-between;align-items:center;min-height:42px;cursor:pointer;font:600 11px var(--sans)}.filter-group>summary span{font:10px var(--sans);color:var(--muted)}.filter-chip-list{display:flex;flex-wrap:wrap;gap:6px;padding:3px 0 12px}.filter-chip{min-height:34px;display:inline-flex;align-items:center;gap:8px;padding:4px 8px;background:#f8f6f0;border:1px solid var(--line);border-radius:2px;color:var(--ink-soft);cursor:pointer;text-align:left;font:500 10px var(--sans)}.filter-chip small{color:var(--muted);font:10px var(--sans)}.filter-chip:hover,.filter-chip.is-active{border-color:var(--forest);background:#e7eee8;color:var(--forest)}.filter-chip.is-active{box-shadow:inset 0 -2px var(--forest)}.clear-button{border:0;background:transparent;padding:10px 0 3px;color:var(--clay);font:600 10px var(--sans);cursor:pointer;text-decoration:underline;text-underline-offset:3px}.active-filters{display:flex;flex-wrap:wrap;gap:6px;padding:0 0 11px}.active-chip{display:inline-flex;align-items:center;gap:8px;min-height:30px;padding:4px 8px;border:1px solid #bdcfc3;background:#e8efe8;color:var(--forest);font:500 10px var(--sans);cursor:pointer}.active-chip span{font-size:15px}.empty-result{grid-column:1/-1;padding:42px;background:var(--surface);text-align:center;border:1px solid var(--line)}.empty-result h3{font:600 26px var(--display);margin:0}.empty-result p{color:var(--muted);font:14px var(--sans)}.aside-note,.course-note{display:block;margin-top:18px;padding:17px;background:#e9e5d9;border:1px solid var(--line);text-decoration:none}.aside-note>p:not(.kicker){font:16px/1.5 var(--serif);margin:7px 0;color:var(--ink-soft)}.aside-note>a{font:600 10px var(--sans);color:var(--forest);text-decoration:none}.course-note{background:var(--forest);color:#fbf7ec}.course-note span,.course-note strong{display:block}.course-note>span:first-child{font:700 9px var(--sans);letter-spacing:.14em;color:#e4c78d}.course-note strong{font:600 22px/1.15 var(--display);margin:9px 0}.course-note .text-link{color:#fff}.site-footer{min-height:100px;padding:24px max(calc((100vw - var(--measure))/2 + 28px),28px);border-top:1px solid var(--line-dark);display:flex;align-items:center;justify-content:space-between;gap:20px;background:#e9e5d9}.site-footer div strong,.site-footer div span{display:block}.site-footer div strong{font:700 19px var(--display)}.site-footer div span,.site-footer>a{font:11px var(--sans);color:var(--muted)}.site-footer>a{text-decoration:none}.site-footer>a:hover{text-decoration:underline}.button:focus-visible,a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid #ad7a35;outline-offset:2px}
@media(max-width:950px){.masthead-mark{max-width:220px}.library-area{grid-template-columns:minmax(0,1fr) 260px;gap:20px}.story-card h3{font-size:22px}}
@media(max-width:720px){body{font-size:16px}.header-inner{padding:10px 18px;align-items:flex-start;flex-direction:column;gap:8px}.site-header nav{gap:18px;width:100%;overflow:auto}.page-shell{padding:0 18px 54px}.crumb{margin:17px 0}.masthead{min-height:0;padding:28px 22px;display:block}.masthead h1{font-size:43px}.masthead-copy>p:last-child{font-size:16px}.masthead-mark{justify-content:flex-start;margin-top:21px;max-width:none}.search-block{padding:17px 15px}.search-block form>label{font-size:20px}.search-row{display:grid;grid-template-columns:1fr}.search-row input{width:100%}.search-row .button{width:100%}.suggestions{align-items:flex-start}.category-nav{margin:0 -18px;padding:12px 18px}.editors-picks{padding:24px 0}.section-heading h2{font-size:27px}.picks-grid{grid-template-columns:1fr;gap:13px}.lead-story{grid-template-columns:1fr}.lead-art,.lead-art img{min-height:150px;max-height:150px;height:150px}.lead-copy{padding:18px}.pick-list{padding-left:8px}.pick-link{padding:10px 5px}.library-area{grid-template-columns:1fr;padding-top:26px}.library-aside{position:static;grid-row:1}.results-heading{align-items:flex-start;flex-direction:column}.sort-label{width:100%;justify-content:space-between}.sort-label select{max-width:none;flex:1}.story-grid{grid-template-columns:1fr}.story-card{min-height:0;padding:16px}.story-card h3{font-size:25px}.story-deck{-webkit-line-clamp:4}.site-footer{padding:20px 18px}}
/* TVCL article typography: shared 13px reading text and 15px section titles */
.reader-page .reader-main>section :is(h2,h3,h4),.reader-page .reader-toc h2{font:600 15px/1.4 var(--sans);color:var(--clay)}
.reader-page .reader-main>section :is(p,li,blockquote,td,th,dd,dt,figcaption),.reader-page .crumb,.reader-page .reader-head>.kicker,.reader-page .reader-byline,.reader-page .reader-tag,.reader-page .reader-controls button,.reader-page .reader-controls a,.reader-page .reader-toc nav a,.reader-page .toc-exit,.reader-page .two-views b,.reader-page .causal-thread li>b,.reader-page .reader-related-card span,.reader-page .reader-related-card strong,.reader-page .reader-prevnext a,.reader-page .reader-footer{font-size:13px;color:var(--ink-soft)}
.reader-page .reader-main>section :is(p,li,blockquote,td,th,dd,dt,figcaption){line-height:1.6}
.reader-page .reader-tag,.reader-page .reader-related-card span{font-weight:500}
.reader-page .reader-controls button,.reader-page .reader-controls a,.reader-page .reader-related-card strong{font-weight:600}
.reader-page .reader-toc h2{letter-spacing:.08em}
.reader-page .two-views b,.reader-page .causal-thread li>b{line-height:1.4}
.reader-page .reader-related-card strong,.reader-page .reader-prevnext a{font-family:var(--sans);line-height:1.5}
.reader-page .reader-prevnext a{max-width:48%}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*::before,*::after{transition-duration:.01ms!important;animation-duration:.01ms!important;animation-iteration-count:1!important}}
'''


def wiki_button(label, key):
    return f'<button class="wiki-chip" type="button" data-wiki-key="{esc(key)}">✦ {esc(label)}</button>'


def render_markdown(text):
    """Render the small Markdown subset used in article bodies without dependencies."""
    pat = re.compile(r"\[([^\]]+)\]\(wiki:([A-Za-z0-9]+)\)")
    chips = []
    value = pat.sub(lambda m: chips.append(wiki_button(m.group(1), m.group(2))) or f"@@TVCLWIKI{len(chips)-1}@@", text or "")

    def inline(line):
        line = esc(line)
        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)
        line = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", line)
        line = re.sub(r"`([^`]+)`", r"<code>\1</code>", line)
        for i, chip in enumerate(chips):
            line = line.replace(f"@@TVCLWIKI{i}@@", chip)
        return line

    blocks, paragraph, listing, list_tag = [], [], [], None
    def flush_paragraph():
        if paragraph:
            blocks.append("<p>" + " ".join(inline(x.strip()) for x in paragraph) + "</p>")
            paragraph.clear()
    def flush_list():
        nonlocal list_tag
        if listing:
            blocks.append(f"<{list_tag}>" + "".join(f"<li>{inline(x)}</li>" for x in listing) + f"</{list_tag}>")
            listing.clear()
        list_tag = None

    for raw in value.splitlines():
        line = raw.strip()
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        item = re.match(r"^(?:[-*+•]\s+|(\d+)\.\s+)(.+)$", line)
        if not line:
            flush_paragraph(); flush_list(); continue
        if match:
            flush_paragraph(); flush_list()
            level = min(len(match.group(1)) + 2, 6)
            blocks.append(f"<h{level}>{inline(match.group(2))}</h{level}>")
        elif item:
            flush_paragraph()
            kind = "ol" if item.group(1) else "ul"
            if list_tag and list_tag != kind:
                flush_list()
            list_tag = kind
            listing.append(item.group(2))
        else:
            flush_list(); paragraph.append(line)
    flush_paragraph(); flush_list()
    return "\n".join(blocks)


def schema_for(article, category, data):
    canonical = article["canonicalUrl"]
    author = article.get("authorName", "Bộ Tộc Tử Vi Chữa Lành")
    graph = [
        {"@type": "Article", "headline": article["title"], "description": article["seo"]["metaDescription"],
         "mainEntityOfPage": {"@type": "WebPage", "@id": canonical}, "url": canonical,
         "author": {"@type": "Person", "name": author}, "publisher": {"@type": "Organization", "name": "Bộ Tộc Tử Vi Chữa Lành", "url": SITE + "/"},
         "datePublished": article.get("datePublished", "2026-10-30") + "T08:00:00+07:00", "dateModified": article.get("dateModified", article.get("datePublished", "2026-10-30")) + "T08:00:00+07:00", "articleSection": category["name"], "keywords": article["seo"].get("keywords", []), "inLanguage": "vi"},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["question"], "acceptedAnswer": {"@type": "Answer", "text": f["answer"]}} for f in article.get("faq", [])]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Trang chủ", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Bài viết", "item": SITE + "/bai-viet/"},
            {"@type": "ListItem", "position": 3, "name": category["name"], "item": SITE + "/bai-viet/" + category["id"] + "/"},
            {"@type": "ListItem", "position": 4, "name": article["title"], "item": canonical}
        ]}
    ]
    return {"@context": "https://schema.org", "@graph": graph}


def render_article(article, category, data):
    title = article["seo"].get("metaTitle") or article["title"] + " | Tử Vi Chữa Lành"
    description = article["seo"].get("metaDescription") or article["subtitle"]
    canonical = article["canonicalUrl"]
    tags = "".join(f'<a class="tag-link" href="/bai-viet/?tag={html.escape(key, quote=True)}">✦ {esc(label)}</a>' for key, label in zip(article.get("tags", []), article.get("tagLabels", [])))
    toc = "".join(f'<a href="#{slugify(s["heading"])}">{esc(s["heading"])}</a>' for s in article["sections"])
    sections = "".join(f'<section class="content-section" id="{slugify(s["heading"])}"><h2>{esc(s["heading"])}</h2>{render_markdown(s.get("bodyMarkdown", ""))}</section>' for s in article["sections"])
    faqs = "".join(f'<details class="faq-item"><summary>{esc(f["question"])}</summary><p>{esc(f["answer"])}</p></details>' for f in article.get("faq", []))
    prompts = "".join(f'<li>{esc(p)}</li>' for p in article.get("reflectionPrompts", []))
    wiki = json_script(data["wikiEntries"])
    schema = json_script(schema_for(article, category, data))
    tags_json = json_script(article.get("tags", []))
    related = sorted((x for x in data["articles"] if x["id"] != article["id"]), key=lambda x: sum(t in x.get("tags", []) for t in article.get("tags", [])), reverse=True)[:4]
    related_html = "".join(f'<a class="related-card" href="{article_url(a)}"><span>{esc(a["categoryName"])}</span><strong>{esc(a["title"])}</strong></a>' for a in related)
    prev_next = data["articles"]
    i = next(i for i, a in enumerate(prev_next) if a["id"] == article["id"])
    prev = f'<a href="{article_url(prev_next[i-1])}">← {esc(prev_next[i-1]["title"])}</a>' if i else '<a href="/bai-viet/">← Về thư viện bài viết</a>'
    nxt = f'<a href="{article_url(prev_next[i+1])}">{esc(prev_next[i+1]["title"])} →</a>' if i+1 < len(prev_next) else '<a href="/bai-viet/">Khám phá thêm bài viết →</a>'
    return f'''<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{esc(canonical)}"><meta property="og:type" content="article"><meta property="og:site_name" content="Tử Vi Chữa Lành — Bộ Tộc Tử Vi Chữa Lành">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(canonical)}"><meta property="og:image" content="{SITE}/assets/img/hero-shanshui.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description)}">
<script type="application/ld+json">{schema}</script><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap" rel="stylesheet">
<style>
:root{{--paper:#fcfbf9;--ink:#1e293b;--blue:#0369a1;--green:#047857;--font:18px}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:var(--font)/1.78 Inter,Arial,sans-serif}}body.warm{{--paper:#f7f1e3}}a{{color:var(--blue)}}.topline{{height:4px;position:fixed;top:0;z-index:5;background:linear-gradient(90deg,#f59e0b,#0ea5e9,#10b981);width:0}}header{{background:#0f172a;color:#e2e8f0;padding:1rem clamp(1rem,5vw,4rem);display:flex;justify-content:space-between;align-items:center;gap:1rem}}header a{{color:white;text-decoration:none;font-weight:700}}header nav{{display:flex;gap:1rem;flex-wrap:wrap;font-size:.85rem}}.wrap{{max-width:1200px;margin:auto;padding:1rem clamp(1rem,4vw,3rem) 4rem}}.crumbs{{font-size:.82rem;color:#64748b;margin:1rem 0 2rem}}.hero{{border-radius:1.2rem;padding:clamp(1.5rem,4vw,3.2rem);color:white;background:linear-gradient(115deg,#0f172aeb,#075985d9),url('/assets/img/hero-shanshui.jpg') center/cover;margin-bottom:1.5rem}}.eyebrow{{color:#fbbf24;font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase}}h1,h2,h3{{font-family:'Playfair Display',Georgia,serif;line-height:1.3}}h1{{font-size:clamp(2rem,4vw,3.1rem);margin:.5rem 0}}.subtitle{{font-size:1.05rem;max-width:800px;color:#f1f5f9}}.tools,.chips,.tag-list,.nav-row{{display:flex;gap:.5rem;flex-wrap:wrap;align-items:center}}.tools button,.tools a,.tag-link{{border:1px solid #cbd5e1;border-radius:999px;background:#fff;color:#334155;padding:.4rem .75rem;cursor:pointer;text-decoration:none;font:600 .82rem Inter,Arial}}.layout{{display:grid;grid-template-columns:minmax(0,1fr) 270px;gap:2rem;align-items:start}}main{{min-width:0}}aside{{position:sticky;top:1rem;background:#fff;border:1px solid #e7e5e4;border-radius:1rem;padding:1rem}}aside h2{{font-size:1.15rem;margin:.2rem 0 .8rem}}aside a{{display:block;font-size:.82rem;text-decoration:none;margin:.45rem 0;color:#475569}}.summary,.myth,.flow,.practice,.faq{{background:#fff;border:1px solid #e7e5e4;border-radius:1rem;padding:1.2rem;margin:1rem 0}}.summary{{border-left:4px solid #f59e0b}}.myth-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1rem}}.myth-grid div{{background:#f8fafc;padding:.8rem;border-radius:.8rem}}.content-section{{margin:2rem 0}}.content-section h2{{font-size:1.65rem;border-bottom:1px solid #e7e5e4;padding-bottom:.5rem}}.content-section h3{{font-size:1.2rem}}.content-section p,.content-section li{{line-height:1.9}}.wiki-chip{{display:inline-flex;align-items:center;border:1px solid #bae6fd;background:#f0f9ff;color:#0369a1;border-radius:999px;padding:.05rem .55rem;font:600 .86em Inter;cursor:pointer}}.tags{{margin:1.5rem 0}}.tag-link{{display:inline-flex;margin:.2rem}}.related{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.7rem}}.related-card{{display:flex;flex-direction:column;background:#fff;border:1px solid #e7e5e4;border-radius:.8rem;padding:.9rem;text-decoration:none;color:#1e293b;line-height:1.5}}.related-card span{{font-size:.7rem;color:#047857;margin-bottom:.3rem}}.related-card strong{{font-family:'Playfair Display',Georgia,serif}}.prevnext{{display:flex;justify-content:space-between;gap:1rem;margin:2rem 0}}.prevnext a{{max-width:48%;text-decoration:none}}.modal{{position:fixed;inset:0;background:#0f172a99;display:none;place-items:center;padding:1rem;z-index:10}}.modal.open{{display:grid}}.modal-card{{max-width:560px;width:100%;background:#fff;border-radius:1rem;padding:1.5rem;box-shadow:0 20px 70px #0003}}.modal-card h2{{margin-top:0}}.close{{float:right;border:0;background:none;font-size:1.5rem;cursor:pointer}}footer{{background:#0f172a;color:#cbd5e1;padding:2rem;text-align:center;font-size:.85rem}}@media(max-width:800px){{.layout{{grid-template-columns:1fr}}aside{{position:static;order:-1}}.myth-grid,.related{{grid-template-columns:1fr}}header{{align-items:flex-start;flex-direction:column}}}}
</style></head><body><div class="topline" id="progress"></div>
<header><a href="/">✦ Tử Vi Chữa Lành</a><nav><a href="/">Trang chủ</a><a href="/bai-viet/">Bài viết & Chiêm nghiệm</a><a href="/khoa-hoc-tu-vi-chua-lanh/">Khóa học</a></nav></header>
<div class="wrap"><div class="crumbs"><a href="/">Trang chủ</a> › <a href="/bai-viet/">Bài viết</a> › <a href="/bai-viet/{category['id']}/">{esc(category['shortName'])}</a> › {esc(article['title'])}</div>
<section class="hero"><div class="eyebrow">{esc(category['name'])} · {esc(article.get('readTime',''))} đọc</div><h1>{esc(article['title'])}</h1><p class="subtitle">{esc(article['subtitle'])}</p><p>Chia sẻ bởi {esc(article.get('authorName','Bộ Tộc Tử Vi Chữa Lành'))}</p></section>
<div class="tools" aria-label="Tùy chỉnh trải nghiệm đọc"><button id="font-down" type="button" aria-label="Giảm cỡ chữ">A−</button><button id="font-up" type="button" aria-label="Tăng cỡ chữ">A+</button><button id="warm-toggle" type="button">Nền giấy ấm</button><a href="/bai-viet/">Tìm và lọc bài viết</a></div>
<div class="layout"><main id="article-content"><section class="summary"><h2>✦ Điểm cốt lõi trong 30 giây</h2><p>{esc(article['subtitle'])}</p></section>
<section class="myth"><h2>Lầm tưởng thường gặp và góc nhìn Tử Vi Chữa Lành</h2><div class="myth-grid"><div><h3>Lầm tưởng</h3><p>{esc(article['mythVsTruth']['myth'])}</p></div><div><h3>Góc nhìn chữa lành</h3><p>{esc(article['mythVsTruth']['truth'])}</p></div></div></section>
<section class="flow"><h2>Nhìn lá số qua nhiều lớp</h2><p>{render_markdown(article.get('chart3P4CAxes',''))}</p><ol>{''.join(f'<li><strong>{esc(s["step"])}</strong>: {render_markdown(s["description"])}</li>' for s in article.get('causalFlow5Steps',[]))}</ol></section>
{sections}<section class="content-section" id="cau-hoi-thuong-gap"><h2>Câu hỏi thường gặp</h2>{faqs}</section>
<section class="practice"><h2>Câu hỏi tự soi chiếu</h2><ul>{prompts}</ul><h3>🌱 Thực hành nhỏ hôm nay</h3><p>{esc(article.get('microPractice',''))}</p></section>
<div class="tags"><h2>Đọc tiếp theo Sao, Cung và chủ đề</h2><div class="tag-list">{tags}</div></div>
<section class="content-section"><h2>Bài viết liên quan</h2><div class="related">{related_html}</div></section><nav class="prevnext" aria-label="Bài viết trước và tiếp theo">{prev}{nxt}</nav></main>
<aside><h2>📑 Mục lục nội dung</h2>{toc}<a href="#cau-hoi-thuong-gap">Câu hỏi thường gặp</a><hr><h2>Bắt đầu từ đây</h2><a href="/bai-viet/">8 bài nền tảng và toàn bộ thư viện</a><a href="/bai-viet/{category['id']}/">Xem chuyên đề {esc(category['shortName'])}</a></aside></div></div>
<footer>✦ Lá số là bản đồ, không phải bản án. · Tử Vi, Tâm lý và Đạo học cùng soi sáng con đường chuyển hóa.</footer>
<div class="modal" id="wiki-modal" role="dialog" aria-modal="true" aria-labelledby="wiki-title"><div class="modal-card"><button class="close" id="wiki-close" aria-label="Đóng">×</button><p class="eyebrow">Tàng Kinh Các</p><h2 id="wiki-title"></h2><p id="wiki-type"></p><p id="wiki-summary"></p><h3>Góc nhìn chuyển hóa</h3><p id="wiki-healing"></p><a id="wiki-filter" href="/bai-viet/">Tìm các bài viết cùng chủ đề →</a></div></div>
<script>
const WIKI={wiki};const TAGS={tags_json};const CONTENT=document.getElementById('article-content');
document.addEventListener('click',e=>{{const b=e.target.closest('[data-wiki-key]');if(b){{const k=b.dataset.wikiKey,x=WIKI[k];if(!x)return;document.getElementById('wiki-title').textContent=x.title;document.getElementById('wiki-type').textContent=x.type;document.getElementById('wiki-summary').textContent=x.summary;document.getElementById('wiki-healing').textContent=x.healingView;document.getElementById('wiki-filter').href='/bai-viet/?tag='+encodeURIComponent(k);document.getElementById('wiki-modal').classList.add('open')}}}});
document.getElementById('wiki-close').onclick=()=>document.getElementById('wiki-modal').classList.remove('open');document.getElementById('wiki-modal').onclick=e=>{{if(e.target.id==='wiki-modal')e.currentTarget.classList.remove('open')}};
document.getElementById('font-down').onclick=()=>document.documentElement.style.setProperty('--font',Math.max(15,parseInt(getComputedStyle(document.documentElement).getPropertyValue('--font'))-1)+'px');document.getElementById('font-up').onclick=()=>document.documentElement.style.setProperty('--font',Math.min(23,parseInt(getComputedStyle(document.documentElement).getPropertyValue('--font'))+1)+'px');document.getElementById('warm-toggle').onclick=()=>document.body.classList.toggle('warm');
const progress=()=>{{const max=document.documentElement.scrollHeight-innerHeight;document.getElementById('progress').style.width=(max>0?scrollY/max*100:0)+'%'}};addEventListener('scroll',progress,{{passive:true}});progress();
</script></body></html>'''


def render_article_news(article, category, data):
    title = article["seo"].get("metaTitle") or article["title"] + " | Tử Vi Chữa Lành"
    description = article["seo"].get("metaDescription") or article["subtitle"]
    canonical = article["canonicalUrl"]
    tags = "".join(f'<a class="reader-tag" href="/bai-viet/?tag={html.escape(k, quote=True)}">{esc(label)}</a>' for k, label in zip(article.get("tags", []), article.get("tagLabels", [])))
    toc = "".join(f'<a href="#{slugify(s["heading"])}">{esc(s["heading"])}</a>' for s in article["sections"])
    sections = "".join(f'<section class="reader-section" id="{slugify(s["heading"])}"><h2>{esc(s["heading"])}</h2>{render_markdown(s.get("bodyMarkdown", ""))}</section>' for s in article["sections"])
    faqs = "".join(f'<details class="reader-faq-item"><summary>{esc(f["question"])}</summary><p>{esc(f["answer"])}</p></details>' for f in article.get("faq", []))
    prompts = "".join(f'<li>{esc(p)}</li>' for p in article.get("reflectionPrompts", []))
    steps = "".join(f'<li><b>{esc(s["step"])}</b><p>{render_markdown(s["description"])}</p></li>' for s in article.get("causalFlow5Steps", []))
    wiki = json_script(data["wikiEntries"])
    schema = json_script(schema_for(article, category, data))
    related = sorted((x for x in data["articles"] if x["id"] != article["id"]), key=lambda x: sum(t in x.get("tags", []) for t in article.get("tags", [])), reverse=True)[:4]
    related_html = "".join(f'<a class="reader-related-card" href="{article_url(a)}"><span>{esc(a["categoryName"])} · {esc(a.get("readTime",""))}</span><strong>{esc(a["title"])}</strong></a>' for a in related)
    i = next(i for i, a in enumerate(data["articles"]) if a["id"] == article["id"])
    prev = f'<a href="{article_url(data["articles"][i-1])}">← {esc(data["articles"][i-1]["title"])}</a>' if i else '<a href="/bai-viet/">← Về thư viện</a>'
    nxt = f'<a href="{article_url(data["articles"][i+1])}">{esc(data["articles"][i+1]["title"])} →</a>' if i+1 < len(data["articles"]) else '<a href="/bai-viet/">Khám phá thêm bài viết →</a>'
    return f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="robots" content="index, follow, max-image-preview:large"><link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="article"><meta property="og:site_name" content="Tử Vi Chữa Lành — Bộ Tộc Tử Vi Chữa Lành"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{esc(canonical)}"><meta property="og:image" content="{SITE}/assets/img/{'bai-viet-ban-do-la-so.svg' if article['id'] == 'la-so-tu-vi-co-phai-la-ban-an-dinh-menh' else 'hero-shanshui.jpg'}"><meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{schema}</script><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&family=Cormorant+Garamond:wght@500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="/assets/css/style.css"><link rel="stylesheet" href="/assets/css/homepage-nav.css"><link rel="stylesheet" href="/bai-viet/assets/newsroom.css"><style>{reader_css()}</style></head>
<body class="reader-page"><a class="skip-link" href="#reader-content">Bỏ qua điều hướng</a><div class="reader-progress" id="progress"></div><header class="site-header"><div class="site-header-inner"><a href="/" class="brand-lockup"><span class="logo-mark" role="img" aria-label="Logo Tử Vi Chữa Lành"></span><span class="titles"><span class="main-title">Tử Vi Chữa Lành</span><span class="sub-title">Bộ Tộc Tử Vi Chữa Lành</span></span></a><nav class="main-nav" aria-label="Điều hướng chính"><a class="nav-home" href="/">Trang chủ</a><a class="active" aria-current="page" href="/bai-viet/">Bài viết &amp; Chiêm nghiệm</a><a href="/khoa-hoc-tu-vi-chua-lanh/">Khóa học</a></nav></div></header><script src="/assets/js/homepage-nav.js" defer></script>
<main id="reader-content" class="reader-shell"><nav class="crumb" aria-label="Đường dẫn"><a href="/">Trang chủ</a><span>/</span><a href="/bai-viet/">Bài viết</a><span>/</span><a href="/bai-viet/{category['id']}/">{esc(category['shortName'])}</a></nav>
<article><header class="reader-head"><p class="kicker">{esc(category['shortName'])} <span>·</span> {esc(article.get('readTime',''))} đọc</p><h1>{esc(article['title'])}</h1><p class="reader-deck">{esc(article['subtitle'])}</p><p class="reader-byline">Chia sẻ bởi {esc(article.get('authorName','Bộ Tộc Tử Vi Chữa Lành'))}</p><div class="reader-tags">{tags}</div></header>
<div class="reader-controls" aria-label="Tùy chỉnh trải nghiệm đọc"><button id="font-down" type="button" aria-label="Giảm cỡ chữ">A−</button><button id="font-up" type="button" aria-label="Tăng cỡ chữ">A+</button><button id="warm-toggle" type="button" aria-pressed="false">Nền giấy ấm</button><a href="/bai-viet/">Tìm bài khác</a></div>
<div class="reader-layout"><div class="reader-main"><section class="causal-thread"><h2>Mạch soi chiếu</h2><p>{render_markdown(article.get('chart3P4CAxes',''))}</p><ol>{steps}</ol></section>{sections}
<section class="two-views"><h2>Hai góc nhìn</h2><div><p><b>Lầm tưởng thường gặp</b>{esc(article['mythVsTruth']['myth'])}</p><p><b>Góc nhìn Tử Vi Chữa Lành</b>{esc(article['mythVsTruth']['truth'])}</p></div></section>
<section class="reader-faq" id="cau-hoi-thuong-gap"><h2>Câu hỏi thường gặp</h2>{faqs}</section><section class="reflection"><h2>Câu hỏi tự soi chiếu</h2><ul>{prompts}</ul><h3>Thực hành nhỏ hôm nay</h3><p>{esc(article.get('microPractice',''))}</p></section>
<section class="related-section"><h2>Bài viết cùng Sao, Cung và chủ đề</h2><div>{related_html}</div></section><nav class="reader-prevnext" aria-label="Bài viết trước và tiếp theo">{prev}{nxt}</nav></div>
<aside class="reader-toc"><h2>Mục lục bài viết</h2><nav>{toc}<a href="#cau-hoi-thuong-gap">Câu hỏi thường gặp</a></nav><a class="toc-exit" href="/bai-viet/{category['id']}/">Xem chuyên đề →</a><a class="toc-exit" href="/bai-viet/">Tìm trong thư viện →</a></aside></div></article></main>
<footer class="reader-footer"><span>Tử Vi Chữa Lành · Lá số là bản đồ, không phải bản án.</span><a href="/">Về trang chủ</a></footer>
<div class="wiki-modal" id="wiki-modal" role="dialog" aria-modal="true" aria-labelledby="wiki-title"><div class="wiki-card"><button id="wiki-close" class="wiki-close" aria-label="Đóng cửa sổ tra cứu">×</button><p class="kicker">Tàng Kinh Các</p><h2 id="wiki-title"></h2><p id="wiki-type"></p><p id="wiki-summary"></p><h3>Góc nhìn chuyển hóa</h3><p id="wiki-healing"></p><a id="wiki-filter" href="/bai-viet/">Tìm các bài cùng chủ đề →</a></div></div>
<script>const WIKI={wiki};const modal=document.getElementById('wiki-modal');document.addEventListener('click',e=>{{const b=e.target.closest('[data-wiki-key]');if(b){{const x=WIKI[b.dataset.wikiKey];if(!x)return;document.getElementById('wiki-title').textContent=x.title;document.getElementById('wiki-type').textContent=x.type;document.getElementById('wiki-summary').textContent=x.summary;document.getElementById('wiki-healing').textContent=x.healingView;document.getElementById('wiki-filter').href='/bai-viet/?tag='+encodeURIComponent(b.dataset.wikiKey);modal.classList.add('open')}}}});document.getElementById('wiki-close').onclick=()=>modal.classList.remove('open');modal.onclick=e=>{{if(e.target===modal)modal.classList.remove('open')}};document.addEventListener('keydown',e=>{{if(e.key==='Escape')modal.classList.remove('open')}});let fs=18;document.getElementById('font-down').onclick=()=>{{fs=Math.max(15,fs-1);document.querySelector('.reader-main').style.setProperty('--reader-font',fs+'px')}};document.getElementById('font-up').onclick=()=>{{fs=Math.min(23,fs+1);document.querySelector('.reader-main').style.setProperty('--reader-font',fs+'px')}};document.getElementById('warm-toggle').onclick=e=>{{const v=document.body.classList.toggle('warm');e.currentTarget.setAttribute('aria-pressed',String(v))}};const tick=()=>{{const m=document.documentElement.scrollHeight-innerHeight;document.getElementById('progress').style.width=(m>0?scrollY/m*100:0)+'%'}};addEventListener('scroll',tick,{{passive:true}});tick();</script></body></html>'''


def reader_css():
    return r'''
.reader-page{--reader-font:18px}.reader-shell{max-width:1220px;margin:auto;padding:0 28px 72px}.reader-head{max-width:900px;margin:4px auto 0;padding:15px 0 25px;border-bottom:1px solid var(--line-dark)}.reader-head>.kicker{margin-bottom:8px}.reader-head h1{font:600 clamp(40px,5.2vw,66px)/.98 var(--display);letter-spacing:-.025em;margin:0 0 14px}.reader-deck{max-width:820px;margin:0;font:21px/1.5 var(--serif);color:var(--ink-soft)}.reader-byline{margin:14px 0 0;color:var(--muted);font:11px var(--sans)}.reader-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:15px}.reader-tag{padding:5px 8px;border:1px solid var(--line);background:var(--surface);color:var(--forest);font:500 10px var(--sans);text-decoration:none}.reader-tag:hover{border-color:var(--forest)}.reader-controls{max-width:900px;margin:15px auto;display:flex;gap:7px}.reader-controls button,.reader-controls a{min-height:38px;padding:7px 11px;border:1px solid var(--line);background:var(--surface);color:var(--forest);font:600 11px var(--sans);text-decoration:none;cursor:pointer}.reader-layout{display:grid;grid-template-columns:minmax(0,760px) 240px;justify-content:center;gap:50px;align-items:start}.reader-main{min-width:0;font:var(--reader-font)/1.85 var(--serif)}.reader-main>section{margin:25px 0}.reader-main h2{font:600 27px/1.15 var(--display);margin:0 0 10px;color:var(--ink)}.two-views{padding:18px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.two-views>div{display:grid;grid-template-columns:1fr 1fr;gap:20px}.two-views p{margin:0;color:var(--ink-soft)}.two-views b{display:block;margin-bottom:4px;font:700 9px var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}.two-views p+p{padding-left:20px;border-left:1px solid var(--line)}.causal-thread{padding-bottom:18px;border-bottom:1px solid var(--line)}.causal-thread>p{margin:0 0 12px;color:var(--ink-soft)}.causal-thread ol{display:grid;grid-template-columns:repeat(5,1fr);list-style:none;padding:0;margin:0}.causal-thread li{padding:8px 9px 0 0;border-top:1px solid var(--line-dark)}.causal-thread li+li{padding-left:10px;border-left:1px solid var(--line)}.causal-thread li>b{font:700 9px/1.4 var(--sans);color:var(--forest)}.causal-thread li p{margin:4px 0 0;color:var(--muted);font:12px/1.45 var(--serif)}.reader-section{margin:33px 0!important}.reader-section h2{font:600 34px/1.1 var(--display);margin:0 0 14px;padding:0;border:0}.reader-section p{margin:0 0 14px;line-height:1.9}.reader-section h3{font:600 23px/1.25 var(--display)}.wiki-chip{border:0;border-bottom:1px solid #79a597;border-radius:0;background:transparent;color:var(--forest);padding:0 1px;font:600 .94em var(--serif);cursor:pointer}.wiki-chip:hover{background:#e4eae0}.reader-toc{position:sticky;top:12px;border-left:1px solid var(--line-dark);padding-left:17px}.reader-toc h2{font:700 9px var(--sans);letter-spacing:.13em;text-transform:uppercase;color:var(--clay);margin:0 0 9px}.reader-toc nav a{display:block;margin:0;padding:7px 0;border-bottom:1px solid var(--line);font:12px/1.35 var(--serif);color:var(--ink-soft);text-decoration:none}.reader-toc nav a:hover,.toc-exit:hover{color:var(--forest);text-decoration:underline}.toc-exit{display:block;margin-top:12px;font:600 10px var(--sans);color:var(--forest);text-decoration:none}.reader-faq{padding-top:20px;border-top:1px solid var(--line-dark)}.reader-faq-item{padding:12px 0;border-bottom:1px solid var(--line)}.reader-faq-item summary{cursor:pointer;font:600 17px/1.4 var(--serif)}.reader-faq-item p{color:var(--muted);margin:8px 0 0}.reflection{padding:18px;background:#eee9dc}.reflection h3{font:600 23px var(--display);margin:16px 0 4px}.reflection ul{padding-left:20px}.related-section{padding-top:21px;border-top:1px solid var(--line-dark)}.related-section>div{display:grid;grid-template-columns:1fr 1fr;gap:0 22px}.reader-related-card{display:block;padding:13px 0;border-bottom:1px solid var(--line);text-decoration:none;color:var(--ink)}.reader-related-card span{display:block;margin-bottom:3px;font:700 9px var(--sans);color:var(--clay)}.reader-related-card strong{font:600 19px var(--display)}.reader-related-card:hover strong{color:var(--forest);text-decoration:underline;text-decoration-color:var(--amber)}.reader-prevnext{display:flex;justify-content:space-between;gap:20px;margin:30px 0;padding-top:16px;border-top:1px solid var(--line)}.reader-prevnext a{max-width:48%;font:12px/1.4 var(--sans);color:var(--forest);text-decoration:none}.reader-footer{display:flex;justify-content:space-between;gap:15px;padding:22px max(calc((100vw - 1220px)/2 + 28px),28px);background:#e9e5d9;color:var(--ink-soft);font:11px var(--sans)}.reader-footer a{color:var(--forest);text-decoration:none}.wiki-modal{position:fixed;inset:0;z-index:30;display:none;place-items:center;padding:18px;background:#102b26a6}.wiki-modal.open{display:grid}.wiki-card{max-width:540px;width:100%;padding:24px;background:var(--surface);border:1px solid var(--line-dark);box-shadow:0 22px 70px #12282044}.wiki-card h2{font:600 32px var(--display);margin:8px 50px 0 0}.wiki-card h3{font:700 9px var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--clay)}.wiki-card p{font:15px/1.65 var(--serif)}.wiki-card>a{color:var(--forest);font:600 12px var(--sans)}.wiki-close{float:right;width:40px;height:40px;border:1px solid var(--line);background:transparent;color:var(--ink);font:22px var(--sans);cursor:pointer}.reader-page a:focus-visible,.reader-page button:focus-visible,.reader-page summary:focus-visible{outline:3px solid var(--amber);outline-offset:3px}
@media(max-width:850px){.reader-layout{grid-template-columns:minmax(0,1fr) 205px;gap:25px}.causal-thread ol{grid-template-columns:repeat(3,1fr);row-gap:12px}}
@media(max-width:680px){.reader-shell{padding:0 18px 48px}.reader-head h1{font-size:44px}.reader-deck{font-size:18px}.reader-layout{grid-template-columns:1fr;gap:15px}.reader-toc{position:static;order:-1;border:1px solid var(--line);padding:12px;background:var(--surface)}.reader-toc nav{display:grid;grid-template-columns:1fr 1fr;gap:0 10px}.reader-toc h2{margin-bottom:5px}.causal-thread ol{grid-template-columns:1fr 1fr}.two-views>div{grid-template-columns:1fr;gap:12px}.two-views p+p{padding:12px 0 0;border:0;border-top:1px solid var(--line)}.related-section>div{grid-template-columns:1fr}.reader-footer{padding:18px;flex-direction:column}.reader-prevnext{font-size:10px}}
'''


def render_articles(data):
    KB = LT.load_kb()
    categories = {c["id"]: c for c in data["categories"]}
    for article in data["articles"]:
        category = categories[article["category"]]
        path = OUT / article["category"] / article["id"] / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(LT.render_article(article, category, data, KB, sys.modules[__name__]), encoding="utf-8")


def update_sitemap(data):
    sitemap = ROOT / "sitemap.xml"
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    text = sitemap.read_text(encoding="utf-8") if sitemap.exists() else '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>\n'
    root = ET.fromstring(text)
    existing = {node.findtext(ns + "loc") for node in root.findall(ns + "url")}
    urls = [(SITE + "/bai-viet/", "0.9")]
    urls.extend((SITE + f"/bai-viet/{c['id']}/", "0.8") for c in data["categories"])
    urls.extend((a["canonicalUrl"], "0.7") for a in data["articles"])
    additions = [f"  <url>\n    <loc>{html.escape(url)}</loc>\n    <priority>{priority}</priority>\n  </url>" for url, priority in urls if url not in existing]
    if additions:
        close = text.rfind("</urlset>")
        if close < 0:
            raise ValueError("sitemap.xml thiếu thẻ đóng urlset")
        prefix = text[:close].rstrip()
        text = prefix + "\n" + "\n".join(additions) + "\n</urlset>\n"
        sitemap.write_text(text, encoding="utf-8")


def build():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if len(data.get("articles", [])) != 80 or sum(len(group["items"]) for group in data.get("tagGroups", [])) != 45 or len(data.get("wikiEntries", {})) != 45:
        raise ValueError("Nguồn chuyên mục không khớp số lượng 80 bài và 45 mục từ điển/thẻ lọc.")
    render_hubs(data)
    render_articles(data)
    update_sitemap(data)
    print(f"Generated 5 category hubs and {len(data['articles'])} static articles in {OUT}")


if __name__ == "__main__":
    build()
