import re
src=open('../index.html').read()
data=open('../data.js').read()
lcss=open('node_modules/leaflet/dist/leaflet.css').read(); ljs=open('node_modules/leaflet/dist/leaflet.js').read()
src=src.replace('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">','<style>'+lcss+'</style>')
src=src.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>','<script>'+ljs+'</script>')
src=src.replace('<script src="data.js"></script>','<script>'+data+'</script>')
src=src.replace('<!doctype html>\n','')
for t in ['<html lang="ko">','</html>','<head>','</head>','<body>','</body>']: src=src.replace(t,'')
src=re.sub(r'<meta charset="utf-8">\n|<meta name="viewport"[^>]*>\n','',src)
assert 'cdnjs' not in src
open('bipl-artifact.html','w').write(src.strip()+'\n')
