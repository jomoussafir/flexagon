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
test('KaTeX environments render inside display and inline math',()=>{
 for(const formula of [
  String.raw`\[\begin{aligned} a &= b \\ &= c \end{aligned}\]`,
  String.raw`\[\begin{align} a &= b \\ c &= d \end{align}\]`,
  String.raw`\[\begin{array}{cc} a & b \\ c & d \end{array}\]`,
  String.raw`$$\begin{array}{cc} a & b \\ c & d \end{array}$$`,
  String.raw`\[ f(x)=\begin{cases} 1 & x>0 \\ 0 & x\le 0 \end{cases} \]`,
  String.raw`$\begin{pmatrix} a & b \\ c & d \end{pmatrix}$`,
 ])assert.ok(render(formula).includes('class="katex"'),formula);
});
test('bare LaTeX environments outside math are still rejected',()=>{
 for(const statement of [
  String.raw`\begin{align} a &= b \\ c &= d \end{align}`,
  String.raw`\begin{array}{cc} a & b \\ c & d \end{array}`,
  String.raw`\begin{tabular}{c} x \end{tabular}`,
 ])assert.throws(()=>render(statement),/Unsupported LaTeX environment/,statement);
});
