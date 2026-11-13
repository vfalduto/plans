/* Scène : zoom (boutons, molette, pincement), déplacement, recadrage, mesure, calques et zones de meuble.
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

  // la viewBox du dessin visible de la vue, en nombres
  const vb = (p, vue) => p.evaluate(v => {
    const s = document.querySelector(`section[data-vue="${v}"] .element:not([hidden]) > svg`);
    return s.getAttribute("viewBox").split(/\s+/).map(Number);
  }, vue);
  // le rectangle de la scène de la vue, en pixels de la page
  const scene = (p, vue) => p.evaluate(v => {
    const r = document.querySelector(`section[data-vue="${v}"] .scene`).getBoundingClientRect();
    return {x: r.left, y: r.top, w: r.width, h: r.height};
  }, vue);
  const echelle = p => p.evaluate(() => {
    const c = document.querySelector('section[data-vue="camera"] .cadre');
    const m = /scale\(([\d.]+)\)/.exec(c.style.transform || "");
    return m ? +m[1] : 1;
  });
  const fiche = p => p.evaluate(() => {
    const s = document.querySelector('section[data-vue="plan"]');
    return {nom: s.querySelector(".fiche-nom").textContent, corps: s.querySelector(".fiche-meuble").innerText,
            ici: s.querySelectorAll("rect.zone.ici").length, hash: location.hash};
  });

  await page.context().route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//,
                             r => r.fulfill({status: 200, contentType: "text/css", body: ""}));
  await preparer(page);

  try {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#plan");
    await page.evaluate(() => localStorage.clear());
    await ouvrir(page, DOC + "#plan");

    // Zoom par bouton, puis recadrage
    const v0 = await vb(page, "plan");
    await page.click('section[data-vue="plan"] [data-z="0.7"]');
    let v = await vb(page, "plan");
    verifier(Math.abs(v[2] / v0[2] - 0.7) < 0.01, `« + » : largeur ${v0[2]} -> ${v[2]} (attendu x 0,7)`);
    await page.click('section[data-vue="plan"] [data-z="1.43"]');
    v = await vb(page, "plan");
    verifier(Math.abs(v[2] / v0[2] - 1.001) < 0.01, `« - » après « + » : largeur ${v[2]} au lieu de ${v0[2]}`);
    await page.click('section[data-vue="plan"] [data-z="0.7"]');
    await page.click('section[data-vue="plan"] [data-z="0"]');
    v = await vb(page, "plan");
    verifier(v.every((x, i) => Math.abs(x - v0[i]) < 1e-6), `recadrer : ${v} au lieu de ${v0}`);

    // Molette et glisser
    let r = await scene(page, "plan");
    await page.mouse.move(r.x + r.w * 0.7, r.y + r.h * 0.6);
    await page.mouse.wheel(0, -300);
    await attendre(page, () => document.querySelector('section[data-vue="plan"] .element svg').viewBox.baseVal.width < 105,
                   "molette : la viewBox ne change pas");
    v = await vb(page, "plan");
    verifier(v[2] < v0[2], `molette vers le haut : largeur ${v[2]} (origine ${v0[2]})`);
    await page.click('section[data-vue="plan"] [data-z="0"]');
    await page.mouse.move(r.x + r.w * 0.6, r.y + r.h * 0.7);
    await page.mouse.down();
    await page.mouse.move(r.x + r.w * 0.5, r.y + r.h * 0.6, {steps: 4});
    await page.mouse.up();
    v = await vb(page, "plan");
    verifier(v[0] > v0[0] + 1 && v[1] > v0[1] + 1 && Math.abs(v[2] - v0[2]) < 1e-6,
             `glisser : viewBox ${v} (origine ${v0}), la vue devait se déplacer vers le bas et la droite du dessin`);
    verifier((await fiche(page)).hash === "#plan", "glisser : un glisser ne doit pas toucher une zone");
    await page.click('section[data-vue="plan"] [data-z="0"]');

    // Mesure : deux clics (à droite des zones), « Mesuré : N cm »
    const bm = 'section[data-vue="plan"] .b-mesure';
    await page.click(bm);
    verifier(await page.getAttribute(bm, "aria-pressed") === "true", "mesure : le bouton ne s'enfonce pas");
    verifier(await page.evaluate(() => document.querySelector('section[data-vue="plan"] .scene').classList.contains("mesure")),
             "mesure : la scène n'a pas la classe mesure");
    await page.mouse.click(r.x + r.w * 0.6, r.y + r.h * 0.5);
    await page.mouse.click(r.x + r.w * 0.8, r.y + r.h * 0.5);
    const mes = 'section[data-vue="plan"] .bandeau .mes';
    await attendre(page, () => !document.querySelector('section[data-vue="plan"] .bandeau .mes').hidden,
                   "mesure : rien dans .bandeau .mes après deux clics");
    const texte = await page.textContent(mes);
    verifier(/^Mesuré : \d+(,\d)? cm$/.test(texte), `mesure : texte « ${texte} »`);
    verifier(await page.evaluate(() => document.querySelectorAll('section[data-vue="plan"] .element svg .pt-mesure').length) === 2,
             "mesure : deux points attendus sur le dessin");
    // en mode mesure, toucher une zone ne l'ouvre pas
    const z = await page.evaluate(() => {
      const b = document.querySelector('section[data-vue="plan"] rect.zone').getBoundingClientRect();
      return {x: b.left + b.width / 2, y: b.top + b.height / 2};
    });
    await page.mouse.click(z.x, z.y);
    verifier((await fiche(page)).ici === 0, "mesure : un clic sur une zone ouvre sa fiche");
    await page.click(bm);
    verifier(await page.evaluate(() => document.querySelector('section[data-vue="plan"] .bandeau .mes').hidden),
             "mesure : le texte reste affiché quand l'outil est relâché");
    verifier(await page.evaluate(() => document.querySelectorAll('section[data-vue="plan"] .pt-mesure').length) === 0,
             "mesure : les points restent quand l'outil est relâché");

    // Zones de meuble : clic, Entrée, Espace, adresse
    let f = await fiche(page);
    verifier(f.corps.includes("Touchez un meuble pour afficher sa fiche."), `zone : texte initial absent (${f.corps})`);
    await page.mouse.click(z.x, z.y);
    f = await fiche(page);
    verifier(f.nom === "Banc" && f.corps.includes("95 cm") && f.ici === 1 && f.hash === "#plan?k=0",
             `zone : clic ${JSON.stringify(f)}`);
    await page.click('section[data-vue="plan"] .fiche-meuble >> text=Fermer');
    f = await fiche(page);
    verifier(f.nom === "Plan" && f.corps.includes("Touchez un meuble") && f.ici === 0 && f.hash === "#plan",
             `zone : Fermer ${JSON.stringify(f)}`);
    await page.focus('section[data-vue="plan"] rect.zone');
    await page.keyboard.press("Enter");
    f = await fiche(page);
    verifier(f.nom === "Banc" && f.ici === 1, `zone : Entrée ${JSON.stringify(f)}`);
    await page.click('section[data-vue="plan"] .fiche-meuble >> text=Fermer');
    await page.focus('section[data-vue="plan"] rect.zone');
    await page.keyboard.press("Space");
    f = await fiche(page);
    verifier(f.nom === "Banc" && f.ici === 1, `zone : Espace ${JSON.stringify(f)}`);
    await ouvrir(page, DOC + "#plan?k=0");
    f = await fiche(page);
    verifier(f.nom === "Banc" && f.ici === 1, `zone : #plan?k=0 à l'ouverture ${JSON.stringify(f)}`);
    await page.evaluate(() => { location.hash = "#plan?k=9"; });
    f = await fiche(page);
    verifier(f.nom === "Plan" && f.ici === 0, `zone : k inconnu ${JSON.stringify(f)}`);
    await page.evaluate(() => { location.hash = "#explication"; });
    await page.evaluate(() => { location.hash = "#plan?k=0"; });
    f = await fiche(page);
    verifier(f.nom === "Banc" && f.ici === 1, `zone : lien « Montrer sur le plan » depuis une autre vue ${JSON.stringify(f)}`);

    // Calques : boutons, classe sur la section, mémoire
    const cotes = 'section[data-vue="plan"] .calques button[data-calque="cotes"]';
    verifier(await page.evaluate(() => document.querySelectorAll('input[type="checkbox"]').length) === 0, "calques : case à cocher");
    await page.click(cotes);
    verifier(await page.getAttribute(cotes, "aria-pressed") === "false", "calques : aria-pressed reste vrai");
    verifier(await page.evaluate(() => document.querySelector('section[data-vue="plan"]').classList.contains("sans-cotes")),
             "calques : sans-cotes absent après le clic");
    await ouvrir(page, DOC + "#plan");
    verifier(await page.evaluate(() => document.querySelector('section[data-vue="plan"]').classList.contains("sans-cotes")),
             "calques : sans-cotes perdu après un rechargement");
    verifier(await page.getAttribute(cotes, "aria-pressed") === "false", "calques : le bouton ne reflète pas la mémoire");
    verifier(!await page.evaluate(() => document.querySelector('section[data-vue="plan"]').classList.contains("sans-passages")),
             "calques : sans-passages ajouté sans raison");
    await page.click(cotes);
    verifier(!await page.evaluate(() => document.querySelector('section[data-vue="plan"]').classList.contains("sans-cotes")),
             "calques : sans-cotes reste après le second clic");

    // k absent ou inconnu : le premier élément actif, jamais un élément grisé
    await ouvrir(page, DOC + "#coupes");
    await page.evaluate(() => {
      document.querySelector('section[data-vue="coupes"] .segments button[data-k="A"]').disabled = true;
      location.hash = "#coupes?k=zz";
    });
    const seg = await page.evaluate(() =>
      [...document.querySelectorAll('section[data-vue="coupes"] .segments button[aria-pressed="true"]')].map(b => b.dataset.k));
    verifier(JSON.stringify(seg) === '["B"]', `k inconnu : segment ${JSON.stringify(seg)} au lieu de ["B"]`);

    // Pincement sur un rendu (tactile émulé par CDP)
    const cdp = await page.context().newCDPSession(page);
    await cdp.send("Emulation.setTouchEmulationEnabled", {enabled: true, maxTouchPoints: 2});
    await ouvrir(page, DOC + "#camera");
    r = await scene(page, "camera");
    const cx = r.x + r.w / 2, cy = r.y + r.h / 2;
    const doigts = (a) => [{x: cx - a, y: cy, id: 0}, {x: cx + a, y: cy, id: 1}];
    verifier(await echelle(page) === 1, "rendu : échelle initiale différente de 1");
    const centre = await page.evaluate(() => {
      const s = document.querySelector('section[data-vue="camera"] .scene').getBoundingClientRect();
      const c = document.querySelector('section[data-vue="camera"] .cadre').getBoundingClientRect();
      return [c.left + c.width / 2 - (s.left + s.width / 2), c.top + c.height / 2 - (s.top + s.height / 2)];
    });
    verifier(centre.every(d => Math.abs(d) < 2), `rendu : le cadre n'est pas centré dans la scène (${centre})`);
    await cdp.send("Input.dispatchTouchEvent", {type: "touchStart", touchPoints: doigts(30)});
    for (const a of [50, 80, 110]) await cdp.send("Input.dispatchTouchEvent", {type: "touchMove", touchPoints: doigts(a)});
    await cdp.send("Input.dispatchTouchEvent", {type: "touchEnd", touchPoints: []});
    const k = await echelle(page);
    verifier(k > 1, `pincement : échelle ${k}`);
    await page.click('section[data-vue="camera"] [data-z="0"]');
    verifier(await echelle(page) === 1, "rendu : recadrer ne rend pas l'échelle 1");
    await page.click('section[data-vue="camera"] [data-z="0.7"]');
    verifier(await echelle(page) > 1, "rendu : « + » ne zoome pas");
    await cdp.send("Emulation.setTouchEmulationEnabled", {enabled: false});
  } catch (e) {
    echecs.push(`exception : ${e.message.split("\n")[0]}`);
  }

  return {ok: echecs.length === 0 && erreurs.length === 0, echecs, erreurs};
}
