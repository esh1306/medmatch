const CASES={
 fisher:{name:"Fisher",ref:"PFD 2026-0166",pt:["J. Fisher (synthetic)","DOB xx/xx/1950","Epilepsy"],
  stops:[{doc:0,date:"8 Apr 2025",place:"GP surgery",what:"GP stops phenobarbital. Existing list still has sodium valproate."},
         {doc:1,date:"9 to 15 Apr 2025",place:"Community response team",what:"Handwritten chart still gives phenobarbital twice a day.",bad:1},
         {doc:2,date:"15 Apr 2025",place:"Home care agency",what:"eMAR set up without sodium valproate. Six days of missed doses.",bad:1}],
  outcome:"Mr Fisher died in May 2025. The coroner found there was no system in place to cross check the records.",
  quote:"There was no system in place to cross check."},
 elliott:{name:"Elliott",ref:"PFD 2025-0515",pt:["T. Elliott (synthetic)","DOB xx/xx/1941","Chronic kidney disease"],
  stops:[{doc:0,date:"Before admission",place:"GP surgery",what:"Repeat list includes Oramorph (morphine sulfate)."},
         {doc:1,date:"Hospital discharge",place:"Hospital ward",what:"Oramorph switched to oxycodone because of his kidneys."},
         {doc:2,date:"After discharge",place:"Care home",what:"Oxycodone added as new medication; Oramorph not removed.",bad:1}],
  outcome:"The coroner reported that oxycodone was added as new and additional medication, not replacement medication.",
  quote:"Incorrectly added to the record as new and additional medication - not replacement medication."},
 burgess:{name:"Burgess",ref:"PFD 2024-0077",pt:["M. Burgess (synthetic)","DOB xx/xx/19xx","Epilepsy"],
  stops:[{doc:0,date:"July 2022",place:"Neurology and GP",what:"Brivaracetam 4 ml twice daily, confirmed by neurology."},
         {doc:1,date:"26 Jul 2022",place:"Care home",what:"10 ml twice daily started after a 111 call.",bad:1}],
  outcome:"The care provider's response records that 4 ml was the correct dose while 10 ml twice daily was being given.",
  quote:"The appropriate dose of Brivaracetam was 4ml twice daily."}
};
const STEPS=["Journey","Documents","Extract","Normalise","Check","Rule check","Worklist"];
let cur="fisher",step=0,D={},timers=[],playing=false,playT=null;
const $=s=>document.querySelector(s),stage=$("#stage");
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const later=(f,ms)=>timers.push(setTimeout(f,ms));
function clear(){timers.forEach(clearTimeout);timers=[]}
async function load(c){if(!D[c])D[c]=await (await fetch(`data/${c}.json`)).json();return D[c]}
function nav(){
 $("#cases").innerHTML=Object.keys(CASES).map(k=>`<button data-c="${k}" class="${k==cur?"on":""}">${CASES[k].name}</button>`).join("");
 $("#progress").innerHTML=STEPS.map((s,i)=>`<button class="st ${i<step?"done":i==step?"on":""}" data-s="${i}"><b>${String(i+1).padStart(2,"0")}</b>${s}<i></i></button>`).join("");
 $("#play").textContent=playing?"Pause":"Play";
}
document.addEventListener("click",e=>{const c=e.target.closest("[data-c]"),s=e.target.closest("[data-s]");
 if(c){cur=c.dataset.c;step=0;render()} if(s){step=+s.dataset.s;render()}});
$("#next").onclick=()=>{if(step<STEPS.length-1){step++;render()}else{const ks=Object.keys(CASES);cur=ks[(ks.indexOf(cur)+1)%ks.length];step=0;render()}};
$("#prev").onclick=()=>{if(step>0){step--;render()}};
$("#play").onclick=()=>{playing=!playing;nav();if(playing)schedule();else clearTimeout(playT)};
document.addEventListener("keydown",e=>{if(e.key=="ArrowRight")$("#next").click();if(e.key=="ArrowLeft")$("#prev").click();if(e.key==" "){e.preventDefault();$("#play").click()}});
const DWELL=[7000,6000,9000,8000,0,6000,14000];
function schedule(){clearTimeout(playT);if(!playing)return;let ms=DWELL[step]||checkDur+2500;
 if(step==STEPS.length-1){playing=false;nav();return}
 playT=setTimeout(()=>{step++;render()},ms)}
let checkDur=10000;
function docKind(label){return /handwritten/i.test(label)?"hand":/emar/i.test(label)?"emar":/discharge/i.test(label)?"letter":/MAR/.test(label)?"mar":"list"}
const ORG={list:["Riverside Medical Practice","Repeat medicines summary"],letter:["General Hospital, Ward 7","Discharge summary"],hand:["Community Response Team","Medication administration record"],emar:["HomeCare Services","Electronic MAR"],mar:["Oak Lodge Care Home","Medication administration record"]};
function lines(d,label){return (d.result.normalised_lines[label]||[])}
function paper(d,i,{mini=false,rot=0}={}){const doc=d.case.documents[i],k=docKind(doc.label),[org,sub]=ORG[k],C=CASES[cur];
 const L=lines(d,doc.label);let body;
 if(k=="hand"){body=`<table class="hand"><tr><th>Medicine</th><th>Dose</th><th>Given</th></tr>${L.map((l,j)=>`<tr class="ln" data-l="${i}-${j}"><td>${esc(l.original.split("|")[0])}</td><td>${esc(l.dose||"")}</td><td class="ticks">${l.status=="not given"?"–":"✓✓✓✓✓✓"}</td></tr>`).join("")}</table>`}
 else if(k=="emar"||k=="mar"){const days=["M","T","W","T","F","S","S"];body=`<table class="emar"><tr><th>Medicine</th><th>Dose / freq</th>${days.map(x=>`<th style="text-align:center">${x}</th>`).join("")}</tr>${L.map((l,j)=>`<tr class="ln" data-l="${i}-${j}"><td>${esc(l.generic_name? l.original.split(/\s{2,}|\|/)[0]:l.original)}</td><td>${esc((l.dose||"")+" "+(l.frequency||""))}</td>${days.map((x,n)=>`<td class="g ${n>4?"x":""}">${n>4?"·":"✓"}</td>`).join("")}</tr>`).join("")}</table>`}
 else{body=`<table><tr><th>Medicine and instructions</th><th>Status</th></tr>${L.map((l,j)=>`<tr class="ln" data-l="${i}-${j}"><td class="${l.status=="stopped"?"stopped":""}">${esc(l.original.replace(/^[-•]\s*/,""))}</td><td><span class="chip">${esc(l.status)}</span></td></tr>`).join("")}</table>`}
 return `<div class="paper ${mini?"mini":""} ${k=="hand"?"handbg":""}" style="--rot:${rot}deg" data-doc="${i}">
  <div class="lh"><div><div class="org">${org}</div><div class="sub">${sub}</div></div><div class="sub" style="text-align:right">${esc(doc.label)}</div></div>
  <div class="pt"><span>Patient</span><span>Born</span><span>Condition</span><b>${C.pt[0]}</b><b>${C.pt[1]}</b><b>${C.pt[2]}</b></div>
  ${body}<div class="stamp">SYNTHETIC, reconstructed from coroner report ${C.ref}</div></div>`}
function head(k,h,l){return `<div class="kicker">${k}</div><h1>${h}</h1><p class="lede">${l}</p>`}
async function render(){clear();nav();const d=await load(cur),C=CASES[cur],r=d.result;const docs=d.case.documents;
 const S=[journey,documents,extract,normalise,check,rules,worklist][step];stage.innerHTML=`<div class="scene">${S(d,C,r,docs)}</div>`;post[step]&&post[step](d,C,r,docs);schedule()}
function journey(d,C,r,docs){return head(`Case ${C.name} · ${C.ref}`,"One patient, several care settings, several medicine records","Each handover produces a new medicines record. Nobody checks the new one against the last prescriber instruction.")+
 `<div class="journey"><div class="jline"><i id="jl"></i></div><div class="stops" style="grid-template-columns:repeat(${C.stops.length},1fr)">${C.stops.map((s,i)=>`<div class="stop ${s.bad?"bad":""}" id="st${i}"><div class="dot"></div><div class="date">${s.date}</div><div class="place">${s.place}</div><div class="what">${s.what}</div><div class="thumb">${paper(d,s.doc,{mini:true})}</div></div>`).join("")}</div>
 <div class="card outcome" id="oc"><span class="tag">Outcome</span><span>${C.outcome}</span></div></div>`}
const post={0:(d,C)=>{later(()=>$("#jl").style.width="100%",100);C.stops.forEach((s,i)=>later(()=>$("#st"+i).classList.add("in"),200+i*900));later(()=>$("#oc").classList.add("in"),400+C.stops.length*900)},
 1:(d,C,r,docs)=>{docs.forEach((x,i)=>later(()=>document.querySelector(`[data-doc="${i}"]`).classList.add("in"),150+i*450))},
 2:(d,C,r,docs)=>{document.querySelectorAll(".paper").forEach(p=>p.classList.add("in"));let t=300;const items=[...document.querySelectorAll(".sitem")];
   items.forEach((it,n)=>{const row=document.querySelector(`tr[data-l="${it.dataset.l}"]`);later(()=>{document.querySelectorAll("tr.hl").forEach(x=>x.classList.remove("hl"));row&&row.classList.add("hl");it.classList.add("in");const sl=$(".slist");sl.scrollTop=sl.scrollHeight},t);t+=Math.min(450,7000/items.length)});later(()=>document.querySelectorAll("tr.hl").forEach(x=>x.classList.remove("hl")),t+400)},
 3:()=>{document.querySelectorAll(".map").forEach((m,i)=>later(()=>m.classList.add("in"),200+i*700))},
 4:(d,C,r)=>runMatrix(r,false),5:(d,C,r)=>runMatrix(r,true),
 6:()=>{document.querySelectorAll(".fcard").forEach((m,i)=>later(()=>m.classList.add("in"),200+i*700));later(()=>$(".quote").classList.add("in"),400+document.querySelectorAll(".fcard").length*700)}};
function documents(d,C,r,docs){return head("The documents","What each setting actually wrote down","Three formats, three teams: a printed GP list, a handwritten chart and an electronic MAR. Same medicines, different words.".replace("Three formats, three teams",docs.length==2?"Two formats, two teams":"Three formats, three teams"))+
 `<div class="docs" style="grid-template-columns:repeat(${docs.length},1fr)">${docs.map((x,i)=>paper(d,i,{rot:[-.6,.4,-.3][i]})).join("")}</div>`}
function extract(d,C,r,docs){const n=r.normalisation;const items=[];docs.forEach((doc,i)=>lines(d,doc.label).forEach((l,j)=>items.push({i,j,l,doc})));
 return head("Step A · Extract","Every medicine line becomes structured data","An LLM reads each document and returns name, strength, dose, frequency and status for every line. Calls go through the Mubit gateway.")+
 `<div class="split compact"><div class="docs" style="grid-template-columns:repeat(${Math.min(docs.length,2)},1fr)">${docs.slice(0,2).map((x,i)=>paper(d,i)).join("")}${docs.length>2?`<div style="grid-column:span 2">${paper(d,2)}</div>`:""}</div>
 <div><div class="badge"><span class="live"></span>LLM via Mubit gateway · ${esc(n[0].model)} · <code>${esc(n[0].mubit_request_id)}</code></div>
 <div class="slist">${items.map(x=>`<div class="card sitem" data-l="${x.i}-${x.j}"><span class="src">${esc(x.doc.label)}</span><span><span class="nm">${esc(x.l.generic_name)}</span> <span class="dz">${esc([x.l.strength&&x.l.strength+" "+(x.l.strength_unit||""),x.l.dose,x.l.frequency].filter(Boolean).join(" · "))}</span></span><span class="st-pill ${esc(x.l.status)}">${esc(x.l.status)}</span></div>`).join("")}</div></div></div>`}
function normalise(d,C,r,docs){const seen=new Set(),maps=[];
 docs.forEach(doc=>lines(d,doc.label).forEach(l=>{const o=l.original.replace(/^[-•]\s*/,"").split(/\||\s{3,}/)[0].trim();const key=l.canonical_name+o;if(seen.has(key))return;seen.add(key);
  const changed=!o.toLowerCase().includes(l.canonical_name.split(" ")[0])||/\b(bd|od|tds|qds|on|prn|iu|1g)\b/i.test(l.original);maps.push({o:l.original.replace(/^[-•]\s*/,"").replace(/\s{2,}|\|/g," ").replace(/\s+/g," ").trim(),c:l.canonical_text,doc:doc.label,changed})}));
 maps.sort((a,b)=>b.changed-a.changed);const show=maps.slice(0,7);
 return head("Step B · Normalise","Different words, same medicine","Brand names, abbreviations and units are mapped to one canonical form before anything is compared, so “Vit D3 800iu” and “colecalciferol 800 units” are not a conflict. Backed by a synonym table citing RxNorm, openFDA and NHS dm+d.")+
 `<div class="maps">${show.map(m=>`<div class="map"><div class="card a">${esc(m.o)}</div><div class="arrow"><i></i></div><div class="card b">${esc(m.c)}<small>${esc(m.doc)}</small></div></div>`).join("")}</div>
 <p class="mapnote">Regression check, run live: Vit D3 vs cholecalciferol 0.09, acetaminophen vs paracetamol 0.13, Adcal-D3 vs calcium carbonate + colecalciferol 0.07, b.d. vs twice daily 0.07, 1 g vs 1000 mg 0.10. None flagged.</p>`}
function matrixHTML(r,rules){const docs=[...new Set(r.medicines.flatMap(m=>m.comparisons.map(c=>c.doc)))];const n=r.medicines.reduce((a,m)=>a+m.comparisons.length,0);
 return `<div class="legend"><span><i style="background:var(--red)"></i>Violation &ge; 0.4, flagged</span><span><i style="background:var(--grey)"></i>Below 0.4, not verified</span>${rules?`<span><i style="background:var(--amber-soft);border:1px solid #ecd6ad"></i>Code rule (not Sapling)</span>`:""}<span style="margin-left:auto" class="counter" id="cnt">0 of ${n} Sapling calls</span></div>
 <table class="matrix"><tr><th>Medicine</th>${docs.map(x=>`<th>${esc(x)}</th>`).join("")}</tr>${r.medicines.map((m,i)=>`<tr><td class="mn">${esc(m.name)}<small>${m.currently_prescribed?"currently prescribed":"not currently prescribed"}</small></td>${docs.map(dc=>{const c=m.comparisons.find(x=>x.doc==dc);if(!c)return`<td><div class="cell na">not compared</div></td>`;const v=c.sapling.violation;
  return `<td><div class="cell" data-v="${v}" data-ms="${Math.round(c.sapling.model_ms||0)}"><div class="p">${v.toFixed(2)}</div><div class="bar"><i></i></div><div class="meta">${esc(c.sapling.status)} · ${Math.round(c.sapling.model_ms||0)} ms</div>${c.rule?`<div class="rule">Code rule: ${esc(c.rule.split(":")[0])}</div>`:""}</div></td>`}).join("")}</tr>`).join("")}</table>`}
function check(d,C,r){return head("Step C · Check with Banyan Sapling","Every medicine against every care record","For each pair, Sapling judges the care line against the current prescription under one policy: stopped means stopped, replacements replace, doses match, nothing goes missing. Real cached outputs, replayed.")+matrixHTML(r,false)}
function rules(d,C,r){return head("Step D · Rule check","Missing and extra, checked in code","A simple, labelled code rule marks medicines that are prescribed but absent from a chart, or on a chart but no longer prescribed. It sits alongside Sapling, never instead of it.")+matrixHTML(r,true)}
function runMatrix(r,rulesMode){const cells=[...document.querySelectorAll(".cell:not(.na)")];const gap=rulesMode?0:Math.min(1500,12000/cells.length);checkDur=gap*cells.length+800;
 cells.forEach((c,i)=>{const fill=()=>{c.classList.remove("run");c.classList.add("done");const v=+c.dataset.v;if(v>=.4)c.classList.add("flag");c.querySelector(".bar i").style.width=Math.max(3,v*100)+"%";$("#cnt").textContent=`${i+1} of ${cells.length} Sapling calls`};
  if(rulesMode){fill()}else{later(()=>c.classList.add("run"),i*gap);later(fill,i*gap+Math.min(gap*.8,900))}});
 if(rulesMode)document.querySelectorAll(".rule").forEach((x,i)=>later(()=>x.classList.add("in"),600+i*600))}
function worklist(d,C,r){const flagged=r.medicines.filter(m=>m.comparisons.some(c=>c.flag)),grey=r.medicines.filter(m=>!m.comparisons.some(c=>c.flag));const n=r.medicines.reduce((a,m)=>a+m.comparisons.length,0);
 const clean=s=>{const m=s.match(/original text: "([^"]*)"/);return m?m[1].replace(/\s*\|\s*/g," · ").replace(/\s{2,}/g," "):s.split(": ").slice(1).join(": ")};
 return head("Result","Pharmacist worklist","Flagged medicines first, each with the two lines that disagree. Unflagged rows are not called safe: they are “no conflict found, not verified”.")+
 `<div class="wl"><div>${flagged.map(m=>m.comparisons.filter(c=>c.flag).map(c=>{const v=c.sapling.violation;const absent=/not on this chart/.test(c.rule||"");
  return `<div class="card fcard"><h3>${esc(m.name)}<span class="score">Sapling violation ${v.toFixed(2)}</span></h3><div class="why">${esc(c.doc)}${c.rule?" · "+esc(c.rule):""}</div>
  <div class="pair"><div class="q"><div class="from">Prescriber record</div><div class="t">${esc(clean(c.prescriber_line))}</div></div><div class="conn"></div><div class="q r"><div class="from">${esc(c.doc)}</div><div class="t">${absent?"Not on this chart":esc(clean(c.care_line||""))}</div></div></div>
  <div class="flags">${c.sapling_flag?`<span class="f-s">Sapling ≥ 0.4</span>`:""}${c.rule?`<span class="f-r">Code rule: ${esc(c.rule.split(":")[0])}</span>`:""}</div></div>`}).join("")).join("")}
  <details class="greys"><summary>${grey.length} medicines: no conflict found, not verified</summary><div class="card">${grey.map(m=>`<div class="gitem"><span>${esc(m.name)}</span><span>max violation ${m.max_violation.toFixed(2)}</span></div>`).join("")}</div></details></div>
  <div><div class="card tally"><div class="big">${flagged.length}</div><div style="color:var(--ink2);margin:4px 0 12px">flagged for pharmacist review</div>
  <div class="row"><span>Medicines checked</span><b>${r.medicines.length}</b></div><div class="row"><span>Documents</span><b>${d.case.documents.length}</b></div><div class="row"><span>Sapling calls</span><b>${n}</b></div><div class="row"><span>LLM calls via Mubit</span><b>${r.normalisation.length}</b></div><div class="row" style="border:0"><span>Run</span><b>${esc(r.run_at)}</b></div></div>
  <div class="card quote"><div class="kicker">Coroner</div><blockquote>“${esc(C.quote)}”</blockquote><a href="${esc(d.case.source_url)}">${esc(d.case.ref)}</a></div></div></div>`}
render();
