/* Эхо — landing: blocks appear each time they scroll into view, the connection phone plays the
   steps by itself, the hero phone plays the story. Without JavaScript or with "reduce motion"
   everything is simply shown. */
(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasIO = "IntersectionObserver" in window;
  var each = function (list, fn) { Array.prototype.forEach.call(list, fn); };

  // 0. Phone width: the bottom button shows once the hero button is scrolled away, hides at the end.
  var sticky = document.querySelector(".sticky-cta");
  if (sticky) {
    if (!hasIO) { sticky.classList.add("on"); }
    else {
      var heroGone = false, endSeen = false;
      var upd = function () { sticky.classList.toggle("on", heroGone && !endSeen); };
      var heroBtn = document.querySelector(".hero .cta"), fin = document.querySelector(".final");
      if (heroBtn) new IntersectionObserver(function (e) { heroGone = !e[0].isIntersecting && e[0].boundingClientRect.top < 0; upd(); }).observe(heroBtn);
      if (fin) new IntersectionObserver(function (e) { endSeen = e[0].isIntersecting; upd(); }).observe(fin);
    }
  }

  // 1. Blocks appear every time they come into view (scrolling down and up).
  var blocks = document.querySelectorAll(".reveal");
  if (reduce || !hasIO) {
    each(blocks, function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { e.target.classList.toggle("in", e.isIntersecting); });
    }, { threshold: 0.08 });
    each(blocks, function (el) { io.observe(el); });
  }

  // 2. Connection: one phone shows the steps one after another; buttons and swipes switch them.
  var box = document.querySelector(".connect");
  var shots = document.querySelectorAll(".shot");
  var steps = document.querySelectorAll(".step[data-shot]");
  var caps = document.querySelectorAll(".cap");
  if (box && shots.length) {
    var STEP_MS = 4000, cur = 0, timer = null, visible = !hasIO, holdUntil = 0;
    box.style.setProperty("--step-ms", STEP_MS + "ms");
    var go = function (i) {
      cur = (i + shots.length) % shots.length;
      each(shots, function (s, k) { s.classList.toggle("on", k === cur); });
      each(caps, function (s, k) { s.classList.toggle("on", k === cur); });
      each(steps, function (s, k) {
        s.classList.remove("cur");
        if (k === cur) { void s.offsetWidth; s.classList.add("cur"); }
      });
    };
    var tick = function () {
      clearTimeout(timer);
      if (reduce) return;
      timer = setTimeout(function () {
        if (visible && Date.now() >= holdUntil) go(cur + 1);
        tick();
      }, STEP_MS);
    };
    var hold = function () { holdUntil = Date.now() + 2 * STEP_MS; box.classList.add("paused");
      setTimeout(function () { box.classList.remove("paused"); }, 2 * STEP_MS); };
    each(steps, function (s) {
      s.addEventListener("click", function () { go(+s.getAttribute("data-shot")); hold(); tick(); });
    });
    var phoneEl = box.querySelector(".shots"), x0 = null;
    phoneEl.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    phoneEl.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) { go(cur + (dx < 0 ? 1 : -1)); hold(); tick(); }
    });
    if (hasIO) {
      new IntersectionObserver(function (en) {
        visible = en[0].isIntersecting;
        if (visible) { go(cur); tick(); }
      }, { threshold: 0.3 }).observe(box);
    }
    if (reduce) box.classList.add("paused");
    tick();
  }

  // 3. The hero phone: Алина writes and deletes → the notice → her voice note gets a transcript →
  //    she edits a message → the notice with «Было» and «Стало». Then again.
  var phone = document.querySelector(".phone.tg");
  if (!phone || reduce) return;
  phone.classList.add("story");
  var q = function (name) { return phone.querySelector('[data-s="' + name + '"]'); };
  var scene = function (name) { phone.setAttribute("data-scene", name); };
  var show = function (name) { q(name).classList.add("show"); };
  var hide = function (name) { q(name).classList.remove("show"); };
  var plan = [
    [0, function () {
      each(phone.querySelectorAll("[data-s]"), function (el) { el.classList.remove("show", "del", "edited"); });
      scene("chat");
    }],
    [700, function () { show("msg"); }],
    [2600, function () { q("msg").classList.add("del"); }],
    [3500, function () { hide("msg"); }],
    [3900, function () { scene("bot"); }],
    [4300, function () { show("notice"); }],
    [7600, function () { scene("chat"); }],
    [8200, function () { show("voice"); }],
    [9700, function () { show("tr"); }],
    [12300, function () { show("edit"); }],
    [14000, function () { q("edit").classList.add("edited"); }],
    [15400, function () { scene("bot"); }],
    [15800, function () { show("notice2"); }],
  ];
  var LOOP = 20500, timers = [];
  function run() {
    timers.forEach(clearTimeout);
    timers = plan.map(function (p) { return setTimeout(p[1], p[0]); });
    timers.push(setTimeout(run, LOOP));
  }
  run();
})();
