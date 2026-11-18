// build_data.py와 같은 규칙으로 data.js를 다시 만든다 (이 컴퓨터엔 Python이 없어서 Node로 옮김)
// 실행: ego-browser nodejs -e 'await import("file:///D:/SEONA2/bipl-lunch-map/tools/build_data_port.mjs")' (Node만 있으면 node build_data_port.mjs)
const fs = await import("node:fs/promises");
const { fileURLToPath } = await import("node:url");
const dir = fileURLToPath(new URL("../", import.meta.url)).replace(/\\/g, "/");
const py = (await fs.readFile(dir + "tools/build_data.py", "utf8")).replace(/\r\n/g, "\n");
const block = (name) => { const a = py.indexOf("\n" + name + " = {"); const b = py.indexOf("\n}", a); return py.slice(a, b + 2); };
const tuples = (txt) => { const o = new Map(); for (const line of txt.split("\n")) { const m = line.match(/^ "(.+?)": \((.*)\),$/); if (m) o.set(m[1], JSON.parse("[" + m[2] + "]")); } return o; };
const barsTxt = py.slice(py.indexOf("BARS = {"), py.indexOf("}", py.indexOf("BARS = {")));
const BARS = new Set([...barsTxt.split("\n").map(l => l.replace(/#.*$/, "")).join("\n").matchAll(/"([^"]+)"/g)].map(m => m[1]));
const nlTxt = py.slice(py.indexOf("NO_LUNCH = {"), py.indexOf("}", py.indexOf("NO_LUNCH = {")));
const NO_LUNCH = new Set([...nlTxt.split("\n").map(l => l.replace(/#.*$/, "")).join("\n").matchAll(/"([^"]+)"/g)].map(m => m[1]));
const exTxt = py.slice(py.indexOf("EXCLUDE = {"), py.indexOf("}", py.indexOf("EXCLUDE = {")));
const EXCLUDE = new Set([...exTxt.split("\n").map(l => l.replace(/#.*$/, "")).join("\n").matchAll(/"([^"]+)"/g)].map(m => m[1]));
const CAT_FIX = JSON.parse(py.match(/^CAT_FIX = (\{.*\})$/m)[1]);
const NAME_FIX = JSON.parse(py.match(/^NAME_FIX = (\{.*\})$/m)[1]);
const N = tuples(block("N")), S = tuples(block("S")), M = tuples(block("M"));
const CHECKED = py.match(/^CHECKED = "(.+)"$/m)[1];
const menuFor = (name) => { for (const [k, v] of M) if (name.startsWith(k) || name.includes(k)) return v; return null; };
const rows = JSON.parse(await fs.readFile(dir + "tools/all_rows.json", "utf8"));
const PLACE_IDS = JSON.parse(await fs.readFile(dir + "tools/place_ids.json", "utf8"));
const out = [];
for (const r of rows) {
  if (r.dist == null || r.dist > 600 || BARS.has(r.name) || NO_LUNCH.has(r.name) || EXCLUDE.has(r.name)) continue;
  const name = NAME_FIX[r.name] ?? r.name, cat = CAT_FIX[r.name] ?? r.cat;
  const m = N.get(name) || S.get(name) || menuFor(name);
  const item = { name, addr: r.addr, cat, src: r.src.split(",").map(s => s === "전체" ? "전체 가맹점" : "비플식권"), lat: r.lat, lon: r.lon, dist: r.dist, approx: r.acc === "근사" };
  const ids = PLACE_IDS[name] || {};
  if (ids.kakao) item.kakaoId = ids.kakao;
  if (ids.naver) item.naverId = ids.naver;
  if (cat !== "편의점·마트") {
    if (m) { item.menu = m[0]; item.menuSrc = { url: m[1], label: m[2], checked: m.length > 4 ? m[4] : CHECKED }; if (m[3]) item.menuNote = m[3]; }
    else { item.menu = []; item.menuNote = "대표메뉴 미확인"; }
  }
  out.push(item);
}
const old = (await fs.readFile(dir + "data.js", "utf8"));
const crlf = old.includes("\r\n");
const head = old.replace(/\r\n/g, "\n").split("\n").slice(0, 3).join("\n") + "\n";
let txt = head + "window.STORES = " + JSON.stringify(out, null, 1) + ";\n";
if (crlf) txt = txt.replace(/\n/g, "\r\n");
await fs.writeFile(dir + "data.js", txt, "utf8");
const cnt = {}; out.forEach(x => cnt[x.cat] = (cnt[x.cat] || 0) + 1);
console.log({ BARS: BARS.size, N: N.size, S: S.size, M: M.size, total: out.length, cnt, withMenu: out.filter(x => x.menu && x.menu.length).length, noMenu: out.filter(x => x.menu && !x.menu.length).map(x => x.name) });
