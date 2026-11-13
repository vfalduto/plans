/* Interaction des pages de site/ : onglets des vues, état dans l'adresse, menu de gauche, fiche.
   Le contenu est entièrement dans le HTML écrit par commun/gabarit.py : ce script lit ses attributs data-* et montre
   une vue à la fois. Sans lui, la classe sans-js reste sur <html> et les vues se suivent.
   Repris de la maquette validée (plans/maquette/app.html : memo, lire, rail, brancherFiche). */
(function () {
"use strict";

const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];

/* ------------------------------------------------------------------ mémoire du lecteur
   localStorage, sous le préfixe « plans: ». Chaque accès est rattrapé : en navigation privée ou si le stockage est
   bloqué, on lit la valeur par défaut et on n'écrit rien. */
const memo = {
  lit(cle, defaut) {
    try { const v = localStorage.getItem("plans:" + cle); return v === null ? defaut : JSON.parse(v); } catch (e) { return defaut; }
  },
  pose(cle, valeur) {
    try { localStorage.setItem("plans:" + cle, JSON.stringify(valeur)); } catch (e) { /* stockage indisponible */ }
  },
};
const donnees = (id, defaut) => { try { return JSON.parse($("#" + id).textContent); } catch (e) { return defaut; } };

const racine = document.documentElement, app = $("#app");
racine.classList.remove("sans-js");   // déjà fait par le script en tête de page (gabarit.TETE_JS), sauf s'il a échoué
racine.classList.add("js");
const mobile = matchMedia("(max-width:919px)");

/* ------------------------------------------------------------------ menu de gauche
   Ordinateur : réduit à 56 px par défaut, déplié par #b-rail, état mémorisé sous « rail-reduit ».
   Mobile : tiroir ouvert par #b-maison, refermé par « Fermer » ou Échap. */
const bRail = $("#b-rail"), bMaison = $("#b-maison"), bFermer = $("#rail .rail-fermer");
function poserRail(reduit) {
  app.classList.toggle("rail-reduit", reduit);
  if (!bRail) return;
  const action = reduit ? "Déplier le menu" : "Réduire le menu";
  bRail.setAttribute("aria-expanded", String(!reduit));
  bRail.setAttribute("aria-label", action);
  bRail.title = action;
}
function tiroir(ouvert) {
  app.classList.toggle("rail-ouvert", ouvert);
  if (ouvert && bFermer) bFermer.focus();
  else if (!ouvert && bMaison && $("#rail").contains(document.activeElement)) bMaison.focus();
}
poserRail(memo.lit("rail-reduit", true) !== false);
if (bRail) bRail.addEventListener("click", () => {
  const reduit = !app.classList.contains("rail-reduit");
  memo.pose("rail-reduit", reduit);
  poserRail(reduit);
});
if (bMaison) bMaison.addEventListener("click", () => tiroir(true));
if (bFermer) bFermer.addEventListener("click", () => tiroir(false));
document.addEventListener("keydown", e => { if (e.key === "Escape" && app.classList.contains("rail-ouvert")) tiroir(false); });

/* document de la pièce : la valeur de #c-doc est l'adresse relative de la page */
const choixDoc = $("#c-doc");
if (choixDoc) choixDoc.addEventListener("change", () => location.assign(choixDoc.value));

/* ------------------------------------------------------------------ fiche
   Sur ordinateur, un panneau toujours ouvert ; sur mobile, une feuille basse que son titre ouvre et ferme. */
function majFiches() {
  for (const f of $$(".fiche")) {
    const t = $(".fiche-tete", f);
    if (t) t.setAttribute("aria-expanded", String(!mobile.matches || f.classList.contains("ouverte")));
  }
}
for (const f of $$(".fiche")) {
  const t = $(".fiche-tete", f);
  if (t) t.addEventListener("click", () => {
    if (!mobile.matches) return;
    f.classList.toggle("ouverte");
    majFiches();
  });
}
majFiches();
mobile.addEventListener("change", majFiches);

/* ------------------------------------------------------------------ état dans l'adresse : #<vue>?k=<repère>&c=<variante comparée> */
const sections = $$("#contenu > section.vue[data-vue]");
const onglets = $$("nav.vues a[data-vue]");
const vues = sections.map(s => s.dataset.vue);   // dans l'ordre des onglets : la première est la vue par défaut
const variantes = donnees("variantes", []);      // [[id, nom, adresse relative]]
const base = document.body.dataset.variante || "";
const figee = document.body.hasAttribute("data-figee");   // version figée (archive/) : jamais comparée
let courant = null;                              // l'état montré
const surMontrer = [];                           // fonctions (etat, section, k) appelées après chaque montrer()

/* Un état valide depuis le fragment : vue inconnue → la première ; c inconnu, égal à la base ou sur une version figée
   → pas de comparaison ; ancien c=1 → l'autre variante (la première qui n'est pas la base). k est gardé tel quel :
   montrer() le vérifie. */
function lireEtat(hash) {
  const [chemin, requete = ""] = String(hash || "").replace(/^#/, "").split("?");
  const q = new URLSearchParams(requete), ids = variantes.map(v => v[0]);
  let c = q.get("c");
  if (c === "1") c = ids.find(x => x !== base) || null;
  if (figee || !ids.includes(c) || c === base) c = null;
  return {vue: vues.includes(chemin) ? chemin : vues[0], k: q.get("k") || "", c};
}
function fragment(etat) {
  const q = new URLSearchParams();
  if (etat.k) q.set("k", etat.k);
  if (etat.c) q.set("c", etat.c);
  const s = q.toString();
  return "#" + etat.vue + (s ? "?" + s : "");
}
/* Écrit l'état dans l'adresse : nouvelle entrée d'historique quand la vue change (« précédent » revient à l'onglet
   d'avant), remplacement sinon. */
function ecrireEtat(etat, {remplace = courant !== null && etat.vue === courant.vue} = {}) {
  const h = fragment(etat);
  if (h === location.hash) return;
  history[remplace ? "replaceState" : "pushState"](null, "", h);
}

/* Montre la vue de l'état (html[data-vue], que site.css suit) et, dans sa section, l'élément k (le premier si k est
   inconnu) avec sa fiche et son segment ; marque l'onglet courant. Les onglets portent l'état (c) pour s'ouvrir tel
   quel dans un autre onglet. L'élément cloné d'une autre variante (.element.b, comparaison) n'en fait pas partie. */
function montrer(etat) {
  courant = etat;
  const section = sections.find(s => s.dataset.vue === etat.vue);
  racine.dataset.vue = etat.vue;
  for (const a of onglets) {
    if (a.dataset.vue === etat.vue) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
    a.setAttribute("href", fragment({vue: a.dataset.vue, k: "", c: etat.c}));
  }
  const elements = $$(".scene > .element[data-k]:not(.b)", section);
  // un élément grisé (bouton du segment désactivé) n'est jamais montré : k absent, inconnu ou grisé donne le premier actif
  const grises = $$(".segments button[data-k]:disabled", section).map(b => b.dataset.k);
  const actifs = elements.filter(x => !grises.includes(x.dataset.k));
  const k = actifs.some(x => x.dataset.k === etat.k) ? etat.k : (actifs[0] || elements[0] || {dataset: {k: ""}}).dataset.k;
  for (const x of elements) x.hidden = x.dataset.k !== k;
  let titre = null;
  for (const x of $$(".fiche-element[data-k]", section)) {
    x.hidden = x.dataset.k !== k;
    if (!x.hidden) titre = x.dataset.titre;
  }
  for (const b of $$(".segments button[data-k]", section)) b.setAttribute("aria-pressed", String(b.dataset.k === k));
  const nom = $(".fiche-nom", section);
  if (nom && titre !== null) nom.textContent = titre;
  for (const f of surMontrer) f(etat, section, k);
}
function aller(etat, options) {
  ecrireEtat(etat, options);
  montrer(etat);
}
/* Adresse changée hors du script (précédent, suivant, lien, saisie) : on montre l'état lu, et l'adresse est corrigée
   s'il était invalide. popstate et hashchange arrivent souvent ensemble : le second ne refait rien. */
function suivreAdresse() {
  const etat = lireEtat(location.hash);
  if (location.hash && fragment(etat) !== location.hash) ecrireEtat(etat, {remplace: true});
  if (courant && fragment(etat) === fragment(courant)) return;
  montrer(etat);
}

/* ------------------------------------------------------------------ scène : zoom, déplacement, pincement, mesure
   Un « élément » de la scène (div.element) contient soit des dessins (<svg> enfants directs, qui partagent la même
   viewBox quand on en superpose plusieurs), soit un rendu (figure.cadre). Le dessin zoome par sa viewBox, le rendu
   par un transform (échelle de 1 à 8). Les gestes sont écoutés sur l'élément ; les boutons de .outils, posés à côté,
   n'y arrivent pas. */
const SVG = "http://www.w3.org/2000/svg";
const noeud = (nom, attrs, parent) => {
  const n = document.createElementNS(SVG, nom);
  for (const [cle, v] of Object.entries(attrs)) n.setAttribute(cle, v);
  if (parent) parent.appendChild(n);
  return n;
};
const cm = d => d.toFixed(d < 100 ? 1 : 0).replace(".", ",");

/* Molette, glisser à un doigt ou à la souris, pincement à deux doigts, et clic (sans glisser) ;
   zoomer(f, x, y) : f < 1 rapproche, (x, y) en pixels de la page ; glisser(dx, dy) en pixels ; clic(e, cible). */
function brancherGestes(hote, {glisser, zoomer, clic}) {
  hote.addEventListener("wheel", e => { e.preventDefault(); zoomer(Math.exp(e.deltaY * 0.0016), e.clientX, e.clientY); }, {passive: false});
  const doigts = new Map();
  let geste = null;
  hote.addEventListener("pointerdown", e => {
    if (e.target.closest("button, input, .poignee, a")) return;
    hote.setPointerCapture(e.pointerId);
    doigts.set(e.pointerId, {x: e.clientX, y: e.clientY});
    if (doigts.size === 1) geste = {x: e.clientX, y: e.clientY, bouge: false, cible: e.target};
    else if (geste) geste.bouge = true;
  });
  hote.addEventListener("pointermove", e => {
    const d = doigts.get(e.pointerId);
    if (!d) return;
    if (doigts.size === 1) {
      if (Math.hypot(e.clientX - geste.x, e.clientY - geste.y) > 6) geste.bouge = true;
      if (geste.bouge) glisser(e.clientX - d.x, e.clientY - d.y);
    } else if (doigts.size === 2) {
      const [p, q] = [...doigts.values()], avant = Math.hypot(p.x - q.x, p.y - q.y);
      d.x = e.clientX; d.y = e.clientY;
      const [p2, q2] = [...doigts.values()], apres = Math.hypot(p2.x - q2.x, p2.y - q2.y);
      if (apres > 0) zoomer(avant / apres, (p2.x + q2.x) / 2, (p2.y + q2.y) / 2);
    }
    d.x = e.clientX; d.y = e.clientY;
  });
  const fin = e => {
    if (!doigts.delete(e.pointerId)) return;
    if (doigts.size === 0 && geste && !geste.bouge && e.type === "pointerup" && clic) clic(e, geste.cible);
    if (doigts.size === 0) geste = null;
  };
  hote.addEventListener("pointerup", fin);
  hote.addEventListener("pointercancel", fin);
}

/* Dessin SVG dans `element` : zoom par la viewBox (de 1/14 à 1,25 de la largeur d'origine, marges comprises),
   déplacement, mesure de deux points. opt.mesure(distance | null) est appelé à chaque mesure, null quand elle s'efface ;
   opt.touche(cible) à chaque clic sans glisser hors mesure. Renvoie {zoomer(f, x, y), recadrer(), mesurer(on), lier(hote)} :
   lier(hote) donne la même viewBox aux SVG d'un autre élément (la variante comparée) et y écoute les mêmes gestes,
   jusqu'à ce qu'il quitte la page. */
function dessin(element, opt = {}) {
  let jumeau = null;
  const svgs = () => [element, jumeau].filter(e => e && e.isConnected).flatMap(e => $$(":scope > svg", e)), premier = svgs()[0];
  const b = premier.viewBox.baseVal, v0 = {x: b.x - b.width * 0.03, y: b.y - b.height * 0.13, w: b.width * 1.06, h: b.height * 1.22};
  let v = {...v0}, mesure = false, pm = [];
  const trace = noeud("g", {class: "trace-mesure"}, premier);
  const pose = () => svgs().forEach(s => s.setAttribute("viewBox", `${v.x} ${v.y} ${v.w} ${v.h}`));
  const versPlan = (cx, cy) => new DOMPoint(cx, cy).matrixTransform(premier.getScreenCTM().inverse());
  function tracer() {                          // cote mesurée, à taille d'écran constante
    trace.replaceChildren();
    if (pm.length < 2 && opt.mesure) opt.mesure(null);
    if (!pm.length) return;
    const u = 1 / premier.getScreenCTM().a;     // unités du plan par pixel
    for (const p of pm) noeud("circle", {class: "pt-mesure", cx: p.x, cy: p.y, r: 4 * u}, trace);
    if (pm.length === 2) {
      const [p, q] = pm, d = Math.hypot(q.x - p.x, q.y - p.y);
      noeud("line", {class: "trait-mesure", x1: p.x, y1: p.y, x2: q.x, y2: q.y}, trace);
      const t = noeud("text", {class: "txt-mesure", x: (p.x + q.x) / 2, y: (p.y + q.y) / 2 - 8 * u, "text-anchor": "middle", "font-size": 14 * u}, trace);
      t.textContent = cm(d) + " cm";
      if (opt.mesure) opt.mesure(d);
    }
  }
  function zoomer(f, cx, cy) {
    const r = element.getBoundingClientRect(), p = versPlan(cx === undefined ? r.left + r.width / 2 : cx, cy === undefined ? r.top + r.height / 2 : cy);
    const w = Math.min(v0.w * 1.25, Math.max(v0.w / 14, v.w * f));
    f = w / v.w;
    v = {x: p.x - (p.x - v.x) * f, y: p.y - (p.y - v.y) * f, w, h: v.h * f};
    pose(); tracer();
  }
  pose();
  const gestes = {
    zoomer,
    glisser(dx, dy) { const m = premier.getScreenCTM(); v.x -= dx / m.a; v.y -= dy / m.d; pose(); },
    clic(e, cible) {
      if (mesure) { const p = versPlan(e.clientX, e.clientY); pm = pm.length === 2 ? [p] : [...pm, p]; tracer(); }
      else if (opt.touche) opt.touche(cible);
    },
  };
  brancherGestes(element, gestes);
  return {zoomer, recadrer() { v = {...v0}; pose(); tracer(); },
          mesurer(on) { mesure = on; if (!on) { pm = []; tracer(); } },
          lier(hote) { jumeau = hote; brancherGestes(hote, gestes); pose(); }};
}

/* Rendu dans `element` (son figure.cadre) : déplacement et zoom par transform, échelle de 1 à 8 ;
   apres() est appelé après chaque changement. lier(hote) applique la même transformation au cadre d'un autre élément
   (la variante comparée) et y écoute les mêmes gestes. */
function vueImage(element, apres) {
  const cadre = $(":scope > .cadre", element);
  let k = 1, tx = 0, ty = 0, jumeau = null;
  const pose = () => {
    const t = `translate(${tx}px,${ty}px) scale(${k})`, autre = jumeau && jumeau.isConnected && $(":scope > .cadre", jumeau);
    cadre.style.transform = t;
    if (autre) autre.style.transform = t;
    if (apres) apres();
  };
  function zoomer(f, cx, cy) {
    const r = element.getBoundingClientRect(), px = (cx ?? r.left + r.width / 2) - r.left, py = (cy ?? r.top + r.height / 2) - r.top;
    const k2 = Math.min(8, Math.max(1, k / f)), g = k2 / k, ox = cadre.offsetLeft, oy = cadre.offsetTop;
    tx = px - ox - g * (px - ox - tx); ty = py - oy - g * (py - oy - ty); k = k2;
    if (k === 1) tx = ty = 0;
    pose();
  }
  const gestes = {zoomer, glisser(dx, dy) { tx += dx; ty += dy; pose(); }};
  brancherGestes(element, gestes);
  return {zoomer, recadrer() { k = 1; tx = ty = 0; pose(); },
          lier(hote) { jumeau = hote; brancherGestes(hote, gestes); pose(); }};
}

/* Le contrôleur d'un élément de scène, créé à son premier affichage (getScreenCTM demande qu'il soit visible). */
const controleurs = new WeakMap();
function controleur(element) {
  if (controleurs.has(element)) return controleurs.get(element);
  const section = element.closest("section.vue"), scene = element.closest(".scene");
  let c = null;
  if ($(":scope > svg", element)) {
    scene.classList.add("dessin");
    c = dessin(element, {
      mesure(d) {
        const m = $(".bandeau .mes", section);
        if (!m) return;
        m.hidden = d === null;
        if (d !== null) m.textContent = "Mesuré : " + cm(d) + " cm";
      },
      touche(cible) { toucherMeuble(section, cible); },
    });
  } else if ($(":scope > .cadre", element)) {
    scene.classList.add("image");
    c = vueImage(element);
  }
  if (c && c.mesurer) c.mesurer($(".b-mesure", section)?.getAttribute("aria-pressed") === "true");
  controleurs.set(element, c);
  return c;
}
const elementActif = section => $(".scene > .element:not([hidden]):not(.b)", section);

/* Zones de meuble du plan : rect.zone[data-meuble=n] et son <template data-meuble=n data-titre> dans la fiche.
   L'état est dans l'adresse (#plan?k=n) : toucher une zone change l'adresse, montrer() fait le reste. */
const meubleDefaut = new WeakMap();   // section -> contenu d'origine de .fiche-meuble
function toucherMeuble(section, cible) {
  if (!$("rect.zone[data-meuble]", section) || courant.vue !== section.dataset.vue) return;
  const z = cible.closest && cible.closest("rect.zone[data-meuble]");
  const k = z ? z.dataset.meuble : "";
  if (k !== courant.k) aller({...courant, k});
}
function montrerMeuble(section, n) {
  const zones = $$("rect.zone[data-meuble]", section), corps = $(".fiche-meuble", section);
  if (!zones.length || !corps) return;
  if (!meubleDefaut.has(section)) meubleDefaut.set(section, corps.innerHTML);
  const zone = zones.find(z => z.dataset.meuble === n);
  const modele = zone && $$("template[data-meuble]", section).find(t => t.dataset.meuble === n);
  for (const z of zones) z.classList.toggle("ici", z === zone);
  const fiche = $(".fiche", section), nom = $(".fiche-nom", section);
  if (!modele) {
    corps.innerHTML = meubleDefaut.get(section);
    const neutre = $(".fiche-element[data-k='']", section);
    if (nom && neutre && neutre.dataset.titre) nom.textContent = neutre.dataset.titre;
    return;
  }
  corps.replaceChildren(modele.content.cloneNode(true));
  const fermer = document.createElement("button");
  fermer.type = "button"; fermer.className = "btn"; fermer.textContent = "Fermer";
  fermer.addEventListener("click", () => {
    fiche.classList.remove("ouverte"); majFiches();
    aller({...courant, k: ""});
  });
  let actions = $(".actions", corps);
  if (!actions) { actions = document.createElement("div"); actions.className = "actions"; corps.appendChild(actions); }
  actions.appendChild(fermer);
  if (nom) nom.textContent = modele.dataset.titre;
  fiche.classList.add("ouverte"); majFiches();
  fiche.scrollTop = 0;
}

/* Calques du plan : boutons à bascule (aria-pressed), classe sans-<id> sur la section, choix mémorisé sous « calques »
   (la liste des calques masqués ; ceux des autres documents sont conservés). */
function brancherCalques(section) {
  const boutons = $$(".calques button[data-calque]", section);
  if (!boutons.length) return;
  const memorises = memo.lit("calques", []), masques = Array.isArray(memorises) ? memorises : [];
  const poser = (b, actif) => {
    b.setAttribute("aria-pressed", String(actif));
    section.classList.toggle("sans-" + b.dataset.calque, !actif);
  };
  for (const b of boutons) {
    poser(b, !masques.includes(b.dataset.calque));
    b.addEventListener("click", () => {
      poser(b, b.getAttribute("aria-pressed") !== "true");
      const ids = boutons.map(x => x.dataset.calque), ailleurs = memo.lit("calques", []).filter(x => !ids.includes(x));
      memo.pose("calques", [...ailleurs, ...boutons.filter(x => x.getAttribute("aria-pressed") === "false").map(x => x.dataset.calque)]);
    });
  }
}

function brancherScenes() {
  for (const section of sections) {
    const scene = $(".scene", section);
    if (!scene) continue;
    for (const b of $$(".outils [data-z]", section)) b.addEventListener("click", () => {
      const el = elementActif(section), c = el && controleur(el);
      if (!c) return;
      if (+b.dataset.z) c.zoomer(+b.dataset.z); else c.recadrer();
    });
    const bm = $(".b-mesure", section);
    if (bm) bm.addEventListener("click", () => {
      const on = bm.getAttribute("aria-pressed") !== "true";
      bm.setAttribute("aria-pressed", String(on));
      scene.classList.toggle("mesure", on);
      for (const el of $$(".scene > .element", section)) { const c = controleurs.get(el); if (c && c.mesurer) c.mesurer(on); }
      if (!on) { const m = $(".bandeau .mes", section); if (m) m.hidden = true; }
    });
    scene.addEventListener("keydown", e => {
      if ((e.key === "Enter" || e.key === " ") && e.target.matches && e.target.matches("rect.zone[data-meuble]")) {
        e.preventDefault();
        toucherMeuble(section, e.target);
      }
    });
    brancherCalques(section);
  }
  surMontrer.push((etat, section, k) => {
    const el = elementActif(section);
    if (el) controleur(el);
    montrerMeuble(section, etat.k);
    // « Position » : le trait de la coupe ou le point de vue de l'élément affiché (même data-k) passe au premier plan
    for (const x of $$(".mini [data-k]", section)) x.classList.toggle("ici", x.dataset.k === k);
  });
}

/* ------------------------------------------------------------------ comparaison de deux variantes
   #<vue>?c=<variante> : la page de la variante comparée est chargée (fetch), et son élément de même vue et de même
   repère est cloné dans la scène, après celui de la base, avec la classe b. La poignée règle le rideau : --pos sur la
   scène, et site.css découpe chacun des deux éléments à cette position. Les éléments couvrent toute la scène et ne
   sont jamais zoomés eux-mêmes (seuls leurs SVG ou leur cadre le sont) : la coupure reste sous la poignée à tout zoom,
   sans le calage de la maquette. Le contrôleur de la base pilote aussi le clone (lier) : zoom, déplacement et mesure
   valent pour les deux. Bandeau : la base à gauche, la variante comparée à droite. Une version figée n'est jamais
   comparée. */
const COMPARABLES = ["plan", "coupes", "iso", "camera", "plans"];   // vues où deux variantes se superposent
const nomVariante = id => (variantes.find(v => v[0] === id) || [id, id])[1];

const pages = new Map();   // id de variante -> Promise<Document>
function chargerVariante(id) {
  if (!pages.has(id)) {
    const v = variantes.find(x => x[0] === id);
    const p = (v ? fetch(v[2]) : Promise.reject(new Error("variante inconnue : " + id)))
      .then(r => { if (!r.ok) throw new Error(`${v[2]} : ${r.status}`); return r.text(); })
      .then(html => new DOMParser().parseFromString(html, "text/html"));
    pages.set(id, p);
    p.catch(() => { if (pages.get(id) === p) pages.delete(id); });   // un échec (réseau, 404, file://) se retente
  }
  return pages.get(id);
}

/* Rideau : la poignée se glisse (souris, doigt) ou se règle aux flèches du clavier, de 4 points, entre 4 et 96 %.
   La position reste sur la scène quand la comparaison change de repère ou de variante. */
const POIGNEE = '<div class="poignee" role="slider" tabindex="0" aria-label="Rideau de comparaison" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50"></div>';
function rideau(scene, poignee) {
  const actuelle = () => parseFloat(scene.style.getPropertyValue("--pos")) || 50;
  const poser = t => {
    t = Math.max(4, Math.min(96, t));
    scene.style.setProperty("--pos", t + "%");
    poignee.setAttribute("aria-valuenow", Math.round(t));
  };
  poignee.addEventListener("pointerdown", e => { poignee.setPointerCapture(e.pointerId); e.preventDefault(); });
  poignee.addEventListener("pointermove", e => {
    if (!poignee.hasPointerCapture(e.pointerId)) return;
    const r = scene.getBoundingClientRect();
    poser((e.clientX - r.left) / r.width * 100);
  });
  poignee.addEventListener("keydown", e => {
    if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
    e.preventDefault();
    poser(actuelle() + (e.key === "ArrowLeft" ? -4 : 4));
  });
  poser(actuelle());
}
const etiquette = (texte, manque) => {
  const s = document.createElement("span");
  s.className = manque ? "etiq-var manque" : "etiq-var";
  s.textContent = texte;
  return s;
};

let comparaison = null, tour = 0;   // la comparaison posée ou en chargement ; tour écarte un chargement dépassé
function retirerComparaison() {
  if (!comparaison) return;
  for (const n of comparaison.poses) n.remove();
  comparaison.scene.classList.remove("compare");
  comparaison = null;
}
async function comparer(etat) {
  const section = sections.find(s => s.dataset.vue === etat.vue), scene = section && $(".scene", section);
  const el = scene && elementActif(section);
  const voulue = Boolean(!figee && etat.c && COMPARABLES.includes(etat.vue) && el);
  if (voulue && comparaison && comparaison.el === el && comparaison.c === etat.c) return;   // déjà posée ou en chargement
  retirerComparaison();
  const jeton = ++tour;
  if (!voulue) return;
  const c = etat.c, poses = [];
  comparaison = {scene, el, c, poses};
  let page = null;
  try { page = await chargerVariante(c); } catch (e) { /* étiquette « comparaison indisponible » */ }
  if (jeton !== tour) return;
  const k = el.dataset.k, autre = page && $$("section.vue", page).find(s => s.dataset.vue === etat.vue);
  const original = autre && $$(".scene > .element[data-k]", autre).find(x => x.dataset.k === k);
  const grise = autre && $$(".segments button[data-k]:disabled", autre).some(b => b.dataset.k === k);
  let droite;
  if (!page) droite = etiquette(nomVariante(c) + " : comparaison indisponible", true);
  else if (!original || grise) droite = etiquette(nomVariante(c) + " : pas d'équivalent", true);
  else {
    const clone = document.importNode(original, true), modele = document.createElement("template");
    modele.innerHTML = POIGNEE;
    const poignee = modele.content.firstElementChild, outils = $(":scope > .outils", scene);
    clone.classList.add("b");
    clone.hidden = false;
    for (const z of $$(".zone", clone)) z.remove();   // les meubles se touchent sur la base seule
    scene.insertBefore(clone, outils);
    scene.insertBefore(poignee, outils);
    scene.classList.add("compare");
    poses.push(clone, poignee);
    const ctl = controleur(el);
    if (ctl && ctl.lier) ctl.lier(clone);
    rideau(scene, poignee);
    droite = etiquette(nomVariante(c));
  }
  const gauche = etiquette(nomVariante(base)), bandeau = $(":scope > .bandeau", scene);
  poses.push(gauche, droite);
  if (bandeau) { bandeau.prepend(gauche); bandeau.append(droite); }
}

/* Barre : « Comparer » pose c (la première autre variante) ou le retire, « avec » change c ; tous deux sont cachés
   hors de COMPARABLES. Le choix de variante charge l'autre page en gardant l'état, et échange c et la base si c devient
   la base. En comparaison, aucun meuble n'est choisi sur le plan (maquette) : k ne reste que s'il désigne un élément
   de la vue (coupe, caméra). */
const bComp = $("#c-comp"), choixAutre = $("#c-autre"), avec = choixAutre && choixAutre.closest("label");
const choixVariante = $("#c-variante"), cases = $(".b-cases");
function majBarre(etat) {
  const comparable = !figee && COMPARABLES.includes(etat.vue);
  if (bComp) { bComp.hidden = !comparable; bComp.setAttribute("aria-pressed", String(!!etat.c)); }
  if (avec) { avec.hidden = !(comparable && etat.c); if (etat.c) choixAutre.value = etat.c; }
  if (cases) cases.classList.toggle("deux-choix", Boolean(avec && !avec.hidden));
}
function repereEnComparaison(etat) {
  const section = sections.find(s => s.dataset.vue === etat.vue);
  return section && $$(".scene > .element[data-k]:not(.b)", section).some(x => x.dataset.k === etat.k) ? etat.k : "";
}
function brancherComparaison() {
  if (bComp) bComp.addEventListener("click", () => {
    const autre = (variantes.find(v => v[0] !== base) || [null])[0];
    aller({...courant, k: repereEnComparaison(courant), c: courant.c ? null : autre});
  });
  if (choixAutre) choixAutre.addEventListener("change", () => aller({...courant, k: repereEnComparaison(courant), c: choixAutre.value}));
  if (choixVariante) {
    choixVariante.addEventListener("change", () => {
      const v = variantes.find(x => x[0] === choixVariante.value);
      if (!v || v[0] === base) return;
      location.assign(v[2] + fragment({...courant, c: courant.c === v[0] ? base : courant.c}));
    });
    addEventListener("pageshow", () => { choixVariante.value = base; });   // retour arrière : la variante de la page
  }
  surMontrer.push(etat => { majBarre(etat); comparer(etat); });
}

/* ------------------------------------------------------------------ options du document (« Personnaliser »)
   #options liste les Option du document (nom, surfaces, type, valeurs, css, filtre, ref). Le choix de chacune est
   mémorisé sous « <pièce>/<document>:<id> », donc partagé entre les variantes ; il est aussi gardé dans `choix`, pour
   que la page le suive sans stockage. appliquer() pose la variable CSS sur <html> (les dessins la suivent) et, pour
   une option à filtre, règle les pentes de #filtre-<id> : les rendus recolorés (img.calque, sous masque, portant
   filter:url(#filtre-<id>)) suivent, clone de la comparaison compris, puisque le filtre est global à la page. */
const options = donnees("options", []);
const echapper = t => String(t).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const cleOption = o => `${document.body.dataset.piece}/${document.body.dataset.document}:${o.id}`;
const valeurDe = (o, code) => o.valeurs.find(v => v.code === code);
const choix = {};   // option.id -> code choisi
for (const o of options) { const m = memo.lit(cleOption(o), o.defaut); choix[o.id] = valeurDe(o, m) ? m : o.defaut; }

/* Applique la valeur `code` de l'option : variable CSS, filtre, puis mémoire (sauf `memoriser` faux, au chargement). */
function appliquer(option, code, memoriser = true) {
  const v = valeurDe(option, code) || valeurDe(option, option.defaut);
  if (!v) return;
  choix[option.id] = v.code;
  if (option.css) racine.style.setProperty(option.css, v.couleur);
  if (option.filtre) {
    ["R", "G", "B"].forEach((c, i) => {
      const f = $(`#filtre-${option.id} feFunc${c}`);
      if (f) f.setAttribute("slope", (parseInt(v.couleur.substr(1 + 2 * i, 2), 16) / 255 / option.ref).toFixed(4));
    });
  }
  if (memoriser) memo.pose(cleOption(option), v.code);
}
const nbChangees = () => options.filter(o => choix[o.id] !== o.defaut).length;

function blocOption(o) {
  const bouton = v => `<button type="button" data-v="${echapper(v.code)}" style="--c:${echapper(v.couleur)}" aria-pressed="false">` +
    (o.type === "nuancier" ? "<i></i>" : `<i style="background:${echapper(v.couleur)}"></i>`) + `${echapper(v.nom)}</button>`;
  const grille = o.type === "nuancier" ? "nuances" : "choix-opt";
  const commande = [...new Set(o.valeurs.map(v => v.groupe))].map(g => (g ? `<h4>${echapper(g)}</h4>` : "") +
    `<div class="${grille}">${o.valeurs.filter(v => v.groupe === g).map(bouton).join("")}</div>`).join("");
  return `<section data-o="${echapper(o.id)}"><h3>${echapper(o.nom)}` +
    (o.surfaces.length ? ` <span>(${echapper(o.surfaces.join(", "))})</span>` : "") + `</h3>${commande}<p class="info"></p>` +
    (o.portee ? `<p class="remarque">${echapper(o.portee)}</p>` : "") + "</section>";
}
function brancherOptions() {
  const panneau = $("#panneau-options"), voile = $("#voile-options"), ouvreur = $("#c-options");
  if (!options.length || !panneau || !voile) return;
  panneau.innerHTML = '<div class="tete-feuille"><h2>Personnaliser</h2><button type="button" class="fermer" aria-label="Fermer">' +
    '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>' + options.map(blocOption).join("") +
    '<p class="actions"><button type="button" class="btn" id="b-origine">Valeurs d\'origine</button></p>';
  const afficher = () => {
    for (const o of options) {
      const v = valeurDe(o, choix[o.id]), bloc = $(`section[data-o="${o.id}"]`, panneau);
      for (const b of $$("[data-v]", bloc)) b.setAttribute("aria-pressed", String(b.dataset.v === v.code));
      $(".info", bloc).innerHTML = `<b>${echapper(v.nom)}</b> <span class="num">${echapper(v.couleur)}</span>` +
        (v.note ? `, ${echapper(v.note)}` : "") +
        (v.lien ? ` <a href="${echapper(v.lien)}" target="_blank" rel="noopener">Voir la fiche</a>` : "");
    }
    const n = nbChangees(), pastille = $("#n-options");
    $("#b-origine", panneau).disabled = n === 0;
    if (pastille) {
      pastille.hidden = n === 0;
      pastille.textContent = n;
      pastille.setAttribute("aria-label", `${n} option${n > 1 ? "s" : ""} modifiée${n > 1 ? "s" : ""}`);
    }
  };
  for (const b of $$("[data-v]", panneau)) b.addEventListener("click", () => {
    appliquer(options.find(o => o.id === b.closest("section").dataset.o), b.dataset.v);
    afficher();
  });
  $("#b-origine", panneau).addEventListener("click", () => {
    for (const o of options) appliquer(o, o.defaut);
    afficher();
  });
  const montrerPanneau = ouvert => {
    panneau.hidden = voile.hidden = !ouvert;
    if (ouvreur) ouvreur.setAttribute("aria-expanded", String(ouvert));
    if (ouvert) $(".fermer", panneau).focus();
    else if (ouvreur && panneau.contains(document.activeElement)) ouvreur.focus();
  };
  if (ouvreur) { ouvreur.setAttribute("aria-haspopup", "dialog"); ouvreur.addEventListener("click", () => montrerPanneau(panneau.hidden)); }
  $(".fermer", panneau).addEventListener("click", () => montrerPanneau(false));
  voile.addEventListener("click", () => montrerPanneau(false));
  document.addEventListener("keydown", e => { if (e.key === "Escape" && !panneau.hidden) montrerPanneau(false); });
  for (const o of options) appliquer(o, choix[o.id], false);
  afficher();
}
brancherOptions();

if (sections.length) {
  brancherScenes();
  brancherComparaison();
  for (const a of onglets) a.addEventListener("click", e => {
    if (a.getAttribute("aria-disabled") === "true") { e.preventDefault(); return; }   // vue sans contenu
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;     // autre onglet du navigateur
    e.preventDefault();
    aller({vue: a.dataset.vue, k: "", c: courant.c});
  });
  for (const b of $$(".segments button[data-k]")) b.addEventListener("click", () => {
    aller({...courant, vue: b.closest("section.vue").dataset.vue, k: b.dataset.k});
  });
  addEventListener("popstate", suivreAdresse);
  addEventListener("hashchange", suivreAdresse);
  suivreAdresse();
}
})();
