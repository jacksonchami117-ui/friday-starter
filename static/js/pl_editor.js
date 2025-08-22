(function(){
  const cid = window.CAMPAIGN_ID;
  const assetsUl = document.getElementById('asset-list');
  const trackVideo = document.getElementById('track-video');
  const trackOver = document.getElementById('track-overlays');
  const timeline = document.getElementById('timeline');
  const zoomInput = document.getElementById('zoom');
  const stageVideo = document.getElementById('stage-video');
  const overlayLayer = document.getElementById('overlay-layer');
  const btnSave = document.getElementById('btn-save');
  const btnAddText = document.getElementById('btn-add-text');

  let manifest = { segments: [], overlays: [] };
  let pxPerSec = 80; // base zoom

  function timeToX(t){ return Math.round(t * pxPerSec); }
  function xToTime(x){ return Math.max(0, x / pxPerSec); }

  function loadAssets(){
    fetch(`/campaigns/${cid}/assets`).then(r=>r.json()).then(d=>{
      assetsUl.innerHTML='';
      (d.items||[]).forEach(item=>{
        const li = document.createElement('li');
        li.className='asset-item';
        li.setAttribute('draggable','true');
        li.dataset.name=item.name;
        li.dataset.url=item.url;
        li.dataset.type=item.type;
        li.innerHTML = (item.thumb? `<img src="${item.thumb}" alt="">` : `<div style="width:56px;height:36px;border-radius:6px;background:#232739"></div>`) + 
                       `<div class="meta"><div class="name" title="${item.name}">${item.name}</div><div class="muted">${item.type}</div></div>`;
        li.addEventListener('dragstart',ev=>{
          ev.dataTransfer.setData('text/plain', JSON.stringify(item));
        });
        assetsUl.appendChild(li);
      });
    });
  }

  function createSeg(name, url, start, end){
    const id = 'seg_'+Math.random().toString(36).slice(2,8);
    manifest.segments.push({ id, src:url, name, start: start||0, end: end||5 });
    draw();
  }

  function createOverlay(text, start, end, x, y){
    const id = 'ov_'+Math.random().toString(36).slice(2,8);
    manifest.overlays.push({ id, text: text||"Your text {{first}}", start:start||0, end:end||3, x:x||20, y:y||20, size:18, color:"#ffffff" });
    draw();
  }

  function draw(){
    // clear tracks
    [trackVideo, trackOver].forEach(t=>{ t.innerHTML=''; t.style.width = Math.max(600, timeToX(totalDuration()+4)) + 'px'; });

    // segments
    manifest.segments.forEach(seg=>{
      const el = document.createElement('div');
      el.className='segment';
      el.tabIndex=0;
      el.dataset.id=seg.id;
      el.style.left = timeToX(seg.start)+'px';
      el.style.width = Math.max(20, timeToX(seg.end-seg.start))+'px';
      el.innerHTML = `<div class="name">${seg.name||extractName(seg.src)}</div><div class="handle left"></div><div class="handle right"></div>`;
      addSegHandlers(el, seg, trackVideo);
      trackVideo.appendChild(el);
    });

    // overlays
    manifest.overlays.forEach(ov=>{
      const el = document.createElement('div');
      el.className='segment';
      el.tabIndex=0;
      el.dataset.id=ov.id;
      el.style.left = timeToX(ov.start)+'px';
      el.style.width = Math.max(20, timeToX(ov.end-ov.start))+'px';
      el.innerHTML = `<div class="name">"${ov.text}"</div><div class="handle left"></div><div class="handle right"></div>`;
      addSegHandlers(el, ov, trackOver, true);
      trackOver.appendChild(el);
    });

    renderOverlayLayer();
  }

  function extractName(u){ try { return decodeURIComponent(u.split('/').pop()); } catch(e){ return u; } }

  function totalDuration(){
    if(manifest.segments.length===0) return 0;
    return Math.max(...manifest.segments.map(s=>s.end));
  }

  function addSegHandlers(el, item, container, isOverlay){
    function select(){ document.querySelectorAll('.segment').forEach(x=>x.classList.remove('selected')); el.classList.add('selected'); }
    el.addEventListener('mousedown', e=>{ if(e.target.classList.contains('handle')) return; select(); dragging(e, item, container); });
    el.addEventListener('keydown', e=>{
      if(!el.classList.contains('selected')) return;
      const step = e.shiftKey ? 1 : 0.1;
      if(e.key==='Delete'){ // remove
        if(isOverlay) manifest.overlays = manifest.overlays.filter(x=>x.id!==item.id);
        else manifest.segments = manifest.segments.filter(x=>x.id!==item.id);
        draw(); return;
      }
      if(['ArrowLeft','ArrowRight'].includes(e.key)){
        const delta = (e.key==='ArrowLeft'?-step:step);
        item.start = Math.max(0, item.start + delta);
        item.end = Math.max(item.start+0.1, item.end + delta);
        draw();
      }
    });
    // resize left/right
    el.querySelector('.handle.left').addEventListener('mousedown', e=>resizing(e,item,true));
    el.querySelector('.handle.right').addEventListener('mousedown', e=>resizing(e,item,false));
  }

  function dragging(e, item, container){
    const startX = e.clientX, origLeft = timeToX(item.start);
    const onMove = (ev)=>{
      const dx = ev.clientX - startX;
      const nx = Math.max(0, origLeft + dx);
      item.start = xToTime(nx);
      item.end = Math.max(item.start+0.1, item.end + xToTime(dx));
      draw();
    };
    const onUp = ()=>{ window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
  }

  function resizing(e, item, leftSide){
    e.stopPropagation();
    const startX = e.clientX, origStart = item.start, origEnd = item.end;
    const onMove = (ev)=>{
      const dx = ev.clientX - startX;
      if(leftSide){
        const ns = Math.max(0, origStart + xToTime(dx));
        item.start = Math.min(ns, item.end-0.1);
      }else{
        const ne = Math.max(origStart+0.1, origEnd + xToTime(dx));
        item.end = ne;
      }
      draw();
    };
    const onUp = ()=>{ window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
  }

  // Overlay layer: show first overlay text at approximate position
  function renderOverlayLayer(){
    overlayLayer.innerHTML='';
    manifest.overlays.forEach(ov=>{
      const box = document.createElement('div');
      box.className='overlay-box';
      box.style.left = (ov.x||20) + 'px';
      box.style.top = (ov.y||20) + 'px';
      box.style.fontSize = (ov.size||18) + 'px';
      box.style.color = ov.color || '#fff';
      box.textContent = ov.text;
      box.setAttribute('contenteditable','false');
      box.addEventListener('dblclick', ()=>{
        box.setAttribute('contenteditable','true'); box.focus();
      });
      box.addEventListener('blur', ()=>{
        box.setAttribute('contenteditable','false'); 
        ov.text = box.textContent.trim() || ov.text;
      });
      overlayLayer.appendChild(box);
    });
  }

  // Drag target: video track
  trackVideo.addEventListener('dragover', e=>{ e.preventDefault(); });
  trackVideo.addEventListener('drop', e=>{
    e.preventDefault();
    const data = e.dataTransfer.getData('text/plain');
    if(!data) return;
    const item = JSON.parse(data);
    const t = xToTime(e.offsetX);
    createSeg(item.name, item.url, t, t+5);
  });

  // Text overlay add
  btnAddText.addEventListener('click', ()=> createOverlay("Your text {{first}}", 0, 3, 20, 20));

  // Save manifest
  btnSave.addEventListener('click', ()=>{
    fetch(`/campaigns/${cid}/manifest`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify(manifest)
    }).then(r=>r.json()).then(d=>{
      if(d && d.ok) alert("Saved.");
      else alert("Save failed.");
    }).catch(()=>alert("Save failed."));
  });

  // Asset upload (library dropzone)
  const dz = document.getElementById('asset-drop');
  const fi = document.getElementById('asset-file');
  function uploadOne(file){
    const fd = new FormData();
    fd.append('file', file);
    return fetch(`/campaigns/${cid}/assets/upload`, { method:'POST', body: fd }).then(r=>r.json());
  }
  function pick(){ fi.click(); }
  fi.addEventListener('change', ()=>{
    const files = Array.from(fi.files||[]);
    Promise.all(files.map(uploadOne)).then(loadAssets);
  });
  dz.addEventListener('click', pick);
  dz.addEventListener('dragover', e=>{ e.preventDefault(); dz.classList.add('drag');});
  dz.addEventListener('dragleave', ()=> dz.classList.remove('drag'));
  dz.addEventListener('drop', e=>{
    e.preventDefault(); dz.classList.remove('drag');
    const files = Array.from(e.dataTransfer.files||[]);
    Promise.all(files.map(uploadOne)).then(loadAssets);
  });

  // Zoom
  zoomInput.addEventListener('input', ()=>{
    pxPerSec = 80 * parseFloat(zoomInput.value||'1');
    draw();
  });

  // Load manifest + assets
  fetch(`/campaigns/${cid}/manifest`).then(r=>r.json()).then(m=>{ manifest = m||manifest; draw(); });
  loadAssets();
})();
