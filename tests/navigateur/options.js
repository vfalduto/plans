/* Personnaliser : choix d'une teinte (variable CSS, pentes du filtre, pastille), mémorisation partagée entre les
   variantes, rendus recolorés (y compris le clone de la comparaison), « Valeurs d'origine », sans localStorage.
   Lancé par tests/navigateur/lancer.sh, qui ouvre la racine du site d'essai avant d'appeler ce script. */
async page => {
  const BASE = new URL(page.url()).origin;
  const DOC = `${BASE}/essai/amenagement/`;
  const echecs = [], erreurs = [];
  const verifier = (vrai, message) => { if (!vrai) echecs.push(message); };

  const preparer = async p => {
    p.on("console", m => { if (m.type() === "error") erreurs.push(`console : ${m.text()}`); });
    p.on("pageerror", e => erreurs.push(`page : ${e.message}`));
    p.setDefaultTimeout(3000);
    await p.emulateMedia({reducedMotion: "reduce"});
  };
  const ouvrir = async (p, adresse) => { await p.goto("about:blank"); await p.goto(adresse); };
  const attendre = async (p, condition, message) => {
    try { await p.waitForFunction(condition, null, {timeout: 2000}); } catch (e) { echecs.push(message); }
  };

  // ce que montre la page : variable CSS, pentes du filtre, pastille, bouton choisi, panneau
  const lire = p => p.evaluate(() => {
    const pastille = document.querySelector("#n-options"), panneau = document.querySelector("#panneau-options");
    const pente = c => +document.querySelector(`#filtre-teinte feFunc${c}`).getAttribute("slope");
    return {
      css: getComputedStyle(document.documentElement).getPropertyValue("--teinte").trim().toLowerCase(),
      pentes: ["R", "G", "B"].map(pente),
      pastille: pastille.hidden ? "" : pastille.textContent,
      etiquette: pastille.getAttribute("aria-label"),
      choisi: [...document.querySelectorAll("#panneau-options [data-v][aria-pressed='true']")].map(b => b.dataset.v),
      ouvert: panneau.checkVisibility(),
      info: (panneau.querySelector(".info") || {}).textContent || "",
      stocke: localStorage.getItem("plans:essai/amenagement:teinte"),
    };
  });
  const pentes = hex => [1, 3, 5].map(i => parseInt(hex.substr(i, 2), 16) / 255 / 0.8);
  const proches = (a, b) => a.length === b.length && a.every((x, i) => Math.abs(x - b[i]) < 0.001);
  const calque = (p, selecteur) => p.evaluate(s => {
    const i = document.querySelector(s);
    if (!i) return null;
    const c = getComputedStyle(i);
    return {filtre: c.filter, masque: c.maskImage || c.webkitMaskImage};
  }, selecteur);
  const ouvrirPanneau = async p => { await p.click("#c-options"); await attendre(p, () => document.querySelector("#panneau-options").checkVisibility(), "le panneau ne s'ouvre pas"); };

  await page.context().route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//,
                             r => r.fulfill({status: 200, contentType: "text/css", body: ""}));
  await preparer(page);

  try {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#camera");
    await page.evaluate(() => localStorage.clear());
    await ouvrir(page, DOC + "#camera");

    // Valeur d'origine : v1, pas de pastille, panneau fermé
    let l = await lire(page);
    verifier(l.css === "#eeebe3" && proches(l.pentes, pentes("#EEEBE3")) && l.pastille === "" && !l.ouvert,
             `origine : ${JSON.stringify(l)}`);

    // Le panneau : groupes, boutons, sans case à cocher, « Valeurs d'origine »
    await ouvrirPanneau(page);
    const p = await page.evaluate(() => {
      const f = document.querySelector("#panneau-options");
      return {titre: f.querySelector("h2").textContent, groupes: [...f.querySelectorAll("h4")].map(x => x.textContent),
              valeurs: [...f.querySelectorAll("[data-v]")].map(b => b.dataset.v), cases: f.querySelectorAll("input").length,
              origine: [...f.querySelectorAll("button")].some(b => b.textContent.trim() === "Valeurs d'origine"),
              dialogue: f.getAttribute("role"), focus: document.activeElement.className};
    });
    verifier(p.titre === "Personnaliser" && JSON.stringify(p.groupes) === JSON.stringify(["Clairs", "Verts", "Ocres"]) &&
             JSON.stringify(p.valeurs) === JSON.stringify(["v1", "v2", "v3"]) && p.cases === 0 && p.origine && p.dialogue === "dialog",
             `panneau : ${JSON.stringify(p)}`);
    verifier(/fermer/.test(p.focus), `panneau : le focus n'entre pas dans le panneau (${p.focus})`);

    // Choisir v2 : variable, pentes, pastille, info, mémoire
    await page.click('#panneau-options [data-v="v2"]');
    l = await lire(page);
    verifier(l.css === "#a9b8a0", `v2 : --teinte = ${l.css}`);
    verifier(proches(l.pentes, pentes("#A9B8A0")), `v2 : pentes ${l.pentes}, attendu ${pentes("#A9B8A0")}`);
    verifier(l.pastille === "1" && /1 option/.test(l.etiquette || ""), `v2 : pastille « ${l.pastille} », étiquette « ${l.etiquette} »`);
    verifier(JSON.stringify(l.choisi) === '["v2"]' && l.info.includes("Sauge") && l.info.includes("peinture seulement"),
             `v2 : choisi ${l.choisi}, info « ${l.info} »`);
    verifier(l.stocke === JSON.stringify("v2"), `v2 : mémoire ${l.stocke}`);

    // Rendu recoloré : le calque porte le filtre et le masque
    let c = await calque(page, 'section[data-vue="camera"] .element:not(.b) img.calque');
    verifier(c && c.filtre.includes("filtre-teinte") && c.masque.includes("svg+xml"), `calque : ${JSON.stringify(c)}`);

    // Échap ferme le panneau et rend le focus à « Personnaliser »
    await page.keyboard.press("Escape");
    verifier(!(await lire(page)).ouvert, "Échap ne ferme pas le panneau");
    verifier(await page.evaluate(() => document.activeElement.id) === "c-options", "le focus ne revient pas sur #c-options");
    await ouvrirPanneau(page);
    await page.mouse.click(20, 500);   // hors du panneau : le voile
    verifier(!(await lire(page)).ouvert, "le voile ne ferme pas le panneau");

    // Partagé entre les variantes, après rechargement
    await ouvrir(page, DOC + "b.html#camera");
    l = await lire(page);
    verifier(l.css === "#a9b8a0" && l.pastille === "1" && proches(l.pentes, pentes("#A9B8A0")), `variante B : ${JSON.stringify(l)}`);
    await ouvrirPanneau(page);
    verifier(JSON.stringify((await lire(page)).choisi) === '["v2"]', "variante B : v2 n'est pas coché dans le panneau");
    await page.keyboard.press("Escape");

    // Comparaison : le clone de l'autre variante est recoloré aussi
    await ouvrir(page, DOC + "#camera?c=b");
    await attendre(page, () => document.querySelector('section[data-vue="camera"] .element.b img.calque'), "comparaison : pas de clone");
    c = await calque(page, 'section[data-vue="camera"] .element.b img.calque');
    verifier(c && c.filtre.includes("filtre-teinte") && c.masque.includes("svg+xml"), `clone : ${JSON.stringify(c)}`);
    const dans = await page.evaluate(() => {
      const i = document.querySelector('section[data-vue="camera"] .element.b img.calque');
      return i.checkVisibility() && i.getBoundingClientRect().width > 10;
    });
    verifier(dans, "clone : le calque n'est pas visible");

    // Valeurs d'origine
    await ouvrirPanneau(page);
    await page.click("#panneau-options >> text=Valeurs d'origine");
    l = await lire(page);
    verifier(l.css === "#eeebe3" && proches(l.pentes, pentes("#EEEBE3")) && l.pastille === "" &&
             JSON.stringify(l.choisi) === '["v1"]', `origine rendue : ${JSON.stringify(l)}`);
    await ouvrir(page, DOC + "b.html#camera");
    l = await lire(page);
    verifier(l.css === "#eeebe3" && l.pastille === "", `origine après rechargement : ${JSON.stringify(l)}`);

    // Une valeur mémorisée inconnue donne la valeur d'origine
    await page.evaluate(() => localStorage.setItem("plans:essai/amenagement:teinte", JSON.stringify("zzz")));
    await ouvrir(page, DOC + "#camera");
    l = await lire(page);
    verifier(l.css === "#eeebe3" && l.pastille === "", `valeur inconnue : ${JSON.stringify(l)}`);
    await page.evaluate(() => localStorage.clear());

    // Sans localStorage : la valeur d'origine s'affiche, le choix tient le temps de la page, sans erreur
    const privee = await page.context().newPage();
    await preparer(privee);
    await privee.addInitScript(() => {
      const refus = () => { throw new DOMException("stockage refusé", "SecurityError"); };
      Storage.prototype.getItem = refus;
      Storage.prototype.setItem = refus;
    });
    await privee.setViewportSize({width: 1440, height: 900});
    await privee.goto(DOC + "#camera");
    const lirePrivee = () => privee.evaluate(() => ({
      css: getComputedStyle(document.documentElement).getPropertyValue("--teinte").trim().toLowerCase(),
      pastille: document.querySelector("#n-options").hidden ? "" : document.querySelector("#n-options").textContent}));
    let q = await lirePrivee();
    verifier(q.css === "#eeebe3" && q.pastille === "", `sans localStorage : ${JSON.stringify(q)}`);
    await privee.click("#c-options");
    await privee.click('#panneau-options [data-v="v3"]');
    q = await lirePrivee();
    verifier(q.css === "#b5735a" && q.pastille === "1", `sans localStorage, après choix : ${JSON.stringify(q)}`);
    await privee.close();

    // Mobile : feuille basse, pas de défilement horizontal
    await page.setViewportSize({width: 390, height: 844});
    await ouvrir(page, DOC + "#camera");
    await ouvrirPanneau(page);
    const m = await page.evaluate(() => {
      const r = document.querySelector("#panneau-options").getBoundingClientRect();
      return {bas: r.bottom, gauche: r.left, droite: r.right, h: innerHeight, l: innerWidth, defil: document.documentElement.scrollWidth};
    });
    verifier(Math.abs(m.bas - m.h) <= 1 && m.gauche >= 0 && m.droite <= m.l && m.defil <= m.l, `mobile : ${JSON.stringify(m)}`);
  } catch (e) {
    echecs.push(`exception : ${e.message.split("\n")[0]}`);
  }

  return {ok: echecs.length === 0 && erreurs.length === 0, echecs, erreurs};
}
