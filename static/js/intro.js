(function(){
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const el = document.getElementById('console');
  const lines = [
    'Initiating FRIDAY protocol…',
    'Mission: Orchestrate agents, ship outcomes, keep the hub in sync.',
    'Performing system checks…',
    'Agent link …… OK',
    'Neural net status …… Online',
    'All systems green.',
    'Launching dashboard…'
  ];
  let i = 0;
  function typeLine() {
    if (i >= lines.length) {
      setTimeout(() => window.location.href = '/dashboard', 600);
      return;
    }
    const text = lines[i++];
    if (prefersReduced) {
      el.textContent += text + '\n';
      setTimeout(typeLine, 100);
    } else {
      let idx = 0;
      const timer = setInterval(() => {
        el.textContent = el.textContent + text.charAt(idx++);
        if (idx >= text.length) { clearInterval(timer); el.textContent += '\n'; setTimeout(typeLine, 120); }
      }, 12);
    }
  }
  window.addEventListener('keydown', (e)=>{
    if (e.key === 'Escape' || e.key === 'Enter') {
      window.location.href = '/dashboard';
    }
  });
  typeLine();
})();
