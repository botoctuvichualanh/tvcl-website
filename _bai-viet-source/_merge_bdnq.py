import json,sys
N=["SAO / HẠT GIỐNG","DUYÊN / BỐI CẢNH","TÂM / LĂNG KÍNH","HÀNH / PHẢN ỨNG","NGHIỆP / MÔ THỨC LẶP","VẬN / THỜI ĐIỂM","QUẢ / SỰ KIỆN","CHUYỂN HÓA / NHÂN MỚI"]
p='_bai-viet-source/03_tuvichualanh_80_articles_database.json'
d=json.load(open(p,encoding='utf-8'))
new=json.load(open(sys.argv[1],encoding='utf-8'))
for a in d['articles']:
  k=str(a['index'])
  if k in new:
    assert len(new[k])==8,k
    a['causalFlow8Steps']=[{"step":n,"description":t,"example":e} for n,(t,e) in zip(N,new[k])]
json.dump(d,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('merged',sorted(new,key=int),'| total 8-step:',sum(1 for a in d['articles'] if a.get('causalFlow8Steps')))
