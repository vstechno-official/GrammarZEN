const API_BASE = '';
const state = {lastResult:null,currentFilter:'all',issues:[],isLoading:false,correctedText:'',originalText:''};
const $ = id => document.getElementById(id);
const $$ = sel => document.querySelectorAll(sel);
const elements = {
inputText:$('inputText'),correctBtn:$('correctBtn'),clearBtn:$('clearBtn'),
pasteBtn:$('pasteBtn'),copyBtn:$('copyBtn'),applyBtn:$('applyBtn'),
charCount:$('charCount'),wordCountStat:$('wordCount'),sentenceCountStat:$('sentenceCount'),
scoreCircle:$('scoreCircle'),scoreTextMain:$('scoreTextMain'),scoreGrade:$('scoreGrade'),
scoreIssues:$('scoreIssues'),readabilityVal:$('readabilityVal'),sentimentVal:$('sentimentVal'),
avgSentVal:$('avgSentVal'),vocabVal:$('vocabVal'),processingTime:$('processingTime'),
issuesList:$('issuesList'),suggestionsList:$('suggestionsList'),suggestionsPanel:$('suggestionsPanel'),
correctedOutput:$('correctedOutput'),copyBar:$('copyBar'),
loadingOverlay:$('loadingOverlay'),loadingText:$('loadingText'),
scoreMini:$('scoreMini')
};
function updateCounts(){
const t=elements.inputText.value;
elements.charCount.textContent=t.length;
elements.wordCountStat.textContent=t.trim()?t.trim().split(/\s+/).length:0;
elements.sentenceCountStat.textContent=t.trim()?t.split(/[.!?]+/).filter(s=>s.trim()).length:0;
}
function setLoading(l,msg='Analyzing your text...'){
state.isLoading=l;
elements.loadingOverlay.style.display=l?'flex':'none';
elements.loadingText.textContent=msg;
elements.correctBtn.disabled=l;
}
function showToast(msg,type='info'){
const ex=document.querySelector('.toast');
if(ex)ex.remove();
const t=document.createElement('div');
t.className=`toast ${type}`;
t.textContent=msg;
document.body.appendChild(t);
requestAnimationFrame(()=>{
t.classList.add('show');
setTimeout(()=>{t.classList.remove('show');setTimeout(()=>t.remove(),300);},3000);
});
}
function switchTab(name){
$$('.tab-btn').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));
$$('.tab-content').forEach(c=>c.classList.toggle('active',c.id===`tab-${name}`));
}
function updateScoreRing(score){
const offset=314-(score/100)*314;
elements.scoreCircle.style.strokeDashoffset=offset;
const color=score>=85?'#4ade80':score>=70?'#6366f1':score>=50?'#fbbf24':'#f87171';
elements.scoreCircle.style.stroke=color;
const grade=score>=95?'Excellent':score>=85?'Very Good':score>=70?'Good':score>=50?'Fair':'Needs Work';
elements.scoreTextMain.textContent=Math.round(score);
elements.scoreGrade.textContent=grade;
elements.scoreGrade.style.color=color;
if(elements.scoreMini)elements.scoreMini.textContent=`Score: ${Math.round(score)}`;
}
function getSeverityIcon(s){
if(s==='error')return`<svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>`;
if(s==='warning')return`<svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>`;
return`<svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/></svg>`;
}
function escapeHtml(str){
const d=document.createElement('div');
d.appendChild(document.createTextNode(str));
return d.innerHTML;
}
function renderIssues(issues,filter='all'){
const filtered=filter==='all'?issues:issues.filter(i=>i.severity===filter);
if(filtered.length===0){
elements.issuesList.innerHTML=`<div class="empty-state" style="padding:32px 16px;"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg><p>${filter==='all'?'No issues found.<br>Your text looks great!':`No ${filter} issues found.`}</p></div>`;
return;
}
elements.issuesList.innerHTML=filtered.map((issue,idx)=>`
<div class="issue-item ${issue.severity}" data-index="${idx}">
<div class="issue-severity ${issue.severity}">${getSeverityIcon(issue.severity)} ${issue.severity.charAt(0).toUpperCase()+issue.severity.slice(1)}</div>
<div class="issue-message">${escapeHtml(issue.message)}</div>
<div class="issue-context">${escapeHtml(issue.context)}</div>
${issue.replacements.length>0?`<div class="issue-replacements">${issue.replacements.slice(0,4).map(r=>`<span class="replacement-chip" data-replacement="${escapeHtml(r)}" data-offset="${issue.offset}" data-length="${issue.length}">${escapeHtml(r)}</span>`).join('')}</div>`:''}
</div>`).join('');
elements.issuesList.querySelectorAll('.replacement-chip').forEach(chip=>{
chip.addEventListener('click',e=>{
e.stopPropagation();
applyReplacement(parseInt(chip.dataset.offset),parseInt(chip.dataset.length),chip.dataset.replacement);
});
});
}
function applyReplacement(offset,length,replacement){
const text=elements.inputText.value;
elements.inputText.value=text.slice(0,offset)+replacement+text.slice(offset+length);
updateCounts();
showToast(`Replaced with "${replacement}"`, 'success');
correctText();
}
function updateFilterCounts(issues){
const counts={all:issues.length,error:0,warning:0,style:0};
issues.forEach(i=>{if(counts[i.severity]!==undefined)counts[i.severity]++;});
$$('.filter-btn').forEach(btn=>{
const f=btn.dataset.filter;
const c=counts[f]??0;
btn.textContent=f==='all'?`All (${c})`:`${f.charAt(0).toUpperCase()+f.slice(1)} (${c})`;
});
}
function getReadabilityLabel(s){
if(s>=90)return'Very Easy';if(s>=70)return'Easy';if(s>=50)return'Medium';if(s>=30)return'Hard';return'Very Hard';
}
function renderResult(data){
state.lastResult=data;state.correctedText=data.corrected_text;state.issues=data.issues;
updateScoreRing(data.score);
elements.scoreIssues.textContent=data.issue_count===0?'No issues found':`${data.issue_count} issue${data.issue_count!==1?'s':''} found`;
elements.readabilityVal.textContent=`${data.readability_score} — ${getReadabilityLabel(data.readability_score)}`;
const smap={positive:'#4ade80',negative:'#f87171',neutral:'#9090aa'};
const sc=smap[data.sentiment]||'#9090aa';
const sarrow=data.sentiment==='positive'?'↑':data.sentiment==='negative'?'↓':'→';
elements.sentimentVal.innerHTML=`<span style="color:${sc};font-weight:600;">${sarrow} ${data.sentiment.charAt(0).toUpperCase()+data.sentiment.slice(1)} (${data.sentiment_polarity>0?'+':''}${data.sentiment_polarity})</span>`;
elements.avgSentVal.textContent=`${data.avg_sentence_length} words`;
elements.vocabVal.textContent=`${data.vocabulary_richness}%`;
elements.processingTime.textContent=`${data.processing_time_ms}ms`;
elements.correctedOutput.innerHTML=data.corrected_text?`<p style="white-space:pre-wrap;line-height:1.8;">${escapeHtml(data.corrected_text)}</p>`:`<div class="empty-state"><p>No corrections needed.</p></div>`;
elements.copyBar.style.display='flex';
renderIssues(data.issues,state.currentFilter);
updateFilterCounts(data.issues);
if(data.suggestions&&data.suggestions.length>0){
elements.suggestionsPanel.style.display='block';
elements.suggestionsList.innerHTML=data.suggestions.map(s=>`<div class="suggestion-item"><svg class="suggestion-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg><span>${escapeHtml(s)}</span></div>`).join('');
}else{elements.suggestionsPanel.style.display='none';}
if(data.issue_count===0)showToast('Perfect! No grammar issues found.','success');
else showToast(`Found ${data.issue_count} issue${data.issue_count!==1?'s':''}. Check the panel.`,'info');
}
async function correctText(){
const text=elements.inputText.value.trim();
if(!text){showToast('Please enter some text.','error');return;}
if(text.length>10000){showToast('Text exceeds 10,000 character limit.','error');return;}
state.originalText=text;
setLoading(true,'Analyzing grammar and style...');
try{
const res=await fetch(`${API_BASE}/api/correct`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text,mode:'full'})});
if(!res.ok){const err=await res.json().catch(()=>({}));throw new Error(err.detail||`Server error: ${res.status}`);}
const data=await res.json();
renderResult(data);
switchTab('corrected');
}catch(err){showToast(err.message||'Failed to process text.','error');}
finally{setLoading(false);}
}
function clearAll(){
elements.inputText.value='';updateCounts();
const empty1=`<div class="empty-state"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg><p>Your corrected text<br>will appear here.</p></div>`;
elements.correctedOutput.innerHTML=empty1;
elements.issuesList.innerHTML=`<div class="empty-state" style="padding:32px 16px;"><p>Issues will appear<br>after analysis.</p></div>`;
elements.suggestionsList.innerHTML='';elements.suggestionsPanel.style.display='none';
elements.copyBar.style.display='none';
updateScoreRing(0);elements.scoreIssues.textContent='';elements.scoreTextMain.textContent='—';elements.scoreGrade.textContent='';
elements.readabilityVal.textContent='—';elements.sentimentVal.textContent='—';elements.avgSentVal.textContent='—';elements.vocabVal.textContent='—';elements.processingTime.textContent='';
state.lastResult=null;state.issues=[];state.correctedText='';
updateFilterCounts([]);showToast('Cleared.','info');
}
function applyCorrections(){
if(!state.correctedText){showToast('No corrections to apply.','error');return;}
elements.inputText.value=state.correctedText;updateCounts();switchTab('input');showToast('Corrections applied to input.','success');
}
function copyToClipboard(text){
if(!text){showToast('Nothing to copy.','error');return;}
navigator.clipboard.writeText(text).then(()=>showToast('Copied to clipboard!','success')).catch(()=>{
const ta=document.createElement('textarea');ta.value=text;ta.style.cssText='position:fixed;opacity:0;';document.body.appendChild(ta);ta.select();document.execCommand('copy');document.body.removeChild(ta);showToast('Copied to clipboard!','success');
});
}
function init(){
const samples=["She don't know nothing about the situation that happend yesterday at the office.","Their are many reasons why people chooses to study grammer and writing skills.","He goed to the store and buyed alot of items that costed him very much money.","The team have not yet submitted there report which were due last weak.","I am very very happy to announce that we has won the competiton!"];
let si=0;
$('sampleBtn').addEventListener('click',()=>{elements.inputText.value=samples[si%samples.length];si++;updateCounts();showToast('Sample text loaded!','info');});
$('pasteBtn').addEventListener('click',async()=>{try{const t=await navigator.clipboard.readText();elements.inputText.value=t;updateCounts();showToast('Pasted from clipboard.','info');}catch{showToast('Clipboard access denied.','error');}});
$('clearBtn').addEventListener('click',clearAll);
$('correctBtn').addEventListener('click',correctText);
$('copyBtn').addEventListener('click',()=>copyToClipboard(state.correctedText));
$('copyOrigBtn').addEventListener('click',()=>copyToClipboard(elements.inputText.value));
$('applyBtn').addEventListener('click',applyCorrections);
elements.inputText.addEventListener('input',updateCounts);
document.addEventListener('keydown',e=>{
if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();correctText();}
if((e.ctrlKey||e.metaKey)&&e.key==='k'){e.preventDefault();clearAll();}
});
$$('.tab-btn').forEach(btn=>btn.addEventListener('click',()=>switchTab(btn.dataset.tab)));
$$('.filter-btn').forEach(btn=>btn.addEventListener('click',()=>{
$$('.filter-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');
state.currentFilter=btn.dataset.filter;renderIssues(state.issues,state.currentFilter);
}));
updateCounts();updateFilterCounts([]);switchTab('input');
}
document.addEventListener('DOMContentLoaded',init);
