import json
rows = json.load(open("all_rows.json"))
CHECKED = "2026-11-17"

BARS = {"한식주점 오감", "리얼펍 상무점", "인과연 혼술바", "술에취한바다", "위스키픽", "서로혼술바 상무점", "2층맥주집",
        # 2026-11-18 추가 제외 (메뉴·영업시간으로 보아 점심 음식점이 아님, 사용자 결정)
        "시그널",        # 카카오맵 업종 '유흥주점', 메뉴 없음
        "아이케이케이",  # 인허가 정보 '유흥주점(노래주점)', 지도 앱에 없음
        "빽바지집",      # 카카오맵 '치평동빽바지포차'(실내포장마차, 16:30~01:00)
}

# 점심 영업 안 함 (2026-11-18 카카오맵·네이버 영업시간 확인, 사용자 지시로 제외)
NO_LUNCH = {
    "쪽갈비대장 상무직영점",  # 매일 17:00 오픈
    "돈 고기집 상무점",        # 매일 17:00 오픈
}

# 그 밖에 사용자가 빼라고 한 곳 (2026-11-18)
EXCLUDE = {
    "뉴벨퀴진",  # 지도 앱에 없음. 같은 주소의 '육시육분'과 같은 가게인지 확인 안 됨
}

# 업종 바로잡기 (2026-11-18, 사용자 결정): 지도 앱 업종이 커피전문점
CAT_FIX = {"모람": "카페", "티파라치": "카페"}
# 이름 바로잡기: 앱 표기 '뉴벨퀴진' → 인허가 이름 '누벨퀴진'
NAME_FIX = {"뉴벨퀴진": "누벨퀴진"}

# 메뉴는 tools/menus.json 한 곳에서만 고친다 (2026-11-19). 키 = 가게 고정 id, 값 = {"menu": [...], "menuSrc": {...}, "menuNote": "..."}
# 예전의 N(네이버)·S(가게별)·M(브랜드) 메뉴 표는 이 파일로 옮기면서 없앴다 (git 기록에 남아 있음)
MENUS = json.load(open("menus.json", encoding="utf-8"))

# 가게 고유번호 (지도 앱 버튼이 검색창이 아니라 가게 페이지로 바로 가도록). 2026-11-18 에고브라우저로 이름·주소를 대조해 모음
PLACE_IDS = json.load(open("place_ids.json", encoding="utf-8"))

# 고정 id: 후기(store_id)가 여기에 붙으므로 한 번 정한 id는 store_ids.json에 저장해 두고 절대 바꾸지 않는다
# 처음 정할 때 규칙: kakaoId → "kakao-번호", 없으면 naverId → "naver-번호", 둘 다 없으면 이름으로 만든 "name-slug"
import os, re, unicodedata
SID = json.load(open("store_ids.json", encoding="utf-8")) if os.path.exists("store_ids.json") else {}
def slug(n):
    return "name-" + re.sub(r"[^0-9a-z가-힣]+", "-", unicodedata.normalize("NFC", n).lower()).strip("-")

# 제로페이 (2026-11-19): zeropay_merge.json
#   both: 비플 목록의 가게 중 제로페이 가맹점과 상호·도로명주소가 둘 다 맞아 같은 가게로 본 곳(이름) → 배지 둘 다
#   rows: 제로페이에만 있는 새 가게 (좌표·거리·kakaoId·naverId 포함, 술집·저녁 장사·점심 영업 없음은 이미 뺀 상태)
ZP = json.load(open("zeropay_merge.json", encoding="utf-8")) if os.path.exists("zeropay_merge.json") else {"both": [], "rows": []}
ZP_BOTH = set(ZP["both"])

out = []
def finish(item, ids):
    if ids.get("kakao"): item["kakaoId"] = ids["kakao"]
    if ids.get("naver"): item["naverId"] = ids["naver"]
    name = item["name"]
    if name not in SID:
        SID[name] = ("kakao-" + item["kakaoId"]) if item.get("kakaoId") else ("naver-" + item["naverId"]) if item.get("naverId") else slug(name)
    item["id"] = SID[name]
    # 음식 분류(한식·중식 등, 검색용)도 menus.json에서 가져온다
    if (MENUS.get(item["id"]) or {}).get("cuisine"): item["cuisine"] = MENUS[item["id"]]["cuisine"]
    if item["cat"] != "편의점·마트":
        mm = MENUS.get(item["id"])
        if mm and mm.get("menu"):
            item["menu"] = mm["menu"]; item["menuSrc"] = mm["menuSrc"]
            if mm.get("menuNote"): item["menuNote"] = mm["menuNote"]
        else:
            item["menu"] = []; item["menuNote"] = (mm or {}).get("menuNote") or "대표메뉴 미확인"
    out.append(item)

for r in rows:
    if r["dist"] is None or r["dist"] > 600 or r["name"] in BARS or r["name"] in NO_LUNCH or r["name"] in EXCLUDE:
        continue
    name = NAME_FIX.get(r["name"], r["name"])
    cat = CAT_FIX.get(r["name"], r["cat"])
    item = {
        "id": None, "name": name, "addr": r["addr"], "cat": cat,
        "src": ["전체 가맹점" if s == "전체" else "비플식권" for s in r["src"].split(",")],
        "pay": ["비플식권"] + (["제로페이"] if name in ZP_BOTH else []),
        "lat": r["lat"], "lon": r["lon"], "dist": r["dist"], "approx": r["acc"] == "근사",
    }
    finish(item, PLACE_IDS.get(name, {}))

for z in ZP["rows"]:
    item = {"id": None, "name": z["name"], "addr": z["addr"], "cat": z["cat"], "src": [], "pay": ["제로페이"],
            "lat": z["lat"], "lon": z["lon"], "dist": z["dist"], "approx": False}
    if z.get("check", True): item["zpCheck"] = True  # 제로페이에만 있는 가게: 결제 가능 여부 확인 필요
    finish(item, {"kakao": z.get("kakaoId"), "naver": z.get("naverId")})

ids_all = [x["id"] for x in out]
assert len(ids_all) == len(set(ids_all)), "id 중복"
json.dump(SID, open("store_ids.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

sources = [{"name": "비플페이 앱 '전체 가맹점 사용처'·'비플식권 사용처' 화면", "pay": "비플식권", "checked": CHECKED}]
if ZP["rows"] or ZP["both"]:
    sources.append({"name": "제로페이 가맹점 찾기", "pay": "제로페이", "url": ZP["source"], "checked": ZP["checked"]})
meta = {"origin": {"name": "L.L.M Academy", "addr": "광주 서구 상무중앙로 44", "lat": 35.1508811, "lon": 126.8489117},
        "radius": 600, "checked": CHECKED, "sources": sources}
with open("../data.js", "w", encoding="utf-8", newline="\n") as f:
    f.write("// 자동 생성 파일 (tools/build_data.py 또는 tools/build_data_port.mjs). 직접 고치지 말 것 — 메뉴는 tools/menus.json, 규칙은 tools/build_data.py\n")
    f.write("// 가게 목록 출처는 META.sources. 비플 목록 좌표는 OpenStreetMap Nominatim, 제로페이 가게 좌표는 카카오맵 기준\n")
    f.write("window.META = " + json.dumps(meta, ensure_ascii=False) + ";\n")
    f.write("window.STORES = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
import collections
print(len(out), collections.Counter(x["cat"] for x in out), sum(1 for x in out if x.get("menu")), "with menu")
