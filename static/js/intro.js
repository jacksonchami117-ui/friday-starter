const consoleEl = document.getElementById("console");

function printLine(text, delay = 50, callback) {
  let i = 0;
  const interval = setInterval(() => {
    consoleEl.innerHTML += text[i];
    i++;
    if (i >= text.length) {
      clearInterval(interval);
      consoleEl.innerHTML += "\n\n"; // extra spacing
      if (callback) callback();
    }
  }, delay);
}

function printAscii(asciiArray, delay = 200) {
  asciiArray.forEach((line, i) => {
    setTimeout(() => {
      consoleEl.innerHTML += line + "\n";
    }, i * delay);
  });
}

// Clean ASCII for FRIDAY (centered block letters)
const fridayAscii = [
"███████╗██████╗ ██╗██████╗  █████╗ ██╗   ██╗",
"██╔════╝██╔══██╗██║██╔══██╗██╔══██╗╚██╗ ██╔╝",
"█████╗  ██████╔╝██║██████╔╝███████║ ╚████╔╝ ",
"██╔══╝  ██╔═══╝ ██║██╔═══╝ ██╔══██║  ╚██╔╝  ",
"██║     ██║     ██║██║     ██║  ██║   ██║   ",
"╚═╝     ╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝   ╚═╝   "
];

// Boot sequence lines
const lines = [
  "[06:34:30] INCOMING HTTP REQUEST DETECTED ...",
  "[07:12:38] SERVICE WAKING UP ...",
  "[09:45:59] ALLOCATING RESOURCES ...",
  "[10:25:51] BOOTING CORE SYSTEMS ...",
  "[11:31:41] INITIALIZING FRIDAY PROTOCOL ...",
  "[13:45:50] F.R.I.D.A.Y = Fully Responsive Intelligent Deployment & Analytics Yield",
  "[15:09:56] MISSION: Orchestrate agents, ship outcomes, synchronize hub systems.",
  "[16:22:05] PERFORMING SYSTEM DIAGNOSTICS ...",
  "[17:07:37] AGENT LINK ........ OK",
  "[18:05:41] NEURAL NET STATUS ... ONLINE",
  "[19:44:05] ENCRYPTION LAYER ... ACTIVE",
  "[20:35:15] ALL SUBSYSTEMS GREEN.",
  ""
];

// Print sequence
function runIntro() {
  let idx = 0;
  function next() {
    if (idx < lines.length) {
      printLine(lines[idx], 25, () => {
        idx++;
        next();
      });
    } else {
      // ASCII logo after logs
      setTimeout(() => {
        printAscii(fridayAscii, 300);
        setTimeout(() => {
          printLine("OPERATION F.R.I.D.A.Y. ENGAGED", 40, () => {
            setTimeout(() => {
              window.location.href = "/home";
            }, 2500);
          });
        }, 2500);
      }, 800);
    }
  }
  next();
}

runIntro();
