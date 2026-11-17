import json, time, urllib.parse, urllib.request, os, math
from candidates import STORES
CACHE="geo_cache.json"
cache=json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def q(addr):
    url="https://nominatim.openstreetmap.org/search?"+urllib.parse.urlencode({"q":"광주광역시 서구 "+addr,"countrycodes":"kr","format":"json","addressdetails":1,"limit":1})
    req=urllib.request.Request(url,headers={"User-Agent":"lunch-map-geocoder/0.1"})
    return json.load(urllib.request.urlopen(req,timeout=30))
for addr in sorted({s[1] for s in STORES}):
    if addr in cache: continue
    try: r=q(addr)
    except Exception as e: print("ERR",addr,e); continue
    if r:
        a=r[0]; cache[addr]={"lat":float(a["lat"]),"lon":float(a["lon"]),"exact":"house_number" in a.get("address",{}),"name":a["display_name"]}
    else: cache[addr]=None
    json.dump(cache,open(CACHE,"w"),ensure_ascii=False,indent=1)
    time.sleep(1.1)
print("done",len(cache), "exact",sum(1 for v in cache.values() if v and v["exact"]), "none",sum(1 for v in cache.values() if not v))
