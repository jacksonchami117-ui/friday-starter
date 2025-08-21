async function fetchJSON(u){ const r = await fetch(u); if(!r.ok) throw new Error("fetch failed"); return r.json(); }

(async function(){
  try{
    const metrics = await fetchJSON("/metrics");
    const el = document.getElementById("metrics");
    el.innerHTML = `
      <div class="kpis">
        <div><div class="kpi">${metrics.jobs_total}</div><div class="muted">Total Jobs</div></div>
        <div><div class="kpi">${metrics.jobs_done}</div><div class="muted">Done</div></div>
        <div><div class="kpi">${metrics.jobs_running}</div><div class="muted">Running</div></div>
        <div><div class="kpi">${metrics.jobs_queued}</div><div class="muted">Queued</div></div>
        <div><div class="kpi">${metrics.jobs_failed}</div><div class="muted">Failed</div></div>
      </div>`;
    const ctx = document.getElementById("jobsChart");
    if (ctx && window.Chart){
      new Chart(ctx, {
        type: "pie",
        data: {
          labels: ["Done","Running","Queued","Failed"],
          datasets: [{ data: [metrics.jobs_done, metrics.jobs_running, metrics.jobs_queued, metrics.jobs_failed] }]
        }
      });
    }
  }catch(e){ console.error(e); }
})();
