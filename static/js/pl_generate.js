(function(){
  const startBtn = document.getElementById('btn-start');
  const jobsWrap = document.getElementById('jobs');
  const bar = document.getElementById('bar');
  const ul = document.getElementById('job-list');

  function li(text){ const li=document.createElement('li'); li.textContent=text; return li; }

  function pollStatus(){
    fetch('/render/status').then(r=>r.json()).then(data=>{
      const total = data.total || (data.items? data.items.length : 0) || 1;
      const done = data.done || (data.items? data.items.filter(x=>x.status==='DONE').length:0);
      const pct = Math.round((done/total)*100);
      bar.style.width = pct + "%";
      ul.innerHTML = "";
      (data.items||[]).slice(-10).forEach(j=>{
        const friendly = window.statusText.toUser(j.status, j.reason);
        ul.appendChild(li(`${friendly.primary}${friendly.detail? ' — '+friendly.detail:''}`));
      });
      if(done < total){ setTimeout(pollStatus, 1500); }
    }).catch(()=> setTimeout(pollStatus, 2000));
  }

  async function startWithManifest(){
    try{
      const manifest = await fetch(`/campaigns/${window.CAMPAIGN_ID}/manifest`).then(r=>r.json());
      // Try new API first
      const res = await fetch('/render/api/start', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ manifest, cid: window.CAMPAIGN_ID })
      });
      if(res.ok){ pollStatus(); return; }
      // Fallback to legacy start
      await fetch('/render/start', { method:'POST' });
      pollStatus();
    }catch(e){
      await fetch('/render/start', { method:'POST' });
      pollStatus();
    }
  }

  startBtn.addEventListener('click', ()=>{
    startBtn.disabled = true;
    jobsWrap.hidden = false;
    startWithManifest();
  });
})();
