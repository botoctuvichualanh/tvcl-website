#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Trích tri thức Mặt sáng / Mặt tối / Chuyển hóa từ bộ Core MD TVCL v3.2.0
thành _bai-viet-source/kb_digest.json cho trang bài viết.
Chạy: python kb_extract.py <thu_muc_core_files_TVCL>"""
import json, re, sys
from pathlib import Path

KB = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent / "_bai-viet-source" / "kb_digest.json"
STAR_FILES = ["06_TVCL_14_CHINH_TINH.md", "07_TVCL_HUNG_TINH.md", "08_TVCL_CAT_TINH.md", "09_TVCL_TU_HOA_LOC_MA.md"]
STARS = {
    "TuVi": ["Tử Vi"], "ThienCo": ["Thiên Cơ"], "ThaiDuong": ["Thái Dương"], "VuKhuc": ["Vũ Khúc"],
    "ThienDong": ["Thiên Đồng"], "LiemTrinh": ["Liêm Trinh"], "ThienPhu": ["Thiên Phủ"], "ThaiAm": ["Thái Âm"],
    "ThamLang": ["Tham Lang"], "CuMon": ["Cự Môn"], "ThienTuong": ["Thiên Tướng"], "ThienLuong": ["Thiên Lương"],
    "ThatSat": ["Thất Sát"], "PhaQuan": ["Phá Quân"], "KinhDa": ["Kình Dương", "Đà La"],
    "KhongKiep": ["Địa Không", "Địa Kiếp"], "HoaTinh": ["Hỏa Tinh", "Linh Tinh"],
    "XuongKhuc": ["Văn Xương", "Văn Khúc"], "TaHuu": ["Tả Phù", "Hữu Bật"], "KhoiViet": ["Thiên Khôi", "Thiên Việt"],
    "HoaLoc": ["Hóa Lộc", "Lộc Tồn"], "HoaQuyen": ["Hóa Quyền"], "HoaKhoa": ["Hóa Khoa"], "HoaKy": ["Hóa Kỵ"],
    "ThienMa": ["Thiên Mã"],
}
PALACES = {
    "CungMenhThan": "MỆNH", "CungPhuMau": "PHỤ MẪU", "PhucDuc": "PHÚC ĐỨC", "CungDienTrach": "ĐIỀN TRẠCH",
    "CungQuanLoc": "QUAN LỘC", "CungNoBoc": "NÔ BỘC", "CungThienDi": "THIÊN DI", "CungTatAch": "TẬT ÁCH",
    "CungTaiBach": "TÀI BẠCH", "CungTuTuc": "TỬ TỨC", "PhuThe": "PHU THÊ", "CungHuynhDe": "HUYNH ĐỆ",
}

def clean(s):
    s = re.sub(r"\*\*|__|`", "", s).strip()
    s = re.sub(r"^[-*•+]\s+", "", s)
    return s.strip(" .;").strip()

def bullets(lines, limit=3):
    out = []
    for ln in lines:
        t = ln.strip()
        if re.match(r"^[-*•+]\s+", t):
            c = clean(t)
            if c:
                out.append(c[0].upper() + c[1:])
        if len(out) >= limit:
            break
    return out

FEAR = re.compile(r"tai nạn|mổ xẻ|hình thương|pháp luật|tai họa|tai hoạ|tổn thất|chết|yểu|bần tiện|tù tội|lao lý|phá sản|ly hôn|ly dị|điềm hung|mắc nợ|thù chuốc oán|bệnh tật|hao tổn|ngục tù|tàn ác|bạo tàn|lừa đảo|xâm hại|tai ách|máu|cướp đoạt|họa|hình khắc|tổn hại nặng", re.I)

def gentle(items, keep=3):
    out = []
    for s in items:
        if FEAR.search(s):
            continue
        s = re.sub(r"^(Hung|Cát)\s+chủ\s+về\s+", "", s)
        s = re.sub(r"[,;]\s*trầm cảm$", "", re.sub(r"trầm cảm,\s*", "", s))
        s = s[0].upper() + s[1:] if s else s
        out.append(s)
    return out[:keep]

def block_after(lines, label_re):
    """Dòng sau nhãn **...:** cho tới nhãn đậm kế tiếp hoặc heading."""
    for i, ln in enumerate(lines):
        if re.match(label_re, ln.strip()):
            body = []
            for x in lines[i + 1:]:
                if re.match(r"^\s*(\*\*[^*]+:\*\*|#)", x):
                    break
                body.append(x)
            return body
    return []

def inline_after(lines, label_re):
    for ln in lines:
        m = re.match(label_re + r"\s*(.+)$", ln.strip())
        if m:
            return clean(m.group(1))
    return ""

def star_record(name, texts):
    for txt in texts:
        lines = txt.splitlines()
        start = next((i for i, l in enumerate(lines) if re.match(rf"^###\s+{re.escape(name)}\s+–\s+Bản ghi tóm tắt", l)), None)
        if start is None:
            continue
        sec = []
        for l in lines[start + 1:]:
            if l.startswith("#"):
                break
            sec.append(l)
        rec = {
            "name": name,
            "image": inline_after(sec, r"\*\*Hình tượng[^*]*:\*\*"),
            "light": gentle(bullets(block_after(sec, r"^\*\*Điểm mạnh"), 6)),
            "shadow": gentle(bullets(block_after(sec, r"^\*\*Điểm yếu"), 8)),
            "heal": gentle(bullets(block_after(sec, r"^\*\*Chữa lành"), 4), 2),
            "keywords": inline_after(sec, r"\*\*Từ khóa:\*\*"),
        }
        if rec["light"] or rec["shadow"]:
            return rec
    return None

def palace_record(upper, txt):
    lines = txt.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(rf"^##\s+\d+\.\s+CUNG\s+{re.escape(upper)}\b", l)), None)
    if start is None:
        return None
    sec = []
    for l in lines[start + 1:]:
        if re.match(r"^##\s", l):
            break
        sec.append(l)
    def sub(title_re, limit):
        i = next((k for k, l in enumerate(sec) if re.match(rf"^###\s+{title_re}", l)), None)
        if i is None:
            return []
        body = []
        for l in sec[i + 1:]:
            if l.startswith("###"):
                break
            body.append(l)
        return body
    definition = ""
    for l in sub("Định nghĩa TVCL", 0):
        t = l.strip()
        if t and not t.startswith(("|", "#", ">")) and not re.match(r"^[-*•]", t):
            definition = clean(t)
            break
    rec = {
        "name": "Cung " + upper.title(),
        "definition": definition,
        "good": bullets(sub(r"Khi .*tốt", 0), 2),
        "bad": bullets(sub(r"Khi .*xấu", 0), 2),
        "remedy": bullets(sub("Cách cải mệnh", 0), 4),
    }
    return rec if (rec["definition"] or rec["remedy"]) else None

def main():
    texts = [(KB / f).read_text(encoding="utf-8") for f in STAR_FILES]
    palace_txt = (KB / "05_TVCL_12_CUNG.md").read_text(encoding="utf-8")
    digest, missing = {}, []
    for key, names in STARS.items():
        recs = [r for r in (star_record(n, texts) for n in names) if r]
        if recs:
            digest[key] = {"kind": "star", "items": recs}
        else:
            missing.append(key)
    for key, upper in PALACES.items():
        rec = palace_record(upper, palace_txt)
        if rec:
            digest[key] = {"kind": "palace", "items": [rec]}
        else:
            missing.append(key)
    digest["_source"] = "Knowledge Base TVCL v3.2.0 — core_files_TVCL 05–09"
    OUT.write_text(json.dumps(digest, ensure_ascii=False, indent=1), encoding="utf-8")
    print("OK", len(digest) - 1, "mục; thiếu:", missing)

if __name__ == "__main__":
    main()
