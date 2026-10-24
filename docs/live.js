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
 el.innerHTML=`<div class="lhead"><div class="kicker">Live product</div><h1>Run the real pipeline on editable records</h1>
 <p class="lede">Three steps: the records go in, an LLM via the Mubit gateway extracts every medicine line, Banyan Sapling judges each medicine against each care chart, and the pharmacist gets a worklist.</p>
 <div class="status" id="lstat">Checking live server...</div></div>
 <section class="lstep"><div class="lnum">1</div><div class="lbody"><h2>Input documents</h2><p class="hint">The prescriber record and the care charts for one patient. Edit any line, or apply a preset, then run the check.</p>
 <div class="lbar"><div class="cases lcases" id="lcases">${["fisher","elliott","burgess"].map(k=>`<button data-lc="${k}" class="${k==liveCase?"on":""}">${CASES[k].name}</button>`).join("")}</div>
 <div class="presets ed">${(PRESETS[liveCase]||[]).map((p,i)=>`<button data-p="${i}">${p[0]}</button>`).join("")}<button data-p="reset">Reset</button></div></div>
 <div class="tagrid ed" style="grid-template-columns:repeat(${d.case.documents.length},1fr)">${d.case.documents.map((x,i)=>`<div class="tacard"><label><span class="role ${x.role=="care"?"care":"rx"}">${x.role=="care"?"Care chart":"Prescriber"}</span>${esc(x.label)}</label><textarea id="ta${i}" spellcheck="false">${esc(x.text)}</textarea></div>`).join("")}</div>
 <button class="btn primary" id="runbtn">Check records</button></div></section>
 <section class="lstep"><div class="lnum">2</div><div class="lbody"><h2>Pipeline running</h2><p class="hint">A: an LLM through the Mubit gateway extracts and normalises every medicine line (each call returns an mreq request ID). B: Sapling scores each medicine against each care chart; violation &ge; 0.4 is flagged.</p>
 <div class="phases"><div class="ph" id="ph1"><b>A</b><span>Extract via Mubit gateway</span><em id="ph1s">waiting</em></div><div class="ph" id="ph2"><b>B</b><span>Sapling judgement</span><em id="ph2s">waiting</em></div></div>
 <div class="log" id="log"><div>Ready. Press Check records.</div></div><div id="lmat" class="lmat"></div></div></section>
 <section class="lstep" id="ls3"><div class="lnum">3</div><div class="lbody"><h2>Pharmacist worklist</h2><p class="hint">Only the contradictions a pharmacist needs to resolve. Unflagged medicines are “no conflict found, not verified”, never “safe”.</p>
 <div class="lw" id="lwl"><div class="empty">Results appear here after the check.</div></div></div></section>`;
 document.querySelectorAll("textarea").forEach((t,i)=>t.oninput=()=>t.classList.toggle("changed",t.value!=orig[i]));
 ping()}
async function ping(){const s=document.getElementById("lstat");try{const r=await fetch(window.MEDMATCH_LIVE_URL+"/api/health",{cache:"no-store"});if(!r.ok)throw 0;s.className="status";s.innerHTML=`Live server online · LLM via Mubit gateway (api.mubit.ai) · Sapling on the Banyan HF endpoint`;return true}catch(e){s.className="status off";s.textContent="Live server offline, showing replay";return false}}
document.addEventListener("click",async e=>{const lc=e.target.closest("[data-lc]"),p=e.target.closest("[data-p]");
 if(lc){liveCase=lc.dataset.lc;liveInit()}
 if(p){const tas=[...document.querySelectorAll(".ed textarea")];let vals=p.dataset.p=="reset"?[...orig]:tas.map(t=>t.value);if(p.dataset.p!="reset")PRESETS[liveCase][+p.dataset.p][1](vals);tas.forEach((t,i)=>{t.value=vals[i];t.classList.toggle("changed",vals[i]!=orig[i])})}
 if(e.target.id=="runbtn")runLive()});
const ph=(n,t,st)=>{const e=document.getElementById('ph'+n);if(!e)return;e.className='ph '+(st||'');document.getElementById('ph'+n+'s').textContent=t};
const cleanL=s=>{s=s||'';const m=s.match(/original text: "([^"]*)"/);return m?m[1].replace(/\s*\|\s*/g,' · ').replace(/\s{2,}/g,' '):(s.includes(': ')?s.split(': ').slice(1).join(': '):s)};
const lg=(cls,t)=>{const l=document.getElementById("log");l.insertAdjacentHTML("beforeend",`<div class="${cls}">${esc(t)}</div>`);l.scrollTop=l.scrollHeight};
function cellHTML(v,ms,rule){const f=v>=.4;return `<div class="cell done ${f?"flag":""}"><div class="p">${v.toFixed(2)}</div><div class="bar"><i style="width:${Math.max(3,v*100)}%"></i></div><div class="meta">${(ms/1000).toFixed(1)} s</div>${rule?`<div class="rule in">Code rule: ${esc(rule.split(":")[0])}</div>`:""}</div>`}
function wlHTML(r){const fl=r.medicines.filter(m=>m.flag||m.comparisons.some(c=>c.flag)),gr=r.medicines.length-fl.length;
 return `<div class="wlsum"><b>${fl.length}</b> flagged for review · ${r.medicines.length} medicines checked · ${gr} no conflict found, not verified</div>`+fl.map(m=>m.comparisons.filter(c=>c.flag).map(c=>{const absent=/not on this chart/.test(c.rule||"");return `<div class="card fcard in"><h3>${esc(m.name)}<span class="score">${c.sapling_flag?"Sapling violation "+c.sapling.violation.toFixed(2):""}</span></h3><div class="why">${esc(c.doc)}${c.rule?" · "+esc(c.rule):""}</div>
 ${c.prescriber_line?`<div class="pair"><div class="q"><div class="from">Prescriber record</div><div class="t">${esc(cleanL(c.prescriber_line))}</div></div><div class="conn"></div><div class="q r"><div class="from">${esc(c.doc)}</div><div class="t">${absent||!c.care_line?"Not on this chart":esc(cleanL(c.care_line))}</div></div></div>`:""}
 <div class="flags">${c.sapling_flag?`<span class="f-s">Sapling ≥ 0.4</span>`:""}${c.rule?`<span class="f-r">Code rule: ${esc(c.rule.split(":")[0])}</span>`:""}</div></div>`}).join("")).join("")+(fl.length?"":`<div class="card fcard in" style="border-left-color:var(--grey)"><h3>No conflict found, not verified</h3></div>`)}
async function runLive(){const btn=document.getElementById("runbtn");btn.disabled=true;btn.textContent="Running...";document.getElementById("log").innerHTML="";document.getElementById("lwl").innerHTML=`<div class="empty">Running…</div>`;ph(1,"waiting");ph(2,"waiting");let nl=0,ns=0;
 const d=await load(liveCase);const docs=d.case.documents.map((x,i)=>({role:x.role,label:x.label,text:document.getElementById("ta"+i).value}));
 const care=docs.filter(x=>x.role=="care").map(x=>x.label);const rows={};const mat=document.getElementById("lmat");
 const draw=()=>{mat.innerHTML=`<table class="matrix"><tr><th>Medicine</th>${care.map(c=>`<th>${esc(c)}</th>`).join("")}</tr>${Object.keys(rows).map(n=>`<tr><td class="mn">${esc(n)}</td>${care.map(c=>rows[n][c]?`<td>${rows[n][c]}</td>`:`<td><div class="cell run"></div></td>`).join("")}</tr>`).join("")}</table>`};
 if(!(await ping())){lg("f","Live server offline, showing replay from cache");ph(1,"replay (cached)","done");const r=d.result;for(const m of r.medicines){rows[m.name]={};for(const c of m.comparisons){await new Promise(z=>setTimeout(z,600));rows[m.name][c.doc]=cellHTML(c.sapling.violation,c.sapling.model_ms||0,c.rule);lg(c.flag?"f":"s",`Replay · Sapling: ${m.name} x ${c.doc}, violation ${c.sapling.violation.toFixed(2)}`);ph(2,`${++ns} calls (replay)`,"run");draw()}}ph(2,`${ns} calls (replay)`,"done");document.getElementById("lwl").innerHTML=wlHTML(d.result);btn.disabled=false;btn.textContent="Check records";return}
 lg("","POST /api/check · sending "+docs.length+" documents");const t0=performance.now();
 try{const res=await fetch(window.MEDMATCH_LIVE_URL+"/api/check",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({case_id:liveCase,documents:docs})});
 const rd=res.body.getReader(),dec=new TextDecoder();let buf="";
 for(;;){const {value,done}=await rd.read();if(done)break;buf+=dec.decode(value,{stream:true});let i;while((i=buf.indexOf("\n"))>=0){const line=buf.slice(0,i).trim();buf=buf.slice(i+1);if(!line)continue;const ev=JSON.parse(line);
  if(ev.type=="llm"){ph(1,`${++nl} call${nl>1?"s":""} · ${ev.mubit_request_id}`,"run");lg("m",`Mubit gateway · ${ev.model} · ${ev.mubit_request_id} · ${(ev.latency_ms/1000).toFixed(1)} s · ${ev.doc}: ${ev.lines.length} lines`);ev.lines.forEach(l=>{if(!rows[l.canonical_name])rows[l.canonical_name]={}});draw()}
  if(ev.type=="sapling"){ph(1,`${nl} calls done`,"done");ph(2,`${++ns} calls`,"run");(rows[ev.name]=rows[ev.name]||{})[ev.doc]=cellHTML(ev.violation,ev.wall_ms,ev.rule);lg(ev.flag?"f":"s",`Sapling · ${ev.name} x ${ev.doc} · violation ${ev.violation.toFixed(2)} · ${(ev.wall_ms/1000).toFixed(1)} s${ev.rule?" · code rule: "+ev.rule.split(":")[0]:""}`);draw()}
  if(ev.type=="error")lg("f","Error: "+ev.message);
  if(ev.type=="done"){const r=ev.result;const fl=r.medicines.filter(m=>m.flag);lg("s",`Done in ${((performance.now()-t0)/1000).toFixed(1)} s · ${r.medicines.length} medicines · ${fl.length} flagged`);
   ph(2,`${ns} calls done`,"done");document.getElementById("lwl").innerHTML=wlHTML(r);setTimeout(()=>document.getElementById("ls3").scrollIntoView({behavior:"smooth",block:"start"}),300)}}}
 }catch(e){lg("f","Stream failed: "+e)}
 btn.disabled=false;btn.textContent="Check records"}
document.body.dataset.tab="landing";setTab("landing");
