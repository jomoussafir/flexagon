// Encrypt the traced figure library for the OVH private storage directory.
// Reuses the storage key created by encrypt-ovh-library.mjs so the plugin can read
// both libraries with the one LPDJ_PRIVATE_FILE_KEY already configured on the host.
// Output: private-data/ovh-transfer/encrypted/figures/ (upload it to
// /wp-content/lpdj-private-storage/figures/). Nothing is uploaded by this script.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const transfer=path.join(root,'private-data/ovh-transfer');
const source=path.join(root,'private-data/figures');
const output=path.join(transfer,'encrypted/figures');
const keyFile=path.join(transfer,'storage-key');
let key;
try{key=await fs.readFile(keyFile);if(key.length!==32)throw Error('Invalid key length');}
catch(error){throw Error('Storage key not found at private-data/ovh-transfer/storage-key. Run encrypt-ovh-library.mjs first, or restore the key from your private backup, so the figures use the key already configured on OVH.',{cause:error});}
const manifest=JSON.parse(await fs.readFile(path.join(source,'manifest.json'),'utf8'));
if(manifest.format!=='lpdj-figures-v1')throw Error('Unexpected figure manifest format.');
await fs.rm(output,{recursive:true,force:true});
await fs.mkdir(output,{recursive:true,mode:0o700});
async function encrypt(file,target){
 const name=path.basename(file), plain=await fs.readFile(file), nonce=crypto.randomBytes(12);
 const cipher=crypto.createCipheriv('aes-256-gcm',key,nonce);
 cipher.setAAD(Buffer.from('LPDJENC1:'+name));
 const encrypted=Buffer.concat([cipher.update(plain),cipher.final()]);
 await fs.mkdir(path.dirname(target),{recursive:true,mode:0o700});
 await fs.writeFile(target,Buffer.concat([Buffer.from('LPDJENC1'),nonce,cipher.getAuthTag(),encrypted]),{mode:0o600});
 return {file:path.relative(source,file),bytes:plain.length,sha256:crypto.createHash('sha256').update(plain).digest('hex')};
}
// Only redrawn figures are served by the plugin, so only they (and the manifest) travel.
const report=[await encrypt(path.join(source,'manifest.json'),path.join(output,'manifest.json.lpdj'))];
let redrawn=0;
for(const figure of manifest.figures){
 if(!figure.redrawn)continue;
 redrawn++;
 for(const kind of ['pdf','svg']){
  const file=path.join(source,figure.redrawn.dir,figure.redrawn[kind]);
  report.push(await encrypt(file,path.join(output,figure.redrawn.dir,figure.redrawn[kind]+'.lpdj')));
 }
}
await fs.writeFile(path.join(transfer,'figures-audit.json'),JSON.stringify({format:'LPDJENC1/AES-256-GCM',generated:new Date().toISOString(),figures:manifest.count,redrawn,files:report},null,2),{mode:0o600});
console.log(`Encrypted ${report.length} files for ${redrawn} redrawn figures into private-data/ovh-transfer/encrypted/figures/.`);
console.log(`Upload that directory to /wp-content/lpdj-private-storage/figures/ (permissions 700/600) and add to lpdj-private-storage.php:\n  define('LPDJ_FIGURE_DIR', LPDJ_TRANSFER_DIR . '/figures');`);
