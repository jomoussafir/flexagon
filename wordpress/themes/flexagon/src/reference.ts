import {escapeHTML as esc} from '../../../../shared/latex/render.ts';

// Render the requested page explicitly; iPhone's native viewer ignores #page links.
export function mountReference(host:HTMLElement, initial:any, getPage:(page:number)=>Promise<any>, assetBase:string) {
    let current=initial, zoom=1, stopped=false, busy=false, pendingResize=false, loadedUrl='', pdf:any, loading:any, renderTask:any, timer:any;
    host.innerHTML=`<div class="reference-controls"><button class="button secondary small" data-pdf="previous">← Previous</button><form class="reference-page-form"><label>PDF page <input name="page" type="number" min="1" max="${initial.totalPages}" value="${initial.page}" required></label><span>of ${initial.totalPages}</span><button class="button secondary small" type="submit">Go</button></form><button class="button secondary small" data-pdf="next">Next →</button><button class="button secondary small" data-pdf="original">Problem page</button><button class="button secondary small" data-pdf="out" aria-label="Zoom out">−</button><button class="button secondary small" data-pdf="in" aria-label="Zoom in">+</button><a class="text-link reference-file" target="_blank" rel="noopener">Open PDF ↗</a></div><p class="reference-status" role="status"></p><button class="button secondary small reference-retry" hidden>Retry</button><div class="reference-sheet" aria-label="${esc(initial.title)}"></div>`;
    const sheet=host.querySelector<HTMLElement>('.reference-sheet')!;
    const status=host.querySelector<HTMLElement>('.reference-status')!;
    const retry=host.querySelector<HTMLButtonElement>('.reference-retry')!;
    const input=host.querySelector<HTMLInputElement>('input')!;
    const controls=host.querySelectorAll<HTMLButtonElement>('button');
    function setControls() {
        controls.forEach(b=>b.disabled=busy);
        for (const [action,disabled] of Object.entries({previous:current.page<=1,next:current.page>=current.totalPages,original:current.page===initial.originalPage,out:zoom<=1,in:zoom>=3})) {
            host.querySelector<HTMLButtonElement>(`[data-pdf="${action}"]`)!.disabled=busy||disabled;
        }
        input.disabled=busy;input.value=String(current.page);
        host.querySelector<HTMLAnchorElement>('.reference-file')!.href=current.url+'#page='+current.pageInFile;
        sheet.setAttribute('aria-busy',String(busy));
    }
    async function paint(page:number) {
        if(stopped||busy)return;
        busy=true;retry.hidden=true;status.textContent=`Loading PDF page ${page}…`;setControls();
        try {
            const metadata=page>=current.partStart&&page<=current.partEnd?{...current,page,pageInFile:page-current.partStart+1}:await getPage(page);
            if(stopped)return;
            current=metadata;setControls();
            const pdfjs=await import(assetBase+'pdf.mjs');
            if(stopped)return;
            if(loadedUrl!==current.url) {
                await loading?.destroy();
                pdfjs.GlobalWorkerOptions.workerSrc=assetBase+'pdf.worker.mjs';
                loading=pdfjs.getDocument({url:current.url,withCredentials:true,disableRange:true,disableStream:true,isEvalSupported:false,cMapUrl:assetBase+'cmaps/',cMapPacked:true,standardFontDataUrl:assetBase+'standard_fonts/',wasmUrl:assetBase+'wasm/'});
                pdf=await loading.promise;loadedUrl=current.url;
            }
            if(stopped)return;
            const pageObject=await pdf.getPage(current.pageInFile);
            if(stopped)return;
            const base=pageObject.getViewport({scale:1});
            const width=Math.max(1,Math.min(sheet.clientWidth-24,1100))*zoom;
            const ratio=Math.min(window.devicePixelRatio||1,2,Math.sqrt(12000000/(width*width*base.height/base.width)));
            const viewport=pageObject.getViewport({scale:width/base.width*ratio});
            const canvas=document.createElement('canvas');canvas.width=Math.ceil(viewport.width);canvas.height=Math.ceil(viewport.height);
            canvas.style.width=width+'px';canvas.style.height=width*base.height/base.width+'px';
            canvas.setAttribute('role','img');canvas.setAttribute('aria-label',`${initial.title} — PDF page ${current.page}`);
            sheet.replaceChildren(canvas);renderTask=pageObject.render({canvas,canvasContext:canvas.getContext('2d')!,viewport});await renderTask.promise;
            if(!stopped)status.textContent=`PDF page ${current.page} of ${current.totalPages}`;
        } catch(error) {
            if(!stopped){status.textContent='Unable to display this PDF page. Try again or use Open PDF.';retry.hidden=false;}
        } finally {
            busy=false;if(!stopped){setControls();if(pendingResize){pendingResize=false;void paint(current.page);}}
        }
    }
    host.querySelector<HTMLFormElement>('form')!.onsubmit=e=>{e.preventDefault();const page=Number(input.value);if(Number.isInteger(page)&&page>=1&&page<=current.totalPages)void paint(page);};
    host.querySelectorAll<HTMLButtonElement>('[data-pdf]').forEach(button=>button.onclick=()=>{
        const action=button.dataset.pdf;if(busy)return;
        if(action==='in')zoom=Math.min(3,zoom+.5);if(action==='out')zoom=Math.max(1,zoom-.5);
        void paint(action==='previous'?current.page-1:action==='next'?current.page+1:action==='original'?initial.originalPage:current.page);
    });
    retry.onclick=()=>void paint(current.page);
    let width=sheet.clientWidth;
    const observer=new ResizeObserver(()=>{if(sheet.clientWidth===width)return;width=sheet.clientWidth;clearTimeout(timer);timer=setTimeout(()=>{if(busy)pendingResize=true;else void paint(current.page);},150);});
    observer.observe(sheet);void paint(initial.page);
    return ()=>{stopped=true;clearTimeout(timer);observer.disconnect();renderTask?.cancel();void loading?.destroy();};
}
