import base64,os,json
s=open('bipl-artifact.html').read()
tiles={f[:-4]:"data:image/png;base64,"+base64.b64encode(open("tiles/"+f,"rb").read()).decode() for f in os.listdir("tiles")}
old='L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {maxZoom:19,'
assert old in s
new=('var EmbeddedTiles = L.TileLayer.extend({getTileUrl:function(c){return (window.TILES||{})[c.z+"_"+c.x+"_"+c.y] || "data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==";}});\n'
     '  new EmbeddedTiles("", {minZoom:14, maxZoom:17,')
s=s.replace(old,new)
s=s.replace('L.map("map", {scrollWheelZoom:false})','L.map("map", {scrollWheelZoom:false, minZoom:14, maxZoom:17})')
i=s.rfind('<script>'); s=s[:i]+'<script>window.TILES='+json.dumps(tiles)+';</script>\n'+s[i:]
assert 'window.TILES=' in s
open('bipl-artifact.html','w').write(s)
print(os.path.getsize('bipl-artifact.html')//1024,"KB")
