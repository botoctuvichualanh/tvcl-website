# -*- coding: utf-8 -*-
"""SEO meta chuẩn cho toàn site (Phương án A, 01/11/2026).
Nguồn duy nhất cho title/description: build.py đọc DOCS_META + HOME_DESC;
seo_patch.py dùng chung để vá các trang HTML không có generator (sao-*, khóa học...).
Chuẩn: description 120–160 ký tự, title ≤65 ký tự (kể cả hậu tố), 1 H1/trang."""

SUFFIX = " — Tử Vi Chữa Lành"
HOME_DESC = "Tử Vi Chữa Lành kết hợp Tử Vi, Tâm lý học và Đạo học để bạn hiểu mình, nhận diện khuynh hướng và chuyển hóa cuộc sống. Lá số là bản đồ, không phải bản án."

# Trang /docs/ sinh bởi build.py — title KHÔNG gồm hậu tố (template tự thêm).
DOCS_META = {
  "01-hien-phap-tvcl": {"desc": "Hiến Pháp Tử Vi Chữa Lành: nguyên tắc 5 Không – 5 Luôn, tinh thần luận giải từ bi và cam kết đạo đức của người đồng hành trên hành trình Hiểu Mình."},
  "02-tu-dien-thuat-ngu": {"desc": "Từ điển thuật ngữ Tử Vi Chữa Lành: giải nghĩa dễ hiểu cung, sao, Tứ Hóa, tam phương tứ chính và ngôn ngữ chữa lành dành cho người mới học Tử Vi."},
  "03-triet-ly-nen-tang": {"desc": "Triết lý nền tảng của Tử Vi Chữa Lành: lá số là bản đồ, không phải bản án. Kết hợp Tử Vi, Tâm lý học và Đạo học để Hiểu Mình, Cải Mệnh & Chữa Lành."},
  "04-khung-luan-giai-la-so": {"desc": "Khung luận giải lá số Tử Vi theo TVCL: đọc hệ sinh thái tam phương tứ chính, nhìn cả Mặt Sáng – Mặt Tối của sao và biến lá số thành lộ trình chuyển hóa."},
  "05-12-cung": {"title": "12 Cung Trong Tử Vi: Ý Nghĩa Từng Cung",
                 "desc": "Giải mã 12 Cung trên lá số Tử Vi: Mệnh, Phúc Đức, Quan Lộc, Tài Bạch, Phu Thê… Mỗi cung là một vùng đời sống giúp bạn Hiểu Mình theo Tử Vi Chữa Lành."},
  "06-14-chinh-tinh": {"title": "14 Chính Tinh Là Sao Gì? Ý Nghĩa Từng Sao",
                 "desc": "14 Chính Tinh là 14 nguyên mẫu năng lượng cốt lõi: Tử Vi, Thiên Cơ, Thái Dương, Vũ Khúc, Thất Sát… Luận đủ Mặt Sáng, Mặt Tối theo Tử Vi Chữa Lành."},
  "07-hung-tinh": {"title": "Hung Tinh Là Sao Gì? Lục Sát Tinh Trong Tử Vi",
                 "desc": "Hung tinh là vùng bài học cần chữa lành, không phải lời nguyền. Hiểu Kình Dương, Đà La, Hỏa Tinh, Linh Tinh, Địa Không, Địa Kiếp và hướng chuyển hóa."},
  "08-cat-tinh": {"title": "Cát Tinh Là Sao Gì? Lục Cát Tinh Trong Tử Vi",
                 "desc": "Cát tinh là phước báu cần dụng. Ý nghĩa Tả Phù, Hữu Bật, Văn Xương, Văn Khúc, Thiên Khôi, Thiên Việt và cách khai thác năng lượng sao theo Tử Vi Chữa Lành."},
  "09-tu-hoa-loc-ma": {"title": "Tứ Hóa & Lộc Mã: Hóa Lộc, Quyền, Khoa, Kỵ",
                 "desc": "Tứ Hóa Lộc – Quyền – Khoa – Kỵ và Lộc Mã trong Tử Vi: dòng chảy năng lượng của lá số, cách nhận diện cơ hội, bài học và hướng dụng theo Tử Vi Chữa Lành."},
  "10-gioi-thieu-tvcl": {"desc": "Tử Vi Chữa Lành là gì? Tầm nhìn, sứ mệnh và con đường kết hợp Tử Vi, Tâm lý học, Đạo học của Bộ Tộc TVCL để mỗi người Hiểu Mình, Cải Mệnh & Chữa Lành."},
  "11-huong-dan-van-phong": {"desc": "Hướng dẫn văn phong Tử Vi Chữa Lành: luận giải ấm áp, từ bi, trao quyền, không gieo sợ hãi, dùng ngôn ngữ bản đồ thay cho lời kết luận tuyệt đối."},
  "12-ten-goi-slogan-dinh-vi": {"desc": "Tên gọi, slogan và định vị Tử Vi Chữa Lành: ý nghĩa “Lá số là bản đồ, không phải bản án” và tinh thần Hiểu Mình, Cải Mệnh & Chữa Lành của Bộ Tộc."},
  "cc1-y-nghia-14-chinh-tinh-cu-tai-12-cung": {"desc": "Ý nghĩa 14 Chính Tinh khi cư tại 12 cung: tra cứu Tử Vi, Thiên Cơ, Thái Dương… ở Mệnh, Tài Bạch, Quan Lộc, Phu Thê với Mặt Sáng, Mặt Tối theo TVCL."},
  "cc2-y-nghia-18-trung-tinh-cu-tai-12-cung": {"desc": "Ý nghĩa 18 Trung Tinh khi cư tại 12 cung: tra cứu năng lượng từng sao ở Mệnh, Tài Bạch, Quan Lộc, Phu Thê… cùng Mặt Sáng, Mặt Tối và hướng chuyển hóa."},
  "th1-tinh-hoa-tvcl": {"desc": "Tinh Hoa Tử Vi Chữa Lành: tri thức nền tảng qua năm phần — đổi cách nhìn, bốn lăng kính, đọc tấm bản đồ lá số, chữa lành và cải mệnh, ứng dụng."},
  # tt1: Codex đã chuyển hướng sang /tu-vi-dau-so-toan-thu/ (01/11)
}

# 28 trang sao (HTML tĩnh, không có generator): tên, nguyên mẫu ngắn
STARS = {
  "sao-tu-vi": ("Tử Vi", "Hoàng Đế, năng lượng lãnh đạo và quy tụ"),
  "sao-thien-co": ("Thiên Cơ", "bộ óc mưu lược, trí tuệ linh hoạt"),
  "sao-thai-duong": ("Thái Dương", "Mặt Trời, minh chủ dẫn dắt cộng đồng"),
  "sao-vu-khuc": ("Vũ Khúc", "đại tướng tài chính, nhà kinh doanh thực thi"),
  "sao-thien-dong": ("Thiên Đồng", "đứa trẻ của Trời, người mang niềm vui"),
  "sao-liem-trinh": ("Liêm Trinh", "quan giám sát, người giữ nguyên tắc"),
  "sao-thien-phu": ("Thiên Phủ", "người quản kho, nhà điều hành tài chính"),
  "sao-thai-am": ("Thái Âm", "Mặt Trăng, người mẹ, nhà kế hoạch tài chính"),
  "sao-tham-lang": ("Tham Lang", "người chinh phục, nhà ngoại giao"),
  "sao-cu-mon": ("Cự Môn", "nhà phát ngôn, nhà diễn thuyết"),
  "sao-thien-tuong": ("Thiên Tướng", "tể tướng giữ ấn, người phò tá tận tâm"),
  "sao-thien-luong": ("Thiên Lương", "thanh quan ngự sử, bậc trưởng lão"),
  "sao-that-sat": ("Thất Sát", "chủ soái nơi biên cương, đại tướng quyền uy"),
  "sao-pha-quan": ("Phá Quân", "tướng tiên phong, người khai phá"),
  "sao-kinh-duong": ("Kình Dương", "lưỡi kiếm chưa rèn, sức mạnh quyết đoán"),
  "sao-da-la": ("Đà La", "gai trong giày, nỗi đau âm thầm cần nhìn thấu"),
  "sao-hoa-tinh": ("Hỏa Tinh", "ngọn lửa hành động bùng nổ"),
  "sao-linh-tinh": ("Linh Tinh", "than hồng âm ỉ, người giữ lửa"),
  "sao-dia-khong": ("Địa Không", "khoảng trống trong tâm, nhà hiền triết"),
  "sao-dia-kiep": ("Địa Kiếp", "năng lượng phá tán, bài học buông bỏ"),
  "sao-ta-phu": ("Tả Phù", "người trợ lực thực thi bên Hoàng Đế"),
  "sao-huu-bat": ("Hữu Bật", "nhà mưu lược giỏi kết nối"),
  "sao-van-xuong": ("Văn Xương", "trí tuệ hệ thống, cây viết sắc"),
  "sao-van-khuc": ("Văn Khúc", "tài hoa nghệ thuật, tư duy cảm thụ"),
  "sao-thien-khoi": ("Thiên Khôi", "quý nhân bề trên, cửa Trời mở lối"),
  "sao-thien-viet": ("Thiên Việt", "quý nhân trợ giúp âm thầm"),
}

def star_meta(slug):
    name, arch = STARS[slug]
    title = f"Sao {name} Là Sao Gì? Mặt Sáng & Mặt Tối" + SUFFIX
    desc = f"Sao {name} là sao gì? {arch[0].upper()+arch[1:]}. Giải mã Mặt Sáng, Mặt Tối và cách chuyển hóa năng lượng sao {name} theo Tử Vi Chữa Lành."
    if len(desc) < 120:
        desc = desc[:-1] + " để Hiểu Mình."
    return title, desc

# Trang HTML viết tay khác (đường dẫn file → desc mới)
PAGE_DESC = {
  "khoa-hoc-tu-vi-bi-kip-chua-lanh/index.html": "Khóa Tử Vi Bí Kíp Chữa Lành: ứng dụng Tử Vi, Tâm lý và Đạo học để hiểu mình, chữa lành tổn thương. Thầy Quán Trung trực tiếp giảng dạy qua Zoom.",
  "luan-van-han/index.html": "Khóa Luận Vận Hạn Tử Vi dành cho người đã biết Tử Vi: hơn 80 video, 5 buổi thực hành qua Zoom, hiểu dòng chảy vận hạn trên chính lá số của bạn.",
  "chinh-sach-bao-mat/index.html": "Chính sách bảo mật của Tử Vi Chữa Lành (tuvichualanh.com): thông tin chúng tôi nhận, cách sử dụng, bảo vệ dữ liệu và công cụ quản lý kênh YouTube TVCL.",
  "khoa-hoc-tu-vi-chua-lanh/index.html": "Khóa học Tử Vi Chữa Lành: kết hợp Tử Vi, Tâm lý học và Đạo học để hiểu mình sâu sắc, chuyển hóa vòng lặp cũ và chủ động định hướng cuộc đời.",
}

# 14 trang Toàn Thư (Codex dựng trang; Claude chuẩn hóa mô tả 01/11)
PAGE_DESC.update({
  "sao-cu-mon-tu-vi-dau-so-toan-thu/index.html": "Sao Cự Môn trong Tử Vi Đẩu Số Toàn Thư: ngôn ngữ, chất vấn, phân tích và khả năng nói ra điều chưa nói. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-liem-trinh-tu-vi-dau-so-toan-thu/index.html": "Sao Liêm Trinh trong Tử Vi Đẩu Số Toàn Thư: nguyên tắc, ranh giới, sức hút và năng lực tự rèn luyện. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-pha-quan-tu-vi-dau-so-toan-thu/index.html": "Sao Phá Quân trong Tử Vi Đẩu Số Toàn Thư: đổi mới, phá bỏ khuôn cũ và tái cấu trúc điều không còn phù hợp. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-thai-am-tu-vi-dau-so-toan-thu/index.html": "Sao Thái Âm trong Tử Vi Đẩu Số Toàn Thư: nội tâm, sự nuôi dưỡng, chiều sâu cảm nhận và tài sản tích lũy. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-thai-duong-tu-vi-dau-so-toan-thu/index.html": "Sao Thái Dương trong Tử Vi Đẩu Số Toàn Thư: ánh sáng, sự hiện diện, tinh thần đóng góp và vai trò công khai. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-tham-lang-tu-vi-dau-so-toan-thu/index.html": "Sao Tham Lang trong Tử Vi Đẩu Số Toàn Thư: ham muốn, sức hút xã hội và năng lực khai mở tiềm năng. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-that-sat-tu-vi-dau-so-toan-thu/index.html": "Sao Thất Sát trong Tử Vi Đẩu Số Toàn Thư: quyết đoán, dũng khí hành động và khả năng đối diện thách thức. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-thien-co-tu-vi-dau-so-toan-thu/index.html": "Sao Thiên Cơ trong Tử Vi Đẩu Số Toàn Thư: trí tuệ linh hoạt, mưu lược và khả năng xoay chuyển. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-thien-dong-tu-vi-dau-so-toan-thu/index.html": "Sao Thiên Đồng trong Tử Vi Đẩu Số Toàn Thư: sự hòa ái, khả năng thích nghi và nhu cầu sống nhẹ nhàng. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-thien-luong-tu-vi-dau-so-toan-thu/index.html": "Sao Thiên Lương trong Tử Vi Đẩu Số Toàn Thư: đạo lý, kinh nghiệm, che chở và khả năng chỉ dẫn. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-thien-phu-tu-vi-dau-so-toan-thu/index.html": "Sao Thiên Phủ trong Tử Vi Đẩu Số Toàn Thư: kho tàng, sự bao bọc, năng lực quản trị và gìn giữ nguồn lực. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-thien-tuong-tu-vi-dau-so-toan-thu/index.html": "Sao Thiên Tướng trong Tử Vi Đẩu Số Toàn Thư: bảo hộ, điều phối, tinh thần phục vụ và vai trò cầu nối. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-tu-vi-tu-vi-dau-so-toan-thu/index.html": "Sao Tử Vi trong Tử Vi Đẩu Số Toàn Thư: trung tâm, uy quyền và năng lực quy tụ. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
  "sao-vu-khuc-tu-vi-dau-so-toan-thu/index.html": "Sao Vũ Khúc trong Tử Vi Đẩu Số Toàn Thư: tài chính, kỷ luật, năng lực thực thi và tính tự chủ. Mặt sáng và vùng cần điều hòa theo Tử Vi Chữa Lành.",
})
