const consoleEl = document.getElementById("console");

function stamp() { return new Date().toTimeString().slice(0,8); }
async function typeLine(line, delay=20) {
  for (let i=0;i<line.length;i++) {
    consoleEl.textContent += line[i];
    await new Promise(r=>setTimeout(r,delay));
  }
  consoleEl.textContent += "\n";
}
async function runLog() {
  const lines = [
    `[${stamp()}] INCOMING HTTP REQUEST DETECTED ...`,
    `[${stamp()}] SERVICE WAKING UP ...`,
    `[${stamp()}] ALLOCATING RESOURCES ...`,
    `[${stamp()}] STARTING SYSTEM ...`,
    `[${stamp()}] ENVIRONMENT READY ...`,
  ];
  for (const l of lines) await typeLine(l,15);

  const box = [
    "┌──────────────────────────┐",
    "│   WELCOME TO FRIDAY      │",
    "└──────────────────────────┘"
  ];
  for (const b of box) await typeLine(b,2);

  await typeLine(`[${stamp()}] SYSTEM ONLINE`,15);
  setTimeout(()=> window.location.href="/home",2000);
}

// grid
const gridEl = document.getElementById("grid");
for (let i=0;i<81;i++) {
  const d=document.createElement("div");
  d.className="cell";
  gridEl.appendChild(d);
}
const cells = Array.from(gridEl.children);
setInterval(()=>{
  cells.forEach(c=>c.classList.remove("active"));
  for (let i=0;i<5;i++) cells[Math.floor(Math.random()*cells.length)].classList.add("active");
},200);

runLog();

