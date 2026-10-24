const LANDING=[
 {t:'In 2026 a coroner wrote: “no system in place to cross check”.',s:'Fisher, Prevention of Future Deaths report 2026-0166',u:'https://www.judiciary.uk/prevention-of-future-death-reports/john-fisher-prevention-of-future-deaths-report/'},
 {t:'273 coroner reports flag unreliable hospital discharge.',s:'PFD Monitor, recurring concern (2013 to Jun 2026)',u:'https://pfdmonitor.org/concerns/recurring-concern-ba5e203f1b24ff50a1bd80b9/'},
 {t:'Only 66% of NHS discharge medicine checks were completed in August 2026.',s:'NHSBSA, Discharge Medicines Service data',u:'https://www.nhsbsa.nhs.uk/prescription-data/dispensing-data/nhs-discharge-medicines-service'},
 {t:'Medicines get stopped, swapped and dropped between care settings, and nobody checks the charts against each other.',s:'',u:''}];
let tab="landing",typed=false;
function setTab(t){tab=t;document.body.dataset.tab=t;document.querySelectorAll("[data-t]").forEach(b=>b.classList.toggle("on",b.dataset.t==t));if(t=="landing")landing();if(t=="live")liveInit();if(t=="story")render()}
document.addEventListener("click",e=>{const b=e.target.closest("[data-t]");if(b)setTab(b.dataset.t)});
async function landing(){const el=document.getElementById("landing");if(typed)return;typed=true;
 el.innerHTML=LANDING.map((x,i)=>`<p class="tw" id="tw${i}"></p><p class="src" id="sr${i}">${x.u?`Source: <a href="${x.u}" target="_blank">${x.s}</a>`:""}</p>`).join("")+`<div class="ctas" id="ctas"><button class="btn primary" data-t="story">See the journey</button><button class="btn ghost" data-t="live">Try it live</button></div>`;
 for(let i=0;i<LANDING.length;i++){const p=document.getElementById("tw"+i);p.classList.add("cur");for(const ch of LANDING[i].t){p.textContent+=ch;await new Promise(r=>setTimeout(r,28))}p.classList.remove("cur");document.getElementById("sr"+i).classList.add("in");await new Promise(r=>setTimeout(r,500))}
 document.getElementById("ctas").classList.add("in")}
let liveCase="fisher",orig=[];
const PRESETS={fisher:[["Add valproate to the agency eMAR",d=>{d[2]=d[2].replace("(no further medicines recorded)","05  Sodium valproate 200mg/5ml  10ml  Morning, Tea  liquid\n(no further medicines recorded)")}],["Remove phenobarbital from the handwritten chart",d=>{d[1]=d[1].split("\n").filter(l=>!/Phenobarbital/i.test(l)).join("\n")}]],
 burgess:[["Change brivaracetam to 4 ml on the chart so it matches",d=>{d[1]=d[1].replace(/10 ml(\s+BD)/,"4 ml$1")}],["Remove omeprazole from the chart",d=>{d[1]=d[1].split("\n").filter(l=>!/Omeprazole/i.test(l)).join("\n")}]],
 elliott:[["Remove Oramorph from the care home eMAR",d=>{d[2]=d[2].split("\n").filter(l=>!/Oramorph/i.test(l)).join("\n")}]]};
async function liveInit(){const el=document.getElementById("live");const d=await load(liveCase);orig=d.case.documents.map(x=>x.text);
 el.innerHTML=`<div class="kicker">Live product</div><h1>Run the real pipeline on editable records</h1>
 <div class="status" id="lstat">Checking live server...</div>
 <div class="lgrid"><div class="ed"><div class="cases lcases" id="lcases" style="margin:0 0 8px">${["fisher","elliott","burgess"].map(k=>`<button data-lc="${k}" class="${k==liveCase?"on":""}">${CASES[k].name}</button>`).join("")}</div>
 <div class="presets">${(PRESETS[liveCase]||[]).map((p,i)=>`<button data-p="${i}">${p[0]}</button>`).join("")}<button data-p="reset">Reset</button></div>
 ${d.case.documents.map((x,i)=>`<label>${esc(x.label)} (${x.role=="care"?"care chart":"prescriber"})</label><textarea id="ta${i}" spellcheck="false">${esc(x.text)}</textarea>`).join("")}
 <button class="btn primary" id="runbtn" style="margin-top:12px;width:100%">Check records</button></div>
 <div><div class="log" id="log"><div>Ready. Press Check records.</div></div><div id="lmat"></div><div class="lw" id="lwl"></div></div></div>`;
 document.querySelectorAll("textarea").forEach((t,i)=>t.oninput=()=>t.classList.toggle("changed",t.value!=orig[i]));
 ping()}
async function ping(){const s=document.getElementById("lstat");try{const r=await fetch(window.MEDMATCH_LIVE_URL+"/api/health",{cache:"no-store"});if(!r.ok)throw 0;s.className="status";s.innerHTML=`Live server online · LLM via Mubit gateway (api.mubit.ai) · Sapling on the Banyan HF endpoint`;return true}catch(e){s.className="status off";s.textContent="Live server offline, showing replay";return false}}
document.addEventListener("click",async e=>{const lc=e.target.closest("[data-lc]"),p=e.target.closest("[data-p]");
 if(lc){liveCase=lc.dataset.lc;liveInit()}
 if(p){const tas=[...document.querySelectorAll(".ed textarea")];let vals=p.dataset.p=="reset"?[...orig]:tas.map(t=>t.value);if(p.dataset.p!="reset")PRESETS[liveCase][+p.dataset.p][1](vals);tas.forEach((t,i)=>{t.value=vals[i];t.classList.toggle("changed",vals[i]!=orig[i])})}
 if(e.target.id=="runbtn")runLive()});
const lg=(cls,t)=>{const l=document.getElementById("log");l.insertAdjacentHTML("beforeend",`<div class="${cls}">${esc(t)}</div>`);l.scrollTop=l.scrollHeight};
function cellHTML(v,ms,rule){const f=v>=.4;return `<div class="cell done ${f?"flag":""}"><div class="p">${v.toFixed(2)}</div><div class="bar"><i style="width:${Math.max(3,v*100)}%"></i></div><div class="meta">${(ms/1000).toFixed(1)} s</div>${rule?`<div class="rule in">Code rule: ${esc(rule.split(":")[0])}</div>`:""}</div>`}
async function runLive(){const btn=document.getElementById("runbtn");btn.disabled=true;btn.textContent="Running...";document.getElementById("log").innerHTML="";document.getElementById("lwl").innerHTML="";
 const d=await load(liveCase);const docs=d.case.documents.map((x,i)=>({role:x.role,label:x.label,text:document.getElementById("ta"+i).value}));
 const care=docs.filter(x=>x.role=="care").map(x=>x.label);const rows={};const mat=document.getElementById("lmat");
 const draw=()=>{mat.innerHTML=`<table class="matrix"><tr><th>Medicine</th>${care.map(c=>`<th>${esc(c)}</th>`).join("")}</tr>${Object.keys(rows).map(n=>`<tr><td class="mn">${esc(n)}</td>${care.map(c=>rows[n][c]?`<td>${rows[n][c]}</td>`:`<td><div class="cell run"></div></td>`).join("")}</tr>`).join("")}</table>`};
 if(!(await ping())){lg("f","Live server offline, showing replay from cache");const r=d.result;for(const m of r.medicines){rows[m.name]={};for(const c of m.comparisons){await new Promise(z=>setTimeout(z,600));rows[m.name][c.doc]=cellHTML(c.sapling.violation,c.sapling.model_ms||0,c.rule);lg(c.flag?"f":"s",`Replay · Sapling: ${m.name} x ${c.doc}, violation ${c.sapling.violation.toFixed(2)}`);draw()}}btn.disabled=false;btn.textContent="Check records";return}
 lg("","POST /api/check · sending "+docs.length+" documents");const t0=performance.now();
 try{const res=await fetch(window.MEDMATCH_LIVE_URL+"/api/check",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({case_id:liveCase,documents:docs})});
 const rd=res.body.getReader(),dec=new TextDecoder();let buf="";
 for(;;){const {value,done}=await rd.read();if(done)break;buf+=dec.decode(value,{stream:true});let i;while((i=buf.indexOf("\n"))>=0){const line=buf.slice(0,i).trim();buf=buf.slice(i+1);if(!line)continue;const ev=JSON.parse(line);
  if(ev.type=="llm"){lg("m",`Mubit gateway · ${ev.model} · ${ev.mubit_request_id} · ${(ev.latency_ms/1000).toFixed(1)} s · ${ev.doc}: ${ev.lines.length} lines`);ev.lines.forEach(l=>{if(!rows[l.canonical_name])rows[l.canonical_name]={}});draw()}
  if(ev.type=="sapling"){(rows[ev.name]=rows[ev.name]||{})[ev.doc]=cellHTML(ev.violation,ev.wall_ms,ev.rule);lg(ev.flag?"f":"s",`Sapling · ${ev.name} x ${ev.doc} · violation ${ev.violation.toFixed(2)} · ${(ev.wall_ms/1000).toFixed(1)} s${ev.rule?" · code rule: "+ev.rule.split(":")[0]:""}`);draw()}
  if(ev.type=="error")lg("f","Error: "+ev.message);
  if(ev.type=="done"){const r=ev.result;const fl=r.medicines.filter(m=>m.flag);lg("s",`Done in ${((performance.now()-t0)/1000).toFixed(1)} s · ${r.medicines.length} medicines · ${fl.length} flagged`);
   document.getElementById("lwl").innerHTML=`<h3 style="margin:16px 0 8px;font-size:16px">Worklist: ${fl.length} flagged</h3>`+fl.map(m=>m.comparisons.filter(c=>c.flag).map(c=>`<div class="card fcard"><h3>${esc(m.name)}<span class="score">${c.sapling_flag?"Sapling "+c.sapling.violation.toFixed(2):""}${c.rule?" · Code rule: "+esc(c.rule.split(":")[0]):""}</span></h3><div class="why">${esc(c.doc)}</div></div>`).join("")).join("")+(fl.length?"":`<div class="card fcard" style="border-left-color:var(--grey)"><h3>No conflict found, not verified</h3></div>`)}}}
 }catch(e){lg("f","Stream failed: "+e)}
 btn.disabled=false;btn.textContent="Check records"}
document.body.dataset.tab="landing";setTab("landing");
