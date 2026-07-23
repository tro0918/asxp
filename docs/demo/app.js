const SKILL = `---
name: refund-policy
description: Use this policy skill to determine refund eligibility, deadlines, and fees.
license: Apache-2.0
metadata:
  author: demo.local
  version: "1.0.0"
---

# Refund policy

Check the order number, delivery date, and whether the package was opened. Standard products can be refunded within seven days of delivery. An opened product returned for change of mind incurs a KRW 3,000 return shipping fee. Delegate to the origin agent only when the original policy text or an exception classification is required.

──────────────── asxp.json ────────────────
{
  "specVersion": "0.2",
  "package": {"name": "refund-policy", "version": "1.0.0", "publisher": "demo.local"},
  "skill": {"entrypoint": "SKILL.md", "id": "asxp://demo.local/refund-policy"},
  "permissions": ["orders.read", "refunds.evaluate"],
  "privacy": "delegated",
  "origin": {"syncUrl": "https://agent-a.demo.local/skills/refund-policy"},
  "bindings": [
    {"type": "mcp", "server": "io.demo.orders", "tools": ["lookup_order", "evaluate_refund"]},
    {"type": "asxp-http", "url": "https://agent-a.demo.local/delegations"}
  ],
  "revision": "sha256:7e91c4d8…"
}`;

const state={exported:false,imported:false,active:false,version:'1.0.0',logs:[]};
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const els={export:$('#exportBtn'),import:$('#importBtn'),activate:$('#activateBtn'),sync:$('#syncBtn'),inspect:$('#inspectBtn'),packet:$('#packet'),packetState:$('#packetState'),drop:$('#dropzone'),status:$('#skillStatus'),detail:$('#skillDetail'),caps:$('#capsB'),runtime:$('#runtime'),runtimeBadge:$('#runtimeBadge'),logs:$('#logs'),dialog:$('#skillDialog'),skillText:$('#skillText'),toast:$('#toast')};

function now(){return new Date().toLocaleTimeString('en-GB',{hour12:false,hour:'2-digit',minute:'2-digit',second:'2-digit'})}
function log(type,event,text){state.logs.push({time:now(),type,event,text});renderLogs()}
function renderLogs(){els.logs.innerHTML=state.logs.length?state.logs.map(x=>`<div class="log ${x.type}"><time>${x.time}</time><b>${x.event}</b><span>${x.text}</span></div>`).join(''):'<div style="color:#75829b">No events yet.</div>';els.logs.scrollTop=els.logs.scrollHeight}
function toast(text){els.toast.textContent=text;els.toast.classList.add('show');setTimeout(()=>els.toast.classList.remove('show'),1800)}
function stage(n){$$('.stage').forEach((x,i)=>x.classList.toggle('active',i<=n))}
function addMessage(agent,type,text,label){const chat=$(`#chat${agent}`);const div=document.createElement('div');div.className=`message ${type}`;div.innerHTML=`<span>${label}</span>${text}`;chat.append(div);chat.scrollTop=chat.scrollHeight}
function thinking(agent,cb){addMessage(agent,'tool-msg','Working…','runtime');setTimeout(()=>{const chat=$(`#chat${agent}`);chat.lastElementChild.remove();cb()},420)}

els.export.onclick=()=>{state.exported=true;els.packet.classList.add('exported');els.packetState.textContent='v1.0.0 · verified';els.import.disabled=false;els.inspect.disabled=false;stage(1);log('success','PACK','refund-policy@1.0.0 → .asxp artifact');log('','INTEGRITY','per-file SHA-256 · revision 7e91c4d8');toast('Exported the .asxp package')};
els.import.onclick=()=>{state.imported=true;els.drop.classList.add('ready');els.status.textContent='refund-policy v1.0.0';els.detail.textContent='Origin linked · 2 tools · 2 permissions';els.import.classList.add('hidden');els.activate.classList.remove('hidden');stage(2);log('success','IMPORT','Schema and signature verified');log('warn','POLICY','orders.read, refunds.evaluate awaiting approval');toast('Imported into Agent B')};
els.activate.onclick=()=>{state.active=true;els.drop.classList.remove('ready');els.drop.classList.add('enabled');els.status.textContent='refund-policy · active';els.detail.textContent='Inline instructions + tools · origin delegation available';els.activate.classList.add('hidden');els.sync.classList.remove('hidden');['lookup_order','evaluate_refund','ask_refund_policy'].forEach(x=>{const s=document.createElement('span');s.className='imported';s.textContent=x;els.caps.append(s)});els.runtimeBadge.textContent='SKILL ACTIVE';els.runtimeBadge.style.color='var(--mint)';els.runtime.innerHTML=`<div class="runtime-block"><b>INSTRUCTIONS · refund-policy</b><p>Standard products are refundable within seven days… delegate only when the original policy is required.</p></div><div class="runtime-block"><b>FLATTENED TOOLS</b><p>refund-policy__lookup_order<br>refund-policy__evaluate_refund</p></div><div class="runtime-block"><b>AUTO-DELEGATION</b><p>ask_refund_policy → origin /v1/delegations · maxDepth 3</p></div>`;stage(3);log('success','ACTIVATE','Injected instructions into Agent B context');log('success','TOOLS','Flattened 2 tools + synthesized ask_refund_policy');toast('Skill activated')};
els.sync.onclick=()=>{log('','RESOLVE','If-None-Match: sha256:7e91c4d8');els.sync.disabled=true;setTimeout(()=>{els.sync.disabled=false;log('success','304','Installed revision is current');toast('Already up to date')},550)};
els.inspect.onclick=()=>{els.skillText.textContent=SKILL;els.dialog.showModal()};$('#closeDialog').onclick=()=>els.dialog.close();$('#copyBtn').onclick=async()=>{await navigator.clipboard.writeText(SKILL).catch(()=>{});toast('Copied to clipboard')};$('#downloadBtn').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([SKILL],{type:'text/plain'}));a.download='refund-policy-package.txt';a.click();URL.revokeObjectURL(a.href);log('','DOWNLOAD','Saved package preview');};

function answerA(q){if(/section 12|original|exception/i.test(q))return 'I checked the original policy index. Section 12 excludes hygiene-sealed goods, made-to-order products, and digital content. We still need the product classification to determine whether opening this package alone triggers an exception.';if(/2048|refund|fee|deadline/i.test(q))return 'ORD-2048 is a standard product delivered yesterday. It is within the seven-day refund window. A change-of-mind return is allowed after opening, but a KRW 3,000 return shipping fee applies.';return 'For a refund policy question, please provide the order number, delivery date, and whether the package was opened.'}
function answerB(q){if(!state.active){log('warn','NO_SKILL','Agent B has no refund-policy capability');return 'My current tools can only create tickets and search for customers, so I cannot determine refund eligibility. Please ask the policy agent.'}if(/section 12|original|exception/i.test(q)){addMessage('B','delegate-msg','ask_refund_policy { purpose: "policy_exception", maxDepth: 3 }','auto-delegation');log('warn','DELEGATE','Private RAG required → calling Agent A');const result=answerA(q);log('success','RESULT','Origin response received · trace axp-'+Date.now().toString().slice(-5));return 'I delegated this to the origin Policy Expert.\n\n'+result}addMessage('B','tool-msg','lookup_order { order_id: "ORD-2048" } → delivered yesterday\nevaluate_refund { opened: true } → eligible, fee: 3000','flattened tools');log('','TOOL_CALL','refund-policy__lookup_order');log('success','TOOL_CALL','refund-policy__evaluate_refund → eligible');return 'ORD-2048 is eligible for a refund. It is within seven days of delivery, and because this is an opened change-of-mind return, a KRW 3,000 return shipping fee applies.'}
$$('.composer').forEach(form=>form.onsubmit=e=>{e.preventDefault();const input=form.querySelector('input'),q=input.value.trim(),agent=form.dataset.agent;if(!q)return;addMessage(agent,'user-msg',q,'You');input.value='';thinking(agent,()=>addMessage(agent,'agent-msg',agent==='A'?answerA(q):answerB(q),agent==='A'?'Policy Expert':'Ops Assistant'))});
$$('[data-prompt]').forEach(btn=>btn.onclick=()=>{const input=$('.composer[data-agent="B"] input');input.value=btn.dataset.prompt;input.focus();toast('Test question added to Agent B')});
$('#clearLog').onclick=()=>{state.logs=[];renderLogs()};$('#resetBtn').onclick=()=>location.reload();
renderLogs();log('','READY','ASXP Agent Lab initialized');
