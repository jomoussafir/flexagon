import { render, escapeHTML as esc } from '../../../../shared/latex/render.ts';

declare global { interface Window { LPDJ: any } }
const cfg = window.LPDJ;
let session = cfg.session;
const root = document.querySelector('#app')!;
const categories: Record<string,string> = {Algebra:'Algèbre',Geometry:'Géométrie','Number Theory':'Théorie des nombres',Combinatorics:'Combinatoire',Logic:'Logique'};
const progress: Record<string,string> = {unseen:'Non vu',bookmarked:'Favori',attempted:'Essayé',solved:'Résolu'};
const statuses: Record<string,string> = {draft:'Brouillon',submitted:'À valider',returned:'À corriger',published:'Publié'};
const actions: Record<string,string> = {save:'Enregistrement',submit:'Soumission',publish:'Publication',return:'Retour à l’auteur',unpublish:'Retrait'};
let listing: any = null, problem: any = null, language = 'fr', editorLanguage = 'fr', dirty = false, routeSequence = 0;
let filters = {search:'',category:'',difficulty:'',source:'',progress:'',status:'',sort:'newest'};
let lastRoute = location.hash || '#/';
let avatar = 0;
const $ = (selector: string) => document.querySelector(selector) as any;
const value = (id: string) => ($('#'+id) as HTMLInputElement)?.value ?? '';
const checked = (id: string) => !!($('#'+id) as HTMLInputElement)?.checked;
const titleOf = (p: any) => p.versions.fr?.title || p.versions.en?.title || 'Sans titre';
const date = (s: string) => new Date(s).toLocaleDateString('fr-FR', {day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'});
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
    if(!response.ok)throw new Error(result.message||'Une erreur est survenue. Réessayez.');
    return result;
}
function shell(content:string, active='') {
    const user=session.user;
    root.innerHTML=`${session.local?`<div class="local-banner"><span class="local-dot"></span>Aperçu local · Les e-mails restent sur ce Mac${user?.admin?'<a href="#/courrier">Boîte e-mail de test ↗</a>':''}</div>`:''}
    <header class="header container"><a class="brand" href="#/" aria-label="Le Problème du Jour — Accueil"><img src="${cfg.logo}" alt="" width="52" height="52"><span>Le Problème du Jour<small>LA COMMUNAUTÉ MATHÉMATIQUE</small></span></a>
    <nav aria-label="Navigation principale"><a ${active==='collection'?'aria-current="page"':''} href="#/">Problèmes</a>${user?`<a ${active==='mine'?'aria-current="page"':''} href="#/mes-propositions">Mes propositions</a>${user.admin?`<a ${active==='review'?'aria-current="page"':''} href="#/administration">Validation</a>`:''}<a class="profile-link" href="#/profil" aria-label="Mon profil">${user.avatar?`<img src="${esc(user.avatar)}" alt="">`:`<span>${esc(user.pseudo.slice(0,1).toUpperCase())}</span>`}<span>${esc(user.pseudo)}</span></a>`:`<a href="#/connexion">Connexion</a><a class="button small" href="#/inscription">Créer un compte</a>`}</nav></header>
    <main id="main" class="container" tabindex="-1">${content}</main>
    <footer class="footer container"><span>Le Problème du Jour <span class="footer-dot">·</span> Chercher. Partager. Comprendre.</span><a href="#/aide">LaTeX & figures</a><a href="#/confidentialite">Confidentialité & contributions</a></footer>`;
}
function intro(kicker:string,title:string,subtitle:string,extra='') { return `<div class="page-heading"><div><p class="eyebrow">${kicker}</p><h1>${title}</h1><p class="muted">${subtitle}</p></div>${extra}</div>`; }
function notice() { return '<div id="form-message" role="alert" tabindex="-1"></div>'; }
function field(id:string,label:string,type='text',extra='') { return `<label for="${id}">${label}<input id="${id}" name="${id}" type="${type}" ${extra}></label>`; }
function langSquares(p:any) { return `<span class="language-squares" aria-label="Versions">${['fr','en'].map(l=>`<span class="lang-square level-${p.difficulty} ${p.versions[l]?.title?'':'absent'}" title="${l.toUpperCase()} · ${p.versions[l]?.approved?'validé':'non validé'} · niveau ${p.difficulty}">${l.toUpperCase()}${p.versions[l]?.approved?'<b aria-label="validé">✓</b>':''}</span>`).join('')}</span>`; }
function sourceOrder(a:string,b:string) { const names=session.sources;const x=names.indexOf(a),y=names.indexOf(b);return (x<0?99:x)-(y<0?99:y)||a.localeCompare(b,'fr'); }
function empty(title:string,text:string,button='') { return `<div class="empty"><div class="empty-symbol" aria-hidden="true">∅</div><h2>${title}</h2><p>${text}</p>${button}</div>`; }
function gated() {
    shell(`<section class="welcome"><div><p class="eyebrow">UN ESPACE POUR LES ESPRITS CURIEUX</p><h1>Les bonnes questions<br>se partagent.</h1><p class="lead">Proposez un problème, prenez le temps de chercher.<br>Une collection construite ensemble, relue avec soin.</p><div class="button-row"><a class="button" href="#/inscription">Rejoindre la communauté <span>↗</span></a><a class="text-link" href="#/connexion">J’ai déjà un compte →</a></div><p class="small muted">Un compte pour lire, proposer et retrouver vos problèmes.</p></div><div class="hero-logo"><img src="${cfg.logo}" alt="Pavage du disque de Poincaré" width="340" height="340"><span>À chaque problème, une nouvelle perspective.</span></div></section>
    <div class="principles"><article><span>01</span><h3>Partagez une idée</h3><p>Un énoncé en français ou en anglais, écrit en LaTeX et accompagné de vos figures.</p></article><article><span>02</span><h3>Une relecture attentive</h3><p>Chaque proposition est vérifiée par un administrateur avant sa publication.</p></article><article><span>03</span><h3>Cherchez à votre rythme</h3><p>Cinq niveaux de difficulté, des mots-clés et votre progression personnelle.</p></article></div>`, 'collection');
}
async function collection(scope='published') {
    if(!session.user){gated();return;}
    if(scope==='review'&&!session.user.admin){shell(empty('Accès réservé','Cette page est réservée aux administrateurs.'));return;}
    const seq=routeSequence;
    shell(intro(scope==='published'?'LA COLLECTION':scope==='mine'?'VOTRE ATELIER':'ESPACE ADMINISTRATEUR',scope==='published'?'Un problème. À vous de jouer.':scope==='mine'?'Mes propositions':'Relire, puis partager.',scope==='published'?'Des problèmes pour chercher, réfléchir et progresser.':scope==='mine'?'Vos brouillons, vos échanges et vos problèmes publiés.':'Vérifiez chaque version avant de la rendre accessible à la communauté.')+'<p class="loading">Chargement…</p>',scope==='published'?'collection':scope==='mine'?'mine':'review');
    listing=await api('problems?scope='+scope);if(seq!==routeSequence)return;
    const total=listing.published, pending=listing.items.filter((p:any)=>p.state==='submitted').length;
    shell(intro(scope==='published'?'LA COLLECTION':scope==='mine'?'VOTRE ATELIER':'ESPACE ADMINISTRATEUR',scope==='published'?'Un problème. À vous de jouer.':scope==='mine'?'Mes propositions':'Relire, puis partager.',scope==='published'?'Des problèmes pour chercher, réfléchir et progresser.':scope==='mine'?'Chaque idée commence par un brouillon.':'Une validation indépendante pour les versions françaises et anglaises.',`<button class="button" data-action="new">＋ Proposer un problème</button>`)+
    `<section class="stats"><div><strong>${scope==='published'?total:listing.total}</strong><span>${scope==='published'?'problèmes publiés':'propositions'}</span></div><div><strong>${scope==='review'?pending:Object.keys(listing.sources).length}</strong><span>${scope==='review'?'à valider':'sources'}</span></div><div><strong>1–5</strong><span>niveaux de difficulté</span></div><p>${scope==='published'?'Une collection qui grandit avec vos contributions.':scope==='review'?'Les brouillons restent privés. Seules les versions cochées sont publiées.':'Vous pouvez reprendre une proposition à tout moment.'}</p></section>
    ${scope==='published'&&total?`<div class="source-counts">${Object.entries(listing.sources).sort(([a],[b])=>sourceOrder(a,b)).map(([s,c])=>`<button data-source="${esc(s)}">${esc(s)} <b>${c}</b></button>`).join('')}</div>`:''}
    <section class="collection"><div class="section-label"><h2>${scope==='published'?'Explorer les problèmes':scope==='mine'?'Vos problèmes':'Toutes les propositions'}</h2>${scope==='published'?'<button class="text-link" data-action="pick">Au hasard ↗</button>':''}</div>
    <div class="filters"><label class="search-label" for="search">Rechercher<input id="search" type="search" placeholder="Titre, mot-clé…" value="${esc(filters.search)}"></label>
    <label for="category">Catégorie<select id="category">${option('','Toutes',filters.category)}${Object.entries(categories).map(([v,l])=>option(v,l,filters.category)).join('')}</select></label>
    <label for="difficulty">Difficulté<select id="difficulty">${option('','Tous les niveaux',filters.difficulty)}${[1,2,3,4,5].map(n=>option(String(n),`Niveau ${n}`,filters.difficulty)).join('')}</select></label>
    <label for="source">Source<select id="source">${option('','Toutes les sources',filters.source)}${[...new Set(listing.items.map((p:any)=>p.source))].sort(sourceOrder).map((s:any)=>option(s,s,filters.source)).join('')}</select></label>
    <label for="${scope==='published'?'progress':'status'}">${scope==='published'?'Progression':'Statut'}<select id="${scope==='published'?'progress':'status'}">${option('','Tous',scope==='published'?filters.progress:filters.status)}${Object.entries(scope==='published'?progress:statuses).map(([v,l])=>option(v,l,scope==='published'?filters.progress:filters.status)).join('')}</select></label></div>
    <div class="list-tools"><span id="result-count" aria-live="polite"></span><label for="sort">Trier par <select id="sort">${[['newest','Plus récents'],['difficulty-asc','Difficulté croissante'],['difficulty-desc','Difficulté décroissante'],['fr','Validation FR'],['en','Validation EN'],['title','Titre']].map(([v,l])=>option(v,l,filters.sort)).join('')}</select></label><button class="text-link" data-action="reset-filters">Effacer les filtres</button></div><div id="problem-list" data-scope="${scope}"></div></section>`,scope==='published'?'collection':scope==='mine'?'mine':'review');
    drawList();
}
function filtered() {
    return listing.items.filter((p:any)=>!filters.search||[...Object.values(p.versions).map((v:any)=>v.title),...p.keywords].join(' ').toLocaleLowerCase().includes(filters.search.toLocaleLowerCase())).filter((p:any)=>!filters.category||p.category===filters.category).filter((p:any)=>!filters.difficulty||p.difficulty===Number(filters.difficulty)).filter((p:any)=>!filters.source||p.source===filters.source).filter((p:any)=>!filters.progress||p.progress===filters.progress).filter((p:any)=>!filters.status||p.state===filters.status).sort((a:any,b:any)=>filters.sort==='title'?titleOf(a).localeCompare(titleOf(b),'fr'):filters.sort==='difficulty-asc'?a.difficulty-b.difficulty:filters.sort==='difficulty-desc'?b.difficulty-a.difficulty:['fr','en'].includes(filters.sort)?Number(!!b.versions[filters.sort]?.approved)-Number(!!a.versions[filters.sort]?.approved):b.id-a.id);
}
function drawList() {
    const items=filtered(),scope=$('#problem-list').dataset.scope;
    $('#result-count').textContent=`${items.length} problème${items.length!==1?'s':''}`;
    $('#problem-list').innerHTML=items.length?`<div class="problem-table">${items.map((p:any)=>`<a class="problem-row" href="#/${scope==='published'?'probleme':'editer'}/${p.id}"><span class="problem-name"><strong>${esc(titleOf(p))}</strong><small>${esc(categories[p.category])} <span>·</span> ${esc(p.source)} ${scope!=='published'?`<span>·</span> ${esc(p.author)}`:''}</small></span><span class="level-label">Niveau ${p.difficulty}</span>${langSquares(p)}<span class="status ${scope==='published'?p.progress:p.state}">${scope==='published'?progress[p.progress]:statuses[p.state]}</span><span class="row-arrow">↗</span></a>`).join('')}</div>`:listing.total?empty('Aucun résultat','Essayez une autre combinaison de filtres.','<button class="button secondary" data-action="reset-filters">Effacer les filtres</button>'):empty(scope==='published'?'La collection commence avec vous.':'Votre prochain problème commence ici.',scope==='published'?'Aucun problème n’est encore publié. Proposez le premier : il sera relu avant d’apparaître ici.':'Importez un énoncé LaTeX ou écrivez-le directement dans votre atelier.','<button class="button" data-action="new">＋ Proposer un problème</button>');
}
function auth(kind:string,params:URLSearchParams) {
    const signup=kind==='inscription', login=kind==='connexion', forgot=kind==='mot-de-passe', resend=kind==='renvoyer', reset=kind==='reinitialiser', verify=kind==='confirmer';
    const heading=signup?'Rejoignez la communauté.':login?'Heureux de vous retrouver.':forgot?'Un nouveau départ.':resend?'Confirmez votre adresse.':reset?'Choisissez un mot de passe.':'Une dernière étape.';
    shell(`<div class="auth-layout"><aside><img src="${cfg.logo}" alt="" width="200" height="200"><p class="eyebrow">LE PROBLÈME DU JOUR</p><h2>Le plaisir de chercher.<br>Le plaisir de partager.</h2><p class="muted">Votre compte vous donne accès à la collection et à votre espace de contribution.</p></aside><section class="auth-card"><h1>${heading}</h1><p class="muted">${signup?'Un pseudo, un e-mail et un peu de curiosité.':verify?'Cliquez ci-dessous pour confirmer votre adresse e-mail.':'Votre e-mail est votre identifiant.'}</p>${notice()}<form id="auth-form" data-kind="${kind}">
    ${signup?field('pseudo','Pseudo','text','required minlength="2" maxlength="40" autocomplete="nickname"'):''}
    ${!reset&&!verify?field('email','Adresse e-mail','email','required autocomplete="email"'):''}
    ${signup||login||reset?field('password','Mot de passe','password',`required ${login?'':'minlength="12"'} maxlength="200" autocomplete="${login?'current-password':'new-password'}"`)+(!login?'<p class="field-help">Au moins 12 caractères.</p>':''):''}
    ${signup?'<label class="check"><input id="accept" type="checkbox" required><span>J’accepte les <a href="#/confidentialite" target="_blank">conditions de contribution et de confidentialité</a>.</span></label><label class="check"><input id="notifications" type="checkbox"><span>Me prévenir par e-mail des nouveaux problèmes.</span></label>':''}
    ${login?'<label class="check"><input id="remember" type="checkbox"><span>Rester connecté sur cet appareil</span></label>':''}
    <button class="button full" type="submit">${signup?'Créer mon compte':login?'Se connecter':verify?'Confirmer mon adresse':reset?'Enregistrer le mot de passe':'Envoyer le lien'} <span>→</span></button></form>
    <div class="auth-links">${login?'<a href="#/mot-de-passe">Mot de passe oublié ?</a><a href="#/renvoyer">Renvoyer la confirmation</a><p>Pas encore de compte ? <a href="#/inscription">Inscrivez-vous</a></p>':'<a href="#/connexion">← Retour à la connexion</a>'}</div></section></div>`);
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
    try{content=math(v,p.assets);}catch(error:any){content=`<p class="notice error">Le rendu de cet énoncé doit être corrigé : ${esc(error.message)}</p><pre>${esc(v.latex)}</pre>`;}
    shell(`<div class="reader-heading"><a class="text-link" href="#/">← La collection</a><span class="badge">${esc(categories[p.category])}</span><span class="muted">${esc(p.source)} · Niveau ${p.difficulty}</span></div>
    <article class="reading-card"><div class="reader-top"><p class="eyebrow">LE PROBLÈME DU JOUR</p>${Object.keys(p.versions).length>1?`<div class="segmented" aria-label="Langue">${Object.keys(p.versions).map(l=>`<button data-reader-lang="${l}" aria-pressed="${language===l}">${l.toUpperCase()}</button>`).join('')}</div>`:`<span class="small muted">${language.toUpperCase()}</span>`}</div><h1>${esc(v.title)}</h1><div class="math-content">${content}</div><div class="tags">${p.keywords.map((k:string)=>`<span>${esc(k)}</span>`).join('')}</div><div class="reader-foot"><span>Proposé par <strong>${esc(p.author)}</strong></span>${p.editable?`<a href="#/editer/${p.id}">Modifier →</a>`:''}</div></article>
    <section class="progress-card"><div><h2>Où en êtes-vous ?</h2><p class="muted">Votre progression reste personnelle.</p></div><div class="segmented progress-buttons">${Object.entries(progress).map(([key,label])=>`<button data-progress="${key}" aria-pressed="${p.progress===key}">${label}</button>`).join('')}</div></section>`,'collection');
}
async function editor(id:string) {
    if(!session.user){routeTo('/connexion');return;}
    const seq=routeSequence;problem=await api('problems/'+id+'?context=edit');if(seq!==routeSequence)return;
    editorLanguage=problem.versions.fr?.title||!problem.versions.en?.title?'fr':'en';dirty=false;showEditor();
}
function collectEditor() {
    if(!$('#problem-title'))return;
    const v=problem.versions[editorLanguage];v.title=value('problem-title');v.latex=value('latex');if(session.user.admin)v.approved=checked('approved');
    problem.category=value('edit-category');problem.difficulty=Number(value('edit-difficulty'));problem.source=value('edit-source');problem.keywords=value('keywords').split(',').map((s:string)=>s.trim()).filter(Boolean);if(session.user.admin)problem.reviewNote=value('review-note');
}
function showEditor() {
    const p=problem,v=p.versions[editorLanguage];
    shell(`${intro('L’ATELIER',titleOf(p)==='Sans titre'?'Une nouvelle proposition':esc(titleOf(p)),'Écrivez, prévisualisez et soumettez votre problème.',`<span class="status ${p.state}">${statuses[p.state]}</span>`)}
    ${p.hasPublished?`<div class="notice soft">Une version est en ligne. Vos modifications restent privées jusqu’à leur prochaine publication. <a href="#/probleme/${p.id}">Voir la version publiée →</a></div>`:''}
    ${p.reviewNote&&!session.user.admin?`<div class="notice soft"><strong>Note de l’administrateur</strong><p>${esc(p.reviewNote)}</p></div>`:''}
    ${notice()}<div class="editor-meta"><label for="edit-category">Catégorie<select id="edit-category">${Object.entries(categories).map(([key,label])=>option(key,label,p.category)).join('')}</select></label><label for="edit-difficulty">Difficulté<select id="edit-difficulty">${[1,2,3,4,5].map(n=>option(String(n),`${n} — ${['Accessible','Facile','Intermédiaire','Difficile','Très difficile'][n-1]}`,String(p.difficulty))).join('')}</select></label><label for="edit-source">Source<input id="edit-source" list="sources" value="${esc(p.source)}" maxlength="160"><datalist id="sources">${[...session.sources,'Communauté'].map((s:string)=>`<option value="${esc(s)}">`).join('')}</datalist></label><label for="keywords">Mots-clés<input id="keywords" value="${esc(p.keywords.join(', '))}" placeholder="probabilité, entiers…"><span class="field-help">Séparés par des virgules.</span></label></div>
    <section class="editor-panel"><div class="editor-toolbar"><div class="segmented">${['fr','en'].map(l=>`<button data-editor-lang="${l}" aria-pressed="${l===editorLanguage}">${l==='fr'?'Français':'English'} ${p.versions[l].approved?'✓':''}</button>`).join('')}</div><label class="import-button" for="tex-file">Importer un .tex ↗<input type="file" id="tex-file" accept=".tex,text/plain"></label></div>
    <div class="editor-title"><label for="problem-title">Titre de la version ${editorLanguage==='fr'?'française':'anglaise'}<input id="problem-title" value="${esc(v.title)}" maxlength="200" placeholder="Un titre clair pour votre problème"></label></div>
    <div class="editor-columns"><div class="latex-pane"><label for="latex">ÉNONCÉ LATEX</label><textarea id="latex" spellcheck="false" placeholder="Écrivez votre énoncé ici. Utilisez $…$ pour les formules.">${esc(v.latex)}</textarea><span class="field-help">Texte, formules et figures. <a href="#/aide" target="_blank">Voir les commandes prises en charge ↗</a></span></div><div class="preview-pane"><p class="eyebrow">APERÇU DE L’ÉNONCÉ</p><div id="latex-preview" class="math-content"></div></div></div>
    ${session.user.admin?`<div class="approval"><label class="check"><input id="approved" type="checkbox" ${v.approved?'checked':''}><span>J’ai vérifié cette version ${editorLanguage.toUpperCase()} et j’autorise sa publication.</span></label><p class="field-help">Seules les versions cochées seront publiées. Vérifiez les deux langues séparément.</p></div>`:''}</section>
    <section class="attachments"><div><h2>Figures</h2><p class="muted">SVG simple, PNG ou JPEG · 2 Mo maximum par image</p><label class="button secondary small upload-label" for="figure-file">＋ Ajouter une figure<input id="figure-file" type="file" accept=".svg,.png,.jpg,.jpeg"></label></div><div class="asset-list">${Object.entries(p.assets).map(([name,a]:any)=>`<div class="asset"><img src="${esc(a.url)}" alt="${esc(name)}"><div><strong>${esc(name)}</strong><button class="text-link" data-insert="${esc(name)}">Insérer dans l’énoncé →</button></div></div>`).join('')||'<p class="muted">Vos figures apparaîtront ici.<br>Elles resteront attachées à ce problème.</p>'}</div></section>
    ${session.user.admin?`<label class="review-note" for="review-note">Note à l’auteur<textarea id="review-note" rows="3" placeholder="Précisez les corrections demandées, si nécessaire.">${esc(p.reviewNote||'')}</textarea></label>`:''}
    <div class="save-bar"><span id="save-state">${dirty?'Modifications non enregistrées':'Dernière sauvegarde : '+date(p.updated)}</span><div class="button-row"><button class="button secondary" data-save="save">Enregistrer</button>${session.user.admin?'<button class="button" data-save="publish">Enregistrer & publier ↗</button><button class="text-link" data-save="return">Retourner à l’auteur</button>':'<button class="button" data-save="submit">Soumettre à validation →</button>'}</div></div>
    <div class="editor-bottom"><button class="text-link" data-action="history">Historique des versions</button>${session.user.admin&&p.hasPublished?'<button class="text-link danger" data-save="unpublish">Retirer de la publication</button>':!p.hasPublished?'<button class="text-link danger" data-action="delete-draft">Supprimer le brouillon</button>':''}</div><div id="history"></div>`,session.user.admin?'review':'mine');
    preview();
}
function preview(){const v={latex:value('latex')};try{$('#latex-preview').innerHTML=v.latex?math(v,problem.assets):'<p class="preview-placeholder">Votre énoncé prend forme ici…</p>';}catch(error:any){$('#latex-preview').innerHTML=`<p class="notice error">${esc(error.message)}</p>`;}}
async function saveProblem(action:string) {
    collectEditor();
    if(action==='unpublish'&&!confirm('Retirer ce problème de la collection ? Le brouillon sera conservé.'))return;
    if(action==='submit'||action==='publish')for(const [lang,v] of Object.entries(problem.versions) as any){if(action==='submit'||v.approved){try{math(v,problem.assets);}catch(error:any){message(`${lang.toUpperCase()} : ${error.message}`,true);return;}}}
    const buttons=document.querySelectorAll<HTMLButtonElement>('[data-save]');buttons.forEach(b=>b.disabled=true);
    try{problem=await api('problems/'+problem.id,{...problem,action});dirty=false;showEditor();toast(({save:'Brouillon enregistré.',submit:'Problème soumis à validation.',publish:'Les versions validées sont publiées.',return:'Problème retourné à l’auteur.',unpublish:'Problème retiré de la collection.'} as any)[action]);}catch(error:any){message(error.message,true);}finally{buttons.forEach(b=>b.disabled=false);}
}
function profile() {
    if(!session.user){routeTo('/connexion');return;}const u=session.user;avatar=0;
    shell(`${intro('VOTRE ESPACE','Mon profil','Votre identité dans la communauté, vos préférences et votre compte.')}<div class="profile-grid"><section class="panel"><h2>Votre profil</h2>${notice()}<form id="profile-form"><div class="avatar-editor">${u.avatar?`<img id="avatar-preview" src="${esc(u.avatar)}" alt="Votre image de profil">`:`<span id="avatar-placeholder">${esc(u.pseudo.slice(0,1).toUpperCase())}</span>`}<div><label class="button secondary small upload-label" for="avatar-file">Choisir une image<input type="file" id="avatar-file" accept=".png,.jpg,.jpeg,.svg"></label><p class="field-help">Un portrait ou un dessin · 2 Mo maximum</p></div></div>${field('pseudo','Pseudo','text',`required minlength="2" maxlength="40" value="${esc(u.pseudo)}"`)}<label>Adresse e-mail<input type="email" value="${esc(u.email)}" disabled></label><label class="check"><input type="checkbox" id="notifications" ${u.notifications?'checked':''}><span>Recevoir un e-mail lorsqu’un nouveau problème est publié.</span></label><button class="button">Enregistrer les préférences</button></form></section><aside class="panel account-panel"><p class="eyebrow">VOTRE COMPTE</p><h3>${u.admin?'Administrateur':'Membre de la communauté'}</h3><p class="muted">${u.admin?'Vous pouvez proposer, relire et publier les problèmes.':'Vos propositions sont relues avant publication.'}</p><a href="#/mot-de-passe">Changer mon mot de passe →</a><button class="button secondary" data-action="logout">Se déconnecter</button>${!u.admin?'<details class="delete-account"><summary>Supprimer mon compte</summary><p>Vos brouillons et votre profil seront supprimés. Vos problèmes déjà publiés resteront disponibles, sous « Compte supprimé ».</p><label for="delete-password">Confirmez votre mot de passe<input id="delete-password" type="password" autocomplete="current-password"></label><button class="button danger" data-action="delete-account">Supprimer définitivement</button></details>':''}</aside></div>`);
    $('#profile-form').onsubmit=async(e:Event)=>{e.preventDefault();try{const data:any={pseudo:value('pseudo'),notifications:checked('notifications')};if(avatar)data.avatar=avatar;session.user=await api('profile',data);profile();toast('Profil enregistré.');}catch(error:any){message(error.message,true);}};
}
function help() {shell(`${intro('GUIDE DE CONTRIBUTION','Vos idées, en LaTeX.','Écrivez directement ou importez un fichier .tex. L’aperçu se met à jour pendant votre saisie.')}<div class="help-grid"><section class="panel"><h2>Texte et formules</h2><p>Écrivez l’énoncé seul : le préambule et l’environnement document sont retirés lors de l’import.</p><pre>Déterminer les entiers $n$ tels que $n^2 + 1$ soit premier.

\\[
  a^2 + b^2 = c^2
\\]</pre><p>Formules en ligne : <code>$…$</code> ou <code>\\(…\\)</code>. Formules centrées : <code>\\[…\\]</code> ou <code>$$…$$</code>. Les listes <code>itemize</code> sont acceptées.</p><p>Pour un prix, écrivez <code>\\$ 100</code>.</p></section><section class="panel"><h2>Des figures dans l’énoncé</h2><p>Téléversez une figure puis cliquez sur « Insérer dans l’énoncé ».</p><pre>Voir la figure~\\ref{fig:exemple}.

\\begin{figure}
\\centering
\\includegraphics[width=0.7\\linewidth]{figure-1.svg}
\\caption{Une légende courte}
\\label{fig:exemple}
\\end{figure}</pre><p>La numérotation recommence à 1 dans chaque problème. Utilisez exactement le nom du fichier téléversé.</p></section><section class="panel"><h2>Bien préparer ses images</h2><p>Préférez un SVG simple pour les dessins géométriques. Les SVG doivent contenir des tracés et formes, sans scripts, styles CSS ni ressources externes. Exportez les textes en chemins depuis votre logiciel de dessin si nécessaire.</p><p>Les PNG et JPEG conviennent aussi. Limites : 2 Mo par image, 20 figures par problème. Pour TikZ, compilez le dessin ailleurs puis exportez-le en SVG ou PNG.</p></section><section class="panel"><h2>De votre atelier à la collection</h2><ol><li>Enregistrez votre brouillon.</li><li>Vérifiez l’aperçu dans chaque langue.</li><li>Soumettez le problème à validation.</li><li>Un administrateur peut corriger, retourner ou publier les versions vérifiées.</li></ol><p>LaTeX est utilisé pour l’énoncé et les mathématiques. Les paquets arbitraires, macros personnalisées et commandes système ne sont pas exécutés.</p></section></div>`);}
function privacy(){shell(`${intro('LA COMMUNAUTÉ','Confidentialité & contributions','Des règles simples pour partager les problèmes avec soin.')}<article class="panel prose"><h2>Votre compte</h2><p>Votre adresse e-mail sert à vous connecter et à confirmer votre compte. Elle n’est pas affichée aux autres membres. Votre pseudo accompagne vos problèmes publiés. Le mot de passe est stocké sous forme de hachage par WordPress.</p><h2>Vos contributions</h2><p>Proposez uniquement des énoncés et des figures que vous êtes autorisé à partager. Indiquez la source et les crédits. En soumettant un problème, vous autorisez sa relecture, ses corrections et sa publication sur le site et les applications associées.</p><p>Une correction mineure peut être publiée par un administrateur. Pour un changement mathématique substantiel, l’administrateur doit vous retourner la proposition avec une explication.</p><h2>Ce qui reste privé</h2><p>Les brouillons sont visibles par leur auteur et les administrateurs. Les membres ont accès aux versions publiées. Votre progression est personnelle. Les images ne sont accessibles qu’aux personnes autorisées à voir le problème correspondant.</p><h2>E-mails et suppression</h2><p>Les notifications de nouveaux problèmes sont facultatives. Vous pouvez les arrêter dans votre profil. La suppression de compte retire votre profil et vos brouillons ; les contributions déjà publiées restent disponibles avec une attribution anonyme.</p><h2>Cookies</h2><p>Le site utilise les cookies WordPress nécessaires à la connexion. Aucun outil publicitaire ou de mesure d’audience n’est inclus.</p>${session.local?'<div class="notice soft">Version locale : aucun e-mail n’est envoyé. Avant l’ouverture publique, les coordonnées de l’éditeur du site et les mentions légales seront complétées.</div>':''}</article>`);}
async function mailbox(){if(!session.user?.admin||!session.local){routeTo('/');return;}const mail=await api('mailbox');shell(`${intro('APERÇU LOCAL','Boîte e-mail de test','Ces messages sont enregistrés sur votre Mac ; ils n’ont pas été envoyés.')}<div class="mailbox">${mail.length?mail.map((m:any)=>`<article class="panel"><p class="small muted">${esc(String(m.to))} · ${date(m.date)}</p><h2>${esc(m.subject)}</h2><pre>${esc(m.message).replace(/https?:\/\/[^\s<&]+/g,(url:string)=>`<a href="${url}" target="_blank" rel="noopener">${url}</a>`)}</pre></article>`).join(''):empty('Aucun e-mail pour le moment','Créez un compte de test pour recevoir son lien de confirmation ici.')}</div>`);}
async function route(){
    const current=location.hash||'#/';if(dirty&&current!==lastRoute&&!confirm('Quitter sans enregistrer vos modifications ?')){history.replaceState(null,'',lastRoute);return;}
    lastRoute=current;dirty=false;routeSequence++;const [path,query]=current.replace(/^#/,'').split('?');const parts=path.split('/').filter(Boolean);const page=parts[0]||'';document.title='Le Problème du Jour';window.scrollTo(0,0);
    try{if(!session)session=await api('session');
        if(['connexion','inscription','mot-de-passe','renvoyer','reinitialiser','confirmer'].includes(page))auth(page,new URLSearchParams(query));
        else if(page==='mes-propositions'){filters.status='';filters.progress='';await collection('mine');}
        else if(page==='administration'){filters.status='';filters.progress='';await collection('review');}
        else if(page==='probleme')await reader(parts[1]);else if(page==='editer')await editor(parts[1]);else if(page==='profil')profile();else if(page==='aide')help();else if(page==='confidentialite')privacy();else if(page==='courrier')await mailbox();else {filters.status='';await collection();}
    }catch(error:any){shell(empty('Cette page n’est pas disponible.',esc(error.message),'<a class="button" href="#/">Retour à la collection</a>'));}
}
root.addEventListener('input',(e)=>{
    const target=e.target as HTMLInputElement;
    if(target.id==='search'){filters.search=target.value;drawList();}
    if($('#latex')&&['latex','problem-title','edit-category','edit-difficulty','edit-source','keywords','approved','review-note'].includes(target.id)){
        dirty=true;$('#save-state').textContent='Modifications non enregistrées';
        if(['latex','problem-title'].includes(target.id)){problem.versions[editorLanguage].approved=false;if($('#approved'))$('#approved').checked=false;}
        if(['edit-category','edit-difficulty','edit-source','keywords'].includes(target.id)){for(const v of Object.values(problem.versions) as any)v.approved=false;if($('#approved'))$('#approved').checked=false;}
        if(target.id==='latex')preview();
    }
});
root.addEventListener('change',async(e)=>{
    const target=e.target as HTMLInputElement;
    if(['category','difficulty','source','progress','status','sort'].includes(target.id)){(filters as any)[target.id]=target.value;drawList();}
    try{
        if(target.id==='tex-file'&&target.files?.[0]){if(target.files[0].size>60000)throw Error('Le fichier .tex doit peser moins de 60 Ko.');let text=await target.files[0].text();const body=/\\begin\{document\}([\s\S]*?)\\end\{document\}/.exec(text);if(body)text=body[1].trim();$('#latex').value=text;problem.versions[editorLanguage].approved=false;if($('#approved'))$('#approved').checked=false;dirty=true;$('#save-state').textContent='Modifications non enregistrées';preview();}
        if((target.id==='figure-file'||target.id==='avatar-file')&&target.files?.[0]){
            if(target.files[0].size>2*1024*1024)throw Error('Chaque image doit peser au maximum 2 Mo.');
            const isFigure=target.id==='figure-file';if(isFigure)collectEditor();const data=new FormData();data.append('file',target.files[0]);data.append('problem',isFigure?String(problem.id):'0');if(isFigure)data.append('revision',String(problem.revision));target.disabled=true;
            const uploaded=await api('assets',data);
            if(isFigure){problem.assets[uploaded.name]=uploaded.asset;problem.revision=uploaded.revision;showEditor();toast('Figure ajoutée. Cliquez sur « Insérer dans l’énoncé ».');}
            else{avatar=uploaded.asset.id;const existing=$('#avatar-preview')||$('#avatar-placeholder');existing.outerHTML=`<img id="avatar-preview" src="${esc(uploaded.asset.url)}" alt="Nouvelle image de profil">`;toast('Image ajoutée. Enregistrez vos préférences.');}
        }
    }catch(error:any){message(error.message,true);}finally{target.disabled=false;}
});
root.addEventListener('click',async(e)=>{
    const b=(e.target as HTMLElement).closest<HTMLElement>('[data-action],[data-save],[data-reader-lang],[data-editor-lang],[data-insert],[data-progress],[data-source]');if(!b)return;
    try{
        if(b.dataset.save){await saveProblem(b.dataset.save);return;}
        if(b.dataset.readerLang){language=b.dataset.readerLang;showReader();return;}
        if(b.dataset.editorLang){collectEditor();editorLanguage=b.dataset.editorLang;showEditor();return;}
        if(b.dataset.insert){const text=$('#latex');const label='fig:'+b.dataset.insert.replace(/\.[^.]+$/,'');text.setRangeText(`\n\n\\begin{figure}\n\\centering\n\\includegraphics[width=0.7\\linewidth]{${b.dataset.insert}}\n\\caption{Une légende}\n\\label{${label}}\n\\end{figure}\n`,text.selectionStart,text.selectionEnd,'end');problem.versions[editorLanguage].approved=false;if($('#approved'))$('#approved').checked=false;dirty=true;$('#save-state').textContent='Modifications non enregistrées';preview();text.focus();return;}
        if(b.dataset.progress){await api('problems/'+problem.id+'/progress',{progress:b.dataset.progress});problem.progress=b.dataset.progress;showReader();return;}
        if(b.dataset.source){filters.source=b.dataset.source;$('#source').value=b.dataset.source;drawList();return;}
        if(b.dataset.action==='new'){if(!session.user){routeTo('/connexion');return;}b.setAttribute('disabled','');const created=await api('problems',{});routeTo('/editer/'+created.id);}
        if(b.dataset.action==='reset-filters'){filters={search:'',category:'',difficulty:'',source:'',progress:'',status:'',sort:'newest'};for(const [id,v] of Object.entries(filters))if($('#'+id))$('#'+id).value=v;drawList();}
        if(b.dataset.action==='pick'){const items=filtered();if(!items.length){toast('Aucun problème disponible avec ces filtres.');return;}routeTo('/probleme/'+items[Math.floor(Math.random()*items.length)].id);}
        if(b.dataset.action==='logout'){await api('auth/logout',{});location.hash='#/';location.reload();}
        if(b.dataset.action==='delete-draft'&&confirm('Supprimer ce brouillon, ses figures et son historique ?')){await api('problems/'+problem.id,{},'DELETE');dirty=false;routeTo('/mes-propositions');toast('Brouillon supprimé.');}
        if(b.dataset.action==='delete-account'&&confirm('Supprimer définitivement votre compte et vos brouillons ?')){await api('account',{password:value('delete-password')},'DELETE');location.hash='#/';location.reload();}
        if(b.dataset.action==='history'){const entries=await api('problems/'+problem.id+'/history');$('#history').innerHTML=`<section class="panel"><h2>Historique</h2>${entries.length?entries.map((entry:any)=>`<details class="history-entry"><summary>${esc(actions[entry.action]||entry.action)} · ${date(entry.date)} · ${esc(entry.by)}</summary><p>Révision ${entry.snapshot.revision} — ${esc(titleOf(entry.snapshot))}</p>${Object.entries(entry.snapshot.versions).map(([lang,v]:any)=>`<h3>${lang.toUpperCase()} ${v.approved?'✓':''}</h3><pre>${esc(v.title)}\n\n${esc(v.latex)}</pre>`).join('')}</details>`).join(''):'<p>Aucune sauvegarde pour le moment.</p>'}</section>`;}
    }catch(error:any){message(error.message,true);}finally{b.removeAttribute('disabled');}
});
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
window.addEventListener('hashchange',route);
route();
