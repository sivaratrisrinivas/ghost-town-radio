(() => {
const $ = s => document.querySelector(s);
const voice = $('#voice'), amb = $('#amb'), knob = $('#knob'), playBtn = $('#play');
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
let B, FACTS, SRC, hour = new Date().getHours(), idx = 0, playing = false, level = 0, analyser, actx, buf;
const pad = n => String(n).padStart(2, '0');
const label = h => `${pad(h)}:00`;

async function boot() {
  [B, FACTS, SRC] = await Promise.all(['broadcast', 'facts', 'sources'].map(n => fetch(`data/${n}.json`).then(r => r.json())));
  buildScale(); buildSchedule(); setHour(hour, true);
  if (!reduced) initGhosts();
  if (location.hash.startsWith('#h')) setHour(+location.hash.slice(2) % 24, true);
}
function buildScale() {
  const s = $('#scale');
  for (let h = 0; h < 24; h++) {
    const t = document.createElement('div'); t.className = 'tick' + (h % 3 === 0 ? ' major' : '');
    if (h % 3 === 0) t.innerHTML = `<span>${h}</span>`; s.appendChild(t);
  }
}
function buildSchedule() {
  const ol = $('#schedule');
  B.hours.forEach(H => {
    const li = document.createElement('li'), b = document.createElement('button');
    b.innerHTML = `<b>${label(H.hour)}</b><span>${H.title}</span>`;
    b.onclick = () => { setHour(H.hour, true); if (!playing) toggle(); };
    li.appendChild(b); ol.appendChild(li);
  });
}
function setHour(h, restart) {
  hour = (h + 24) % 24;
  const H = B.hours[hour];
  const pct = 4 + (hour / 23) * 92;
  $('#needle').style.left = pct + '%';
  $('#clock').textContent = label(hour); $('#theme').textContent = H.title;
  knob.setAttribute('aria-valuenow', hour); knob.setAttribute('aria-valuetext', `${label(hour)}, ${H.title}`);
  $('.knob-face').style.transform = `rotate(${-150 + (hour / 23) * 300}deg)`;
  document.documentElement.style.setProperty('--h', (250 + hour * 11) % 360);
  document.querySelectorAll('#schedule button').forEach((b, i) => b.setAttribute('aria-current', i === hour));
  freq(hour);
  if (restart) { idx = 0; showLine(); if (playing) playLine(); else show(null); }
}
function freq(h) { $('#freq').textContent = (540 + h * 37.5).toFixed(1); }
function tick() { if (navigator.vibrate) navigator.vibrate(6); click(); }
function click() {
  if (!actx) return; const o = actx.createOscillator(), g = actx.createGain();
  o.frequency.value = 1800; g.gain.value = .04; g.gain.exponentialRampToValueAtTime(.0001, actx.currentTime + .03);
  o.connect(g).connect(actx.destination); o.start(); o.stop(actx.currentTime + .03);
}
// ---- knob: pointer drag by angle, haptic-feeling easing, keyboard slider
let dragging = false, lastA = 0, acc = 0, base = 0;
const ang = e => { const r = knob.getBoundingClientRect(); return Math.atan2(e.clientY - (r.top + r.height / 2), e.clientX - (r.left + r.width / 2)) * 180 / Math.PI; };
knob.addEventListener('pointerdown', e => { dragging = true; knob.setPointerCapture(e.pointerId); knob.classList.add('drag'); lastA = ang(e); acc = 0; base = hour; });
knob.addEventListener('pointermove', e => {
  if (!dragging) return; let a = ang(e), d = a - lastA; if (d > 180) d -= 360; if (d < -180) d += 360; lastA = a; acc += d;
  const h = Math.max(0, Math.min(23, Math.round(base + acc / (300 / 23))));
  if (h !== hour) { hour = h; tick(); preview(h); }
  $('.knob-face').style.transform = `rotate(${-150 + ((base + acc / (300 / 23)) / 23) * 300}deg)`;
});
const end = () => { if (!dragging) return; dragging = false; knob.classList.remove('drag'); setHour(hour, true); };
knob.addEventListener('pointerup', end); knob.addEventListener('pointercancel', end);
function preview(h) { $('#needle').style.left = (4 + h / 23 * 92) + '%'; $('#clock').textContent = label(h); $('#theme').textContent = B.hours[h].title; freq(h); }
knob.addEventListener('keydown', e => {
  const k = { ArrowRight: 1, ArrowUp: 1, ArrowLeft: -1, ArrowDown: -1, PageUp: 3, PageDown: -3 }[e.key];
  if (k) { e.preventDefault(); setHour(hour + k, true); tick(); }
  if (e.key === 'Home') { e.preventDefault(); setHour(0, true); }
  if (e.key === 'End') { e.preventDefault(); setHour(23, true); }
});
document.addEventListener('keydown', e => { if (e.code === 'Space' && !['BUTTON', 'A'].includes(document.activeElement.tagName)) { e.preventDefault(); toggle(); } });
// ---- playback
function initAudio() {
  if (actx) return; actx = new (window.AudioContext || window.webkitAudioContext)();
  analyser = actx.createAnalyser(); analyser.fftSize = 256; buf = new Uint8Array(analyser.frequencyBinCount);
  for (const el of [voice, amb]) { const s = actx.createMediaElementSource(el), g = actx.createGain(); g.gain.value = el === amb ? .35 : 1; s.connect(g); g.connect(analyser); g.connect(actx.destination); el._g = g; }
}
function toggle() {
  playing = !playing; initAudio();
  playBtn.setAttribute('aria-pressed', playing); playBtn.setAttribute('aria-label', playing ? 'Pause broadcast' : 'Play broadcast');
  $('#playicon').setAttribute('d', playing ? 'M7 5h4v14H7zM13 5h4v14h-4z' : 'M8 5v14l11-7z'); $('#onair').classList.toggle('live', playing);
  if (playing) { actx.resume(); amb.play().catch(() => {}); playLine(); } else { voice.pause(); amb.pause(); clearTimeout(silT); }
}
playBtn.onclick = toggle; $('#skip').onclick = () => next();
const L = () => B.hours[hour].lines[idx];
let silT;
function playLine() {
  const l = L(); show(l); clearTimeout(silT);
  if (l.audio) { voice.src = l.audio; voice.play().catch(() => {}); } else { silT = setTimeout(next, 3500); }
}
voice.addEventListener('ended', () => setTimeout(next, 450));
function next() {
  idx++; if (idx >= B.hours[hour].lines.length) { hour = (hour + 1) % 24; setHour(hour, false); idx = 0; }
  if (playing) playLine(); else showLine();
}
function showLine() { show(null); }
function esc(s) { return s.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c])); }
function show(l) {
  const k = $('#kicker'), said = $('#said'), q = $('#quote'), c = $('#cite');
  if (!l) { k.textContent = 'Press play. The DJ only says what the archives said.'; said.textContent = ''; q.innerHTML = ''; c.textContent = ''; return; }
  if (l.type === 'silence') { k.textContent = 'Static. The archive has nothing on this, so the DJ says nothing.'; said.textContent = ''; q.innerHTML = ''; c.textContent = ''; return; }
  if (l.type === 'bridge') { k.textContent = `Hollis Vane, linking. No facts in this line.`; said.textContent = l.text; q.innerHTML = ''; c.textContent = ''; return; }
  const f = FACTS[l.fact_id], s = SRC[f.source_id];
  k.textContent = l.type === 'quote' ? 'Word for word, from the paper' : 'The claim, and the words behind it';
  said.textContent = f.claim;
  q.innerHTML = l.type === 'quote' ? `<mark>“${esc(f.quote)}”</mark>` : `“${esc(f.quote)}”`;
  c.innerHTML = `${esc(s.title)} · ${s.date} · <a href="${s.url}" target="_blank" rel="noopener">Read the page on archive.org</a> · ${esc(s.license_short)}`;
}
// ---- ghosts canvas (30fps, DPR capped, pauses when hidden)
function initGhosts() {
  const cv = $('#ghosts'), g = cv.getContext('2d'); let W, H, last = 0, t = 0;
  const frags = Object.values(FACTS).map(f => f.quote.split(' ').slice(0, 7).join(' ')).sort(() => Math.random() - .5).slice(0, 14);
  const items = frags.map((s, i) => ({ s, x: Math.random(), y: Math.random(), v: .01 + Math.random() * .02, p: Math.random() * 6 }));
  const blobs = Array.from({ length: 7 }, (_, i) => ({ x: Math.random(), y: Math.random(), r: .25 + Math.random() * .3, p: Math.random() * 6, hs: i * 37 }));
  const size = () => { const d = Math.min(devicePixelRatio || 1, 1.5); W = cv.width = innerWidth * d; H = cv.height = innerHeight * d; g.setTransform(d, 0, 0, d, 0, 0); W /= d; H /= d; };
  size(); addEventListener('resize', size);
  const frame = ts => {
    requestAnimationFrame(frame); if (document.hidden || ts - last < 33) return; last = ts; t += .033;
    if (analyser && playing) { analyser.getByteFrequencyData(buf); let s = 0; for (let i = 0; i < 40; i++) s += buf[i]; level += (s / 40 / 255 - level) * .25; } else level *= .95;
    document.documentElement.style.setProperty('--lvl', level.toFixed(3));
    const hh = (+getComputedStyle(document.documentElement).getPropertyValue('--h') || 268);
    g.globalCompositeOperation = 'source-over'; g.fillStyle = '#07060b'; g.fillRect(0, 0, W, H); g.globalCompositeOperation = 'lighter';
    for (const b of blobs) {
      const x = (b.x + Math.sin(t * .1 + b.p) * .15) * W, y = (b.y + Math.cos(t * .08 + b.p) * .15) * H, r = (b.r + level * .35) * Math.max(W, H);
      const gr = g.createRadialGradient(x, y, 0, x, y, r); const hue = (hh + b.hs + t * 6) % 360;
      gr.addColorStop(0, `hsla(${hue},85%,${40 + level * 30}%,.22)`); gr.addColorStop(1, 'transparent'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
    }
    g.globalCompositeOperation = 'source-over'; g.font = 'italic 15px Georgia,serif';
    for (const it of items) { it.y -= it.v * .033; if (it.y < -.05) it.y = 1.05; const a = .10 + .06 * Math.sin(t * .5 + it.p) + level * .15;
      g.fillStyle = `rgba(243,234,215,${a})`; g.fillText(it.s, ((it.x + Math.sin(t * .05 + it.p) * .03) * (W - 220)), it.y * H); }
  };
  requestAnimationFrame(frame);
}
boot();
})();
