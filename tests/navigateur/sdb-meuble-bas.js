/* @site reel : le meuble bas de la salle de bain sur le vrai site/, construit par python3 site.py (lancer.sh le sert).
   - Vues : les cinq vues et les onze repères de Plans, à 1440, 1100 et 390 px : sans erreur de console ni réponse en
     erreur, rien ne déborde (onze boutons dans la fiche, tableaux à trois colonnes).
   - Entrée sans fragment : Plans, élévation ; ni Comparer, ni variante, ni Personnaliser.
   - Mesurer : les deux bouts de la plus longue cote de l'élévation donnent « Mesuré : 115 cm » ; caché sur l'iso.
   - Fiche de Plans : les liens Découpe et Montage.
   - Dessins : aucun aplat noir, aucun texte hors du viewBox (exceptions dans GARDES).
   - Achats : totaux, lien « Meuble haut » vers les achats du meuble haut.
   - Anciennes adresses, historique (seize entrées, V8.5 en tête, onze versions figées), redirections, accueil, et la
     page sans JavaScript. */
async page => {
  const BASE = new URL(page.url()).origin;
  const DOC = `${BASE}/sdb/meuble-bas/`;
  const VUES = ["plans", "decoupe", "montage", "achats", "explication"];
  const REPERES = ["elevation", "iso", "iso-ouvert", "eclate", "plan", "coupe", "placard", "porte", "joue", "colonne",
                    "colonne-dessus"];
  const LARGEURS = [[1440, 900], [1100, 800], [390, 844]];
  const echecs = [], erreurs = [];
  const verifier = (vrai, message) => { if (!vrai) echecs.push(message); };
  const egal = (a, b) => JSON.stringify(a) === JSON.stringify(b);

  const preparer = async p => {
    p.on("console", m => { if (m.type() === "error") erreurs.push(`console : ${m.text()}`); });
    p.on("pageerror", e => erreurs.push(`page : ${e.message}`));
    p.on("response", r => { if (r.status() >= 400) erreurs.push(`${r.status()} : ${r.url()}`); });
    p.on("requestfailed", r => {   // une requête interrompue par le changement de page n'est pas une erreur du site
      const raison = (r.failure() || {}).errorText || "";
      if (!raison.includes("ERR_ABORTED")) erreurs.push(`échec : ${r.url()} (${raison})`);
    });
    p.setDefaultTimeout(3000);
    await p.emulateMedia({reducedMotion: "reduce"});
  };
  // polices de Google : feuille vide, le test ne dépend pas du réseau
  const sansPolices = ctx => ctx.route(/^https:\/\/fonts\.(googleapis|gstatic)\.com\//,
                                       r => r.fulfill({status: 200, contentType: "text/css", body: ""}));
  const ouvrir = async (p, adresse) => { await p.goto("about:blank"); await p.goto(adresse); };
  const attendre = async (p, condition, arg, message) => {
    try { await p.waitForFunction(condition, arg, {timeout: 3000}); return true; } catch (e) { echecs.push(message); return false; }
  };
  const partie = async (nom, f) => {
    try { await f(); } catch (e) { echecs.push(`${nom} : exception : ${e.message.split("\n")[0]}`); }
  };

  // Ce qui dépasse : la page en largeur ; la barre, les onglets, la scène, la fiche et le panneau hors de l'écran ;
  // un contenu plus large que sa boîte (barre, fiche, article de lecture), donc coupé ou à faire défiler en largeur.
  const debordements = p => p.evaluate(() => {
    const l = innerWidth, res = [];
    const vu = e => e && e.checkVisibility({visibilityProperty: true, opacityProperty: true});
    if (document.documentElement.scrollWidth > l) res.push(`page : ${document.documentElement.scrollWidth} px pour ${l}`);
    const section = [...document.querySelectorAll("#contenu > section.vue")].find(s => vu(s));
    const boites = [["barre", document.querySelector("#barre")], ["onglets", document.querySelector("nav.vues")],
                    ["panneau", document.querySelector("#panneau-options")]];
    if (section) for (const sel of [".scene", ".fiche", ".lecture"]) boites.push([sel, section.querySelector(sel)]);
    for (const [nom, e] of boites) {
      if (!vu(e)) continue;
      const r = e.getBoundingClientRect();
      if (r.left < -1 || r.right > l + 1) res.push(`${nom} : de ${Math.round(r.left)} à ${Math.round(r.right)} px pour ${l}`);
      if (nom !== ".scene" && e.scrollWidth > e.clientWidth + 1) res.push(`${nom} : contenu de ${e.scrollWidth} px dans ${e.clientWidth}`);
    }
    return res;
  });
  // le repère k de Plans est affiché
  const repereAffiche = (p, k, t) => attendre(p, k => {
    const e = document.querySelector(`section[data-vue="plans"] .scene > .element[data-k="${k}"]`);
    return e && e.checkVisibility();
  }, k, `${t} : le repère ne s'affiche pas`);
  const vueAffichee = (p, vue, t) => attendre(p, v => {
    const s = document.querySelector(`section[data-vue="${v}"]`);
    return s && s.checkVisibility();
  }, vue, `${t} : la vue ne s'affiche pas`);

  await sansPolices(page.context());
  await preparer(page);

  // repères de dessin repris à l'identique dont un texte sort du viewBox : "repère" → raison (vide : aucun)
  const GARDES = {};

  // ------------------------------------------------------------------ 1. toutes les vues, tous les repères, toutes les largeurs
  await partie("vues", async () => {
    for (const [largeur, hauteur] of LARGEURS) {
      await page.setViewportSize({width: largeur, height: hauteur});
      for (const vue of VUES) {
        const ks = vue === "plans" ? REPERES : [""];
        for (const k of ks) {
          const t = `${largeur} px, ${vue}${k ? " " + k : ""}`;
          await ouvrir(page, `${DOC}#${vue}${k ? "?k=" + k : ""}`);
          await vueAffichee(page, vue, t);
          if (k) await repereAffiche(page, k, t);
          const e = await page.evaluate(() => ({
            vues: [...document.querySelectorAll("#contenu > section.vue")].filter(s => s.checkVisibility()).map(s => s.dataset.vue),
            hash: location.hash}));
          verifier(egal(e.vues, [vue]), `${t} : vues visibles ${JSON.stringify(e)}`);
          const d = await debordements(page);
          verifier(d.length === 0, `${t} : déborde (${d.join(" ; ")})`);
        }
      }
    }
  });

  // ------------------------------------------------------------------ 2. sans fragment : Plans, élévation
  await partie("sans fragment", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC);
    await repereAffiche(page, "elevation", "sans fragment");
    const e = await page.evaluate(() => ({
      vues: [...document.querySelectorAll("#contenu > section.vue")].filter(s => s.checkVisibility()).map(s => s.dataset.vue),
      elements: [...document.querySelectorAll('section[data-vue="plans"] .scene > .element')].filter(x => x.checkVisibility()).map(x => x.dataset.k),
      comp: !!document.querySelector("#c-comp"), variante: !!document.querySelector("#c-variante"),
      perso: document.body.innerText.includes("Personnaliser")}));
    verifier(egal(e.vues, ["plans"]) && egal(e.elements, ["elevation"]), `sans fragment : ${JSON.stringify(e)}`);
    verifier(!e.comp && !e.variante && !e.perso, `sans fragment : Comparer, variante ou Personnaliser présent ${JSON.stringify(e)}`);
  });

  // ------------------------------------------------------------------ 3. Mesurer
  await partie("Mesurer", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#plans?k=elevation");
    await repereAffiche(page, "elevation", "Mesurer");
    await page.click('section[data-vue="plans"] .b-mesure');
    const bouts = await page.evaluate(() => {
      const svg = document.querySelector('section[data-vue="plans"] .scene > .element[data-k="elevation"] > svg');
      const lignes = [...svg.querySelectorAll("line.dim")];
      const long = lignes.reduce((a, b) => Math.hypot(b.x2.baseVal.value - b.x1.baseVal.value, b.y2.baseVal.value - b.y1.baseVal.value)
        > Math.hypot(a.x2.baseVal.value - a.x1.baseVal.value, a.y2.baseVal.value - a.y1.baseVal.value) ? b : a);
      const m = long.getScreenCTM();
      const pt = (x, y) => { const p = svg.createSVGPoint(); p.x = x; p.y = y; const q = p.matrixTransform(m); return [q.x, q.y]; };
      return {a: pt(long.x1.baseVal.value, long.y1.baseVal.value), b: pt(long.x2.baseVal.value, long.y2.baseVal.value),
              l: innerWidth, h: innerHeight};
    });
    for (const [x, y] of [bouts.a, bouts.b]) await page.mouse.click(x, y);
    const texte = await page.evaluate(() => {
      const m = document.querySelector('section[data-vue="plans"] .bandeau .mes');
      return m && !m.hidden ? m.textContent.trim() : "";
    });
    verifier(texte === "Mesuré : 115 cm", `Mesurer : bandeau « ${texte} » (bouts ${JSON.stringify(bouts)})`);
    await ouvrir(page, DOC + "#plans?k=iso");
    await repereAffiche(page, "iso", "Mesurer, iso");
    const visible = await page.evaluate(() => document.querySelector('section[data-vue="plans"] .b-mesure').checkVisibility());
    verifier(!visible, "Mesurer : le bouton reste visible sur la vue iso");
  });

  // ------------------------------------------------------------------ 4. fiche de Plans : liens Découpe et Montage
  await partie("fiche", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    for (const [nom, hash] of [["Découpe", "#decoupe"], ["Montage", "#montage"]]) {
      await ouvrir(page, DOC + "#plans?k=elevation");
      await repereAffiche(page, "elevation", `fiche ${nom}`);
      const lien = page.locator(`section[data-vue="plans"] .fiche a:has-text("${nom}")`).first();
      await lien.click();
      await attendre(page, h => location.hash === h, hash, `fiche : le lien « ${nom} » ne mène pas à ${hash}`);
    }
  });

  // ------------------------------------------------------------------ 5. dessins : pas de noir, texte dans le viewBox
  // Le svg de tête de chaque élément de Plans. site.js agrandit le viewBox des dessins de scène : le texte se compare
  // au viewBox d'origine, lu dans le HTML servi (même rang parmi les dessins de la section).
  await partie("dessins", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC);
    const html = await page.evaluate(async u => (await fetch(u)).text(), DOC);
    for (const k of REPERES) {
      const t = `dessins, ${k}`;
      await ouvrir(page, `${DOC}#plans?k=${k}`);
      await repereAffiche(page, k, t);
      const r = await page.evaluate(([v, source]) => {
        const SEL = ".scene > .element > svg";
        const section = document.querySelector(`section[data-vue="${v}"]`);
        const d0 = new DOMParser().parseFromString(source, "text/html").querySelector(`section[data-vue="${v}"]`);
        const tous = [...section.querySelectorAll(SEL)], origine = [...d0.querySelectorAll(SEL)];
        const noirs = [], dehors = [], svgs = tous.filter(s => s.checkVisibility());
        for (const svg of svgs) {
          const o = origine[tous.indexOf(svg)].getAttribute("viewBox").trim().split(/[\s,]+/).map(Number);
          const [x0, y0, w, h] = o;
          for (const e of svg.querySelectorAll("path,rect,circle,ellipse,polygon,polyline,line,text,tspan")) {
            if (e.closest("defs,clipPath,marker,mask,symbol")) continue;
            const s = getComputedStyle(e);
            if (s.fill === "rgb(0, 0, 0)" && e.tagName !== "line") noirs.push(`${e.tagName}${e.getAttribute("class") ? "." + e.getAttribute("class") : ""}`);
          }
          const versSvg = svg.getScreenCTM().inverse();
          for (const tx of svg.querySelectorAll("text")) {
            if (!tx.checkVisibility() || !tx.textContent.trim() || tx.closest(".trace-mesure")) continue;
            const b = tx.getBBox(), m = versSvg.multiply(tx.getScreenCTM());
            const pts = [[b.x, b.y], [b.x + b.width, b.y], [b.x, b.y + b.height], [b.x + b.width, b.y + b.height]].map(([x, y]) => {
              const p = svg.createSVGPoint(); p.x = x; p.y = y; return p.matrixTransform(m);
            });
            const g = 0.5;
            if (Math.min(...pts.map(p => p.x)) < x0 - g || Math.max(...pts.map(p => p.x)) > x0 + w + g
                || Math.min(...pts.map(p => p.y)) < y0 - g || Math.max(...pts.map(p => p.y)) > y0 + h + g)
              dehors.push(tx.textContent.trim().slice(0, 30));
          }
        }
        return {n: svgs.length, noirs, dehors};
      }, ["plans", html]);
      verifier(r.n > 0, `${t} : aucun dessin visible`);
      verifier(r.noirs.length === 0, `${t} : aplat noir ${JSON.stringify(r.noirs.slice(0, 8))}`);
      verifier(r.dehors.length === 0 || k in GARDES, `${t} : texte hors du viewBox ${JSON.stringify(r.dehors.slice(0, 8))}`);
    }
  });

  // ------------------------------------------------------------------ 6. Achats : totaux, lien vers le meuble haut
  await partie("achats", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#achats");
    await vueAffichee(page, "achats", "achats");
    const total = await page.evaluate(() => document.querySelector('section[data-vue="achats"]').textContent.replace(/\s+/g, " "));
    for (const m of ["296,82 €", "476,64 €"]) verifier(total.includes(m), `achats : « ${m} » absent`);
    const lien = page.locator('section[data-vue="achats"] a:has-text("Meuble haut")').first();
    const [reponse] = await Promise.all([page.waitForNavigation(), lien.click()]);
    const ici = await page.evaluate(() => location.pathname + location.hash);
    verifier(ici === "/sdb/meuble-haut/#achats" && reponse && reponse.status() === 200,
             `achats : « Meuble haut » mène à ${ici} (${reponse && reponse.status()})`);
  });

  // ------------------------------------------------------------------ 7. anciennes adresses
  await partie("anciennes adresses", async () => {
    const suivre = async (entree, chemin) => {
      await page.goto("about:blank");
      await page.goto(BASE + entree);
      await attendre(page, c => location.pathname === c && document.readyState === "complete", chemin, `${entree} : n'arrive pas à ${chemin}`);
      return page.evaluate(() => ({chemin: location.pathname, hash: location.hash}));
    };
    const cas = [
      ["/sdb-meuble-bas.html#f-placard", "/sdb/meuble-bas/", "#plans?k=placard"],
      ["/sdb-meuble-bas.html#finition", "/sdb/meuble-bas/", "#decoupe"],
      ["/sdb-meuble-bas.html#structure", "/sdb/meuble-bas/", "#explication"],
      ["/sdb-meuble-bas.html#f-face", "/sdb/meuble-bas/", "#plans?k=elevation"],
      ["/sdb-meuble-bas.html#changements", "/sdb/meuble-bas/historique.html", ""],
      ["/sdb-meuble-bas.html#inconnue", "/sdb/meuble-bas/", ""],
      ["/sdb-meuble-bas.html", "/sdb/meuble-bas/", ""],
    ];
    for (const [entree, chemin, hash] of cas) {
      const r = await suivre(entree, chemin);
      verifier(r.chemin === chemin && r.hash === hash, `${entree} : ${JSON.stringify(r)} au lieu de ${chemin}${hash}`);
    }
  });

  // ------------------------------------------------------------------ 8. historique et versions figées
  await partie("historique", async () => {
    await ouvrir(page, DOC + "historique.html");
    const h = await page.evaluate(() => {
      const li = [...document.querySelectorAll("ol.fil li")];
      return {n: li.length, premiere: li.length ? li[0].textContent : "",
              figees: [...document.querySelectorAll('a[href*="archives/"]')].map(a => a.href)};
    });
    verifier(h.n === 16, `historique : ${h.n} entrées au lieu de 16`);
    verifier(h.premiere.includes("V8.5"), `historique : la première entrée n'est pas en V8.5 : « ${h.premiere.slice(0, 60)} »`);
    verifier(h.figees.length === 11, `historique : ${h.figees.length} versions figées au lieu de 11`);
    for (const u of h.figees) {
      const statut = await page.evaluate(async u => (await fetch(u)).status, u);
      verifier(statut === 200, `historique : ${u} en statut ${statut}`);
    }
  });

  // ------------------------------------------------------------------ 9. les pages du meuble haut et des achats : redirections
  await partie("redirections", async () => {
    for (const adresse of ["/sdb-meuble-achats.html", "/sdb-meuble-haut.html"]) {
      await page.goto("about:blank");
      const r = await page.goto(BASE + adresse);
      verifier(r && r.status() === 200, `${adresse} : statut ${r && r.status()}`);
      await attendre(page, () => location.pathname === "/sdb/meuble-haut/", null, `${adresse} : n'arrive pas sur /sdb/meuble-haut/`);
    }
  });

  // ------------------------------------------------------------------ 10. accueil
  await partie("accueil", async () => {
    await ouvrir(page, BASE + "/");
    const n = await page.evaluate(() => document.querySelectorAll('svg a[href="sdb/meuble-bas/"][aria-label="Salle de bain"]').length);
    verifier(n === 1, `accueil : ${n} lien de la salle de bain vers sdb/meuble-bas/ sur le plan`);
  });

  // ------------------------------------------------------------------ 11. sans JavaScript
  await partie("sans JavaScript", async () => {
    const sansJs = await page.context().browser().newContext({javaScriptEnabled: false});
    try {
      await sansPolices(sansJs);
      const p = await sansJs.newPage();
      await preparer(p);
      for (const [largeur, hauteur] of [[1440, 900], [390, 844]]) {
        await p.setViewportSize({width: largeur, height: hauteur});
        await p.goto(DOC);
        const s = await p.evaluate(() => {
          const vues = [...document.querySelectorAll("#contenu > section.vue")].filter(x => x.checkVisibility())
            .map(x => { const r = x.getBoundingClientRect(); return [x.dataset.vue, Math.round(r.top + scrollY), Math.round(r.bottom + scrollY)]; });
          const texte = document.querySelector("#contenu").innerText;
          return {classe: document.documentElement.className, vues,
                  titres: ["Pièces", "Pose de la colonne", "Les deux meubles", "Mesures"].filter(x => texte.includes(x))};
        });
        const suite = s.vues.every((v, i) => i === 0 || v[1] >= s.vues[i - 1][2] - 1);
        verifier(s.classe.includes("sans-js") && egal(s.vues.map(v => v[0]), VUES) && suite && s.titres.length === 4,
                 `sans JavaScript, ${largeur} px : ${JSON.stringify(s)}`);
        const d = await debordements(p);
        verifier(!d.some(x => x.startsWith("page")), `sans JavaScript, ${largeur} px : déborde (${d.join(" ; ")})`);
      }
    } finally {
      await sansJs.close();
    }
  });

  return {ok: echecs.length === 0 && erreurs.length === 0, echecs, erreurs};
}
