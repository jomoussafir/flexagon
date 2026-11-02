export type ProgressProblem = {id:number;category:string;difficulty:number;source:string;progress:string;keywords:string[];versions:Record<string,{title:string}>};
export type ProgressFilters = {groupBy:'category'|'difficulty'|'source';mode:'all'|'unseen'|'seen'|'bookmarked'|'attempted'|'solved'|'unsolved';search:string;category:string;difficulty:string;source:string};
export const problemTitle = (p:{versions:Record<string,{title:string}>}) => p.versions.en?.title || p.versions.fr?.title || Object.values(p.versions).find(v=>v.title)?.title || 'Untitled';
// Published difficulty is bucketed into three bands; 1–2 easy, 3 medium, 4–5 hard.
const difficultyBandOrder = ['very-easy','easy','medium','hard','very-hard'];
export const difficultyBand = (d:number):string => d===1?'very-easy':d===2?'easy':d===3?'medium':d===4?'hard':'very-hard';
export function progressGroups(items:ProgressProblem[], filters:ProgressFilters, compareSources:(a:string,b:string)=>number) {
    const search=filters.search.trim().toLocaleLowerCase();
    const matching=items.filter(p=>(!filters.category||p.category===filters.category)&&(!filters.difficulty||difficultyBand(p.difficulty)===filters.difficulty)&&(!filters.source||p.source===filters.source)&&(!search||[...Object.values(p.versions).map(v=>v.title),...p.keywords].join(' ').toLocaleLowerCase().includes(search)));
    const groups=new Map<string,ProgressProblem[]>();
    for(const p of matching){const key=filters.groupBy==='difficulty'?difficultyBand(p.difficulty):String(p[filters.groupBy]);if(!groups.has(key))groups.set(key,[]);groups.get(key)!.push(p);}
    const matchesStatus=(p:ProgressProblem)=>filters.mode==='all'||(filters.mode==='unsolved'?p.progress!=='solved':p.progress===filters.mode);
    const solved=matching.filter(p=>p.progress==='solved').length;
    return {total:matching.length,solved,unsolved:matching.length-solved,shown:matching.filter(matchesStatus).length,groups:[...groups].sort(([a],[b])=>filters.groupBy==='difficulty'?difficultyBandOrder.indexOf(a)-difficultyBandOrder.indexOf(b):filters.groupBy==='source'?compareSources(a,b):a.localeCompare(b)).map(([key,problems])=>({key,total:problems.length,solved:problems.filter(p=>p.progress==='solved').length,items:problems.filter(matchesStatus).sort((a,b)=>a.difficulty-b.difficulty||problemTitle(a).localeCompare(problemTitle(b)))})).filter(g=>g.items.length)};
}
