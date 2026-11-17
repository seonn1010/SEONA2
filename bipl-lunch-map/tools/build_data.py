import json
rows = json.load(open("all_rows.json"))
CHECKED = "2026-11-17"

BARS = {"한식주점 오감", "리얼펍 상무점", "인과연 혼술바", "술에취한바다", "위스키픽", "서로혼술바 상무점", "2층맥주집"}

# 대표메뉴: (메뉴목록, 출처URL, 출처설명, 비고)
M = {
 "파리바게뜨": (["샌드위치", "고추장 불고기 샌드위치", "빵·케이크"], "https://www.news1.kr/amp/industry/distribution/6242111", "뉴스1 (브랜드 기준)", "브랜드 공통 메뉴 기준"),
 "메가MGC커피": (["메가리카노", "할메가커피", "바닐라라떼"], "https://www.smarttoday.co.kr/ko-kr/articles/104376", "스마트투데이 (판매 상위 메뉴 보도)", "브랜드 공통 메뉴 기준"),
 "텐퍼센트커피": (["텐라떼(시그니처 라떼)", "아인슈페너 라떼"], "https://polle.com/lkhun71/posts/1181", "폴레 방문 후기", "브랜드 공통 메뉴 기준"),
 "우지커피": (["딥 카페라떼"], "https://www.hankyung.com/article/2026050562841", "한국경제", "브랜드 공통 메뉴 기준"),
 "크리스피크림도넛": (["오리지널 글레이즈드"], "https://www.insight.co.kr/news/339766", "인사이트", "브랜드 공통 메뉴 기준"),
 "KFC": (["징거버거", "핫크리스피치킨"], "https://news.bizwatch.co.kr/article/consumer/2025/07/04/0022", "비즈워치", "브랜드 공통 메뉴 기준"),
 "봉구스밥버거": (["봉구스 밥버거", "햄치즈 밥버거", "제육 밥버거"], "https://www.insight.co.kr/news/133179", "인사이트", "브랜드 공통 메뉴 기준"),
 "프랭크버거": (["치즈버거", "오리지널 버거", "비프&쉬림프 버거"], "https://autoreserve.com/th/restaurants/JZUQmGby1jWwYufMoWXb", "오토리저브 (다른 지점 메뉴)", "다른 지점 메뉴 기준"),
 "왓더버거": (["왓더버거", "불고기버거", "치킨버거"], "https://autoreserve.com/it/restaurants/fQh3izgLT2gZqENJaLXe", "오토리저브 (다른 지점 메뉴)", "다른 지점 메뉴 기준"),
 "서가앤쿡": (["목살 스테이크", "크림 파스타", "필라프"], "https://polle.com/place/4zg5KT/%EC%84%9C%EA%B0%80%EC%95%A4%EC%BF%A1", "폴레 리뷰", "다른 지점 메뉴 기준"),
 "국수나무": (["잔치국수", "돈까스", "냉면"], "https://autoreserve.com/fr/restaurants/Tc2QFFYdHXUVq6K6HTgR", "오토리저브 (다른 지점 메뉴)", "다른 지점 메뉴 기준"),
 "김가네": (["김가네 김밥", "참치김밥", "라볶이"], "https://polle.com/place/16oJPq/%EA%B9%80%EA%B0%80%EB%84%A4%20%EA%B9%80%EB%B0%A5", "폴레 리뷰", "다른 지점 메뉴 기준"),
 "미카도스시": (["초밥", "롤", "우동"], "https://autoreserve.com/en/restaurants/dTLdnGnqtLdfEWeUH15R", "오토리저브 (다른 지점 메뉴)", "다른 지점 메뉴 기준"),
 "개성손만두": (["만두전골", "손만두"], "https://autoreserve.com/en/restaurants/GwXo7e1mbQu1zNS2X5Xg", "오토리저브 (다른 지점 메뉴)", "다른 지점 메뉴 기준"),
 "매운날": (["치즈갈비찜"], "https://polle.com/place/4b3S1y/%EB%A7%A4%EC%9A%B4%EB%82%A0", "폴레 (광주 첨단 지점)", "다른 지점 메뉴 기준"),
 "할멈탕수육김밥": (["탕수육", "떡볶이", "김밥"], "https://polle.com/moya95/posts/865", "폴레 후기 (광주 다른 지점)", "다른 지점 메뉴 기준"),
 "상무쌈밥": (["수육쌈밥", "제육쌈밥", "애호박찌개"], "https://daangn.com/kr/local-profile/%EC%83%81%EB%AC%B4%EC%8C%88%EB%B0%A5-iucinxccfb4s/", "당근 업체 페이지", ""),
 "채가곰탕": (["곰탕(한우 암소)"], "https://hotplacehunter.co.kr/sns/article/79174/", "핫플헌터", ""),
 "진미가람": (["돼지갈비", "석갈비", "숯불쌈밥"], "https://www.siksinhot.com/toplists/best/041474_Gwangju", "식신", ""),
 "꾸다": (["돼지짜글이(점심)", "우거지 해장국(점심)"], "https://polle.com/place/1A0gbJ/%EA%BE%B8%EB%8B%A4", "폴레 리뷰", "저녁엔 주점 메뉴 위주"),
 "현완단겸": (["상추튀김", "오징어튀김"], "https://polle.com/place/1l8pMC/%ED%98%84%EC%99%84%EB%8B%A8%EA%B2%B8%20%EC%83%81%EC%B6%94%ED%8A%80%EA%B9%80", "폴레 리뷰", ""),
 "골든웨이브": (["우삼겹 쌀국수(점심)", "소고기 쌀국수", "쏨땀"], "https://www.trvlogue.com/ko/soi-yeonnam-gwangju-sangmu", "트래블로그 (소이연남 광주상무점 후기)", "같은 주소(운천로 261)의 '소이연남 광주상무점' 정보 — 같은 가게인지 미확인"),
}
def menu_for(name):
    for k, v in M.items():
        if name.startswith(k) or k in name:
            return v
    return None

out = []
for r in rows:
    if r["dist"] is None or r["dist"] > 600 or r["name"] in BARS:
        continue
    m = menu_for(r["name"])
    item = {
        "name": r["name"], "addr": r["addr"], "cat": r["cat"],
        "src": ["전체 가맹점" if s == "전체" else "비플식권" for s in r["src"].split(",")],
        "lat": r["lat"], "lon": r["lon"], "dist": r["dist"], "approx": r["acc"] == "근사",
    }
    if r["cat"] != "편의점·마트":
        if m:
            item["menu"] = m[0]; item["menuSrc"] = {"url": m[1], "label": m[2], "checked": CHECKED}
            if m[3]: item["menuNote"] = m[3]
        else:
            item["menu"] = []; item["menuNote"] = "대표메뉴 미확인"
    out.append(item)

meta = {"origin": {"name": "L.L.M Academy", "addr": "광주 서구 상무중앙로 44", "lat": 35.1508811, "lon": 126.8489117},
        "radius": 600, "checked": CHECKED}
with open("../data.js", "w") as f:
    f.write("// 자동 생성 파일: 비플페이 앱 '전체 가맹점 사용처'·'비플식권 사용처' 화면 캡처를 옮겨 적고,\n")
    f.write("// 주소 좌표는 OpenStreetMap Nominatim으로 변환함 (" + CHECKED + ")\n")
    f.write("window.META = " + json.dumps(meta, ensure_ascii=False) + ";\n")
    f.write("window.STORES = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
import collections
print(len(out), collections.Counter(x["cat"] for x in out), sum(1 for x in out if x.get("menu")), "with menu")
