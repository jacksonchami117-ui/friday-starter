document.addEventListener("DOMContentLoaded", () => {
  const dz = document.getElementById("dropzone");
  const fp = document.getElementById("filepicker");
  const assets = document.getElementById("assets");
  const timeline = document.getElementById("timeline");
  const saveBtn = document.getElementById("saveManifest");
  const startBtn = document.getElementById("startRender");
  const addTextBtn = document.getElementById("addText");
  const preview = document.getElementById("manifestPreview");
  const campaignInput = document.getElementById("campaign-id");

  const segments = []; // {type: "video"|"text", ...}

  function renderManifest(){
    const manifest = { version: 1, segments };
    preview.textContent = JSON.stringify(manifest, null, 2);
    return manifest;
  }

  function addVideoSegment(path, start=0, end=null){
    segments.push({ type: "video", src: path, start, end });
    drawTimeline();
    renderManifest();
  }

  function addTextOverlay(){
    const text = prompt("Text:");
    if(!text) return;
    const start = parseFloat(prompt("Start seconds:", "0")) || 0;
    const endRaw = prompt("End seconds (optional):", "");
    const end = endRaw === "" ? null : parseFloat(endRaw);
    const fontsize = parseInt(prompt("Font size:", "48")) || 48;
    segments.push({ type: "text", text, start, end, x: "(w-text_w)/2", y: "(h-text_h)-50", fontsize, fontcolor: "white" });
    drawTimeline();
    renderManifest();
  }

  function drawTimeline(){
    timeline.innerHTML = "";
    segments.forEach((s, i) => {
      const div = document.createElement("div");
      div.className = "tl-item " + (s.type === "text" ? "text" : "video");
      if(s.type === "video"){
        div.textContent = `#${i+1} VIDEO ${s.src.split("/").slice(-1)[0]} [${s.start || 0}s - ${s.end ?? "end"}]`;
      }else{
        div.textContent = `#${i+1} TEXT "${s.text}" [${s.start || 0}s - ${s.end ?? "∞"}]`;
      }
      div.onclick = () => {
        if(s.type === "video"){
          const ns = parseFloat(prompt("Start seconds:", s.start ?? 0)) || 0;
          const neRaw = prompt("End seconds (blank = clip end):", s.end ?? "");
          s.start = ns; s.end = (neRaw === "" ? null : parseFloat(neRaw));
        } else {
          const nt = prompt("Text:", s.text) || s.text;
          const ns = parseFloat(prompt("Start seconds:", s.start ?? 0)) || 0;
          const neRaw = prompt("End seconds (blank = none):", s.end ?? "");
          s.text = nt; s.start = ns; s.end = (neRaw === "" ? null : parseFloat(neRaw));
        }
        drawTimeline();
        renderManifest();
      };
      timeline.appendChild(div);
    });
  }

  // Uploads
  function uploadFiles(files){
    [...files].forEach(async (file) => {
      const fd = new FormData();
      fd.append("file", file);
      const r = await fetch(window.__uploadsEndpoint, { method: "POST", body: fd });
      if(!r.ok){ alert("Upload failed"); return; }
      const j = await r.json();
      const li = document.createElement("li");
      li.dataset.path = j.path;
      li.textContent = `${j.filename} (${(file.size/1024/1024).toFixed(2)} MB)`;
      li.onclick = () => addVideoSegment(j.path, 0, null);
      assets.appendChild(li);
    });
  }

  dz.onclick = () => fp.click();
  dz.ondragover = (e) => { e.preventDefault(); dz.classList.add("hover"); };
  dz.ondragleave = () => dz.classList.remove("hover");
  dz.ondrop = (e) => { e.preventDefault(); dz.classList.remove("hover"); uploadFiles(e.dataTransfer.files); };
  fp.onchange = (e) => uploadFiles(fp.files);

  addTextBtn.onclick = addTextOverlay;

  saveBtn.onclick = async () => {
    const manifest = renderManifest();
    const r = await fetch(window.__saveManifestEndpoint, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(manifest) });
    const j = await r.json();
    if(!j.ok){ alert("Save failed"); return; }
    saveBtn.dataset.manifestId = j.manifest_id;
    alert("Saved manifest: " + j.manifest_id);
  };

  startBtn.onclick = async () => {
    let manifest_id = saveBtn.dataset.manifestId;
    if(!manifest_id){
      const manifest = renderManifest();
      // direct start without saving first
      const r = await fetch(window.__renderStartEndpoint, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ manifest }) });
      const j = await r.json();
      if(!j.ok){ alert("Start failed"); return; }
      alert("Job started: " + j.job_id);
      return;
    }
    const r = await fetch(window.__renderStartEndpoint, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ manifest_id }) });
    const j = await r.json();
    if(!j.ok){ alert("Start failed"); return; }
    alert("Job started: " + j.job_id);
  };

  document.getElementById("add-scroll").onclick = () => {
    const seg = document.createElement("div");
    seg.className = "segment scroll";
    seg.textContent = "Scroll Segment";
    timeline.appendChild(seg);
  };

  document.getElementById("add-page").onclick = () => {
    const seg = document.createElement("div");
    seg.className = "segment page";
    seg.textContent = "New Page";
    timeline.appendChild(seg);
  };

  document.getElementById("save-manifest").onclick = () => {
    const cid = campaignInput.value.trim() || "demo";
    const segments = [...timeline.querySelectorAll(".segment")].map(s => ({
      type: s.className.replace("segment ", ""),
      label: s.textContent
    }));
    fetch(`/editor/save/${cid}`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({segments})
    }).then(r=>r.json()).then(d=>alert("Saved "+d.path));
  };

  document.getElementById("load-manifest").onclick = () => {
    const cid = campaignInput.value.trim() || "demo";
    fetch(`/editor/load/${cid}`).then(r=>r.json()).then(data=>{
      timeline.innerHTML="";
      if(data.segments){
        data.segments.forEach(seg=>{
          const div=document.createElement("div");
          div.className="segment "+seg.type;
          div.textContent=seg.label||seg.type;
          timeline.appendChild(div);
        });
      } else alert("No manifest for "+cid);
    });
  };
});
