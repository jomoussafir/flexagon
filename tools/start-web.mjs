import { runCLI } from '@wp-playground/cli';
import { Server } from 'node:net';
import { access, mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFile } from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
process.chdir(root);
const port=Number(process.env.LPDJ_PORT||9400);
const localURL=`http://127.0.0.1:${port}`;
try {
    const response=await fetch(localURL+'/wp-json/lpdj/v1/session',{signal:AbortSignal.timeout(1000)});
    const data=await response.json();
    if(response.ok&&data.local){console.log(`Website already running: ${localURL}`);if(!process.argv.includes('--no-open'))execFile('open',[localURL]);process.exit(0);}
} catch {}
const state=path.join(root,'.local');
await mkdir(path.join(state,'wordpress'),{recursive:true});
let credentials;
try{credentials=JSON.parse(await readFile(path.join(state,'admin.json'),'utf8'));}
catch{credentials={email:'admin@localhost.test',password:crypto.randomBytes(18).toString('base64url')};await writeFile(path.join(state,'admin.json'),JSON.stringify(credentials,null,2),{mode:0o600});}
await writeFile(path.join(root,'Local access.txt'),`LOCAL PREVIEW ONLY — LE PROBLÈME DU JOUR\n\nWebsite: ${localURL}\nEmail: ${credentials.email}\nPassword: ${credentials.password}\n\nThese credentials only work in the local preview on this Mac.\nDo not reuse them on OVH. This file is excluded from Git and deployment packages.\n` ,{mode:0o600});
// Playground currently listens on all interfaces. Limit every server in this local
// launcher to loopback before starting it; development mail and credentials stay local.
const listen=Server.prototype.listen;
Server.prototype.listen=function(...args){if(typeof args[0]==='number'){const callback=args.find(a=>typeof a==='function');return listen.call(this,{port:args[0],host:'127.0.0.1'},callback);}return listen.apply(this,args);};
const phpString=s=>"'"+s.replaceAll('\\','\\\\').replaceAll("'","\\'")+"'";
let existingWordPress=false;
try { await access(path.join(state,'wordpress/wp-load.php')); existingWordPress=true; } catch {}
const server=await runCLI({command:'server',port,wp:'7.1.3',php:'8.3',login:false,workers:6,
    wordpressInstallMode:existingWordPress?'install-from-existing-files-if-needed':'download-and-install',
    'site-url':`http://127.0.0.1:${port}`,
    'mount-before-install':[{hostPath:path.join(state,'wordpress'),vfsPath:'/wordpress'},{hostPath:path.join(root,'wordpress/plugins/le-probleme-du-jour'),vfsPath:'/wordpress/wp-content/plugins/le-probleme-du-jour'},{hostPath:path.join(root,'wordpress/themes/le-probleme-du-jour'),vfsPath:'/wordpress/wp-content/themes/le-probleme-du-jour'}],
    blueprint:{constants:{WP_ENVIRONMENT_TYPE:'local',LPDJ_LOCAL_PREVIEW:true,DISABLE_WP_CRON:false},steps:[{step:'runPHP',code:`<?php
        require '/wordpress/wp-load.php';
        require_once ABSPATH . 'wp-admin/includes/plugin.php';
        activate_plugin('le-probleme-du-jour/le-probleme-du-jour.php');
        switch_theme('le-probleme-du-jour');
        if (!get_option('_lpdj_local_setup')) {
            $user = get_user_by('login', 'admin');
            if ($user) wp_update_user(['ID'=>$user->ID,'user_email'=>${phpString(credentials.email)},'user_pass'=>${phpString(credentials.password)},'display_name'=>'Administrator']);
            update_option('blogname', 'Le Problème du Jour');
            update_option('blogdescription', '');
            update_option('permalink_structure', '/%postname%/');
            update_option('blog_public', 0);
            update_option('_lpdj_local_setup', 1);
            flush_rewrite_rules();
        }
    `}]}});
console.log(`\nLe Problème du Jour: ${server.serverUrl}\nLocal administrator credentials: .local/admin.json\nKeep this window open. Press Ctrl+C to stop.\n`);
if(!process.argv.includes('--no-open'))execFile('open',[server.serverUrl]);
let closing=false;
async function shutdown(){if(closing)return;closing=true;await server[Symbol.asyncDispose]();process.exit(0);}
process.on('SIGINT',shutdown);process.on('SIGTERM',shutdown);
