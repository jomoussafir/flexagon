export type ProgressProblem = {id:number;category:string;difficulty:number;source:string;progress:string;keywords:string[];versions:Record<string,{title:string}>};
export type ProgressFilters = {groupBy:'category'|'difficulty'|'source';mode:'solved'|'unsolved'|'all';search:string;category:string;difficulty:string;source:string};
export const problemTitle = (p:{versions:Record<string,{title:string}>}) => p.versions.en?.title || p.versions.fr?.title || Object.values(p.versions).find(v=>v.title)?.title || 'Untitled';
export function progressGroups(items:ProgressProblem[], filters:ProgressFilters, compareSources:(a:string,b:string)=>number) {
    const search=filters.search.trim().toLocaleLowerCase();
    const matching=items.filter(p=>(!filters.category||p.category===filters.category)&&(!filters.difficulty||p.difficulty===Number(filters.difficulty))&&(!filters.source||p.source===filters.source)&&(!search||[...Object.values(p.versions).map(v=>v.title),...p.keywords].join(' ').toLocaleLowerCase().includes(search)));
    const groups=new Map<string,ProgressProblem[]>();
    for(const p of matching){const key=String(p[filters.groupBy]);if(!groups.has(key))groups.set(key,[]);groups.get(key)!.push(p);}
    const solved=matching.filter(p=>p.progress==='solved').length;
    return {total:matching.length,solved,unsolved:matching.length-solved,groups:[...groups].sort(([a],[b])=>filters.groupBy==='difficulty'?Number(a)-Number(b):filters.groupBy==='source'?compareSources(a,b):a.localeCompare(b)).map(([key,problems])=>({key,total:problems.length,solved:problems.filter(p=>p.progress==='solved').length,items:problems.filter(p=>filters.mode==='all'||(filters.mode==='solved')===(p.progress==='solved')).sort((a,b)=>a.difficulty-b.difficulty||problemTitle(a).localeCompare(problemTitle(b)))})).filter(g=>g.items.length)};
}
