import { runCLI } from '@wp-playground/cli';
import { Server } from 'node:net';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const filename=path.resolve(process.argv[2]||path.join(root,'private-data/legacy-export/import.json'));
const bundle=JSON.parse(await fs.readFile(filename,'utf8'));
if(bundle.format!=='lpdj-legacy-v1'||!Array.isArray(bundle.problems)||!bundle.problems.length)throw Error('Expected a complete lpdj-legacy-v1 export.');
// Never mount a live SQLite database in two WordPress processes.
try { const response=await fetch('http://127.0.0.1:9410/wp-json/lpdj/v1/session',{signal:AbortSignal.timeout(700)});if(response.ok)throw Error('Stop the local website before importing, then run npm start afterwards.'); }
catch(error){if(error.message.startsWith('Stop the local'))throw error;}
const state=path.join(root,'.local/wordpress');
await fs.access(path.join(state,'wp-load.php'));
const backup=path.join(root,'backups','before-legacy-import-'+Date.now());
await fs.mkdir(backup,{recursive:true});
await fs.cp(path.join(state,'wp-content/database'),path.join(backup,'database'),{recursive:true});
const listen=Server.prototype.listen;
Server.prototype.listen=function(...args){if(typeof args[0]==='number')return listen.call(this,{port:args[0],host:'127.0.0.1'},args.find(a=>typeof a==='function'));return listen.apply(this,args);};
const server=await runCLI({command:'server',port:9402,wp:'7.1.3',php:'8.3',workers:6,login:false,
    wordpressInstallMode:'install-from-existing-files-if-needed',
    'site-url':'http://127.0.0.1:9410',
    'mount-before-install':[{hostPath:state,vfsPath:'/wordpress'},{hostPath:path.join(root,'wordpress/plugins/flexagon'),vfsPath:'/wordpress/wp-content/plugins/flexagon'},{hostPath:path.dirname(filename),vfsPath:'/legacy-import'}],
    blueprint:{constants:{WP_ENVIRONMENT_TYPE:'local',LPDJ_LOCAL_PREVIEW:true,DISABLE_WP_CRON:true},steps:[]}});
try {
    const ids={};let skipped=0;
    for(let offset=0;offset<bundle.problems.length;offset+=25){
        const result=await server.playground.run({code:`<?php
            require '/wordpress/wp-load.php'; wp_set_current_user(1);
            update_option('blogdescription','');
            $admin=get_user_by('id',1);if($admin && $admin->display_name==='Administrateur')wp_update_user(['ID'=>1,'display_name'=>'Administrator']);
            $bundle=json_decode(file_get_contents('/legacy-import/'.base64_decode('${Buffer.from(path.basename(filename)).toString('base64')}')),true);
            $result=lpdj_import_legacy(array_slice($bundle['problems'],${offset},25),$bundle['figures'],$bundle['history']);
            if(is_wp_error($result)){http_response_code(500);echo $result->get_error_message();exit;}
            echo wp_json_encode($result);
        `});
        if(result.httpStatusCode!==200||result.exitCode!==0)throw Error(result.text);
        let data;try{data=JSON.parse(result.text);}catch{throw Error(result.text.slice(0,1000));}
        Object.assign(ids,data.created,data.skipped);skipped+=Object.keys(data.skipped).length;
        console.log(`Imported or matched ${Math.min(offset+25,bundle.problems.length)} / ${bundle.problems.length}`);
    }
    const audit=await server.playground.run({code:`<?php
        require '/wordpress/wp-load.php'; wp_set_current_user(1);
        $bundle=json_decode(file_get_contents('/legacy-import/'.base64_decode('${Buffer.from(path.basename(filename)).toString('base64')}')),true);
        $expected=[];foreach($bundle['problems'] as $p)$expected[$p['id']]=$p;
        $report=['matched'=>0,'published'=>0,'figures'=>0,'history'=>0,'sources'=>[],'errors'=>[]];
        $posts=get_posts(['post_type'=>'lpdj_problem','post_status'=>'private','posts_per_page'=>-1]);
        foreach($posts as $post){
            $key=get_post_meta($post->ID,'_lpdj_legacy_id',true);if(!isset($expected[$key]))continue;
            $draft=get_post_meta($post->ID,'_lpdj_draft',true);$p=$expected[$key];
            if(get_post_meta($post->ID,'_lpdj_legacy',true)!==$p)$report['errors'][]=$key.': original metadata';
            if(get_post_meta($post->ID,'_lpdj_legacy_history',true)!==($bundle['history'][$key]??[]))$report['errors'][]=$key.': history';
            if($draft['revision']===1)foreach(['en','fr'] as $lang){
                if($draft['versions'][$lang]['latex']!==$p['versions'][$lang]['statement'] || $draft['versions'][$lang]['title']!==$p['versions'][$lang]['title'] || $draft['versions'][$lang]['approved']!==$p['versions'][$lang]['approved'])$report['errors'][]=$key.': '.$lang;
            }
            foreach($p['assets'] as $name)if(empty($draft['assets'][$name])||!get_post($draft['assets'][$name]['id']))$report['errors'][]=$key.': missing figure '.$name;
            $report['matched']++;$report['published']+=(bool)get_post_meta($post->ID,'_lpdj_published',true);
            $report['figures']+=count($draft['assets']);$report['history']+=count($bundle['history'][$key]??[]);
            $report['sources'][$draft['source']]=($report['sources'][$draft['source']]??0)+1;unset($expected[$key]);
        }
        foreach(array_keys($expected) as $key)$report['errors'][]=$key.': missing problem';
        echo wp_json_encode($report);
    `});
    if(audit.exitCode!==0)throw Error(audit.text);
    const report=JSON.parse(audit.text);
    await fs.writeFile(path.join(path.dirname(filename),'verification.json'),JSON.stringify(report,null,2),{mode:0o600});
    if(report.errors.length)throw Error(JSON.stringify(report.errors));
    console.log(JSON.stringify(report));
    await fs.writeFile(path.join(path.dirname(filename),'wordpress-ids.json'),JSON.stringify(ids,null,2),{mode:0o600});
    console.log(`Complete: ${Object.keys(ids).length} problems; ${skipped} existing records left unchanged. Nothing published.`);
} finally {await server[Symbol.asyncDispose]();}
