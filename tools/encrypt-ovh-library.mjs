import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const transfer=path.join(root,'private-data/ovh-transfer');
const output=path.join(transfer,'encrypted');
await fs.mkdir(path.join(output,'references'),{recursive:true,mode:0o700});
const keyFile=path.join(transfer,'storage-key');
let key;try{key=await fs.readFile(keyFile);if(key.length!==32)throw Error('Invalid existing key');}
catch(error){if(error.code!=='ENOENT')throw error;key=crypto.randomBytes(32);await fs.writeFile(keyFile,key,{mode:0o600,flag:'wx'});}
async function encrypt(source,target){
 const name=path.basename(source), plain=await fs.readFile(source), nonce=crypto.randomBytes(12);
 const cipher=crypto.createCipheriv('aes-256-gcm',key,nonce);
 cipher.setAAD(Buffer.from('LPDJENC1:'+name));
 const encrypted=Buffer.concat([cipher.update(plain),cipher.final()]);
 const envelope=Buffer.concat([Buffer.from('LPDJENC1'),nonce,cipher.getAuthTag(),encrypted]);
 await fs.writeFile(target,envelope,{mode:0o600});
 return {file:name,bytes:plain.length,encryptedBytes:envelope.length};
}
const bundle=JSON.parse(await fs.readFile(path.join(transfer,'catalogue.json'),'utf8'));
const report=[];
report.push(await encrypt(path.join(transfer,'catalogue.json'),path.join(output,'catalogue.json.lpdj')));
for(const entry of bundle.references){
 const source=path.join(root,'private-data/references',entry.file);
 const bytes=await fs.readFile(source);
 if(crypto.createHash('sha256').update(bytes).digest('hex')!==entry.sha256)throw Error('Reference changed since export: '+entry.file);
 report.push(await encrypt(source,path.join(output,'references',entry.file+'.lpdj')));
}
const php=`<?php\n// Site-specific private library key. Exclude this file from code packages.\nif (!defined('ABSPATH')) { http_response_code(404); exit; }\ndefine('LPDJ_PRIVATE_FILE_KEY', '${key.toString('base64')}');\ndefine('LPDJ_TRANSFER_DIR', WP_CONTENT_DIR . '/lpdj-private-storage');\ndefine('LPDJ_REFERENCE_DIR', LPDJ_TRANSFER_DIR . '/references');\n`;
await fs.writeFile(path.join(transfer,'lpdj-private-storage.php'),php,{mode:0o600});
await fs.writeFile(path.join(transfer,'encryption-audit.json'),JSON.stringify({format:'LPDJENC1/AES-256-GCM',files:report},null,2),{mode:0o600});
console.log('Encrypted '+report.length+' files. Configuration and key remain private; no secret printed.');
