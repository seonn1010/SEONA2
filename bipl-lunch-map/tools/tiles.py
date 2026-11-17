import math,os,time,urllib.request
lat,lon=35.1508811,126.8489117
dlat=1250/111320; dlon=1250/(111320*math.cos(math.radians(lat)))
def t(la,lo,z):
    n=2**z; x=int((lo+180)/360*n); y=int((1-math.asinh(math.tan(math.radians(la)))/math.pi)/2*n); return x,y
total=0
for z in (14,15,16,17):
    x0,y0=t(lat+dlat,lon-dlon,z); x1,y1=t(lat-dlat,lon+dlon,z)
    for x in range(x0,x1+1):
        for y in range(y0,y1+1):
            p=f"tiles/{z}_{x}_{y}.png"
            if os.path.exists(p): continue
            req=urllib.request.Request(f"https://tile.openstreetmap.org/{z}/{x}/{y}.png",headers={"User-Agent":"lunch-map-preview/0.1 (personal study project)"})
            open(p,"wb").write(urllib.request.urlopen(req,timeout=30).read()); total+=1; time.sleep(0.2)
    print(z,(x1-x0+1)*(y1-y0+1),"tiles")
print("downloaded",total, sum(os.path.getsize("tiles/"+f) for f in os.listdir("tiles"))//1024,"KB")
