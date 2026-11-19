// 2026-11-19: 제로페이 새 가게 64곳 메뉴(picked_from_raw.json + picked_browse.json)를 menus.json에 합친다. 기존 항목은 건드리지 않는다
// 실행: ego-browser nodejs -e 'await import("file:///D:/SEONA2/bipl-lunch-map/tools/merge_picked_menus.mjs")'
const fs = await import("node:fs");
const T = "D:/SEONA2/bipl-lunch-map/tools/", P = T + "menus_parts/";
const menus = JSON.parse(fs.readFileSync(T + "menus.json", "utf8"));
const targets = [5,6,7,8].flatMap(i => JSON.parse(fs.readFileSync(P + `targets_${i}.json`, "utf8")));
const picks = { ...JSON.parse(fs.readFileSync(P + "picked_from_raw.json", "utf8")), ...JSON.parse(fs.readFileSync(P + "picked_browse.json", "utf8")) };
// 원본 글자 전체 (출처 판단용)
const rawText = {};
for (const d of fs.readdirSync(P).filter(d => /^raw_\d$/.test(d))) for (const f of fs.readdirSync(P + d).filter(f => f.endsWith(".json"))) {
  const j = JSON.parse(fs.readFileSync(P + d + "/" + f, "utf8"));
  for (const [k, v] of Object.entries(j)) { const t = targets.find(t => k === t.id || k.endsWith(t.id)); if (t) rawText[t.id] = (rawText[t.id] || "") + JSON.stringify(v); }
}
const TAGS = new Set(["국물","면","밥","고기","튀김","분식","매움","가벼움","커피","논커피","달달함"]), KINDS = new Set(["meal","drink","dessert"]);
const errs = [], report = [];
for (const t of targets) {
  const p = picks[t.id]; if (!p) { errs.push("빠짐 " + t.name); continue; }
  const menu = p.menu.map(([name, price, kind, tags, rep]) => ({ name, price, kind, tags, rep }));
  const reps = menu.filter(m => m.rep).length;
  if (menu.length && !((reps >= 2 && reps <= 3) || (menu.length <= 2 && reps === menu.length))) errs.push(`${t.name} rep ${reps}/${menu.length}`);
  for (const m of menu) { if (!KINDS.has(m.kind)) errs.push(`${t.name} kind`); if (m.tags.some(x => !TAGS.has(x)) || m.tags.length > 3) errs.push(`${t.name} tags ${m.tags}`); if (m.price !== null && !Number.isInteger(m.price)) errs.push(`${t.name} price`); }
  // 출처: 네이버 페이지 원본이면 네이버, 아니면 카카오맵
  let src = p.src;
  if (!src) src = /m\.place\.naver\.com\/(?:restaurant|place|cafe)\/\d+/.test(rawText[t.id] || "") ? "naver" : "kakao";
  const nid = t.naverId || ((rawText[t.id] || "").match(/m\.place\.naver\.com\/(?:restaurant|place|cafe)\/(\d+)/) || [])[1];
  const menuSrc = src === "naver" && nid
    ? { url: `https://map.naver.com/p/entry/place/${nid}`, label: "네이버 지도 매장 메뉴", checked: "2026-11-19" }
    : { url: `https://place.map.kakao.com/${t.kakaoId}`, label: "카카오맵 매장 메뉴", checked: "2026-11-19" };
  const o = { name: t.name, menu, menuSrc };
  if (p.menuNote) o.menuNote = p.menuNote;
  else if (/1마리 단위/.test(p.note || "")) o.menuNote = "1마리 단위 메뉴예요";
  else if (/주문\(배달\) 화면 기준/.test(p.note || "")) o.menuNote = "주문(포장·배달) 화면 기준 가격일 수 있어요";
  if (p.note) o.note = p.note;
  if (p.noMenuPage) o.noMenuPage = true;
  menus[t.id] = o;
  report.push({ cat: t.cat, name: t.name, n: menu.length, nulls: menu.filter(m => m.price == null).map(m => m.name), src: menuSrc.label.startsWith("네이버") ? "네이버" : "카카오", noMenuPage: !!p.noMenuPage, empty: !menu.length });
}
console.log(JSON.stringify({ errs, count: report.length }));
if (!errs.length) fs.writeFileSync(T + "menus.json", JSON.stringify(menus, null, 1) + "\n");
fs.writeFileSync(P + "report_new_64.json", JSON.stringify(report, null, 1) + "\n");
