import json,re,math,collections
from candidates import STORES
c=json.load(open("geo_cache.json"))
A=(35.1508811,126.8489117)
def d(a,b):
    R=6371000;p1,p2=map(math.radians,(a[0],b[0]));dp=p2-p1;dl=math.radians(b[1]-a[1])
    return 2*R*math.asin(math.sqrt(math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2))
def split(a):
    m=re.match(r"(.+?) (\d+)(?:-\d+)?$",a); return (m.group(1),int(m.group(2))) if m else (a,None)
anch=collections.defaultdict(list)
for a,v in c.items():
    if v["exact"]:
        r,n=split(a); anch[r].append((n,v["lat"],v["lon"]))
# 수동 보정 (도로 구간 좌표, 근사)
manual={
 "마륵복개로":(35.1463041,126.8508220), "마륵로":(35.1465915,126.8452195),
 "상무공원로 10":(35.1498012,126.8429811), "상무민주로":(35.1528130,126.8582934),
 "운천로 261":(35.1553222,126.8549795),
}
pos={}
for a,v in c.items():
    r,n=split(a)
    if v["exact"]: pos[a]=(v["lat"],v["lon"],"정확"); continue
    if a=="치평동 1208-5": pos[a]=None; continue
    if a in manual: pos[a]=(*manual[a],"근사"); continue
    if r in manual: pos[a]=(*manual[r],"근사"); continue
    pts=sorted(set(anch.get(r,[])))
    if len(pts)>=2 and n is not None:
        lo=[p for p in pts if p[0]<=n]; hi=[p for p in pts if p[0]>=n]
        p1,p2=(lo[-1],hi[0]) if lo and hi else ((pts[0],pts[1]) if not lo else (pts[-2],pts[-1]))
        if p1[0]==p2[0]: pos[a]=(p1[1],p1[2],"보정"); continue
        t=(n-p1[0])/(p2[0]-p1[0]); pos[a]=(p1[1]+t*(p2[1]-p1[1]),p1[2]+t*(p2[2]-p1[2]),"보정"); continue
    if len(pts)==1: pos[a]=(pts[0][1],pts[0][2],"근사"); continue
    pos[a]=(v["lat"],v["lon"],"근사")
rows=[]
for name,addr,cat,src in STORES:
    p=pos[addr]
    dist=None if p is None else round(d(A,p[:2]))
    rows.append(dict(name=name,addr="광주 서구 "+addr,cat=cat,src=src,lat=p and round(p[0],6),lon=p and round(p[1],6),acc=p[2] if p else "미확인",dist=dist))
rows.sort(key=lambda r:(r["dist"] is None, r["dist"] or 0))
json.dump(rows,open("all_rows.json","w"),ensure_ascii=False,indent=1)
for r in rows:
    if r["dist"] is None or r["dist"]<=1300: print(r["dist"],r["acc"],r["cat"],r["name"],"|",r["addr"],"|",r["src"])
