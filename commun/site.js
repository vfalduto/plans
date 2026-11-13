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
let courant = null;                              // l'état montré
const surMontrer = [];                           // fonctions (etat, section, k) appelées après chaque montrer()

/* Un état valide depuis le fragment : vue inconnue → la première ; c inconnu ou égal à la base → pas de comparaison ;
   ancien c=1 → l'autre variante (la première qui n'est pas la base). k est gardé tel quel : montrer() le vérifie. */
function lireEtat(hash) {
  const [chemin, requete = ""] = String(hash || "").replace(/^#/, "").split("?");
  const q = new URLSearchParams(requete), ids = variantes.map(v => v[0]);
  let c = q.get("c");
  if (c === "1") c = ids.find(x => x !== base) || null;
  if (!ids.includes(c) || c === base) c = null;
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
   quel dans un autre onglet. */
function montrer(etat) {
  courant = etat;
  const section = sections.find(s => s.dataset.vue === etat.vue);
  racine.dataset.vue = etat.vue;
  for (const a of onglets) {
    if (a.dataset.vue === etat.vue) a.setAttribute("aria-current", "page");
    else a.removeAttribute("aria-current");
    a.setAttribute("href", fragment({vue: a.dataset.vue, k: "", c: etat.c}));
  }
  const elements = $$(".scene > .element[data-k]", section);
  const k = elements.some(x => x.dataset.k === etat.k) ? etat.k : elements.length ? elements[0].dataset.k : "";
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

if (sections.length) {
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
