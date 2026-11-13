/* Anciennes adresses : ancre traduite en vue et repère, ancre inconnue ou absente vers la vue par défaut.
   Lancé par tests/navigateur/lancer.sh, qui ouvre la racine du site d'essai avant d'appeler ce script. */
async page => {
  const BASE = new URL(page.url()).origin;
  const echecs = [], erreurs = [];
  const verifier = (vrai, message) => { if (!vrai) echecs.push(message); };

  page.on("console", m => { if (m.type() === "error") erreurs.push(`console : ${m.text()}`); });
  page.on("pageerror", e => erreurs.push(`page : ${e.message}`));
  page.setDefaultTimeout(3000);
  await page.context().route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//,
                             r => r.fulfill({status: 200, contentType: "text/css", body: ""}));

  // ouvre `entree`, attend d'être arrivé sur la nouvelle page et que la vue soit là, puis lit l'adresse et la vue
  const aller = async entree => {
    await page.goto("about:blank");
    await page.goto(BASE + entree);
    try {
      await page.waitForFunction(() => location.pathname.startsWith("/essai/") && document.querySelector("#contenu > section.vue"),
                                 null, {timeout: 3000});
    } catch (e) { echecs.push(`${entree} : pas de vue atteinte`); }
    return page.evaluate(() => ({
      chemin: location.pathname, hash: location.hash,
      vues: [...document.querySelectorAll("#contenu > section.vue")].filter(s => s.checkVisibility())
        .map(s => s.dataset.vue),
    }));
  };

  try {
    let r = await aller("/ancienne.html#coupe-b-b-mur-de-la-salle-de-bain");
    verifier(r.chemin === "/essai/amenagement/", `ancre de coupe : chemin ${r.chemin}`);
    verifier(r.hash === "#coupes?k=B", `ancre de coupe : fragment ${r.hash}`);
    verifier(r.vues.join() === "coupes", `ancre de coupe : vues ${r.vues}`);

    r = await aller("/ancienne.html#plan");
    verifier(r.hash === "#plan" && r.vues.join() === "plan", `ancre exacte : ${r.hash} ${r.vues}`);

    r = await aller("/ancienne.html#inconnue");
    verifier(r.chemin === "/essai/amenagement/", `ancre inconnue : chemin ${r.chemin}`);
    verifier(r.hash === "" && r.vues.join() === "plan", `ancre inconnue : ${r.hash} ${r.vues}`);

    r = await aller("/ancienne.html");
    verifier(r.chemin === "/essai/amenagement/", `sans ancre : chemin ${r.chemin}`);
    verifier(r.hash === "" && r.vues.join() === "plan", `sans ancre : ${r.hash} ${r.vues}`);

    // depuis un sous-dossier, vers une autre variante
    r = await aller("/vieux/ancienne.html#coupe-c-c-coupe");
    verifier(r.chemin === "/essai/amenagement/b.html", `sous-dossier : chemin ${r.chemin}`);
    verifier(r.hash === "#coupes?k=C", `sous-dossier : fragment ${r.hash}`);
  } catch (e) {
    echecs.push(`exception : ${e.message}`);
  }
  return {ok: echecs.length === 0 && erreurs.length === 0, echecs, erreurs};
}
