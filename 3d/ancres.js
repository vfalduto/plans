/* Ancres communes à toutes les pages à sommaire (inséré tel quel par les générateurs et dans les pages statiques).
   - chaque titre h2 reçoit un id lisible (« plan », « debit »…), suffixé par la version figée s'il y en a une ;
   - un clic sur un lien du sommaire ou sur un titre h2 met l'ancre dans l'adresse (#…) ;
   - une adresse avec ancre ouvre la bonne version et défile jusqu'au titre ; précédent / suivant aussi. */
(function () {
  function slug(t) {
    return t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "section";
  }
  function texte(h) {
    var c = h.cloneNode(true);
    c.querySelectorAll("a, span, button").forEach(function (x) { x.remove(); });
    return c.textContent.trim() || h.textContent.trim();
  }
  var pris = {};
  document.querySelectorAll("[id]").forEach(function (e) { pris[e.id] = true; });
  function ancre(h) {          // titre d'une section qui porte déjà l'id (Changements) : l'ancre est celle de la section
    if (h.id) return h.id;
    var p = h.parentNode;
    if (p && p.tagName === "SECTION" && p.id && p.querySelector("h2") === h) return p.id;
    var ver = h.closest(".ver"), suf = ver && ver.dataset.v && ver.dataset.v !== "courante" ? "-" + slug(ver.dataset.v) : "";
    var base = slug(texte(h)) + suf, id = base, k = 2;
    while (pris[id]) id = base + "-" + k++;
    pris[id] = true;
    h.id = id;
    return id;
  }
  document.querySelectorAll("h2").forEach(ancre);
  var st = document.createElement("style");
  st.textContent = "h2[id],section[id]>h2{cursor:pointer}h2[id]:hover::after,section[id]>h2:hover::after" +
    "{content:' #';color:var(--muted,#888);font-weight:400}";
  document.head.appendChild(st);
  function cible(id) {
    var e = id && document.getElementById(id);
    if (e && e.tagName === "SECTION") e = e.querySelector("h2") || e;
    return e;
  }
  function montrer(e) {        // titre dans une version cachée : basculer sur cette version d'abord
    var ver = e.closest(".ver[hidden]");
    if (ver) {
      var b = document.querySelector('.vbar button[data-v="' + ver.dataset.v + '"]');
      if (b) b.click();
    }
  }
  function va(id, doux) {
    var e = cible(id);
    if (!e) return;
    montrer(e);
    e.scrollIntoView({behavior: doux ? "smooth" : "auto"});
  }
  function pose(id) {
    if (location.hash !== "#" + id) history.pushState(null, "", "#" + id);
  }
  document.addEventListener("click", function (ev) {
    var a = ev.target.closest(".toc a[href^='#']");
    if (a) { pose(decodeURIComponent(a.getAttribute("href").slice(1))); return; }
    var h = ev.target.closest("h2");
    if (h && !ev.target.closest("a, button, summary")) {
      var id = ancre(h);
      pose(id);
      va(id, true);
    }
  }, true);
  window.addEventListener("popstate", function () { va(decodeURIComponent(location.hash.slice(1)), true); });
  window.addEventListener("load", function () {
    if (location.hash) setTimeout(function () { va(decodeURIComponent(location.hash.slice(1)), false); }, 0);
  });
})();
