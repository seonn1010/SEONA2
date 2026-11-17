import json, time, urllib.parse, urllib.request, re, math
c=json.load(open("geo_cache.json"))
A=(35.1508811,126.8489117)
def d(a,b):
    R=6371000;p1,p2=map(math.radians,(a[0],b[0]));dp=p2-p1;dl=math.radians(b[1]-a[1])
    return 2*R*math.asin(math.sqrt(math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2))
def q(s):
    url="https://nominatim.openstreetmap.org/search?"+urllib.parse.urlencode({"q":"광주광역시 서구 "+s,"countrycodes":"kr","format":"json","addressdetails":1,"limit":1})
    r=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"lunch-map-geocoder/0.1"}),timeout=30))
    time.sleep(1.1)
    if r and "house_number" in r[0].get("address",{}): return r[0]
far=("동천","하남대로","유림로","내방로 23","천변좌하로")
for addr,v in c.items():
    if v["exact"] or v.get("approx") or any(f in addr for f in far): continue
    m=re.match(r"(.+?) (\d+)(?:-\d+)?$",addr)
    if not m: continue
    road,n=m.group(1),int(m.group(2))
    hit=None
    for k in [0,2,-2,4,-4,6,-6,8,-8,10,-10,14,-14,20,-20]:
        nn=n+k
        if nn<1: continue
        r=q(f"{road} {nn}")
        if r: hit=(nn,r);break
    if hit:
        nn,r=hit; v.update(lat=float(r["lat"]),lon=float(r["lon"]),approx=f"{road} {nn} 기준(오차 약 {abs(nn-n)*10}m)")
        print("OK",addr,"->",nn,int(d(A,(v['lat'],v['lon']))))
    else:
        v["approx"]="미확인"; print("FAIL",addr)
    json.dump(c,open("geo_cache.json","w"),ensure_ascii=False,indent=1)
