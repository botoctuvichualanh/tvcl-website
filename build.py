#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build script — TVCL Knowledge Base website (static HTML)."""
import re, os, html, base64, json, secrets
import markdown as md
from unidecode import unidecode
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = os.path.dirname(os.path.abspath(__file__))
KB = "/sessions/tender-compassionate-noether/mnt/TVCL AI Co-work/01_KnowledgeBase"
OVERRIDE_DIR = "/sessions/tender-compassionate-noether/mnt/outputs/web_overrides"
DOCS_OUT = os.path.join(ROOT, "docs")

SITE_TITLE = "Tử Vi Chữa Lành"
COMMUNITY = "Bộ Tộc Tử Vi Chữa Lành"
SLOGAN = "Tử Vi Chữa Lành: Ứng dụng Tử Vi, Tâm Lý, Đạo Học để Hiểu Mình, Cải Mệnh & Chữa Lành"
TAGLINE = "Lá số là bản đồ, không phải bản án"
SITE_URL = "https://tuvichualanh.com"
SITE_DESC = "Tử Vi Chữa Lành kết hợp Tử Vi, Tâm lý học, Phật học và Đạo học để giúp bạn hiểu mình, nhận diện khuynh hướng, thuận thời và chuyển hóa cuộc sống. Lá số là bản đồ, không phải bản án."
HOME_OG_TITLE = f"{SITE_TITLE} | Tử Vi, Tâm lý & Đạo học"
HOME_OG_DESC = "Ứng dụng Tử Vi, Tâm lý và Đạo học trên hành trình Hiểu Mình – Cải Mệnh – Chữa Lành."
HERO_SUBTITLE = "Ứng dụng Tử Vi, Tâm lý và Đạo học trên hành trình Hiểu Mình – Cải Mệnh – Chữa Lành."
PHILOSOPHY_SUB = "Tử Vi cho ta thấy khuynh hướng. Nhận thức và hành động quyết định cách ta bước đi cùng khuynh hướng ấy."
OG_IMAGE = f"{SITE_URL}/assets/img/hero-shanshui.jpg"
FAVICON = f"{SITE_URL}/assets/img/logo.png"
GA_MEASUREMENT_ID = "G-KQS81YHTXF"
GA_SNIPPET = f'''<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_MEASUREMENT_ID}');
</script>'''

# ---- Password-gated categories -----------------------------------------
# Nội dung của các category có id trong set này sẽ bị mã hóa AES-256-GCM
# ngay trong file HTML tĩnh (không cần server). Người đọc phải nhập đúng
# SITE_PASSWORD thì trình duyệt mới giải mã và hiển thị được nội dung.
# ĐỔI MẬT KHẨU: KHÔNG hardcode ở đây (repo là public, hardcode = lộ mật khẩu
# cho bất kỳ ai xem source trên GitHub). Đặt biến môi trường TVCL_SITE_PASSWORD
# trước khi build, ví dụ:
#   export TVCL_SITE_PASSWORD='mat-khau-moi'
#   python3 build.py
PROTECTED_CATEGORY_IDS = {"lieu-phap-tam-ly", "tu-vi-dao-hoc", "ban-do-nhan-qua", "tai-loc", "toan-thu"}
SITE_PASSWORD = os.environ.get("TVCL_SITE_PASSWORD")
if not SITE_PASSWORD:
    raise SystemExit(
        "Thiếu biến môi trường TVCL_SITE_PASSWORD — không tìm thấy mật khẩu để mã hóa "
        "nội dung protected. Đặt: export TVCL_SITE_PASSWORD='mat-khau-cua-ban' rồi chạy lại."
    )
PBKDF2_ITERATIONS = 200000

# ---- Per-page SEO overrides ---------------------------------------------
# Mặc định, <title>/<meta description>/OG/Twitter/JSON-LD của mỗi trang doc
# dùng chung mô tả của cả category (cat["desc"]) — điều này khiến nhiều
# trang có description trùng nhau, không khớp đúng từ khóa người dùng hay
# tìm (ví dụ "sao Thiên Cơ là sao gì"). DOC_META_OVERRIDES cho phép đặt
# title/description riêng cho từng trang theo slug, ưu tiên tên các sao/cung
# cụ thể để tăng khả năng khớp truy vấn tìm kiếm thực tế.
DOC_META_OVERRIDES = {
    "05-12-cung": {
        "title": "12 Cung Trong Tử Vi: Mệnh, Quan Lộc, Tài Bạch, Phu Thê...",
        "desc": "Giải mã 12 Cung trong lá số Tử Vi — Cung Mệnh, Phúc Đức, Tật Ách, Quan Lộc, Tài Bạch, Điền Trạch, Phụ Mẫu, Phu Thê, Tử Tức, Huynh Đệ, Nô Bộc, Thiên Di — theo Tử Vi Chữa Lành, ứng dụng Tâm lý học để Hiểu Mình.",
    },
    "06-14-chinh-tinh": {
        "title": "14 Chính Tinh Là Sao Gì? Tử Vi, Thiên Cơ, Thái Dương...",
        "desc": "Sao Tử Vi, Thiên Cơ, Thái Dương, Vũ Khúc, Thiên Đồng, Liêm Trinh, Thiên Phủ, Thái Âm, Tham Lang, Cự Môn, Thiên Tướng, Thiên Lương, Thất Sát, Phá Quân là sao gì? Luận giải đủ 14 Chính Tinh theo Tử Vi Chữa Lành.",
    },
    "07-hung-tinh": {
        "title": "Hung Tinh Là Sao Gì? Kình Dương, Đà La, Hỏa Tinh, Địa Không...",
        "desc": "Hung tinh là vùng bài học cần chữa lành, không phải lời nguyền. Luận giải Kình Dương, Đà La, Hỏa Tinh, Linh Tinh, Địa Không, Địa Kiếp — đủ Mặt Sáng, Mặt Tối và hướng chuyển hóa theo Tử Vi Chữa Lành.",
    },
    "08-cat-tinh": {
        "title": "Cát Tinh Là Sao Gì? Tả Phù, Hữu Bật, Văn Xương, Thiên Khôi...",
        "desc": "Cát tinh là phước báu cần dụng. Luận giải Tả Phù, Hữu Bật, Văn Xương, Văn Khúc, Thiên Khôi, Thiên Việt — ý nghĩa và cách khai thác năng lượng sao theo Tử Vi Chữa Lành.",
    },
}

def encrypt_for_gate(html_str, password):
    """AES-256-GCM encrypt with a PBKDF2-derived key — decryptable in-browser
    via the Web Crypto API (see assets/js/protect.js). Fresh salt/iv per doc."""
    salt = secrets.token_bytes(16)
    iv = secrets.token_bytes(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=PBKDF2_ITERATIONS)
    key = kdf.derive(password.encode("utf-8"))
    ct = AESGCM(key).encrypt(iv, html_str.encode("utf-8"), None)
    return {
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ct": base64.b64encode(ct).decode(),
        "iter": PBKDF2_ITERATIONS,
    }

# Web-only rewritten versions (trimmed / reworded for public readers).
# Original KB core files stay untouched as the internal source of truth.
OVERRIDES = {
    "core_12_files/01_TVCL_CONSTITUTION.md": os.path.join(OVERRIDE_DIR, "01_TVCL_CONSTITUTION_web.md"),
    "core_12_files/04_TVCL_RESPONSE_FRAMEWORK.md": os.path.join(OVERRIDE_DIR, "04_TVCL_RESPONSE_FRAMEWORK_web.md"),
    "core_12_files/11_TVCL_WRITING_GUIDE.md": os.path.join(OVERRIDE_DIR, "11_TVCL_WRITING_GUIDE_web.md"),
    "core_12_files/10_TVCL_BRAND_GUIDE.md": os.path.join(OVERRIDE_DIR, "10_TVCL_BRAND_GUIDE_web.md"),
    "core_12_files/12_TVCL_BRAND_ASSETS.md": os.path.join(OVERRIDE_DIR, "12_TVCL_BRAND_ASSETS_web.md"),
    "web_override/TVCL_TuVi_DauSo_ToanThu_14ChinhTinh.md": os.path.join(OVERRIDE_DIR, "TVCL_TuVi_DauSo_ToanThu_14ChinhTinh.md"),
    "web_override/LieuPhap_cbt.md": os.path.join(OVERRIDE_DIR, "LieuPhap_cbt.md"),
    "web_override/LieuPhap_act.md": os.path.join(OVERRIDE_DIR, "LieuPhap_act.md"),
    "web_override/LieuPhap_ifs.md": os.path.join(OVERRIDE_DIR, "LieuPhap_ifs.md"),
    "web_override/LieuPhap_tongquan.md": os.path.join(OVERRIDE_DIR, "LieuPhap_tongquan.md"),
    "web_override/DaoHoc_daophat.md": os.path.join(OVERRIDE_DIR, "DaoHoc_daophat.md"),
    "web_override/DaoHoc_daogiao.md": os.path.join(OVERRIDE_DIR, "DaoHoc_daogiao.md"),
    "web_override/DaoHoc_linhhon.md": os.path.join(OVERRIDE_DIR, "DaoHoc_linhhon.md"),
    "web_override/BanDoNhanQua.md": os.path.join(OVERRIDE_DIR, "BanDoNhanQua.md"),
    "web_override/ChinhTinhCuCung.md": os.path.join(OVERRIDE_DIR, "ChinhTinhCuCung.md"),
    "web_override/TrungTinhCuCung.md": os.path.join(OVERRIDE_DIR, "TrungTinhCuCung.md"),
    "web_override/TaiLoc_1_NuoiDuong.md": os.path.join(OVERRIDE_DIR, "TaiLoc_1_NuoiDuong.md"),
    "web_override/TaiLoc_2_NiemTin.md": os.path.join(OVERRIDE_DIR, "TaiLoc_2_NiemTin.md"),
    "web_override/TaiLoc_3_KichLoc.md": os.path.join(OVERRIDE_DIR, "TaiLoc_3_KichLoc.md"),
}

CATEGORIES = [
    {
        "id": "gioi-thieu",
        "name": "Giới Thiệu TVCL",
        "desc": "TVCL là gì, tầm nhìn, sứ mệnh, tên gọi và định vị của Bộ Tộc",
        "accent": "outline",
        "show_badge": False,
        "docs": [
            ("core_12_files/10_TVCL_BRAND_GUIDE.md", "10", "Giới Thiệu TVCL"),
            ("core_12_files/12_TVCL_BRAND_ASSETS.md", "12", "Tên Gọi, Slogan & Định Vị"),
        ],
    },
    {
        "id": "nen-tang",
        "name": "Nền Tảng & Triết Lý",
        "desc": "Hiến pháp, triết lý, thuật ngữ và khung luận giải của TVCL",
        "accent": "blue",
        "docs": [
            ("core_12_files/01_TVCL_CONSTITUTION.md", "01", "Hiến Pháp TVCL"),
            ("core_12_files/02_TVCL_GLOSSARY.md", "02", "Từ Điển Thuật Ngữ"),
            ("core_12_files/03_TVCL_PHILOSOPHY.md", "03", "Triết Lý Nền Tảng"),
            ("core_12_files/04_TVCL_RESPONSE_FRAMEWORK.md", "04", "Khung Luận Giải Lá Số"),
            ("core_12_files/11_TVCL_WRITING_GUIDE.md", "11", "Hướng Dẫn Văn Phong"),
        ],
    },
    {
        "id": "tri-thuc-la-so",
        "name": "Tri Thức Lá Số",
        "desc": "12 Cung, 14 Chính Tinh, Cát Tinh, Hung Tinh, Tứ Hóa",
        "accent": "green",
        "docs": [
            ("core_12_files/05_TVCL_12_CUNG.md", "05", "12 Cung"),
            ("core_12_files/06_TVCL_14_CHINH_TINH.md", "06", "14 Chính Tinh"),
            ("core_12_files/07_TVCL_HUNG_TINH.md", "07", "Hung Tinh"),
            ("core_12_files/08_TVCL_CAT_TINH.md", "08", "Cát Tinh"),
            ("core_12_files/09_TVCL_TU_HOA_LOC_MA.md", "09", "Tứ Hóa — Lộc Mã"),
            ("web_override/ChinhTinhCuCung.md", "CC1", "Ý Nghĩa 14 Chính Tinh Cư Tại 12 Cung", "14 Chính Tinh Cư Cung"),
            ("web_override/TrungTinhCuCung.md", "CC2", "Ý Nghĩa 18 Trung Tinh Cư Tại 12 Cung", "18 Trung Tinh Cư Cung"),
        ],
    },
    {
        "id": "lieu-phap-tam-ly",
        "name": "Liệu Pháp Tâm Lý",
        "desc": "CBT, ACT, IFS và góc nhìn Tâm lý học trong chuyển hóa Tử Vi",
        "accent": "teal",
        "docs": [
            ("web_override/LieuPhap_tongquan.md", "T4", "Tử Vi & Tâm Lý Học — Tổng Quan", "Tâm Lý Học Tổng Quan"),
            ("web_override/LieuPhap_cbt.md", "T1", "CBT — Nhận Thức Hành Vi", "CBT"),
            ("web_override/LieuPhap_act.md", "T2", "ACT — Chấp Nhận & Cam Kết", "ACT"),
            ("web_override/LieuPhap_ifs.md", "T3", "IFS — Hệ Thống Gia Đình Nội Tâm", "IFS"),
        ],
    },
    {
        "id": "tu-vi-dao-hoc",
        "name": "Tử Vi & Đạo Học",
        "desc": "Nhân Quả — Đạo Phật, Âm Dương Ngũ Hành — Đạo Giáo, Thuyết Linh Hồn với Tử Vi",
        "accent": "green-outline",
        "docs": [
            ("web_override/DaoHoc_daophat.md", "D1", "Tử Vi & Đạo Phật — Nhân Quả, Nghiệp", "Đạo Phật"),
            ("web_override/DaoHoc_daogiao.md", "D2", "Đạo Giáo & Tử Vi Chữa Lành", "Đạo Giáo"),
            ("web_override/DaoHoc_linhhon.md", "D3", "Thuyết Linh Hồn Với Tử Vi", "Thuyết Linh Hồn"),
        ],
    },
    {
        "id": "ban-do-nhan-qua",
        "name": "Bản Đồ Nhân Quả Trong Tử Vi",
        "desc": "Mô hình SAO → DUYÊN → TÂM → HÀNH → NGHIỆP → VẬN → QUẢ trong Tử Vi Chữa Lành",
        "accent": "ink-outline",
        "docs": [
            ("web_override/BanDoNhanQua.md", "N1", "Bản Đồ Nhân Quả Trong Tử Vi"),
        ],
    },
    {
        "id": "tai-loc",
        "name": "Tử Vi Chữa Lành Tài Lộc",
        "desc": "Nuôi dưỡng khí chất Hóa Lộc, nhận diện niềm tin về tiền và cách kích Lộc cho 10 Chính Tinh Hóa Lộc",
        "accent": "gold",
        "docs": [
            ("web_override/TaiLoc_1_NuoiDuong.md", "TL1", "Nuôi Dưỡng Khí Chất Hóa Lộc"),
            ("web_override/TaiLoc_2_NiemTin.md", "TL2", "Nhận Diện Niềm Tin Về Tiền"),
            ("web_override/TaiLoc_3_KichLoc.md", "TL3", "Cách Kích Lộc Cho 10 Chính Tinh Hóa Lộc"),
        ],
    },
    {
        "id": "tinh-hoa",
        "name": "Tinh Hoa TVCL",
        "desc": "Tóm gọn tinh hoa và tri thức nền tảng của Tử Vi Chữa Lành",
        "accent": "ink",
        "docs": [
            ("ban_thao/TVCL_Sach_TinhHoa.md", "TH1", "Tinh Hoa TVCL"),
        ],
    },
    {
        "id": "toan-thu",
        "name": "Tử Vi Đẩu Số Toàn Thư",
        "desc": "Tri thức từ Tử Vi Đẩu Số Toàn Thư — 14 Chính Tinh chuyên sâu",
        "accent": "teal-outline",
        "docs": [
            ("web_override/TVCL_TuVi_DauSo_ToanThu_14ChinhTinh.md", "TT1", "Tử Vi Đẩu Số Toàn Thư"),
        ],
    },
]

# Sub-item detectors: given (id, title_text) pairs of a doc's H2 headings,
# return the ones that are "browsable items" (star / cung / etc.) so the
# reader can jump straight to them instead of scrolling the whole page.
def _filter_cung(h2s):
    return [(i, t) for i, t in h2s if re.match(r"^\d{1,2}\.\s*CUNG\b", t)]

def _filter_roman_all(h2s):
    return [(i, t) for i, t in h2s if re.match(r"^[IVXLCM]+\.\s", t)]

def _filter_digit(h2s):
    return [(i, t) for i, t in h2s if re.match(r"^\d\.\s", t)]

def _filter_tu_hoa(h2s):
    whitelist = {"II", "III", "IV", "V", "XII", "XIII"}
    out = []
    for i, t in h2s:
        m = re.match(r"^([IVXLCM]+)\.\s", t)
        if m and m.group(1) in whitelist:
            out.append((i, t))
    return out

def _filter_digit_all(h2s):
    return [(i, t) for i, t in h2s if re.match(r"^\d{1,2}\.\s", t)]

def _filter_all(h2s):
    return h2s

def _filter_no_muclucc(h2s):
    return [(i, t) for i, t in h2s if "MỤC LỤC" not in t.upper()]

CHANNELS = [
    {
        "title": "Kênh Cộng Đồng",
        "tone": "blue",
        "links": [
            ("Fanpage Bộ Tộc Tử Vi Chữa Lành", "https://www.facebook.com/tuvichualanh/"),
            ("Group Facebook Cộng Đồng Tử Vi Chữa Lành", "https://www.facebook.com/groups/congdongtuvichualanh"),
            ("Tài liệu TVCL miễn phí (Zalo)", "https://zalo.me/g/aqtxsx783"),
            ("Tử Vi Chữa Lành — Podcast trên Spotify", "https://open.spotify.com/show/360Khz3n8hnTJ89lq31Zd4"),
            ("Tử Vi Chữa Lành — YouTube", "https://www.youtube.com/@tuvichualanh"),
            ("Lấy lá số Tử Vi chuẩn TVCL", "https://www.daotuvi.com/"),
        ],
    },
    {
        "title": "Nhóm Zalo Chuyên Đề (miễn phí)",
        "tone": "green",
        "links": [
            ("Bộ Tộc Tử Vi Chữa Lành", "https://zalo.me/g/mykxsq198"),
            ("Tâm Lý Học Chữa Lành", "https://zalo.me/g/nkjvcd698"),
            ("Tâm Lý Học Trẻ Em", "https://zalo.me/g/ztdpej867"),
            ("Tử Vi Chữa Lành Tài Lộc", "https://zalo.me/g/gzverp694"),
            ("Luận Tử Vi Cho Con", "https://zalo.me/g/gaxmii224"),
            ("Tử Vi Chữa Lành Tình Duyên", "https://zalo.me/g/smxfrt156"),
            ("Tử Vi & Đạo", "https://zalo.me/g/jbspyv017"),
        ],
    },
    {
        "title": "Khóa Học TVCL",
        "tone": "teal",
        "links": [
            ("Luận Nhanh Lá Số Tử Vi", "/khoa-hoc/luan-nhanh-tu-vi/"),
            ("Tử Vi Chữa Lành", "https://tuvichualanh.com/khoa-hoc-tu-vi-chua-lanh/"),
            ("Tâm Lý Học Chữa Lành", "https://forms.gle/1spisoX7VQRmdUN16"),
            ("Tử Vi Luận Vận Hạn", "https://forms.gle/Q8Prn21P3rthntUr6"),
            ("Tử Vi Chữa Lành Tài Lộc", "https://forms.gle/LA967HBgEniFXNqv7"),
            ("Tử Vi Bí Kíp Chữa Lành", "https://forms.gle/SVMkEzbNj8hVAkd79"),
        ],
        "note": {
            "heading": "KHÓA HỌC CHUYÊN SÂU: 1 NĂM MỞ 1 LẦN",
            "items": ["Tử Vi Chữa Lành Nâng Cao", "Tử Vi Chữa Lành Tình Duyên"],
            "contact": "Liên hệ Bộ tộc để đăng ký",
        },
    },
]

# Sub-item anchor id -> dedicated sao-*.html slug (no ".html").
# When a subitem's anchor id has an entry here, sidebar/quicknav link
# straight to that star's own page instead of an in-page anchor.
STAR_PAGE_SLUGS = {
    # 06-14-chinh-tinh
    "i-tu-vi": "sao-tu-vi",
    "ii-thien-co": "sao-thien-co",
    "iii-thai-duong": "sao-thai-duong",
    "iv-vu-khuc": "sao-vu-khuc",
    "v-thien-ong": "sao-thien-dong",
    "vi-liem-trinh": "sao-liem-trinh",
    "vii-thien-phu": "sao-thien-phu",
    "viii-thai-am": "sao-thai-am",
    "ix-tham-lang": "sao-tham-lang",
    "x-cu-mon": "sao-cu-mon",
    "xi-thien-tuong": "sao-thien-tuong",
    "xii-thien-luong": "sao-thien-luong",
    "xiii-that-sat": "sao-that-sat",
    "xiv-pha-quan": "sao-pha-quan",
    # 07-hung-tinh
    "1-kinh-duong-duong-nhan-chien-than-quyen-uy": "sao-kinh-duong",
    "2-a-la-con-quay-cung-ten-nha-nghien-cuu-noi-tam": "sao-da-la",
    "3-hoa-tinh-ngon-lua-bung-chay-ngon-lua-tam-linh": "sao-hoa-tinh",
    "4-linh-tinh-ngon-lua-am-i-nguoi-giu-lua-bo-toc": "sao-linh-tinh",
    "5-ia-khong-ho-en-khoang-trong-nha-hien-triet": "sao-dia-khong",
    "6-ia-kiep-mat-mat-hon-loan-nha-tu-thien": "sao-dia-kiep",
    # 08-cat-tinh
    "1-ta-phu-nguoi-ho-tro-thuc-tien-anh-hung-hao-han-trong-tinh-nghia": "sao-ta-phu",
    "2-huu-bat-nha-muu-luoc-tai-hoa": "sao-huu-bat",
    "3-van-xuong-tri-tue-van-chuong-nha-tri-thuc-quan-van-chu-khoa-cu-chu-chinh-luan": "sao-van-xuong",
    "4-van-khuc-nghe-thuat-va-cam-xuc-tai-nang-nghe-thuat-nguoi-tai-hoa-nang-khieu": "sao-van-khuc",
    "5-thien-khoi-quy-nhan-bac-nhat-quy-nhan-danh-tieng": "sao-thien-khoi",
    "6-thien-viet-quy-nhan-tro-giup-ngam": "sao-thien-viet",
}

SUBITEM_FILTERS = {
    "05-12-cung": _filter_cung,
    "06-14-chinh-tinh": _filter_roman_all,
    "07-hung-tinh": _filter_digit,
    "08-cat-tinh": _filter_digit,
    "09-tu-hoa-loc-ma": _filter_tu_hoa,
    "tt1-tu-vi-dau-so-toan-thu": _filter_digit_all,
    "th1-tinh-hoa-tvcl": _filter_no_muclucc,
    "t1-cbt-nhan-thuc-hanh-vi": _filter_all,
    "t2-act-chap-nhan-cam-ket": _filter_all,
    "t3-ifs-he-thong-gia-dinh-noi-tam": _filter_all,
    "t4-tu-vi-tam-ly-hoc-tong-quan": _filter_all,
    "d1-tu-vi-dao-phat-nhan-qua-nghiep": _filter_all,
    "d2-dao-giao-tu-vi-chua-lanh": _filter_all,
    "d3-thuyet-linh-hon-voi-tu-vi": _filter_all,
    "n1-ban-do-nhan-qua-trong-tu-vi": _filter_all,
    "cc1-y-nghia-14-chinh-tinh-cu-tai-12-cung": _filter_digit_all,
    "cc2-y-nghia-18-trung-tinh-cu-tai-12-cung": _filter_digit_all,
    "tl3-cach-kich-loc-cho-10-chinh-tinh-hoa-loc": _filter_digit_all,
}

# flatten with slug + prev/next
FLAT = []
for cat in CATEGORIES:
    for entry in cat["docs"]:
        path, num, title = entry[0], entry[1], entry[2]
        short = entry[3] if len(entry) > 3 else title
        ascii_title = unidecode(title).lower()
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_title).strip("-")
        slug = f"{num.lower()}-{slug}".strip("-")
        FLAT.append({"path": path, "num": num, "title": title, "short": short, "cat": cat, "slug": slug})

for i, d in enumerate(FLAT):
    d["prev"] = FLAT[i-1] if i > 0 else None
    d["next"] = FLAT[i+1] if i < len(FLAT)-1 else None

MD_EXT = ["extra", "sane_lists", "toc", "tables", "smarty"]

H2_RE = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.S)

def load_source(d):
    src = OVERRIDES.get(d["path"]) or os.path.join(KB, d["path"])
    with open(src, encoding="utf-8") as f:
        raw = f.read()
    fm = {}
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            fm_raw, raw = parts[1], parts[2]
            for line in fm_raw.strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"')
    return raw, fm

def render_all():
    """First pass: convert every doc's markdown, extract meta + sub-item anchors."""
    for d in FLAT:
        raw, fm = load_source(d)
        body_html = md.markdown(raw, extensions=MD_EXT)
        d["body_html"] = body_html
        d["fm"] = fm

        h2s = [(i, re.sub("<[^>]+>", "", t)) for i, t in H2_RE.findall(body_html)]
        h2s = [(i, html.unescape(t).strip()) for i, t in h2s]
        filt = SUBITEM_FILTERS.get(d["slug"])
        d["subitems"] = filt(h2s) if filt else []

def header_html(depth=""):
    return f'''<header class="site-header">
  <div class="site-header-inner">
    <a href="{depth}index.html" class="brand-lockup">
      <span class="logo-mark" role="img" aria-label="Logo Tử Vi Chữa Lành"></span>
      <div class="titles">
        <span class="main-title">Tử Vi Chữa Lành</span>
        <span class="sub-title">Bộ Tộc Tử Vi Chữa Lành</span>
      </div>
    </a>
    <nav class="main-nav">
      <a href="{depth}index.html">Trang chủ</a>
      {"".join(f'<a href="{depth}index.html#{c["id"]}">{html.escape(c["name"])}</a>' for c in CATEGORIES)}
    </nav>
  </div>
</header>'''

def footer_html():
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="foot-slogan">{html.escape(SLOGAN)}</div>
    <div class="foot-tagline">{html.escape(TAGLINE)}</div>
    <div class="foot-meta">© {COMMUNITY} · Knowledge Base v3.1.1</div>
  </div>
</footer>'''

def subitems_ul(d, prefix=""):
    items = "".join(
        f'<li><a href="{prefix}{STAR_PAGE_SLUGS[i]}.html">{html.escape(t)}</a></li>'
        if i in STAR_PAGE_SLUGS else
        f'<li><a href="{prefix}{d["slug"]}.html#{i}">{html.escape(t)}</a></li>'
        for i, t in d["subitems"]
    )
    return f'<ul class="subitem-list">{items}</ul>'

def doc_nav_entry(d, active_slug, prefix=""):
    """Render one doc entry for sidebar/homepage: plain link, or <details> accordion if it has subitems."""
    cat = d["cat"]
    accent = cat.get("accent", "blue")
    show_badge = cat.get("show_badge", True)
    badge = f'<span class="doc-badge accent-{accent} blank"></span>' if show_badge else ""
    row_cls = "doc-row" if show_badge else "doc-row no-badge"
    cls = "active" if d["slug"] == active_slug else ""
    link = f'<a class="{cls}" href="{prefix}{d["slug"]}.html">{html.escape(d.get("short", d["title"]))}</a>'

    if d["subitems"]:
        open_attr = " open" if d["slug"] == active_slug else ""
        arrow = '<span class="arrow-mark">▸</span>' if show_badge else ""
        return (f'<li><details{open_attr}>'
                f'<summary class="{row_cls}">{arrow}{badge}{link}</summary>'
                f'{subitems_ul(d, prefix)}'
                f'</details></li>')
    arrow_spacer = '<span class="arrow-spacer"></span>' if show_badge else ""
    return f'<li><div class="{row_cls}">{arrow_spacer}{badge}{link}</div></li>'

def sidebar_html(active_slug):
    blocks = []
    for cat in CATEGORIES:
        items = []
        for entry in cat["docs"]:
            d = next(x for x in FLAT if x["path"] == entry[0])
            items.append(doc_nav_entry(d, active_slug, prefix=""))
        blocks.append(f'<h4>{html.escape(cat["name"])}</h4><ul>{"".join(items)}</ul>')
    return f'<div class="sidebar">{"".join(blocks)}</div>'

def doc_page(d):
    fm = d["fm"]
    meta_bits = []
    if fm.get("version"): meta_bits.append(f"Phiên bản {fm['version']}")
    if fm.get("updated"): meta_bits.append(f"Cập nhật {fm['updated']}")
    if fm.get("status"): meta_bits.append(fm["status"])
    meta_line = " · ".join(meta_bits)

    nav_bits = []
    if d["prev"]:
        nav_bits.append(f'<a href="{d["prev"]["slug"]}.html">← {html.escape(d["prev"]["title"])}</a>')
    else:
        nav_bits.append("<span></span>")
    if d["next"]:
        nav_bits.append(f'<a href="{d["next"]["slug"]}.html">{html.escape(d["next"]["title"])} →</a>')
    else:
        nav_bits.append("<span></span>")

    quicknav = ""
    if d["subitems"]:
        chips = "".join(
            f'<a href="{STAR_PAGE_SLUGS[i]}.html">{html.escape(t)}</a>'
            if i in STAR_PAGE_SLUGS else
            f'<a href="#{i}">{html.escape(t)}</a>'
            for i, t in d["subitems"]
        )
        quicknav = f'<div class="quicknav"><span>Đi nhanh tới:</span>{chips}</div>'

    protected = d["cat"]["id"] in PROTECTED_CATEGORY_IDS
    _meta_override = DOC_META_OVERRIDES.get(d["slug"], {})
    meta_title = _meta_override.get("title", d["title"])
    meta_desc = _meta_override.get("desc", d["cat"]["desc"])
    protect_script = ""
    if protected:
        payload = encrypt_for_gate(d["body_html"], SITE_PASSWORD)
        body_block = f'''<div class="lock-gate" id="lock-gate">
      <div class="lock-card">
        <div class="lock-icon">🔒</div>
        <h3>Nội dung dành riêng cho học viên lớp Tử Vi Chữa Lành</h3>
        <p>Phần này cần mật khẩu để đọc. Hãy nhắn tin fanpage Bộ tộc để được nhận mật khẩu hay đăng ký tham gia Hành trình Tử Vi Chữa Lành. Nếu bạn đã được cấp quyền, hãy bảo mật, sử dụng chỉ cho riêng bạn.</p>
        <form id="lock-form">
          <input type="password" id="lock-password" placeholder="Nhập mật khẩu" autocomplete="off">
          <button type="submit">Mở khóa</button>
        </form>
        <p class="lock-error" id="lock-error" style="display:none">Mật khẩu chưa đúng, thử lại nhé.</p>
      </div>
    </div>
    <script type="application/json" id="protected-payload">{json.dumps(payload)}</script>
    <div id="protected-content" style="display:none"></div>'''
        protect_script = '<script src="../assets/js/protect.js" defer></script>'
    else:
        body_block = d["body_html"]

    page = f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(meta_title)} — {SITE_TITLE}</title>
<meta name="description" content="{html.escape(meta_desc)}">
<link rel="canonical" href="{SITE_URL}/docs/{d["slug"]}.html">
<link rel="icon" href="{FAVICON}">
{GA_SNIPPET}
{'<meta name="robots" content="noindex, nofollow">' if protected else ''}
<meta property="og:type" content="article">
<meta property="og:site_name" content="{html.escape(SITE_TITLE)} — {html.escape(COMMUNITY)}">
<meta property="og:title" content="{html.escape(meta_title)} — {SITE_TITLE}">
<meta property="og:description" content="{html.escape(meta_desc)}">
<meta property="og:url" content="{SITE_URL}/docs/{d["slug"]}.html">
<meta property="og:image" content="{OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(meta_title)} — {SITE_TITLE}">
<meta name="twitter:description" content="{html.escape(meta_desc)}">
<meta name="twitter:image" content="{OG_IMAGE}">
<script type="application/ld+json">{json.dumps({
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": meta_title,
    "description": meta_desc,
    "url": f"{SITE_URL}/docs/{d['slug']}.html",
    "inLanguage": "vi",
    "isAccessibleForFree": not protected,
    "isPartOf": {"@type": "WebSite", "name": SITE_TITLE, "url": SITE_URL},
    "publisher": {"@type": "Organization", "name": COMMUNITY, "url": SITE_URL},
    "image": OG_IMAGE,
}, ensure_ascii=False)}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,500;1,600;1,700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/css/style.css">
{protect_script}
</head>
<body>
{header_html(depth="../")}
<div class="doc-layout">
  {sidebar_html(d["slug"])}
  <main class="doc-content">
    <div class="doc-kicker">{html.escape(d["cat"]["name"])} · Tài liệu {d["num"]}</div>
    {"" if not meta_line else f'<div class="meta-box">{html.escape(meta_line)}</div>'}
    {quicknav}
    {body_block}
    <div class="doc-nav-links">{nav_bits[0]}{nav_bits[1]}</div>
  </main>
</div>
{footer_html()}
</body>
</html>'''
    return page

def channels_html():
    cards = []
    for grp in CHANNELS:
        items = "".join(
            f'<li><a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(label)}</a></li>'
            for label, url in grp["links"]
        )
        note = ""
        if grp.get("note"):
            n = grp["note"]
            note_items = "".join(f"<div>{html.escape(x)}</div>" for x in n["items"])
            note = (f'<div class="channel-note">'
                    f'<strong class="channel-note-heading">{html.escape(n["heading"])}</strong>'
                    f'<div class="channel-note-items">{note_items}</div>'
                    f'<div class="channel-note-contact">{html.escape(n["contact"])}</div>'
                    f'</div>')
        tone = grp.get("tone", "blue")
        cards.append(f'''<div class="cat-card channel-card tone-{tone}">
      <h3>{html.escape(grp["title"])}</h3>
      <ul class="channel-list">{items}</ul>
      {note}
    </div>''')
    return f'''<section class="section channel-section band-dark" id="cong-dong">
  <div class="container">
    <div class="section-kicker-wrap"><span class="kicker-label">Bộ Tộc Tử Vi Chữa Lành</span></div>
    <h2 class="section-title">Kết Nối Với Bộ Tộc TVCL</h2>
    <p class="section-sub">Kênh thông tin và khóa học chính thức — cùng đồng hành trên hành trình Hiểu Mình, Cải Mệnh &amp; Chữa Lành</p>
    <div class="cat-grid">
      {"".join(cards)}
    </div>
    <div class="btn-row" style="margin-top:36px">
      <a href="https://zalo.me/g/mykxsq198" target="_blank" rel="noopener" class="btn btn-gold">Gia Nhập Cộng Đồng →</a>
    </div>
  </div>
</section>'''

def homepage_links_new_tab(page):
    """Open information pages separately; keep in-page navigation in place."""
    from urllib.parse import urljoin, urlsplit

    def update(match):
        tag = match.group(0)
        href = re.search(r'\bhref=["\']([^"\']*)["\']', tag)
        if not href or re.search(r'\bdownload(?:\s|=|>)', tag):
            return tag
        url = urlsplit(urljoin(SITE_URL + "/", html.unescape(href.group(1))))
        if url.scheme not in ("http", "https"):
            return tag
        if url.netloc == urlsplit(SITE_URL).netloc and url.path in ("/", "/index.html") and not url.query:
            return tag
        tag = re.sub(r'\s+target=["\'][^"\']*["\']', '', tag)
        rel = re.search(r'\s+rel=["\']([^"\']*)["\']', tag)
        values = set(rel.group(1).split()) if rel else set()
        values.add("noopener")
        tag = re.sub(r'\s+rel=["\'][^"\']*["\']', '', tag)
        return tag[:-1] + ' target="_blank" rel="' + ' '.join(sorted(values)) + '">'

    return re.sub(r'<a\b[^>]*>', update, page)

def index_page():
    cat_blocks = []
    for cat in CATEGORIES:
        items = "".join(
            doc_nav_entry(next(x for x in FLAT if x["path"] == entry[0]), active_slug=None, prefix="docs/")
            for entry in cat["docs"]
        )
        lock_badge = ' <span class="lock-tag" title="Cần mật khẩu để đọc">🔒 Cần mật khẩu</span>' if cat["id"] in PROTECTED_CATEGORY_IDS else ""
        accent = cat.get("accent", "blue")
        cat_blocks.append(f'''<div class="cat-card cat-accent-{accent}" id="{cat["id"]}">
      <h3>{html.escape(cat["name"])}{lock_badge}</h3>
      <p>{html.escape(cat["desc"])}</p>
      <ul class="doc-list">{items}</ul>
    </div>''')

    page = f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{HOME_OG_TITLE}</title>
<meta name="description" content="{html.escape(SITE_DESC)}">
<link rel="canonical" href="{SITE_URL}/">
<link rel="icon" href="{FAVICON}">
{GA_SNIPPET}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{html.escape(SITE_TITLE)} — {html.escape(COMMUNITY)}">
<meta property="og:title" content="{HOME_OG_TITLE}">
<meta property="og:description" content="{html.escape(HOME_OG_DESC)}">
<meta property="og:url" content="{SITE_URL}/">
<meta property="og:image" content="{OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{HOME_OG_TITLE}">
<meta name="twitter:description" content="{html.escape(HOME_OG_DESC)}">
<meta name="twitter:image" content="{OG_IMAGE}">
<script type="application/ld+json">{json.dumps({
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": "Organization",
            "@id": f"{SITE_URL}/#organization",
            "name": COMMUNITY,
            "url": SITE_URL,
            "logo": f"{SITE_URL}/assets/img/logo.png",
            "sameAs": [u for grp in CHANNELS for _, u in grp["links"]][:6],
        },
        {
            "@type": "WebSite",
            "@id": f"{SITE_URL}/#website",
            "name": SITE_TITLE,
            "alternateName": COMMUNITY,
            "url": SITE_URL,
            "description": SITE_DESC,
            "inLanguage": "vi",
            "publisher": {"@id": f"{SITE_URL}/#organization"},
        },
    ],
}, ensure_ascii=False)}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,500;1,600;1,700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css?v=course-slider-20260907">
</head>
<body>
{header_html(depth="")}
<section class="hero">
  <div class="hero-art"><div class="hero-seal logo-mark" role="img" aria-label="Tử Vi Chữa Lành"></div></div>
  <div class="hero-inner">
    <div class="hero-content">
      <p class="hero-pillars">Hiểu Mình – Cải Mệnh – Chữa Lành</p>
      <h1><span>Tử Vi</span> Chữa Lành</h1>
      <p class="slogan">{html.escape(HERO_SUBTITLE)}</p>
      <p class="tagline-big">Lá số là bản đồ chữa lành</p>
      <div class="btn-row hero-btn-row">
        <a href="#kham-pha" class="btn btn-forest">✦ Khám Phá Tàng Kinh Các</a>
        <a href="#cong-dong" class="btn btn-outline">Kết Nối Với Bộ Tộc →</a>
      </div>
      <p class="five-khong">Không định mệnh luận<span class="dot">·</span>Không gieo sợ hãi<span class="dot">·</span>Tôn trọng sự thật<span class="dot">·</span>Hướng đến chuyển hóa</p>
    </div>
  </div>
</section>
<section class="section learning-section" id="khoa-hoc-su-kien" aria-labelledby="learning-title">
  <div class="container">
    <div class="section-kicker-wrap"><span class="kicker-label">Học tập &amp; kết nối cùng Bộ Tộc</span></div>
    <h2 class="section-title" id="learning-title">Khóa học &amp; Sự kiện sắp diễn ra</h2>
    <p class="section-sub">Chọn một hành trình phù hợp để hiểu mình sâu hơn và cùng nhau thực hành.</p>
    <div class="learning-filters" role="group" aria-label="Lọc khóa học và sự kiện" hidden>
      <button type="button" data-learning-filter="all" aria-pressed="true">Tất cả</button>
      <button type="button" data-learning-filter="course" aria-pressed="false">Khóa học</button>
      <button type="button" data-learning-filter="event" aria-pressed="false">Sự kiện</button>
    </div>
    <div class="learning-slider-controls" aria-label="Điều khiển danh sách khóa học">
      <button type="button" data-slide-direction="-1" aria-label="Xem khóa học phía trước">←</button>
      <button type="button" data-slide-direction="1" aria-label="Xem khóa học tiếp theo">→</button>
    </div>
    <div class="learning-grid" tabindex="0" role="region" aria-label="Khóa học theo lịch khai giảng, cuộn ngang để xem thêm">
      <article class="learning-card" data-learning-kind="event">
        <a class="learning-art learning-art-healing" href="cung-phuc-duc/" aria-label="Xem khóa học Giải Mã Cung Phúc Đức" target="_blank" rel="noopener"><img src="cung-phuc-duc/assets/celestial-hero.png" alt="Bản đồ sao và hoa sen của khóa Giải Mã Cung Phúc Đức" loading="lazy" decoding="async"></a>
        <div class="learning-card-body"><p class="learning-category">Sự kiện · Không cần nền tảng Tử Vi</p>
          <h3><a href="cung-phuc-duc/" target="_blank" rel="noopener">Giải Mã Cung Phúc Đức</a></h3><p>Khám phá nền phúc, mối liên hệ với gia đình, dòng họ và đời sống tinh thần; học cách quán chiếu để vun bồi nội lực, tìm sự an trú từ bên trong.</p>
          <div class="learning-date"><span class="learning-date-label">Khai giảng</span><strong>12/09</strong><span class="learning-date-detail">Lịch học: 12 – 14 – 15/09<br>19:30 – 22:30 · Học qua Zoom</span></div>
          <a class="learning-link" href="cung-phuc-duc/" target="_blank" rel="noopener">Xem khóa học <span aria-hidden="true">↗</span><span class="learning-sr"> Giải Mã Cung Phúc Đức</span></a>
        </div>
      </article>
      <article class="learning-card" data-learning-kind="course">
        <a class="learning-art learning-art-s36" href="khoa-hoc/luan-nhanh-tu-vi/" aria-label="Xem khóa học Luận Nhanh Lá Số Tử Vi S36" target="_blank" rel="noopener"><img src="assets/img/luan-nhanh-lop-zoom.png" alt="Buổi học Zoom cùng cộng đồng Luận Nhanh Lá Số Tử Vi" loading="lazy" decoding="async"></a>
        <div class="learning-card-body"><p class="learning-category">Lớp S36 · Dành cho người mới</p>
          <h3><a href="khoa-hoc/luan-nhanh-tu-vi/" target="_blank" rel="noopener">Luận Nhanh Lá Số Tử Vi S36</a></h3><p>Từng bước lập, đọc và hiểu lá số của chính mình. Thực hành cùng lớp trong 5 buổi, 15 tiếng Zoom và học lại miễn phí.</p>
          <div class="learning-date"><span class="learning-date-label">Khai giảng</span><strong><time datetime="2026-09-17">17/09</time></strong><span class="learning-date-detail">17, 18, 21, 22, 24/09 · 19h30–22h30<br>5 buổi · 15 tiếng Zoom · Học lại miễn phí</span></div>
          <a class="learning-link" href="khoa-hoc/luan-nhanh-tu-vi/" target="_blank" rel="noopener">Xem khóa học <span aria-hidden="true">↗</span><span class="learning-sr"> Luận Nhanh Lá Số Tử Vi S36</span></a>
        </div>
      </article>
      <article class="learning-card" data-learning-kind="course">
        <a class="learning-art learning-art-foundation" href="luan-van-han/" aria-label="Xem khóa học Tử Vi Luận Vận Hạn" target="_blank" rel="noopener"><img src="luan-van-han/assets/cong-dong.jpg" alt="Cộng đồng Tử Vi Chữa Lành trong buổi gặp gỡ học viên" loading="lazy" decoding="async"></a>
        <div class="learning-card-body"><p class="learning-category">Khóa học · Dành cho người đã biết Tử Vi</p>
          <h3><a href="luan-van-han/" target="_blank" rel="noopener">Tử Vi Luận Vận Hạn</a></h3><p>Kết nối Nguyên Cục, Đại Vận và Tiểu Vận; nghiệm lý trên lá số của chính mình để hiểu nhịp chuyển cuộc đời và chủ động trước mỗi bước ngoặt.</p>
          <div class="learning-date"><span class="learning-date-label">Khai giảng</span><strong>28/09</strong><span class="learning-date-detail">Tử Vi Luận Vận Hạn</span></div>
          <a class="learning-link" href="luan-van-han/" target="_blank" rel="noopener">Xem khóa học <span aria-hidden="true">↗</span><span class="learning-sr"> Tử Vi Luận Vận Hạn</span></a>
        </div>
      </article>
      <article class="learning-card" data-learning-kind="course">
        <a class="learning-art learning-art-timing" href="khoa-hoc-tu-vi-bi-kip-chua-lanh/" aria-label="Xem khóa học Tử Vi Bí Kíp Chữa Lành" target="_blank" rel="noopener"><img src="khoa-hoc-tu-vi-bi-kip-chua-lanh/assets/og.png" alt="Tử Vi Bí Kíp Ứng Dụng Chữa Lành — Lá số là bản đồ, không phải bản án" loading="lazy" decoding="async"></a>
        <div class="learning-card-body"><p class="learning-category">Khóa học · Tử Vi, Tâm lý &amp; Đạo học</p>
          <h3><a href="khoa-hoc-tu-vi-bi-kip-chua-lanh/" target="_blank" rel="noopener">Tử Vi Bí Kíp Chữa Lành</a></h3><p>Dùng lá số như một bản đồ tâm thức để nhận diện niềm tin lõi, những mô thức đang lặp lại và tìm hướng chuyển hóa qua Tử Vi, Tâm lý và Đạo học.</p>
          <div class="learning-date"><span class="learning-date-label">Khai giảng</span><strong><time datetime="2026-10-08">08/10/2026</time></strong><span class="learning-date-detail">5 tối Thứ Năm · Học qua Zoom</span></div>
          <a class="learning-link" href="khoa-hoc-tu-vi-bi-kip-chua-lanh/" target="_blank" rel="noopener">Xem khóa học <span aria-hidden="true">↗</span><span class="learning-sr"> Tử Vi Bí Kíp Chữa Lành</span></a>
        </div>
      </article>
    </div>
    <p class="learning-sr" id="learning-result" aria-live="polite" aria-atomic="true"></p>
  </div>
</section>
<script>
(() => {{
  const section = document.getElementById('khoa-hoc-su-kien');
  const filters = section.querySelector('.learning-filters');
  filters.hidden = false;
  const slider = section.querySelector('.learning-grid');
  section.querySelectorAll('[data-slide-direction]').forEach(button => {{
    button.addEventListener('click', () => {{
      const card = slider.querySelector('.learning-card:not([hidden])');
      if (!card) return;
      const distance = card.getBoundingClientRect().width + parseFloat(getComputedStyle(slider).columnGap);
      slider.scrollBy({{ left: Number(button.dataset.slideDirection) * distance, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' }});
    }});
  }});

  filters.addEventListener('click', (event) => {{
    const button = event.target.closest('button');
    if (!button) return;
    const kind = button.dataset.learningFilter;
    filters.querySelectorAll('button').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    section.querySelectorAll('[data-learning-kind]').forEach(item => {{ item.hidden = kind !== 'all' && !item.dataset.learningKind.split(' ').includes(kind); }});
    section.querySelector('.learning-grid').hidden = false;
    slider.scrollLeft = 0;
    section.querySelector('#learning-result').textContent = kind === 'event' ? 'Hiển thị sự kiện Giải Mã Cung Phúc Đức.' : kind === 'course' ? 'Hiển thị 3 khóa học.' : 'Hiển thị 1 sự kiện và 3 khóa học theo lịch khai giảng.';
  }});
}})();
</script>
<section class="section intro-section">
  <div class="container intro-container">
    <p>Chào mừng bạn đến với một trong những hành trình quan trọng nhất của đời người: <strong>Hiểu Mình — Cải Mệnh — Chữa Lành</strong>, để sống sâu sắc hơn, có ý nghĩa hơn và bình an hơn.</p>
    <p><strong>Bộ Tộc Tử Vi Chữa Lành (TVCL)</strong> là cộng đồng học tập, thực hành và chuyển hóa bản thân thông qua sự kết hợp giữa Tử Vi Đẩu Số, Tâm lý học hiện đại, Phật học và Đạo học phương Đông.</p>
    <p>TVCL tiếp cận lá số như một <strong>bản đồ chữa lành</strong> — một hệ ngôn ngữ biểu tượng và bản đồ khuynh hướng giúp mỗi người quán chiếu khí chất, năng lực, nguồn lực, điểm mù, mô thức tâm lý, những vùng dễ tổn thương và các bài học phát triển trong cuộc đời.</p>
    <p>Lá số không phải bản án định mệnh. Đó là một tấm bản đồ để ta hiểu mình rõ hơn, sống tỉnh thức hơn và chủ động chuyển hóa bằng nhận thức, tu tập cùng những lựa chọn có trách nhiệm.</p>
  </div>
</section>
<section class="section band-dark philosophy-section">
  <div class="container">
    <div class="section-kicker-wrap"><span class="kicker-label">Triết Lý Tử Vi Chữa Lành</span></div>
    <p class="philosophy-quote">“{html.escape(TAGLINE)}.”</p>
    <p class="philosophy-sub">{html.escape(PHILOSOPHY_SUB)}</p>
  </div>
</section>
<section class="section" id="kham-pha">
  <div class="container">
    <div class="section-kicker-wrap"><span class="kicker-label">Thư Viện Tri Thức TVCL</span></div>
    <h2 class="section-title">Khám phá Tàng Kinh Các TVCL</h2>
    <p class="section-sub">Toàn bộ hệ tri thức nền tảng của Bộ Tộc — từ triết lý gốc đến chi tiết từng lá số</p>
    <div class="cat-grid">
      {"".join(cat_blocks)}
    </div>
  </div>
</section>
{channels_html()}
{footer_html()}
</body>
</html>'''
    return homepage_links_new_tab(page)

def sitemap_xml():
    # Không đưa các trang cần mật khẩu (nội dung mã hoá, crawler không đọc
    # được) vào sitemap — tránh lãng phí crawl budget / tín hiệu thin content.
    urls = [(f"{SITE_URL}/", "1.0")]
    urls += [(f"{SITE_URL}/docs/{d['slug']}.html", "0.8") for d in FLAT if d["cat"]["id"] not in PROTECTED_CATEGORY_IDS]
    items = "\n".join(
        f"  <url>\n    <loc>{html.escape(u)}</loc>\n    <priority>{p}</priority>\n  </url>"
        for u, p in urls
    )
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>
'''

def robots_txt():
    return f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""

def not_found_page():
    return f'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Không tìm thấy trang — {SITE_TITLE}</title>
<meta name="robots" content="noindex, follow">
<link rel="icon" href="{FAVICON}">
{GA_SNIPPET}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,500;1,600;1,700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600;8..60,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css?v=course-slider-20260907">
</head>
<body>
{header_html(depth="")}
<section class="section intro-section">
  <div class="container intro-container" style="text-align:center;padding:64px 24px;">
    <h1 style="font-family:'Cormorant Garamond','Noto Serif',Georgia,serif;font-size:44px;margin:0 0 16px;">Không tìm thấy trang này</h1>
    <p style="margin:0 0 28px;opacity:.8;">Trang bạn tìm có thể đã đổi tên hoặc chưa từng tồn tại. Lá số là bản đồ — và đây là lối quay lại bản đồ chính.</p>
    <div class="btn-row" style="justify-content:center;">
      <a href="/" class="btn btn-forest">Về Trang Chủ Tử Vi Chữa Lành</a>
    </div>
  </div>
</section>
{footer_html()}
</body>
</html>'''

def main():
    os.makedirs(DOCS_OUT, exist_ok=True)
    render_all()
    for d in FLAT:
        out = doc_page(d)
        with open(os.path.join(DOCS_OUT, f'{d["slug"]}.html'), "w", encoding="utf-8") as f:
            f.write(out)
        print("wrote", d["slug"], "subitems:", len(d["subitems"]))
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_page())
    print("wrote index.html")
    with open(os.path.join(ROOT, "CNAME"), "w", encoding="utf-8") as f:
        f.write("tuvichualanh.com\n")
    print("wrote CNAME")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_xml())
    print("wrote sitemap.xml")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_txt())
    print("wrote robots.txt")
    with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8") as f:
        f.write(not_found_page())
    print("wrote 404.html")

if __name__ == "__main__":
    main()
