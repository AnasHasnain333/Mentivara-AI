"""
Guided breathing widget.

It is a small, self-contained HTML/CSS/JS block rendered with
streamlit.components.v1.html. All timing and animation run in the browser, so
Streamlit reruns can never reset the timer or interrupt the animation, and the
widget never needs a webcam or network connection.
"""

BREATHING_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root { --ink:#16323F; --muted:#5B7083; --teal:#0F766E; --blue:#2563A6; --soft:#EEF5F7; --border:#D5E3E8; }
  * { box-sizing: border-box; }
  body { margin:0; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color:var(--ink); background:transparent; }
  .wrap { max-width: 560px; margin: 0 auto; padding: 8px 12px 16px; text-align:center; }
  .settings { display:flex; flex-wrap:wrap; gap:12px; justify-content:center; align-items:center; margin-bottom:12px; }
  .group { display:flex; border:1px solid var(--border); border-radius:8px; overflow:hidden; }
  .group button { border:0; background:#fff; color:var(--ink); padding:8px 14px; font-size:14px; cursor:pointer; min-height:40px; }
  .group button + button { border-left:1px solid var(--border); }
  .group button[aria-pressed="true"] { background:var(--teal); color:#fff; }
  .group button:disabled { opacity:.55; cursor:not-allowed; }
  select, label.chk { font-size:14px; color:var(--ink); }
  select { padding:8px; border:1px solid var(--border); border-radius:8px; background:#fff; min-height:40px; }
  select:disabled, input:disabled { opacity:.55; }
  label.chk { display:flex; align-items:center; gap:6px; min-height:40px; }
  .stage { position:relative; width:min(300px, 80vw); height:min(300px, 80vw); margin: 6px auto 10px; }
  .ring { position:absolute; inset:0; border-radius:50%; border:2px dashed var(--border); }
  #circle { position:absolute; inset:0; margin:auto; width:88%; height:88%; border-radius:50%;
            background:#CDE7E4; border:3px solid var(--teal); transform: scale(.55); will-change: transform; }
  .label { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; pointer-events:none; }
  #phase { font-size: 24px; font-weight:600; }
  #phaseSec { font-size: 40px; font-weight:700; color:var(--teal); line-height:1.1; min-height:44px; }
  .time { font-size:15px; color:var(--muted); margin-bottom:6px; }
  .bar { height:8px; background:var(--soft); border-radius:99px; overflow:hidden; border:1px solid var(--border); }
  #fill { height:100%; width:0%; background:var(--teal); }
  #reminder { min-height:44px; margin:12px 0; color:var(--muted); font-size:15px; }
  .controls { display:flex; gap:10px; justify-content:center; flex-wrap:wrap; }
  .controls button { font-size:16px; min-height:44px; padding:0 20px; border-radius:8px; cursor:pointer; border:1px solid var(--teal); }
  .primary { background:var(--teal); color:#fff; }
  .secondary { background:#fff; color:var(--teal); }
  button:focus-visible, select:focus-visible, input:focus-visible { outline:3px solid var(--blue); outline-offset:2px; }
  .hidden { display:none !important; }
  #done { margin-top:14px; padding:12px; background:var(--soft); border-left:4px solid var(--teal); border-radius:4px; text-align:left; }
  .safety { margin-top:14px; font-size:13px; color:var(--muted); }
</style>
</head>
<body>
<div class="wrap">
  <div class="settings" id="settings">
    <div class="group" role="group" aria-label="Session length">
      <button type="button" data-min="1" aria-pressed="false">1 min</button>
      <button type="button" data-min="3" aria-pressed="true">3 min</button>
      <button type="button" data-min="5" aria-pressed="false">5 min</button>
    </div>
    <select id="pace" aria-label="Breathing pace">
      <option value="4,2,4">Gentle pace (in 4 · hold 2 · out 4)</option>
      <option value="5,2,6">Slower pace (in 5 · hold 2 · out 6)</option>
      <option value="4,0,6">Long exhale (in 4 · out 6)</option>
    </select>
    <label class="chk"><input type="checkbox" id="skipHold"> Skip the hold</label>
  </div>

  <div class="stage">
    <div class="ring"></div>
    <div id="circle"></div>
    <div class="label" aria-live="polite">
      <div id="phase">Ready</div>
      <div id="phaseSec"></div>
    </div>
  </div>

  <div class="time">Time left: <strong id="remain">03:00</strong></div>
  <div class="bar" role="progressbar" aria-label="Session progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" id="bar"><div id="fill"></div></div>
  <div id="reminder">Choose a length and press Start. Breathe at a pace that feels comfortable.</div>

  <div class="controls">
    <button type="button" class="primary" id="start">Start</button>
    <button type="button" class="secondary hidden" id="pause">Pause</button>
    <button type="button" class="primary hidden" id="resume">Resume</button>
    <button type="button" class="secondary hidden" id="stop">Stop</button>
  </div>

  <div id="done" class="hidden" role="status">
    <strong>Well done.</strong> You finished your session. Notice how your body feels right now.
    You can start another round whenever you like.
  </div>
  <div class="safety">You can stop at any time. If you feel dizzy or uncomfortable, stop and breathe normally.
  This exercise is for relaxation only and is not a treatment for any condition.</div>
</div>

<script>
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var MIN_SCALE = reduceMotion ? 0.8 : 0.55, MAX_SCALE = 1.0;
  var REMINDERS = [
    "Let your shoulders drop and soften your jaw.",
    "Breathe at a pace that feels comfortable. There is no right or wrong.",
    "If a thought arrives, let it pass and return to your breath.",
    "Relax your hands. Feel your feet on the floor.",
    "You can stop at any time.",
    "Notice the air moving gently in and out."
  ];

  var state = "idle";            // idle | running | paused | done
  var minutes = 3;
  var phases = [], cycleMs = 0, totalMs = 0, elapsed = 0, last = 0, lastPhaseKey = "";

  function fmt(sec) {
    sec = Math.max(0, Math.ceil(sec));
    var m = Math.floor(sec / 60), s = sec % 60;
    return (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
  }

  function buildPlan() {
    var p = $("pace").value.split(",").map(Number);
    var skip = $("skipHold").checked;
    phases = [{ name: "Breathe in", ms: p[0] * 1000, kind: "in" }];
    if (p[1] > 0 && !skip) phases.push({ name: "Hold gently", ms: p[1] * 1000, kind: "hold" });
    phases.push({ name: "Breathe out", ms: p[2] * 1000, kind: "out" });
    cycleMs = phases.reduce(function (a, ph) { return a + ph.ms; }, 0);
    // whole number of breaths, so the session never ends mid-breath
    var cycles = Math.max(1, Math.round(minutes * 60000 / cycleMs));
    totalMs = cycles * cycleMs;
  }

  function ease(p) { return 0.5 - 0.5 * Math.cos(Math.PI * p); }

  // Pure helper: where are we in the breathing cycle at `elapsedMs`?
  function frameAt(elapsedMs) {
    var t = elapsedMs % cycleMs, i = 0;
    while (i < phases.length - 1 && t >= phases[i].ms) { t -= phases[i].ms; i++; }
    var ph = phases[i], prog = Math.min(1, t / ph.ms), scale;
    if (ph.kind === "in") scale = MIN_SCALE + (MAX_SCALE - MIN_SCALE) * ease(prog);
    else if (ph.kind === "hold") scale = MAX_SCALE;
    else scale = MAX_SCALE - (MAX_SCALE - MIN_SCALE) * ease(prog);
    return { index: i, name: ph.name, secondsLeft: Math.ceil((ph.ms - t) / 1000), scale: scale,
             cycle: Math.floor(elapsedMs / cycleMs) };
  }

  function setButtons() {
    $("start").classList.toggle("hidden", state !== "idle" && state !== "done");
    $("pause").classList.toggle("hidden", state !== "running");
    $("resume").classList.toggle("hidden", state !== "paused");
    $("stop").classList.toggle("hidden", state !== "running" && state !== "paused");
    var locked = (state === "running" || state === "paused");
    document.querySelectorAll(".group button").forEach(function (b) { b.disabled = locked; });
    $("pace").disabled = locked; $("skipHold").disabled = locked;
    $("done").classList.toggle("hidden", state !== "done");
  }

  function render() {
    var f, remainSec, pct;
    if (state === "idle") {
      $("circle").style.transform = "scale(" + MIN_SCALE + ")";
      return;
    }
    if (state === "done") {
      $("circle").style.transform = "scale(" + MIN_SCALE + ")";
      $("phase").textContent = "Complete";
      $("phaseSec").textContent = "";
      $("remain").textContent = "00:00";
      $("fill").style.width = "100%";
      $("bar").setAttribute("aria-valuenow", "100");
      return;
    }
    f = frameAt(elapsed);
    $("circle").style.transform = "scale(" + f.scale.toFixed(4) + ")";
    var key = state + f.name;
    if (state === "paused") { $("phase").textContent = "Paused"; $("phaseSec").textContent = ""; }
    else {
      if (key !== lastPhaseKey) { $("phase").textContent = f.name; }
      $("phaseSec").textContent = f.secondsLeft;
    }
    lastPhaseKey = key;
    remainSec = (totalMs - elapsed) / 1000;
    $("remain").textContent = fmt(remainSec);
    pct = Math.min(100, (elapsed / totalMs) * 100);
    $("fill").style.width = pct.toFixed(1) + "%";
    $("bar").setAttribute("aria-valuenow", String(Math.round(pct)));
    if (state === "running") $("reminder").textContent = REMINDERS[f.cycle % REMINDERS.length];
  }

  function tick(now) {
    if (state === "running") {
      var dt = Math.min(now - last, 200);   // ignore long gaps (hidden tab)
      last = now; elapsed += dt;
      if (elapsed >= totalMs) { elapsed = totalMs; state = "done"; setButtons(); }
    }
    render();
    requestAnimationFrame(tick);
  }

  function resetIdle() {
    state = "idle"; elapsed = 0; lastPhaseKey = "";
    buildPlan();
    $("phase").textContent = "Ready"; $("phaseSec").textContent = "";
    $("remain").textContent = fmt(totalMs / 1000);
    $("fill").style.width = "0%"; $("bar").setAttribute("aria-valuenow", "0");
    $("reminder").textContent = "Choose a length and press Start. Breathe at a pace that feels comfortable.";
    setButtons(); render();
  }

  document.querySelectorAll(".group button").forEach(function (b) {
    b.addEventListener("click", function () {
      minutes = Number(b.getAttribute("data-min"));
      document.querySelectorAll(".group button").forEach(function (x) {
        x.setAttribute("aria-pressed", x === b ? "true" : "false");
      });
      resetIdle();
    });
  });
  $("pace").addEventListener("change", resetIdle);
  $("skipHold").addEventListener("change", resetIdle);

  $("start").addEventListener("click", function () {
    buildPlan(); elapsed = 0; lastPhaseKey = ""; last = performance.now();
    state = "running"; setButtons();
  });
  $("pause").addEventListener("click", function () {
    state = "paused"; $("reminder").textContent = "Paused. Resume when you are ready."; setButtons();
  });
  $("resume").addEventListener("click", function () {
    last = performance.now(); state = "running"; lastPhaseKey = ""; setButtons();
  });
  $("stop").addEventListener("click", resetIdle);

  window.__breathing = { frameAt: frameAt, buildPlan: buildPlan, get total() { return totalMs; } };
  resetIdle();
  requestAnimationFrame(tick);
})();
</script>
</body>
</html>
"""


def breathing_html():
    return BREATHING_HTML
