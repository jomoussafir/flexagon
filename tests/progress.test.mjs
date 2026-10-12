import test from 'node:test';
import assert from 'node:assert/strict';
import {progressGroups,problemTitle} from '../wordpress/themes/le-probleme-du-jour/src/progress.ts';

const defaults={groupBy:'category',mode:'solved',search:'',category:'',difficulty:'',source:''};
const samples=[
    {id:1,category:'Logic',difficulty:2,source:'Community',progress:'solved',keywords:['truth'],versions:{en:{title:'Two doors'}}},
    {id:2,category:'Geometry',difficulty:5,source:'IMO',progress:'bookmarked',keywords:['circle'],versions:{es:{title:'Tres cuadrados'}}},
    {id:3,category:'Logic',difficulty:1,source:'Community',progress:'unseen',keywords:[],versions:{en:{title:'Four coins'}}},
    {id:4,category:'Geometry',difficulty:3,source:'IMO',progress:'attempted',keywords:[],versions:{en:{title:'A triangle'},fr:{title:'Un triangle'}}},
    {id:5,category:'Logic',difficulty:3,source:'Moscow Puzzles',progress:'solved',keywords:[],versions:{'und-12345678':{title:'Custom language title'}}}
];
const compareSources=(a,b)=>['Moscow Puzzles','IMO','Community'].indexOf(a)-['Moscow Puzzles','IMO','Community'].indexOf(b);
const view=filters=>progressGroups(samples,{...defaults,...filters},compareSources);

test('Solved view retains group and total denominators',()=>{
    const v=view({});assert.deepEqual([v.total,v.solved,v.unsolved],[5,2,3]);
    assert.deepEqual(v.groups.map(g=>[g.key,g.total,g.solved,g.items.map(p=>p.id)]),[['Logic',3,2,[1,5]]]);
});
test('Unsolved includes unseen, bookmarked and attempted; All includes every item',()=>{
    assert.deepEqual(view({mode:'unsolved'}).groups.flatMap(g=>g.items.map(p=>p.id)).sort(),[2,3,4]);
    assert.equal(view({mode:'all'}).groups.flatMap(g=>g.items).length,5);
});
test('Grouping supports numeric difficulty and the configured source order',()=>{
    assert.deepEqual(view({mode:'all',groupBy:'difficulty'}).groups.map(g=>g.key),['1','2','3','5']);
    assert.deepEqual(view({mode:'all',groupBy:'source'}).groups.map(g=>g.key),['Moscow Puzzles','IMO','Community']);
});
test('Filters combine and search covers translated titles and keywords',()=>{
    assert.equal(view({mode:'all',category:'Geometry',difficulty:'5',source:'IMO',search:'CUADRADOS'}).total,1);
    assert.equal(view({search:'truth'}).solved,1);
    assert.equal(view({mode:'all',category:'Logic',source:'IMO'}).total,0);
});
test('Any language can supply the title; grouping does not mutate the catalogue',()=>{
    const before=structuredClone(samples);view({mode:'all'});
    assert.deepEqual(samples,before);assert.equal(problemTitle(samples[1]),'Tres cuadrados');
    assert.equal(problemTitle(samples[4]),'Custom language title');
});
