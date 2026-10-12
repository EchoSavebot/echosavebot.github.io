/* Эхо — landing: blocks appear on scroll, connection screenshots follow the steps, the hero phone
   plays a short story. Without JavaScript or with "reduce motion" everything is simply shown. */
(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasIO = "IntersectionObserver" in window;
  var each = function (list, fn) { Array.prototype.forEach.call(list, fn); };

  // 1. Blocks appear when scrolled to.
  var blocks = document.querySelectorAll(".reveal");
  if (reduce || !hasIO) {
    each(blocks, function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    each(blocks, function (el) { io.observe(el); });
  }

  // 2. Connection: the phone shows the screenshot of the step in the middle of the screen.
  var shots = document.querySelectorAll(".shot");
  var steps = document.querySelectorAll(".step[data-shot]");
  function showShot(i) {
    each(shots, function (s, k) { s.classList.toggle("on", k === i); });
    each(steps, function (s, k) { s.classList.toggle("cur", k === i); });
  }
  if (shots.length && hasIO) {
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) showShot(+e.target.getAttribute("data-shot")); });
    }, { rootMargin: "-45% 0px -45% 0px" });
    each(steps, function (s) { so.observe(s); });
  }
  each(steps, function (s) {
    s.addEventListener("mouseenter", function () { showShot(+s.getAttribute("data-shot")); });
  });

  // 3. The hero phone: Алина writes and deletes, Эхо sends the notice, a voice note gets a transcript.
  var phone = document.querySelector(".phone");
  if (!phone || reduce) return;
  phone.classList.add("story");
  var q = function (name) { return phone.querySelector('[data-s="' + name + '"]'); };
  var scene = function (name) { phone.setAttribute("data-scene", name); };
  var show = function (name) { q(name).classList.add("show"); };
  var plan = [
    [0, function () {
      each(phone.querySelectorAll("[data-s]"), function (el) { el.classList.remove("show", "del", "vanish"); });
      scene("chat");
    }],
    [700, function () { show("msg"); }],
    [2600, function () { q("msg").classList.add("del"); }],
    [3700, function () { q("msg").classList.add("vanish"); }],
    [4300, function () { scene("bot"); }],
    [4700, function () { show("notice"); }],
    [8200, function () { q("msg").classList.remove("show"); scene("chat"); }],
    [8800, function () { show("voice"); }],
    [10200, function () { show("tr"); }],
  ];
  var LOOP = 14500, timers = [];
  function run() {
    timers.forEach(clearTimeout);
    timers = plan.map(function (p) { return setTimeout(p[1], p[0]); });
    timers.push(setTimeout(run, LOOP));
  }
  run();
})();
