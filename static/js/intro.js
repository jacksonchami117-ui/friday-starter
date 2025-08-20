document.addEventListener("DOMContentLoaded", () => {
  const consoleDiv = document.getElementById("console");

  const logs = [
    "INCOMING HTTP REQUEST DETECTED ...",
    "SERVICE WAKING UP ...",
    "ALLOCATING RESOURCES ...",
    "BOOTING CORE SYSTEMS ...",
    "INITIALIZING F.R.I.D.A.Y. PROTOCOL ...",
    "F.R.I.D.A.Y. = Fully Responsive Intelligent Deployment & Analytics Yield",
    "MISSION: Orchestrate agents, ship outcomes, synchronize hub systems.",
    "Performing system diagnostics...",
    "Agent link ........ OK",
    "Neural net status ... Online",
    "Encryption layer ... Active",
    "All subsystems green.",
    "",
    "███████╗██████╗ ██╗██████╗  █████╗ ██╗   ██╗",
    "██╔════╝██╔══██╗██║██╔══██╗██╔══██╗╚██╗ ██╔╝",
    "█████╗  ██████╔╝██║██████╔╝███████║ ╚████╔╝ ",
    "██╔══╝  ██╔═══╝ ██║██╔═══╝ ██╔══██║  ╚██╔╝  ",
    "███████╗██║     ██║██║     ██║  ██║   ██║   ",
    "╚══════╝╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝   ╚═╝   ",
    "",
    "OPERATION FRIDAY ENGAGED.",
    ">>> Launching dashboard..."
  ];

  function randomTimestamp() {
    const h = String(Math.floor(Math.random() * 24)).padStart(2, "0");
    const m = String(Math.floor(Math.random() * 60)).padStart(2, "0");
    const s = String(Math.floor(Math.random() * 60)).padStart(2, "0");
    return `[${h}:${m}:${s}]`;
  }

  async function typeLine(text, isLast=false) {
    return new Promise(resolve => {
      const line = document.createElement("div");
      consoleDiv.appendChild(line);

      let i = 0;
      function typeChar() {
        if (i < text.length) {
          line.textContent += text[i];
          i++;
          setTimeout(typeChar, 25);
        } else {
          if (isLast) {
            line.classList.add("blink-red");
          } else {
            const cursor = document.createElement("span");
            cursor.className = "cursor";
            line.appendChild(cursor);
          }
          resolve();
        }
      }
      typeChar();
    });
  }

  async function run() {
    for (let j = 0; j < logs.length; j++) {
      const prefix = logs[j].match(/^█/) ? "" : randomTimestamp() + " ";
      await typeLine(prefix + logs[j], j === logs.length-1);
      await new Promise(r => setTimeout(r, 200));
    }
    setTimeout(() => {
      window.location.href = "/home";
    }, 3000);
  }

  run();
});
