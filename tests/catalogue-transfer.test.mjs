import assert from 'node:assert/strict';
import { runCLI } from '@wp-playground/cli';
import { Server } from 'node:net';
import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
const root=fileURLToPath(new URL('../', import.meta.url)).replace(/\/$/, '');
const encrypted=process.env.LPDJ_ENCRYPTED_TEST==='1';
const key=encrypted?(await fs.readFile(root+'/private-data/ovh-transfer/storage-key')).toString('base64'):null;
const listen=Server.prototype.listen;
Server.prototype.listen=function(...args){if(typeof args[0]==='number')return listen.call(this,{port:args[0],host:'127.0.0.1'},args.find(a=>typeof a==='function'));return listen.apply(this,args);};
const server=await runCLI({command:'server',port:9403,wp:'7.1.3',php:'8.3',workers:4,login:false,
 'mount-before-install':[
 {hostPath:root+'/wordpress/plugins/flexagon',vfsPath:'/wordpress/wp-content/plugins/flexagon'},
 {hostPath:root+'/tools/lpdj-catalogue-transfer',vfsPath:'/wordpress/wp-content/plugins/lpdj-catalogue-transfer'},
 {hostPath:root+'/private-data/ovh-transfer',vfsPath:'/lpdj-transfer'},
 {hostPath:root+'/private-data/references',vfsPath:'/lpdj-references'}],
 blueprint:{constants:{WP_ENVIRONMENT_TYPE:'local',LPDJ_LOCAL_PREVIEW:true,LPDJ_TRANSFER_DIR:encrypted?'/lpdj-transfer/encrypted':'/lpdj-transfer',LPDJ_REFERENCE_DIR:encrypted?'/lpdj-transfer/encrypted/references':'/lpdj-references',...(encrypted?{LPDJ_PRIVATE_FILE_KEY:key}:{}),DISABLE_WP_CRON:true},steps:[{step:'runPHP',code:`<?php require '/wordpress/wp-load.php';require_once ABSPATH.'wp-admin/includes/plugin.php';activate_plugin('flexagon/flexagon.php');activate_plugin('lpdj-catalogue-transfer/lpdj-catalogue-transfer.php');$id=wp_insert_user(['user_login'=>'migrator','user_pass'=>wp_generate_password(32),'user_email'=>'migrator@example.test','role'=>'administrator']);echo $id;`}]}});
async function php(code){const r=await server.playground.run({code:`<?php require '/wordpress/wp-load.php';wp_set_current_user(get_user_by('login','migrator')->ID);${code}`});if(r.exitCode!==0||r.httpStatusCode!==200)throw Error(r.text);try{return JSON.parse(r.text);}catch{throw Error(r.text.slice(0,2500));}}
try{
 assert.match(await php(`wp_set_current_user(0);try{lpdj_transfer_bundle();echo '"unexpected"';}catch(Throwable $e){echo json_encode($e->getMessage());}`),/Administrator/);console.log('PASS administrator-only transfer');
 assert.match(await php(`try{lpdj_transfer_step(str_repeat('0',64));echo '"unexpected"';}catch(Throwable $e){echo json_encode($e->getMessage());}`),/file changed/);console.log('PASS changed export rejected before writing');
 assert.match(await php(`try{lpdj_transfer_decode('O:8:"stdClass":0:{}');echo '"unexpected"';}catch(Throwable $e){echo json_encode($e->getMessage());}`),/object/);console.log('PASS serialized objects rejected');
 if(encrypted){
  const integrity=await php(`$raw=file_get_contents(LPDJ_TRANSFER_DIR.'/catalogue.json.lpdj');$bad=$raw;$bad[strlen($bad)-1]=chr(ord($bad[strlen($bad)-1])^1);echo wp_json_encode(['valid'=>lpdj_private_decrypt($raw,'catalogue.json')!==false,'tampered'=>lpdj_private_decrypt($bad,'catalogue.json')===false,'wrongName'=>lpdj_private_decrypt($raw,'different.json')===false]);`);
  assert.deepEqual(integrity,{valid:true,tampered:true,wrongName:true});console.log('PASS authenticated encryption: Node/PHP interoperability, tamper rejection and filename binding');
 }
 let state;let last='';let steps=0;
 do{
  state=await php(`try{$b=lpdj_transfer_bundle();$s=lpdj_transfer_step($b['hash'],150);echo wp_json_encode(['phase'=>$s['phase'],'offset'=>$s['offset'],'total'=>$s['total']]);}catch(Throwable $e){http_response_code(500);echo $e->getMessage();}`);
  if(state.phase!==last||state.offset%600===0){console.log('TRANSFER',state.phase,state.offset+'/'+state.total);last=state.phase;}
  if(++steps>60)throw Error('Unexpected transfer loop');
 }while(state.phase!=='done');
 const report=await php(`$b=lpdj_transfer_bundle();$s=get_option('_lpdj_catalogue_transfer_v1');$report=['counts'=>[],'published'=>[],'errors'=>[],'references'=>lpdj_transfer_references($b)];foreach($b['records'] as $old=>$record){$id=$s['ids'][(string)$old];$p=get_post($id);$expected=lpdj_transfer_expected($record,$s['ids']);$report['counts'][$p->post_type]=($report['counts'][$p->post_type]??0)+1;if($p->post_content!==$expected['content'])$report['errors'][]='content:'.$old;if((int)$p->post_author!==get_current_user_id())$report['errors'][]='author:'.$old;foreach($expected['meta'] as $key=>$value)if(get_post_meta($id,$key,true)!==$value)$report['errors'][]='meta:'.$old.':'.$key;if(get_post_meta($id,'_lpdj_published',true))$report['published'][]=$p->post_title;}echo wp_json_encode($report);`);
 assert.deepEqual(report.errors,[]);assert.equal(report.counts.lpdj_problem,1856);assert.equal(report.counts.lpdj_asset,3);assert.equal(report.counts.lpdj_history,3);assert.deepEqual(report.published.sort(),['Equidistant lines','Uneven Floor']);assert.equal(report.references,104);console.log('PASS full catalogue round trip, remapped IDs/ownership, LaTeX, figures, histories and publication snapshots');console.log('PASS all 104 reference files match their SHA-256 hashes');
 const again=await php(`$b=lpdj_transfer_bundle();$s=lpdj_transfer_step($b['hash']);echo wp_json_encode(['phase'=>$s['phase'],'count'=>wp_count_posts('lpdj_problem')->private,'events'=>array_values(array_filter(array_keys(wp_get_scheduled_event('lpdj_notify_published') ? ['unexpected'=>1]:[])))]);`);
 assert.equal(again.phase,'done');assert.equal(+again.count,1856);assert.deepEqual(again.events,[]);console.log('PASS repeating completed import neither duplicates content nor schedules publication mail');
 await fs.writeFile(root+'/private-data/ovh-transfer/'+(encrypted?'isolated-encrypted-test.json':'isolated-test.json'),JSON.stringify({passed:true,steps,report},null,2),{mode:0o600});
 console.log('ALL TRANSFER TESTS PASSED');
}finally{await server[Symbol.asyncDispose]();}
