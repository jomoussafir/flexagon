import {test} from 'node:test';
import assert from 'node:assert/strict';
import {render} from '../render.ts';
test('salary example renders escaped currency as ordinary text',()=>{
 const statement=String.raw`Which yields a larger amount with the same starting salary:
Plan I, with four annual increases of \$ 100 each, or
Plan II, with two biennial increases of 200 each?`;
 assert.equal(render(statement),'<p>'+statement.replace('\\$','$')+'</p>');
});
test('multiple currency amounts do not become a formula',()=>{
 assert.equal(render(String.raw`Pay \$100 or \$200.`),'<p>Pay $100 or $200.</p>');
});
test('currency can surround real inline mathematics',()=>{
 const result=render(String.raw`Pay \$100 for $x^2$ or \$200 for $y$.`);
 assert.ok(result.startsWith('<p>Pay $100 for '));
 assert.equal((result.match(/class="katex"/g)||[]).length,2);
 assert.ok(result.includes('or $200 for'));
});
test('escaped currency inside mathematics remains valid TeX',()=>{
 const result=render(String.raw`$\$100 + x$`);
 assert.equal((result.match(/class="katex"/g)||[]).length,1);
 assert.ok(result.includes('100'));
});
test('existing math delimiters and HTML escaping are preserved',()=>{
 for(const formula of [String.raw`$x^2$`,String.raw`$$x^2$$`,String.raw`\(x^2\)`,String.raw`\[x^2\]`])assert.ok(render(formula).includes('class="katex"'));
 assert.equal(render(String.raw`<script> \$5`),'<p>&lt;script&gt; $5</p>');
 assert.throws(()=>render(String.raw`$\unknowncommand$`));
});
