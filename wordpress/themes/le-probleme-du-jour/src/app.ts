import { render, escapeHTML as esc } from '../../../../shared/latex/render.ts';

declare global { interface Window { LPDJ: any } }
const cfg = window.LPDJ;
let session = cfg.session;
const root = document.querySelector('#app')!;
const categories: Record<string,string> = {Algebra:'Algebra',Geometry:'Geometry','Number Theory':'Number Theory',Combinatorics:'Combinatorics',Logic:'Logic'};
const progress: Record<string,string> = {unseen:'Unseen',bookmarked:'Bookmarked',attempted:'Attempted',solved:'Solved'};
const statuses: Record<string,string> = {draft:'Draft',submitted:'Awaiting review',returned:'Changes requested',published:'Published'};
const actions: Record<string,string> = {save:'Saved',submit:'Submitted',publish:'Published',return:'Returned to author',unpublish:'Unpublished'};
let listing: any = null, problem: any = null, language = 'en', editorLanguage = 'en', dirty = false, routeSequence = 0;
let filters = {search:'',category:'',difficulty:'',source:'',progress:'',status:'',sort:'newest'};
let lastRoute = location.hash || '#/';
let avatar = 0;
let listPage = 1;
const pageSize = 50;
const $ = (selector: string) => document.querySelector(selector) as any;
const value = (id: string) => ($('#'+id) as HTMLInputElement)?.value ?? '';
const checked = (id: string) => !!($('#'+id) as HTMLInputElement)?.checked;
const titleOf = (p: any) => p.versions.en?.title || p.versions.fr?.title || 'Untitled';
const date = (s: string) => new Date(s).toLocaleDateString('en-GB', {day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'});
const option = (val:string, label:string, selected:string) => `<option value="${esc(val)}" ${selected===val?'selected':''}>${esc(label)}</option>`;
function toast(message:string) { const t=$('#toast'); t.textContent=message; t.classList.add('visible'); setTimeout(()=>t.classList.remove('visible'),5000); }
function message(text:string, error=false) { const e=$('#form-message'); if(e){e.textContent=text;e.className='notice '+(error?'error':'success');e.focus();}else toast(text); }
function routeTo(path:string) { location.hash='#'+path; }
async function api(path:string, data?:any, method?:string) {
    const url=new URL(cfg.api+path,location.href);
    // Also support WordPress installations using plain permalinks (?rest_route=...).
    if(cfg.api.includes('?rest_route=')) { const [p,q]=path.split('?'); const base=new URL(cfg.api); base.searchParams.set('rest_route',base.searchParams.get('rest_route')!+p); new URLSearchParams(q).forEach((v,k)=>base.searchParams.set(k,v)); url.href=base.href; }
    const headers:Record<string,string>={'X-WP-Nonce':session.nonce,'X-LPDJ-Form':session.formNonce};
    if(data && !(data instanceof FormData))headers['Content-Type']='application/json';
    const response=await fetch(url,{method:method||(data?'POST':'GET'),headers,credentials:'same-origin',body:data?(data instanceof FormData?data:JSON.stringify(data)):undefined});
    const result=await response.json();
    if(!response.ok)throw new Error(result.message||'Something went wrong. Please try again.');
    return result;
}
function shell(content:string, active='') {
    const user=session.user;
    root.innerHTML=`${session.local?`<div class="local-banner"><span class="local-dot"></span>Local preview · Emails stay on this Mac${user?.admin?'<a href="#/courrier">Test inbox ↗</a>':''}</div>`:''}
    <header class="header container"><a class="brand" href="#/" aria-label="Le Problème du Jour — Home"><img src="${cfg.logo}" alt="" width="52" height="52"><span>Le Problème du Jour</span></a>
    <nav aria-label="Main navigation"><a ${active==='collection'?'aria-current="page"':''} href="#/">Problems</a>${user?`<a ${active==='mine'?'aria-current="page"':''} href="#/mes-propositions">My submissions</a>${user.admin?`<a ${active==='review'?'aria-current="page"':''} href="#/administration">Admin review</a>`:''}<a class="profile-link" href="#/profil" aria-label="My profile">${user.avatar?`<img src="${esc(user.avatar)}" alt="">`:`<span>${esc(user.pseudo.slice(0,1).toUpperCase())}</span>`}<span>${esc(user.pseudo)}</span></a>`:`<a href="#/connexion">Sign in</a><a class="button small" href="#/inscription">Create account</a>`}</nav></header>
    <main id="main" class="container" tabindex="-1">${content}</main>
    <footer class="footer container"><span>Le Problème du Jour</span><a href="#/aide">LaTeX & figures</a><a href="#/confidentialite">Privacy & contributions</a></footer>`;
}
function intro(title:string,extra='') { return `<div class="page-heading"><h1>${title}</h1>${extra}</div>`; }
function notice() { return '<div id="form-message" role="alert" tabindex="-1"></div>'; }
function field(id:string,label:string,type='text',extra='') { return `<label for="${id}">${label}<input id="${id}" name="${id}" type="${type}" ${extra}></label>`; }
function langSquares(p:any) { return `<span class="language-squares" aria-label="Versions">${['fr','en'].map(l=>`<span class="lang-square level-${p.difficulty} ${p.versions[l]?.title?'':'absent'}" title="${l.toUpperCase()} · ${p.versions[l]?.approved?'verified':'not verified'} · level ${p.difficulty}">${l.toUpperCase()}${p.versions[l]?.approved?'<b aria-label="verified">✓</b>':''}</span>`).join('')}</span>`; }
function sourceOrder(a:string,b:string) { const names=session.sources;const x=names.indexOf(a),y=names.indexOf(b);return (x<0?99:x)-(y<0?99:y)||a.localeCompare(b,'en'); }
function empty(title:string,text:string,button='') { return `<div class="empty"><div class="empty-symbol" aria-hidden="true">∅</div><h2>${title}</h2><p>${text}</p>${button}</div>`; }
function gated() {
    shell(`<section class="welcome"><div><h1>Le Problème du Jour</h1><div class="button-row"><a class="button" href="#/inscription">Create account</a><a class="button secondary" href="#/connexion">Sign in</a></div></div><div class="hero-logo"><img src="${cfg.logo}" alt="Poincaré disk tiling" width="340" height="340"></div></section>`, 'collection');
}
async function collection(scope='published') {
    if(!session.user){gated();return;}
    if(scope==='review'&&!session.user.admin){shell(empty('Restricted access','This page is for administrators.'));return;}
    const seq=routeSequence;
    shell(intro(scope==='published'?'Problems':scope==='mine'?'My submissions':'Admin review')+'<p class="loading">Loading…</p>',scope==='published'?'collection':scope==='mine'?'mine':'review');
    listing=await api('problems?scope='+scope);if(seq!==routeSequence)return;listPage=1;
    const total=listing.published, pending=listing.items.filter((p:any)=>p.state==='submitted').length;
    const sourceCounts:Record<string,number> = scope==='published'?listing.sources:listing.items.reduce((counts:any,p:any)=>{counts[p.source]=(counts[p.source]||0)+1;return counts;},{});
    shell(intro(scope==='published'?'Problems':scope==='mine'?'My submissions':'Admin review',`<button class="button" data-action="new">＋ Submit a problem</button>`)+
    `<section class="stats"><div><strong>${(scope==='published'?total:listing.total).toLocaleString('en-GB')}</strong><span>${scope==='published'?'published problems':'submissions'}</span></div><div><strong>${(scope==='review'?pending:Object.keys(listing.sources).length).toLocaleString('en-GB')}</strong><span>${scope==='review'?'awaiting review':'sources'}</span></div><div><strong>1–5</strong><span>difficulty levels</span></div></section>
    ${listing.total?`<div class="source-counts">${Object.entries(sourceCounts).sort(([a],[b])=>sourceOrder(a,b)).map(([s,c])=>`<button data-source="${esc(s)}">${esc(s)} <b>${c}</b></button>`).join('')}</div>`:''}
    <section class="collection"><div class="section-label"><h2>${scope==='published'?'Browse problems':scope==='mine'?'Your problems':'All submissions'}</h2>${scope==='published'?'<button class="text-link" data-action="pick">Pick one ↗</button>':''}</div>
    <div class="filters"><label class="search-label" for="search">Search<input id="search" type="search" placeholder="Title, keyword…" value="${esc(filters.search)}"></label>
    <label for="category">Category<select id="category">${option('','All',filters.category)}${Object.entries(categories).map(([v,l])=>option(v,l,filters.category)).join('')}</select></label>
    <label for="difficulty">Difficulty<select id="difficulty">${option('','All levels',filters.difficulty)}${[1,2,3,4,5].map(n=>option(String(n),`Level ${n}`,filters.difficulty)).join('')}</select></label>
    <label for="source">Source<select id="source">${option('','All sources',filters.source)}${[...new Set(listing.items.map((p:any)=>p.source))].sort(sourceOrder).map((s:any)=>option(s,s,filters.source)).join('')}</select></label>
    <label for="${scope==='published'?'progress':'status'}">${scope==='published'?'Progress':'Status'}<select id="${scope==='published'?'progress':'status'}">${option('','All',scope==='published'?filters.progress:filters.status)}${Object.entries(scope==='published'?progress:statuses).map(([v,l])=>option(v,l,scope==='published'?filters.progress:filters.status)).join('')}</select></label></div>
    <div class="list-tools"><span id="result-count" aria-live="polite"></span><label for="sort">Sort by <select id="sort">${[['newest','Newest'],['difficulty-asc','Difficulty: low to high'],['difficulty-desc','Difficulty: high to low'],['fr','Verified FR'],['en','Verified EN'],['title','Title']].map(([v,l])=>option(v,l,filters.sort)).join('')}</select></label><button class="text-link" data-action="reset-filters">Clear filters</button></div><div id="problem-list" data-scope="${scope}"></div></section>`,scope==='published'?'collection':scope==='mine'?'mine':'review');
    drawList();
}
function filtered() {
    return listing.items.filter((p:any)=>!filters.search||[...Object.values(p.versions).map((v:any)=>v.title),...p.keywords].join(' ').toLocaleLowerCase().includes(filters.search.toLocaleLowerCase())).filter((p:any)=>!filters.category||p.category===filters.category).filter((p:any)=>!filters.difficulty||p.difficulty===Number(filters.difficulty)).filter((p:any)=>!filters.source||p.source===filters.source).filter((p:any)=>!filters.progress||p.progress===filters.progress).filter((p:any)=>!filters.status||p.state===filters.status).sort((a:any,b:any)=>filters.sort==='title'?titleOf(a).localeCompare(titleOf(b),'en'):filters.sort==='difficulty-asc'?a.difficulty-b.difficulty:filters.sort==='difficulty-desc'?b.difficulty-a.difficulty:['fr','en'].includes(filters.sort)?Number(!!b.versions[filters.sort]?.approved)-Number(!!a.versions[filters.sort]?.approved):b.id-a.id);
}
function drawList(reset=true) {
    if(reset)listPage=1;
    const all=filtered(),scope=$('#problem-list').dataset.scope;
    const pages=Math.max(1,Math.ceil(all.length/pageSize));listPage=Math.min(listPage,pages);
    const items=all.slice((listPage-1)*pageSize,listPage*pageSize);
    $('#result-count').textContent=`${all.length.toLocaleString('en-GB')} problem${all.length!==1?'s':''}`;
    $('#problem-list').innerHTML=items.length?`<div class="problem-table">${items.map((p:any)=>`<a class="problem-row" href="#/${scope==='published'?'probleme':'editer'}/${p.id}"><span class="problem-name"><strong>${esc(titleOf(p))}</strong><small>${esc(categories[p.category])} <span>·</span> ${esc(p.source)} ${scope!=='published'?`<span>·</span> ${esc(p.author)}`:''}</small></span><span class="level-label">Level ${p.difficulty}</span>${langSquares(p)}<span class="status ${scope==='published'?p.progress:p.state}">${scope==='published'?progress[p.progress]:statuses[p.state]}</span><span class="row-arrow">↗</span></a>`).join('')}</div>`:listing.total?empty('No results','Try different filters.','<button class="button secondary" data-action="reset-filters">Clear filters</button>'):empty(scope==='published'?'No published problems':'No submissions',scope==='published'?'':'','<button class="button" data-action="new">＋ Submit a problem</button>');
    if(pages>1)$('#problem-list').insertAdjacentHTML('beforeend',`<nav class="pagination" aria-label="Problem list pages"><button class="button secondary small" data-action="previous-page" ${listPage===1?'disabled':''}>← Previous</button><span>Page ${listPage} of ${pages}</span><button class="button secondary small" data-action="next-page" ${listPage===pages?'disabled':''}>Next →</button></nav>`);
}
function auth(kind:string,params:URLSearchParams) {
    const signup=kind==='inscription', login=kind==='connexion', forgot=kind==='mot-de-passe', resend=kind==='renvoyer', reset=kind==='reinitialiser', verify=kind==='confirmer';
    const heading=signup?'Create account':login?'Sign in':forgot?'Reset password':resend?'Confirm your email':reset?'Choose a password':'Confirm your account';
    shell(`<div class="auth-layout"><aside><img src="${cfg.logo}" alt="Poincaré disk tiling" width="240" height="240"></aside><section class="auth-card"><h1>${heading}</h1>${notice()}<form id="auth-form" data-kind="${kind}">
    ${signup?field('pseudo','Display name','text','required minlength="2" maxlength="40" autocomplete="nickname"'):''}
    ${!reset&&!verify?field('email','Email address','email','required autocomplete="email"'):''}
    ${signup||login||reset?field('password','Password','password',`required ${login?'':'minlength="12"'} maxlength="200" autocomplete="${login?'current-password':'new-password'}"`)+(!login?'<p class="field-help">At least 12 characters.</p>':''):''}
    ${signup?'<label class="check"><input id="accept" type="checkbox" required><span>I accept the <a href="#/confidentialite" target="_blank">contribution and privacy terms</a>.</span></label><label class="check"><input id="notifications" type="checkbox"><span>Email me when a new problem is published.</span></label>':''}
    ${login?'<label class="check"><input id="remember" type="checkbox"><span>Remember me on this device</span></label>':''}
    <button class="button full" type="submit">${signup?'Create account':login?'Sign in':verify?'Confirm email':reset?'Save password':'Send link'} <span>→</span></button></form>
    <div class="auth-links">${login?'<a href="#/mot-de-passe">Forgot password?</a><a href="#/renvoyer">Resend confirmation</a><p>No account yet? <a href="#/inscription">Create account</a></p>':'<a href="#/connexion">← Back to sign in</a>'}</div></section></div>`);
    $('#auth-form').onsubmit=async(e:Event)=>{
        e.preventDefault();const form=e.currentTarget as HTMLFormElement;const btn=form.querySelector('button')!;btn.disabled=true;
        try{
            const result=await api('auth/'+({inscription:'register',connexion:'login','mot-de-passe':'forgot',renvoyer:'resend',reinitialiser:'reset',confirmer:'verify'} as any)[kind],{pseudo:value('pseudo'),email:value('email'),password:value('password'),remember:checked('remember'),accept:checked('accept'),notifications:checked('notifications'),...Object.fromEntries(params)});
            if(login){session=result;location.hash='#/';location.reload();}else{message(result.message);if(verify||reset)form.hidden=true;else form.reset();}
        }catch(error:any){message(error.message,true);}finally{btn.disabled=false;}
    };
}
function math(version:any,assets:any) { return render(version.latex,Object.fromEntries(Object.entries(assets||{}).map(([name,a]:any)=>[name,a.url]))); }
async function reader(id:string) {
    if(!session.user){routeTo('/connexion');return;}
    const seq=routeSequence;problem=await api('problems/'+id);if(seq!==routeSequence)return;
    if(!problem.versions[language])language=Object.keys(problem.versions)[0];
    showReader();
}
function showReader() {
    const p=problem,v=p.versions[language];let content;
    try{content=math(v,p.assets);}catch(error:any){content=`<p class="notice error">The statement needs a rendering correction: ${esc(error.message)}</p><pre>${esc(v.latex)}</pre>`;}
    shell(`<div class="reader-heading"><a class="text-link" href="#/">← Problems</a><span class="badge">${esc(categories[p.category])}</span><span class="muted">${esc(p.source)} · Level ${p.difficulty}</span></div>
    <article class="reading-card"><div class="reader-top"><p class="eyebrow">LE PROBLÈME DU JOUR</p>${Object.keys(p.versions).length>1?`<div class="segmented" aria-label="Language">${Object.keys(p.versions).map(l=>`<button data-reader-lang="${l}" aria-pressed="${language===l}">${l.toUpperCase()}</button>`).join('')}</div>`:`<span class="small muted">${language.toUpperCase()}</span>`}</div><h1>${esc(v.title)}</h1><div class="math-content">${content}</div><div class="tags">${p.keywords.map((k:string)=>`<span>${esc(k)}</span>`).join('')}</div><div class="reader-foot"><span>Submitted by <strong>${esc(p.author)}</strong></span>${p.editable?`<a href="#/editer/${p.id}">Edit →</a>`:''}</div></article>
    <section class="progress-card"><div><h2>Progress</h2></div><div class="segmented progress-buttons">${Object.entries(progress).map(([key,label])=>`<button data-progress="${key}" aria-pressed="${p.progress===key}">${label}</button>`).join('')}</div></section>`,'collection');
}
async function editor(id:string) {
    if(!session.user){routeTo('/connexion');return;}
    const seq=routeSequence;problem=await api('problems/'+id+'?context=edit');if(seq!==routeSequence)return;
    editorLanguage=problem.versions.en?.title||!problem.versions.fr?.title?'en':'fr';dirty=false;showEditor();
}
function collectEditor() {
    if(!$('#problem-title'))return;
    const v=problem.versions[editorLanguage];v.title=value('problem-title');v.latex=value('latex');if(session.user.admin)v.approved=checked('approved');
    problem.category=value('edit-category');problem.difficulty=Number(value('edit-difficulty'));problem.source=value('edit-source');problem.keywords=value('keywords').split(',').map((s:string)=>s.trim()).filter(Boolean);if(session.user.admin)problem.reviewNote=value('review-note');
}
function showEditor() {
    const p=problem,v=p.versions[editorLanguage];
    shell(`${intro(titleOf(p)==='Untitled'?'New problem':esc(titleOf(p)),`<span class="status ${p.state}">${statuses[p.state]}</span>`)}
    ${p.hasPublished?`<div class="notice soft">A version is published. Changes stay private until you publish again. <a href="#/probleme/${p.id}">View published version →</a></div>`:''}
    ${p.reviewNote&&!session.user.admin?`<div class="notice soft"><strong>Administrator’s note</strong><p>${esc(p.reviewNote)}</p></div>`:''}
    ${notice()}<div class="editor-meta"><label for="edit-category">Category<select id="edit-category">${Object.entries(categories).map(([key,label])=>option(key,label,p.category)).join('')}</select></label><label for="edit-difficulty">Difficulty<select id="edit-difficulty">${[1,2,3,4,5].map(n=>option(String(n),`${n} — ${['Introductory','Easy','Intermediate','Hard','Very hard'][n-1]}`,String(p.difficulty))).join('')}</select></label><label for="edit-source">Source<input id="edit-source" list="sources" value="${esc(p.source)}" maxlength="160"><datalist id="sources">${[...session.sources,'Community'].map((s:string)=>`<option value="${esc(s)}">`).join('')}</datalist></label><label for="keywords">Keywords<input id="keywords" value="${esc(p.keywords.join(', '))}" placeholder="probability, integers…"><span class="field-help">Separate with commas.</span></label></div>
    ${p.legacy?`<details class="source-details"><summary>Original source details</summary><p>${p.legacy.sources.map((s:any)=>`${esc(s.title)} · Problem ${esc(s.number)} · PDF page ${s.page}`).join('<br>')}</p><p class="muted">${esc(p.legacy.note)}</p><a class="text-link" href="${esc(p.legacy.reviewUrl)}" target="_blank" rel="noopener">Open original review & reference PDF ↗</a></details>`:''}
    <section class="editor-panel"><div class="editor-toolbar"><div class="segmented">${['fr','en'].map(l=>`<button data-editor-lang="${l}" aria-pressed="${l===editorLanguage}">${l==='fr'?'French':'English'} ${p.versions[l].approved?'✓':''}</button>`).join('')}</div><label class="import-button" for="tex-file">Import .tex ↗<input type="file" id="tex-file" accept=".tex,text/plain"></label></div>
    <div class="editor-title"><label for="problem-title">Title — ${editorLanguage==='fr'?'French':'English'}<input id="problem-title" value="${esc(v.title)}" maxlength="300" placeholder="Problem title"></label></div>
    <div class="editor-columns"><div class="latex-pane"><label for="latex">LATEX STATEMENT</label><textarea id="latex" spellcheck="false" placeholder="Write your statement here. Use $…$ for formulas.">${esc(v.latex)}</textarea><span class="field-help">Text, formulas and figures. <a href="#/aide" target="_blank">Supported commands ↗</a></span></div><div class="preview-pane"><p class="eyebrow">STATEMENT PREVIEW</p><div id="latex-preview" class="math-content"></div></div></div>
    ${session.user.admin?`<div class="approval"><label class="check"><input id="approved" type="checkbox" ${v.approved?'checked':''}><span>I have verified this ${editorLanguage.toUpperCase()} version and approve it for publication.</span></label><p class="field-help">Only checked versions will be published. Verify each language separately.</p></div>`:''}</section>
    <section class="attachments"><div><h2>Figures</h2><p class="muted">Plain SVG, PNG or JPEG · Up to 2 MB per image</p><label class="button secondary small upload-label" for="figure-file">＋ Add figure<input id="figure-file" type="file" accept=".svg,.png,.jpg,.jpeg"></label></div><div class="asset-list">${Object.entries(p.assets).map(([name,a]:any)=>`<div class="asset"><img src="${esc(a.url)}" alt="${esc(name)}"><div><strong>${esc(name)}</strong><button class="text-link" data-insert="${esc(name)}">Insert into statement →</button></div></div>`).join('')||'<p class="muted">No figures attached.</p>'}</div></section>
    ${session.user.admin?`<label class="review-note" for="review-note">Note to author<textarea id="review-note" rows="3" placeholder="Describe any changes needed.">${esc(p.reviewNote||'')}</textarea></label>`:''}
    <div class="save-bar"><span id="save-state">${dirty?'Unsaved changes':'Last saved: '+date(p.updated)}</span><div class="button-row"><button class="button secondary" data-save="save">Save</button>${session.user.admin?'<button class="button" data-save="publish">Save & publish ↗</button><button class="text-link" data-save="return">Return to author</button>':'<button class="button" data-save="submit">Submit for review →</button>'}</div></div>
    <div class="editor-bottom"><button class="text-link" data-action="history">Revision history</button>${session.user.admin&&p.hasPublished?'<button class="text-link danger" data-save="unpublish">Unpublish</button>':!p.hasPublished?'<button class="text-link danger" data-action="delete-draft">Delete draft</button>':''}</div><div id="history"></div>`,session.user.admin?'review':'mine');
    preview();
}
function preview(){const v={latex:value('latex')};try{$('#latex-preview').innerHTML=v.latex?math(v,problem.assets):'<p class="preview-placeholder">Statement preview</p>';}catch(error:any){$('#latex-preview').innerHTML=`<p class="notice error">${esc(error.message)}</p>`;}}
async function saveProblem(action:string) {
    collectEditor();
    if(action==='unpublish'&&!confirm('Unpublish this problem? The draft will be kept.'))return;
    if(action==='submit'||action==='publish')for(const [lang,v] of Object.entries(problem.versions) as any){if(action==='submit'||v.approved){try{math(v,problem.assets);}catch(error:any){message(`${lang.toUpperCase()} : ${error.message}`,true);return;}}}
    const buttons=document.querySelectorAll<HTMLButtonElement>('[data-save]');buttons.forEach(b=>b.disabled=true);
    try{problem=await api('problems/'+problem.id,{...problem,action});dirty=false;showEditor();toast(({save:'Draft saved.',submit:'Submitted for review.',publish:'Verified versions published.',return:'Returned to author.',unpublish:'Problem unpublished.'} as any)[action]);}catch(error:any){message(error.message,true);}finally{buttons.forEach(b=>b.disabled=false);}
}
function profile() {
    if(!session.user){routeTo('/connexion');return;}const u=session.user;avatar=0;
    shell(`${intro('My profile')}<div class="profile-grid"><section class="panel"><h2>Your profile</h2>${notice()}<form id="profile-form"><div class="avatar-editor">${u.avatar?`<img id="avatar-preview" src="${esc(u.avatar)}" alt="Your profile image">`:`<span id="avatar-placeholder">${esc(u.pseudo.slice(0,1).toUpperCase())}</span>`}<div><label class="button secondary small upload-label" for="avatar-file">Choose image<input type="file" id="avatar-file" accept=".png,.jpg,.jpeg,.svg"></label><p class="field-help">A portrait or drawing · Up to 2 MB</p></div></div>${field('pseudo','Display name','text',`required minlength="2" maxlength="40" value="${esc(u.pseudo)}"`)}<label>Email address<input type="email" value="${esc(u.email)}" disabled></label><label class="check"><input type="checkbox" id="notifications" ${u.notifications?'checked':''}><span>Email me when a new problem is published.</span></label><button class="button">Save preferences</button></form></section><aside class="panel account-panel"><p class="eyebrow">ACCOUNT</p><h3>${u.admin?'Administrator':'Member'}</h3><a href="#/mot-de-passe">Change password →</a><button class="button secondary" data-action="logout">Sign out</button>${!u.admin?'<details class="delete-account"><summary>Delete account</summary><p>Your profile and drafts will be deleted. Published problems remain available, attributed to “Deleted account”.</p><label for="delete-password">Confirm your password<input id="delete-password" type="password" autocomplete="current-password"></label><button class="button danger" data-action="delete-account">Delete permanently</button></details>':''}</aside></div>`);
    $('#profile-form').onsubmit=async(e:Event)=>{e.preventDefault();try{const data:any={pseudo:value('pseudo'),notifications:checked('notifications')};if(avatar)data.avatar=avatar;session.user=await api('profile',data);profile();toast('Profile saved.');}catch(error:any){message(error.message,true);}};
}
function help() {shell(`${intro('LaTeX & figures')}<div class="help-grid"><section class="panel"><h2>Text and formulas</h2><p>Type a statement or import a .tex file. The preamble and document wrapper are removed on import.</p><pre>Find the integers $n$ for which $n^2 + 1$ is prime.

\\[
  a^2 + b^2 = c^2
\\]</pre><p>Inline formulas: <code>$…$</code> or <code>\\(…\\)</code>. Display formulas: <code>\\[…\\]</code> or <code>$$…$$</code>. Lists using <code>itemize</code> are supported.</p><p>For a price, write <code>\\$ 100</code>.</p></section><section class="panel"><h2>Figures in the statement</h2><p>Upload an image, then select “Insert into statement”.</p><pre>See figure~\\ref{fig:example}.

\\begin{figure}
\\centering
\\includegraphics[width=0.7\\linewidth]{figure-1.svg}
\\caption{A short caption}
\\label{fig:example}
\\end{figure}</pre><p>Numbering starts at 1 for each problem. Use the exact uploaded filename.</p></section><section class="panel"><h2>Image files</h2><p>Use plain SVG for geometric drawings, containing shapes and paths without scripts, CSS or external resources. Convert text to paths in your drawing software if needed.</p><p>PNG and JPEG are also supported. Limits: 2 MB per image, 20 figures per problem. Compile TikZ separately and export the drawing as SVG or PNG.</p></section><section class="panel"><h2>Review and publication</h2><ol><li>Save your draft.</li><li>Check the preview in each language.</li><li>Submit for review.</li><li>An administrator can edit, return or publish the verified versions.</li></ol><p>LaTeX is used for statements and mathematics. Arbitrary packages, custom macros and system commands are not executed.</p></section></div>`);}
function privacy(){shell(`${intro('Privacy & contributions')}<article class="panel prose"><h2>Your account</h2><p>Your email address is used to sign in and confirm your account. It is not shown to other members. Your display name appears beside your published problems. WordPress stores passwords as hashes.</p><h2>Your contributions</h2><p>Only submit statements and figures you are permitted to share. Include sources and credits. Submitting a problem authorises its review, correction and publication on this website and its associated apps.</p><p>Administrators may publish minor corrections directly. A substantial mathematical change should be returned to the contributor with an explanation.</p><h2>Private information</h2><p>Drafts are visible to their author and administrators. Members can read published versions. Your progress is private. Images are accessible only to people allowed to view the corresponding problem.</p><h2>Emails and account deletion</h2><p>New-problem notifications are optional and can be disabled in your profile. Deleting your account removes your profile and drafts. Published contributions remain available with anonymous attribution.</p><h2>Cookies</h2><p>The site uses the WordPress cookies required for sign-in. It includes no advertising or analytics tools.</p>${session.local?'<div class="notice soft">Local preview: no emails are sent. The site operator’s contact details and legal notice must be added before public launch.</div>':''}</article>`);}
async function mailbox(){if(!session.user?.admin||!session.local){routeTo('/');return;}const mail=await api('mailbox');shell(`${intro('Test inbox')}<div class="mailbox">${mail.length?mail.map((m:any)=>`<article class="panel"><p class="small muted">${esc(String(m.to))} · ${date(m.date)}</p><h2>${esc(m.subject)}</h2><pre>${esc(m.message).replace(/https?:\/\/[^\s<&]+/g,(url:string)=>`<a href="${url}" target="_blank" rel="noopener">${url}</a>`)}</pre></article>`).join(''):empty('No emails yet','Confirmation emails for test accounts appear here.')}</div>`);}
async function route(){
    const current=location.hash||'#/';if(dirty&&current!==lastRoute&&!confirm('Leave without saving your changes?')){history.replaceState(null,'',lastRoute);return;}
    lastRoute=current;dirty=false;routeSequence++;const [path,query]=current.replace(/^#/,'').split('?');const parts=path.split('/').filter(Boolean);const page=parts[0]||'';document.title='Le Problème du Jour';window.scrollTo(0,0);
    try{if(!session)session=await api('session');
        if(['connexion','inscription','mot-de-passe','renvoyer','reinitialiser','confirmer'].includes(page))auth(page,new URLSearchParams(query));
        else if(page==='mes-propositions'){filters.status='';filters.progress='';await collection('mine');}
        else if(page==='administration'){filters.status='';filters.progress='';await collection('review');}
        else if(page==='probleme')await reader(parts[1]);else if(page==='editer')await editor(parts[1]);else if(page==='profil')profile();else if(page==='aide')help();else if(page==='confidentialite')privacy();else if(page==='courrier')await mailbox();else {filters.status='';await collection();}
    }catch(error:any){shell(empty('Page unavailable',esc(error.message),'<a class="button" href="#/">Back to problems</a>'));}
}
root.addEventListener('input',(e)=>{
    const target=e.target as HTMLInputElement;
    if(target.id==='search'){filters.search=target.value;drawList();}
    if($('#latex')&&['latex','problem-title','edit-category','edit-difficulty','edit-source','keywords','approved','review-note'].includes(target.id)){
        dirty=true;$('#save-state').textContent='Unsaved changes';
        if(['latex','problem-title'].includes(target.id)){problem.versions[editorLanguage].approved=false;if($('#approved'))$('#approved').checked=false;}
        if(['edit-category','edit-difficulty','edit-source','keywords'].includes(target.id)){for(const v of Object.values(problem.versions) as any)v.approved=false;if($('#approved'))$('#approved').checked=false;}
        if(target.id==='latex')preview();
    }
});
root.addEventListener('change',async(e)=>{
    const target=e.target as HTMLInputElement;
    if(['category','difficulty','source','progress','status','sort'].includes(target.id)){(filters as any)[target.id]=target.value;drawList();}
    try{
        if(target.id==='tex-file'&&target.files?.[0]){if(target.files[0].size>60000)throw Error('The .tex file must be under 60 KB.');let text=await target.files[0].text();const body=/\\begin\{document\}([\s\S]*?)\\end\{document\}/.exec(text);if(body)text=body[1].trim();$('#latex').value=text;problem.versions[editorLanguage].approved=false;if($('#approved'))$('#approved').checked=false;dirty=true;$('#save-state').textContent='Unsaved changes';preview();}
        if((target.id==='figure-file'||target.id==='avatar-file')&&target.files?.[0]){
            if(target.files[0].size>2*1024*1024)throw Error('Each image must be no larger than 2 MB.');
            const isFigure=target.id==='figure-file';if(isFigure)collectEditor();const data=new FormData();data.append('file',target.files[0]);data.append('problem',isFigure?String(problem.id):'0');if(isFigure)data.append('revision',String(problem.revision));target.disabled=true;
            const uploaded=await api('assets',data);
            if(isFigure){problem.assets[uploaded.name]=uploaded.asset;problem.revision=uploaded.revision;showEditor();toast('Figure added. Select “Insert into statement”.');}
            else{avatar=uploaded.asset.id;const existing=$('#avatar-preview')||$('#avatar-placeholder');existing.outerHTML=`<img id="avatar-preview" src="${esc(uploaded.asset.url)}" alt="New profile image">`;toast('Image uploaded. Save your preferences.');}
        }
    }catch(error:any){message(error.message,true);}finally{target.disabled=false;}
});
root.addEventListener('click',async(e)=>{
    const b=(e.target as HTMLElement).closest<HTMLElement>('[data-action],[data-save],[data-reader-lang],[data-editor-lang],[data-insert],[data-progress],[data-source]');if(!b)return;
    try{
        if(b.dataset.action==='previous-page'||b.dataset.action==='next-page'){listPage+=b.dataset.action==='next-page'?1:-1;drawList(false);$('#problem-list').scrollIntoView({block:'start'});return;}
        if(b.dataset.save){await saveProblem(b.dataset.save);return;}
        if(b.dataset.readerLang){language=b.dataset.readerLang;showReader();return;}
        if(b.dataset.editorLang){collectEditor();editorLanguage=b.dataset.editorLang;showEditor();return;}
        if(b.dataset.insert){const text=$('#latex');const label='fig:'+b.dataset.insert.replace(/\.[^.]+$/,'');text.setRangeText(`\n\n\\begin{figure}\n\\centering\n\\includegraphics[width=0.7\\linewidth]{${b.dataset.insert}}\n\\caption{A caption}\n\\label{${label}}\n\\end{figure}\n`,text.selectionStart,text.selectionEnd,'end');problem.versions[editorLanguage].approved=false;if($('#approved'))$('#approved').checked=false;dirty=true;$('#save-state').textContent='Unsaved changes';preview();text.focus();return;}
        if(b.dataset.progress){await api('problems/'+problem.id+'/progress',{progress:b.dataset.progress});problem.progress=b.dataset.progress;showReader();return;}
        if(b.dataset.source){filters.source=b.dataset.source;$('#source').value=b.dataset.source;drawList();return;}
        if(b.dataset.action==='new'){if(!session.user){routeTo('/connexion');return;}b.setAttribute('disabled','');const created=await api('problems',{});routeTo('/editer/'+created.id);}
        if(b.dataset.action==='reset-filters'){filters={search:'',category:'',difficulty:'',source:'',progress:'',status:'',sort:'newest'};for(const [id,v] of Object.entries(filters))if($('#'+id))$('#'+id).value=v;drawList();}
        if(b.dataset.action==='pick'){const items=filtered();if(!items.length){toast('No problems match these filters.');return;}routeTo('/probleme/'+items[Math.floor(Math.random()*items.length)].id);}
        if(b.dataset.action==='logout'){await api('auth/logout',{});location.hash='#/';location.reload();}
        if(b.dataset.action==='delete-draft'&&confirm('Delete this draft, its figures and revision history?')){await api('problems/'+problem.id,{},'DELETE');dirty=false;routeTo('/mes-propositions');toast('Draft deleted.');}
        if(b.dataset.action==='delete-account'&&confirm('Permanently delete your account and drafts?')){await api('account',{password:value('delete-password')},'DELETE');location.hash='#/';location.reload();}
        if(b.dataset.action==='history'){const entries=await api('problems/'+problem.id+'/history');$('#history').innerHTML=`<section class="panel"><h2>History</h2>${entries.length?entries.map((entry:any)=>`<details class="history-entry"><summary>${esc(actions[entry.action]||entry.action)} · ${date(entry.date)} · ${esc(entry.by)}</summary><p>Revision ${entry.snapshot.revision} — ${esc(titleOf(entry.snapshot))}</p>${Object.entries(entry.snapshot.versions).map(([lang,v]:any)=>`<h3>${lang.toUpperCase()} ${v.approved?'✓':''}</h3><pre>${esc(v.title)}\n\n${esc(v.latex)}</pre>`).join('')}</details>`).join(''):'<p>No saved revisions yet.</p>'}</section>`;}
    }catch(error:any){message(error.message,true);}finally{b.removeAttribute('disabled');}
});
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
window.addEventListener('hashchange',route);
route();
