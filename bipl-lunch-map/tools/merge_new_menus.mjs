// menus_5~8.json(새 가게)을 tools/menus.json에 추가. 기존 40곳 항목은 건드리지 않는다
const fs = await import("node:fs");
const T = "D:/SEONA2/bipl-lunch-map/tools/";
const menus = JSON.parse(fs.readFileSync(T+"menus.json","utf8"));
const TAGS = new Set(["국물","면","밥","고기","튀김","분식","매움","가벼움","커피","논커피","달달함"]);
const KINDS = new Set(["meal","drink","dessert"]);
const errs = [], added = [], missing = [], report = [];
for (const i of [5,6,7,8]) {
  const targets = JSON.parse(fs.readFileSync(T+`menus_parts/targets_${i}.json`,"utf8"));
  let part = {}; try { part = JSON.parse(fs.readFileSync(T+`menus_parts/menus_${i}.json`,"utf8")); } catch { errs.push(`menus_${i}.json 없음`); }
  for (const t of targets) {
    const v = part[t.id]; if (!v) { missing.push(t.name); continue; }
    const reps = v.menu.filter(m=>m.rep).length;
    if (v.menu.length && !((reps>=2&&reps<=3) || (v.menu.length<=2 && reps===v.menu.length))) errs.push(`${t.name} rep ${reps}/${v.menu.length}`);
    for (const m of v.menu) {
      if (!KINDS.has(m.kind)) errs.push(`${t.name} kind ${m.kind}`);
      if ((m.tags||[]).some(x=>!TAGS.has(x)) || (m.tags||[]).length>3) errs.push(`${t.name} tags ${m.tags}`);
      if (m.price!==null && !Number.isInteger(m.price)) errs.push(`${t.name} price ${m.price}`);
    }
    const o = {name: t.name, menu: v.menu.map(m=>({name:m.name, price:m.price, kind:m.kind, tags:m.tags||[], rep:!!m.rep})), menuSrc: v.menuSrc};
    const n = v.note || "";
    if (/1마리 단위/.test(n)) o.menuNote = "1마리 단위 메뉴예요";
    else if (/주문|배달|포장/.test(n) && /다를 수/.test(n)) o.menuNote = "주문(포장·배달) 화면 기준 가격이라 매장 가격과 다를 수 있어요";
    if (n) o.note = n;
    if (v.noMenuPage) o.noMenuPage = true;
    menus[t.id] = o; added.push(t.id);
    report.push([t.cat, t.name, v.menu.length, v.menu.filter(m=>m.price==null).map(m=>m.name), v.menuSrc?.label||"-", !!v.noMenuPage, o.menuNote||""]);
  }
}
console.log(JSON.stringify({added: added.length, missing, errs}));
if (!errs.length || process.argv.includes("--force")) fs.writeFileSync(T+"menus.json", JSON.stringify(menus,null,1)+"\n");
fs.writeFileSync(process.env.TEMP+"/new_menu_report.json", JSON.stringify(report,null,1));
