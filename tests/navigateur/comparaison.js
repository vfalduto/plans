/* Comparaison de variantes : « Comparer », « avec », choix de la variante, état partageable dans l'adresse (c=),
   étiquettes du bandeau, rideau, échec de chargement, version figée.
   Lancé par tests/navigateur/lancer.sh, qui ouvre la racine du site d'essai avant d'appeler ce script.
   Le document d'essai a trois variantes, a, b et c (« A », « B », « C ») : leurs dessins sont un rectangle de 60, 70
   et 80 de large, et a n'a pas de coupe D. */
async page => {
  const BASE = new URL(page.url()).origin;
  const DOC = `${BASE}/essai/amenagement/`;
  const echecs = [], erreurs = [];
  const verifier = (vrai, message) => { if (!vrai) echecs.push(message); };
  const egal = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  let refus404 = false;   // pendant l'essai d'échec de chargement, le 404 de c.html est voulu

  const preparer = async p => {
    p.on("console", m => {
      if (m.type() !== "error" || (refus404 && /404/.test(m.text()))) return;
      erreurs.push(`console : ${m.text()}`);
    });
    p.on("pageerror", e => erreurs.push(`page : ${e.message}`));
    p.setDefaultTimeout(3000);
    await p.emulateMedia({reducedMotion: "reduce"});
  };
  const ouvrir = async (p, adresse) => { await p.goto("about:blank"); await p.goto(adresse); };
  const attendre = async (p, condition, arg, message) => {
    try { await p.waitForFunction(condition, arg, {timeout: 2000}); } catch (e) { echecs.push(message); }
  };
  // la comparaison est posée quand le bandeau de la vue a ses deux étiquettes (le chargement est asynchrone)
  const comparee = (p, vue, message) =>
    attendre(p, v => document.querySelectorAll(`section[data-vue="${v}"] .bandeau .etiq-var`).length === 2, vue, message);

  // ce que montrent la scène de la vue et la barre
  const lire = (p, vue) => p.evaluate(v => {
    const s = document.querySelector(`section[data-vue="${v}"]`), scene = s.querySelector(".scene");
    const r = scene.getBoundingClientRect(), milieu = r.left + r.width / 2;
    const visibles = sel => [...scene.querySelectorAll(sel)].filter(x => x.checkVisibility());
    const comp = document.querySelector("#c-comp"), autre = document.querySelector("#c-autre");
    return {
      hash: location.hash,
      dessins: visibles(".element > svg").map(x => x.querySelector("rect:not(.zone)").getAttribute("width")),
      viewBox: [...new Set(visibles(".element > svg").map(x => x.getAttribute("viewBox")))],
      cadres: visibles(".element > .cadre").map(x => x.style.transform),
      zones: visibles("rect.zone").length,
      poignee: visibles(".poignee").length,
      clones: document.querySelectorAll(".scene > .element.b, .poignee").length,
      etiquettes: visibles(".bandeau .etiq-var").map(x => {
        const b = x.getBoundingClientRect();
        return {texte: x.textContent, manque: x.classList.contains("manque"), bas: Math.round(r.bottom - b.bottom),
                cote: b.right <= milieu ? "gauche" : b.left >= milieu ? "droite" : "milieu"};
      }),
      outils: s.querySelector(".outils").getBoundingClientRect().top,
      comparer: comp.checkVisibility() ? comp.getAttribute("aria-pressed") : "caché",
      avec: autre.closest("label").checkVisibility() ? autre.value : "caché",
      deuxChoix: document.querySelector(".b-cases").classList.contains("deux-choix"),
      base: document.querySelector("#c-variante").value,
    };
  }, vue);
  const textes = e => e.etiquettes.map(x => x.texte);
  const rect = (p, sel) => p.evaluate(s => {
    const b = document.querySelector(s).getBoundingClientRect();
    return {x: b.left, y: b.top, w: b.width, h: b.height};
  }, sel);
  // position du rideau : --pos de la scène (50 % par défaut) et aria-valuenow de la poignée
  const position = (p, vue) => p.evaluate(v => {
    const s = document.querySelector(`section[data-vue="${v}"] .scene`);
    return [parseFloat(getComputedStyle(s).getPropertyValue("--pos")) || 50, +s.querySelector(".poignee").getAttribute("aria-valuenow")];
  }, vue);
  const proche = (a, b) => Math.abs(a - b) < 0.01;

  await page.context().route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//,
                             r => r.fulfill({status: 200, contentType: "text/css", body: ""}));
  await preparer(page);

  try {
    await page.setViewportSize({width: 1440, height: 900});

    // Bouton : #plan?c=b, deux dessins, la poignée, « A » et « B » en bas de la scène ; les outils ne bougent pas
    await ouvrir(page, DOC + "#plan");
    let e = await lire(page, "plan");
    verifier(e.comparer === "false" && e.avec === "caché" && !e.deuxChoix && e.poignee === 0 && e.etiquettes.length === 0,
             `sans comparaison : ${JSON.stringify(e)}`);
    const haut = e.outils;
    await page.click("#c-comp");
    await comparee(page, "plan", "Comparer : pas d'étiquettes A et B");
    e = await lire(page, "plan");
    verifier(e.hash === "#plan?c=b", `Comparer : adresse « ${e.hash} », attendu « #plan?c=b »`);
    verifier(egal(e.dessins, ["60", "70"]), `Comparer : dessins ${JSON.stringify(e.dessins)}, attendu A (60) et B (70)`);
    verifier(e.poignee === 1 && e.clones === 2, `Comparer : ${e.poignee} poignée visible, ${e.clones} clone et poignée dans la page`);
    verifier(egal(e.etiquettes.map(x => [x.texte, x.cote, x.manque]), [["A", "gauche", false], ["B", "droite", false]]),
             `Comparer : étiquettes ${JSON.stringify(e.etiquettes)}`);
    verifier(e.etiquettes.every(x => x.bas >= 0 && x.bas <= 24), `Comparer : étiquettes loin du bas de la scène ${JSON.stringify(e.etiquettes)}`);
    verifier(e.outils === haut, `Comparer : les outils passent de ${haut} à ${e.outils} px du haut`);
    verifier(e.comparer === "true" && e.avec === "b" && e.deuxChoix, `Comparer : barre ${JSON.stringify([e.comparer, e.avec, e.deuxChoix])}`);
    verifier(e.zones === 0, `Comparer : ${e.zones} zone(s) de meuble visible(s), aucune attendue en comparaison`);
    verifier(e.viewBox.length === 1, `Comparer : les deux dessins n'ont pas la même viewBox ${JSON.stringify(e.viewBox)}`);

    // zoom et déplacement valent pour les deux variantes, y compris en glissant sur la variante comparée (à droite)
    await page.click('section[data-vue="plan"] [data-z="0.7"]');
    const z = await lire(page, "plan");
    verifier(z.viewBox.length === 1 && z.viewBox[0] !== e.viewBox[0], `Comparer, « + » : viewBox ${JSON.stringify(z.viewBox)}`);
    let r = await rect(page, 'section[data-vue="plan"] .scene');
    await page.mouse.move(r.x + r.w * 0.8, r.y + r.h * 0.5);
    await page.mouse.down();
    await page.mouse.move(r.x + r.w * 0.7, r.y + r.h * 0.4, {steps: 4});
    await page.mouse.up();
    const g = await lire(page, "plan");
    verifier(g.viewBox.length === 1 && g.viewBox[0] !== z.viewBox[0],
             `Comparer, glisser sur la variante B : viewBox ${JSON.stringify(g.viewBox)} (avant ${z.viewBox})`);
    verifier(g.hash === "#plan?c=b", `Comparer, glisser : adresse « ${g.hash} »`);
    await page.click('section[data-vue="plan"] [data-z="0"]');

    // Choix « avec » : C
    await page.selectOption("#c-autre", "c");
    await attendre(page, () => location.hash === "#plan?c=c"
                     && (document.querySelectorAll('section[data-vue="plan"] .bandeau .etiq-var')[1] || {}).textContent === "C",
                   null, "avec C : la comparaison ne passe pas à C");
    e = await lire(page, "plan");
    verifier(e.hash === "#plan?c=c" && egal(e.dessins, ["60", "80"]) && egal(textes(e), ["A", "C"]) && e.avec === "c" && e.clones === 2,
             `avec C : ${JSON.stringify([e.hash, e.dessins, textes(e), e.avec, e.clones])}`);

    // « Comparer » une seconde fois : la comparaison est retirée
    await page.click("#c-comp");
    e = await lire(page, "plan");
    verifier(e.hash === "#plan" && egal(e.dessins, ["60"]) && e.clones === 0 && e.etiquettes.length === 0
             && e.comparer === "false" && e.avec === "caché" && !e.deuxChoix && e.zones === 1,
             `Comparer une seconde fois : ${JSON.stringify(e)}`);

    // un meuble choisi sur le plan : la comparaison le referme (maquette : pas de meuble choisi en comparaison)
    await ouvrir(page, DOC + "#plan?k=0");
    await page.click("#c-comp");
    await comparee(page, "plan", "meuble choisi, Comparer : pas de comparaison");
    e = await lire(page, "plan");
    const nom = await page.textContent('section[data-vue="plan"] .fiche-nom');
    verifier(e.hash === "#plan?c=b" && nom === "Plan", `meuble choisi, Comparer : adresse « ${e.hash} », fiche « ${nom} »`);

    // Ancienne forme : c=1 compare avec la première autre variante
    await ouvrir(page, DOC + "#plan?c=1");
    await comparee(page, "plan", "#plan?c=1 : pas de comparaison");
    e = await lire(page, "plan");
    verifier(e.hash === "#plan?c=b" && egal(textes(e), ["A", "B"]) && egal(e.dessins, ["60", "70"]),
             `#plan?c=1 : ${JSON.stringify([e.hash, textes(e), e.dessins])}`);

    // c égal à la base : retiré de l'adresse, rien n'est chargé
    const demandes = [];
    const noter = q => demandes.push(q.url());
    page.on("request", noter);
    await ouvrir(page, DOC + "#plan?c=a");
    await page.waitForTimeout(300);
    e = await lire(page, "plan");
    page.off("request", noter);
    verifier(e.hash === "#plan" && e.comparer === "false" && e.clones === 0 && e.etiquettes.length === 0
             && !demandes.some(u => /\/[bc]\.html$/.test(u)),
             `#plan?c=a sur a : ${JSON.stringify([e.hash, e.comparer, e.clones, textes(e), demandes])}`);

    // Adresse mal formée : aucune erreur, la vue s'affiche, avec ou sans comparaison
    for (const [adresse, dessins] of [["#coupes?k=%E0%A4%A", ["60"]], ["#coupes?k=%E0%A4%A&c=b", ["60", "70"]]]) {
      await ouvrir(page, DOC + adresse);
      if (dessins.length === 2) await comparee(page, "coupes", `${adresse} : pas de comparaison`);
      e = await lire(page, "coupes");
      const vue = await page.evaluate(() => document.documentElement.dataset.vue);
      verifier(vue === "coupes" && egal(e.dessins, dessins), `${adresse} : vue ${vue}, dessins ${JSON.stringify(e.dessins)}`);
    }

    // Lien direct : b.html#coupes?k=D&c=a, et a n'a pas de coupe D
    await ouvrir(page, DOC + "b.html#coupes?k=D&c=a");
    await comparee(page, "coupes", "b.html#coupes?k=D&c=a : pas d'étiquettes");
    e = await lire(page, "coupes");
    verifier(egal(e.etiquettes.map(x => [x.texte, x.manque]), [["B", false], ["A : pas d'équivalent", true]]),
             `b.html#coupes?k=D&c=a : étiquettes ${JSON.stringify(e.etiquettes)}`);
    verifier(e.hash === "#coupes?k=D&c=a" && egal(e.dessins, ["70"]) && e.clones === 0 && e.comparer === "true" && e.avec === "a",
             `b.html#coupes?k=D&c=a : ${JSON.stringify([e.hash, e.dessins, e.clones, e.comparer, e.avec])}`);

    // Échange : sur a, #plan?c=b, choisir B comme base charge b.html#plan?c=a
    await ouvrir(page, DOC + "#plan?c=b");
    await comparee(page, "plan", "#plan?c=b : pas de comparaison");
    await page.selectOption("#c-variante", "b");
    try { await page.waitForURL(DOC + "b.html#plan?c=a"); } catch (x) { echecs.push(`échange : adresse ${page.url()}, attendu b.html#plan?c=a`); }
    await comparee(page, "plan", "échange : pas de comparaison sur b");
    e = await lire(page, "plan");
    verifier(egal(textes(e), ["B", "A"]) && egal(e.dessins, ["70", "60"]) && e.base === "b",
             `échange : ${JSON.stringify([textes(e), e.dessins, e.base])}`);
    // c reste quand il ne devient pas la base ; le repère suit
    await ouvrir(page, DOC + "#coupes?k=B&c=c");
    await page.selectOption("#c-variante", "b");
    try { await page.waitForURL(DOC + "b.html#coupes?k=B&c=c"); } catch (x) { echecs.push(`choix de B avec c=c : adresse ${page.url()}`); }
    // « précédent » : le choix de variante montre de nouveau A
    await page.goBack();
    try { await page.waitForURL(DOC + "#coupes?k=B&c=c"); } catch (x) { echecs.push(`précédent : adresse ${page.url()}`); }
    await attendre(page, () => document.querySelector("#c-variante").value === "a", null,
                   "précédent après le choix de B : le choix de variante ne montre pas A");
    // un meuble choisi sur le plan (k = rang de sa zone, qui désigne un autre meuble dans l'autre variante) : retiré
    await ouvrir(page, DOC + "#plan?k=0");
    await page.selectOption("#c-variante", "b");
    try { await page.waitForURL(DOC + "b.html#plan"); } catch (x) { echecs.push(`choix de B depuis #plan?k=0 : adresse ${page.url()}, attendu b.html#plan`); }
    const meuble = await page.evaluate(() => document.querySelectorAll('section[data-vue="plan"] rect.zone.ici').length);
    verifier(meuble === 0, `choix de B depuis #plan?k=0 : ${meuble} meuble choisi sur B`);

    // Changement d'onglet : Coupes garde c ; Explication cache « Comparer » ; Plan retrouve la comparaison
    await ouvrir(page, DOC + "#plan?c=b");
    await comparee(page, "plan", "onglets : pas de comparaison sur le plan");
    await page.click('nav.vues a[data-vue="coupes"]');
    await comparee(page, "coupes", "onglet Coupes : pas de comparaison");
    e = await lire(page, "coupes");
    verifier(e.hash === "#coupes?c=b" && egal(e.dessins, ["60", "70"]) && e.comparer === "true" && e.clones === 2,
             `onglet Coupes : ${JSON.stringify([e.hash, e.dessins, e.comparer, e.clones])}`);
    await page.click('nav.vues a[data-vue="explication"]');
    const x = await page.evaluate(() => ({
      hash: location.hash, comparer: document.querySelector("#c-comp").checkVisibility(),
      avec: document.querySelector("#c-autre").closest("label").checkVisibility(),
      deux: document.querySelector(".b-cases").classList.contains("deux-choix"),
      clones: document.querySelectorAll(".scene > .element.b, .poignee").length,
    }));
    verifier(egal(x, {hash: "#explication?c=b", comparer: false, avec: false, deux: false, clones: 0}),
             `onglet Explication : ${JSON.stringify(x)}`);
    await page.click('nav.vues a[data-vue="plan"]');
    await comparee(page, "plan", "retour sur Plan : la comparaison ne revient pas");
    e = await lire(page, "plan");
    verifier(e.hash === "#plan?c=b" && e.poignee === 1 && e.comparer === "true",
             `retour sur Plan : ${JSON.stringify([e.hash, e.poignee, e.comparer])}`);

    // Échec de chargement : c.html en 404, « C : comparaison indisponible », la scène reste utilisable
    refus404 = true;
    await page.route(DOC + "c.html", q => q.fulfill({status: 404, contentType: "text/html", body: "absent"}));
    await ouvrir(page, DOC + "#plan?c=c");
    await comparee(page, "plan", "c.html en 404 : pas d'étiquettes");
    e = await lire(page, "plan");
    verifier(egal(e.etiquettes.map(x => [x.texte, x.manque]), [["A", false], ["C : comparaison indisponible", true]]),
             `c.html en 404 : étiquettes ${JSON.stringify(e.etiquettes)}`);
    verifier(egal(e.dessins, ["60"]) && e.clones === 0, `c.html en 404 : ${JSON.stringify([e.dessins, e.clones])}`);
    await page.click('section[data-vue="plan"] [data-z="0.7"]');
    const apres = await lire(page, "plan");
    verifier(apres.viewBox[0] !== e.viewBox[0], "c.html en 404 : le zoom ne marche plus");
    await page.unroute(DOC + "c.html");
    refus404 = false;

    // Rideau au clavier : 4 points par flèche ; à la souris : la poignée suit, le dessin ne bouge pas
    await ouvrir(page, DOC + "#plan?c=b");
    await comparee(page, "plan", "rideau : pas de comparaison");
    let pos = await position(page, "plan");
    verifier(proche(pos[0], 50) && pos[1] === 50, `rideau : position initiale ${pos}`);
    await page.focus('section[data-vue="plan"] .poignee');
    await page.keyboard.press("ArrowRight");
    pos = await position(page, "plan");
    verifier(proche(pos[0], 54) && pos[1] === 54, `rideau, flèche droite : ${pos}, attendu 54`);
    await page.keyboard.press("ArrowLeft");
    await page.keyboard.press("ArrowLeft");
    pos = await position(page, "plan");
    verifier(proche(pos[0], 46) && pos[1] === 46, `rideau, deux flèches gauches : ${pos}, attendu 46`);
    const vb = (await lire(page, "plan")).viewBox;
    const h = await rect(page, 'section[data-vue="plan"] .poignee');
    r = await rect(page, 'section[data-vue="plan"] .scene');
    await page.mouse.move(h.x + h.w / 2, h.y + h.h / 2);
    await page.mouse.down();
    await page.mouse.move(r.x + r.w * 0.75, h.y + h.h / 2, {steps: 5});
    await page.mouse.up();
    pos = await position(page, "plan");
    verifier(Math.abs(pos[0] - 75) < 0.5, `rideau à la souris : ${pos}, attendu 75`);
    verifier(egal((await lire(page, "plan")).viewBox, vb), "rideau à la souris : le dessin s'est déplacé");

    // Rideau sur un rendu zoomé ×2 et déplacé : la coupure reste sous la poignée (à moins de 1 px)
    await ouvrir(page, DOC + "#camera?c=b");
    await comparee(page, "camera", "#camera?c=b : pas de comparaison");
    e = await lire(page, "camera");
    verifier(e.cadres.length === 2 && e.poignee === 1, `#camera?c=b : ${JSON.stringify([e.cadres, e.poignee])}`);
    await page.click('section[data-vue="camera"] [data-z="0.7"]');
    await page.click('section[data-vue="camera"] [data-z="0.7"]');
    r = await rect(page, 'section[data-vue="camera"] .scene');
    await page.mouse.move(r.x + r.w * 0.3, r.y + r.h * 0.5);
    await page.mouse.down();
    await page.mouse.move(r.x + r.w * 0.22, r.y + r.h * 0.46, {steps: 4});
    await page.mouse.up();
    e = await lire(page, "camera");
    const echelle = +((/scale\(([\d.]+)\)/.exec(e.cadres[0] || "") || [0, 1])[1]);
    verifier(e.cadres.length === 2 && e.cadres[0] === e.cadres[1] && Math.abs(echelle - 2) < 0.1,
             `rendu zoomé : transformations ${JSON.stringify(e.cadres)}, attendu les mêmes, à l'échelle 2`);
    await page.focus('section[data-vue="camera"] .poignee');
    for (let i = 0; i < 3; i++) await page.keyboard.press("ArrowRight");
    const coupure = await page.evaluate(() => {
      const s = document.querySelector('section[data-vue="camera"] .scene'), p = s.querySelector(".poignee");
      const b = p.getBoundingClientRect(), x = b.left + b.width / 2, y = s.getBoundingClientRect().top + s.clientHeight / 2;
      p.style.pointerEvents = "none";                  // on sonde ce qui est sous la poignée
      const cote = dx => {
        const el = (document.elementFromPoint(x + dx, y) || document.body).closest(".element");
        return el ? (el.classList.contains("b") ? "B" : "A") : null;
      };
      const res = {gauche: cote(-1), droite: cote(1), pos: getComputedStyle(s).getPropertyValue("--pos").trim()};
      p.style.pointerEvents = "";
      return res;
    });
    verifier(coupure.gauche === "A" && coupure.droite === "B" && proche(parseFloat(coupure.pos), 62),
             `rendu zoomé : sous la poignée ${JSON.stringify(coupure)}, attendu A à 1 px à gauche, B à 1 px à droite, --pos 62 %`);

    // Version figée (body[data-figee]) : jamais comparée, c retiré, rien n'est chargé
    await page.route(DOC, async q => {
      const rep = await q.fetch();
      await q.fulfill({response: rep, body: (await rep.text()).replace("<body", '<body data-figee="V1.2"')});
    });
    demandes.length = 0;
    page.on("request", noter);
    await ouvrir(page, DOC + "#plan?c=b");
    await page.waitForTimeout(300);
    e = await lire(page, "plan");
    page.off("request", noter);
    await page.unroute(DOC);
    verifier(e.hash === "#plan" && e.comparer === "caché" && e.avec === "caché" && e.clones === 0 && e.etiquettes.length === 0
             && !demandes.some(u => /\/[bc]\.html$/.test(u)),
             `version figée : ${JSON.stringify([e.hash, e.comparer, e.avec, e.clones, textes(e), demandes])}`);

    // Mobile : « avec » visible, la version cède sa place, les étiquettes en bas de la scène, pas de défilement en largeur
    await page.setViewportSize({width: 390, height: 844});
    await ouvrir(page, DOC + "#plan?c=c");
    await comparee(page, "plan", "mobile : pas de comparaison");
    e = await lire(page, "plan");
    const m = await page.evaluate(() => ({
      defile: document.documentElement.scrollWidth > innerWidth,
      version: document.querySelector(".b-case.version").checkVisibility(),
    }));
    verifier(e.avec === "c" && e.deuxChoix && !m.version && !m.defile && egal(textes(e), ["A", "C"])
             && e.etiquettes.every(x => x.bas >= 0 && x.bas <= 24),
             `mobile : ${JSON.stringify([e.avec, e.deuxChoix, m, e.etiquettes])}`);
  } catch (e) {
    echecs.push(`exception : ${e.message.split("\n")[0]}`);
  }

  return {ok: echecs.length === 0 && erreurs.length === 0, echecs, erreurs};
}
