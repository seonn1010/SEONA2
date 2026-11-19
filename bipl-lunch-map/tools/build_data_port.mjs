// build_data.py와 같은 규칙으로 ../data.js를 만든다 (이 컴퓨터엔 Python이 없어서 Node로 옮김)
// 실행: ego-browser nodejs -e 'await import("file:///D:/SEONA2/bipl-lunch-map/tools/build_data_port.mjs")'  (Node가 있으면 node build_data_port.mjs)
// 규칙(제외 목록·업종/이름 바로잡기)은 build_data.py에서 읽어 온다. 메뉴는 menus.json, 제로페이는 zeropay_merge.json, 고정 id는 store_ids.json
const fs = await import("node:fs/promises");
const { fileURLToPath } = await import("node:url");
const dir = fileURLToPath(new URL("../", import.meta.url)).replace(/\\/g, "/");
const T = dir + "tools/";
const py = (await fs.readFile(T + "build_data.py", "utf8")).replace(/\r\n/g, "\n");
const nameSet = (key) => {
  const a = py.indexOf(key + " = {"), txt = py.slice(a, py.indexOf("}", a));
  return new Set([...txt.split("\n").map(l => l.replace(/#.*$/, "")).join("\n").matchAll(/"([^"]+)"/g)].map(m => m[1]));
};
const BARS = nameSet("BARS"), NO_LUNCH = nameSet("NO_LUNCH"), EXCLUDE = nameSet("EXCLUDE");
const CAT_FIX = JSON.parse(py.match(/^CAT_FIX = (\{.*\})$/m)[1]);
const NAME_FIX = JSON.parse(py.match(/^NAME_FIX = (\{.*\})$/m)[1]);
const CHECKED = py.match(/^CHECKED = "(.+)"$/m)[1];
const readJson = async (f, dflt) => { try { return JSON.parse(await fs.readFile(T + f, "utf8")); } catch (e) { if (dflt !== undefined) return dflt; throw e; } };

const rows = await readJson("all_rows.json");
const PLACE_IDS = await readJson("place_ids.json");
const MENUS = await readJson("menus.json");
const SID = await readJson("store_ids.json", {});
const ZP = await readJson("zeropay_merge.json", { both: [], rows: [] });
const ZP_BOTH = new Set(ZP.both);
const slug = (n) => "name-" + n.normalize("NFC").toLowerCase().replace(/[^0-9a-z가-힣]+/g, "-").replace(/^-+|-+$/g, "");

const out = [];
function finish(item, ids) {
  if (ids.kakao) item.kakaoId = ids.kakao;
  if (ids.naver) item.naverId = ids.naver;
  // 고정 id: 후기(store_id)가 여기에 붙으므로 한 번 정한 id는 store_ids.json에 저장해 두고 절대 바꾸지 않는다
  if (!SID[item.name]) SID[item.name] = item.kakaoId ? "kakao-" + item.kakaoId : item.naverId ? "naver-" + item.naverId : slug(item.name);
  item.id = SID[item.name];
  // 음식 분류(한식·중식 등, 검색용)도 menus.json에서 가져온다
  if (MENUS[item.id] && (MENUS[item.id].cuisine || []).length) item.cuisine = MENUS[item.id].cuisine;
  if (item.cat !== "편의점·마트") {
    const mm = MENUS[item.id];
    if (mm && mm.menu && mm.menu.length) { item.menu = mm.menu; item.menuSrc = mm.menuSrc; if (mm.menuNote) item.menuNote = mm.menuNote; }
    else { item.menu = []; item.menuNote = (mm && mm.menuNote) || "대표메뉴 미확인"; }
  }
  out.push(item);
}
for (const r of rows) {
  if (r.dist == null || r.dist > 600 || BARS.has(r.name) || NO_LUNCH.has(r.name) || EXCLUDE.has(r.name)) continue;
  const name = NAME_FIX[r.name] ?? r.name, cat = CAT_FIX[r.name] ?? r.cat;
  finish({ id: null, name, addr: r.addr, cat, src: r.src.split(",").map(s => s === "전체" ? "전체 가맹점" : "비플식권"),
    pay: ["비플식권", ...(ZP_BOTH.has(name) ? ["제로페이"] : [])], lat: r.lat, lon: r.lon, dist: r.dist, approx: r.acc === "근사" }, PLACE_IDS[name] || {});
}
for (const z of ZP.rows) {
  finish({ id: null, name: z.name, addr: z.addr, cat: z.cat, src: [], pay: ["제로페이"], lat: z.lat, lon: z.lon, dist: z.dist, approx: false, ...(z.check !== false ? { zpCheck: true } : {}) },
    { kakao: z.kakaoId, naver: z.naverId });
}
const dup = out.map(x => x.id).filter((v, i, a) => a.indexOf(v) !== i);
if (dup.length) throw new Error("id 중복: " + dup.join(", "));
const unknown = Object.keys(MENUS).filter(k => !k.startsWith("_") && !out.some(x => x.id === k));
if (unknown.length) console.warn("menus.json에 있지만 data.js에 없는 id:", unknown);
await fs.writeFile(T + "store_ids.json", JSON.stringify(SID, null, 1) + "\n", "utf8");

const sources = [{ name: "비플페이 앱 '전체 가맹점 사용처'·'비플식권 사용처' 화면", pay: "비플식권", checked: CHECKED }];
if (ZP.rows.length || ZP.both.length) sources.push({ name: "제로페이 가맹점 찾기", pay: "제로페이", url: ZP.source, checked: ZP.checked });
const meta = { origin: { name: "L.L.M Academy", addr: "광주 서구 상무중앙로 44", lat: 35.1508811, lon: 126.8489117 }, radius: 600, checked: CHECKED, sources };
let txt = "// 자동 생성 파일 (tools/build_data.py 또는 tools/build_data_port.mjs). 직접 고치지 말 것 — 메뉴는 tools/menus.json, 규칙은 tools/build_data.py\n"
  + "// 가게 목록 출처는 META.sources. 비플 목록 좌표는 OpenStreetMap Nominatim, 제로페이 가게 좌표는 카카오맵 기준\n"
  + "window.META = " + JSON.stringify(meta) + ";\n"
  + "window.STORES = " + JSON.stringify(out, null, 1) + ";\n";
await fs.writeFile(dir + "data.js", txt, "utf8");
const cnt = {}; out.forEach(x => cnt[x.cat] = (cnt[x.cat] || 0) + 1);
console.log({ total: out.length, cnt, zpBoth: out.filter(x => x.pay.length === 2).length, zpOnly: out.filter(x => x.pay[0] === "제로페이").length,
  withMenu: out.filter(x => x.menu && x.menu.length).length, noMenu: out.filter(x => x.menu && !x.menu.length).map(x => x.name) });
