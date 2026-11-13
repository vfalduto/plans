/* Navigation : onglets, état dans l'adresse, menu de gauche, fiche ; à 1440 × 900 puis 390 × 844.
   Lancé par tests/navigateur/lancer.sh, qui ouvre la racine du site d'essai avant d'appeler ce script. */
async page => {
  const BASE = new URL(page.url()).origin;
  const DOC = `${BASE}/essai/amenagement/`;
  const echecs = [], erreurs = [];
  const verifier = (vrai, message) => { if (!vrai) echecs.push(message); };
  const egal = (a, b) => JSON.stringify(a) === JSON.stringify(b);

  const preparer = async p => {
    p.on("console", m => { if (m.type() === "error") erreurs.push(`console : ${m.text()}`); });
    p.on("pageerror", e => erreurs.push(`page : ${e.message}`));
    p.setDefaultTimeout(3000);
    await p.emulateMedia({reducedMotion: "reduce"});   // pas de transition à attendre
  };
  const ouvrir = async (p, adresse) => { await p.goto("about:blank"); await p.goto(adresse); };
  const attendre = async (p, condition, message) => {
    try { await p.waitForFunction(condition, null, {timeout: 2000}); } catch (e) { echecs.push(message); }
  };

  // ce que montre la page : vue visible, onglet courant, élément, fiche et segment de la vue
  const lire = p => p.evaluate(() => {
    const vues = [...document.querySelectorAll("#contenu > section.vue")].filter(s => s.checkVisibility());
    const s = vues[0];
    const visibles = sel => (s ? [...s.querySelectorAll(sel)] : []).filter(x => x.checkVisibility());
    return {
      hash: location.hash,
      sansJs: document.documentElement.classList.contains("sans-js"),
      vues: vues.map(x => x.dataset.vue),
      onglets: [...document.querySelectorAll("nav.vues a[aria-current='page']")].map(a => a.dataset.vue),
      elements: visibles(".scene > .element").map(x => x.dataset.k),
      fiches: visibles(".fiche-element").map(x => x.dataset.k),
      segments: (s ? [...s.querySelectorAll(".segments button[aria-pressed='true']")] : []).map(b => b.dataset.k),
      nom: s ? (s.querySelector(".fiche-nom") || {}).textContent : null,
      texte: s ? s.innerText : "",
    };
  });
  const rail = p => p.evaluate(() => {
    const r = document.querySelector("#rail"), b = r.getBoundingClientRect();
    return {gauche: b.left, largeur: b.width, visible: r.checkVisibility({visibilityProperty: true}),
            deplie: document.querySelector("#b-rail").getAttribute("aria-expanded")};
  });

  // polices de Google : feuille vide, le test ne dépend pas du réseau
  await page.context().route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//,
                             r => r.fulfill({status: 200, contentType: "text/css", body: ""}));
  await preparer(page);

  try {
    for (const [largeur, hauteur] of [[1440, 900], [390, 844]]) {
      await page.setViewportSize({width: largeur, height: hauteur});
      const t = `${largeur} px, `;
      let e;

      // Ouverture : la vue Plan seule, la classe sans-js retirée
      await ouvrir(page, DOC);
      e = await lire(page);
      verifier(!e.sansJs, t + "ouverture : la classe sans-js reste sur <html>");
      verifier(egal(e.vues, ["plan"]), t + `ouverture : vues visibles ${JSON.stringify(e.vues)}, attendu ["plan"]`);
      verifier(egal(e.onglets, ["plan"]), t + `ouverture : onglet courant ${JSON.stringify(e.onglets)}`);

      // Onglets : l'adresse suit, « précédent » revient sur Plan
      await page.click('nav.vues a[data-vue="coupes"]');
      e = await lire(page);
      verifier(e.hash === "#coupes", t + `onglet Coupes : adresse « ${e.hash} », attendu « #coupes »`);
      verifier(egal(e.vues, ["coupes"]), t + `onglet Coupes : vues visibles ${JSON.stringify(e.vues)}`);
      verifier(egal(e.onglets, ["coupes"]), t + `onglet Coupes : onglet courant ${JSON.stringify(e.onglets)}`);
      await page.goBack();
      await attendre(page, () => document.querySelector('section[data-vue="plan"]').checkVisibility(),
                     t + "précédent : la vue Plan ne revient pas");
      e = await lire(page);
      verifier(e.hash === "" && egal(e.vues, ["plan"]) && egal(e.onglets, ["plan"]),
               t + `précédent : ${JSON.stringify([e.hash, e.vues, e.onglets])}`);

      // Repère : #coupes?k=B montre B et presse son segment
      await ouvrir(page, DOC + "#coupes?k=B");
      e = await lire(page);
      verifier(egal(e.vues, ["coupes"]), t + `k=B : vues visibles ${JSON.stringify(e.vues)}`);
      verifier(egal(e.elements, ["B"]), t + `k=B : éléments visibles ${JSON.stringify(e.elements)}`);
      verifier(egal(e.fiches, ["B"]), t + `k=B : fiches visibles ${JSON.stringify(e.fiches)}`);
      verifier(egal(e.segments, ["B"]), t + `k=B : segments pressés ${JSON.stringify(e.segments)}`);
      verifier(e.nom === "Coupe B-B", t + `k=B : titre de la fiche « ${e.nom} »`);

      // segment C : l'adresse change sans nouvelle entrée d'historique
      if (largeur < 920) await page.click('section[data-vue="coupes"] .fiche-tete');
      const avant = await page.evaluate(() => history.length);
      await page.click('section[data-vue="coupes"] .segments button[data-k="C"]');
      e = await lire(page);
      verifier(e.hash === "#coupes?k=C", t + `segment C : adresse « ${e.hash} »`);
      verifier(egal(e.elements, ["C"]) && egal(e.segments, ["C"]) && e.nom === "Coupe C-C",
               t + `segment C : ${JSON.stringify([e.elements, e.segments, e.nom])}`);
      verifier(await page.evaluate(() => history.length) === avant, t + "segment C : nouvelle entrée d'historique");

      // repère inconnu : le premier élément
      await ouvrir(page, DOC + "#coupes?k=Z");
      e = await lire(page);
      verifier(egal(e.elements, ["A"]) && egal(e.segments, ["A"]) && e.nom === "Coupe A-A",
               t + `k=Z : ${JSON.stringify([e.elements, e.segments, e.nom])}, attendu l'élément A`);

      // Vue vide atteinte par l'adresse : le message, l'onglet reste grisé
      await ouvrir(page, DOC + "#iso");
      e = await lire(page);
      verifier(egal(e.vues, ["iso"]), t + `#iso : vues visibles ${JSON.stringify(e.vues)}`);
      verifier(e.texte.includes("Pas encore rendu"), t + `#iso : texte « ${e.texte} »`);
      verifier(await page.getAttribute('nav.vues a[data-vue="iso"]', "aria-disabled") === "true",
               t + "#iso : l'onglet Iso n'a plus aria-disabled");

      // État invalide : la vue par défaut, l'adresse corrigée
      await ouvrir(page, DOC + "#inconnu?c=zz");
      e = await lire(page);
      verifier(egal(e.vues, ["plan"]), t + `#inconnu?c=zz : vues visibles ${JSON.stringify(e.vues)}`);
      verifier(e.hash === "#plan", t + `#inconnu?c=zz : adresse « ${e.hash} », attendu « #plan »`);

      // adresse changée sur la page (lien, saisie) : la vue suit
      await page.evaluate(() => { location.hash = "#camera"; });
      await attendre(page, () => document.querySelector('section[data-vue="camera"]').checkVisibility(),
                     t + "#camera tapé dans l'adresse : la vue Caméra ne s'affiche pas");
    }

    // Menu (ordinateur) : réduit à 56 px, déplié par #b-rail, mémorisé
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC);
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    let r = await rail(page);
    verifier(r.largeur === 56 && r.deplie === "false", `menu : ${JSON.stringify(r)}, attendu réduit à 56 px`);
    await page.click("#b-rail");
    r = await rail(page);
    verifier(r.largeur === 264 && r.deplie === "true", `menu après #b-rail : ${JSON.stringify(r)}, attendu déplié`);
    await page.reload();
    r = await rail(page);
    verifier(r.largeur === 264, `menu après rechargement : ${r.largeur} px, attendu déplié`);

    // Sans localStorage : le menu reste réduit (le stockage dit pourtant « déplié »), aucune erreur
    const privee = await page.context().newPage();
    await preparer(privee);
    await privee.addInitScript(() => {
      const refus = () => { throw new DOMException("stockage refusé", "SecurityError"); };
      Storage.prototype.getItem = refus;
      Storage.prototype.setItem = refus;
    });
    await privee.setViewportSize({width: 1440, height: 900});
    await privee.goto(DOC + "#coupes?k=B");
    r = await rail(privee);
    verifier(r.largeur === 56, `sans localStorage : menu à ${r.largeur} px, attendu 56`);
    const p = await lire(privee);
    verifier(egal(p.vues, ["coupes"]) && egal(p.elements, ["B"]), `sans localStorage : ${JSON.stringify([p.vues, p.elements])}`);
    await privee.click("#b-rail");
    r = await rail(privee);
    verifier(r.largeur === 264, `sans localStorage : #b-rail ne déplie pas le menu (${r.largeur} px)`);
    await privee.close();

    // Mobile
    await page.setViewportSize({width: 390, height: 844});
    await ouvrir(page, DOC + "#coupes");
    const nav = await page.evaluate(() => {
      const n = document.querySelector("nav.vues");
      return {position: getComputedStyle(n).position, bas: n.getBoundingClientRect().bottom, hauteur: innerHeight};
    });
    verifier(nav.position === "fixed" && Math.abs(nav.bas - nav.hauteur) <= 1, `mobile : onglets ${JSON.stringify(nav)}, attendu fixés en bas`);

    const fiche = () => page.evaluate(() => {
      const f = document.querySelector('section[data-vue="coupes"] .fiche');
      return {hauteur: f.getBoundingClientRect().height, ecran: innerHeight,
              ouverte: f.querySelector(".fiche-tete").getAttribute("aria-expanded")};
    });
    let f = await fiche();
    verifier(Math.round(f.hauteur) === 48 && f.ouverte === "false", `mobile : fiche fermée ${JSON.stringify(f)}, attendu 48 px`);
    await page.click('section[data-vue="coupes"] .fiche-tete');
    f = await fiche();
    verifier(f.hauteur > 48 && f.hauteur <= 0.54 * f.ecran + 0.5 && f.ouverte === "true",
             `mobile : fiche ouverte ${JSON.stringify(f)}, attendu au plus 54 % de ${f.ecran} px`);
    await page.click('section[data-vue="coupes"] .fiche-tete');
    f = await fiche();
    verifier(Math.round(f.hauteur) === 48 && f.ouverte === "false", `mobile : fiche refermée ${JSON.stringify(f)}`);

    r = await rail(page);
    verifier(!r.visible, `mobile : le menu est visible avant #b-maison ${JSON.stringify(r)}`);
    await page.click("#b-maison");
    r = await rail(page);
    verifier(r.visible && r.gauche === 0 && r.largeur === 390, `mobile : #b-maison n'ouvre pas le tiroir ${JSON.stringify(r)}`);
    const focus = () => page.evaluate(() => document.activeElement.id || document.activeElement.className);
    verifier(await focus() === "rail-fermer", `mobile : le focus n'entre pas dans le tiroir (${await focus()})`);
    await page.click("#rail .rail-fermer");
    r = await rail(page);
    verifier(!r.visible, `mobile : « Fermer » ne referme pas le tiroir ${JSON.stringify(r)}`);
    verifier(await focus() === "b-maison", `mobile : le focus ne revient pas sur #b-maison (${await focus()})`);

    for (const vue of ["plan", "coupes", "iso", "camera", "explication"]) {
      await ouvrir(page, `${DOC}#${vue}`);
      const l = await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
      verifier(l[0] <= l[1], `mobile, ${vue} : la page défile en largeur (${l[0]} > ${l[1]})`);
    }
  } catch (e) {
    echecs.push(`exception : ${e.message.split("\n")[0]}`);
  }

  return {ok: echecs.length === 0 && erreurs.length === 0, echecs, erreurs};
}
