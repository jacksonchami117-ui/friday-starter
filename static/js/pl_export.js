(function(){
  const tbody = document.querySelector('#export-table tbody');
  const search = document.getElementById('search');
  const btnExport = document.getElementById('btn-export');

  function row(r){
    const tr=document.createElement('tr');
    const cells=[
      r.business,r.first,r.last,r.email,r.website,r.phone||'',r.date||'',window.statusText.compact(r.status),
      r.video||''
    ];
    cells.forEach(c=>{ const td=document.createElement('td'); td.textContent=c||''; tr.appendChild(td);});
    return tr;
  }

  function load(){
    fetch(`/campaigns/${window.CAMPAIGN_ID}/progress.csv`).then(r=>r.text()).then(text=>{
      const lines = text.trim().split(/\r?\n/); if(lines.length===0) return;
      const head = lines.shift().split(',');
      const idx = (name)=> head.indexOf(name);
      const rs = lines.map(l=>l.split(',')).map(a=>({
        business:a[idx('business')]||'',first:a[idx('first')]||'',last:a[idx('last')]||'',
        email:a[idx('email')]||'',website:a[idx('website')]||'',phone:a[idx('phone')]||'',
        date:a[idx('date')]||'',status:a[idx('status')]||'',video:a[idx('video')]||'',thumb:a[idx('thumb')]||''
      }));
      render(rs);
    });
  }

  function render(rs){
    const q = (search.value||'').toLowerCase();
    const r2 = rs.filter(r=>{
      return !q || [r.business,r.first,r.last,r.email,r.website].some(x=> (x||'').toLowerCase().includes(q));
    });
    tbody.innerHTML = ""; r2.forEach(r=>tbody.appendChild(row(r)));
  }

  search.addEventListener('input', load);
  btnExport.addEventListener('click', ()=>{ window.location.href = `/campaigns/${window.CAMPAIGN_ID}/progress.csv`; });
  load();
})();
