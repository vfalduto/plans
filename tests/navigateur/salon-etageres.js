/* @site reel : les Étagères du salon sur le vrai site/, construit par python3 site.py (tests/navigateur/lancer.sh le sert).
   - Vues : pour chaque variante (Actuelle, Rangs, Décalée, Escalier), les six vues, les cinq repères de Plans
     (élévation, dessus, profil, travée, détail) et celui d'Iso (iso), à 1440, 1100 et 390 px : sans erreur de
     console ni réponse en erreur, rien ne déborde, aucun défilement horizontal, aucun onglet grisé.
   - Variante : choisir Rangs depuis #plans?k=dessus charge rangs.html#plans?k=dessus ; pastille « V1.9 » ; pas de
     « Personnaliser ».
   - Comparaison : #plans?k=dessus&c=escalier, deux dessins de même viewBox, « Actuelle » et « Escalier » en bas, rien
     de la variante comparée coupé ; aucun « pas d'équivalent » ni « comparaison indisponible » sur les six repères
     (Plans et Iso) ; l'adresse rechargée redonne le même état ; Escalier en base inverse les deux ; « Comparer »
     caché hors de Plans et d'Iso.
   - Mesurer : les centres de deux montants voisins de l'élévation donnent 55 cm (± 0,5) ; pas de Mesurer dans Iso ;
     l'ancienne adresse #plans?k=iso ouvre l'onglet Iso (#iso?k=iso).
   - Dessins lisibles (scènes, Découpe, Explication) : aucune forme ni texte noir par défaut, aucune police à chasse
     fixe ; aucun texte hors du viewBox, sauf les écarts connus de la référence (ECARTS_CONNUS : l'étiquette « mur »
     du dessin de l'entaille, en Découpe), relevés sans échec.
   - Explication : quatre vignettes, celle de la variante en aria-current ; Actuelle : deux images chargées ; les
     trois autres : aucune image, « les voir » mène à l'Explication d'Actuelle.
   - Anciennes adresses (chaque ancre, #iso → #iso?k=iso, inconnue, aucune, changements), historique (dix
     changements sous Actuelle, V1.9 en tête, aucun ailleurs, aucune version figée), et la page sans JavaScript
     (1440 et 390 px). */
async page => {
  const BASE = new URL(page.url()).origin;
  const DOC = `${BASE}/salon/etageres/`;
  const VUES = ["plans", "iso", "decoupe", "montage", "achats", "explication"];
  const REPERES = {plans: ["elevation", "dessus", "profil", "travee", "detail"], iso: ["iso"]};   // repères par vue
  const TOUS = Object.entries(REPERES).flatMap(([v, ks]) => ks.map(k => [v, k]));            // [vue, repère]
  const VARIANTES = {actuelle: "", rangs: "rangs.html", decalee: "decalee.html", escalier: "escalier.html"};
  const NOMS = {actuelle: "Actuelle", rangs: "Rangs", decalee: "Décalée", escalier: "Escalier"};
  const LARGEURS = [[1440, 900], [1100, 800], [390, 844]];
  const ANCRES = {dispositions: "explication", iso: "iso?k=iso", meuble: "plans?k=elevation", presentoir: "explication",
                  rendus: "explication", materiaux: "explication", debit: "decoupe", charges: "explication",
                  achats: "achats", montage: "montage", valider: "explication"};
  // textes hors du viewBox déjà dans le dessin de référence (tracé identique à la virgule près), par vue
  const ECARTS_CONNUS = {decoupe: ["mur"]};
  const echecs = [], erreurs = [], releves = [];
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

  // Ce qui dépasse : la page en largeur ; la barre, les onglets, la scène, la fiche hors de l'écran ; un contenu plus
  // large que sa boîte (barre, fiche, article de lecture), donc coupé ou à faire défiler en largeur.
  const debordements = p => p.evaluate(() => {
    const l = innerWidth, res = [];
    const vu = e => e && e.checkVisibility({visibilityProperty: true, opacityProperty: true});
    if (document.documentElement.scrollWidth > l) res.push(`page : ${document.documentElement.scrollWidth} px pour ${l}`);
    const section = [...document.querySelectorAll("#contenu > section.vue")].find(s => vu(s));
    const boites = [["barre", document.querySelector("#barre")], ["onglets", document.querySelector("nav.vues")]];
    if (section) for (const sel of [".scene", ".fiche", ".lecture"]) boites.push([sel, section.querySelector(sel)]);
    for (const [nom, e] of boites) {
      if (!vu(e)) continue;
      const r = e.getBoundingClientRect();
      if (r.left < -1 || r.right > l + 1) res.push(`${nom} : de ${Math.round(r.left)} à ${Math.round(r.right)} px pour ${l}`);
      if (nom !== ".scene" && e.scrollWidth > e.clientWidth + 1) res.push(`${nom} : contenu de ${e.scrollWidth} px dans ${e.clientWidth}`);
    }
    return res;
  });
  // le repère k de la vue (plans ou iso) est affiché
  const repereAffiche = (p, vue, k, t) => attendre(p, ([v, k]) => {
    const e = document.querySelector(`section[data-vue="${v}"] .scene > .element[data-k="${k}"]:not(.b)`);
    return e && e.checkVisibility();
  }, [vue, k], `${t} : le repère ne s'affiche pas`);
  const vueAffichee = (p, vue, t) => attendre(p, v => {
    const s = document.querySelector(`section[data-vue="${v}"]`);
    return s && s.checkVisibility();
  }, vue, `${t} : la vue ne s'affiche pas`);
  // la vue visible (Plans ou Iso) a ses deux étiquettes de comparaison
  const comparee = (p, t) => attendre(p, () => {
    const s = [...document.querySelectorAll("#contenu > section.vue")].find(x => x.checkVisibility());
    return Boolean(s) && s.querySelectorAll(".bandeau .etiq-var").length === 2;
  }, null, `${t} : pas d'étiquettes`);

  await sansPolices(page.context());
  await preparer(page);

  // ------------------------------------------------------------------ 1. vues : variantes, repères, largeurs
  await partie("vues", async () => {
    for (const [cle, fichier] of Object.entries(VARIANTES)) {
      for (const [largeur, hauteur] of LARGEURS) {
        await page.setViewportSize({width: largeur, height: hauteur});
        for (const vue of VUES) {
          for (const k of REPERES[vue] || [""]) {
            const t = `${cle}, ${largeur} px, ${vue}${k ? " " + k : ""}`;
            await ouvrir(page, `${DOC}${fichier}#${vue}${k ? "?k=" + k : ""}`);
            await vueAffichee(page, vue, t);
            if (k) await repereAffiche(page, vue, k, t);
            const e = await page.evaluate(() => ({
              vues: [...document.querySelectorAll("#contenu > section.vue")].filter(s => s.checkVisibility()).map(s => s.dataset.vue),
              grises: document.querySelectorAll('nav.vues a[aria-disabled="true"]').length}));
            verifier(egal(e.vues, [vue]), `${t} : vues visibles ${JSON.stringify(e.vues)}`);
            verifier(e.grises === 0, `${t} : ${e.grises} onglet(s) grisé(s)`);
            const d = await debordements(page);
            verifier(d.length === 0, `${t} : déborde (${d.join(" ; ")})`);
          }
        }
      }
    }
  });

  // ------------------------------------------------------------------ 2. variante, pastille, pas de Personnaliser
  await partie("variante", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#plans?k=dessus");
    await repereAffiche(page, "plans", "dessus", "variante");
    const b = await page.evaluate(() => ({
      version: (document.querySelector(".b-case.version .num") || {}).textContent,
      perso: !!document.querySelector("#c-options"),
      choix: [...document.querySelectorAll("#c-variante option")].map(o => o.textContent)}));
    verifier(b.version === "V1.9", `variante : pastille « ${b.version} »`);
    verifier(!b.perso, "variante : un bouton Personnaliser est présent");
    verifier(egal(b.choix, Object.values(NOMS)), `variante : choix ${JSON.stringify(b.choix)}`);
    await page.selectOption("#c-variante", "rangs");
    await attendre(page, () => location.pathname.endsWith("/salon/etageres/rangs.html") && location.hash === "#plans?k=dessus",
                   null, "variante : Rangs ne s'ouvre pas sur rangs.html#plans?k=dessus");
    await repereAffiche(page, "plans", "dessus", "variante, Rangs");
  });

  // ------------------------------------------------------------------ 3. comparaison
  const lireComparaison = p => p.evaluate(() => {
    const scene = [...document.querySelectorAll("#contenu > section.vue")].find(x => x.checkVisibility()).querySelector(".scene");
    const svgs = [...scene.querySelectorAll(".element > svg")].filter(x => x.checkVisibility());
    const coupe = [];
    for (const svg of svgs) {      // le contenu du dessin tient dans son viewBox : rien n'est coupé
      const vb = svg.viewBox.baseVal, b = svg.getBBox();
      if (b.x < vb.x - 0.5 || b.y < vb.y - 0.5 || b.x + b.width > vb.x + vb.width + 0.5 || b.y + b.height > vb.y + vb.height + 0.5)
        coupe.push({vb: [vb.x, vb.y, vb.width, vb.height], b: [b.x, b.y, b.width, b.height]});
    }
    return {hash: location.hash, chemin: location.pathname, n: svgs.length,
            viewBox: [...new Set(svgs.map(x => x.getAttribute("viewBox")))],
            etiquettes: [...scene.querySelectorAll(".bandeau .etiq-var")].map(x => x.textContent),
            manque: scene.querySelectorAll(".bandeau .etiq-var.manque").length, coupe};
  });
  await partie("comparaison", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#plans?k=dessus&c=escalier");
    await comparee(page, "comparaison dessus");
    let e = await lireComparaison(page);
    verifier(e.n === 2 && e.viewBox.length === 1, `comparaison dessus : ${e.n} dessins, viewBox ${JSON.stringify(e.viewBox)}`);
    verifier(egal(e.etiquettes, ["Actuelle", "Escalier"]) && e.manque === 0, `comparaison dessus : ${JSON.stringify(e.etiquettes)}`);
    verifier(e.coupe.length === 0, `comparaison dessus : dessin coupé ${JSON.stringify(e.coupe)}`);
    await page.reload();
    await comparee(page, "comparaison rechargée");
    const r = await lireComparaison(page);
    verifier(r.hash === "#plans?k=dessus&c=escalier" && egal(r.etiquettes, e.etiquettes),
             `comparaison rechargée : ${JSON.stringify([r.hash, r.etiquettes])}`);
    for (const [vue, k] of TOUS) {
      for (const c of ["rangs", "escalier"]) {
        await ouvrir(page, `${DOC}#${vue}?k=${k}&c=${c}`);
        await comparee(page, `comparaison ${k} avec ${c}`);
        e = await lireComparaison(page);
        verifier(e.manque === 0 && egal(e.etiquettes, ["Actuelle", NOMS[c]]), `comparaison ${k} avec ${c} : ${JSON.stringify(e.etiquettes)}`);
        verifier(e.viewBox.length === 1, `comparaison ${k} avec ${c} : viewBox ${JSON.stringify(e.viewBox)}`);
        verifier(e.coupe.length === 0, `comparaison ${k} avec ${c} : dessin coupé ${JSON.stringify(e.coupe)}`);
      }
    }
    await ouvrir(page, DOC + "#plans?k=dessus&c=escalier");
    await comparee(page, "base Escalier");
    await page.selectOption("#c-variante", "escalier");
    await attendre(page, () => location.pathname.endsWith("/escalier.html"), null, "base Escalier : la page ne change pas");
    await comparee(page, "base Escalier, chargée");
    e = await lireComparaison(page);
    verifier(e.hash === "#plans?k=dessus&c=actuelle" && egal(e.etiquettes, ["Escalier", "Actuelle"]),
             `base Escalier : ${JSON.stringify([e.hash, e.etiquettes])}`);
    for (const vue of VUES.slice(2)) {
      await ouvrir(page, `${DOC}#${vue}`);
      await vueAffichee(page, vue, `Comparer, ${vue}`);
      const vu = await page.evaluate(() => document.querySelector("#c-comp").checkVisibility());
      verifier(!vu, `Comparer : visible dans ${vue}`);
    }
  });

  // ------------------------------------------------------------------ 4. Mesurer
  await partie("Mesurer", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    await ouvrir(page, DOC + "#plans?k=elevation");
    await repereAffiche(page, "plans", "elevation", "Mesurer");
    await page.click('section[data-vue="plans"] .b-mesure');
    const centres = await page.evaluate(() => {
      const svg = document.querySelector('section[data-vue="plans"] .scene > .element[data-k="elevation"] > svg');
      return [...svg.querySelectorAll("rect.mont")].slice(0, 2).map(r => {
        const b = r.getBoundingClientRect();
        return [b.left + b.width / 2, b.top + b.height / 2];
      });
    });
    for (const [x, y] of centres) await page.mouse.click(x, y);
    const texte = await page.evaluate(() => {
      const m = document.querySelector('section[data-vue="plans"] .bandeau .mes');
      return m && !m.hidden ? m.textContent.trim() : "";
    });
    const m = /^Mesuré : ([\d,]+) cm$/.exec(texte), v = m ? parseFloat(m[1].replace(",", ".")) : NaN;
    verifier(Math.abs(v - 55) <= 0.5, `Mesurer : bandeau « ${texte} » (centres ${JSON.stringify(centres)})`);
    await ouvrir(page, DOC + "#iso?k=iso");
    await repereAffiche(page, "iso", "iso", "Mesurer, iso");
    const mi = await page.evaluate(() => ({
      dansIso: document.querySelectorAll('section[data-vue="iso"] .b-mesure').length,
      visibles: [...document.querySelectorAll(".b-mesure")].filter(b => b.checkVisibility()).length}));
    verifier(mi.dansIso === 0 && mi.visibles === 0, `Mesurer : présent dans Iso ${JSON.stringify(mi)}`);
    // ancienne adresse : l'iso était un repère de Plans
    await ouvrir(page, DOC + "#plans?k=iso");
    await repereAffiche(page, "iso", "iso", "#plans?k=iso");
    await attendre(page, () => location.hash === "#iso?k=iso", null, "#plans?k=iso : l'adresse ne devient pas #iso?k=iso");
    const o = await page.evaluate(() => ({
      vues: [...document.querySelectorAll("#contenu > section.vue")].filter(s => s.checkVisibility()).map(s => s.dataset.vue),
      courant: [...document.querySelectorAll("nav.vues a[aria-current='page']")].map(a => a.dataset.vue)}));
    verifier(egal(o, {vues: ["iso"], courant: ["iso"]}), `#plans?k=iso : ${JSON.stringify(o)}`);
  });

  // ------------------------------------------------------------------ 5. dessins lisibles
  await partie("dessins", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    for (const [cle, fichier] of Object.entries(VARIANTES)) {
      const adresse = DOC + fichier;
      await ouvrir(page, adresse);
      const html = await page.evaluate(async u => (await fetch(u)).text(), adresse);
      const etats = [...TOUS, ["decoupe", ""], ["explication", ""]];
      for (const [vue, k] of etats) {
        const t = `dessins, ${cle}, ${vue}${k ? " " + k : ""}`;
        await ouvrir(page, `${adresse}#${vue}${k ? "?k=" + k : ""}`);
        await vueAffichee(page, vue, t);
        if (k) await repereAffiche(page, vue, k, t);
        const r = await page.evaluate(([v, source]) => {
          const SEL = ".scene > .element > svg, .lecture svg";
          const section = document.querySelector(`section[data-vue="${v}"]`);
          const d0 = new DOMParser().parseFromString(source, "text/html").querySelector(`section[data-vue="${v}"]`);
          const tous = [...section.querySelectorAll(SEL)], origine = [...d0.querySelectorAll(SEL)];
          const noirs = [], chasse = [], dehors = [], svgs = tous.filter(s => s.checkVisibility());
          for (const svg of svgs) {
            const [x0, y0, w, h] = origine[tous.indexOf(svg)].getAttribute("viewBox").trim().split(/[\s,]+/).map(Number);
            for (const e of svg.querySelectorAll("path,rect,circle,ellipse,polygon,polyline,line,text,tspan")) {
              if (e.closest("defs,clipPath,marker,mask,symbol")) continue;
              const s = getComputedStyle(e), nom = `${e.tagName}${e.getAttribute("class") ? "." + e.getAttribute("class") : ""}`;
              if (e.tagName !== "line" && s.fill === "rgb(0, 0, 0)") noirs.push(nom + " (fill)");
              if (s.stroke === "rgb(0, 0, 0)") noirs.push(nom + " (stroke)");
              if (e.tagName === "text" && /mono|courier|consol/i.test(s.fontFamily)) chasse.push(`${nom} : ${s.fontFamily}`);
            }
            // un dessin dans un dessin (la cote d'un sous-svg) se compare à son propre viewBox : seuls les textes du svg
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
                dehors.push(tx.textContent.trim().slice(0, 40));
            }
          }
          return {n: svgs.length, noirs, chasse, dehors};
        }, [vue, html]);
        verifier(r.n > 0, `${t} : aucun dessin visible`);
        verifier(r.noirs.length === 0, `${t} : noir par défaut ${JSON.stringify(r.noirs.slice(0, 8))}`);
        verifier(r.chasse.length === 0, `${t} : police à chasse fixe ${JSON.stringify(r.chasse.slice(0, 4))}`);
        const connus = ECARTS_CONNUS[vue] || [], inconnus = r.dehors.filter(x => !connus.includes(x));
        verifier(inconnus.length === 0, `${t} : texte hors du viewBox ${JSON.stringify(inconnus.slice(0, 8))}`);
        if (r.dehors.length > inconnus.length)
          releves.push(`${t} : texte hors du viewBox, comme dans la référence ${JSON.stringify(r.dehors.filter(x => connus.includes(x)))}`);
      }
    }
  });

  // ------------------------------------------------------------------ 6. Explication
  await partie("explication", async () => {
    await page.setViewportSize({width: 1440, height: 900});
    for (const [cle, fichier] of Object.entries(VARIANTES)) {
      const t = `explication, ${cle}`;
      await ouvrir(page, `${DOC}${fichier}#explication`);
      await vueAffichee(page, "explication", t);
      const e = await page.evaluate(() => {
        const s = document.querySelector('section[data-vue="explication"]');
        return {vignettes: [...s.querySelectorAll("a.dispo")].map(a => [a.getAttribute("href"), a.getAttribute("aria-current")]),
                images: s.querySelectorAll("img").length};
      });
      verifier(e.vignettes.length === 4, `${t} : ${e.vignettes.length} vignettes`);
      verifier(egal(e.vignettes.map(v => v[1] === "page"), Object.keys(VARIANTES).map(c => c === cle)),
               `${t} : aria-current ${JSON.stringify(e.vignettes)}`);
      if (cle === "actuelle") {
        verifier(e.images === 2, `${t} : ${e.images} images au lieu de 2`);
        for (let i = 0; i < e.images; i++) {
          await page.locator('section[data-vue="explication"] img').nth(i).scrollIntoViewIfNeeded();
          await attendre(page, i => { const im = document.querySelectorAll('section[data-vue="explication"] img')[i];
                                      return im.complete && im.naturalWidth > 0; }, i, `${t} : image ${i + 1} non chargée`);
        }
      } else {
        verifier(e.images === 0, `${t} : ${e.images} images au lieu d'aucune`);
        const lien = page.locator('section[data-vue="explication"] a:has-text("les voir")').first();
        await lien.click();
        await attendre(page, d => location.href === d + "#explication", DOC, `${t} : « les voir » ne mène pas à ${DOC}#explication`);
      }
    }
  });

  // ------------------------------------------------------------------ 7. anciennes adresses
  await partie("anciennes adresses", async () => {
    const suivre = async (entree, chemin) => {
      await page.goto("about:blank");
      await page.goto(BASE + entree);
      await attendre(page, c => location.pathname === c && document.readyState === "complete", chemin, `${entree} : n'arrive pas à ${chemin}`);
      return page.evaluate(() => ({chemin: location.pathname, hash: location.hash}));
    };
    const cas = [...Object.entries(ANCRES).map(([a, f]) => [`/salon-etageres.html#${a}`, "/salon/etageres/", "#" + f]),
                 ["/salon-etageres.html#changements", "/salon/etageres/historique.html", ""],
                 ["/salon-etageres.html#inconnue", "/salon/etageres/", ""],
                 ["/salon-etageres.html", "/salon/etageres/", ""]];
    for (const [entree, chemin, hash] of cas) {
      const r = await suivre(entree, chemin);
      verifier(r.chemin === chemin && r.hash === hash, `${entree} : ${JSON.stringify(r)} au lieu de ${chemin}${hash}`);
    }
    await suivre("/salon-etageres.html", "/salon/etageres/");
    await repereAffiche(page, "plans", "elevation", "/salon-etageres.html : Plans, élévation");
  });

  // ------------------------------------------------------------------ 8. historique
  await partie("historique", async () => {
    await ouvrir(page, DOC + "historique.html");
    const h = await page.evaluate(() => [...document.querySelectorAll("section.variante")].map(s => ({
      nom: s.querySelector("h2").textContent, n: s.querySelectorAll("ol.fil li").length,
      h3: [...s.querySelectorAll("h3")].map(x => x.textContent),
      premiere: (s.querySelector("ol.fil li") || {textContent: ""}).textContent.slice(0, 60)})));
    verifier(h.length > 0 && h[0].premiere.includes("V1.9"), `historique : la première entrée d'Actuelle n'est pas en V1.9 : « ${h.length ? h[0].premiere : ""} »`);
    verifier(egal(h.map(s => [s.nom, s.n]), [["Actuelle", 10], ["Rangs", 0], ["Décalée", 0], ["Escalier", 0]]),
             `historique : ${JSON.stringify(h)}`);
    verifier(h.every(s => s.h3.every(x => x === "Changements")), `historique : une section autre que Changements ${JSON.stringify(h)}`);
  });

  // ------------------------------------------------------------------ 9. sans JavaScript
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
          const dessins = [...document.querySelectorAll('section[data-vue="plans"] .scene > .element > svg, section[data-vue="iso"] .scene > .element > svg')]
            .filter(x => x.checkVisibility()).length;
          return {classe: document.documentElement.className, vues, dessins};
        });
        const suite = s.vues.every((v, i) => i === 0 || v[1] >= s.vues[i - 1][2] - 1);
        verifier(s.classe.includes("sans-js") && egal(s.vues.map(v => v[0]), VUES) && suite && s.dessins === 6,
                 `sans JavaScript, ${largeur} px : ${JSON.stringify(s)}`);
        const d = await debordements(p);
        verifier(!d.some(x => x.startsWith("page")), `sans JavaScript, ${largeur} px : déborde (${d.join(" ; ")})`);
      }
    } finally {
      await sansJs.close();
    }
  });

  return {ok: echecs.length === 0 && erreurs.length === 0, echecs, erreurs, releves};
}
