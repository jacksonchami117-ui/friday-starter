
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
    "",
    "",
    "┌──────────────────────────────────────────┐",
    "│         W E L C O M E   T O              │",
    "│               F R I D A Y                │",
    "└──────────────────────────────────────────┘", 
    "",
    ""
  ];
  for (const row of box) await typeLine(row, 2);

  await typeLine("", 1);
  await typeLine(`[${stamp()}] SYSTEM ONLINE ✅`, 15);
  await typeLine("", 1);
  setTimeout(()=> window.location.href="/home", 2000);
}

// grid
const gridEl = document.getElementById("grid");
const SIZE = 9;
function buildGrid() {
  gridEl.innerHTML = "";
  for (let i = 0; i < SIZE * SIZE; i++) {
    const d = document.createElement("div");
    d.className = "cell";
    gridEl.appendChild(d);
  }
}
function animateGrid() {
  const cells = Array.from(gridEl.children);
  let cx = SIZE - 3, cy = 1;
  const shapes = [
    [[0,0],[1,0],[2,0],[1,1]],
    [[0,0],[0,1],[0,2],[1,2]],
    [[1,0],[0,1],[1,1],[2,1],[1,2]],
    [[0,0],[1,0],[0,1],[1,1]],
  ];
  let s = 0;
  setInterval(() => {
    cells.forEach(c => c.classList.remove("active"));
    const shape = shapes[s % shapes.length];
    shape.forEach(([dx, dy]) => {
      const x = Math.max(0, Math.min(SIZE-1, cx + dx));
      const y = Math.max(0, Math.min(SIZE-1, cy + dy));
      cells[y * SIZE + x].classList.add("active");
    });
    cx += Math.random() > 0.5 ? 1 : -1;
    cy += Math.random() > 0.5 ? 1 : -1;
    if (cx < 1) cx = 1; if (cx > SIZE-3) cx = SIZE-3;
    if (cy < 1) cy = 1; if (cy > SIZE-3) cy = SIZE-3;
    s++;
  }, 180);
}
(function () { buildGrid(); animateGrid(); runLog(); })();
