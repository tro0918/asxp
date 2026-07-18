const SKILL = `---
name: refund-policy
description: 주문 환불 가능 여부, 기한, 수수료를 판단할 때 사용하는 정책 스킬.
asxp-version: 0.1
version: 1.0.0
id: asxp://demo.local/refund-policy
revision: sha256:7e91c4d8
publisher: demo.local
privacy: delegated
permissions: orders.read refunds.evaluate
origin-url: https://agent-a.demo.local/v1/skills/refund-policy
delegation-url: https://agent-a.demo.local/v1/delegations
ae-tools-json: '[{"name":"lookup_order","description":"주문 상태 조회","kind":"mock","inputSchema":{"type":"object","properties":{"order_id":{"type":"string"}},"required":["order_id"]}},{"name":"evaluate_refund","description":"환불 정책 평가","kind":"mock","inputSchema":{"type":"object","properties":{"order_id":{"type":"string"},"opened":{"type":"boolean"}},"required":["order_id"]}}]'
---

# Refund policy

주문 번호와 수령일, 개봉 여부를 확인하세요. 일반 상품은 수령 후 7일 이내 환불할 수 있습니다. 개봉 상품은 단순 변심 환불 시 반품비 3,000원이 발생합니다. 원본 약관 조항이나 예외 품목 판정이 필요한 경우에만 원본 에이전트에 위임하세요.`;

const state={exported:false,imported:false,active:false,version:'1.0.0',logs:[]};
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const els={export:$('#exportBtn'),import:$('#importBtn'),activate:$('#activateBtn'),sync:$('#syncBtn'),inspect:$('#inspectBtn'),packet:$('#packet'),packetState:$('#packetState'),drop:$('#dropzone'),status:$('#skillStatus'),detail:$('#skillDetail'),caps:$('#capsB'),runtime:$('#runtime'),runtimeBadge:$('#runtimeBadge'),logs:$('#logs'),dialog:$('#skillDialog'),skillText:$('#skillText'),toast:$('#toast')};

function now(){return new Date().toLocaleTimeString('ko-KR',{hour12:false,hour:'2-digit',minute:'2-digit',second:'2-digit'})}
function log(type,event,text){state.logs.push({time:now(),type,event,text});renderLogs()}
function renderLogs(){els.logs.innerHTML=state.logs.length?state.logs.map(x=>`<div class="log ${x.type}"><time>${x.time}</time><b>${x.event}</b><span>${x.text}</span></div>`).join(''):'<div style="color:#75829b">이벤트가 아직 없습니다.</div>';els.logs.scrollTop=els.logs.scrollHeight}
function toast(text){els.toast.textContent=text;els.toast.classList.add('show');setTimeout(()=>els.toast.classList.remove('show'),1800)}
function stage(n){$$('.stage').forEach((x,i)=>x.classList.toggle('active',i<=n))}
function addMessage(agent,type,text,label){const chat=$(`#chat${agent}`);const div=document.createElement('div');div.className=`message ${type}`;div.innerHTML=`<span>${label}</span>${text}`;chat.append(div);chat.scrollTop=chat.scrollHeight}
function thinking(agent,cb){addMessage(agent,'tool-msg','처리 중…','runtime');setTimeout(()=>{const chat=$(`#chat${agent}`);chat.lastElementChild.remove();cb()},420)}

els.export.onclick=()=>{state.exported=true;els.packet.classList.add('exported');els.packetState.textContent='v1.0.0 · signed';els.import.disabled=false;els.inspect.disabled=false;stage(1);log('success','EXPORT','refund-policy@1.0.0 → canonical manifest');log('','SIGN','sha256:7e91c4d8 · kid demo-2026');toast('skill.md를 Export했습니다')};
els.import.onclick=()=>{state.imported=true;els.drop.classList.add('ready');els.status.textContent='refund-policy v1.0.0';els.detail.textContent='Origin 연결됨 · 2 tools · 2 permissions';els.import.classList.add('hidden');els.activate.classList.remove('hidden');stage(2);log('success','IMPORT','schema 및 서명 검증 완료');log('warn','POLICY','orders.read, refunds.evaluate 승인 대기');toast('Agent B로 가져왔습니다')};
els.activate.onclick=()=>{state.active=true;els.drop.classList.remove('ready');els.drop.classList.add('enabled');els.status.textContent='refund-policy · 활성';els.detail.textContent='Inline instructions + tools · origin delegation 사용 가능';els.activate.classList.add('hidden');els.sync.classList.remove('hidden');['lookup_order','evaluate_refund','ask_refund_policy'].forEach(x=>{const s=document.createElement('span');s.className='imported';s.textContent=x;els.caps.append(s)});els.runtimeBadge.textContent='SKILL ACTIVE';els.runtimeBadge.style.color='var(--mint)';els.runtime.innerHTML=`<div class="runtime-block"><b>INSTRUCTIONS · refund-policy</b><p>일반 상품은 수령 후 7일 이내 환불 가능… 원본 약관이 필요할 때만 위임.</p></div><div class="runtime-block"><b>FLATTENED TOOLS</b><p>refund-policy__lookup_order<br>refund-policy__evaluate_refund</p></div><div class="runtime-block"><b>AUTO-DELEGATION</b><p>ask_refund_policy → origin /v1/delegations · maxDepth 3</p></div>`;stage(3);log('success','ACTIVATE','instructions를 Agent B context에 주입');log('success','TOOLS','2 tools 평탄화 + ask_refund_policy 합성');toast('스킬이 활성화되었습니다')};
els.sync.onclick=()=>{log('','RESOLVE','If-None-Match: sha256:7e91c4d8');els.sync.disabled=true;setTimeout(()=>{els.sync.disabled=false;log('success','304','현재 revision이 최신입니다');toast('최신 버전입니다')},550)};
els.inspect.onclick=()=>{els.skillText.textContent=SKILL;els.dialog.showModal()};$('#closeDialog').onclick=()=>els.dialog.close();$('#copyBtn').onclick=async()=>{await navigator.clipboard.writeText(SKILL).catch(()=>{});toast('내용을 복사했습니다')};$('#downloadBtn').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([SKILL],{type:'text/markdown'}));a.download='refund-policy.skill.md';a.click();URL.revokeObjectURL(a.href);log('','DOWNLOAD','portable skill.md 저장');};

function answerA(q){if(/12조|원본|예외/.test(q))return '원본 정책 인덱스를 확인했습니다. 약관 12조 예외는 위생 밀봉 상품, 주문 제작 상품, 디지털 콘텐츠입니다. 포장 개봉만으로 예외가 되는지는 상품 분류를 추가 확인해야 합니다.';if(/2048|환불|수수료|기한/.test(q))return 'ORD-2048은 어제 배송 완료된 일반 상품입니다. 수령 후 7일 이내이며, 개봉 상태의 단순 변심 환불은 가능하지만 반품비 3,000원이 발생합니다.';return '환불 정책 질문이라면 주문 번호, 수령일, 개봉 여부를 알려주세요.'}
function answerB(q){if(!state.active){log('warn','NO_SKILL','Agent B에 refund-policy capability 없음');return '현재 제 도구에는 티켓 생성과 고객 검색만 있어 환불 가능 여부를 판단할 수 없습니다. 정책 담당 에이전트에게 문의해 주세요.'}if(/12조|원본|예외/.test(q)){addMessage('B','delegate-msg','ask_refund_policy { purpose: "policy_exception", maxDepth: 3 }','auto-delegation');log('warn','DELEGATE','private RAG 필요 → Agent A 호출');const result=answerA(q);log('success','RESULT','origin 응답 수신 · trace axp-'+Date.now().toString().slice(-5));return '원본 Policy Expert에 위임해 확인했습니다.\n\n'+result}addMessage('B','tool-msg','lookup_order { order_id: "ORD-2048" } → delivered yesterday\nevaluate_refund { opened: true } → eligible, fee: 3000','flattened tools');log('','TOOL_CALL','refund-policy__lookup_order');log('success','TOOL_CALL','refund-policy__evaluate_refund → eligible');return '확인 결과 ORD-2048은 환불 가능합니다. 수령 후 7일 이내이고, 포장을 연 단순 변심 건이므로 반품비 3,000원이 발생합니다.'}
$$('.composer').forEach(form=>form.onsubmit=e=>{e.preventDefault();const input=form.querySelector('input'),q=input.value.trim(),agent=form.dataset.agent;if(!q)return;addMessage(agent,'user-msg',q,'You');input.value='';thinking(agent,()=>addMessage(agent,'agent-msg',agent==='A'?answerA(q):answerB(q),agent==='A'?'Policy Expert':'Ops Assistant'))});
$$('[data-prompt]').forEach(btn=>btn.onclick=()=>{const input=$('.composer[data-agent="B"] input');input.value=btn.dataset.prompt;input.focus();toast('Agent B 입력창에 테스트 질문을 넣었습니다')});
$('#clearLog').onclick=()=>{state.logs=[];renderLogs()};$('#resetBtn').onclick=()=>location.reload();
renderLogs();log('','READY','ASXP Agent Lab initialized');
